<!-- 67차 CC 배치 보고서 — TAC(트리아세틸셀룰로스) 산소투과 수집 결과 -->

# 67차 CC — TAC 산소투과

표적: 산소확산 해석 `oxygen_stack_2d` 의 적층 ④ TAC 40 µm.
요청서 `PDE/oxygen-diffusion/물성요청_산소확산_원자재6종.md` 3순위 항목.

라이브 DB 는 읽기 전용으로만 열었다. **DB 에 직접 쓴 것은 없다.** 산출물은 `out_cc/` 안의 JSON 두 개다.

---

## 1. (a)/(b) 판단 — (a) 로 갔다. 새 카드를 만들었다

브리프가 물은 것: 순수 TAC 값을 **재료 88 `Polarizer (TAC/PVA)`** 에 붙일 것인가, 새 카드를 세울 것인가.

**(a) 새 카드를 세웠다.** 이름은
`Cellulose triacetate (TAC/CTA) optical film, display polarizer protective film class (grade not identified)`.
**재료 88 은 한 칸도 건드리지 않았다.**

이유 넷.

1. **88 은 물성적으로 스택이다.** 편광판은 TAC / 연신·요오드 염착 PVA / TAC 의 적층이고, PVA 는 건조 조건에서 대표적인 고산소배리어 소재로 알려져 있다(이번 배치는 PVA 의 산소투과값 자체를 확인하지 않았다 — 그래서 이것은 숫자가 아니라 분리 근거로만 쓴다). 즉 이 적층 전체의 산소투과는 TAC 단층의 투과와 같을 수 없다. TAC 단층 값을 88 에 붙이면 그 카드를 읽는 쪽은 그것을 적층의 값으로 읽는다 — 조건 문자열로 막을 수 있는 종류의 오독이 아니다.
2. **해석이 원하는 것은 단층이다.** `oxygen_stack_2d` 의 ④층은 그 적층의 TAC **한 장(40 µm)** 이다. 해석은 층별로 `Dᵢ·Sᵢ·tᵢ` 를 쌓으므로 스택 카드가 아니라 단층 카드를 읽어야 한다.
3. **조건 어휘가 88 에 안 맞는다.** 이번에 넣는 값은 아세틸 치환도(DS)·가소제 유무·RH 로 갈리는데, 이 조건들은 "TAC 단층" 에 붙는 것이지 "TAC/PVA 적층" 에 붙는 말이 아니다.
4. **되돌리기 비용.** 새 카드는 더하기다. 88 에 잘못 붙였다가 나중에 떼는 것은 다른 소비자(스마트폰 display 카드 18물성을 이미 쓰는 쪽)까지 흔든다.

부작용으로 88 의 산소 칸은 여전히 비어 있다. 그것이 맞다 — **적층 전체의 산소투과는 아무도 재지 않았고 나는 그것을 지어낼 수 없다.**

---

## 2. 넣은 값 — 5행

### 2.1 TAC 카드 (신규) — `physical.gas_permeability_o2` 3행, 전부 tier 3

`out_cc/cc01_tac_o2.json`

| # | 값 mol/(m·s·Pa) | Barrer | 조건 | 출처 | tier |
|---|---|---|---|---|---|
| 1 | 2.6102e-16 | 0.780 | 25 °C, RH 미기재, **가소화 CA** | Membranes 2024, 14, 148 Table 3 → 원표 **Pauly, Polymer Handbook VI 장** | 3 |
| 2 | 1.6508e-16 | 0.493 | 20 °C, **RH 0%**, 캐스팅 CA 치밀막 | BioResources 8(2):3098 (Paunonen 2013) → 원측정 Nakai 2005 | 3 |
| 3 | 4.0755e-17 | 0.122 | 23 °C, **RH 50%**, CA 배리어 필름 | Chem. Rev. 2025 Table 3 → 원측정 Zhou 2022 | 3 |

