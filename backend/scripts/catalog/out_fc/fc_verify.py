# 70차 FC — out_ed 의 2026-08-19 자 산출물 여섯이 라이브 DB 에 이미 들어갔는지 재현 가능하게 대조한다
#
# 사용: MATERIALTWIN_DATA_DIR 무관 — 라이브 DB 를 읽기 전용으로 직접 연다.
#   python3 backend/scripts/catalog/out_fc/fc_verify.py
#
# 세 가지를 센다.
#   ① 값 1:1 소진 대조 — JSON 행마다 DB 행 하나를 소진시켜 값 중복 오탐을 막는다
#   ② 출처 동일성 — 매칭된 DB 행의 source 가 JSON 의 doi/url/title 과 같은가
#   ③ 생성시각 — 그 행이 언제 DB 에 들어갔는가
import json
import sqlite3
from collections import Counter
from pathlib import Path

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"
OUT_ED = Path(__file__).resolve().parents[1] / "out_ed"
FILES = ["ed01_battery_corpus", "ed02_ndfeb_grades", "ed03_ferrite",
         "ed04_liebig", "ed05_sep_pouch", "ed06_ccaw"]


def close(a, b):
    if a is None or b is None:
        return a is b
    if a == b:
        return True
    return abs(a - b) <= max(1e-9, max(abs(a), abs(b)) * 1e-4)


def src_same(row, js):
    doi = (js.get("doi") or "").lower().strip()
    url = (js.get("url") or "").strip()
    ti = (js.get("title") or "").strip().lower()
    return ((doi and (row[1] or "").lower() == doi)
            or (url and (row[2] or "") == url)
            or (ti and (row[3] or "").lower()[:40] == ti[:40]))


def main():
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    born = Counter()
    total = hit = src_hit = 0
    for f in FILES:
        d = json.loads((OUT_ED / f"{f}.json").read_text())
        fh = ft = 0
        for m in d["materials"]:
            nm = m.get("match_name") or m["new_material"]["name"]
            r = c.execute("select id from material where name=?", (nm,)).fetchone()
            if not r:
                print(f"  ✗ 카드 없음: {nm}")
                ft += len(m.get("properties", []))
                continue
            mid, src = r[0], m["source"]
            bykey = {}
            for p in m.get("properties", []):
                bykey.setdefault(p["key"], []).append(p)
            for key, ps in bykey.items():
                pool = list(c.execute(
                    "select pv.id,pv.value_num,pv.created_at,s.id,s.doi,s.url,s.title "
                    "from property_value pv left join source s on s.id=pv.source_id "
                    "where pv.material_id=? and pv.property_key=?", (mid, key)))
                used = set()
                for p in ps:
                    total += 1
                    ft += 1
                    cand = [x for x in pool
                            if x[0] not in used and close(x[1], p.get("value"))]
                    if not cand:
                        print(f"  ✗ 값 없음: {nm[:40]} {key} {p.get('value')}")
                        continue
                    x = cand[0]
                    used.add(x[0])
                    hit += 1
                    fh += 1
                    born[x[2][:10]] += 1
                    if src_same(x[3:], src):
                        src_hit += 1
                    else:
                        print(f"  ⚠ 출처 다름: {nm[:40]} {key} {p.get('value')}")
        print(f"{f}: {fh}/{ft} 라이브 DB 에 있다")
    print(f"\n합계 {hit}/{total} · 그중 출처까지 같은 행 {src_hit}")
    print("DB 생성일 분포:", dict(born))


if __name__ == "__main__":
    main()
