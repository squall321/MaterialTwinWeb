# 70차 FD — Prony 항 수집

**한 줄** — EC 가 지목한 격자 밖 표적 다섯 건은 **하나도 Prony 항을 인쇄하지 않는다**(디지타이즈해도 넣을 칸이 없다).
대신 **코퍼스에 아직 아무도 안 캔 Prony 표가 남아 있었다** — 논문 4편에서 **211행**, 여기에 Chowdhury 2019 의 미채굴분 **78행**을
더해 **289행 · 재료 5종 · 새 Prony 세트 8벌**을 준비했다. **디지타이즈는 한 건도 하지 않았다.**

> 라이브 DB 는 읽기 전용으로만 열었다. 적재는 하지 않았다 — `out_fd/fd70_*.json` 이 결과물이다.
> `out_fd/` 는 **44차 FB/FA/FC 배치가 이미 쓰던 디렉터리**였다(`fd01_fb_substrate_optical_glass.json` 등 3건).
> 파일명이 겹치지 않게 이번 산출물은 전부 `fd70_` 접두어를 붙였다.

---

## 1. 표적별 결과

| 표적 | 표였나 그림이었나 | 결과 |
|---|---|---|
| **Chowdhury 2019** (재료 738) | **표** — Table 2·4·5·6·7 | **78행** — Table 2(DMA 7쌍)·Table 6/7(완화 17쌍) 전량 + WLF 3세트 |
| Chen 2012 (재료 1301, LED 실리콘) | **그림뿐** | ✗ **원문이 Prony 항을 인쇄하지 않는다** |
| Watanabe 2018 (재료 1430, E-67) | **그림뿐** | ✗ Prony 항 미인쇄 + **귀속 문제**(Fig.5 는 프리프레그 시편이다) |
| Sadeghinia 2012 (재료 743, EMC) | **그림뿐** | ✗ 원문이 *"A Prony series **could** be fitted"* — **안 했다** |
| Chopin 2018 (재료 741·742, PSA) | **그림뿐** | ✗ Prony 자체가 없다 — G(t) 를 멱함수 t^-0.23 로 근사한다 |
| Fuensanta 2019 (재료 592~596·1175) | 표는 있으나 Prony 아님 | ✗ Prony 없음. **Table 9 의 G′ 10칸은 53차 OB 가 이미 다 넣었다** |
| **(추가) Chiu 2015** EMC | **표** — Table 1·2·3 | **82행** — 체적 17항 + 전단 21항 + κg·μg + WLF 2분기 |
| **(추가) Chae 2010** EMC | **표** — Table I·II | **82행** — 인장 21항(T_ref 110 °C) + 18항(T_ref 120 °C) + E∞ 2개 + WLF |
| **(추가) Park 2011** UF-B | **표** — Table 1 | **27행** — 인장 13항 + E∞ |
| **(추가) Raghavan 2011** PSR | **표** — Table I | **20행** — 정규화 전단 10항 |

**합계 289행 · 재료 5종(기존 1 · 신규 4) · Prony 세트 8벌.** 산출 JSON 은 적재기 규칙과 무결성검사
(`Prony 항에 항번호 없음`·`Prony 가중치·완화시간 항수 불일치`·단위·범위·조건충돌·notes 존재)로
`validate_fd.py` 에 걸어 **위반 0** 을 확인했다. 라이브 DB 를 쓰지 않는 읽기 전용 검증기다.

---

## 2. Chowdhury 2019 에서 몇 쌍을 옮겼는가 — **EC 의 지시가 절반 틀렸다**

EC 는 *"table-5.md 에 13쌍이 이미 뽑혀 있다 · 디지타이즈가 필요 없는 최고가치 한 건"* 이라고 넘겼다.
**열어 보니 그 13쌍은 이미 DB 에 있었다.** 52차 NA·53차 OB 가 이 논문을 채굴해 재료 738 에 **53행**을 넣어 뒀다 —
Table 4 전단 7쌍(14행) · Table 5 전단·체적 13쌍(39행) · 포아송비 · WLF 1벌. **EC 는 재료 617 을 표적으로 적었지만
실제 값은 738 에 붙어 있어서 격자에 안 잡혔다.**

남아 있던 것은 이것이다.

