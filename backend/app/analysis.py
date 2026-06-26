# 인장 σ-ε 곡선에서 재료 물성을 산출하는 순수 numpy 함수 모듈(scipy 불요, PLAN §6.1).
from __future__ import annotations

from typing import Literal

import numpy as np

from .schemas import ProcessingParams


# ── R² → confidence 등급(거부 아님 — C1) ──────────────────────────────────────
def _confidence(r2: float) -> Literal["high", "ok", "low"]:
    if r2 >= 0.999:
        return "high"
    if r2 >= 0.99:
        return "ok"
    return "low"


def _r2(y: np.ndarray, y_hat: np.ndarray) -> float:
    """결정계수. 분산 0이면 0.0 반환(0除 방지)."""
    ss_res = float(np.sum((y - y_hat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    if ss_tot <= 0.0:
        return 0.0
    return 1.0 - ss_res / ss_tot


# ── 영률 E ────────────────────────────────────────────────────────────────────
def youngs_modulus(
    strain: np.ndarray,
    stress: np.ndarray,
    e_range: tuple[float, float] = (0.0005, 0.0025),
    toe_correct: bool = True,
    category: str | None = None,
) -> dict:
    """탄성구간 σ-ε 선형회귀로 영률(Pa)을 산출한다.

    절편 포함 polyfit deg=1(원점강제 금지). R²는 confidence 등급으로만 환산하고
    값은 항상 반환한다(C1). category=='polymer'면 secant modulus 분기.
    반환: dict(E_pa, r2, confidence, e_range_used, n_points, method).
    """
    strain = np.asarray(strain, dtype=float)
    stress = np.asarray(stress, dtype=float)
    lo, hi = e_range

    # ── 폴리머 분기: secant modulus(할선 = (σ_hi-σ_lo)/(ε_hi-ε_lo)) ──
    if category == "polymer":
        s_lo = float(np.interp(lo, strain, stress))
        s_hi = float(np.interp(hi, strain, stress))
        E = (s_hi - s_lo) / (hi - lo) if hi > lo else float("nan")
        return {
            "E_pa": E,
            "r2": float("nan"),  # secant은 회귀 아님
            "confidence": "low",  # 폴리머는 선형구간 부재 → 항상 경고
            "e_range_used": (lo, hi),
            "n_points": 2,
            "method": "secant",
        }

    # ── toe(발끝) 보정: 선형구간 직선을 ε축 외삽해 절편 ε0 제거 ──
    e_used = strain
    if toe_correct:
        m0 = (lo <= strain) & (strain <= hi)
        if int(np.count_nonzero(m0)) >= 2:
            sl, ic = np.polyfit(strain[m0], stress[m0], 1)
            if sl > 0:
                eps0 = -ic / sl  # σ=0 인 ε절편
                e_used = strain - eps0

    mask = (e_used >= lo) & (e_used <= hi)
    n = int(np.count_nonzero(mask))
    if n < 2:
        # 구간에 점이 부족해도 전체 양의구간 폴백으로 값은 항상 반환(C1)
        mask = stress > 0
        n = int(np.count_nonzero(mask))
    if n < 2:
        return {
            "E_pa": float("nan"),
            "r2": 0.0,
            "confidence": "low",
            "e_range_used": (lo, hi),
            "n_points": n,
            "method": "polyfit_deg1",
        }

    slope, intercept = np.polyfit(e_used[mask], stress[mask], 1)
    y_hat = slope * e_used[mask] + intercept
    r2 = _r2(stress[mask], y_hat)
    return {
        "E_pa": float(slope),
        "r2": r2,
        "confidence": _confidence(r2),
        "e_range_used": (lo, hi),
        "n_points": n,
        "method": "polyfit_deg1",
    }


# ── 0.2% offset 항복 Rp0.2 ───────────────────────────────────────────────────
def yield_strength_offset(
    strain: np.ndarray,
    stress: np.ndarray,
    E: float,
    offset: float = 0.002,
) -> dict:
    """offset 직선 σ=E·(ε−offset)과 곡선의 첫 안정 교점(Pa).

    부호변화(곡선−직선: +→−) 지점을 선형보간. 교점 없으면 value=None+reason.
    """
    strain = np.asarray(strain, dtype=float)
    stress = np.asarray(stress, dtype=float)
    if E is None or not np.isfinite(E) or E <= 0:
        return {"value": None, "reason": "E_invalid"}

    line = E * (strain - offset)
    diff = stress - line  # 곡선이 직선 위면 +, 아래면 −
    # 첫 부호변화(+ → −): 곡선이 offset 직선을 아래로 가로지름
    sign = np.sign(diff)
    for i in range(1, len(diff)):
        if sign[i - 1] > 0 and sign[i] <= 0:
            # 선형보간: diff=0 교점에서의 stress
            d0, d1 = diff[i - 1], diff[i]
            t = d0 / (d0 - d1) if (d0 - d1) != 0 else 0.0
            sy = stress[i - 1] + t * (stress[i] - stress[i - 1])
            return {"value": float(sy), "reason": None}
    return {"value": None, "reason": "no_intersection_brittle"}


# ── UTS(Rm) ──────────────────────────────────────────────────────────────────
def uts(stress: np.ndarray, trim_tail: bool = False, tail_frac: float = 0.05) -> dict:
    """최대 공칭응력(Pa). trim_tail이면 끝단 tail_frac을 노이즈로 제외."""
    stress = np.asarray(stress, dtype=float)
    s = stress
    if trim_tail and len(stress) > 20:
        cut = int(len(stress) * (1.0 - tail_frac))
        s = stress[:cut]
    idx = int(np.argmax(s))
    return {"value": float(s[idx]), "index": idx}


# ── 연신율(균일 Ag, 파단 A) ───────────────────────────────────────────────────
def elongation(strain: np.ndarray, stress: np.ndarray) -> dict:
    """uniform=UTS 시점 변형률, fracture=마지막점 또는 force −90% 급락 검출점."""
    strain = np.asarray(strain, dtype=float)
    stress = np.asarray(stress, dtype=float)
    u_idx = int(np.argmax(stress))
    uniform = float(strain[u_idx])

    # 파단 검출: UTS 이후 max 대비 10% 이하로 급락한 첫 지점
    peak = stress[u_idx]
    frac_idx = len(strain) - 1
    fracture_detected = False
    if peak > 0:
        for i in range(u_idx + 1, len(stress)):
            if stress[i] <= 0.1 * peak:
                frac_idx = i
                fracture_detected = True
                break
    fracture = float(strain[frac_idx])
    return {
        "uniform": uniform,
        "fracture": fracture,
        "fracture_detected": fracture_detected,
    }


# ── Hollomon n, K ────────────────────────────────────────────────────────────
def hollomon_n_k(strain_plastic: np.ndarray, stress: np.ndarray) -> dict:
    """log-log 선형회귀로 가공경화지수 n, 강도계수 K(Pa). σ=K·εp^n.

    양수 ε_p, σ 만 사용. 점이 부족하면 n=K=None.
    """
    ep = np.asarray(strain_plastic, dtype=float)
    s = np.asarray(stress, dtype=float)
    m = (ep > 0) & (s > 0)
    if int(np.count_nonzero(m)) < 2:
        return {"n": None, "K_pa": None, "n_points": int(np.count_nonzero(m))}
    n, lnK = np.polyfit(np.log(ep[m]), np.log(s[m]), 1)
    return {"n": float(n), "K_pa": float(np.exp(lnK)), "n_points": int(np.count_nonzero(m))}


# ── 전체 산출 ─────────────────────────────────────────────────────────────────
def compute_all(
    strain: np.ndarray,
    stress: np.ndarray,
    A0: float | None = None,
    e_range: tuple[float, float] = (0.0005, 0.0025),
    offset: float = 0.002,
    toe_correct: bool = True,
    category: str | None = None,
) -> dict:
    """모든 물성을 산출하고 ProcessingParams를 채워 dict로 반환한다.

    반환 키: youngs_modulus_pa, yield_strength_pa, uts_pa, uniform_elongation,
    fracture_elongation, strain_hardening_n, strength_coeff_k_pa, params(ProcessingParams).
    """
    strain = np.asarray(strain, dtype=float)
    stress = np.asarray(stress, dtype=float)

    ym = youngs_modulus(strain, stress, e_range=e_range, toe_correct=toe_correct, category=category)
    E = ym["E_pa"]

    ys = yield_strength_offset(strain, stress, E, offset=offset)
    rm = uts(stress)
    el = elongation(strain, stress)

    # 소성변형률 εp = ε − σ/E (E 유효할 때만 Hollomon)
    if E is not None and np.isfinite(E) and E > 0:
        ep = strain - stress / E
        nk = hollomon_n_k(ep, stress)
    else:
        nk = {"n": None, "K_pa": None, "n_points": 0}

    params = ProcessingParams(
        e_range=tuple(ym["e_range_used"]),
        offset=offset,
        toe=toe_correct,
        r2=ym["r2"] if np.isfinite(ym["r2"]) else 0.0,
        confidence=ym["confidence"],
        n_points=ym["n_points"],
    )

    return {
        "youngs_modulus_pa": E if np.isfinite(E) else None,
        "yield_strength_pa": ys["value"],
        "uts_pa": rm["value"],
        "uniform_elongation": el["uniform"],
        "fracture_elongation": el["fracture"],
        "strain_hardening_n": nk["n"],
        "strength_coeff_k_pa": nk["K_pa"],
        "params": params,
        "extra_metrics": {
            "yield_reason": ys["reason"],
            "ym_method": ym["method"],
            "fracture_detected": el["fracture_detected"],
        },
    }
