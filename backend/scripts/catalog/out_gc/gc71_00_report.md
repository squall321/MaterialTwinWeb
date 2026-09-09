# 71차 GC — 70차 FB 의 「일곱 번째 축 = 지역」을 시험했고, **그 가설은 틀렸다**

70차 FB 는 Cytec 미국판 SDS 가 `Specific Gravity/Density` 를 채우고 Solvay 영국판이 `Density` 를 비운 것을 보고
**부재의 일곱째 축은 지역이다**, 다음 파동은 **미국판 SDS 를 표적으로 삼아라** 라고 넘겼다.

이 배치는 그 지시를 그대로 따랐다 — 미국판을 찾아 다녔다. 그리고 **찾을수록 가설이 무너졌다.**
같은 제품의 두 지역판을 **둘 다 연 쌍 156건**을 모았고, 미국·영어판만 밀도를 찍은 것은 **4건(2.6 %)** 이다.
반대 방향(비영어판만 찍음)도 0건이 아니다 — 두산에서 2건이 나온다.

표적은 `role=product` 인데 `physical.density` 가 비어 있는 재료 **124종**이다(70차 FB 때 107종, 그 사이 CCL 19종이 새로 들어왔다).

---

## 1. 지역축 검증표 — 이 배치의 핵심 수치

### 1-가. 손으로 고른 쌍 20건 (문서를 한 장씩 열어 9절을 대조했다)

| # | 제품 | 연 지역판 | 미국/영어판 | 비영어·비미국판 | 판정 |
|---|---|---|---|---|---|
| 1 | **3M DP100 Clear** (표적 2389) | US · CA · **GB · DE · FR** | 1.15 / 1.17 | 1,15 / 1,17 (전부) | 둘 다 찍음 |
| 2 | **3M DP100NS** (표적 2418) | US · CA · **GB · DE · FR** | 1.15 / 1.18 | 1,15 / 1,18 (전부) | 둘 다 찍음 |
| 3 | **DuPont/Dow CYCLOTENE 4022-35** (표적 1360) | US · **GB · DE** (같은 Version 11.0) | 0.94 | 0.94 / 0,94 | 둘 다 찍음 |
| 4 | **DuPont Teijin Films Mylar** (2254 형제) | US MSDS 2009 `1.2-1.4` | EU AIS 2016 `1.23-1.41` | | 둘 다 찍음(EU 가 더 정밀) |
| 5 | **Doosan DSflex-900** | 수출 영문 `1.45/0.92` | 국문 `2.50 ±0.50` | | ★ 둘 다 찍는데 **수가 다르다** |
| 6 | **MGC CCL-EL190T/EL230T** (2724·2725) | 영문 `Specific Gravity of Resin 1.44/1.42` | 일문 `樹脂比重 1.44/1.42` | | 둘 다 찍음(단, **수지**의 값) |
| 7 | **Cytec/Solvay FM 300-2** (FB 가 가설을 세운 벤더) | US SDS 0059418 `Not available` | UK SDS 2023 `No data available` | | 둘 다 **안 찍음** |
| 8 | **Rogers RO4000** (1277·1278) | en MSDS·PSIS `NA` | cn·fr·de·sp `NA` | | 둘 다 안 찍음 |
| 9 | **MGC CCL-HL820WDI** (2726) | 영문 (행 없음) | 일문 (행 없음) | | 둘 다 안 찍음 |
| 10 | **Sumitomo Sumilite ELC** (2727~2730) | 영문 사양표 (행 없음) | 일문 사양표 (행 없음) | | 둘 다 안 찍음 |
| 11 | **Sumitomo Sumilite ELC-PWB** (2731·2732) | 영문 (행 없음) | 일문 (행 없음) | | 둘 다 안 찍음 |
| 12 | **Resonac MCL-E-679FG** (2741·2742) | 본사 총괄카탈로그 (행 없음) | EU 법인 페이지 (행 없음) | | 둘 다 안 찍음 |
| 13~18 | **OLED 소분자 6종** — Ir(ppy)3 · ADN · TCTA · TAPC · CBP · mCP | 미국 OSHA 판 `No data available` | Ossila 영국 CLP 판 `Not known.` | | 둘 다 안 찍음 |
| **19** | **OLED BCP (bathocuproine)** — 표적 1760 | **Thermo Fisher 미국판 `Density / Specific Gravity  1.17 g/cm3`** | Ossila 영국판 `Density Not known.` | | ★ **미국판만 찍는다** |
| 20 | **Zeon ZEONEX 330R** | US `0.95` | **EU 판이 존재하지 않는다** | | 지역판 없음 |