**세 행이 전부 tier 3 인 이유는 하나로 모인다 — 셀룰로스 아세테이트(CA)이지 트리아세테이트(CTA)가 아니다.** 각 행의 `grade_scope` 에 그 어긋남을 세 겹(화학·배합·제품)으로 적었다. 개별 사유는 여기에 더해 (1) RH 미기재 + 가소제 첨가, (2) 막분리용 캐스팅 치밀막, (3) 리뷰의 2차 인용 + 원측정 유료.

**이 값들은 TAC 에 대해 하한 쪽이다.** 아세틸 치환도가 오르면 산소투과가 오른다는 것이 문헌 합의이고(Puleo, Paul & Kelley, *J. Membr. Sci.* 47:301, 1989 — 내가 연 리뷰 셋이 모두 이 결론을 인용한다), CTA(DS≈2.9) 는 CA(DS≈2.4~2.5) 보다 위다. **그 방향만 적었고 그것으로 TAC 값을 계산하지 않았다.** 역산 금지 원칙이다.

**그 간격이 얼마인지에 대한 유일한 실측 단서** — *Membranes* 2021, 11, 245(PMC8067227)가 **같은 연구실·같은 방법**으로 순수 CTA(DS≈2.84)와 순수 CDA(DS≈2.45) 를 나란히 잰다. Table 3 verbatim: `CTA/CA (100:0) 18.50 ± 0.12` · `CTA/CA (0:100) 11.08 ± 0.42` (CO₂ Barrer). 즉 **DS 2.45 → 2.84 에서 CO₂ 투과가 1.67 배**다. 산소가 정확히 같은 비율일 이유는 없으므로 **이 비를 O₂ 값에 곱하지 않았다.** 다만 "CA → CTA 는 오더가 아니라 배수 수준의 차이" 라는 것은 이 한 쌍이 말해 준다. (같은 논문은 O₂ 를 재지 않았다 — §8 참조.)

### 2.2 COC 필름 등급 2종 (신규) — tier 1

`out_cc/cc02_coc_film_o2.json`

| 카드 | 값 mol/(m·s·Pa) | Barrer | 원문 | 조건 |
|---|---|---|---|---|
| TOPAS 6013F-04 (Tg 138 °C) | 1.4459e-16 | 0.432 | 280 cm³·100 µm/(m²·day·bar) | 23 °C, 50 % RH, ASTM D3985 |
| TOPAS 5013F-04 (Tg 136 °C) | 1.2909e-16 | 0.386 | 250 cm³·100 µm/(m²·day·bar) | 23 °C, 50 % RH, ASTM D3985 |

벤더 문서에 그 등급 이름으로 인쇄된 값이라 **tier 1** 이다. 다만 **이것은 COC 이지 COP 가 아니다** — §6 에 적었다.

### 2.3 검증

`ingest_agent_json.py` dry-run 통과 — `ok 5 / new_mat 5`, 단위·범위·조건충돌 위반 0.

---

## 3. 이미 이 카드가 쓰는 출처 3300 · 2015 · 853 을 열어 본 결과

브리프의 핵심 질문이다. 셋 다 열었고(853 은 열지 못했다 — 아래) 결과는 이렇다.

### 출처 3300 — matmake "Properties of Cellulose Acetate (CA)" (database)

- 내려받아 전문을 폈다. `local_path`: `/data/paper_patent_corpus/standards_appnotes/display/cc_src3300_matmake_cellulose_acetate.html`
- **산소 열이 없다.** 이 페이지의 물성 표는 Physical(밀도·흡수율) · Mechanical(인장·굴곡·경도) · Thermal(융점·열전도·비열·CTE) · Electrical(유전율·저항·절연파괴) · Optical(굴절률) · Hazardous(UL94) 뿐이고 **기체투과 항목 자체가 없다.**
- 부가 확인 — 이 페이지는 제목대로 **CA(아세테이트)** 이지 CTA 가 아니고, DS·아세틸 함량도 안 적는다. 참고문헌은 Cardarelli *Materials Handbook*(2018) · CRC Handbook 97th · Oxford Engineering Tables 셋이다.

### 출처 2015 — ACS Omega, "Tailoring Nanocellulose-Cellulose Triacetate Interfaces…" (doi 10.1021/acsomega.8b01616)

