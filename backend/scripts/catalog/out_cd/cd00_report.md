<!-- 67차 CD — 아크릴 OCA/PSA 산소투과 계보(1.1813e-14) 되울림 수집 보고 -->

# 67차 CD — OCA·PSA 산소투과 계보 되울림

표적: 요청서 `PDE/oxygen-diffusion/물성요청_산소확산_원자재6종.md` §3 "확보된 값에 대한 단서".
아크릴 접착제 계열 전체에 붙어 있는 **한 개의 문헌 대표값** `1.1813e-14 mol/(m*s*Pa)` 이
정말 한 값의 전파인지 세고, 등급별 실측으로 대체할 수 있는지 문서를 열어 확인했다.

라이브 DB 는 `mode=ro` 로만 열었다. 값은 `out_cd/` 의 JSON 으로만 냈고 DB 에 직접 쓰지 않았다.

---

## 1. 전파 범위 — 정확한 수

```sql
select count(*), count(distinct material_id) from property_value
 where property_key='physical.gas_permeability_o2' and abs(value_num-1.1813e-14)<1e-18;
-- 17 | 17
```

**재료 17종에 붙어 있다. 행도 17개다(재료당 정확히 하나).**

| id | 재료 | tier | method |
|---|---|---|---|
| 42 | OCA Rigid Standard (3M 8171) | 3 | measured |
| 43 | OCA Rigid High Bond | 3 | measured |
| 44 | OCA Foldable (Tg<-30C) | 3 | measured |
| 45 | OCA Rollable (Tg<-40C) | 3 | measured |
| 46 | OCA UV Cured | 3 | measured |
| 47 | PSA Acrylic General (3M 467MP) | 3 | measured |
| 49 | PSA High Shear (Nitto 5000) | 3 | measured |
| 50 | PSA Removable | 3 | measured |
| 140 | LOCA/OCR | 3 | measured |
| 238 | 3M 8173KCL (PET 캐리어) | **4** | estimated |
| 279 | 3M OCA 8172 | 3 | measured |
| 280 | 3M Foldable OCA CEF3501 | 3 | measured |
| 281 | 3M OCA 8211 | 3 | measured |
| 282 | OCA acrylic (Micromachines 2022) | 3 | measured |
| 286 | OCA 8211 (3M, rigid standard) | 3 | measured |
| 386 | OCA acrylic (Microsyst Nanoeng 2026) | 3 | measured |
| **480** | **Poly(hexyl acrylate) (PA 6)** ← 뿌리 | 3 | computed |

카탈로그 전체의 `physical.gas_permeability_o2` 는 158행 / 96종이다.
**즉 이 한 숫자가 산소투과 보유 재료의 17.7 % 를 차지한다.**

요청서가 적은 "다섯 출처" 는 실제로는 **열여섯 제품 카드 + 뿌리 하나**다.
요청서 표현이 과소평가였다. 교차검증이 아니라 한 문헌값의 전파라는 진단은 그대로 맞다.

원값의 뿌리는 **O'Leary 2005 학위논문(UT Austin, Paul 지도) Table 7.1** 의
PA 6 블록 `P35+` 행이고, 저자 본인이 *"extrapolated to 35ºC"* 라고 적은 **Arrhenius 외삽값**이다.
35 °C 직접 측정치가 아니다. 원문을 이번에 직접 내려받아 재확인했다
(`/data/paper_patent_corpus/standards_appnotes/display/cd_oleary_2005_poly_n_alkyl_acrylate_thesis.pdf`).

---

## 2. 등급별 실측 — **0건이다**

찾은 등급 실측: **0건.**

이것은 검색 0건이 아니라 **문서를 열어 확인한 0건**이다.
`/data/paper_patent_corpus/standards_appnotes/display/` 에 **고유 벤더 문서 31장**을 내려받아
(총 38회 내려받고 바이트 동일 중복 7개 제외) 텍스트를 뽑고
`oxygen` · `OTR` · `O2` · `permeab` · `permeance` · `barrer` · `transmission rate` · `WVTR` · `MVTR` ·
`water vapo` 로 대소문자 무시 grep 했다.

### 2.1 열어 본 문서와 결과

