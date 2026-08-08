# 결로(표면) 젖음 물성 수집 결과를 F_dew.json으로 조립하는 스크립트
import json, os, re, sys

OUT = "/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/w6parts/F_dew.json"
TGT = "/home/koopark/claude/MaterialTwinWeb/.agent_work/targets/g_dew.txt"

names = {}
for line in open(TGT, encoding="utf-8"):
    if line.startswith("#"):
        continue
    p = line.rstrip("\n").split("\t")
    if len(p) >= 4:
        names[int(p[0])] = p[1]

ACC = "https://www.accudynetest.com/polymer_surface_data/%s.pdf"


def acc_src(slug, label):
    return {
        "title": "Surface Energy Data for %s - AccuDyne Test polymer surface data compilation (Diversified Enterprises, 2009)" % label,
        "kind": "database",
        "url": ACC % slug,
        "year": 2009,
    }


mats = {}   # id -> {"match_name":..., "source":..., "properties":[...]}
rows = []   # (mid, source, prop)


def add(mid, source, prop):
    rows.append((mid, source, prop))


# ---------------------------------------------------------------- recipes
# 각 recipe: (slug, label, key, value, unit, method, cond_base, verify_string, source_detail)
R = {}

R["pi_ca"] = dict(slug="polyimide_kapton", label="Polyimide, CAS # 25038-81-7",
    key="physical.contact_angle_water", value=70.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 70",
    detail="Egitto, 1990 (ref 65) 행, Mst. Type = 'Contact angle', Data = 'θWY = 70o; no temp cited', Comments = 'Kapton film.'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "as-received Kapton film, no plasma / no corona (원자료가 표면 이력을 적지 않았다)",
          "temperature": "not cited"})

R["pi_se"] = dict(slug="polyimide_kapton", label="Polyimide, CAS # 25038-81-7",
    key="physical.surface_energy", value=0.0440, unit="J/m^2", method="contact angle, van Oss acid-base (LW/AB)",
    verify="γs = 44.0 mJ/m2",
    detail="Gotoh, 2004 (ref 92) 행 — 'γs = 44.0 mJ/m2 (γsLW = 42.5, γsAB = 1.5, γs+ = 0.1, γs- = 6.0)', 테스트 액체 water/diiodomethane/ethylene glycol, sessile drop, Kapton 100H",
    cond={"method_detail": "sessile drop, acid-base analysis; LW 42.5, AB 1.5, gamma+ 0.1, gamma- 6.0 mJ/m^2",
          "surface_treatment": "as-received Kapton 100H film, untreated",
          "temperature": "not cited"})

