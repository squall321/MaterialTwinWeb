# /data/paper_patent_corpus 전문(md) 16,000편을 SQLite FTS5로 색인하고 검색한다.
#
# 왜 어휘검색인가
#   코퍼스에 이미 Qdrant 벡터 인덱스가 있지만, 우리가 찾는 것은 "비슷한 주제의 논문"이 아니라
#   **인쇄된 숫자**다 — `activation energy`, `kJ/mol`, `365 nm`, `Table 3`. 의미검색은 이걸 못 집는다.
#   물성 수집은 정확 문자열 검색과 근접 문맥이 전부다.
#
# 왜 제목으로 중복을 제거하나
#   44,966개 md 중 고유 논문은 16,007편이다. snowball_papers가 다른 분야에서 같은 논문을
#   다시 받아 왔다. 중복을 남기면 같은 값을 두 번 넣고 tier가 어긋난다.
#
# 사용
#   build                        색인 생성(약 3분)
#   search "<FTS 질의>" [-n 20] [-d materials_papers] [-r "정규식"]
#   near "<FTS 질의>" -r "정규식"   질의로 좁힌 뒤 정규식이 걸린 줄만 문맥과 함께 출력
from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys

ROOT = "/data/paper_patent_corpus/structured"
DB = "/data/paper_patent_corpus/_index/corpus_fts.db"
# snowball은 다른 분야에서 재수집한 사본이라 원본 디렉터리를 우선한다.
_PREF = ("materials_papers", "mech_papers", "rel_papers", "pkg_papers", "elec_papers",
         "cae_papers", "expert_papers", "smartphone_pcb", "standards_appnotes")


def _title_key(fname: str) -> str:
    """'Author - 2004 - Title' 파일명에서 제목만 뽑아 소문자로."""
    m = re.match(r"^(.*?) - (\d{4}) - (.*)$", fname)
    return (m.group(3) if m else fname).strip().lower()


def _meta(fname: str) -> tuple[str, str]:
    m = re.match(r"^(.*?) - (\d{4}) - (.*)$", fname)
    return (m.group(1), m.group(2)) if m else ("", "")


def build() -> None:
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    if os.path.exists(DB):
        os.remove(DB)
    c = sqlite3.connect(DB)
    c.executescript("""
        pragma journal_mode=off; pragma synchronous=off;
        create table doc(id integer primary key, path text, title text,
                         author text, year text, domain text, subdir text);
        create virtual table ft using fts5(title, body, content='');
    """)
    # 제목 → (우선순위, 경로). 낮은 우선순위 숫자가 이긴다.
    best: dict[str, tuple[int, str, str]] = {}
    for dp, _dn, fn in os.walk(ROOT):
        for f in fn:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), ROOT)
            dom = rel.split(os.sep, 1)[0]
            pri = _PREF.index(dom) if dom in _PREF else len(_PREF)
            k = _title_key(f[:-3])
            if k not in best or pri < best[k][0]:
                best[k] = (pri, os.path.join(dp, f), rel)
    print(f"고유 논문 {len(best)}편 — 색인 시작", file=sys.stderr)

    n = 0
    for k, (_pri, path, rel) in best.items():
        try:
            body = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        fname = os.path.basename(path)[:-3]
        author, year = _meta(fname)
        parts = rel.split(os.sep)
        c.execute("insert into doc(path,title,author,year,domain,subdir) values(?,?,?,?,?,?)",
                  (path, fname, author, year, parts[0], parts[1] if len(parts) > 2 else ""))
        c.execute("insert into ft(rowid,title,body) values(?,?,?)",
                  (c.execute("select last_insert_rowid()").fetchone()[0], fname, body))
        n += 1
        if n % 2000 == 0:
            c.commit()
            print(f"  {n}편", file=sys.stderr)
    c.commit()
    c.execute("create index doc_dom on doc(domain)")
    c.commit()
    print(f"완료: {n}편 → {DB}", file=sys.stderr)


def _rows(c, query: str, domain: str | None, limit: int):
    sql = ("select d.id,d.title,d.domain,d.subdir,d.path from ft "
           "join doc d on d.id=ft.rowid where ft match ?")
    args: list = [query]
    if domain:
        sql += " and d.domain=?"
        args.append(domain)
    sql += " order by rank limit ?"
    args.append(limit)
    return c.execute(sql, args).fetchall()


