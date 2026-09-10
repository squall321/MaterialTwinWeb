# 73차 IC — 두 파동째 막혀 있던 Kenner 1995 를 새 키로 열고, Gower 2004 에서 부호 함정을 또 한 번 잡았다

**결론 네 줄.**
1. **Kenner 1995 를 닫았다.** 새로 열린 `mechanical.relaxation_modulus` 의 **첫 손님**이다 — Fig. 2 마스터커브 3벌에서 **49점**을 디지타이즈하고, 원문이 인쇄한 영시간계수 3개·초기기울기 2개·Tg 1개를 더해 **55행**. 재료 1종(MP7100)·출처 1건 모두 신규.
2. **Gower 2004 의 부호를 600 dpi 렌더로 전수 확인했다 — 25칸 중 15칸이 뒤집혀 있었다.** 그리고 이 논문의 **WLF C1/C2 열이 72차 HA 가 없다고 적은 "두 번째 검산 열"**이었다. 새로 넣은 것은 **20행**(15 °C 이동인자 5 + WLF 10 + Mz 5), **재료는 전부 기존 것**.
3. **Baek 2008 은 못 닫았다.** Tg 를 어디서도 못 찾았고, **HA 가 제시한 논리 자체가 약했던 것**도 확인했다(§4).
4. **새 색인(29,846편)에서 미채굴 문서 두 편**을 찾았다 — **Amagai 1999**(시간축 완화계수 그림 + Prony 10항, 부호까지 렌더 확인 완료)와 **Michaelides 1999**.

| 파일 | 내용 | 행 |
|---|---|---:|
| `ic73_01_kenner1995_relaxation_modulus.json` | Kenner 1995 Fig.2 마스터커브 3벌 + 인쇄 스칼라 | **55** |
| `ic73_02_gower2004cta_shift_factor_wlf.json` | Gower 2004(CTA) Table 2 — a_T(15 °C)·WLF C1/C2·Mz | **20** |
| | **합계** | **75** |

부속 — `build_ic73_01.py`·`build_ic73_02.py`(생성기, 검산이 `assert` 다) · `ic73_extract.py`·`ic73_track.py`(Fig.2 추출기) · `ic73_kenner_fig2_points.json`(49점 좌표) · 렌더 크롭 5장.

> **라이브 DB 에는 쓰지 않았다.** 검증은 전부 `sqlite3 .backup()` 으로 뜬 **WAL 포함 일관 사본**에 `--apply` 로 했다(§7a — 그냥 `cp` 하면 안 된다).

---

## 1. Kenner 1995 를 닫았는가 — **닫았다. 두 파동(71차 GA·72차 HA) 연속으로 막혀 있던 자리다**

GA 는 *"Prony 항이 표로 인쇄되지 않는다"*, HA 는 *"시간축 `E(t)` (Pa) 키 부재로 두 파동째 막힘"* 이라 적었다.
**이번에 키가 생겼고, 곡선은 표가 아니라 그림이었으므로 디지타이즈가 맞는 길이었다.**

- 출처 — V. H. Kenner, M. R. Julian, C. H. Popelar, M. K. Chengalva, **MRS Proceedings 390, 97–102 (1995)**, doi `10.1557/proc-390-97`. **Crossref 로 서지·저자 4인·권·연도를 확인했다**(DB 에 없던 출처다).
- 재료 — **신규 1종.** `Epoxy molding compound MP7100 (silica-filled epoxy, Tg 110 C, Nitto-Denko, Kenner 1995 OSU)`. 실리카 고충전 에폭시, Intel 이 공급한 ASTM D638-91 type IV 도그본, 175 °C 5 h 후경화. `role = evidence`.

### (a) 넣은 것 — 55행

| 갈래 | 키 | 행 | method / tier |
|---|---|---:|---|
| Fig.2 마스터커브 3벌 | `mechanical.relaxation_modulus` | **49** | `digitized` / t1 |
| 본문 인쇄 영시간계수 3개 | `mechanical.relaxation_modulus` (`time_s = 0`) | **3** | `computed` / t2 |
| 본문 인쇄 정속변형률 초기기울기 2개 | `mechanical.youngs_modulus_at_rate` | **2** | `measured` / t1 |
| 본문·Fig.3 인쇄 Tg | `thermal.glass_transition` | **1** | `estimated` / t2 |

곡선별 구간 — **ε₀ = 0.25 %**: log t = −9…+9 (19점) · **0.5 %**: −9…+9 (19점) · **1.0 %**: 0…+10 (11점).
전 행에 `curve_type = master_curve` · `reference_temperature_c = 100` · `reference_temperature_printed = true` · `relaxation_mode = tensile` · `strain_pct` 를 달았다. 그림 표제가 **`Master Stress Relaxation Curves for MP7100 Molding Compound at 100 °C`** 이고 본문이 *"all shifting was arbitrarily effected relative to the 100 °C relaxation curve"* 라 못박는다 — **71차 GA 가 세운 기준온도 규칙을 그대로 통과한다.**

