<!-- 67차 CA 수집 배치 보고서 — 엣지 실링재 산소 물성 -->

# 67차 CA — 엣지 실링재 (요청서 1순위)

기준일 2026-09-08 · 대상 `PDE/oxygen-diffusion/물성요청_산소확산_원자재6종.md` §4 1순위
산출 `backend/scripts/catalog/out_ca/`

**한 줄 요약** — 실링재의 정체는 특허 9건으로 확정했다(에폭시가 아니라 **에폭시 아크릴레이트**다).
실링 폭도 문서로 확보했다. 그런데 **에폭시 산소투과 문헌 자체가 123 배로 갈라져 있다**.
`h` 는 이 밴드 안에 들어오므로 물리적으로 닫히는 것이 맞지만, **밴드를 좁히려면 실링재를 직접 재야 한다.**

---

## 1. 실링재의 정체 — 어디까지 확정했는가

요청서는 "미확인 (에폭시계 추정)" 이라고만 적혀 있었다. **이 추정은 절반만 맞다.**

### 1.1 확정 — LCD ODF 메인 실은 "에폭시"가 아니라 "에폭시 아크릴레이트"다

**주수지는 부분 (메타)아크릴화 비스페놀A/F 에폭시(= 에폭시 (메타)아크릴레이트)가 50~80 wt%,
미변성 에폭시수지는 15~20 wt% 에 불과하다.** 경화는 UV 라디칼 + 잠재 열경화의 병용이다.

서로 무관한 **특허 9건이 수렴**한다. 출원인은 다음과 같다 (Sharp · Hitachi Displays · Mitsui · Sekisui ·
Nippon Kayaku · Kumho · ITRI · BOE · CSOT).

업계 상태를 못박은 문장 — **US 8,193,258 B2** (ITRI) 배경.

> "Currently, sealant materials used for the ODF process are mainly crystallized acrylic modified epoxy resin."

같은 특허가 이 실의 역할도 명시한다. **우리 해석의 전제와 정확히 일치한다.**

> "The sealant in the ODF process is used to bond the two glass substrates, and also prevent the liquid
> crystals from pollution, avoid liquid crystal leakage, and **avoid water vapor and oxygen from permeating
> into the LCD panels**."

**전문 배합 실례 2건 (원문 verbatim)**

**Sharp US 10,739,647 B2**

> "the sealant contains an acrylic resin (epoxy-modified) (EBECRYL3700 available from Daicel-Allnex Ltd.,
> **about 50 wt %**), an epoxy resin (Epikote 806 available from Japan Epoxy Resins Co. Ltd., **about 20 wt %**),
> a hydrazide-based curing agent (dihydrazide adipate available from Otsuka Chemical Co., Ltd., **about 10 wt %**),
> an acrylic-epoxy resin, a silane coupling agent (KBM-403 available from Shin-Etsu Chemical Co., Ltd.,
> **about 0.2 wt %**), an organic filler, and an inorganic filler (ADMAFINE SO-C2 available from Admatechs
> Company Limited) (the total amount of the organic filler and the inorganic filler is **about 10 wt %**)."

**Hitachi Displays US 7,746,428 B2**

> "**80 parts by weight of epoxy acrylate of a bisphenol F epoxy resin**, 20 parts by weight of RE203
> (made by NIPPON KAYAKU Co., Ltd.; epoxy equivalent weight 233 g/eq, ethylene oxide added bisphenol S epoxy
> resin) as an epoxy resin, 1.2 parts by weight of [카바졸계 라디칼 광개시제] … 10 parts by weight of
> isophtalic acid dihydrazido … **13 parts by weight of alumina** … 3.9 parts by weight of rubber
> (paraloid EXL-2655)"

**BOE US 10,138,399 B2** (청구항)

> "the sealant composition comprises: **70-80 wt % of a low-viscosity epoxy acrylate** conforming to the
> structure of Formula I, 0.5-1 wt % of a photoinitiator, 5-15 wt % of silica microspheres, 5-15 wt % of
> resinous elastic microspheres, and 1-2 wt % of silane coupling agent"

**ITRI US 8,193,258 B2** 청구항 1~21 (전문 열람) — 올리고머는 "an unsaturated mono-carboxylic acid modified
bisphenol A epoxy resin and an unsaturated mono-carboxylic acid modified bisphenol F epoxy resin" 100부 기준,
에폭시수지 20~60부, 광개시제 2~10부, 이미다졸/이미다졸린계 열경화제 1~10부, 아크릴 모노머 5~30부,
충전재(SiO2·talc·Al2O3·clay) 10~50부, 실란커플링제 2~10부.
A:F 당량비 0.05:0.95~0.3:0.7, 불포화산:(A+F) 당량비 1.1:1.

