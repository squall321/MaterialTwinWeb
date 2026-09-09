# 69차 EB — 「벤더 자국어 총합 카탈로그」를 아홉 벤더로 넓혀 본 결과

**한 줄 답: 자국어가 문을 연 게 아니다. 「전 등급을 한 표에 늘어놓는 총합 특성일람표」라는 *형식*이 열었고, Panasonic 은 그 형식을 자국어로만 내는 아홉 중 하나였다.**

68차 DC 는 Panasonic 일본어 총합 카탈로그 한 건에서 열두 값을 얻고 영문 TDS·설계가이드 21건에서 0을 얻었다.
DC 는 그것을 *언어* 가설로 적었다 — 「영문 TDS 는 국제 판매용이라 항목을 줄이고, 자국어 총합 카탈로그는 자국 설계자를 상대로 전 등급을 한 표에 늘어놓는다」.
이 배치는 그 가설을 **아홉 벤더·네 언어**로 두드렸다. **가설은 절반만 맞다.**

**수확: 9 재료 · 22 행** (`out_eb/eb01_materials.json`) · **판정 갱신 148건** (`out_eb/eb02_verdicts.json`)

---

## 1. 벤더별·언어별 수확표 — 이 배치의 답

| 벤더 | 언어 | 자국어 총합표를 찾았나 | **영문판과의 차이** | 표적 등급에 낸 값 |
|---|---|---|---|---:|
| **Panasonic** (일본) | 일본어 | **찾았다** — 2013판 · **2021판** 두 판 | **자국어에만 있다.** 영/일 이중언어 자동차 카탈로그(2024-11)의 `General properties 一般特性` 표는 Tg·CTE·T288·Peel **여섯 행뿐**이고 탄성률·비열·열전도율·포아송비가 **전부 없다** | **16** |
| **Nan Ya 南亞塑膠** (대만) | 번체 | **자국어 총합 카탈로그가 없다** — 대만 CCL 포털(`cclqc.npc.com.tw`)의 UI 는 번체지만 **내주는 시트 38장이 전부 영문**이다 | 차이 0 | **6** — 자국어가 아니라 **독일 파트너 Datenblatt** 에서 나왔다 |
| **MGC 三菱ガス化学** (일본) | 일본어 | 찾았다 — `lineup/{hfbt,fr4,led}.html` 13등급 | **차이 0.** 영문 `/eng/products/sc/btprint/lineup/*.html` 이 **행 하나까지 같다** | 0 (DB 에 등급 없음) |
| **Sumitomo Bakelite 住友ベークライト** (일본) | 일본어 | 찾았다 — ELC `spec/index.html` | **차이 0.** 영문 spec 페이지와 **행 순서·값 완전 동일**, 라벨만 번역 | 0 (DB 에 등급 없음) |
| **Resonac** (일본) | 일본어 | 찾았다 — `2023-2024MCL_catalog_JP.pdf` 66쪽 | 차이 0. 영문 2025-05 카탈로그도 `Tensile modulus` / `Flexural modulus` 를 똑같이 가른다 | 0 (등급 접미가 다름) |
| **Arisawa 有沢製作所** (일본) | 일본어 | 찾았다 — 일본어 시트 19장. **총합 카탈로그는 없다** | **차이 0.** C33 영문판과 일본어판이 내용상 쌍둥이 | **0 — 표에 열이 없다** |
| **Doosan 두산전자** (한국) | 한국어 | **한국어판이 없다.** 전 등급 TDS 는 `/download/product/kr/CCL_All_Properties_PDF_240930_v9.pdf` **한 파일**이고 en·cn·jp 검색 페이지가 **모두 그 파일을 가리킨다**(md5 동일) | **차이 0.** `/kr/`·`/en/`·`/cn/` 제품 상세표 **24행 전부 동일**, 한국어판조차 행 이름이 영어 | 0 |
| **Shengyi 生益科技** (중국) | 중국어 | 중국어 카탈로그가 **없다** — 중국 사이트(`syst.com.cn`)가 **영문 TDS 를 서빙**한다 | 차이 0 | 0 |
| **Elite Material 台光電子** (대만) | 번체 | **없다.** zh-TW·zh-CN·en 세 로케일의 PDF 목록이 **완전 동일**(각 43장) | 차이 0 | 0 |

**네 문장으로 요약한다.**

1. **아홉 벤더 중 자국어에만 있는 표를 가진 벤더는 Panasonic 하나다.** 나머지 여덟은 자국어판과 영문판이 같거나, 자국어 총합표가 아예 없다.
2. **그렇다고 DC 의 수확이 우연은 아니었다.** MGC·Sumitomo·Resonac 은 **똑같이 풍부한 총합 특성일람표**를 낸다 — 다만 두 언어로 낸다. **형식은 일반적이고, 언어 비대칭만 Panasonic 특유다.**
3. **이번 배치의 두 번째 수확(Nan Ya)은 자국어가 아니라 독일어에서 나왔다.** 자국어(번체) 포털은 0을 냈고, **독일 파트너 Technolam 의 `19. Other / weitere` 절**이 열전도율·비열을 찍었다. 언어가 아니라 **「IPC-4101 서식 바깥에 자기 열을 덧붙이는 형식」**이 문이다.
4. **DB 가 그 형식과 안 맞물린다.** 총합표가 가장 풍부한 세 벤더(MGC·Sumitomo·Resonac)의 등급이 **우리 DB 에 하나도 없고**, DB 에 있는 벤더(Doosan·Shengyi·EMC)는 어느 언어로도 그 열을 안 찍는다.

### 형식 가설의 **선행 증거**도 확인했다 — 이미 DB 안에 있었다

