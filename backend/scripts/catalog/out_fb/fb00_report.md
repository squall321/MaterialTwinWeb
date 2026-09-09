# 70차 FB — 69차 ED 가 받아 둔 Ellsworth 색인을 표적 목록에 맞춰 돌린다

69차 ED 가 벤더 열다섯의 색인을 통째로 받아 `out_ed/indexes/` 에 17 파일로 남겼고,
그중 가장 큰 것이 **Ellsworth Document Library(EDL)** 다 — 다중 벤더 24,113 고유 (문서·언어)쌍 · 발행처 1,407.
이 배치는 **네트워크를 다시 치지 않고 그 8.9 MB 를 표적 목록에 로컬로 맞춰** 돌린 뒤, 걸린 문서만 받아 9절을 읽었다.

표적은 `role=product` 인데 `physical.density` 가 비어 있는 재료 **107종**이다
(69차 ED 가 셀 때 114종이었고 그 사이 7칸이 닫혔다).

---

## 1. 색인 매칭 수확표 — 이게 핵심 수치다

| 단계 | 수 | 무엇을 셌나 |
|---|---|---|
| 표적 | **107종** | `role=product` · `physical.density` 없음 |
| 표적의 제조사가 EDL 발행처 1,407 중에 **있는** 것 | **17종** | Zymet · Cytec/Solvay · 3M · DuPont Teijin Films · Permabond · Rogers · Taiyo America · Dow · Von Roll Isola |
| 그중 **등급 또는 그 계열 문서가 색인에 실제로 걸린** 것 | **6종** | 591 · 737 · 1109 · 2389 · 2418 (등급·계열 적중 5) + 2254 (같은 제조사의 **다른 상표** Mylar A 만 적중 — §4 에서 기각) |
| 내려받아 연 문서 | **11건** | SDS 7 · TDS 4 (전부 `webaps.ellsworth.com/edl/Actions/?document=<id>`, 무인증 200) |
| 그중 밀도·비중을 **실수로 찍은** 것 | **6건** | (+ TDS 1건이 미경화 A/B 액의 `lb/gal` 순중량만) |
| **값을 넣은 재료** | **3종 · 5행** | 밀도 3종 4행 + 점도 1종 1행 |
| **선 카드** | **1장** | `*MAT_GENERAL_VISCOELASTIC (076, 4항)` — Zymet X6-82-5LV50 |
| 판정 갱신 | **14종** | 철회 3 · 보강 11 |

**중요 — 유통사 색인의 진짜 값어치는 '찾은 것' 이 아니라 '못 찾았음을 전수로 증명한 것' 이다.**
EDL 24,113 항목에서 토큰 적중 0건을 확인한 표적 등급: `melinex` · `getek` · `ro4350` · `ro4003` · `fr408` ·
`cyclotene` · `anisolm` · `esp110` · `pdm-1` · `abf` · `agl-1020` · `5250-4` · `h23008` · `xp-3` · `panlite` ·
`u-8437` · `alx-2` · `yph-160` · `kgk-200` · `af-130`. **전부 0건이다.**
발행처 목록에 아예 없는 제조사도 셌다 — Hexcel · Ajinomoto · Hitachi/Resonac · Doosan · Kyodo Giken ·
Lamics · Asahi Glass · Sekisui · Kunshan Yubo · Fujikura · Hyperion · Osaka Gas · Conoco · BP-Amoco ·
Yangzi · General Electric · SABIC · Isola Group **전부 0**.

### 발행처 이름이 같아도 다른 회사·다른 사업부다 — 함정 셋
69차 ED 가 Permabond ESP110 을 Henkel Ireland 의 동명 제품과 헷갈릴 뻔한 것과 같은 자리가 셋 더 나왔다.