**집계 — 20쌍 중**
- 양쪽 다 찍음 **6** (그중 1건은 **수가 서로 다르다** — DSflex-900)
- 양쪽 다 안 찍음 **12**
- **미국/영어판만 찍음 1**(BCP)
- 비미국판만 찍음 **0**
- 지역판이 아예 없음 1(Zeon) · 지역판이 나뉘지 않음 1(Isola — 한 문서가 OSHA·REACH·CLP·WHMIS 를 동시에 인용)

### 1-나. Ellsworth 색인의 다국어판 쌍 136건 (기계로 판독하고 불일치는 전부 손으로 확인했다)

EDL 24,113 항목 중 **같은 `item_id` 에 언어코드가 둘 이상 달린 SDS 가 1,390건**이다.
그중 **170건을 무작위(seed 71)로 뽑아 340건을 내려받았고**, 텍스트층이 깨진 34쌍을 뺀 **136쌍**을 셌다.

| | 건수 |
|---|---|
| 두 판이 **둘 다 찍음** | **123** |
| 두 판이 **둘 다 안 찍음** | **10** |
| **영어(미국)판만 찍음** | **3** |
| 비영어판만 찍음 | **0** |
| **일치율** | **133/136 = 97.8 %** |

영어판만 찍은 3건은 전부 *다른 문서*였다 — HumiSeal 604 Thinner·2A64A 의 불문판은 **1999/45/CE 구서식**이라 9절이
`État·Couleur·Odeur·Point d'éclair` 네 줄뿐이고, Resinlab UR1049 Cream A 의 서문판은 `ꞏ Densidad: Indeterminado.` 다.

**그리고 둘 다 찍는 쌍에도 함정이 있다** — 값 비교가 가능한 119쌍 중 **9쌍이 다른 수를 찍는다**.
그중 진짜 모순 넷: Loctite Stycast 1090 BK `0.85` vs `2.45` · Stycast 1264 Part B `0.97` vs `1.6` ·
HumiSeal TS300 `1.00` vs `1.15 g/cm3` · ITW MA300 `0.96 g/cm3 estimated` vs `Densità relativa 1.03`(물리량 자체가 다르다).

### 1-다. 결론 — 축은 지역이 아니라 **템플릿이고, 템플릿을 정하는 것은 그 문서를 마지막에 다시 만든 사람이다**

**156쌍(20 + 136) 중 미국·영어판만 찍은 것은 4쌍, 2.6 % 다.** FB 의 가설은 일반 규칙이 아니다.
그리고 FB 가 가설을 세운 그 자리도 이번에 열어 보니 다른 이야기였다 —

> FB 는 **FM 300**(미국, 2017-02-05, 찍음)과 **FM 300-2**(영국, 2023-08-25, 안 찍음)를 비교했다.
> **등급이 다르고 연도도 6년 차이다.** 이번에 EDL `item_id 40945` 로 **같은 등급의 미국판**
> `FM(R) 300-2 Adhesive Red` SDS 0059418(2017-11-21, CYTEC INDUSTRIES INC., Princeton NJ)을 받아
> 이미지 PDF 를 300 dpi 렌더 + OCR 로 읽었고 9절이 **`Specific Gravity/Density:  Not available`** 이다.
> **같은 등급의 미국판도 비어 있다** — 지역이 아니라 제품이 갈랐다.

가장 결정적인 반증은 **한 회사·한 템플릿 안에서 나온다.**
Thermo Fisher/Acros 의 같은 미국 OSHA 템플릿이 같은 개정 주기(2025-12-19·20·21)에
**BCP 에서는 `Density / Specific Gravity  1.17 g/cm3` 를 찍고 TCTA 에서는 같은 행을 `No data available` 로 비운다.**
같은 시트가 TCTA 융점에는 `297 - 300 °C … Measured` 를 찍는다 — 서식이 막는 것이 아니라 **그 물질의 값을 안 가지고 있는 것**이다.