- PMC6645492 전문을 내려받아 텍스트로 폈다. `local_path`: `.../cc_src2015_acsomega8b01616_CTA_PEG.html`(+ `.txt`)
- **산소 열이 없다.** 전문에서 `oxygen` 0건 · `permeab` 0건 · `barrer` 0건 · `OTR` 0건 · `diffusion` 0건이다. `solubility` 1건은 참고문헌 제목 안이다.
- 이 논문은 PEG 그래프팅 밀도에 따른 **역학·열** 물성 논문이다(초록이 그렇게 말한다). Table 1·2 도 역학/열이다. **재료는 진짜 CTA 인데 기체 데이터가 없다** — 이번 표적에 대해서는 빈 문이다.

### 출처 853 — Polymer Handbook (Brandrup, Immergut, Grulke) 4th ed. (book)

- **원권을 열지 못했다.** 카탈로그의 이 출처 레코드는 `url`·`doi`·`local_path` 가 전부 비어 있다. `/data/paper_patent_corpus` 전역 검색에서 사본 0건, `books/expert_books/04_materials_science` 에도 없다. archive.org 에는 **3판(1989)·1판(1975)만** 있고 둘 다 대출 제한이라 search-inside API 가 403 이며, 4판은 아예 없다.
- **그런데 브리프의 질문에는 답이 나왔다 — 있다.**
  내가 실제로 연 오픈액세스 논문 **Membranes 2024, 14, 148**(PMC11279174) 의 Table 3 이 셀룰로스막의 H₂O·CO₂·H₂·**O₂**·N₂ 투과도를 Barrer 로 싣고, 그 표의 참고문헌 [72] 가
  `Pauly S. "Permeability and Diffusion Data", The Wiley Database of Polymer Properties, Wiley, 2003, 543–568` 이다.
  Wiley Database of Polymer Properties 는 Polymer Handbook 의 온라인판이고, 장 제목과 쪽 범위(543–568)가 Polymer Handbook 4판 **VI/543–VI/569** 와 일치한다. **즉 853 의 VI 장 기체투과 표에 셀룰로스 아세테이트 행이 있고 그 O₂ 값은 0.780 Barrer 다.**
  다만 **원권을 못 열었으므로 출처는 853 이 아니라 내가 실제로 연 Membranes 2024 로 달았다.** 계보는 notes 에 적어 두었다. 853 을 직접 붙이는 것은 열지 않은 문서를 인용하는 것이다.
- **853 에 대해 남은 것** — 그 표에 **셀룰로스 트리아세테이트 행이 따로 있는지** 는 확인하지 못했다. Membranes 2024 는 표의 일부 행만 재현한다. 4판 VI 장 원권 한 권을 열면 그 한 줄이 이 표적을 통째로 닫을 수 있다.

---

## 4. CA 와 CTA 를 구별할 수 있었나 — 구별은 했다. 넣은 값에 붙일 DS 는 못 얻었다