- 재료 251·252 **Chukoh CHUKOH FLO CGN-500 / CGS-500A** 는 코어7이 **꽉 차 있고**, 출처 1811 이 `CHUKOH FLO 銅張積層板 製品カタログ (catalog05_lami_ja)` — **일본어 총합 카탈로그**다. 그 표는 `比重 g/cc` 를 6등급 가로로 늘어놓는다.
- 재료 97 **BT Resin** 의 영률 28/32 GPa · 인장강도 270/290 MPa · 비열 1000 J/(kg·K) · 밀도 2100/2000 · 포아송 0.19 는 전부 출처 306 = **MGC `CCL-HL832NX` lineup 페이지**에서 왔다. 그런데 그 URL 은 `.../eng/products/...` — **영문 페이지다.**

두 번째 사실이 이 배치의 답을 앞당겨 말해 준다. **MGC 의 그 풍부한 표는 이미 영문으로 수확돼 있었다.** 자국어를 뒤질 필요가 없었던 것이다.

---

## 2. 영문 문서에 없고 자국어 문서에만 있던 항목 — 구체적으로

**딱 한 벤더, Panasonic 뿐이다.** 그리고 그 차이는 이렇게 생겼다.

Panasonic 이중언어(영/일) 자동차 카탈로그 `Panasonic_CircuitBoardMaterials_Catalog_all_2024-11.pdf` 의 `■ General properties ⼀般特性` 표 verbatim — 이게 **영문 독자가 받는 전부**다:

```
             Item                     Test method         Condition    Unit    R-1566S  R-1755D  R-1755M  R-1566  R-1755E  R-1766
  Glass transition temp.(Tg)               DSC               A         ℃        175      163      153      148     133     140
  CTE x-axis                   α1   IPC-TM-650 2.4.24        A        ppm/℃    11-13    10-12    11-13    11-13   11-13   11-13
  CTE y-axis                   α1                                              13-15    12-14    13-15    13-15   13-15   13-15
  CTE z-axis                   α1   IPC-TM-650 2.4.24        A                   40       43       40       40      42      65
                               α2                                               180      236      240      180     250     270
  T288(with copper)                 IPC-TM-650 2.4.24.1      A         min        10       15       18        3      25       1
  Peel strength 1oz(35μm)           IPC-TM-650 2.4.8         A        kN/m      1.6      1.3      1.5      1.8     1.6     2.0
The sample thickness is 0.8mm.
```

**여섯 행. 강성도 없고 비열도 없고 열전도율도 없고 포아송비도 없다.** 이 여섯 등급은 전부 우리 표적이다.

같은 여섯 등급에 대해 **일본어 전용** 특성일람표(2013·2021)는 이 열들을 더 찍는다:

| 자국어에만 있는 열 | 시험법 verbatim | 단위 |
|---|---|---|
| `比熱` | `DSC法` · `25℃` | `J/kg℃` |
| `熱伝導率` | `レーザーフラッシュ法` · `25℃` | `W/m・K` |
| `ポアソン比` | 2013 `JISK7113` / 2021 `JIS K 7161-1` · `23±3℃` | `−` |
| `ヤング率（引張りモード）` | `ASTM D3039` · タテ/ヨコ | `GPa` |
| `曲げ弾性係数` | `JIS C 6481` · タテ/ヨコ | `GPa` |
| `比重` | `JISK6911` | `−` |

그리고 **2021년판은 2013년판이 못 덮은 등급 R-1566S 를 덮는다.** 68차 DC 가 §5-4 에서 「2013 카탈로그의 뒷 판을 찾아라」라고 넘긴 그 문서다. 찾았고, 그 등급의 영률이 열렸다.

### 반례를 정직하게 적는다 — 나머지 여덟 벤더의 「자국어 전용 항목」은 **0개**다

Sumitomo Bakelite ELC — 영/일 spec 페이지가 **완전히 같은 표**다:
```
EN: Tensil modules | Machine Direction | A | GPa | 15 | 14 | 14 | 14
                     Cross Direction   |   |     | 15 | 12 | 12 | 12
JA: 引っ張り弾性率   | タテ             | A | GPa | 15 | 14 | 14 | 14
                     ヨコ              |   |     | 15 | 12 | 12 | 12
```

Doosan DS-7402HD — `/kr/` · `/en/` · `/cn/` 세 페이지가 **24행 모두 동일**하고, **한국어 페이지의 행 이름조차 영어**다:
```
Mechanical | Young's modulus | 24  | GPa   | As received | IPC-TM-650 2.4.18.3
             Density         | 1.7 | g/㎤  | -           | -
             Poisson ratio   | 0.2 | -     | -           | -
```
→ 세 언어 어디에도 **비열 행이 없다.** Doosan 60등급의 비열 빈칸은 언어를 바꿔서 닫히지 않는다.

Doosan 은 한 걸음 더 확실하다 — **전 등급 TDS 파일이 언어별로 존재하지도 않는다.** 검색 페이지 소스의 다운로드 훅이 `pdfDown(this, '/download/product/kr/CCL_All_Properties_PDF_240930_v9.pdf')` 하나이고, **en·cn·jp 검색 페이지도 같은 파일을 가리킨다**(경로의 `kr` 은 언어가 아니라 폴더 이름이다. `/download/product/{en,cn,jp}/…` 는 HTTP 200 이지만 `text/html` 오류 페이지 26,177 B 를 준다).

---

## 3. 열 밀림을 어떻게 확인했는가

브리프의 요구 — 「CJK 표는 `pdftotext -layout` 이 열을 섞는다. 값을 옮기기 전에 해당 페이지를 300~400 dpi 로 렌더해 눈으로 대조해라」 — 를 **값을 넣은 세 문서 전부**에 적용했다.