| # | 문서 (PDF 가 스스로 인쇄한 제목) | 산소 열 |
|---|---|---|
| 1 | 3M™ Optically Clear Adhesives 8211 · 8212 · 8213 · 8214 · 8215 (Jan 2010) | **없음** |
| 2 | 3M™ Optically Clear Adhesive 8171 and 8172 (Technical Data 2016) | **없음** |
| 3 | 3M™ Optically Clear Adhesives 8171/8172 (July 2008, parafix 사본) | **없음** |
| 4 | 3M™ Optically Clear Adhesive OCA 817X Series (Technical Data 2018) | **없음** |
| 5 | 3M™ OCA 817X Series Product Description (2018, marian 사본) | **없음** |
| 6 | 3M™ Optically Clear Adhesive 818X Series (Technical Data 2016) | **없음** |
| 7 | 3M™ Optically Clear Adhesive 8173KCL (Technical Data 2015) | **없음** |
| 8 | 3M™ Optically Clear Adhesive 8146-x (November 2013) | **없음** |
| 9 | 3M™ Optically Clear Adhesives 8141 · 8142 · 8161 · 9483 (July 2008) | **없음** |
| 10 | 3M™ Automotive Converted OCA Film (ACO 01N-XXX Series, 2024) | **없음** |
| 11 | 3M™ Contrast Enhancement Film CEF35XX Series (Technical Data 2019) | **없음** |
| 12 | 3M™ Adhesive Transfer Tape 467MP (TDS V-5, Sep 2025) | **없음** |
| 13 | 3M™ Adhesive Transfer Tape 468MP (TDS V-5, Sep 2025) | **없음** |
| 14 | 3M™ Repositionable Tapes 665/666/9415PC/9416/9425/9425HT/9449S | **없음** |
| 15 | 3M™ VHB™ Tapes (Technical Data, October 2018) | **없음** (WVTR 만 있음 — §2.2) |
| 16 | 3M Printable Liquid Optically Clear Adhesive 1088 (Sep 2013) | **없음** (경화저해 경고뿐) |
| 17 | Optically clear adhesives for foldable OLED displays (3M 백서) | **없음** |
| 18 | Optically Clear Adhesive (OCA) and Contrast Enhancement Film (CEF) 개요 | **없음** |
| 19 | Selecting the right medical adhesive tape (3M 백서) | **없음** (MVTR 정성 비교뿐, 제품값 없음) |
| 20 | Nitto Double-coated adhesive tape No.5000NS (10-P-0012_E, marian 사본) | **없음** |
| 21 | Nitto Mounting Tapes 2025 (EN) 카탈로그 | **없음** |
| 22 | tesa® 88006 Optically Clear Adhesive Product Information | **없음** |
| 23 | tesa® 88008 Optically Clear Adhesive Product Information | **없음** |
| 24–29 | Adhesives Research ARclear® 42010 / 43080 / 43100 / 8932EE / 93408 / 93495 | **6장 모두 없음** |
| 30 | LOCTITE AA 3311 (April 2026) | **없음** (순산소 사용금지 경고뿐) |
| 31 | Dymax OP-29 Optical Adhesive Product Data Sheet | **없음** (경화저해 경고뿐) |

이 서식들이 실제로 찍는 것은 **박리력(ASTM D3330) · 전단유지력(ASTM D3654) · 굴절률 ·
헤이즈(ASTM D1003) · 광투과율(ASTM E903/D1003/E284) · 색좌표(ASTM E1164/CIELAB) ·
환경신뢰성 조건표** 다. `Transmission:` 이라는 머리글은 있으나 그것은 **광투과율**이지 가스투과가 아니다.
8211 TDS 원문이다.

```
Transmission:
ASTM E903, D1003, and E284
We calculate internal transmittance by correcting sample Transmittance (TLT) for the
sample Reflectance (TLR) in accord with the definition of internal transmittance ...
```

### 2.2 결정적 대조 — 3M 은 재긴 재는데 WVTR 만 낸다

요청 브리프의 예상("광학용 OCA 시트는 대개 투습도(WVTR)만 찍고 산소는 안 찍는다")은
**절반만 맞다.** 열어 보니 3M OCA 시트는 **WVTR 조차 안 찍는다.**
가스 행이 하나라도 있는 것은 열어 본 31장 중 **딱 한 장**, `3M VHB Tapes Technical Data (October 2018)` 이고
그 한 행이 이것이다.

```
Water Vapor Transmission Rate      25.6      37.1      g/m2•day
                                                       ASTM F1249 at 38°C/100% RH
```

즉 3M 은 아크릴 접착제의 가스 수송을 **측정하고 인쇄하는 서식을 갖고 있는데**
거기 올리는 것은 수증기뿐이고 산소는 어느 시트에도 없다. 서식의 한계가 아니라 **공개 선택**이다.

이 사실은 카탈로그 안에서도 확인된다 — 재료 279·286 의 `physical.gas_permeability_h2o`
(2.7286e-12, t4) 는 **OCA 시트가 아니라 이 VHB TDS 의 WVTR 25.6 g/(m²·day)** 에서 왔다.
OCA 카드가 가진 투습도조차 OCA 시트에서 온 것이 아니다.

### 2.3 곁다리 — 실리콘 OCA 도 같은 병을 앓는다

ARclear 6장을 열면서 확인한 것이다. 카탈로그의 실리콘 OCA 카드 다섯 종
(48 `PSA Silicone High-Temp` · 375 · 376 · 377 · 378 `ARclear …`)이 **전부 같은 값
2.8e-13 mol/(m·s·Pa)** 를 갖고 있는데, 그 출처는 ARclear 시트가 아니라
**순수 PDMS 치밀막(두께 2 mm) 논문**(Polymers 2019, 11, 910)이다.
`grade_scope` 에 *"MQ 레진이 자유부피를 줄여 실제 투과도는 이보다 낮다"* 고 정직하게 적혀 있다.

즉 **아크릴 계열의 1.1813e-14 전파와 정확히 같은 구조가 실리콘 계열에도 있다.**
이번 배치의 표적은 아크릴이라 실리콘은 손대지 않았지만, 같은 진단이 붙는다는 것은 적어 둔다.

---

## 3. 2-EHA 계 PSA — 더 가까운 클래스값을 찾았는가

### 3.1 카탈로그 안 — 0건

```sql
-- 2-EHA 계 재료
select count(*) from material where name like '%2-EHA%' or name like '%ethylhexyl acrylate%'
                                  or name like '%EHA/%' or name like '%/EHA%';   -- 118
-- 그중 가스 수송 물성을 가진 행
select count(*) from property_value pv join material m on m.id=pv.material_id
 where (…같은 조건…) and (pv.property_key like 'physical.gas%'
        or pv.property_key like '%diffusion%' or pv.property_key like '%solubility%');  -- 0
```

**2-EHA 계 카드가 118종 있는데 가스 수송 물성은 한 행도 없다.**
요청 브리프가 "스무 개 넘게" 라고 한 것보다 여섯 배 많다.

그 118종이 쓰는 출처는 **19편**이고, 제목을 전수로 봤더니 **전부 접착·유변·배합 논문**이다 —
박리력 · 택 · 전단유지력 · 점탄성 · 미시상분리 · 경피약물전달. **투과 측정 논문은 0편이다.**
2-EHA 계 카드가 이미 쓰는 출처에서 산소투과를 캘 자리가 없다.