### (b) **검산 둘 — 이 49점의 근거다**

**검산① 원문이 인쇄한 영시간계수 3개가 곡선 왼쪽 끝의 앵커다.**

| 곡선 | 원문 인쇄 E(0) | 우리 판독(좌측 끝) | 차이 |
|---|---:|---:|---:|
| ε₀ = 0.25 % | **21,400 MPa** | 21,115 MPa | **−1.3 %** |
| ε₀ = 0.5 % | **17,300 MPa** | 17,029 MPa | **−1.6 %** |
| ε₀ = 1.0 % | **3,000 MPa** | 2,969 MPa | **−1.0 %** |

세 곡선이 전부 −1 ~ −1.6 % 로 **부호가 같은 계통오차**다(원문이 밝힌 완화계수 정확도는 **±4 %**).
이 앵커가 특히 강한 이유 — **1.0 % 곡선의 3,000 MPa 은 다른 둘의 1/7 이라 "자릿수를 잃은 값" 처럼 보인다.** 그런데 판독해 보니 그 곡선은 **환산시간 log t = −0.26 에서야 시작하고**(나머지 둘은 −9.3), 시작점이 정확히 log₁₀ 3.47 이다. 원문 자신이 *"the shortcomings of, in particular, the 1.0 % strain master curve"* 라 쓰는 그 절단이다. **인쇄값이 맞다.**

**검산② 다른 그림이 같은 값을 말한다 — 기준온도가 100 °C 이므로 a_T = 1 이라 두 그림이 겹쳐야 한다.**
Fig.1(0.5 % 변형률 **등온** 완화곡선 9벌)의 **100 °C 곡선**을 **따로 디지타이즈**해 0.5 % 마스터커브와 대조했다.

| log t | 1 | 1.5 | 2 | 2.5 | 3 | 3.5 |
|---|---:|---:|---:|---:|---:|---:|
| 차이 (decade) | 0.014 | 0.012 | 0.022 | 0.030 | 0.040 | 0.031 |

**축도 다르고(Fig.1 은 log t 0~5 / Fig.2 는 −10~15) 눈금도 다른 두 그림이 0.012~0.040 decade 안에서 만난다.** 곡선 배정(어느 것이 0.25/0.5/1.0 % 인가)이 틀렸다면 이 검산은 통과할 수 없다.

### (c) 판독 방법과 오차 — 숨기지 않는다

- **900 dpi 렌더.** 축 보정은 검출한 주눈금으로만 했다 — 가로 6개(직선회귀 잔차 **최대 0.21 px**), 세로 6개(**최대 2.6 px = 0.005 decade**).
- **스캔이 기울어져 있다**(1,400 px 에 4 px). 상·하 프레임선을 x 마다 재어 1차 보정했다 — 우측 끝에서 **0.006 decade** 를 되돌린다.
- 곡선은 **실선(Master Curve)과 원형 마커(Prony Series Fits)가 겹친 두께 ~35 px 밴드**다. 마커가 곡선 위에 중심을 두므로 **밴드 상·하 끝의 중점**을 곡선값으로 잡았다. 컬럼 추적으로 세 곡선을 분리하고, **추적 결과를 원본에 겹쳐 그려 눈으로 확인했다**(`ic73_fig2_overlay.png`).
- **세 곡선이 합쳐지는 구간은 잘랐다.** 0.25 %·0.5 % 는 **log t = +9.3** 에서, 1.0 % 는 **+10.3** 에서 서로 25 px 안으로 붙는다. 그 너머는 밴드 중심이 어느 곡선도 아니므로 **넣지 않았다** — 세 곡선 모두 log t ≳ 11 에서 고무상 평탄부(≈ 2.83 = 680 MPa)로 수렴하는데, **그 평탄값은 원문이 인쇄하지 않아 검산할 수단이 없다.**
- **단조감소 위반 3건** — 전부 좌측 평탄부이고 크기가 **+0.0003 ~ +0.0004 decade(= 0.2 px 미만)** 다. 판독 잡음이지 값이 아니다. **강제로 펴지 않았다** — 곡선을 매끄럽게 만들면 그건 우리 값이 된다.
- **`digitize_curve.py` 는 쓰지 않았다.** Fig.2 는 마커와 실선이 겹친 3중 곡선이라 단색 도구가 감당하지 못한다. 전용 추적기(`ic73_track.py`)를 쓰고 눈금 잔차·중첩 검증화를 함께 남겼다. (**x 축이 이미 `log t` 로 인쇄돼 있어 `--logx` 재샘플 문제 자체가 없다.**)

