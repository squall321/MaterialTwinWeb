# 재료 DB 인사이트 — 클래스 분류·물성 통계·Ashby 물성공간·taxonomy 지식그래프·커버리지 갭.
from __future__ import annotations

import re
from collections import defaultdict

import numpy as np
from sqlalchemy.orm import Session

from app.models import Material, ProcessedResult, Specimen, Test

# ── 재료 클래스 분류(이름·카테고리·mat_type 패턴) ─────────────────────────────
# 각 클래스: (표시명, 계열, 정규식). 위에서부터 첫 매치.
_METAL_CLASSES: list[tuple[str, str, re.Pattern]] = [
    ("Stainless Steel", "steel", re.compile(r"\b(SUS|STS|17-4PH|stainless)", re.I)),
    ("Carbon/Alloy Steel", "steel", re.compile(r"(SPCC|SCM|S45C|carbon|alloy_steel|mild)", re.I)),
    ("Aluminum Alloy", "aluminum", re.compile(r"\b(AL\d|Al\d|ADC\d|alumin)", re.I)),
    ("Titanium Alloy", "titanium", re.compile(r"(Ti\d|Ti_|Ti6Al|Ti3Al|titanium|Grade[1-9])", re.I)),
    ("Magnesium Alloy", "magnesium", re.compile(r"(Mg_|AZ\d|ZK\d|magnes)", re.I)),
    ("Nickel Superalloy", "nickel", re.compile(r"(Inconel|Ni_|nickel|superalloy)", re.I)),
    ("Copper Alloy", "copper", re.compile(r"(C\d{5}|brass|bronze|CU\b|copper|phosphor)", re.I)),
    ("Refractory Metal", "refractory", re.compile(r"(Tungsten|W_|Mo_|Ta_|refractory)", re.I)),
]
_POLYMER_CLASSES: list[tuple[str, str, re.Pattern]] = [
    ("Elastomer/Rubber", "elastomer", re.compile(r"(rubber|NBR|EPDM|silicone|butyl|SIS)", re.I)),
    ("Foam", "foam", re.compile(r"(foam|PORON|cushion)", re.I)),
    ("Adhesive Tape", "adhesive", re.compile(r"(tape|OCA|PSA|VHB|adhesive|bond)", re.I)),
    ("Damping Polymer", "damping", re.compile(r"(damp|isodamp|EAR|isolator|vibration)", re.I)),
    ("Thermal Interface", "thermal", re.compile(r"(thermal|TIM|interface pad)", re.I)),
]


def classify(name: str, category: str) -> tuple[str, str]:
    """(클래스 표시명, 계열) 반환. 미분류는 (기타-카테고리, category)."""
    nm = name or ""
    table = _METAL_CLASSES if category == "metal" else _POLYMER_CLASSES
    for label, family, pat in table:
        if pat.search(nm):
            return label, family
    return (f"Other {category.title()}", category)


# ── 재료별 대표 물성 추출(대표 test) ──────────────────────────────────────────
def _material_rows(session: Session) -> list[dict]:
    """재료마다 클래스 + 대표 물성(E/UTS/yield/density/kind)을 모은다."""
    rows = []
    for mat in session.query(Material).all():
        t = (session.query(Test).join(Specimen)
             .filter(Specimen.material_id == mat.id).first())
        pr = (session.query(ProcessedResult).filter_by(test_id=t.id).one_or_none()
              if t else None)
        cls, family = classify(mat.name, mat.category)
        attrs = mat.attributes or {}
        row = {"id": mat.id, "name": mat.name, "category": mat.category,
               "cls": cls, "family": family, "test_id": t.id if t else None,
               "density_g_cm3": attrs.get("rho_g_cm3")}
        if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
            row.update(kind="viscoelastic", E_gpa=_g(pr.extra_metrics.get("E0_pa")),
                       einf_mpa=_m(pr.extra_metrics.get("Einf_pa")))
        elif pr:
            row.update(kind="elastoplastic", E_gpa=_g(pr.youngs_modulus_pa),
                       uts_mpa=_m(pr.uts_pa), yield_mpa=_m(pr.yield_strength_pa),
                       elong_pct=round((pr.fracture_elongation or 0) * 100, 1) if pr.fracture_elongation else None)
        rows.append(row)
    return rows


def _g(pa):
    return round(pa / 1e9, 2) if isinstance(pa, (int, float)) else None


def _m(pa):
    return round(pa / 1e6, 1) if isinstance(pa, (int, float)) else None


