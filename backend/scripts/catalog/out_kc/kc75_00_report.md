# 75차 KC — Chukoh 미채굴 4등급 · D902 모드 확정 · MT77 개정판 결정 · 유전율 온도계수 실사

**한 줄** — 74차 JD 가 넘긴 넷을 전부 닫았다. **Chukoh 4등급을 새 카드로 세워 60행**을 캤고,
**`ASTM D 902` 를 인장으로 확정**해 TLX-8 다섯 행에 모드를 박았고, **Astra MT77 을 Rev D 기준으로 정하면서**
Rev D 가 인쇄하지 않는 굽힘탄성률 2행을 채웠고, **유전율 온도계수를 19등급에서 실사**해 키 신설 근거표를 남겼다.

> **나는 라이브 DB 를 읽기 전용으로만 열었고 적재하지 않았다** — `out_kc/kc75_*.json` 이 내 결과물이다.
> 리허설은 `snapshot_db.py` 사본에서 했다(`cp` 안 썼다). 사본에 `--apply` 한 결과
> **값 62행 ok · 신규 재료 4종 · 정정 5행 ok · 거부 0**,
> `verdicts_check` 는 라이브와 **출력이 한 글자도 다르지 않았고**(기존 경고 39건 그대로, 내 판정에서 나온 경고 0),
> `integrity_check` 는 **개수 줄 하나만 달랐다**(재료 2784→2788 · 값 46709→46771). 새 이상 0건.
> `analysis_readiness` 는 **모든 해석에서 `필수 완비` 수가 그대로다**(구조 817 · 벤딩 268 · 열전달 667 · 열응력 746 …) —
> 차이는 **전부 +4**(새 카드 4장)이고 그 4 가 붙은 자리는 `youngs_modulus`·`poisson_ratio`·`conductivity`·`specific_heat`
> 의 **`없음` 칸뿐**이다. 즉 **벤더가 안 찍는 칸에만 붙었다** — §6(1)의 판정과 정확히 일치한다. 퇴행 0건.
>
> ⚠ **`analysis_readiness.py` 는 DB 경로가 7행에 박혀 있어 `MATERIALTWIN_DATA_DIR` 를 무시한다** —
> 처음에 사본을 가리켰다고 믿고 돌린 두 번이 **둘 다 라이브를 읽어** 출력이 바이트까지 같았다.
> 읽기 전용이라 라이브에 해는 없었지만 **리허설이 조용히 무력화됐다.** 위 수치는 경로를 갈아끼운
> 임시 사본으로 다시 돌려 얻은 것이다. `apply_core_verdicts.py` 가 65차 AD 때 고친 것과 **같은 병**이다 — §7-7.

---

## 1. 이번 파동 파일

| 파일 | 내용 |
|---|---|
| `kc75_01_chukoh_4grades.json` | **신규 재료 4종 + 값 60행** — CGP-500A · CGA-500 · CGH-500 · CGK-500 |
| `kc75_02_astra_flexmod.json` | Astra MT77 굽힘탄성률 MD/TD, **2행** |
| `kc75_03_tlx8_d902_mode.json` | TLX-8 의 `ASTM D 902` 다섯 행에 시험모드, **정정 5행** |
| `build_kc75.py` | 위 JSON 생성기 — 원문 표의 숫자가 리터럴로 박혀 있고 단위 환산이 한 곳에만 있다 |
| `kc75_chukoh_tbl_top_350dpi.png` · `kc75_chukoh_tbl_bot_350dpi.png` | **Chukoh 製品性能 표 350 dpi 렌더 2장** — 열 순서·지수 위첨자·CTE 부호를 증명한다 |

**코어 판정 12칸**(재료 4종 × 3키)은 `apply_core_verdicts.py` 를 쓰지 않는다 — 신규 카드라
`new_material.attributes.core_absent_from_vendor_sheet` 에 **dict 로 박아 태어날 때부터 들고 나온다**
(251·252 와 같은 모양). 적재 한 번으로 값과 판정이 같이 선다.

---

