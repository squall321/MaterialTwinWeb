# 규격코드 지문으로 이름이 갈린 재료쌍 후보를 뽑는다 — 64차 ZC (3판: 조성변종·단위 잡음 제거)
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
    mats.append((i, n or "", code or "", cat or "", d.get("role", ""), cnt.get(i, 0), d))
byid = {m[0]: m for m in mats}

UNIT = re.compile(r"^\s*(?:°?\s*[CKF]\b|C\b|K\b|U?M\b|[UÜ]M\b|NM\b|MM\b|CM\b|M\b|MPA|GPA|KPA|PA\b|"
                  r"H\b|HR\b|HOUR|MIN\b|SEC|S\b|MS\b|HZ|KHZ|MHZ|GHZ|WT|AT\.?%|VOL|PPM|DPI|MESH|RPM|"
                  r"V\b|W\b|KV\b|PSI|%|X\b|/|:|GRIT|LB|KG|G\b|ML|NP\b|Å|ANG|NP)", re.I)
PRE = re.compile(r"(?:AT|SAMPLE|CASE|SET|GRIT|MESH|NO\.|#|VER|REV)\s*$", re.I)
YEAR = re.compile(r"^(?:19|20)\d{2}$")
CU   = re.compile(r"(CDA|BRASS|BRONZE|COPPER|\bCU\b|C1\d{4}|C2\d{4}|C3\d{4}|C5\d{4})", re.I)
# 조성 변종 신호 — 이 조각이 한쪽에만 있으면 '같은 실물' 이 아니라 '그것으로 만든 다른 것' 이다
VAR = re.compile(r"(\+|\bwt\s?%|\bvol\s?%|\bat\s?%|\bphr\b|\bfilled\b|\bfiller\b|\bblend\b|\breinforc|"
                 r"\bdoped\b|\bwith\b|\bcoating\b|\bcoated\b|\bjoint\b|\bweld|\bsurface\b|\badherend\b|"
                 r"\bsubstrate\b|\bdrug\b|\bpaste\b|\bcomposite\b|\bfibre\b|\bfiber\b)", re.I)

def cores(name):
    up, out = name.upper(), set()
    for m in re.finditer(r"\d{3,}", up):
        run, s, e = m.group(0), m.start(), m.end()
        if UNIT.match(up[e:e+6]):  continue
        if PRE.search(up[max(0,s-12):s]): continue
        if YEAR.match(run) and not re.search(r"(AA|AL|EN\s?AW-?|ALLOY)\s*$", up[max(0,s-12):s]): continue
        if len(run) == 3 and not CU.search(name): continue     # 맨 3자리는 구리계에서만 코어로 본다
        out.add(run)
        if len(run) == 5 and run.endswith("00") and CU.search(name): out.add(run[:3])
        if len(run) == 3 and CU.search(name): out.add(run + "00")
    return out

def grams(name, k=6):
    """문자·숫자가 섞인 k-그램 — `Ti6Al4V` 처럼 숫자런이 짧은 조성 표기를 잡는다."""
    s = re.sub(r"[^A-Z0-9]", "", name.upper())
    out = set()
    for i in range(len(s) - k + 1):
        g = s[i:i+k]
        if re.search(r"\d", g) and re.search(r"[A-Z]", g): out.add("G:" + g)
    return out

def squash(s): return re.sub(r"[^A-Z0-9]", "", s.upper())

by_fp = defaultdict(list)
for m in mats:
    for k in cores(m[1]) | grams(m[1]):
        by_fp[k].append(m)

pairs = {}
for k, group in by_fp.items():
    if len(group) < 2 or len(group) > 12: continue
    for a, b in itertools.combinations(group, 2):
        sa, sb = squash(a[1]), squash(b[1])
        if sa in sb or sb in sa: continue
        pairs.setdefault(tuple(sorted((a[0], b[0]))), set()).add(k)

def variant_pair(A, B):
    """한쪽에만 조성·공정 변종 신호가 있으면 '같은 실물' 후보에서 뺀다."""
    return bool(VAR.search(A[1])) != bool(VAR.search(B[1]))

kept, dropped_variant, dropped_shape = [], 0, 0
for (x, y), ks in pairs.items():
    A, B = byid[x], byid[y]
    thick, thin = (A, B) if A[5] >= B[5] else (B, A)
    if variant_pair(A, B): dropped_variant += 1; continue
    if not (thin[5] <= 15 and thick[5] >= 20): dropped_shape += 1; continue
    kept.append((thin[5], -thick[5], sorted(ks), thick, thin))
kept.sort()
print(f"# 지문 일치쌍 {len(pairs)} → 조성변종 제외 {dropped_variant} · 모양(얇음<=15 & 두꺼움>=20) 미달 {dropped_shape} → 후보 {len(kept)}")
for thin_n, negthick, ks, thick, thin in kept:
    tag = ",".join(sorted(k for k in ks if not k.startswith("G:")))[:24] or "gram"
    print(f"[{tag}] T {thick[0]}({thick[5]}|{thick[4][:4]}|{thick[3][:4]}) {thick[1][:74]}")
    print(f"{'':>{len(tag)+3}} t {thin[0]}({thin[5]}|{thin[4][:4]}|{thin[3][:4]}) {thin[1][:74]}")
