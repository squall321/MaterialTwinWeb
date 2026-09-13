# 74차 JD — RF 라미네이트 벤더군

**한 줄** — `subsystem='rf'` 19종 + 같은 벤더의 PCB 표적 5종을 열어, 벤더 시트 **열두 장을 원본으로 다시 읽고**
**값 40행 · 정정 4행 · 판정 9칸**을 준비했다. 그중 **12행은 본문 검색이 못 보는 표 층(`tables/*.md`)에서 나왔다** —
벤더 시트에 없는 **극저온(25 K) 복소유전율**이다.

> **나는 라이브 DB 를 읽기 전용으로만 열었고 적재하지 않았다** — `out_jd/jd74_*.json` 이 내 결과물이다.
> 리허설은 `snapshot_db.py` 사본에서 했다(`cp` 안 썼다). 사본에 `--apply` 한 결과 **값 40행 ok · 정정 4행 ok · 거부 0**,
> `verdicts_check` 의 **bad 0 · 내 판정에서 나온 경고 0**, `analysis_readiness` **차이 없음**이었다.

---

## 1. 벤더별 수확표

| 벤더 | 재료 | 값 행 | 무엇을 캤나 |
|---|---|---:|---|
| **Rogers** | 246 CLTE · 247 CLTE-AT · 2793 RO3035 · 2794 RO3006 · 2795 RO3010 | **11** | CLTE 굽힘탄성률 CMD·NASA 아웃개싱 2 · CLTE-AT 아크저항 · RO3000 세 등급 UL94 · RO3035 극저온 유전 4 |
| **Taconic / AGC** | 250 TSM-DS3 · 271 TLY-5 · 272 RF-35 · 273 TLX-8 | **15** | TSM-DS3 포아송비 CD·아크저항 · TLY-5 박리 2 · TLX-8 박리 3 · TLY-5·RF-35 극저온 유전 8 |
| **Isola** | 220 370HR · 221 IS400 · 222 I-Tera MT40 · 254 Astra MT77 | **8** | 아크저항 4 · 370HR·IS400 굽힘탄성률 MD/TD 4 |
| **Chukoh** | 251 CGN-500 · 252 CGS-500A | **6** | 200 ℃ 박리강도 2 · C-96/40/90 체적·표면저항률 4 |
| **Arisawa** | 253 C33 커버레이 | **0** | 카탈로그(영·일 양판)를 다시 열었다 — **한 장짜리 제품시트라 새로 캘 행이 없다**(§6) |
| | **합계** | **40** | |

**정정 4행**(재료 245·246) · **판정 9칸**(재료 245·246·2793·2794·2795).

### 이번 파동 파일

| 파일 | 내용 |
|---|---|
| `jd74_01_isola.json` | Isola 네 등급 — 아크저항 4 · 굽힘탄성률 4, **8행** |
| `jd74_02_rogers.json` | CLTE · CLTE-AT · RO3000 세 등급, **7행** |
| `jd74_03_taconic_chukoh.json` | TSM-DS3 · TLY-5 · TLX-8 · CGN-500 · CGS-500A, **13행** |
| `jd74_04_jacob2009_cryo_tables.json` | **표 층 수확** — Jacob 2009 SPDR 극저온 복소유전율, **12행** |
| `jd74_05_corrections.json` | CLTE·CLTE-XT 영률 칸의 D790 표기를 판정 창에 제 칸으로, **4행** |
| `jd74_06_verdicts.json` | 코어 빈칸 판정 **9칸 / 재료 5종** |
| `build_jd74.py` | 위 JSON 생성기 — 원문 표의 숫자가 리터럴로 박혀 있고 단위 환산이 한 곳에만 있다 |
| `jd74_ro3000_mechphys_350dpi.png` | **RO3000 2면 350 dpi 크롭** — 열 순서와 비열 빈칸을 증명한다 |
| `jd74_tlx8_peel_350dpi.png` | **TLX-8 2면 350 dpi 크롭** — 박리강도 병합 칸이 어느 시험법에 걸리는지 증명한다 |

---

## 2. Isola 의 `Young's Modulus` = D790 문제 — 만났다. 셋 중 둘은 이미 표시돼 있었다

브리핑이 경고한 그대로였다. 로컬 원본으로 확인한 결과:

