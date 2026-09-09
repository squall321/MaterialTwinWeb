# Moisture Sensitivity 책 8장(Jang & Han)의 NCP 인장 Prony 13항·WLF·E0 를 표 그대로 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "book",
       "title": "Modeling of Moisture Diffusion and Moisture-Induced Stresses in Semiconductor and MEMS "
                "Packages (Chapter 8 of `Moisture Sensitivity of Plastic Packages of IC Devices`)",
       "authors": "C. Jang, B. Han",
       "year": 2010,
       "doi": "10.1007/978-1-4419-5719-1_8",
       "url": "https://doi.org/10.1007/978-1-4419-5719-1_8",
       "publisher": "Springer US, in: X.J. Fan, E. Suhir (eds.), Moisture Sensitivity of Plastic Packages "
                    "of IC Devices, pp. 197-224",
       "local_path": "/data/paper_patent_corpus/snowball_papers/from_rel/"
                     "2010 - Moisture Sensitivity of Plastic Packages of IC Devices.pdf"}

NEWMAT = {"name": "Non-conductive paste (NCP) flip-chip adhesive, cast and cured on EMC, Tg 125 C, "
                  "E0 3.25 GPa (Moisture Sensitivity of Plastic Packages Ch.8, Jang & Han 2010)",
          "category": "polymer",
          "attributes": {"role": "evidence",
                         "role_reason": "원문이 'NCP (non-conductive paste)' 라고만 하고 제조사·등급을 밝히지 않는다. "
                                        "특정되는 것은 Tg 125 °C 와 시편 제작법(액상 NCP 를 EMC 블록 위에 붓고 경화)뿐이다",
                         "role_confidence": "medium",
                         "material_class": "non-conductive paste (NCP), flip-chip underfill adhesive",
                         "subsystem": "packaging",
                         "subsystem_basis": "플립칩 접합용 비전도성 페이스트다.",
                         "glass_transition_c": 125,
                         "process": "liquid NCP poured onto an EMC block and cured; bi-material strip "
                                    "13.83 x 4.10 mm, NCP layer 1.79 mm on EMC 1.61 mm"}}

# ── Table 8.7 `Constants for viscoelastic model of NCP` (PDF 215쪽) ──
# **PDF 215쪽을 350 dpi 로 그려 13항 전부를 눈으로 대조했다** (ga71_t87_crop.png).
# docling 추출과 렌더가 완전히 일치한다 — 이 표에는 잃어버린 부호도 곱셈기호도 없다.
E_INF = 0.0091
E_I = [0.0507, 0.0259, 0.0700, 0.0682, 0.0022, 0.0558, 0.0680,
       0.0724, 0.0892, 0.1109, 0.1082, 0.0709, 0.1985]
LAM = [255.0, 5340.0, 1.36e5, 9.80e5, 5.20e6, 5.0e7, 5.0e7,
       5.0e8, 5.0e9, 5.0e10, 5.0e11, 5.0e12, 5.0e13]
TREF_K, C1, C2 = 298.0, 41.28, 321.2
E0_PA = 3.25e9   # Table 8.6 — `Young's modulus (GPa) : 3.25 (E0)`

assert len(E_I) == len(LAM) == 13
SUM_E = sum(E_I)
assert abs(SUM_E + E_INF - 1.0) < 1e-12, SUM_E     # 검산 — 정확히 1 로 닫힌다

SET = "moisturebook2010_ch8_ncp_tensile_13term"
CHECK = (f"**검산 — 가중치 합이 정확히 1 로 닫힌다.** sum e_i = {SUM_E:.4f}, "
         f"+ e_inf {E_INF} = {SUM_E + E_INF:.6f} (오차 0). 정규화 급수이므로 이것이 곧 E(0) 재현이다 — "
         f"E(0) = E0 * (e_inf + sum e_i) = E0 = 3.25 GPa (Table 8.6 에 인쇄된 값과 동일). "
         f"평형계수는 E_inf = e_inf * E0 = {E_INF} * 3250 = {E_INF*3250:.2f} MPa 이지만 "
         f"**우리가 곱해서 만든 값이라 넣지 않았다** — 무차원 e_inf 만 실었다.")

