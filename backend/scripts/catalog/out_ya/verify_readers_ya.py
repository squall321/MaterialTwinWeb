#!/usr/bin/env python3
# 정정 전후로 온도를 읽는 코드가 무엇을 다르게 답하는지 두 DB 를 나란히 놓고 전수로 대조한다(63차 YA).
"""`temperature_k`(그리고 `temperature`)를 읽는 코드는 라이브에 넷이다.

| 읽는 자리 | 무엇을 하나 | 이 배치가 바꾸나 |
|---|---|---|
| `app/catalog_compare._temp_distance` | 대표값 순위 넷째 자리(상온에서 얼마나 먼가) | **바꾼다** — 이 대조의 표적 |
| `app/dyna_export._COND_SHOW` | 카드 주석의 `T …K` 태그 | 바꾼다(태그가 새로 붙는다) |
| `scripts/catalog/tie_verdicts.temp_c` | 동률 판정에서 온도축이 닫혔는지 | 바꾼다(문자열 훑기 → 숫자 칸) |
| `frontend/src/lib/catalog-ui.formatConditions` | 조건 요약 문자열 | 바꾼다(`temperature=…` → `T … K`) |
| `scripts/catalog/integrity_check` | `$.temperature_k` 존재 검사 | **안 바꾼다**(출력이 글자까지 같다) |

`_condition_axis_count` 는 `_before_correction` 을 안 세므로 조건 칸 수가 안 변한다 —
그래서 `_rep_rank` 의 다섯째 자리는 전수에서 한 군도 안 움직인다. 이 스크립트가 그것을 증명한다.

사용: python3 verify_readers_ya.py <정정전.db> <정정후.db>
"""
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from app.catalog_compare import (  # noqa: E402
    _condition_axis_count, _rep_rank, _temp_distance)
from app.dyna_export import _cond_tag  # noqa: E402


class Row:
    __slots__ = ("id", "material_id", "property_key", "value_num", "conditions", "quality_tier")


def load(db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    out = defaultdict(list)
    for i, m, k, v, c, t in con.execute(
            "select id,material_id,property_key,value_num,conditions,quality_tier "
            "from property_value"):
        r = Row()
        r.id, r.material_id, r.property_key, r.value_num, r.quality_tier = i, m, k, v, t
        r.conditions = json.loads(c) if c else None
        out[(m, k)].append(r)
    con.close()
    return out


def main():
    a, b = load(sys.argv[1]), load(sys.argv[2])
    keys = set(a) | set(b)
    print(f"군 {len(keys)}  (전 {len(a)} · 후 {len(b)})")

    axis_moved = [r.id for k in keys for r in a.get(k, [])
                  if _condition_axis_count(r.conditions)
                  != _condition_axis_count(next((x.conditions for x in b.get(k, [])
                                                 if x.id == r.id), r.conditions))]
    print(f"조건 칸 수가 바뀐 행: {len(axis_moved)}  {axis_moved[:10]}")

    dist = [r.id for k in keys for r in a.get(k, [])
            if _temp_distance(r.conditions)
            != _temp_distance(next((x.conditions for x in b.get(k, []) if x.id == r.id),
                                   r.conditions))]
    print(f"`_temp_distance` 가 바뀐 행: {len(dist)}")

    rep_changed, val_changed = [], []
    for k in sorted(keys):
        ra, rb = a.get(k, []), b.get(k, [])
        if len(ra) < 2 and len(rb) < 2:
            continue
        ha = sorted(ra, key=_rep_rank)[0] if ra else None
        hb = sorted(rb, key=_rep_rank)[0] if rb else None
        if ha is None or hb is None or ha.id == hb.id:
            continue
        rep_changed.append((k, ha, hb))
        if ha.value_num != hb.value_num:
            val_changed.append((k, ha, hb))
    print(f"\n대표행이 바뀐 군 {len(rep_changed)} · 그중 **값이 실제로 달라지는 군** "
          f"{len(val_changed)}")
    for k, ha, hb in rep_changed:
        mark = "  ← 값이 바뀐다" if ha.value_num != hb.value_num else "  (값 같음)"
        print(f"  재료{k[0]} {k[1]}")
        print(f"     전 pv{ha.id} t{ha.quality_tier} {ha.value_num} "
              f"거리 {_temp_distance(ha.conditions):.2f}")
        print(f"     후 pv{hb.id} t{hb.quality_tier} {hb.value_num} "
              f"거리 {_temp_distance(hb.conditions):.2f}{mark}")

    # 카드 태그 — 새 태그가 붙는 행을 센다(사라지는 태그가 있으면 그것이 결함이다).
    gained, lost = 0, 0
    for k in keys:
        bb = {x.id: x for x in b.get(k, [])}
        for r in a.get(k, []):
            if r.id not in bb:
                continue
            ta, tb = _cond_tag(r.conditions), _cond_tag(bb[r.id].conditions)
            if ta == tb:
                continue
            if "T " in tb and "T " not in ta:
                gained += 1
            elif "T " in ta and "T " not in tb:
                lost += 1
    print(f"\n카드 조건 태그 — 온도 태그가 새로 붙은 행 {gained} · **사라진 행 {lost}**")


if __name__ == "__main__":
    main()
