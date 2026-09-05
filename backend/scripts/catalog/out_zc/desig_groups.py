# 규격 지정(alloy/UNS/등급코드)을 정규화해 같은 지정이 서로 다른 표기로 서 있는 재료군을 모은다 — 64차 ZC
import sqlite3, json, re, os
from collections import defaultdict

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
cnt = {r[0]: r[1] for r in c.execute("select material_id,count(*) from property_value group by material_id")}
mats = []
for i, n, cat, a in c.execute("select id,name,category,attributes from material"):
    try: d = json.loads(a) if a else {}
    except Exception: d = {}
    mats.append((i, n or "", cat or "", d.get("role", ""), cnt.get(i, 0), d))

# (정규화키, 정규식) — 규격 지정 체계의 화이트리스트. 지정이 없는 이름은 아무 군에도 안 들어간다.
PATS = [
 ("AL",   re.compile(r"(?:\bAA|\bEN\s?AW[-\s]?|\bAl[\s-]?|\b)([1-8]\d{3})(?:[-\s]?([THFO]\d{0,4}))?\b", re.I)),
 ("SUS",  re.compile(r"\b(?:SUS|AISI|SAE|Type|SS|UNS\s?S|ASTM\s?A)[\s_-]?(\d{3}[A-Z]?)\b", re.I)),
 ("WNR",  re.compile(r"\b1\.(\d{4})\b")),
 ("CU",   re.compile(r"\b(?:C|CDA\s?|UNS\s?C)(\d{3,5})\b")),
 ("MG",   re.compile(r"\b(A[ZEM]|ZK|ZE|WE)\s?(\d{2}[A-Z]?)\b", re.I)),
 ("TI64", re.compile(r"\bTi[\s-]?6\s?Al[\s-]?4\s?V\b", re.I)),
 ("TIGR", re.compile(r"\bTi[\s_-]?Grade\s?(\d)\b|\bGrade\s?(\d)\b", re.I)),
 ("ZN",   re.compile(r"\b(ZAMAK|ZA)[\s-]?(\d{1,2})\b", re.I)),
 ("INC",  re.compile(r"\b(?:Inconel|Alloy)[\s_-]?(\d{3})\b", re.I)),
 ("SC",   re.compile(r"\bS(\d{2})C\b")),
 ("SCM",  re.compile(r"\bSCM[\s_-]?(\d{3})\b", re.I)),
 ("PH",   re.compile(r"\b17[\s-]?4\s?PH\b", re.I)),
 ("SAC",  re.compile(r"\bSACX?[\s-]?(\d{3,4})\b", re.I)),
 ("NDFE", re.compile(r"\bN(3[05-9]|4[0258]|5[02])\b")),
 ("RO",   re.compile(r"\bRO\s?(\d{4})[A-Z]?\b", re.I)),
 ("CR",   re.compile(r"\bP(9[12])\b")),
]

def desigs(name):
    out = set()
    for tag, pat in PATS:
        for m in pat.finditer(name):
            g = [x for x in m.groups() if x] if m.groups() else []
            out.add(tag + ":" + "".join(g).upper())
    return out

groups = defaultdict(list)
for m in mats:
    for d in desigs(m[1]):
        groups[d].append(m)

def squash(s): return re.sub(r"[^A-Z0-9]", "", s.upper())

nprint = 0
for k in sorted(groups):
    g = groups[k]
    if len(g) < 2: continue
    # 같은 지정을 '같은 인쇄형' 으로 담고 있으면 검색이 둘 다 잡는다 — 표기가 갈린 군만 본다
    forms = set()
    for m in g:
        for tag, pat in PATS:
            mm = pat.search(m[1])
            if mm and (tag + ":" + "".join(x for x in mm.groups() if x).upper() if mm.groups() else tag + ":") == k:
                forms.add(squash(mm.group(0)))
    nprint += 1
    print(f"\n### {k}  (재료 {len(g)}종 · 인쇄형 {sorted(forms)})")
    for m in sorted(g, key=lambda x: -x[4]):
        print(f"    {m[0]:5d} 값{m[4]:4d} {m[3][:4]:5s} {m[2][:4]:5s} {m[1][:88]}")
print(f"\n# 지정군 {nprint}개 (2종 이상)")
