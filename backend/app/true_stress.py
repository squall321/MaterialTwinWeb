# 진응력-진변형률 변환 + Considère 넥킹점 산출(PLAN §6.2, numpy만). 넥킹 전 유효.
from __future__ import annotations

import numpy as np


def to_true(eng_strain: np.ndarray, eng_stress: np.ndarray) -> dict:
    """공칭 → 진응력/진변형률 변환. 넥킹 전 체적일정 가정에서 유효.

    ε_true = ln(1+ε_nom),  σ_true = σ_nom·(1+ε_nom).
    반환: dict(true_strain, true_stress). 입력의 유한·(1+ε)>0 구간만 사용.
    """
    en = np.asarray(eng_strain, dtype=float)
    es = np.asarray(eng_stress, dtype=float)
    m = np.isfinite(en) & np.isfinite(es) & ((1.0 + en) > 0)
    et = np.log1p(en[m])
    st = es[m] * (1.0 + en[m])
    return {"true_strain": et, "true_stress": st}


def considere_necking(true_strain: np.ndarray, true_stress: np.ndarray) -> dict:
    """Considère 넥킹 개시점: dσ_true/dε_true = σ_true 를 처음 만족(교차)하는 지점.

    가공경화율이 진응력 아래로 떨어지는 첫 교차를 선형보간으로 찾는다.
    반환: dict(strain, stress, index) 또는 넥킹 미검출 시 값 None + reason.
    """
    et = np.asarray(true_strain, dtype=float)
    st = np.asarray(true_stress, dtype=float)
    if et.size < 3:
        return {"strain": None, "stress": None, "index": None, "reason": "too_few_points"}

    # 가공경화율 dσ/dε (중앙차분 → np.gradient).
    dsde = np.gradient(st, et)
    g = dsde - st  # >0: 경화율>응력(안정), <=0: 넥킹 개시
    # 첫 부호변화(+ → −)를 처음부터 찾는다. 초기 2%는 gradient 경계·항복 전이
    # 노이즈를 피해 스킵(안정구간 g>0에서 시작하도록).
    start = max(1, int(et.size * 0.02))
    for i in range(start, et.size):
        if g[i - 1] > 0 and g[i] <= 0:
            g0, g1 = g[i - 1], g[i]
            t = g0 / (g0 - g1) if (g0 - g1) != 0 else 0.0
            strain = float(et[i - 1] + t * (et[i] - et[i - 1]))
            stress = float(st[i - 1] + t * (st[i] - st[i - 1]))
            return {"strain": strain, "stress": stress, "index": i, "reason": None}
    return {"strain": None, "stress": None, "index": None, "reason": "no_necking_onset"}


def true_curve_with_necking(eng_strain: np.ndarray, eng_stress: np.ndarray) -> dict:
    """공칭 곡선 → 진곡선 + 넥킹점. UI kind=true 곡선/마커용 한 방에 반환.

    진곡선은 넥킹 개시까지만 물리적으로 유효하므로 valid_upto_index를 함께 준다.
    """
    conv = to_true(eng_strain, eng_stress)
    et, st = conv["true_strain"], conv["true_stress"]
    neck = considere_necking(et, st)
    return {
        "true_strain": et,
        "true_stress": st,
        "necking": neck,
        "valid_upto_index": neck["index"],
    }