## 2. Chukoh 4등급 — **60행 · 카드 4장**

`Chukoh_CopperCladLaminate_Catalog05_JA.pdf` 2면 `製品性能` 표가 여섯 등급을 한 표에 싣는다.
이미 라이브에 있던 251 CGN-500 · 252 CGS-500A 를 뺀 **네 등급**이 표적이었다.

### 2.1 열 순서 — **밀리지 않았다. 렌더로 증명했다**

72차 HC 의 Rogers 무늬(파일 이름과 인쇄면 열 순서가 다름)를 의심해 **350 dpi 로 렌더해 눈으로 봤다.**

```
試験項目 | 単位 | 試験方法 | CGS-500A | CGN-500 | CGP-500A | CGA-500 | CGH-500 | CGK-500
```

**인쇄면 열 순서가 `pdftotext` 추출 순서와 정확히 같다.** 교차검증도 맞았다 —
추출한 CGS-500A 열(比誘電率 2.15 · CTE 40/38/217 · 曲げ強さ 50)이 라이브 252 의
pv4157 · pv4163~4165 · pv4161 과 한 칸도 틀리지 않는다. **열 대응이 옳다.**

### 2.2 `docling`·`pdftotext` 가 뭉갠 두 자리 — 둘 다 렌더로 잡았다

| 뭉갠 것 | 텍스트 추출 | 렌더 확인 |
|---|---|---|
| **저항률의 위첨자** | `1015` · `1014` · `1013` 처럼 지수가 본문에 붙어 버린다 | **10¹⁵ · 10¹⁴ · 10¹³** — 지수로 읽고 박았다 |
| **CTE 부호** | 부호 없음 | **열여덟 칸 전부 양수다** — 이 표에서 마이너스가 붙는 자리는 측정구간 `-65〜150℃` 하나뿐이고 그 부호는 텍스트에도 남았다 |

브리핑이 경고한 **PTFE 계의 음수 축은 이 표에 없다.** 지어내지 않았고, 없는 것을 없다고 적었다.

### 2.3 등급별 수확 — 15행 × 4등급

| 인쇄 행 | 물성키 | 환산 | CGP-500A | CGA-500 | CGH-500 | CGK-500 |
|---|---|---|---|---|---|---|
| 比誘電率 | `electrical.dielectric_constant` | — | 2.60 | 3.00 | 3.45 | 5.00 |
| 誘電正接 | `electrical.dissipation_factor` | — | 0.0018 | 0.0030 | 0.0027 | 0.0040 |
| 体積抵抗率 (A) | `electrical.resistivity_volume` | Ω·cm ×0.01 | 1e13 | 1e13 | 1e13 | 1e11 |
| 体積抵抗率 (C-96/40/90) | 〃 | 〃 | 1e12 | 1e12 | 1e12 | 1e11 |
| 表面抵抗率 (A) | `electrical.surface_resistivity` | 환산 없음 | 1e14 | 1e14 | 1e14 | 1e12 |
| 表面抵抗率 (C-96/40/90) | 〃 | 〃 | 1e14 | 1e14 | 1e14 | 1e12 |
| **曲げ強さ** (A) | `mechanical.flexural_strength` | MPa ×1e6 | 120 MPa | 60 MPa | 120 MPa | 240 MPa |
| 吸水率 | `chemical.water_absorption_24h` | % ÷100 | 0.0001 | 0.0002 | 0.0002 | 0.0004 |
| 線膨張係数 **X軸** | `thermal.expansion_linear` | ppm ×1e-6 | 16 | 16 | 13 | 12 |
| 線膨張係数 **Y軸** | 〃 | 〃 | 20 | 20 | 14 | 13 |
| 線膨張係数 **Z軸** | 〃 | 〃 | **216** | **216** | **174** | **120** |
| 比重 | `physical.density` | g/cc ×1000 | 2200 | 2300 | 2300 | 2400 |
| 引き剥がし強さ (A) | `interface.peel_strength` | kN/m ×1000 | 3000 | 1500 | 1500 | 1500 |
| 引き剥がし強さ (200℃雰囲気) | 〃 | 〃 | 1500 | 1000 | 1000 | 1200 |
| 耐薬品性 | `chemical.chemical_resistance` | 문자열 | 優 | 優 | 優 | 優 |
| | | | **15행** | **15행** | **15행** | **15행** |