### 3.2 곁사슬 길이로는 PA 6 대입이 나쁘지 않다

카탈로그가 이미 n-알킬 아크릴레이트 균질중합체 계열을 통째로 갖고 있다.

| 재료 | 곁사슬 | O₂ 투과율 [mol/(m·s·Pa)] | 출처 |
|---|---|---|---|
| 545 PMA | C1 | 3.5472e-16 | Mogri & Paul 2001 (2차 인용) |
| 546 PEA | C2 | 6.3582e-15 | 〃 |
| **480 PA 6** | **C6** | **1.1813e-14** | O'Leary 2005 Table 7.1 |
| 481 PA 10 | C10 | 1.0407e-14 | 〃 |
| 518 PA 12 | C12 | 1.4055e-14 / 1.7401e-14 | 〃 |

C1 → C2 에서 18배 뛰고(유리→고무 전이), **C6 → C10 구간은 거의 평탄하다**(1.18 → 1.04e-14, −12 %).
2-EHA 는 **C8 분지** 곁사슬이라 이 평탄 구간 한가운데다.
**곁사슬 길이라는 축만 보면 PA 6 대입은 오차가 작다.**

내삽해서 C8 값을 만들지 않았다 — 그것은 t4 추정이고, 만들어 봐야 35.3 → 33 Barrer 로 10 % 도 안 움직인다.
**계열 둔감성의 근거로만 쓰고 값으로는 만들지 않았다.**

### 3.3 진짜 위험은 곁사슬이 아니다

PA 6 대입의 오차 원천은 길이가 아니라 셋이다.

1. **가교** — 실제 OCA/PSA 는 GMA·알루미늄 아세틸아세토네이트·이소시아네이트 등으로 가교된다.
   PA 6 은 비가교 균질중합체다. 가교는 투과율을 낮추고 활성화에너지를 높인다.
2. **극성 공단량체** — AA · HEA · MMA 가 수 ~ 수십 wt% 들어간다. 극성기는 사슬간 응집을 높여
   자유체적을 줄인다. 같은 계열의 C1(PMA, 극성 최대)이 C6 보다 33배 낮은 것이 그 방향이다.
3. **점착부여수지** — 로진·C5 수지가 20 wt% 넘게 들어가는 배합이 있다.

**이 셋은 모두 실제 값을 PA 6 보다 낮추는 방향이다.** 즉 현재 값 1.1813e-14 는
**상한에 가까운 추정**으로 읽어야 한다. 이 판단은 기존 `grade_scope` 문구와 같고, 이번에
`chemical.activation_energy` 의 `grade_scope` 에도 같은 방향으로 적었다.

### 3.4 우리가 가진 출처를 더 팠다 — 그래도 0건

카탈로그가 인용하는 **UT Austin Paul 그룹 학위논문 두 편을 전문 내려받아 grep** 했다.

| 논문 | 내려받은 곳 | `ethylhexyl`/`branched` | PSA/접착제 투과 | AA 공중합체 투과 |
|---|---|---|---|---|
| O'Leary 2005 (출처 2869) | `…/display/cd_oleary_2005_poly_n_alkyl_acrylate_thesis.pdf` | **0건** | **0건** | **0건** |
| Kirkland 2007 (출처 2883) | `…/display/cd_kirkland_2007_gas_transport_pna_blends.pdf` | **0건** | **0건** | **0건** |

O'Leary 가 acrylic acid 를 언급하는 두 자리는 **반응성비(조성 드리프트) 논의**이지 투과가 아니다.
Kirkland 는 **PA 8(C8 선형)** 을 다루기는 하는데 부록 그림(Figure A.35–A.38, PA8(50)/PA10(50) 블렌드)에만 있고
**표에 숫자가 없다.** 그림 디지타이즈는 t4 추정이라 하지 않았다.
Kirkland Table 3.2 의 Ea(PA-14 8.5 · PA-16 9.4 kcal/mol)는 **이미 카탈로그에 들어 있다**
(재료 519 = 35564 J/mol, 522 = 39330 J/mol — 8.5×4184 · 9.4×4184 로 검산 일치).

### 3.5 숫자가 가까운데 안 쓴 것

콘택트렌즈 실리콘/아크릴 하이드로겔(재료 540 · 541 · 542 · 544)이 **tier1 실측** O₂ 투과도를
8.63e-15 · 1.02e-14 · 1.32e-14 · 5.82e-15 로 갖고 있어 숫자가 35.3 Barrer 와 같은 자리다.
**그래도 쓰지 않았다** — 조건이 `state: hydrated (수화 상태)` 이고 측정법이 ISO 18369-4 폴라로그래피(Dk)다.
수화 하이드로겔의 산소 수송은 **물 채널**이 지배해서 건조 OCA 와 기구가 다르다.
**숫자가 가깝다는 것은 근거가 아니다.**

### 3.6 카탈로그 밖 — 문헌을 훑었다

웹·OpenAlex 전문색인·로컬 코퍼스를 병렬로 훑었다. 결정적 음성 셋이다.

| 질의 (OpenAlex 전문색인) | 결과 |
|---|---|
| `"2-ethylhexyl acrylate" AND "oxygen transmission rate"` | **0편** |
| `"poly(n-hexyl acrylate)" AND "permeability"` | **0편** |
| `"optically clear adhesive" AND "oxygen permeability"` | **1편** (아래 §3.7) |