### (d) 판단이 갈릴 수 있는 곳 셋 — 미리 밝힌다

1. **제조사 철자.** 원문은 *"manufactured by **Nitto-Dinko**"* 라 인쇄한다. Nitto-Denko 의 오식으로 보고 **재료명에는 Nitto-Denko** 를 쓰되, `attributes.manufacturer_printed_verbatim = "Nitto-Dinko"` 로 인쇄 철자를 그대로 남겼다. **값이 아니라 표기를 기록한 것이다.**
2. **영시간계수를 `time_s = 0` 으로 넣었다.** 인쇄된 절대값이지만 **Prony 적합의 t→0 극한**이라 `measured` 가 아니라 `computed`·t2 로 적었다. 원문 자신이 이 값을 데이터의 단시간 절단 때문에 실제 순간계수보다 낮다고 밝힌다.
3. **Tg 는 `estimated`·t2 다.** 원문 verbatim이 *"This was taken to give an **estimate** of the glass transition temperature"* 다 — DSC/TMA 가 아니라 완화곡선의 온도의존성(100 s 기준)에서 읽은 값이다. Fig.3 이 축 위에 `T = Tg = 110 °C` 를 다시 인쇄한다. **원문이 스스로 추정이라 부르는 것을 실측으로 올리지 않았다.**

---

## 2. Gower 2004 의 부호를 렌더로 확인했는가 — **했다. 25칸 중 15칸이 뒤집혀 있었다**

**먼저 어느 논문인지 갈랐다.** 코퍼스에 **Gower 2004 가 두 편** 있다.

| 논문 | DOI | 이동인자 표 |
|---|---|---|
| **Gower & Shanks 2004, 사슬이동제(CTA) 수준** (Macromol. Chem. Phys. 205, 2139–2150) | `10.1002/macp.200400177` | **있다 — Table 2** ← 이번 대상 |
| Gower & Shanks 2004, 단량체 조성 (J. Appl. Polym. Sci. 93, 2909–2917) | `10.1002/app.20873` | **없다**(Table I 조성 · Table II 물성뿐) |

### (a) 실측 — **부호가 어떻게 뒤집히는가**

Table 2 의 `log a_T` 25칸을 **600 dpi 렌더로 전수 대조**했다(`ic73_gower04_t2_crop.png`).

| 온도 | docling / pdftotext 표 추출 | **600 dpi 원본 렌더** | 판정 |
|---|---|---|---|
| 15 °C (5칸) | `0.60 0.60 0.65 0.80 1.0` | `0.60 0.60 0.65 0.80 1.0` | **정상** |
| 25 °C (5칸) | `0 0 0 0 0` | `0 0 0 0 0` | **정상** |
| 35 °C (5칸) | `0.50 0.50 0.55 0.60 0.70` | **`−0.50 −0.50 −0.55 −0.60 −0.70`** | **뒤집힘** |
| 50 °C (5칸) | `1.10 1.10 1.15 1.30 1.50` | **`−1.10 −1.10 −1.15 −1.30 −1.50`** | **뒤집힘** |
| 65 °C (5칸) | `1.60 1.60 1.65 1.85 2.00` | **`−1.60 −1.60 −1.65 −1.85 −2.00`** | **뒤집힘** |

**72차 HA 가 Gower 2006 Table 4 에서 잡은 것과 같은 함정인데, 이쪽이 더 고약하다.**
2006 Table 4 는 45칸이 **전부** 음수라 통째로 뒤집혔다 — 즉 "전부 양수" 라는 이상함이 눈에 띈다.
**2004 Table 2 는 25칸 중 10칸이 멀쩡하다**(15 °C 는 원래 양수, 25 °C 는 0). 그래서 추출 결과가 `0.60 / 0 / 0.50 / 1.10 / 1.60` 처럼 **"온도가 올라가면 이동인자가 커진다"는 그럴듯한 단조 표**로 보인다. **부호를 잃은 표가 정상 표의 모양을 갖춘다.**

### (b) **HA 가 "없다" 고 적은 두 번째 검산 열을 찾았다**

HA 는 Gower 2006 45칸에 대해 *"표 안에서 서로를 검산해 줄 두 번째 열이 없다"* 고 적었다.
**이 논문의 Table 2 에는 그 열이 있다 — WLF `C1`·`C2` 다.**

원문 식 (5) verbatim(600 dpi 렌더, `ic73_gower04_eq5b.png`) —
`log(a_T) = −C₁(T − T₀)/(C₂ + T + T₀)`

| 함수형 | 20칸(폴리머 5종 × 15/35/50/65 °C) 최대 어긋남 |
|---|---:|
| **표준형 `C₂ + (T − T₀)`** | **0.026 decade** |
| 인쇄된 대로 `C₂ + T + T₀` | **0.654 decade** |

