# MaterialTwin MCP 서버 — 재료 DB·물성·곡선·구성방정식·LS-DYNA 카드 조회 + 물성 등록/수정/삭제 도구.
from __future__ import annotations

import os
import sys
from pathlib import Path

# 어느 cwd에서 실행되든 backend 디렉터리를 import 경로에 넣는다.
_BACKEND = Path(__file__).resolve().parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
# DB/DATA_DIR 기본값(미주입 시 backend/var/data). .mcp.json env가 우선.
os.environ.setdefault("MATERIALTWIN_DATA_DIR", str(_BACKEND / "var" / "data"))
os.environ.setdefault("MATERIALTWIN_DATABASE_URL", f"sqlite:///{_BACKEND / 'var' / 'data' / 'materialtwin.db'}")

import io
import numpy as np
import matplotlib
matplotlib.use("Agg")  # 헤드리스 렌더.
import matplotlib.pyplot as plt
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image
from sqlalchemy import func

from app import analysis, curve_store, fitting, insights, viscoelastic
from app.cards import lsdyna_mat024_card, lsdyna_mat098_card
from app.db import SessionLocal
from app.models import ConstitutiveFit, Material, ProcessedResult, RawCurveRef, Specimen, Test
from app.routers.properties import _plastic_true
from app.unit_systems import get_system

mcp = FastMCP("materialtwin")


def _mpa(v):
    return round(float(v) / 1e6, 2) if isinstance(v, (int, float)) else None


def _gpa(v):
    return round(float(v) / 1e9, 3) if isinstance(v, (int, float)) else None


@mcp.tool()
def list_materials(category: str | None = None, query: str | None = None, limit: int = 50) -> list[dict]:
    """재료 목록을 조회한다. category(metal/polymer/rubber…)와 query(이름·코드 부분일치)로 필터.

    각 항목: id, name, category, mat_type, 대표 E(GPa)·UTS(MPa) 또는 점탄성 E0(MPa).
    """
    with SessionLocal() as s:
        q = s.query(Material)
        if category:
            q = q.filter(Material.category == category)
        if query:
            like = f"%{query}%"
            q = q.filter(Material.name.ilike(like))
        out = []
        for mat in q.order_by(Material.id).limit(limit).all():
            row = {"id": mat.id, "name": mat.name, "category": mat.category,
                   "mat_type": (mat.attributes or {}).get("mat_type")}
            # 대표 test의 물성(유효 시험 우선, 웹과 동일 규칙).
            t = (s.query(Test).join(Specimen).filter(Specimen.material_id == mat.id,
                                                     Test.valid == True)  # noqa: E712
                 .order_by(Test.id).first())
            if t:
                pr = s.query(ProcessedResult).filter_by(test_id=t.id).one_or_none()
                if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
                    row["kind"] = "viscoelastic"
                    row["E0_MPa"] = _mpa(pr.extra_metrics.get("E0_pa"))
                    row["Einf_MPa"] = _mpa(pr.extra_metrics.get("Einf_pa"))
                elif pr:
                    row["kind"] = "elastoplastic"
                    row["E_GPa"] = _gpa(pr.youngs_modulus_pa)
                    row["UTS_MPa"] = _mpa(pr.uts_pa)
                row["test_id"] = t.id
            out.append(row)
        return out


@mcp.tool()
def get_material(material_id: int) -> dict:
    """재료 상세: 메타데이터 + 시편·시험 목록 + 각 시험 물성 요약."""
    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": "not found"}
        specs = []
        for sp in s.query(Specimen).filter_by(material_id=material_id).all():
            tests = []
            for t in s.query(Test).filter_by(specimen_id=sp.id).all():
                pr = s.query(ProcessedResult).filter_by(test_id=t.id).one_or_none()
                info = {"test_id": t.id, "test_type": t.test_type}
                if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
                    info.update(kind="viscoelastic", E0_MPa=_mpa(pr.extra_metrics.get("E0_pa")),
                                Einf_MPa=_mpa(pr.extra_metrics.get("Einf_pa")),
                                tau_s=pr.extra_metrics.get("tau_s"))
                elif pr:
                    info.update(kind="elastoplastic", E_GPa=_gpa(pr.youngs_modulus_pa),
                                yield_MPa=_mpa(pr.yield_strength_pa), UTS_MPa=_mpa(pr.uts_pa),
                                elong_pct=round((pr.fracture_elongation or 0) * 100, 1))
                tests.append(info)
            specs.append({"specimen_id": sp.id, "label": sp.label, "tests": tests})
        return {"id": mat.id, "name": mat.name, "category": mat.category,
                "description": mat.description, "attributes": mat.attributes, "specimens": specs}


