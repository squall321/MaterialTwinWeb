# LS-DYNA 일관 단위계 레지스트리 — 내부 SI(Pa·kg/m³·1/s) 값을 목표 단위계로 변환.
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UnitSystem:
    """일관 단위계 하나. 질량·길이·시간 기본단위(SI 대비 배율)로 파생 배율을 유도한다.

    mass_kg / length_m / time_s : 목표 단위 1개가 몇 SI 단위인지(예: tonne=1e3 kg).
    """

    key: str
    label: str
    stress_unit: str
    density_unit: str
    mass_kg: float
    length_m: float
    time_s: float

    @property
    def f_stress(self) -> float:
        """Pa → 목표 응력단위 배율. [stress]=mass/(length·time²)."""
        return self.length_m * self.time_s**2 / self.mass_kg

    @property
    def f_density(self) -> float:
        """kg/m³ → 목표 밀도단위 배율. [density]=mass/length³."""
        return self.length_m**3 / self.mass_kg

    @property
    def f_rate(self) -> float:
        """1/s → 1/목표시간단위 배율(완화속도 β·변형률속도)."""
        return self.time_s


# 자동차 충돌해석 표준 계열. ton_mm_s가 기본(응력 MPa로 일관).
SYSTEMS: dict[str, UnitSystem] = {
    "ton_mm_s": UnitSystem("ton_mm_s", "ton, mm, s", "MPa", "tonne/mm^3", 1.0e3, 1.0e-3, 1.0),
    "kg_m_s": UnitSystem("kg_m_s", "kg, m, s (SI)", "Pa", "kg/m^3", 1.0, 1.0, 1.0),
    "g_mm_ms": UnitSystem("g_mm_ms", "g, mm, ms", "MPa", "g/mm^3", 1.0e-3, 1.0e-3, 1.0e-3),
    "kg_mm_ms": UnitSystem("kg_mm_ms", "kg, mm, ms", "GPa", "kg/mm^3", 1.0, 1.0e-3, 1.0e-3),
}

DEFAULT_SYSTEM = "ton_mm_s"


def get_system(key: str | None) -> UnitSystem:
    """단위계 키 조회. None이면 기본(ton_mm_s). 미지원 키는 ValueError."""
    if key is None:
        return SYSTEMS[DEFAULT_SYSTEM]
    if key not in SYSTEMS:
        raise ValueError(f"unknown unit system: {key!r} (choices: {', '.join(SYSTEMS)})")
    return SYSTEMS[key]
