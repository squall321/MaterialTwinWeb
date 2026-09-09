<!-- 68차 DB 수집 배치 보고서 — 67차가 세운 신규 카드 4장의 코어7 빈칸 28칸 -->

# 68차 DB — 신규 카드 4장의 코어7

기준일 2026-09-09 · 표적 재료 2701 · 2704 · 2705 · 2708 의 코어7 빈칸 28칸
산출 `backend/scripts/catalog/out_db/` · **라이브 DB 는 읽기 전용으로만 열었고 `--apply` 는 돌리지 않았다.**

**한 줄 요약** — **28칸 중 26칸을 닫았다. 카드는 3장이 섰다**(밀도+영률+포아송비 완비).
그런데 닫은 방식이 정직하게 말하면 **거의 전부 클래스값**이다 — 이 네 층 자신을 잰 문서는 여전히 0 건이고,
67차가 프레임 실·사이드실에서 내린 결론("실링재 벤더도 실링재 특허도 산소를 재지 않는다")이
**코어7 에서도 그대로 성립한다: 그들은 역학·열 물성도 재지 않는다.**
그 대신 이번에 새로 연 문 세 개가 값을 냈다 — **Granta 클래스표 3종 · allnex/Sartomer 올리고머 벤더시트 2종 ·
BOE 특허의 비교열 1개**.

---

## 1. 카드별 성적

| 재료 id | 카드 | 이전 보유 | 이번에 닫은 코어7 | 남은 빈칸 | 카드가 섰나 |
|---|---|---:|---:|---:|---|
| **2701** | 프레임 실 (에폭시 아크릴레이트) | 3 | **7 / 7** | 0 | ✅ 섰다 |
| **2704** | 저온 유기 평탄화막 / CF 오버코트 | 1 | **7 / 7** | 0 | ✅ 섰다 |
| **2705** | TAC / CTA 광학필름 | 2 | **7 / 7** | 0 | ✅ 섰다 |
| **2708** | 모듈 사이드실링재 | 1 | **5 / 7** | 2 (포아송비 · CTE) | ❌ 포아송비가 없다 |

**카드가 선 것 3장 / 4장.** 2708 만 포아송비가 비어 서지 못했다(§4.1).

물성 행 **52 건 등록(전량 tier 3, tier 1 · tier 4 는 하나도 만들지 않았다)**, 출처 9 건.

| 파일 | 재료 | 행 | 출처 |
|---|---|---:|---|
| `db01_tac_core7.json` | 2705 | 14 | AZoM/Granta Cellulose Acetate · ACS Omega 8b01616 |
| `db02_overcoat_core7.json` | 2704 | 14 | BOE US11332634B2 TABLE 2 · AZoM/Granta PMMA |
| `db03_frame_sealant_core7.json` | 2701 | 17 | AZoM/Granta Epoxy · allnex RADCURE 가이드 · Sartomer CN120A75 TDS |
| `db04_side_seal_core7.json` | 2708 | 7 | LG디스플레이 US11099608B2 · matmake Butyl Rubber (IIR) |
| `db05_verdicts.json` | 4종 | 판정 6건 | 2708 의 빈칸 2건 + 카드 3장의 `core_doors_tried` |

검증 — `ingest_agent_json.py` dry-run **`ok 52`, 위반 0**. `apply_core_verdicts.py` dry-run **병합 4 / 재료 4**.
(경고 2건은 "이미 채굴된 출처"인데, 둘 다 **다른 재료**에 붙은 기존 행이라 정상이다.)

---

## 2. 디스크에 있던 문서 vs 새로 받은 문서

브리프가 "다시 받지 말고 디스크부터 전수로 훑어라"고 했다. 그렇게 했고, 결과를 먼저 적는다.

### 2.1 디스크 전수 조사 결과 — **특허 59건에서 코어7 은 4칸밖에 안 나왔다**

`/data/paper_patent_corpus/standards_appnotes/display/` 의 특허 텍스트 **59개 파일**(`*_fpo.txt` · `FPO_*.txt` ·
`pat_*.txt` · `*_OCR.txt`)을 `modulus` · `thermal expansion` · `specific heat` · `thermal conductivity` ·
`poisson` · `tensile strength` · `g/cm3` 패턴으로 전수 grep 하고, 히트가 난 것은 전부 문맥까지 폈다.

