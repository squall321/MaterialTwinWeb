# 같은 실물을 가리키는데 이름 표기가 갈려 검색이 한쪽만 잡는 재료쌍의 후보를 뽑는다 — 64차 ZC
import sqlite3, json, re, os, itertools
from collections import defaultdict

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)

cnt = {r[0]: r[1] for r in c.execute("select material_id,count(*) from property_value group by material_id")}
mats = []
for i, n, code, cat, a in c.execute("select id,name,material_code,category,attributes from material"):
    try: d = json.loads(a) if a else {}
    except Exception: d = {}
    mats.append((i, n or "", code or "", cat or "", d.get("role", ""), cnt.get(i, 0)))

STOP = {"2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011",
        "2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023",
        "2024","2025","2026","1980","1985","1986","1988","1990","1992","1993"}  # 연도 (2024 는 뒤에서 되살린다)

def tokens(name):
    """이름에서 '규격코드처럼 생긴' 토큰을 뽑는다. 인접 토큰 결합도 만든다(`CDA 360` → `CDA360`)."""
    raw = re.split(r"[^A-Za-z0-9]+", name.upper())
    raw = [t for t in raw if t]
    out = set()
    cands = list(raw) + ["".join(p) for p in zip(raw, raw[1:])]
    for t in cands:
        if not re.search(r"\d", t):      # 숫자가 없으면 규격코드가 아니다
            continue
        if len(t) < 3:
            continue
        out.add(t)
    return out

def cores(name):
    """토큰에서 '숫자 코어'(길이 3 이상 숫자 런)를 뽑는다. 연도는 뺀다."""
    out = set()
    for t in tokens(name):
        for run in re.findall(r"\d{3,}", t):
            if run in STOP and "AA2024" not in t and "AL2024" not in t and "2024T" not in t:
                continue
            out.add(run)
            if len(run) == 5 and run.endswith("00"):   # UNS C36000 ↔ CDA 360
                out.add(run[:3])
            if len(run) == 3:
                out.add(run + "00")
    return out

def squash(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())

by_core = defaultdict(list)
for m in mats:
    for k in cores(m[1]):
        by_core[k].append(m)

pairs = {}
for k, group in by_core.items():
    if len(group) < 2 or len(group) > 25:     # 25종 넘게 걸리는 코어는 코어가 아니다(잡음)
        continue
    for a, b in itertools.combinations(group, 2):
        # 검색 실패 조건 — 두 이름이 서로를 부분문자열로 안 담는다(정규화 후)
        sa, sb = squash(a[1]), squash(b[1])
        if sa in sb or sb in sa:
            continue
        key = tuple(sorted((a[0], b[0])))
        pairs.setdefault(key, set()).add(k)

print(f"# 재료 {len(mats)}종 · 숫자코어 {len(by_core)}개 · 후보쌍 {len(pairs)}")
byid = {m[0]: m for m in mats}
rows = []
for (x, y), ks in pairs.items():
    A, B = byid[x], byid[y]
    thick, thin = (A, B) if A[5] >= B[5] else (B, A)
    rows.append((thin[5], thick[5], sorted(ks), thick, thin))
rows.sort(key=lambda r: (r[0], -r[1]))
for thin_n, thick_n, ks, thick, thin in rows:
    print(f"[{'/'.join(ks)}] 두꺼움 {thick[0]}({thick[5]},{thick[4][:4]},{thick[3][:4]}) {thick[1][:78]}")
    print(f"{'':>10} 얇음   {thin[0]}({thin[5]},{thin[4][:4]},{thin[3][:4]}) {thin[1][:78]}")