**박리강도는 각도를 지어내지 않았다.** 카탈로그가 각도를 찍지 않으므로 `peel_angle_source` 에
`시트 미인쇄` 라고 출처를 밝혔다(68차 DD 규약). 각주 `※引き剥がし強さは、1oz銅箔（0.035㎜）の測定値です` 는
`substrate` 에 담았다.

**`比重`(비중)을 `physical.density` 로 옮긴 근거** — 단위 칸이 `g/cc` 라 수치가 그대로 밀도다.
형제 등급 252(pv4166)가 이미 같은 처리이고, 그 관례를 그대로 따랐다.

**`耐薬品性 = 優` 는 넣었고 `燃焼性 = 不燃` 은 안 넣었다 — 74차 JD 가 묶어 뒀던 둘을 갈랐다.**
`chemical.chemical_resistance` 는 **단위가 없는 정성 키**이고 라이브 24행 중 20행이 벤더 인쇄
정성 서술을 t1·measured 로 담고 있다 — `優` 는 그 자리에 맞다(시험법 칸이 `-` 라는 것도 조건에 적었다).
반면 `thermal.flammability_ul94` 는 **UL 94 등급 칸**이고 `不燃` 은 UL 94 등급이 아니다 — JD 판단을 유지했다.

### 2.4 이방성 축 — **4종에서 갈랐다**(+ Astra 1종 = 5종)

| 재료 | 물성 | 갈라 넣은 축 | 면내 대비 z |
|---|---|---|---|
| CGP-500A | `thermal.expansion_linear` | **X 16 / Y 20 / Z 216 ppm/℃** | **z 가 11~13배** |
| CGA-500 | 〃 | **X 16 / Y 20 / Z 216** | **z 가 11~13배** |
| CGH-500 | 〃 | **X 13 / Y 14 / Z 174** | **z 가 12~13배** |
| CGK-500 | 〃 | **X 12 / Y 13 / Z 120** | **z 가 9~10배** |
| 254 Astra MT77 | `mechanical.flexural_modulus` | **MD 18.62 GPa / TD 17.44 GPa** | (면내 이방) |

`conditions.direction` 은 X/Y 를 `in-plane`, Z 를 `through-thickness` 로 정규화하고
**인쇄 글자는 `direction_verbatim` 에 그대로** 남겼다(251·252 관례). **축마다 별도 행이다.**

---

## 3. TLX-8 의 `ASTM D 902` — **인장으로 확정했다. 키 이동은 필요 없었다**

74차 JD 가 *"규격 본문을 못 봐서 단정하지 않았다"* 고 넘긴 표적이다. **닫았다.**

### 3.1 규격이 무엇을 재는가

**ASTM D902 = `Standard Test Methods for Flexible Resin-Coated Glass Fabrics and Glass Fabric Tapes
Used for Electrical Insulation`** (2020-03-09 **철회**, 최종판 D902-12).

규격이 열거하는 시험 **전수**:

> Breaking Strength · Conditioning · Dielectric Breakdown Voltage and Dielectric Strength ·
> Dissipation Factor and Relative Permittivity · Effect of Elevated Temperature · Resistance to Oil ·
> Sampling · Thermal Endurance · Thickness · **Thread Count** · Weight · Weight Loss at Elevated Temperature

**굽힘·휨 시험이 하나도 없다.** 기계시험은 `Breaking Strength` 하나뿐이고,
그 절차는 **ASTM D828(정속신장 인장시험)** 을 참조한다.

### 3.2 왜 굽힘일 수 없는가 — 근거 셋