| 디스크 문서 | 코어7 을 냈나 | 무엇을 냈나 |
|---|---|---|
| **BOE US11332634B2** (스캔 PDF, 400 dpi 재OCR) | ✅ | **2704 밀도 1.2~1.3 g/cm3** — TABLE 2 의 'Existing Overcoat Layer Material' 열 |
| **LG디스플레이 US11099608B2** | ✅ | **2708 영률 0.14 GPa(제1 실) · 1.8 GPa(제2 실)** — 문단 267 |
| **ACS Omega 8b01616** (67차 CC 가 "산소 열 없음"으로 닫은 문서) | ✅ | **2705 영률 1.03 GPa · 인장강도 40.8 MPa** — Table 1 neat CTA |
| 삼성디스플레이 US10928662B2 | ✗ | TABLE 1 이 연신율·박리강도·전단접착강도 셋뿐 — **영률·인장강도·밀도 열이 없다** |
| 삼성SDI US10822449B2 | ✗ | TABLE 1 이 연필경도·투과율·헤이즈·유전율·내약품성·아웃가스뿐 |
| Kaneka US10259948B2 | ✗ | TABLE 1 은 부식, TABLE 2 는 ZrP 함량·투과율·헤이즈·산소투과 — 역학·열 열 없음 |
| LG디스플레이 US2025/0221249A1 | ✗ | CTE 를 **비로만** 인쇄한다(실링재의 1/10~1/1000) — 절대값이 없다 |
| US10985345 · US11730011 · US11183653 | ✗ | 148 GPa · 200 GPa · 3000 W/mK 는 **유리·금속·그래파이트** 값이지 실링재가 아니다 |
| 프레임 실 특허 9건(67차 CA 목록) | ✗ | 조성·점도·Tg·투습·접착력·비저항만 |
| Sekisui Photolec S 벤더 물성표 | ✗ | 점도·Ti·WVTR·전단접착력·Tg 만 |

> **디스크에서 나온 코어7 은 28칸 중 4칸이다.** 브리프가 기대한 "특허 실시예가 경화물의 경도·탄성률·접착력·CTE 를
> 인쇄하는 경우가 많다" 는 **이 코퍼스에서는 성립하지 않았다** — 인쇄되는 것은 경도(연필경도)·접착력이고,
> **탄성률은 두 건, CTE 는 0 건**이다. 특히 삼성디스플레이 US10928662B2 는 브리프가 지목한 문서인데
> 박리강도·전단·연신율만 인쇄하고 코어7 은 한 칸도 없다(그 셋은 코어7 키가 아니다).

**브리프가 있다고 한 파일 중 실재하지 않은 것** — 코니카미놀타 자사 기술보고 PDF(`*konica*` · `sugitani` ·
`takebe`), Eastman/Daicel 셀룰로스 에스터 핸드북(`cfl116_mp.*` · `chempoint_ce.*` · `E-325`).
`/data/paper_patent_corpus` 전역에서 **0 건**이다. 이것은 부재 주장이 아니라 "브리프의 파일 목록이 어긋났다"는 보고다.

### 2.2 새로 받은 문서 — 6종, 22칸

| 새 문서 | 절대경로 | 낸 칸 |
|---|---|---|
| AZoM/Granta **Cellulose Acetate** | `/data/paper_patent_corpus/standards_appnotes/display/db_azom_1461_cellulose_acetate.html` | 2705 밀도·포아송비·열전도율·비열·CTE·영률 |
| AZoM/Granta **Epoxy Resin - General Purpose** | `.../db_azom_630.html` | 2701 코어7 전 칸 |
| AZoM/Granta **PMMA General Purpose** | `.../db_azom_788.html` | 2704 영률·포아송비·인장강도·열전도율·비열·CTE |
| **allnex RADCURE Product Guide** (Epoxy Acrylates 표) | `.../db_allnex_RADCURE_product_guide_coatings_inks_americas.pdf` | 2701 인장강도(EBECRYL 3700) |
| **Sartomer CN120A75 TDS** | `.../db_sartomer_CN120A75_tds.pdf` | 2701 영률·인장강도 |
| **matmake Butyl Rubber (IIR)** | `.../db_matmake_butyl_rubber.html` | 2708 밀도·인장강도·열전도율·비열 |

---

## 3. 값의 근거 — 카드별로

### 3.1 재료 2701 프레임 실 — 7/7, 그런데 **인장강도가 5.2 배, 영률이 13 배 갈린다**

**출처 A — AZoM/Granta 'Epoxy Resin - General Purpose'** (범용 에폭시 클래스표, 코어7 전 칸).
표 verbatim (열 머리글 `Property | Minimum Value (S.I.) | Maximum Value (S.I.) | Units (S.I.)`).

```
Density              1.14   1.46   Mg/m3
Young's Modulus      2.5    4.4    GPa
Poisson's Ratio      0.4    0.45
Tensile Strength     40     60     MPa
Specific Heat        1200   1280   J/kg.K
Thermal Conductivity 0.15   0.6    W/m.K
Thermal Expansion    80     150    10-6/K
Glass Temperature    350    410    K
Shear Modulus        0.9    1.6    GPa
```

