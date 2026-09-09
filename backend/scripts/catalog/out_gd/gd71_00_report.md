<!-- 71차 GD 수집 배치 보고서 — 70차 FA 의 인계 목록 넷을 각각 끝까지 밀어붙인다 -->

# 71차 GD — 문 하나는 열렸고 문 하나는 닫혔다

**한 줄 답: Sumitomo LαZ 는 온도별 영률을 내주며 카드 13장이 섰고, IPC-4101 은 밀도를 규정하지 않는다는 것이 확인돼 「슬래시시트로 19칸을 닫는다」는 70차 FA 의 기대는 근거째 닫혔다.**

**수확: 재료 33장 · 물성 566행** (t1 540 · t3 26 · **t4 0**) · 자체검증 오류 0 · 새로 받은 문서 0건
**판정 6건** (`gd71_09_verdicts.json`)

| 표적 | 결과 | 카드 | 물성행 |
|---|---|---:|---:|
| **① Sumitomo LAZ** | **13등급** — 온도별 영률 26행이 들어왔다(4785 7 · 6785 4 · 2002 1 · **7752 1**) | **13** | **106** |
| **② IPC-4101 로 밀도 19장** | **0칸 — 규격에 밀도 항목이 없다.** 판정으로 기록 | 0 | 0 |
| **③ Resonac 나머지 쪽** | **20등급** — 총합표 세 쪽(PDF 6·7·8)을 렌더 대조로 전부 담았다 | **20** | **460** |
| **④ MGC FR-4 밀도 2칸** | **0칸 — 벤더가 어디에도 안 찍는다.** 판정으로 기록 | 0 | 0 |

---

## ② 이 배치의 핵심 물음 — **IPC-4101 본문에 밀도 항목이 있었는가**

### 답: **없다. 어느 개정판에도 없고 슬래시시트에도 없다. 닫힌 문이다.**

70차 FA 는 이렇게 남겼다 — 「IPC-4101 슬래시시트가 문일 수 있다 … 규격서 본문이 시트별 밀도를 규정하면 **t2 로 19칸이 한 번에 닫힌다**」. 그리고 68차 DC 는 §3.9.1 여덟 항목에 탄성률이 없음만 확인하고 **밀도는 확인하지 않았다.** 이 배치가 그 자리를 메웠다. **네 층을 팠고 네 층이 같은 답을 준다.**

**층 1 — 규격 목차 네 판(1997 원판 · C · D · E)**
`density`·`gravity` 적중 **0**. §3.9.1 *Physical Requirements of Laminate Materials* 는 C/D/E 에서 여덟 항목으로 고정이다:
Peel Strength · Dimensional Stability · Flexural Strength · Flexural Strength at Elevated Temperature · Thermal Conductivity · CTE · Z-Axis CTE/Total Expansion · Fracture Toughness.
§3.8.4 *Dimensional* 은 Length/Width · Thickness · Bow and Twist 뿐이다. 1997 원판의 Table 1~10 도 cladding type · foil weight · 길이폭 허용차 · 시험빈도 · 두께허용차 · bow and twist · 샘플링뿐이다. **밀도가 들어갈 자리 자체가 없다.**

**층 2 — IPC 자신의 인증시험 보고서 (슬래시시트가 요구하는 물성을 전수로 나열한다)**
IPC Validation Services `TEST REPORT (Self-Tested Data)` 두 건 — Arlon 85HP(`IPC-4101/40`, `IPC-4101E/41` 인용) · Ventec Suzhou(`IPC-4101/41`, `IPC-4101D/41` 인용). 벤더도 개정판도 다른데 `SUMMARIZED TEST RESULTS` 항목이 **완전히 같다**:

```
Peel Strength · Volume Resistivity · Surface Resistivity · Moisture Absorption
Dielectric Breakdown · Permittivity @1MHz · Loss Tangent @1MHz · Flexural Strength
Arc Resistance · Thermal Stress · Electric Strength · Flammability
Glass Transition Temperature · Decomposition Temperature · Z-Axis CTE
Time to Delamination · Dimensional Stability · Solderability
Chemical Resistance · Metal Surface Cleanability · Pressure Cooker Test
```
두 보고서 전문 grep 에서 `densit|gravit` 적중 **0**.

