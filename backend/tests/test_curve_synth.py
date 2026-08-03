# σ-ε 곡선 합성 회귀 — 물리적으로 불가능한 조합(항복>인장)과 연성/취성 분기를 못박는다.
from __future__ import annotations

import numpy as np

from app.curve_synth import KIND_SYNTHETIC, synthesize


def test_ductile_metal_without_yield_is_not_treated_as_brittle():
    """동박처럼 항복 미공표 + 연신율이 큰 금속을 취성으로 그리면 곡선이 통째로 틀린다."""
    out = synthesize(E=1.1e11, sigy=None, uts=2.06e8, elong=0.08)
    assert out is not None
    assert "brittle" not in out["model"]
    s = np.asarray(out["stress_pa"])
    # 소성 평탄부가 있어야 한다 — 마지막 구간이 UTS에서 평평.
    assert abs(s[-1] - 2.06e8) < 1e3
    assert abs(s[-1] - s[-5]) < 1e3


def test_low_elongation_without_yield_stays_brittle():
    out = synthesize(E=7e10, sigy=None, uts=5e7, elong=0.005)
    assert out is not None and "brittle" in out["model"]


def test_yield_above_uts_is_flagged_not_silently_used():
    """항복>인장은 두 값의 출처가 다르다는 뜻 — 조용히 넘기면 안 된다."""
    out = synthesize(E=1.1e11, sigy=2.5e8, uts=2.06e8, elong=0.04)
    assert out is not None
    assert out.get("inconsistent") is True
    assert "항복" in out["note"]
    # 인장강도를 쓰지 않았으므로 최대응력이 항복을 넘지 않는다.
    assert max(out["stress_pa"]) <= 2.5e8 * 1.001


def test_hollomon_curve_passes_through_uts_at_fracture():
    out = synthesize(E=2.0e11, sigy=2.5e8, uts=5.0e8, elong=0.30)
    assert out is not None and out["kind"] == KIND_SYNTHETIC
    assert abs(max(out["stress_pa"]) - 5.0e8) / 5.0e8 < 0.02
    e = np.asarray(out["strain"])
    assert np.all(np.diff(e) >= -1e-12)          # 변형률 단조 증가
    assert abs(e[-1] - 0.30) < 1e-6


def test_missing_modulus_returns_none():
    assert synthesize(E=0, sigy=1e8, uts=2e8, elong=0.1) is None