| EDL 발행처 | 겉보기 | 실제 | 표적 |
|---|---|---|---|
| `Von Roll Isola USA, Inc.` | Isola FR408·GETEK 인 줄 안다 | **다른 회사다** — 항목 6건이 전부 전기절연 바니시·솔더킷(`7031 Insulating Varnish` · `3022 E Solder Kit` · `EB-41` · `E-kote 3030`). PCB 라미네이트 0건 | 1273 · 1274 |
| `Rogers Corporation` | RO4350·RO4003 인 줄 안다 | **엘라스토머·테이프 사업부다** — 항목 14건이 전부 `Poron` · `Bisco Silicone` · `MOX-TAPE` · `HT-800`. 고주파 회로재 0건 | 1277 · 1278 |
| `Taiyo America, Inc.` | PDM-1·PDM-4 인 줄 안다 | **솔더레지스트·잉크뿐이다** — 항목 9건이 `PSR-4000` 3계열 · `UVR-150` 2건 · `S-222NA` · `HD-3` · RoHS 총괄. 감광성 드라이필름 유전체 0건 | 984 · 985 |

**유통사 색인은 발행처 이름이 아니라 발행처의 *제품 목록*을 열어 봐야 한다.**

---

## 2. 가장 중요한 발견 — **§131 의 나머지 반쪽을 정정한다. Solvay/Cytec 은 SDS 를 웹에 두고 있고 그 SDS 는 밀도를 찍는다**

카탈로그의 오래된 판정 두 줄이 이번에 깨졌다.

| 깨진 진술 | 누가 세웠나 | 무엇이 깼나 |
|---|---|---|
| *"구조용 필름접착제는 밀도를 인쇄하지 않는다(§131)"* | 46차 HD (TDS 를 열고) | **TDS 에 대해서는 여전히 맞다. SDS 는 찍는다.** 69차 ED 가 3M 에서 반쪽(AF 131-2 = 0.96 · AF 191 = 1.26)을 정정했고, 이 배치가 Solvay/Cytec 에서 나머지 반쪽을 정정한다 |
| *"Solvay(현 Syensqo)는 SDS 를 웹에 두지 않는다 — 계정 메일 자동발송뿐이다"* | 69차 ED (sitemap 4,025 URL · CDX PDF 3,209 을 훑고) | **자사 사이트에는 없는 것이 맞다. 유통사가 제조사 자사 PDF 를 무인증으로 서빙한다.** `FM(R) 300 Adhesive Film` SDS 0001535 · `FM(R) 73 M Adhesive Film` SDS 0001202, 둘 다 2017-02-05 자 Cytec 원본 |
| *"Zymet 사는 없어져 시트를 구할 길도 없다"* | 57차 SA | **Zymet 은 살아 있다.** `zymet.com` HTTP 200 · `(c) 2005-2024 Zymet` · 제품군 12쪽 sitemap. 등급별 TDS 는 웹에 없지만 **EDL 이 자사 SDS 를 서빙한다** |

**교훈 — '제조사 사이트에 없다' 는 '웹에 없다' 가 아니다.**
ED 가 "요청제라 아무리 파도 웹에 없다" 로 닫은 벤더 여섯 중 **둘을 유통사 색인으로 다시 물었다** —
**Solvay/Cytec 은 문서가 나와 값 셋이 섰고**, Permabond 는 반대로 **부재가 두 번째 독립 색인에서 확정됐다**(§7-나).
어느 쪽이든 판정이 한 단계 단단해진다. 다음 파동은 **요청제 벤더를 만나면 곧바로 유통사 색인으로 우회해라.**

### 그리고 부재의 원인에 **일곱째 축**이 생겼다 — 지역판
69차 ED 는 부재의 원인을 벤더별로 다섯 갈래로 갈랐다(두산=템플릿 · Senju=연도 · 3M=제품 · Rogers·Isola=정책 · 여섯 벤더=요청제).
Solvay/Cytec 은 **어느 갈래도 아니고 지역판으로 갈린다.**

