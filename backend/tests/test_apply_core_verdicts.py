# 판정 병합기(`scripts/catalog/apply_core_verdicts.py`)가 앞 사유문을 지우지 않는지 못박는다 — 76차.
#
# 왜 여기 있나. 같은 판정 칸을 두 번째로 바꾸는 순간 앞 사유가 흔적 없이 사라지고 있었다
# (`<attr>_before_correction` 은 처음 한 번만 남는다). 스냅샷 대조로 32칸이 그렇게 지워진 것을
# 찾았다 — 74차 적용 10칸, 75차 적용 22칸. 되돌리면 다음 파동이 또 조용히 지운다.
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "catalog"))
acv = pytest.importorskip("apply_core_verdicts")

KEY = "core_absent_from_vendor_sheet"


def test_second_overwrite_keeps_the_earlier_reason():
    old = {"physical.density": "71차 GC 가 영문 카탈로그와 유럽 법인 페이지를 열었다."}
    new = {"physical.density": "74차 JA 가 구판 두 권을 전수했다."}
    got = acv.merge_reasons(old, new, "74차 JA")["physical.density"]
    assert got.startswith("74차 JA 가 구판 두 권을 전수했다.")
    assert "71차 GC 가 영문 카탈로그와 유럽 법인 페이지를 열었다." in got
    assert "74차 JA 가 이 칸을 새 사유로 바꾸며" in got


def test_rerunning_the_same_file_does_not_grow_the_text():
    old = {"physical.density": "앞 사유."}
    new = {"physical.density": "새 사유."}
    once = acv.merge_reasons(old, new, "B")
    assert acv.merge_reasons(once, new, "B") == once


def test_new_reason_that_already_carries_the_old_one_is_not_duplicated():
    old = {"physical.density": "앞 사유."}
    new = {"physical.density": "새 사유. 앞 사유."}
    assert acv.merge_reasons(old, new, "B") == new


def test_other_keys_are_kept_and_new_keys_are_added():
    old = {"physical.density": "밀도 사유.", "thermal.specific_heat": "비열 사유."}
    new = {"mechanical.poisson_ratio": "포아송 사유."}
    assert acv.merge_reasons(old, new, "B") == {**old, **new}


def test_keep_before_stacks_instead_of_clobbering():
    attrs = {}
    acv.keep_before(attrs, KEY, None)              # 정정 전에 없었다
    acv.keep_before(attrs, KEY, {"a": "1"})
    acv.keep_before(attrs, KEY, {"a": "1"})        # 같은 기록은 한 번만
    assert attrs[f"{KEY}_before_correction"] == [None, {"a": "1"}]


def _run(db: Path, tmp: Path, batch: str, verdict: dict) -> None:
    p = tmp / f"{batch}.json"
    p.write_text(json.dumps({"batch": batch, "verdicts": [
        {"material_id": 1, "name": "시험재", KEY: verdict}]}, ensure_ascii=False))
    argv = sys.argv
    sys.argv = ["apply_core_verdicts.py", "--db", str(db), str(p), "--apply"]
    try:
        assert acv.main() == 0
    finally:
        sys.argv = argv


def test_three_waves_on_one_cell_keep_all_three_reasons(tmp_path):
    """실제 사고 경로 — 71차가 만들고, 74차가 바꾸고, 75차가 또 바꾼다."""
    db = tmp_path / "m.db"
    con = sqlite3.connect(db)
    con.execute("create table material (id integer primary key, name text, attributes text)")
    con.execute("insert into material values (1, '시험재', '{}')")
    con.commit()
    con.close()
    for batch, text in (("71차 GC", "GC 근거."), ("74차 JA", "JA 근거."), ("75차 KA", "KA 근거.")):
        _run(db, tmp_path, batch, {"physical.density": text})
    attrs = json.loads(sqlite3.connect(db).execute(
        "select attributes from material where id=1").fetchone()[0])
    reason = attrs[KEY]["physical.density"]
    assert reason.startswith("KA 근거.")
    assert "JA 근거." in reason and "GC 근거." in reason
    assert attrs[f"{KEY}_before_correction"] is None    # 첫 판정 전에는 칸이 없었다
