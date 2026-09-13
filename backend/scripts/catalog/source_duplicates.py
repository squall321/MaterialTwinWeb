# 중복 **출처행**을 여러 지문으로 전수 검출하고 부류로 가른다(53차 OA · §568).
#
# 왜 새 모듈인가 — `merge_duplicate_sources.py` 는 **지운다**(`delete from source`).
# §565 가 그것을 금지한다: dev 에서 지운 행은 운영에 그대로 남고 되돌아오지도 않는다.
# 여기서는 한 행도 지우지 않는다. 찾고, 부류로 가르고, 손확인 결과를 같이 낸다.
#
# 왜 출처가 값보다 앞인가 — 값 중복 검출의 묶음 키에 `source_id` 가 들어 있어서
# **같은 시트가 출처 두 행으로 들어오면 중복 검출이 통째로 눈을 감는다**(§568).
#
# ── 측정 규율 셋 ──────────────────────────────────────────────────────────────
# 1. **URL 쿼리를 떼지 마라**(§568). `azom.com/properties.aspx?ArticleID=…` ·
#    `asm.matweb.com/search/specificmaterial.asp?bassnum=…` ·
#    `taimide.com.tw/api/download.ashx?id=…` 는 **쿼리로 페이지가 갈린다.**
#    조정자가 첫 측정에서 떼었다가 1,014행 오탐을 냈다. 스킴·`www.`·끝 슬래시만 정규화한다.
# 2. **DOI 는 대소문자를 무시한다.** DOI 는 규격상 대소문자 구분이 없다 —
#    `10.1007/BF02692566` 과 `10.1007/bf02692566` 은 같은 문헌이다(실측 3군).
# 3. **`local_path` 는 혼자서는 지문이 아니다.** 실측 — Doosan CCL 편찬 PDF 한 경로가
#    **55개 제품 페이지 출처에 찍혀 있다.** 제품이 다르면 다른 문헌이다(§426).
#    같은 경로 + 같은 정규화 제목일 때만 지문으로 쓴다.
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from collections import defaultdict

# `MATERIALTWIN_DB` 만 보면 형제 도구와 어긋난다 — 배치가 `MATERIALTWIN_DATA_DIR=<사본>`
# 으로 리허설할 때 이 도구만 라이브를 읽는다(66차 BB 가 mined_index 에서 잡은 병).
# 직접 지목하는 기존 호출을 깨지 않으려 `MATERIALTWIN_DB` 는 그대로 받고, 없으면 형제를 따른다.
DB = os.environ.get("MATERIALTWIN_DB") or os.path.join(
    os.environ.get("MATERIALTWIN_DATA_DIR",
                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
    "materialtwin.db")

# 병합기(`_materialtwin_merge.py`)가 쓰는 출처 자연키. **이 조합이 지문이 될 수 있는가**가
# 이 배치의 물음이었고, 라이브 2,943행 실측으로 **2,943/2,943 완전 유일**이었다.
# → 옮긴 값의 `conditions.moved_from_source` 에 이 조합(비어 있지 않은 칸만)을 적는다.
#   §535 가 재료에서 "id 가 아니라 이름" 을 가르쳤는데, 출처에는 이름이 없다 —
#   자연키가 그 자리다.
SOURCE_NATURAL_KEY = ["kind", "doi", "isbn", "url", "title", "publisher", "license"]


def norm_title(s: str | None) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9가-힣]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def norm_doi(s: str | None) -> str:
    s = (s or "").strip().lower()
    for p in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if s.startswith(p):
            s = s[len(p):]
    return s.rstrip("/")


def norm_url(s: str | None) -> str:
    """스킴·`www.`·끝 슬래시만 벗긴다. **쿼리는 남긴다**(§568)."""
    s = (s or "").strip()
    if not s:
        return ""
    s = re.sub(r"^https?://", "", s, flags=re.I)
    s = re.sub(r"^www\.", "", s, flags=re.I)
    return s.rstrip("/").lower()


# 벤더 문서번호 — 판(edition)을 가르는 **긍정형** 지문이다(§426 의 뒷면).
# DuPont 은 Qnity 분사 후 같은 시트를 `EI-#####` 와 `QE-#####` 두 번호로 낸다.
# 번호가 같으면 같은 시트다 — 실측 10172·10206·10207 세 쌍이 그렇다.
DOCNUM = re.compile(r"\b(EI|QE)-(\d{5})\b", re.I)

# 판·개정 토큰 — 제목에 이것이 **한쪽에만** 있으면 같은 문서라고 단정하지 마라(§426).
EDITION_TOKEN = re.compile(
    r"\b(ed(?:ition)?\.?\s*\d+|rev\.?\s*[\d.]+|version\s*[\d.]+|pub\s*#?[\d-]+|"
    r"20\d{2}|1?\d/\d{2})\b", re.I)


