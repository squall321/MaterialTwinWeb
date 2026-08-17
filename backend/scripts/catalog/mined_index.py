#!/usr/bin/env python3
# 이미 채굴한 논문을 **DOI·경로·제목·인용키 네 축으로** 조회한다 — 선별기 앞단에 붙이는 도구.
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
#   ④ **인용키**(`Tsai 2013`)로도 찾는다 — 배치들이 완전 제목이 아니라 이 꼴로 조회한다(33차 AG).
#   ⑤ **"출처가 있다 ≠ 채굴됐다"**(222번) — `property_value` 행 수와 최소 등급을 함께 낸다.
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

    **코퍼스 폴더명 접두(`Liu - 2007 - `)도 벗긴다.** 브리프·PREAMBLE 이 배치에게
    `--title "Tsai - 2013 - Properties of ..."` 꼴로 조회하라고 지시하는데,
    이 접두가 붙으면 마지막 45자 절단 창이 통째로 밀려 **같은 논문이 안 걸렸다.**
    36차 AR 실측 — 출처 300편을 무작위로 뽑아 대조하니 맨제목은 300/300,
    폴더명 꼴은 **19/300(6.3%)** 이었다. Liu 2007 이 그렇게 `null` 로 나왔다.
    """
    s = s or ""
    m = re.match(r"^.*?\(\d{4}(?:/\d{4})?\),\s*(.+)$", s)
    if m:
        s = m.group(1)
    s = re.sub(r"^\s*\S[^-–]{0,38}?\s[-–]\s(?:19|20)\d{2}\s[-–]\s", "", s)
    s = re.sub(r",\s*[A-Z][A-Za-z .&]+$", "", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", s.lower())[:45]


def author_year_keys(title: str | None, authors: str | None, year) -> set[str]:
    """`Tsai 2013` 같은 **인용키**로도 찾게 한다.

    배치들이 완전 제목이 아니라 인용키로 조회한다(33차 AG 가 Tsai 2013 을 이렇게 놓쳤다).
    성(姓)과 연도만 있으면 되므로 제목 접두(`Tsai, Lin, Chen 등 (2013), ...`)와
    `authors`/`year` 컬럼 양쪽에서 뽑는다.
    """
    out: set[str] = set()
    yrs = {str(year)} if year else set()
    m = re.match(r"^(.*?)\((\d{4})(?:/\d{4})?\),", title or "")
    if m:
        yrs.add(m.group(2))
        head = m.group(1)
    else:
        head = authors or ""
    if authors:
        head = head + " " + authors
    # 성만 뽑는다 — `Tsai, Lin, Chen 등` · `Tsai, Lin & Chen` 둘 다 받는다.
    for w in re.findall(r"[A-Z][a-zA-Z\u00C0-\u024F'-]{1,}", head):
        if w.lower() in ("et", "al", "and"):
            continue
        for y in yrs:
            out.add(f"{unicodedata.normalize('NFKD', w).encode('ascii','ignore').decode().lower()}{y}")
    return out


_STOP = {"with", "from", "using", "based", "study", "effect", "effects", "properties",
         "property", "analysis", "novel", "high", "material", "materials", "their",
         "characterization", "investigation", "influence", "behavior", "behaviour"}


def citation_keys(title: str | None) -> list[str]:
    """조회어에서 `성+연도` 후보를 뽑는다 — **전체 제목도 받는다.**

    코퍼스 파일명은 `Tsai - 2013 - Properties of ...` 꼴이고 DB 제목은
    `Tsai, Lin, Chen 등 (2013), Properties of ...` 꼴이다. 둘 다에서 첫 성과 연도를 뽑는다.
    """
    t = (title or "").strip()
    if not t:
        return []
    out: list[str] = []
    yrs = re.findall(r"(?:19|20)\d{2}", t[:120])
    if not yrs:
        return []
    # 첫 대문자 낱말이 성이다(`Tsai - 2013 - ...` · `Tsai, Lin (2013), ...` · `Tsai 2013`).
    for w in re.findall(r"[A-Z][a-zA-Z\u00C0-\u024F'-]{1,}", t[:60])[:3]:
        if w.lower() in ("the", "and", "for", "of", "on", "in", "a", "an"):
            continue
        base = unicodedata.normalize("NFKD", w).encode("ascii", "ignore").decode().lower()
        out += [base + y for y in yrs[:2]]
    return out


def _merge(idx: dict, axis: str, key: str, rec: dict) -> None:
    """같은 키에 **합산**한다 — `setdefault` 로 첫 건만 남기면 안 된다.

    36차에 실측했다: 제목 정규화(45자 절단)가 59건 충돌하고 그중 **28건은 행수가 갈린다**.
    먼저 들어온 것이 0~2행이면 **채굴이 끝난 논문이 미채굴로 보인다** — 실제로
    Ehrler 2002(143행)·Fujishima 2017(59행)·Narahashi 2010(19행)이 그렇게 표적 목록에 올라
    배치 둘이 중복 작업을 했다.

    충돌의 정체는 대개 **같은 논문·같은 데이터시트가 출처로 중복 등록된 것**이다
    (DuPont Kapton HN 이 4건 = 15+35+13+2행). 그러니 "이 논문이 채굴됐나" 의 답은
    **합계**이지 첫 건이 아니다. 등급은 가장 좋은 것(최소값)을 쓴다.
    """
    old = idx[axis].get(key)
    if old is None:
        idx[axis][key] = dict(rec)
        return
    # **DOI 가 갈리면 다른 논문이다 — 합산하면 안 된다.**
    # 실측: 제목 충돌 59묶음 중 18묶음이 서로 다른 DOI 였다. Iridium 착물 둘은
    # RSC Advances 대 Dalton Transactions 이고, PTH 신뢰성 둘은 같은 호의 연속 논문이다
    # (…90016-8 과 …90017-x). 뭉쳐서 행수를 더하면 **한 번도 안 판 논문이 채굴됨으로 보인다** —
    # 첫 건만 보던 옛 오류(재발굴, 일 낭비)보다 **더 나쁜 방향이다. 논문을 잃는다.**
    # 창을 넓혀도 안 없어진다(200자에서도 9묶음 남고 적중은 29% 잃는다) — 창이 아니라 DOI 문제다.
    # → 합산은 하되 **모호 표시**를 달고, 조회에서 `confidence: low` 로 내보낸다.
    #   대량 필터는 `low` 로 절대 제외하지 않으므로 그 논문은 표적에 남는다.
    da, db_ = (old.get("doi") or "").strip(), (rec.get("doi") or "").strip()
    seen = set(old.get("_dois") or ([da] if da else []))
    if db_:
        seen.add(db_)
    old["_dois"] = sorted(seen)
    if len(seen) > 1:
        old["ambiguous"] = True
    old["rows"] = (old.get("rows") or 0) + (rec.get("rows") or 0)
    a, b = old.get("min_tier"), rec.get("min_tier")
    old["min_tier"] = min([x for x in (a, b) if x is not None], default=None)
    # 제목은 행이 가장 많은 쪽을 대표로 남긴다 — 보고에 쓰인다.
    if (rec.get("rows") or 0) > (old.get("_top") or 0):
        old["_top"], old["title"] = rec.get("rows") or 0, rec.get("title")


def build(c: sqlite3.Connection) -> dict:
    """네 축의 색인을 만든다. 값은 (source_id, 행수, 최소등급).

    **행수는 합산이다**(`_merge`) — 같은 논문이 출처로 중복 등록돼 있어서다.
    """
    idx: dict[str, dict] = {"doi": {}, "path": {}, "title": {}, "authoryear": {}, "matname": {}}
    # 출처별 집계를 **한 번에** 만든다 — 건마다 count 를 돌면 2,700회라 색인 구축이 분 단위로 간다.
    sagg = {r[0]: (r[1], r[2]) for r in c.execute(
        "select source_id,count(*),min(quality_tier) from property_value "
        "where source_id is not null group by 1")}
    for sid, doi, title, lp in c.execute("select id,doi,title,local_path from source"):
        n, tier = sagg.get(sid, (0, None))
        rec = {"source_id": sid, "rows": n, "min_tier": tier, "title": title, "doi": doi}
        if doi:
            _merge(idx, "doi", norm_doi(doi), rec)
        if lp:
            # 경로는 **디렉터리명**으로 본다 — 파일명에 확장자·중복 접미가 붙는다.
            _merge(idx, "path", Path(str(lp)).name.lower(), rec)
        if title:
            _merge(idx, "title", norm_title(title), rec)
        for k in author_year_keys(title, None, None):
            _merge(idx, "authoryear", k, rec)
    # **재료명 축** — 배치들이 재료를 `... (Watanabe 2018)` 꼴로 짓는다(재료의 74%).
    # 출처 제목이 달라도 재료명이 걸리면 그 논문은 이미 채굴된 것이다(34차 AI 제안).
    magg = {r[0]: (r[1], r[2]) for r in c.execute(
        "select material_id,count(*),min(quality_tier) from property_value group by 1")}
    for name, mid in c.execute("select name, id from material"):
        for m in re.finditer(r"([A-Z][a-zA-Z\u00C0-\u024F'-]+)\s+((?:19|20)\d{2})", name or ""):
            k = (unicodedata.normalize("NFKD", m.group(1)).encode("ascii", "ignore")
                 .decode().lower() + m.group(2))
            n, tier = magg.get(mid, (0, None))
            _merge(idx, "matname", k, {"source_id": None, "material_id": mid,
                                       "rows": n, "min_tier": tier, "title": name})
    return idx


def look(idx: dict, *, doi=None, path=None, title=None) -> dict | None:
    def _out(r, how):
        # **모호 묶음은 낮은 신뢰다** — 제목이 같은 다른 논문이 섞여 있다는 뜻이다.
        # DOI 축으로 직접 맞은 것은 모호할 수 없다(DOI 가 곧 식별자다).
        d = {**r, "matched_by": how}
        if how != "doi" and r.get("ambiguous"):
            d["confidence"] = "low"
            d["ambiguous_dois"] = r.get("_dois")
        return d

    if doi and (r := idx["doi"].get(norm_doi(doi))):
        return {**r, "matched_by": "doi"}
    if path:
        key = Path(str(path)).name.lower()
        if r := idx["path"].get(key):
            return _out(r, "path")
        # md 파일 경로를 주면 부모 디렉터리가 논문 이름이다.
        if r := idx["path"].get(Path(str(path)).parent.name.lower()):
            return _out(r, "path(parent)")
    if title and (r := idx["title"].get(norm_title(title))):
        return _out(r, "title")
    # **부제가 붙고 안 붙고로 갈린다** — 코퍼스 파일명은 `… Viscoelasticity` 인데
    # DB 제목은 `… Viscoelasticity: An Introduction` 이라 45자 절단이 부제 한복판에서 끊긴다
    # (36차에 Brinson 2008 이 그렇게 제목 축을 통째로 비껴갔다).
    # 한쪽이 다른 쪽의 **접두**면 같은 논문으로 본다 — 25자 이상을 요구해 짧은 제목의 오탐을 막는다.
    if title and len(q0 := norm_title(title)) >= 25:
        for k, r in idx["title"].items():
            if len(k) >= 25 and (k.startswith(q0) or q0.startswith(k)):
                return _out(r, "title(prefix)")
    # **인용키 조회** — `Tsai 2013` 뿐 아니라 **코퍼스 제목에서도 뽑는다.**
    # 35차 AK 가 찾았다 — `^Surname YYYY$` 만 받으면 `--json` 에 전체 제목을 넣었을 때
    # 인용키·재료명 축이 **통째로 죽는다**(같은 27편에 제목 0건 대 인용키 7건).
    # **인용키·재료명 축은 오탐한다** — 35차 AL 실측: 흔한 성(Wang·Liu·Zhang)에서
    # 6건 중 3건이 **다른 논문**이었다. 오탐을 믿으면 **미채굴 논문을 버린다**.
    # → 제목 낱말이 겹치는지 확인하고, 못 하면 `confidence: low` 로 내보낸다.
    def _tok(x: str) -> set:
        return {w for w in re.findall(r"[a-z]{4,}", (x or "").lower()) if w not in _STOP}
    q = _tok(title)
    for k in citation_keys(title):
        for axis in ("authoryear", "matname"):
            r = idx[axis].get(k)
            if not r:
                continue
            ov = len(q & _tok(str(r.get("title"))))
            # 제목 낱말이 둘 이상 겹치면 확정, 아니면 낮은 신뢰로 넘긴다.
            how = axis.replace("authoryear", "author+year").replace("matname", "material-name")
            conf = "low" if (ov < 2 or r.get("ambiguous")) else "high"
            out = {**r, "matched_by": how, "confidence": conf, "title_token_overlap": ov}
            if r.get("ambiguous"):
                out["ambiguous_dois"] = r.get("_dois")
            return out
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="이미 채굴한 논문인지 DOI·경로·제목·인용키로 조회")
    ap.add_argument("--doi")
    ap.add_argument("--path")
    ap.add_argument("--title", help="완전 제목 또는 인용키(`Tsai 2013`)")
    # 배치가 후보 목록을 통째로 넘겨 거르는 용도.
    ap.add_argument("--json", help="[{doi?,path?,title?}, ...] 파일 — 미채굴만 남겨 stdout 으로")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    idx = build(c)
    print(f"[DB] {DB}\n     출처 {len(idx['doi'])} DOI · {len(idx['path'])} 경로 · "
          f"{len(idx['title'])} 제목 · {len(idx['authoryear'])} 인용키 · "
          f"{len(idx['matname'])} 재료명", file=sys.stderr)

    if a.json:
        items = json.load(open(a.json))
        out, hit = [], 0
        for it in items:
            r = look(idx, doi=it.get("doi"), path=it.get("path"), title=it.get("title"))
            # **행이 한둘이고 전부 tier3 이면 클래스 전이만 하고 논문은 안 판 것이다**(222번).
            # **낮은 신뢰 일치로는 빼지 않는다** — 오탐으로 미채굴 논문을 버리는 쪽이 더 나쁘다.
            solid = bool(r) and r.get("confidence") != "low"
            mined = solid and (r["rows"] > 2 or (r["min_tier"] or 9) <= 2)
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