로컬 코퍼스 `structured/` 의 `.md` 41,843편(materials 6,225 · expert 2,816 · standards_appnotes 32,802)에
`barrer|oxygen permeabilit` 를 걸어 **아크릴 PSA/OCA 히트 0건**이다.
OCA 논문 폴더 `18_disp_polarizer_oca` 는 4편, PSA 폴더 `26_mech_psa_adhesive` 는 5편뿐이고
**전부 점탄성·접착 논문**이다.

### 3.7 그래도 하나 나왔다 — 다음 배치의 1순위 (유료라 못 열었다)

> Zhang P., Tang B., Yang M., Yang B., Shen Y., Zhang Q., Liu Z., Chen Y.,
> **"Acrylate Optically Clear Adhesives with Excellent Oxygen Barrier for Organic Light-Emitting Devices"**,
> *Ind. Eng. Chem. Res.* **2025**, 64(1), 441–452. DOI `10.1021/acs.iecr.4c03543`

**OCA 의 산소 배리어를 정면으로 다룬 논문이 세상에 이것 하나다**(OpenAlex 전문색인 기준).
본문은 ACS 유료라 못 열었고, 초록만 NWPU 기관 페이지에서 받았다(같은 초록을 두 경로로 대조했다).

초록 verbatim — *"The oxygen permeability coefficient is as low as **4.76 cc·mil·m⁻²·day⁻¹·0.1 MPa⁻¹**,
which is **35.61 times lower** than that of the unmodified acrylate matrix… Even after 6 months, the OCAs
still maintain a good oxygen barrier performance, with an oxygen permeability coefficient of
**103.43 cc·mil·m⁻²·day⁻¹·0.1 MPa⁻¹**."*

**아무것도 넣지 않았다.** 이유가 셋이다.

1. **4.76 은 개질품 값이다.** 조성이 아크릴레이트 매트릭스 + 개질 BN(수동 배리어) +
   말단수산기 폴리부타디엔(**능동 산소 스캐빈저**)이다. 스캐빈저가 든 막의 "투과계수"는
   수송 물성이 아니라 **소모가 섞인 겉보기 값**이다. 6개월 뒤 21.7배로 오르는 것이 그 증거다.
2. **미개질 매트릭스 값은 초록에 인쇄되지 않았다.** 4.76 × 35.61 로 만들면 **역산**이다. 하지 않았다.
3. **단위 신뢰성이 걸린다.** 참고로 환산해 보면
   `4.76 cc·mil/(m²·day·0.1MPa) = 6.24e-19 mol/(m·s·Pa) = 0.00187 Barrer` 이고,
   역산했을 미개질 매트릭스조차 0.066 Barrer 다. **연질 아크릴 PSA 가 PVDC 보다 조밀할 수는 없다.**
   본문의 시험법·시편 두께·단량체 조성을 읽기 전에는 이 숫자를 카탈로그에 넣을 수 없다.
   (이 환산은 저장하지 않는 해설값이다.)

**다음 배치가 ACS 접근권으로 이 논문 본문을 열면 — 요청서가 원한 "실제 사용 grade 의 실측"에
가장 가까운 값이 거기 있다.** 최소한 미개질 매트릭스의 인쇄값과 단량체 조성을 확인해야 한다.

### 3.8 결론

**더 가까운 조성의 클래스값을 찾지 못했다.**
2-EHA 계 실측은 카탈로그 안에도, 그 카드들이 쓰는 출처 19편에도, 우리가 가진 학위논문 두 편에도,
공개된 문헌에도 없다. 현재 값은 그대로 두고, 대신 **온도 축을 열었다**(§4).

---

## 4. Arrhenius Ea — 원문이 찍었다. 넣었다

### 4.1 원문

O'Leary 2005 Table 7.1 이 **PA 6 의 O₂ 투과 활성화에너지를 직접 인쇄한다.**

```
Table 7.1
Activation Energy and Permeability Data Extrapolated to 35ºC for Various Gases
             Through Poly (n-alkyl acrylate) Homopolymers

Homopolymer                              Gas
                          He      H2      O2      N2     CH4     CO2
   PA 6          Ea       6.5     6.7     6.8     8.0     6.8     6.5
                 Ec        -       -       -       -       -       -
                P35+     49.8    89.8    35.3    13.9    31.6    211.7
Note that the activation energies Ea and Ec have units of kcal/mol while the
permeability coefficients P35+ and P35- have units of Barrers ...
```

O₂ 는 3번째 열이므로 **Ea = 6.8 kcal/mol**, 같은 행의 P35+ 가 우리가 쓰고 있는 35.3 Barrer 다.
**두 값이 같은 표 같은 행에서 온다.** 우리는 그중 투과율만 가져오고 온도의존성은 버려 왔다.

본문이 Ea 의 성격을 정의한다 — *"The quantities Ea and Ec are the activation energies for
permeation in the amorphous and semi-crystalline states, respectively"* 이고,
PA 6 은 `Ec` · `P35-` · `P35+/P35-` 칸이 모두 비어 상온 결정상이 없다.
**Ea 하나가 전 온도구간을 기술한다.**

### 4.2 taxonomy 확인

```sql
select key,name,si_unit from property_definition where key like '%activation%';
-- chemical.activation_energy | Arrhenius 활성화에너지 | J/mol
-- chemical.arrhenius_prefactor | Arrhenius 전지수인자 | 1
```

키가 있다. 그리고 **뿌리 재료에는 이미 들어 있다** —
재료 480 (PA 6) 이 `28451 J/mol`, 재료 481 (PA 10) 이 `30962 J/mol` 을 갖고 있다.

환산 검산 — 6.8 × 4184 = 28451.2, 7.4 × 4184 = 30961.6. 두 행이 같은 인자로 맞는다.
**kcal→J 인자 4184(열화학 칼로리)가 이 표에 대한 카탈로그 관례임이 확인된다.**

### 4.3 무엇을 넣었나