**Nippon Kayaku US 7,824,746 B2** — 충전재 함량과 경화 노선을 함께 인쇄한다.

> "Content of the inorganic filler … is generally **5 to 40% by weight, preferably 15 to 25% by weight**."
> "The heat-curing method and the photocuring method have such various problems, and actually **the combined
> photo- and heat-curing method is believed to be the most practical method**."

### 1.2 확정 — 벤더 제품이 이 용도로 지목된다

**Sharp US 11,168,254 B2** 가 제품명을 직접 적는다. 우리 `ca02` 카드의 근거다.

> "The sealing member 40 may contain an epoxy resin or a (meth)acryl resin … As the sealing member 40,
> for example, **Photolec available from Sekisui Chemical Co., Ltd.** may be used."

그 Photolec S 의 벤더 물성표 (전량 열람).

```
Curing conditions              UV+Heat 3000mJ/cm2+120℃60min
Viscosity (25℃, 1rpm) MPa·s    Standard 280,000 / Soft 230,000
Ti (1rpm/10rpm)                Standard 1.15 / Soft 1.37
W V T R (60℃90%RH) g/m²        Standard 34 / Soft 71
Shear bond strength Glass/Glass N/25 mm²   >500 / >500
Tg (DMA) ℃                     Standard 95 / Soft 45
```

ITRI 특허의 "UV 후 120 °C 열경화" 가 상용품에서 그대로 확인된다.
**다만 세키스이는 수지 계열을 공개하지 않는다** — 페이지에 에폭시·아크릴레이트라는 단어가 없다.

### 1.3 확정 — OLED 는 LCD 와 경화화학이 다르다 (같은 재료가 아니다)

**우리 해석 대상은 OLED 다.** 그래서 이 구분이 중요하다.
**Mitsui US 7,495,035 B2** 가 이유를 인쇄한다.

> "The organic EL element … has low heat resistance, and its heat-resistant temperature is said to be in the
> range of **about 80 to 120 °C**. Therefore, in the sealing of the organic EL display, there is a problem that
> **a thermosetting epoxy resin cannot be completely cured by heating**."

그래서 OLED 는 **UV 양이온 경화 에폭시/옥세탄** 으로 간다. 반대로 그 양이온 경화는 LCD 에서 실격이다 —
**Nippon Kayaku US 7,824,746 B2**.

> "Since a liquid crystal sealing material of cationic polymerization type generates ions in photocuring,
> when it is used in the liquid crystal dropping process, it has such a problem that the ion components
> elute in the liquid crystal and the specific resistance value of the liquid crystal is reduced."

**두 용도가 정반대 제약에 밀려 정반대 경화화학으로 갈렸다.** OLED 쪽의 나머지 갈래는

- **dam-and-fill** — CSOT US 10,818,870 B2 "the dam adhesive is an UV-curable adhesive; and the fill adhesive
  is a thermally curable adhesive"; BOE US 10,622,584 B2 청구항 "wherein the dam and the filler comprise
  **epoxy resin** or hexamethyldisiloxane"
- **유리 프릿** — Samsung SDI US 7,545,094 B2 (수지가 아님)

**어느 갈래든 주쇄는 에폭시다.** 이 카드에 에폭시 계열 산소값을 붙인 근거가 그것이다.

### 1.4 확정하지 못한 것

- **이 패널이 쓰는 제품명과 실제 배합비.** 사내 BOM 없이는 공개문서로 좁혀지지 않는다.
- **편광판/OCA 라미네이트 측면을 덮는 모듈 레벨 사이드실링재.** 요청서 적층은
  `Glass / OCA / TAC / PSA / 유기평탄화막 / G CF / TFE CVD` 이고 산소가 들어오는 곳은
  **이 라미네이트의 노출된 측면**이다. 이것이 셀 프레임 실과 같은 재료인지 별도 수지인지
  **문서를 하나도 열지 못했다.** 증거 없음이지 부재 아님이다.
- **충전재가 용융실리카인지 알루미나인지** — 공급사마다 갈리고 특허에 둘 다 나온다.

**그래서 카드 이름이 배합비를 주장하지 않는다.**
`Display panel edge/frame sealant, epoxy-backbone perimeter seal (LCD ODF: dual UV+thermal epoxy acrylate,
silica/alumina filled; OLED: UV-cationic epoxy or dam-and-fill epoxy) — composition class, panel grade not identified`

---

## 2. 넣은 값 — 총 11건 · 재료 카드 3장 신규

### 2.1 `ca01_edge_sealant_o2.json` — 실링재 계열 카드 1장, 값 9건 (전량 tier 3)

