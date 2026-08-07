#!/usr/bin/env python
# 해석별 물성 커버리지 — "필요한 것의 몇 %"를 재료×물성 격자로 정직하게 센다.
#
# 분모를 두 가지로 낸다.
#   (a) 셀 채움률  = 채워진 (재료, 필수물성) 칸 / 전체 칸.  물성 수집의 진척도.
#   (b) 재료 준비율 = 그 해석을 실제로 돌릴 수 있는 재료 수 / 대상 재료 수.  해석 가능성.
# (a)가 높아도 (b)는 낮을 수 있다 — 재료마다 마지막 한 칸이 다르면 그렇다.
#
# 사용: .venv/bin/python scripts/catalog/coverage_report.py [--json]
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"

E = "mechanical.youngs_modulus"
NU = "mechanical.poisson_ratio"
G = "mechanical.shear_modulus"
RHO = "physical.density"
CTE = "thermal.expansion_linear"
TC = "thermal.conductivity"
HC = "thermal.specific_heat"

# 택일군 — 하나만 있어도 그 역할이 채워진다.
PLAS = (("mechanical.yield_strength",), ("mechanical.tensile_strength", "mechanical.elongation_at_break"))
RATE = ("mechanical.cowper_symonds_c", "mechanical.cowper_symonds_p",
        "mechanical.dynamic_increase_factor", "mechanical.yield_strength_at_rate",
        "mechanical.johnson_cook_c")
PRONY = ("mechanical.prony_relaxation_time", "mechanical.prony_tensile_modulus",
         "mechanical.prony_shear_modulus", "mechanical.prony_relative_modulus", G)
WET = ("physical.contact_angle_water", "physical.surface_energy")
MOIST = ("physical.water_vapor_transmission", "physical.gas_permeability_h2o",
         "physical.diffusion_coefficient", "chemical.water_absorption_24h")
HYPER = ("mechanical.hyperelastic_coefficient", "mechanical.hyperelastic_exponent")
ADH = ("interface.peel_strength", "interface.lap_shear_strength", "interface.die_shear_strength")
# taxonomy 실명이다. volume_resistivity·loss_tangent로 쓰면 존재하지 않는 키를 세게 돼
# 전기·EMI가 실제보다 낮게 나온다(실제로 그랬다 — 유전율 하나만 세고 있었다).
ELEC = ("electrical.dielectric_constant", "electrical.resistivity_volume",
        "electrical.dissipation_factor")
FATIG = ("mechanical.fatigue_strength_coefficient", "mechanical.fatigue_ductility_coefficient",
         "mechanical.darveaux_constant", "mechanical.morrow_energy_coefficient")
O2 = ("physical.gas_permeability_o2", "physical.gas_solubility")
PHOTO = ("optical.excited_state_lifetime", "optical.stern_volmer_constant",
         "optical.bimolecular_quenching_rate")

# 대상 필터 — 전 재료가 대상이 아닌 해석이 있다. 벌크 금속에 층두께를 요구하면 척도가 왜곡된다.
FILMISH = ("film", "tape", "oca", "ocr", "psa", "adhesive", "coating", "laminate",
           "foil", "sheet", "pi base", "foam", "폼")
# 산소 소광은 두 역할로 갈라야 한다. 한 묶음으로 재면 분모가 거짓이 된다.
#   발광체 — 고립 분자다. 투과계수·용해도는 벌크 수송 물성이라 정의 자체가 없다.
#   매트릭스 — 벌크 필름이다. 여기수명·Stern-Volmer는 발광체가 아니면 없다.
# 이전 정의는 둘을 한 스코프에 넣고 양쪽을 다 요구해서, 92종 중 71종이
# "원리적으로 못 채우는 칸"을 세고 있었다. 0.0%는 수집 실패가 아니라 척도 오류였다.
EMITTER = ("emitter", "dopant", "tadf", "iridium", "ir(", "ir-", "pt(", "pd(",
           "ptoep", "pdoep", "porphyrin", "coumarin", "photoinitiator", "irgacure",
           "thioxanthone", "benzophenone", "quantum dot", "phosphorescent", "phosphor dye",
           "red phosphor", "blue emitter", "o2 sensor")
