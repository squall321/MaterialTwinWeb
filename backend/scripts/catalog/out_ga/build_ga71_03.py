# Samieian 2019 가 인쇄한 PVB 중간막의 Prony 6항 2분기와 짝인 축소다항 초탄성 상수를 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "journal",
       "title": "On the bonding between glass and PVB in laminated glass",
       "authors": "M.A. Samieian, D. Cormie, D. Smith, W. Wholey, B.R.K. Blackman, J.P. Dear, P.A. Hooper",
       "year": 2019,
       "doi": "10.1016/j.engfracmech.2019.04.006",
       "url": "https://doi.org/10.1016/j.engfracmech.2019.04.006",
       "publisher": "Engineering Fracture Mechanics, vol. 214, pp. 504-519",
       "local_path": "/data/paper_patent_corpus/cae_papers/14_glass_fracture/"
                     "Samieian - 2019 - On the bonding between glass and PVB in laminated glass.pdf"}

NEWMAT = {"name": "Polyvinyl butyral (PVB) interlayer for laminated glass, 0.76-2.28 mm, rate-branched "
                  "reduced-polynomial hyperelastic + Prony model at 20 C (Del Linz 2016 via Samieian 2019)",
          "category": "polymer",
          "attributes": {"role": "evidence",
                         "role_reason": "원문이 `PVB` 라고만 하고 제조사·등급(Saflex/Trosifol 등)을 밝히지 않는다. "
                                        "특정되는 것은 두께(0.76 / 1.52 / 2.28 mm)와 시험온도 20 °C 뿐이다",
                         "role_confidence": "medium",
                         "material_class": "polyvinyl butyral (PVB) laminated-glass interlayer",
                         "subsystem": "glass",
                         "subsystem_basis": "접합유리의 중간막이다.",
                         "process": "through-cracked tensile / pure PVB tensile, 0.01-10 m/s, 20-60 C"}}

# ── Table 4 `Prony series constants for reduced polynomial viscoelastic model` (PDF 12쪽) ──
# ── Table 3 `Material constants for reduced polynomial hyperelastic model` (같은 쪽) ──
# **PDF 12쪽을 350 dpi 로 그려 두 표를 전부 눈으로 대조했다** (ga71_sam_t3_crop.png · ga71_sam_t4_crop.png).
# 지수의 마이너스 부호(1e-4 ~ 1e-6)가 렌더에도 그대로 있다 — 추출과 완전 일치, 잃은 부호 없음.
BRANCH = {
    "low": {"label": "up to 8/s",
            "tau": [1e-4, 1e-3, 1e-2, 0.1, 1.0, 100.0],
            "g":   [0.0, 0.898, 0.0, 0.0, 0.0, 0.102],
            "C":   [40.7, 75.7, 0.0]},
    "high": {"label": "above 20/s",
             "tau": [1e-6, 1e-5, 1e-3, 0.1, 10.0, 1000.0],
             "g":   [0.0, 0.948, 0.0151, 0.00112, 0.0, 0.0],
             "C":   [311.0, 0.0112, 1.3]},
}
TEMP_C = 20.0

for b in BRANCH.values():
    assert len(b["tau"]) == len(b["g"]) == 6
    b["sum_g"] = sum(b["g"])
    assert b["sum_g"] <= 1.0 + 1e-12, b["sum_g"]
    b["g_inf"] = 1.0 - b["sum_g"]

RECITE = ("**이 표의 값은 Samieian 이 직접 잰 것이 아니라 Del Linz 의 모형을 그대로 옮겨 쓴 것이다** — "
          "본문 verbatim: *\"For the glass a linear elastic material model was used and for the PVB a "
          "viscoelastic material model developed by Del-Linz was used [25].\"* "
          "[25] = Del Linz et al., *Determining Material Response for Polyvinyl Butyral (PVB) in Blast "
          "Loading Situations*, Experimental Mechanics 56(9) 1501-1517 (2016), doi 10.1007/s11340-016-0179-5. "
          "**출처를 Samieian 2019 로 적은 것은 우리가 실제로 열고 렌더로 대조한 문서가 그것이기 때문이다** — "
          "원출처 논문은 코퍼스에 없다. 원출처를 확보하면 이 행들의 출처를 옮기고 값을 대조해라.")

