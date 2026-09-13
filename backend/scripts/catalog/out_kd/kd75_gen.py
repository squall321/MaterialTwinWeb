#!/usr/bin/env python3
# 75차 KD 산출물 생성기 — 캡션만 남은 표를 코퍼스 전역에서 세고, 우리 빈칸과 겹치는 것을
# 원본 PDF 렌더로 복구한 결과를 파일로 굳힌다. 라이브 DB 는 읽기 전용으로만 만진다.
from __future__ import annotations

import collections
import csv
import json
import os
import re
import sqlite3
import subprocess
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
CORPUS = "/data/paper_patent_corpus"
STRUCT = os.path.join(CORPUS, "structured")
DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                                 "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
                  "materialtwin.db")

CORE7 = ["physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
         "thermal.expansion_linear", "thermal.conductivity", "thermal.specific_heat",
         "mechanical.tensile_strength"]
VERDICT_ATTRS = ["core_not_applicable", "core_absent_from_vendor_sheet",
                 "core_rejected_printed_value", "core_no_public_document"]

NUM = re.compile(r"\d")
# 「물성을 약속하는 캡션」 — 복구 우선순위를 매기는 데만 쓴다. 판정 근거로 쓰지 않는다.
PROP_CAPTION = re.compile(
    r"materi\w* propert|propert\w* of|mechanical propert|thermal propert|physical propert"
    r"|elastic|modulus|CTE|thermal expansion|conductivit|specific heat|density|poisson"
    r"|tensile|物性|特性|材料特性|parameters used|material constant|properties used", re.I)


# ---------------------------------------------------------------- ① 코퍼스 전역 계수
def scan_tables() -> list[dict]:
    """`tables/*.md` 를 전수로 읽어 파일마다 판별 지표를 낸다.

    지표를 하나만 쓰지 않는 이유는 보고서 ⑥에 적었다 — `|` 유무는 **필요조건이지
    충분조건이 아니다.** 셀은 있는데 숫자가 한 칸도 없는 표도 물성 출처가 못 된다.
    """
    out = []
    for root, _dirs, files in os.walk(STRUCT):
        if os.path.basename(root) != "tables":
            continue
        for f in files:
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            b = open(p, "rb").read()
            t = b.decode("utf-8", "replace")
            lines = t.splitlines()
            nonempty = [l for l in lines if l.strip()]
            pipe = data = cells = numcells = 0
            for l in lines:
                if "|" not in l:
                    continue
                pipe += 1
                s = l.strip()
                if s.replace("|", "").replace("-", "").replace(":", "").replace(" ", "") == "":
                    continue                                   # 구분선
                data += 1
                for c in (x.strip() for x in s.strip("|").split("|")):
                    cells += 1
                    if NUM.search(c):
                        numcells += 1
            out.append(dict(p=p, dom=os.path.relpath(p, STRUCT).split("/")[0],
                            size=len(b), lines=len(nonempty), pipe=pipe, data=data,
                            cells=cells, numcells=numcells,
                            head=(nonempty[0][:160] if nonempty else "")))
    return out


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    dom = collections.defaultdict(lambda: dict(tables=0, no_pipe=0, no_datarow=0,
                                               no_numeric_cell=0, zero_byte=0))
    for r in rows:
        d = dom[r["dom"]]
        d["tables"] += 1
        if r["pipe"] == 0:
            d["no_pipe"] += 1
        if r["data"] == 0:
            d["no_datarow"] += 1
        if r["numcells"] == 0:
            d["no_numeric_cell"] += 1
        if r["size"] == 0:
            d["zero_byte"] += 1
    return dict(
        total_tables=n,
        criterion_A_no_pipe=sum(1 for r in rows if r["pipe"] == 0),
        criterion_B_no_data_row=sum(1 for r in rows if r["data"] == 0),
        criterion_C_no_numeric_cell=sum(1 for r in rows if r["numcells"] == 0),
        criterion_D_no_digit_anywhere=sum(1 for r in rows if not NUM.search(r["head"]) and r["numcells"] == 0 and r["pipe"] == 0),
        zero_byte=sum(1 for r in rows if r["size"] == 0),
        by_domain=dict(sorted(dom.items(), key=lambda kv: -kv[1]["no_pipe"])))


