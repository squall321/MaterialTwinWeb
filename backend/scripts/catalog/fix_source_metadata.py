# 출처 메타데이터 정리 — ① URL 내 DOI 추출 ② 저자접두 제거 후 재조회 ③ 비논문 출처 종류 교정.
import difflib
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
APPLY = "--apply" in sys.argv
UA = "MaterialTwinWeb/1.0 (https://github.com/squall321/MaterialTwinWeb; mailto:squall321@gmail.com)"
SIM_MIN = 0.92
OK_TYPES = {"journal-article", "proceedings-article"}

DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"'<>&?#]+)", re.I)
# 저자·연도 접두("Jiang et al. 2016,", "Kang et al. (1999)") 제거용.
AUTHOR_PREFIX = re.compile(r"^[A-Z][A-Za-z\-']+(\s*(&|and)\s*[A-Z][A-Za-z\-']+)?\s*"
                           r"(et al\.?)?\s*[\(\[]?\d{4}[\)\]]?\s*[,\-–]\s*")

# 논문이 아닌 출처 → 올바른 kind. (제목/URL 패턴 → kind)
RECLASS_URL = [
    ("rogerscorp.com", "datasheet"), ("multimedia.3m.com", "datasheet"),
    ("pcdn.co", "datasheet"), ("sciencedirect.com/topics", "web"),
    ("azom.com", "web"), ("mykin.com", "web"), ("allpcb.com", "web"),
    ("eureka.patsnap.com", "web"), ("hbfuller.com", "web"),
    ("uspto.gov", "other"), ("patents.google.com", "other"),
]
RECLASS_TITLE = [
    ("US Patent", "other"), ("(patent)", "other"),
    ("Data Sheet", "datasheet"), ("Spec Sheet", "datasheet"),
    ("whitepaper", "datasheet"), ("technical overview", "web"),
    ("Ultimate Guide", "web"), ("- overview", "web"),
    ("Properties and Applications", "web"), ("class reference", "web"),
    ("클래스", "other"), ("문헌 클래스", "other"), ("등가근사", "other"),
    ("계열 문헌값", "other"), ("(문헌)", "other"), ("Equivalent approximation", "other"),
]


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&[a-z]+;", " ", s)
    s = re.sub(r"[^a-z0-9가-힣]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def similarity(a, b):
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    short, long_ = (na, nb) if len(na) <= len(nb) else (nb, na)
    if len(short) >= 40 and long_.startswith(short):
        return 0.97
    return difflib.SequenceMatcher(None, na, nb).ratio()


def strip_prefix(t):
    t = AUTHOR_PREFIX.sub("", t or "").strip()
    t = re.sub(r"\s*\([^)]*et al[^)]*\)\s*$", "", t).strip()   # 꼬리 "(Yu et al., 2016)"
    t = re.sub(r"\s*\(US Patent[^)]*\)\s*$", "", t).strip()
    return t


def crossref(title):
    q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 8,
                                "select": "DOI,title,type,issued,container-title,is-referenced-by-count"})
    req = urllib.request.Request(f"https://api.crossref.org/works?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)["message"]["items"]


def resolve(title):
    try:
        items = crossref(title)
    except Exception:
        return None
    cands = []
    for it in items:
        cand = (it.get("title") or [""])[0]
        if not cand:
            continue
        sim = similarity(title, cand)
        if sim < SIM_MIN or it.get("type", "") not in OK_TYPES:
            continue
        cands.append({"doi": it.get("DOI"), "title": cand, "sim": sim,
                      "cites": it.get("is-referenced-by-count") or 0,
                      "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0]})
    if not cands:
        return None
    cands.sort(key=lambda x: (x["sim"] >= 0.999, x["cites"], -(x["year"] or 9999)), reverse=True)
    return cands[0]


def main():
    c = sqlite3.connect(DB)
    rows = c.execute("""select id, title, url, kind from source
        where kind='journal' and (doi is null or doi='')""").fetchall()
    taken = {d for (d,) in c.execute("select doi from source where doi is not null and doi<>''")}

    from_url = reclass = resolved = left = 0
    print(f"대상 {len(rows)}건\n")
    print("── ① URL에서 DOI 추출 ──")
    remaining = []
    for sid, title, url, kind in rows:
        m = DOI_RE.search(url or "")
        if m:
            doi = m.group(1).rstrip(".").rstrip("/")
            if doi in taken:
                print(f"  · [{sid}] 이미 존재하는 DOI({doi}) — 건너뜀")
                remaining.append((sid, title, url, kind))
                continue
            print(f"  ✓ [{sid}] {doi}  ← {(title or '')[:44]}")
            if APPLY:
                c.execute("update source set doi=? where id=?", (doi, sid))
            taken.add(doi)
            from_url += 1
        else:
            remaining.append((sid, title, url, kind))

    print("\n── ② 비논문 출처 종류 교정 ──")
    still = []
    for sid, title, url, kind in remaining:
        newk = None
        for pat, k in RECLASS_URL:
            if pat in (url or ""):
                newk = k
                break
        if not newk:
            for pat, k in RECLASS_TITLE:
                if pat.lower() in (title or "").lower():
                    newk = k
                    break
        if newk:
            print(f"  ✓ [{sid}] journal → {newk:9s} {(title or '')[:48]}")
            if APPLY:
                c.execute("update source set kind=? where id=?", (newk, sid))
            reclass += 1
        else:
            still.append((sid, title, url, kind))

    print("\n── ③ 저자접두 제거 후 CrossRef 재조회 ──")
    seen = {}
    for sid, title, url, kind in still:
        t = strip_prefix(title)
        if t != title:
            print(f"  · 재시도: {title[:40]} → {t[:40]}")
        if t in seen:
            hit = seen[t]
        else:
            hit = resolve(t)
            seen[t] = hit
            time.sleep(0.35)
        if hit and hit["doi"] not in taken:
            print(f"  ✓ [{sid}] [{hit['sim']:.2f}] {hit['doi']:30s} 인용{hit['cites']}")
            if APPLY:
                c.execute("update source set doi=? where id=?", (hit["doi"], sid))
            taken.add(hit["doi"])
            resolved += 1
        else:
            left += 1

    if APPLY:
        c.commit()
    print(f"\n{'[APPLY]' if APPLY else '[DRY-RUN]'} URL추출 {from_url} / 종류교정 {reclass} / 재조회해결 {resolved} / 잔여 {left}")
    n = c.execute("select count(*) from source where doi is not null and doi<>''").fetchone()[0]
    jn = c.execute("select count(*) from source where kind='journal'").fetchone()[0]
    jd = c.execute("select count(*) from source where kind='journal' and doi is not null and doi<>''").fetchone()[0]
    print(f"DOI 보유 출처 {n} | journal {jn}건 중 DOI {jd}건")


if __name__ == "__main__":
    main()