| 같은 벤더 · 같은 갈래 | 9절 밀도 칸 |
|---|---|
| 미국 Cytec 템플릿 `FM(R) 300 Adhesive Film` SDS 0001535 (2017-02-05) | **`Specific Gravity/Density:  1.3 -  1.4-`** |
| 미국 Cytec 템플릿 `FM(R) 73 M Adhesive Film` SDS 0001202 (2017-02-05) | **`Specific Gravity/Density:  1.16`** |
| EU/UK 템플릿 `FM(R) 300-2 ADHESIVE FILM` (2023-08-25, *Transition document following UK exit from the EU*) | `Density  No data available` · `Relative density  No data available` |

**연도로도(2017 vs 2023) 설명이 되지만 템플릿이 아예 다른 규격이다** — 미국 OSHA HCS 서식은
`Specific Gravity/Density` 한 칸이고 EU CLP 서식은 `Density` / `Relative density` 두 칸인데 후자를 비운다.
**다음 파동의 표적은 '옛 날짜' 도 '구판' 도 아니라 「미국판 SDS」다.**

---

## 3. 넣은 값 — 3종 5행

| 재료 | 키 | 값 | 등급 | 근거 (9절 verbatim) |
|---|---|---|---|---|
| **737 Zymet X6-82-5LV50** | `physical.density` | **1650 kg/m³** | t3 | Zymet `X6-82-5LV` SDS v005 (2020-04-29) — `Specific Gravity  1.65 g/cc` |
| **737** | `rheological.viscosity` | **20.0 Pa·s** | t3 | 같은 9절 `Viscosity  20,000 cps` |
| **591 FM300K** | `physical.density` | **1300 / 1400 kg/m³** (2행) | t3 | Cytec `FM(R) 300 Adhesive Film` SDS 0001535 (2017-02-05) — `Specific Gravity/Density:  1.3 -  1.4-` |
| **1109 FM-73** | `physical.density` | **1160 kg/m³** | t3 | Cytec `FM(R) 73 M Adhesive Film` SDS 0001202 (2017-02-05) — `Specific Gravity/Density:  1.16` |

### 세 값 모두 t3 인 이유 — 등급이 한 칸씩 어긋난다
브리프의 t1 정의는 *"그 등급에 인쇄된 값"* 이다. 셋 다 그 조건을 못 채운다.

| 재료 | 문서가 적은 등급 | 우리 표적 등급 | `grade_scope` 에 적은 것 |
|---|---|---|---|
| 737 | `X6-82-5LV` | `X6-82-5LV50` (Chhanda 2012 원문 verbatim) | 꼬리 `50` 이 무엇인지 **두 문서 어디에도 인쇄되지 않았다.** 충전율·점도 코드라고 추정하지 않았다 |
| 591 | `FM(R) 300 Adhesive Film` (계열 한 장) | `FM300K` | 3절이 `May be supplied on one of the following carrier(s):` 로 캐리어 변종을 한 문서로 덮는다. 다만 9절 `Color: green` 이 범위를 좁힌다 — 벤더 TDS Table 1 에서 green 은 **FM 300K · 300M · 300U** 이고 FM 300(tight knit)만 blue 다 |
| 1109 | `FM(R) 73 M` (매트 캐리어 변종) | `FM-73` (Thiedmann 1987 이 캐리어를 안 적는다) | **이 재료의 전단강도 4행이 이미 같은 근거로 t3 + `grade_measured`/`grade_target` 을 달고 있다.** 그 관례를 그대로 따랐다 |

### 검산
- **Zymet 1.65 g/cc** — 3절 `Silica 45-75 wt%` · 에폭시 2종. 실리카 2.2 를 60 wt%, 에폭시 1.16 을 40 wt% 로 놓으면
  1/ρ = 0.6/2.2 + 0.4/1.16 = 0.6175 → **1.62 g/cc**. 인쇄값과 2 % 안에서 닫힌다.
- **FM 73M 1.16 vs FM 300 1.3-1.4** — 서로가 서로의 검산이다. FM 73M 은 3절에 무기 충전재도 할로겐도 없는
  고무변성 에폭시라 무충전 에폭시 대역(1.15~1.20)에 정확히 들고, FM 300 은 `Modified polymer
  (halogenated aromatic glycidyl ether) 50 - 75 %` 라 브롬화 에폭시가 절반 이상이어서 뚜렷이 무겁다. **조성이 값의 차이를 설명한다.**