R["pi_upilex_ca"] = dict(slug="polyimide_kapton", label="Polyimide, CAS # 25038-81-7",
    key="physical.contact_angle_water", value=71.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 71",
    detail="Matienzo, 1992 (ref 243) 행 — 'θWY = 71o; no temp cited', Comments = 'Upilex-R (BPDA-ODA) film.'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "as-received Upilex-R (BPDA-ODA) film, untreated", "temperature": "not cited"})

R["epoxy_se"] = dict(slug="epoxy", label="Epoxies and epoxy resins",
    key="physical.surface_energy", value=0.0462, unit="J/m^2", method="contact angle, geometric mean",
    verify="γs = 46.2 mJ/m2",
    detail="Comyn, 2006 (ref 279) 행 — 'γs = 46.2 mJ/m2 (γsd = 41.2; γsp = 5.0)', Comments = 'Amine cured epoxide surface.'",
    cond={"method_detail": "contact angle; dispersive 41.2, polar 5.0 mJ/m^2",
          "surface_treatment": "amine-cured epoxide surface, as-cured", "temperature": "not cited"})

R["ptfe_se"] = dict(slug="ptfe", label="PTFE: Polytetrafluoroethylene, CAS # 9002-84-0",
    key="physical.surface_energy", value=0.0191, unit="J/m^2", method="contact angle, geometric mean",
    verify="γs = 19.1 mJ/m2",
    detail="Owens, 1969 (ref 155) 행 — 'γs = 19.1 mJ/m2 (γsd = 18.6, γsp = 0.5)', 테스트 액체 water 및 diiodomethane, geometric mean",
    cond={"method_detail": "contact angle with water and diiodomethane, geometric mean equation; dispersive 18.6, polar 0.5 mJ/m^2",
          "surface_treatment": "as-received PTFE, untreated", "temperature": "not cited"})

R["pe_se"] = dict(slug="polyethylene", label="PE: Polyethylene, CAS # 9002-88-4",
    key="physical.surface_energy", value=0.0332, unit="J/m^2", method="contact angle, geometric mean",
    verify="γs = 33.2 mJ/m2",
    detail="Owens, 1969 (ref 155) 행 — 'γs = 33.2 mJ/m2 (γsd = 33.2, γsp = 0.0)', 테스트 액체 water 및 diiodomethane",
    cond={"method_detail": "contact angle with water and diiodomethane; dispersive 33.2, polar 0.0 mJ/m^2",
          "surface_treatment": "untreated PE (no corona / no flame treatment)", "temperature": "not cited"})

R["pe_ca_ldpe"] = dict(slug="polyethylene", label="PE: Polyethylene, CAS # 9002-88-4",
    key="physical.contact_angle_water", value=97.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 97",
    detail="Westerdahl, 1974 (ref 63) 행 — 'θWY = 97o; no temp cited', Comments = 'Commercial low density PE film, thickness 30 mils.'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "commercial LDPE film, untreated (no corona)", "temperature": "not cited"})

R["pp_se"] = dict(slug="polypropylene", label="PP: Polypropylene, CAS #s 9003-08-0 (atactic) and 25085-53-4 (isotactic)",
    key="physical.surface_energy", value=0.0303, unit="J/m^2", method="contact angle, geometric mean",
    verify="γs = 30.3 mJ/m2",
    detail="Occhiello, 1991 (ref 202) 행 — 'γs = 30.3 mJ/m2 (γsd = 26.7, γsp = 3.6)', 테스트 액체 water 및 diiodomethane",
    cond={"method_detail": "contact angle with water and diiodomethane; dispersive 26.7, polar 3.6 mJ/m^2",
          "surface_treatment": "untreated PP (no corona / no flame treatment)", "temperature": "not cited"})

R["pvf_se"] = dict(slug="polyvinyl_fluoride_pvf", label="PVF: Poly(vinyl fluoride), CAS # 24981-14-4",
    key="physical.surface_energy", value=0.0367, unit="J/m^2", method="contact angle, van Oss acid-base (LW/AB)",
    verify="γs = 36.7 mJ/m2 (γsLW = 34.8",
    detail="Lloyd, 1995 (ref 218) 행 — 'γs = 36.7 mJ/m2 (γsLW = 34.8, γsAB = 1.9, γs+ = 0.2, γs- = 4.5)', Comments = 'Tedlar.'",
    cond={"method_detail": "acid-base analysis; LW 34.8, AB 1.9, gamma+ 0.2, gamma- 4.5 mJ/m^2",
          "surface_treatment": "DuPont Tedlar PVF film, as-received", "temperature": "not cited"})

R["pvf_ca"] = dict(slug="polyvinyl_fluoride_pvf", label="PVF: Poly(vinyl fluoride), CAS # 24981-14-4",
    key="physical.contact_angle_water", value=80.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 80",
    detail="Wu, 1971 (ref 29) 행 — 'θWY = 80o, 20oC'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "untreated PVF film", "temperature_c": 20})

R["pvc_ca"] = dict(slug="polyvinyl_chloride_pvc", label="PVC: Poly(vinyl chloride), CAS # 9002-86-2",
    key="physical.contact_angle_water", value=85.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 85",
    detail="Moshonov, 1980 (ref 118) 행 — 'θWY = 85o; no temp cited', Comments = '물방울 적용 60초 후 측정, 석유에테르 세정 후 메탄올 린스, PVC contained 20% dioctyl phthalate'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop, read 60 s after drop placement)",
          "surface_treatment": "plasticized PVC (20% dioctyl phthalate), cleaned with petroleum ether then rinsed with methanol",
          "temperature": "not cited"})

R["pu_se"] = dict(slug="polyurethane", label="PUR: Polyurethanes",
    key="physical.surface_energy", value=0.0355, unit="J/m^2", method="contact angle, three-liquid",
    verify="γs = 35.5 mJ/m2",
    detail="Fukuzawa, 1994 (ref 113) 행 — 'γs = 35.5 mJ/m2; no temp cited', 테스트 액체 water, formamide, diiodomethane",
    cond={"method_detail": "contact angle with water, formamide and diiodomethane; angles read 15 s after drop placement",
          "surface_treatment": "as-cast polyurethane, untreated", "temperature": "not cited"})

R["pu_ca"] = dict(slug="polyurethane", label="PUR: Polyurethanes",
    key="physical.contact_angle_water", value=82.4, unit="deg", method="sessile drop contact angle",
    verify="θWY = 82.4",
    detail="Fukuzawa, 1994 (ref 113) 행 — 'θWY = 82.4o; no temp cited', Comments = 'Contact angle measured after stabilizing for 15 secs.'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop, read after 15 s stabilization)",
          "surface_treatment": "as-cast polyurethane, untreated", "temperature": "not cited"})

R["peha_se"] = dict(slug="other_polymers", label="PEHA: Poly(2-ethylhexyl acrylate), CAS # 9003-77-4 ('Assorted Polymers' sheet)",
    key="physical.surface_energy", value=0.0302, unit="J/m^2", method="pendant drop of polymer melt, extrapolated to 20 C",
    verify="γs = 30.2 mJ/m2",
    detail="'PEHA: Poly(2-ethylhexyl acrylate)' 절, Wu, 1971 (ref 41) 행 — 'γs = 30.2 mJ/m2 (γsd = 29.4, γsp = 0.8); 20oC', Mn = 34,000",
    cond={"method_detail": "direct measurement of the polymer melt extrapolated to 20 C; dispersive 29.4, polar 0.8 mJ/m^2; Mn = 34,000",
          "temperature_c": 20})

R["pdms_se"] = dict(slug="polydimethylsiloxane", label="PDMS: Polydimethylsiloxane, CAS #9016-00-6",
    key="physical.surface_energy", value=0.0209, unit="J/m^2", method="contact angle, harmonic mean",
    verify="γs = 20.9 mJ/m2",
    detail="Sowell, 1972 (ref 48) 행 — 'γs = 20.9 mJ/m2; 20oC', 테스트 액체 water, glycerol, formamide, tricresyl phosphate",
    cond={"method_detail": "contact angle with water, glycerol, formamide, tricresyl phosphate", "temperature_c": 20,
          "surface_treatment": "untreated cured PDMS"})

R["pdms_ca"] = dict(slug="polydimethylsiloxane", label="PDMS: Polydimethylsiloxane, CAS #9016-00-6",
    key="physical.contact_angle_water", value=99.5, unit="deg", method="sessile drop contact angle",
    verify="θWY = 99.5",
    detail="Sowell, 1972 (ref 48) 행 — 'θWY = 99.5o; 20oC'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)", "temperature_c": 20,
          "surface_treatment": "untreated cured PDMS"})

