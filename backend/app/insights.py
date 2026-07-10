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


def classify(name: str, category: str | None) -> tuple[str, str]:
    """(클래스 표시명, 계열) 반환. 미분류는 (기타-카테고리, category). category=None 안전."""
    nm = name or ""
    cat = category or "unclassified"
    table = _METAL_CLASSES if cat == "metal" else _POLYMER_CLASSES
    for label, family, pat in table:
        if pat.search(nm):
            return label, family
    return (f"Other {cat.title()}", cat)


# ── 재료별 대표 물성 추출(대표 test) ──────────────────────────────────────────
def _material_rows(session: Session) -> list[dict]:
    """재료마다 클래스 + 대표 물성(E/UTS/yield/density/kind)을 모은다.

    단일 outerjoin 쿼리 후 재료별 최소 test.id를 선택(대표 test = 유효 시험 중 id 최소,
    웹 상세와 동일 규칙). 재료당 2쿼리 N+1을 제거 — 대시보드 5엔드포인트 선형 악화 방지.
    """
    from sqlalchemy import and_

    q = (
        session.query(Material, Test, ProcessedResult)
        .outerjoin(Specimen, Specimen.material_id == Material.id)
        .outerjoin(Test, and_(Test.specimen_id == Specimen.id, Test.valid == True))  # noqa: E712
        .outerjoin(ProcessedResult, ProcessedResult.test_id == Test.id)
        .order_by(Material.id, Test.id)
    )
    # 재료별 첫 유효 test 행(정렬 덕에 처음 만나는 non-null t가 최소 id).
    picked: dict[int, tuple] = {}
    for mat, t, pr in q.all():
        cur = picked.get(mat.id)
        if cur is None or (cur[1] is None and t is not None):
            picked[mat.id] = (mat, t, pr)

    rows = []
    for mat, t, pr in picked.values():
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
    rows.sort(key=lambda r: r["id"])
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
    """Ashby 물성공간 산점: 재료별 (E, UTS, 밀도, 비물성, 클래스). 탄소성만(강도 정의)."""
    pts = []
    for r in _material_rows(session):
        if r.get("kind") == "elastoplastic" and r.get("E_gpa") and r.get("uts_mpa"):
            rho = r.get("density_g_cm3")
            pts.append({"name": r["name"], "id": r["id"], "cls": r["cls"], "family": r["family"],
                        "E_gpa": r["E_gpa"], "uts_mpa": r["uts_mpa"], "yield_mpa": r.get("yield_mpa"),
                        "density": rho, "elong_pct": r.get("elong_pct"),
                        # 비강도 σ/ρ [kN·m/kg], 비강성 E/ρ [MN·m/kg]. ρ 없으면 None.
                        "spec_strength": round(r["uts_mpa"] / rho, 1) if rho else None,
                        "spec_stiffness": round(r["E_gpa"] / rho, 2) if rho else None,
                        "test_id": r["test_id"]})
    return {"points": pts, "families": sorted({p["family"] for p in pts})}


def _box(vals: np.ndarray) -> dict | None:
    """박스플롯 5수치 + 평균·n. 빈 배열이면 None."""
    v = vals[np.isfinite(vals)]
    if v.size == 0:
        return None
    q1, med, q3 = (float(x) for x in np.percentile(v, [25, 50, 75]))
    return {"min": round(float(v.min()), 2), "q1": round(q1, 2), "median": round(med, 2),
            "q3": round(q3, 2), "max": round(float(v.max()), 2),
            "mean": round(float(v.mean()), 2), "n": int(v.size)}


# 계열 표시명·정렬(금속 먼저, 강성 큰 순 경향).
_FAMILY_ORDER = ["steel", "nickel", "titanium", "copper", "aluminum", "magnesium",
                 "refractory", "metal"]
_FAMILY_LABEL = {"steel": "강", "nickel": "니켈합금", "titanium": "티탄", "copper": "동합금",
                 "aluminum": "알루미늄", "magnesium": "마그네슘", "refractory": "내화금속",
                 "metal": "기타 금속"}