@mcp.tool()
def get_curve(test_id: int, kind: str = "nominal", max_points: int = 200) -> dict:
    """시험 곡선 포인트(다운샘플). kind: nominal(공칭 σ-ε)·true(진응력)·relaxation(점탄성 E(t))."""
    with SessionLocal() as s:
        if not s.get(Test, test_id):
            return {"error": "test not found"}
    df = curve_store.read_curve(test_id)
    if kind == "true":
        if "eng_strain" not in df.columns:
            return {"error": "이 시험은 인장 곡선이 없습니다(점탄성은 kind='relaxation' 사용)."}
        en = np.asarray(df["eng_strain"]); es = np.asarray(df["eng_stress_Pa"])
        from app import true_stress
        c = true_stress.true_curve_with_necking(en, es)
        x, y = np.asarray(c["true_strain"]), np.asarray(c["true_stress"])
        xl, yl = "true_strain", "true_stress_Pa"
        neck = c["necking"]
    else:
        cols = {"nominal": ("eng_strain", "eng_stress_Pa"), "relaxation": ("time_s", "relax_modulus_Pa")}
        xl, yl = cols.get(kind, cols["nominal"])
        if xl not in df.columns or yl not in df.columns:
            have = "relaxation" if "time_s" in df.columns else "nominal/true"
            return {"error": f"kind={kind!r} 곡선이 없습니다. 이 시험은 {have} 곡선만 있습니다."}
        x, y = np.asarray(df[xl], dtype=float), np.asarray(df[yl], dtype=float)
        neck = None
    xs, ys = curve_store.lttb_downsample(x[np.isfinite(x)], y[np.isfinite(y)], n_out=max_points)
    return {"kind": kind, "x_label": xl, "y_label": yl, "n": int(xs.size),
            "x": [round(float(v), 6) for v in xs], "y": [round(float(v), 3) for v in ys],
            "necking": neck}


@mcp.tool()
def get_fits(test_id: int) -> list[dict]:
    """구성방정식 피팅 결과(Hollomon/Swift/Voce/Johnson-Cook)와 R²·파라미터."""
    with SessionLocal() as s:
        rows = s.query(ConstitutiveFit).filter_by(test_id=test_id).order_by(ConstitutiveFit.r2.desc()).all()
        return [{"model": r.model, "r2": round(r.r2, 4) if r.r2 else None,
                 "params": r.params, "n_points": r.n_points} for r in rows]


@mcp.tool()
def get_mat_card(test_id: int, units: str = "ton_mm_s", model: str = "piecewise") -> str:
    """LS-DYNA 재료카드 텍스트. 탄소성→*MAT_024(기본)·johnson_cook(*MAT_098), 점탄성→*MAT_VISCOELASTIC.

    units: ton_mm_s(기본)·kg_m_s·g_mm_ms·kg_mm_ms. model: piecewise·johnson_cook(탄소성만).
    """
    try:
        u = get_system(units)
    except ValueError as exc:
        return f"error: {exc}"
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            return "error: test not found"
        pr = s.query(ProcessedResult).filter_by(test_id=test_id).one_or_none()
        if pr is None:
            return "error: no properties"
        mat = test.specimen.material
        if (pr.extra_metrics or {}).get("kind") == "viscoelastic":
            p = pr.extra_metrics.get("lsdyna_prony", {})
            rho_t = (mat.attributes or {}).get("prony_lsdyna", {}).get("RHO") or 1.1e-9
            # GI는 0(완전 완화)이 유효값 — falsy 폴백 금지(None일 때만 기본값).
            gi = p.get("GI")
            return viscoelastic.mat_viscoelastic_card(
                title=mat.name, rho_si=rho_t * 1.0e12,
                bulk_pa=(p.get("BULK") or 2000.0) * 1.0e6, G0_pa=(p.get("G0") or 1.0) * 1.0e6,
                Ginf_pa=(0.1 if gi is None else gi) * 1.0e6, beta=p.get("BETA") or 1.0, units=u)
        if not pr.youngs_modulus_pa or pr.youngs_modulus_pa <= 0:
            return "error: invalid E for card"
        df = curve_store.read_curve(test_id)
        ep, st = _plastic_true(df, pr.youngs_modulus_pa)
        gen = lsdyna_mat098_card if model == "johnson_cook" else lsdyna_mat024_card
        return gen(title=mat.name, E_pa=pr.youngs_modulus_pa,
                   yield_pa=pr.yield_strength_pa, plastic_strain=ep, true_stress=st, units=u)


@mcp.tool()
def search_by_property(prop: str = "UTS_MPa", min_value: float = 0, max_value: float = 1e9,
                       limit: int = 30) -> list[dict]:
    """물성값으로 재료 검색. prop: UTS_MPa·yield_MPa·E_GPa. 범위 내 재료를 값 내림차순 반환."""
    field = {"UTS_MPa": ProcessedResult.uts_pa, "yield_MPa": ProcessedResult.yield_strength_pa,
             "E_GPa": ProcessedResult.youngs_modulus_pa}.get(prop)
    if field is None:
        return [{"error": f"unknown prop {prop}"}]
    scale = 1e6 if "MPa" in prop else 1e9
    with SessionLocal() as s:
        rows = (s.query(Material.name, ProcessedResult)
                .join(Test, Test.id == ProcessedResult.test_id)
                .join(Specimen, Specimen.id == Test.specimen_id)
                .join(Material, Material.id == Specimen.material_id)
                .filter(field.isnot(None), field >= min_value * scale, field <= max_value * scale)
                .order_by(field.desc()).limit(limit).all())
        return [{"name": nm, "test_id": pr.test_id, prop: round(getattr(pr, field.key) / scale, 2)}
                for nm, pr in rows]


