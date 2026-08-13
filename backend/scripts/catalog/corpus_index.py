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
from collections import Counter

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


# 물성표 탐지용 신호 — (라벨 정규식, 단위 정규식, 카탈로그 키).
# **라벨만 보면 안 된다.** 본문에 'modulus'라는 단어가 있는 것과 표에 숫자가 실린 것은 다르다.
# 라벨과 단위가 같은 표 안에 함께 있고 숫자가 있을 때만 물성표로 친다.
_SIG = [
    (r"young|elastic modulus|tensile modulus|모듈러스|\bE\b", r"\b(GPa|MPa|N/mm)", "youngs_modulus"),
    (r"poisson|포아송", r"0\.[0-9]{2}", "poisson_ratio"),
    (r"density|밀도", r"(g/cm|kg/m|g cm)", "density"),
    (r"thermal expansion|\bCTE\b|expansion coeff", r"(ppm|10\s?[-−]\s?6|/K|/°C|K\s?-1)", "expansion_linear"),
    (r"thermal conductivity|열전도", r"W/\(?m", "conductivity"),
    (r"specific heat|비열|heat capacity", r"J/\(?(kg|g)", "specific_heat"),
    (r"tensile strength|인장강도", r"\b(MPa|GPa)", "tensile_strength"),
    (r"yield strength|항복", r"\b(MPa|GPa)", "yield_strength"),
    (r"elongation|연신", r"%", "elongation_at_break"),
    (r"dielectric constant|permittivity|유전율|Dk\b", r"[0-9]\.[0-9]", "dielectric_constant"),
    (r"loss tangent|dissipation factor|\bDf\b|tan\s?δ", r"0\.0", "dissipation_factor"),
    (r"glass transition|\bTg\b", r"(°C|K\b)", "glass_transition"),
    (r"refractive index|굴절률", r"1\.[0-9]{2}", "refractive_index"),
    (r"resistivity|저항률", r"(Ω|ohm)", "resistivity_volume"),
    (r"transmittance|투과율", r"%", "transmittance"),
    # 17차 추가 — 배치 둘이 "이 키들은 -k로 못 찾는다"고 보고했다. 없는 것을 부재로 읽지 않도록 넓힌다.
    (r"fracture toughness|K\s?_?ic\b|파괴인성", r"MPa\s?[·. ]?\s?m|MPa\s?m\^?0?\.?5", "fracture_toughness"),
    (r"hardness|경도|\bHv?\b", r"(GPa|HV|kgf/mm|Shore)", "hardness"),
    (r"weibull|와이블", r"m\s?=|modulus", "weibull_modulus"),
    (r"contact angle|접촉각", r"(°|deg)", "contact_angle_water"),
    (r"surface energy|surface tension|표면에너지", r"(mN/m|mJ/m|dyne)", "surface_energy"),
    (r"viscosity|점도", r"(Pa[·. ]?s|cP|mPa)", "viscosity"),
    (r"(peel|lap shear|die shear|adhesion) strength|박리|전단강도", r"(N/mm|N/m\b|MPa|kgf)", "interface_strength"),
    (r"flexural strength|굽힘강도|modulus of rupture|\bMOR\b", r"\b(MPa|GPa)", "flexural_strength"),
]


def _tables(text: str):
    """마크다운 표 블록을 통째로 뽑는다(연속된 `|` 줄)."""
    buf, out = [], []
    for ln in text.splitlines():
        if ln.lstrip().startswith("|"):
            buf.append(ln)
        else:
            if len(buf) >= 3:
                out.append("\n".join(buf))
            buf = []
    if len(buf) >= 3:
        out.append("\n".join(buf))
    return out


def scan_build() -> None:
    """물성표 적중을 **색인에 한 번 구워 둔다.** 전수 스캔이 8분 걸려 매번 돌릴 수 없다.

    이후 `tables` 조회는 SQL 한 방이라 즉시 끝난다.
    """
    c = sqlite3.connect(DB)
    c.executescript("drop table if exists ptab;"
                    "create table ptab(doc_id integer, key text, n_in_table integer);")
    n = 0
    for did, path in c.execute("select id,path from doc").fetchall():
        try:
            body = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "|" not in body:
            continue
        best: set = set()
        for tb in _tables(body):
            low = tb.lower()
            hits = {k for lab, un, k in _SIG
                    if re.search(lab, low, re.I) and re.search(un, tb, re.I)}
            if len(hits) > len(best):
                best = hits
        if best:
            c.executemany("insert into ptab values(?,?,?)",
                          [(did, k, len(best)) for k in best])
            n += 1
        if n and n % 2000 == 0:
            c.commit()
            print(f"  {n}편", file=sys.stderr)
    c.commit()
    c.execute("create index ptab_k on ptab(key)")
    c.execute("create index ptab_d on ptab(doc_id)")
    c.commit()
    print(f"물성표 보유 논문 {n}편 색인 완료", file=sys.stderr)