두산이 이 진단을 수치로 받친다. 같은 제품의 **국문/영문 쌍 61건** 중
54쌍은 양쪽 다 비고 · **4쌍은 영문만**(DS-7409DV 계열) · **2쌍은 국문만**(DS-7402H BS (D) · DS-7409HD BS) 찍는다.
**방향이 양쪽으로 갈린다.** 언제나 맞히는 것은 하나뿐이다 — **구서식 21/21 찍음 · GHS 신서식 1/160.**
그리고 국문판은 전부 2022-12-16 에 한꺼번에 신서식으로 다시 만들어졌고, 영문판은 등급마다 따로 만들어졌다.
**즉 축은 지역도 연도도 아니고, 그 문서를 마지막에 재발행한 사람이 어느 틀을 집었느냐다.**

### 1-라. 덤 — 브리프가 시켜 본 EDL `region` 인자는 **가짜다**

`document=34315`·`42304` 에 `region=0..5` 를 넣어 각각 받아 md5 를 비교했다 — **여섯 값이 전부 같은 파일**이다.
반면 **`language` 는 진짜다** — `document=2009`(DAPCO 2100)에서 `en` 638,774 B · `es` 133,745 B 로 다른 파일이 오고
`fr·de·zh·ja` 는 208 B 오류 스텁이 온다. **다음 파동은 `region` 을 만지지 마라. 지역판은 `language` 로만 나온다.**

---

## 2. 넣은 값 — **1종 1행**

| 재료 | 키 | 값 | 등급 | 근거 (9절 verbatim) |
|---|---|---|---|---|
| **1760 BCP (bathocuproine)** | `physical.density` | **1170 kg/m³** | t2 `handbook` | Thermo Fisher Scientific Chemicals `Bathocuproin` B22841, Revision 5(2025-12-21), US OSHA HCS 2024 — `Density / Specific Gravity             1.17 g/cm3` |

**왜 이 값은 살렸나** — 같은 9절이 바로 다음 행에 **`Bulk Density  No data available` 를 따로 둔다.**
즉 1.17 은 겉보기(벌크) 밀도가 아니라 **참밀도 자리**다. 이 템플릿이 두 칸을 구분한다는 것이 이 값을 살렸다.
단위가 인쇄되어 있어 물밀도를 곱하지 않았다(1.17 g/cm³ = 1170 kg/m³). 1절 `CAS No 4733-39-5` 로 동정이 정확히 걸린다.

**왜 t2 인가** — 9절의 `Remarks•Method` 열이 이 행에서 **비어 있다**(같은 시트가 다른 물질의 융점에는 `Measured` 를 찍는다).
측정법이 인쇄되지 않은 공급사 편찬 상수라, 69차 ED 가 **같은 재료의 융점**을 Ossila SDS 에서 `handbook`·t2 로 넣은 관례를 그대로 따랐다.
(`method` 어휘는 `measured·handbook·datasheet·computed·estimated·digitized` 여섯뿐이다.)

**형태를 못박았다** — 인쇄값은 `Physical State  Powder Solid`, 즉 **승화정제 분말**의 것이고
Swensen 2011 의 소자층은 **진공증착 비정질 박막**이다. 비정질 박막은 결정 분말보다 보통 몇 % 가볍다.
**그 보정을 계산해 넣지 않았고** `conditions.physical_form` 에 사실만 남겼다(70차 FB 의 미경화/경화 처리와 같은 자리).

**교차확인과 그 한계** — Acros Organics 판(AC161340, Revision 5, 2025-12-19)이 같은 행에 같은 1.17 을 찍는다.
**두 시트는 Thermo Fisher 계열의 같은 템플릿이라 독립 출처가 아니다 — 그렇게 세지 않았다.**
같은 미국 시장의 **TCI America(D0711, 2024-10-29)와 Chem-Impex(47659, 2024-08-06)는 이 칸을 비운다.**

## 3. 카드 — **0장**

라이브 DB 사본(`VACUUM INTO`)에 이 값을 넣고 카드 생성기를 돌렸다.

| | 넣기 전 | 넣은 뒤 |
|---|---|---|
| `mechanical` | `밀도·영률 없음(카드 생성 불가)` | **`영률 없음(카드 생성 불가)`** |
| `thermal` | `밀도·비열·열전도율 없음(카드 생성 불가)` | **`비열·열전도율 없음(카드 생성 불가)`** |

밀도 한 칸이 지워졌지만 **카드는 서지 않는다.** OLED 소분자에는 영률·비열·열전도율이 한 칸도 없다.
70차 FB 의 Zymet 처럼 "밀도만 채우면 나온다" 인 자리가 이번 표적에는 없었다.