| 시트 | `Young's Modulus` 행의 시험법 칸 | 라이브 상태 |
|---|---|---|
| Isola 370HR Rev C | **`ASTM D790-15e2`** | 네 행 전부 `test_standard` 에 D790-15e2 **이미 있다** |
| Isola IS400 Rev C | **`ASTM D790-15e2`** | 네 행 전부 `test_standard` 에 **이미 있다** |
| Isola I-Tera MT40 Rev F | **`ASTM D790-15e2`** | `test_standard` 있고 `mechanical.flexural_modulus` 짝도 **이미 서 있다** |
| Isola Astra MT77 Rev D | — | **이 개정판에는 `Young's Modulus` 행 자체가 없다**(§7) |

**새로 넣는 값에서 어떻게 처리했는가 — 이름이 아니라 시험규격을 보고 키를 골랐다.**
370HR·IS400 은 D790 값이 영률 칸에만 있고 **굽힘 키가 비어 있었다**. 그래서 73차 IA 가 EMC 에서 한 것과 같이
**같은 출처·같은 수를 `mechanical.flexural_modulus` 로도 세웠다**(네 행). 새로 캔 수가 아니다.
넣는 행의 조건칸에는 `test_standard: ASTM D790-15e2` · `test_mode: flexural` · `loading_mode: bending` ·
`test_method: 3-point bend` 를 **전부 판정 창 안에** 적었고, `source_row_name` 에 벤더가 인쇄한 행 이름을 그대로 남겼다.
**영률 칸의 원행은 지우지 않았다** — 삭제는 사람이 정한다.

### 370HR 네 행은 **고치지 않았다** — 고치면 앞 파동의 판정이 사라진다

정정 후보로 열었다가 물렸다. pv3356·3357·6081·6082 는 이미 `test_standard: ASTM D790-15e2` 를 판정 창 안에 갖고 있고,
그 조건칸에는 **54차 PB·51차 MA 의 동률 판정 기록**(`verdict_tie_axis`·`verdict_tie_note` 와 각각의 `_before_correction`)이
길게 들어 있다. 정정기는 `conditions` 를 **통째로 교체**한다 — `test_mode` 한 칸 꾸미자고 두 파동의 판정을 지울 수는 없다.
**표기가 이미 유효한 행은 건드리지 않는다.**

### 71차 GB 가 지목한 재료 245·246 — **같은 무늬가 맞았다. 다만 Isola 가 아니라 Rogers 다**

Rogers CLTE/CLTE-XT 시트를 원본으로 열었다. 기계물성 블록의 행은 셋뿐이다 —
`Flexural Strength … ASTM D790` · `Tensile Strength … ASTM D638` · **`Flex Modulus (MD, CMD) … ASTM D790`**.
**인장탄성률 행이 아예 없다.** 영률 칸에 앉은 8122·7984(CLTE) · 3247·3261 MPa(CLTE-XT)는 그 **Flex Modulus** 행이다.

- **정정 4행** — 시험모드가 `method_detail` 한국어 산문에만 있어 규격을 토큰으로 읽는 쪽에서는 안 보였다.
  `test_standard`·`test_mode`·`loading_mode`·`test_method` 를 **제 칸으로 덧붙였다**. 기존 칸은 하나도 지우지 않았고
  52차 NA 의 되돌리기 표시도 그대로 옮겨 담았다. 값·단위·등급·method·출처는 한 칸도 안 바꿨다.
- **새 행 1** — 246 CLTE 는 `flexural_modulus` 에 **MD 8122 만 있고 CMD 7984 짝이 빠져 있었다.** 채웠다.
  245 CLTE-XT 는 MD·CMD 둘 다 이미 있었다.
- **판정 2칸** — 245·246 의 `mechanical.poisson_ratio`. 이 시트에는 포아송비 행도 없다(지금 값은 형제 등급 CLTE-AT 에서
  빌린 t3 와 클래스 대표값 t4 다).
  **영률 칸에는 판정을 달지 않았다** — 그 칸은 빈칸이 아니라 **이름이 틀린 칸**이고, t1 값이 있는 칸에 부재 판정을 달면
  `verdicts_check` 가 선언·데이터 어긋남으로 신고한다.

### 247 CLTE-AT 는 무고했다
`Young's Modulus 1790 (260) MPa (ksi) … IPC TM-650 2.4.18.3` — **인장 시험법으로 잰 인장탄성률이 맞다.**
같은 시트가 인장강도도 같은 2.4.18.3 으로 찍고, 굽힘은 따로 `Flexural Strength … IPC TM-650 2.4.4` 로 찍는다.

---

## 3. 이방성 축 — **4종에서 갈랐다**