**인쇄된 분모의 `+T₀` 는 오식이다** — 이 논문 자신의 Table 2 를 재현하지 못한다.
예(AA4M91-3, C1 = 5.95 · C2 = 109.3 · T₀ = 25 °C) — T=15 → **+0.599**(인쇄 +0.60) · T=35 → **−0.499**(−0.50) · T=50 → **−1.108**(−1.10) · T=65 → **−1.594**(−1.60).
**우리가 값을 고친 것이 아니라 이 상수들이 속한 함수형을 확정한 것이고, 인쇄된 식은 `equation_verbatim` 에 글자 그대로 남겼다.**

**그리고 이 검산이 부호를 독립으로 증명한다** — C1·C2 는 양수인데, 이 함수형이 35/50/65 °C 에서 음수를 내놓는다. 추출본의 양수와는 어떤 조합으로도 맞출 수 없다.

### (c) **72차 HA 의 정정이 옳았음을 다른 출처로 확인했다 — 그래서 15칸은 다시 넣지 않았다**

이 논문의 폴리머 **AA4M91-3 … AA4M02-3 다섯 종은 DB 재료 1664~1668 과 같은 재료다**(조성이 소수 둘째 자리까지 같다 — Gower 2006 이 세운 것).
그 다섯 종의 **35/50/65 °C 15칸이, HA 가 Gower 2006 Table 4 에서 부호를 고쳐 넣은 값과 한 자리도 틀리지 않고 같다.**

→ **두 논문이 같은 이동인자를 인쇄한다. HA 의 부호 정정이 독립 출처로 검증됐다.**
→ 같은 이유로 **그 15칸은 중복이라 다시 넣지 않았다.**

### (d) 넣은 것 — 20행, **신규 재료 0종**

| 키 | 행 | 무엇이 새로운가 |
|---|---:|---|
| `mechanical.tts_shift_factor` (T = **15 °C**) | **5** | **2006 Table 4 에 없는 새 온도다.** T < T₀ 라 a_T > 1 인 첫 사례이기도 하다 |
| `mechanical.wlf_c1` | **5** | DB 에 이 재료들의 WLF 가 하나도 없었다 |
| `mechanical.wlf_c2` | **5** | 〃 |
| `structure.molecular_weight` (**Mz**) | **5** | DB 에는 같은 폴리머의 Mn·Mw 만 있었다(2006 출처). z 평균은 이 논문에만 있다 |

환산 — `a_T = 10^(log a_T)`, 다섯 칸 전부 왕복 검산(`log10(a_T)` 되돌리기) **불일치 0**.
기준온도 25 °C (298 K) 는 본문·그림 캡션에 여러 번 인쇄돼 있다 — *"superpositioning the curves at a reference temperature of 25 °C"*, *"(reference temperature: T₀ = 298 K)"*.

**`fit_r2` 로 옮기지 않은 것 하나** — 원문이 인쇄한 것은 `Correlation coefficient`(= r, 0.990~0.999)이지 r² 가 아니다. 조건 축 이름이 `fit_r2` 라고 그쪽에 넣으면 **한 칸에 다른 양이 들어간다.** `fit_correlation_coefficient_printed` 로 인쇄 이름 그대로 남겼다.

### (e) **`a_C` 는 이동인자 키에 넣으면 안 된다 — Table 3 을 버린 이유**

Table 3 의 `a_C` 는 *"Horizontal **polymer composition** shift factors"* 다. 온도축이 아니라 **조성축**의 이동인자이고, 다섯 마스터커브를 하나의 "super" 마스터커브로 겹치려고 쓴 것이다.
**HA 가 §8-3 에서 경고한 그대로다**(*"밑과 축을 먼저 갈라라 — 세 종류가 같은 단어를 쓴다"*). `tts_shift_factor` 에 들어가면 무차원이라 어떤 가드에도 안 걸리고 조용히 오염된다. **넣지 않았다.**

---

## 3. 못 넣은 것 — **셋으로 갈라 적는다**

### (가) 문서에 없었다
- **Baek 2008 의 기준온도** — §4. 두 재료의 Tg 가 어디에도 인쇄돼 있지 않다.
- **Kenner 의 고무상 평탄값** — 세 마스터커브가 log t ≳ 11 에서 ≈ 680 MPa 로 수렴하는데 **원문이 그 값을 인쇄하지 않는다.** 검산 앵커가 없어 그 구간을 넣지 않았다.
- **Kenner 의 이동인자 표** — Fig.3 에 `Log a_T` 대 온도가 **그림으로만** 있다(오차막대 포함, T₀ = 100 °C). 이번에 넣지 않았다 — §6-2 로 넘긴다.
- **Kenner Prony 항** — Fig.2 에 마커로만 표시되고 **항 값이 표로 인쇄되지 않는다.** 71차 GA 판정 그대로다.