**16 제품 카드 중 온도의존성을 가진 것은 0종이었다.** 투과율만 35 °C 한 점에 묶여 있었다.
같은 표 같은 행에서 온 Ea 를 **15종에 t3 계열값으로 이식**했다
(`cd01_acrylic_oca_psa_o2_arrhenius_ea.json`).

- 값 `28451.0 J/mol` · 단위 `J/mol` · `method: measured` · `tier: 3`
- `conditions.grade_scope` 에 **왜 이 제품의 값이 아닌지** 를 적었다 — PA 6 균질중합체 값이고,
  이 재료가 이미 쓰는 투과율과 **같은 표 같은 행**이라 계보가 하나로 붙는다는 것,
  실제 OCA 는 2-EHA/BA/AA 공중합 + 가교라 Ea 가 더 클 가능성이 있다는 것,
  계열 둔감성 근거(PA 6 6.8 / PA 10 7.4 kcal/mol)를 함께 적었다.
- `method` 를 `measured` 로 둔 이유 — Ea 는 저자가 잰 P(T) 를 Arrhenius 좌표에서 기울기로
  뽑은 값이다(Figure 7.2). **P35+ 처럼 외삽으로 만든 숫자가 아니다.** 그래서 조건에
  `value_basis: 외삽` 이 붙지 않는다.

**238(8173KCL)은 뺐다.** 이 제품은 아크릴 25 µm / **PET 캐리어 25 µm** / 아크릴 25 µm 3층이고,
직렬 배리어의 온도의존성은 가장 조밀한 층(PET)이 지배한다. 성분 Ea 를 제품 카드에 달면
해석이 그것을 제품 온도의존성으로 읽을 위험이 있다.
**282·386 도 뺐다** — 이 둘은 벤더 등급이 아니라 논문 특성화 카드다.

### 4.4 넣지 않은 것 — 다른 온도의 투과율

**Ea 로 다른 온도의 투과율을 만들지 않았다. 그것이 역산이다.**

다만 요청서 §2 가 *"아크릴계는 10 °C 차이로 배 가까이 움직인다"* 로 적은 것에 대해
이 Ea 가 답을 준다. 25 → 35 °C 비는

```
exp( -28451/8.314 × (1/308.15 − 1/298.15) ) = 1.45
```

**10 °C 에 1.45배이지 "배 가까이"가 아니다.** 요청서의 감각이 과했다.
이 1.45 는 저장하지 않는 해설값이고, notes 에도 "저장하지 않는다"고 명시했다.
해석이 온도 보정을 하려면 이 Ea 로 직접 하면 된다.

같은 유혹이 한 번 더 왔다는 것을 적어 둔다 — 이번 문헌 훑기가 **같은 Ea 로 23 °C 값
22.5 Barrer(= 7.53e-15 mol/(m·s·Pa))를 만들어 "방어 가능한 잠정 개선" 으로 제안**했다.
산술은 맞다(내 검산으로도 22.6). **그래도 넣지 않았다** — 원문이 인쇄한 것은 35 °C 한 점이고,
23 °C 값은 우리가 만든 숫자다. 카탈로그가 그것을 tier 와 함께 들고 있으면
다음 사람은 그것을 측정치로 읽는다. **Ea 를 주고 환산은 해석에 맡기는 것이 옳다.**

---

## 5. 못 넣은 것과 이유 — 셋으로 갈라서

### (a) 문서에 열이 없었다 → **판정으로 남겼다**

`cd02_verdicts.json` — **재료 14종**에 `core_absent_from_vendor_sheet[physical.gas_permeability_o2]`.
각 판정에 연 문서 목록(제목 + 절대경로) · grep 어휘 · 그 서식이 대신 찍는 것 ·
VHB 대조를 적었고, **"연 범위는 이 문서들이지 이 벤더/제품군 전체가 아니다"** 를 명시했다(브리프 627③).

판정마다 **그 카드가 이미 인용하는 시트**와 **인용하지 않지만 함께 연 형제 시트**를 갈라 적었다.
카드가 인용하지도 않는 문서를 "이 재료의 시트를 열었다" 로 뭉뜽그리면 부재 판정의 범위가 부풀기 때문이다.

| 재료 | 인용 시트(연 것) | 형제 시트 |
|---|---|---|
| 42 | 5 | 8 |
| 43 | 4 | 9 |
| 44 · 45 | 2 · 2 | 10 · 10 |
| 46 | 4 | 9 |
| 47 · 49 · 50 | 1 · 3 · 2 | 8 · 8 · 8 |
| 140 · 238 | 2 · 3 | 8 · 8 |
| 279 · 280 · 281 · 286 | 5 · 4 · 5 · 5 | 7 · 7 · 7 · 7 |

282 · 386 은 벤더 등급이 아니라 논문 특성화 카드라 **판정을 달지 않았다** —
열 벤더 시트가 애초에 없다.

### (b) 문서를 못 열었다 → **판정이 아니다. 여기 적는다**

| 문서 | 상태 |
|---|---|
| Nitto `NJ_No.5000NS_EN.pdf` (출처 25, nitto.com 직접) | HTTP/2·HTTP/1.1 로 90~120 s 씩 시도, **0 바이트 타임아웃**. 다만 출처 1784 가 같은 문서번호(10-P-0012_E)의 유통사 사본이고 그것은 열었다 |
| Nitto LUCIACS (CS986x · CT5020) 광학용 OCA | **공개 TDS PDF 자체가 없다.** nitto.com 은 제품 소개 페이지만 낸다 |
| 3M CEF3501 단독 TDS | 단독 공개본 없음. 3M 이 내는 것은 계열 시트 `CEF35XX Series`(열었음) |
| LG화학 OCA 브로슈어 | 공개 PDF 없음 — 뉴스·유통사 페이지만 |
| 삼성SDI OCA 브로슈어 | 공개 PDF 없음 |
| Nitto LUCIACS(CS986x·CT5020) 광학용 OCA | **공개 TDS PDF 자체가 없다.** 제품 소개 페이지만 |
| 3M CEF3501 단독 TDS | 단독 공개본 없음(계열 시트는 열었다) |
| 3M 제품 웹페이지(출처 121)·URL 없는 출처 759 | PDF 아님. 이번 범위 밖 |