**자기검산** — `E = 2G(1+v)` 로 되돌리면 2×0.9×1.40 = 2.52 GPa, 2×1.6×1.45 = 4.64 GPa 로
인쇄된 2.5~4.4 GPa 와 1~5 % 안에서 맞는다. 열 배치와 단위가 확인된다.

**출처 B — allnex RADCURE Product Guide, Epoxy Acrylates 표, EBECRYL 3700 행.**
**이 올리고머는 이 용도에 이름이 찍혀 있다** — Sharp US 10,739,647 B2 가 실 배합을
`an acrylic resin (epoxy-modified) (EBECRYL3700 available from Daicel-Allnex Ltd., about 50 wt %)` 로 인쇄한다.

```
Product      Description                  Func  Viscosity cP   Color  Acid   Tensile   Tensile      Tg    Density
                                                                Value  Strength  Elongation  °C   g/ml 25°C
                                                                        psi        %
EBECRYL 3700 Bisphenol-A Epoxy Diacrylate   2   800000 (25C)   2.5    0.2    12000      5        65    1.18
                                                2317 (65.5C)
```

12000 psi × 6894.757 = **8.2737e7 Pa (82.74 MPa)** 를 인장강도로 넣었다.
**밀도 1.18 g/ml 는 넣지 않았다** — 표 머리글이 `Density g/ml at 25 °C` 로 **경화 전 액상 올리고머**의 값이다.
경화수축분만큼 고형물이 더 무거우므로 이것을 `physical.density` 에 넣으면 물리량이 다르다.

**출처 C — Sartomer CN120A75 TDS 의 `CURED PROPERTIES`.**
Kaneka US10259948B2 Comparative Example 1 이 담은 **에폭시 아크릴레이트 CN120** 계열이다.

```
CURED PROPERTIES
Tg (°C), by DSC          84
Young Modulus (MPa)      331
Elongation at break (%)  4
Tensile Strength (MPa)   16
```

자기검산 — 16 MPa / 4 % = 할선탄성률 400 MPa 로 인쇄된 331 MPa 와 같은 자릿수다(정합).
**액상 밀도 1.03 g/mL 는 TDS 스스로 `LIQUID PROPERTIES` 로 분류하므로 넣지 않았다.**

> **이번 배치의 최대 갈림 — 같은 화학을 두 벤더가 6.9 배 다르게 찍는다.**
> `CN120A75` = 비스페놀A 에폭시 아크릴레이트 + **25 % TPGDA**, 인장 **16 MPa** / 연신 4 % / Tg 84 °C.
> `EBECRYL 3700-25R` = 비스페놀A 에폭시 디아크릴레이트 + **25 % TRPGDA(=TPGDA)**, 인장 **15900 psi = 109.6 MPa** /
> 연신 4 % / Tg 71 °C.
> **연신율은 둘 다 4 % 인데 강도가 6.9 배다.** 두 시트 모두 시험규격·경화선량·시편두께를 인쇄하지 않아 가르지 못했다.
> allnex 표는 각주로 스스로 `Not a specification` 이라고 적는다.
>
> 그 결과 이 카드의 **인장강도 밴드는 16 ~ 82.7 MPa (5.2 배)**, **영률 밴드는 0.331 ~ 4.4 GPa (13.3 배)** 다.
> 두 밴드 다 등록했다 — 어느 한쪽을 조용히 버리는 것이 부정직하기 때문이다. **평균 내지 마라.**
> 물리적으로는 방향이 설명된다: 아민 경화 에폭시망(Granta)과 UV 라디칼 경화 에폭시 아크릴레이트망은
> 가교점 밀도와 사슬 유연성이 다르다. 실제 프레임 실은 여기에 **무기 충전 10~25 wt% + 120 °C 열경화 후처리**가
> 더 붙어 밴드 위쪽으로 간다 — 그 배수는 문서가 말하지 않아 계산하지 않았다.

### 3.2 재료 2704 오버코트 — 7/7, 밀도만 이 층 자신의 문서에서 나왔다

**출처 A — BOE US 11,332,634 B2 TABLE 2.** 스캔 PDF 라 400 dpi 로 다시 렌더해 tesseract 로 두 번 읽었다.

```
                       Overcoat Layer
Parameters of Physical Material Prepared   Existing Overcoat
Properties             in Example 6        Layer Material
Density (g/cm3)        1.00 to 1.05        1.2 to 1.3
Dielectric Constant    ... to 2.5          3 to 4
```

**오른쪽 열이 이 카드다.** 같은 특허 배경부가 못박는다 —
`At present, the OC material mainly consists of acrylic resin-epoxy resin as a basic skeleton component ...
At present, the most commonly used acrylic resin is polymethyl methacrylate.`
왼쪽 열(1.00~1.05)은 BOE 가 새로 제안한 **가교 폴리스티렌계**라 이 카드가 아니다 — 넣지 않았다.