CAVEAT = ("**원문이 tau_6 과 tau_7 을 둘 다 5e7 s 로 인쇄한다.** 5.20e6 -> 5e7 -> 5e7 -> 5e8 로 "
          "10년 간격이 한 칸 끊기므로 둘 중 하나(아마 tau_6 = 5e6)가 오식으로 보이지만, "
          "**우리가 고칠 수 없어 인쇄된 대로 실었다.** 350 dpi 렌더로 확인한 인쇄값이다 "
          "(ga71_t87_crop.png). 급수를 쓸 때는 이 두 항이 사실상 한 항으로 합쳐진다는 것을 알고 써라.")

COMMON = ("재료는 논문이 등급명을 밝히지 않은 플립칩용 비전도성 페이스트(NCP)다(Tg 125 °C). "
          "액상 NCP 를 EMC 블록 위에 붓고 경화한 이중재 스트립 시편(NCP 1.79 mm / EMC 1.61 mm)을 "
          "DMA·TMA 로 재고 **인장 모드 응력완화 시험**으로 Prony 급수를 얻었다 — 원문 verbatim: "
          "*\"Since a stress relaxation test was carried out in a tensile mode, a Prony series was obtained "
          "in terms of tensile moduli\"*. 급수 형태는 E(t) = E0 * [e_inf + sum_i e_i exp(-t/tau)] 이고 "
          "tau 는 **환산시간(reduced time)** 이며 이동함수는 WLF 다. 적합 결과라 method=computed, "
          "표 인쇄값이므로 tier1. " + CHECK + " " + CAVEAT)

props = []


def add(key, value, unit, method, cond, notes):
    props.append({"key": key, "value": value, "unit": unit, "method": method,
                  "tier": 1, "conditions": cond, "notes": notes})


def base(i):
    return {"prony_term": i, "prony_terms_total": 13, "term_index": i, "set_id": SET,
            "model": "generalized_maxwell", "series": "tensile",
            "relaxation_mode": "tensile (uniaxial stress relaxation)",
            "reference_temperature_k": TREF_K,
            "reference_temperature_c": round(TREF_K - 273.15, 2),
            "shift_function": "WLF",
            "normalisation": "e_i = E_i / E0, E0 = 3.25 GPa (Table 8.6)",
            "time_axis": "reduced time (WLF-shifted)",
            "source_data": "tensile stress relaxation + DMA, bi-material NCP/EMC strip"}


NOTE_TREF = ("**기준온도는 인쇄돼 있다** — Table 8.7 이 T_ref = 298 K 로 적는다(= 24.85 °C; 저자가 25 °C 를 "
             "뜻한 것으로 보이나 인쇄값은 298 K 이므로 그대로 실었다). ")

for i, (e, lam) in enumerate(zip(E_I, LAM), start=1):
    n = (f"Table 8.7 `Constants for viscoelastic model of NCP`, 13항 중 {i}번. " + NOTE_TREF + COMMON)
    add("mechanical.prony_relative_modulus", e, "1", "computed",
        dict(base(i), term=f"e{i}"),
        f"정규화 인장완화 가중치 e_{i} = {e} (열 머리글 `e i`). " + n)
    add("mechanical.prony_relaxation_time", lam, "s", "computed",
        dict(base(i), term=f"lambda{i}"),
        f"완화시간 lambda_{i} = {lam:g} s (열 머리글 `λ i (s)`). " + n)

add("mechanical.prony_relative_modulus", E_INF, "1", "computed",
    {"term": "e_inf", "prony_term": "inf", "set_id": SET, "model": "generalized_maxwell",
     "series": "tensile", "relaxation_mode": "tensile (uniaxial stress relaxation)",
     "reference_temperature_k": TREF_K, "reference_temperature_c": round(TREF_K - 273.15, 2),
     "normalisation": "e_inf = E_inf / E0, E0 = 3.25 GPa (Table 8.6)",
     "basis": "급수 밖 평형항이라 항번호가 없는 것이 맞다 — 원문 열 머리글이 `∞` 다"},
    "Table 8.7 의 `∞` 열 — **정규화 평형(장기) 인장계수** e_inf = 0.0091. "
    "급수 밖 항이라 완화시간이 없는 것이 옳다. " + NOTE_TREF + COMMON)