- **환산** — Zymet 은 `g/cc` 단위가 인쇄되어 물밀도를 곱하지 않았다. Cytec 두 건은 단위 없는
  `Specific Gravity/Density` 라 무차원 비중으로 읽고 **기준온도가 인쇄되지 않아 물밀도 1000 을 쓴 뒤 그 사실을 conditions 에 적었다.**

### 세 값 모두 **미경화** 상태의 것이다 — `physical_form` 에 못박았다
- 737 — `Physical state Liquid` · `Color Cream` (단, 1액형이고 3절에 휘발성 용제가 한 줄도 없다)
- 591 · 1109 — `Appearance: film` · `Flash Point: Not applicable` (캐리어가 든 미경화 접착필름. FM 73M 은 잔류 MEK 1.2~1.5 wt%)

---

## 4. 액상·미경화라 버린 것 — **문서 4건 · 인쇄값 6개**

| 문서 | 찍힌 값 | 왜 버렸나 |
|---|---|---|
| **3M DP100 Clear 캐나다판 SDS** (11-3180-4 v16.05, 2022-06-07) | `Density 1.15 g/ml`(A) · `1.17 g/ml`(B) | **2액형의 A액·B액 각각**이다. 69차 ED 가 미국판에서 읽은 것과 같은 수라 판정을 재확인만 했다 |
| **3M DP100NS 캐나다판 SDS** (11-2403-1 v14.00, 2018-06-27) | `Density 1.15 g/ml`(A) · `1.18 g/ml`(B) | 같음 |
| **3M DP100NS TDS** (2024-06) | `Base Net Weight 9.6 - 10.0 lb/gal` · `Accelerator Net Weight 9.2 - 9.6 lb/gal` | `Typical **Uncured** Physical Properties` 표의 행이다. 환산하면 1150~1198 · 1102~1150 kg/m³ 로 **위 SDS 액상값과 정확히 일치한다** — 즉 같은 물건이고 경화물이 아니다. 같은 TDS 의 `Typical Cured Characteristics` 표에는 압축강도·Shore D 만 있고 **밀도 행이 없다** |
| **Cytec `FM(R) 300-2 Adhesive Red` SDS 0059418** (2017-11-21) | (없음) | 9절이 `Appearance: liquid` · `Percent Volatile ~16(methyl ethyl ketone)` · 1절 `Intended/Recommended Use: **Intermediate**` — **필름이 아니라 바니시 중간체**다. 밀도 칸도 `Not available` 이라 가져올 값도 없었다 |

**액상이라고 무조건 버리지는 않았다 — 갈린 자리는 「2액형인가」다.**
DP100 은 A액·B액이 따로 기술되고 혼합비가 9절에 없어 경화물 밀도를 만들 길이 없다(역산 금지).
Zymet X6-82-5LV 는 **1액형**이고 3절에 용제가 없어 액 자체가 곧 모재다 — 68차 DA·69차 ED 가 Ablebond 965-1L 에서 쓴 근거와 같아
`physical_form: liquid, as supplied (uncured)` 로 적고 넣었다.

### 형태·상표가 달라 버린 것 — 1건
| 문서 | 찍힌 값 | 왜 버렸나 |
|---|---|---|
| **DuPont Teijin Films `Mylar(R) A Polyester Film` Article Information Sheet v2.8** (2016-04-26) | `Density: 1.23 - 1.41 g/cm3` | EDL 의 `DuPont Teijin Films` 항목은 **단 한 건**이고 그게 이것이다. 표적 2254 는 **Melinex** 50 µm 광학등급 무코팅 필름이다. ㉠ 상표가 다르다 ㉡ 같은 절이 `Colour: various` 라 스스로 밝히듯 **1.23-1.41 은 안료·보이드 함유판까지 덮는 계열 폭**이다(순수 이축연신 PET 는 1.39~1.40 한 점). 하한 1.23 은 보이드가 든 등급이 아니면 나올 수 없다. 69차 ED 가 2009 판을 버린 논지와 같다 |

