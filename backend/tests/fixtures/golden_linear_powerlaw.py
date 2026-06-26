# 알려진 E·K·n으로 해석적 σ-ε 곡선과 정답 물성을 생성하는 골든 픽스처(C3).
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GoldenCurve:
    """해석적으로 생성한 σ-ε 곡선과 그 정답 물성(SI: ε 무차원, σ Pa)."""

    strain: np.ndarray
    stress: np.ndarray
    E_true_pa: float       # 영률 정답
    rp02_true_pa: float    # 0.2% offset 항복 정답
    uts_true_pa: float     # 인장강도 정답
    K_pa: float            # Hollomon 강도계수
    n: float               # 가공경화지수


def make_golden(
    E: float = 200e9,        # 강철 영률 200 GPa
    sigma_y: float = 350e6,  # 항복응력(탄성↔소성 경계)
    K: float = 700e6,        # Hollomon 강도계수 σ=K·εp^n
    n: float = 0.15,         # 가공경화지수
    eps_max: float = 0.20,   # 곡선 끝 변형률
    n_points: int = 8000,
    noise_pa: float = 0.0,
    seed: int = 0,
) -> GoldenCurve:
    """piecewise 모델로 σ-ε 곡선 생성.

    탄성: σ=E·ε (ε≤ε_y),  소성: σ=K·εp^n (εp=ε−σ/E, ε>ε_y).
    경계 ε_y=σ_y/E. 소성구간은 ε에서 σ를 뉴턴법으로 역산(σ=K·(ε−σ/E)^n).
    정답: E는 탄성기울기, UTS는 곡선 끝 응력. Rp0.2는 offset 직선과의 교점을
    동일 생성함수로 수치 산출(테스트 정답과 알고리즘 정답이 같은 곡선서 나옴).
    """
    eps_y = sigma_y / E
    eps = np.linspace(0.0, eps_max, n_points)
    sigma = np.empty_like(eps)

    elastic = eps <= eps_y
    sigma[elastic] = E * eps[elastic]

    # 소성: σ = K·(ε − σ/E)^n  를 σ에 대해 뉴턴법으로 푼다.
    pl = ~elastic
    e_pl = eps[pl]
    s = np.full_like(e_pl, sigma_y)  # 초기값
    for _ in range(60):
        ep = e_pl - s / E
        ep = np.clip(ep, 1e-12, None)
        f = K * ep ** n - s
        df = K * n * ep ** (n - 1) * (-1.0 / E) - 1.0
        s = s - f / df
    sigma[pl] = s

    stress = sigma.copy()
    if noise_pa > 0.0:
        rng = np.random.default_rng(seed)
        stress = stress + rng.normal(0.0, noise_pa, size=stress.shape)

    # Rp0.2: offset 직선 σ=E·(ε−0.002)과 (노이즈 없는) 곡선의 교점을 수치 산출
    rp02 = _true_rp02(eps, sigma, E)
    uts_true = float(np.max(sigma))

    return GoldenCurve(
        strain=eps,
        stress=stress,
        E_true_pa=E,
        rp02_true_pa=rp02,
        uts_true_pa=uts_true,
        K_pa=K,
        n=n,
    )


def _true_rp02(eps: np.ndarray, sigma: np.ndarray, E: float) -> float:
    """무노이즈 곡선과 offset(0.002) 직선의 첫 교점 응력(정답값)."""
    line = E * (eps - 0.002)
    diff = sigma - line
    for i in range(1, len(diff)):
        if diff[i - 1] > 0 and diff[i] <= 0:
            d0, d1 = diff[i - 1], diff[i]
            t = d0 / (d0 - d1)
            return float(sigma[i - 1] + t * (sigma[i] - sigma[i - 1]))
    return float("nan")


def make_polymer_noisy(
    E: float = 2e9,          # 폴리머 ~2 GPa
    sigma_max: float = 40e6,
    n_points: int = 2000,
    noise_pa: float = 3e6,   # 큰 노이즈
    seed: int = 7,
) -> GoldenCurve:
    """선형구간이 불명확하고 노이즈가 큰 폴리머류 입력(C1 회귀 테스트용).

    완만한 거듭제곱 경화 + 큰 노이즈로 R²가 낮아지도록 구성.
    """
    eps = np.linspace(0.0, 0.05, n_points)
    sigma = sigma_max * (1.0 - np.exp(-E / sigma_max * eps))
    rng = np.random.default_rng(seed)
    stress = sigma + rng.normal(0.0, noise_pa, size=sigma.shape)
    return GoldenCurve(
        strain=eps,
        stress=stress,
        E_true_pa=E,
        rp02_true_pa=float("nan"),
        uts_true_pa=float(np.max(sigma)),
        K_pa=float("nan"),
        n=float("nan"),
    )