| 표 | 무엇 | 이번에 넣은 행 |
|---|---|---:|
| **Table 2** | **DMA** 마스터커브 7쌍 (전단 α·τ + 체적 α) | 21 |
| **Table 6/7** | **응력완화** 17쌍 (전단 α·τ + 체적 α) — 저자가 권장하는 세트 | 51 |
| Table 4·5·6/7 | 각 세트에 딸린 WLF 상수 3벌 (C1·C2) | 6 |
| | | **78** |

**검산** — Table 2 의 α 합 0.9144, Table 6/7 의 α 합 0.6243 으로 둘 다 1 이하다.
Table 6/7 은 **PDF 10쪽을 240 dpi 로 그려 17항 전부를 눈으로 대조**했다(`chow_t6b-10.png`·`chow_t6c-10.png`).

**넣지 않은 것 둘.**
- **Table 4 의 체적 열** — 53차 OB 가 *"α2 가 전단 3.27e-2 인데 체적은 3.27e-1 이라 한쪽이 오식이므로 체적 열 전체를 유보한다"* 고
  적어 뒀다. **그 판단이 맞다**(PDF 원문 대조 완료 — 정말 그렇게 인쇄돼 있다). 그대로 유보한다.
- **Table 1·3 의 이동인자표**(a_T, 100~140 °C) — **DB 에 이동인자 키가 없다.**

**WLF 3벌은 넣되 못을 박았다.** Table 4/5/6·7 의 상수는 전부 **음수**이고(C1 ≈ -12.2~-13.7, C2 ≈ -44~-54),
52차 NA 가 같은 논문 Table 1·2 로 확정한 규약 `log10 a_T = -C1(T-T0)/(C2+T-T0)` 에 넣으면
원문 Table 3 의 인쇄값(100/110/130/140 °C 에서 2.7 / 1.7 / -1.0 / -1.5)을 **재현하지 못한다** —
예컨대 17쌍 세트는 +3.79 / +2.24 / -3.54 / -9.99 가 나온다. 부호를 뒤집어도 안 맞는다.
값·검산결과·"이 상수로 마스터커브를 옮기지 마라"를 `conditions.checksum_vs_printed_shift_factors = FAILED` ·
`usable_for_shifting = false` 와 notes 에 적어 넣었다. **브리프 §2 의 "WLF 상수가 원문에 있으면 반드시 같이 넣어라"를 따르되
쓸 수 없다는 사실을 값과 함께 실었다.**

---

## 3. 디지타이즈 — **한 건도 하지 않았다. `--logx` 를 쓸 일이 없었다**

브리프가 `digitize_curve.py` 의 `--logx` 버그 수정을 알려 줬지만 **이번 파동에는 디지타이즈할 표적이 없었다.**
격자 밖 표적 다섯 건의 그림을 전부 열어 봤고, 결론은 **그림의 질이 아니라 담을 칸이 없다**는 것이다.

| 그림 | 무엇이 그려져 있나 | 버린 이유 |
|---|---|---|
| Chen 2012 `Fig. 4` | 저장탄성률 마스터커브에 6개 Maxwell 요소를 맞춘 그림 | **항 값이 인쇄되지 않는다.** 곡선을 디지타이즈해도 나오는 것은 E(t) 이지 Prony 항이 아니다. 6항으로 되맞추는 것은 디지타이즈가 아니라 **모델 선택**이다(EC 가 Baek 2008 에서 내린 것과 같은 판단). WLF C1=22.7·C2=281.5(T_ref 283 K)는 **이미 DB 에 있다** |
| Watanabe 2018 `Fig. 5` | 414 K 기준 완화계수 마스터커브 | 두 겹으로 막힌다 — ① Prony 항 미인쇄 ② **본문이 *"Materials constants and shift factors were determined by DMA using the **pre-preg**"* 라 이 곡선의 시료는 프리프레그(수지+유리포)다.** 재료 1430 은 **순수 E-67 수지**라 옮기면 §140 위반이다. 게다가 y 축이 완화계수(Pa)인데 **시간축 완화계수 키가 DB 에 없다** |
| Sadeghinia 2012 `Fig. 9~11` | 경화도별 전단완화 마스터커브 7개 + 정규화 마스터커브 | 원문이 *"A Prony series **could** be fitted to the normalized mastercurves"* 라고만 쓴다 — **저자가 안 했다.** Fig. 11 의 정규화 곡선은 `relaxation_modulus_normalized` 키 표적인데 **그 키가 아직 없다.** WLF·Arrhenius 상수는 이미 DB 에 있다 |
| Chopin 2018 `Fig. 2(e)` | b_T·G(t) 전단완화 마스터커브 | **Prony 가 아예 없는 논문이다** — 본문이 *"roughly approximated by a power law G ~ t^-β with β = 0.23"* 로 끝낸다. 게다가 y 축은 **수직이동인자로 재조정된** b_T·G′ 라 raw G′ 가 아니다(b_T ≈ 1 ± 10 %). WLF C1·C2 는 이미 DB 에 있다 |
| Fuensanta 2019 `Figure 14` | 25 °C 4 decade G′·G″ 마스터커브 | Prony 없음. **표 9 의 0.1·100 rad/s G′ 10칸은 53차 OB 가 이미 `mechanical.shear_modulus` 로 다 넣었다**(재료 592~596). 그림을 캐도 같은 곡선의 중간점이 늘 뿐이고 tier3 다 |

