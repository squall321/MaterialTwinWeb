# journal 출처의 DOI를 CrossRef로 실제 조회해 채운다. 지어내지 않음 — 엄격 검증 통과분만 기록.
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
# CrossRef 예의: 연락처 명시(polite pool) + 요청 간 간격.
UA = "MaterialTwinWeb/1.0 (https://github.com/squall321/MaterialTwinWeb; mailto:squall321@gmail.com)"
SIM_MIN = 0.92          # 제목 유사도 하한(엄격)
OK_TYPES = {"journal-article", "proceedings-article"}
PREFER = ("journal-article", "proceedings-article")


def norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"<[^>]+>", "", s)          # CrossRef 제목의 HTML 태그(<i>,<sub>) 제거.
    s = re.sub(r"&[a-z]+;", " ", s)        # HTML 엔티티.
    s = re.sub(r"[‘’“”']", "", s)
    s = re.sub(r"[^a-z0-9가-힣]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def similarity(a: str, b: str) -> float:
    """제목 유사도. 저장 제목이 잘린 경우(접두 일치)를 정당하게 인정한다."""
    na, nb = norm(a), norm(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    # 한쪽이 다른 쪽의 접두이고 40자 이상 겹치면 사실상 동일 논문(제목 절단).
    short, long_ = (na, nb) if len(na) <= len(nb) else (nb, na)
    if len(short) >= 40 and long_.startswith(short):
        return 0.97
    return difflib.SequenceMatcher(None, na, nb).ratio()


def clean_title(raw: str) -> str:
    """저장된 출처 제목에서 논문 제목만 추출('Author et al., "Title", Journal ...' 형태 대응)."""
    m = re.search(r"[‘'\"](.+?)[’'\"]", raw)
    if m and len(m.group(1)) > 20:
        return m.group(1)
    # "Journal X (2013) 121" 같은 꼬리 제거.
    return re.sub(r",?\s*[A-Z][A-Za-z .]+\s+\d+\s*\(\d{4}\)\s*\d+.*$", "", raw).strip()


def crossref(title: str):
    q = urllib.parse.urlencode({
        "query.bibliographic": title, "rows": 8,
        "select": "DOI,title,type,issued,container-title,is-referenced-by-count",
    })
    req = urllib.request.Request(f"https://api.crossref.org/works?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)["message"]["items"]


def best_match(title: str):
    """유사도·문헌종류로 최적 후보 선택. 기준 미달이면 None."""
    try:
        items = crossref(title)
    except Exception as e:
        return None, f"API 실패: {e}"
    cands, best_sim, best_cand = [], 0.0, ""
    for it in items:
        cand = (it.get("title") or [""])[0]
        if not cand:
            continue
        sim = similarity(title, cand)
        if sim > best_sim:
            best_sim, best_cand = sim, cand
        if sim < SIM_MIN or it.get("type", "") not in OK_TYPES:
            continue
        cands.append({
            "doi": it.get("DOI"), "title": cand, "sim": sim, "type": it.get("type", ""),
            "year": (it.get("issued", {}).get("date-parts") or [[None]])[0][0],
            "journal": (it.get("container-title") or [""])[0],
            "cites": it.get("is-referenced-by-count") or 0,
        })
    if not cands:
        if best_sim < SIM_MIN:
            return None, f"유사도 미달 {best_sim:.2f} (후보: {best_cand[:50]})"
        return None, "문헌종류 부적합(원저널 논문 아님)"
    # 재수록·챕터본을 피해 원저를 고른다 — 인용수가 압도적으로 많은 쪽이 원저.
    # (정확 제목일치 우선 → 인용수 → 이른 연도)
    cands.sort(key=lambda x: (x["sim"] >= 0.999, x["cites"], -(x["year"] or 9999)), reverse=True)
    return cands[0], None


def main():
    c = sqlite3.connect(DB)
    rows = c.execute("""select id, title from source
        where kind='journal' and (doi is null or doi='') and title is not null and title<>''
        order by id""").fetchall()
    # 같은 제목은 1회만 조회(API 호출 절감).
    by_title = {}
    for sid, t in rows:
        by_title.setdefault(t, []).append(sid)
    print(f"대상 출처 {len(rows)}건 / 고유 제목 {len(by_title)}건\n")

    resolved = skipped = 0
    updates = []
    for i, (raw_title, sids) in enumerate(sorted(by_title.items()), 1):
        t = clean_title(raw_title)
        hit, why = best_match(t)
        if hit:
            resolved += 1
            updates.append((hit["doi"], sids, raw_title, hit))
            print(f"  ✓ [{hit['sim']:.2f}] {hit['doi']:34s} {hit['title'][:52]}")
            print(f"      ({hit['journal'][:40]}, {hit['year']}, 인용{hit['cites']}) x{len(sids)}건")
        else:
            skipped += 1
            print(f"  · SKIP {raw_title[:56]}")
            print(f"      → {why}")
        time.sleep(0.35)   # rate limit 예의.
        if i % 25 == 0:
            print(f"  --- {i}/{len(by_title)} ---")

    print(f"\n{'[APPLY]' if APPLY else '[DRY-RUN]'} 해결 {resolved} / 미해결 {skipped}")
    if APPLY and updates:
        for doi, sids, _, hit in updates:
            for sid in sids:
                # DOI 중복(UNIQUE 제약) 대비 — 이미 같은 DOI를 가진 출처가 있으면 건너뜀.
                dup = c.execute("select id from source where doi=? and id<>?", (doi, sid)).fetchone()
                if dup:
                    continue
                c.execute("update source set doi=? where id=? and (doi is null or doi='')", (doi, sid))
        c.commit()
        n = c.execute("select count(*) from source where doi is not null and doi<>''").fetchone()[0]
        print(f"적용 후 DOI 보유 출처: {n}")


if __name__ == "__main__":
    main()