1. **수록 시험에 굽힘이 없다.** 유일한 기계시험이 Breaking Strength 이고 그 참조가 D828 인장이다.
2. **시편 형태가 굽힘을 허용하지 않는다.** 대상은 `Thread Count` 를 세는 **유연한 코팅 유리직물·테이프**다 —
   늘어진 직물 테이프는 3점 굽힘으로 잴 수가 없다. 굳은 적층판용 규격은 D902 가 아니라 **ASTM D709** 다.
   (JD 의 가설 *"유리섬유 적층 절연재 규격이라 굽힘 계열일 가능성"* 은 **규격의 대상을 적층판으로 잘못 본 것**이다.)
3. **벤더 자신이 D902 로 인장강도를 찍는다.** 라이브 pv6274·pv6275 —
   `Tensile Strength (MD) | ASTM D 902 | psi | 35,600` · `(CD) | ASTM D 902 | 27,500`.
   **같은 시트 계열에서 같은 규격이 인장강도를 재고 있다.** 이게 결정적이다.

**결론 — TLX-8 의 D902 모듈러스는 인장이다. `mechanical.youngs_modulus` 에 이미 제대로 앉아 있어 키를 옮기지 않았다.**
**Isola 의 `Young's Modulus`=D790 함정과 다른 자리다.**

### 3.3 MD 에서 40 % 갈리는 이유는 모드가 아니라 시험법이다

같은 MD 인데 D902 6,757 vs D3039 11,238 N/mm² 다. 둘 다 인장이므로 이 차이는 **모드 차이가 아니라
시험법 차이**다 — D902 는 전(全)두께 직물 스트립을 그립으로 잡아 크로스헤드 변위로 읽고,
D3039 는 탭 붙인 강성 복합재 쿠폰을 신율계로 읽는다. 그립 슬립·직물 크림프가 D902 쪽 겉보기 강성을 낮춘다.
**두 행 다 살려 뒀고, `test_standard` 가 판정 창 안에 있어 대표값 선택기가 갈라 본다.**

### 3.4 정정 5행 — **기존 조건칸을 한 칸도 지우지 않았다**

브리핑 경고(정정기가 `conditions` 를 통째로 갈아끼운다)를 그대로 지켰다.
다섯 행의 기존 조건을 **라이브에서 읽어 전부 담고** 모드 칸만 덧붙였다.

| pv | 재료 | 키 | 보존한 앞 파동 기록 |
|---|---|---|---|
| 5414 | 273 | `youngs_modulus` MD 6,757 | 54차 PA 되돌리기 표시 |
| 6353 | 273 | `youngs_modulus` MD 6,757(중복) | **52차 NB 중복 판정** + 54차 PA |
| 6354 | 273 | `youngs_modulus` TD 8,274 | 54차 PA |
| 6274 | 273 | `tensile_strength` MD | **51차 MA 동률 판정** + 52차 NA |
| 6275 | 273 | `tensile_strength` TD | **51차 MA 동률 판정** + 52차 NA |

덧붙인 칸 — `test_mode: tensile` · `loading_mode: tension` ·
`test_method: strip tensile / breaking strength (ASTM D902, 절차는 ASTM D828 정속신장 인장)` ·
`test_standard_scope` · `mode_confirmed_by`. **값·단위·등급·method·출처는 한 칸도 안 바꿨다.**
`correction_reason`·`corrected_by` 는 앞 기록 뒤에 이어 붙였다(`54차 PA → 75차 KC`).

**`ASTM D 3039` 행은 손대지 않았다** — 원래 모호하지 않다.

---

## 4. Astra MT77 — **Rev D(2021-04-20)를 기준으로 정했다**

### 4.1 왜 Rev D 인가

시트 자신이 **개정 이력을 인쇄한다**(Rev D 3면 NOTES):

```
A: Initial release - 4/17
B: Corrected units for Flexural and Tensile Strength - 8/18
C: Change MOT to RTI 5/19
D: Changed VLP2 to HVLP to align with common industry terms 4/21
```

근거 셋이다.