R["pip_se"] = dict(slug="other_polymers", label="Poly(isoprene), CAS # 9003-31-0 ('Assorted Polymers' sheet)",
    key="physical.surface_energy", value=0.0320, unit="J/m^2", method="contact angle",
    verify="γs = 32 mJ/m2",
    detail="'Poly(isoprene), CAS # 9003-31-0' 절, Lee, 1967 (ref 221) 행 — 'γs = 32 mJ/m2; no temp cited', Comments = 'cis-isomer polyisoprene'",
    cond={"method_detail": "contact angle; cis-isomer polyisoprene; test liquids not stated by the source",
          "temperature": "not cited"})

R["al_ca"] = dict(slug="aluminum_foil", label="Aluminum foil, CAS #7429-90-5",
    key="physical.contact_angle_water", value=78.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 78",
    detail="Hansen, 1993 (ref 109) 행 — 'θWY = 78o; no temp cited', Comments = 'Sample aged for 14 days.'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "as-received aluminium foil aged 14 days in ambient air (대기 재오염 평형 상태). 같은 출처의 1일 숙성(aged 1 day) 값은 84.5도다.",
          "temperature": "not cited"})

R["al_se"] = dict(slug="aluminum_foil", label="Aluminum foil, CAS #7429-90-5",
    key="physical.surface_energy", value=0.0429, unit="J/m^2", method="contact angle, harmonic mean",
    verify="γs = 42.9 mJ/m2",
    detail="Hansen, 1993 (ref 109) 행 — 'γs = 42.9 mJ/m2 (γsd = 32.1, γsp = 10.8)', 테스트 액체 water 및 diiodomethane, harmonic mean, 'Sample aged for 14 days.'",
    cond={"method_detail": "contact angle with water and diiodomethane, harmonic mean equation; dispersive 32.1, polar 10.8 mJ/m^2",
          "surface_treatment": "as-received aluminium foil aged 14 days in ambient air; the 1-day-aged value in the same row block is 39.4 mJ/m^2",
          "temperature": "not cited"})

