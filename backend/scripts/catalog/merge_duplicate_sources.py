# 중복 출처행 병합 — (정규화 제목 + publisher)가 같은 행을 하나로 통합, property_value를 재지정.
# publisher를 키에 포함해 업체 귀속(어느 업체 데이터시트인지)을 보존한다.
import re
import sqlite3
import sys
from collections import defaultdict

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
APPLY = "--apply" in sys.argv


def norm(s):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9가-힣]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def richness(row):
    """정보량 — DOI > URL > publisher > 제목길이. 가장 풍부한 행을 대표로."""
    sid, title, doi, url, pub, kind, isbn, authors, year = row
    return (1 if doi else 0, 1 if url else 0, 1 if pub else 0,
            1 if isbn else 0, 1 if authors else 0, 1 if year else 0,
            len(title or ""), -sid)


c = sqlite3.connect(DB)
rows = c.execute("""select id, title, doi, url, publisher, kind, isbn, authors, year
                    from source""").fetchall()
groups = defaultdict(list)
for r in rows:
    if r[1]:
        groups[(norm(r[1]), (r[4] or "").strip().lower())].append(r)

merged = removed = repointed = 0
print(f"출처 {len(rows)}행 / 그룹 {len(groups)}개\n")
for key, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    if len(members) < 2:
        continue
    members.sort(key=richness, reverse=True)
    keep, drop = members[0], members[1:]
    # 대표 행에 빠진 식별정보를 버리는 행에서 흡수(정보 손실 방지).
    kdoi, kurl, kpub, kisbn, kauth, kyear = keep[2], keep[3], keep[4], keep[6], keep[7], keep[8]
    for d in drop:
        kdoi = kdoi or d[2]
        kurl = kurl or d[3]
        kpub = kpub or d[4]
        kisbn = kisbn or d[6]
        kauth = kauth or d[7]
        kyear = kyear or d[8]
    n_pv = c.execute("select count(*) from property_value where source_id in (%s)"
                     % ",".join(str(d[0]) for d in drop)).fetchone()[0]
    print(f"  ×{len(members)}행 → keep#{keep[0]}  ({n_pv}개 물성값 재지정)  {keep[1][:52]}")
    if APPLY:
        c.execute("""update source set doi=?, url=?, publisher=?, isbn=?, authors=?, year=?
                     where id=?""", (kdoi, kurl, kpub, kisbn, kauth, kyear, keep[0]))
        for d in drop:
            c.execute("update property_value set source_id=? where source_id=?", (keep[0], d[0]))
            c.execute("delete from source where id=?", (d[0],))
            removed += 1
    else:
        removed += len(drop)
    repointed += n_pv
    merged += 1

if APPLY:
    c.commit()
print(f"\n{'[APPLY]' if APPLY else '[DRY-RUN]'} 병합그룹 {merged} / 제거행 {removed} / 재지정 물성값 {repointed}")
print(f"출처 행: {c.execute('select count(*) from source').fetchone()[0]}")
print(f"출처없는 물성값(0이어야): {c.execute('select count(*) from property_value where source_id is null').fetchone()[0]}")
orphan = c.execute("""select count(*) from property_value pv
    left join source s on s.id=pv.source_id where s.id is null""").fetchone()[0]
print(f"끊어진 참조(0이어야): {orphan}")