1. **Rev B 의 변경 사유가 `단위 오류 정정`이다.** 굽힘·인장 강도의 단위가 Rev A 에서 틀렸고 B 가 고쳤다 —
   **B 이전 사본은 알려진 오류를 품은 문서다.** 라이브의 출처 2803 은 `03/17 DSAstraMT77Q` 로
   **Rev A(4/17)보다도 앞선다.** (74차 JD 가 2747·2803 을 "2017년 Rev B" 로 적었는데, 2803 은 Rev B 가 아니다.)
2. **두 판이 실제로 어긋나는 자리를 찾았다.** 03/17 시트는 `Flexural Strength B. Crosswise = **38** ksi ·
   시험법 **ASTM D790-10**` 을 찍는데, Rev D 는 `**39.0** ksi · **IPC-TM-650 2.4.4B**` 다.
   **값도 시험법도 다르다.** 라이브의 여섯 행(pv3430·3431·4188·4189·6137·6138)은 전부 39.0 ksi + 2.4.4B —
   **이미 Rev D 를 따르고 있었다.** 기준을 Rev D 로 정하면 라이브를 고칠 것이 없다.
3. **Rev D 는 최신판이고 로컬에 원본이 있다.**

### 4.2 그러면 Rev D 가 지운 모듈러스 행은 어떻게 하나 — **살린다. 충돌이 아니라 부재다**

Rev D 에는 모듈러스 행이 **아예 없다.** 값이 바뀐 것이 아니라 **행이 사라진 것**이므로
03/17 시트의 모듈러스와 **모순되지 않는다.** 그래서 기존 t1 인장탄성률 4행(pv12968·12969·13435·13436)은
**그대로 두고**, `datasheet_revision` 으로 출처 판을 명시한다. **삭제는 사람이 정한다.**

### 4.3 부산물 — 굽힘탄성률 2행을 캤다

03/17 시트를 원본으로 다시 열었더니 **Isola 의 D790 함정과 정반대 자리**였다.
이 시트는 인장과 굽힘을 **제 이름으로 따로 인쇄한다**:

```
Tensile Modulus/Young's Modulus    A. Lengthwise 2,784 | B. Crosswise 2,526  ksi  ASTM D3039-095a
Flexural Modulus/Taylor's Modulus  A. Lengthwise 2,701 | B. Crosswise 2,529  ksi  ASTM D790-10
```

인장 쪽은 라이브에 이미 있었고 **굽힘 쪽 짝이 비어 있었다**(재료 254 의 `mechanical.flexural_modulus` 0행).
채웠다 — **MD 2,701 ksi = 18.62 GPa · TD 2,529 ksi = 17.44 GPa**, `test_standard: ASTM D790-10` ·
`test_mode: flexural` · `loading_mode: bending` 을 전부 판정 창 안에.

> TD 인장 **2,526** 과 TD 굽힘 **2,529** 는 **세 자리에서 갈리는 서로 다른 수다** —
> 같은 수를 두 키에 옮긴 것이 아니다(73차 IA·74차 JD 의 처리와 다른 경우다).

---

## 5. 유전율 온도계수 — **19등급에 인쇄돼 있다. 음수가 절반이다**

74차 JD 의 요청대로 **키를 만들지 않고 근거표만 남긴다.** 마이그레이션은 사람이 한다.
`property_definition` 275종을 전수 확인했다 — **`electrical.thermal_coefficient_dielectric_constant` 는 없다.**

`standards_appnotes/pcb` · `poly` 의 **375개 문서(PDF 283 · HTML 92)를 전수 훑고,
적중한 시트는 전부 350 dpi 로 다시 렌더해 부호를 눈으로 확인했다.**

### 5.1 근거표 — 5개 벤더 · 19등급

