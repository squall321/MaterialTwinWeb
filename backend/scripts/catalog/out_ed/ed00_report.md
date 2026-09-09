# 69차 ED — 벤더 SDS 색인을 통째로 받아 전수로 읽는다

68차 DA 가 SDS 19건을 열어 7건에서 밀도를 얻고 카드 한 장을 세우면서 기법 셋을 남겼다.
① 두산 공개 MSDS 120건 전수 스캔 ② 벤더 SDS 색인을 REST 로 통째로 받는 기법 ③ 단종 등급의 옛 SDS.
이 배치는 그 셋을 **벤더 열여섯으로 규모를 키워** 실행했다(그중 열다섯은 색인을 통째로 받았다).

표적은 `role=product` 인데 `physical.density` 가 비어 있는 재료 **전체 114종**이고,
그중 **등급명이 특정된 상용품 66종**이 SDS 로 찾을 수 있는 갈래다(나머지 48종은 논문이 제품명을 안 찍은 연구 시편이라
SDS 경로가 원리상 닫혀 있다 — 판정을 건드리지 않았다).

---

## 1. 벤더별 색인 수확표 — 이게 핵심 수치다

| 벤더 | 색인을 어떻게 통째로 받았나 | 색인 규모 | 9절까지 편 SDS | 밀도·비중에 실수를 찍은 것 |
|---|---|---|---|---|
| **Doosan 전자소재** | `POST /rest/product/msds/list` → `GET /file/productAttachment/download/<id>` (무인증) | 제품 **120** · 첨부 **183** · 고유 파일 **181** | **181 (전수)** | **22** (제품값 21 · 성분값 1) |
| **Ossila** | Shopify `products.json?limit=250&page=N` 6쪽 | 상품 **1,258** | **7** | **0** (융점은 6건) |
| **Rogers** | 제품 페이지 HTML + web.archive CDX (sitemap·API 둘 다 없음) | EHS 경로 **148** · `/msds/` **119** | **8** (7개정 × 5언어) | **0** |
| **Isola** | sitemap 의 `documentation` 포스트타입 | 문서 **206** · SDS 페이지 **51** · 첨부 **868** | **6** (FR408 3세대 + 프리프레그 + GETEK 2판) | **0** |
| **3M** | `POST searchapi.3m.com/search/3mcom/v1/search` + 아카이브 제품페이지에서 `mwsId` 추출 → `multimedia.3m.com` | 구조용 필름접착제 카테고리 **48 제품 ID** | **9** (필름 5 + DP100 4) | **6** (필름 2 · DP100 액상 4) |
| **Permabond** | `GET /wp-json/wp/v2/media?media_type=application&page=1..60` | 미디어 **5,964** (= 올린 모든 PDF) | **0** (표적이 색인에 없음) | — |
| **Hexcel** | `GET /wp-json/wp/v2/media` (`X-WP-Total: 1886`) + CDX PDF 전수 | 고유 미디어 **1,814** · PDF **1,389** · 아카이브 PDF **2,886** | **1** (2005 섬유 MSDS) | **1** |
| **Solvay / Syensqo / Cytec** | Syensqo sitemap + 옛 cytec.com CDX | sitemap **4,025 URL** · 제품 **2,012** · 아카이브 PDF **3,209**(MSDS 1,368, 전부 화학 BU) | **1** (형제 등급 FM 300-2) | **0** |
| **DuPont Teijin Films / Teijin** | `mylar.com` `/wp-json/wp/v2/media` + 옛 SDS 색인 페이지 아카이브 | 고유 미디어 **521** · PDF **293** · 역사적 SDS 색인 **5항목** | **9** (Tetoron 3 · Teonex 2 · Mylar 2 · PET 칩 1 · Panlite 1) | **9** |
| **Henkel** | 색인 미확보(SDS 포털이 요청·로그인제) — 문서를 개별 확보했다 | — | **3** | **3** |
| **KOKI** | 옛 `koki.org` CDX → `pdf/BL/sd_-_*.pdf` | 아카이브 URL **410** · SDS **11** | **3** | **3** |
| **Senju** | sitemap 982(ja) + 694(en) + CDX | SDS **0** (요청제) | **2** (유통사 호스팅) | **1** |
| **Taiyo (太陽)** | sitemap 1,892 + CDX 9,614 + CDX 2,277→PDF 285 + 라이브러리 검색 API | 색인 **넷** | **0** (표적이 색인에 없음) | — |
| **Ajinomoto Fine-Techno** | Yoast `sitemap.xml` → `page-sitemap.xml` (**전 사이트**) + WP 미디어 REST | 페이지 **75** · 미디어 PDF **1** | **0** (사이트에 SDS 자체가 없음) | — |
| **Hitachi Chemical (현 Resonac)** | web.archive CDX `products/sds/` | URL **238** · SDS PDF **98** | **0** (표적 갈래가 색인에 없음) | — |
| **Lumtec** | sitemap | MSDS PDF **211** (전부 404) | **1** | **0** |

