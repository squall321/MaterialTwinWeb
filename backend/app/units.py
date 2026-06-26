# SI 단위 정규화/표시변환 단일 모듈(파서 원본단위→SI는 여기서만 수행).
from __future__ import annotations

import math

# ── 입력(편의 단위) → SI 정규화 ──────────────────────────────────────────────


def mm_to_m(value: float) -> float:
    return value * 1e-3


def m_to_mm(value: float) -> float:
    return value * 1e3


def kn_to_n(value: float) -> float:
    return value * 1e3


def n_to_kn(value: float) -> float:
    return value * 1e-3


def mpa_to_pa(value: float) -> float:
    return value * 1e6


def pa_to_mpa(value: float) -> float:
    return value * 1e-6


def gpa_to_pa(value: float) -> float:
    return value * 1e9


def pa_to_gpa(value: float) -> float:
    return value * 1e-9


def percent_to_ratio(value: float) -> float:
    return value / 100.0


def ratio_to_percent(value: float) -> float:
    return value * 100.0


def degc_to_k(value: float) -> float:
    return value + 273.15


def k_to_degc(value: float) -> float:
    return value - 273.15


def mm_per_min_to_m_per_s(value: float) -> float:
    return value * 1e-3 / 60.0


def m_per_s_to_mm_per_min(value: float) -> float:
    return value * 1e3 * 60.0


# ── 형상 → 초기 단면적 A0 (SI: m²) ──────────────────────────────────────────


def area_from_geometry(
    geometry_type: str,
    width_m: float | None = None,
    thickness_m: float | None = None,
    diameter_m: float | None = None,
) -> float:
    """형상별 초기 단면적(m²)을 계산한다. 입력은 모두 SI(m).

    flat: width_m * thickness_m, round: π/4 * diameter_m².
    """
    if geometry_type == "flat":
        if width_m is None or thickness_m is None:
            raise ValueError("flat 형상은 width_m, thickness_m 필수.")
        if width_m <= 0 or thickness_m <= 0:
            raise ValueError("width_m, thickness_m 는 양수여야 한다.")
        return width_m * thickness_m
    if geometry_type == "round":
        if diameter_m is None:
            raise ValueError("round 형상은 diameter_m 필수.")
        if diameter_m <= 0:
            raise ValueError("diameter_m 는 양수여야 한다.")
        return math.pi / 4.0 * diameter_m * diameter_m
    raise ValueError(f"알 수 없는 geometry_type: {geometry_type!r}")