1. `pdftotext -layout` 로 표를 뽑는다.
2. `pdftoppm -r 300~350 -png -f <p> -l <p>` 로 같은 쪽을 렌더한다.
3. **렌더한 그림을 실제로 보고**, ① 열 머리글 순서 ② 단위 행 ③ 표적 등급 행의 각 칸이 텍스트 추출과 자리까지 일치하는지 대조한다.

| 문서 | PDF 쪽 | 렌더 | 대조 결과 |
|---|---|---|---|
| Panasonic 2013 총합카탈로그 | 18 (印刷 17) | 350 dpi | **일치.** `品番 \| 比重 \| 比熱 \| 熱伝導率 \| ポアソン比 \| Tg(TMA/DSC/DMA) \| 熱分解温度` 순서 확인. R-1755V 행이 그림에서 `1.96 / 910 / 0.53 / 0.2 / 165 / 173 / 190 / 350` |
| Panasonic 2013 총합카탈로그 | 19 (印刷 18) | 350 dpi | **일치.** `曲げ弾性係数(JIS C6481に準拠) 縦\|横` 바로 오른쪽에 `ヤング率(引張り)(ASTM D3039) 縦\|横` 가 따로 서 있음을 확인. **R-1566S 행이 이 판에 없다는 것도 그림으로 확정** |
| Panasonic 2021 특성일람표 | 1 (印刷 9) | 350 dpi | **일치.** 맨 오른쪽 열이 `熱伝導率 / レーザーフラッシュ法 / 25℃ / W/m・K`. R-1566S 행 `170 175 195 355 40 180 11~13 13~15 0.62` |
| Panasonic 2021 특성일람표 | 2 (印刷 10) | 350 dpi | **일치.** `曲げ弾性係数 JIS C 6481 タテ\|ヨコ` → `ヤング率(引張りモード) ASTM D3039 タテ\|ヨコ` → `ポアソン比 JIS K 7161-1 23±3℃` 세 블록 경계 확인. R-1566S `24 22 20.7 19.7 0.2` |
| Technolam NP-175FTL/FR/FB (2021-01) | 3 (`Performance List 2/2`) | 300 dpi | **일치.** 두 두께 구간(`<0,50 mm` · `≥0,50 mm`) 각각이 `Specification\|Property` 두 칸으로 갈리는 4열 구조 확인. 이 행들의 `Specification` 칸은 전부 `-` 이고 `Property` 칸에만 값이 있다 |

### 렌더가 실제로 잡아낸 것 세 가지

- **2021년판 쪽머리에만 있는 시편 두께 단서.** 텍스트 추출에서는 흩어져 읽히는데 그림에서 한 줄로 읽힌다:
  `板厚: 1.6mm、ポアソン比: 0.8mm、ヤング率(引張りモード): 0.1mm、貫層耐電圧: 0.2mm`
  → **이 표에서 영률만 0.1 mm 시편, 포아송비는 0.8 mm, 나머지는 1.6 mm 다.** 조건에 `specimen_thickness_mm` 로 박았다. 2013년판 쪽머리는 `板厚：1.6mm（R-1515B, R-1515Sは0.8mm）` 뿐이라 비열·열전도율을 1.6 mm 로 적었다.
- **포아송비 시험법이 판 사이에 바뀐다.** 2013 `JISK7113` → 2021 `JIS K 7161-1`. 값은 둘 다 0.2. (K7113 이 K7161 로 대체된 결과지 다른 물성이 아니다.)
- **Technolam 시트 하단 각주의 적용 범위.** `Performance List 1. to 18. follows IPC-4101 template … shows minimum or maximum properties expectable` — **그 min/max 단서는 1~18 항에만 걸리고**, 우리가 쓴 값들은 그 바깥의 `19. Other` 절이다. 그림에서 각주 위치를 확인하지 않았으면 전형값을 규격 한계로 오독할 뻔했다.

### 교차판 검산

- Panasonic 두 판이 8년 간격으로 겹치는 네 등급의 熱伝導率 를 소수점까지 같게 찍는다 — R-1755D 0.63 · R-1755E 0.55 · R-1566 0.62 · R-1766 0.38. 영률도 R-1755D 19.2/17.8 · R-1755E 20.0/18.5 · R-1566 20.9/19.8 · R-1766 17.8/16.5 로 동일. **한 판의 오독이었다면 이렇게 안 겹친다.**
- Technolam 2018-02 판과 2021-01 판이 `0,53 / 0,46 / 0,91 / 2,10` 을 3년 간격으로 동일하게 찍는다.
- **Technolam 값이 상용구가 아님도 확인했다** — 같은 발행처의 다른 계열 시트가 서로 다른 값을 찍는다: 비열 `NPG-170TL/R/B·NPG-150N 0,946` · `NPG-170D 0,95` vs `NP-175 계열 0,91`; 열전도율 `NPG-170TL/R/B 0,43/0,39` · `NPG-150N 0,42/0,37` · `NPG-180BH 0,55/0,46` vs `NP-175 계열 0,53/0,46`.

HTML 표(MGC·Sumitomo·Doosan)는 렌더 대신 **`<tr>`/`<td>` 를 직접 파싱해 셀 경계를 확정**했다 — 레이아웃 추측이 끼어들 자리가 없다. Doosan 은 같은 파서로 `/kr/`·`/en/`·`/cn/` 세 판을 뽑아 행 단위로 대조했다.

---

## 4. 넣은 값 — 9 재료 · 22 행 (`out_eb/eb01_materials.json`)