**층 3 — 슬래시시트 요구표를 IPC 참조 문단번호까지 옮긴 벤더 시트 (결정적, 로컬에 있다)**
Technolam/Nan Ya 세 시트가 `Specification | Property | Test Method (IPC-TM-650) | Ref. Para.` 네 열 구조다. 번호 붙은 IPC 요구 행이 정확히 **18개**이고 각각 실제 Ref. Para.(3.9.1.1 · 3.11.1.3 · 3.9.1.7 …)를 갖는다. 그리고 밀도는 구분선 아래 **`19. Other`** 에만 나오고 — verbatim(/126):

```
Density (50 % resin content)  Dichte 50 % Harzgehalt  -  2,10  -  2,10  g/cm³  -  -
                                     규격값 = "-"        시험법 = "-"   Ref.Para. = "-"
```

**규격값도, IPC-TM-650 시험법도, 문단번호도 전부 `-` 다.** 같은 칸에 Young's Modulus 와 Specific Heat 가 나란히 있다 — 셋 다 **벤더가 덤으로 붙인 값**이지 IPC 요구가 아니다. /21(1,92) · /128(2,00) 도 같은 취급이다.

**층 4 — `IPC-TM-650 2.3.5` 는 실재하지만 IPC-4101 이 부르지 않는다**
`2.3.5 — Density, Insulating Material, Rev B, 8/97`(물치환법)은 실재한다. 그런데 그 문서 §2.0 이 `Applicable Document  None` 이고, **로컬 PCB 코퍼스 212개 PDF 와 네 판 목차 전부에서 `2.3.5` 적중 0** 이다. 시험법은 있는데 규격이 그것을 호출하지 않는다.

**남긴 한계를 정직하게 적는다.** IPC 가 유료로 파는 공식 슬래시시트 페이지 자체는 열지 못했다(shop.ipc.org 유료, ANSI 미리보기는 5.7 KB HTML 껍데기만 준다). 판정은 ①IPC 자신의 /40·/41 인증보고서 두 건과 ②문단번호가 붙은 /21·/126·/128 요구표 재현 세 건에 선다. **두 근거는 서로 독립인데 물성 집합이 정확히 일치하고 양쪽 다 밀도를 제외한다.**

### 결과 — **t2 로 닫힌 카드 0장. 밀도 빈칸은 오히려 늘었다.**

| | 밀도 빈칸 |
|---|---:|
| 70차 FA 가 남긴 것 | 19 |
| 71차 GD 가 세운 카드가 더한 것 (LAZ 13 + Resonac 20) | 33 |
| **합계** | **52** |

**그리고 이것이 이 판정의 값이다** — 밀도는 규격 층의 문제가 아니라 **벤더 TDS 층**의 문제다. 실제로 밀도를 찍는 시트는 IPC 가 아니라 `ASTM D792` 나 `Internal Method` 를 시험법으로 적는다. 로컬 코퍼스에서 확인했다:

- Nan Ya `NP-730`: `Density (Specific Gravity) | g/cm | 2.1 | 2.05~2.15 | ASTM D792`
- Shengyi `SCGA-500 GF255`: `Density | ASTM D792 | g/cm3 | 2.25`
- Park/Nelco `N4000-6`·`N4000-13`: `Density [50% resin content] … Internal Method`

---

## ① Sumitomo LAZ — **가장 확실했고 실제로 가장 많이 나왔다**

FA 가 「로컬에 있음」이라고 적은 것이 맞았다. 파일 셋을 전부 열었다.

| 파일 | 등급 | 카드 |
|---|---|---:|
| `SumitomoBakelite_LAZ-4785_PackageCore_Spec_ja_2026-09-09.html` | TH-G · GH-G · TH-B · GS-BA · GS-BE · GH-T · GS-W | **7** |
| `SumitomoBakelite_LAZ-6785_Prepreg_Spec_ja_2026-09-09.html` | **LAZ-2002**(하위등급 없음) · LAZ-6785 TT-R · GT-R · TS-FG · GS-FG | **5** |
| `SumitomoBakelite_LAZ-7752_SolderResistAlt_Spec_ja_2026-09-09.html` | VerJB | **1** |

**7752 는 FA 의 인계 목록에 없던 표적이다.** 같은 LαZ 계열 형제 페이지가 로컬에 있었고 서식이 같아 함께 담았다(솔더레지스트 대체재, `弾性率` 30 ℃ 15 GPa → 260 ℃ **2.6 GPa** — Tg 260 ℃ 를 넘어서며 강성이 6배 떨어지는 것이 그대로 보인다).

### 온도별 영률 26행 — `youngs_modulus` 에 `temperature_c` 로 넣었다