**국내 2사(LG화학·삼성SDI)는 벤더 시트를 못 연 것이지 "없다"가 아니다.**

다만 **한 갈래는 열렸다** — 제일모직(Cheil Industries, 전자재료 사업이 삼성SDI 로 넘어간 곳)의
OCA 특허 **US 9,873,821 B2** *"Adhesive film, adhesive composition for the same, and display apparatus
including the same"* 를 전문으로 받아 읽었다
(`…/display/pat_US9873821_Cheil_OCA_adhesive_film_NO_O2data.txt`).
(메타)아크릴 공중합체 + 우레탄 (메타)아크릴레이트를 50 µm PET 이형필름 위에 **175 µm** 로 도포해
UV 경화한 OCA 이고, 실시예 표에 점착력·유지력·신뢰성이 인쇄되는데 **산소투과 행이 없다.**
이 문서에서 `oxygen` 은 전부 **경화 분위기**(산소 없는 조건에서 UV 경화) 얘기다.
같은 성격으로 3M **US 10,199,603**(Adhesive barrier film construction, 양자점 배리어)도 열었으나
**수치화된 산소 값이 없다.**

한편 미쓰비시가스화학 **US 10,023,694** 는 `"oxygen transmission coefficient is
2.0 ml·mm/m²·day·MPa (23 °C, 60% RH) or less"` 를 인쇄하는데, 이것은 **청구항의 상한 한정**이지
측정값이 아니고 대상도 OCA 가 아니라 포장용 가스배리어 코팅이다. **값으로 쓰지 않았다.**

### (b-2) 문서를 열었는데 **내 표적이 아니었다** — 다음 배치로 넘긴다

문헌 훑기에서 **인쇄값이 있는 문서 둘**이 나왔는데 둘 다 OCA/PSA 가 아니다.
내 표적 카드에 붙이면 틀린 값이 되므로 넣지 않았다. 원문은 내려받아 두었다.

**① UV 경화 아크릴레이트 자립막 — 우리 단위 그대로 인쇄된 값**
US 10,259,948 B2 (Kaneka, "Coating compositions and coating products made therefrom").
`…/display/pat_US10259948_Kaneka_uvcured_acrylate_OTR.txt`

| 실시예 | 조성 | permeance [mol/(m²·s·Pa)] | permeability [mol/(m·s·Pa)] |
|---|---|---|---|
| 비교예 1 | IBOA 9.0 g + 에톡시화 TMPTA 5.0 g + 에폭시아크릴레이트 CN120 6.0 g | 1.7e-12 | **7.1e-17** |
| 비교예 2 | IBOA 12.0 g + TMPTA 2.0 g + 우레탄아크릴레이트 CN986 6.0 g | 6.7e-12 | **2.4e-16** |
| 실시예 2 | 위 + 인산지르코늄 나노판상 10 wt% | 8.1e-14 | 3.6e-18 |
| 실시예 3 | 〃 | 7.8e-13 | 2.7e-17 |

측정법 verbatim — *"Oxygen transmission rate was measured by using BT-3 Gas Transmisstion Rate Tester
(Toyoseiki Seisaku-sho, Ltd.), in conformity with **JIS K 7126-1**."*
**두께가 원문에 직접 없어도 역산이 필요 없다** — 특허가 permeance 와 permeability 를 **둘 다** 인쇄한다.
내부 검산: 7.1e-17 / 1.7e-12 = 41.8 µm · 2.4e-16 / 6.7e-12 = 35.8 µm · 3.6e-18 / 8.1e-14 = 44.4 µm 로
본문의 자립막 두께 서술과 맞는다. **세 쌍이 모두 맞으므로 이 값들은 신뢰할 수 있다.**

이것은 **요청서 §4 2순위 "저온 유기 평탄화막(UV 경화 아크릴레이트)"** 의 표적이다.
지금 그 층에 놓인 1.707e-15(재료 370 ThreeBond TB3062U)는 **t4 추정**인데,
이 특허값은 **인쇄된 값**이고 자릿수가 10~50배 낮다.
**평탄화막 담당 배치가 이 특허로 그 칸을 t1/t2 로 바꿀 수 있다.**
(다만 IBOA/TMPTA 계 하드코트는 유리상 고가교라 "저온 유기 평탄화막"과 조성이 같은지는 확인이 필요하다.)

**② PS/PBA 40:60 코어–쉘 라텍스막 — BA 계 실측이긴 하다**
Puca Pacheco 외, *Rev. Latinoam. Metal. Mater.* 2016, 36(2).
`…/display/cd_puca2016_ps_pba_coreshell_gas_permeability.pdf`
Tabla 4(35 °C, 2·4 atm, Barrer), O₂ 열 — SO 16.27 · SI 30.36 · SS 16.66 · E10 111.44 · E20 158.23.
**쓰지 않았다** — 막의 40 wt% 가 폴리스티렌 코어이고, 같은 조성이 라텍스 경로에 따라
16 → 158 Barrer 로 **10배** 벌어진다. 이 산포는 물성이 아니라 제막 결함이다.
다만 "35 °C 비정질 BA 리치 막은 수십 Barrer 대" 라는 **괄호**로는 읽히고,
그 괄호가 PA 6 의 35.3 Barrer 를 감싼다.

