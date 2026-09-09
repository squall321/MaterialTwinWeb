# Chiu 2015 EMC(체적 17항·전단 21항 Prony + WLF 2분기)를 원문 표 그대로 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "journal",
       "title": "Development of a Consistent Multiaxial Viscoelastic Model for Package Warpage Simulation",
       "authors": "Tz-Cheng Chiu, Dong-Yi Huang, Bo-Sheng Lee, Dao-Long Chen, Ping-Feng Yang, Chin-Li Kao",
       "year": 2015,
       "publisher": "IEEE (65th ECTC)",
       "doi": None, "url": None,
       "local_path": "/data/paper_patent_corpus/cae_papers/06_warpage_thermomech/"
                     "Chiu - 2015 - Development of a consistent multiaxial viscoelastic model for package warpage simulation.pdf"}

NEWMAT = {"name": "Epoxy molding compound, commercial low-filler 70 wt% fused silica, Tg 120 C "
                  "(ASE/NCKU multiaxial viscoelastic characterisation, Chiu 2015)",
          "category": "composite",
          "attributes": {"role": "product",
                         "role_reason": "원문이 'The EMC considered in this study is a commercial compound with "
                                        "70 wt% silica filler' 라 상용품을 측정했다고 밝힌다. 다만 등급명은 안 밝힌다",
                         "role_confidence": "medium",
                         "material_class": "epoxy molding compound (EMC), fused-silica filled",
                         "subsystem": "packaging",
                         "subsystem_basis": "패키지 워피지 해석용 봉지재다.",
                         "filler_content_wt_pct": 70,
                         "process": "as-cured EMC specimen; tensile DMA (TA Q800) + torsional DMA "
                                    "(Anton Paar MCR-302) + TMA (TA Q400)"}}

# ── Table 1 — 체적(bulk) Prony, M = 17. 원문 PDF 대조 완료 ───────────────────
BULK_W   = [0.01465, 0.01299, 0.02094, 0.14107, 0.25298, 0.19838, 0.09532, 0.02866, 0.02617,
            0.01994, 0.01821, 0.02287, 0.02303, 0.01877, 0.02122, 0.03037, 0.01677]
BULK_TAU = [1.00e11, 1.00e9, 1.00e7, 1.00e5, 1.00e3, 1.00e1, 1.00e-1, 1.00e-3, 1.00e-5,
            1.00e-7, 1.00e-9, 1.00e-11, 1.00e-13, 1.00e-15, 1.00e-17, 1.00e-19, 1.00e-21]
# ── Table 2 — 전단(shear) Prony, N = 21 ────────────────────────────────────
SHEAR_W   = [0.01195, 0.00933, 0.01734, 0.00537, 0.00287, 0.03466, 0.19450, 0.27206, 0.11137,
             0.05611, 0.03779, 0.02332, 0.02072, 0.01981, 0.01986, 0.02892, 0.02698, 0.01614,
             0.02442, 0.01664, 0.03148]
SHEAR_TAU = [1.00e17, 1.00e15, 1.00e13, 1.00e11, 1.00e9, 1.00e7, 1.00e5, 1.00e3, 1.00e1,
             1.00e-1, 1.00e-3, 1.00e-5, 1.00e-7, 1.00e-9, 1.00e-11, 1.00e-13, 1.00e-15,
             1.00e-17, 1.00e-19, 1.00e-21, 1.00e-23]
assert len(BULK_W) == len(BULK_TAU) == 17
assert len(SHEAR_W) == len(SHEAR_TAU) == 21
SB, SS = sum(BULK_W), sum(SHEAR_W)
assert SB < 1 and SS < 1, (SB, SS)

COMMON = ("Chiu 2015 는 인장 DMA(Young 저장탄성률)와 비틀림 DMA(전단 저장탄성률)를 각각 재고, "
          "Laplace-Carson 영역에서 탄성-점탄성 대응원리로 체적·전단 완화계수를 따로 만들었다 "
          "— **체적 항수(17)와 전단 항수(21)가 다른 것은 오기가 아니라 이 절차의 결과다.** "
          "재료는 논문이 등급명을 밝히지 않은 상용 EMC(퓨즈드 실리카 70 wt%), DMA·TMA 로 잰 Tg = 120 °C. "
          "Prony 적합값이므로 method=computed, 표에 인쇄된 값이므로 tier1.")

props = []
def add(key, value, unit, cond, notes, method="computed"):
    props.append({"key": key, "value": value, "unit": unit, "method": method,
                  "tier": 1, "conditions": cond, "notes": notes})

SET_K = "chiu2015_bulk_17term"
SET_G = "chiu2015_shear_21term"
NOTE_K = (f"Table 1 `Prony series constants for the bulk modulus (2), M = 17`, T_ref = 120 °C. "
          f"17개 w 합 = {SB:.5f} <= 1 (검산) — 남는 {1-SB:.5f} 가 평형 체적항이다. "
          f"표 우하단에 유리상 체적탄성률 `κg = 14 GPa` 가 함께 인쇄돼 있다(따로 등록). " + COMMON)