R["pei_ca"] = dict(slug="other_polymers", label="PEI: Polyetherimide, CAS # 61128-46-9 ('Assorted Polymers' sheet)",
    key="physical.contact_angle_water", value=85.0, unit="deg", method="sessile drop contact angle",
    verify="θWY = 85",
    detail="'PEI: Polyetherimide, CAS # 61128-46-9' 절, Kogoma, 1987 (ref 66) 행 — 'θWY = 85o; no temp cited'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "untreated PEI; the same section also prints 68 deg (Asfardjani, 1991, ref 76) — 산포가 크다",
          "temperature": "not cited"})

R["pet_fab_se"] = dict(slug="pet", label="PET: Poly(ethylene terephthalate), CAS # 25038-59-9",
    key="physical.surface_energy", value=0.0400, unit="J/m^2", method="contact angle",
    verify="γs = 40.0 mJ/m2",
    detail="Tagawa, 1990 (ref 229) 행 — 'γs = 40.0 mJ/m2 (γsd = 28.3; γsp = 11.7)', 테스트 액체 water 및 n-alkane, Comments = 'PET fabric.'",
    cond={"method_detail": "contact angle with water and n-alkane; dispersive 28.3, polar 11.7 mJ/m^2",
          "surface_treatment": "PET fabric (직물 형태), untreated", "temperature": "not cited"})

R["pet_fab_ca"] = dict(slug="pet", label="PET: Poly(ethylene terephthalate), CAS # 25038-59-9",
    key="physical.contact_angle_water", value=75.8, unit="deg", method="sessile drop contact angle",
    verify="θWY = 75.8",
    detail="Hsieh, 1998 (ref 228) 행 — 'θWY = 75.8o; no temp cited', Comments = 'Regular denier PET fabric.'",
    cond={"test_liquid": "water", "angle_type": "static (Young, sessile drop)",
          "surface_treatment": "regular-denier PET fabric, untreated", "temperature": "not cited"})

# ------------------------------------------------------------ target lists
GS = "grade_scope"

def emit(recipe_key, targets, scope_note, extra_notes=""):
    r = R[recipe_key]
    src = acc_src(r["slug"], r["label"])
    for mid in targets:
        cond = dict(r["cond"])
        cond[GS] = scope_note
        note = "AccuDyne Test '%s' 시트의 %s. " % (r["slug"], r["detail"])
        note += "Mst. Type 열이 'Calculated'가 아니고 실측 행임을 확인했다. "
        note += "AccuDyne 시트는 1차 출처를 인쇄하는 편찬 DB라 원논문까지 따라가지 못했다 -> tier 3. "
        if extra_notes:
            note += extra_notes
        add(mid, src, {"key": r["key"], "value": r["value"], "unit": r["unit"], "tier": 3,
                       "method": r["method"], "conditions": cond, "notes": note.strip()})


# --- A. 폴리이미드 필름 ---------------------------------------------------
PI_FULL = [209, 210, 211, 217]        # Kapton 150EN-C / 150EN-A / 140EN-Z / Taimide TL-025
emit("pi_ca", PI_FULL, "class value - AccuDyne 행은 PMDA-ODA Kapton 필름 값이다. 대상 등급은 같은 계열의 상용 PI 베이스 필름이지만 제조사 슬립제/표면 처리가 다를 수 있다",
     "이 값은 **무처리** 표면이다. 동일 시트의 대기압 DBD/플라즈마 처리품은 이보다 훨씬 낮으니 혼동하지 말 것.")
emit("pi_se", PI_FULL, "class value - AccuDyne 행은 Kapton 100H 측정값이다. 대상 등급은 같은 계열의 상용 PI 베이스 필름이다")

emit("pi_se", [212], "class value - Kapton 150MT+는 열전도 충전제가 들어간 등급이라 표면에 필러가 노출된다. 매트릭스인 PI 기준값이다",
     "충전 등급이라 접촉각은 넣지 않았다(표면 거칠기·필러 노출에 민감).")
emit("pi_se", [218], "class value - Taimide BK-025는 low-gloss(매트) 표면이라 질감이 있다. 매트릭스인 PI 기준값이다",
     "매트 표면은 Wenzel 거칠기 효과로 접촉각이 매끄러운 필름보다 크게 나오므로 접촉각은 넣지 않았다.")