브리프가 지목한 대로 **`youngs_modulus_at_rate` 를 쓰지 않았다**(그건 율속 축이고 이것은 온도 축이다). `mechanical.youngs_modulus` + `conditions.temperature_c ∈ {30, 260}`, **30 ℃ 와 260 ℃ 는 두 행**이고 평균 0건이다.

| 등급 | 30 ℃ | 260 ℃ | 비 |
|---|---:|---:|---:|
| LAZ-4785 TH-G / TH-B | 32 GPa | 21 GPa | 0.66 |
| LAZ-4785 GH-G | 31 | 20 | 0.65 |
| LAZ-4785 GS-BA | 29 | 18 | 0.62 |
| LAZ-4785 GS-BE / GH-T / GS-W | 18 | 10 | 0.56 |
| LAZ-2002 / LAZ-6785 TT-R | 22 | 11 / 10 | 0.50 / 0.45 |
| LAZ-6785 GT-R | 21 | 9 | 0.43 |
| LAZ-6785 TS-FG | 18 | 10 | 0.56 |
| LAZ-6785 GS-FG | 17 | 9 | 0.53 |
| LAZ-7752 VerJB | 15 | **2.6** | 0.17 |

**리플로 피크(260 ℃) 강성이 직접 읽히는 표는 이 카탈로그에서 드물다.** 저CTE·고유리함량 코어일수록 유지율이 높고(0.66) SR 대체 필름은 0.17 까지 떨어진다 — 물리적으로 앞뒤가 맞는다.

### 등급은 **t3** 다 — 승격 판정을 다음 배치에 넘긴다

`弾性率` 행에 인장/굽힘 표기가 **전혀 없다.** 그런데 같은 표의 CTE 행은 `TMA(引張モード)` 로 모드를 박아 두고, 같은 벤더의 스미라이트 ELC 표(70차 FA 가 담은 6등급)는 `曲げ弾性率` 와 `引っ張り弾性率` 를 **행 이름으로** 가른다. **이 벤더는 적을 때는 적는다 — 여기서 안 적은 것은 누락이지 인장 확정이 아니다.** 세 페이지 전문에 시험규격 번호도 하나 없다(`JIS` 0회 · `ASTM` 0회 · `IPC` 0회).

70차 FA 가 MGC BT 13등급의 `ヤング率` 를 같은 사유로 t3 에 둔 선례를 따랐다. `conditions.test_mode = "unconfirmed"` · `grade_scope` 에 사유를 적었다 — **「값 자체는 이 등급의 이 온도에 인쇄된 것이고 등급 범위 문제는 없다. t3 로 내린 이유는 시험모드 미확정이다」**. 승온 측정이라는 사실이 DMA 를 시사하지만 **문서가 그것을 말하지 않으므로 그 추론으로 등급을 올리지 않았다.**

### 같은 표에서 조건이 확정된 나머지는 t1 로 들어갔다

`Tg(DMA)` 13행 · `CTE-1 xy/z (TMA 引張モード)` 17행 · `熱伝導率` 4행 · `Dk/Df(1 GHz)` 각 11행 · `ピール強度` 13행 · `吸水率(D-24/23)` 11행. CTE 는 행 이름에 모드가 박혀 있어 t1 이다 — **같은 표 안에서 영률만 t3 인 이유가 바로 이 대비다.**

---

## ③ Resonac — 총합표 세 쪽을 전부 담았다 (20등급)

FA 는 PDF 5쪽과 6쪽의 679FG 두 열만 담았다. 이 배치는 **PDF 6쪽의 남은 5열 + 7쪽 8열 + 8쪽 7열**을 담았다.

| 쪽 | 새로 담은 등급 |
|---|---|
| PDF 6 (인쇄 7) | GEA-705G · GEA-770G · MCL-HS200 · MCL-HS200(D) · MCL-HS100 |
| PDF 7 (인쇄 8) | MCL-HS100(D) · GH-200(D) · GH-100(D) · MCL-HD60 · MCL-HD90 · MCL-HD90(D) · MCF-200HS · MCF-770G(P) |
| PDF 8 (인쇄 9) | MCL-LW-990(RFD) · MCL-LW-910G · MCL-LW-900G · MCL-HE-679G(S) · AS-400HS · MCL-I-671 · TD-002 |

**밀도·포아송비·비열·인장강도는 세 쪽 어디에도 행이 없다.** FA 가 66쪽 전수 grep 으로 내린 판정을 세 쪽 렌더로 재확인했다 — 세 쪽 행 구성이 완전히 같고 Resonac 의 기계축은 `弾性率(引張/曲げモード)` 두 행뿐이며 **강도 행 자체가 없다.**