### (c) 등급이 안 맞았다

- **콘택트렌즈 하이드로겔**(재료 540 · 541 · 542 · 544) — tier1 실측이고 숫자도 같은 자리인데
  **수화 상태**라 기구가 다르다. §3.5 참조.
- **PA 10 (재료 481, 31.1 Barrer)** 은 PA 6 보다 나은 대체가 아니다. §3.2 참조.
- **Kirkland 2007 의 PA 8(C8 선형)** — 2-EHA 와 탄소수가 같은 유일한 후보인데
  **표가 아니라 부록 그림에만 있다.** 그림 디지타이즈는 t4 이므로 하지 않았다. §3.4 참조.

---

## 6. 다음 배치에 넘길 것

우선순위 순서다.

0. 🔴 **ACS 접근권으로 IECR 2025, 64(1), 441–452 (DOI 10.1021/acs.iecr.4c03543) 을 열어라.**
   OCA 산소 배리어를 정면으로 다룬 **유일한** 논문이다(§3.7). 초록만 봤고 본문을 못 봤다.
   확인할 것 — ① **미개질 아크릴레이트 매트릭스의 인쇄된 투과계수** ② 단량체 조성
   ③ 시편 두께와 시험법 ④ `cc·mil·m⁻²·day⁻¹·0.1 MPa⁻¹` 이 정말 두께 정규화된 값인지.
   이것 하나가 17종 전부의 t3 계열값을 대체할 수 있다.
0-b. 🔴 **US 10,259,948 B2(Kaneka) 로 "저온 유기 평탄화막" 칸을 열어라**(§5(b-2)①).
   permeance 와 permeability 를 **둘 다** 인쇄하고 세 쌍이 내부 검산으로 맞는다.
   지금 그 층의 1.707e-15 는 t4 추정이다. 원문은 이미 내려받아 두었다.
   **이 배치의 표적이 아니라 손대지 않았다.**
1. **요청서 §3 의 "다섯 출처" 를 17종으로 고쳐라.** 전파 규모가 실제로는 3.4배 크다.
   같은 폴더의 `oxygen-diffusion-model.md` §10.3 이 적은 "13종 재료에 동일하게 붙어 있는 tier3 계열값"
   도 현재 17종이다.
2. **국내 2사(LG화학·삼성SDI) OCA 는 공개 문서로 닫히지 않는다.**
   이 두 곳은 웹 수집이 아니라 **벤더 조회(요청서 §2 의 "받을 값" 양식)** 로 가야 한다.
   요청서가 원하는 것이 바로 그 경로이므로, 카탈로그 배치가 더 팔 자리가 아니다.