---

## 5. 같은 등급의 두 숫자가 다른 물건이었던 사례 — **세 얼굴이 나왔다**

브리프가 예고한 '동박 포함/미포함' 함정(69차 ED, 두산 CCL)이 이 갈래에서 **다른 얼굴 셋**으로 나왔다.

### (가) SDS 의 밀도 ≠ TDS 의 면적중량÷두께 — FM300K
| 출처 | 수 | 무엇인가 |
|---|---|---|
| SDS 0001535 9절 | **1300~1400 kg/m³** | 재료의 밀도 |
| TDS(AEAD-00002 Rev 01, 2011-08-12) Table 1 `FM 300K \| 0.05 psf (244 gsm) \| 0.008 in (0.20 mm)` | 244 ÷ 0.2032 mm = **1201 kg/m³** | **필름의 겉보기 면적밀도** |
| 같은 표 `FM 300K \| 0.08 psf (390 gsm) \| 0.013 in (0.32 mm)` | 390 ÷ 0.3302 mm = **1181 kg/m³** | 같음 |

**10~15 % 어긋난다.** 그리고 결정적으로 — 같은 표의 **FM 300 두 행끼리도 서로 안 맞는다**
(0.08 psf/0.013 in = 1181 vs 0.10 psf/0.015 in = 1286, **9 % 차**). `nominal thickness` 가 0.001 in 단위 반올림이고
면적중량 공차가 `± 0.005 psf (± 25 gsm)` 이기 때문이다.
**면적중량÷두께는 밀도가 아니다 — 계산값을 넣지 않았다.** 브리프의 '역산 금지' 가 여기서 값을 살렸다.

### (나) 필름접착제 TDS 의 `Density` 행은 **그 시트 안의 다른 제품** 행이다 — 세 시트에서 같은 모양
| 시트 | `Density` 행 | 실제로 누구 값인가 |
|---|---|---|
| `Solvay_FM300_AdhesiveFilm_TDS_2018-06-14.pdf` | `7.3 lbs/gal (875 g/L)` | **BR(R) 127 부식방지 프라이머** Table 3 |
| `Solvay_FM73_FilmAdhesive_TDS.pdf` | `7.3 lb/gal (875 g/L)` | 같음 (46차 HD 가 이미 정정) |
| `Cytec FM(R) 47 Adhesive TDS` (2006-03-28, `item_id 61911`) | `Weight 7.85 lb/gal Nominal` | **FM 47 Liquid Adhesive** — 같은 시트의 필름 행들은 `psf (kg/m²)` 면적중량만 준다 |

**세 시트가 같은 모양이다.** 필름 행에는 밀도가 없고, 시트에 하나 있는 밀도는 언제나 **곁들이 액상 제품**의 것이다.
§131 은 이 구조를 정확히 짚은 규칙이었고 **TDS 에 대해서는 지금도 유효하다.**

### (다) 색인의 이름과 문서의 이름이 다르다 — 제일 위험한 함정
EDL 색인이 `FM 300U` 라 부르는 `item_id 40941` 을 받아 보니 **문서 제품명은 `FM(R) 300 Adhesive Film`**(계열 문서)이었다.
`FM 300U` 만 보고 "무지지 필름이니 우리 knit 등급과 다르다" 며 안 열었으면 이 배치의 값 절반을 놓쳤다.
**유통사 색인의 `name` 은 유통사의 상품명이지 문서의 제품명이 아니다 — 반드시 열어서 1절을 읽어라.**

---

## 6. 카드 — 1장이 섰다

라이브 DB 사본(`VACUUM INTO`)에 이번 값을 넣고 카드 생성기를 돌려 확인했다.