**벤더 열다섯의 색인을 통째로 받았고 그 사본을 `out_ed/indexes/` 에 파일 17개로 남겼다.**

| | 68차 DA | **69차 ED** |
|---|---|---|
| 색인을 통째로 받은 벤더 | 1 (두산, 제품 단위 120) | **15** |
| 9절까지 편 SDS·MSDS (두산 전수 제외) | 19 | **50** |
| 그중 밀도·비중에 실수를 찍은 것 | 7 (37 %) | **23** (46 %) |
| 두산 색인 문서 단위 전수 스캔 | — | **181건** (그중 실수 22) |
| 코퍼스에 남긴 SDS·MSDS 누계 | 19 | **74** (이번에 55건 늘렸다) |

다음 파동은 이 파일들을 다시 긁을 필요가 없다.

**색인을 못 여는 벤더는 이유가 하나로 수렴한다 — 요청제다.**
Hexcel(`SDSUSOffice@Hexcel.com`), Senju(영업담당·문의폼), Permabond(Gravity Form), Solvay(계정 메일 자동발송, 자기 문서로
*"activated for 99.98 % of Solvay sales"* 라 밝힌다), Teijin(개인정보 등록 CGI), Taiyo(`SDSinfo@taiyo-america.com`).
**이 여섯은 아무리 파도 웹에 없다** — 판정에 그 이유를 적어 다음 파동이 다시 안 파게 했다.

## 2. 가장 중요한 발견 — DA 의 가설을 181건으로 재고 **정정한다**

DA 는 *"SDS 는 최신판일수록 물성을 덜 찍는다 — 다음 파동은 옛 판을 찾아라"* 로 끝냈다.
두산 181건을 전수로 세니 **원인은 개정 연도가 아니라 템플릿**이다.

| 템플릿 | 문서 수 | 비중에 실수를 찍은 것 | 비율 |
|---|---|---|---|
| **구판** — `SPECIFIC GRAVITY : (Water=1.0) …` (제품 단위 한 칸) | 21 | **21** | **100 %** |
| **신판 GHS** — `N. Specific gravity` (CAS 성분 열) | 160 | **1** | **0.6 %** |

그 신판 1건(DSF-900SQ, 2023-04-11)조차 `1.33 - 1.45 g/cm3` 가 **첫 열 CAS 25038-59-9(PET) 의 성분값**이지
제품값이 아니다. 즉 신판이 제품 밀도를 찍은 사례는 **160건 중 0건**이다.

연도로 세면 이 구조가 안 보인다 — 2022년 33건 중 5건, 2025년 42건 중 **12건**으로 오히려 늘어난다.
**구판 템플릿이 2025-11-13 자 DS-7409DV (N) 까지 아직 발행되고 있기 때문**이다.
그러니 다음 파동의 표적은 *"옛 날짜"* 가 아니라 *"제품 단위 9절을 쓰는 문서"* 다.

**그리고 이 규칙은 두산 안에서만 성립한다.** 이번에 다른 벤더에서 반례를 둘 찾았다.
- **Rogers** — GHS 이전 템플릿인 2009-05-12 판도 `SPECIFIC GRAVITY: NA (Water = 1)` · `DENSITY: NA` 로 비어 있다.
- **Isola** — 1998년까지 거슬러 올라가는 구판(Chemistry & Industrial Hygiene 템플릿, 2010-02-12 개정)도 `Specific Gravity: Not Determined` 다.

두 벤더 다 2절에 이유를 적는다 — 제품이 SDS 의무 대상이 아닌 **성형품(article)** 이라 9절을 채울 의무가 없다.

**세 번째 갈래도 나왔다 — 3M 은 템플릿도 연도도 아니고 제품마다 갈린다.**
같은 3M 구조용 필름접착제 갈래에서 **AF 131-2**(2015-03-24)가 `Density .96 g/cm3 [@ 20 ºC]` 를,
**AF 191**(2024-09-20)이 `Density 1.26 g/cm3` 를 찍는데, **AF 130-2**(2019-01-14) · AF 30(2018) · AF 126-2(2025)는 비운다.
연도로도 템플릿으로도 설명이 안 된다.
**그리고 이것이 브리프 §131 을 정정한다** — *"구조용 필름접착제 시트는 밀도를 인쇄하지 않는다"* 는
**TDS 에만 맞고 SDS 에는 틀리다.**