### (나) 못 열었다
- **Kim 2008** `10.1002/pen.21152` — Wiley 403, 코퍼스 없음. Baek 의 유일한 남은 경로다(§4).
- **Hong 2007** `10.1007/BF02875826` — Springer 로그인 벽. **열려도 소용없다**(재료가 다르다 — HA 확인).

### (다) 키가 없었다
- **이번 파동에는 없다.** 두 파동 연속 막혀 있던 시간축 완화계수 키가 열렸고, 이번에 막힌 것 중 키 부재가 원인인 것은 하나도 없다.
  (다만 **Prony 상대계수 `C_i` 와 이산 환산시간의 짝**은 기존 `prony_relative_modulus`·`prony_relaxation_time` 로 담긴다 — Amagai 1999 이 그 형태다. §5)

---

## 4. Baek 2008 을 닫았는가 — **못 닫았다. 그리고 HA 가 제시한 논리 자체가 생각보다 약했다**

전용 조사를 붙여 코퍼스(재빌드된 29,846편)·라이브 DB·공개 웹을 전수로 훑었다. **결과는 셋 다 없음이다.**

### (a) HA 의 경로 — **찾지 못했을 뿐 아니라, 근거가 약했다**

HA 는 *"Baek 이 쓴 WLF 보편상수 17.4·51.6 K 는 **T_ref = Tg 규약**이다"* 라며 두 재료의 Tg 를 구하라고 넘겼다.
원문을 다시 열어 보니 그 상수가 나오는 자리는 **식 (7)** 이고, 그 식은 이렇다(원문 verbatim) —
> `C1' = C1g/(1 + (θ* − θg)/C2g),  C2' = C2g + θ* − θg` … *"where C1g and C2g are universal constants, which are 17.4 and 51.6 K, respectively."*

**이 식은 Tg 기준 상수를 임의의 θ\* 기준으로 옮기는 변환식이다.** 즉 17.4·51.6 이 나온다는 사실은 θ\* = Tg 를 뜻하지 않는다 — **오히려 θ\* 가 Tg 가 아닐 때 쓰는 식이다.** HA 의 추론은 방향이 반대였다.

### (b) 새로 확인한 것 — **대체 등급으로 우회하는 길도 막혀 있다**

원문 verbatim —
> *"Properties of ABS (**Techno ABS 545, Techno polymer**) were employed as the properties of the film and properties of a PC/ABS polymer alloy (**Lupoy HR-5007AB, LG Chemical**) were adopted as the properties of the substrate resin."*

즉 **Table 2 의 물성은 Moldflow 데이터베이스의 대체 등급**이고, g(t) 30점을 낸 **실제 DMA 시편(제일 HP-1000X · Nissha 필름)과 다른 재료다.** 대체 등급의 Tg 를 구해도 쓸 수 없다.

### (c) 어디까지 갔는가

| 경로 | 결과 |
|---|---|
| 원문 재독(docling + `pdftotext -layout` + Figure 1 확인) | `θg` 는 **식 (7) 의 기호로만** 나온다. 숫자·T_ref 없음. Fig.1 축·캡션에도 온도 표기 없음 |
| 코퍼스 FTS(29,846편) — `HP-1000X` · `Lupoy` · `Techno ABS` | **Baek 2008 단 한 편**에만 나온다 |
| 코퍼스 — `Nissha` | Baek 2008 + 무관한 터치스크린 리뷰 3편 |
| 같은 연구실 형제 논문 4편(`10.1002/pen.21152` 등) | **코퍼스에 없다** |
| 라이브 DB | 재료 **2388**(Nissha 필름, 출처 4556 = Baek 2008)에 4행이 있는데 **Tg 는 없다.** HP-1000X 기판은 **재료 자체가 없다** |
| 공개 웹 | **HDT·Vicat 만 나온다** — Infino HP-1000XA `Vicat 123 °C` · `HDT(1.8 MPa) 110 °C`, Starex HP-1000X `HDT 105 °C`, Lupoy HR5007A `HDT 113 °C`. **HDT·Vicat 는 Tg 가 아니다 — 섞지 않았다** |
| 근접 오적중 | Lee 2014(`10.1007/s12541-014-0357-2`)가 *"The glass transition temperature of the polymer is 116.2 °C"* 를 인쇄하는데 **ABS XR 404/LG · Kurz 필름**이라 다른 재료다. **쓰지 않았다** |

**따라서 30점은 이번에도 미등록이다**(`out_ec/ec_baek2008_relaxation.csv`). **추론으로 T₀ 를 만들면 그건 우리 값이 된다.**

---

## 5. 새 색인에서 새로 걸린 문서가 있었는가 — **있다. 두 편이 진짜다**

