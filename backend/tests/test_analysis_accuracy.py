# 골든 픽스처로 분석 정확도를 검증하는 게이트 테스트(C3·C1, pytest).
from __future__ import annotations

import numpy as np

from app import analysis
from tests.fixtures.golden_linear_powerlaw import make_golden, make_polymer_noisy


def test_youngs_modulus_within_2pct():
    g = make_golden()
    res = analysis.youngs_modulus(g.strain, g.stress)
    assert res["E_pa"] is not None
    rel = abs(res["E_pa"] - g.E_true_pa) / g.E_true_pa
    assert rel <= 0.02, f"E 상대오차 {rel:.4%} > 2% (E={res['E_pa']:.3e})"
    # 깨끗한 곡선이므로 신뢰도 high
    assert res["confidence"] == "high"


def test_yield_strength_within_2mpa():
    g = make_golden()
    E = analysis.youngs_modulus(g.strain, g.stress)["E_pa"]
    ys = analysis.yield_strength_offset(g.strain, g.stress, E)
    assert ys["value"] is not None, f"항복 교점 미검출: {ys['reason']}"
    diff_mpa = abs(ys["value"] - g.rp02_true_pa) / 1e6
    assert diff_mpa <= 2.0, f"Rp0.2 오차 {diff_mpa:.3f} MPa > 2 MPa"


def test_uts_within_half_pct():
    g = make_golden()
    rm = analysis.uts(g.stress)
    rel = abs(rm["value"] - g.uts_true_pa) / g.uts_true_pa
    assert rel <= 0.005, f"UTS 상대오차 {rel:.4%} > 0.5%"


def test_compute_all_consistency():
    g = make_golden()
    out = analysis.compute_all(g.strain, g.stress)
    assert out["youngs_modulus_pa"] is not None
    assert out["yield_strength_pa"] is not None
    assert out["uts_pa"] is not None
    # ProcessingParams가 직렬화 가능해야 함
    assert out["params"].confidence in ("high", "ok", "low")
    assert out["params"].n_points >= 2


def test_polymer_noisy_returns_value_low_confidence():
    """C1 회귀: 노이즈 큰 폴리머 입력에서도 E가 None이 아니라 값+confidence='low'."""
    g = make_polymer_noisy()
    res = analysis.youngs_modulus(g.strain, g.stress, category="polymer")
    assert res["E_pa"] is not None
    assert np.isfinite(res["E_pa"]), "폴리머 E가 값으로 반환되어야 함(거부 금지)"
    assert res["confidence"] == "low"


def test_noisy_nonpolymer_not_rejected():
    """C1 회귀: 노이즈가 커 R²<0.99여도 거부하지 않고 값+low로 반환."""
    g = make_golden(noise_pa=20e6)  # 탄성구간 침범할 큰 노이즈
    res = analysis.youngs_modulus(g.strain, g.stress)
    assert res["E_pa"] is not None and np.isfinite(res["E_pa"])
    assert res["confidence"] in ("high", "ok", "low")  # 어떤 경우든 값 반환