**출처 A — Polymers 2021, 13, 1517 (doi 10.3390/polym13091517) Table 3.** 표 전량을 원문대로 읽었다.

```
Material          Test Temp.  Tg    l      P × 10^16      D × 10^13   S × 10^5    Ref.
                  (°C)        (°C)  (µm)   (mol/m−s−Pa)   (m2/s)      (mol/m3−Pa)
DGEBA/PGE/DDM     30          117   20     -              1.60        20.9        [109]
DGEBA/DDM         30          164   20     -              2.40        18.0        [109]
                  40          164   20     -              2.80        30.3        [109]
Epon828/A2049     25          150   ~150   0.47           4.97        9.44        [110]
                  40          150   ~150   0.80           10.1        7.63        [110]
                  65          150   ~150   1.70           32.8        5.19        [110]
                  80          150   ~150   2.57           52.2        4.82        [110]
```

**출처 B — Polymers 2025, 17, 1684 (doi 10.3390/polym17121684) Table 1 / §3.8.**

```
Epoxy | DGEBA 71.4 wt% | T-403 28.6 wt% | ... | 150 ± 3 µm | ... | 12.299   ← 열 머리글 'Oxygen Permeability (barrer)'
```

| # | key | 값 | 조건 | method | tier | 왜 이 등급인가 |
|---|---|---|---|---|---|---|
| 1 | gas_permeability_o2 | 4.7e-17 | 25 °C, dry | measured | 3 | P 가 **인쇄된** 값. (a) 리뷰의 2차 인용 (b) 실링재가 아닌 무충전 DGEBA 값을 빌린 계열값 |
| 2 | gas_permeability_o2 | 8.0e-17 | 40 °C, dry | measured | 3 | 위와 같음. 신뢰성 온도대용 |
| 3 | gas_permeability_o2 | 4.32e-17 | 30 °C, dry | **computed** | 3 | P 열이 `-` 라 **원문이 인쇄한 D 와 S 를 곱했다.** 우리 곱셈이므로 computed |
| 4 | gas_permeability_o2 | 3.344e-17 | 30 °C, dry | **computed** | 3 | 위와 같음 (PGE 희석 조성) |
| 5 | diffusion_coefficient | 2.40e-13 | 30 °C, dry | measured | 3 | 인쇄값. 계열값이라 3 |
| 6 | gas_solubility | 1.80e-4 | 30 °C, dry | measured | 3 | 인쇄값. 계열값이라 3 |
| 7 | diffusion_coefficient | 1.60e-13 | 30 °C, dry | measured | 3 | 인쇄값. 계열값이라 3 |
| 8 | gas_solubility | 2.09e-4 | 30 °C, dry | measured | 3 | 인쇄값. 계열값이라 3 |
| 9 | gas_permeability_o2 | **4.1157e-15** | 온도 미인쇄 | measured | 3 | 자립막 기상투과 실측. 계열값 + 부차측정 + **온도 미인쇄**. §3.1 의 충돌 당사자 |

**tier 4 는 하나도 만들지 않았다.** 추정으로 채운 칸이 없다.

**환산 검산 (Barrer 되돌리기, DB 관례 1 Barrer = 3.3464e-16 mol/(m·s·Pa))**

```
3.344e-17 / 3.3464e-16 = 0.0999 Barrer   DGEBA/PGE/DDM 30 °C  (= 1.60e-13 × 20.9e-5)
4.32e-17  / 3.3464e-16 = 0.129  Barrer   DGEBA/DDM     30 °C  (= 2.40e-13 × 18.0e-5)
4.7e-17   / 3.3464e-16 = 0.140  Barrer   Epon828/A2049 25 °C
8.0e-17   / 3.3464e-16 = 0.239  Barrer   Epon828/A2049 40 °C
4.1157e-15/ 3.3464e-16 = 12.299 Barrer   DGEBA/T-403   (출처 B, 원문이 Barrer 로 직접 인쇄)
```

출처 A 의 넷은 자기검산(P = D×S)이 인쇄된 P 와 0.2~3.7% 로 맞아 열 배치가 확인된다.

### 2.2 `ca02_photolec_s_vendor.json` — 벤더 제품 카드 2장, 값 2건 (tier 1)

| 재료 | key | 값 | tier | 근거 |
|---|---|---|---|---|
| Sekisui Photolec S (Standard) | thermal.glass_transition | 368.15 K (= 95 °C) | **1** | 그 제품 벤더 물성표의 DMA Tg |
| Sekisui Photolec S (Soft) | thermal.glass_transition | 318.15 K (= 45 °C) | **1** | 같은 표 Soft 열 |

