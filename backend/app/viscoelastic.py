# 점탄성 분석(Prony/일반화 Maxwell) — 완화계수 곡선·Prony 피팅·MAT_VISCOELASTIC 카드.
# 완화탄성률 E(t) = E_inf + Σ E_i·exp(-t/τ_i). LS-DYNA는 전단 G 기준(G0,GI,BETA).
from __future__ import annotations

import numpy as np
from scipy.optimize import curve_fit


def shear_relaxation(G0: float, Ginf: float, beta: float, t: np.ndarray) -> np.ndarray:
    """1항 Prony 전단 완화계수 G(t)=Ginf+(G0-Ginf)·exp(-beta·t) (LS-DYNA MAT_VISCOELASTIC)."""
    t = np.asarray(t, dtype=float)
    return Ginf + (G0 - Ginf) * np.exp(-beta * t)


def youngs_from_shear(G: np.ndarray | float, nu: float) -> np.ndarray | float:
    """전단탄성률→영률 E=2G(1+ν). 점탄성 완화에서 ν는 근사적으로 상수 가정."""
    return 2.0 * np.asarray(G, dtype=float) * (1.0 + nu)


def prony_series(t: np.ndarray, E_inf: float, terms: list[tuple[float, float]]) -> np.ndarray:
    """일반화 Maxwell: E(t)=E_inf+Σ E_i·exp(-t/τ_i). terms=[(E_i, τ_i), ...]."""
    t = np.asarray(t, dtype=float)
    out = np.full_like(t, E_inf, dtype=float)
    for Ei, tau in terms:
        out = out + Ei * np.exp(-t / tau)
    return out


def relaxation_curve_from_lsdyna(
    G0: float, Ginf: float, beta: float, nu: float,
    decades: tuple[float, float] = (-4, 3), n: int = 200,
) -> dict:
    """LS-DYNA 1항 Prony(G0,Ginf,beta) → 로그 시간축 완화 영률 곡선 E(t).

    beta[1/s]의 특성시간 τ=1/beta를 중심으로 로그 스팬. 반환 SI: time[s], E[Pa].
    """
    tau = 1.0 / beta if beta > 0 else 1.0
    t = np.logspace(np.log10(tau) + decades[0], np.log10(tau) + decades[1], n)
    G = shear_relaxation(G0, Ginf, beta, t)
    E = youngs_from_shear(G, nu)
    # MPa→Pa (DB 단위계 t/mm/s/K → MPa).
    return {"time_s": t, "E_pa": E * 1e6, "tau_s": tau, "E0_pa": youngs_from_shear(G0, nu) * 1e6,
            "Einf_pa": youngs_from_shear(Ginf, nu) * 1e6}


def fit_prony(time_s: np.ndarray, E_pa: np.ndarray, n_terms: int = 3) -> dict:
    """완화곡선 E(t)에 n항 Prony 급수를 피팅한다(τ는 로그 등분 고정, E_i만 최소제곱).

    비선형 τ 탐색 대신 시간범위에 로그 등분한 고정 τ 그리드에서 선형 최소제곱(NNLS 유사)로
    안정적으로 적합한다. 반환: E_inf, terms[(E_i,τ_i)], r2, rmse_pa.
    """
    t = np.asarray(time_s, dtype=float)
    E = np.asarray(E_pa, dtype=float)
    m = np.isfinite(t) & np.isfinite(E) & (t > 0)
    t, E = t[m], E[m]
    if t.size < n_terms + 2:
        return {"E_inf_pa": None, "terms": [], "reason": "too_few_points"}

    # 고정 τ 그리드(로그 등분).
    taus = np.logspace(np.log10(t.min()), np.log10(t.max()), n_terms)
    # 설계행렬 A[:,0]=1(E_inf), A[:,j]=exp(-t/τ_j).
    A = np.column_stack([np.ones_like(t)] + [np.exp(-t / tau) for tau in taus])
    # 비음수 최소제곱(모듈러스는 양수).
    try:
        from scipy.optimize import nnls
        coef, _ = nnls(A, E)
    except Exception:
        coef, *_ = np.linalg.lstsq(A, E, rcond=None)
        coef = np.clip(coef, 0, None)
    E_inf = float(coef[0])
    terms = [(float(coef[j + 1]), float(taus[j])) for j in range(n_terms) if coef[j + 1] > 0]

    E_hat = prony_series(t, E_inf, terms)
    ss_res = float(np.sum((E - E_hat) ** 2))
    ss_tot = float(np.sum((E - np.mean(E)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    rmse = float(np.sqrt(ss_res / t.size))
    return {
        "E_inf_pa": E_inf,
        "terms": terms,
        "r2": r2,
        "rmse_pa": rmse,
        "n_terms": len(terms),
        "E0_pa": float(E_inf + sum(Ei for Ei, _ in terms)),
        "reason": None,
    }


def mat_viscoelastic_card(
    title: str, rho_si: float, bulk_pa: float, G0_pa: float, Ginf_pa: float, beta: float,
    mid: int = 1, units: "UnitSystem | str | None" = None,
) -> str:
    """LS-DYNA *MAT_VISCOELASTIC 카드(1항 Prony). 입력 SI(Pa·kg/m³·1/s), units로 변환.

    기본 단위계 ton, mm, s → MPa. G(t)=Ginf+(G0-Ginf)·exp(-beta·t).
    """
    from app.unit_systems import UnitSystem, get_system

    u = units if isinstance(units, UnitSystem) else get_system(units)
    fs = u.f_stress
    lines = [
        "$ MaterialTwinWeb — LS-DYNA *MAT_VISCOELASTIC 자동 생성",
        f"$ material: {title}",
        f"$ 단위계: {u.label} → 응력 {u.stress_unit}, 밀도 {u.density_unit}. "
        "G(t)=Ginf+(G0-Ginf)·exp(-beta·t)",
        "*MAT_VISCOELASTIC",
        "$#     mid       rho      bulk        g0        gi      beta",
        f"{mid:>10}{rho_si * u.f_density:>10.4g}{bulk_pa * fs:>10.4g}"
        f"{G0_pa * fs:>10.4g}{Ginf_pa * fs:>10.4g}{beta * u.f_rate:>10.4g}",
        "*END",
    ]
    return "\n".join(lines) + "\n"