### 인쇄된 구간은 전부 두 행 — 평균 0건

Resonac 표는 값이 전부 구간(`17 - 19`)이라 `conditions.bound: "lower"/"upper"` 로 갈랐다. 460행 전부가 이 방식이다.

### 이 쪽들이 준 반례 하나 — **굽힘이 인장보다 낮은 등급이 있다**

형제 배치 `out_gb`(71차 GB)가 MGC BT 영률 승격을 판정하며 「인장이 굽힘보다 큰 사례 0건」을 근거의 하나로 쓰고 있다. **PDF 8쪽이 반례를 준다** — 렌더로 확인한 값이다:

| 등급 | 弾性率(引張モード) | 弾性率(曲げモード) |
|---|---|---|
| MCL-LW-990 (RFD) | **16 - 22** | 14 - 19 |
| MCL-LW-910G | **18 - 24** | 16 - 21 |
| MCL-LW-900G | **18 - 24** | 16 - 21 |
| TD-002 | **6 - 9** | 5 - 8 |
| (대조) MCL-HE-679G(S) | 17 - 23 | **23 - 26** |
| (대조) MCL-I-671 | 21 - 24 | **24 - 26** |

같은 표 안에서 방향이 갈린다. **「굽힘은 항상 인장보다 크다」는 전제는 이 벤더에서 성립하지 않는다** — GB 가 참고할 값이다.

---

## 열 밀림을 어떻게 확인했는가

**HTML 3장 (Sumitomo LAZ) — 렌더 대신 `<tr>`/`<td>` 직접 파싱.**
`html.parser` 로 `colspan`/`rowspan` 까지 읽어 셀 경계를 확정했다. 레이아웃 추측이 끼어들 자리가 없으므로 열 밀림 위험이 **원천적으로** 없다. 이 파싱이 실제로 값을 바꾼 자리가 둘 있다:

1. **프리프레그 표의 1열 소속.** 헤더가 `LAZ-` 아래 `2002`(rowspan=2)와 `6785`(colspan=4)로 갈린다. `rowspan=2` 때문에 **`2002` 열에는 하위등급 이름이 없다** — 텍스트만 읽으면 `TT-R` 이 2002 에 붙는다. 태그를 읽어야 `TT-R` 이 6785 의 첫 등급임이 확정된다.
2. **CTE-1 z 의 시험모드.** `TMA(引張モード)` 셀이 CTE-1 xy 행에 `rowspan=2` 로 걸려 **z 행까지 덮는다.** 태그로 확인하고 z 행에도 인장모드를 달았다.

**PDF 3쪽 (Resonac) — `pdftotext -layout` + 350 dpi 렌더 대조를 값을 옮긴 세 쪽 전부에 적용했다.** 각 쪽마다 ①표 머리 ②전기특성대 ③기계특성대 ④하단대(CTE z·熱伝導率·Slash sheet) 네 조각을 잘라 눈으로 대조했다.

| 쪽 | 렌더로 확정한 열 순서 | 대조 결과 |
|---|---|---|
| PDF 6 | `GEA-705G ǀ GEA-770G ǀ 679FG(R) ǀ 679FG(S) ǀ HS200 ǀ HS200(D) ǀ HS100` | **일치.** FA 가 보고한 순서를 이 배치가 독립으로 재확인했다 |
| PDF 7 | `MCL-HS100(D) ǀ GH-200(D) ǀ GH-100(D) ǀ MCL-HD60 ǀ MCL-HD90 ǀ MCL-HD90(D) ǀ MCF-200HS ǀ MCF-770G(P)` | **순서는 맞는데 텍스트가 두 줄로 쪼갠다** — 아래 참조 |
| PDF 8 | `MCL-LW-990(RFD) ǀ MCL-LW-910G ǀ MCL-LW-900G ǀ MCL-HE-679G(S) ǀ AS-400HS ǀ MCL-I-671 ǀ TD-002` | **행 하나가 실제로 밀렸다** — 아래 참조 |

### 렌더가 실제로 잡아낸 것

