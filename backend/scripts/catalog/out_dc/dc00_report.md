# 68차 DC — 영률 25종, 대부분 PCB 라미네이트

표적 25종은 전부 **카드 한 칸(영률)만 남은 재료**였고 전부 이미 부재판정이 걸려 있었다.
판정문은 대개 *"제품 TDS 에 영률 행이 없다"* 였다 — 그건 **그 형식에 없다는 뜻이지 공개 문서에 없다는 뜻이 아니다**(브리프 §627).
이 배치는 TDS 밖의 형식만 두드렸다.

**결과 — 25종 중 9종에 카드가 섰다.** 값 21행. **굽힘탄성률로 채운 칸은 0건이다**(그 이유는 §3).

---

## 1. 형식별 수확 — 이 배치의 핵심 수치

| # | 형식 | 실제로 연 문서 | 값 | 카드 |
|---|---|---|---|---|
| ① | **IPC-4101 규격·슬래시시트** | 6 | **0** | 0 |
| ② | **벤더 설계가이드·공정가이드·응용노트** | 7 | **0** | 0 |
| ③ | **벤더 자국어 '총합 카탈로그'** ← 브리프에 없던 형식 | 1 | **12** | **6** |
| ④ | **유럽 공급사가 다시 낸 IPC-4101 서식 Datenblatt** | 14 | **8** | **2** |
| ⑤ | **학술 문헌** | 11 | **1** | **1** |
| ⑥ | 기존 TDS 의 새 개정판·다른 판형 재독 | 7 | 0 | 0 |
| | **합계** | **46** | **21** | **9** |

### ① IPC-4101 슬래시시트 — **구조적으로 닫힌 문이다. 다시 두드리지 마라**

브리프의 첫 가설은 `CCL 이 IPC-4101 /126 으로 분류되니 규격 본문이 요구 물성을 인쇄할 것` 이었다. 규격을 실제로 열어 **이 물성에 대해서는 그 가설이 틀렸음을 확정했다.**

IPC 배포 **IPC-4101E 공식 목차**의 §3.9.1 `Physical Requirements of Laminate Materials` 하위 항목 전부:

> 3.9.1.1 Peel Strength(+열스트레스후·고온·공정약품후 세 변형) · 3.9.1.2 Dimensional Stability ·
> **3.9.1.3 Flexural Strength** · **3.9.1.4 Flexural Strength at Elevated Temperature** ·
> 3.9.1.5 Thermal Conductivity · 3.9.1.6 CTE(선택) · 3.9.1.7 Z-Axis CTE/Total Expansion(선택) · 3.9.1.8 Fracture Toughness(선택)

**여덟이 전부이고 어떤 탄성률도 없다.** §3.10 화학·§3.11 전기·§3.12 환경에도 없다.
1997 초판에 `modulus`·`elastic` 낱말 **0건**. 슬래시시트 재판본(`IPC4101/24`)도 Tg·Dk·보강재·수지계뿐.
→ **슬래시시트는 굽힘'강도' 하한을 규정하지 그 등급의 탄성률을 규정하지 않는다.**

부수 수확 — Panasonic 공식 대응표를 확보했다: R-1755V→/126, R-1755M·R-1755D→/99, R-1755E→/101, R-1766→/21, R-1566→/127.

**덫 하나 적어 둔다.** `inorsen.com/downloads/resources/pdf/ipc-4101.pdf` 가 "IPC-4101" 제목 아래 `Young's Modulus: 18-24 GPa` 를 찍는다. **등급이 없는 마케팅 개요이고 IPC-4101 에 없는 값을 규격 것처럼 붙여 놓았다. 쓰지 마라.**

### ② 벤더 설계가이드 — 존재하지만 이 물성이 없거나, 아예 공개되지 않는다

- Shengyi 는 S7439 에 대해 TDS 말고 **`Process Guidelines`·`Lineups`** 를 실제로 따로 낸다. 셋 다 받아 낱말 검색 — `modulus`·`GPa` **0건**.
- Elite Material 공개 문서구역 전수 — 내주는 PDF **48 장이 모두 등급별 TDS 한 종류**이고 설계가이드류가 **존재하지 않는다**.
- Panasonic 제품페이지는 `[ プロセスガイドライン ]` 칸을 두지만 내용이 **「担当営業にお問い合わせください」**(영업 문의) — 공개 문서가 아니다.