| 재료 | 값 | 등급 | 출처 | 왜 새 값인가 |
|---|---|:--:|---|---|
| **Panasonic R-1566S** | 영률 タテ **20.7** / ヨコ **19.7** GPa (ASTM D3039 인장) · 열전도율 **0.62** · 포아송비 **0.2** | t1 | **2021판** | **68차 DC 가 못 닫은 칸.** DC §4-다 「R-1566S 가 2013 총합카탈로그 표에 없다 — 형제 여섯은 다 열렸는데 이 하나만 남았다」. DC §5-4 가 요구한 '뒷 판'이 2021년판이고, 거기 이 등급이 처음 실렸다 |
| Panasonic R-1755V | 비열 **910** J/(kg·K) · 열전도율 **0.53** | t1 | 2013판 | DC §5-1 인계 |
| Panasonic R-1755M | 비열 **930** · 열전도율 **0.57** | t1 | 2013판 | DC §5-1 인계 |
| Panasonic R-1755D | 비열 **900** · 열전도율 **0.63** | t1 | 2013판 (2021 교차확인) | DC §5-1 인계 |
| Panasonic R-1755E | 비열 **930** · 열전도율 **0.55** | t1 | 2013판 (2021 교차확인) | DC §5-1 인계 |
| Panasonic R-1566 | 비열 **950** · 열전도율 **0.62** | t1 | 2013판 (2021 교차확인) | DC §5-1 인계 |
| Panasonic R-1766 | 비열 **920** · 열전도율 **0.38** | t1 | 2013판 (2021 교차확인) | DC §5-1 인계 |
| **Nan Ya NP-175FR** | 비열 **910** J/(kg·K) · 열전도율 **0.53**(ASTM E1461) **/ 0.46**(ASTM D5470) | t2 | Technolam 2021-01 `19. Other` | **DC §5-2 인계.** 「현재 2440·2441 은 열전도율·비열이 비어 있다」 |
| **Nan Ya NP-175FTL** | 위와 같음 | t2 | 위와 같음 | DC §5-2 인계 |

### 규율 점검

- **굽힘탄성률로 채운 칸은 0건이다.** R-1566S 의 같은 행에 `曲げ弾性係数(JIS C 6481) タテ 24 / ヨコ 22 GPa` 가 나란히 있다. 영률 칸에는 `ヤング率(引張りモード)(ASTM D3039)` 쪽 20.7/19.7 을 넣었다 — 굽힘값을 넣었다면 이 등급의 강성을 **16 % 부풀렸을 것**이다.
- **Doosan 구판 카탈로그의 `Flexural Modulus Gpa 27-30` 도 쓰지 않았다.** 굽힘이다.
- 경사(タテ)·위사(ヨコ)는 **두 행으로 갈랐다.** 평균 내지 않았다.
- **같은 물성의 두 시험법도 두 행으로 갈랐다** — Nan Ya 열전도율 `ASTM E1461 0.53` 과 `ASTM D5470 0.46` 은 15 % 차이가 나는데 이건 등급 차가 아니라 시험법 차다. 평균 내지 않았다.
- **포아송비 0.2 는 t4 를 갈아탄다.** R-1566S 의 현재 포아송비는 클래스 중앙값 0.172(t4)다. 제조사가 그 등급에 `JIS K 7161-1, 23±3℃` 로 인쇄한 0.2 가 t1 이다. **인쇄 자릿수가 한 자리이므로 0.20 으로 부풀려 읽지 마라.**
- **Nan Ya 2종을 t2 로 낮춘 이유**를 `grade_scope` 에 적었다 — 발행처가 제조사 Nan Ya 가 아니라 유럽 파트너 Technolam 이고, 시트 한 장이 NP-175FTL·FR·FB 세 등급을 가르지 않는다. (68차 DC 가 같은 시트의 영률에 매긴 등급과 같다.)
- **환산 검산** — 0,91 J/g°C(유럽식 쉼표) × 1000 g/kg = 910 J/(kg·K); 되돌리면 910/1000 = 0.91. 20.7 GPa × 1e9 = 2.07e10 Pa; 되돌리면 2.07e10/1e9 = 20.7.

### 동시 배치와 겹칠 수 있다 — 정직하게 적는다

이 배치가 도는 동안 형제 배치가 같은 Panasonic 파일들을 받아 갔고(09:01), 공유 스크래치패드에 **같은 쪽의 렌더**(`cat2013_p-018.png` · `pl2021_p-1.png`)를 09:11 에 남겼다. **R-1755V/M/D/E·R-1566·R-1766 의 비열·열전도율 12행은 그쪽과 겹칠 수 있다.** 겹쳐도 값이 같으면 병합 단계에서 지워질 뿐이고, 확인한 값을 빼는 쪽이 더 나쁘다고 판단해 넣었다. **R-1566S 4행과 Nan Ya 6행은 겹치지 않을 것이다.**
같은 이유로 이 배치는 **Doosan MSDS/SDS 축**(형제 배치가 120제품 183첨부를 잡고 있다)과 **ITEQ Chen 2007 논문 축**은 건드리지 않았다.

---

## 5. 못 넣은 것 — 셋으로 갈라 적는다

### (가) 형식에 그 항목이 없었다 (문서를 열었고 행이 없음을 확인)

