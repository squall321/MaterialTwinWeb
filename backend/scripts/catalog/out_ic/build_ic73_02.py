# Gower & Shanks 2004(사슬이동제) Table 2 → a_T(15 C) · WLF C1/C2 · Mz JSON 생성기
import json, math

SRC = {
    "kind": "journal",
    "title": ("Gower & Shanks (2004), The Effect of Chain Transfer Agent Level on Adhesive "
              "Performance and Peel Master-Curves for Acrylic Pressure Sensitive Adhesives, "
              "Macromol. Chem. Phys. 205, 2139-2150"),
    "doi": "10.1002/macp.200400177",
    "url": "https://doi.org/10.1002/macp.200400177",
    "year": 2004,
    "authors": "M. D. Gower, R. A. Shanks",
    "publisher": "Wiley-VCH",
    "local_path": ("/data/paper_patent_corpus/mech_papers/26_psa_chem/"
                   "Gower - 2004 - The Effect of Chain Transfer Agent Level on Adhesive Performance "
                   "and Peel Master‐Curves for Acrylic Pressure Sensitive Adhesives.pdf"),
}

# DB 재료명(Gower 2006 이 세운 것) ↔ 2004 논문의 폴리머 코드. 조성이 자릿수까지 같다.
MATS = [
 ("Acrylic PSA emulsion copolymer AA4M91-3 (BA/EHA/MMA/AA 91.00/0.00/5.00/4.00 wt%, Gower 2006)",
  "AA4M91-3", 0.60, 5.95, 109.3, 0.999, 644000),
 ("Acrylic PSA emulsion copolymer AA4M61-3 (BA/EHA/MMA/AA 61.34/25.00/9.66/4.00 wt%, Gower 2006)",
  "AA4M61-3", 0.60, 5.95, 109.3, 0.999, 1973000),
 ("Acrylic PSA emulsion copolymer AA4M50-3 (BA/EHA/MMA/AA 50.00/34.56/11.44/4.00 wt%, Gower 2006)",
  "AA4M50-3", 0.65, 5.51, 93.3, 0.990, 2024000),
 ("Acrylic PSA emulsion copolymer AA4M25-3 (BA/EHA/MMA/AA 25.00/55.61/15.39/4.00 wt%, Gower 2006)",
  "AA4M25-3", 0.80, 5.49, 79.8, 0.996, 4305000),
 ("Acrylic PSA emulsion copolymer AA4M02-3 (BA/EHA/MMA/AA 1.98/75.00/19.02/4.00 wt%, Gower 2006)",
  "AA4M02-3", 1.0, 5.09, 61.3, 0.997, 2270000),
]

T0_C, T0_K = 25.0, 298.15
EQ_PRINTED = "log(a_T) = -C_1(T - T_0)/(C_2 + T + T_0)      (5)"
EQ_USED = "log10(a_T) = -C1*(T-T0)/(C2+(T-T0))"

# 원문 Table 2 의 인쇄된 log a_T (35/50/65 C 는 이미 DB 에 Gower 2006 출처로 들어가 있다)
PRINTED_AT = {
 "AA4M91-3": {15: 0.60, 35: -0.50, 50: -1.10, 65: -1.60},
 "AA4M61-3": {15: 0.60, 35: -0.50, 50: -1.10, 65: -1.60},
 "AA4M50-3": {15: 0.65, 35: -0.55, 50: -1.15, 65: -1.65},
 "AA4M25-3": {15: 0.80, 35: -0.60, 50: -1.30, 65: -1.85},
 "AA4M02-3": {15: 1.0,  35: -0.70, 50: -1.50, 65: -2.00},
}