- **구별은 했다.** 이번에 넣은 세 값이 전부 "cellulose acetate" 로 인쇄된 것이지 "cellulose triacetate" 가 아니라는 사실은 원문 문자열로 확정했다. 그래서 셋 다 tier 3 이고 `grade_scope` 에 그 이유를 적었다.
- **DS/아세틸 함량은 못 얻었다 — 넣은 세 행에 대해서는.** 세 출처 어느 것도 DS·아세틸 함량을 인쇄하지 않는다. 그래서 `conditions` 에 `degree_of_substitution` 이나 `acetyl_content_pct` 를 **넣지 않았다** — 모르는 것을 적지 않았다.
- **DS 를 인쇄하는 산소 문헌은 딱 하나 찾았고, 그 값은 못 쓴다.** *Polymers* 2026, 18(6), 740(PMC13029833)이 `CA, whose acetyl and hydroxyl content was, respectively, 39.8 wt% and 3.5 wt%` 라고 아세틸 함량을 적고, 순수 CA 막의 `permeability of O2 was only increased from 1.00 Barrer to 1.19 Barrer` 로 **O₂ = 1.00 Barrer** 를 인쇄한다(두께 100 µm, ASTM D1434 M 법 / GB/T 1038, Δp 0.1 MPa). 아세틸 39.8 wt% 는 완전치환의 화학양론 상한(트리아세테이트 반복단위 C₁₂H₁₆O₈, 3 × 43.04 / 288.25 = **44.8 wt%**)보다 낮아 트리아세테이트가 아니고, 논문도 스스로 CA 라고 부른다. **그런데 이 값은 넣지 않았다 — §8 의 배제 사유를 보라.**
- **막힌 지점 두 곳.**
  1. DS 별 산소투과의 1차 문헌인 **Puleo, Paul & Kelley (1989) J. Membr. Sci. 47:301–332** — DS 1.75 / 2.45 / 2.84 세 시료의 35 °C, 1 atm 투과계수 표를 갖고 있다. ScienceDirect 유료이고 OpenAlex 기준 OA 사본이 없다. 내가 연 리뷰 넷(RSC Adv 2024 · Membranes 2024 · Polymers 2021 PMC8067227 · Polymers 2021 PMC8625587)이 모두 이 논문을 **결론만** 인용하고 숫자 표는 재현하지 않는다.
  2. **Bras, Vaca-Garcia, Borredon, Glasser (2007) Cellulose 14:367–374, "Oxygen and water vapor permeability of fully substituted long chain cellulose esters"** — HAL 오픈액세스 원문을 실제로 내려받아 열었다(`.../cc_Bras2007_Cellulose_LCCE_O2_WVP.pdf`). Table 1 이 **C. Acetate DS 2.99 ± 0.01** 로 완전치환 아세테이트를 명시하는데, **Table 2 에서 그 행의 O₂ 투과도 칸이 `–` 다.** 산소는 C8·C12·C16·C18 과 셀로판만 쟀다.
     같은 논문 Table 3 의 회귀식 `O₂ = 0.0058 × (아실 몰부피) − 0.5157 (R²=0.93)` 에 아세테이트의 몰부피 81.6 cm³/mol 을 넣으면 **−0.042 로 음수**가 나온다. 즉 이 모델은 아세테이트까지 외삽되지 않는다. **그래서 계산하지 않았다.**

---

## 5. 습도 — 넣을 수 있는 만큼만 넣었고, 습도 곡선은 아직 없다

요청서가 "TAC 은 셀룰로스계라 흡습 영향이 크다" 고 지적한 대로 습도가 조건축이어야 한다. 내가 확보한 것은 이렇다.

| RH | 값 (Barrer) | 시료 |
|---|---|---|
| 0 % | 0.493 | 캐스팅 CA 치밀막 (20 °C) |
| 50 % | 0.122 | CA 배리어 필름 (23 °C) |
| 미기재 | 0.780 | 가소화 CA (25 °C) |

**이 셋은 습도 곡선이 아니다.** 시료가 서로 다르므로 0 % → 50 % 의 4 배 차를 습도 효과로 읽으면 안 된다. 그 경고를 각 행의 notes 에 적었다. 참고로 카탈로그가 이미 가진 재료 75 PMMA 는 **한 논문 한 시료**로 RH 0/50/80 세 점을 갖는다(4.79 → 4.25 → 4.02e-17, 즉 0→50 % 에서 11 % 감소). **CA/CTA 에 대한 그런 단일시료 습도 시리즈는 이번에 못 찾았다.**

---

## 6. 벤더 시트 — TAC 은 0건, COP 도 0건, COC 만 있었다

### TAC (t1 후보) — 전부 빈손

열어 본 것: Goodfellow "Cellulose acetate film" 제품 페이지(기체투과 행 자체가 없다 — 화학저항·전기·물리·역학·열만), Fujifilm FUJITAC(영문·일문 `酸素透過率`·`ガス透過` 로도 검색), Konica Minolta KC4UY/KC8UX, Eastman 셀룰로스 에스터, Daicel, SK microworks.
**공개 문서로 산소 행을 인쇄하는 디스플레이용 TAC 데이터시트를 한 건도 찾지 못했다.** TAC 시트는 광학(헤이즈·Re/Rth·투과율)·치수·투습에 최적화돼 있고 기체 배리어 행을 아예 싣지 않는다.