| 재료 | 물성 | 갈라 넣은 축 |
|---|---|---|
| 220 Isola 370HR | `mechanical.flexural_modulus` | **MD 25.81 GPa / TD 21.91 GPa** (인쇄 `A. Length` / `B. Cross`) |
| 221 Isola IS400 | `mechanical.flexural_modulus` | **MD 25.26 GPa / TD 22.95 GPa** |
| 246 Rogers CLTE | `mechanical.flexural_modulus` | **TD 7.984 GPa** 를 채워 MD 8.122 GPa 와 축을 닫았다 |
| 250 AGC TSM-DS3 | `mechanical.poisson_ratio` | **TD 0.20** 을 채워 MD 0.24 와 축을 닫았다 |

**축을 안 갈랐지만 확인한 것** — PTFE·세라믹 충전계의 CTE 는 이미 x/y/z 세 행으로 서 있었다(RO3000 네 등급 ·
CLTE 계 · TLY-5 · TLX-8 · Chukoh 2종 전수). **z 축이 x/y 의 한 자릿수 위인 것도 그대로다** —
RT/duroid 5880 은 면내 31·48 ppm/℃ 에 z 가 **237 ppm/℃**, Chukoh CGS-500A 는 40·38 에 z 가 **217**,
TLX-8 은 21·23 에 z 가 **215**. 이번 파동에서 **부호를 잃은 행은 없었다** — RO3000·CLTE·Taconic 시트의
CTE 는 전부 양수이고, 음수가 나올 수 있는 칸(`Thermal Coefficient of Dielectric Constant`, RO3035 −45 ppm/℃ 등)은
**물성키가 없어 애초에 넣지 않았다**(§6).

---

## 4. 표 층에서 **12행** — 본문 검색은 **0행**이었다

§2 지시대로 표 층부터 두드렸다. 결과가 갈렸다.

- **본문 검색 0행.** `RT/duroid`·`RO4350B RO3003 Rogers laminate Young modulus Poisson` 로 친 질의의 적중은
  **전부 안테나 설계 논문**이었다 — duroid 를 기판으로 *쓴다*고 적을 뿐 물성표를 인쇄하지 않는다.
- **표 층 12행.** `tables/*.md` 를 등급 이름으로 훑어 28건이 걸렸고, 그중 하나가 값이었다 —
  **Jacob 2009, "Low Loss Dielectric Materials for High Frequency Applications", Table 1.**
  저자가 **Split Post Dielectric Resonator(SPDR, TE01δ)** 로 **RO3035 · TLY-5-0100 · RF35-0200** 세 라미네이트의
  복소유전율을 **25 K 와 290 K** 에서 직접 쟀다. **벤더 시트에는 상온밖에 없다** — 카탈로그에 없던 온도축이다.

| 등급 | 재료 | f (MHz) 25 K / 290 K | Dk 25 K / 290 K | tanδ 25 K / 290 K |
|---|---:|---|---|---|
| RO3035 | 2793 | 9704.967 / 9695.140 | **3.58 / 3.65** | **0.0025 / 0.00370** |
| TLY-5-0100 (10 mil) | 271 | 9911.2 / 9911.5 | **2.48 / 2.42** | **0.0009 / 0.0015** |
| RF35-0200 (20 mil) | 272 | 9784.0 / 9781.9 | **3.59 / 3.61** | **0.0025 / 0.0042** |

**온도 표기에 함정이 있다.** 초록과 본문 일부는 `10K` 라고 쓰고 표 머리글은 `25K` 라고 쓴다. 같은 논문 안에서 어긋난다.
**표를 따랐다**(`temperature_k: 25`) — 값이 실린 자리가 표이기 때문이다. 이 어긋남을 각 행 notes 에 그대로 적었다.

나머지 27건의 표는 값이 아니었다 — 안테나 패치 치수·대역폭, 시뮬레이션 입력으로 벤더 Dk 를 재인용한 표
(Ndip 2018 은 RO4350B 3.66 / Astra MT77 3.00 을 그대로 옮겨 적는다), Hong 2001 은 **색인 페이지**였다.

---

## 5. RO3000 — 렌더로 대조했다. **한 칸씩 밀지 않았고, 캘 값은 UL94 셋뿐이었다**

브리핑 경고가 정확했다. 2면을 **350 dpi 로 렌더해 눈으로 확인했다**(`jd74_ro3000_mechphys_350dpi.png`).

- 열 순서는 파일 이름과 다르다 — 인쇄면은 **RO3003 | RO3035 | RO3006 | RO3010**.
  CTE-z 가 25 · 24 · 24 · 16 이고 라이브의 241 · 2793 · 2794 · 2795 값과 정확히 맞는다 → **열 대응이 옳다**.