**교차검증이 닫힌다** — 같은 특허 TABLE 3 이 `Density | around 1.05 | 1.15 to 1.19` 로 가교 PS 와 **PMMA 단독**을
비교한다. PMMA 단독 1.15~1.19 → 실제 오버코트 배합 1.2~1.3 은 에폭시·가교제·계면활성제가 더해진 방향과 맞고,
두 열이 1.19~1.20 에서 이어진다. 오식이 아니다.

**출처 B — AZoM/Granta 'PMMA General Purpose'** (나머지 여섯 칸).

```
Young's Modulus      2.7    3.2    GPa
Poisson's Ratio      0.4    0.43
Tensile Strength     50     75     MPa
Specific Heat        1400   1450   J/kg.K
Thermal Conductivity 0.2    0.21   W/m.K
Thermal Expansion    68     72     10-6/K
Density              1.15   1.2    Mg/m3   ← BOE 열이 있으므로 이 행은 넣지 않았다
```

이 클래스값을 붙인 **유일한 근거는 위 BOE 배경 문장**이다(주골격 아크릴 수지 = PMMA).
그리고 각 행의 `grade_scope` 에 어긋남을 적었다 — **이 층은 에폭시 10~30 wt% 를 담고 가교된 열경화막이고
PMMA 는 가교 안 된 선형 열가소성이다.** 가교는 보통 영률·강도를 올리고 CTE 를 내리므로
**이 밴드는 아크릴 골격 쪽의 하한 성격**이다. 에폭시 공성분 쪽 밴드(Granta 범용 에폭시: 2.5~4.4 GPa ·
0.40~0.45 · 40~60 MPa · 1200~1280 J/kgK · 0.15~0.6 W/mK · 80~150 ppm/K)는 **이 카드에 넣지 않았고**
다음 배치가 판단할 몫으로 남긴다.

**CTE 를 특허에서 못 가져온 이유** — TABLE 3 의 `Thermal Expansion Coefficient (/K) 6.84*10-5` 는
**가교 폴리스티렌**의 값이고, **PMMA 열은 원문에서 대시로 비어 있다**(400 dpi 재OCR 로 두 번 확인).

### 3.3 재료 2705 TAC — 7/7, 두 칸은 진짜 CTA 실측이다

**출처 A — ACS Omega 10.1021/acsomega.8b01616 Table 1 'neat CTA' 행** (디스크에 이미 있던 문서).
**67차 CC 가 이 문서를 열어 "산소 열이 없다"고 판정했는데, 같은 문서의 역학 표는 차 있었다.**

```
sample     Young's modulus (GPa)  ultimate strength (MPa)  yield strength (MPa)  elongation at break (%)  toughness (MJ/m3)
neat CTA   1.03 ± 0.07            40.8 ± 2.2               40.8 ± 2.3            11.6 ± 4.1               3.6 ± 1.7
```

영률 1.03 GPa · 인장강도 40.8 MPa 를 넣었다. **인장항복 = 인장강도라 취성 파단이고 연신 11.6 % 와 정합한다.**

**출처 B — AZoM/Granta 'Cellulose Acetate'** (나머지 다섯 칸 + 영률 밴드).

```
Density              1.28    1.32    Mg/m3
Poisson's Ratio      0.3827  0.3989
Young's Modulus      2.4     4.1     GPa
Tensile Strength     31      55.2    MPa
Specific Heat        1451    1509    J/kg.K
Thermal Conductivity 0.167   0.335   W/m.K
Thermal Expansion    180     270     10-6/K
Shear Modulus        0.8628  1.474   GPa
Glass Temperature    325.4   338.6   K      ← 이 행이 이 표의 정체를 말한다
```

**자기검산** — `E = 2G(1+v)`: 2×0.8628×1.3827 = 2.386 GPa, 2×1.474×1.3989 = 4.124 GPa 로
인쇄된 2.4~4.1 GPa 와 각각 0.6 % 안에서 맞는다.

**교차검증 두 건** — (a) 인장강도: Granta 31~55.2 MPa 가 실측 40.8 MPa 를 감싼다(그래서 Granta 인장 행은
넣지 않았다). (b) 열전도율: 별개 논문 *Heat Flow in Solvent-Free, Dense Amorphous and Semi-Crystalline
Cellulose Derivatives* (PMC12805645)가 50 µm CA 필름을 D-TOPS 로 293~373 K 에서 재어 0.15~0.21 W/m/K 를
적는데, 이는 Granta 구간(0.167~0.335)의 아래쪽에 들어온다. **그 논문 값은 등록하지 않았다 — 수치가 Figure 7(b)
축에만 있다.**