색인 재빌드를 확인했다 — **20,692 → 29,846편**. 구 색인 백업(`corpus_fts.db.pre-w72-20260909`)과 **경로 차집합**으로 갈랐다.

| 질의 | 신 | 구 | 새로 걸린 것 |
|---|---:|---:|---:|
| `"relaxation modulus"` | 64 | 58 | 6 |
| `"prony"` | 70 | 58 | 13 |
| `"shift factor"` | 86 | 79 | 7 |
| `"time-temperature superposition"` | 74 | 67 | 7 |
| `"WLF"` | 98 | 90 | 8 |

**71차 GA 의 6번은 닫혔다** — GA 가 *"색인이 이번 파동 최대 수확 문서를 통째로 놓치고 있다"* 며 지목한 `2010 - Moisture Sensitivity of Plastic Packages of IC Devices` 가 **다섯 질의 전부에 들어왔다.**

새로 걸린 것 중 **솔버 매뉴얼(LS-DYNA·Radioss·OpenFOAM·FEniCS)·계측기 시트(TA ARES-G2)·규격(IPC-JEDEC9301)·무관 논문(전력계통 OPF, rfc8257)** 을 걸러내면 **진짜 후보는 둘이다.**

### ⭐ **Amagai 1999** — 다음 파동의 1순위. **부호까지 렌더로 확인해 뒀다**
`Characterization of chip scale packaging materials`, Microelectronics Reliability **39**(1999) 1365–1377.
경로 — `/data/paper_patent_corpus/snowball_papers/from_rel/Amagai - 1999 - …`
**DB 에 출처가 없다 — 한 번도 채굴되지 않았다.**

- **Fig. 4 `Relaxation modulus of molding compound`** — 세로 `Relaxation modulus (MPa)` **0~10,000 선형**, 가로 `log(t/t₀)` **−2~4**, `t₀ = 1200 s`. **절대값 곡선이라 이번에 열린 키의 정확한 표적이다.**
- **Table 2 인쇄 앵커** — `G(0) = 11040 MPa` · `G(∞) = 1608 MPa` · 상수 `0.6` · 아레니우스 `H/R = 36145` · `Standard temperature 120 °C` · CTE `8/35 ppm/°C` · 경화수축 `0.000615` · 포아송비 `0.3`. **디지타이즈를 검산할 앵커가 둘(G0·G∞) 있다.**
- **Table 1 `Cᵢ at the reduced time`** — 10항. `prony_relative_modulus` + 이산 환산시간의 짝이다. **Cᵢ 합 = 1.000001 로 검산된다.**
- ⚠ **부호 함정이 또 있다. 600 dpi 렌더로 확인했다** — `log(t·t₀)` 열의 **앞 다섯 칸이 음수인데 docling 이 전부 잃는다.**

  | | docling `tables/table-1.md` | **600 dpi 원본 렌더** |
  |---|---|---|
  | 열 전체 | `2.000 0.699 0.398 0.222 0.097 0 0.041 0.079 0.146 2.000` | **`−2.000 −0.699 −0.398 −0.222 −0.097 0 0.041 0.079 0.146 2.000`** |

  Cᵢ 열은 멀쩡하다(합 1.000001). **10칸 중 5칸이 뒤집힌다.**
- ⚠ 표 머리글은 `log(t · t₀)` 로 **점**이 찍혀 있는데, 본문과 Fig.4 축은 `log(t/t₀)` 로 **나눗셈**이다. **어느 쪽이 맞는지 다음 파동이 본문 식으로 확정해라** — 우리가 고르면 그건 우리 값이 된다.
- ⚠ 원문은 `G` 를 쓰면서(`shear modulus`) 표 머리글은 `Relaxation modulus (MPa)` 다. **`relaxation_mode` 를 shear 로 볼지 tensile 로 볼지 본문 식으로 확정해라.**

### **Michaelides 1999** — 두 번째 후보
`Die cracking and reliable die design for flip-chip assemblies`.
경로 — `/data/paper_patent_corpus/structured/snowball_papers/from_materials/Michaelides - 1999 - …`. **DB 에 출처 없음.**
본문 verbatim — *"the stress relaxation curve, as a function of time, was determined from the DMA data for several temperatures. These curves were then horizontally shifted in time to create a master curve at a **reference temperature of 438 K (165 °C)** (Fig. 5)."* 언더필 재료, Prony 급수, 아레니우스 이동인자(Fig. 6).
⚠ **docling 표 추출이 완전히 실패했다**(`table-1.md` 가 빈 머리글, `table-2.md` 가 제목 한 줄). **값은 그림과 렌더에만 있다.**