| 벤더 | 시트 | 등급 | **TCDk** | 단위 | 측정 구간 | 주파수 / 시험법 | 부호 렌더 확인 |
|---|---|---|---:|---|---|---|:--:|
| Rogers | RO3000 (2024-01) | RO3003 | **−3** | ppm/℃ | −50~150℃ | 10 GHz · IPC TM-650 2.5.5.5 | ✔ |
| Rogers | 〃 | RO3035 | **−45** | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Rogers | 〃 | RO3006 | **−262** | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Rogers | 〃 | RO3010 | **−395** | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Rogers | CLTE/CLTE-XT | CLTE | **6** (부호 미인쇄) | ppm/℃ | −50~150℃ | 10 GHz · 2.5.5.5 | ✔ |
| Rogers | 〃 | CLTE-XT | **−8** | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Rogers | CLTE-AT | CLTE-AT | **−10** | ppm/℃ | **0~100℃** | 10 GHz · 2.5.5.5 | ✔ |
| Rogers | RO4003C/RO4350B | RO4003C | **+40** | ppm/℃ | −50~150℃ | 2.5.5.5 · **주파수 미인쇄** · Z축 | ✔ |
| Rogers | 〃 | RO4350B | **+50** | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Rogers | RO4835 | RO4835 | **+50** | ppm/℃ | −50~150℃ | 2.5.5.5 · 주파수 미인쇄 | ✔ |
| Rogers | RT/duroid 5870·5880 | RT/duroid 5870 | **−115** | ppm/℃ | −50~150℃ | 2.5.5.5 · Z축 | ✔ |
| Rogers | 〃 | RT/duroid 5880 | **−125** | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Rogers | ULTRALAM 3850HT | 3850HT | **(+)24** | ppm/℃ | −50~150℃ | **8 GHz** · IPC 2.5.5.5 | ✔ |
| Nanya | NP-730 | NP-730 | **76** (부호 미인쇄) | ppm/℃ | −50~150℃ | 10 GHz · IPC-TM-650 **2.5.5.13** | ✔ |
| Nanya | NP-822 | NP-822 | **80** (부호 미인쇄) | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Nanya | NP-826 | NP-826 | **71** (부호 미인쇄) | ppm/℃ | −50~150℃ | 〃 | ✔ |
| Shengyi | LNB33 | LNB33 | **+125** | ppm/℃ | −40~150℃ | 10 GHz · **IEC 61189-2-721** | ✔ |
| Shengyi | S7136H | S7136H | **+50** | ppm/℃ | **−55~85℃** | IPC-TM-650 **2.5.5.15** · Z축 | ✔ |
| Shengyi | SCGA-500 GF255 | SCGA-500 | **−70** | ppm/℃ | −40~150℃ | 10 GHz · IEC 61189-2-721 | ✔ |

### 5.2 키를 만들 때 반드시 챙길 것 — 실사에서 나온 다섯

1. **음수가 정상이다. 하한 가드를 0 으로 두면 안 된다.** 19칸 중 **9칸이 음수**이고 최소가 **−395 ppm/℃**(RO3010)다.
   42차 DA 의 포아송비와 **같은 사고가 난다.** 하한은 넉넉히 잡아라(예: −1e-3 ~ +1e-3 1/K).
2. **단위는 `1/K` 다.** 전부 ppm/℃ 로 인쇄되고 온도 *차이* 당 계수라 ℃⁻¹ = K⁻¹ 이다 — **×1e-6 환산만** 하면 된다.
3. **측정 구간이 시트마다 다르다. `temperature_range_c` 를 필수로 걸어라.**
   −50~150 이 표준이지만 **CLTE-AT 는 0~100**, **S7136H 는 −55~85**, Shengyi 계는 −40~150 이다.
   구간이 다르면 수를 나란히 놓을 수 없다.
   > **74차 JD 의 표를 여기서 하나 고친다** — CLTE-AT 의 구간은 −50~150 이 아니라 **0~100℃** 다.
   > 시트의 홍보 문구에 나오는 `−55~150℃` 는 **사용온도**지 TCDk 측정창이 아니다.
4. **시험법이 넷으로 갈린다** — IPC-TM-650 **2.5.5.5** / **2.5.5.13** / **2.5.5.15** / IEC **61189-2-721**.
   `test_standard` 를 판정 창에 박아야 대표값 선택기가 갈라 본다.