**PDF 7쪽 — 헤더가 세 줄로 흩어진다.** `pdftotext -layout` 출력이 이렇다:
```
        MCL-HS100                    MCL-HD60   MCL-HD90   MCL-HD90   MCF-200HS   MCF-770G
         (D タイプ)                                          (D タイプ)              (P タイプ)
  製품  特性  単位        GH-200    GH-100
                        (D タイプ) (D タイプ)
```
**이 텍스트만 읽으면 `MCL-HS100` 다음이 `MCL-HD60` 이고 `GH-200`·`GH-100` 은 뒤로 밀린다.** 350 dpi 렌더에서 실제 좌→우 순서가 `MCL-HS100(D) → GH-200(D) → GH-100(D) → MCL-HD60 …` 임을 확인했다(GH 두 열에는 `TYPE-F` 로고가 붙어 있어 그림으로만 보인다). 데이터 행의 값 개수(8개)가 이 순서와 맞는 것도 함께 확인했다.

**PDF 8쪽 — `CTE y` 행이 실제로 한 칸 밀렸다.** 텍스트 출력이 이렇다:
```
              CTE y
                                                                                    6 - 9*5      ← TD-002 값이 윗줄로 튄다
              (<Tg) (圧縮)
                          7 - 10   12 - 15   12 - 15   12 - 15   30 - 55   12 - 16   ← 6개뿐
```
텍스트 그대로 읽으면 **TD-002 의 CTE y 가 사라지고 나머지가 한 칸씩 당겨질 수 있다.** 렌더로 `7-10 ǀ 12-15 ǀ 12-15 ǀ 12-15 ǀ 30-55 ǀ **12-16** ǀ 6-9*5` 를 확정했다 — 그리고 이 행에서 `MCL-I-671` 만 CTE x(12-15)와 CTE y(12-16)가 **다르다.** 렌더 없이는 이 한 자리를 못 잡는다. 사유를 해당 행 notes 에 박았다.

### 각주는 쪽마다 다시 읽었다

표 하단 각주 verbatim: **`*1: 空洞共振器; *2: RT箔; *3: HVLP箔, *4: 0.8 mmt; *5: 引張`**

- **`*4`(0.8 mmt)는 `弾性率(曲げモード)` 와 `CTE z` 행에만** 붙는다. `弾性率(引張モード)` 에는 각주 번호가 없다 → 인장탄성률의 시편 두께는 표 맨 위 `厚み` 다(열마다 0.025 / 0.1 / 0.2 / 0.4 / 0.8 mm 로 **다르다**). 굽힘은 전부 0.8 mm 로 박았다.
- **`*5`(引張)와 행 이름 `(圧縮)` 가 충돌한다.** 각주가 **칸 단위**로 걸린다는 것이 증거다 — PDF 7쪽은 CTE x/y 여덟 칸 전부에 `*5` 가 붙고, PDF 6쪽은 다섯 칸에만(679FG 두 칸에는 없다), PDF 8쪽은 TD-002 한 칸에만 붙는다. 행 전체가 引張이면 행 이름을 바꿨을 것이다. **각주를 따랐고 원문 표기 충돌 사실을 해당 행 notes 에 verbatim 으로 남겼다.**
- **`*2`(RT箔)·`*3`(HVLP箔)는 PDF 8쪽의 `ピール強度(18μm)` 칸에만** 붙고 등급마다 다르다(LW-990·LW-910G 는 `*3`, LW-900G·HE-679G·AS-400HS 는 `*2`, MCL-I-671·TD-002 는 각주 없음). `conditions.copper_foil_type` 에 갈라 넣었다.
- **`*1`(空洞共振器)은 PDF 8쪽 Dk/Df 칸에만** 붙는다. 표 좌측 묶음 이름이 `電気特性(SPDR)` 이므로 각주 없는 칸은 SPDR, 붙은 칸은 공동공진기로 갈랐다. **같은 쪽 안에서 `MCL-I-671` 의 Dk(1GHz)·Df(1GHz) 만 `*1` 이 없다** — 그 두 칸만 SPDR 이다.

---

## 그 밖의 규율 점검

