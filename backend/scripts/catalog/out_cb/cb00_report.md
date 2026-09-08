<!-- 67차 CB 수집 보고서 — 저온 유기 평탄화막(적층 ②)의 정체 규명과 산소투과계수 -->

# 67차 CB — 저온 유기 평탄화막

요청서 `PDE/oxygen-diffusion/물성요청_산소확산_원자재6종.md` 의 2순위 항목이다.
적층 ②, 두께 15 µm, 현재 가정으로 총 산소투과의 13.7% 를 차지한다.

---

## 1. 평탄화막의 정체 — 어디까지 확정했는가

**적층 위치까지 문서로 확정했다. 소재 계열도 확정했다. 벤더 제품명은 확정 못 했다.**

### 1.1 적층 위치 — 완전히 일치하는 특허를 찾았다

`US 9,978,816 B2` (삼성디스플레이, 2018-05-22 등록, KR 우선권 10-2015-0058112).
로컬 사본 `/data/paper_patent_corpus/standards_appnotes/display/US9978816B2_SamsungDisplay_OLED_CF_overcoat530_stack.pdf`
(스캔 PDF 라 직접 OCR 해서 읽었다 — `US9978816B2_OCR.txt`).

원문 verbatim.

> "An overcoat 530 for protecting the color filter and planarizing a surface of the layer with the color filter may be provided on the first to third color filters 510R, 510G, and 510B."

> "the encapsulation layer 400, the color filter layer CF, the overcoat 530, the first adhesive layer 600, the touch panel 700, the second adhesive layer 800, the window 900, and the first light blocking layers 850a and 850b are sequentially laminated."

> "The first adhesive layer 600 may use a silicon and/or acryl-based compressive adhesive such as a PSA with a low modulus value"

이 순서가 해석 적층표와 그대로 맞는다.

| 해석 적층표 | US9978816B2 |
|---|---|
| TFE CVD (하부 경계) | encapsulation layer 400 |
| ① G CF 3 µm | color filter layer CF (510R/G/B) |
| ② Acrylic (저온 유기막) 15 µm | **overcoat 530** |
| ③ PSA 15 µm | first adhesive layer 600 = PSA |

**②는 컬러필터 오버코트다.** 그리고 같은 특허가 ③을 별개의 PSA 층으로 명시하므로,
**②에 점착제 값을 물려주는 것은 두 층을 같은 재료로 취급하는 것**이다.

### 1.2 소재 계열 — 아크릴-에폭시 가교 열경화물, 유리상

`US 11,332,634 B2` (BOE·허페이신성, 2022-05-17, CN 우선일 2017-08-30) 배경부 verbatim.
직접 내려받아 OCR 로 읽었다.

> "At present, the OC material mainly consists of acrylic resin-epoxy resin as a basic skeleton component, and an OC raw material available for a coating process may be obtained by adding a crosslinking agent, a surface modifier, a solvent, and the like. As one of the main skeleton components, acrylic resin exhibits high optical properties, but there is room for improvement in hygroscopicity and dielectric properties. **At present, the most commonly used acrylic resin is polymethyl methacrylate.**"

청구항 1 verbatim — 스티렌+(메타)아크릴레이트 10~30 wt% / 에폭시 수지 10~30 wt% /
가교제(디비닐벤젠) 1~3 wt% / 광·열개시제 0.1~0.5 wt% / 계면활성제 1~3 wt% / 용제 40~77 wt%.
경화는 150~250 °C 5~15 분 + UV 5~10 분 (종래 LCD CF 용).

같은 계열을 삼성디스플레이도 인쇄한다 — `US 2014/0240645 A1` 합성예 1 의 평탄화막용 아크릴 공중합체는
**메타크릴산 30 / 스티렌 30 / 글리시딜메타크릴레이트 40 중량부**, 프리베이크 100 °C.
그리고 `US 9,978,816 B2` 는 오버코트의 유기 절연막 재질로
"a general purpose polymer (PMMA and/or PS), a polymer derivative having a phenol group, an acryl-based polymer, ..." 를 나열한다.