### ③ 벤더 자국어 '총합 카탈로그' — **이 배치 최대의 수확이자 형식 교훈**

Panasonic 여섯 등급의 부재판정을 깬 것은 새 TDS 가 아니라 **2013년 일본어 「電子回路基板材料」 총합 카탈로그(160쪽)** 였다.
그 카탈로그의 `特性一覧表《参考値》板厚：1.6mm` 두 쪽짜리 표는 **`曲げ弾性係数（JIS C6481）` 열 옆에 따로 `ヤング率（引張り）（ASTM D3039）` 열**을 둔다 — 굽힘과 인장을 원문이 스스로 갈라 인쇄한다.

시험조건도 같은 카탈로그가 인쇄한다(인쇄쪽 19 `試験項目の用語解説`):
> 「●ヤング率（ASTM D3039）下図の様に幅15mmの短冊状サンプルをつかみ間距離125mmで引張・圧縮試験機にセットします。引張り速度2mm/分で引張り強度を測定し、引張り応力と歪みの関係から求めます。」

**교훈: 벤더의 제품페이지·등급별 TDS·SDS 를 다 열고도 "없다"고 하기 전에, 그 벤더가 자국어로 내는 수십~수백 쪽짜리 총합 카탈로그를 찾아라.**

### ④ 유럽 공급사가 다시 낸 IPC-4101 서식 Datenblatt — 두 번째 새 형식

Technolam GmbH(독일, Nan Ya 의 유럽 파트너)는 제조사 TDS 와 **별개의** `Data Sheet / Datenblatt` 를 낸다.
IPC-4101 항목 1~18 을 그대로 따른 뒤 **`19. Other / weitere` 절을 덧붙여 IPC-4101 이 규정하지 않는 행을 더 찍는다**:

> `Young's Modulus / E-Modul` (Kettrichtung 경사 · Schussrichtung 위사, GPa) · `Specific Heat at 25 °C` ·
> `Density (50 % resin content)` · `Thermal Conductivity`(ASTM-E-1461 / ASTM-D-5470 두 값) · `Caloric Value` · `CTI`

Nan Ya NP-175FR·NP-175FTL 의 영률이 이 문으로 열렸다(23-25 / 22-24 GPa, 세 판이 여섯 해 동안 같다).
다만 Technolam 은 **Nan Ya 전용**이다 — 받아 본 열넉 장이 전부 Nan Ya 계열이고 EMC·Shengyi·Panasonic 시트는 한 장도 없다.

### ⑤ 학술 문헌 — 한 건 열렸고, 이 문은 **제대로 열리지 않았다**

SAC107(Sn-1.0Ag-0.7Cu)의 영률이 **JSME 2011년도 연차대회 논문 S031021**(佐竹 외, 鉛フリーはんだ材の低サイクル疲労強度特性)의 `Table 1 Tensile Test Results` 에서 나왔다 — 31 GPa.
58·60·66차가 두드린 스물한 문은 전부 **솔더합금 디렉터리**였고, 이번에 열린 것은 **이 조성을 직접 인장시험한 일본어 학회논문**이다.

**그러나 이 문은 표적 전반에 대해서는 열리지 않았다.** OpenAlex·Semantic Scholar 는 제목·초록만 색인해서 **논문 표 안에 사는 등급명을 못 찾고**, DuckDuckGo·Mojeek·scholar.archive.org·HathiTrust 전문검색은 이 실행환경에서 막혔다(403·DNS).
→ **CCL 등급명에 대한 학술 0건은 부재의 근거가 아니다.** 다음 배치의 1순위.

---

## 2. 넣은 값과 선 카드

**9 재료 · 21 행 · 카드 9 장** (`out_dc/dc01_materials.json`)