### COP (요청서 3순위 "COP 전환") — 문서를 열었고, 산소 행이 없었다

- **ZEON ZeonorFilm 개요서** `https://www.zeonsmi.com/uploads/downloads/ZeonorFilm-overview-V2025.08.13.pdf` (ZF14/ZF16 계열) 를 실제로 내려받아 열었다.
  **산소 행이 없다. 그리고 수증기투과 행도 없다** — 흡습률(ASTM D570)은 있지만 투습도가 아니다.
  실제로 실린 항목: 비중 · 흡수율 · 굴절률 · 광투과율 · 헤이즈 · 리타데이션 · 유전율 · 인장강도/신율 · 연필경도 · Tg(140/170 °C) · 선팽창계수 · 등급/두께.
- JSR ARTON · Mitsui APEL 은 산소투과를 인쇄한 공개 시트를 찾지 못했다.
- 카탈로그의 **재료 72 `COP Zeonex`** 는 산소투과 칸이 여전히 비어 있고, **이번 배치는 72 를 건드리지 않았다.**

### COC (대체로 세운 기준점) — TOPAS 가 인쇄한다

`https://topas.com/wp-content/uploads/2023/05/TOPAS-Packaging-Brochure.pdf` (내가 직접 내려받아 pdftotext 로 표를 확인했다) 의 Table 4·5 가 8 등급의 산소투과를 ASTM D3985, 23 °C/50 % RH 로 인쇄한다.

```
9506F-500 170 · 8007F-600 200 · 7010F-600 260 · 6013F-04 280
9903D-10  400 · 8007F-04  200 · 5013F-04  250 · E-140   1200     [cm3·100µm/(m2·day·bar)]
```

이 중 **Tg 가 디스플레이 광학필름 대역에 걸리는 두 등급(6013F-04 Tg 138 °C · 5013F-04 Tg 136 °C)만 카드로 세웠다.** 나머지 여섯은 같은 문서에 있으니 다음 배치가 필요하면 바로 가져가면 된다.

**COC ≠ COP 를 카드 설명·grade_scope 양쪽에 박아 두었다.** COC 는 에틸렌-노보넨 공중합체이고 COP 는 개환중합 후 수소화한 노보넨 단독중합체다. 편광판 전환 검토에 쓰는 것은 보통 COP 쪽이므로, 이 두 카드는 **시클로올레핀 계열의 오더를 세우는 용도**이지 ZeonorFilm 의 대체값이 아니다.

경고 하나 — 유통사 문서 Entec Polymers "TOPAS COC Product Guide"(2021-05-10) 는 5013F-04 250 · 6013F-04 280 · E-140 1200 은 맞게 적지만 **7010F-600 을 260 이 아니라 26 으로 인쇄한다.** 교차검증에 쓰지 마라.

---

## 7. 해석에 바로 넘길 결론 — ④층 가정이 한 자릿수 높다

요청서는 현재 해석이 TAC 을 **"OCA 의 1/10"** 으로 놓았고 근거가 없다고 적었다.

```
OCA        1.1813e-14 mol/(m·s·Pa)  = 35.30 Barrer
OCA/10     1.1813e-15               =  3.53 Barrer   ← 현재 ④층 가정
```

이번에 문서로 확보한 셀룰로스 아세테이트 범위는 **0.122 ~ 0.780 Barrer** 다. 즉 현재 가정은

| 비교 대상 | 현재 가정이 몇 배 높은가 |
|---|---|
| 가소화 CA 0.780 Barrer | **4.5 배** |
| 캐스팅 CA 치밀막 0.493 Barrer | **7.2 배** |
| CA 배리어 필름 0.122 Barrer | **29 배** |

