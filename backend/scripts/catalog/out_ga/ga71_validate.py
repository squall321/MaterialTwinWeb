# 적재 없이 out_ga/ga71_*.json 을 적재기·무결성검사 규칙으로 미리 검증한다(라이브 DB 는 읽기 전용).
import json, os, sqlite3, glob, collections

DB = os.environ.get("MATERIALTWIN_DATA_DIR",
                    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web") + "/materialtwin.db"
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
defs = {k: u for k, u in c.execute("select key,si_unit from property_definition")}
mats = {n: i for n, i in c.execute("select name,id from material")}
srcs = {d for (d,) in c.execute("select doi from source where doi is not null")}

# ingest_agent_json.py 의 RANGE 에서 이 배치가 쓰는 키만 옮겼다(2026-09-09 확인).
RANGE = {"mechanical.prony_relaxation_time": (1e-40, 1e40),
         "mechanical.hyperelastic_coefficient": (-1e9, 1e9),
         "mechanical.youngs_modulus": (1e3, 1.5e12),
         "mechanical.poisson_ratio": (-1.0, 0.5),
         "physical.density": (1.0, 25000.0),
         "thermal.expansion_linear": (-1e-4, 5e-3)}
METHOD_OK = {"measured", "handbook", "computed", "estimated"}
bad = 0


def cond_sig(d):
    return json.dumps(d, sort_keys=True, ensure_ascii=False) if d else ""


for path in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "ga71_*.json"))):
    doc = json.load(open(path, encoding="utf-8"))
    print(f"\n=== {os.path.basename(path)}  batch={doc.get('batch')}")
    for ent in doc["materials"]:
        name = ent.get("match_name")
        if name:
            mid = mats.get(name)
            print(f"  재료 매칭: {'[' + str(mid) + ']' if mid else '✗ 이름이 DB 에 없다'} {name[:70]}")
            if mid is None:
                bad += 1
        else:
            nm = ent["new_material"]
            print(f"  신규 재료: {nm['name'][:100]}  ({len(nm['name'])}자, category={nm['category']})")
            if len(nm["name"]) > 200:
                print("    ✗ 재료명 200자 초과"); bad += 1
            if nm["name"] in mats:
                print(f"    ! 같은 이름이 이미 DB 에 있다 [{mats[nm['name']]}]"); bad += 1
        src = ent["source"]
        if src.get("kind") in ("journal", "book") and not src.get("doi"):
            print("    ✗ journal/book 출처인데 DOI 가 없다 — 70차에 무결성 검사가 잡은 항목"); bad += 1
        else:
            print(f"    출처 doi={src.get('doi')}  {'(이미 DB 에 있는 DOI)' if src.get('doi') in srcs else '(신규)'}")
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
                print(f"    ✗ 범위 밖 {k}={v} (허용 {lo}~{hi})"); bad += 1
            if p.get("method") not in METHOD_OK:
                print(f"    ✗ method 어휘 밖: {p.get('method')}"); bad += 1
            if p.get("tier") not in (1, 2, 3, 4):
                print(f"    ✗ tier {p.get('tier')}"); bad += 1
            if not p.get("notes"):
                print(f"    ✗ notes 없음 {k}"); bad += 1
            cd = p.get("conditions") or {}
            # 무결성검사: Prony 항에 항번호 (장기 평형계수만 예외)
            if k.startswith("mechanical.prony_") and k != "mechanical.prony_long_term_modulus":
                if "term" not in json.dumps(cd, ensure_ascii=False):
                    print(f"    ✗ Prony 항번호 없음 {k}"); bad += 1
            # 브리프 §2 — 기준온도가 조건에 있는가(없으면 없다고 적었는가)
            if k.startswith("mechanical.prony_"):
                if not any(x in cd for x in ("reference_temperature_c", "reference_temperature_k",
                                             "reference_temperature_printed")):
                    print(f"    ✗ Prony 항에 기준온도 정보가 없다(있다/없다 둘 다 안 적혔다) {k}"); bad += 1
                if "relaxation_mode" not in cd and cd.get("term", "").startswith(("g", "e", "E")):
                    print(f"    ✗ relaxation_mode 없음 {k}"); bad += 1
            sig = (k, cond_sig(cd))
            if sig in seen and abs(seen[sig] - float(v)) > 1e-15:
                print(f"    ✗ 조건 충돌 {k}: {seen[sig]} vs {v}"); bad += 1
            elif sig in seen:
                print(f"    ! 같은 조건 중복행 {k}={v}"); bad += 1
            seen[sig] = float(v)
            # 무결성검사 SQL 과 같은 규칙 — 평형항(term 에 inf/equil)은 급수 밖이라 항수에서 뺀다.
            t = str(cd.get("term", "")).lower()
            if not (k == "mechanical.prony_relative_modulus" and ("inf" in t or "equil" in t)):
                terms[(cd.get("set_id"), cd.get("series"), k)] += 1
        # 무결성검사: 가중치·완화시간 항수 일치(set_id + series 로 묶는다. 평형항은 term 에 inf 가 있어 빠진다)
        groups = collections.defaultdict(dict)
        for (sid, ser, k), n in terms.items():
            groups[(sid, ser)][k] = n
        for (sid, ser), d in sorted(groups.items(), key=lambda x: str(x[0])):
            nt = d.get("mechanical.prony_relaxation_time", 0)
            nw = d.get("mechanical.prony_relative_modulus", 0)
            ne = d.get("mechanical.prony_tensile_modulus", 0)
            nb = d.get("mechanical.prony_relative_bulk_modulus", 0)
            for lbl, n in (("g", nw), ("E", ne), ("K", nb)):
                if nt and n and nt != n:
                    print(f"    ✗ 항수 불일치 {sid}/{ser}: tau {nt} vs {lbl} {n}"); bad += 1
            print(f"    · {sid} / {ser}: " + ", ".join(f"{kk.split('.')[-1]}x{vv}" for kk, vv in sorted(d.items())))
        print(f"    행 {len(ent['properties'])}")

print(f"\n{'위반 0 — 통과' if bad == 0 else f'위반 {bad} 건'}")
