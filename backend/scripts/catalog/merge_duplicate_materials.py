#!/usr/bin/env python
# 같은 제품이 다른 이름으로 두 번 등록된 재료를 하나로 병합. 물성값·시편을 대표 재료로 옮긴다.
#
# 사용: merge_duplicate_materials.py [--apply]
#
# 수집이 여러 라운드로 나뉘다 보니 같은 제품을 서술어만 달리해 다시 등록하는 일이 생긴다
# (예: "Rogers RO4003C High-Frequency Laminate" / "Rogers RO4003C Hydrocarbon-Ceramic Laminate").
# 이름 정규화로는 안 잡히므로 **제품코드**로 묶는다.
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import defaultdict

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"

# 벤더 제품코드 패턴. 서술어가 달라도 코드가 같으면 같은 제품이다.
CODE = re.compile(
    r"\b(?:RO|RT|TLY|TLX|TSM|CLTE|CGN|CGS|MT|IT|TU|NP|MEGTRON|ULTRALAM)-?\d{1,5}[A-Z]*\b", re.I)


def codes_of(name: str) -> tuple:
    return tuple(sorted({m.group(0).upper().replace("-", "") for m in CODE.finditer(name)}))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    groups: dict[tuple, list] = defaultdict(list)
    for mid, name in c.execute("select id, name from material"):
        k = codes_of(name)
        if k:
            groups[k].append((mid, name))

    merged = moved = removed = 0
    for k, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        # 대표는 물성값이 많은 쪽, 동수면 id가 작은 쪽(먼저 만들어진 것).
        scored = []
        for mid, name in members:
            n = c.execute("select count(*) from property_value where material_id=?", (mid,)).fetchone()[0]
            sp = c.execute("select count(*) from specimen where material_id=?", (mid,)).fetchone()[0]
            scored.append((n + sp * 100, -mid, mid, name, n))
        scored.sort(reverse=True)
        keep_id, keep_name = scored[0][2], scored[0][3]
        print(f"  {'/'.join(k)}  → 대표 #{keep_id} {keep_name[:46]}")
        for _, _, mid, name, n in scored[1:]:
            print(f"      흡수 #{mid} {name[:46]:46s} 물성 {n}")
            if a.apply:
                c.execute("update property_value set material_id=? where material_id=?", (keep_id, mid))
                c.execute("update specimen set material_id=? where material_id=?", (keep_id, mid))
                c.execute("delete from material where id=?", (mid,))
                moved += n
                removed += 1
        merged += 1

    if a.apply:
        c.commit()
    print(f"\n{'[APPLIED]' if a.apply else '[DRY-RUN]'} 병합 묶음 {merged} / 흡수된 재료 {removed} / 이동 물성 {moved}")
    print(f"재료 수: {c.execute('select count(*) from material').fetchone()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