---

## 4. 버린 것 — **문서 12건 · 인쇄값 19개**

### 4-가. 2액형이라 버렸다 — 새로 연 문서 7건 · 값 13개
3M DP100 Clear·DP100NS 의 **영국·독일·프랑스판 여섯 건과 2011년 프랑스 구판 한 건.**
전부 A액·B액 각각의 액상 밀도(1,15 / 1,17 / 1,18 g/ml)이고 혼합비가 9절에 없어 경화물 밀도를 만들 길이 없다(역산 금지).
같은 9절이 `Physical state Liquid` · `Specific Physical Form Viscous` · 인화점 240~257 °C · 점도 수만 cP 를 함께 찍는다.
**69차 ED·70차 FB 의 결론이 지역판 다섯을 다 열고도 그대로다.**

### 4-나. 용매가 든 미경화 액상이라 버렸다 — 문서 3건 · 값 4개
**CYCLOTENE 4022-35** 미국·영국·독일판(전부 2023, Version 11.0)의 `0.94 g/cm3`.
같은 9절이 `Physical state  Liquid.` · `Flash point  closed cup 44 °C … Literature (setaflash)` ·
`Kinematic Viscosity  192 mm2/s at 25 °C` 로 **메시틸렌 용액**임을 스스로 못 박는다.
68차 DA 가 2006년판 `0.9521` 을 기각한 논지가 그대로다 — 게다가 2006년 0.9521 과 2023년 0.94 가 같은 물건이라는 것이 이로써 확인된다.

### 4-다. 2액형도 미경화도 아닌데 **대상이 달라** 버렸다 — 문서 2건 · 값 2개
| 문서 | 찍힌 값 | 왜 버렸나 |
|---|---|---|
| **MGC FR-4 제품표**(일문·영문 두 판) | `樹脂比重 / Specific Gravity of Resin  1.44 (EL190T) · 1.42 (EL230T)` | **행 이름이 스스로 밝힌다 — 수지의 비중이다.** 우리 재료는 유리직물과 동박을 포함한 동장적층판이다. 같은 표의 다른 행(Tg·CTE·曲げ弾性率·ピール強度)은 전부 적층판 값이라 **이 한 행만 대상이 다르다** |
| **Doosan DST-9000 · DST-9000HT 영문 SDS** | `SPECIFIC GRAVITY : (Water=1.0) 2.5 to 3.3` | ㉠ 등급이 다르다(표적은 DST-9000**S**) ㉡ 1절이 `Al based Cu Clad Laminate`, 2절이 `Copper 2.4~88 wt%` · `Al 9.65~94.3 wt%` — **알루미늄 방열판 두께가 구성마다 달라 벌어진 조립체의 겉보기 밀도**(폭 32 %)지 재료의 산포가 아니다. 이 재료가 담은 값들(Dk 6.5 · k 2.5 W/mK · CTE 25/55 ppm)은 **절연층**의 것이다 |

**이 두 건이 69차 ED 의 CCL 함정과 70차 FB 의 면적중량÷두께 함정의 같은 얼굴이다** —
같은 시트 안에 밀도처럼 생긴 수가 있는데 그것이 **다른 물건**의 값이다.

---

## 5. 못 넣은 것 — 셋으로 갈라 적는다

### (가) 미국판 9절도 비었다 — 문서를 열고 확인했다
| 표적 | 연 미국판 | verbatim |
|---|---|---|
| 1651 · 1746 · 1761 · 1762 · 1763 · 1764 (OLED 6종) | TCI America · Acros/Fisher · Chem-Impex | `Relative density : No data available` / `Density / Specific Gravity  No data available` / `RELATIVE DENSITY`(값 칸 공백) |
| 618 · 619 CYCOM 5250-4 (형제 FM 300-2) | Cytec Industries Inc. SDS 0059418 (2017-11-21) | `Specific Gravity/Density:  Not available` |
| 1277 · 1278 Rogers RO4350·RO4003 | MSDS 2009-05-12 · PSIS 2022-07-05 | `SPECIFIC GRAVITY: NA (Water = 1)` · `DENSITY: NA` |
| 1273 Isola FR408 | 2016·2020·2024 (한 문서가 OSHA·REACH·CLP·WHMIS 동시 인용) | `SPECIFIC GRAVITY (@25 oC): Not Available for product` |
| 2483 DSR-1000 · 2509 DS-7409S (N) | 두산 영문판(GHS 신서식) | `N. Specific gravity  No data available` |
| 2724~2742 (MGC · Sumitomo · Resonac CCL 19종) | 일문·영문 제품표 양쪽 | **밀도 행 자체가 없다**(수지 비중 행 하나 제외) |