> **이 카드에서 정직하게 적어야 할 두 가지.**
>
> **① Granta 의 CA 는 가소화 성형 그레이드다.** 같은 표가 `Glass Temperature 325.4~338.6 K (52~66 °C)` 를
> 인쇄한다. 이 카드의 CTA 는 같은 배치의 ACS Omega Table 2 에서 **Tg 180.3 ± 2.7 °C** 다. **같은 재료가 아니다.**
> 그래서 다섯 칸 전부 `grade_scope` 에 이 어긋남을 박았다.
>
> **② CTE 180~270 ppm/K 는 이 배치에서 가장 약한 칸이다.** 유리상 폴리머의 CTE 는 Tg 근방에서 급증하는데
> Granta 의 CA 는 실온이 Tg 로부터 30~45 K 아래일 뿐이고, 이 카드의 CTA 는 160 K 아래다.
> **이 값은 TAC 필름의 상한으로만 읽어라 — 대표값이 아니다.** 그 문장을 `conditions.grade_scope` 에 그대로 적었다.
> 무가소 CTA 필름의 CTE 를 인쇄한 문서는 확보하지 못했다(ACS Omega 는 CTE 를 재지만 **Figure 6 그래프에만** 있고 표가 없다).
>
> **③ 영률이 2.3~4.0 배 어긋나고 방향이 이상하다.** 실측 CTA 1.03 GPa < 가소화 CA 클래스 2.4~4.1 GPa 인데,
> 가소제는 보통 영률을 **내린다**. 어느 쪽이 옳은지 가르지 못했다 — 세 행을 다 등록했다. 밴드로 써라.

### 3.4 재료 2708 사이드실 — 5/7

**출처 A — LG디스플레이 US 11,099,608 B2 문단 267.** 이 문서는 재료의 자리와 역할을 우리 카드와 같게 적는다 —
`The first seal member 160 and the second seal member 170 ... to seal the side surface of the display panel 120 ...
The moisture absorbent serves to absorb moisture and oxygen from the outside and thus minimize the permeation of
moisture and oxygen through the side portion of the display panel 120.`

> `For example, the first seal member 160 may have a modulus of elasticity of approximately **0.14 GPa** and the
> second seal member 170 may have a modulus of elasticity of approximately **1.8 GPa**, but are not limited thereto.`

**두 행을 다 넣었다** — 롤러블 2층 사이드실의 내측(유연)과 외측(강성)이다. 평균 내지 마라.
**`method` 를 `measured` 로 두지 않았다** — `may have ... approximately` 는 설계 서술이지 시험 결과 보고가 아니다.
이 특허에 실시예 물성표는 없다.

**혼동 주의 두 건을 걸러냈다** — 같은 특허 문단 254 의 `200 MPa to 900 MPa` 는 **금속 봉지기판**이고,
문단 255 의 `6.5 MPa` 는 **제1 접착층(OCA/PSA)**이다. 둘 다 실링재가 아니라 넣지 않았다.

**출처 B — matmake 'Butyl Rubber (IIR) - Properties'** (밀도 917 kg/m³ · 인장 17 MPa · 열전도율 0.13~0.23 W/mK ·
비열 1950 J/kgK).

**교차검증이 네 칸 모두 닫힌다** — 카탈로그 재료 59 `Waterproof Butyl Seal` 이 서로 **독립인** 출처들에서
밀도 920 kg/m³ (MDPI Polymers) · 열전도율 0.13(MDPI)·0.2(Hofmann) · 비열 1900(Hofmann) · 인장 16 MPa(H.B. Fuller)를
갖고 있고, 이번 네 값이 전부 그 안 또는 3 % 안에 든다.

> **그런데 이 출처는 행 단위로 검증해야 한다.** 같은 페이지의 `Young's Modulus (E) | 0.3 - 3.4 GPa` 는
> 같은 표의 `Ultimate Tensile Strength 17 MPa` · `Elongation at Break 700 - 950%` 와 **자기모순**이다
> (0.3 GPa 면 17 MPa 에서 변형률 5.7 % 다). **그 행은 쓰지 않았다.**
> 같은 사이트의 Cellulose Acetate 페이지도 굴곡탄성률 8.3~27.6 GPa 를 영률 1.0~4.0 GPa 보다 크게 인쇄한다.
> **matmake 는 통째로 신뢰할 출처가 아니다 — 행마다 자기검산과 카탈로그 교차검증을 통과한 것만 썼다.**
> (그래서 2705 에는 matmake CA 를 쓰지 않고 내부 정합이 확인되는 Granta 를 썼다.)

---

## 4. 못 넣은 것 — 셋을 구분해서

### 4.1 문서를 열었는데 **그 열이 없었던** 것 → 판정으로 기록했다 (`db05_verdicts.json`)