**Senju 는 DA 의 원래 가설(옛 판이 더 찍는다)을 그대로 보여 준다** — 같은 벤더 같은 제품군에서
2015-10-29 판이 `Specific gravity: Product 7.4(Solder)` 를 찍는데 2023-11-06 EU 판은 `Density and/or relative
density  data not available` 로 비운다. (다만 그 7.4 는 스스로 `(Solder)` 라 적어 **합금**의 값이지 페이스트가 아니다 —
KOKI 가 페이스트로 찍은 4-5 와 정반대다. 같은 갈래라도 무엇을 잰 값인지 문서마다 다르다.)

**정리 — '구판을 노려라' 는 벤더별로 참·거짓이 갈리는 전술이고, 판정은 벤더마다 따로 세워야 한다.**

| 벤더 | 무엇이 부재를 결정하나 |
|---|---|
| Doosan | **템플릿** (구판 100 % · 신판 0.6 %) |
| Senju | **개정 연도** (2015 찍음 · 2023 비움) — DA 가설 그대로 |
| 3M | **제품** (같은 연도·같은 템플릿에서 갈린다) |
| Rogers · Isola | **벤더 정책** — 성형품 면제라 구판도 신판도 안 찍는다 |
| Hexcel · Solvay · Permabond · Senju · Teijin · Taiyo | **요청제** — 웹에 SDS 자체가 없다 |

---

## 3. 넣은 값 — 13종 31행

### 밀도 (7종 14행)
| 재료 | 값 | 등급 | 근거 |
|---|---|---|---|
| **KOKI S3X48-M500**(2125) · **S3X58-M500**(2126) · **S3X70-M500**(2127) | **4000 / 5000 kg/m³** (각 2행) | t1 | KOKI SDS(EU CLP, 2015-07-10, 체코어) 9절 `· Hustota při 20 °C: 4-5 g/cm3` · 성상 `Pastovité` |
| **Ablebond 965-1L**(1226) | **3400 kg/m³** | t1 | Henkel `LOCTITE ABLESTIK 965-1L known as Ablebond 965-1L` SDS(005.0/2018 · 006.0/2019 두 판) 9절 `Specific gravity: 3.4` |
| **SABIC HDPE M300054**(1525) | **954 kg/m³** | t1 | SABIC **TDS** `Density kg/m³ 954 ASTM D 1505` — 2010·2022 두 개정판이 같은 수 |
| **Teijin PET 필름**(2223) | **1400 kg/m³** | t3 | Tetoron Film Clear Type MSDS(2001-09-14) `Specific gravity : 1.4 g/cm 3` |
| **Teijin PEN 필름**(2224) | **1350 / 1360 kg/m³** (2행) | t3 | Teonex MSDS(2000-01-13) `Specific gravity : 1.35-1.36 g/cm 3` |

### 융점 (8종 12행)
| 재료 | 값 | 등급 | 근거 |
|---|---|---|---|
| ADN(1746) | 655.15 / 657.15 K | t2 | Ossila SDS `382-384 °C (lit.)` |
| BCP(1760) | 553.15 / 555.15 K | t2 | `280-282 °C (lit.)` |
| CBP(1763) | 554.15 / 558.15 K | t2 | `281-285 °C (lit.)` |
| mCP(1764) | 446.15 / 451.15 K | t1 | `173-178 °C` (`(lit.)` 없음) |
| TAPC(1762) | 459.15 K | t1 | `186 °C` (`(lit.)` 없음) |
| fac-Ir(ppy)3(1651) | 724.15 K | t2 | `451 °C (lit.)` |
| Teijin PET 필름(2223) | 531.15 K | t3 | Tetoron Clear MSDS `Melting point : 258 C` |
| Teijin PEN 필름(2224) | 542.15 K | t3 | Teonex MSDS `Melting point : 269 C` |

### 점도 (2종 8행)
| 재료 | 값 | 등급 | 근거 |
|---|---|---|---|
| 3M DP100 Clear(2389) | A액 8.0/15.0 · B액 10.0/30.0 Pa·s | t1 | 3M SDS 9절 `Viscosity 8,000-15,000 cP [@73 ºF]` · `10,000-30,000 cP [@73.4 ºF]` |
| 3M DP100 NS(2418) | A액 50.0/85.0 · B액 90.0/150.0 Pa·s | t1 | `50,000-85,000 cP` · `90,000-150,000 cP [@73.4 ºF]` |

**재료 13종 · 31행.** 밀도 7종 14행 · 융점 8종 12행 · 점도 2종 8행이다.