# ── 인사이트 집계 ─────────────────────────────────────────────────────────────
def overview(session: Session) -> dict:
    """대시보드 헤드라인: 총계·카테고리·클래스별 분포·시험유형."""
    rows = _material_rows(session)
    by_cat = defaultdict(int)
    by_cls = defaultdict(int)
    by_family = defaultdict(int)
    kinds = defaultdict(int)
    for r in rows:
        by_cat[r["category"]] += 1
        by_cls[r["cls"]] += 1
        by_family[r["family"]] += 1
        if r.get("kind"):
            kinds[r["kind"]] += 1
    n_fit = session.query(ProcessedResult).count()
    return {
        "total_materials": len(rows),
        "total_analyzed": n_fit,
        "by_category": dict(sorted(by_cat.items(), key=lambda x: -x[1])),
        "by_class": dict(sorted(by_cls.items(), key=lambda x: -x[1])),
        "by_family": dict(by_family),
        "by_kind": dict(kinds),
    }


def property_space(session: Session) -> dict:
    """Ashby 물성공간 산점: 재료별 (E, UTS, 밀도, 클래스). 탄소성만(강도 정의)."""
    pts = []
    for r in _material_rows(session):
        if r.get("kind") == "elastoplastic" and r.get("E_gpa") and r.get("uts_mpa"):
            pts.append({"name": r["name"], "id": r["id"], "cls": r["cls"], "family": r["family"],
                        "E_gpa": r["E_gpa"], "uts_mpa": r["uts_mpa"], "yield_mpa": r.get("yield_mpa"),
                        "density": r.get("density_g_cm3"), "elong_pct": r.get("elong_pct"),
                        "test_id": r["test_id"]})
    return {"points": pts, "families": sorted({p["family"] for p in pts})}


def property_stats(session: Session) -> dict:
    """물성 분포 통계: E·UTS·yield·연신율의 평균/중앙/범위 + 히스토그램 빈."""
    rows = [r for r in _material_rows(session) if r.get("kind") == "elastoplastic"]
    out = {}
    for key, unit in [("E_gpa", "GPa"), ("uts_mpa", "MPa"), ("yield_mpa", "MPa"), ("elong_pct", "%")]:
        vals = np.array([r[key] for r in rows if r.get(key) is not None], dtype=float)
        if vals.size == 0:
            out[key] = None
            continue
        hist, edges = np.histogram(vals, bins=12)
        out[key] = {"unit": unit, "n": int(vals.size),
                    "min": round(float(vals.min()), 1), "max": round(float(vals.max()), 1),
                    "mean": round(float(vals.mean()), 1), "median": round(float(np.median(vals)), 1),
                    "hist": [int(h) for h in hist],
                    "edges": [round(float(e), 1) for e in edges]}
    # 점탄성 E0 분포도 별도.
    v = [r for r in _material_rows(session) if r.get("kind") == "viscoelastic" and r.get("E_gpa")]
    out["viscoelastic_count"] = len(v)
    return out


# 재료과학이 통상 다루는 계열(커버리지 기준선). 있으면 present, 없으면 gap.
_EXPECTED_FAMILIES = {
    "metal": ["steel", "aluminum", "titanium", "magnesium", "nickel", "copper", "refractory"],
    "polymer": ["elastomer", "foam", "adhesive", "damping", "thermal"],
    "other": ["composite", "ceramic", "glass"],
}


def coverage_gaps(session: Session) -> dict:
    """taxonomy 커버리지: 기대 계열 대비 보유/부족. 지식그래프 노드·엣지 포함."""
    rows = _material_rows(session)
    fam_count = defaultdict(int)
    cls_by_family = defaultdict(set)
    for r in rows:
        fam_count[r["family"]] += 1
        cls_by_family[r["family"]].add(r["cls"])

    coverage = []
    for group, fams in _EXPECTED_FAMILIES.items():
        for fam in fams:
            n = fam_count.get(fam, 0)
            coverage.append({"group": group, "family": fam, "count": n,
                             "status": "rich" if n >= 5 else "sparse" if n >= 1 else "missing"})

    # 지식그래프: root → category → family → (샘플 재료). 노드/엣지.
    nodes = [{"id": "root", "label": "Material DB", "type": "root", "value": len(rows)}]
    edges = []
    cats = defaultdict(int)
    for r in rows:
        cats[r["category"]] += 1
    for cat, n in cats.items():
        cid = f"cat:{cat}"
        nodes.append({"id": cid, "label": cat, "type": "category", "value": n})
        edges.append({"source": "root", "target": cid})
    fam_cat = {}
    for r in rows:
        fam_cat[r["family"]] = r["category"]
    for fam, n in fam_count.items():
        fid = f"fam:{fam}"
        nodes.append({"id": fid, "label": fam, "type": "family", "value": n})
        edges.append({"source": f"cat:{fam_cat[fam]}", "target": fid})

    return {"coverage": coverage, "graph": {"nodes": nodes, "edges": edges}}