| 재료·키 | 연 문서 | 결과 |
|---|---|---|
| **2708 `mechanical.poisson_ratio`** | matmake Butyl Rubber 전량 · US11099608B2 전문 · US10928662B2 TABLE 1 · 67차 CE 의 사이드실 특허 25건 · AZoM/Granta properties.aspx ID 직접 타진 | **포아송비 행 자체가 없다.** matmake 서식에 포아송비 칸이 없고, Granta 계열에 부틸고무/PIB 항목을 **찾지 못했다**(실리콘고무 920 · E-SBR 1844 는 있다. ID 12개를 직접 두드리고 사이트 검색도 했으나 부틸 레코드가 잡히지 않았다 — 전수 열거는 아니므로 '없다'가 아니라 '못 찾았다'다) |
| **2708 `thermal.expansion_linear`** | 같은 문서들 + US2025/0221249A1 + US2024/0224729A1 + US2025/0212658A1 | matmake 의 Thermal 구획은 열전도율·비열·Tg 셋뿐(같은 사이트 CA 페이지엔 CTE 행이 **있으므로** 서식 문제가 아니다). LGD US2025/0221249A1 은 CTE 를 **비로만** 인쇄한다(`1/10 to 1/1000 of ... the sealing member`) — **절대값이 문서 어디에도 없다.** US2025/0212658A1 의 CTE 언급은 **Invar 봉지기판**이다 |

**추정으로 채우지 않았다.** 엘라스토머 관례값 0.49 를 붙이지 않은 이유 — 이 카드는 같은 문서가 0.14 GPa 와
**1.8 GPa** 를 함께 찍는다. 1.8 GPa 면 유리상이고 거기에 0.49 를 붙이면 체적탄성률이 30 GPa 로 튄다.
**어느 상태에 놓이는지가 미확정인 카드에 관례값 하나를 붙이는 것이 오히려 틀린 값이 된다.**
부틸고무 CTE 통념(190 ppm/K 대)도 같은 이유로 적지 않았다 — 실제 실링재는 무기 충전 20 wt% 대(흄드실리카 3.7 % +
CaO 18 %)라 그 값에서 크게 내려가고, **내려가는 배수를 문서가 말하지 않는다.** 역산 금지.

카드 2701 · 2704 · 2705 에도 "어느 문을 열었고 무엇이 없었나"를 `core_doors_tried` 로 남겼다 —
다음 파동이 같은 문을 두 번 두드리지 않게.

### 4.2 문서를 열었고 값도 있는데 **등급이 안 맞아** 안 넣거나 tier 를 내린 것

| 인쇄된 값 | 어떻게 했나 |
|---|---|
| EBECRYL 3700 `Density 1.18 g/ml at 25 °C` · CN120A75 `Density at 25°C 1.03 g/mL` | **넣지 않았다.** 둘 다 표/시트가 **액상 올리고머**로 분류한 값이다. 경화막 밀도가 아니다 — 경화수축분만큼 다르다 |
| BOE US11332634B2 TABLE 3 `Thermal Expansion Coefficient 6.84e-5 /K` | **넣지 않았다.** **가교 폴리스티렌**의 값이고 PMMA 열은 대시로 비어 있다 |
| BOE TABLE 2 왼쪽 열 `Density 1.00 to 1.05` | **넣지 않았다.** BOE 가 새로 제안한 가교 PS 계이지 이 카드가 아니다 |
| AZoM/Granta CA `Tensile Strength 31~55.2 MPa` | **넣지 않았다.** 같은 카드에 실측 40.8 MPa 가 들어갔고 두 문서가 어긋나지 않는다(감싼다). 어긋난 것은 영률뿐이고 그쪽은 세 행을 다 넣었다 |
| matmake Butyl `Young's Modulus 0.3~3.4 GPa` | **넣지 않았다.** 같은 표의 인장강도·파단연신과 자기모순 |
| US11099608B2 `200~900 MPa` · `6.5 MPa` | **넣지 않았다.** 금속 봉지기판과 OCA/PSA 접착층이다 |
| 삼성디스플레이 US10928662B2 박리 1600~2100 N/m · 전단 7.5~9 N/mm² · 연신 100~300 % | **코어7 키가 아니다.** `interface.peel_strength` · `interface.lap_shear_strength` · `mechanical.elongation_at_break` 로 별도 배치가 가져갈 몫이다(이번 표적 밖이라 손대지 않았다) |
| ACS Omega Table 2 `E' at 23 °C 2.94 GPa` (neat CTA) | **넣지 않았다.** DMA 저장탄성률은 인장 영률과 다른 물리량이다. 같은 시료인데 인장 1.03 GPa 와 **2.9 배** 갈리는 것을 notes 에 적어 두었다 |
| ACS Omega 본문 `density of the nanocomposite ... approximately 1.15` | **넣지 않았다.** **복합막**의 밀도이지 순수 CTA 가 아니다(원표 SI Table S2 는 디스크에 없다) |
| *Heat Flow in ... Cellulose Derivatives* CA 열전도율 0.15~0.21 W/m/K | **넣지 않았다.** 수치가 Figure 7(b) 축에만 있다. 교차검증으로만 썼다 |
| ACS Omega Figure 6 CTE | **넣지 않았다.** 그래프뿐이고 표가 없다 |