- `Specifc Heat Capacity` 행의 값은 **셋뿐이다** — 0.9 · (빈칸) · 0.86 · 0.8 J/g/K.
  **빈칸은 RO3035 다.** 텍스트만 보면 한 칸 밀릴 자리인데 렌더로 확인했다. **이웃 값을 끌어다 채우지 않았다** — 판정으로 닫았다.
- 기계물성 블록의 행은 셋뿐이다 — `Copper Peel Strength` · `Young's Modulus`(2단, ASTM D638) · `Dimensional Stability`.
  **포아송비 행도 인장강도 행도 없다.** 72차 HC 가 이미 나머지를 전부 옮겨 놓았고, **남아 있던 것은 `Flammability V-0` 뿐**이었다 — 세 등급에 넣었다.

박리강도는 시트가 각도를 안 찍는다(68차 DD). 이번에 넣은 박리 행(TLY-5 2 · TLX-8 3 · Chukoh 2)은 전부
`peel_angle_source` 에 **"시트 미인쇄 — 규격이 규정하는 각도"** 라고 출처를 밝혔고 **각도 숫자를 값으로 지어내지 않았다.**

---

## 6. 못 넣은 것 셋

### (1) 판정으로 닫은 것 — **9칸 / 재료 5종** (문서를 열어 그 행이 없음을 확인했다)

| 재료 | 칸 | 근거 |
|---|---|---|
| 2793 RO3035 | `poisson_ratio` · `tensile_strength` · **`specific_heat`** | RO3000 시트에 포아송비·인장강도 행 자체가 없고, 비열은 **행은 있는데 RO3035 칸이 빈칸**(렌더로 확인) |
| 2794 RO3006 | `poisson_ratio` · `tensile_strength` | 같은 시트 · 같은 사유 |
| 2795 RO3010 | `poisson_ratio` · `tensile_strength` | 같은 시트 · 같은 사유 |
| 246 CLTE | `poisson_ratio` | CLTE/CLTE-XT 시트에 포아송비 행 없음 |
| 245 CLTE-XT | `poisson_ratio` | 같은 시트 · 같은 사유 |

형제 등급 241 RO3003 에는 같은 사유의 판정이 이미 들어가 있었다 — 이번에 RO3035·RO3006·RO3010 을 맞췄다.

### (2) 물성키가 없어 못 넣은 것 — **인쇄돼 있는데 담을 칸이 없다**

| 인쇄 행 | 어디에 | 왜 못 넣었나 |
|---|---|---|
| `Thermal Coefficient of Dielectric Constant` (RO3035 −45 · RO3006 −262 · RO3010 −395 · CLTE +6 · CLTE-XT −8 · CLTE-AT −10 ppm/℃) | RO3000 · CLTE 계 전수 | **키 없음.** 유전율의 온도계수는 `electrical.*` 에 자리가 없다. **RF 벤더가 예외 없이 찍는 행이다 — 키를 만들 값어치가 있다** |
| `Dimensional Stability (MD, CMD)` (mm/m) | RO3000 · TLX-8 · TLY-5 · Isola 전수 | 키 없음 |
| `Dielectric Breakdown` (kV — 전압이지 강도가 아니다) | Isola 4종 · TLX-8 45 kV · TSM-DS3 47.5 kV | `electrical.dielectric_strength` 는 V/m 다. 두께를 곱해 되돌리면 **역산**이 된다 — 안 했다 |
| `絶縁抵抗`(절연저항, Ω) | Chukoh 2종 | 체적·표면저항률과 다른 물리량인데 키가 없다 |
| `Initiation Tear Strength` (kg) · `NASA WVR`(%) · `CHE`(ppm/%RH) | ULTRALAM 2종 · TLY-5 · TLX-8 | 키 없음 |

### (3) 값으로 안 넣기로 한 것 — **인쇄돼 있지만 그 재료의 측정값이 아니다**

- **Isola `Comparative Tracking Index` `3 (175-249)` Class (Volts)** — 370HR · IS400 · Astra MT77.
  인쇄된 것은 **UL 746A 성능 등급 Class 3** 이고, 괄호의 175–249 V 는 **그 등급의 정의 구간**이지 이 재료를 재서 얻은 수가 아니다.
  `electrical.comparative_tracking_index` 의 단위가 V 라 숫자를 넣으면 **등급의 정의를 측정값으로 둔갑시킨다** — 넣지 않았다.
  (I-Tera MT40 Rev F 는 아예 `3` 만 찍고 볼트를 안 준다.)
