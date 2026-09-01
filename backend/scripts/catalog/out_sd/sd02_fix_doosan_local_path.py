#!/usr/bin/env python3
# Doosan 제품 페이지 15종의 `source.local_path` 를 전제품 TDS PDF 에서 **제품 페이지 HTML** 로 옮긴다.
#
# 왜 — 값은 제품 페이지에서 읽었는데 경로가 전제품 TDS v9 를 가리켰다(54차 PB 가 잡고 56차 RC 가 확인).
# 그 TDS 는 55등급을 싣는데 **이 15등급은 거기 없다.** 경로를 따라가면 아무것도 안 나오는
# 322행의 계보가 끊긴 상태였다. `url` 은 처음부터 옳았다 — 틀린 것은 `local_path` 뿐이다.
#
# **값은 건드리지 않는다.** 경로 한 칸만 바꾼다.
# 사용:  sd02_fix_doosan_local_path.py [--apply]
from __future__ import annotations

import argparse
import os
import sqlite3

DB = os.path.join(
    os.environ.get("MATERIALTWIN_DATA_DIR",
                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
    "materialtwin.db")
DEST = "/data/paper_patent_corpus/standards_appnotes/pcb"
STAMP = "2026-09-01"

# source_id → 제품 페이지 URL 슬러그. 슬러그는 DB 의 `url` 에서 그대로 왔다.
SLUG = {
    4612: "DS-7409DYN", 4613: "DS-7409DYN2", 4614: "DS-7409DYQ",
    4615: "DS-7409HG", 4619: "DS-7409HG_KNF", 4631: "DS-9000",
    4632: "DSF-900HT", 4639: "DSflex-600DI", 4640: "DSflex-600G",
    4641: "DSflex-600H", 4642: "DSflex-600HF", 4643: "DSflex-600LUF",
    4647: "DSflex-900L", 4648: "DSflex-900U", 4649: "DSflex-900UM",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    c = sqlite3.connect(DB)
    print(f"[DB] {DB}")
    n_row = n_src = 0
    for sid, slug in sorted(SLUG.items()):
        got = c.execute("select url,local_path from source where id=?", (sid,)).fetchone()
        if not got:
            print(f"  ✗ 없는 source {sid}")
            continue
        url, old = got
        if not url.endswith("/" + slug):
            print(f"  ✗ {sid} url 이 슬러그와 다르다 — {url}")
            continue
        new = f"{DEST}/Doosan_CCL_{slug}_ProductPage_en_{STAMP}.html"
        if not os.path.exists(new):
            print(f"  ✗ {sid} 코퍼스에 파일이 없다 — {new}")
            continue
        rows = c.execute("select count(*) from property_value where source_id=?",
                         (sid,)).fetchone()[0]
        n_row += rows
        if old == new:
            print(f"  · {sid} 이미 옳다")
            continue
        n_src += 1
        print(f"  · [{sid}] {slug:16s} {rows:3d}행  {os.path.basename(old or '(없음)')} "
              f"→ {os.path.basename(new)}")
        if a.apply:
            c.execute("update source set local_path=? where id=?", (new, sid))
    if a.apply:
        c.commit()
        print(f"\n[적용됨] 출처 {n_src}종 · 그 출처가 받치는 값 {n_row}행")
    else:
        print(f"\n[예행] 출처 {n_src}종 · 그 출처가 받치는 값 {n_row}행 — --apply 를 붙이면 쓴다")
    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