5. **방향이 붙는 시트가 있다.** RO4003C·RO4350B·RT/duroid·S7136H 는 **Z축**이라고 찍는다 —
   `conditions.direction` 을 받아라. 나머지는 방향을 안 찍는다(지어내지 마라).

### 5.3 부호 없이 인쇄되는 네 칸 — **`+` 를 지어내지 마라**

CLTE(6) · NP-730(76) · NP-822(80) · NP-826(71)은 **부호 글자가 아예 없다**(렌더로 확인).
양수로 읽는 것이 맞지만 **시트가 `+` 를 찍은 것은 아니다** — ULTRALAM(`(+) 24`)·RO4003C(`+40`)처럼
명시적으로 부호를 찍는 시트와 구분해 `sign_printed: false` 같은 표시를 남기는 것을 권한다.

---

## 6. 못 넣은 것 셋

### (1) 판정으로 닫은 것 — **12칸 / 재료 4종**(문서를 열어 그 행이 없음을 확인했다)

| 재료 | 칸 | 근거 |
|---|---|---|
| CGP-500A · CGA-500 · CGH-500 · CGK-500 | `mechanical.youngs_modulus` | 카탈로그 `製品性能` 표의 행은 **열둘**이고 **탄성률 행이 아예 없다** — 강도축이 `曲げ強さ` 하나다. 350 dpi 렌더로 열두 행 전수를 다시 셌다 |
| 같은 4종 | `mechanical.poisson_ratio` | 같은 표 · 같은 사유. 이 벤더는 탄성상수를 인쇄하지 않는다(57차 SB 가 251·252 에서 확인한 것과 같은 표) |
| 같은 4종 | `thermal.specific_heat` | 전권 텍스트에 `比熱` 0건 · `熱伝導` 0건. 이 표의 열물성은 `線膨張係数` 하나뿐이다 |

형제 등급 251·252 에 이미 같은 사유의 판정이 들어가 있었다 — 네 등급을 맞췄다.

### (2) 물성키가 없어 못 넣은 것 — **인쇄돼 있는데 담을 칸이 없다**

| 인쇄 행 | 어디에 | 몇 칸 | 왜 못 넣었나 |
|---|---|---:|---|
| **`Thermal Coefficient of Dielectric Constant`** | RF 라미네이트 **19등급** (§5) | **19** | **키 없음.** 5개 벤더가 찍는다 — 키를 만들 값어치가 있다 |
| `絶縁抵抗`(절연저항, Ω) | Chukoh 4등급 × (A · D-2/100) | **8** | 체적·표면저항률과 **다른 물리량**인데 키가 없다. CGP 1e13/1e13 · CGA 1e13/1e10 · CGH 1e13/1e12 · CGK 1e11/1e10 Ω |
| `Dimensional Stability` (mm/M) | TLX-8(MD/CD × After Bake/Thermal Stress) | 4 | 키 없음 |
| `Dielectric Breakdown` (kV — 전압이지 강도가 아니다) | TLX-8 45 kV | 1 | `electrical.dielectric_strength` 는 V/m 다. 두께를 곱해 되돌리면 **역산**이 된다 — 안 했다 |

### (3) 값으로 안 넣기로 한 것 — **인쇄돼 있지만 그 재료의 측정값이 아니다**

- **Chukoh `燃焼性 = 不燃`**(4등급) — `thermal.flammability_ul94` 는 UL 94 등급 칸이다.
  **`不燃`(불연)은 UL 94 등급이 아니다.** 74차 JD 의 판단을 유지했다.
  (같이 묶여 있던 `耐薬品性 = 優` 는 **갈라서 넣었다** — §2.3.)
- **Astra MT77 03/17 시트의 `Flexural Strength` 두 행** — 라이브가 이미 Rev D 값(49.0/39.0 ksi)을 갖고 있고
  03/17 은 **Rev B 가 정정한 단위 오류 이전 문서**다(§4.1). **옛 판의 38 ksi 를 넣지 않았다.**

### (4) 문서를 못 연 것 — **판정이 아니다**

