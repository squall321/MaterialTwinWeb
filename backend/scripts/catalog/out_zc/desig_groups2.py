# 규격 지정을 정규화해 같은 지정이 다른 표기로 서 있는 재료군을 모은다 — 64차 ZC (2판: 연도·소결온도 잡음 제거)
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

B = r"(?<![A-Za-z0-9])"      # `_` 를 경계로 본다 — `SUS_17-4PH_H900`·`C36000_FreeCutting` 이 안 걸리던 이유다
E = r"(?![A-Za-z0-9])"
def hits(name):
    out = set()
    up = name
    # ── 알루미늄 전신재 — 연도·소결온도와 갈라야 한다
    for m in re.finditer(B + r"(AA|EN\s?AW[-\s]?|Al[\s-]?)?([1-8]\d{3})([-\s]?[THFO]\d{0,4})?" + E, up, re.I):
        pre, num, tmp = m.group(1) or "", m.group(2), (m.group(3) or "").strip("- ")
        ctx = up[max(0, m.start()-45): m.end()+45].lower()
        strong = bool(pre) or bool(tmp) or "alumin" in ctx or "aluminum" in ctx
        if not strong: continue
        if 1900 <= int(num) <= 2030 and not pre: continue
        out.add("AL:" + num + tmp.upper())
    for m in re.finditer(B + r"(?:SUS|AISI|SAE|Type|SS|UNS\s?S)[\s_-]?(\d{3}[A-Z]?)" + E, up, re.I):
        out.add("SUS:" + m.group(1).upper())
    for m in re.finditer(B + r"C(\d{5})" + E, up):        # UNS 구리
        out.add("CU:" + m.group(1))
    for m in re.finditer(B + r"(?:CDA|C)\s?(\d{3})" + E, up):   # CDA 3자리 = UNS 5자리 + 00
        out.add("CU:" + m.group(1) + "00")
    for m in re.finditer(B + r"(A[ZEM]|ZK|ZE|WE)\s?(\d{2}[A-Z]?)" + E, up):
        out.add("MG:" + (m.group(1) + m.group(2)).upper())
    for m in re.finditer(r"Ti[\s_-]?6\s?Al[\s_-]?4\s?V", up, re.I): out.add("TI:6AL4V")
    for m in re.finditer(r"Ti[\s_-]?3\s?Al[\s_-]?2\.?5\s?V", up, re.I): out.add("TI:3AL25V")
    for m in re.finditer(B + r"(ZAMAK|ZA)[\s-]?(\d{1,2})" + E, up, re.I):
        out.add("ZN:" + m.group(1).upper() + m.group(2))
    for m in re.finditer(B + r"(?:Inconel|Alloy)[\s_-]?(\d{3})" + E, up, re.I): out.add("NI:" + m.group(1))
    for m in re.finditer(B + r"S(\d{2})C" + E, up):  out.add("STEEL:S%sC" % m.group(1))
    for m in re.finditer(B + r"SCM[\s_-]?(\d{3})" + E, up, re.I): out.add("STEEL:SCM" + m.group(1))
    for m in re.finditer(r"17[\s_-]?4\s?PH", up, re.I): out.add("STEEL:174PH")
    for m in re.finditer(B + r"SACX?[\s_-]?(\d{3,4})" + E, up, re.I): out.add("SAC:" + m.group(1))
    for m in re.finditer(B + r"RO[\s_-]?(\d{4})[A-Z]?" + E, up, re.I): out.add("RO:" + m.group(1))
    for m in re.finditer(B + r"P(9[12])" + E, up): out.add("STEEL:P" + m.group(1))
    for m in re.finditer(B + r"1\.(\d{4})" + E, up): out.add("WNR:1." + m.group(1))
    return out

groups = defaultdict(list)
for m in mats:
    for d in hits(m[1]): groups[d].append(m)

def forms(name, key):
    return {re.sub(r"[^A-Z0-9]", "", s.upper()) for s in [name]}

n = 0
for k in sorted(groups):
    g = groups[k]
    if len(g) < 2: continue
    n += 1
    print(f"\n### {k}  ({len(g)}종)")
    for m in sorted(g, key=lambda x: -x[4]):
        print(f"    {m[0]:5d} 값{m[4]:4d} {m[3][:4]:5s} {m[2][:4]:5s} {m[1][:90]}")
print(f"\n# 지정군 {n}개 (2종 이상) / 지정이 잡힌 재료 {len({m[0] for g in groups.values() for m in g})}종")

# ── 템퍼를 벗긴 기저 지정군 — `7075-T6` 와 `7075-T651` 은 여기서만 만난다
base = defaultdict(list)
for m in mats:
    for d in hits(m[1]):
        if d.startswith(("AL:", "MG:", "CU:", "SUS:", "TI:", "ZN:", "SAC:", "RO:")):
            b = re.sub(r"(?<=AL:\d{4}).*$", "", d)
            base[b].append(m)
print("\n\n@@@@ 템퍼 제거 기저군 @@@@")
nb = 0
for k in sorted(base):
    g = {m[0]: m for m in base[k]}.values()
    g = sorted(g, key=lambda x: -x[4])
    if len(g) < 2: continue
    tempers = {d for m in g for d in hits(m[1]) if d.startswith(k)}
    if len(tempers) < 2: continue      # 표기가 안 갈렸으면 이미 한 이름이다
    nb += 1
    print(f"\n### {k}  ({len(g)}종 · 지정 표기 {sorted(tempers)})")
    for m in g:
        print(f"    {m[0]:5d} 값{m[4]:4d} {m[3][:4]:5s} {m[2][:4]:5s} {m[1][:90]}")
print(f"\n# 표기가 갈린 기저군 {nb}개")