**왜 Tg 를 넣었는가.** 요청서 §10.2 가 "재료명이 아니라 **Tg 대비 사용온도**가 O2 확산의 지배 인자다"
라고 못박았다. 그리고 §1.2 에서 보듯 Sharp 특허가 **이 제품을 프레임 실로 지목한다.**
**표준 그레이드는 25~60 °C 전 구간에서 유리상**, **소프트 그레이드는 45 °C 를 넘으면 고무상**이다 —
60 °C 신뢰성 시험에서 두 그레이드의 산소 거동이 갈릴 수 있다. 그 갈림은 **값으로 넣지 않았다.** 재지 않았다.

---

## 3. 못 넣은 것 — 네 가지를 구분해서

### 3.1 문서를 열었고 값도 있는데 **두 출처가 123 배 어긋난 것** ← 이번 배치 최대 발견

동료심사 저널 두 편이 **같은 계열(무충전 DGEBA/아민 에폭시 자립막)** 에 대해 두 자릿수 다른 값을 인쇄한다.

| 출처 | 시료 | 두께 | 값 | 측정 |
|---|---|---|---|---|
| Polymers 2021, 13, 1517 T3 | Epon828/A2049, DGEBA/DDM, DGEBA/PGE/DDM | 20 · 150 µm | **0.100 ~ 0.239 Barrer** | 기상투과 (dry), 2차 인용 |
| Polymers 2025, 17, 1684 §3.8 | DGEBA + T-403 | 150 µm | **12.299 Barrer** | GTR10-GPA 자립막 기상투과 |

**둘 다 등록했다.** 어느 한쪽을 조용히 버리는 것이 오히려 부정직하기 때문이다.
notes 에 **"상한/하한 밴드로 쓰고 평균 내지 마라"** 고 적었다.

읽을 때 걸리기 쉬운 함정 하나 — Polymers 2025 의 Table 1 캡션은 "…immersed in 3.5 wt% of NaCl aqueous
solution containing 2 wt% of ACQ" 로 끝난다. **그 침지 조건은 임피던스·Cu²⁺ 열에만 걸린다.**
투과도 열은 별도 자립막 측정이다 — 원문 §3.8 "(GPA) measurements were conducted on **free-standing films**
of neat epoxy". 캡션만 보고 "젖은 상태 값" 으로 오독하면 안 된다.

**어느 쪽이 옳은가 — 가르지 못했다.** 판단 재료만 남긴다.

- 12.3 Barrer 는 폴리카보네이트(약 1.4 Barrer)보다 높고 폴리에틸렌 수준이다. **유리상 가교 에폭시로는 통념 밖**이다.
- 다만 T-403 은 유연한 폴리에테르 삼관능 아민(Mw 440)이라 DDM·A2049 같은 강직한 아민보다 자유부피가 크고
  Tg 가 낮다. 투과도가 높은 **방향은 맞다**. 그러나 **88 배는 경화제 차이로 설명되지 않는다.**
- Polymers 2025 는 **시험 온도와 습도를 인쇄하지 않았다.** conditions 에 넣지 못했고 그 자체가 감점 요인이다.

### 3.2 문서를 열었고 그 열이 **있었는데** 검산에 걸려 **버린** 것

**ACS Omega 2025, doi 10.1021/acsomega.5c00860** (PMC12096231)
"Improved Mechanical and Physical Properties of Epoxy Acrylate Oligomers … for the Effective Encapsulation
of the Triple-Cation Perovskite Solar Cells".

**에폭시 아크릴레이트(= 실링재의 주수지 계열)를 UV 경화해 OTR 을 실제로 잰 유일한 오픈액세스 문헌**이라
가장 기대했던 출처다. 본문·SI 전량을 열었다. 측정조건도 인쇄되어 있다.

```
"OTR was measured using the MOCON Ox-TRAN 2/21 oxygen permeability analyzer (ASTM D3985-05)."
"The film thickness applied was 100 μm."

Table S1. OTR and WVTR values of AdAc-MOs based polymers.
   Sample   OTR         WVTR
            g/m2.day    g/m2.day
   %0.00    9.31        5.47      ← 미변성 에폭시 아크릴레이트
   %1.71    7.46        5.10
```

**넣지 않았다. 이유 세 겹.**

1. **어느 열이 산소인지 원문이 스스로 어긋난다.** 초록과 결과 본문은 "WVTR of 7.46 … and an OTR of 5.10" ·
   "OTR and WVTR values of 5.10 cm3/m2 day and 7.46 gr/m2 day" 로 **7.46 을 WVTR** 에 놓는다.
   SI Table S1 은 같은 %1.71 행에서 **7.46 을 OTR** 열에 놓는다. 정확히 뒤집혀 있다.
