# 스칼라 물성(E·항복·UTS·연신율) → σ-ε 곡선 합성. 실측 곡선이 없는 재료용(항상 '합성'으로 표시).
from __future__ import annotations

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_compare import representative_numeric
from app.models import PropertyValue

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
    # 항복강도가 없는 경우. 연신율로 연성/취성을 가른다 —
    # 동박·솔더처럼 항복을 공표하지 않는 연성 금속을 취성으로 취급하면 곡선이 통째로 틀린다.
    if sigy is None:
        if uts is None:
            return None
        ef = elong if elong and elong > 0 else uts / E
        ductile = ef > 0.02                  # 파단연신율 2% 초과면 소성 구간이 있다고 본다
        if ductile:
            ey = uts / E
            e = np.concatenate([np.linspace(0.0, ey, 12), np.linspace(ey, ef, max(8, n_points - 12))])
            s = np.concatenate([E * np.linspace(0.0, ey, 12), np.full(max(8, n_points - 12), uts)])
            return {"strain": e, "stress_pa": s, "kind": KIND_SYNTHETIC,
                    "model": "elastic-perfectly plastic (yield unknown, capped at UTS)",
                    "note": "항복강도 미공표 — UTS를 소성 평탄부로 둔 보수적 근사. "
                            "실제 항복은 이보다 낮으므로 소성 개시를 과대평가한다."}
        e = np.linspace(0.0, ef, max(8, n_points // 3))
        s = np.minimum(E * e, uts)          # UTS에서 파단(그 위로 올라가지 않음)
        return {"strain": e, "stress_pa": s, "kind": KIND_SYNTHETIC, "model": "linear-elastic (brittle)",
                "note": "취성 재료 — 항복 없이 탄성 파단. 파단점까지 선형."}
    # 항복이 인장강도보다 크면 두 값이 서로 다른 출처·제품에서 왔다는 뜻이다.
    inconsistent = uts is not None and uts <= sigy
    # 연성: 탄성 + 멱경화.
    ey = sigy / E
    if uts is None or uts <= sigy or not elong or elong <= ey:
        # 완전소성(경화 정보 없음).
        ef = max(elong or ey * 10, ey * 2)
        e = np.concatenate([np.linspace(0, ey, 12), np.linspace(ey, ef, n_points - 12)])
        s = np.concatenate([E * np.linspace(0, ey, 12), np.full(n_points - 12, sigy)])
        note = "UTS/연신율 정보 부족 — 완전소성 근사."
        if inconsistent:
            note = (f"⚠ 항복({sigy/1e6:.0f} MPa)이 인장강도({uts/1e6:.0f} MPa)보다 커서 "
                    "두 값의 출처·조건이 다르다. 항복만 써서 완전소성으로 근사했다.")
        return {"strain": e, "stress_pa": s, "kind": KIND_SYNTHETIC, "model": "elastic-perfectly plastic",
                "note": note, "inconsistent": inconsistent}
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


def _consistent_yield_uts(db: Session, material_id: int,
                          sigy: float | None, uts: float | None) -> tuple[float | None, float | None, str | None]:
    """항복 ≤ 인장이 되도록 정합한 조합을 고른다.

    대표값은 물성마다 독립으로 뽑히므로 YS와 UTS가 서로 다른 출처·제품·두께에서 올 수 있고,
    그러면 물리적으로 불가능한 YS>UTS가 나온다. 이때는 신뢰등급이 더 좋은 쪽을 남기고
    반대쪽을 같은 재료의 다른 후보로 바꿔 정합을 회복한다.
    """
    if sigy is None or uts is None or sigy <= uts:
        return sigy, uts, None
    rows = {}
    for key in (K_SIGY, K_UTS):
        rows[key] = db.execute(
            select(PropertyValue.value_num, PropertyValue.quality_tier)
            .where(PropertyValue.material_id == material_id,
                   PropertyValue.property_key == key,
                   PropertyValue.value_num.is_not(None))
            .order_by(PropertyValue.quality_tier)
        ).all()
    best = None
    for ys, ty in rows[K_SIGY]:
        for ut, tu in rows[K_UTS]:
            if ys <= ut:
                score = (ty + tu, ty, tu)
                if best is None or score < best[0]:
                    best = (score, ys, ut)
    if best is None:
        return sigy, None, "항복이 인장강도보다 커서(출처 불일치) 인장강도를 빼고 합성했다."
    _, ys, ut = best
    if (ys, ut) != (sigy, uts):
        return ys, ut, (f"대표값 조합이 물리적으로 모순(항복 {sigy/1e6:.0f} > 인장 {uts/1e6:.0f} MPa)이라, "
                        f"정합한 조합(항복 {ys/1e6:.0f} / 인장 {ut/1e6:.0f} MPa)으로 바꿔 합성했다.")
    return ys, ut, None


def synth_for_material(db: Session, material_id: int, n_points: int = 60) -> dict | None:
    """재료의 대표 스칼라로 σ-ε 곡선 합성. 스칼라 부족 시 None."""
    reps = representative_numeric(db, list(SCALAR_KEYS))
    def v(k):
        return reps.get(k, {}).get(material_id)
    sigy, uts, fixnote = _consistent_yield_uts(db, material_id, v(K_SIGY), v(K_UTS))
    out = synthesize(v(K_E), sigy, uts, v(K_ELONG), n_points=n_points)
    if out is not None and fixnote:
        out["note"] = f"{fixnote} {out.get('note') or ''}".strip()
        out["inconsistent"] = True
    if out is not None:
        out["inputs"] = {"E_pa": v(K_E), "yield_pa": sigy,
                         "uts_pa": uts, "elongation": v(K_ELONG)}
        srcs = scalar_sources(db, material_id)
        out["sources"] = srcs
        out["provenance"] = provenance_line(srcs)
    return out