emit("pi_se", [110], "class value - MPI(modified polyimide)는 고주파용으로 수지를 변성한 등급이라 순 PMDA-ODA와 표면 화학이 다를 수 있다")
emit("pi_upilex_ca", [449], "class value - UBE UMS-A2는 UBE의 modified polyimide 중공사 막이다. AccuDyne 행은 같은 UBE 계열인 Upilex-R(BPDA-ODA) 필름 측정값이다",
     "중공사 막은 다공질 스킨층을 가져 실제 겉보기 접촉각은 더 클 수 있다.")

# --- B. 에폭시 기재 라미네이트/수지 ---------------------------------------
EPOXY_LAM = [220, 221, 224, 226, 229, 234, 227, 95, 436, 97]
emit("epoxy_se", EPOXY_LAM,
     "class value - amine-cured epoxide surface. 대상은 유리포/충전제가 들어간 에폭시 라미네이트이고 경화제가 아민계가 아닐 수 있다. 라미네이트 표면은 수지가 지배하므로 에폭시 기준값을 썼다",
     "같은 행이 이미 DB의 FR4 Glass-Epoxy Laminate / High-Tg FR-4 Prepreg에 tier3으로 들어가 있어 세트 일관성이 유지된다.")
emit("epoxy_se", [438],
     "class value - E-44(WSR6101)는 DGEBA + Jeffamine(폴리에테르아민) 경화계로 AccuDyne의 'amine cured epoxide surface' 행과 화학종이 거의 같다(무충전)",
     "같은 시트의 Wu 1989 DGEBA+TETA 행은 39.1 mJ/m2로 경화제에 따라 39~47 대역에 산포한다.")
emit("epoxy_se", [371, 372],
     "class value - DELO KATIOBOND는 양이온 UV 경화 에폭시다. AccuDyne 행은 아민 경화 에폭시라 경화 메커니즘이 다르다")

# --- C. PTFE 기재 RF 라미네이트 -------------------------------------------
PTFE_LAM = [251, 252, 241, 248, 245, 246, 247, 272, 273, 271]
emit("ptfe_se", PTFE_LAM,
     "class value - 순 PTFE 측정값이다. 대상은 세라믹 충전/직조 유리 보강 PTFE 라미네이트라 표면에 충전제·유리가 일부 노출된다",
     "충전제 노출 때문에 접촉각은 넣지 않았다(순 PTFE 108도보다 낮게 나올 수 있다).")

# --- D. 폴리에틸렌 --------------------------------------------------------
emit("pe_se", [387, 388, 389],
     "class value - EPE는 발포 구조라 기재 고분자(LDPE) 표면에너지를 썼다",
     "발포체는 셀 벽/기공이 거칠기를 만들어 접촉각은 의미가 약해 표면에너지만 넣었다.")
emit("pe_se", [346], "class value - Avery OF 2429의 배면은 LDPE 필름이다. 접착면(열감응성 접착제)은 이 값이 아니다")
emit("pe_ca_ldpe", [346], "class value - Avery OF 2429의 배면은 LDPE 필름이다. 접착면은 이 값이 아니다")

# --- E. 폴리프로필렌 ------------------------------------------------------
emit("pp_se", [439], "class value - Reflexolar OSBS의 대기측(백색) 층이 PP다. 백색 안료(TiO2)가 들어가 순 PP와 다를 수 있다")

# --- F. PVF (Tedlar) 백시트 -----------------------------------------------
emit("pvf_se", [440], "class value - Madico TPE-HD의 대기측은 백색 PVF(Tedlar계)다. AccuDyne 행은 Tedlar 측정값이지만 백색 안료 유무가 다를 수 있다")
emit("pvf_ca", [440], "class value - Madico TPE-HD의 대기측은 백색 PVF다. AccuDyne 행은 순 PVF 필름 측정값이다")

# --- G. PVC 웨이퍼 테이프 기재 --------------------------------------------
emit("pvc_ca", [288, 278],
     "class value - 대상의 기재 필름이 연질 PVC다. AccuDyne 행도 가소제(DOP 20%)가 들어간 PVC라 계열이 맞는다",
     "이 값은 **접착면이 아닌 기재 필름 바깥면**의 값이다. 아크릴 접착면은 다른 값을 가진다.")

