#!/usr/bin/env python3
# 64차 ZB 가 조달했으나 코퍼스에 못 넣은 문서 열 장의 `source.local_path` 를 채운다(§626 규율 4).
#
# 왜 — ZB 는 이 세션의 쓰기 권한이 막혀 `/data/paper_patent_corpus/...` 에 복사하지 못했고
#      `local_path` 를 비운 채 인계했다. 65차 AD 는 쓰기가 열려 있어 열 장을 전부 넣었다.
#      비어 있으면 다음 파동이 같은 문서를 다시 받는다(§4 — 경로는 글자 단위로 같게).
#
# **값은 한 칸도 안 건드린다.** `source.local_path` 한 칸만 채우고, 이미 차 있으면 덮지 않는다.
# 사용:  ad05_fill_source_local_path.py [--apply]
from __future__ import annotations

import argparse
import os
import sqlite3

DB = os.path.join(
    os.environ.get("MATERIALTWIN_DATA_DIR",
                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
    "materialtwin.db")
DEST = "/data/paper_patent_corpus/standards_appnotes/mech"

# source_id → (url 끝조각으로 검산할 문자열, 코퍼스 파일명)
PLAN = {
    4826: ("kiyomine.co.jp/product/nickel/", "Kiyomine_NickelSilver_product_page_ja_2026-09.html"),
    4827: ("alloys.copper.org/alloy/C75200", "CDA_alloys_C75200_NickelSilver_65-18.html"),
    4828: ("tokkin.co.jp/search/non-ferrous/copper-alloys/c7701/",
           "TOKKIN_C7701_SpringNickelSilver_product_page_ja_2026-09.html"),
    4829: ("banjou/result/bjr001007.pdf", "JCBA_banjou_bjr001007_Table1-2_MechProps_C7701.pdf"),
    4830: ("banjou/result/bjr002001.pdf", "JCBA_banjou_bjr002001_Table2-2_FatigueFractureStress.pdf"),
    4831: ("tokkin.co.jp/search/non-ferrous/copper-alloys/c5210/",
           "TOKKIN_C5210_SpringPhosphorBronze_product_page_ja_2026-09.html"),
    4832: ("alloys.copper.org/alloy/C52100", "CDA_alloys_C52100_PhosphorBronze_8pct_C.html"),
    4833: ("banjou/result/bjr001005.pdf", "JCBA_banjou_bjr001005_Table1-2_MechProps_C5210.pdf"),
    4834: ("dowa-metaltech.co.jp/products/ycut-m/",
           "DOWA_Metaltech_YCuT-M_TitaniumCopper_product_page_ja_2026-09.html"),
    4835: ("banjou/result/bjr001006.pdf", "JCBA_banjou_bjr001006_Table1-2_MechProps_C1720_C1990.pdf"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    c = sqlite3.connect(DB)
    print(f"[DB] {DB}")
    n_src = n_row = 0
    for sid, (frag, fname) in sorted(PLAN.items()):
        got = c.execute("select url,local_path from source where id=?", (sid,)).fetchone()
        if not got:
            print(f"  ✗ 없는 source {sid}")
            continue
        url, old = got
        if frag not in (url or ""):
            print(f"  ✗ {sid} url 이 계획과 다르다 — {url}")
            continue
        new = os.path.join(DEST, fname)
        if not os.path.exists(new):
            print(f"  ✗ {sid} 코퍼스에 파일이 없다 — {new}")
            continue
        rows = c.execute("select count(*) from property_value where source_id=?", (sid,)).fetchone()[0]
        if old:
            print(f"  · {sid} 이미 차 있다 — 덮지 않는다 ({old})")
            continue
        n_src += 1
        n_row += rows
        print(f"  · [{sid}] {rows:3d}행  (없음) → {fname}")
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