@mcp.tool()
def plot_curve(test_id: int, kind: str = "auto") -> Image:
    """시험 곡선을 그래프 이미지(PNG)로 렌더한다.

    kind='auto'면 탄소성은 공칭+진응력 σ-ε(넥킹 마커), 점탄성은 완화 E(t) 로그곡선.
    'nominal'/'true'/'relaxation'으로 강제 지정도 가능.
    """
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            raise ValueError("test not found")
        pr = s.query(ProcessedResult).filter_by(test_id=test_id).one_or_none()
        mat = test.specimen.material
        is_visco = bool(pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic")
        name = mat.name
    df = curve_store.read_curve(test_id)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=120)
    fig.patch.set_facecolor("#0A0E14"); ax.set_facecolor("#070A0F")

    if is_visco or kind == "relaxation":
        t = np.asarray(df["time_s"], dtype=float); E = np.asarray(df["relax_modulus_Pa"], dtype=float) / 1e6
        ax.semilogx(t, E, color="#34D399", lw=2)
        ax.set_xlabel("time  t (s)"); ax.set_ylabel("relaxation modulus  E(t) (MPa)")
        ax.set_title(f"{name} — viscoelastic relaxation", color="#E6EBF2")
        if pr:
            em = pr.extra_metrics
            ax.axhline(em["Einf_pa"] / 1e6, color="#5E6B7D", ls="--", lw=1, label=f"E∞={em['Einf_pa']/1e6:.2f} MPa")
            ax.axhline(em["E0_pa"] / 1e6, color="#56B4E9", ls=":", lw=1, label=f"E₀={em['E0_pa']/1e6:.2f} MPa")
            ax.legend(loc="best", framealpha=0.2)
    else:
        en = np.asarray(df["eng_strain"], dtype=float); es = np.asarray(df["eng_stress_Pa"], dtype=float) / 1e6
        ax.plot(en, es, color="#56B4E9", lw=2, label="engineering σ")
        if kind in ("auto", "true"):
            from app import true_stress
            c = true_stress.true_curve_with_necking(np.asarray(df["eng_strain"]), np.asarray(df["eng_stress_Pa"]))
            ax.plot(c["true_strain"], np.asarray(c["true_stress"]) / 1e6, color="#34D399", lw=1.5, ls="--", label="true σ")
            nk = c["necking"]
            if nk and nk["strain"] is not None:
                ax.plot(nk["strain"], nk["stress"] / 1e6, "^", color="#F0A92C", ms=9,
                        label=f"necking ε_t={nk['strain']:.3f}")
        ax.set_xlabel("strain  ε"); ax.set_ylabel("stress  σ (MPa)")
        E = _gpa(pr.youngs_modulus_pa) if pr else None
        U = _mpa(pr.uts_pa) if pr else None
        ax.set_title(f"{name} — E={E} GPa, UTS={U} MPa", color="#E6EBF2")
        ax.legend(loc="best", framealpha=0.2)

    ax.grid(True, color="#1C2530", lw=0.6)
    for sp in ax.spines.values():
        sp.set_color("#26303D")
    fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return Image(data=buf.getvalue(), format="png")


@mcp.tool()
def database_summary() -> dict:
    """DB 요약: 총 재료 수·카테고리별·시험유형별·피팅 레코드 수."""
    with SessionLocal() as s:
        from collections import Counter
        cats = Counter(x[0] for x in s.query(Material.category).all())
        ttypes = Counter(x[0] for x in s.query(Test.test_type).all())
        return {"materials": s.query(func.count(Material.id)).scalar(),
                "by_category": dict(cats), "tests_by_type": dict(ttypes),
                "constitutive_fits": s.query(func.count(ConstitutiveFit.id)).scalar()}


@mcp.tool()
def material_taxonomy() -> dict:
    """재료 클래스 분류 개요 — 클래스별(스테인리스·알루미늄·티탄…)·계열별·시험유형별 분포."""
    with SessionLocal() as s:
        return insights.overview(s)


@mcp.tool()
def property_distribution() -> dict:
    """물성 분포 통계 — E·UTS·yield·연신율의 범위·평균·중앙·히스토그램."""
    with SessionLocal() as s:
        return insights.property_stats(s)


@mcp.tool()
def coverage_gaps() -> list[dict]:
    """커버리지 갭 — 재료과학 표준 계열 대비 보유/부족/없음(rich/sparse/missing)."""
    with SessionLocal() as s:
        return insights.coverage_gaps(s)["coverage"]


@mcp.tool()
def find_materials_in_property_range(
    E_min_gpa: float = 0, E_max_gpa: float = 1e9,
    uts_min_mpa: float = 0, uts_max_mpa: float = 1e9, limit: int = 30,
) -> list[dict]:
    """Ashby 물성 박스로 재료 검색(AX). E(GPa)·UTS(MPa) 범위에 드는 재료를 반환."""
    with SessionLocal() as s:
        pts = insights.property_space(s)["points"]
    out = [p for p in pts if E_min_gpa <= p["E_gpa"] <= E_max_gpa
           and uts_min_mpa <= p["uts_mpa"] <= uts_max_mpa]
    out.sort(key=lambda p: -p["uts_mpa"])
    return [{"name": p["name"], "id": p["id"], "cls": p["cls"],
             "E_gpa": p["E_gpa"], "uts_mpa": p["uts_mpa"], "test_id": p["test_id"]}
            for p in out[:limit]]