### (나) 미국판을 못 찾았다 — 그래서 '9절에 없다' 고 적지 않았다
- **2254 Melinex** — 미국판(Mylar MSDS)과 EU 판(Mylar A AIS) **둘 다 찍는데 둘 다 Mylar 다.** Melinex 자체 문서는 여전히 못 열었다(아카이브 적중 0 · EDL 0건).
- **1109/591 계열의 형제 FM 73M** — **반대 방향**이다. 미국판은 있고(`1.16`) **EU/UK 판이 없다.** 유통사 여섯 곳(aerospheres·ami-con·conro·e-aircraftsupply·gracoroberts·bigcommerce CDN)을 뒤졌고 전부 미국 Cytec 판이거나 로그인·403 이었다.
- **Zeon ZEONEX 330R** — `zeon.eu` 는 문서를 두지 않고 미국 `zeonsmi.com` 으로 넘긴다. 그 32건이 전부 `_USENG.pdf` 이고 330R 은 아예 없다. **EU 판이 존재한다는 증거가 없다.**
- **2461 · 2462 · 2463 · 2480 (Doosan DYN·DYN2·DYQ·DS-9000)** — 벤더 MSDS 색인(제품 120 · 첨부 183)에 **이 등급이 없다.** 이번에 `doosanelectromaterials.com` 과 `doosanelectronics.com` 이 **같은 사이트**임을 확인했고(같은 `/kr` 리다이렉트 · 같은 51,604 B), `POST /rest/product/msds/list` 를 `{}`·`{"lang":"en"}`·`{"language":"en"}` 셋으로 불러도 **응답이 230,290 B 로 동일**하다 — **MSDS 색인은 언어·지역으로 갈리지 않는 한 벌**이다. 영문 제품 페이지의 `<ul id="contents-msds">` 가 **빈 채로** 렌더된다.

### (다) 등급이 안 맞았다
- **2486 DST-9000S** — 문서는 DST-9000 · DST-9000HT (§4-다)
- **2254 Melinex** — 문서는 Mylar (다른 상표, 계열 폭 1.23-1.41)
- **2724 · 2725 MGC** — 행이 적층판이 아니라 수지 (§4-다)

---

## 6. 산출물

| 파일 | 내용 |
|---|---|
| `out_gc/gc71_00_report.md` | 이 보고서 |
| `out_gc/gc71_01_region_axis.json` | **지역축 검증표 15항목(제품 단위 20쌍) + EDL 다국어 실험 결과 + `region` 인자 시험** |
| `out_gc/gc71_02_edl_language_pairs_scored.json` | EDL 170항목 340문서의 9절 판독 결과(원자료) |
| `out_gc/gc71_03_verdicts.json` | 판정 **42종** — 신규 19(MGC 3 · Sumitomo 6 · Resonac 10) · 보강 22 · **철회 1**(1760 BCP) |
| `out_gc/gc71_04_materials.json` | 값 **1종 1행** |
| `out_gc/gen_gc71_03_verdicts.py` | 판정 생성기(옛 판정문을 새 문단 뒤에 그대로 보존한다) |
| `out_gc/gc71_harvest_edl_language_pairs.py` · `gc71_score_edl_language_pairs.py` | EDL 다국어판 수집기·판독기 |
| `/data/paper_patent_corpus/standards_appnotes/sds/` | SDS **22건 추가** → 누계 **103건** |

새로 남긴 SDS 22건 — 미국판 13건(`ThermoFisher_Bathocuproine-B22841_SDS_US_2025-12-21.pdf` ·
`AcrosOrganics_Bathocuproine-AC161340_SDS_US_2025-12-19.pdf` · `AcrosOrganics_TCTA-AC459180_SDS_US_2025-12-20.pdf` ·
`TCI-America_*` 7건 · `Chem-Impex_*` 3건), 지역판 9건(`DuPont-RohmHaas_CYCLOTENE-4022-35_SDS_US_2023-07-31.pdf` ·
`DuPont_CYCLOTENE-4022-35_SDS_{GB,DE}_2023-09-06.pdf` · `3M_DP100NS-Translucent_SDS_{GB,DE}_2020-02-18.pdf` ·
`3M_DP100NS-Translucent_SDS_FR_2022-07-28.pdf` · `3M_DP100-Clear_SDS_FR_2019-06-05.pdf` ·
`3M_DP100-Plus-Clear_SDS_DE_2022-10-12.pdf` · `3M_DP100-Plus-Clear_SDS_GB_2021-05-04.pdf`).

