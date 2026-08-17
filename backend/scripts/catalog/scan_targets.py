#!/usr/bin/env python3
# 다음 파동의 표적 논문을 뽑는다 — 기채굴(mined_index)과 **기폐기(정본 대장)** 를 둘 다 걸러서.
#
# 왜 필요한가
#   36차에 표적 목록을 손으로 만들었더니 **두 방향으로 틀렸다.**
#   ① 이미 캔 논문 셋(Ehrler 143행 · Fujishima 59행 · Narahashi 19행)이 목록에 올라
#      배치들이 중복 작업을 했다 — `mined_index` 결함이었고 고쳤다(브리프 407·410).
#   ② **판정하고 버린 논문 9편이 그대로 남았다.** 행이 0이니 기채굴 조회로는 영영 안 걸린다.
#      다음 파동이 열어서 읽고 같은 이유로 다시 버린다. 이쪽은 조회가 아니라 **기록**의 문제다.
#
# 그래서 폐기를 정본 대장 하나에 모은다 — `_index/_verdicts/discarded.jsonl`.
# 배치는 논문을 버릴 때마다 여기에 한 줄 덧붙인다(제목·파동·사유).
#
# **대장은 보수적으로 쓴다.** 거짓 폐기는 **논문을 잃고**, 놓친 폐기는 재발굴로 일만 낭비한다.
# 그래서 제목 정규화가 정확히 맞을 때만 거른다 — 접두·인용키 같은 느슨한 축은 안 쓴다.
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mined_index import DB as MT_DB, build, look, norm_title  # noqa: E402

CORPUS = "/data/paper_patent_corpus/_index/corpus_fts.db"
VERDICTS = Path("/data/paper_patent_corpus/_index/_verdicts/discarded.jsonl")


def load_verdicts() -> dict[str, dict]:
    """정본 폐기 대장을 읽는다. 키는 정규화 제목."""
    out: dict[str, dict] = {}
    if not VERDICTS.exists():
        return out
    for ln in VERDICTS.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if t := r.get("title"):
            out[norm_title(t)] = r
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="다음 파동 표적 추출 — 기채굴·기폐기를 걸러서")
    ap.add_argument("--min-keys", type=int, default=4, help="합집합 물성키 하한")
    ap.add_argument("--limit", type=int, default=0, help="0이면 전부")
    ap.add_argument("--out", help="JSON 저장 경로")
    a = ap.parse_args()

    idx = build(sqlite3.connect(MT_DB))
    verd = load_verdicts()
    cp = sqlite3.connect(CORPUS)
    rows = cp.execute(
        """select d.path, d.title, max(p.n_keys_union) nk, sum(p.n_num_rows) nr,
                  group_concat(distinct p.key) ks
             from ptab p join doc d on d.rowid = p.doc_id
            group by p.doc_id having nk >= ? order by nk desc, nr desc""",
        (a.min_keys,),
    ).fetchall()

    out, n_mined, n_disc, n_amb = [], 0, 0, 0
    for p, t, nk, nr, ks in rows:
        r = look(idx, path=p, title=t)
        if r and r.get("confidence") != "low" and (r["rows"] > 2 or (r["min_tier"] or 9) <= 2):
            n_mined += 1
            continue
        if (v := verd.get(norm_title(t))):
            n_disc += 1
            continue
        if r and r.get("ambiguous"):
            n_amb += 1
        out.append({"path": p, "title": t, "nk": nk, "nr": nr, "keys": ks,
                    "prior": r, "ambiguous": bool(r and r.get("ambiguous"))})

    print(f"[코퍼스] 합집합 {a.min_keys}키+ {len(rows)}편", file=sys.stderr)
    print(f"  기채굴 제외 {n_mined}편 · **기폐기 제외 {n_disc}편**(대장 {len(verd)}건)"
          f" → 표적 {len(out)}편", file=sys.stderr)
    if n_amb:
        print(f"  그중 {n_amb}편은 제목 충돌로 **모호** — 반드시 열어서 확인해라", file=sys.stderr)

    if a.limit:
        out = out[: a.limit]
    if a.out:
        json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
        print(f"  → {a.out}", file=sys.stderr)
    else:
        for u in out[:30]:
            print(f"  {u['nk']}키 {u['nr']:>4}행 | {os.path.basename(u['path'])[:78]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