- **Chukoh `燃焼性 = 不燃` · `耐薬品性 = 優`** — `thermal.flammability_ul94` 는 UL 94 등급 칸이다. **不燃은 UL 94 등급이 아니다.**
- **CLTE-AT `Dielectric Breakdown`** — 행은 있는데 **값 칸이 비어 있다**.
- **Isola Astra MT77 의 영률** — Rev D(2021-04-20)에는 `Young's Modulus` 행이 **없다**. 라이브의 19.195 / 17.416 GPa 는
  **2017년 Rev B 사본(s2747·s2803)에서 온 것이고 거기에는 `ASTM D3039-095a`(인장)로 인쇄돼 있다.**
  Isola 의 D790 무늬와 **다른 자리다.** 그 두 행은 `mode: tensile` · `test_standard: ASTM D3039-095a` 를 이미
  판정 창에 갖고 있어 **손대지 않았다.** 다만 같은 제품의 신·구 개정판이 서로 다른 행 구성을 갖는다는 사실은 §7 에 넘긴다.

### (4) 문서를 못 연 것 — **판정이 아니다**

- `https://www.agc-multimaterial.com/agc-downloads/AGC_RF-35_TDS.pdf` — **404.** 재료 272 는 다른 사본
  (madpcb · hemeixin · pwcircuits · RF-35TC TDS)으로 이미 채워져 있어 이번 파동에서 막힌 칸은 없다.
  **판정을 달지 않았다.**

---

## 7. 다음 배치에 넘길 것

1. **`electrical.thermal_coefficient_dielectric_constant` 키를 만들어라.** RF 라미네이트 벤더가 **예외 없이** 찍는 행인데
   담을 칸이 없어 이번에만 **여섯 등급 분을 버렸다**(RO3035 −45 · RO3006 −262 · RO3010 −395 · CLTE +6 · CLTE-XT −8 ·
   CLTE-AT −10 ppm/℃, 여기에 RO3003 −3 · ULTRALAM 3850HT +24 까지 여덟). **음수가 정상인 물성이라 범위 가드 하한을
   0 으로 두면 안 된다**(42차 DA 의 포아송비와 같은 사고가 난다). RO3000 표는 부호가 `-3 · -45 · -262 · -395` 로
   네 칸 다 음수다 — `docling` 이 마이너스를 잃는 자리이니 **렌더 대조를 필수로 걸어라.**
2. **Taconic TLX-8 의 `Young's Modulus` 블록에 시험규격이 둘 섞여 있다.** 350 dpi 로 확인했다 —
   **MD 6,757 / CD 8,274 N/mm² 는 `ASTM D 902`**, **MD 11,238 N/mm² 는 `ASTM D 3039`** 다.
   같은 방향(MD)에서 D902 쪽이 D3039 쪽보다 **40 % 낮다.** D902 는 유리섬유 적층 절연재 규격이라 굽힘 계열일
   가능성이 있는데, **규격 본문을 못 봐서 단정하지 않았다.** 세 행 모두 `test_standard` 가 판정 창 안에 있어
   대표값 선택기가 갈라 볼 수는 있다. **규격을 열 수 있는 파동이 mode 를 확정해라.**
3. **Chukoh 카탈로그에 아직 안 캔 등급이 넷 있다** — `CGP-500A` · `CGA-500` · `CGH-500` · `CGK-500`.
   같은 표에 열두 행(比誘電率·誘電正接·체적/표면저항률·絶縁抵抗·曲げ強さ·吸水率·CTE x/y/z·比重·引き剥がし強さ×2)이
   전부 인쇄돼 있다. **재료 4종 × 약 12행 = 40행 대의 표적이다**(`Chukoh_CopperCladLaminate_Catalog05_JA.pdf`).
4. **Isola Astra MT77 의 개정판 차이.** Rev B(2017)에는 `Young's Modulus … ASTM D3039-095a` 행이 있고
   Rev D(2021)에는 없다. **어느 개정판을 카탈로그의 기준으로 삼을지** 정해 둘 필요가 있다 — 같은 문제가
   I-Tera MT40 Rev F(2025-12-08, 로컬에 이미 최신본이 있다)에도 온다.
5. **이 파동의 40행은 코어 카드를 한 장도 세우지 못했다.** `analysis_readiness` 가 라이브와 사본에서 **똑같이 나왔다** —
   2793·2794·2795 를 막는 것은 **포아송비 한 칸**이고, 그 칸은 §6(1)대로 **벤더가 안 찍는다.**
   이 세 등급을 해석 격자에 세우려면 **클래스 대표값(t3, `grade_scope` 필수)** 을 놓든지 **다른 문헌을 찾든지** 정해야 한다 —
   형제 등급 241 RO3003 에는 이미 t4 클래스 가정값 0.17 이 서 있다. **같은 계열인데 한쪽만 비어 있는 것이 지금 상태다.**
