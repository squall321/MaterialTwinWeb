# 구성방정식 피팅(Hollomon/Swift/Voce/Johnson-Cook, scipy 최소제곱, PLAN §6.3).
from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit


# ── 모델 정의: σ = f(εp; params) ──────────────────────────────────────────────
def _hollomon(ep, K, n):
    return K * np.power(np.clip(ep, 1e-12, None), n)


def _swift(ep, K, eps0, n):
    return K * np.power(np.clip(eps0 + ep, 1e-12, None), n)


def _voce(ep, sigma0, Q, b):
    return sigma0 + Q * (1.0 - np.exp(-b * ep))


# Johnson-Cook의 준정적·상온 항만(변형률·온도항=1): σ = A + B·εp^n.
def _johnson_cook_static(ep, A, B, n):
    return A + B * np.power(np.clip(ep, 1e-12, None), n)


_MODELS = {
    "hollomon": {"fn": _hollomon, "p0": None, "params": ["K_pa", "n"]},
    "swift": {"fn": _swift, "p0": None, "params": ["K_pa", "eps0", "n"]},
    "voce": {"fn": _voce, "p0": None, "params": ["sigma0_pa", "Q_pa", "b"]},
    "johnson_cook": {"fn": _johnson_cook_static, "p0": None, "params": ["A_pa", "B_pa", "n"]},
}

MODEL_NAMES = tuple(_MODELS.keys())


def _initial_guess(model: str, ep: np.ndarray, sigma: np.ndarray) -> list[float]:
    """물리적으로 타당한 초기값(수렴 안정화)."""
    s_max = float(np.max(sigma))
    s_min = float(np.min(sigma))
    if model == "hollomon":
        return [s_max, 0.15]
    if model == "swift":
        return [s_max, 0.005, 0.15]
    if model == "voce":
        return [s_min, max(s_max - s_min, 1.0), 10.0]
    if model == "johnson_cook":
        return [s_min, max(s_max - s_min, 1.0), 0.15]
    return [1.0, 1.0]


def fit_model(model: str, strain_plastic: np.ndarray, stress: np.ndarray) -> dict:
    """소성변형률-진응력 데이터에 한 구성모델을 피팅한다.

    반환: dict(model, params{name:value}, r2, rmse_pa, n_points) 또는 실패 시 reason.
    """
    if model not in _MODELS:
        return {"model": model, "params": None, "reason": "unknown_model"}
    ep = np.asarray(strain_plastic, dtype=float)
    sg = np.asarray(stress, dtype=float)
    m = np.isfinite(ep) & np.isfinite(sg) & (ep >= 0) & (sg > 0)
    ep, sg = ep[m], sg[m]
    spec = _MODELS[model]
    if ep.size < len(spec["params"]) + 1:
        return {"model": model, "params": None, "reason": "too_few_points", "n_points": int(ep.size)}

    p0 = _initial_guess(model, ep, sg)
    try:
        popt, _ = curve_fit(spec["fn"], ep, sg, p0=p0, maxfev=10000)
    except Exception as exc:  # 수렴 실패도 graceful.
        return {"model": model, "params": None, "reason": f"fit_failed:{type(exc).__name__}", "n_points": int(ep.size)}

    y_hat = spec["fn"](ep, *popt)
    ss_res = float(np.sum((sg - y_hat) ** 2))
    ss_tot = float(np.sum((sg - np.mean(sg)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    rmse = float(np.sqrt(ss_res / ep.size))
    return {
        "model": model,
        "params": {name: float(v) for name, v in zip(spec["params"], popt)},
        "r2": r2,
        "rmse_pa": rmse,
        "n_points": int(ep.size),
        "reason": None,
    }


def fit_all(strain_plastic: np.ndarray, stress: np.ndarray) -> list[dict]:
    """등록된 모든 구성모델을 피팅해 리스트 반환(R² 내림차순)."""
    out = [fit_model(m, strain_plastic, stress) for m in MODEL_NAMES]
    out.sort(key=lambda r: (r.get("r2") is not None, r.get("r2") or -1), reverse=True)
    return out


def johnson_cook_card_params(
    strain_plastic: np.ndarray, true_stress: np.ndarray, yield_pa: float
) -> dict:
    """*MAT_098 Simplified J-C 카드용 물리 파라미터(A=항복 고정, B·n 피팅).

    자유 3파라미터 J-C 피팅은 A·B가 상호식별 불가라 A가 음수로 발산하곤 한다.
    카드에는 A=σy(항복)로 고정하고 소성경화 σ-A=B·εp^n 만 적합해 물리값을 낸다.
    반환: {A_pa, B_pa, n, r2} 또는 실패 시 params 대신 reason.
    """
    ep = np.asarray(strain_plastic, dtype=float)
    sg = np.asarray(true_stress, dtype=float)
    A = float(yield_pa)
    m = np.isfinite(ep) & np.isfinite(sg) & (ep > 1e-9) & (sg > A)
    ep, sg = ep[m], sg[m]
    if ep.size < 3:
        return {"reason": "too_few_hardening_points", "n_points": int(ep.size)}
    # log(σ-A) = log B + n·log εp → 선형회귀로 초기값, 이후 비선형 정밀화.
    lx, ly = np.log(ep), np.log(sg - A)
    n0, logB0 = np.polyfit(lx, ly, 1)
    # 초기값을 경계 [B≥1, 0≤n≤1] 안으로 클램프 — 감소·가속 경화나 노이즈로 log-log
    # 기울기가 경계를 벗어나면 curve_fit이 'infeasible'로 즉시 실패해 카드가 조용히
    # 완전소성(B=0)으로 떨어지던 문제 방지.
    B0 = min(max(float(np.exp(logB0)), 1.0), 1e30)
    n0c = min(max(float(n0), 0.0), 1.0)
    try:
        (B, n), _ = curve_fit(
            lambda e, B, n: A + B * np.power(e, n),
            ep, sg, p0=[B0, n0c],
            bounds=([1.0, 0.0], [np.inf, 1.0]), maxfev=10000,
        )
    except Exception as exc:
        return {"reason": f"fit_failed:{type(exc).__name__}", "n_points": int(ep.size)}
    y_hat = A + B * np.power(ep, n)
    ss_res = float(np.sum((sg - y_hat) ** 2))
    ss_tot = float(np.sum((sg - np.mean(sg)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"A_pa": A, "B_pa": float(B), "n": float(n), "r2": r2, "n_points": int(ep.size)}