### 등급을 왜 이렇게 매겼나
- **t1** — 문서가 그 등급 이름을 스스로 적고 값을 찍은 것(KOKI 는 1절 상품명 칸이 세 등급을 나열하고, Henkel 은 `known as Ablebond 965-1L` 이라 적는다).
- **t2** — Ossila 가 값 옆에 `(lit.)` 를 붙여 **스스로 문헌 인용임을 밝힌 것**. method 를 `handbook` 으로 두고 t2 로 내렸다(적재기 규칙 — t1 은 method 가 measured·digitized 일 때만 준다, 브리프 3). 같은 문서에서 `(lit.)` 가 없는 두 건(mCP·TAPC)만 t1 이다.
- **t3 + `grade_scope`** — 출처 논문이 등급 코드를 안 찍었고 벤더 문서도 계열 한 장인 것(Teijin 필름 둘). 등급이 특정되면 t1 로 올릴 수 있다.

### KOKI 값이 기존 판정을 뒤집는다
2125~2127 의 `core_not_applicable['physical.density']` 는
*"솔더 페이스트라 코어 7물성이 이 재료에 정의되지 않는다"* 였다.
영률·포아송비·인장강도에 대해서는 그 말이 맞다 — 미경화 페이스트는 자립 시편이 없다.
**그러나 밀도는 자립 시편을 요구하지 않는다.** 벤더가 실제로 쟀고 9절에 찍었다.
`ed08_verdicts.json` 에 철회문을 앞에 세우고 옛 판정문을 뒤에 그대로 보존했다.
(`apply_core_verdicts.py` 는 dict 의 **키 하나만 지우는 기능이 없어** 삭제 대신 철회문으로 덮었다.)

### Ablebond 965-1L — 인화점이 있는데도 넣은 이유
9절에 `Flash point: > 93 °C` 가 있어 이 배치의 경계 신호에 걸린다. 그래도 넣었다.
**3절 조성에 휘발성 용제가 한 줄도 없기 때문**이다 —
`Silver 70-80 % · Bisphenol-F Epichlorhydrin resin 10-20 % · 1,4-Bis(2,3-epoxypropoxy)butane 5-10 % · Phenol-formaldehyde 1-5 %`.
1,4-비스(2,3-에폭시프로폭시)부탄은 **반응성 희석제**라 경화물에 그대로 남는다 — 68차 DA 가 기각한
Photo-BCB(메시틸렌 **용액**)와 결정적으로 다른 자리다.
검산도 맞는다 — 은 10.49 를 75 wt%, 에폭시 1.15 를 25 wt% 로 놓으면 3.46 g/cm³ 이고 인쇄값이 3.4 다.
다만 이 값은 **미경화 페이스트**의 것이고 그 사실을 `conditions.physical_form` 에 적었다.

### SABIC 값은 SDS 가 아니라 TDS 에서 왔다 — 그 사실을 밝힌다
이 배치의 경로는 SDS 색인이지만, SABIC 은 SDS 를 로그인 뒤에 두고 있어 못 열었고
대신 유통사가 호스팅한 **벤더 TDS 두 개정판**을 얻었다. 12년 사이 Shore D 가 68→60,
1 % 시컨트가 1200→750 MPa 로 바뀌는데 **밀도만 954 로 같다** — 두 판 대조가 검산 역할을 했다.
기존 부재판정(59차 UD)은 *"Faiz 2014 논문에 밀도 열이 없다"* 라 지금도 맞고,
이 값은 그 진술을 뒤집는 것이 아니라 **다른 문서에서 온 것**이다.

## 4. 형태·동정이 안 맞아 버린 것 — **문서 11건 · 재료 7종**

**이번 파동에서 함정의 얼굴이 셋으로 갈렸다.**

### (가) 미경화 액상이라 기각 — 4문서 / 재료 2종
| 문서 | 찍힌 값 | 왜 버렸나 |
|---|---|---|
| **3M DP100 Clear Part A**(2022-10-10) | `Density 1.15 g/ml` | 9절이 스스로 `Physical state Liquid` · `Specific Physical Form Viscous` · `Flash Point 257 ºC` · `Viscosity 8,000-15,000 cP` 를 함께 찍는다 |
| **3M DP100 Clear Part B**(2025-06-13) | `Density 1.17 g/ml` | 같음(인화점 249 ºC · 점도 10,000-30,000 cP) |
| **3M DP100 NS Part A**(2024-07-29) | `Density 1.15 g/ml` | 같음 |
| **3M DP100 NS Part B**(2024-11-11) | `Density 1.18 g/ml` | 같음 |

DP100 은 **2액형**이고 SDS 는 A액·B액을 각각 따로 기술한다.
두 액에서 혼합·경화물 밀도를 만들어 내는 것은 역산이라 하지 않았다(혼합비도 9절에 없다).
**대신 같은 9절의 점도는 넣었다** — 점도는 미경화 상태에만 정의되는 물성이라 형태 불일치가 없다.

