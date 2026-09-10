# 73차 ID — 마지막 V5 카드(2743 Chiu 2015 EMC) 판정을 판정 JSON 에 덧붙인다.
import json

TAG = "**[73차 ID]** "
DOC = ("/data/paper_patent_corpus/cae_papers/06_warpage_thermomech/"
       "Chiu - 2015 - Development of a consistent multiaxial viscoelastic model for package warpage simulation.pdf (7쪽)")
COMMON = (
  "\n\n**연 문서** — 이 카드의 유일한 출처인 " + DOC + " 를 전권으로 열었다."
  "\n\n**이 논문의 표는 셋이 전부다** — Table 1(체적완화계수 Prony 17항) · Table 2(전단완화계수 Prony 21항) · "
  "Table 3(WLF 이동인자). **세 표 모두 이미 이 카드에 들어가 있다**(prony_relative_bulk_modulus 17행 · "
  "prony_relative_modulus 21행 · prony_relaxation_time 38행 · wlf_c1/c2 각 2행 · bulk_modulus · shear_modulus)."
  "\n\n**그리고 이 제품에는 열 벤더 시트가 없다** — 원문이 `The EMC considered in this study is a commercial "
  "compound with 70 wt% silica filler` 라고만 쓰고 **등급명을 끝까지 안 밝힌다**(카드의 `role_reason` 이 이미 "
  "그렇게 적어 두었다). 어느 벤더의 어느 등급인지 물을 대상이 없으므로 벤더 문서 층 자체가 열리지 않는다.")

ABSENT = (TAG + "**전권 토큰 검사에서 0건이다** — `density` 0 · `g/cm` 0 · `specific heat` 0 · "
          "`conductivit` 0 · `tensile strength` 0. 이 논문은 다축 점탄성 모델을 세우는 논문이라 "
          "인장 DMA(TA Q800) · 비틀림 DMA(Anton Paar MCR-302) · TMA(TA Q400) 셋만 돌렸고, "
          "**이 물성은 측정 대상이 아니었다.**" + COMMON)

FIGONLY = (TAG + "**이 물성은 이 논문에 그림으로만 있다 — 표에도 본문에도 숫자가 없다.** "
           "그래프 판독은 금지이므로(브리프 0절 3항) 값으로 옮길 수 없다." + COMMON)

FIG = {
 "thermal.expansion_linear":
   "\n\n**어느 그림인가** — `Figure 7. CTE measured by TMA.` 다. y축이 `CTE (ppm/oC)` 0~100, "
   "x축이 `T (oC)` −100~300 인 곡선 두 줄(exp. / fitted)이고, **본문은 이 그림을 가리키며 "
   "`the test result is shown in Fig. 7` 라고만 쓴다.** α1·α2 를 숫자로 인쇄한 자리가 없다.",
 "mechanical.poisson_ratio":
   "\n\n**어느 그림인가** — `Figure 9. Viscoelastic Poisson's ratio calculated from the …` 와 "
   "`Figure 13. The fitted Poisson's ratio, reference temperature: 120 °C` 둘이다. "
   "둘 다 **시간의존 포아송비 곡선**이고 단일 숫자가 아니다. 본문이 숫자를 말하는 자리는 "
   "`Poisson's ratio reaches negative value, which is physically …` 처럼 **부호를 말하는 서술**뿐이다. "
   "**주의 — 이 카드에는 체적계수 κg=14 GPa 와 전단계수가 이미 있는데, 거기서 ν 를 만들면 역산이다.** "
   "브리프 0절 2항이 금지한 그 자리다.",
 "mechanical.youngs_modulus":
   "\n\n**어느 그림인가** — `Figure 1`(인장 DMA 측정점과 Young's storage modulus 마스터커브) · "
   "`Figure 6`(원본/수정 마스터커브 대조) · `Figure 10`(fitted Young's storage modulus mastercurve) 이다. "
   "**전부 저장탄성률 마스터커브(주파수축)이고 정적 영률의 인쇄값이 아니다.** "
   "카드가 이미 담은 것은 이 마스터커브를 Laplace-Carson 영역에서 변환한 **Prony 계수**이고, "
   "그것이 이 논문이 숫자로 인쇄한 전부다.",
}

verdicts = [{
  "material_id": 2743,
  "name": "Epoxy molding compound, commercial low-filler 70 wt% fused silica, Tg 120 C (ASE/NCKU multiaxial viscoelastic characterisation, Chiu 2015)",
  "core_no_public_document": {
     "physical.density": ABSENT,
     "thermal.specific_heat": ABSENT,
     "thermal.conductivity": ABSENT,
     "mechanical.tensile_strength": ABSENT,
     "thermal.expansion_linear": FIGONLY + FIG["thermal.expansion_linear"],
     "mechanical.poisson_ratio": FIGONLY + FIG["mechanical.poisson_ratio"],
     "mechanical.youngs_modulus": FIGONLY + FIG["mechanical.youngs_modulus"],
  },
}]

doc = json.load(open('id73_02_verdicts.json'))
doc['verdicts'] += verdicts
json.dump(doc, open('id73_02_verdicts.json','w'), ensure_ascii=False, indent=1)
n = sum(len(v.get('core_absent_from_vendor_sheet', v.get('core_no_public_document', {}))) for v in doc['verdicts'])
print("재료", len(doc['verdicts']), "· 칸", n)