# --- H. 폴리우레탄 폼/고무 -------------------------------------------------
PU_FOAM = [54, 65, 66, 384, 385, 390, 391]
emit("pu_se", PU_FOAM,
     "class value - 기재 고분자(폴리우레탄) 표면에너지다. 대상은 발포체/미세발포체라 폴리올·이소시아네이트 조합이 다를 수 있다",
     "발포체라 접촉각은 넣지 않았다(셀 구조가 지배한다).")
emit("pu_se", [396], "class value - PUR 고무의 기재 고분자 표면에너지다")
emit("pu_ca", [396], "class value - PUR 고무의 기재 고분자 접촉각이다. 배합(가교·충전제)이 다르면 이 대역을 벗어난다")

# --- I. 아크릴 PSA 테이프 --------------------------------------------------
ACRYLIC = [51, 52, 322, 323, 324, 325, 326, 327, 328, 329,      # 3M VHB
           330, 331, 332, 333, 334,                             # tesa ACXplus
           340, 355, 356, 357, 358,                             # Lohmann pure/dispersion acrylic
           341, 342, 344, 354,                                  # Avery acrylic transfer/foam
           363, 360,                                            # tesa 4965, 3M 9415PC
           238, 282, 386]                                       # OCA acrylic
emit("peha_se", ACRYLIC,
     "class value - 아크릴 PSA의 주단량체인 poly(2-ethylhexyl acrylate) 용융체 측정값이다. 상용 PSA는 아크릴산·점착부여제·가교제가 들어가 수 mJ/m2 달라질 수 있다",
     "노출면이 아크릴 점착제인 제품만 골랐다(VHB·ACXplus·pure acrylic·acrylic transfer·OCA). 같은 행이 이미 DB의 3M OCA 8172/8211에 tier3으로 들어가 있다.")

# --- J. 실리콘 PSA / 실리콘 부품 -------------------------------------------
SIL_PSA = [375, 376, 377, 378, 362]
emit("pdms_se", SIL_PSA, "class value - 노출면이 실리콘 점착제다. 실리콘 PSA는 MQ 레진이 섞여 순 PDMS보다 약간 높을 수 있다")
emit("pdms_ca", SIL_PSA, "class value - 노출면이 실리콘 점착제다. 순 PDMS 기준값이다")
emit("pdms_se", [237, 256],
     "class value - 기재 고분자(PDMS) 표면에너지다. 대상은 발포/유리 보강 실리콘이라 표면에 충전제·유리가 노출된다",
     "발포·충전 등급이라 접촉각은 넣지 않았다.")

# --- K. 고무계 (NR / SIS) --------------------------------------------------
RUBBER = [399, 400, 394, 420, 55, 382, 366]
emit("pip_se", RUBBER,
     "class value - cis-폴리이소프렌(= 천연고무 기재, SIS의 중간 블록) 측정값이다. 카본블랙 충전·SBR 블렌드·점착부여제는 반영되지 않았다",
     "카본블랙이 들어간 고무는 블룸/충전 표면 노출로 값이 올라갈 수 있다.")

# --- L. 알루미늄 합금 ------------------------------------------------------
AL = [13, 14, 16, 22]
emit("al_ca", AL,
     "class value - AccuDyne 행은 상용 알루미늄 포일(거의 순수한 알루미늄)의 대기 노출 표면이다. 대상은 1050/1100(포일 계열)·3003·7050 합금으로 합금원소가 다르다",
     "금속의 진공 표면에너지(~1000 mJ/m2)가 아니라 **대기 산화/오염된 서비스 표면의 젖음 관련 표면장력**이다. DB의 Al2024-T3 82도·Al5052 82도·Al6061 68.6도와 같은 대역이다.")
emit("al_se", AL,
     "class value - 상용 알루미늄 포일의 대기 노출 표면이다. 대상은 합금원소가 다른 압연재다",
     "금속 진공 표면에너지와 혼동하지 말 것 — 이 값은 젖음 대역(수십 mJ/m2)의 고체 표면장력이다.")

# --- M. PEI 필름 -----------------------------------------------------------
emit("pei_ca", [84], "class value - AccuDyne 행은 등급 미명시 PEI다. Ultem 필름 자체 측정이 아니다",
     "같은 절에 68도(Asfardjani, 1991) 행도 있어 산포가 17도나 된다. 더 좋은 1차 값이 나오면 대체해라.")