2. **단위가 세 군데에서 다르다.** SI 표 `g/m2.day`, 본문 `cm3/m2 day`, 실험절 `g/m2 s`.
3. **검산이 깨진다.** 어느 배정을 택하든 두께 100 µm · Δp 1 atm 으로 되돌리면

   | 재료 | 𝒫 [mol/(m·s·Pa)] | Barrer | 출처 |
   |---|---|---|---|
   | ACS Omega 미변성 에폭시 아크릴레이트 (OTR 환산) | 2.79e-18 ~ 4.74e-18 | **0.0083 ~ 0.0142** | 이번 환산 |
   | PET (Prism Sheet / BEF), 카탈로그 재료 | 9.683e-18 | 0.0289 | DB t3 |
   | PMMA Optical (Acrylic), 카탈로그 재료 | 2.956e-17 ~ 4.79e-17 | 0.088 ~ 0.143 | DB t3 |
   | 이번 배치 등록 에폭시 밴드 | 3.344e-17 ~ 4.116e-15 | 0.100 ~ 12.299 | DB t3 |

   즉 **무충전 UV 경화 유기 코팅이 PET 보다 2~3.5 배 더 좋은 산소배리어**라는 결론이 나온다.
   **물리적으로 성립하지 않는다.** 자립막 100 µm 가 아니라 배리어 기판 위 코팅을 잰 것으로 보이나
   원문이 밝히지 않는다.

> §3.1 과 §3.2 의 차이가 판단 기준이다. §3.1 은 **두 문서가 서로** 어긋난 것이라 둘 다 남겼고,
> §3.2 는 **한 문서가 자기 자신과** 어긋나고 결과가 물리적으로 불가능해 버렸다.
> 원문은 다음 배치가 다시 판단할 수 있게 내려받아 두었다.

### 3.3 문서를 열었는데 그 열이 **없었던** 것

| 문서 | 열었나 | 산소 열이 있었나 |
|---|---|---|
| Sekisui Photolec S 제품 물성표 | ○ 전량 | ✗ **없다.** WVTR 만 있고 산소는 인쇄하지 않는다 |
| US 8,193,258 B2 (ITRI) 청구항 1~21 | ○ 전량 | ✗ **없다.** 조성·경화조건만 |
| 프레임 실 특허 9건 (Sharp · Hitachi · Mitsui · Nippon Kayaku · Kumho · BOE · CSOT 등) | ○ | ✗ **한 건도 경화물의 산소투과도를 인쇄하지 않는다.** 인쇄하는 것은 조성·점도·Tg·투습·접착력·비저항이다 |
| `sekisuichemical-hppc.com/en/technology/epoxy/` · `kyoritsu-chem.com/en/products/wr/` | ○ | ✗ 화학·그레이드·경화 데이터 자체가 없다 |

**Photolec S 의 WVTR 은 넣지 않았다.** 인쇄 단위가 `g/m²` (60 °C 90%RH) 로 **시간 기준이 없고 두께도 없다.**
투과 물성으로 성립하지 않는 표기다. 34 · 71 이라는 숫자는 이 보고서에만 남긴다.

> **이것이 이번 배치의 구조적 결론이다** — 실링재 벤더도 실링재 특허도 **산소를 재지 않는다.**
> 그들의 관심사는 액정 오염·비저항·투습이지 산소가 아니다. 요청서가 실링재의 𝒫 를 원한다면
> **문헌으로는 계열값까지가 한계이고, 그 이상은 직접 측정밖에 없다.**

### 3.4 문서를 **못 연** 것 (부재의 근거가 아니다)

| 문서 | 왜 못 열었나 |
|---|---|
| **Damian, Espuche, Escoubes**, Polym. Degrad. Stab. 2001;72:447-458, doi 10.1016/S0141-3910(01)00045-3 | Table 3 `[109]` 의 1차 출처. OpenAlex 조회 `oa_status: closed`, 어떤 리포지터리에도 전문 없음 |
| **Celina & Quintana**, Polymer 2018;150:326-342, doi 10.1016/j.polymer.2018.06.047 | Table 3 `[110]` 의 1차 출처. OpenAlex 는 green OA / OSTI 1702459 라는데 `servlets/purl/1702459` 가 **HTTP 404 에 HTML** 을 돌려준다. 52차 배치와 같은 실패 |
| **CN 105940767 A** · **CN 109076660 A** (Sekisui, organic EL 실런트) | Google Patents 봇 차단 후 HTTP 503. **내용에 대해 아무 주장도 하지 않는다** |
| **WO 2005/085943 A1** | Espacenet description HTTP 403, Patentscope 는 셸 페이지만 |
| Justia `20150160485` | HTTP 403 (동일 문서를 Google Patents 로 우회 확보) |