# 매트릭스는 산소가 실제로 확산해 지나가는 벌크 층이다.
MATRIX_O2 = ("oca", "psa", "optically clear", "color filter", "encapsulation", "barrier",
             "polyimide", "acrylate", "coverlay", "adhesive film")
# 피로는 반복하중을 받는 구조·솔더 계열이 대상이다.
FATIGUE_CAT = ("metal", "composite", "ceramic")
ELASTOMER = ("rubber", "foam")
ABSORBENT = ("polymer", "composite", "rubber", "foam")

# (이름, 필수물성, [택일군], 대상필터, 설명)
ANALYSES = [
    ("구조·강성", [E, NU, RHO], [], None,
     "정적 변형·모달. 모든 해석의 기본 골격"),
    ("낙하·충격", [E, NU, RHO], [PLAS, RATE], None,
     "율속 경화가 없으면 항복을 20~50% 과소평가한다"),
    ("열전달·방열", [RHO, TC, HC], [], None,
     "SoC 발열 → 방열시트 → 프레임 경로의 과도해석"),
    ("열응력·워피지", [E, NU, RHO, CTE], [], None,
     "리플로우 휨, 라미네이션 잔류응력, 온도사이클"),
    ("폴더블 벤딩", [E, NU, RHO], [PRONY], "film",
     "점탄성 완화가 접힘자국(crease) 회복을 지배한다"),
    ("결로(표면)", [RHO, TC, HC], [WET], None,
     "표면온도가 이슬점 아래로 가는가 + 물방울이 맺히는가"),
    ("결로(투습)", [RHO, TC, HC], [MOIST], "absorbent",
     "실링을 통과하는 수증기량. 밀폐공간 내부 결로"),
    ("초탄성(실링·완충)", [RHO], [HYPER], "elastomer",
     "가스켓 압축, 완충폼 거동"),
    ("접착·박리", [RHO], [ADH], "film",
     "낙하 시 실제로 깨지는 건 접착층인 경우가 많다"),
    ("전기·EMI", [], [ELEC], None,
     "고속 신호 무결성, 안테나, 차폐"),
    ("피로·수명", [E, RHO], [FATIG], "fatigue",
     "솔더 열피로, 장기 반복하중"),
    ("산소소광-발광체", [], [PHOTO], "emitter",
     "여기수명·Stern-Volmer. 소광 자체를 푸는 쪽"),
    ("산소확산-매트릭스", [], [O2], "matrix_o2",
     "산소가 지나가는 벌크 층의 투과·용해"),
]


def load():
    c = sqlite3.connect(DB)
    mat = {i: (n, cat) for i, n, cat in c.execute("select id,name,category from material")}
    own = defaultdict(set)
    for mid, k in c.execute("select material_id, property_key from property_value"):
        own[mid].add(k)
    return c, mat, own


def scope(mat, filt):
    if filt == "film":
        return [m for m in mat if any(w in mat[m][0].lower() for w in FILMISH)]
    if filt == "elastomer":
        return [m for m in mat if mat[m][1] in ELASTOMER]
    if filt == "absorbent":
        return [m for m in mat if mat[m][1] in ABSORBENT]
    if filt == "emitter":
        return [m for m in mat if any(w in mat[m][0].lower() for w in EMITTER)]
    if filt == "matrix_o2":
        return [m for m in mat if any(w in mat[m][0].lower() for w in MATRIX_O2)]
    if filt == "fatigue":
        return [m for m in mat if mat[m][1] in FATIGUE_CAT]
    return list(mat)


def grp_ok(ks, grp):
    """택일군 판정. PLAS는 '항복 OR (인장 AND 연신)'이라 중첩 튜플로 온다."""
    if grp and isinstance(grp[0], tuple):
        return any(all(k in ks for k in alt) for alt in grp)
    return any(k in ks for k in grp)