def family_stats(session: Session) -> dict:
    """재료 계열별 물성 분포(박스플롯) + 비강도·비강성 + 자동 인사이트.

    이것이 '그룹 간 차이'의 핵심: E(log 권장)·UTS·밀도·비강도·비강성을 계열마다 5수치로.
    """
    rows = [r for r in _material_rows(session)
            if r.get("kind") == "elastoplastic" and r.get("E_gpa") and r.get("uts_mpa")]
    by_fam: dict[str, list] = defaultdict(list)
    for r in rows:
        by_fam[r["family"]].append(r)

    metrics = [
        ("E_gpa", "탄성계수 E", "GPa"),
        ("uts_mpa", "인장강도 UTS", "MPa"),
        ("density_g_cm3", "밀도 ρ", "g/cm³"),
        ("spec_strength", "비강도 σ/ρ", "kN·m/kg"),
        ("spec_stiffness", "비강성 E/ρ", "MN·m/kg"),
    ]

    def spec_str(r):
        rho = r.get("density_g_cm3")
        return r["uts_mpa"] / rho if rho else np.nan

    def spec_stf(r):
        rho = r.get("density_g_cm3")
        return r["E_gpa"] / rho if rho else np.nan

    getter = {"E_gpa": lambda r: r.get("E_gpa"), "uts_mpa": lambda r: r.get("uts_mpa"),
              "density_g_cm3": lambda r: r.get("density_g_cm3"),
              "spec_strength": spec_str, "spec_stiffness": spec_stf}

    fams = [f for f in _FAMILY_ORDER if f in by_fam] + \
           [f for f in by_fam if f not in _FAMILY_ORDER]
    out_metrics = []
    for key, label, unit in metrics:
        boxes = []
        for fam in fams:
            vals = np.array([getter[key](r) for r in by_fam[fam]], dtype=float)
            b = _box(vals)
            if b:
                boxes.append({"family": fam, "label": _FAMILY_LABEL.get(fam, fam), **b})
        # E는 범위가 크므로 log축 권장 플래그(최대/최소 비 > 20).
        allv = np.array([getter[key](r) for r in rows], dtype=float)
        allv = allv[np.isfinite(allv) & (allv > 0)]
        log_scale = bool(allv.size and allv.max() / allv.min() > 20)
        out_metrics.append({"key": key, "label": label, "unit": unit,
                            "log_scale": log_scale, "boxes": boxes})

    # 자동 인사이트: 각 비물성/강도의 선두 계열.
    insights_txt = _auto_insights(by_fam, getter)
    return {"families": [{"key": f, "label": _FAMILY_LABEL.get(f, f), "n": len(by_fam[f])} for f in fams],
            "metrics": out_metrics, "insights": insights_txt}


def _auto_insights(by_fam, getter) -> list[dict]:
    """계열별 중앙값 비교로 '가장 ~한 재료군' 문장을 생성."""
    def median_of(fam, key):
        vals = np.array([getter[key](r) for r in by_fam[fam]], dtype=float)
        vals = vals[np.isfinite(vals)]
        return float(np.median(vals)) if vals.size else None

    txt = []
    checks = [
        ("spec_strength", "비강도(경량 대비 강도)", "kN·m/kg", True, "경량 고강도 설계에 유리"),
        ("spec_stiffness", "비강성(경량 대비 강성)", "MN·m/kg", True, "강성-경량 설계에 유리"),
        ("uts_mpa", "절대 인장강도", "MPa", True, "고하중 구조에 유리"),
        ("density_g_cm3", "밀도(가벼움)", "g/cm³", False, "경량화에 유리"),
        ("E_gpa", "탄성계수(강성)", "GPa", True, "변형 저항이 큼"),
    ]
    for key, metric_ko, unit, want_max, why in checks:
        # 그룹 인사이트는 n>=2 계열만 비교(단일 재료의 왜곡·grab-bag 제외).
        ranked = [(fam, median_of(fam, key)) for fam in by_fam
                  if len(by_fam[fam]) >= 2 and fam != "metal"]
        ranked = [(f, v) for f, v in ranked if v is not None]
        if len(ranked) < 2:
            continue
        ranked.sort(key=lambda x: x[1], reverse=want_max)
        lead_fam, lead_val = ranked[0]
        txt.append({"metric": metric_ko, "unit": unit, "leader": _FAMILY_LABEL.get(lead_fam, lead_fam),
                    "value": round(lead_val, 2), "why": why,
                    "runner_up": _FAMILY_LABEL.get(ranked[1][0], ranked[1][0])})
    return txt


def property_stats(session: Session) -> dict:
    """물성 분포 통계: E·UTS·yield·연신율의 평균/중앙/범위 + 히스토그램 빈."""
    all_rows = _material_rows(session)  # 1회만 조회해 탄소성·점탄성 필터 재사용.
    rows = [r for r in all_rows if r.get("kind") == "elastoplastic"]
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
    v = [r for r in all_rows if r.get("kind") == "viscoelastic" and r.get("E_gpa")]
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