**대신 PDF 페이지를 그려 눈으로 읽는 일은 세 번 했다** — 디지타이즈가 아니라 **표 판독**이다.
docling 과 pdftotext 가 **마이너스 부호와 곱셈기호를 잃는다**는 것을 확인했고, 그 표는 전부 이미지로 검증했다.

- `park2011_t1-4.png` — Park 2011 Table 1. docling·pdftotext 는 `log ρ` 1~5 의 마이너스와 **E10·E11·E13 의 음수 부호를 통째로 잃는다.**
  실제 인쇄값은 `-0.22 / -0.29 / -0.08 MPa` 다.
- `chae_t1-5.png` · `chae_t1c-5.png` · `chae_t2-6.png` · `chae_t2b-6.png` — Chae 2010 Table I·II.
  pdftotext 가 곱셈기호 `×` 를 **숫자 9 로** 읽고(`1.6 9 10 8`) 지수 부호를 지운다. 이미지로 39항을 전부 다시 읽었다.
- `chow_t6b-10.png` · `chow_t6c-10.png` — Chowdhury Table 6 의 17항과 WLF.

---

## 4. 새로 캔 네 편 — 무엇을 넣었고 무엇으로 검산했나

### Chiu 2015 (신규 재료 · `fd70_02`) — **이번 파동 최대 수확**
`Development of a Consistent Multiaxial Viscoelastic Model for Package Warpage Simulation` (ECTC 2015).
상용 EMC(퓨즈드 실리카 70 wt%, Tg 120 °C)를 인장 DMA + 비틀림 DMA + TMA 로 재고
**체적 17항(Table 1)과 전단 21항(Table 2)을 따로** 인쇄한다. 항수가 다른 것은 오기가 아니라
Laplace-Carson 영역에서 두 물성을 따로 만든 절차의 결과다 — 조건과 notes 에 적었다.

- 검산 — 체적 Σw = 0.96234, 전단 Σw = 0.98164, 둘 다 1 이하.
- 유리상 계수도 표 우하단에 인쇄돼 있다 — `κg = 14 GPa` → `mechanical.bulk_modulus`,
  `μg = 4.8 GPa` → `mechanical.shear_modulus`. **이 둘이 있어야 정규화 급수가 쓸 수 있는 값이 된다.**
- **WLF 가 두 벌이다**(Table 3) — T_ref 120 °C 공유, 120 °C **위** (41.6, 148.6) · **아래** (210, 1625).
  `conditions.branch` 로 갈랐다. 하나로 합치면 안 된다.

### Chae 2010 (신규 재료 · `fd70_05`)
`Characterization of the Viscoelasticity of Molding Compounds in the Time Domain` (JEM 39(4), doi 10.1007/s11664-010-1078-7).
87 wt% 충전 EMC 를 **두 가지 방식**으로 적합한 세트가 둘 다 인쇄돼 있다 —
Approach I(마스터커브 먼저, T_ref 110 °C, 21항) · Approach II(ANSYS 가 Prony·WLF 동시적합, T_ref 120 °C, 18항).