TREF_NOTE = ("**기준온도가 인쇄돼 있지 않다 — 이 급수는 마스터커브 적합이 아니기 때문이다.** "
             "Del Linz 의 모형은 온도 하나(20 °C)에서 **율속 구간별로 두 벌**을 맞춘 것이고, "
             "다른 온도는 시간-온도 중첩으로 **시험율속을 옮겨** 다룬다 — 본문 verbatim: "
             "*\"The loading rate-dependency was accounted for in the material model, by simply adjusting "
             "the loading rate being applied to the glass. The temperature dependency, however, was treated "
             "differently. Time-temperature superposition was used to predict the behaviour of the PVB at a "
             "different temperature, by shifting the test rate.\"* "
             "그래서 `reference_temperature_c` 대신 **모형이 성립하는 온도** `temperature_c = 20` 을 적고 "
             "`reference_temperature_printed = false` 로 없다는 사실을 남겼다. "
             "20 °C 는 원문이 이 모형의 기준 시험조건으로 못박은 온도다(*\"if the temperature was increased "
             "from 20 °C to 30 °C, the loading rate would have to be reduced by a factor of approximately 16\"*). "
             "**Del Linz 의 WLF 상수는 이 논문에 인쇄되지 않는다** — Hooper [27] 의 데이터로 얻었다고만 쓴다.")

MODE_NOTE = ("**완화모드는 전단(편차)이다 — 다만 원문이 그 말을 쓰지 않는다.** 표에는 g_i 라고만 적혀 있고, "
             "해석은 Abaqus 로 했다([24] Simulia, Abaqus 2016). Abaqus 의 시간영역 점탄성(*VISCOELASTIC, "
             "TIME=PRONY)에서 g_i 는 **정규화 전단완화계수**이고 축소다항 초탄성의 순간응답에 곱해진다. "
             "그 규약으로 읽었다는 사실을 `relaxation_mode_basis` 에 남겼다 — 원문 문장이 아니라 우리의 판독이다.")

props = []


def add(key, value, unit, method, cond, notes):
    props.append({"key": key, "value": value, "unit": unit, "method": method,
                  "tier": 1, "conditions": cond, "notes": notes})


