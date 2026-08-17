#!/usr/bin/env python3
# 폐기 대장의 건강 상태를 점검한다 — `integrity_check.py` 의 대장 판.
#
# 왜 필요한가
#   대장은 **여러 배치가 동시에 쓰는 파일**이다. 37차 AV 가 짚었다 —
#   읽어서 고쳐 쓰는(read-modify-write) 방식이면 병렬 파동이 서로를 덮어쓴다.
#   그리고 대장이 조용히 망가지면 **두 방향으로 손해**다:
#     · 줄이 헛돌면 → 버린 논문을 다음 파동이 다시 연다(일 낭비)
#     · 줄이 잘못 걸리면 → **멀쩡한 논문이 표적에서 사라진다**(논문을 잃는다, 418번)
#
# **규칙: 대장은 append-only 다.** 새 줄은 `>>` 로 덧붙여라. 기존 줄을 고쳐야 하면
# 다른 파동이 도는 중이 아닌지 확인하고, 고친 뒤 이 점검기를 돌려라.
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mined_index import DB as MT_DB  # noqa: E402
from scan_targets import CORPUS, VERDICTS, norm_full  # noqa: E402


def main() -> int:
    lines = [ln for ln in VERDICTS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    recs, bad = [], []
    for i, ln in enumerate(lines, 1):
        try:
            recs.append((i, json.loads(ln)))
        except json.JSONDecodeError as e:
            bad.append(f"{i}행 JSON 파싱 실패 — {e}")

    # 코퍼스·DB 조회 준비
    cp = sqlite3.connect(CORPUS)
    corp = {norm_full(t): p for p, t in cp.execute(
        "select path,title from doc where title is not null")}
    paths = set(corp.values())
    mt = sqlite3.connect(MT_DB)
    agg = {r[0]: r[1] for r in mt.execute(
        "select source_id,count(*) from property_value where source_id is not null group by 1")}
    rows: dict[str, int] = {}
    for sid, t in mt.execute("select id,title from source where title is not null"):
        k = norm_full(t)
        rows[k] = max(rows.get(k, 0), agg.get(sid, 0))

    seen, stale, conflict, nopath = set(), [], [], []
    for i, r in recs:
        t = r.get("title")
        if not t:
            bad.append(f"{i}행 title 없음")
            continue
        k = norm_full(t)
        if k in seen:
            bad.append(f"{i}행 제목 중복 — {t[:56]}")
        seen.add(k)
        # ① DB 에 값이 있는데 폐기로 적혔나 — **가장 위험한 오류다**
        if rows.get(k, 0) > 2:
            conflict.append(f"{i}행 — DB 값 {rows[k]}행이 있다: {t[:56]}")
        # ② 코퍼스의 어떤 논문과도 안 걸리나
        p = r.get("path")
        if p and p in paths:
            continue
        if k in corp:
            nopath.append(i)
            continue
        if not r.get("not_in_corpus"):
            stale.append(f"{i}행 — 코퍼스에 안 걸린다: {t[:56]}")

    print(f"대장 {len(lines)}줄 · 파싱 {len(recs)}")
    print(f"  path 있는 줄 {sum(1 for _, r in recs if r.get('path'))} / {len(recs)}")
    for lbl, xs in (("**치명 — DB 에 값이 있는데 폐기다**(418번)", conflict),
                    ("형식 오류", bad),
                    ("코퍼스에 안 걸린다 — `path` 를 박아라(428번)", stale)):
        if xs:
            print(f"\n✗ {lbl} {len(xs)}건")
            for x in xs[:8]:
                print(f"    {x}")
    if nopath:
        print(f"\n· 제목으로는 걸리지만 `path` 가 없는 줄 {len(nopath)}개 — "
              f"제목 표기가 흔들리면 죽는다. 채워 두는 편이 안전하다")
    n = len(conflict) + len(bad) + len(stale)
    print(f"\n{'✔ 이상 0개' if n == 0 else f'✗ 이상 {n}개'}")
    return 1 if conflict or bad else 0


if __name__ == "__main__":
    sys.exit(main())