@mcp.tool()
def plot_ashby() -> Image:
    """전체 재료의 Ashby 물성공간(E–UTS 로그-로그, 계열별 색)을 그래프 이미지로 렌더."""
    with SessionLocal() as s:
        pts = insights.property_space(s)["points"]
    fam_color = {"steel": "#56B4E9", "aluminum": "#E69F00", "titanium": "#CC79A7",
                 "magnesium": "#009E73", "nickel": "#F0A92C", "copper": "#D55E00",
                 "refractory": "#8FA1B3", "metal": "#9AA7B8"}
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=120)
    fig.patch.set_facecolor("#0A0E14"); ax.set_facecolor("#070A0F")
    fams = sorted({p["family"] for p in pts})
    for fam in fams:
        fp = [p for p in pts if p["family"] == fam]
        ax.scatter([p["E_gpa"] for p in fp], [p["uts_mpa"] for p in fp],
                   s=[30 + 12 * (p.get("density") or 3) for p in fp],
                   c=fam_color.get(fam, "#9AA7B8"), alpha=0.8, edgecolors="black",
                   linewidths=0.4, label=fam)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Young's modulus  E (GPa)"); ax.set_ylabel("UTS  (MPa)")
    ax.set_title("Ashby material property space  (E–UTS)", color="#E6EBF2")
    ax.legend(loc="lower right", framealpha=0.2, fontsize=8, ncol=2)
    ax.grid(True, which="both", color="#1C2530", lw=0.5)
    for sp in ax.spines.values():
        sp.set_color("#26303D")
    fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return Image(data=buf.getvalue(), format="png")


# ════════════════════════════════════════════════════════════════════════════
# 쓰기 도구 — 재료 등록/시험 등록/수정/삭제. 웹 API와 동일 검증·저장 경로(C2·C4).
# ════════════════════════════════════════════════════════════════════════════

# 시드와 동일한 명목 시편 치수(mm 입력 기본값). 물성은 응력-변형률에서 나오므로 무관.
_DEF_GAUGE_MM, _DEF_WIDTH_MM, _DEF_THICK_MM = 50.0, 12.5, 2.0
_VALID_CATEGORIES = ("metal", "polymer", "rubber", "composite", "ceramic", "foam")


def _next_label(s, material_id: int) -> str:
    """해당 재료의 다음 시편 라벨(S1, S2, …)."""
    n = s.query(func.count(Specimen.id)).filter(Specimen.material_id == material_id).scalar() or 0
    return f"S{n + 1}"


def _validate_arrays(x: list[float], y: list[float], xname: str, yname: str,
                     min_points: int = 20) -> str | None:
    """배열 쌍 공통 검증. 문제 있으면 한국어 사유, 없으면 None."""
    if not isinstance(x, (list, tuple)) or not isinstance(y, (list, tuple)):
        return f"{xname}/{yname}는 숫자 배열이어야 합니다."
    if len(x) != len(y):
        return f"{xname}({len(x)})와 {yname}({len(y)}) 길이가 다릅니다."
    if len(x) < min_points:
        return f"점이 너무 적습니다({len(x)} < {min_points}). 물성 계산에 최소 {min_points}점 필요."
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if not (np.all(np.isfinite(xa)) and np.all(np.isfinite(ya))):
        return "NaN/Inf 값이 포함되어 있습니다."
    return None


@mcp.tool()
def register_material(name: str, category: str = "metal", material_code: str | None = None,
                      description: str | None = None) -> dict:
    """새 재료를 등록한다. category: metal/polymer/rubber/composite/ceramic/foam.

    material_code는 전사 고유코드(중복 시 에러). 등록 후 register_tensile_test 또는
    register_relaxation_test로 시험 데이터를 붙인다.
    """
    name = (name or "").strip()
    if not name or len(name) > 200:
        return {"error": "name은 1~200자 필수입니다."}
    if category not in _VALID_CATEGORIES:
        return {"error": f"category는 {'/'.join(_VALID_CATEGORIES)} 중 하나여야 합니다."}
    from sqlalchemy.exc import IntegrityError
    with SessionLocal() as s:
        mat = Material(name=name, material_code=material_code or None, category=category,
                       description=(description or None),
                       attributes={"source": "mcp"})
        s.add(mat)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return {"error": f"material_code '{material_code}'가 이미 존재합니다."}
        return {"material_id": mat.id, "name": mat.name, "category": mat.category,
                "message": "등록 완료. register_tensile_test/register_relaxation_test로 시험을 추가하세요."}