| 재료 | 결과 |
|---|---|
| **737 Zymet X6-82-5LV50** | **`*MAT_GENERAL_VISCOELASTIC (076, 4항)` 생성됨** |
| 591 FM300K | 막힘 — `영률 없음(카드 생성 불가)` |
| 1109 FM-73 | 막힘 — `영률 없음(카드 생성 불가)` |

넣기 전 737 의 생성기 사유가 이랬다 — verbatim:
`밀도 없음(카드 생성 불가) · **Prony 4항이 준비돼 있다** — *MAT_076은 영률을 쓰지 않으니 **밀도만** 채우면 바로 나온다`.
**밀도 한 칸이 Prony 4항짜리 점탄성 덱 하나를 세웠다.**

---

## 7. 못 넣은 것 — 셋으로 갈라 적는다

### (가) 문서를 열었는데 밀도가 없었다 — 문서 4건
| 문서 | verbatim |
|---|---|
| Cytec `FM(R) 300-2 Adhesive Red` SDS 0059418 (2017-11-21) | `Specific Gravity/Density:  Not available` (게다가 `Appearance: liquid` 인 중간체) |
| Cytec `FM 300` TDS (2011-08-12) · Solvay `FM 300` TDS (2018-06-14) · Solvay `FM 73` TDS · Solvay `FM 300-2` TDS (`item_id 40946`) | 필름 행에 밀도 없음. 시트의 `Density 7.3 lbs/gal (875 g/L)` 는 전부 **BR(R) 127 프라이머** Table 3 행 |
| Cytec `FM 47` TDS (2006-03-28) | 필름 행은 면적중량만. `7.85 lb/gal` 는 FM 47 **액상** 접착제 행 |
| 3M `DP100NS` TDS (2024-06) | `Typical Cured Characteristics` 표에 밀도 행 없음 |

### (나) 색인에 그 등급이 없었다 — 표적 12종 (제조사는 색인에 있는데 등급이 없는 것)
| 표적 | 제조사가 색인에 있나 | 등급 적중 |
|---|---|---|
| 1110 AF-130 | 3M ✓ (1,362건) | **0** — 3M 의 `AF<숫자>` 는 AF-111 · AF42 · AF 126FR · AF 126-2/3 · AF 163-2 · AF 3024 여섯 갈래뿐 |
| 1658 Permabond ESP110 | Permabond ✓ (284건 전수 열거) | **0** — ES5xx 1액형 · ET5xxx 2액형뿐. 69차 ED 의 자사 미디어 5,964건 결과와 **독립적으로 일치** → 단종 확정 |
| 984 · 985 Taiyo PDM | Taiyo America ✓ (9건) | **0** — PSR-4000·UVR-150·S-222NA·HD-3 뿐 |
| 1273 · 1274 Isola FR408 · GETEK | `Von Roll Isola` ✓ (**다른 회사**) | **0** |
| 1277 · 1278 Rogers RO4350 · RO4003 | Rogers ✓ (**다른 사업부**) | **0** |
| 618 · 619 Cytec 5250-4-RTM | Cytec ✓ (50건) | **0** — Dapco/Conap 항공 실런트 + FM 필름 몇 갈래뿐. `cycom` 은 Cycom 3001 한 건 |
| 1360 Photo-BCB (Dow Cyclotene) | Dow ✓ (1,166건) | **0** — `cyclotene`·`benzocyclo`·`bcb` 전부 0 |
| 2254 Melinex | DuPont Teijin Films ✓ (**1건뿐**) | **0** — 그 1건은 Mylar A(§4 에서 기각) |

### (다) 제조사가 색인에 아예 없다 — 발행처 1,407 중 0건
Hexcel(1652 · 1653) · Ajinomoto(978~983 · 1241) · Hitachi Chemical/Resonac(1098 · 1291 · 1430) ·
Doosan(2461 · 2462 · 2463 · 2480 · 2483 · 2486 · 2509) · Kyodo Giken(740) · Lamics(1352) ·
Asahi Glass(1358 · 1359) · Sekisui(1315) · Kunshan Yubo(1300) · Fujikura(2588) · Hyperion(2015) ·
Osaka Gas(2027) · Conoco(2031) · BP-Amoco(2032) · Yangzi(1462) · General Electric · SABIC · Isola Group.
**EDL 은 미국 접착제·실런트·전자조립 유통 채널의 색인이라 라미네이트·필름·배터리·금속 갈래가 원리상 없다.**