SIGN_NOTE = (
  "**부호 함정 실측** — 이 표를 docling·pdftotext 로 읽으면 35/50/65 C 의 15칸에서 마이너스 부호가 "
  "통째로 사라진다(`-0.50` → `0.50`). 15 C 의 5칸은 원래 양수라 그대로 나오고, 25 C 의 5칸은 0 이다. "
  "즉 25칸 중 **15칸이 뒤집히고 10칸은 멀쩡해서** 표 모양만 보면 정상으로 보인다. "
  "600 dpi 렌더로 25칸을 전수 확인했다. 72차 HA 가 Gower 2006 Table 4 에서 잡은 것과 같은 함정이다."
)
WLF_CHECK = (
  "**이 표는 자기 안에서 검산된다 — 그리고 그 검산이 원문 식 (5) 의 오식을 잡아낸다.** "
  f"원문 식 verbatim(600 dpi 렌더) — `{EQ_PRINTED}`. 인쇄된 분모 `C2 + T + T0` 로는 이 논문 자신의 "
  "Table 2 를 재현하지 못한다(최대 어긋남 **0.654 decade**). 표준형 `C2 + (T - T0)` 로 계산하면 "
  "20칸(폴리머 5종 x 15/35/50/65 C) 전부가 **최대 0.026 decade** 안에서 맞는다. "
  "예 — AA4M91-3, C1 = 5.95 · C2 = 109.3 · T0 = 25 C: "
  "T=15 -> +0.599(인쇄 +0.60) · T=35 -> -0.499(-0.50) · T=50 -> -1.108(-1.10) · T=65 -> -1.594(-1.60). "
  "**따라서 인쇄된 `+T_0` 는 오식이고, 우리가 값을 고친 것이 아니라 이 상수들이 속한 함수형을 확정한 것이다.** "
  "인쇄된 식은 `equation_verbatim` 에 글자 그대로 남겼다."
)
CROSS = (
  "**교차확인 — 이 논문의 35/50/65 C 15칸은 Gower 2006 Table 4 가 같은 폴리머에 대해 인쇄한 값과 "
  "한 자리도 틀리지 않고 같다**(DB 재료 1664~1668, 출처 4236, 72차 HA 가 넣은 것). "
  "그래서 그 15칸은 **다시 넣지 않았다**(중복). 대신 이 대조가 HA 의 부호 정정이 옳았음을 "
  "독립 출처로 증명한다."
)