| 재료 | 값 | 시험 | 출처 형식 |
|---|---|---|---|
| Nan Ya NP-175FR | 경사 23-25 · 위사 22-24 GPa (4행) | 원문 이름 `Young's Modulus`, **시험방법 칸 `-`** | ④ Technolam Datenblatt |
| Nan Ya NP-175FTL | 경사 23-25 · 위사 22-24 GPa (4행) | 위와 같음 | ④ |
| Panasonic R-1755V | 縦 20.3 · 横 18.2 GPa | **인장 ASTM D3039** | ③ 2013 총합카탈로그 |
| Panasonic R-1755M | 縦 20.5 · 横 19.0 GPa | 인장 ASTM D3039 | ③ |
| Panasonic R-1755D | 縦 19.2 · 横 17.8 GPa | 인장 ASTM D3039 | ③ |
| Panasonic R-1755E | 縦 20.0 · 横 18.5 GPa | 인장 ASTM D3039 | ③ |
| Panasonic R-1566 | 縦 20.9 · 横 19.8 GPa | 인장 ASTM D3039 | ③ |
| Panasonic R-1766 | 縦 17.8 · 横 16.5 GPa | 인장 ASTM D3039 | ③ |
| SAC107 | 31 GPa | 인장, 室温, ε̇≈1e-4/s, n=2 | ⑤ JSME 2011 S031021 |

등급: Panasonic 6종과 SAC107 은 **t1**(제조사·저자가 그 등급에 인쇄한 값). Nan Ya 2종은 **t2** — 발행처가 제조사가 아닌 유럽 파트너이고, 시험방법 칸이 비어 있으며, 같은 값을 같은 발행처의 NPG-170 계열 시트가 되풀이해 **등급별 실측이 아니라 계열 공통값**으로 읽히기 때문이다. 그 사유를 `conditions.grade_scope` 에 적었다.

인쇄된 구간(23-25 · 22-24)은 평균 내지 않고 `bound: lower`/`upper` 두 행으로 갈랐다. 경사·위사가 갈려 인쇄된 곳은 두 방향을 각각 넣었다.

---

## 3. 굽힘탄성률로 채운 칸 — **0건. 하마터면 12건이 될 뻔했다**

이 배치는 중간에 **Panasonic 여섯 등급의 굽힘탄성률(JIS C6481, 23~24 GPa)을 영률 칸에 옮긴 12행을 실제로 만들었다.** 브리프가 그것을 허용했고, 동종 벤더 Isola 가 `Young's Modulus` 라는 이름의 행을 `ASTM D790`(3점굽힘)으로 재는 업계 관행이 근거가 됐다.

**그 12행을 뒤에 찾은 진짜 인장 영률로 전부 갈아치웠다.** 두 값이 이렇게 갈렸기 때문이다:

| 등급 | 曲げ弾性係数 (JIS C6481) 縦 | ヤング率(引張り) (ASTM D3039) 縦 | 차 |
|---|---|---|---|
| R-1755V | 24 | 20.3 | −15 % |
| R-1755M | 24 | 20.5 | −15 % |
| R-1755D | 23 | 19.2 | −17 % |
| R-1755E | 24 | 20.0 | −17 % |
| R-1566 | 24 | 20.9 | −13 % |
| R-1766 | 23 | 17.8 | **−23 %** |

**굽힘값을 그대로 넣었다면 이 여섯 등급의 강성을 12~23 % 부풀렸을 것이다.** 대칭 유리직물 적층판이라 두 값이 가까울 것이라는 물리적 직관은 이 크기의 오차를 정당화하지 못한다.

이 대조는 **검색어 교훈**으로도 남는다 — Isola 는 굽힘값에 `Young's Modulus` 라는 이름을 붙이고, Panasonic 은 둘을 갈라 찍는다. **이름만 보고 인장으로 읽으면 안 된다.** 그리고 Nan Ya 의 23-25 GPa 는 시험방법 칸이 비어 있는데 **인장대(17~21)가 아니라 굽힘대(23~24)에 놓인다** — 그 사실을 값의 notes 에 적어 두었다.

같은 이유로 **비-CCL 세 갈래는 굽힘값으로 메우지 않았다**:
- LEXAN 3413R(PC-GF30) — 형제 3412R(GF20)은 인장 6000 MPa 가 굽힘 5511 MPa 보다 **높다**. 사출 유리충전계는 대소가 반대로도 난다.
- Victrex PES 420P·430P — 스킨-코어 배향으로 굽힘이 인장을 웃도는 것이 보통이고 등급마다 차가 다르다.
- 1314 언더필 — 이번 배치가 손대지 않았다.

---

## 4. 못 넣은 것 — 셋으로 갈라 적는다