# --- N. PET 펠트 -----------------------------------------------------------
emit("pet_fab_se", [267], "class value - AccuDyne 행은 PET 직물(fabric) 측정값이다. 대상은 PET 부직포(felt) 패널로 섬유 형태가 비슷하다")
emit("pet_fab_ca", [267], "class value - AccuDyne 행은 regular-denier PET 직물이다. 대상은 12.7 mm 부직포 패널로 공극률이 훨씬 높다",
     "다공성 섬유 집합체라 겉보기 접촉각은 Cassie-Baxter 상태로 훨씬 클 수 있다. 표면에너지 쪽을 우선 써라.")

# ============================================================ 비-AccuDyne
CU_ED_SRC = {"title": "Thin Copper Foils: From Electrodeposition Conditions to Adhesion Performances",
             "kind": "journal",
             "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13164644/fullTextXML",
             "doi": "10.3390/ma19091838"}
for mid in [258, 259, 260]:
    add(mid, CU_ED_SRC, {"key": "physical.contact_angle_water", "value": 84.0, "unit": "deg", "tier": 3,
        "method": "sessile drop, static water contact angle",
        "conditions": {"test_liquid": "distilled water", "angle_type": "static (sessile drop)",
            "surface_treatment": "as-deposited electrodeposited Cu film from sulfate bath solution IV (CuSO4 + Cl- + PEG6000 + MPSA), galvanostatic on a 316L stainless-steel cathode; Ra/RMS 85 nm; no anti-tarnish or silane treatment",
            "reported_uncertainty": "+-3.7 deg",
            GS: "class value - 논문은 실험실 전해동박이다. 대상은 CCL용 상용 ED 동박으로 방청(anti-tarnish)/실란 커플링 처리가 들어가 표면 화학이 다르다"},
        "notes": "3.5절 본문 인쇄값 — 'the corresponding water contact angle values of 66 +- 5.7 deg (solution I) and 84 +- 3.7 deg (solution IV)'. 그림(Figure 17)이 아니라 본문에 숫자가 있다. DB의 압연동박 79도·HVLP 82.3도와 같은 대역이라 자릿수 검산을 통과한다. 주의 — 동박 논문의 '표면에너지 1,050 mJ/m2' 같은 진공값과는 다른 양이다."})

CU_RA_SRC = {"title": "O2/Ar 플라즈마를 이용한 구리호일 표면 개질에 관한 연구 (A Study on the Surface Modification Mechanism of Copper Foil Using O2/Ar Plasma)",
             "kind": "journal",
             "url": "https://koreascience.kr/article/JAKO201334064307342.pdf",
             "doi": "10.4313/JKEM.2013.26.11.836", "year": 2013}
add(261, CU_RA_SRC, {"key": "physical.contact_angle_water", "value": 79.0, "unit": "deg", "tier": 3,
    "method": "sessile drop, static water contact angle (D.I. water, 10 uL)",
    "conditions": {"test_liquid": "deionized water", "angle_type": "static (sessile drop, 10 uL)",
        "surface_treatment": "Ref 시편 = 18 um 압연동박(rolled copper foil), 플라즈마 처리 전 무처리 기준면. RMS 거칠기 1.54 nm",
        GS: "class value - JX HA 압연연화동박은 방청(anti-tarnish)/조도 처리가 들어간 제품이다. 논문 시편은 무처리 압연동박이다"},
    "notes": "본문 인쇄값 — '플라즈마 처리 전의 접촉각은 79도이고, 플라즈마 처리 후의 접촉각은 25도로 매우 낮아진 것을 확인할 수 있다'. **플라즈마 처리 후 25도는 서비스 상태가 아니라 배제했다.** 같은 논문의 무처리 polar 4.72 / dispersion 38.67 mN/m는 합을 내가 계산해야 하고 총값은 그림에만 있어 surface_energy는 넣지 않았다."})

# ------------------------------------------------------------------ assemble
for mid, src, prop in rows:
    if mid not in names:
        print("!! unknown target id", mid, file=sys.stderr)
        continue
    key = (mid, json.dumps(src, sort_keys=True))
    m = mats.get(key)
    if m is None:
        m = {"match_name": names[mid], "source": src, "properties": []}
        mats[key] = m
    m["properties"].append(prop)

out = {"materials": list(mats.values())}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

ids = sorted({mid for mid, _, _ in rows})
print("materials(entries):", len(out["materials"]), " distinct target ids:", len(ids), " property rows:", len(rows))
from collections import Counter
print(Counter(p["key"] for _, _, p in rows))