props_by_mat = {}
for name, code, log15, C1, C2, r, Mz in MATS:
    a15 = 10.0 ** log15
    common_cond = {
        "reference_temperature_c": T0_C,
        "reference_temperature_printed": True,
        "curve_type": "master_curve",
        "polymer_code": code,
        "failure_mode": "cohesive",
        "master_curve": ("log(reduced peel stress) vs log(reduced peeling rate), 180 deg peel, "
                         "cohesive-failure region, T_ref = 25 C (298 K); reduced peel force "
                         "P_r = 298*P/T"),
        "log_base": "log10",
    }
    props = [{
        "key": "mechanical.tts_shift_factor", "value": a15, "unit": "1",
        "method": "computed", "tier": 1,
        "conditions": {**common_cond, "temperature_c": 15.0,
            "printed_as": "log10_a_T", "value_printed": log15,
            "sign_convention": ("a_T > 1 below T_ref (T = 15 C < 25 C) — 저온에서 완화가 느려진다. "
                                "35/50/65 C 에서는 a_T < 1 이다. 72차 HA 가 Gower 2006 에 쓴 것과 "
                                "같은 시간영역 규약이라 한 키에 섞여도 안전하다"),
            "shift_function": ("empirical (isothermal peel-rate curves superposed); WLF C1/C2 로 "
                               "적합됨 — 같은 표의 wlf_c1/wlf_c2 행 참조"),
            "relaxation_mode": ("not applicable — 완화탄성률 곡선이 아니라 180 deg 박리력 "
                                "마스터커브의 이동인자다"),
            "set_id": f"gower2004cta_table2_peel_mastercurve_{code}",
        },
        "notes": (
            f"이동인자 a_T = {a15:.6g} (무차원), T = 15 C, 기준온도 T0 = 25 C. "
            f"원문 표 verbatim — `Table 2. AA4M-3 copolymer molecular weights and polydispersity indices, "
            f"the effect of test temperature on the logarithm of the temperature shift factors for the "
            f"cohesive failure region of the peel master-curves, and results from WLF analysis of the data "
            f"from the peel master-curves.` 의 `{code}` 열, `log a_T at 15 C` 행. "
            f"**원문 인쇄값은 log10(a_T) = {log15} 다.** 환산 산술 — a_T = 10^({log15}) = {a15:.6g}, "
            f"왕복 검산 log10({a15:.6g}) = {math.log10(a15):.4f} 로 인쇄값과 일치한다. "
            f"기준온도 근거(본문 verbatim, 600 dpi 렌더) — `The master-curves of log(reduced peel stress) "
            f"against log(reduced peeling rate) were constructed via the Boltzmann superposition principle "
            f"by applying shift factors aT to peel adhesion versus peeling rate curves at a range of test "
            f"temperatures and superpositioning the curves at a reference temperature of 25 C.` "
            f"그림 캡션도 `(reference temperature: T0 = 298 K)` 를 여러 번 인쇄한다. "
            f"**15 C 는 Gower 2006 Table 4 에 없는 새 온도다** — 그래서 이 칸이 새 값이다. " + CROSS + " "
            + SIGN_NOTE + " " + WLF_CHECK
        )}, {
        "key": "mechanical.wlf_c1", "value": C1, "unit": "1",
        "method": "computed", "tier": 1,
        "conditions": {
            "reference_temperature_k": T0_K, "reference_temperature_c": T0_C,
            "equation_verbatim": EQ_PRINTED,
            "equation_reconstructed": EQ_USED,
            "equation_note": ("인쇄된 분모 `C2 + T + T0` 는 이 논문 자신의 Table 2 를 재현하지 못한다"
                              "(최대 0.654 decade). 표준형 `C2 + (T - T0)` 는 20칸 전부를 "
                              "최대 0.026 decade 안에서 재현한다 — 인쇄된 `+T0` 는 오식이다"),
            "log_base": "log10",
            "sign_convention": "log a_T = -C1*dT/(C2+dT)",
            "valid_temperature_range_c": [15, 65],
            "fit_correlation_coefficient_printed": r,
            "fit_r2_note": ("원문이 인쇄한 것은 `Correlation coefficient` (= r) 이지 r^2 가 아니다. "
                            "그래서 fit_r2 로 옮기지 않고 인쇄 이름 그대로 남긴다"),
            "polymer_code": code,
            "method_detail": ("180 deg peel master-curve (Hounsfield 10KM, 6 rates 10-500 mm/min, "
                              "10 temperatures 238-338 K, mirror-finish stainless steel); "
                              "C1/C2 는 (T-T0)/log(a_T) 대 (T-T0) 직선적합에서 얻었다"),
        },
        "notes": (
            f"WLF C1 = {C1} (무차원), T0 = 25 C (298 K), {code}. "
            f"원문 Table 2 의 `C1` 행 인쇄값 그대로다(600 dpi 렌더 확인). "
            f"원문 본문 verbatim — `Plotting (T-T0)/log(aT) versus (T-T0) yielded a straight line and "
            f"allowed determination of the WLF parameters, C1 and C2. The analysis was applied to the "
            f"cohesive failure domain of log peel master-curves for the AA4M-3 copolymers ... The plots "
            f"were linear and therefore consistent with Equation (5).` "
            f"인쇄된 상관계수 r = {r}. " + WLF_CHECK + " "
            f"**이 값이 왜 중요한가 — 72차 HA 는 Gower 2006 의 a_T 45칸에 대해 `표 안에서 서로를 "
            f"검산해 줄 두 번째 열이 없다` 고 적었다. 이 논문의 C1/C2 열이 바로 그 두 번째 열이다.**"
        )}, {
        "key": "mechanical.wlf_c2", "value": C2, "unit": "K",
        "method": "computed", "tier": 1,
        "conditions": {
            "reference_temperature_k": T0_K, "reference_temperature_c": T0_C,
            "equation_verbatim": EQ_PRINTED,
            "equation_reconstructed": EQ_USED,
            "equation_note": ("인쇄된 분모 `C2 + T + T0` 는 이 논문 자신의 Table 2 를 재현하지 못한다"
                              "(최대 0.654 decade). 표준형 `C2 + (T - T0)` 는 20칸 전부를 "
                              "최대 0.026 decade 안에서 재현한다 — 인쇄된 `+T0` 는 오식이다"),
            "log_base": "log10",
            "sign_convention": "log a_T = -C1*dT/(C2+dT)",
            "valid_temperature_range_c": [15, 65],
            "fit_correlation_coefficient_printed": r,
            "fit_r2_note": ("원문이 인쇄한 것은 `Correlation coefficient` (= r) 이지 r^2 가 아니다"),
            "polymer_code": code,
            "unit_note": ("원문은 단위를 안 붙이고 숫자만 인쇄한다. WLF 의 C2 는 온도차 단위라 K 다"
                          "(=C 와 같은 크기). 값은 그대로 두었다"),
            "method_detail": ("180 deg peel master-curve; C1/C2 는 (T-T0)/log(a_T) 대 (T-T0) "
                              "직선적합에서 얻었다"),
        },
        "notes": (
            f"WLF C2 = {C2} K, T0 = 25 C (298 K), {code}. 원문 Table 2 의 `C2` 행 인쇄값 그대로다. "
            f"원문은 단위를 인쇄하지 않는다 — WLF 의 C2 는 온도차라 K 로 넣었고 값은 안 바꿨다. "
            f"인쇄된 상관계수 r = {r}. " + WLF_CHECK
        )}, {
        "key": "structure.molecular_weight", "value": Mz / 1000.0, "unit": "kg/mol",
        "method": "measured", "tier": 1,
        "conditions": {
            "statistic": "Mz (z average)", "test_method": "GPC",
            "fraction": "whole polymer (gel-free)", "polymer_code": code,
        },
        "notes": (
            f"Mz = {Mz} g/mol = {Mz/1000.0:.6g} kg/mol, {code}. 원문 Table 2 의 `Mz` 행 인쇄값이다. "
            f"**DB 에는 같은 폴리머의 Mn·Mw 만 있었다**(Gower 2006 출처 4236 에서 온 것) — z 평균은 "
            f"이 2004 논문에만 인쇄돼 있다. Mn·Mw 는 두 논문이 같은 값을 인쇄하므로 다시 넣지 않았다. "
            f"단위 환산 — 원문 g/mol -> DB 정의 단위 kg/mol, 1000 으로 나눴다."
        )},
    ]
    props_by_mat[name] = props