### (가) 형식에 그 항목이 없었다 (문서를 열었고 행이 없음을 확인) — 13종
- **Elite Material 5종**(EM-370Z·EM-370(5)·EM-890·EM-888·EM-891) — TDS 48장 전수 + IPC-4101 + 유통사 3경로. 이 벤더의 강도축은 `Flexural Strength Warp/Fill` 하나다.
- **Shengyi 3종**(S1170·S1170G·S7439) — TDS + **Process Guidelines** + Lineups + 스캔 브로슈어 + 2006 물성표 + 웹표 xlsx 셀 단위 재독(공유문자열 79개 전수, `modul`·`弹性`·`Young` 0건).
- **Panasonic R-1566S** — 전용 카탈로그(2020-07)에 `曲げ弾性率` 가 **그래프로만** 있고 숫자 표가 없다. 제품페이지 HTML 셀 단위 재독 — `弾性率` 0건.
- **LEXAN 3413R** — 64차가 못 열었던 **Asia Rev 20190920** 을 새로 열었으나 MECHANICAL 절이 인장은 강도·연신만, 강성은 `Flexural Modulus 6610 MPa (ASTM D790)` 만 찍는다. SABIC ASTM 서식의 규칙이다.
- **Victrex PES 3종** — Thompson 1983 표 5장을 직접 재독. `Table 2` 의 강성축은 `Flexural modulus (ASTM D790)` 하나이고 인장탄성률 행이 없다.

### (나) 문서를 못 열었다 (판정이 아니다 — 다음 배치의 표적)
- **학술 전문(全文)색인 전반** — Google Scholar·CORE·Elsevier 접근 없음. **CCL 등급명에 대한 0건은 무효다.**
- `matweb.com` 의 **`SABIC Lexan 3413R Polycarbonate (Europe)`** 항목 — HTTP 403. **Europe 항목이 따로 존재한다는 사실 자체가 유럽 데이터의 존재를 시사한다.**
- `matmatch.com` — DNS 차단. `Victrex 430P` 를 상품명으로 여는 PES-GF30 페이지가 있다(다만 계열값이라 t3).
- **Searle & Pfeiffer, Polym. Eng. Sci. 25(8):474-476 (1985), ICI Americas 저자** — 유료. **ICI 자신이 쓴 PES 등급표가 실릴 가장 유력한 후보.**
- ICI 원 브로슈어 `Victrex, Polyethersulphone…`(1979) — 특허 인용에만 존재, 온라인 부재.
- MATEC Web Conf. 300, 12004 (2019) Makino/Ogawa/Itoh — 403. 전문색인상 `Sn1.0Ag0.7Cu` 와 `Young's modulus` 를 함께 담고 있다.
- ANSI webstore 의 IPC-4101E 전문 — 403(목차로 대체 판정).

### (다) 등급이 안 맞았다
- **R-1566S 가 2013 총합카탈로그 표에 없다** — 그 카탈로그보다 뒤에 나온 등급이다. 형제 여섯은 다 열렸는데 이 하나만 남았다.
- **`SAC107 + BiIn` 40 GPa 를 기각했다** — Sci. Rep. 2025;15:24340 Table 1 이 찍지만 본문이 Senju M40 = Sn-1.0Ag-0.7Cu-**1.6Bi-0.2In** 으로 밝힌다. 조성이 다르다. **이 40 GPa 를 SAC107 에 병합하지 마라.**
- Victrex 계열 — Sumikaexcel 은 3600P/4100P/4800P/5200P 계열이고 ICI 코드 대응표가 없다. 高分子論文集 1993·1994 의 인장탄성률은 **4800P** 값이다.
- Technolam 의 23-25 / 22-24 GPa 는 NPG-170TL/R/B 시트도 똑같이 찍는다 → 등급 특정값이 아니라 계열값. t2 로 낮추고 `grade_scope` 에 적었다.

### 이번 배치가 손대지 않은 것 (정직하게 적는다)
- **581 Sn-9Zn-2.5Bi-0.5In-0.01P** — 논문이 만든 개발합금이라 세상에 Liu 2014 한 편뿐이고, 66차까지 그 한 편을 전권으로 다 열었다. 이번 배치는 **새 문서를 하나도 열지 않았다** — 그러므로 판정을 갱신하지 않았다.
- **1314 리워커블 언더필** — 마찬가지로 새 문서를 열지 않았다.
- **111 Liquid Electrolyte** — 기존 `core_not_applicable`(액체라 전단강성이 없어 영률이 정의되지 않는다)이 물리적으로 옳다. 손대지 않았다.

