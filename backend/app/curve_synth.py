# 스칼라 물성(E·항복·UTS·연신율) → σ-ε 곡선 합성. 실측 곡선이 없는 재료용(항상 '합성'으로 표시).
from __future__ import annotations

import numpy as np
from sqlalchemy.orm import Session

from app.catalog_compare import representative_numeric

K_E = "mechanical.youngs_modulus"
K_SIGY = "mechanical.yield_strength"
K_UTS = "mechanical.tensile_strength"
K_ELONG = "mechanical.elongation_at_break"
SCALAR_KEYS = (K_E, K_SIGY, K_UTS, K_ELONG)

# 곡선 출처 구분 — 그래프·카드에서 반드시 표기한다.
KIND_MEASURED = "measured"     # 실제 인장시험 곡선
KIND_SYNTHETIC = "synthetic"   # 스칼라에서 합성


def synthesize(E: float, sigy: float | None, uts: float | None,
               elong: float | None, n_points: int = 60) -> dict | None:
    """스칼라 → 공칭 σ-ε 곡선.

    연성(항복 있음): 탄성직선 → Hollomon 멱경화(σ=K·εp^n)로 UTS·연신율을 통과.
    취성(항복 없음): 파단까지 선형(E) — 세라믹·유리·열경화성 수지.
    반환 {strain, stress_pa, kind, model, note} 또는 입력 부족 시 None.
    """
    if not E or E <= 0:
        return None
    # 취성: 항복이 정의되지 않음 → 파단까지 탄성.
    if sigy is None:
        if uts is None:
            return None
        ef = elong if elong and elong > 0 else uts / E
        e = np.linspace(0.0, ef, max(8, n_points // 3))
        s = np.minimum(E * e, uts)          # UTS에서 파단(그 위로 올라가지 않음)
        return {"strain": e, "stress_pa": s, "kind": KIND_SYNTHETIC, "model": "linear-elastic (brittle)",
                "note": "취성 재료 — 항복 없이 탄성 파단. 파단점까지 선형."}
    # 연성: 탄성 + 멱경화.
    ey = sigy / E
    if uts is None or uts <= sigy or not elong or elong <= ey:
        # 완전소성(경화 정보 없음).
        ef = max(elong or ey * 10, ey * 2)
        e = np.concatenate([np.linspace(0, ey, 12), np.linspace(ey, ef, n_points - 12)])
        s = np.concatenate([E * np.linspace(0, ey, 12), np.full(n_points - 12, sigy)])
        return {"strain": e, "stress_pa": s, "kind": KIND_SYNTHETIC, "model": "elastic-perfectly plastic",
                "note": "UTS/연신율 정보 부족 — 완전소성 근사."}
    ep_f = elong - ey                        # 파단 시 소성변형률
    # Hollomon: σ = K εp^n. (εp_f, uts)와 (εp→0+, sigy)를 잇도록 n을 로그비로 결정.
    eps0 = 1e-4
    n_h = np.log(uts / sigy) / np.log(ep_f / eps0)
    n_h = float(np.clip(n_h, 0.01, 0.6))
    K = uts / (ep_f ** n_h)
    e_el = np.linspace(0.0, ey, 12)
    ep = np.linspace(eps0, ep_f, n_points - 12)
    s_pl = np.maximum(K * ep ** n_h, sigy)
    e = np.concatenate([e_el, ey + ep])
    s = np.concatenate([E * e_el, s_pl])
    return {"strain": e, "stress_pa": s, "kind": KIND_SYNTHETIC,
            "model": f"elastic + Hollomon hardening (n={n_h:.3f})",
            "note": "항복·UTS·연신율 스칼라에서 합성한 근사 곡선(실측 아님)."}


def scalar_sources(db: Session, material_id: int) -> dict:
    """합성에 쓰인 스칼라들의 출처(업체·DOI·제목) — 그래프에 표기용."""
    from sqlalchemy import select

    from app.models import PropertyValue

    out: dict[str, str] = {}
    for pv in db.execute(select(PropertyValue).where(
            PropertyValue.material_id == material_id,
            PropertyValue.property_key.in_(SCALAR_KEYS),
            PropertyValue.value_num.isnot(None))).scalars().all():
        src = pv.source
        if src is None:
            continue
        tag = src.publisher or src.title or ""
        if src.doi:
            tag = f"{tag} (DOI {src.doi})" if tag else f"DOI {src.doi}"
        out.setdefault(pv.property_key, tag)
    return out


def provenance_line(sources: dict) -> str:
    """출처들을 한 줄로 압축 — 같은 출처면 하나로 묶는다."""
    uniq: list[str] = []
    for t in sources.values():
        t = (t or "").strip()
        if t and t not in uniq:
            uniq.append(t)
    if not uniq:
        return "출처 미상"
    line = " · ".join(u[:44] for u in uniq[:2])
    return line + (f" 외 {len(uniq) - 2}건" if len(uniq) > 2 else "")


def synth_for_material(db: Session, material_id: int, n_points: int = 60) -> dict | None:
    """재료의 대표 스칼라로 σ-ε 곡선 합성. 스칼라 부족 시 None."""
    reps = representative_numeric(db, list(SCALAR_KEYS))
    def v(k):
        return reps.get(k, {}).get(material_id)
    out = synthesize(v(K_E), v(K_SIGY), v(K_UTS), v(K_ELONG), n_points=n_points)
    if out is not None:
        out["inputs"] = {"E_pa": v(K_E), "yield_pa": v(K_SIGY),
                         "uts_pa": v(K_UTS), "elongation": v(K_ELONG)}
        srcs = scalar_sources(db, material_id)
        out["sources"] = srcs
        out["provenance"] = provenance_line(srcs)
    return out