**1차 출처를 못 연 결과로 남은 미해결 이상 신호 2건.**

1. Table 3 에서 DGEBA/PGE/DDM (Tg 117 °C, 가교밀도 낮음) 의 D = 1.60e-13 이
   DGEBA/DDM (Tg 164 °C, 가교밀도 높음) 의 D = 2.40e-13 **보다 작다.** 유리상에서 Tg 가 47 K 내려가면
   보통 D 는 **오른다.** 방향이 반대다. → 두 D 를 단독 확산 입력으로 쓰지 말고 짝인 S 와 함께 P 로만 쓰라고
   notes 에 적었다.
2. **DGEBA/DDM 40 °C 줄은 아예 등록하지 않았다.** S 가 30 °C 18.0 → 40 °C 30.3 으로 **온도와 함께 올라가는데**,
   같은 표 Epon828/A2049 계열은 9.44 → 7.63 → 5.19 → 4.82 로 내려간다. 물리흡착의 발열 부호와도 어긋난다.
   인쇄값 자체가 의심스러워 보류했다.

### 3.5 검색은 했으나 문헌 자체를 찾지 못한 것

Europe PMC 전문검색 오픈액세스로
`("frame seal" OR "edge seal" OR "sealant") AND ("oxygen permeability" OR "oxygen transmission")
AND (display OR OLED OR "liquid crystal")` 30건을 훑었으나
**디스플레이 실을 통과하는 산소를 실제로 잰 논문은 없었다.** 식품포장·콘택트렌즈·페로브스카이트가 대부분이다.

> **이것은 부재의 근거가 아니다.** 오픈액세스 밖(Elsevier/Wiley 유료, 일본어 사내지, 벤더 비공개 TDS)에
> 있을 수 있다. 특히 **일본·중국 특허의 실시예 표**는 이번에 열지 못한 것이 남아 있다 (§3.4).

---

## 4. 실링 폭·두께 — 문서로 확보했다 (형상이므로 DB 에 넣지 않았다)

요청서가 `h ≈ 𝒫_seal / (𝒮 · t_seal)` 을 위해 실링 폭과 두께를 같이 요구했다.
**물성이 아니라 형상이므로 카탈로그 값으로 넣지 않았다.** 본 절에만 적는다.

### 4.1 실링 폭 (확산 경로장 𝒮) — 원문 verbatim

| 출처 | 인쇄된 값 |
|---|---|
| **Hitachi Displays US 7,746,428 B2** | "a width W of the frame-like ultraviolet-curing sealing material 120 … is **usually approximately 1 mm**" |
| **Sharp US 11,168,254 B2** | "The sealing member 40 may have a width in a plan view of **0.4 mm or more and 5 mm or less**. A more preferred lower limit … is 0.6 mm, and a more preferred upper limit is 4 mm, and a further preferred upper limit is 2 mm." |
| **Mitsui US 7,903,230 B2** | "in a range of 0.5 to 5 mm, preferably 0.5 to 2 mm, **more preferably 0.7 to 1.2 mm** of the resulting sealing width after the cell fabrication" |
| **Sharp US 10,739,647 B2** | "a narrow-frame liquid crystal display having a sealing member width … of **0.6 mm or less**" / "The UV sealant 1 was applied … to obtain a sealing member width of 0.6 mm." |
| **CSOT US 11,740,513 B2** | "the sealant must have a certain width **about 1300 μm**" / "width of a sealant must be narrower (**even less than 300 μm**)" |
| **Sekisui JP 2007-003911 A** (실시예) | "押しつぶされたシール剤の線幅は**約１．２ｍｍ**" (압착된 실런트의 선폭 약 1.2 mm) |

**정리 — 통상 0.6 ~ 1.3 mm, 협베젤 극단 0.3 mm, 청구 범위 상한 5 mm.**

### 4.2 실링 두께 (LCD 셀갭)

| 출처 | 인쇄된 값 |
|---|---|
| **Mitsui US 6,555,187 B1** | "a prescribed cell gap thickness of **5±0.1 μm**" / "a glass short fiber spacer of 5 μm" |
| **Mitsui + Sharp US 7,566,377 B2** | "the cell gap maintained at **5 μm**" |
| **Nippon Kayaku US 7,678,433 B2** | "As a spacer, 1 g of **glass fiber (5 μm)** was added to 100 g of the obtained sealant" |

### 4.3 참고 — OLED 쪽 형상 (다른 구조라 그대로 쓰면 안 된다)