NOTE_G = (f"Table 2 `Prony series constants for the shear modulus (3), N = 21`, T_ref = 120 °C. "
          f"21개 w 합 = {SS:.5f} <= 1 (검산) — 남는 {1-SS:.5f} 가 평형 전단항이다. "
          f"표 우하단에 유리상 전단탄성률 `μg = 4.8 GPa` 가 함께 인쇄돼 있다(따로 등록). " + COMMON)

for i, (w, t) in enumerate(zip(BULK_W, BULK_TAU), start=1):
    base = {"term_index": i, "prony_terms_total": 17, "set_id": SET_K,
            "model": "generalized_maxwell", "series": "volumetric",
            "relaxation_mode": "volumetric (bulk)",
            "reference_temperature_c": 120.0, "reference_temperature_k": 393.15,
            "source_data": "tensile DMA (TA Q800) + torsional DMA (Anton Paar MCR-302) storage-modulus "
                           "mastercurves, converted in the Laplace-Carson domain"}
    add("mechanical.prony_relative_bulk_modulus", w, "1", dict(base, term=f"w_kappa{i}"), NOTE_K)
    add("mechanical.prony_relaxation_time", t, "s", dict(base, term=f"tau_kappa{i}"),
        f"Table 1 체적 완화시간 tau^kappa_{i} (열 머리글 'τiκ (s)'). " + NOTE_K)

for i, (w, t) in enumerate(zip(SHEAR_W, SHEAR_TAU), start=1):
    base = {"term_index": i, "prony_terms_total": 21, "set_id": SET_G,
            "model": "generalized_maxwell", "series": "shear", "relaxation_mode": "shear",
            "reference_temperature_c": 120.0, "reference_temperature_k": 393.15,
            "source_data": "tensile DMA (TA Q800) + torsional DMA (Anton Paar MCR-302) storage-modulus "
                           "mastercurves, converted in the Laplace-Carson domain"}
    add("mechanical.prony_relative_modulus", w, "1", dict(base, term=f"w_mu{i}"), NOTE_G)
    add("mechanical.prony_relaxation_time", t, "s", dict(base, term=f"tau_mu{i}"),
        f"Table 2 전단 완화시간 tau^mu_{i} (열 머리글 'τiμ (s)'). " + NOTE_G)

# 유리상 계수 — Prony 급수의 곱셈 상수다(급수 밖 값이라 항번호가 없다).
add("mechanical.bulk_modulus", 14.0e9, "Pa",
    {"set_id": SET_K, "quantity": "glassy (instantaneous) bulk modulus kappa_g",
     "basis": "Prony 급수의 곱셈 상수 — kappa(t) = kappa_g * (w_inf + sum w_i exp(-t/tau_i))",
     "reference_temperature_c": 120.0, "reference_temperature_k": 393.15},
    "Table 1 우하단 인쇄값 `κg = 14 GPa`. " + NOTE_K)
add("mechanical.shear_modulus", 4.8e9, "Pa",
    {"set_id": SET_G, "quantity": "glassy (instantaneous) shear modulus mu_g",
     "basis": "Prony 급수의 곱셈 상수 — mu(t) = mu_g * (w_inf + sum w_i exp(-t/tau_i))",
     "reference_temperature_c": 120.0, "reference_temperature_k": 393.15},
    "Table 2 우하단 인쇄값 `μg = 4.8 GPa`. " + NOTE_G)

# ── Table 3 — WLF 시프트 함수. **두 분기다** ────────────────────────────────
WLF_NOTE = ("Table 3 `Model parameters for the WLF shift function (15)`. **한 재료에 WLF 가 두 벌이다** — "
            "T_ref = 120 °C 를 공유하되 120 °C **위**는 (C1, C2) = (41.6, 148.6), **아래**는 (210, 1625) 다. "
            "하나로 합치면 안 된다. 원문 식은 log(aT) = -C1(T-T0)/(C2+(T-T0)) 형태의 표준 WLF 다. "
            "Tg = 120 °C 라 분기점이 곧 유리전이다. " + COMMON)
for branch, c1, c2 in (("above_tg", 41.6, 148.6), ("below_tg", 210.0, 1625.0)):
    cond = {"set_id": f"chiu2015_wlf_{branch}", "reference_temperature_c": 120.0,
            "reference_temperature_k": 393.15, "log_base": "log10",
            "branch": ("T > 120 C (rubbery side)" if branch == "above_tg" else "T < 120 C (glassy side)"),
            "equation_verbatim": "log(aT) = -C1 (T - T0) / (C2 + (T - T0))",
            "applies_to_sets": [SET_K, SET_G]}
    add("mechanical.wlf_c1", c1, "1", dict(cond), WLF_NOTE)
    add("mechanical.wlf_c2", c2, "K", dict(cond), WLF_NOTE)

doc = {"batch": "70차 FD",
       "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("fd02_chiu2015_emc_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {len(props)}행  (bulk Σw={SB:.5f}, shear Σw={SS:.5f})")