- **t4 는 0건이다.** 추정·계산으로 만든 값이 하나도 없다. 등급 분포는 **t1 540행 · t3 26행**.
- **역산 0건.** `樹脂比重` 을 밀도로 만들지 않았다(④ 판정 참조).
- **인쇄된 구간은 두 행.** Resonac 460행 전부 `bound: lower/upper`. **평균 0건.**
- **같은 물성의 다른 측정법도 두 행.** Tg 는 TMA/DMA 를 갈랐고(Resonac 81행), CTE 는 축(x/y/z)·구간(<Tg/>Tg)·모드(圧縮/引張)로 갈랐다(157행).
- **`N.D.`·`－` 는 비웠다.** LAZ 표의 `N.D.` 12칸(GH-T·GS-W 의 CTE z·Dk·Df·吸水率·熱伝導率, GS-BE 의 CTE z·熱伝導率)과 Resonac 의 `－` 칸에 값을 만들지 않았다.
- **환산 검산을 566행 notes 전부에 넣었다.** 예: `32 GPa x 1e9 = 3.2e+10 Pa; 되돌리면 3.2e+10/1e9 = 32`, `255 + 273.15 = 528.15 K`, `14 ppm/℃ x 1e-6 = 1.4e-05 1/K`, `0.7 kN/m x 1000 = 700 N/m`, `0.4 % / 100 = 0.004`.
- **`attributes.role` 을 33장 전부에 넣었다**(`product`, `role_reason`·`role_confidence` 포함). 격자가 조용히 product 로 세는 사고를 막는다.
- **이름 최장 55자** — 200자 제한에 여유가 크다.
- **별칭이 형제 카드와 겹치지 않게 만들었다.** LAZ-4785 7장이 다 `LAZ-4785` 를 물면 매칭이 모호해지므로 등급이 붙은 꼴만 넣었다. Resonac 도 `MCL-HS200` 과 `MCL-HS200(D)` 가 서로를 안 물게 갈랐다.
- **라이브 DB 는 읽기 전용으로만 썼다** (중복 확인 · 물성정의 단위 대조 · 밀도 보유 등급 조회). **쓰기 0건.**
- **중복 확인 — 적중 0.** `LAZ`·`LαZ`·`4785`·`6785`·`7752`·`MCL-HS`·`MCL-HD`·`MCL-LW`·`MCL-HE`·`GEA-`·`GH-200`·`GH-100`·`MCF-200HS`·`MCF-770G`·`AS-400`·`MCL-I-671`·`TD-002` 로 `name`·`description` 을 훑었다. `LAZ` 12건이 걸렸지만 전부 **polysilazane**(재료 695~700 등)이라 무관하다.
- **동시 배치와 겹치지 않는다 — 확인했다.** `out_ga`(솔더) · `out_gb`(MGC BT 영률 승격 판정) · `out_gc`(유리·페라이트) 산출물을 등급 토큰으로 훑었다. `out_gb` 가 `MCL-E-705G` 를 한 번 언급하지만 **근거로 인용한 것**이고 카드를 건드리지 않는다. 브리프 지시대로 **MGC BT 영률은 한 행도 건드리지 않았다.**

---

## 못 넣은 것 — 셋으로 갈라 적는다

### (가) 표에 열이 없었다 (문서를 열었고 열 부재를 확인)

| 표적 | 연 문서 | 확인한 부재 |
|---|---|---|
| **LAZ 13등급 — 밀도·포아송비·비열·인장강도 (52칸)** | HTML 3장 전수 | 토큰 검사 — `比重` 0 · `ポアソン` 0 · `ポアッソン` 0 · `比熱` 0 · `引張強さ` 0. `密度` 는 적중하지만 전부 산문(`高密度パッケージ基板材料`·`高密度実装化`)이다 |
| **Resonac 20등급 — 밀도·포아송비·비열·인장강도 (80칸)** | PDF 6·7·8쪽 렌더 전수 | 세 쪽 행 구성이 완전히 같고 네 물성 행이 없다. Resonac 의 기계축은 `弾性率` 두 행뿐이다 |
| **MGC EL190T·EL230T — 밀도 (2칸)** | `fr4.html` 일본어·**영문** 두 판 | 두 판 다 적층판 밀도 행이 없다. 있는 것은 `樹脂比重`/`Specific Gravity of Resin`(무차원, 1.44/1.42) |
| **Resonac 여러 등급 — Tg(TMA)** | PDF 7·8쪽 | MCL-HD60·HD90·HD90(D)·MCF-200HS·MCF-770G(P)·AS-400HS 여섯 열이 `－` 다(Tg(DMA)만 있다) |
| **Resonac 여러 등급 — CTE z** | PDF 7쪽 | MCL-HD60 이후 다섯 열이 `－` 다 |
| **Resonac 전 등급 — CTE z (DIC)** | PDF 6·7·8쪽 | 세 쪽 21열 전부 `－` 다 |
| **Resonac 5등급 — 熱伝導率** | PDF 6·7·8쪽 | GEA-705G · GH-100(D) 이후 · AS-400HS · TD-002 가 `－` 다 |
| **LAZ GH-T·GS-W — Dk/Df/吸水率/熱伝導率/CTE z** | LAZ-4785 표 | 원문이 `N.D.` 로 인쇄한 칸이다(형제 등급에는 값이 있다) |