def search(query: str, domain: str | None, limit: int, rx: str | None) -> None:
    c = sqlite3.connect(DB)
    pat = re.compile(rx, re.I) if rx else None
    shown = 0
    for _i, title, dom, sub, path in _rows(c, query, domain, limit * 4 if pat else limit):
        if pat:
            try:
                body = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if not pat.search(body):
                continue
        print(f"[{dom}/{sub}] {title}")
        print(f"    {path}")
        shown += 1
        if shown >= limit:
            break
    if not shown:
        print("(적중 없음)")


def near(query: str, domain: str | None, limit: int, rx: str, ctx: int) -> None:
    """질의로 문서를 좁힌 뒤, 정규식이 걸린 줄을 앞뒤 문맥과 함께 낸다.

    **값을 옮기기 전에 원문 문장을 눈으로 보게 하는 것**이 목적이다 —
    검색 결과만 보고 넣으면 표의 인접 열을 그대로 오독한다.
    """
    c = sqlite3.connect(DB)
    pat = re.compile(rx, re.I)
    hit_docs = 0
    for _i, title, dom, sub, path in _rows(c, query, domain, limit * 6):
        try:
            lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        hits = [j for j, ln in enumerate(lines) if pat.search(ln)]
        if not hits:
            continue
        hit_docs += 1
        print(f"\n══ [{dom}/{sub}] {title}\n   {path}")
        for j in hits[:6]:
            lo, hi = max(0, j - ctx), min(len(lines), j + ctx + 1)
            for m in range(lo, hi):
                mark = ">>" if m == j else "  "
                print(f"   {mark} {lines[m][:190]}")
            print("   " + "-" * 60)
        if hit_docs >= limit:
            break
    if not hit_docs:
        print("(적중 없음)")


def doi_of(title: str) -> tuple[str | None, str | None]:
    """논문 제목으로 DOI를 되찾는다 — `(doi, 근거경로)`.

    두 곳을 본다. `catalog.csv`(8,047행 중 7,788건이 DOI 보유)를 먼저 보고,
    없으면 그 논문 폴더의 `document.docling.json`에서 뽑는다.
    **인제스트가 만든 journal 출처는 DOI가 비기 쉬운데**, 원문이 디스크에 있으므로
    웹에 물어볼 필요가 없다.
    """
    import csv
    import io

    def _n(s):
        s = re.sub(r"[^a-z0-9]+", " ", (s or "").lower())
        return re.sub(r"\s+", " ", s).strip()

    tk = _n(title)
    try:
        for r in csv.DictReader(io.open("/data/paper_patent_corpus/catalog.csv",
                                        encoding="utf-8-sig")):
            if r.get("doi") and _n(r.get("title"))[:55] == tk[:55]:
                return r["doi"], "catalog.csv"
    except OSError:
        pass
    c = sqlite3.connect(DB)
    for path, in c.execute("select path from doc"):
        if _n(os.path.basename(path)[:-3])[-len(tk[:55]):] and tk[:50] in _n(os.path.basename(path)[:-3]):
            j = os.path.join(os.path.dirname(path), "document.docling.json")
            if os.path.exists(j):
                try:
                    blob = open(j, encoding="utf-8", errors="replace").read(400_000)
                except OSError:
                    continue
                m = re.search(r"10\.[0-9]{4,9}/[^\"'\\ ,]{4,60}", blob)
                if m:
                    return m.group(0).rstrip(".;"), j
    return None, None


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    p = sub.add_parser("doi")
    p.add_argument("title")
    for name in ("search", "near"):
        p = sub.add_parser(name)
        p.add_argument("query")
        p.add_argument("-n", "--limit", type=int, default=20)
        p.add_argument("-d", "--domain")
        p.add_argument("-r", "--regex", default=None)
        p.add_argument("-c", "--ctx", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "build":
        build()
    elif a.cmd == "doi":
        d, where = doi_of(a.title)
        print(f"{d}\t{where}" if d else "(못 찾음)")
    elif a.cmd == "search":
        search(a.query, a.domain, a.limit, a.regex)
    else:
        if not a.regex:
            ap.error("near 는 -r 정규식이 필요하다")
        near(a.query, a.domain, a.limit, a.regex, a.ctx)


if __name__ == "__main__":
    main()
