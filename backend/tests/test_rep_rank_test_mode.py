# 대표값 선택이 **시험모드**를 본다 — 72차 HB 가 찾은 결함의 회귀시험.
#
# 굽힘탄성률은 인장보다 12~55% 크다. `mechanical.youngs_modulus` 칸에 굽힘값이 앉아
# 있어도 선택기에 모드 항이 없어서, 같은 등급·같은 조건수면 **먼저 들어온 행이 이겼다**.
# 실측: 재료 233 은 진짜 인장값(ASTM D3039, 13.50 GPa)이 DB 에 있는데도 굽힘 행
# (19.00 GPa)이 앞 파동에 먼저 들어왔다는 이유로 DYNA 카드 대표였다 — 40.7% 과대.
from __future__ import annotations

from app.catalog_compare import _mode_rank, _rep_rank


class _PV:
    """`_rep_rank` 가 읽는 속성만 가진 최소 대역."""

    def __init__(self, pid, key, value, cond, tier=1):
        self.id = pid
        self.property_key = key
        self.value_num = value
        self.conditions = cond
        self.quality_tier = tier


YM = "mechanical.youngs_modulus"


def test_mode_rank_reads_test_standard():
    assert _mode_rank(_PV(1, YM, 1e10, {"test_standard": "ASTM D3039"})) == 0   # 인장
    assert _mode_rank(_PV(2, YM, 1e10, {"test_standard": "ASTM D790-15e2"})) == 2  # 굽힘
    assert _mode_rank(_PV(3, YM, 1e10, {})) == 1                                # 미표기


def test_tensile_beats_flexural_even_when_inserted_later():
    """이것이 실제로 났던 사고다 — 굽힘이 먼저 들어와 id 가 작다."""
    flex = _PV(10448, YM, 19.0e9, {"test_standard": "flexural modulus"})
    tens = _PV(45589, YM, 13.5e9, {"test_standard": "ASTM D3039"})
    assert sorted([flex, tens], key=_rep_rank)[0] is tens


def test_unmarked_sits_between_marked_tensile_and_marked_flexural():
    """미표기를 가운데 두는 것이 핵심이다.

    굽힘을 맨 아래 두기만 하면 「표시할수록 밀린다」가 되어 오염을 숨기는 쪽이 이득이
    된다. 인장을 맨 위에 둬야 정직한 표기가 보상받는다.
    """
    tens = _PV(3, YM, 1e10, {"test_standard": "ASTM D3039"})
    bare = _PV(2, YM, 2e10, {})
    flex = _PV(1, YM, 3e10, {"test_standard": "ASTM D790"})
    assert [p.id for p in sorted([flex, bare, tens], key=_rep_rank)] == [3, 2, 1]


def test_tier_still_outranks_mode():
    """모드는 등급 **아래**다 — t1 굽힘이 t3 인장을 이긴다."""
    t1_flex = _PV(1, YM, 3e10, {"test_standard": "ASTM D790"}, tier=1)
    t3_tens = _PV(2, YM, 1e10, {"test_standard": "ASTM D3039"}, tier=3)
    assert sorted([t3_tens, t1_flex], key=_rep_rank)[0] is t1_flex


def test_window_is_narrow_enough_to_ignore_incidental_words():
    """조건 전 칸을 훑으면 곁말에 걸린다.

    재료 77 의 3점굽힘 행은 `"air side always used as the tensile side"` 를 갖고 있다.
    시험 식별 칸만 보면 그 행은 정확히 굽힘으로 잡힌다.
    """
    pv = _PV(1, "mechanical.flexural_strength", 8.7e8, {
        "strength_property": "modulus of rupture (MOR) from three-point bending",
        "surface_state": "air side always used as the tensile side, tin side taped",
    })
    assert _mode_rank(pv) == 0


def test_key_without_expected_mode_is_neutral():
    """모드 개념이 없는 키는 이 항이 순위를 흔들면 안 된다."""
    a = _PV(1, "physical.density", 1000.0, {"test_standard": "ASTM D792"})
    b = _PV(2, "physical.density", 1100.0, {})
    assert _mode_rank(a) == _mode_rank(b) == 1