### 4.3 문서를 **못 연** 것 (부재의 근거가 아니다)

| 문서 | 왜 못 열었나 |
|---|---|
| **코니카미놀타 TAC 기술보고 PDF** (`*konica*` · `sugitani` · `takebe`) | **디스크에 없다.** `/data/paper_patent_corpus` 전역 검색 0 건. 브리프의 파일 목록이 어긋났다 |
| **Eastman/Daicel 셀룰로스 에스터 핸드북** (`cfl116_mp.*` · `chempoint_ce.*` · Eastman `E-325`) | 같음 — 디스크에 없다 |
| **Sartomer 무희석 CN120 TDS** | 제품 페이지가 JS 렌더라 PDF 링크를 못 뽑았고, 파일명 추정 2회가 404. 25 % TPGDA 희석품(CN120A75)으로 대체 |
| **Lee et al., Jpn. J. Appl. Phys. 54 (2015) 076701**, *Effects of thermomechanical properties of polarizer components on light leakage in TFT-LCD* | **TAC 필름의 E·CTE 를 FEA 입력표로 가졌을 확률이 가장 높은 문서.** JJAP 유료, ResearchGate/Academia 는 봇 차단 |
| **ACS AMI 2015, 7, 11041** (Yano 그룹, *Low-Birefringent and Highly Tough Nanocellulose-Reinforced CTA*) | 같은 그룹이 TMA 로 neat CTA 의 CTE 를 재는 문헌. closed OA |
| **ACS Omega 8b01616 의 SI (Table S2 밀도 · Figure S3)** | 본문 XML/HTML 만 디스크에 있고 SI 는 없다 |
| **Granta/CES 의 Butyl Rubber 레코드** | AZoM 무료 미러에 그 항목이 없다(§4.1) |
| **Rubber Technology Handbook (Hofmann)** — 카탈로그 출처 971 | **DB 에 등록만 돼 있고 `url` · `local_path` 가 비어 있다.** 재료 59 가 이미 이 책으로 포아송비 0.49 를 갖고 있으므로 실물 한 권이면 2708 의 빈칸 하나가 닫힌다. 67차 CE 가 출처 853(Polymer Handbook)에 대해 지적한 것과 **같은 종류의 구멍이다** |

---

## 5. 이 값들을 해석에 쓸 때

1. **전부 tier 3 다. t1 은 한 건도 없다.** 이 네 층 자신을 잰 문서는 여전히 0 건이다.
   각 행의 `conditions.grade_scope` 에 "왜 이 제품의 값이 아닌지"를 세 겹(화학·배합·제품)으로 적었다 — 반드시 읽어라.
2. **밴드로 인쇄된 것은 두 행이다. 평균 내지 마라.** 특히 2701 의 영률 0.331~4.4 GPa(13.3 배)와
   인장강도 16~82.7 MPa(5.2 배)는 **밴드 자체가 결론**이다.
3. **2705 의 CTE 180~270 ppm/K 는 상한이지 대표값이 아니다**(§3.3 ②). 감도해석에 쓸 때
   하한을 60~90 ppm/K 대로 함께 돌려라 — 그 하한은 문서 근거가 아니라 유리상 폴리머의 일반론이므로 **DB 에 넣지 않았다.**
4. **2708 의 영률은 두 부재의 값이다.** 단층 사이드실을 모델링한다면 0.14 GPa(내측 유연)와 1.8 GPa(외측 강성) 중
   어느 구조인지 먼저 정해라. 한 값으로 두 부재를 쓰지 마라.
5. **2701 과 2708 은 다른 재료다**(67차 CE §1 이 특허 3건으로 확정). 한 값으로 두 면을 쓰지 마라.

---

## 6. 다음 배치에 넘길 것

