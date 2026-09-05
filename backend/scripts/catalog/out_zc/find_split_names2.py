# 규격코드 지문으로 이름이 갈린 재료쌍 후보를 뽑는다 — 64차 ZC (단위·연도·시료코드 잡음 제거판)
import sqlite3, json, re, os, itertools, sys
from collections import defaultdict

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
cnt = {r[0]: r[1] for r in c.execute("select material_id,count(*) from property_value group by material_id")}
mats = []
for i, n, code, cat, a in c.execute("select id,name,material_code,category,attributes from material"):
    try: d = json.loads(a) if a else {}
    except Exception: d = {}
    mats.append((i, n or "", code or "", cat or "", d.get("role", ""), cnt.get(i, 0), d))
byid = {m[0]: m for m in mats}

# 숫자 뒤에 오면 그 숫자가 규격코드가 아니라 측정조건임을 뜻하는 꼬리
UNIT = re.compile(r"^\s*(?:°?\s*[CKF]\b|C\b|K\b|U?M\b|[UÜ]M\b|NM\b|MM\b|CM\b|M\b|MPA|GPA|KPA|PA\b|"
                  r"H\b|HR\b|HOUR|MIN\b|SEC|S\b|MS\b|HZ|KHZ|MHZ|GHZ|WT|AT\.?%|VOL|PPM|DPI|MESH|RPM|"
                  r"V\b|W\b|KV\b|PSI|%|X\b|/|:|GRIT|LB|KG|G\b|ML|NP\b|Å|ANG)", re.I)
# 숫자 앞에 오면 조건임을 뜻하는 머리
PRE = re.compile(r"(?:AT|SAMPLE|CASE|SET|TYPE\s+OF|GRIT|MESH|NO\.|#|VER|REV|V)\s*$", re.I)
YEAR = re.compile(r"^(?:19|20)\d{2}$")

def occurrences(name):
    """(코어, 원문 위치) — 단위 꼬리·연도·시료코드 잡음을 걸러낸 규격코드 후보."""
    up = name.upper()
    out = set()
    for m in re.finditer(r"\d{3,}", up):
        run, s, e = m.group(0), m.start(), m.end()
        tail = up[e:e+6]
        head = up[max(0, s-12):s]
        if UNIT.match(tail):          # 180 C · 15 um · 250 MPa
            continue
        if PRE.search(head):          # at 180 · sample 3
            continue
        if YEAR.match(run) and not re.search(r"(AA|AL|EN\s?AW-?|ALLOY)\s*$", head):
            continue                  # (Li 2018) 같은 연도
        if re.search(r"[.,]\s*$", head) and YEAR.match(run):
            continue
        out.add(run)
        if len(run) == 5 and run.endswith("00"):
            out.add(run[:3])          # UNS C36000 ↔ CDA 360
        if len(run) == 3:
            out.add(run + "00")
    return out

def squash(s): return re.sub(r"[^A-Z0-9]", "", s.upper())

by_core = defaultdict(list)
for m in mats:
    for k in occurrences(m[1]):
        by_core[k].append(m)

pairs = {}
for k, group in by_core.items():
    if len(group) < 2 or len(group) > 20:
        continue
    for a, b in itertools.combinations(group, 2):
        sa, sb = squash(a[1]), squash(b[1])
        if sa in sb or sb in sa:      # 이름이 서로를 담으면 검색이 이미 둘 다 잡는다
            continue
        pairs.setdefault(tuple(sorted((a[0], b[0]))), set()).add(k)

rows = []
for (x, y), ks in pairs.items():
    A, B = byid[x], byid[y]
    thick, thin = (A, B) if A[5] >= B[5] else (B, A)
    rows.append((thin[5], -thick[5], sorted(ks), thick, thin))
rows.sort()
print(f"# 후보쌍 {len(pairs)} (재료 {len(mats)}종 · 코어 {len(by_core)}개)")
for thin_n, negthick, ks, thick, thin in rows:
    print(f"[{'/'.join(ks)}] T {thick[0]}({thick[5]}|{thick[4][:4]}|{thick[3][:4]}) {thick[1][:76]}")
    print(f"{'':>{len('/'.join(ks))+3}} t {thin[0]}({thin[5]}|{thin[4][:4]}|{thin[3][:4]}) {thin[1][:76]}")