- **교차검산이 아름답다** — 순간계수 E(0) = E∞ + ΣEk 가 Approach I 20,856 MPa · Approach II 20,939 MPa 로
  **0.40 % 차이**다. 서로 다른 절차로 뽑은 두 세트가 같은 유리상 탄성률로 수렴한다.
- **WLF 는 저자가 스스로 부정한 값이다** — C1 = 2.01e11, C2 = 1.51e12(T_ref 120 °C).
  본문 verbatim: *"These large numbers resulted in an almost linear result … the WLF equation alone could not
  describe this material's temperature-dependent behavior properly."* 인쇄값이라 tier1 로 남기되
  `usable_for_shifting = false` · `authors_own_verdict` 를 조건에 박았다.

### Park 2011 (신규 재료 UF-B · `fd70_04`)
`Thermal fracture toughness measurement for underfill during temperature change` (Microelectronics Reliability 51).
상용 언더필 UF-B(Tg 100 °C)의 **인장완화 13항 + E∞ = 91.6 MPa**, T_ref = Tg = 100 °C.

- 검산 — E(0) = 91.6 + 11,495.94 = **11,587.5 MPa ≈ 11.6 GPa** 로 실리카 충전 언더필의 유리상 대역과 맞는다.
- **E10·E11·E13 이 음수다**(-0.22 / -0.29 / -0.08 MPa). 제약 없는 적합의 산물이고 **원문에 그렇게 인쇄돼 있다** — 그대로 넣었다.
- 이동함수는 WLF 도 Arrhenius 도 아니다. 마스터커브가 Tg 위아래를 다 담아 선형성이 깨져
  저자가 s = 1/T − 1/T_M 에 대한 **5차 다항식**을 썼다. A1~A5 가 인쇄돼 있지만
  **PDF 텍스트에서 곱셈기호·부호가 뭉개져 확정하지 못했고, 우리 DB 에 다항 이동함수 키가 없어 넣지 않았다.**

### Raghavan 2011 (신규 재료 PSR · `fd70_03`)
`Methodology to Predict Substrate Warpage …` (IEEE T-CPMT 1(7)).
솔더레지스트(PSR) 유전체의 **정규화 전단 Prony 10항**, T_ref = 110 °C.

- 검산 — Σg = 0.98 ≤ 1, g∞ = 0.02.
- **G0 가 인쇄되지 않는다.** 원문 식이 `G(t) = G0·g(t)` 라 이 급수만으로는 차원이 없다 — 조건에 `normalisation` 으로 밝혔다.
- WLF **식은 쓰지만 C1·C2 수치는 인쇄하지 않는다**(Fig. 3 그림뿐). 넣지 않았다.
- **DB 의 재료 204(Taiyo PSR-4000 계열)에 붙이지 않았다.** Raghavan 의 PSR 은 제조사·등급 미기재이고
  공정만 특정된다(UV 40 mW/cm² 5~7분 + 170 °C 30분). 다른 제품에 붙이면 §140 위반이다 — 신규 재료로 뺐다.

---

## 5. EC 의 "천장은 13종" 예측이 맞았는가 — **전제가 틀려서 숫자도 틀렸다**

EC 는 *"디지타이즈로 캘 수 있는 천장은 한 자릿수 % · 격자 밖 표적 T3~T7 + Chowdhury 표를 다 하면 13종"* 이라고 적었다.

**두 갈래로 틀렸다.**

1. **위쪽으로 틀렸다** — T3~T7 다섯 건은 **하나도 못 넣는다**(0종). Prony 항을 인쇄한 논문이 하나도 없다.
   EC 는 "그림 적중"으로 표적을 골랐는데, 점탄성 그림이 있다는 것과 **Prony 항이 인쇄돼 있다**는 것은 다른 조건이다.
   Chowdhury 도 EC 가 몰랐던 절반(Table 2·6/7)만 남아 있었고 나머지는 이미 채굴돼 있었다.
2. **아래쪽으로도 틀렸다** — 천장을 정하는 것은 **디지타이즈 능력이 아니라 "인쇄된 Prony 표를 아무도 안 훑었다"는 사실**이다.
   코퍼스에서 `prony` 를 전수로 걸어 **문서 61건**을 찾았고(`prony_docs.txt`·`prony_corpus_survey.md`),
   그중 **Prony 표가 실제로 있고 DB 에 없는 것이 최소 8편**이다. 이번에 4편만 처리했다.
   **디지타이즈 없이, 표를 옮기는 것만으로 이번 파동에서 재료 4종이 새로 섰다.**

