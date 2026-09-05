# 규격 별칭을 재료 attributes.aliases 에 박는다 — 64차 ZC. 각 별칭은 그 재료의 출처 제목에 실제로 인쇄된 이름만 쓴다.
import sqlite3, json, os, re, sys

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
APPLY = "--apply" in sys.argv
if "--db" in sys.argv: DB = sys.argv[sys.argv.index("--db") + 1]

# 재료 id → 별칭 목록. 전부 그 재료에 이미 붙어 있는 출처 제목에 인쇄된 표기다(아래에서 전수 검증한다).
ALIASES = {
  1:  ["Grade 201", "UNS S20100"],
  2:  ["Grade 301", "UNS S30100"],
  3:  ["Grade 304", "UNS S30400", "AISI Type 304", "AISI 304"],
  4:  ["Grade 304L", "UNS S30403", "AISI 304L"],
  5:  ["Grade 316", "UNS S31600", "AISI Type 316", "SS-316"],
  6:  ["Grade 316L", "UNS S31603", "AISI Type 316L", "AISI 316L", "Type 316L"],
  7:  ["Grade 410", "UNS S41000", "AISI Type 410"],
  8:  ["Grade 420", "UNS S42000", "AISI Type 420"],
  9:  ["Grade 430", "UNS S43000", "AISI 430"],
  10: ["17-4 PH", "UNS S17400", "Alloy 17-4PH", "Grade 630"],
  12: ["SAE-AISI 4140", "AISI 4140", "SAE 4140", "42CrMo4"],
  19: ["UNS A96061", "AA6061-T6"],
  22: ["7050-T73651", "AA7050-T7451"],
  23: ["7075-T651", "AA7075-T6", "AA 7075-T6", "AA7075"],
  24: ["Ti-6Al-4V", "Ti-6Al-4V Grade 5", "TA6V", "TC4"],
  25: ["Ti-6Al-4V ELI", "Grade 23", "UNS R56401"],
  26: ["Ti-3Al-2.5V", "Ti 3Al 2.5V", "UNS R56320", "Grade 9"],
  27: ["Inconel 625", "INCONEL alloy 625", "Nickel Alloy 625", "Alloy 625", "N06625"],
  30: ["Grade 1 Unalloyed Ti", "UNS R50250", "CP Ti Grade 1", "TIMETAL 35A"],
  31: ["Grade 2 Unalloyed Ti", "UNS R50400", "CP Ti Grade 2", "TIMETAL 50A"],
  32: ["Grade 4 Unalloyed Ti", "UNS 50700", "CP Ti Grade 4", "TIMETAL 75A", "Titanium Grade 4"],
  33: ["AZ31B-H24", "UNS M11311", "M11311"],
  34: ["AZ91D-F", "M11916"],
  35: ["ZK60A-T5", "UNS M16600"],
  36: ["SAE-AISI 1045", "AISI 1045", "SAE1045", "45 steel"],
  37: ["UNS C26000", "Cartridge Brass"],
  38: ["UNS C36000", "Free-Cutting Brass", "Free Cutting Brass"],
  39: ["UNS C51000", "Phosphor Bronze"],
  40: ["Inconel 718", "INCONEL alloy 718", "Nickel Alloy 718", "Alloy 718", "N07718"],
}
BASIS = ("64차 ZC — 이 재료의 규격 지정이 인쇄되는 다른 표기다. 각 별칭은 이 재료에 이미 붙어 있는 "
         "출처 제목에 그대로 인쇄된 이름만 넣었다(출처 id 는 aliases_sources). 값·조건·출처를 바꾸지 "
         "않았고 레코드를 합치지도 않았다. 붙인 이유는 카탈로그 이름이 `_` 로 붙은 표기라 "
         "`name LIKE '%<규격명>%'` 검색이 이 레코드를 못 잡기 때문이다(브리프 586·608).")

def norm(s): return re.sub(r"\s+", " ", s or "").strip().lower()

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
rows = {r["id"]: r for r in con.execute("select id,name,attributes from material")}
allnames = [(r["id"], r["name"]) for r in rows.values()]

plan, rejected = [], []
seen = {}
for mid, al in sorted(ALIASES.items()):
    m = rows[mid]
    titles = [t for (t,) in con.execute(
        """select distinct s.title from property_value v join source s on s.id=v.source_id
            where v.material_id=?""", (mid,))]
    keep, src = [], {}
    for a in al:
        na, nn = norm(a), norm(m["name"])
        if na in nn:
            rejected.append((mid, a, "이미 이름이 담고 있다 — 검색 도달이 안 는다")); continue
        hit = [t for t in titles if na in norm(t)]
        if not hit:
            rejected.append((mid, a, "이 재료의 출처 제목에 인쇄된 적이 없다")); continue
        sid = con.execute("""select s.id from property_value v join source s on s.id=v.source_id
                             where v.material_id=? and lower(s.title) like ? limit 1""",
                          (mid, "%" + na + "%")).fetchone()
        keep.append(a); src[a] = sid[0] if sid else None
    for a in keep:
        seen.setdefault(norm(a), []).append(mid)
    plan.append((mid, m["name"], keep, src))

dupes = {a: ms for a, ms in seen.items() if len(ms) > 1}
print(f"== 별칭 계획 — 재료 {len(plan)}종 · 별칭 {sum(len(k) for _,_,k,_ in plan)}개")
for mid, nm, keep, src in plan:
    print(f"  {mid:4d} {nm}")
    for a in keep: print(f"        + {a!r:34s} (출처 {src[a]})")
print(f"\n== 기각 {len(rejected)}개")
for mid, a, why in rejected: print(f"  {mid:4d} - {a!r:34s} {why}")
print(f"\n== 두 재료에 같은 별칭: {dupes if dupes else '없음'}")

# 별칭이 다른 재료 이름과 충돌하는지 — 별칭 검색이 엉뚱한 재료를 부르지는 않는지 본다
print("\n== 별칭이 다른 재료 이름에도 걸리는 경우")
coll = 0
for mid, nm, keep, src in plan:
    for a in keep:
        others = [(i, n) for i, n in allnames if i != mid and norm(a) in norm(n)]
        if others:
            coll += 1
            print(f"  {mid} {a!r} → {[(i, n[:52]) for i, n in others[:4]]}")
print(f"  총 {coll}건")

if APPLY:
    n = 0
    for mid, nm, keep, src in plan:
        if not keep: continue
        d = json.loads(rows[mid]["attributes"] or "{}")
        d["aliases"] = keep
        d["aliases_basis"] = BASIS
        d["aliases_sources"] = {a: src[a] for a in keep}
        con.execute("update material set attributes=?, updated_at=updated_at where id=?",
                    (json.dumps(d, ensure_ascii=False), mid))
        n += 1
    con.commit()
    print(f"\n적용: 재료 {n}종")
else:
    print("\n(예행 — --apply 를 주면 쓴다)")
con.close()
