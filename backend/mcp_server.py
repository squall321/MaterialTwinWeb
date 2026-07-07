# MaterialTwin MCP 서버 — 재료 DB·물성·곡선·구성방정식·LS-DYNA 카드를 MCP 도구로 노출(읽기전용).
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

from app import curve_store, insights, viscoelastic
from app.cards import lsdyna_mat024_card
from app.db import SessionLocal
from app.models import ConstitutiveFit, Material, ProcessedResult, Specimen, Test
from app.routers.properties import _plastic_true

mcp = FastMCP("materialtwin")


def _mpa(v):
    return round(v / 1e6, 2) if isinstance(v, (int, float)) else None


def _gpa(v):
    return round(v / 1e9, 3) if isinstance(v, (int, float)) else None


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
            # 대표 test의 물성.
            t = (s.query(Test).join(Specimen).filter(Specimen.material_id == mat.id).first())
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
        en = np.asarray(df["eng_strain"]); es = np.asarray(df["eng_stress_Pa"])
        conv = viscoelastic  # noqa - placeholder to avoid unused import warnings
        from app import true_stress
        c = true_stress.true_curve_with_necking(en, es)
        x, y = np.asarray(c["true_strain"]), np.asarray(c["true_stress"])
        xl, yl = "true_strain", "true_stress_Pa"
        neck = c["necking"]
    else:
        cols = {"nominal": ("eng_strain", "eng_stress_Pa"), "relaxation": ("time_s", "relax_modulus_Pa")}
        xl, yl = cols.get(kind, cols["nominal"])
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
def get_mat_card(test_id: int) -> str:
    """LS-DYNA 재료카드 텍스트. 탄소성→*MAT_024, 점탄성→*MAT_VISCOELASTIC."""
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
            return viscoelastic.mat_viscoelastic_card(
                title=mat.name, rho=1.1e-9, bulk_mpa=p.get("BULK") or 2000.0,
                G0_mpa=p.get("G0") or 1.0, Ginf_mpa=p.get("GI") or 0.1, beta=p.get("BETA") or 1.0)
        if not pr.youngs_modulus_pa or pr.youngs_modulus_pa <= 0:
            return "error: invalid E for card"
        df = curve_store.read_curve(test_id)
        ep, st = _plastic_true(df, pr.youngs_modulus_pa)
        return lsdyna_mat024_card(title=mat.name, E_pa=pr.youngs_modulus_pa,
                                  yield_pa=pr.yield_strength_pa, plastic_strain=ep, true_stress=st)


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


if __name__ == "__main__":
    mcp.run()
