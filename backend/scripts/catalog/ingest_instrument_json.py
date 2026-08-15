#!/usr/bin/env python3
# 장비 카탈로그 배치가 낸 JSON을 instrument/instrument_capability로 적재한다(기본 dry-run).
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

DB = os.environ.get(
    "MATERIALTWIN_DB",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db",
)
CAT = {"thermal", "mechanical", "surface", "chemical", "particle",
       "optical", "electrical", "ndt", "reliability"}
CONF = {"high", "medium", "low"}


def _src(c, doc_path: str | None, title: str | None) -> int | None:
    """카탈로그 PDF를 datasheet 출처로 dedup 등록한다.

    **경로가 식별자다** — 같은 시리즈 브로슈어가 제목만 조금씩 다르게 인쇄되는 일이 흔해서
    제목으로 합치면 서로 다른 카탈로그가 뭉친다(브리프 22번의 반대 방향 위험).
    """
    if not doc_path:
        return None
    r = c.execute("select id from source where local_path=?", (doc_path,)).fetchone()
    if r:
        return r[0]
    c.execute(
        "insert into source(kind,title,local_path,retrieved_at) "
        "values('datasheet',?,?,datetime('now'))",
        (title or Path(doc_path).stem, doc_path),
    )
    return c.execute("select last_insert_rowid()").fetchone()[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    keys = {k for k, in c.execute("select key from property_definition")}
    print(f"[DB] {DB}\n     정의 {len(keys)}종 · 기존 장비 "
          f"{c.execute('select count(*) from instrument').fetchone()[0]}대")

    files: list[Path] = []
    for p in a.paths:
        pp = Path(p)
        files += sorted(pp.glob("*.json")) if pp.is_dir() else [pp]

    n_inst = n_cap = n_skip = 0
    for f in files:
        try:
            doc = json.load(open(f))
        except Exception as e:
            print(f"  ✗ {f.name}: JSON 파손 — {e}")
            continue
        if not (isinstance(doc, dict) and isinstance(doc.get("instruments"), list)):
            print(f"  · {f.name}: 장비 문서가 아니다(`instruments` 배열 없음) — 건너뛴다")
            continue

        for ins in doc["instruments"]:
            vendor, model = (ins.get("vendor") or "").strip(), (ins.get("model") or "").strip()
            cat = (ins.get("category") or "").strip()
            if not (vendor and model and cat in CAT):
                print(f"  ✗ 장비 식별 불가: vendor={vendor!r} model={model!r} category={cat!r}")
                n_skip += 1
                continue
            sid = _src(c, ins.get("doc_path"), ins.get("doc_title")) if a.apply else None
            row = c.execute(
                "select id from instrument where vendor=? and model=?", (vendor, model)
            ).fetchone()
            if row:
                iid = row[0]
            elif a.apply:
                c.execute(
                    "insert into instrument(vendor,model,category,technique,description,"
                    "doc_path,source_id,notes) values(?,?,?,?,?,?,?,?)",
                    (vendor, model, cat, ins.get("technique"), ins.get("description"),
                     ins.get("doc_path"), sid, ins.get("notes")),
                )
                iid = c.execute("select last_insert_rowid()").fetchone()[0]
                n_inst += 1
            else:
                iid = None
                n_inst += 1

            for cap in ins.get("capabilities") or []:
                k, tech = cap.get("property_key"), (cap.get("technique") or "").strip()
                if k not in keys:
                    print(f"  ✗ 미정의 키 {k!r} — {vendor} {model}")
                    n_skip += 1
                    continue
                if not tech:
                    print(f"  ✗ 기법 없음 — {vendor} {model} / {k}")
                    n_skip += 1
                    continue
                conf = cap.get("mapping_confidence") or "high"
                if conf not in CONF:
                    print(f"  ✗ 신뢰도 어휘 밖 {conf!r} — {vendor} {model} / {k}")
                    n_skip += 1
                    continue
                # **범위는 단위와 함께가 아니면 값이 아니다.** 숫자만 있으면 버린다.
                lo, hi, unit = cap.get("range_min"), cap.get("range_max"), cap.get("range_unit")
                if (lo is not None or hi is not None) and not unit:
                    print(f"  ✗ 범위에 단위 없음 — {vendor} {model} / {k} ({lo}~{hi})")
                    n_skip += 1
                    continue
                if lo is not None and hi is not None and lo > hi:
                    print(f"  ✗ 범위 역전 {lo} > {hi} — {vendor} {model} / {k}")
                    n_skip += 1
                    continue
                # **`insert or replace` 는 조용히 덮어쓴다.** 유니크 키가
                # (장비, 키, 기법)이라 **규격만 다른 행이 서로를 지운다** — 24차 Q 가 짚었다.
                # 규격이 여러 개면 한 행에 모아 적는 게 맞고, 정말 다른 측정이면 기법을 달리해라.
                if iid is not None:
                    prev = c.execute(
                        "select standard from instrument_capability "
                        "where instrument_id=? and property_key=? and technique=?",
                        (iid, k, tech),
                    ).fetchone()
                    if prev is not None and (prev[0] or "") != (cap.get("standard") or ""):
                        print(f"  ⚠ 덮어씀 — {vendor} {model} / {k} / {tech}: "
                              f"규격 {prev[0]!r} → {cap.get('standard')!r}. "
                              f"**규격이 여럿이면 한 행에 모아 적어라.**")
                n_cap += 1
                if not a.apply:
                    continue
                c.execute(
                    "insert or replace into instrument_capability(instrument_id,property_key,"
                    "technique,standard,range_min,range_max,range_unit,resolution,accuracy,"
                    "temperature_min_k,temperature_max_k,specimen,mapping_confidence,"
                    "source_detail,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (iid, k, tech, cap.get("standard"), lo, hi, unit, cap.get("resolution"),
                     cap.get("accuracy"), cap.get("temperature_min_k"),
                     cap.get("temperature_max_k"), cap.get("specimen"), conf,
                     cap.get("source_detail"), cap.get("notes")),
                )

    print(f"[{'APPLY' if a.apply else 'DRY-RUN'}] 장비 {n_inst} · 능력 {n_cap} · 거부 {n_skip}")
    if a.apply:
        c.commit()
    else:
        print("       --apply 를 붙이면 적용한다")
    return 0


if __name__ == "__main__":
    sys.exit(main())