### (나) 제품행이 아니라 성분행·용제행이라 기각 — 2건
| 문서 | 찍힌 값 | 왜 버렸나 |
|---|---|---|
| **Doosan DSF-900SQ MSDS**(2023-04-11) | `N. Specific gravity  1.33 - 1.45 g/cm3` | 신판 GHS 의 **CAS 열 첫 칸**이고 그 CAS 25038-59-9 는 PET 다 — **성분값** |
| **Isola GETEK FR-4 Prepreg MSDS**(2010-07-02) | `Flash Point: 4degC (Toluene)` | 9절이 스스로 톨루엔을 지목한다 — **잔류 용제의 값**. 비중 칸은 `Not Determined` 라 가져올 밀도도 없었다 |

### (다) 형태·동정이 다른 제품이라 기각 — 5건
| 문서 | 찍힌 값 | 왜 버렸나 |
|---|---|---|
| **Loctite ESP110**(Henkel Ireland, 2011-02-09) | `Density 1,5 g/cm3 (20 °C)` | **이름만 같은 다른 회사 제품이다.** 우리 재료는 **Permabond** ESP110 인데 이 문서의 공급자는 Henkel Ireland 이고 9절 외관이 `paste / silver` 다 |
| **Hexcel Magnamite(R) J Sized Carbon Fiber MSDS**(2005-02-01) | `Specific Gravity (Water=1) 1.7-1.8` | **섬유**의 값이고 우리 재료(1652·1653)는 **오토클레이브 경화 UD 라미나**다. 게다가 등급이 아니라 J-사이징 계열 전체를 덮는 문서다 |
| **Teijin Panlite(R) AM-8030 SDS**(2017-04-01) | `Specific gravity 1.24` | **사출용 PC 수지 등급**이고 우리 재료(2225)는 **광학용 PC 필름 195 µm** 다. 형태가 다르다 |
| **DuPont Teijin Films Clear Homopolymer PET Chip MSDS**(2006-08-25) | `Specific Gravity 1.3-1.5` | **칩(펠릿)** 이고 우리 재료(2254)는 **이축연신 필름**이다. 비정 칩과 배향 결정 필름은 밀도가 다르다 |
| **DuPont Teijin Films Mylar(R) non-PVdC MSDS**(2009-10-26) | `Specific Gravity 1.2-1.4` | 형태는 맞으나(`Form: Transparent film`) **Melinex 와 다른 상표**이고, 1.2-1.4 는 코팅·공압출까지 덮는 넓은 계열 폭이다 |

**함정이 걸린 자리를 세면 액상 4 · 성분/용제 2 · 형태·동정 5 = 총 11문서다.**
68차 DA 는 액상 1건이었다. 규모가 커지자 **액상/경화물보다 제품행/성분행·형태 불일치가 더 자주 걸렸다.**

### 새로 발견한 함정 — **동박이 붙은 값과 안 붙은 값**
두산 DS-7409DV (N) 은 카탈로그에 **1420 kg/m³**(제품 페이지 인쇄값, t1)로 들어 있는데,
같은 등급의 벤더 SDS(2025-11-13, 구판 템플릿)는 `SPECIFIC GRAVITY : (Water=1.0) 1.9+/-0.2` 로
**1700~2100 kg/m³** 를 찍는다. 20~48 % 차이다.
같은 SDS 2절이 이유를 적는다 — `Copper Foil (7440-50-8) 10-30 wt%`.
**SDS 의 비중은 동박이 붙은 완제품(CCL)이고, TDS 의 Density 는 동박을 뺀 적층판이다.**
DSflex-600 도 같다(TDS 1420 vs SDS `1.45/0.92 (film/adhesive)`).
**CCL 갈래에서 SDS 비중을 TDS 밀도 자리에 그대로 옮기지 마라.**
(DA 의 DST-9000 두 행은 이 함정을 이미 피해 `physical_form` 에 `Al base + cured epoxy dielectric + Cu foil` 을 적어 두었다.)

### 벤더 안에서 판이 갈린 것
**DSflex-900** — 영문판(2025-10-14)이 `1.45/0.92 (film/adhesive)`, 국문판(같은 날짜, 제정 2022-04-29)이 `2.50 ±0.50` 이다.
같은 등급·같은 날짜인데 값이 다르다. 이 재료(2495)는 이미 밀도를 갖고 있어 이번 표적이 아니지만
**두 판이 다른 값을 찍는 사례**로 기록해 둔다 — 다음 파동이 확인해야 한다.

## 5. 못 넣은 것 — 넷으로 갈라 적는다

