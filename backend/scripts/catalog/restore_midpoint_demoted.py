#!/usr/bin/env python3
# 중앙값 가드가 부정문에 걸려 강등한 인쇄값을 되돌린다 — 43차 EE 가 연 마지막 항목이다.
#
# 무슨 일이 있었나
#   적재기의 중앙값 가드는 근거에 `중앙값`·`midpoint` 가 보이면 method 를
#   measured/handbook → computed 로 내린다(브리프 451). 그런데 **브리프를 읽은 배치는
#   근거에 "구간의 중앙값은 만들지 않았다" 라고 적는다.** 부정문을 못 보는 가드가
#   그 한 줄 때문에 **인쇄된 값을 "우리가 계산했다" 로 뒤집었다.**
#   가드 자체는 43차 EE 가 고쳤다(`asserts_midpoint`). 이 스크립트는 **이미 든 행**을 고친다.
#
#   실측 — 중앙값 문구가 걸리는 725행 중 442행이 부정문이고, 그중 431행이 computed 였다.
#
# 무엇을 되돌리고 무엇을 안 되돌리나
#   · **되돌린다** — 근거에 계산 지문이 없는 순수 인쇄값 채택 394행.
#     원래 method 는 로더의 `METHOD_MAP` 이 기계적으로 정한다 — datasheet·journal → measured,
#     book·database → handbook. 우리가 물리를 추측하는 게 아니라 매핑을 복원하는 것이다.
#   · **안 되돌린다** — 근거에 환산·계산 지문이 있는 37행(예: kgf/cm → N/m).
#     단위 환산이 method 를 바꾸는지는 별개 판단이라 여기서 정하지 않는다.
#
# 되돌린 행에는 `conditions.method_restored` 를 남긴다 — 되돌릴 수 있어야 한다.
# 한 번 더 돌려도 안전하다(멱등).
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ingest_agent_json import _MIDPOINT, asserts_midpoint  # noqa: E402

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR", "var/data"), "materialtwin.db")

# 진짜 계산·환산의 지문. 하나라도 걸리면 손대지 않는다.
CALC = re.compile(r"계산|산출|환산|역산|혼합칙|피팅|fit(ted|ting)?\b|converted|derived|"
                  r"regress|보간|외삽|extrapolat|interpolat|추정|가정|assum", re.I)
# 출처 종류 → 원래 method. 로더 METHOD_MAP 과 등급 어휘(t2 = 핸드북·규격·인증DB)를 따른다.
BY_KIND = {"datasheet": "measured", "journal": "measured", "standard": "measured",
           "book": "handbook", "database": "handbook", "handbook": "handbook"}


def main() -> int:
    if not os.path.exists(DB):
        print(f"DB 가 없다: {DB} — MATERIALTWIN_DATA_DIR 를 확인하라", file=sys.stderr)
        return 1
    c = sqlite3.connect(DB, timeout=60)
    c.execute("pragma busy_timeout=60000")
    c.row_factory = sqlite3.Row

    rows = c.execute(
        "select pv.id, pv.notes, pv.conditions, pv.quality_tier, s.kind "
        "from property_value pv left join source s on s.id=pv.source_id "
        "where pv.method='computed' and pv.notes is not null and pv.notes != ''").fetchall()

    cand = [r for r in rows
            if _MIDPOINT.search(str(r["notes"])) and not asserts_midpoint(r["notes"])]
    keep = [r for r in cand if CALC.search(str(r["notes"]))]
    fix = [r for r in cand if not CALC.search(str(r["notes"]))]

    done, skipped = Counter(), Counter()
    for r in fix:
        meth = BY_KIND.get(r["kind"] or "")
        if meth is None:
            skipped[r["kind"]] += 1          # 모르는 출처 종류는 건드리지 않는다
            continue
        try:
            d = json.loads(r["conditions"]) if r["conditions"] else {}
        except (TypeError, ValueError):
            d = {}
        if not isinstance(d, dict):
            d = {}
        d["method_restored"] = {
            "from": "computed", "to": meth, "by": "restore_midpoint_demoted.py",
            "reason": "중앙값 가드가 부정문('중앙값은 만들지 않았다')에 걸려 인쇄값을 강등했다"}
        c.execute("update property_value set method=?, conditions=? where id=?",
                  (meth, json.dumps(d, ensure_ascii=False), r["id"]))
        done[meth] += 1
    c.commit()

    print(f"부정문 후보 {len(cand)}행")
    print(f"  · 계산·환산 지문이 있어 손대지 않은 행 {len(keep)}")
    print(f"  · 되돌린 행 {sum(done.values())} — {dict(done)}")
    if skipped:
        print(f"  · 출처 종류를 몰라 넘긴 행 {sum(skipped.values())} — {dict(skipped)}")
    left = c.execute(
        "select count(*) from property_value pv where pv.method='computed' "
        "and pv.notes like '%중앙값%'").fetchone()[0]
    print(f"\n남은 computed + 중앙값 문구 행 {left} (계산 지문이 있거나 진짜 중앙값이다)")
    c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