CTA 가 CA 보다 위라는 방향을 감안해도 — 그리고 그 간격이 §2.1 의 실측 한 쌍에서 CO₂ 기준 1.67 배, 즉 오더가 아니라 배수라는 것을 감안해도 — **`OCA/10` 은 한 자릿수 과대로 보인다.** 참고로 같은 계열(시클로올레핀 COC)의 벤더 실측이 0.39~0.43 Barrer 로 이 범위 한가운데에 떨어진다 — 유리상 광학필름이라면 대략 0.1~1 Barrer 대라는 그림이 두 갈래 문헌에서 같이 나온다.

**따라서 ④층의 투과 기여 3.7 % 는 과대 산정일 가능성이 높다.** 요청서 §6 이 예고한 "실측이 오면 기여도 자체가 재배치될 수 있다" 가 이 층에서 먼저 일어난다. 다만 **이번 값들은 CA 기반 tier 3 이므로 이 재배치를 확정 결론으로 쓰지 말고, ④층을 0.1~1 Barrer 범위의 감도해석 대상으로 두는 것이 맞다.**

---

## 8. 못 넣은 것과 이유

| 못 넣은 것 | 이유 | 종류 |
|---|---|---|
| **CTA(진짜 트리아세테이트)의 O₂ 투과값** | 오픈액세스 어디에서도 숫자를 못 찾았다. Europe PMC 전문검색 `"cellulose triacetate" AND "oxygen permeability"` 17건 · `AND "oxygen transmission rate"` 2건을 전수로 열어 봤고, CTA 혼합기질막 논문 8편(PMC9610833·8400081·8539915·8434370·8625587·12389756·8067227·11279174)은 전부 **CO₂/CH₄** 만 잰다. **가장 아까운 한 편** — *Membranes* 2021, 11, 245(PMC8067227)는 `Cellulose triacetate (CTA, degree of substitution ≈ 2.84)` 와 `cellulose diacetate (CDA, degree of substitution ≈ 2.45)` 를 **DS 까지 인쇄하고 순수 막을 각각 재는데**, Table 3 의 열이 `CO2 Permeability (Barrer)` · `CH4 Permeability (Barrer)` · `CO2/CH4 Selectivity` 뿐이고 **산소 열이 없다.** 전문에서 `oxygen` 1건(문맥상 산소원자)·`O 2` 0건 | 문서에 열이 없었다 |
| **순수 CA 막 O₂ = 1.00 Barrer** (*Polymers* 2026, 18, 740, PMC13029833) — 아세틸 39.8 wt% · 두께 100 µm · ASTM D1434(M)/GB/T 1038 · Δp 0.1 MPa 를 다 인쇄하는 **유일한 조건 완비 문헌** | **의도적으로 배제했다.** 같은 문장이 `the selectivity of the CA/PEGDA membrane increased from 1.26 in the pure CA membrane` 이라고 **CO₂/O₂ = 1.26** 을 적는다. 치밀 CA 막의 CO₂/O₂ 는 Polymer Handbook 계보에서 23.07/0.780 = **29.6** 이다. 선택도가 24 배 낮다는 것은 이 막이 치밀 필름이 아니라 기공 흐름(Knudsen 영역, CO₂/O₂ 이론 0.85)에 가깝다는 뜻이고, 논문 본문도 스스로 `the original microporous structure of membrane` 이라고 미세다공 구조를 말한다. **즉 이 1.00 Barrer 는 고분자 용해-확산 투과계수가 아니라 다공막의 겉보기 투과다.** 해석의 `𝒫 = D·S` 자리에 넣으면 물리량이 다르다. 온도도 원문에 없다 | 등급이 안 맞았다(물리량이 다르다) |
| **CA 의 OTR = 650 cm³/(m²·24 h), 23 °C, 0 % RH** (*Catalysts* 2022, 12, 319 Table 5, 그리고 이를 되받는 *Polymers* 2020, 12, 1248 · *RSC Adv.* 2025) | **두께가 어디에도 안 적혀 있다.** OTR 은 정의상 두께 의존량이라 두께 없이는 `𝒫` 로 환산할 수 없고, `physical.gas_transmission_rate_o2` 행으로 넣어도 요청서가 못 쓴다("OTR 로 오면 두께가 있어야 𝒫 로 환산된다"). 게다가 1차 출처가 5편 묶음 인용(Rodríguez 2012 *J. Food Eng.* 110:262 등, 전부 유료)이라 되짚기도 막혔다 | 조건이 모자랐다 |
| Puleo/Paul/Kelley 1989 의 DS 별 O₂ 표 | ScienceDirect 유료 · OA 사본 없음 | 문서를 못 열었다 |
| Nakai 2005 (J. Membr. Sci. 256:72) 원측정 | Elsevier 유료(리뷰 인용으로 대체) | 문서를 못 열었다 |
| Zhou 2022 (Int. J. Biol. Macromol. 209:1450) 원측정 | Elsevier 유료(리뷰 인용으로 대체) | 문서를 못 열었다 |
| "Transparent and high barrier plasma functionalized acrylic coated **cellulose triacetate** films" (Prog. Org. Coat. 2020, doi 10.1016/j.porgcoat.2020.105988) — **맨 CTA 필름의 OTR 대조군을 가졌을 가능성이 가장 높은 논문** | OpenAlex `oa_status: closed`, 저장소 사본 없음 | 문서를 못 열었다 |
| Číhal 2018 (Polym. Test. 65:468) "PBS–cellulose triacetate blends: Permeation…" | 역시 closed | 문서를 못 열었다 |
| Polymer Handbook 4판 VI 장 원권 | 사본 부재(§3) | 문서를 못 열었다 |
| Massey, *Permeability Properties of Plastics and Elastomers* (2003) | archive.org 대출 제한, search-inside 403 | 문서를 못 열었다 |
| TAC 벤더 시트 값 | 공개 시트에 기체 행 자체가 없다(§6) | 문서에 열이 없었다 |
| **PNNL-26070 Table 4.2** (재료 75 PMMA 가 쓰는 출처 1926) | 내려받아 전문 확인 — `cellulos` 0건. 셀룰로스 계열 행이 아예 없다 | 문서에 열이 없었다 |
| RSC Adv. 2024 의 "0.55 → 0.14 Barrer for oxygen" | 문장이 모호하다. 불소처리 시간에 따른 감소인지 기체 크기에 따른 감소인지 원문이 갈라 적지 않았고, 1차 출처 Belov 2021(Membr. Membr. Technol. 3:114)은 유료라 확인 불가. **모호한 문장을 값으로 만들지 않았다** | 등급이 안 맞았다 |
| 재료 88 · 재료 72 의 산소 칸 | 판단대로 88 은 안 건드렸고(§1), 72 는 COP 산소값 자체를 못 찾았다(§6) | 판단 · 부재 |