@mcp.tool()
def register_tensile_test(material_id: int, strain: list[float], stress_mpa: list[float],
                          specimen_label: str | None = None,
                          gauge_length_mm: float = _DEF_GAUGE_MM,
                          width_mm: float = _DEF_WIDTH_MM,
                          thickness_mm: float = _DEF_THICK_MM,
                          strain_source: str = "extensometer") -> dict:
    """인장시험 곡선(공칭 변형률[무차원]·공칭 응력[MPa])을 등록하고 물성·피팅까지 자동 계산.

    시편을 자동 생성(치수 mm)하고 곡선 저장 → E·항복·UTS·연신 계산 →
    Hollomon/Swift/Voce/Johnson-Cook 피팅까지 수행한다. 저항복 재료는 탄성창을 자동 보정.
    """
    err = _validate_arrays(strain, stress_mpa, "strain", "stress_mpa")
    if err:
        return {"error": err}
    if strain_source not in ("extensometer", "crosshead"):
        return {"error": "strain_source는 extensometer 또는 crosshead여야 합니다."}
    en = np.asarray(strain, dtype=float)
    sp_mpa = np.asarray(stress_mpa, dtype=float)
    if float(np.nanmax(sp_mpa)) > 1e5:
        return {"error": "stress_mpa 값이 비정상적으로 큽니다 — MPa 단위인지 확인하세요(Pa 아님)."}
    if not (gauge_length_mm > 0 and width_mm > 0 and thickness_mm > 0):
        return {"error": "시편 치수는 모두 양수(mm)여야 합니다."}
    stress_pa = sp_mpa * 1e6
    L0, W0, T0 = gauge_length_mm * 1e-3, width_mm * 1e-3, thickness_mm * 1e-3
    A0 = W0 * T0

    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": f"material_id {material_id} 없음. register_material 먼저."}
        # 변형률 단위 착오 검사 — 엘라스토머류는 연신 200% 초과가 정상이라 카테고리별 상한.
        strain_cap = {"rubber": 10.0, "foam": 10.0, "polymer": 5.0}.get(mat.category or "", 2.0)
        if float(np.nanmax(en)) > strain_cap:
            return {"error": f"strain 최대값 {np.nanmax(en):.3g} > {strain_cap}"
                             f"({mat.category or 'metal'} 상한) — 무차원 변형률이어야 합니다(% 아님)."}
        spec = Specimen(material_id=material_id, label=specimen_label or _next_label(s, material_id),
                        geometry_type="flat", gauge_length_m=L0, width_m=W0, thickness_m=T0,
                        area0_m2=A0, standard="mcp")
        s.add(spec); s.commit()
        test = Test(specimen_id=spec.id, test_type="tensile", strain_source=strain_source,
                    source_format="mcp", valid=True)
        s.add(test); s.commit()  # test.id 확정(C2).

        # 곡선 저장 — ingest와 동일 6컬럼 고정 스키마, 트랜잭션 밖 원자적 쓰기(C4).
        import pandas as pd
        n = en.size
        df = pd.DataFrame({"time": np.full(n, np.nan), "force_N": stress_pa * A0,
                           "disp_m": en * L0, "extenso_strain": en,
                           "eng_stress_Pa": stress_pa, "eng_strain": en})
        try:
            rel_path = curve_store.write_curve(test.id, df)
        except Exception as exc:
            # 자동 생성한 시편까지 롤백(delete-orphan cascade로 test도 함께 정리).
            s.delete(spec); s.commit()
            return {"error": f"곡선 저장 실패: {exc}"}
        s.add(RawCurveRef(test_id=test.id, storage="parquet_fs", file_path=rel_path,
                          n_points=int(n), channels=["force", "displacement", "strain", "stress"]))

        # 탄성 회귀: 기본창이 성긴 곡선에서 소성점을 물면 r²가 무너진다 —
        # 점차 좁은 창으로 재시도해 r²≥0.995인 첫 결과를 채택(전부 미달이면 최고 r²).
        metrics = None
        best = None
        for e_range in ((0.0005, 0.0025), (0.0002, 0.0015), (0.0001, 0.001)):
            m = analysis.compute_all(en, stress_pa, A0=A0, e_range=e_range, category=mat.category)
            r2 = getattr(m["params"], "r2", None)
            if best is None or ((r2 or 0) > (getattr(best["params"], "r2", None) or 0)):
                best = m
            if m["youngs_modulus_pa"] and r2 is not None and r2 >= 0.995:
                metrics = m
                break
        if metrics is None:
            metrics = best
        pr = ProcessedResult(
            test_id=test.id,
            youngs_modulus_pa=metrics["youngs_modulus_pa"],
            yield_strength_pa=metrics["yield_strength_pa"],
            uts_pa=metrics["uts_pa"],
            uniform_elongation=metrics["uniform_elongation"],
            fracture_elongation=metrics["fracture_elongation"],
            strain_hardening_n=metrics["strain_hardening_n"],
            strength_coeff_k_pa=metrics["strength_coeff_k_pa"],
            params=metrics["params"].model_dump(),
            extra_metrics=metrics["extra_metrics"],
        )
        s.add(pr); s.commit()

        # 저항복 보정: εy=σy/E < 기본창 상한이면 탄성창을 [0.15εy, 0.7εy]로 재계산(seed._fix_modulus).
        warnings = []
        E, sy = pr.youngs_modulus_pa, pr.yield_strength_pa
        if E and sy and np.isfinite(E) and np.isfinite(sy) and E > 0:
            ey = sy / E
            if ey < 0.0036:
                lo, hi = max(1e-4, 0.15 * ey), max(2e-4, 0.7 * ey)
                # 좁은 창에 점이 부족하면(성긴 곡선) 회귀가 무의미 — 보정 생략.
                # 2점 회귀는 R²=1이라 R²로는 못 거르고 점 수로 가드한다.
                n_win = int(np.sum((en >= lo) & (en <= hi)))
                m2 = (analysis.compute_all(en, stress_pa, A0=A0, e_range=(lo, hi), category=mat.category)
                      if n_win >= 5 else {"youngs_modulus_pa": None})
                E2 = m2["youngs_modulus_pa"]
                # 정당한 보정은 1차 추정과 같은 자릿수(0.5~2배) — 벗어나면 성긴 데이터 아티팩트.
                if (E2 and np.isfinite(E2) and abs(E2 - E) / E > 0.005
                        and 0.5 <= E2 / E <= 2.0):
                    pr.youngs_modulus_pa = E2
                    pr.yield_strength_pa = m2["yield_strength_pa"]
                    pr.strain_hardening_n = m2["strain_hardening_n"]
                    pr.strength_coeff_k_pa = m2["strength_coeff_k_pa"]
                    pr.params = m2["params"].model_dump()
                    s.commit()
                    warnings.append("저항복 재료 — 탄성창을 항복변형률 기준으로 자동 보정했습니다.")

        # 구성방정식 피팅.
        fit_summary = []
        if pr.youngs_modulus_pa and pr.youngs_modulus_pa > 0:
            dfc = curve_store.read_curve(test.id)
            ep, st = _plastic_true(dfc, pr.youngs_modulus_pa)
            for r in fitting.fit_all(ep, st):
                if r.get("params") is None:
                    continue
                s.add(ConstitutiveFit(test_id=test.id, model=r["model"], params=r["params"],
                                      r2=r.get("r2"), rmse_pa=r.get("rmse_pa"),
                                      n_points=r.get("n_points")))
                fit_summary.append({"model": r["model"], "r2": round(r["r2"], 4) if r.get("r2") else None})
            s.commit()
        else:
            warnings.append("영률 계산 실패 — 탄성 구간 데이터가 부족합니다. 카드 생성 불가.")

        return {"material_id": material_id, "specimen_id": spec.id, "test_id": test.id,
                "properties": {"E_GPa": _gpa(pr.youngs_modulus_pa), "yield_MPa": _mpa(pr.yield_strength_pa),
                               "UTS_MPa": _mpa(pr.uts_pa),
                               "elong_pct": round((pr.fracture_elongation or 0) * 100, 1)},
                "fits": fit_summary, "warnings": warnings,
                "message": "등록 완료. get_mat_card(test_id)로 LS-DYNA 카드를 뽑을 수 있습니다."}