### (라) 등급명이 없어 색인 매칭 대상 자체가 아니다 — 48종
69차 ED 가 센 48종(논문이 제품명을 인쇄하지 않은 연구 시편)이 그대로다. 판정을 건드리지 않았다.

---

## 8. 산출물

| 파일 | 내용 |
|---|---|
| `out_fb/fb04_materials.json` | 값 **3종 5행** (밀도 3종 4행 · 점도 1종 1행) |
| `out_fb/fb05_verdicts.json` | 판정 **14종** — 철회 3(737 · 591 · 1109) · 보강 11. 옛 판정문 전문을 보존하고 `**[70차 FB …]**` 문단을 앞·뒤에 붙였다 |
| `out_fb/gen_fb04_materials.py` · `gen_fb05_verdicts.py` | 위 둘의 생성기 |
| `/data/paper_patent_corpus/standards_appnotes/sds/` | SDS 7건 추가 → 누계 **81건** |
| `/data/paper_patent_corpus/standards_appnotes/adhesive/` | TDS 2건 추가 (`Cytec_FM300_AdhesiveFilm_TDS_2011-08-12.pdf` · `3M_ScotchWeld_DP100NS_TDS_2024-06.pdf`) |

새로 남긴 SDS 7건 —
`Zymet_X6-82-5LV_SDS_2020-04-29.pdf` ·
`Solvay-Cytec_FM-300-Adhesive-Film_SDS_2017-02-05.pdf` ·
`Solvay-Cytec_FM-73M-Adhesive-Film_SDS_2017-02-05.pdf` ·
`Solvay-Cytec_FM-300-2-Adhesive-Red_SDS_2017-11-21.pdf` ·
`DuPont-Teijin-Films_Mylar-A-Polyester-Film_AIS_2016-04-26.pdf` ·
`3M_DP100-Clear_SDS_2022-06-07_ca.pdf` · `3M_DP100NS-Translucent_SDS_2018-06-27_ca.pdf`.

**DB 에는 아무것도 쓰지 않았다.** 예행과 사본 리허설만 돌렸다.

```
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  .venv/bin/python scripts/catalog/ingest_agent_json.py   scripts/catalog/out_fb/fb04_materials.json   # [DRY-RUN] ok 5
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  python3        scripts/catalog/apply_core_verdicts.py scripts/catalog/out_fb/fb05_verdicts.json    # [예행] 병합 14 · 재료 14
# 사본 리허설(VACUUM INTO 사본에 --apply → 카드 생성기·정합성검사 → 사본 삭제)
#   → *MAT_GENERAL_VISCOELASTIC (076, 4항) 1장 · integrity_check 신규 이상 0
```

※ `out_fb/` 에는 8월 19일자 다른 배치의 `fb01`~`fb03` 이 이미 있었다(커밋됨). 덮지 않으려고 번호를 `fb04`·`fb05` 로 이어 붙였다.
※ `ingest_agent_json.py` 는 `MATERIALTWIN_DATA_DIR` 을 줘도 `[DB] sqlite:////data/appdata/materialtwin_web/materialtwin.db`
   (낡은 개발 DB)를 연다 — 69차 ED 때와 같다. **스키마·단위·범위 검사는 유효하지만 그 도구의 DB 경로를 믿지 마라.**
   재료명 대조는 라이브 DB 에서 뽑은 문자열을 그대로 썼고, 값 적용 리허설은 라이브 사본에서 따로 했다.

---

## 9. 다음 파동에 넘길 것