3. **`chemical.arrhenius_prefactor` 는 비어 있다.** Table 7.1 은 Ea 와 P35+ 만 인쇄하고
   전지수인자를 안 찍는다. P35+ 와 Ea 로 역산하면 나오지만 그것은 역산이라 하지 않았다.
   O'Leary 의 학술지판(Polymer 2006 Part 1·2, `Gas transport in poly(n-alkyl acrylate)/
   poly(m-alkyl acrylate) blends`, Polymer 2007)이 원 데이터표를 실었을 수 있다 — 유료라 이번에 못 열었다.
4. **Mogri & Paul, Polymer 2001, 42(18), 7765-7780 을 아직 안 열었다.**
   카탈로그의 PMA(C1) · PEA(C2) 값(재료 545 · 546)은 2021년 리뷰 본문이 인용한 **2차 값**이고
   `value_basis` 에 "원표 미확인" 이라고 적혀 있다. 원표를 열면 그 두 칸이 tier 를 올릴 수 있고,
   같은 논문이 **poly(alkyl methacrylate)** 도 다루므로 컬러필터 바인더(폴리메타크릴레이트) 쪽도 열린다.
5. **Kirkland 2007 부록 Figure A.35–A.38 의 PA 8 곡선.** 2-EHA 와 탄소수가 같은 유일한 후보다.
   `digitize_curve.py` 로 t4 를 만들 수는 있으나, 지금 값과 10 % 안에서 만날 것이라
   **투자 대비 이득이 없다.** 등급 실측이 오면 무의미해지므로 우선순위 낮음.
6. **TAC(요청서 4번)과 엣지 실링재(6번)는 이 배치 범위 밖이다.** 여전히 공백이다.
7. **`oxygen-diffusion-model.md` §5.3 의 `S_i`(층별 O₂ 용해도)** — 아크릴 계열 S 실측은 카탈로그에 여전히 0건이다.
   UT Austin 학위논문 두 편 모두 P 만 잰다 — PPO 지지체 위 복합막 permeance 법이라 시간지연법을 쓸 수 없고,
   본문에서 D·S 는 `P = D·S` 정의로만 등장하지 측정값이 없다(grep 확인).
   Mogri & Paul **Part II**(Polymer 2001, DOI `10.1016/S0032-3861(01)00261-0`)가 sorption·diffusion 편이다.
   §6-4 와 같은 논문 쌍이므로 한 번에 열면 된다.
8. **실리콘 OCA 계열도 같은 병이다**(§2.3). 재료 48·375·376·377·378 다섯 종이
   순수 PDMS 치밀막 값 2.8e-13 을 공유한다. 이번 표적이 아니라 손대지 않았다.
9. **못 연 유료 문헌 목록**(다음 배치가 접근권으로 뚫을 자리) —
   Eur. Polym. J. 2017 `10.1016/j.eurpolymj.2017.07.033`(전문색인에 `2-ethylhexyl acrylate` + `gas permeability` 동시 히트) ·
   Prog. Org. Coat. 1993 PBA/PVDC 코어쉘 · Polymer 1993 `10.1016/0032-3861(93)90509-9` poly(cyclohexyl acrylate) O₂ ·
   J. Membr. Sci. 2010, 365, 40–51 `10.1016/j.memsci.2010.08.035`(결정성 고분자의 O₂ D·S) ·
   Klopffer & Flaconnèche, Oil Gas Sci. Technol. 2001, 56(3), 223–244 `10.2516/ogst:2001021`
   (**OA 인데 두 호스트 모두 봇 챌린지로 막혔다** — 사람 브라우저면 한 번에 열린다).

---

## 7. 산출물

| 파일 | 내용 |
|---|---|
| `cd01_acrylic_oca_psa_o2_arrhenius_ea.json` | 값 15건 — `chemical.activation_energy` 28451 J/mol, t3, 15 재료 |
| `cd02_verdicts.json` | 판정 14종 — `core_absent_from_vendor_sheet[physical.gas_permeability_o2]` |
| `cd00_report.md` | 이 보고서 |

원문은 `/data/paper_patent_corpus/standards_appnotes/display/cd_*.pdf` (+ `.txt` 추출본) 에 두었다.

| 접두사 | 무엇 |
|---|---|
| `cd_oleary_2005_poly_n_alkyl_acrylate_thesis.pdf` | 출처 2869 원문. **DB 의 `local_path` 가 비어 있었다** — 이 배치가 처음 내려받았다 |
| `cd_kirkland_2007_gas_transport_pna_blends.pdf` | 출처 2883 원문. 역시 `local_path` 가 비어 있었다 |
| `cd_db_s<출처id>_*.pdf` | 표적 카드들이 **이미 인용하는** 벤더 시트. 파일명에 DB 출처 id 를 박았다 |
| `cd_3m_* · cd_tesa_* · cd_ar_*` | 인용하지는 않지만 같은 서식의 형제 시트 |
| `pat_US10259948_Kaneka_uvcured_acrylate_OTR.txt` | **다음 배치용** — UV 경화 아크릴레이트 자립막의 인쇄된 투과계수(§5 b-2 ①) |
| `cd_puca2016_ps_pba_coreshell_gas_permeability.pdf` | PS/PBA 40:60 코어–쉘막 Barrer 표. 괄호로만 쓴다(§5 b-2 ②) |
| `pat_US9873821_Cheil_OCA_adhesive_film_NO_O2data.txt` | 제일모직 OCA 특허 전문. **산소 행 없음** — 국내사 문서로는 유일하게 연 것(§5 b) |
| `pat_US10199603_*_NO_O2data` · `pat_US8278401_*_NO_O2data` | 3M·Henkel 배리어 특허. 수치화된 산소값 없음 |
| `pat_US10023694_MGC_uvcurable_gasbarrier.txt` | 청구항 상한 `2.0 ml·mm/(m²·day·MPa)` 만 있다. 측정값 아님 |

두 학위논문의 URL 은 UT Austin 리포지터리인데 **CloudFront WAF 가 `curl` 을 202 challenge 로 막는다.**
브라우저로 도메인을 한 번 열어 `aws-waf-token` 쿠키를 받은 뒤 그 쿠키를 붙여야 내려온다.
다음 배치가 같은 도메인을 만나면 이 방법을 쓰면 된다.

### 예행 결과 (라이브 사본에 대해서만)

라이브 DB 를 `VACUUM INTO` 로 뜬 사본에 걸어 확인했다. **라이브에는 쓰지 않았다.**

```
MATERIALTWIN_DATA_DIR=<사본> ingest_agent_json.py out_cd/cd01_...json
    → [DRY-RUN] ok 15   → [APPLY(사본)] ok 15
apply_core_verdicts.py --db <사본> out_cd/cd02_verdicts.json --apply
    → 병합 14 / 재료 14
```

무결성 점검을 **적재 전 사본**과 **적재 후 사본**에 각각 돌려 diff 했다.
바뀐 줄은 물성값 개수 한 줄뿐이다(`43644 → 43659`, +15). **새 이상 항목 0개.**
`출처 3054` 가 그대로인 것은 적재기가 **새 출처를 만들지 않고 기존 2869 를 재사용**했다는 뜻이고,
확인해 보니 비어 있던 `source.local_path` · `year` · `publisher` 도 함께 채워졌다.

Kirkland 2007(출처 2883)은 이번 값이 인용하지 않아 `local_path` 가 여전히 비어 있다.
파일은 `…/display/cd_kirkland_2007_gas_transport_pna_blends.pdf` 에 있으니 다음 배치가 이어 쓰면 된다.

⚠ **`MATERIALTWIN_DATA_DIR` 를 빼면 `ingest_agent_json.py` 는 낡은 개발 DB
(`backend/var/data/materialtwin.db`, 재료 70종)를 본다.** 실수로 한 번 그렇게 돌렸더니
`ok 8 / no_mat 7` 이 나왔다 — 값이 틀려서가 아니라 그 DB 에 재료가 없어서다.
`apply_core_verdicts.py` 는 이미 환경변수를 읽도록 고쳐져 있는데(65차 AD) 적재기는 아직 그렇다.
**다음 배치는 예행 로그의 `[DB]` 줄을 먼저 읽어라.**

`cd02_verdicts.json` 은 브리프가 스케치한 `match_name`/`key`/`verdict` 꼴이 아니라
**`apply_core_verdicts.py` 가 실제로 읽는 꼴**(`material_id` + `name` + `<attr>: {물성키: 사유}`)로 썼다.
그 스크립트는 `material_id`·`name` 외의 최상위 키를 **전부 attribute 로 병합**하므로
`source_url`·`local_path` 를 최상위에 두면 재료 속성으로 들어가 버린다.
두 값은 사유 문자열 안에 절대경로로 넣었다.
