# 중복 검출기(`scripts/catalog/value_duplicates.py`)의 정규화·분류 규칙을 못박는다 — 52차 NB.
#
# 왜 여기 있나. 이 도구의 판정이 **값을 지우는 데 쓰이지는 않지만**, 어느 행에 중복 표시를
# 다는지를 정한다. 손확인에서 규칙을 세 번 좁혔는데(아래 각 시험이 그 반례다) 그 좁힘이
# 풀리면 멀쩡한 측정이 중복으로 표시된다.
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "catalog"))
vd = pytest.importorskip("value_duplicates")


def sig(raw):
    cond, _ = vd.norm_conditions(json.dumps(raw, ensure_ascii=False))
    return vd.cond_sig(cond)


def verdict(*raws, **row):
    """조건만 다른 행들을 한 군으로 만들어 분류한다."""
    members = []
    for i, raw in enumerate(raws):
        text = json.dumps(raw, ensure_ascii=False)
        cond, ann = vd.norm_conditions(text)
        members.append({"id": i, "raw": text, "cond": cond, "sig": vd.cond_sig(cond), **row})
    return vd.classify(members)[0]


# ── 정규화가 흡수해야 하는 것 ────────────────────────────────────────────────
def test_key_spelling_wobble_collapses():
    """§547 이 센 여섯 흔들림. 이걸 못 흡수하면 중복 검출이 통째로 무력해진다."""
    assert sig({"standard": "ASTM D882"}) == sig({"test_standard": "ASTM D882"})
    assert sig({"standard": "ASTM D882"}) == sig({"test": "ASTM D882"})
    assert sig({"axis": "x"}) == sig({"direction": "x"}) == sig({"orientation": "x"})
    assert sig({"temperature_C": 23}) == sig({"temperature_c": 23})
    assert sig({"frequency_Hz": 1e10}) == sig({"frequency_GHz": 10})


def test_units_are_converted_not_just_renamed():
    """이름만 통일하면 `temperature_k=300` 과 `temperature_c=300` 이 같아져 버린다."""
    assert sig({"temperature_c": 23}) == sig({"temperature_k": 296.15})
    assert sig({"temperature_c": 23}) != sig({"temperature_k": 23})
    assert sig({"thickness_um": 25}) == sig({"thickness_mm": 0.025})


def test_unit_inside_the_value_is_read():
    """브리프가 준 Kapton 세 행이 정확히 이 모양이다 — `"37.5 um"` 대 `37.5`."""
    assert sig({"thickness": "37.5 um"}) == sig({"thickness_um": 37.5})
    assert sig({"temperature": "23 C"}) == sig({"temperature_C": 23})


def test_range_is_read_as_a_number_pair():
    """`40-125` 의 `-` 는 부호가 아니라 구분자다 — 그냥 읽으면 (40, -125) 가 된다."""
    a = sig({"temperature_range_C": "40-125"})
    assert a == sig({"range": "40C to 125C, below Tg"}) == sig({"range": "40-125 degC"})
    assert sig({"temperature_range_C": "-55 to 288"}) == sig({"temperature_range_c": "-55~288"})
    assert a != sig({"temperature_range_C": "40-150"})


def test_our_own_annotations_are_not_conditions():
    """정정 선언·되돌리기 표시·중복 표시는 적재 이력이지 측정 조건이 아니다(§521)."""
    assert sig({"axis": "x"}) == sig({"axis": "x", "correction_reason": "…",
                                      "value_before_correction": 1.0,
                                      "verdict_duplicate_of": "…"})


# ── 정규화가 흡수하면 **안 되는** 것 (손확인에서 좁힌 자리들) ─────────────────
def test_source_table_is_a_real_axis_not_an_annotation():
    """그 문서 안의 **어느 표인가**는 측정을 가른다. 주석으로 취급했더니 BIO-PSA 66군이
    '조건 동일' 로 잘못 올라왔고, 같은 논리면 Table 3 과 Table 5 도 같아진다."""
    assert sig({"source_table": "Table 3"}) != sig({"source_table": "Table 5"})
    assert sig({"axis": "x"}) != sig({"axis": "x", "source_table": "Table 3"})


def test_parenthetical_is_stripped_on_direction_but_not_on_standard():
    """`JIS C-2318` 과 `JIS C-2318 (modified to TDF)` 를 같다고 하면 안 된다."""
    assert sig({"axis": "length (LW)"}) == sig({"direction": "length (warp)"})
    assert sig({"standard": "JIS C-2318"}) != sig({"standard": "JIS C-2318 (modified to TDF)"})


