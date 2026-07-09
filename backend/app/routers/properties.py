# 시험 상세/토글/삭제 + 곡선(LTTB·CSV) + 물성 계산/조회 라우터(곡선 소유자는 test).
from __future__ import annotations

import io
import math
from urllib.parse import quote

import numpy as np
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import analysis, curve_store, fitting, true_stress, viscoelastic
from app.cards import lsdyna_mat024_card, lsdyna_mat098_card
from app.db import get_db
from app.unit_systems import SYSTEMS, get_system
from app.models import ConstitutiveFit, ProcessedResult, RawCurveRef, Test
from app.schemas import PropertiesOut, TestOut, TestPatch

router = APIRouter(prefix="/api", tags=["tests"])


def _get_test(db: Session, tid: int) -> Test:
    t = db.get(Test, tid)
    if t is None:
        raise HTTPException(status_code=404, detail="test not found")
    return t


@router.get("/tests/{tid}", response_model=TestOut)
def get_test(tid: int, db: Session = Depends(get_db)) -> TestOut:
    return TestOut.model_validate(_get_test(db, tid))


@router.patch("/tests/{tid}", response_model=TestOut)
def patch_test(
    tid: int, payload: TestPatch, db: Session = Depends(get_db)
) -> TestOut:
    """valid/invalid_reason 토글(이상치 수동 제외 워크플로)."""
    t = _get_test(db, tid)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(t, field, value)
    db.commit()
    db.refresh(t)
    return TestOut.model_validate(t)


@router.delete("/tests/{tid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test(tid: int, db: Session = Depends(get_db)) -> None:
    """시험 삭제 — raw_curve_ref/processed_result(cascade) + Parquet 파일 동반 정리(C4)."""
    t = _get_test(db, tid)
    curve = curve_store.curve_path(tid)
    db.delete(t)
    db.commit()
    if curve.exists():
        curve.unlink()


def _load_curve(db: Session, tid: int):
    """test_id의 곡선 DataFrame을 로드. ref/파일 누락 시 404."""
    ref = db.query(RawCurveRef).filter(RawCurveRef.test_id == tid).one_or_none()
    if ref is None or ref.storage != "parquet_fs":
        raise HTTPException(status_code=404, detail="curve not available")
    path = curve_store.curve_path(tid)
    if not path.exists():
        raise HTTPException(status_code=404, detail="curve file missing")
    return curve_store.read_curve(tid)


# kind → (x컬럼, y컬럼). nominal=공칭 σ-ε, force_disp=하중-변위, relaxation=점탄성 완화 E(t).
_KIND_COLUMNS = {
    "nominal": ("eng_strain", "eng_stress_Pa"),
    "force_disp": ("disp_m", "force_N"),
    "relaxation": ("time_s", "relax_modulus_Pa"),
}


@router.get("/tests/{tid}/curve")
def get_curve(
    tid: int,
    kind: str = Query(default="nominal"),
    max_points: int = Query(default=2000, ge=3, le=100000),
    db: Session = Depends(get_db),
) -> dict:
    """곡선 포인트(LTTB 다운샘플). 곡선 소유자는 test([gaps] A3).

    kind=true(진응력)는 넥킹 개시까지만 물리 유효 → necking 마커 좌표 동봉(§6.2).
    """
    _get_test(db, tid)
    df = _load_curve(db, tid)

    if kind == "true":
        en = np.asarray(df["eng_strain"], dtype=float)
        es = np.asarray(df["eng_stress_Pa"], dtype=float)
        finite = np.isfinite(en) & np.isfinite(es)
        conv = true_stress.true_curve_with_necking(en[finite], es[finite])
        x = np.asarray(conv["true_strain"], dtype=float)
        y = np.asarray(conv["true_stress"], dtype=float)
        xs, ys = curve_store.lttb_downsample(x, y, n_out=max_points)
        return {
            "kind": "true",
            "x_label": "true_strain",
            "y_label": "true_stress_Pa",
            "n_total": int(x.size),
            "n_returned": int(xs.size),
            "x": [float(v) for v in xs],
            "y": [float(v) for v in ys],
            "necking": conv["necking"],
        }

    if kind not in _KIND_COLUMNS:
        raise HTTPException(status_code=422, detail=f"unknown kind: {kind}")
    df_ = df
    xcol, ycol = _KIND_COLUMNS[kind]
    x = np.asarray(df_[xcol], dtype=float)
    y = np.asarray(df_[ycol], dtype=float)
    finite = np.isfinite(x) & np.isfinite(y)
    x, y = x[finite], y[finite]
    xs, ys = curve_store.lttb_downsample(x, y, n_out=max_points)
    return {
        "kind": kind,
        "x_label": xcol,
        "y_label": ycol,
        "n_total": int(x.size),
        "n_returned": int(xs.size),
        "x": [float(v) for v in xs],
        "y": [float(v) for v in ys],
        "necking": None,
    }


@router.get("/tests/{tid}/curve.csv")
def get_curve_csv(tid: int, db: Session = Depends(get_db)) -> StreamingResponse:
    """곡선 풀해상도 CSV 다운로드. RFC 5987 filename* 동반 Content-Disposition."""
    _get_test(db, tid)
    df = _load_curve(db, tid)
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    fname = f"test_{tid}_curve.csv"
    disposition = (
        f"attachment; filename=\"{fname}\"; filename*=UTF-8''{quote(fname)}"
    )
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": disposition},
    )