| 표적 | 연 문서 | 확인한 부재 |
|---|---|---|
| **Elite Material 5종** (EM-370(Z)·EM-370(5)·EM-888·EM-890·EM-891) — 영률·비열·인장강도 | zh-TW/zh-CN/en 세 로케일 제품 인덱스 + **데이터시트 43장 전수** | 다섯 시트 전부 `modulus\|density\|specific heat\|poisson\|tensile` **0 hit**. 있는 건 `Thermal Conductivity`(ASTM D5470)와 `Flexural Strength Warp/Fill` 뿐 |
| **Shengyi 4종** (S1170·S1170G·S1000-2M·S7439) — 영률·열전도율·비열·인장강도 | 중국 사이트 `syst.com.cn` **109제품 전수** + 중국어 TDS·LineUp·加工指南 | S1170G·S1000-2M·S1000-2 → `Flexural Strength (LW/CW)` 하나뿐. **S7439·S7439G → 기계물성 행이 아예 없다.** 비열·포아송비·밀도 **0 hit** |
| **Nan Ya 2종** — 인장강도 | 대만 포털 시트 38장 + Technolam `19. Other` | Nan Ya 자신의 시트 기계축은 `Flexural strength LW/CW` 하나뿐이고, Technolam §19 에도 인장강도 행이 없다 |
| **Doosan 60종** — 비열 | `/kr/`·`/en/`·`/cn/` 상세표 + 8쪽 All-Properties TDS + REST API + 구판 dse.co.kr | **세 언어 어디에도 비열 열이 없다.** Doosan 의 열물성 축은 `Thermal Conductivity`(ASTM E1461 / D5470)와 `Max. Operating Temperature`(UL 796)다 |
| **Doosan 강성 CCL** — 인장강도 | 같은 문서들 | 8쪽 TDS 에 `Tensile Strength` **열은 있는데** DS-74xx/84xx/85xx 강성 등급 칸이 **비어 있다**. 값이 든 건 DSflex 계열과 DS-7402BS·DS-8402H BS·DS-9530 뿐 — 이미 DB 에 있다 |
| **Arisawa C33** — 인장강도 | 일본어 카탈로그 19장 + 영문 C33 | C33 시트는 `ポリイミド厚さ·接着剤厚さ·誘電率·誘電正接·引きはがし強さ·はんだ耐熱性` **여섯 행이 전부**다. **Arisawa 는 커버레이 어느 등급에도 기계물성을 안 찍는다** — 일본어판·영문판 모두 |
| **Panasonic R-1566S** — 비열 | 2013·2021 두 판 | 2013 판에 R-1566S **행이 없고**, 2021 판에는 `比熱` **열 자체가 없다**. 두 판 사이에 끼여 남았다 |

### (나) 문서를 못 열었다 (판정이 아니다 — 다음 배치의 표적)

- **`industrial.panasonic.com` 전체** — `/jp/products/pcbmaterials` · `/ww/electronic-materials` · `/cdbs/www-data/pdf/EMD0000/ast-ind-261839.pdf` 모두 **60초 타임아웃(000)**. 그래서 넣은 두 Panasonic 출처의 `url` 을 **`null` 로 두고** `url_note` 에 사유를 적었다. 로컬 파일은 있고 내용은 렌더로 확인했지만 **URL 을 지어내지 않았다.**
- **`Technolam_NanYa_NP-155FTL-NP-155FR-NP-155FB_Datasheet_2024-08.pdf`** — HTTP 200 으로 받았으나 **텍스트층 474자의 이미지 스캔**이다. 같은 서식이므로 `19. Other` 절에 NP-155F 계열의 E-Modul·비열·열전도율이 있을 것이 거의 확실하다. **OCR 이 표 본문에서 깨끗이 나오지 않아 값을 옮기지 않았다.** (`NP-140TL`·`NPG-151`·`NP-175FTL 2024-08` 판도 같은 스캔 상태.)
- **`Nanya_CCL_ProductCatalog_2001-09_scanned_52p.pdf`** — 텍스트층 52자의 스캔. Wayback 에서 복원했다. **목차가 등급별 색인이라 다등급 비교표가 아닌 '데이터시트 묶음'으로 보이지만**, 쪽을 렌더해 확인하지 못했다.
- **`Doosan_CCL_DS-8405_LegacyCatalogPage_dse.co.kr_2003_scanned.pdf`** — 96 dpi 스캔. OCR 로는 `Flexural Strength` 만 보이고 비열·인장은 없어 보이나 **OCR 숫자는 넣지 않았다.**
- **`Doosan_CCL_DS-7402_CatalogPDF_doosanelectronics_2019.pdf`** — 텍스트 35자, 이미지 전용.
- **`sekorm.com`** — HTTP **457** + 안티봇 인터스티셜(`当前访问人数过多，完成下方验证可优先进入网站`).
- **Shengyi `SI10US`·`SI13U` TDS PDF** — HTTP 200 이나 **폰트 미임베드**라 텍스트층이 깨진다(620·593자의 잔여 글리프). HTML 제품페이지로 우회했으나 PDF 자체는 OCR 이 필요하다.
- **Doosan `/rest/product/{tds,catalog,attachment,pdf}/list`** — 전부 **404**. `/rest/product/detail` 은 **405**. `/{en,kr}/high-tg-fr-4-substrate-materials/fr-4-ds-7409/` 는 **500**.
- **Sumitomo Bakelite `/ww-attaches/802.pdf`·`804.pdf`** — HTTP 200 이나 이미지 전용(2013 브로슈어 표지·뒷표지).

### (다) 등급이 안 맞았다 — **이 배치의 가장 큰 손실**

풍부한 총합표를 **세 개나 찾았는데 DB 에 그 등급이 없다.**

