#!/usr/bin/env python3
# 배치가 낸 재료 역할 분류(product/evidence)를 material.attributes 에 적용한다.
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    have = {i: (n, at) for i, n, at in
            c.execute("select id,name,attributes from material")}
    print(f"[DB] {DB}\n     재료 {len(have)}종")

    rows: list[dict] = []
    for p in a.paths:
        doc = json.load(open(p))
        rows += doc.get("classification", doc if isinstance(doc, list) else [])
    print(f"     분류 입력 {len(rows)}건")

    st = Counter()
    seen: set[int] = set()
    for r in rows:
        mid, role = r.get("material_id"), r.get("role")
        if mid not in have:
            st["없는 재료"] += 1
            print(f"  ✗ 없는 material_id {mid} — {str(r.get('name'))[:60]}")
            continue
        if role not in ("product", "evidence"):
            st["역할 어휘 밖"] += 1
            print(f"  ✗ role={role!r} — {have[mid][0][:60]}")
            continue
        # **이름 대조는 필수다.** id 만 믿으면 배치가 옛 목록으로 작업했을 때 엉뚱한 재료를 친다.
        if r.get("name") and r["name"].strip() != have[mid][0].strip():
            st["이름 불일치"] += 1
            print(f"  ✗ 이름 불일치 id={mid}\n      DB: {have[mid][0][:70]}\n      입력: {r['name'][:70]}")
            continue
        if mid in seen:
            st["중복"] += 1
            continue
        seen.add(mid)
        st[role] += 1
        if not a.apply:
            continue
        at = json.loads(have[mid][1] or "{}") or {}
        at["role"] = role
        if r.get("reason"):
            at["role_reason"] = r["reason"][:300]
        if r.get("confidence"):
            at["role_confidence"] = r["confidence"]
        if r.get("note"):
            at["role_note"] = r["note"][:300]
        c.execute("update material set attributes=? where id=?",
                  (json.dumps(at, ensure_ascii=False), mid))

    missing = set(have) - seen
    for k, v in st.items():
        print(f"  {k}: {v}")
    # **빠진 재료는 조용히 product 로 남는다** — 그게 안전한 기본값이지만 몇 종인지는 알려야 한다.
    print(f"  분류 안 된 재료: {len(missing)}종 (role 미설정 = 격자에 남는다)")
    if missing and len(missing) <= 25:
        for m in sorted(missing):
            print(f"      [{m}] {have[m][0][:74]}")

    if a.apply:
        c.commit()
        print("[APPLY] 적용했다")
    else:
        print("[DRY-RUN] --apply 를 붙이면 적용한다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