### ㉠ 요청제 벤더를 만나면 곧바로 유통사 색인으로 우회해라 — 이 배치가 그것으로 값을 얻었다
ED 가 "웹에 없다" 로 닫은 여섯(Hexcel · Senju · Permabond · Solvay · Teijin · Taiyo) 중 **Solvay 가 이 경로로 열렸다.**
아직 안 해 본 유통사 색인:
- **Master Bond**(EDL 109건) · **Epoxy Technology**(EDL 다수) · **Indium**(90건) · **Namics**(EDL 에 `U8410-99-1F Underfill` TDS 가 있다)
  — 표적은 아니지만 **언더필·다이어태치 갈래의 벤더가 EDL 에 더 있다.**
- EDL 형제 엔드포인트 두 개가 아직 안 받아졌다 — `/api/literature/search`(712건) · `/api/site/search`(381건).
- **다른 유통사**를 같은 방식으로 훑어라. Digi-Key · Mouser · RS · Farnell 은 전자부품 SDS/TDS 를 같은 구조로 서빙한다.
  Hexcel · Ajinomoto 는 항공·반도체 유통사(예: Composites One · 상사 채널)를 뒤져야 나온다.

### ㉡ 표적을 「미국판 SDS」로 좁혀라
EU/UK CLP 서식은 `Density` / `Relative density` 두 칸을 비우고, 미국 OSHA HCS 서식은 `Specific Gravity/Density` 한 칸을 채운다.
같은 벤더·같은 제품에서 이 차이가 났다(§2). **문서를 고를 때 `region=1`(미국) 판을 먼저 열어라.**

### ㉢ 색인의 이름을 믿지 말고 1절을 읽어라
`FM 300U` 로 색인된 문서가 실제로는 `FM(R) 300 Adhesive Film` 계열 문서였다(§5-다).
반대로 발행처 이름이 같아도 다른 회사·다른 사업부인 경우가 셋 나왔다(§1).
**색인은 후보를 좁히는 도구지 동정하는 도구가 아니다.**

### ㉣ 아직 안 닫힌 표적 — 이 배치가 확인한 상태
| 표적 | 상태 |
|---|---|
| **2254 Melinex** | EDL 에 `melinex` 0건. DTF 항목은 Mylar A 한 건뿐이고 계열 폭이라 못 쓴다. **아직 문서를 못 열었다** |
| **1110 AF-130** | 3M 자사 경로에서 `Density No Data Available` 확인 완료(69차 ED). 유통사 색인에도 다른 판이 없다. **닫힌 판정** |
| **1658 ESP110** | 제조사 색인 5,964건 · 유통사 색인 284건 **양쪽 0건** → 단종 확정. **다시 파지 마라** |
| **984 · 985 PDM** | 다섯 색인 전부 0건. `SDSinfo@taiyo-america.com` 창구뿐 |
| **618 · 619 CYCOM 5250-4-RTM** | Cytec 이 EDL 에 있는데도 이 등급은 0건. 항공 프리프레그는 접착제 유통 채널에 없다 |
| **591 · 1109** | 밀도는 닫혔다. **이제 막는 것은 영률이다** — 카드가 안 서는 유일한 이유다(§6) |

### ㉤ 미경화/경화 형태 차이를 언젠가는 정면으로 처리해야 한다
이번에 넣은 세 밀도는 전부 **미경화** 값이고 논문이 잰 것은 경화물이다. 지금은 `conditions.physical_form` 으로
사실만 남겨 두었다. 필름접착제는 휘발분이 1 % 미만이라 차이가 작고, 1액형 언더필은 경화수축 몇 %가 전부다.
**그러나 이 차이를 `conditions` 에만 두면 대표값 선택이 그것을 못 본다.**
경화수축률(`mechanical.cure_shrinkage`) 키가 이미 있으니, 같은 벤더 시트에서 그 값을 얻으면
미경화→경화 보정을 t4 로 계산해 둘 수 있다. **이번엔 하지 않았다 — 어느 문서도 경화수축을 찍지 않았다.**