- **MGC 三菱ガス化学** — 13 BT 등급 + EL190T/EL230T 가 `引張強さ·ヤング率·曲げ弾性率·熱伝導率·比熱·密度·ポアッソン比` **일곱 열을 전부** 찍는다. 우리 DB 에 `HL832*`·`HL972*`·`GHPL-830SR`·`EL190T`·`EL230T` **어느 것도 제품으로 없다.**
- **Sumitomo Bakelite** — `ELC-4762/4756·4970·4972R&S·4970GS·4765·4768` 가 `曲げ強さ·曲げ弾性率·引っ張り強さ·引っ張り弾性率·熱伝導率` 를 방향별로 찍는다. DB 에 ELC 등급 **없음**.
- **Resonac** — 일본어 66쪽 총합 카탈로그가 `弾性率(引張モード)` 와 `弾性率(曲げモード)` 를 **따로** 찍는다(Panasonic 과 같은 분리). DB 의 `Hitachi MCL-679`(재료 1227·1228)는 코어7이 통째로 비었지만, 카탈로그가 덮는 건 `MCL-E-679FG`·`MCL-HE-679G` 로 **접미가 다른 등급**이다. 등급 특정이 안 되므로 **넣지 않았다.**
- **MGC BT 라미네이트(재료 1276, role=evidence)** — MGC 수지 BT 라미네이트지만 Ehrler 2002 가 잰 무명 시료다. 13등급이 영률 21~34 GPa · 비열 0.9~1.00 J/g·K 로 **넓게 흩어져** 있어 대표값을 고르면 지어내는 셈이 된다. **비워 뒀다.**
- **Shengyi 가 다른 등급에는 인장 물성을 찍는다** — `SCGA-500/GF255`(`Tensile Modulus(LW/CW) 1.2/7.8 GPa`, `Tensile Strength 64/214 MPa`, `Density ASTM D792 2.25 g/cm3`), `S7136H`(`ASTM D638` 로 `16.1/18.5 GPa`, `175/245 MPa`), `LNB33`, `SI10US`(`Young's modulus 50℃ 26 GPa / 200℃ 23 GPa`). **표적 네 등급에는 안 찍는다.** 물성이 시험 레퍼토리에 없는 게 아니라, 그 등급 시트에 안 싣는 것이다.
- **Elite Material 도 마찬가지** — `EM-526`·`EM-528`·`EM-528K`·`EM-A50`·`EM-S370(Z)`·`EM-S376`·`EM-S526`·`EM-S530(K)`·`EM-S570` 열한 등급은 `Flexural Modulus Warp/Fill GPa` 를 찍는다. **표적 다섯 등급만 안 찍는다.** 그것도 굽힘이지 인장이 아니다.
- **Nan Ya 도 마찬가지** — `NP-730`·`NP-822`·`NP-826`(`Density ASTM D792 2.1 g/cm3`, `Thermal Conductivity ASTM F 433 0.6/0.25/0.37 W/mK`) · `NP-536HC`(`ASTM D5470 0.70`) · `NPG-200WT`(`ASTM-D5470 0.65`)는 RF·LED 등급이라 열전도율·밀도를 찍는다. **표적 FR-4 등급에는 없다.**
- **Arisawa 형제 계열** — RT 감광성 커버레이(`弾性率 0.8/1.1 GPa`, `破断強度 19/23 MPa`)와 2층 CCL(`引張り弾性率 5.5~6.5 GPa`)은 기계물성을 찍지만 **C33 이 아니다.** 수지계·구조가 달라 C33 의 값이 될 수 없다.

### 이번 배치가 손대지 않은 것 (정직하게 적는다)

- **Doosan MSDS/SDS 계열** — 동시에 도는 형제 배치가 그 축(120제품 183첨부)을 잡고 있어 건드리지 않았다.
- **ITEQ IT-180 / IT-200DK** (재료 2382·2383) — 형제 배치가 Chen 2007 논문 쪽을 렌더 중이라 손대지 않았다.
- **Panasonic 포아송비 t4→t1 갈아타기(R-1566S 외 6등급)** — 2013 판이 여섯 등급 모두에 `JISK7113 0.2` 를 찍는다. R-1566S 만 넣고 나머지는 형제 배치와의 중복을 피해 남겼다. **DC §5-1 이 이미 넘긴 항목이니 다음 배치가 확인해라.**

---

## 6. 다음 배치에 넘길 것

### 6-1. **DB 에 없는 세 벤더의 등급을 등록하는 게 이 형식의 다음 관문이다**

이 배치의 최대 손실은 문서가 아니라 **재료 목록**이다. 이미 확인된 총합표 세 개가 **지금 당장 코어7 을 여러 칸 채울 수 있는데** 대상 재료가 없다. 등급을 등록만 하면 문서는 이미 로컬에 있다:

- **MGC BT 계열 13등급** — `HL832NX(A)`·`HL832NS`·`HL832NS type LC`·`HL832NSR`·`HL832NSR type LCA`·`HL832NSF`·`HL832NSF typeLCA`·`HL832NSA typeLCA`·`HL972LF typeLD`·`HL972LFG`·`HL972LFG typeLD`·`GHPL-830SR`·`GHPL-830SR typeLC`. 일곱 물성이 한 표에 있다. 로컬 `pcb/MGC_CCL-HL832-HL972_BTResin_Lineup_ja_2026-09-09.html`, 영문 원본 `https://www.mgc.co.jp/eng/products/sc/btprint/lineup/hfbt.html`
- **MGC FR-4 2등급** — `EL190T`·`EL230T`. **시험조건 열(`A`)과 방향(縦/横)까지 가른 가장 깔끔한 표**다. `ポアソン比 縦 0.17 / 横 0.16`(EL190T)처럼 포아송비를 방향별로 찍는 흔치 않은 사례. 로컬 `pcb/MGC_CCL-EL190T-EL230T_FR4_Lineup_ja_2026-09-09.html`
- **Sumitomo Bakelite ELC 6등급** — `ELC-4762/4756`·`4970`·`4972R&S`·`4970GS`·`4765`·`4768`. **인장탄성률과 굽힘탄성률을 방향별로 따로** 찍는다(FR-4 등급은 인장 15 GPa vs 굽힘 16 GPa, CEM-3 등급은 12~14 vs 16~19 — **여기서도 굽힘이 인장보다 높다**). 로컬 `pcb/SumitomoBakelite_Sumilite_ELC_*_Spec_ja_2026-09-09.html`