### 그 밖에 새로 걸린 것(참고)
`3M_OCA_Foldable_OLED_Whitepaper`(prony) · `Demarteau 1996`·`Kraus 1976`·`Sherriff 1973`·`Villey 2015`(전부 PSA 점탄성·TTS) · `Cordier 2008`(초분자 고무) · `NARAYANASWAMY 1971`(유리 구조완화 고전) · `TA_ARES-G2_rheometer`(계측기 시트).

---

## 6. 다음 배치에 넘길 것

1. ⭐ **Amagai 1999 를 채굴해라 — 새 키의 두 번째 손님이고 준비가 끝나 있다**(§5).
   Fig.4 가 **절대값 완화계수 곡선**이고 인쇄 앵커가 둘(`G0 = 11040` · `G∞ = 1608` MPa) 있다. Table 1 의 **부호는 이번에 렌더로 확인해 뒀다**(음수 5칸). 남은 판단 둘 — `log(t·t₀)` vs `log(t/t₀)` 머리글, 그리고 shear/tensile 모드. **둘 다 본문 식으로 확정할 것. 추정하지 마라.**
2. **Kenner 1995 Fig.3 의 이동인자를 넣어라 — 이번에 남긴 유일한 미채굴 값이다.**
   `Log a_T` 대 온도(24~150 °C), **T₀ = 100 °C 가 그림 표제에 인쇄돼 있고**, 오차막대까지 있다. 원문이 *"the shift factor is found to be independent of imposed strain"* 이라 못박으므로 **세 변형률 곡선에 같은 이동인자가 붙는다.** 이번에 넣은 49점의 `set_id` 와 짝이 맞는다. 재료·출처는 이미 서 있다.
3. **Baek 2008 — 남은 길은 하나뿐이다.** `10.1002/pen.21152`(Kim 2008, Polym. Eng. Sci. 48, 1840). 같은 연구실·같은 재료·같은 절차. Wiley 403 이고 코퍼스에 없다. **HA 가 넘긴 "두 재료의 Tg" 경로는 §4(a) 대로 논리가 약하니 매달리지 마라.** SNU S-Space 의 학위논문(Baek 또는 Kim)이 차선이다.
4. **Gower 2004(CTA) Table 1 이 통째로 남아 있다 — 재료 10종.**
   `AA4M91-1 … AA4M02-1`(CTA 무첨가)과 `-2` 계열은 **DB 에 없는 재료다**(`-3` 계열만 1664~1668 로 있다). 인쇄값 — Tg(DSC)·겔분율·loop tack·정적전단유지·점도·pH·고형분·도포량. `-3` 계열의 **정적전단유지**(4.5/7.5/9.0/21.5/51.5 min)도 DB 에 없다.
   ⚠ **여기도 부호 함정이다** — Table 1 의 Tg 열을 docling 으로 읽으면 `39.7` 로 나오는데 **PSA 의 Tg 는 −39.7 °C 다**(같은 저자의 2004 단량체 논문 Table II 는 `- 39.7` 로 부호가 살아 있다). **반드시 렌더로 대조해라.**
   ⚠ Table 3 의 `a_C` 는 **조성 이동인자**다. `tts_shift_factor` 에 넣지 마라(§2e).
5. ⚠⚠ **`out_ic/` 를 폴더째 겨누지 마라 — HA 가 경고한 함정이 여기서는 더 나쁘다.**
   `out_ic/` 에는 **8월 28일 자 `ic01`~`ic04` 4건이 이미 있었다.** 실측 —
   ```
   $ ingest_agent_json.py .../out_ic/ic73_01....json .../out_ic/ic73_02....json --apply
   [APPLY] ok 75 / new_mat 1                      ← 파일로 겨누면 깨끗하다
   $ ingest_agent_json.py .../out_ic/ --apply
   [APPLY] ok 84 / kept_better 19 / new_mat 1     ← 폴더째면 28행이 섞인다
   ```
   **HA 의 `out_ha/` 는 40행이 전부 `kept_better` 라 값이 안 망가졌지만, 여기는 `ic02`(8행)·`ic04`(1행)가 `ok` 로 뜬다 — 즉 라이브 DB 에 중복 9행이 실제로 들어간다.** 집계 오염이 아니라 쓰기 사고다. **반드시 `ic73_*.json` 을 파일로 지정해라.**
6. ⚠ **DB 사본은 `cp` 로 뜨지 마라 — 이번에 사고가 날 뻔했다**(§7a).
7. **`FILMISH` 필터** — EC 6번 · FD 5번 · GA 7번 · HA 6번. **다섯 파동째 살아 있다.** 이번에도 손대지 않았다.
8. **Kenner Memo — Fig.5·6(0.2 % 시컨트계수 마스터커브, T₀ = 100 °C)과 Fig.7·8(응력-변형률 예측/실측)** 이 남아 있다. Fig.6 은 시컨트계수의 마스터커브라 **완화계수와 다른 양**이다(변형률속도축). 키를 고르기 전에 축부터 갈라라.