def tables_query(min_hits: int, limit: int, domain: str | None, want: str | None) -> None:
    """구워 둔 색인에서 즉시 조회한다."""
    c = sqlite3.connect(DB)
    if not c.execute("select name from sqlite_master where name='ptab'").fetchone():
        print("ptab 없음 — 먼저 `scan` 을 돌려라", file=sys.stderr)
        return
    sql = ("select d.id,max(p.n_in_table) n,d.domain,d.subdir,d.title,d.path "
           "from ptab p join doc d on d.id=p.doc_id where p.n_in_table>=?")
    args: list = [min_hits]
    if domain:
        sql += " and d.domain=?"
        args.append(domain)
    if want:
        sql += (" and exists(select 1 from ptab q where q.doc_id=d.id and q.key=?)")
        args.append(want)
    sql += " group by d.id order by n desc limit ?"
    args.append(limit)
    rows = c.execute(sql, args).fetchall()
    tot = c.execute("select count(distinct doc_id) from ptab where n_in_table>=?",
                    (min_hits,)).fetchone()[0]
    print(f"물성표 {min_hits}종 이상 보유 논문 {tot}편 — 상위 {len(rows)}편\n")
    for did, n, dom, sub, title, path in rows:
        keys = [k for k, in c.execute("select key from ptab where doc_id=? order by key", (did,))]
        print(f"[{n}종] {dom}/{sub}  {title[:84]}")
        print(f"   {' · '.join(keys)}")
        print(f"   {path}")
    print("\n── 물성별 보유 논문 수(기준 이상)")
    for k, v in c.execute("select key,count(*) from ptab where n_in_table>=? "
                          "group by key order by 2 desc", (min_hits,)):
        print(f"   {v:5d}  {k}")


def scan_tables(min_hits: int, limit: int, domain: str | None, want: str | None) -> None:
    """물성표를 담은 논문을 **적중 물성 수 순으로** 낸다 — 배치가 훑을 작업목록이다.

    라벨·단위·숫자가 한 표 안에 같이 있어야 적중으로 친다. 그래서 여기서 나온 목록은
    "이 주제를 언급한 논문"이 아니라 **"물성 숫자가 표로 실린 논문"**이다.
    """
    c = sqlite3.connect(DB)
    sql = "select id,title,domain,subdir,path from doc"
    args: list = []
    if domain:
        sql += " where domain=?"
        args.append(domain)
    rows = []
    for _i, title, dom, sub, path in c.execute(sql, args):
        try:
            body = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if "|" not in body:
            continue
        best, keys = 0, set()
        for tb in _tables(body):
            low = tb.lower()
            hits = {k for lab, un, k in _SIG
                    if re.search(lab, low, re.I) and re.search(un, tb, re.I)}
            if len(hits) > best:
                best, keys = len(hits), hits
        if best >= min_hits and (not want or want in keys):
            rows.append((best, sorted(keys), dom, sub, title, path))
    rows.sort(key=lambda r: -r[0])
    print(f"물성표 보유 논문 {len(rows)}편 (기준: 한 표에 {min_hits}종 이상)\n")
    for n, keys, dom, sub, title, path in rows[:limit]:
        print(f"[{n}종] {dom}/{sub}  {title[:86]}")
        print(f"   {' · '.join(keys)}")
        print(f"   {path}")
    agg: Counter = Counter()
    for n, keys, *_ in rows:
        agg.update(keys)
    print("\n── 물성별 보유 논문 수")
    for k, v in agg.most_common():
        print(f"   {v:5d}  {k}")


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
    sub.add_parser("scan")
    p = sub.add_parser("tables")
    p.add_argument("-m", "--min-hits", type=int, default=4)
    p.add_argument("-n", "--limit", type=int, default=40)
    p.add_argument("-d", "--domain")
    p.add_argument("-k", "--want", help="이 물성을 담은 표만")
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
    elif a.cmd == "scan":
        scan_build()
    elif a.cmd == "tables":
        tables_query(a.min_hits, a.limit, a.domain, a.want)
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