**정정된 판단** — Prony 격자의 병목은 "그림이라 못 읽는다"도 "출처가 벤더시트다"도 아니다.
**우리가 가진 논문 중 Prony 표를 인쇄한 것을 전수로 훑지 않았다는 것**이다. 그 작업은 디지타이즈가 아니라 표 전사이고,
비용은 편당 30분이며 값은 tier1 이다.

---

## 6. 못 넣은 것 — 셋 구분

### (a) 문서에 없었다 — 5건
Chen 2012 · Watanabe 2018 · Sadeghinia 2012 · Chopin 2018 · Fuensanta 2019. 위 §3 표 참조.
**다섯 건 다 열었고, 다섯 건 다 Prony 항을 인쇄하지 않는다.**

### (b) 문서를 못 열었다 — **0건**
이번 파동의 모든 표적 PDF·마크다운이 로컬에 있었고 전부 열렸다.

### (c) 키가 없었다 — **4종류. 이번 파동에서 실제로 값이 막혔다**

| 없는 키 | 막힌 값 | 어디에 있나 |
|---|---|---|
| `mechanical.relaxation_modulus_normalized` (무차원, 축 `time_s`·`temperature_k`·`mode`) | EC 의 Baek 2008 30점 · Sadeghinia Fig.11 정규화 마스터커브 · Raghavan Fig.2 | **브리프가 "내가 이 파동에서 만든다"고 했는데 DB 에 아직 없다**(70차 FD 확인) |
| **시간축 완화계수** `E(t)`/`G(t)` (Pa, 축 `reduced_time_s`) | Watanabe Fig.5 · Chen 2012 Fig.4 · Sadeghinia Fig.9·10 · Chae Fig.2 | Prony 항이 아니라 **곡선 그 자체**를 담을 칸이 없다 |
| **이동인자** `a_T` (무차원, 축 `temperature_k`·`reference_temperature_k`) | **Chowdhury Table 1(9온도)·Table 3(5온도)** · Raghavan Fig.3 · Sadeghinia Fig.12·13 | WLF 상수가 못 쓰는 값일 때 **원문 이동인자표가 유일하게 쓸 수 있는 것인데 넣을 데가 없다** |
| **다항·Arrhenius 이동함수 계수** | Park 2011 A1~A5(5차) · Chae Approach I · Watanabe Arrhenius Q=349 kJ/mol | Park·Chae 는 **WLF 를 쓰지 않는다** — WLF 키만 있으면 이 재료들의 이동함수는 영영 못 들어간다 |

---

## 7. 다음 배치에 넘길 것

1. **`mechanical.relaxation_modulus_normalized` 를 실제로 만들어라.** EC 가 넘겼고 브리프가 약속했는데 아직 없다.
   대기 중인 값 — `out_ec/ec_baek2008_relaxation.csv` 30점(좌표까지 다 뽑혀 있다) · Sadeghinia Fig.11.
2. **이동인자 `a_T` 키를 만들어라.** 이번에 **Chowdhury 의 이동인자 14칸이 이 키가 없어 통째로 버려졌다.**
   그 논문의 WLF 상수 3벌이 전부 검산에 실패하므로 **a_T 표가 유일하게 쓸 수 있는 이동 정보인데 넣을 칸이 없다.**
   같은 이유로 Raghavan·Sadeghinia 도 막힌다. `wlf_c1/c2` 보다 이 키가 더 급하다.