doc = {"batch": "73차 IC", "materials": [
    {"match_name": name, "source": SRC, "properties": props}
    for name, props in props_by_mat.items()
]}

with open("/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_ic/"
          "ic73_02_gower2004cta_shift_factor_wlf.json", "w") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)

# --- 자체검산: WLF 상수가 인쇄된 a_T 20칸을 재현하는가 ---
worst_std = worst_pr = 0.0
for _n, code, _l, C1, C2, _r, _m in MATS:
    for T, v in PRINTED_AT[code].items():
        std = -C1 * (T - T0_C) / (C2 + T - T0_C)
        pr = -C1 * (T - T0_C) / (C2 + T + T0_C)
        worst_std = max(worst_std, abs(std - v)); worst_pr = max(worst_pr, abs(pr - v))
assert worst_std < 0.03, worst_std
print(f"WLF 재현 — 표준형 최대 {worst_std:.4f} decade / 인쇄형 최대 {worst_pr:.4f} decade")
for _n, code, l15, *_ in MATS:
    a = 10 ** l15
    assert abs(math.log10(a) - l15) < 1e-12
    print(f"  {code}: log a_T(15 C) = {l15} -> a_T = {a:.6g} (왕복 검산 {math.log10(a):.4f})")
n = sum(len(p) for p in props_by_mat.values())
print(f"총 {n} 행 / 재료 {len(props_by_mat)}종 (전부 기존 재료) / 신규 출처 1")