---

## 5. 다음 배치에 넘길 것

### 5-1. **Panasonic 2013 총합카탈로그가 코어 여러 칸을 한꺼번에 연다 — 가장 큰 인계**

같은 표(인쇄쪽 16~17)가 이 등급들에 대해 **비중·비열·열전도율·포아송비·Tg·Td 를 한꺼번에 인쇄한다.** 특히 **포아송비 `JIS K7113, 23±3℃` = 0.2 가 인쇄돼 있다** — 현재 이 재료들의 포아송비는 전부 t4 클래스 중앙값(class_n=59)이다. **t1 인쇄값으로 갈아탈 수 있다.**

verbatim (단위 행: `−  |  J/kg℃  |  W/m・K  |  −  |  ℃ …`, 시험법 행: `JIS K6911 | DSC法 | レーザーフラッシュ法 | JIS K7113 | TMA法 | DSC法 | DMA法 | TG/DTA法(5%減)`):

| 品番 | 比重 | 比熱 J/kg℃ | 熱伝導率 W/m·K | **ポアソン比** | Tg(TMA) | Tg(DSC) | Tg(DMA) | Td |
|---|---|---|---|---|---|---|---|---|
| R-1755V | 1.96 | 910 | 0.53 | **0.2** | 165 | 173 | 190 | 350 |
| R-1755S | 1.93 | 915 | 0.48 | **0.2** | 170 | 175 | 185 | 370 |
| R-1755D | 1.98 | 900 | 0.63 | **0.2** | 154 | 163 | 185 | 345 |
| R-1755M | 2.00 | 930 | 0.57 | **0.2** | 150 | 153 | 175 | 355 |
| R-1755E | 1.98 | 930 | 0.55 | **0.2** | 133 | 133 | 153 | 370 |
| R-1755C | 1.93 | 915 | 0.48 | **0.2** | 135 | 135 | 155 | 370 |
| R-1766 | 1.91 | 920 | 0.38 | **0.2** | 140 | 140 | 150 | 315 |
| R-1766(T) | 1.91 | 920 | 0.38 | **0.2** | 170 | 170 | 190 | 315 |
| R-1566 | 2.00 | 950 | 0.62 | **0.2** | 145 | 148 | 170 | 350 |

같은 표의 `ヤング率（引張り）` 열에는 이 배치가 안 쓴 형제 등급도 있다 — R-1755S 20.9/18.0 · R-1755C 18.5/16.7 · R-1766(T) 18.9/16.3 · R-1533 19.9/19.3 · R-1705 17.8/16.5 · R-1515E 27.0/25.0 · R-5775 16.3/14.3 · R-5725 17.2/15.9 · R-1577 18.1/16.7 · R-2125 21.8/21.7 GPa. **카탈로그에 이 등급들이 있으면 같은 문서 한 장으로 다 닫힌다.**

로컬: `/data/paper_patent_corpus/standards_appnotes/pcb/Panasonic_ElectronicMaterials_catalog_2013_JP_YoungsModulus_ASTM-D3039_table.pdf`

### 5-2. Technolam Datenblatt 가 Nan Ya 계열 코어를 연다

NP-175FTL/FR/FB 시트 `19. Other` 절 verbatim: `Specific Heat at 25 °C 0,91 J/g°C` · `Density (50 % resin content) 2,10 g/cm³` · `Thermal Conductivity 0,53 (ASTM-E-1461) / 0,46 (ASTM-D-5470) W/mK` · `CTE X/Y 10-14 ppm/°C` · `CTI 3 / 175-249 PLC/V`.
현재 2440·2441 은 열전도율·비열이 비어 있다.

받아 둔 Technolam 시트 열넉 장이 다른 Nan Ya 등급도 덮는다 — NP-140TL/B · NP-155F · NP-175FBH · NPG-150N · NPG-151 · NPG-170TL/R/B · NPG-170D · NPG-180BH · NPGN-150PY · FR-4-11PY · UV-Block FR-4-86.
확인된 E-Modul: NPG-170TL/R/B 와 NPG-150N 은 23-25/22-24, **NPG-170D 는 24/22, NPG-180BH 는 24/22** (계열 공통값이지만 완전한 상용구는 아니다).
**2024~2025 판은 텍스트층 없는 이미지 PDF다 — `pdftoppm -r 200` 으로 렌더해 눈으로 읽어라.**