---

## 9. 다음 배치에 넘길 것

1. **Polymer Handbook 4판 VI 장(Pauly, "Permeability and Diffusion Data", VI/543–VI/569) 원권 조달이 이 표적의 가장 큰 단일 문이다.** 셀룰로스 아세테이트 행이 있다는 것은 §3 에서 확인했다. 남은 것은 **같은 표에 cellulose triacetate 행이 따로 있는지**다. 한 줄이면 이 표적이 tier 2 로 닫힌다. 출처 853 은 이미 카탈로그에 있으니 `local_path` 만 채우면 된다.
2. **Prog. Org. Coat. 2020, 10.1016/j.porgcoat.2020.105988** — 제목이 "cellulose triacetate films" 이고 배리어 논문이라 **맨 CTA 의 OTR 대조군**을 가졌을 확률이 가장 높다. 저자 소속 기관 리포지터리(인도 IIT 계열 추정) · ResearchGate 저자 업로드 · 저자 직접 요청 세 경로가 남아 있다.
3. **Puleo, Paul & Kelley 1989 J. Membr. Sci. 47:301** — DS 1.75/2.45/2.84 × O₂ 표. UT Austin(D.R. Paul 그룹) 학위논문에 같은 표가 재현돼 있을 가능성이 있다. Texas ScholarWorks 를 훑을 값어치가 있다. 이게 열리면 **DS 축이 열리고**, CA→CTA 외삽이 tier 4 추정이 아니라 문서 근거가 된다.
4. **TOPAS Packaging Brochure 의 나머지 6 등급**(9506F-500 · 8007F-600 · 7010F-600 · 9903D-10 · 8007F-04 · E-140). 문서는 이미 `/data/paper_patent_corpus/standards_appnotes/display/cc_TOPAS_Packaging_Brochure.pdf` 에 있고 같은 표에 수증기투과(ISO 15106-3, 38 °C/90 % RH)도 함께 인쇄돼 있다. 카드 6장 + 물성 12행이 한 문서로 닫힌다.
5. **재료 72 `COP Zeonex` 의 `core_absent_from_vendor_sheet` 표기.** ZeonorFilm 개요서를 열었더니 산소 행이 없다는 사실(§6)은 이번 배치 산출물 형식(물성 JSON)으로는 DB 에 못 넣는다. 재료 속성 갱신 배치가 그 문장을 88 의 `optical.emissivity_total` 사례와 같은 형식으로 넣어 주면, 다음 배치가 같은 문을 두 번 두드리지 않는다.
6. **재료 88 의 적층 전체 산소투과는 여전히 공백이고, 그것이 맞다.** 만약 해석이 언젠가 편광판을 한 덩어리로 다뤄야 하면 TAC 단층 + PVA 단층 + 계면으로 조립해야 하고, **PVA 의 산소투과(습도 의존이 극심하다)** 가 그때 새 표적이 된다.