이 세 문서가 같은 것을 가리킨다. **메타크릴산·스티렌·글리시딜메타크릴레이트 공중합체를
에폭시 개환으로 가교한 열경화물**이고, 구성 성분의 균질중합체 Tg 가 각각 228 / 100 / 74 °C 라
가교 전에도 상온에서 유리상이다.

### 1.3 저온 경화가 무엇을 강제하는가

`US 10,822,449 B2` (삼성SDI, 2020-11-03) verbatim.

> "the conventional olefin-based unsaturated compound has a curing temperature of 150° C. or greater and thus may not be cured at a low temperature of 100° C. or less and not applied to a flexible display-manufacturing process."

> "When the surface hardness is low, a haze phenomenon occurs after CVD"

두 가지가 나온다.

- OLED/유연 공정의 오버코트는 **100 °C 이하** 경화다. 요청서가 적은 "≤ 130~230 °C" 보다 더 낮다.
  종래의 150 °C 이상 라디칼 경화는 배제되고, **에폭시 개환(양이온) 경화 또는 100 °C 이하 UV 경화**로 간다.
- 이 층은 **표면경도를 요구받는다.** 경도를 요구하는 층은 상온 고무상일 수 없다.
  점착제(E ~ 0.1 MPa 급)는 이 자리에 들어갈 수 없다는 뜻이다.

같은 특허의 해법은 에폭시-실록산이다 — 아크릴이 아닌 별개 분기다. 다만 해석 적층표의 원본 표기가
`Acrylic (저온 유기막)` 이므로 이 패널은 아크릴 분기다.

### 1.4 확정하지 못한 것

- **벤더·제품명.** 특정하지 못했다. 검색 수준에서 JSR 의 SS/Optomer 계열이 컬러필터 오버코트용
  열경화 아크릴 보호막으로 언급되고 도쿄오카·스미토모·동진쎄미켐도 이 영역 공급사로 나오지만,
  **어느 제품의 데이터시트도 직접 열어 확인하지 못했고 산소투과 항목을 인쇄한 벤더 문서를 찾지 못했다.**
  이 문단은 문서 근거가 아니라 다음 배치를 위한 단서로만 읽어야 한다.
- **15 µm 라는 두께.** 고전적 CF 오버코트는 2~3 µm, TFE 유기막은 4~8 µm 다. 15 µm 는 둘 다보다 두껍다.
  이것이 "두꺼운 잉크젯 평탄화막" 쪽일 가능성을 남긴다 — 그 경우 가교밀도가 낮아 값이 올라간다.
  **이 잔여 위험을 상한값으로 덮었다**(§3, §5).

---

## 2. 1.707e-15 의 계보 — 재료 370·539 는 어디서 왔는가

요청서가 "UV 경화 아크릴레이트 = 1.707e-15" 로 적은 값의 출처를 끝까지 따라갔다.

```
source 2870
 = V. A. Kusuma, PhD dissertation, The University of Texas at Austin, 2009 (지도 B. D. Freeman)
   "Effect of Network Structure Modifications on the Light Gas Transport Properties of
    Cross-linked Poly(ethylene oxide) Membranes"
```

- **재료 539 `XLPEGDA-100`** — t3 handbook. Kusuma Table 5.3/6.3 첫 행 `'--- 100 110 ± 6 15 ± 0.8 5.5 ± 0.3 5.1 ± 0.3 1.9 ± 0.1'`,
  열 머리글 `CO2 H2 CH4 O2 N2` 이므로 O2 = **5.1 Barrer** @ 35 °C, infinite dilution.
  5.1 × 3.3464e-16 = 1.7067e-15. 노트에 `[정규화] 논문이 인용한 문헌값이라 그 논문의 측정이 아님` 이 이미 붙어 있다.