def compute():
    c, mat, own = load()
    out = []
    for name, must, anyof, filt, desc in ANALYSES:
        tgt = scope(mat, filt)
        n = len(tgt)
        # (a) 셀 채움률 — 필수물성은 칸 1개, 택일군은 통째로 칸 1개.
        cells = filled = 0
        miss_by_key = Counter()
        for m in tgt:
            ks = own[m]
            for k in must:
                cells += 1
                if k in ks:
                    filled += 1
                else:
                    miss_by_key[k] += 1
            for grp in anyof:
                cells += 1
                if grp_ok(ks, grp):
                    filled += 1
                else:
                    label = " | ".join(
                        ("+".join(x.split(".", 1)[1] for x in alt) if isinstance(alt, tuple)
                         else alt.split(".", 1)[1]) for alt in grp)
                    miss_by_key["택일군: " + label[:70]] += 1
        # (b) 재료 준비율
        ready = [m for m in tgt
                 if all(k in own[m] for k in must) and all(grp_ok(own[m], g) for g in anyof)]
        out.append({
            "name": name, "desc": desc, "n_target": n,
            "cells": cells, "filled": filled,
            "cell_pct": round(filled * 100 / cells, 1) if cells else 0.0,
            "n_ready": len(ready),
            "ready_pct": round(len(ready) * 100 / n, 1) if n else 0.0,
            "missing": miss_by_key.most_common(6),
        })
    return c, mat, own, out


def property_stats(c, mat, own):
    """물성별 보유 재료 수 — 무엇이 채워졌고 무엇이 비었나."""
    rows = []
    for key, nm, unit, dom in c.execute(
            "select key,name,si_unit,domain from property_definition order by domain,key"):
        m = c.execute("select count(distinct material_id) from property_value where property_key=?",
                      (key,)).fetchone()[0]
        v = c.execute("select count(*) from property_value where property_key=?", (key,)).fetchone()[0]
        rows.append({"key": key, "name": nm, "unit": unit, "domain": dom,
                     "n_mat": m, "n_val": v, "pct": round(m * 100 / len(mat), 1)})
    return rows


def main():
    c, mat, own, cov = compute()
    props = property_stats(c, mat, own)
    if "--json" in sys.argv:
        print(json.dumps({"coverage": cov, "properties": props}, ensure_ascii=False, indent=1))
        return

    tot_cells = sum(x["cells"] for x in cov)
    tot_filled = sum(x["filled"] for x in cov)
    print(f"\n{'해석':20s} {'대상':>5s} {'셀채움':>8s} {'재료준비':>9s}   가장 큰 공백")
    print("  " + "─" * 96)
    for x in cov:
        top = x["missing"][0][0].replace("택일군: ", "") if x["missing"] else "—"
        top = top.split(".", 1)[-1][:34]
        print(f"  {x['name']:20s} {x['n_target']:5d} "
              f"{x['filled']:5d}/{x['cells']:<5d} {x['cell_pct']:5.1f}% "
              f"{x['n_ready']:4d} {x['ready_pct']:5.1f}%   {top}")
    print("  " + "─" * 96)
    print(f"  {'전체':20s} {'':5s} {tot_filled:5d}/{tot_cells:<5d} "
          f"{tot_filled*100/tot_cells:5.1f}%")

    print(f"\n\n  물성 보유율 상위/하위 (재료 {len(mat)}종 기준)")
    ordered = sorted(props, key=lambda p: -p["n_mat"])
    print("\n  ── 잘 채워진 것")
    for p in ordered[:12]:
        print(f"   {p['n_mat']:4d}종 {p['pct']:5.1f}%  {p['name'][:30]:30s} {p['key']}")
    print("\n  ── 비어 있는 것(값은 있으나 재료 수가 적은 것)")
    for p in [x for x in ordered if x["n_mat"] > 0][-12:]:
        print(f"   {p['n_mat']:4d}종 {p['pct']:5.1f}%  {p['name'][:30]:30s} {p['key']}")
    zero = [p for p in props if p["n_mat"] == 0]
    print(f"\n  ── 값이 하나도 없는 정의: {len(zero)}종")
    for p in zero:
        print(f"        {p['name'][:34]:34s} {p['key']}")


if __name__ == "__main__":
    main()