### 6-2. **Panasonic 은 아직 한 칸 남았다 — R-1566S 의 비열**

2013(比熱 있음 · R-1566S 행 없음) ∩ 2021(R-1566S 행 있음 · 比熱 열 없음) = **공집합**.
**두 판 사이의 판을 찾아야 한다.** 로컬에 이미 `Panasonic_ElectronicMaterials_Catalog_2015-11_*`(3장)와 `Panasonic_CircuitBoardMaterials_Catalog_2019-06_*`(4장)가 있다 — **그 판들의 특성일람표 쪽을 렌더해서 `比熱` 열과 R-1566S 행이 동시에 있는지 확인해라.** 있으면 한 칸이 닫힌다.

2013년판 160쪽에는 이 배치가 안 쓴 형제 등급의 비열·열전도율이 더 있다 — `R-1577 935/0.50` · `R-2125 870/0.62` · `R-1755S 915/0.48` · `R-1755C 915/0.48` · `R-1766(T) 920/0.38` · `R-1533 929/0.58` · `R-1705 920/0.38` · `R-1515E 870/0.70` · `R-5775 880/0.42` · `R-5725 850/0.60`. **DB 에 이 등급들이 들어오면 같은 문서 한 장으로 다 닫힌다.**

### 6-3. Technolam 스캔 한 장이 Nan Ya 계열을 더 연다

`Technolam_NanYa_NP-155FTL-NP-155FR-NP-155FB_Datasheet_2024-08.pdf` 는 이 배치가 값을 뽑은 NP-175 시트와 **완전히 같은 서식**이고 `19. Other` 절도 같은 자리에 있다. 텍스트층이 474자뿐이라 **`pdftoppm -r 300` 으로 3/6 쪽을 렌더해 눈으로 읽으면** NP-155F 계열의 E-Modul·비열·열전도율이 한 번에 나온다. `NP-140TL`·`NPG-151`·`NP-175FTL 2024-08` 도 같은 상태다.
Technolam 시트가 덮는 다른 Nan Ya 등급 — `NP-140TL/B` · `NP-155F` · `NP-175FBH` · `NPG-150N` · `NPG-151` · `NPG-170TL/R/B` · `NPG-170D` · `NPG-180BH` · `NPGN-150PY` · `FR-4-11PY` · `UV-Block FR-4-86`.

### 6-4. Nan Ya 대만 포털의 AJAX 엔드포인트를 적어 둔다 (재크롤링용)

`https://cclqc.npc.com.tw/ccl/zh_TW/Index.do` 가 Nan Ya 의 실제 CCL 사업 포털이다(회사 사이트 `npc.com.tw` 와 **다른 호스트**이고, 회사 사이트 電子材料 카테고리에는 CCL 이 두 그룹뿐이라 NP-175x 가 아예 없다). 인증 없이 도는 POST 엔드포인트:
`/ccl/zh_TW/Product/getTglossXYAjax.ajax` · `getSubstrateAjax.ajax` · `getMicroXYAjax.ajax` · `/ccl/zh_TW/Certificate/getCategoryListAjax.ajax` + `searchAjax.ajax`. JSON 의 `filelink` → `/cclfile/pdt/Datasheet_<grade>_<epoch>.pdf`.
**證書及文件下載 카테고리에 型錄(카탈로그) 항목이 없다** — 있는 건 green partner / IATF16949 / CQC / EN45545-2 / ICP-SVHC / ICP-RoHS / SDS 뿐이다.

### 6-5. 검색 규율 — 다음 배치가 시간을 아끼도록

- **먼저 영문판을 확인하고 나서 자국어를 뒤져라.** 이 배치가 MGC 에서 시간을 버렸다 — 자국어 표를 «발견»했는데 그 값은 이미 **영문 페이지에서** DB 에 들어와 있었다.
- **가르는 축은 언어가 아니라 «총합 특성일람표 vs 등급별 TDS» 다.** 벤더에게 물을 질문은 「자국어 문서가 있나?」가 아니라 **「전 등급을 한 표에 늘어놓은 문서가 있나?」**다. 그 표는 영어일 수도 있다(MGC·Sumitomo·Resonac·Doosan 8쪽 TDS).
- **두 번째 축은 «IPC-4101 서식 바깥의 덧붙임 절»이다.** Nan Ya 값 여섯은 자국어가 아니라 **독일 파트너가 IPC-4101 항목 1~18 뒤에 붙인 `19. Other / weitere`** 에서 나왔다. 유통사·상사가 낸 시트를 볼 때 **표 끝의 «기타» 절을 반드시 열어라.**
- **벤더 도메인부터 확정해라.** Shengyi 는 `shengyi.com`·`sytech.com.cn`·`shengyi.com.cn` 이 **전부 도메인 매매·광고 파킹 페이지**다. 진짜는 **`www.syst.com.cn`**. Nan Ya 는 회사 사이트가 아니라 **`cclqc.npc.com.tw`** 다.
- **`Young's Modulus` 라는 이름을 믿지 마라 — 세 번째 변종을 찾았다.** DC 는 Isola(굽힘에 그 이름을 붙임)와 Panasonic(둘을 가름)을 봤다. **MGC 는 세 번째다 — `Young's Modulus` 행과 `Flexural Modulus` 행에 13등급 전부 같은 숫자를 찍는다**(28/28, 27/27, 30/30, 33/33, 32/32, 25/25 …). 두 행이 있다고 두 시험을 한 게 아니다.
- **Resonac 카탈로그의 각주 번호는 쪽마다 다른 뜻이다.** 한 쪽에서 `*2` = `800 μm thickness`, 다른 쪽에서 `*2) Tensile`. 각주를 쪽 단위로 다시 읽어라.
- **일본어 표기 흔들림을 검색어에 다 넣어라.** MGC 는 같은 사이트에서 BT 쪽은 `ポアッソン比`, FR-4 쪽은 `ポアソン比` 로 쓴다. Sumitomo 는 `引っ張り強さ`(っ 있음)라 `引張強さ` 로만 grep 하면 놓친다. Arisawa 는 인장강도를 `破断強度` 로 쓴다.
- **`S1170`(G 없는 것)은 Shengyi 사이트에 존재하지 않는다** — `S1170G` 11회, 맨 `S1170` 0회. DB 재료 601 의 이름을 다시 볼 필요가 있다.