### (가) SDS 를 열었는데 9절에 밀도가 없었다 — 재료 12종
| 재료 | 문서 | 9절 verbatim |
|---|---|---|
| Doosan **DSR-1000**(2483) | GHS-MSDS(2023-12-20) | `N. Specific gravity  No data available ×5` |
| Doosan **DS-7409S (N)**(2509) | 영 2024-04-04 · 국 2021-05-20 | `No data available ×3` · `자료없음 ×3` |
| **3M AF-130**(1110) | AF 130-2 SDS(2019-01-14) | `Specific Physical Form: Film` · `Density  No Data Available` |
| Rogers **RO4350**(1277) · **RO4003**(1278) | RO4000 계열 문서 **7개정 × 5언어** | `SPECIFIC GRAVITY: NA (Water = 1)` (2009 구판도 같다) |
| Isola **FR408**(1273) | 2020 · 2016 · **2010 구판** · 프리프레그 2024 | `Not Available for product` · 구판 `Not Determined` |
| **GETEK**(1274) | 아카이브 2006 라미네이트 · 2010 프리프레그 | `Specific Gravity: Not Determined` |
| OLED 저분자 7종(1651 · 1746 · 1760~1764) | Ossila SDS 7건 | `Density  Not known.` · `Relative density  Not known.` |

**GETEK 은 이번 파동의 성과 하나다** — 기존 판정이 *"한 층 더 내려가려 했으나 문서가 없다"* 로 끝나 있었는데
**그 문서를 아카이브에서 찾아 열었다.** 이 칸은 이제 '문서가 없다' 가 아니라 '문서를 열었고 그 문서가 안 찍는다' 다.

### (나) 벤더 색인을 통째로 받았는데 그 등급이 색인에 없다 — 재료 22종
| 재료 | 색인 | 규모 |
|---|---|---|
| Doosan 5종 (2461 · 2462 · 2463 · 2480 · 2486) | 공개 MSDS 색인 **문서 단위 전수** | 제품 120 · 문서 181 |
| Ajinomoto ABF 6종 + AGL-1020 (978~983 · 1241) | **사이트 전체** sitemap + WP 미디어 REST | 페이지 75 · SDS 페이지 **0** |
| Hitachi ANISOLM(1098) · 빌드업필름(1291) · 에폭시 E-67(1430) | 아카이브 SDS 색인 | URL 238 · SDS PDF 98 (전부 축전지·커패시터) |
| Taiyo PDM-1 · PDM-4 (984 · 985) | 색인 **넷** | 1,892 + 9,614 + 285 + 검색 API |
| Permabond **ESP110**(1658) | WP 미디어 라이브러리 전체 | **5,964건** 중 `ESP` 토큰 0건 |
| Hexcel **M12** 매트릭스(1652 · 1653) | WP 미디어 + CDX PDF 전수 | 1,814 · 1,389 · 2,886 중 SDS 0건 |
| Cytec **FM300K · FM73 · 5250-4**(591 · 1109 · 618 · 619) | Syensqo sitemap + cytec.com CDX | 4,025 URL / PDF 3,209 중 복합재 SDS 0건 |
| PO14(1758) · PO1(1759) | Ossila 상품 색인 | 1,258 품목 |

### (다) 문서가 존재했다는 것까지 확인했으나 사본을 못 얻었다 — 재료 1종
**Melinex 50 µm**(2254). DuPont Teijin Films 의 2008년 SDS 색인 페이지가 매단 항목은 **정확히 다섯**이고
그중 하나가 `Melinex Film MSDS` 다 — **문서가 존재했다는 것은 색인이 증명한다.**
그런데 그 PDF 는 **아카이브가 한 번도 잡지 않았다**(CDX 적중 0).
**문서를 못 연 것은 판정이 아니므로** '9절에 없다' 고 적지 않았다.

### (라) 등급 이름이 없어 SDS 를 찾을 대상 자체가 없다 — **48종**
617 · 641 · 739 · 738 · 964 · 616 · 1356 · 1368 · 1369 · 2305~2312 · 1753~1756 · 1786~1788 ·
2432 · 2290 · 2446~2448 · 2524 · 2525 · 2553 · 2554 · 2678~2684 등.
**표적 114종 중 48종이 여기다.** 판정을 건드리지 않았다.

## 6. 9절에서 밀도 외에 얻은 것

먼저 DB 정의를 확인했다(271키). **`chemical.flash_point` 는 존재하지 않는다** — 끓는점·자연발화온도·증기압도 없다.
그래서 이번 파동은 인화점·끓는점을 **하나도 넣지 않았다**(브리프대로 '있는 것만 넣어라').

9절 항목 중 우리 스키마에 있는 것은 셋뿐이다 — `physical.density` · `thermal.melting_point` · `rheological.viscosity`.

| 얻은 것 | 건수 | 출처 |
|---|---|---|
| `thermal.melting_point` | **8종 12행** | Ossila SDS 6종(`Melting point/freezing point`) + Teijin 필름 2종(`Melting point : 258 C / 269 C`) |
| `rheological.viscosity` | **2종 8행** | 3M DP100 Clear·NS 의 A액·B액 9절 `Viscosity … centipoise` |
| `physical.density` | **7종 14행** | 3절 참조 |