### (나) 문서를 못 열었다

- **IPC-4101 공식 슬래시시트 원본 (모든 시트)** — `shop.ipc.org` 유료. `https://webstore.ansi.org/preview-pages/IPC/preview_IPC+4101E-2017.pdf` 는 5.7 KB HTML 껍데기만 준다. **대신 IPC 자신의 인증시험 보고서 두 건과 문단번호 붙은 요구표 재현 세 건으로 우회했고 그 사실을 판정에 적었다.**
- **`https://www.raypcb.com/ipc-4101/`** — TLS 오류(`unable to verify the first certificate`).
- **MGC 상하이 `mgc-sh.com`** — HTTPS ECONNREFUSED / HTTP 403.

### (다) 등급이 안 맞았다

**이 배치가 스스로 만든 다음 표적뿐이다.**

- **Resonac 개별 제품 쪽 (PDF 9~41쪽)** — `弾性率` 행이 있으나 **총합표와 같은 등급을 다시 찍는 쪽**이 대부분이다. 새 등급이 아니라 같은 등급의 상세 조건(시편·처리)이 붙을 수 있다. 총합표 세 쪽을 다 담았으므로 등급 확장은 여기서 끝이다.
- **Sumitomo LαZ 빌드업 재료 (`/product/it-materials/package/buildup/`)** — 세 페이지의 네비게이션이 네 번째 형제 페이지를 건다. **로컬에 없다.**
- **URL 을 확정하지 못한 문서 4개** — 지어내지 않고 `url: null` + `url_note` 로 남겼다(FA·EB 의 선례). LAZ 3장은 `og:url`·canonical 이 없고 살아 있는 절대 URL 이 구글 태그매니저와 사이트검색뿐이다. 다만 **네비게이션이 형제 페이지만 걸고 자기 자신은 안 거는 구조라 사이트 내 상대 경로는 확정된다** — `/product/it-materials/package/{core,prepreg,sr}/` 를 `url_note` 에 적었다(도메인은 지어내지 않았다).

---

## 다음 배치에 넘길 것

### 1. **밀도는 규격이 아니라 벤더 TDS 에서 온다 — 로컬에 이미 재료가 있다**

②의 판정이 밀도의 방향을 바꿨다. 라이브 DB 이름 조회로 **밀도를 찍는 로컬 시트 중 아직 카드가 없는 것**을 골라 뒀다:

| 문서 | 등급 | 인쇄된 밀도 |
|---|---|---|
| `Technolam_NanYa_NPG-150N-NPG-150NB_Datasheet_2019-02.pdf` | NPG-150N / NB | `2,00 g/cm³` (50 % resin content) |
| `Technolam_NanYa_UV-Block-FR-4-86_Datasheet_2019-02.pdf` | UV Block FR-4-86 | `1,92 g/cm³` |
| `Technolam_NanYa_NPG-170TL-NPG-170R-NPG-170B_…` · `NPG-170DTL/DR/DB` · `NPG-180BH/BHB` | 8등급 | 같은 서식 |
| `Nanya_CCL_NP-730_…pdf` · `NP-822` · `NP-826` | 3등급 | `Density (Specific Gravity) ǀ g/cm ǀ 2.1 ǀ 2.05~2.15 ǀ ASTM D792` |
| `Shengyi_SCGA-500_GF255_TDS_zh_2019.pdf` | SCGA-500 | `Density ǀ ASTM D792 ǀ g/cm3 ǀ 2.25` |
| `Rogers_RO3000_Laminate_DataSheet_…pdf` | RO3006 | 형제 RO3003 은 이미 DB 에 있다 |

**반대로 이미 닫힌 것도 적어 둔다** — NP-175FR/FTL(2440·2441) · Panasonic R-1755 계열(2436·2437·2519·2520) · Rogers RO4003C/RO4350B/RO3003/RO4835/CLTE 계열은 **이미 밀도가 들어 있다**(각 1~3행). 중복 수집하지 마라.
**주의** — `Density (50 % resin content)` 는 수지함량 조건이 붙은 값이다. `conditions` 에 반드시 박아라. `2.05~2.15` 같은 구간은 두 행이다.

### 2. **영률 t3 두 무더기를 한 번에 판정할 수 있다**