# ---------------------------------------------------------------- ② 우리 빈칸
def open_core_cells(c: sqlite3.Connection) -> dict[int, list[str]]:
    """값도 판정도 없는 코어7 칸(V5). `role == product` 인 카드만 센다."""
    have = collections.defaultdict(set)
    for m, k in c.execute("select distinct material_id,property_key from property_value"):
        have[m].add(k)
    out = {}
    for i, n, a in c.execute("select id,name,attributes from material"):
        at = json.loads(a or "{}")
        if at.get("role") != "product":
            continue
        verd = set()
        for vk in VERDICT_ATTRS:
            if isinstance(at.get(vk), dict):
                verd |= set(at[vk])
        miss = [k for k in CORE7 if k not in have[i] and k not in verd]
        if miss:
            out[i] = miss
    return out


# ---------------------------------------------------------------- 자체검증
def self_check(verdicts: dict, c: sqlite3.Connection) -> None:
    keys = {k for (k,) in c.execute("select key from property_definition")}
    names = {i: n for i, n in c.execute("select id,name from material")}
    openc = open_core_cells(c)
    bad = []
    for v in verdicts["verdicts"]:
        mid = v["material_id"]
        if mid not in names:
            bad.append(f"없는 material_id {mid}")
            continue
        if v.get("name") != names[mid]:
            bad.append(f"{mid} 이름 불일치: {v.get('name')!r} != {names[mid]!r}")
        for attr, body in v.items():
            if attr in ("material_id", "name"):
                continue
            if attr not in VERDICT_ATTRS:
                bad.append(f"{mid} 허용되지 않은 판정 키 {attr}")
                continue
            if not isinstance(body, dict):
                bad.append(f"{mid}.{attr} 이 dict 가 아니다 — 집계가 못 읽는다")
                continue
            for k, reason in body.items():
                if k not in keys:
                    bad.append(f"{mid}.{attr} 물성 정의에 없는 키 {k}")
                if not isinstance(reason, str) or len(reason) < 80:
                    bad.append(f"{mid}.{attr}.{k} 사유가 없거나 너무 짧다")
                # 이 배치는 **V5 인 칸만** 닫는다. 이미 값이나 판정이 있는 칸은 건드리지 않는다.
                if k not in openc.get(mid, []):
                    bad.append(f"{mid}.{attr}.{k} 는 V5 가 아니다 — 덮어쓰지 마라")
    if bad:
        raise SystemExit("자체검증 실패:\n  " + "\n  ".join(bad))
    print(f"[self-check] 판정 {sum(len(b) for v in verdicts['verdicts'] for a,b in v.items() if isinstance(b,dict))}칸 · 오류 0")


def main() -> int:
    rows = scan_tables()
    summ = summarise(rows)
    json.dump(summ, open(os.path.join(OUT, "kd75_01_corpus_caption_only_scan.json"), "w"),
              ensure_ascii=False, indent=1)
    print("[①] 표 %d장 중 `|` 없음 %d장 (%.1f%%) · 0바이트 %d장"
          % (summ["total_tables"], summ["criterion_A_no_pipe"],
             100 * summ["criterion_A_no_pipe"] / summ["total_tables"], summ["zero_byte"]))

    # 복구 우선순위 표 — 캡션이 물성을 약속하는 캡션만 표
    lost = [r for r in rows if r["pipe"] == 0]
    cand = [r for r in lost if PROP_CAPTION.search(r["head"])]
    with open(os.path.join(OUT, "kd75_02_priority_targets.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["domain", "table_md", "caption", "doc_dir"])
        for r in sorted(cand, key=lambda r: (r["dom"], r["p"])):
            w.writerow([r["dom"], os.path.relpath(r["p"], STRUCT), r["head"],
                        os.path.relpath(os.path.dirname(os.path.dirname(r["p"])), STRUCT)])
    print("[①] 물성을 약속하는 캡션만 표 %d장 → kd75_02_priority_targets.csv" % len(cand))

    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)          # 읽기 전용
    openc = open_core_cells(c)
    print("[②] V5(값도 판정도 없는) 코어7 칸 %d개 / 재료 %d종"
          % (sum(len(v) for v in openc.values()), len(openc)))

    verdicts = json.load(open(os.path.join(OUT, "kd75_09_verdicts.json")))
    self_check(verdicts, c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