def fingerprints(rows: list[dict]) -> dict[str, dict]:
    """지문별 군. 값은 {지문키: [행…]} 이고 2행 이상인 것만 남긴다."""
    out: dict[str, dict] = {}

    def build(name, fn):
        g = defaultdict(list)
        for r in rows:
            k = fn(r)
            if k:
                g[k].append(r)
        out[name] = {k: v for k, v in g.items() if len(v) > 1}

    build("doi", lambda r: norm_doi(r["doi"]) or None)
    build("url", lambda r: norm_url(r["url"]) or None)
    build("title", lambda r: norm_title(r["title"]) or None)
    build("content_hash", lambda r: r["content_hash"] or None)
    # local_path 는 혼자 지문이 아니다 — 제목까지 같아야 한다(위 규율 3).
    build("local_path+title",
          lambda r: (r["local_path"], norm_title(r["title"])) if r["local_path"] else None)
    build("title+year+publisher",
          lambda r: (norm_title(r["title"]), r["year"],
                     (r["publisher"] or "").strip().lower()) if r["title"] else None)
    build("docnum", lambda r: (m.group(2) if (m := DOCNUM.search(
        f"{r['title'] or ''} {r['url'] or ''}")) else None))
    # 참고용 — 혼자서는 못 쓴다는 것을 수치로 보이기 위해 같이 낸다.
    build("local_path(단독)", lambda r: r["local_path"] or None)
    return out


def load(db: str) -> tuple[list[dict], dict, dict]:
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    rows = [dict(r) for r in c.execute("select * from source")]
    pvn = dict(c.execute(
        "select source_id, count(*) from property_value "
        "where source_id is not null group by source_id").fetchall())
    insn = dict(c.execute(
        "select source_id, count(*) from instrument "
        "where source_id is not null group by source_id").fetchall())
    c.close()
    return rows, pvn, insn


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=DB)
    ap.add_argument("--json", help="군 목록을 이 경로에 JSON 으로 쓴다")
    ap.add_argument("--fingerprint", help="이 지문의 군만 상세 출력")
    args = ap.parse_args()

    rows, pvn, insn = load(args.db)
    by_id = {r["id"]: r for r in rows}
    fps = fingerprints(rows)

    # 자연키 유일성 — 지문으로 쓸 수 있는가.
    nk = defaultdict(list)
    for r in rows:
        nk[tuple(r[k] for k in SOURCE_NATURAL_KEY)].append(r["id"])
    dup_nk = {k: v for k, v in nk.items() if len(v) > 1}
    print(f"출처 {len(rows)}행 · 물성값 참조 {sum(pvn.values())} · 장비 참조 {sum(insn.values())}")
    print(f"자연키 {SOURCE_NATURAL_KEY} 유일성 — "
          f"{len(nk)}고유/{len(rows)}행 · 중복키 {len(dup_nk)}\n")

    print("지문별 검출")
    for name, groups in fps.items():
        nsrc = sum(len(v) for v in groups.values())
        nval = sum(pvn.get(r["id"], 0) for v in groups.values() for r in v)
        nins = sum(insn.get(r["id"], 0) for v in groups.values() for r in v)
        print(f"  {name:22s} {len(groups):4d}군 · 출처 {nsrc:4d}행 · 물성값 {nval:5d} · 장비 {nins}")

    if args.fingerprint:
        for k, v in sorted(fps[args.fingerprint].items(),
                           key=lambda kv: -sum(pvn.get(r["id"], 0) for r in kv[1])):
            print(f"\n### {k}")
            for r in v:
                print(f"  src{r['id']:5d} {r['kind']:9s} pv={pvn.get(r['id'], 0):4d} "
                      f"yr={r['year']} pub={str(r['publisher'])[:24]}")
                print(f"        title = {r['title']}")
                print(f"        url   = {r['url']}")
                print(f"        doi   = {r['doi']}  lp={r['local_path']}")

    if args.json:
        # 지문을 합쳐 후보군을 만든다(어느 지문이 걸었는지 같이 남긴다).
        parent: dict[int, int] = {r["id"]: r["id"] for r in rows}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        why = defaultdict(set)
        for name, groups in fps.items():
            if name == "local_path(단독)":
                continue        # 위 규율 3 — 혼자서는 못 쓴다
            for v in groups.values():
                ids = [r["id"] for r in v]
                for a in ids[1:]:
                    ra, rb = find(ids[0]), find(a)
                    if ra != rb:
                        parent[rb] = ra
                for a in ids:
                    why[a].add(name)
        comp = defaultdict(list)
        for r in rows:
            if why.get(r["id"]):
                comp[find(r["id"])].append(r["id"])
        out = []
        for root, ids in comp.items():
            if len(ids) < 2:
                continue
            out.append({
                "지문": sorted(set().union(*(why[i] for i in ids))),
                "행": [{"id": i, "kind": by_id[i]["kind"], "title": by_id[i]["title"],
                        "doi": by_id[i]["doi"], "url": by_id[i]["url"],
                        "local_path": by_id[i]["local_path"],
                        "publisher": by_id[i]["publisher"], "year": by_id[i]["year"],
                        "물성값": pvn.get(i, 0), "장비": insn.get(i, 0),
                        "판토큰": sorted({m.group(0) for m in
                                        EDITION_TOKEN.finditer(by_id[i]["title"] or "")})}
                       for i in sorted(ids)],
            })
        out.sort(key=lambda g: -sum(r["물성값"] for r in g["행"]))
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print(f"\n후보군 {len(out)}개 → {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