@router.post("/tests/{tid}/properties:compute")
def compute_properties(
    tid: int,
    e_range: tuple[float, float] | None = Body(default=None),
    offset: float = Body(default=0.002),
    toe: bool = Body(default=True),
    db: Session = Depends(get_db),
) -> PropertiesOut:
    """기본 물성 동기 계산(회귀구간/offset 옵션). 곡선 풀해상도로 산출·영속(upsert)."""
    test = _get_test(db, tid)
    df = _load_curve(db, tid)
    strain = np.asarray(df["eng_strain"], dtype=float)
    stress = np.asarray(df["eng_stress_Pa"], dtype=float)

    category = None
    if test.specimen and test.specimen.material:
        category = test.specimen.material.category

    kwargs: dict = {"offset": offset, "toe_correct": toe, "category": category}
    if e_range is not None:
        kwargs["e_range"] = tuple(e_range)
    metrics = analysis.compute_all(strain, stress, A0=None, **kwargs)

    pr = (
        db.query(ProcessedResult)
        .filter(ProcessedResult.test_id == tid)
        .one_or_none()
    )
    if pr is None:
        pr = ProcessedResult(test_id=tid, params={})
        db.add(pr)
    pr.youngs_modulus_pa = metrics["youngs_modulus_pa"]
    pr.yield_strength_pa = metrics["yield_strength_pa"]
    pr.uts_pa = metrics["uts_pa"]
    pr.uniform_elongation = metrics["uniform_elongation"]
    pr.fracture_elongation = metrics["fracture_elongation"]
    pr.strain_hardening_n = metrics["strain_hardening_n"]
    pr.strength_coeff_k_pa = metrics["strength_coeff_k_pa"]
    pr.params = metrics["params"].model_dump()
    pr.extra_metrics = metrics["extra_metrics"]
    db.commit()
    db.refresh(pr)
    return PropertiesOut.model_validate(pr)


@router.get("/tests/{tid}/properties", response_model=PropertiesOut)
def get_properties(tid: int, db: Session = Depends(get_db)) -> PropertiesOut:
    _get_test(db, tid)
    pr = (
        db.query(ProcessedResult)
        .filter(ProcessedResult.test_id == tid)
        .one_or_none()
    )
    if pr is None:
        raise HTTPException(status_code=404, detail="properties not computed")
    return PropertiesOut.model_validate(pr)


def _plastic_true(df, E: float | None) -> tuple[np.ndarray, np.ndarray]:
    """진응력·소성진변형률 (넥킹 개시까지 유효구간). E로 탄성분 제거."""
    en = np.asarray(df["eng_strain"], dtype=float)
    es = np.asarray(df["eng_stress_Pa"], dtype=float)
    finite = np.isfinite(en) & np.isfinite(es)
    conv = true_stress.true_curve_with_necking(en[finite], es[finite])
    et = np.asarray(conv["true_strain"], dtype=float)
    st = np.asarray(conv["true_stress"], dtype=float)
    upto = conv["valid_upto_index"]
    if upto is not None and upto > 2:
        et, st = et[:upto], st[:upto]
    # 소성진변형률 εp = ε_true − σ_true/E. E는 실제 고체 수준(>1 GPa)일 때만 탄성분 제거.
    # (탄성구간 없는 곡선에서 E 회귀가 비물리적으로 작게 나오면 εp가 음수 폭주 →
    #  진변형률을 소성분으로 근사. 대변형에선 탄성분이 무시할 수준이라 타당.)
    if E and np.isfinite(E) and E > 1e9:
        ep = et - st / E
    else:
        ep = et.copy()
    return ep, st


@router.post("/tests/{tid}/fits:compute")
def compute_fits(tid: int, db: Session = Depends(get_db)) -> dict:
    """구성방정식 피팅(Hollomon/Swift/Voce/JC) 산출·영속(교체). PLAN §6.3."""
    _get_test(db, tid)
    pr = (
        db.query(ProcessedResult)
        .filter(ProcessedResult.test_id == tid)
        .one_or_none()
    )
    E = pr.youngs_modulus_pa if pr else None
    df = _load_curve(db, tid)
    ep, st = _plastic_true(df, E)
    results = fitting.fit_all(ep, st)

    # 기존 피팅 교체(재계산 = 덮어쓰기).
    db.query(ConstitutiveFit).filter(ConstitutiveFit.test_id == tid).delete()
    for r in results:
        if r.get("params") is None:
            continue
        db.add(
            ConstitutiveFit(
                test_id=tid,
                model=r["model"],
                params=r["params"],
                r2=r.get("r2"),
                rmse_pa=r.get("rmse_pa"),
                n_points=r.get("n_points"),
            )
        )
    db.commit()
    return {"test_id": tid, "fits": results}


