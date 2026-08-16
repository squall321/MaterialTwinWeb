#!/usr/bin/env python3
# 이미 채굴한 논문을 **DOI·경로·제목 세 축으로** 조회한다 — 선별기 앞단에 붙이는 도구.
#
# 왜 필요한가
#   브리프 226번(선별기 앞단에 DB 조회를 붙여라)을 지켰는데도 31차 AC 의 DOI 처리에서
#   **회수 1건 대 병합 15건**이 나왔다. 새로 캔 16편 중 15편이 이미 DB 에 있던 논문이다.
#   원인은 조회가 **제목 기반**이라서다 — 배치마다 제목 표기가 달라 안 걸린다
#   (저자 접두 · 저널명 접미 · 움라우트 · 부제 절단).
#
# 무엇이 다른가
#   ① DOI 를 최우선으로 본다(정규화: 소문자·공백제거·`https://doi.org/` 접두 제거).
#   ② `local_path` 의 **디렉터리명**으로 본다 — 코퍼스 경로가 곧 논문 식별자다.
#   ③ 제목은 **NFKD 분해 후 결합문자 제거**로 정규화한다(브리프 302번 — `Förster` 와 `Forster`).
#   ④ **"출처가 있다 ≠ 채굴됐다"**(222번) — `property_value` 행 수와 최소 등급을 함께 낸다.
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

DB = os.environ.get(
    "MATERIALTWIN_DB",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db",
)


def norm_doi(s: str | None) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"^https?://(dx\.)?doi\.org/", "", s)
    return re.sub(r"\s+", "", s)


def norm_title(s: str | None) -> str:
    """제목 정규화 — **NFKD 분해 후 결합문자를 지운다.**

    비영숫자를 그냥 지우면 `Förster` 가 `frster` 가 돼 `Forster` 와 안 맞는다(302번).
    저자 접두(`Kim, Lee (2020), `)와 저널명 접미(`, Journal of ...`)도 벗긴다.
    """
    s = s or ""
    m = re.match(r"^.*?\(\d{4}(?:/\d{4})?\),\s*(.+)$", s)
    if m:
        s = m.group(1)
    s = re.sub(r",\s*[A-Z][A-Za-z .&]+$", "", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())[:45]


def build(c: sqlite3.Connection) -> dict:
    """세 축의 색인을 만든다. 값은 (source_id, 행수, 최소등급)."""
    idx: dict[str, dict] = {"doi": {}, "path": {}, "title": {}}
    for sid, doi, title, lp in c.execute("select id,doi,title,local_path from source"):
        n, tier = c.execute(
            "select count(*), min(quality_tier) from property_value where source_id=?", (sid,)
        ).fetchone()
        rec = {"source_id": sid, "rows": n or 0, "min_tier": tier, "title": title}
        if doi:
            idx["doi"][norm_doi(doi)] = rec
        if lp:
            # 경로는 **디렉터리명**으로 본다 — 파일명에 확장자·중복 접미가 붙는다.
            idx["path"][Path(str(lp)).name.lower()] = rec
        if title:
            idx["title"].setdefault(norm_title(title), rec)
    return idx


def look(idx: dict, *, doi=None, path=None, title=None) -> dict | None:
    if doi and (r := idx["doi"].get(norm_doi(doi))):
        return {**r, "matched_by": "doi"}
    if path:
        key = Path(str(path)).name.lower()
        if r := idx["path"].get(key):
            return {**r, "matched_by": "path"}
        # md 파일 경로를 주면 부모 디렉터리가 논문 이름이다.
        if r := idx["path"].get(Path(str(path)).parent.name.lower()):
            return {**r, "matched_by": "path(parent)"}
    if title and (r := idx["title"].get(norm_title(title))):
        return {**r, "matched_by": "title"}
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="이미 채굴한 논문인지 DOI·경로·제목으로 조회")
    ap.add_argument("--doi")
    ap.add_argument("--path")
    ap.add_argument("--title")
    # 배치가 후보 목록을 통째로 넘겨 거르는 용도.
    ap.add_argument("--json", help="[{doi?,path?,title?}, ...] 파일 — 미채굴만 남겨 stdout 으로")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    idx = build(c)
    print(f"[DB] {DB}\n     출처 {len(idx['doi'])} DOI · {len(idx['path'])} 경로 · "
          f"{len(idx['title'])} 제목", file=sys.stderr)

    if a.json:
        items = json.load(open(a.json))
        out, hit = [], 0
        for it in items:
            r = look(idx, doi=it.get("doi"), path=it.get("path"), title=it.get("title"))
            # **행이 한둘이고 전부 tier3 이면 클래스 전이만 하고 논문은 안 판 것이다**(222번).
            mined = bool(r) and r["rows"] > 2 or (bool(r) and (r["min_tier"] or 9) <= 2)
            if mined:
                hit += 1
                continue
            out.append({**it, "_prior": r})
        print(f"     후보 {len(items)}건 중 **기채굴 {hit}건 제외** → {len(out)}건 남음",
              file=sys.stderr)
        json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
        return 0

    r = look(idx, doi=a.doi, path=a.path, title=a.title)
    print(json.dumps(r, ensure_ascii=False, indent=1) if r else "null")
    return 0


if __name__ == "__main__":
    sys.exit(main())