3. **표만 옮기면 되는 Prony 논문이 아직 남았다.** `prony_corpus_survey.md` 가 61개 문서와 DB 채굴 여부를 대조한 표다.
   확인한 미채굴 표는 이렇다 —
   - **`snowball_papers/from_rel/2010 - Moisture Sensitivity of Plastic Packages of IC Devices`** — **Prony 표가 5개**(table-29·31·68·121·123). 책이라 재료가 여러 종일 것이다. **가장 큰 단일 문이다.**
   - `snowball_papers/from_cae/Park - 1999 - Methods of interconversion…` — Prony 표 4개. 다만 **방법론 논문이라 예제 재료일 수 있다** — 재료 정체를 먼저 확인해라.
   - `pkg_papers/17_encapsulant_potting/Haynes - 2013` — table-1·3 은 **Prony 항이 아니라 적합 입력(ω* 실수·허수부 vs 주파수)** 이다. `storage_modulus`/`loss_modulus` 표적이지 Prony 가 아니다.
   - `cae_papers/14_glass_fracture/Samieian - 2019` (PVB) · `pkg_papers/10_emc_filler_lowstress/Kenner - 1995 - Viscoelastic Characterization of an Epoxy-Based Molding Compound` — 본문 적중. 표 여부 미확인.
4. **Wang 2021 · Jia 2019 (foldable OLED 의 OCA) 는 손대지 마라 — 두 겹으로 막힌다.**
   - `Wang 2021` Table 2 의 열 머리글은 `Ei (MPa)` 인데 **다섯 값의 합이 0.9473** 이다. 표 제목은 *"The **relative modulus** and Prony parameter"* 다 — **단위가 오식이거나 제목이 오식이거나 둘 중 하나이고 우리가 고를 수 없다.**
   - 두 논문 다 이 값을 **재인용**한다(Wang 은 각주 23). 원출처를 찾아 확정하기 전에는 넣으면 안 된다.
   - 참고로 `Jia 2019` Table 3 은 같은 α1 = 0.59019 를 쓰면서 **τ1 이 0.01875 로 Wang(0.08175)과 다르다.** 둘 중 하나가 오식이다.
5. **`FILMISH` 필터를 고쳐라** — EC 의 6번 권고가 그대로 살아 있다. 156칸 중 121칸이 유리에폭시 적층판이다.
6. **디지타이즈 도구는 이번에 안 썼다.** EC 가 지적한 `digitize_curve.py` 77행(`np.linspace` → `np.geomspace`)이
   고쳐졌다는 것은 브리프로 전달받았을 뿐 이 배치가 검증하지 않았다. **로그축 그림을 실제로 캐는 다음 배치가 확인해라.**

---

## 부록 — `out_fd/` 이번 파동 파일 (전부 `fd70_` 또는 아래 이름)

| 파일 | 내용 |
|---|---|
| `fd70_01_chowdhury2019_prony.json` | Chowdhury 2019 — 재료 738, Table 2(7쌍)·Table 6/7(17쌍)·WLF 3벌, **78행** |
| `fd70_02_chiu2015_emc_prony.json` | Chiu 2015 — 신규 EMC, 체적 17항·전단 21항·κg·μg·WLF 2분기, **82행** |
| `fd70_03_raghavan2011_psr_prony.json` | Raghavan 2011 — 신규 PSR, 정규화 전단 10항, **20행** |
| `fd70_04_park2011_ufb_prony.json` | Park 2011 — 신규 언더필 UF-B, 인장 13항 + E∞, **27행** |
| `fd70_05_chae2010_emc_prony.json` | Chae 2010 — 신규 EMC, 인장 21항 + 18항 + E∞ 둘 + WLF, **82행** |
| `build_fd70_0*.py` | 위 JSON 을 만든 스크립트(원문 표가 리터럴로 박혀 있고 합·순간계수 검산이 `assert` 다) |
| `validate_fd.py` | 라이브 DB 를 **읽기 전용**으로만 열어 적재기·무결성검사 규칙을 미리 거는 검증기 |
| `prony_docs.txt` | 코퍼스 전수 `grep -i prony` 결과 104개 파일(문서 61건) |
| `prony_corpus_survey.md` | 그 61건을 **DB 채굴 여부·Prony 행수**와 대조한 표 — 3번 권고의 근거 |
| `park2011_t1-4.png` | Park 2011 Table 1 — 잃어버린 마이너스 부호를 눈으로 확인한 크롭 |
| `chae_t1-5.png` · `chae_t1c-5.png` · `chae_t2-6.png` · `chae_t2b-6.png` | Chae 2010 Table I·II 39항 판독 크롭 |
| `chow_t6b-10.png` · `chow_t6c-10.png` | Chowdhury Table 6 의 17항·WLF 대조 크롭 |