---

## 산출물

- `out_eb/eb01_materials.json` — **9 재료 · 22 행** (Panasonic 7재료 16행 t1 · Nan Ya 2재료 6행 t2)
- `out_eb/eb02_verdicts.json` — **판정 148건 / 재료 82종.** 열어 본 형식과 확인한 열 부재를 표적별로 적었다 (Doosan 비열 79 · 인장강도 58 · EMC/Shengyi 영률 8 · Shengyi 열전도율 3, Arisawa C33 인장강도, Panasonic R-1566S 비열은 `not_found_yet`)
- 이 배치가 새로 받아 코퍼스에 넣은 원문 (`/data/paper_patent_corpus/standards_appnotes/pcb/`)
  - **MGC(일본어 라인업 HTML 3)** `MGC_CCL-HL832-HL972_BTResin_Lineup_ja_2026-09-09.html` · `MGC_CCL-EL190T-EL230T_FR4_Lineup_ja_2026-09-09.html` · `MGC_CCL-HL820WDI_ChipLED_BT_Lineup_ja_2026-09-09.html`
  - **Sumitomo Bakelite(일본어 spec HTML 5)** `SumitomoBakelite_Sumilite_ELC_DoubleSided_CCL_Spec_ja_*` · `_Multilayer_PWB_Spec_ja_*` · `LAZ-4785`·`LAZ-6785`·`LAZ-7752`
  - **Resonac(일본어 총합 카탈로그)** `Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf` (66쪽)
  - **Arisawa(일본어 시트 19 + 영문 C33 · 총 20)** `Arisawa_Coverlay_C33_LowDk_Catalog_ja_2025-07.pdf` · `_en_2025-07.pdf` · `Arisawa_PhotosensitiveCoverlay_RT-Series_Catalog_ja_2023-07.pdf` · `Arisawa_2LayerCCL_Catalog_ja_2023-07.pdf` 외
  - **Elite Material(데이터시트 16 + zh-TW 인덱스 1 · 총 17)** `EMC_EM-370Z_EM-37BZ_`·`EM-370-5_`·`EM-888_`·`EM-890_`·`EM-891_Datasheet_20240716.pdf` 및 모듈러스가 있는 11장
  - **Shengyi(중국 사이트 PDF 18 + 제품페이지 HTML 6 · 총 24)** `Shengyi_S1170G_TDS_zh.pdf` · `S1000-2M_`·`S7439_`·`SCGA-500_GF255_`·`S7136H_`·`LNB33_`·`SI10US_`·`SI13U_` 외
  - **Nan Ya(대만 포털 시트 37 + 구판·아카이브 7 · 총 44)** `Nanya_CCL_*_Datasheet_cclqc_zhTWportal_2026-09-09.pdf` · `Nanya_CCL_ProductCatalog_2001-09_scanned_52p.pdf` · `Nanya_CCL_Catalog2007_p75-76_NP-155FTL.pdf` · `Nanya_CCL_NP-175FR-TL-B_Datasheet_2014_archived.pdf` · `Nanya_CCL_NPG-150N-B_`·`NPG-171-B_2014_archived.pdf` · `Nanya_CCL_NP-175FR_Kunshan_2009_speedycircuits.pdf` · `Nanya_CCL_BaseMaterials_Overview_Technolam_via_semach_2p.pdf`
  - **Doosan(구판 카탈로그 8)** `Doosan_CCL_DS-7402_LegacyCatalogPage_dse.co.kr_2005.pdf` · `DS-7402H_`·`DS-7409_`·`DS-7409H_HB_` · `DS-8405_2003_scanned.pdf` · `PREPREG_` · `DS-7402_CatalogPDF_2019.pdf` · `DS-7209A_CatalogPDF_2021.pdf`
- **값의 출처가 된 문서는 전부 이미 코퍼스에 있던 것이다** — `Panasonic_ElectronicMaterials_catalog_2013_JP_*`(68차 DC), `Panasonic_CircuitBoardMaterials_PropertyList_*_2021-03.pdf`, `Technolam_NanYa_NP-175FTL-NP-175FR-NP-175FB_Datasheet_2021-01.pdf`(68차 DC). **이 배치가 새로 받은 문서는 `pcb/` 아래 122개인데, 그 122개에서 나온 값은 0이다** — 그게 §1 수확표의 답이다. 새 문서는 값을 낸 게 아니라 **부재를 확정**했다(판정 148건). 값은 전부 «이미 갖고 있었지만 아직 안 읽은 쪽»에서 나왔다.