---

## 7. 검증 — 무엇을 어떻게 확인했나

### (a) ⚠ **라이브 DB 는 WAL 모드다 — `cp` 로 뜬 사본은 최신이 아니다**

처음에 `cp materialtwin.db` 로 사본을 떠서 적재기를 돌렸더니 **55행 중 52행이 `미정의 key mechanical.relaxation_modulus` 로 거부**됐다.
원인은 값이나 스키마가 아니었다 — **`materialtwin.db-wal` 이 6.7 MB 있었고 이번에 열린 키(정의 278)가 거기에만 있었다.** 본체 파일의 mtime 은 여전히 어제(23:24)다.

**`sqlite3` 의 `.backup()` 으로 다시 떠서 해결했다**(WAL 을 포함한 일관 스냅숏을 만든다).
```python
src = sqlite3.connect('file:.../materialtwin.db?mode=ro', uri=True)
dst = sqlite3.connect('.../dbcopy/materialtwin.db'); src.backup(dst)
```
**다음 파동에 넘긴다** — 사본으로 검증하는 것이 이 저장소의 규율인데, **`cp` 로 뜨면 조용히 낡은 DB 를 검증하게 된다.** 이번엔 새 키가 없어 요란하게 실패했지만, **키가 이미 있는 배치였다면 아무 소리 없이 "구 DB 기준 검증 통과" 가 나왔을 것이다.**

### (b) 적재 검증
- **사본에 `--apply` 로 확인했다**(브리프 §3: 드라이런은 `method` 어휘를 안 잡는다). 라이브 DB 는 **읽기 전용으로만** 열었다.
- 결과 — **`[APPLY] ok 75 / new_mat 1`**. **거부·강등·조건충돌·범위위반 0건.**
- 저장 후 재조회로 확인 — Kenner(재료 2808): `relaxation_modulus` **digitized/t1 49행 + computed/t2 3행**, `youngs_modulus_at_rate` **measured/t1 2행**, `glass_transition` **estimated/t2 1행**. **notes 가 빈 행 0건.**
  Gower(재료 1664~1668, 출처 4927): `tts_shift_factor` **5**, `wlf_c1` **5**, `wlf_c2` **5**, `molecular_weight` **5** — 전부 새 출처에 붙었고 **신규 재료 0종**.
- **새 출처 2건** — `4926` (`10.1557/proc-390-97`, journal, 1995) · `4927` (`10.1002/macp.200400177`, journal, 2004). Gower 2006 출처 `4236` 은 건드리지 않았다.

### (c) 무결성 검사 — **전문 diff 에서 바뀐 줄은 집계 한 줄뿐이다**
적재 전(무손실 사본)과 적재 후에 `integrity_check.py` 를 돌려 100줄을 통째로 diff 했다.
```
< 재료 2777 · 물성값 46498 · 출처 3122 · 정의 275/271
> 재료 2778 · 물성값 46573 · 출처 3124 · 정의 275/272
```
**차이 75 = 55 + 20.** 재료 +1(MP7100) · 출처 +2 · **값이 붙은 정의 +1 — 그게 `mechanical.relaxation_modulus` 다.**
**새로 생긴 이상 0건.** 남은 `이상 1개` 는 이번 파동과 무관한 기존 항목이다.

### (d) 값 자체의 검산
| 검산 | 결과 |
|---|---|
| Kenner 앵커 3개(인쇄 영시간계수 vs 판독 좌측 끝) | **−1.3 / −1.6 / −1.0 %** (원문 정확도 ±4 %) |
| Kenner 교차검산(Fig.1 100 °C 등온곡선 vs 0.5 % 마스터커브) | **0.012 ~ 0.040 decade** 일치 |
| Kenner 단조감소 | 위반 3건, 전부 **0.0004 decade 미만**(0.2 px). 평탄부 판독잡음 — 강제로 펴지 않았다 |
| Kenner 축 보정 잔차 | 가로 **0.21 px** · 세로 **2.6 px (0.005 decade)** · 기울어짐 보정 0.006 decade |
| Gower 부호 | **25칸 전수 600 dpi 렌더 대조 — 15칸 뒤집혀 있었다** |
| Gower WLF 자체검산 | 표준형 **0.026 decade** vs 인쇄형 **0.654 decade** — 인쇄 식 (5) 의 `+T₀` 는 오식 |
| Gower 왕복 검산 | `10^log → log10` 5칸 **불일치 0** |
| Gower 교차검산 | 2004 의 35/50/65 °C 15칸 = 2006 Table 4 값(HA 정정본)과 **완전 일치** |
| Amagai(미채굴, 넘김) | `Cᵢ` 합 **1.000001** · `log(t·t₀)` 부호 **600 dpi 렌더 확인 — 5칸 음수** |