@mcp.tool()
def register_relaxation_test(material_id: int,
                             G0_mpa: float | None = None, Ginf_mpa: float | None = None,
                             beta_per_s: float | None = None,
                             time_s: list[float] | None = None,
                             modulus_mpa: list[float] | None = None,
                             nu: float = 0.45, bulk_mpa: float | None = None,
                             rho_t_mm3: float | None = None) -> dict:
    """점탄성 완화시험을 등록한다. 두 입력 모드 중 하나를 사용.

    (A) Prony 파라미터: G0_mpa·Ginf_mpa·beta_per_s (LS-DYNA *MAT_VISCOELASTIC 정의,
        G(t)=Ginf+(G0-Ginf)e^{-βt}) — 완화 영률 곡선을 생성해 저장.
    (B) 실측 곡선: time_s[초]·modulus_mpa[완화 영률 E(t), MPa] — Prony 3항 피팅 후 저장.
    등록 후 get_mat_card로 *MAT_VISCOELASTIC 카드를 도출할 수 있다.
    """
    mode_a = all(isinstance(v, (int, float)) for v in (G0_mpa, Ginf_mpa, beta_per_s))
    mode_b = time_s is not None and modulus_mpa is not None
    if not mode_a and not mode_b:
        return {"error": "입력 부족 — (A) G0_mpa·Ginf_mpa·beta_per_s 또는 (B) time_s·modulus_mpa 필요."}
    if mode_a and (G0_mpa <= 0 or Ginf_mpa < 0 or beta_per_s <= 0 or G0_mpa <= Ginf_mpa):
        return {"error": "G0>Ginf≥0, beta>0 이어야 합니다(단위: MPa, 1/s)."}
    if not (0.0 <= nu < 0.5):
        return {"error": "nu(포아송비)는 [0, 0.5) 범위여야 합니다."}

    if mode_a:
        rc = viscoelastic.relaxation_curve_from_lsdyna(G0_mpa, Ginf_mpa, beta_per_s, nu)
        t, E_t = np.asarray(rc["time_s"]), np.asarray(rc["E_pa"])
        E0_pa, Einf_pa, tau_s = rc["E0_pa"], rc["Einf_pa"], rc["tau_s"]
        prony_src = {"G0": G0_mpa, "GI": Ginf_mpa, "BETA": beta_per_s, "BULK": bulk_mpa}
    else:
        err = _validate_arrays(time_s, modulus_mpa, "time_s", "modulus_mpa", min_points=8)
        if err:
            return {"error": err}
        t = np.asarray(time_s, dtype=float)
        E_t = np.asarray(modulus_mpa, dtype=float) * 1e6
        if np.any(t < 0) or np.any(E_t <= 0):
            return {"error": "time_s는 0 이상, modulus_mpa는 양수여야 합니다."}
        order = np.argsort(t)
        t, E_t = t[order], E_t[order]
        E0_pa = float(np.max(E_t))
        Einf_pa = float(np.min(E_t))

    fit = viscoelastic.fit_prony(t[t > 0] if mode_b else t, E_t[t > 0] if mode_b else E_t, n_terms=3)
    if fit.get("reason"):
        return {"error": f"Prony 피팅 실패: {fit['reason']} — 시간 범위·점수를 확인하세요."}

    if mode_b:
        # 곡선 모드: 지배항 τ로 1항 등가 Prony를 유도해 카드 생성 경로를 살린다.
        Einf_pa = float(fit.get("E_inf_pa") or Einf_pa)
        terms = fit.get("terms") or []
        if not terms:
            # 지수항 0개 = 감쇠 없음(증가·평탄 곡선) — 물리적으로 완화시험이 아님.
            return {"error": "완화 거동이 감지되지 않습니다 — 시간에 따라 감소하는 modulus 곡선이 필요합니다."}
        dom = max(terms, key=lambda x: x[0])
        tau_s = float(dom[1])
        if tau_s <= 0:
            return {"error": "유효한 완화시간을 추정할 수 없습니다 — 시간 배열을 확인하세요."}
        g_div = 2.0 * (1.0 + nu)
        prony_src = {"G0": E0_pa / g_div / 1e6, "GI": Einf_pa / g_div / 1e6,
                     "BETA": 1.0 / tau_s, "BULK": bulk_mpa}

    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": f"material_id {material_id} 없음. register_material 먼저."}
        pl = {k: v for k, v in prony_src.items() if v is not None}
        if rho_t_mm3:
            pl["RHO"] = rho_t_mm3

        spec = Specimen(material_id=material_id, label=_next_label(s, material_id),
                        geometry_type="flat", gauge_length_m=_DEF_GAUGE_MM * 1e-3,
                        width_m=_DEF_WIDTH_MM * 1e-3, thickness_m=_DEF_THICK_MM * 1e-3,
                        area0_m2=_DEF_WIDTH_MM * _DEF_THICK_MM * 1e-6, standard="relaxation")
        s.add(spec); s.commit()
        test = Test(specimen_id=spec.id, test_type="relaxation", strain_source="relaxation",
                    source_format="mcp", valid=True)
        s.add(test); s.commit()

        import pandas as pd
        df = pd.DataFrame({"time_s": t, "relax_modulus_Pa": E_t})
        try:
            rel_path = curve_store.write_curve(test.id, df)
        except Exception as exc:
            # 자동 생성한 시편까지 롤백(delete-orphan cascade로 test도 함께 정리).
            s.delete(spec); s.commit()
            return {"error": f"곡선 저장 실패: {exc}"}
        s.add(RawCurveRef(test_id=test.id, storage="parquet_fs", file_path=rel_path,
                          n_points=int(t.size),
                          channels=[{"name": "time_s", "unit_si": "s"},
                                    {"name": "relax_modulus_Pa", "unit_si": "Pa"}]))
        # 카드 생성이 참조하는 attributes.prony_lsdyna 갱신 — 곡선 저장 성공 이후에만
        # 커밋해 실패 시 백킹 시험 없는 Prony 파라미터가 남지 않게 한다.
        attrs = dict(mat.attributes or {})
        attrs["prony_lsdyna"] = {**attrs.get("prony_lsdyna", {}), **pl}
        attrs.setdefault("source", "mcp")
        mat.attributes = attrs
        pr = ProcessedResult(
            test_id=test.id, params={"schema_version": 1, "kind": "viscoelastic"},
            youngs_modulus_pa=E0_pa,
            extra_metrics={"kind": "viscoelastic", "E0_pa": E0_pa, "Einf_pa": Einf_pa,
                           "tau_s": tau_s,
                           "prony_fit": {"E_inf_pa": fit.get("E_inf_pa"), "terms": fit.get("terms"),
                                         "r2": fit.get("r2"), "n_terms": fit.get("n_terms")},
                           "lsdyna_prony": pl},
        )
        s.add(pr); s.commit()
        return {"material_id": material_id, "specimen_id": spec.id, "test_id": test.id,
                "E0_MPa": _mpa(E0_pa), "Einf_MPa": _mpa(Einf_pa), "tau_s": round(tau_s, 6),
                "prony_r2": round(fit["r2"], 4) if fit.get("r2") is not None else None,
                "message": "점탄성 등록 완료. get_mat_card(test_id)로 *MAT_VISCOELASTIC 카드를 뽑을 수 있습니다."}