- **MGC BT 13등급 13칸** — 70차 FA 가 남겼고 71차 GB 가 지금 판정 중이다.
- **Sumitomo LαZ 13등급 26칸** — 이 배치가 남긴다. 사유가 다르다(MGC 는 「굽힘 행과 숫자가 같다」, LAZ 는 「모드 표기가 아예 없다」)므로 **같은 결론이 나올 필요는 없다.** 근거는 각 행 `grade_scope`·`notes` 에 다 들어 있고 새 문서는 필요 없다.
- **GB 에게 전할 것** — 이 배치가 PDF 8쪽에서 **굽힘 < 인장인 등급 넷**(MCL-LW-990·LW-910G·LW-900G·TD-002)을 렌더로 확인했다. 「굽힘은 항상 인장보다 크다」는 전제가 Resonac 에서 성립하지 않는다.

### 3. **Sumitomo LαZ 빌드업 페이지 한 장이 남았다**

세 페이지의 네비게이션이 `/product/it-materials/package/buildup/` 를 건다. 같은 서식이면 **온도별 영률이 또 나온다.** 로컬에 없으므로 받아야 한다.

### 4. 검색·전사 규율 (이 배치가 확인한 것)

- **`pdftotext -layout` 이 헤더를 여러 줄로 흩는 방식이 쪽마다 다르다.** PDF 6쪽은 두 줄, 7쪽은 세 줄, 8쪽은 한 줄이다. **줄 수를 보고 안심하지 마라** — 7쪽은 순서가 맞았고 8쪽은 데이터 행 하나가 실제로 밀렸다. 헤더만이 아니라 **값 개수가 열 수와 맞는지**를 행마다 세어라.
- **HTML 의 `rowspan` 은 값이 아니라 소속을 바꾼다.** LAZ 프리프레그 표에서 `2002`(rowspan=2) 때문에 그 열에만 하위등급 이름이 없다 — 텍스트로 읽으면 첫 등급이 엉뚱한 제품에 붙는다. `colspan`/`rowspan` 을 안 읽으면 파싱해도 밀린다.
- **벤더 각주가 행 이름과 충돌할 수 있다.** Resonac CTE 는 행 이름이 `(圧縮)` 인데 칸 각주가 `*5: 引張` 다. **각주가 칸마다 다르게 걸리면 각주가 칸 단위**라는 증거이고 각주가 이긴다. 충돌 사실은 지우지 말고 notes 에 남겨라.
- **`密度` 적중을 밀도 행으로 오해하지 마라.** LαZ 세 페이지 전부 `密度` 가 적중하지만 전부 제품군 이름(`高密度パッケージ基板材料`)이다. Resonac 도 같았다(70차 FA). **적중 위치가 표 안인지 산문인지부터 봐라.**
- **규격이 안 규정하는 물성을 규격에서 찾지 마라.** 밀도는 IPC-4101 의 요구 목록에 없고, 벤더 시트가 그것을 적을 때는 `19. Other` 칸에 `Ref. Para. = -` 로 적는다. **`Ref. Para.` 열이 있는 벤더 시트는 규격 요구와 벤더 덤을 스스로 갈라 준다** — 그 열을 먼저 봐라.

---

## 산출물

- `out_gd/gd71_01_sumitomo_laz.json` — **재료 13장 · 물성 106행** (t1 80 · t3 26)
- `out_gd/gd71_02_resonac_mcl.json` — **재료 20장 · 물성 460행** (t1 460)
- `out_gd/gd71_09_verdicts.json` — **판정 6건** (IPC-4101 밀도 부재 · MGC FR-4 밀도 부재 · LAZ 코어4 부재 · Resonac 코어4 부재 · LAZ 영률 모드 미확정 · Resonac CTE 각주 충돌)
- `out_gd/gd71_gen.py` — 생성기 + 자체검증(단위 대조 · 이름 200자 · 이름 중복 · `role`/`aliases` 필수 · t3 `grade_scope` 필수 · **t4 금지** · notes 필수). **오류 0.**
- **새로 받은 문서 0건.** 값의 출처는 전부 로컬 원문 4개다:
  - `pcb/SumitomoBakelite_LAZ-4785_PackageCore_Spec_ja_2026-09-09.html` (7등급)
  - `pcb/SumitomoBakelite_LAZ-6785_Prepreg_Spec_ja_2026-09-09.html` (5등급)
  - `pcb/SumitomoBakelite_LAZ-7752_SolderResistAlt_Spec_ja_2026-09-09.html` (1등급)
  - `pcb/Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf` PDF 6·7·8쪽 (20등급)
- 네트워크는 **판정 두 건(②·④)에만** 썼다 — 값을 만들지 않았고 카드에 들어간 값 중 웹에서 온 것은 0건이다.