**DB 에는 아무것도 쓰지 않았다.** 예행과 사본 리허설만 돌렸다.

```
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  .venv/bin/python scripts/catalog/ingest_agent_json.py   scripts/catalog/out_gc/gc71_04_materials.json   # [DRY-RUN] ok 1
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  python3        scripts/catalog/apply_core_verdicts.py scripts/catalog/out_gc/gc71_03_verdicts.json    # [예행] 병합 42 · 재료 42
# 사본 리허설(VACUUM INTO 사본에 값·판정을 넣고 카드 생성기·정합성검사 → 사본 삭제)
#   → 카드 0장(사유가 '밀도·영률 없음' → '영률 없음' 으로 줄었다) · integrity_check diff 는 행/출처 수 한 줄뿐, 신규 이상 0
```

※ `ingest_agent_json.py` 는 `MATERIALTWIN_DATA_DIR` 을 줘도 `/data/appdata/materialtwin_web/materialtwin.db`(낡은 개발 DB)를 연다 —
   69차 ED·70차 FB 때와 같다. **스키마·단위·범위 검사는 유효하지만 그 도구의 DB 경로를 믿지 마라.**
※ `property_value.method` 는 CHECK 제약으로 **여섯 어휘**(`measured·handbook·datasheet·computed·estimated·digitized`)만 받는다.
   처음에 `vendor_sheet` 로 썼다가 사본 리허설에서 `CHECK constraint failed: ck_propval_method` 로 걸렸다 —
   **`ingest_agent_json.py` 의 DRY-RUN 은 이것을 안 잡는다.** 다음 파동은 method 어휘를 먼저 확인해라.
※ `out_gc/` 에는 8월 28일자 다른 배치의 `gc01`~`gc04` 가 이미 있었다. 덮지 않으려고 `gc71_` 접두어를 썼다.

---

## 7. 다음 파동에 넘길 것

### ㉠ **지역판을 표적으로 삼지 마라.** 축은 템플릿이고 템플릿은 문서마다 다르다
156쌍의 답이 이것이다. 68차 DA 의 '연도' → 69차 ED 의 '템플릿' → 70차 FB 의 '지역' 세 가설 중
**살아남은 것은 69차 ED 의 템플릿이다.** 다만 한 걸음 더 좁힐 수 있다 —
템플릿은 벤더가 정하는 것이 아니라 **그 문서를 마지막에 재발행한 사람이 집는 것**이다(두산 61쌍이 양방향으로 갈리는 이유).
그러니 다음 파동이 뒤져야 할 것은 **한 벤더 안에서 서로 다른 틀로 발행된 문서들**이고, 그것을 찾는 값싼 방법은
**개정일이 아니라 문서번호·버전 체계의 불연속**이다(두산 구서식은 `MSDS-J-###`, 신서식은 `General_…_Ver.N`).

### ㉡ 시약 벤더 경로는 **물질 단위로** 다시 물어라 — 공급사마다 가진 값이 다르다
BCP 하나가 이 배치의 유일한 값인데, 그것을 준 것은 지역이 아니라 **공급사**다
(Thermo/Acros 찍음 · TCI·Chem-Impex 안 찍음 · Ossila 안 찍음).
**아직 안 물어본 미국 공급사가 남아 있다** — Sigma-Aldrich(이 기계에서 TCP 타임아웃) · Santa Cruz(403) ·
Ambeed(Akamai 403) · Oakwood · AK Scientific · MedChemExpress. 다른 출구에서 접속되는 사람이 열면
**PO1·PO14 를 뺀 OLED 7종과 GST·Ir 착체 갈래가 한 번에 열릴 수 있다.**
그리고 **`Bulk Density` 행이 따로 있는 템플릿을 우선해라** — 그 템플릿에서만 참밀도인지 겉보기인지가 문서 안에서 갈린다.