@mcp.tool()
def update_material(material_id: int, name: str | None = None, category: str | None = None,
                    description: str | None = None, material_code: str | None = None) -> dict:
    """재료 메타데이터를 부분 수정한다(전달한 필드만 갱신)."""
    if category is not None and category not in _VALID_CATEGORIES:
        return {"error": f"category는 {'/'.join(_VALID_CATEGORIES)} 중 하나여야 합니다."}
    from sqlalchemy.exc import IntegrityError
    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": "material not found"}
        if name is not None:
            if not name.strip() or len(name) > 200:
                return {"error": "name은 1~200자여야 합니다."}
            mat.name = name.strip()
        if category is not None:
            mat.category = category
        if description is not None:
            mat.description = description or None
        if material_code is not None:
            mat.material_code = material_code or None
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return {"error": f"material_code '{material_code}'가 이미 존재합니다."}
        return {"material_id": mat.id, "name": mat.name, "category": mat.category,
                "material_code": mat.material_code, "message": "수정 완료."}


@mcp.tool()
def delete_material(material_id: int, confirm: bool = False) -> dict:
    """재료와 하위 시편·시험·곡선을 삭제한다(파괴적 — confirm=True 필요).

    confirm=False면 삭제 대상 미리보기만 반환한다.
    """
    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": "material not found"}
        tids = [t.id for t in s.query(Test).join(Specimen)
                .filter(Specimen.material_id == material_id).all()]
        n_spec = s.query(func.count(Specimen.id)).filter(Specimen.material_id == material_id).scalar()
        if not confirm:
            return {"preview": {"material": mat.name, "specimens": n_spec, "tests": len(tids)},
                    "message": "삭제하려면 confirm=True로 다시 호출하세요."}
        name = mat.name
        s.delete(mat)  # cascade: specimen→test→ref/pr/fit.
        s.commit()
    for tid in tids:  # Parquet 곡선 파일 정리(DB cascade는 파일을 안 지움).
        curve_store.curve_path(tid).unlink(missing_ok=True)
    return {"deleted": name, "tests_removed": len(tids), "message": "삭제 완료."}