- **Samsung SDI US 7,545,094 B2** (유리 프릿 실) — "The width varies among embodiments and ranges from
  **about 300 μm to about 3000 μm**, optionally from about 500 μm to about 1500 μm."
- **BOE US 10,050,228 B2** (TFE dam) — "the dam has a thickness of about **2~5 μm**, and a width of about
  **50~500 μm**" — 단 이 dam 은 무기물(Al2O3, SiNx 등)이지 접착제가 아니다.

---

## 5. 이 값들로 `h` 를 계산하면 — 닫히기는 하는데 밴드가 123 배다

### 5.1 먼저 — 요청서의 `h` 식은 단위가 맞지 않는다

```
요청서:  h ≈ 𝒫_seal / (𝒮 · t_seal)          𝒮 = 실링 폭, t_seal = 두께
차원:    [mol/(m·s·Pa)] / ([m]·[m]) = mol/(m³·s·Pa)      ✗  h 는 [m/s] 여야 한다
```

Robin 조건 `-D ∂C/∂n = h (C − C_edge)` 에서 좌변이 mol/(m²·s), C 가 mol/m³ 이므로 **h 는 반드시 m/s** 다.
실(seal)을 정상상태 저항으로 놓고 다시 세우면

```
J = 𝒫_seal (p_out − p_in) / 𝒮          [mol/(m²·s)]
C = S_layer · p                        (경계에 닿은 층의 헨리 용해도)
⇒  h = 𝒫_seal / (𝒮 · S_layer)

차원: [mol/(m·s·Pa)] / ([m]·[mol/(m³·Pa)]) = m²/s / m = m/s      ✓
```

**나누는 것은 실링재 두께가 아니라 경계에 닿은 층의 산소 용해도다.**
요청서의 `t_seal` 자리에 용해도가 들어가야 한다. 해석 측 확인이 필요하다.

### 5.2 계산 — 슬라이드 역산값은 밴드 안에 들어온다

`S_layer` 는 요청서 §10.4 의 `S ≈ 1e-4 mol/(m³·Pa)` 를 썼다
(**가정이다 — 아크릴계 S 실측은 여전히 카탈로그에 0 건이다**).
𝒫 는 §2.1 의 등록 밴드 0.0999 ~ 12.299 Barrer 를 썼다.

| 실링 폭 𝒮 (출처) | h 하한 (0.0999 Barrer) | h 상한 (12.299 Barrer) |
|---|---|---|
| 0.3 mm (CSOT 협베젤 극단) | 1.11e-09 m/s | 1.37e-07 m/s |
| 0.6 mm (Sharp 협베젤) | 5.57e-10 m/s | 6.86e-08 m/s |
| **1.0 mm (Hitachi 통상)** | **3.34e-10 m/s** | **4.12e-08 m/s** |
| 1.2 mm (Sekisui 실시예) | 2.79e-10 m/s | 3.43e-08 m/s |
| 2.0 mm (Sharp 상한) | 1.67e-10 m/s | 2.06e-08 m/s |

**슬라이드의 역산값 `h_edge = 1.0 × 10⁻⁸ m/s` 는 문서로 확인된 모든 실링 폭에서 이 밴드 안에 들어온다.**

거꾸로, `h = 1.0e-8` 이 성립하려면 필요한 𝒫 는

```
𝒮 = 0.3 mm  →  0.896 Barrer
𝒮 = 0.6 mm  →  1.793 Barrer
𝒮 = 1.0 mm  →  2.988 Barrer
𝒮 = 1.2 mm  →  3.586 Barrer
𝒮 = 2.0 mm  →  5.977 Barrer
```

전부 **0.10 ~ 12.3 Barrer 밴드 안**이다.

### 5.3 그래서 무엇이 남는가

> **요청서의 전제는 옳다** — `h` 는 실링재의 투과도이고, 역산값은 물리적으로 말이 된다.
> 패널 시험 없이 실링재만 재면 닫힌다는 판단도 맞다.
>
> **그러나 문헌만으로는 닫히지 않는다.** 지금 `h` 의 불확실도를 지배하는 것은
> **형상(폭 0.3~2 mm, 6.7 배)이 아니라 에폭시 산소투과 문헌 자체의 123 배 산포**다.
> 두 동료심사 출처가 두 자릿수 어긋나 있고 (§3.1), 어느 쪽이 옳은지 이번 배치는 가르지 못했다.
>
> **결론 — 실링재 실측 1회가 `h` 를 123 배에서 한 자릿수 안으로 줄인다.**
> 시험 항목은 ASTM D3985 (등압법, MOCON) 로 경화된 실링재 자립막의 OTR,
> **시편 두께·온도·습도를 반드시 함께** 받으면 된다. 그것이 이 배치가 문헌으로 도달한 한계선이다.