# ── 분류 ────────────────────────────────────────────────────────────────────
def test_identical_after_normalization_is_certain():
    assert verdict({"direction": "Z", "temperature_range_c": "-55 to 288"},
                   {"axis": "z", "temperature_range_C": "-55 to 288"}) == vd.VERDICT_CERTAIN


def test_real_split_on_a_repeat_axis_is_a_legitimate_repeat():
    """반복 시편·통계량·세트 항이 갈리면 값이 같아도 중복이 아니다(§435)."""
    assert verdict({"set_id": "a", "term": "1"}, {"set_id": "b", "term": "1"}) == vd.VERDICT_REPEAT
    assert verdict({"statistic": "minimum"}, {"statistic": "maximum"}) == vd.VERDICT_REPEAT
    assert verdict({"thickness_mm": 1.5}, {"thickness_mm": 0.7}) == vd.VERDICT_REPEAT


def test_axis_present_on_only_one_side_is_only_a_suspect():
    """**한쪽에만 있는 것은 확정이 아니다.** TAIFLEX 2UPDR2010JD 는 grade 가 한쪽에만
    있는데 그 grade 가 곧 재료 이름이라 중복이다 — 반복으로 확정하면 놓친다."""
    assert verdict({"frequency_hz": 1e10},
                   {"frequency_GHz": 10, "grade": "2UPDR2010JD"}) == vd.VERDICT_SUSPECT
    assert verdict({"standard": "ASTM D638"},
                   {"standard": "ASTM D638", "temperature_C": 23}) == vd.VERDICT_SUSPECT


def test_paren_only_difference_is_a_suspect_not_certain():
    assert verdict({"standard": "JIS C-2318"},
                   {"standard": "JIS C-2318 (modified to TDF)"}) == vd.VERDICT_SUSPECT


def test_value_fingerprint_absorbs_float_noise():
    """`1e-05` 와 `9.999999999999999e-06` 은 같은 값이다 — 비트로 비교하면 못 묶는다."""
    assert vd.val_key(1e-05, None, "1/K") == vd.val_key(9.999999999999999e-06, None, "1/K")
    assert vd.val_key(1e-05, None, "1/K") != vd.val_key(1.2e-05, None, "1/K")
    assert vd.val_key(1e-05, None, "1/K") != vd.val_key(1e-05, None, "1/m")


# ── 표시가 대표값에서 실제로 밀어내는지 ──────────────────────────────────────
def test_marked_duplicate_never_wins_over_its_canonical():
    """**이 시험이 규약의 못이다.** 표시는 `_rep_rank` 를 고치지 않고 그 안에서 푼다 —
    다섯째 자리가 `len(conditions)` 오름차순이라 중복 쪽에 두 칸을 더하면 정본이 이긴다
    (§543·544 가 두 번 재고 버린 *순위 변경* 을 안 한다).

    **그래서 `_rep_rank` 가 살림살이 키를 세지 않게 되면 이 규약이 조용히 죽는다.**
    52차 NC 가 `catalog_alternatives._cond` 에서 살림살이를 뺐고(§546 세 갈래가 무너져서다),
    같은 손질이 `_rep_rank` 로 번지면 표시된 중복이 다시 대표값이 된다.
    여기서 잡는다 — 순위가 조건 수를 세는 한 이 시험은 통과한다.
    """
    from app.catalog_compare import _rep_rank

    class Row:
        def __init__(self, pid, conditions):
            self.id, self.conditions = pid, conditions
            self.property_key, self.value_num, self.quality_tier = "thermal.expansion_linear", 1.92e-05, 1

    canon = Row(6164, {"axis": "MD", "direction": "MD", "range": "25-200C"})
    # 중복은 원래 조건이 **더 적어서** 표시 전에는 이겼다 — 실제 라이브의 재료 255 다.
    dup = Row(4207, {"direction": "MD", "temperature_range_c": "25-200"})
    assert _rep_rank(dup) < _rep_rank(canon)

    dup.conditions = dict(dup.conditions,
                          verdict_duplicate_of='axis="MD" | direction="MD" | range="25-200C"',
                          verdict_duplicate_note="52차 NB")
    assert _rep_rank(canon) < _rep_rank(dup)      # 표시 뒤에는 정본이 이긴다
