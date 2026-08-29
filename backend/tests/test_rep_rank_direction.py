# `direction` 정규화가 **조건 수를 안 흔든다**는 불변식 — 54차 PA 의 회귀 고정.
#
# 왜 별도 파일인가(§553). 같은 파동에 다른 배치가 돌아 `test_rep_rank.py` 를 공유한다.
#
# 왜 있나. 52차 NA 가 `direction` 을 정규값과 원문(`direction_verbatim`)으로 가르면서
# *"`direction` 을 가진 행은 전부 정확히 한 칸 늘어난다"* 로 순위를 상쇄했다.
# **그 상쇄는 군의 모든 행이 `direction` 을 가질 때만 성립한다.** 방향 행과 무방향 행이
# 섞인 군에서는 방향 행만 밀린다 — 54차 PA 의 잔여 4,455행 정정에서 실측으로 4군이 뒤집혔고
# 그중 재료108 열전도율은 **값까지 바뀌었다**(pv4217 면직 15 → pv1051 면내 700 W/mK).
# `direction_verbatim` 은 `direction` 의 **원문**이지 별개의 축이 아니므로 조건 수에서 뺐다.
from __future__ import annotations

from types import SimpleNamespace

from app import catalog_compare as CC


def _pv(pid, key="thermal.conductivity", tier=1, value=1.0, cond=None):
    return SimpleNamespace(id=pid, property_key=key, quality_tier=tier,
                           value_num=value, conditions=cond, method="measured")


def test_direction_verbatim_is_not_counted_as_a_condition():
    """원문 칸을 세면 방향 행이 밀린다 — 안 세야 순서가 보존된다."""
    a = _pv(9, cond={"axis": "through-plane"})
    b = _pv(1, cond={"orientation": "in-plane", "thickness_um": 100})
    assert CC._rep_rank(a) < CC._rep_rank(b)              # 조건 1칸 대 2칸
    # NA 의 분리 — 이름을 옮기고 원문을 남긴다. 축은 여전히 하나다.
    a.conditions = {"direction": "through-thickness", "direction_verbatim": "through-plane"}
    assert CC._rep_rank(a) < CC._rep_rank(b)              # 여전히 1칸으로 세어진다


def test_split_is_rank_neutral_for_every_row_that_has_a_direction():
    """정규화는 군 안의 순서를 **한 자리도** 안 바꾼다 — 미배정(`null`)이 섞여도 그렇다."""
    rows = [_pv(3, cond={"axis": "in-plane", "thickness_um": 17}),
            _pv(1, cond={"direction": "in-plane (X,Y)", "thickness_um": 25}),
            _pv(2, cond={"grade": "17 um", "axis": "L (종방향)"}),
            _pv(4, cond={"orientation": "in-plane", "thickness_um": 40})]
    before = [pv.id for pv in sorted(rows, key=CC._rep_rank)]
    rows[0].conditions = {"thickness_um": 17, "direction": "in-plane",
                          "direction_verbatim": "in-plane"}
    rows[1].conditions = {"direction": "in-plane", "thickness_um": 25,
                          "direction_verbatim": "in-plane (X,Y)"}
    # 어휘로 표현 못 하는 축은 `direction` 을 비운다(§561 ㉡) — 키는 남으므로 한 칸이다.
    rows[2].conditions = {"grade": "17 um", "direction": None,
                          "direction_verbatim": "L (종방향)"}
    assert [pv.id for pv in sorted(rows, key=CC._rep_rank)] == before


def test_real_axis_keys_are_still_counted():
    """반대 못 — `direction` 자체는 여전히 조건이다. 원문 칸만 뺀 것이다."""
    a = _pv(9, cond={"thickness_um": 25})
    b = _pv(1, cond={"thickness_um": 25, "direction": "MD",
                     "direction_verbatim": "machine direction"})
    assert CC._rep_rank(a) < CC._rep_rank(b)
