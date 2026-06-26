# 시험 상세/토글/삭제 + 곡선(LTTB·CSV) + 물성 계산/조회 라우터(곡선 소유자는 test).
from __future__ import annotations

import io
from urllib.parse import quote

import numpy as np
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import analysis, curve_store
from app.db import get_db
from app.models import ProcessedResult, RawCurveRef, Test
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


# kind → (x컬럼, y컬럼). nominal=공칭 σ-ε, force_disp=하중-변위.
_KIND_COLUMNS = {
    "nominal": ("eng_strain", "eng_stress_Pa"),
    "force_disp": ("disp_m", "force_N"),
}


@router.get("/tests/{tid}/curve")
def get_curve(
    tid: int,
    kind: str = Query(default="nominal"),
    max_points: int = Query(default=2000, ge=3, le=100000),
    db: Session = Depends(get_db),
) -> dict:
    """곡선 포인트(LTTB 다운샘플). 곡선 소유자는 test([gaps] A3)."""
    _get_test(db, tid)
    if kind not in _KIND_COLUMNS:
        raise HTTPException(status_code=422, detail=f"unknown kind: {kind}")
    df = _load_curve(db, tid)
    xcol, ycol = _KIND_COLUMNS[kind]
    x = np.asarray(df[xcol], dtype=float)
    y = np.asarray(df[ycol], dtype=float)
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