@router.get("/tests/{tid}/fits")
def get_fits(tid: int, db: Session = Depends(get_db)) -> dict:
    _get_test(db, tid)
    rows = (
        db.query(ConstitutiveFit)
        .filter(ConstitutiveFit.test_id == tid)
        .all()
    )
    fits = [
        {
            "model": r.model,
            "params": r.params,
            "r2": r.r2,
            "rmse_pa": r.rmse_pa,
            "n_points": r.n_points,
        }
        for r in rows
    ]
    return {"test_id": tid, "fits": fits}


def _resolve_units(units: str | None):
    """단위계 키 검증. 미지원이면 422."""
    try:
        return get_system(units)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/tests/{tid}/card.k")
def get_card(
    tid: int,
    units: str | None = Query(None, description=f"단위계: {', '.join(SYSTEMS)}"),
    model: str = Query("piecewise", description="piecewise(*MAT_024) | johnson_cook(*MAT_098)"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """LS-DYNA 탄소성 카드 다운로드. model=piecewise(*MAT_024, 기본)·johnson_cook(*MAT_098)."""
    u = _resolve_units(units)
    if model not in ("piecewise", "johnson_cook"):
        raise HTTPException(status_code=422, detail=f"unknown model: {model!r}")
    test = _get_test(db, tid)
    pr = (
        db.query(ProcessedResult)
        .filter(ProcessedResult.test_id == tid)
        .one_or_none()
    )
    E = pr.youngs_modulus_pa if pr else None
    # 유효한 양의 유한 E가 없으면 카드 생성 거부(음수·NaN E는 물리적으로 무효한
    # 솔버 카드를 만들므로 422로 재계산 유도). 탄성구간 없는 곡선 방어.
    if pr is None or E is None or not math.isfinite(E) or E <= 0:
        raise HTTPException(
            status_code=422,
            detail="valid Young's modulus required before card export (recompute properties)",
        )
    df = _load_curve(db, tid)
    ep, st = _plastic_true(df, pr.youngs_modulus_pa)
    label = test.specimen.material.name if test.specimen and test.specimen.material else f"test{tid}"
    gen = lsdyna_mat098_card if model == "johnson_cook" else lsdyna_mat024_card
    text = gen(
        title=label,
        E_pa=pr.youngs_modulus_pa,
        yield_pa=pr.yield_strength_pa,
        plastic_strain=ep,
        true_stress=st,
        units=u,
    )
    tag = "MAT098_JC" if model == "johnson_cook" else "MAT024"
    fname = f"test_{tid}_{tag}_{u.key}.k"
    disposition = f"attachment; filename=\"{fname}\"; filename*=UTF-8''{quote(fname)}"
    return StreamingResponse(
        iter([text]),
        media_type="text/plain",
        headers={"Content-Disposition": disposition},
    )


@router.get("/tests/{tid}/viscocard.k")
def get_viscocard(
    tid: int,
    units: str | None = Query(None, description=f"단위계: {', '.join(SYSTEMS)}"),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """LS-DYNA *MAT_VISCOELASTIC 카드 다운로드(점탄성 완화 Prony 1항, §점탄성)."""
    u = _resolve_units(units)
    test = _get_test(db, tid)
    pr = (
        db.query(ProcessedResult).filter(ProcessedResult.test_id == tid).one_or_none()
    )
    if pr is None or not pr.extra_metrics or pr.extra_metrics.get("kind") != "viscoelastic":
        raise HTTPException(status_code=422, detail="viscoelastic relaxation result required")
    p = pr.extra_metrics.get("lsdyna_prony", {})
    mat = test.specimen.material if test.specimen else None
    rho_t = (mat.attributes or {}).get("prony_lsdyna", {}).get("RHO") if mat else None
    # 저장값은 ton/mm/s(MPa·tonne/mm³·1/s). 카드 함수는 SI 입력 → 여기서 SI로 환산.
    text = viscoelastic.mat_viscoelastic_card(
        title=mat.name if mat else f"test{tid}",
        rho_si=(rho_t or 1.1e-9) * 1.0e12,
        bulk_pa=(p.get("BULK") or 2000.0) * 1.0e6,
        G0_pa=(p.get("G0") or 1.0) * 1.0e6,
        Ginf_pa=(p.get("GI") or 0.1) * 1.0e6,
        beta=p.get("BETA") or 1.0,
        units=u,
    )
    fname = f"test_{tid}_MAT_VISCOELASTIC_{u.key}.k"
    disposition = f"attachment; filename=\"{fname}\"; filename*=UTF-8''{quote(fname)}"
    return StreamingResponse(
        iter([text]), media_type="text/plain",
        headers={"Content-Disposition": disposition},
    )