**융점을 얻었으나 안 쓴 것도 있다** — Hexcel 섬유 MSDS 의 `Melting Point: Carbon fiber 3600 °C` 는
섬유의 값이라 라미나(1652·1653)에 붙일 수 없다. KOKI SDS 는 `Teplota tání: Není určeno`(미확정)이라 애초에 없다.

DA 의 *"열전도율·비열은 9절 항목이 아니다"* 는 이번 33건에서도 그대로 맞았다 — **한 건도 없었다.**

## 7. 산출물

| 파일 | 내용 |
|---|---|
| `ed07_materials.json` | 값 **13종 31행** (밀도 7종 14행 · 융점 8종 12행 · 점도 2종 8행) |
| `ed08_verdicts.json` | 판정 갱신 **48종** — 옛 판정문을 보존하고 `**[69차 ED …]**` 문단을 덧붙인 전문 |
| `gen_ed07_materials.py` · `gen_ed08_verdicts.py` | 위 둘의 생성기 |
| `indexes/*.json` | **받은 벤더 색인 17 파일** — 다음 파동이 재사용한다 |
| `/data/paper_patent_corpus/standards_appnotes/sds/` | SDS·MSDS 총 **74건**(이번 파동이 **55건** 늘렸다) |
| `/data/paper_patent_corpus/standards_appnotes/poly/SABIC_HDPE_M300054_TDS_*.pdf` | SABIC TDS 두 개정판 |

**DB 에는 아무것도 쓰지 않았다.** 두 도구를 예행으로만 돌렸다.

```
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  .venv/bin/python scripts/catalog/ingest_agent_json.py   scripts/catalog/out_ed/ed07_materials.json   # [DRY-RUN] ok 31
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  .venv/bin/python scripts/catalog/apply_core_verdicts.py scripts/catalog/out_ed/ed08_verdicts.json    # [예행] 병합 48 · 재료 48
```

※ `out_ed/` 에는 8월 19일자 다른 배치의 `ed01`~`ed06` 파일이 이미 있었다. 덮지 않으려고 이번 산출물을
`ed07`·`ed08` 로 번호를 이어 붙였다.

## 8. 다음 파동에 넘길 것

### 재사용 가능한 색인 — `out_ed/indexes/` 17 파일
| 파일 | 무엇을 담았나 | 어떻게 쓰나 |
|---|---|---|
| `doosan_msds_index.json` | 제품 120 · 첨부 183 (attId·파일명·개정일·언어) | `GET /file/productAttachment/download/<attId>` 로 바로 받는다 |
| `doosan_msds_section9_scan.json` | 181건 전부의 템플릿 판별 + 9절 비중 verbatim | **두산 문서를 다시 열 이유가 사라졌다** |
| `ossila_product_index.json` | 1,258 상품(id·title·handle) | SDS 는 `https://downloads.ossila.com/msds/<handle>.pdf` — **정적 경로다** |
| `3m_sds_index.json` | `searchapi.3m.com` 엔드포인트 · `mwsId` 추출 레시피 · 필름접착제 48 제품 ID | `www.3m.com` 이 막혀도 `multimedia.3m.com` 으로 SDS 를 받는 길 |
| `rogers_sds_index.json` | EHS 148 경로 · `/msds/` 119 경로 | Rogers 는 sitemap·API 가 없다. 이 파일이 유일한 색인이다 |
| `isola_sds_index.json` | 문서 206 · SDS 페이지 51 · 첨부 868 | `documentation` 포스트타입이 REST 에 없어 sitemap 이 유일한 색인 |
| `hexcel_sds_index.json` | 라이브 PDF 1,389 + 2005년 섬유 MSDS 12건(아카이브 타임스탬프) | 형제 사이징 11종을 열려면 여기서 시작 |
| `dupont_teijin_films_sds_index.json` | 라이브 PDF 293 + 역사적 SDS 색인 5항목 + 아카이브 MSDS 10 URL | Melinex 사본이 어딘가에서 나오면 바로 대조 |
| `koki_sds_index.json` | 체코어 SDS 11건 + 각 문서가 덮는 등급 목록 | 다른 KOKI 페이스트 등급이 표적이 되면 바로 매칭 |
| `solvay_syensqo_cytec_sds_index.json` | FM 계열·CYCOM 5250 슬러그 전수 | 이 사업부는 SDS 미공개임이 확정 |
| `teijin_resin_sds_index.json` | 게이티드 CGI 엔드포인트 + **폼 필드 이름 전부** | 실명 등록이 되는 사람이 열면 Panlite 필름 SDS 가 나온다 |
| `permabond_sds_index.json` | 미디어 5,964건 | ESP 계열 부재 확정 |
| `taiyo_sds_index.json` | 문서 285건 + 검색 엔드포인트 | 라이브 크롤은 한 단계 더 내려가야 SDS 층에 닿는다(파일에 명시) |
| `senju_sds_index.json` · `ajinomoto_*` · `hitachi_chem_archived_sds_index.json` | 각 벤더의 부재 근거 | **다시 확인할 필요 없다** |