- `Nanya_CCL_ProductCatalog_2001-09_scanned_52p.pdf` — **텍스트 층이 없는 스캔본 52면.**
  OCR 을 돌리지 않아 TCDk 행 유무를 확인하지 못했다. **판정을 달지 않았다.**
  (텍스트 층이 없는 나머지 8개 PDF 는 렌더로 직접 읽어 TCDk 없음을 확인했다.)

---

## 7. 다음 배치에 넘길 것

1. **`electrical.thermal_coefficient_dielectric_constant` 키를 만들어라.** §5 에 **19등급 실사표**를 남겼다 —
   5개 벤더가 예외 없이 찍는 행이다. **하한 가드를 0 으로 두지 마라**(9칸이 음수, 최소 −395 ppm/℃).
   단위 `1/K`(ppm/℃ ×1e-6), **`temperature_range_c` 필수**(구간이 시트마다 다르다),
   `test_standard` 4종 분기, 일부 시트는 `direction: Z`. 부호 미인쇄 4칸은 `+` 를 지어내지 마라.
2. **`electrical.insulation_resistance`(절연저항, Ω) 키를 검토해라.** Chukoh 만 이번에 **8칸**을 버렸고,
   체적저항률(Ω·m)·표면저항률(Ω)과 **물리량이 다르다**. JIS 계 일본 벤더 시트가 관행적으로 찍는 행이라
   Arisawa·Sumitomo 계를 열면 더 나온다.
3. **Chukoh 카탈로그는 이제 전량 채굴됐다.** 여섯 등급(CGS-500A · CGN-500 · CGP-500A · CGA-500 ·
   CGH-500 · CGK-500)이 전부 카탈로그의 열두 행을 갖췄다. **이 벤더에 남은 표적은 없다** —
   단, 여섯 등급 전부 **영률·포아송비가 t3/t4 이거나 비어 있다**(벤더가 안 찍는다). 해석 격자에 세우려면
   클래스 대표값(t3, `grade_scope` 필수)을 놓든지 다른 문헌을 찾아야 한다.
4. **`ASTM D 902` 를 쓰는 다른 Taconic/AGC 등급을 훑어라.** 모드가 확정됐으니(인장) 이제 안전하게 캘 수 있다.
   TLY-5·RF-35·TSM-DS3 시트에 같은 규격이 붙은 행이 더 있는지 보면 된다.
5. **Astra MT77 의 기준을 Rev D 로 정했다. 같은 문제가 I-Tera MT40 에 온다** —
   Rev F(2025-12-08) 로컬본이 최신이고, 구판과 행 구성이 다를 수 있다. **같은 방식으로 개정 이력 인쇄면을 먼저 읽어라** —
   Isola 시트는 NOTES 면에 개정 사유를 찍는다. 그게 어느 판을 믿을지 가르는 가장 싼 근거다.
6. **`Nanya_CCL_ProductCatalog_2001-09_scanned_52p.pdf` 를 OCR 할지 정해라**(§6-4).
7. **`analysis_readiness.py` 의 박힌 DB 경로를 고쳐라.** 7행이
   `DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'` 로 **하드코딩**돼 있고
   `MATERIALTWIN_DATA_DIR` 도 `--db` 도 받지 않는다. **사본에 `--apply` 한 뒤 준비도를 대조하는 리허설이
   조용히 무력화된다** — 나도 두 번 돌려 바이트까지 같은 출력을 받고서야 알았다. 읽기 전용이라 라이브가
   더럽혀지지는 않지만, **차이가 없다는 잘못된 확신**을 준다는 점에서 65차 AD 가 `apply_core_verdicts.py` 에서
   고친 것과 같은 병이고 더 조용하다. 형제 도구(`integrity_check`·`verdicts_check`·`coverage_report`)처럼
   `DEFAULT_DB = os.path.join(os.environ.get('MATERIALTWIN_DATA_DIR', ...), 'materialtwin.db')` 와 `--db` 를 달아라.
   **다른 스크립트에 같은 무늬가 더 있는지도 같이 훑어라.**
