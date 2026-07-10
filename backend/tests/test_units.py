# 단위계 전환·Johnson-Cook 카드·점탄성 SI 변환 검증.
from __future__ import annotations

import numpy as np
import pytest

from app.cards import lsdyna_mat024_card, lsdyna_mat098_card
from app.fitting import johnson_cook_card_params
from app.unit_systems import DEFAULT_SYSTEM, get_system
from app.viscoelastic import mat_viscoelastic_card


# ── 단위계 배율 ───────────────────────────────────────────────────────────────
def test_default_is_ton_mm_s():
    assert DEFAULT_SYSTEM == "ton_mm_s"
    assert get_system(None).key == "ton_mm_s"


def test_unknown_system_raises():
    with pytest.raises(ValueError):
        get_system("furlong_firkin_fortnight")


@pytest.mark.parametrize(
    "key,e_pa,exp_stress,exp_density",
    [
        ("ton_mm_s", 2.07e11, 2.07e5, 7.85e-9),   # MPa, tonne/mm^3
        ("kg_m_s", 2.07e11, 2.07e11, 7850.0),     # SI 그대로
        ("g_mm_ms", 2.07e11, 2.07e5, 7.85e-3),    # MPa, g/mm^3
        ("kg_mm_ms", 2.07e11, 207.0, 7.85e-6),    # GPa, kg/mm^3
    ],
)
def test_conversion_factors(key, e_pa, exp_stress, exp_density):
    u = get_system(key)
    assert e_pa * u.f_stress == pytest.approx(exp_stress, rel=1e-9)
    assert 7850.0 * u.f_density == pytest.approx(exp_density, rel=1e-9)


# ── MAT_024 단위계 적용 ───────────────────────────────────────────────────────
def _hardening_curve():
    ep = np.linspace(0.0, 0.12, 15)
    st = 1.168e9 + 6.0e8 * np.power(np.clip(ep, 1e-9, None), 0.15)
    return ep, st


def test_mat024_default_ton_mm_s():
    ep, st = _hardening_curve()
    text = lsdyna_mat024_card("Steel", E_pa=1.96e11, yield_pa=1.168e9,
                              plastic_strain=ep, true_stress=st)
    assert "ton, mm, s" in text
    # E는 MPa 규모(1.96e5), Pa 규모(1e11)가 아니어야.
    assert "1.96e+05" in text
    assert "1.96e+11" not in text


def test_mat024_si_matches_pa():
    ep, st = _hardening_curve()
    text = lsdyna_mat024_card("Steel", E_pa=1.96e11, yield_pa=1.168e9,
                              plastic_strain=ep, true_stress=st, units="kg_m_s")
    assert "kg, m, s" in text
    assert "1.96e+11" in text


# ── MAT_098 Johnson-Cook: A=항복 고정, 물리 파라미터 ──────────────────────────
def test_jc_card_params_are_physical():
    ep, st = _hardening_curve()
    jc = johnson_cook_card_params(ep, st, yield_pa=1.168e9)
    assert jc["A_pa"] == pytest.approx(1.168e9)  # A=항복 고정
    assert jc["B_pa"] > 0                        # B 양수(자유피팅은 음수 발산)
    assert 0.0 < jc["n"] < 1.0                    # 물리적 경화지수
    assert jc["r2"] > 0.9


def test_mat098_card_structure_and_units():
    ep, st = _hardening_curve()
    text = lsdyna_mat098_card("Steel", E_pa=1.96e11, yield_pa=1.168e9,
                              plastic_strain=ep, true_stress=st)
    assert "*MAT_SIMPLIFIED_JOHNSON_COOK" in text
    assert "ton, mm, s" in text
    assert "*END" in text


@pytest.mark.parametrize("kind", ["accelerating", "noisy_weak"])
def test_jc_card_params_non_power_law_hardening(kind):
    # 비멱법칙(가속) 경화·약경화+노이즈에서 초기값 미클램프로 curve_fit이 즉시 실패해
    # 카드가 완전소성(B=0)으로 조용히 떨어지던 결함 회귀.
    A = 300e6
    ep = np.linspace(0.001, 0.15, 80)
    if kind == "accelerating":
        st = A + 5e9 * ep ** 2  # log-log 기울기 ≈ 2 (경계 밖)
    else:
        rng = np.random.default_rng(0)
        st = A + 2e8 * np.power(ep, 0.05) * (1 + 0.01 * rng.standard_normal(ep.size))
    jc = johnson_cook_card_params(ep, st, yield_pa=A)
    assert "reason" not in jc or jc.get("B_pa") is not None  # fit_failed 아님.
    assert jc["B_pa"] > 0  # 경화가 카드에 반영(완전소성 아님).


# ── 점탄성 SI 입력 → 단위계 변환 ─────────────────────────────────────────────
def test_viscoelastic_si_roundtrip_ton_mm_s():
    # SI로 준 값이 ton_mm_s(MPa)에서 원 MPa 값과 일치해야(왕복).
    text = mat_viscoelastic_card("V", rho_si=1.1e-9 * 1e12, bulk_pa=2.5e6,
                                 G0_pa=0.15e6, Ginf_pa=0.015e6, beta=50.0)
    assert "ton, mm, s" in text
    data = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith(("$", "*"))][0]
    vals = data.split()
    assert float(vals[2]) == pytest.approx(2.5, rel=1e-6)     # bulk MPa
    assert float(vals[3]) == pytest.approx(0.15, rel=1e-6)    # g0 MPa
    assert float(vals[5]) == pytest.approx(50.0, rel=1e-6)    # beta 1/s


def test_viscoelastic_si_system_is_pa():
    text = mat_viscoelastic_card("V", rho_si=1.1e-9 * 1e12, bulk_pa=2.5e6,
                                 G0_pa=0.15e6, Ginf_pa=0.015e6, beta=50.0, units="kg_m_s")
    data = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith(("$", "*"))][0]
    vals = data.split()
    assert float(vals[2]) == pytest.approx(2.5e6, rel=1e-6)   # bulk Pa