### 기법 자산 — 이번에 새로 확인한 것
1. **`GET <host>/wp-json/wp/v2/media?media_type=application&per_page=100&page=N`** 이 현대 벤더 사이트의
   가장 강력한 전수 색인이다. `X-WP-Total` 헤더가 건수를 먼저 알려 준다.
   Permabond 5,964 · Hexcel 1,886 · mylar.com 548 을 이 한 줄로 받았다.
   **"검색이 0건" 이 "N건을 다 봤고 없다" 로 바뀐다.**
2. **Shopify 상점은 `products.json?limit=250&page=N` 으로 전 상품을 준다**(Ossila 1,258).
3. **web.archive CDX `filter=mimetype:application/pdf` + `matchType=domain`** 이 폐업·개편 벤더의 첫 수다.
   다만 **PDF 링크가 표 안에 인라인일 때는 아카이브된 *목록 페이지* 를 받아 raw HTML 을 grep 해야** 잡힌다
   (Hexcel 2005 MSDS 가 그랬다).
4. **스캔 이미지 PDF 는 `pdftotext` 가 아무것도 안 준다.** `pdftoppm -r 150 -png` 로 렌더해 눈으로 읽어야 한다
   (2000년대 일본 벤더 문서에 흔하다 — Tetoron·Teonex 2006 판이 그랬다).
5. **`robots.txt` 가 200 으로 HTML 404 를 돌려주는 사이트가 있다**(senju.com). 상태코드를 믿지 마라.

### 아직 안 닫힌 표적
- **Melinex(2254)** — 문서가 존재했다는 것은 색인이 증명하는데 사본이 없다. 다른 아카이브·유통사 사본을 찾아라.
- **Panlite PC 필름(2225)** — Teijin SDS 포털이 실명 등록 뒤에 있다. 엔드포인트·폼 필드는 색인에 적어 두었다.
- **PO14(1758) · PO1(1759)** — Ossila 색인에 없고 Lumtec sitemap 의 MSDS 211건이 전부 404 다.
  Lumtec 제품 페이지에서 살아 있는 MSDS 경로를 찾으면 열린다(다만 Lumtec 9절은 `Appearance` + `Melting point(DSC)`
  두 줄뿐이라 **밀도는 애초에 없다** — 융점만 노려라).
- **1352 Lamics U-8437-3 · 737 Zymet · 740 KGK-200A50 · 1300 YPH-160 · 1462 PP F401 · 1509 PVC 5225** —
  이번에 색인을 열지 못했다. **문서를 못 연 것은 판정이 아니다** — 건드리지 않았다.
- **1358 ALX-211 · 1359 ALX-215** — 구조적으로 함정이다. AL-X 는 스핀코팅 액상 수지라
  SDS 를 찾아도 그것은 **용액의 밀도**이지 우리가 원하는 190 °C 경화막의 밀도가 아니다(Photo-BCB 와 같은 자리).

### 다음 파동의 표적 셋
1. **부재의 원인이 벤더마다 다르다는 것을 전제로 시작해라**(§2 표).
   두산은 템플릿, Senju 는 연도, 3M 은 제품, Rogers·Isola 는 정책, 여섯 벤더는 요청제다.
   **한 벤더에서 얻은 규칙을 다른 벤더에 옮기지 마라** — 이번에 Rogers 구판이 그 반례였다.
2. **CCL 은 SDS 비중과 TDS 밀도가 다른 물건이다**(동박 포함 여부, §4).
   두산 구판 SDS 22건 중 카탈로그 재료와 겹치는 것들의 값을 TDS 값과 대조하면
   이 차이가 계통적인지 등급마다 다른지 셀 수 있다 — **아직 안 셌다. 색인 파일에 재료가 다 있다.**
3. **`core_not_applicable` 을 다시 세어라.** 이번에 솔더 페이스트 밀도가 '해당없음' 으로 잘못 닫혀 있었다.
   *"자립 시편이 없어 코어 7물성이 정의되지 않는다"* 는 논지가 **밀도까지 싸잡는 자리가 더 있을 것이다** —
   밀도는 자립 시편을 요구하지 않는다. 같은 문구가 걸린 재료를 전수로 뽑아 물성별로 갈라 보아라.