for tag, b in BRANCH.items():
    SET = f"samieian2019_pvb_{tag}rate_6term"
    check = (f"**검산 — 가중치 합.** sum g_i = {b['sum_g']:.5f} <= 1 이므로 "
             f"g_inf = {b['g_inf']:.5f} 다. "
             + ("**저율속 분기는 합이 정확히 1 이라 g_inf = 0 — 이 모형에서 PVB 는 장기에 강성이 0 으로 "
                "완전히 완화한다.** 특이하지만 인쇄된 값이 그렇고, 두 항(g2 = 0.898 · g6 = 0.102)만 "
                "0 이 아니라 합이 자명하게 1.000 이다."
                if tag == "low" else
                "고율속 분기는 네 항 중 세 항만 0 이 아니고 g_inf = 0.03578 이 남는다.")
             + " **절대 계수를 재현할 초기 계수 G0/E0 는 이 논문에 인쇄되지 않는다** — "
               "순간응답은 Table 3 의 축소다항 초탄성 상수가 준다(같이 실었다). "
               "그래서 E(0)/G(0) 를 숫자로 되계산할 수는 없다.")

    common = (f"Table 4 `Prony series constants for reduced polynomial viscoelastic model` 의 "
              f"`{b['label']}` 열, 6항. 짝인 초탄성 상수는 Table 3 의 같은 열이다. "
              f"{check} {TREF_NOTE} {MODE_NOTE} {RECITE} "
              "적합 결과라 method=computed, 표 인쇄값이므로 tier1. "
              "PDF 12쪽 350 dpi 렌더로 두 표를 눈으로 대조했다(ga71_sam_t3_crop.png · ga71_sam_t4_crop.png).")

    def base(i):
        return {"prony_term": i, "prony_terms_total": 6, "term_index": i, "set_id": SET,
                "model": "prony_on_reduced_polynomial_hyperelastic", "series": "shear",
                "relaxation_mode": "shear (deviatoric, normalised)",
                "relaxation_mode_basis": "원문은 모드를 쓰지 않는다 — Abaqus *VISCOELASTIC TIME=PRONY 의 "
                                         "g_i 규약(정규화 전단완화계수)으로 읽었다",
                "temperature_c": TEMP_C,
                "reference_temperature_printed": False,
                "strain_rate_branch": b["label"],
                "normalisation": "g_i = G_i / G_0; G_0 는 축소다항 초탄성의 순간응답이고 수치로 인쇄되지 않는다",
                "values_recited_from": "Del Linz et al. 2016, doi 10.1007/s11340-016-0179-5",
                "source_data": "tensile tests on pure PVB and through-cracked laminated glass, 20 C"}

    for i, (t, g) in enumerate(zip(b["tau"], b["g"]), start=1):
        add("mechanical.prony_relative_modulus", g, "1", "computed",
            dict(base(i), term=f"g{i}"),
            f"정규화 완화 가중치 g_{i} = {g:g} (`{b['label']}` 분기). "
            + ("**0 은 결측이 아니라 인쇄된 값이다** — 6항 격자 중 이 항이 쓰이지 않았다는 뜻이고, "
               "완화시간과 항수를 맞추려면 반드시 함께 있어야 한다. " if g == 0.0 else "")
            + common)
        add("mechanical.prony_relaxation_time", t, "s", "computed",
            dict(base(i), term=f"tau{i}"),
            f"완화시간 tau_{i} = {t:g} s (`{b['label']}` 분기, 행 머리글 `τ i (s)`). " + common)

    # **g_inf 행은 넣지 않았다.** 원문이 인쇄하지 않는 값이고 정규화 정의(sum g + g_inf = 1)에서
    # 바로 나오는 잔차라, 넣으면 "인쇄된 값"(tier1)이 아닌 것이 tier1 행으로 선다.
    # 값(저율속 0.00000 · 고율속 0.03578)은 6항 전부의 notes 검산문에 적어 뒀다 — 빈칸이 틀린 등급보다 낫다.

    for j, cval in enumerate(b["C"], start=1):
        add("mechanical.hyperelastic_coefficient", cval * 1e6, "Pa", "computed",
            {"model": "reduced_polynomial_3", "term": f"C{j}",
             "abaqus_equivalent_term": f"C{j}0",
             "set_id": f"samieian2019_pvb_{tag}rate_redpoly3",
             "paired_prony_set_id": SET,
             "temperature_c": TEMP_C, "strain_rate_branch": b["label"],
             "printed_value_mpa": cval,
             "values_recited_from": "Del Linz et al. 2016, doi 10.1007/s11340-016-0179-5"},
            f"Table 3 `Material constants for reduced polynomial hyperelastic model` 의 "
            f"`{b['label']}` 열 `C{j} (MPa) = {cval:g}` -> Pa 로 환산(x1e6). "
            "**Prony g_i 는 이 초탄성 순간응답에 곱해지는 무차원 가중치라 이 상수 없이는 쓸 수 없다** — "
            "짝으로 실었다. " + RECITE + " PDF 12쪽 350 dpi 렌더 확인(ga71_sam_t3_crop.png).")

add("physical.density", 1100.0, "kg/m^3", "measured",
    {"temperature_c": TEMP_C, "printed_as": "rho = 1100 kg/m3 (Table 2, PVB 행)"},
    "Table 2 `Material model summary` 의 PVB 행 `ρ = 1100 kg/m3`. "
    "밀도는 Del Linz 재인용이 아니라 Samieian 이 모델 요약표에 직접 적은 값이다. "
    "PDF 12쪽 렌더 확인(ga71_sam_t3_crop.png 위쪽 표).")

doc = {"batch": "71차 GA", "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("ga71_03_samieian2019_pvb_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{out.name}: {len(props)} 행,  "
      + ",  ".join(f"{t} sum g = {b['sum_g']:.5f} (g_inf {b['g_inf']:.5f})" for t, b in BRANCH.items()))