@mcp.tool()
def delete_test(test_id: int, confirm: bool = False) -> dict:
    """시험 1건과 곡선·물성·피팅을 삭제한다(파괴적 — confirm=True 필요)."""
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            return {"error": "test not found"}
        mat_name = test.specimen.material.name if test.specimen and test.specimen.material else "?"
        if not confirm:
            return {"preview": {"test_id": test_id, "material": mat_name, "type": test.test_type},
                    "message": "삭제하려면 confirm=True로 다시 호출하세요."}
        s.delete(test)
        s.commit()
    curve_store.curve_path(test_id).unlink(missing_ok=True)
    return {"deleted_test": test_id, "material": mat_name, "message": "삭제 완료."}


@mcp.tool()
def recompute_properties(test_id: int, e_min: float | None = None, e_max: float | None = None) -> dict:
    """인장시험 물성을 재계산한다(탄성 회귀창 e_min~e_max 지정 가능). 피팅도 함께 갱신.

    영률이 이상하게 나온 경우 탄성 구간을 좁혀 재계산할 때 사용한다(변형률 무차원).
    """
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            return {"error": "test not found"}
        pr = s.query(ProcessedResult).filter_by(test_id=test_id).one_or_none()
        if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
            return {"error": "점탄성 시험은 재계산 대상이 아닙니다(완화곡선은 등록 시 피팅됨)."}
        try:
            df = curve_store.read_curve(test_id)
        except FileNotFoundError:
            return {"error": "곡선 파일이 없습니다."}
        if "eng_strain" not in df.columns:
            return {"error": "인장 곡선이 아닙니다."}
        en = np.asarray(df["eng_strain"], dtype=float)
        st_pa = np.asarray(df["eng_stress_Pa"], dtype=float)
        A0 = test.specimen.area0_m2 if test.specimen else None
        cat = test.specimen.material.category if test.specimen and test.specimen.material else None
        if (e_min is None) != (e_max is None):
            return {"error": "e_min과 e_max는 함께 지정해야 합니다(하나만 주면 무시되지 않고 거부)."}
        kwargs = {}
        if e_min is not None and e_max is not None:
            if not (0 <= e_min < e_max):
                return {"error": "0 ≤ e_min < e_max 이어야 합니다."}
            kwargs["e_range"] = (e_min, e_max)
        metrics = analysis.compute_all(en, st_pa, A0=A0, category=cat, **kwargs)
        if pr is None:
            pr = ProcessedResult(test_id=test_id)
            s.add(pr)
        pr.youngs_modulus_pa = metrics["youngs_modulus_pa"]
        pr.yield_strength_pa = metrics["yield_strength_pa"]
        pr.uts_pa = metrics["uts_pa"]
        pr.uniform_elongation = metrics["uniform_elongation"]
        pr.fracture_elongation = metrics["fracture_elongation"]
        pr.strain_hardening_n = metrics["strain_hardening_n"]
        pr.strength_coeff_k_pa = metrics["strength_coeff_k_pa"]
        pr.params = metrics["params"].model_dump()
        pr.extra_metrics = metrics["extra_metrics"]
        s.commit()

        # 피팅 교체(기존 삭제 후 재계산 — 웹 fits:compute와 동일).
        s.query(ConstitutiveFit).filter_by(test_id=test_id).delete()
        fit_summary = []
        if pr.youngs_modulus_pa and pr.youngs_modulus_pa > 0:
            ep, st = _plastic_true(df, pr.youngs_modulus_pa)
            for r in fitting.fit_all(ep, st):
                if r.get("params") is None:
                    continue
                s.add(ConstitutiveFit(test_id=test_id, model=r["model"], params=r["params"],
                                      r2=r.get("r2"), rmse_pa=r.get("rmse_pa"),
                                      n_points=r.get("n_points")))
                fit_summary.append({"model": r["model"], "r2": round(r["r2"], 4) if r.get("r2") else None})
        s.commit()
        return {"test_id": test_id,
                "properties": {"E_GPa": _gpa(pr.youngs_modulus_pa), "yield_MPa": _mpa(pr.yield_strength_pa),
                               "UTS_MPa": _mpa(pr.uts_pa)},
                "e_range_used": (pr.params or {}).get("e_range"),
                "fits": fit_summary, "message": "재계산 완료."}


if __name__ == "__main__":
    mcp.run()
