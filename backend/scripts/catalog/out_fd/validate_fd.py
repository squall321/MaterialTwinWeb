# 적재 없이 out_fd JSON 을 적재기·무결성검사 규칙으로 미리 검증한다(라이브 DB 는 읽기 전용).
import json, os, sqlite3, sys, glob, collections

DB = os.environ.get("MATERIALTWIN_DATA_DIR",
                    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web") + "/materialtwin.db"
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
defs = {k: u for k, u in c.execute("select key,si_unit from property_definition")}
mats = {n: i for n, i in c.execute("select name,id from material")}

RANGE = {"mechanical.prony_relaxation_time": (1e-40, 1e40),
         "mechanical.prony_shear_modulus": (1.0, 1e11)}
METHOD_OK = {"measured", "handbook", "computed", "estimated", "digitized"}
bad = 0

def cond_sig(d):
    return json.dumps(d, sort_keys=True, ensure_ascii=False) if d else ""

for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "fd70_*.json"))):
    doc = json.load(open(path, encoding="utf-8"))
    print(f"\n=== {os.path.basename(path)}  batch={doc.get('batch')}")
    for ent in doc["materials"]:
        name = ent.get("match_name")
        mid = mats.get(name) if name else None
        if name:
            print(f"  재료 매칭: {'[' + str(mid) + ']' if mid else '✗ 이름이 DB 에 없다'} {name[:70]}")
            if mid is None:
                bad += 1
        else:
            nm = ent["new_material"]
            print(f"  신규 재료: {nm['name'][:90]}  ({len(nm['name'])}자, category={nm['category']})")
            if len(nm["name"]) > 200:
                print("    ✗ 재료명 200자 초과"); bad += 1
            if nm["name"] in mats:
                print(f"    ! 같은 이름이 이미 DB 에 있다 [{mats[nm['name']]}]"); bad += 1
        src = ent["source"]
        if not (src.get("doi") or src.get("url") or src.get("title")):
            print("    ✗ 출처 없음"); bad += 1
        seen, terms = {}, collections.Counter()
        for p in ent["properties"]:
            k, v, u = p["key"], p["value"], p.get("unit")
            if k not in defs:
                print(f"    ✗ 미정의 key {k}"); bad += 1; continue
            si = defs[k]
            if si and u and u.replace(" ", "") != si.replace(" ", ""):
                print(f"    ✗ 단위 불일치 {k}: {u} != {si}"); bad += 1
            lo, hi = RANGE.get(k, (None, None))
            if lo is not None and not (lo <= float(v) <= hi):
                print(f"    ✗ 범위 밖 {k}={v}"); bad += 1
            if p.get("method") not in METHOD_OK:
                print(f"    ✗ method 어휘 밖: {p.get('method')}"); bad += 1
            if p.get("tier") not in (1, 2, 3, 4):
                print(f"    ✗ tier {p.get('tier')}"); bad += 1
            if not p.get("notes"):
                print(f"    ✗ notes 없음 {k}"); bad += 1
            # 무결성검사: Prony 항에 항번호
            if k.startswith("mechanical.prony_") and k != "mechanical.prony_long_term_modulus":
                if "term" not in json.dumps(p.get("conditions") or {}):
                    print(f"    ✗ Prony 항번호 없음 {k}"); bad += 1
            sig = (k, cond_sig(p.get("conditions")))
            if sig in seen and abs(seen[sig] - float(v)) > 1e-15:
                print(f"    ✗ 조건 충돌 {k}: {seen[sig]} vs {v}"); bad += 1
            elif sig in seen:
                print(f"    ! 같은 조건 중복행 {k}={v}"); bad += 1
            seen[sig] = float(v)
            cd = p.get("conditions") or {}
            terms[(cd.get("set_id"), cd.get("series"), k)] += 1
        # 무결성검사: 가중치·완화시간 항수 일치(set_id + series 로 묶는다)
        groups = collections.defaultdict(dict)
        for (sid, ser, k), n in terms.items():
            groups[(sid, ser)][k] = n
        for (sid, ser), d in sorted(groups.items(), key=lambda x: str(x[0])):
            nt = d.get("mechanical.prony_relaxation_time", 0)
            nw = d.get("mechanical.prony_relative_modulus", 0)
            nb = d.get("mechanical.prony_relative_bulk_modulus", 0)
            ne = d.get("mechanical.prony_tensile_modulus", 0)
            if nt and nw and nt != nw:
                print(f"    ✗ 항수 불일치 {sid}/{ser}: tau {nt} vs g {nw}"); bad += 1
            if nt and ne and nt != ne:
                print(f"    ✗ 항수 불일치 {sid}/{ser}: tau {nt} vs E {ne}"); bad += 1
            print(f"    · {sid} / {ser}: " + ", ".join(f"{kk.split('.')[-1]}×{vv}" for kk, vv in sorted(d.items())))
        print(f"    총 {len(ent['properties'])}행")
print(f"\n{'✓ 위반 0' if bad == 0 else f'✗ 위반 {bad}건'}")
sys.exit(1 if bad else 0)