- **재료 370 `ThreeBond TB3062U`** — **t4 estimated**. 539 의 값을 그대로 빌려온 추정이다.
  근거는 벤더 데이터시트의 경화물 물성(Young's modulus 38.2 MPa, 신율 250 %, Tg 74 °C, 흡수율 12.8 %)뿐이고,
  노트에 "벤더가 조성을 공개하지 않아 어느 네트워크에 대응하는지 확정할 수 없다" 고 적혀 있다.
  TB3062U 데이터시트를 grep 한 결과 **가스 투과 항목 자체가 없다**는 것도 노트에 남아 있다.

**결론.** 요청서의 "UV 경화 아크릴레이트 1.707e-15" 는 실제로는
**가교 폴리(에틸렌옥사이드) 막 — PEGDA(n=14) 단독 광경화 하이드로겔 네트워크**의 값이다.
CO2 분리막 연구용 재료이고, 친수성·상온 고무상이다.
디스플레이 평탄화막의 대표값이 될 수 없다. **요청서의 후보 표는 두 항목 모두 고무상이었다.**

---

## 3. 넣은 값 — 2건

디렉터리 `backend/scripts/catalog/out_cb/`, 파일 `cb01_materials.json`.
재료 카드는 신규 1건이다(DB 에 평탄화막/오버코트 카드가 하나도 없다 — 이름·별칭 검색 0건).

### 값 ① — 7.1e-17 mol/(m·s·Pa) · **tier 3** · measured

출처 `US 10,259,948 B2` (Kaneka Corporation + The Texas A&M University System, 2019-04-16),
**Comparative Example 1**. 로컬 PDF 를 직접 받았다.

원문 verbatim.

> "A free-standing film containing no inorganic nanoplatelets was then produced in the same manner as in Example 2 except that the drying time for the coating in Example 2 was skipped. The free-standing film had a total light transmittance of 91.3%, a haze of 0.8% and oxygen transmission rate of 1.7\*10⁻¹² mol\*Pa⁻¹\*m⁻²\*s⁻¹ and permeability coefficient for oxygen of **7.1\*10⁻¹⁷** mol\*Pa⁻¹\*m⁻²\*s⁻¹."

시료 조성 (Example 2 에서 ZrP 만 뺀 것) — IBOA(이소보닐 아크릴레이트) 9.0 g / EO3TMPTA(에톡실화 3관능 가교제) 5.0 g /
**에폭시 아크릴레이트 CN120(비스페놀A 에폭시 디아크릴레이트, Sartomer)** 6.0 g / HCPK 광개시제 1 g.
= IBOA 42.8 / EO3TMPTA 23.8 / CN120 28.5 / HCPK 4.8 wt%.
1000 mJ/cm² 메탈할라이드 UV 경화, 두께 30~50 µm, 자립막, 무충전. 전광선투과율 91.3 %, 헤이즈 0.8 %.
측정은 JIS K 7126-1(차압법), Toyoseiki BT-3.

**단위 정정 (원문 오타).** 이 행의 투과계수 단위가 `mol*Pa⁻¹*m⁻²*s⁻¹` 로 인쇄돼 있는데
이는 투과도(permeance)의 단위다. 바로 위 Example 2 는 같은 물리량을
`permeability coefficient for oxygen of 3.6*10⁻¹⁸ mol*m*Pa⁻¹*m⁻²*s⁻¹` 로 `*m` 을 넣어 인쇄한다.
즉 Comparative Example 1 에서 `*m` 이 빠진 식자 오류이고, 단위는 mol/(m·s·Pa) — **DB 단위와 같아 환산이 없다.**

**독립 검산.** 같은 문장이 투과도와 투과계수를 둘 다 인쇄하므로 그 비가 시편 두께여야 한다.

```
7.1e-17 / 1.7e-12 = 4.18e-5 m = 41.8 µm      원문 표기 두께 "about 30 to 50 micrometers" 안 ✅
3.6e-18 / 8.1e-14 = 4.44e-5 m = 44.4 µm      Example 2 로도 같은 검산이 맞는다 ✅
```

**Barrer 되돌림 검산.** 7.1e-17 / 3.3464e-16 = **0.2122 Barrer**.

**세 계열이 같은 자리로 모인다.**

| 재료 | 값 [mol/(m·s·Pa)] | Barrer | 성격 | 출처 |
|---|---|---|---|---|
| UV 경화 아크릴-에폭시 네트워크 | 7.1e-17 | 0.212 | 가교·유리상 | US10259948B2 Comp.Ex.1 (이번 건) |
| PMMA (25 °C, 0 %RH) | 4.79e-17 | 0.143 | 선형·유리상 | DB 재료 75, Membranes 2022 실측 |
| 에폭시-아민 Epon828/A2049 (25 °C) | 4.7e-17 | 0.140 | 가교·유리상 | DB 재료 438, Polymers 2021 실측 |

**tier 3 인 이유.** 인쇄된 실측값이지만 (a) 이 패널이 쓰는 평탄화막 제품·grade 가 아니고,
(b) 원 시료는 방식/배리어 코팅 특허의 비교예라 오버코트용 배합이 아니며,
(c) 이 행에 측정 온도·습도가 다시 인쇄되지 않았다(같은 특허 FIG.5A 계열이 23 °C / 50 %RH, JIS K 7126-1 표준 분위기도 23 °C 라 23 을 적고 그 사실을 조건에 명시했다).

### 값 ② — 3.0118e-16 mol/(m·s·Pa) · **tier 4** · estimated · `bound: "upper"`

감도해석용 상한이다. DB 재료 533 `UV-cured BPAEDA4 homopolymer acrylate network` 의 0.9 Barrer @ 35 °C
(Kusuma Table 8.2 원문 행 `'--- 100 100 12 5.3 0.6 0.9 0.2'`)를 그대로 세웠다.
DB 가 가진 UV 광경화 아크릴레이트 네트워크 12종(재료 527~539)의 O2 범위는 0.45~19.0 Barrer 이고 그중 최저다.
그 계열은 전부 PEG 계 친수성 고무상이므로 유리상 오버코트보다 투과가 높은 쪽이고,
그중 최저값이면 "이 층이 예상보다 성기더라도 여기까지" 라는 상한이 된다.
가교 에폭시-아민 80 °C 값 0.768 Barrer 이 독립 대조다.
`method:"estimated"` · `conditions.assumption:true` · notes 에 근거를 모두 적었다.

---

## 4. 못 넣은 것과 이유

| 항목 | 상태 | 이유 |
|---|---|---|
| 평탄화막 **제품 grade 실측** | 못 넣음 | JSR·TOK·스미토모·동진쎄미켐 공개 문서에 산소투과 항목 자체가 없다. 벤더 데이터시트는 투과율·경도·유전율·내약품성만 인쇄한다 |
| 평탄화막 **직접 측정 논문** | 못 넣음 | "display overcoat / planarization layer" + "oxygen permeability" 로 검색한 문헌·특허에서 이 층 자체를 잰 문서를 찾지 못했다. 검색 0건이 부재의 근거가 아니므로 계열 대체로 갔고 그 사실을 grade_scope 에 적었다 |
| 이 층의 **Tg / 가교밀도** | 못 넣음 | 특허들이 조성은 인쇄하지만 경화물 Tg 나 가교밀도를 인쇄하지 않는다. 요청서 §3 이 요구한 "가교밀도가 PEGDA 계열의 어디쯤인가" 는 **문서로 답하지 못했다** — 성분 균질중합체 Tg(228/100/74 °C)와 표면경도 요구로 "유리상" 까지만 말할 수 있다 |
| ACS Omega 2025 에폭시아크릴레이트 봉지재 OTR | **의도적으로 버렸다** | 형제 배치가 받아둔 `o2_epoxyacrylate_encapsulant_acsomega_2025_PMC12096231_fulltext.xml` 에 100 µm 막의 OTR 5.10 이 인쇄돼 있으나 **단위가 `g/m² day` 로 적혀 있다.** 산소 OTR 을 g 으로 적는 것은 드물어 cc/m²·day 오기 가능성을 배제할 수 없고, 어느 쪽으로 읽느냐에 따라 값이 700배 갈린다(5.44 Barrer vs 0.0078 Barrer). 단위가 확정되지 않은 값은 쓰지 않았다 |
| `physical.gas_permeance_o2` 1.7e-12 | 안 넣음 | US10259948B2 가 직접 인쇄한 값이지만 그 행의 정확한 시편 두께가 "30~50 µm" 범위로만 적혀 있어 두께축을 확정할 수 없다. 투과계수 검산용으로만 notes 에 남겼다 |
| USPTO 스캔 PDF 의 텍스트층 | 해결함 | USPTO `dirsearch-public` PDF 는 전부 이미지 스캔이라 pdftotext 가 0바이트다. tesseract 로 300 dpi OCR 해서 읽었고, OCR 텍스트를 `*_OCR.txt` 로 같이 남겼다. Google Patents 는 중간부터 503 으로 막혀 로컬 OCR 이 주 경로였다 |
| `US 2014/0240645 A1` 로컬 원본 | 못 받음 | 공개공보라 USPTO 특허번호 다운로드 경로가 안 먹고, Google Patents 는 503 이었다. 조성(MAA 30/St 30/GMA 40)은 Google Patents 렌더링으로만 확인했다. **로컬 사본 없음을 JSON 에 `local_path: null` 로 표시했다** |

---

## 5. 요청서의 후보 표를 좁혔는가 — 좁혔다. 그리고 표 자체가 틀렸다

요청서 §4 2순위의 표는 이랬다.

| 후보 | 투과율 | 총 투과 변화 |
|---|---|---|
| 아크릴 점착제 (현재 가정) | 1.181e-14 | 기준 |
| UV 경화 아크릴레이트 | 1.707e-15 | −12.5% |
| PMMA 벌크 | 더 낮음 | 더 큼 |

**두 후보 모두 고무상이었다.**
1.181e-14 는 poly(n-hexyl acrylate) — 가교 없는 상온 고무상 n-알킬 아크릴레이트, 즉 점착제 자체다.
1.707e-15 는 XLPEGDA-100 — 친수성 PEG 하이드로겔 네트워크다.
평탄화막은 **가교된 유리상 아크릴-에폭시 열경화물**이라 둘 다 아니다.

갱신한 표.

| 후보 | 𝒫 [mol/(m·s·Pa)] | Barrer | 현재 대비 | 총 투과 변화 | ②의 새 기여율 |
|---|---|---|---|---|---|
| 아크릴 점착제 (현재 가정) | 1.1813e-14 | 35.30 | 기준 | 기준 | 13.70% |
| 요청서의 UV 경화 분기 (XLPEGDA) | 1.7067e-15 | 5.10 | 1/6.9 | −11.7% | 2.24% |
| **이번 배치 t3 — UV 경화 아크릴-에폭시 네트워크** | **7.1e-17** | **0.212** | **1/166** | **−13.62%** | **0.095%** |
| 이번 배치 t4 상한 — 강직 가교 아크릴레이트망 | 3.0118e-16 | 0.900 | 1/39 | −13.35% | 0.403% |
| (극한) 완전 불투과 | 0 | 0 | — | −13.70% | 0% |

계산은 요청서와 같은 병렬 가정 Σ𝒫ᵢtᵢ, ②의 현재 기여 13.7% 기준이다.

**핵심은 6.9배가 갈리는 자리가 아니게 됐다는 것이다.**
t3 값(−13.62%)과 상한(−13.35%)의 차이는 **0.27 %p** 이고,
상한과 "이 층이 산소를 전혀 안 통과시킨다"(−13.70%)의 차이도 0.35 %p 다.
즉 **남은 4.2배의 불확실성이 총 투과를 0.35 %p 밖에 못 움직인다.**
이 층은 더 이상 감도 항목이 아니다.

거꾸로 말하면 — 지금까지의 13.7% 기여는 **거의 전부 잘못 빌려온 점착제 값 때문**이었다.
바로잡으면 ②는 컬러필터(0.01%)와 같은 등급의 무시 가능 층으로 내려간다.

이것이 재배치를 부른다. 요청서 §6 이 예고한 대로다.
② 가 빠지면 남는 것은 OCA 68.6% · PSA 13.7% · TAC 3.7% 이고, 이 셋의 상대 비중이 커진다.
**OCA 하나가 총 투과의 79% 를 차지하게 된다**(68.6/0.8638).

---

## 6. 다음 배치에 넘길 것

1. **우선순위를 다시 매겨야 한다.** ② 가 닫히면서 요청서 §4 의 3순위 TAC(3.7%) 이
   상대적으로 4.3% 로 올라가지만 여전히 작다. **OCA 가 79% 가 된다** — OCA 의 제품 실측이
   이제 단일 최대 항목이다. 요청서 §3 이 지적한 대로 현재 OCA 값은 13종이 공유하는
   한 문헌값(poly(n-hexyl acrylate) 35.3 Barrer)의 전파이고, 이 배치에서 그 값이
   **점착제로서는 맞지만 다른 층에 물려주면 최대 250배 틀린다**는 것이 드러났다.
   같은 전파가 OCA 자신에게는 맞는지 별도로 검증해야 한다.
2. **③ PSA 도 같은 검사를 받아야 한다.** ③은 진짜 점착제라 1.181e-14 가 계열로는 맞다.
   다만 ②와 ③이 같은 숫자를 갖던 상태가 우연이 아니라 **같은 계열값을 물려받았기 때문**이었음이
   이 배치로 확인됐다. ③의 실제 grade 실측은 여전히 없다.
3. **평탄화막 제품 실측 확보 경로.** 공개 문서로는 닫히지 않는다.
   벤더(JSR·TOK·동진쎄미켐·LG화학)에 **"오버코트/평탄화막 경화물의 산소투과계수 또는
   OTR + 시편 두께"** 를 직접 요청하는 편이 빠르다. 요청 시 이 배치의 카드 이름·별칭을 그대로 쓰면
   "하드코트" 로 잘못 전달되는 사고를 막을 수 있다.
4. **15 µm 두께의 확인.** 고전 CF 오버코트(2~3 µm)·TFE 유기막(4~8 µm) 어느 쪽보다도 두껍다.
   해석 적층표의 15 µm 가 실측인지 가정인지 확인이 필요하다.
   두꺼운 잉크젯 평탄화막이라면 가교밀도가 낮아 상한(3.0118e-16) 쪽으로 붙는다 —
   그래도 총 투과는 0.27 %p 밖에 안 움직이므로 급하지 않다.
5. **`physical.diffusion_coefficient` · `physical.gas_solubility` 는 여전히 공백이다.**
   모델 문서 I-5(계면 조건이 농도 연속인지 분배계수인지)가 풀리지 않으면
   층별 S 가 필요해질 수 있다. 이 배치는 𝒫 만 채웠다.

---

## 부록 — 이 배치가 새로 받아 로컬에 둔 원문

전부 `/data/paper_patent_corpus/standards_appnotes/display/` 아래다.
USPTO 배포 PDF 는 이미지 스캔이라 300 dpi tesseract OCR 텍스트를 같이 남겼다.

```
US10259948B2_Kaneka_TexasAM_coating_compositions.pdf          ← 값 ①의 출처
US9978816B2_SamsungDisplay_OLED_CF_overcoat530_stack.pdf      ← 적층 위치 확정
US9978816B2_OCR.txt
US11332634B2_BOE_overcoat_layer_composition.pdf               ← 소재 계열 확정
US11332634B2_OCR.txt
US10822449B2_SamsungSDI_low_temperature_curing_overcoat.pdf   ← 저온 경화 제약·경도 요구
US10822449B2_OCR.txt
```

주의 — 이 디렉터리에는 동시에 도는 형제 배치들이 받아둔 파일이 이미 많다.
그중 `pat_US10259948_Kaneka_uvcured_acrylate_OTR.txt`(freepatentsonline 전문)를
먼저 발견해 이번 값을 찾았고, 이후 USPTO 공식 PDF 를 직접 받아 대조했다.