| 순위 | 할 일 | 왜 |
|---|---|---|
| 🔴 1 | **2708 포아송비 — 카탈로그 출처 971 `Rubber Technology Handbook (Hofmann)` 의 실물을 확보하고 `local_path` 를 채워라** | 재료 59 가 이미 그것으로 0.49 를 갖고 있다. 한 권이면 **카드 4장이 전부 선다**. 67차 CE 가 출처 853 에 대해 낸 것과 같은 요청이다 — **"등록만 돼 있고 못 여는 출처"가 배치를 세 번째 헛돌게 했다** |
| 🔴 2 | **Sartomer 대 allnex 의 6.9 배 갈림 해소** (§3.1) | 같은 화학(에폭시 디아크릴레이트 + 25 % TPGDA), 같은 연신율 4 %, 인장 16 vs 109.6 MPa. 두 벤더에 시험규격·경화선량·시편두께를 문의하거나 제3의 독립 측정 문헌. 지금 2701 의 강도·강성 불확실도를 지배한다 |
| 🔴 3 | **Lee et al., JpnJAP 54 (2015) 076701 확보** | TAC 필름의 E·CTE 를 FEA 입력표로 가졌을 확률이 가장 높은 문서. 이것 하나로 2705 의 가장 약한 칸(CTE)과 영률 갈림이 동시에 닫힐 수 있다. 저자 소속(한국 대학) 리포지터리 경로가 남았다 |
| 🟡 4 | **ACS Omega 8b01616 의 SI 확보** (Table S2 밀도 · Figure S3) | 2705 밀도를 클래스값에서 실측으로 올릴 수 있다. 본문은 이미 디스크에 있다 |
| 🟡 5 | **2704 에 에폭시 공성분 밴드를 넣을지 판단해라** (§3.2) | 지금은 PMMA 밴드만 넣었다. Granta 범용 에폭시 밴드(CTE 80~150 · 비열 1200~1280)는 PMMA 밴드(68~72 · 1400~1450)와 겹치지 않는다. 두 골격의 봉투를 다 세울지, 한쪽만 둘지는 다음 배치의 판단이다 |
| 🟡 6 | **2708 의 코어7 을 아크릴레이트 갈래로도 세워라** | 지금 밀도·인장·열전도율·비열은 **PIB 갈래**(부틸고무 클래스)에서만 나왔다. 삼성디스플레이 US10928662B2 의 우레탄아크릴레이트/IBOA/THFA 갈래는 코어7 이 통째로 비어 있다. allnex RADCURE 가이드의 Aliphatic Urethane Acrylates 표(이미 디스크에 있다)가 인장강도·연신율·Tg·밀도를 등급별로 인쇄하지만, **어느 등급을 고를지가 문서로 정해지지 않아 이번에는 손대지 않았다**(등급 고르기는 체리피킹이다) |
| 🟡 7 | **US10928662B2 의 박리 1600~2100 N/m · 전단 7.5~9 N/mm² · 연신 100~300 % 를 코어7 밖 키로 등록해라** | 이번 표적이 아니라 안 넣었다. `interface.peel_strength` · `interface.lap_shear_strength` · `mechanical.elongation_at_break` 세 칸이 문서 하나로 닫힌다. **이 카드에서 실제로 측정된 유일한 값들이다**(TABLE 1 이 Example 1 을 200 % / 1940 N/m / 1734 N/m / 8.13 N/mm² 로 인쇄한다) |
| 🟢 8 | **matmake(카탈로그 출처 3300 계열)의 기존 행을 재검증해라** | 이 배치가 두 페이지에서 자기모순 행을 각각 하나씩 찾았다(butyl 영률, CA 굴곡탄성률). 이 사이트에서 온 기존 카탈로그 값이 같은 함정을 밟았는지 확인할 값어치가 있다 |

---

## 7. 산출물

```
backend/scripts/catalog/out_db/
├── db00_report.md                  이 문서
├── db01_tac_core7.json             2705 · 14행 (Granta CA 12 + ACS Omega 2)
├── db02_overcoat_core7.json        2704 · 14행 (BOE 특허 2 + Granta PMMA 12)
├── db03_frame_sealant_core7.json   2701 · 17행 (Granta 에폭시 14 + allnex 1 + Sartomer 2)
├── db04_side_seal_core7.json       2708 · 7행  (LGD 특허 2 + matmake 부틸 5)
└── db05_verdicts.json              판정 — 2708 빈칸 2건 + 카드 3장의 core_doors_tried
```

새로 받은 원문 (`/data/paper_patent_corpus/standards_appnotes/display/`)

```
db_azom_1461_cellulose_acetate.html                          2705 다섯 칸 + 영률 밴드
db_azom_630.html                                             2701 코어7 전 칸 (Granta 범용 에폭시)
db_azom_788.html                                             2704 여섯 칸 (Granta PMMA)
db_allnex_RADCURE_product_guide_coatings_inks_americas.pdf/.txt   EBECRYL 3700 인장 12000 psi
db_sartomer_CN120A75_tds.pdf/.txt                            경화물 영률 331 MPa · 인장 16 MPa
db_matmake_butyl_rubber.html                                 2708 네 칸
```

**총계 — 물성 52건 등록(전량 tier 3), 판정 6건. 코어7 28칸 중 26칸을 닫았고 카드 4장 중 3장이 섰다.**
