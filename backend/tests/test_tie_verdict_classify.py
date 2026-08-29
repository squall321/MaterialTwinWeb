# 동률 판정의 **부류**가 거짓말을 하지 않는지 못박는다(53차 OB).
#
# 왜 여기 있나. 판정문은 값과 함께 운영까지 가고 **다음 사람이 그대로 믿는다**(브리프 505·556).
# 그래서 부류를 정하는 두 갈래에 회귀 못을 박는다.
#   ① 한쪽에만 있는 축이 남아도, **다른 축이 양쪽에 다 적혀 있고 값이 다르면** 축은 닫혀 있다.
#      그때 "이 축이 한쪽에만 적혀 있다" 는 거짓이다(라이브 조건미기재 119군 중 77군이 그랬다).
#   ② `basis` 는 TERM 이지만 값이 `minimum` 대 `typical` 이면 **다른 항이 아니라 산포**다.
#      그때 "대표값 자체가 뜻이 없다 — `set_id`·`term` 으로 묶어 읽어라" 는 거짓이다.
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "catalog"))
tv = pytest.importorskip("tie_verdicts")


class _Row:
    def __init__(self, cond, source_id=1):
        self.conditions = cond
        self.source_id = source_id


def _cls(head_cond, *rival_conds, same_src=True):
    head = _Row(head_cond)
    rivals = [_Row(c, 1 if same_src else 2 + i) for i, c in enumerate(rival_conds)]
    return tv.classify(head, rivals)[0], tv.facets(head, rivals)


def test_closed_axis_beats_one_sided_key():
    """direction 이 MD/TD 로 **양쪽에** 있으면 `test`↔`test_standard` 한 짝 때문에
    조건미기재로 떨어지면 안 된다 — 재료272 Taconic RF-35 의 실제 모양이다."""
    c, f = _cls({"direction": "MD", "test_standard": "ASTM D 790"},
                {"direction": "TD", "test": "ASTM D 790"})
    assert c == "다른조건"
    assert "direction" in f["common"]


def test_truly_one_sided_axis_stays_unspecified():
    """양쪽에 닫힌 축이 없으면 조건미기재 그대로다 — 고침이 이 갈래를 삼키면 안 된다."""
    c, _ = _cls({"load_g": 200}, {"load_gf": 200})
    assert c == "조건미기재"


def test_notation_pair_still_wins_over_closed_axis():
    """표기 짝 판정은 앞에 그대로 둔다 — `axis`↔`direction` 은 키를 통일하면 사라진다."""
    c, _ = _cls({"axis": "x"}, {"direction": "x"})
    assert c == "키표기흔들림"


def test_pure_statistic_basis_is_spread_not_term():
    """`basis: minimum/typical` 은 항이 아니라 산포다 — 진짜 축은 `temper` 다(재료2560)."""
    c, f = _cls({"basis": "minimum", "temper": "T4"},
                {"basis": "typical", "temper": "T6"})
    assert c == "다른조건"
    assert "basis" in f["spread"] and "basis" not in f["term"]


def test_descriptive_basis_is_still_term():
    """51차 MA 가 손확인한 `basis` 는 shear 대 tensile 이다 — 그건 여전히 다른 항이다."""
    c, f = _cls({"basis": "shear"}, {"basis": "tensile"})
    assert c == "다른항"
    assert "basis" in f["term"]


def test_statistic_word_inside_a_sentence_is_not_a_statistic():
    """`quantity: 'average peel force — …'` 는 낱말로 시작할 뿐 통계량이 아니다.
    전체 일치를 봐야 재료1166 이 안 끌려온다."""
    c, f = _cls({"quantity": "average peel force - 저자 고유 처리다"},
                {"quantity": "average maximum peel force - 다른 양이다"})
    assert c == "다른항"
    assert "quantity" in f["term"]
