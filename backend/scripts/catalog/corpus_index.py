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
import glob
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


def _fts_safe(query: str) -> str:
    """FTS5가 연산자로 읽어 버리는 토큰을 따옴표로 감싼다.

    `lead-free solder` 를 그대로 넘기면 FTS5가 `-` 를 NOT 으로 읽어
    `no such column: free` 로 죽는다. **그 스택트레이스가 '적중 없음'처럼 보여서
    갈래를 통째로 버리게 된다** — 20차 E가 실제로 그럴 뻔했다.
    이미 따옴표로 묶인 구, AND/OR/NOT/NEAR 연산자, 접두검색(`foo*`)은 건드리지 않는다.
    """
    out, i, n = [], 0, len(query)
    while i < n:
        ch = query[i]
        if ch == '"':                                   # 인용구는 통째로 보존
            j = query.find('"', i + 1)
            j = n if j < 0 else j + 1
            out.append(query[i:j]); i = j; continue
        if ch.isspace():
            out.append(ch); i += 1; continue
        j = i
        while j < n and not query[j].isspace() and query[j] != '"':
            j += 1
        tok = query[i:j]; i = j
        if tok in ("AND", "OR", "NOT", "NEAR") or tok.startswith("NEAR("):
            out.append(tok)
        elif tok.endswith("*") and tok[:-1].isalnum():   # 접두검색은 연산자다
            out.append(tok)
        elif tok.isalnum():
            out.append(tok)
        else:                                            # 하이픈·슬래시·괄호 등
            out.append('"' + tok.replace('"', '') + '"')
    return "".join(out)


def _rows(c, query: str, domain: str | None, limit: int):
    sql = ("select d.id,d.title,d.domain,d.subdir,d.path from ft "
           "join doc d on d.id=ft.rowid where ft match ?")
    args: list = [_fts_safe(query)]
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
    (r"young|elastic modulus|tensile modulus|모듈러스|\bE\b", r"\b(GPa|MPa|N/mm|MN/m|kgf/mm|psi|lb/in)", "youngs_modulus"),
    (r"poisson|포아송", r"0\.[0-9]{2}", "poisson_ratio"),
    (r"density|밀도", r"(g/cm|kg/m|g cm|lb/in|relative density|specific gravity)", "density"),
    (r"thermal expansion|\bCTE\b|expansion coeff", r"(ppm|10\s?[-−]\s?6|/K|/°C|K\s?-1|per deg|deg C\s?-1|/deg)", "expansion_linear"),
    (r"thermal conductivity|열전도", r"W/\(?m", "conductivity"),
    (r"specific heat|비열|heat capacity", r"J/\(?(kg|g)", "specific_heat"),
    (r"tensile strength|인장강도", r"\b(MPa|GPa|MN/m|kgf/mm|psi|ksi)", "tensile_strength"),
    (r"yield strength|항복", r"\b(MPa|GPa|MN/m|kgf/mm|psi|ksi)", "yield_strength"),
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
    (r"heat distortion|deflection temperature|\bHDT\b", r"(°C|deg C)", "hdt"),
    (r"impact strength|충격강도|charpy|izod", r"(kJ/m|J/m|ft\s?lb|kgf\s?cm)", "impact_strength"),
    (r"dielectric strength|절연내력", r"(kV/mm|MV/m|V/mil)", "dielectric_strength"),
    (r"flexural strength|굽힘강도|modulus of rupture|\bMOR\b", r"\b(MPa|GPa|MN/m|kgf/mm|psi|ksi)", "flexural_strength"),
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
    # `n_in_table` 은 **한 표에 공존하는 물성 종류 수**이지 행 수가 아니다.
    # 23차에 이걸 행 수로 오해해 표적 파일을 만들었더니 sum(n_in_table) == n_keys² 이 돼
    # **격자 판별에 아무 정보가 없었다.** 실제 숫자행을 세는 열을 따로 둔다.
    c.executescript("drop table if exists ptab;"
                    "create table ptab(doc_id integer, key text, n_in_table integer, "
                    "n_num_rows integer, body_kb integer, n_tbl_files integer, n_keys_union integer);")
    n = 0
    for did, path in c.execute("select id,path from doc").fetchall():
        try:
            body = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # **표는 본문 md 에만 있는 게 아니다.** docling 이 표를 `tables/table-N.md` 로 빼면
        # 본문에 파이프가 한 개도 안 남아 이 논문이 **모수에서 통째로 사라진다.**
        # 23차 H 가 찾았다 — 179편 목록이 소진된 줄 알았는데, 표 5장 이상이면서 목록 밖인
        # 논문이 2,359편 있었고 그 상위 두 편에서 105행이 나왔다(Thompson 1983 은 표가 6장).
        tabs = list(_tables(body))
        for tf in sorted(glob.glob(os.path.join(os.path.dirname(path), "tables", "*.md"))):
            try:
                tabs += _tables(open(tf, encoding="utf-8", errors="replace").read())
            except OSError:
                continue
        n_tf = len(glob.glob(os.path.join(os.path.dirname(path), "tables", "*.md")))
        if not tabs:
            continue
        best: set = set()
        uni: set = set()
        best_rows = 0
        for tb in tabs:
            low = tb.lower()
            hits = {k for lab, un, k in _SIG
                    if re.search(lab, low, re.I) and re.search(un, tb, re.I)}
            uni |= hits
            if len(hits) > len(best):
                best = hits
                # **숫자가 둘 이상 든 줄**만 데이터 행으로 센다 — 격자는 행이 많다.
                best_rows = sum(1 for ln in tb.splitlines()
                                if len(re.findall(r"-?\d+(?:\.\d+)?", ln)) >= 2)
        if uni:
            # 본문 길이는 **`bookish` 제목 정규식보다 나은 단행본·리뷰 탐지기**다.
            # 23차 B 실측 — 코퍼스 중앙값 41 KB · p95 104 KB. 100 KB 초과 10편 중 8편이
            # 리뷰/단행본인데 제목 정규식은 3편만 잡았다(Liu 2011은 1.37 MB인데 0이었다).
            kb = len(body) // 1024
            c.executemany("insert into ptab values(?,?,?,?,?,?,?)",
                          [(did, k, len(best), best_rows, kb, n_tf, len(uni)) for k in uni])
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