---

## 부록 — 이번에 열어서 코퍼스에 남긴 문서

전부 `/data/paper_patent_corpus/standards_appnotes/display/` 아래다.

| 파일 | 무엇 |
|---|---|
| `cc_Membranes2024_14_148_cellulose_membranes_PMC11279174.xml` | Table 3 = Pauly/Polymer Handbook 계보의 CA O₂ 0.780 Barrer |
| `cc_Paunonen2013_BioResources_cellulose_derivative_films_review.pdf` | 캐스팅 CA 치밀막 3.7e-12 cm³·m/(m²·s·Pa), 20 °C, 0 % RH |
| `cc_ChemRev2025_lignocellulosic_films_PMC12746420.xml` | Table 3 CA films OP 7,997 cm³·µm/(m²·day·atm), 23 °C, 50 % RH |
| `cc_TOPAS_Packaging_Brochure.pdf` | COC 8 등급 O₂, ASTM D3985, 23 °C/50 % RH |
| `cc_Bras2007_Cellulose_LCCE_O2_WVP.pdf` | DS 2.99 아세테이트의 O₂ 칸이 `–` 라는 **음성 증거** |
| `cc_Polymers2021_CTA_CDA_blend_DS_PMC8067227.xml` | 순수 CTA(DS 2.84) vs CDA(DS 2.45) CO₂ 1.67 배 — DS 방향의 유일한 실측. **산소 열은 없다** |
| `cc_Polymers2026_18_740_CA_PEGDA_PMC13029833.xml` | 아세틸 39.8 wt% CA 막 O₂ 1.00 Barrer — CO₂/O₂ 1.26 이라 다공막. **배제한 값의 근거 문서** |
| `cc_src3300_matmake_cellulose_acetate.html` | 출처 3300 — 기체 행 없음 (음성) |
| `cc_src2015_acsomega8b01616_CTA_PEG.html` | 출처 2015 — 기체 행 없음 (음성) |
| `cc_RSCAdv2024_CA_membranes_gas_sep_PMC11184368.xml` | CA 막 리뷰 — O₂ 문장이 모호해 값으로 안 씀 (음성) |
| `cc_ACSOmega2021_cellulose_esters_sidechain_PMC8482480.xml` | CTA 포함 셀룰로스 에스터 배리어 논문 — WVTR 만, 산소 없음 (음성) |
| `PNNL-26070.pdf` | 출처 1926 Table 4.2 — 셀룰로스 행 없음 (음성) |