**이 계산은 DB 에 넣지 않았다.** 𝒮 는 형상, `S_layer` 는 가정, 결과는 역산이다.
카탈로그 원칙상 역산값은 저장하지 않는다. 해석 측 감도해석 입력으로만 써라.

---

## 6. 다음 배치에 넘길 것

| 순위 | 할 일 | 왜 |
|---|---|---|
| 🔴 1 | **에폭시 산소투과 123 배 충돌 해소** (§3.1) | 지금 `h` 불확실도의 지배 인자다. Polymers 2025 저자에게 시험 온도·습도 문의, 또는 제3의 독립 측정 문헌 확보 |
| 🔴 2 | **일본·중국 특허 실시예 표 훑기** — 특히 이번에 못 연 **CN 105940767 A · CN 109076660 A** (Sekisui organic EL 실런트), WO 2005/085943 A1 | 프레임 실 특허 9건이 산소를 안 찍었지만(§3.3) OLED 전용 실런트 특허는 아직 안 봤다 |
| 🔴 3 | **모듈 레벨 사이드실링재** (§1.4) | 우리 적층에서 산소가 실제로 들어오는 면이다. 문서를 **하나도 열지 못했다** |
| 🟡 4 | **Celina & Quintana 2018 전문 확보** | Table 3 의 1차 출처. OSTI purl 이 2회(52차·67차) 실패. Sandia 리포지터리·저자 문의 필요. 이웃 표에 다른 조성이 있을 수 있다 |
| 🟡 5 | **아크릴계 O2 용해도 S 실측** | `h` 식의 분모다(§5.1). 지금 `S ≈ 1e-4` 가정 위에 §5.2 결론 전체가 서 있고 카탈로그에 아크릴 S 실측이 **0 건**이다 |
| 🟡 6 | **Damian 2001 확보** | Table 3 의 D 역전(§3.4)을 가를 유일한 문서. closed OA 라 유료 경로 필요 |
| 🟢 7 | ACS Omega OTR 재판정 (§3.2) · 요청서 2순위(평탄화막)·3순위(TAC) | 별도 배치 |

### 해석 측에 바로 넘길 세 가지

1. **`h` 식의 분모를 확인해라** (§5.1). `t_seal` 자리에 두께가 아니라 용해도가 들어가야 한다.
2. **역산 `h_edge` = 1e-8 m/s 는 폐기할 값이 아니다** (§5.2). 문서로 확인된 실링 폭 전 범위에서
   문헌 밴드 안에 들어온다. DOE 에서 식별 실패한 것은 값이 틀려서가 아니라 세 변이 Dirichlet 한계라서다.
3. **실링재 자립막 OTR 1회 측정이 가장 싼 수렴 경로다** (§5.3).

---

## 7. 산출물

```
backend/scripts/catalog/out_ca/
├── ca00_report.md                  이 문서
├── ca01_edge_sealant_o2.json       실링재 계열 카드 1장 · 값 9건 (전량 tier 3, 출처 2건)
└── ca02_photolec_s_vendor.json     Photolec S 카드 2장 · 값 2건 (tier 1)
```

내려받은 원문 (`/data/paper_patent_corpus/standards_appnotes/display/`)

```
polym13091517_Polymers2021_epoxy_coatings_review.xml              등록값 8건의 출처 (Table 3)
Polymers2025_17_1684_PMC12197049_DGEBA-T403_epoxy_clay_O2permeability_fulltext.xml   등록값 1건의 출처
US8193258B2_ITRI_ODF_sealant_composition.html                     조성 계열 확정 근거
acsomega5c00860_epoxy_acrylate_encapsulant.xml                    §3.2 폐기 판단 근거
ACSOmega2025_acsomega.5c00860_SI_epoxyacrylate_OTR.pdf            SI Table S1 원본
FPO_7746428 · FPO_11168254 · FPO_10739647 · FPO_7903230 · FPO_7824746 · FPO_7678433 ·
FPO_7566377 · FPO_7253131 · FPO_6555187 · FPO_6001203 · FPO_10138399 · FPO_7495035 ·
FPO_7545094 · FPO_10050228 · FPO_10622584 · FPO_9865842 · US11740513B2.html ·
US20150160485A1.html · US8367744B2.html · US10818870B2.html · US7255823B1.html
                                                                  정체·형상 확정에 쓴 특허 원문
```

**총계 — 재료 카드 3장 신규, 값 11건 등록 (tier 1 두 건, tier 3 아홉 건, tier 4 없음).**
