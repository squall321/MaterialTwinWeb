# 대표값 선택기가 판(版) 충돌 표기를 명시적으로 본다 — 76차 가드의 회귀시험.
#
# 75차 KA 가 같은 표·같은 규격·같은 조건인데 판마다 다른 숫자를 찍는 23칸을 찾았다
# (Resonac 영문판 2026-07 vs 일문판). 약한 쪽 행에만 `edition_conflict` 를 달았는데,
# 그 행들이 대표에서 밀린 것은 규칙 때문이 아니라 **조건 칸이 둘 더 많고 id 가 커서**였다.
# 오늘 라이브에서는 명시 항이 없어도 뒤집히는 군이 0이다 — 그래서 이것은 값을 바꾸는
# 수정이 아니라 **우연이 반대로 설 때를 위한 가드**다. 아래가 그 경우들이다.
from __future__ import annotations

from app.catalog_compare import _condition_axis_count, _edition_rank, _rep_rank


class _PV:
    def __init__(self, pid, value, cond, tier=1, key="mechanical.youngs_modulus"):
        self.id = pid
        self.property_key = key
        self.value_num = value
        self.conditions = cond
        self.quality_tier = tier


def test_conflict_loses_even_when_it_has_fewer_conditions_and_smaller_id():
    """우연(조건 수·적재 순서)이 전부 충돌 행 편일 때도 충돌 행이 진다."""
    conflict = _PV(1, 17e9, {"edition_conflict": "en only; ja editions agree"})
    solid = _PV(99, 18e9, {"test_standard": "IPC-TM-650 2.4.4", "temperature_c": 23,
                           "specimen_thickness_mm": 0.8})
    assert sorted([conflict, solid], key=_rep_rank)[0] is solid


def test_edition_annotations_are_not_counted_as_conditions():
    """판 표기를 달았다는 이유만으로 순위가 바뀌면 안 된다."""
    bare = {"test_standard": "D3039"}
    tagged = {"test_standard": "D3039", "catalog_edition": "ja 2026-04"}
    assert _condition_axis_count(bare) == _condition_axis_count(tagged)


def test_tier_still_outranks_edition_conflict():
    """판 충돌로 밀린 t1 도 그 등급에 인쇄된 값이다 — 다른 물건의 t3 보다는 낫다."""
    t1_conflict = _PV(1, 17e9, {"edition_conflict": "en only"}, tier=1)
    t3_clean = _PV(2, 20e9, {}, tier=3)
    assert sorted([t3_clean, t1_conflict], key=_rep_rank)[0] is t1_conflict


def test_empty_conflict_field_is_not_a_conflict():
    """빈 문자열·None 은 충돌 표기가 아니다."""
    assert _edition_rank(_PV(1, 1.0, {"edition_conflict": ""})) == 0
    assert _edition_rank(_PV(1, 1.0, {"edition_conflict": None})) == 0
    assert _edition_rank(_PV(1, 1.0, {})) == 0


def test_different_test_standard_is_not_edition_conflict():
    """다른 시험법으로 잰 값은 조건으로 갈린다 — 판 충돌이 아니다(Shengyi 시장판)."""
    cn = _PV(1, 3.6, {"test_standard": "IEC 61189-2-721",
                      "catalog_edition": "China-market"}, key="electrical.dielectric_constant")
    assert _edition_rank(cn) == 0
