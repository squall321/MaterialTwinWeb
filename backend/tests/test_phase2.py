# Phase 2·3 회귀 테스트 — 진응력 변환·넥킹·구성방정식 피팅·통계·LS-DYNA 카드.
from __future__ import annotations

import numpy as np

from app import true_stress, fitting, cards
from tests.fixtures.golden_linear_powerlaw import make_golden


# ── 넥킹이 있는 합성 곡선(진응력 Hollomon → 공칭 역변환) ─────────────────────
def _necking_eng_curve(K=700e6, n=0.15, E=200e9, eps_t_max=0.40, N=3000):
    """진응력 σ_t=K·ε_t^n 를 정의하고 공칭으로 역변환. Hollomon: ε_true_neck≈n 에서 공칭 UTS.

    반환: (eng_strain, eng_stress). 공칭은 UTS 후 하강 → Considère 넥킹 존재.
    """
    et = np.linspace(1e-4, eps_t_max, N)
    st = K * et ** n  # 진응력
    en = np.expm1(et)  # ε_nom = e^{ε_t} − 1
    es = st / (1.0 + en)  # σ_nom = σ_t/(1+ε_nom)
    return en, es


# ── 진응력 변환 ────────────────────────────────────────────────────────────
def test_to_true_formula():
    en = np.array([0.0, 0.1, 0.2])
    es = np.array([100.0, 200.0, 300.0])
    r = true_stress.to_true(en, es)
    # ε_true=ln(1+ε), σ_true=σ·(1+ε)
    assert np.allclose(r["true_strain"], np.log1p(en))
    assert np.allclose(r["true_stress"], es * (1 + en))


def test_considere_necking_at_n():
    # Hollomon 진응력이면 넥킹 진변형률 ε_true_neck = n (해석해).
    en, es = _necking_eng_curve(n=0.15)
    conv = true_stress.true_curve_with_necking(en, es)
    neck = conv["necking"]
    assert neck["strain"] is not None, neck["reason"]
    # 해석해 ε_true_neck = n = 0.15. 이산화 오차 감안 관대하게.
    assert abs(neck["strain"] - 0.15) < 0.03


def test_no_necking_when_monotonic():
    # 골든(공칭 단조증가)은 넥킹 미검출이 정상.
    g = make_golden(n_points=1000)
    conv = true_stress.true_curve_with_necking(g.strain, g.stress)
    assert conv["necking"]["strain"] is None


# ── 구성방정식 피팅 ─────────────────────────────────────────────────────────
def _plastic_true_hollomon(K=700e6, n=0.15, E=200e9):
    """넥킹 곡선의 진응력·소성진변형률(넥킹 개시까지). Hollomon 정답 K,n 검증용."""
    en, es = _necking_eng_curve(K=K, n=n, E=E)
    conv = true_stress.true_curve_with_necking(en, es)
    et = np.asarray(conv["true_strain"])
    st = np.asarray(conv["true_stress"])
    upto = conv["valid_upto_index"]
    if upto and upto > 2:
        et, st = et[:upto], st[:upto]
    ep = et - st / E
    return ep, st


def test_hollomon_recovers_n_k():
    # 진응력 σ_t=K·ε_t^n 생성 → 넥킹까지 진곡선 피팅이 K,n 복원.
    ep, st = _plastic_true_hollomon(K=700e6, n=0.15)
    r = fitting.fit_model("hollomon", ep, st)
    assert r["params"] is not None, r.get("reason")
    assert r["r2"] > 0.98
    # εp ≈ ε_true(탄성분 미미) → K·n 근접 복원.
    assert 0.12 < r["params"]["n"] < 0.18
    assert 6e8 < r["params"]["K_pa"] < 8e8


def test_fit_all_returns_all_models_sorted():
    ep, st = _plastic_true_hollomon()
    results = fitting.fit_all(ep, st)
    models = {r["model"] for r in results}
    assert models == set(fitting.MODEL_NAMES)
    # R² 내림차순 정렬(성공한 것들끼리).
    r2s = [r["r2"] for r in results if r.get("r2") is not None]
    assert r2s == sorted(r2s, reverse=True)


def test_fit_graceful_on_garbage():
    # 데이터 부족·비물리 입력도 예외 없이 reason 반환.
    r = fitting.fit_model("swift", np.array([0.0]), np.array([1.0]))
    assert r["params"] is None
    assert "reason" in r


# ── LS-DYNA 카드 ────────────────────────────────────────────────────────────
def test_lsdyna_card_structure():
    ep, st = _plastic_true_hollomon()
    text = cards.lsdyna_mat024_card(
        title="TestSteel", E_pa=200e9, yield_pa=350e6,
        plastic_strain=ep, true_stress=st,
    )
    assert "*MAT_PIECEWISE_LINEAR_PLASTICITY" in text
    assert "*DEFINE_CURVE" in text
    assert "*END" in text
    assert "TestSteel" in text
    # 곡선 데이터 행이 존재(εp, σ 쌍).
    assert text.count("e+") > 5 or text.count("e-") > 5