for nm, val, note in [
        ("mechanical.wlf_c1", C1,
         "Table 8.7 `Shift const. C1 = 41.28` (무차원). 원문 식 verbatim: "
         "log a_T = -C1 (T - T_ref) / (C2 + T - T_ref), T_ref = 298 K."),
        ("mechanical.wlf_c2", C2,
         "Table 8.7 `Shift const. C2 (K) = 321.2`. 원문이 단위를 K 로 명시한다.")]:
    add(nm, val, "1" if nm.endswith("c1") else "K", "computed",
        {"set_id": SET, "model": "WLF", "reference_temperature_k": TREF_K,
         "reference_temperature_c": round(TREF_K - 273.15, 2),
         "applies_to": "moisturebook2010_ch8_ncp_tensile_13term",
         "checksum_vs_printed_shift_factors": "NOT_POSSIBLE — 원문이 a_T 표를 인쇄하지 않아 대조할 값이 없다"},
        note + " **이 상수를 검산할 인쇄된 이동인자표가 원문에 없다** — 값만 그대로 옮겼다. " + COMMON)

add("mechanical.youngs_modulus", E0_PA, "Pa", "measured",
    {"temperature_c": 85.0, "term": "E0",
     "term_meaning": "instantaneous (glassy) tensile modulus that the Prony series 는 정규화 기준으로 쓴다",
     "set_id": SET, "method_detail": "DMA",
     "table_header_caveat": "Table 8.6 의 표제가 `(at 85 °C)` 인데 본문은 이 값을 Prony 급수의 E0 "
                            "(순간계수)로 쓴다 — 표제 온도를 그대로 실었다"},
    "Table 8.6 `Thermo-mechanical and hygroscopic properties of NCP and EMC (at 85 °C)` 의 "
    "`Young's modulus (GPa) : 3.25 (E0)`. **PDF 214쪽 350 dpi 렌더로 확인했다**(ga71_t86_crop.png). "
    "이 값이 없으면 Table 8.7 의 무차원 e_i 는 차원이 없어 쓸 수 없다 — 짝으로 실었다. " + COMMON)

add("mechanical.poisson_ratio", 0.35, "1", "measured",
    {"temperature_c": 85.0, "method_detail": "DMA/TMA"},
    "Table 8.6 의 NCP 열 `Poisson's ratio : 0.35`. PDF 214쪽 렌더 확인. "
    "인장 Prony 급수를 3차원 해석에 쓰려면 포아송비가 필요해 같이 실었다. " + COMMON)

add("thermal.expansion_linear", 65e-6, "1/K", "measured",
    {"temperature_c": 85.0, "method_detail": "TMA",
     "branch": "Tg(125 C) 아래 — 원문이 alpha1/alpha2 를 구분하지 않고 단일값으로 인쇄한다"},
    "Table 8.6 의 NCP 열 `CTE (ppm/°C) : 65` -> 65e-6 1/K. PDF 214쪽 렌더 확인. "
    "NCP 의 Tg 가 125 °C 이고 측정·적용 온도가 85 °C 라 유리상(alpha1) 구간 값이다. " + COMMON)

add("thermal.glass_transition", 125.0 + 273.15, "K", "measured",
    {"method_detail": "DMA", "printed_value_c": 125},
    "8.5.1 절 본문 verbatim: *\"The viscoelasticity was considered only for the NCP that had a "
    "lower glass transition temperature (125 °C)\"* -> 125 °C = 398.15 K. " + COMMON)

doc = {"batch": "71차 GA", "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("ga71_01_moisturebook2010_ncp_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{out.name}: {len(props)} 행,  sum e_i = {SUM_E:.4f} + e_inf {E_INF} = {SUM_E + E_INF:.6f}")