### 5-3. 아직 안 열린 문 (우선순위 순)
1. **학술 전문검색** — Google Scholar 세션 또는 CORE/Elsevier 키. CCL 등급명은 논문 *표 안*에 살아서 초록 색인으로는 절대 안 잡힌다.
2. **EMC·Shengyi 의 자국어 종합 카탈로그** — Panasonic 에서 통한 수가 그대로 통할 수 있다. 검색어: `綜合型錄` · `综合型录` · `产品手册` · `技術資料集`, 그리고 웹아카이브의 구판.
3. **다른 유럽·아시아 유통사의 Datenblatt 서식** — 독일어 검색어가 잘 먹는다: `Datenblatt` + `E-Modul` + `Kettrichtung` + `Schussrichtung` + `Laminat`.
4. **matweb / matmatch 우회** — 403·DNS 로 막혔다. LEXAN 3413R Europe 항목이 여기 있다.
5. **Searle & Pfeiffer 1985 (Polym. Eng. Sci.)** — Victrex PES 세 칸을 한 번에 닫을 후보.

### 5-4. R-1566S 한 칸을 닫는 두 갈래
- (가) **2013 카탈로그의 뒷 판**(2015·2019·최근판)을 찾아라. 그 서식에 R-1566S 행이 있으면 영률·포아송비·비열·열전도율이 한꺼번에 닫힌다.
- (나) 2020-07 전용 카탈로그의 `曲げ弾성率` 온도곡선을 `digitize_curve` 로 읽되 **method `digitized` · t4 · 상온 절편만** 정직하게.

### 5-5. 값 다루는 이의 주의
- **SAC107 31 GPa 는 조건과 함께 읽어야 한다.** 같은 표의 SAC305 도 30 GPa 로 문헌 통상대(40~50)보다 낮다 — 이 논문의 측정계(스트로크 제어 + 시편 부착 변위센서, ε̇≈1e-4/s)가 낮게 나오는 쪽이지 SAC107 만 별종인 것이 아니다. 상온이 이미 0.6 T_m 이라 이 속도에서 점소성이 탄성구간에 섞인다.
- **Nan Ya 23-25 / 22-24 GPa 는 test_mode 가 `not printed` 다.** 값의 크기가 굽힘대에 놓이므로, 면내 인장강성으로 쓰면 12~23 % 높게 잡힐 수 있다.
- **`Young's Modulus` 라는 이름을 믿지 마라.** Isola 는 그 이름을 `ASTM D790`(굽힘)에 붙인다. 찾은 뒤 시험방법 칸을 반드시 확인해라.

---

## 산출물

- `out_dc/dc01_materials.json` — 9 재료 · 21 행
- `out_dc/dc02_verdicts.json` — 13 판정 갱신 (열어 본 형식을 덧붙이는 형태)
- `out_dc/gen_dc02_verdicts.py` — 판정 파일 생성기
- 새로 받은 원문 (`/data/paper_patent_corpus/standards_appnotes/`):
  - `pcb/Panasonic_ElectronicMaterials_catalog_2013_JP_YoungsModulus_ASTM-D3039_table.pdf`
  - `pcb/Technolam_NanYa_*.pdf` (14장)
  - `pcb/JSME2011_S031021_Satake_LowCycleFatigue_LeadFreeSolder_SAC107_Sn-1.0Ag-0.7Cu_YoungsModulus_31GPa.pdf`
  - `pcb/IPC_IPC-4101E_TableOfContents_2017.pdf` · `pcb/IPC-4101_1997_BaseMaterials_Rigid_Multilayer_Spec.pdf`
  - `pcb/LaminatedPlastics_IPC-4101-24_TechnicalDataSheet.pdf` · `pcb/AGC_IPC-4101E_SlashSheet_ReferenceGuide.pdf` · `pcb/Epec_IPC-4101E_SlashSheetMatrix_Panasonic.pdf`
  - `poly/SABIC_LEXAN_FR_Resins_3413R_Asia_TDS_Rev20190920.pdf`
  - `pcb/SciRep2025_Akhtar_AI-FEA_SolderJoint_SenjuM40_SAC107+BiIn_YoungsModulus_40GPa.pdf` (**기각한 값의 근거로 보관**)