### ㉢ 새로 들어온 CCL 19종은 **밀도 축이 구조적으로 닫혔다** — 다시 파지 마라
MGC · Sumitomo Bakelite · Resonac 세 벤더의 제품표를 **일문판·영문판·유럽판까지 전부** 열었고
셋 다 밀도 행이 없으며 셋 다 SDS 를 웹에 두지 않는다(sitemap 전수 `sds|msds` 0건).
IPC-4101 적층판의 구조적 부재(브리프 585)의 세 번째·네 번째·다섯 번째 증거다.
**단 하나 남은 것은 MGC 의 `樹脂比重` 1.44/1.42 인데, 그것은 수지의 값이라 적층판 자리에 못 넣는다** —
유리함량·동박두께가 인쇄되면 혼합칙으로 t4 를 만들 수는 있으나 **이 표는 그 셋을 인쇄하지 않는다.**

### ㉣ 아직 안 닫힌 표적 — 이 배치가 확인한 상태
| 표적 | 상태 |
|---|---|
| **1760 BCP** | **닫혔다** (t2 1170 kg/m³). 이제 막는 것은 영률·비열·열전도율이다 |
| 1651 · 1746 · 1761 · 1762 · 1763 · 1764 | 미국판까지 열었고 비었다. **남은 길은 Sigma-Aldrich 급 공급사이거나 단결정 XRD 논문이다** |
| 1758 · 1759 (PO1 · PO14) | 저자 합성물이라 공급사가 없다. 이 파동도 손대지 않았다 |
| **2254 Melinex** | Mylar 미국판·EU 판을 둘 다 열었고 둘 다 찍지만 둘 다 Mylar 다. **Melinex 자체 문서는 웹에 없다** |
| **1360 Cyclotene** | 미국·영국·독일 2023판을 다 열었다. 셋 다 액상 바니시 값이다. **경화막 밀도는 어느 문서에도 없다** |
| **2389 · 2418 DP100** | 지역판 다섯을 다 열었다. **벤더가 경화물 밀도를 어느 문서에도 찍지 않는다** — 더 팔 곳이 없다 |
| **2486 DST-9000S** | 형제 등급 문서는 있으나 Al 스택의 겉보기 밀도다. **이 등급의 SDS 는 벤더 색인에 없다** |
| 2461 · 2462 · 2463 · 2480 | 두산 공개 색인에 SDS 자체가 없다(언어·지역 무관, 한 벌 색인 전수 확인) |
| 1277 · 1278 · 1273 | 지역판이 나뉘지 않는 벤더다. **다시 파지 마라** |

### ㉤ **둘 다 찍어도 같은 물건이 아닐 수 있다** — 이 배치가 새로 발견한 함정
- **Doosan DSflex-900** — 같은 제품·같은 개정일(2025-10-14)의 국문판이 `2.50 ±0.50`, 영문판이 `1.45/0.92 (film/adhesive)` 다.
  국문은 동박 포함 적층체(3절 `Copper foil 70~95 wt%`), 영문은 폴리이미드 필름과 접착층 각각. **같은 행 이름으로 다른 물건을 답한다.**
- EDL 119쌍 중 **9쌍이 두 언어판에서 다른 수**를 찍고 그중 넷은 설명이 안 되는 모순이다(Stycast 1090 BK `0.85` vs `2.45`).
- **그러므로 값을 옮길 때는 판을 하나만 보지 말고 형제 판의 수를 대조해라.** 어긋나면 둘 다 의심해라.

### ㉥ 카드가 한 장 걸려 있는 자리를 하나 찾았다 — **2743**
표적 목록의 마지막 재료 **2743 `Epoxy molding compound, commercial low-filler 70 wt% fused silica, Tg 120 C (Chiu 2015)`** 는
`prony_relative_modulus` · `prony_relative_bulk_modulus` · `prony_relaxation_time` · `bulk_modulus` · `shear_modulus` · `wlf_c1/c2` 를
**이미 다 가지고 있다.** 70차 FB 가 Zymet 에서 `*MAT_GENERAL_VISCOELASTIC (076)` 을 세운 것과 같은 모양이다.
**다만 이 재료는 논문이 제품명을 인쇄하지 않아 벤더 시트를 붙일 수 없다**(V4). 문서축이 아니라 클래스 대표값 축의 문제다 —
이 배치는 손대지 않았다. **다음 파동이 t3 클래스값으로 채울지 조정자가 정해야 한다.**
