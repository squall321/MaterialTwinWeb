# 71차 GA — FD 가 남긴 미채굴 Prony 표

**한 줄** — FD 가 "미채굴 최소 8편" 이라며 남긴 목록(Moisture 책 · Park 1999 · Kenner 1995 · Samieian 2019 ·
Haynes 2013 + survey 의 Brinson 2008 · Liu 2011)을 **전수로 열었다.** 옮길 수 있었던 것은
**책의 두 장(8장 NCP · 16장 compound B)과 Samieian 2019 셋뿐**이고, 거기서
**Prony 40항 · 재료 3종(전부 신규) · 99행**을 준비했다.
나머지는 **표가 아예 없거나(Kenner · Brinson · Liu 3편)**, **표는 있으나 넣으면 안 되는 값(Park 1999)** 이었다(§8).

> **나는 라이브 DB 를 읽기 전용으로만 열었고 적재하지 않았다** — `out_ga/ga71_*.json` 이 내 결과물이다.
> **다만 보고서를 마무리하는 사이(2026-09-09 22:12) 다른 손이 이 세 JSON 을 라이브 DB 에 적재했다** —
> 재료 **2747**(NCP) · **2748**(compound B) · **2749**(PVB), **99행 전부**가 올바른 출처·DOI 와 함께 들어갔다.
> 적재 후 검산도 다시 걸어 확인했다 — NCP 가중치 14행 합 **정확히 1.0**, compound B ΣEₙ **28,022 MPa**,
> PVB 두 분기 각 6항, **τ 가 1e−32 ~ 1e23 전 15항 그대로**(19차에 Chiu 2018 을 잘랐던 적재기 범위 가드에
> **이번엔 한 항도 안 잘렸다**), 무결성 규칙 `Prony 항번호 없음` **0** · `가중치·완화시간 항수 불일치` **0**.
> `out_ga/` 는 8월 배치가 이미 쓰던 디렉터리라(`sac107_sac205.json` 등 3건) 이번 산출물은 전부 **`ga71_` 접두어**를 붙였다.
> `ga71_validate.py` 를 지금 다시 돌리면 `! 같은 이름이 이미 DB 에 있다 [2747/2748/2749]` 3건이 뜨는데,
> **적재 전 검증에서는 위반 0 이었고 이 3건은 내 행이 실제로 들어간 것을 확인해 주는 신호다**(중복 재료가 아니다).

---

## 1. 문서별 결과 — 표였나 그림이었나, 몇 항을 넣었나, 기준온도가 있었나

| 문서 | Prony 표 | 기준온도 | 넣은 항 | 결과 |
|---|---|---|---:|---|
| **Moisture Sensitivity 책 8장** (Jang & Han) — NCP | **표** Table 8.7 | **있다** T_ref = 298 K | **13** | **33행** — 인장 정규화 13항 + e∞ + WLF + E0·ν·CTE·Tg |
| **Moisture Sensitivity 책 16장** (van Driel 외) — molding compound B | **표** Table 16.2 | **있다** T_ref = 25 °C | **15** | **35행** — 인장 절대 15항 + WLF + Tg·CTE 2분기 |
| **Moisture Sensitivity 책 8장** — Table 8.5 | **표** | — | 0 | ✗ **합성 검증예제다**(§2 참조) |
| **Samieian 2019** — PVB 중간막 | **표** Table 3·4 | **없다**(마스터커브가 아니다) | **6+6** | **31행** — 전단 정규화 6항 × 율속 2분기 + 축소다항 초탄성 6개 + 밀도 |
| Park 1999 — PMMA · 폴리이소부틸렌 | **표** 4개 | ✗ **어디에도 없다** | 0 | ✗ 재인용 + 역산 + **PDF 숫자 전면 오염**(§4) |
| Kenner 1995 — MP7100 EMC | **그림뿐**(Fig. 2) | 있다(100 °C) | 0 | ✗ **Prony 항이 표로 인쇄되지 않는다** |
| Brinson 2008 — 교과서 | **그림뿐**(Fig. 7.19·7.21) | 있다(25 °C) | 0 | ✗ 30항·28항이 **막대그림**이고 원 데이터는 Catsiff & Tobolsky 재인용 |
| Liu 2011 — 교과서 | **없다** | — | 0 | ✗ `prony` 적중이 **색인 페이지**(table-101)였다 |
| Haynes 2013 | — | — | 0 | ✗ FD 판정 재확인(적합 입력이지 Prony 항이 아니다) |
| Wang 2021 · Jia 2019 | — | — | 0 | ✗ FD 지시대로 손대지 않았다 |

**합계 — Prony 40항 · 완화시간 40 · 재료 3종(전부 신규) · 99행 · Prony 세트 4벌.**
산출 JSON 은 적재기·무결성검사 규칙(`Prony 항에 항번호 없음`·`가중치·완화시간 항수 불일치`·단위·범위·method 어휘·
notes 존재·DOI 존재·**기준온도 유무 기록**)으로 `ga71_validate.py` 에 걸어 **위반 0** 을 확인했다.
라이브 DB 를 읽기 전용으로만 여는 검증기다.

### `out_ga/` 이번 파동 파일

| 파일 | 내용 |
|---|---|
| `ga71_01_moisturebook2010_ncp_prony.json` | 8장 NCP — 인장 13항 + e∞ + WLF 2 + E0·ν·CTE·Tg, **33행** |
| `ga71_02_moisturebook2010_compoundB_prony.json` | 16장 compound B — 인장 15항 + WLF 2 + Tg·CTE 2, **35행** |
| `ga71_03_samieian2019_pvb_prony.json` | Samieian PVB — 전단 6항 × 2분기 + 초탄성 6 + 밀도, **31행** |
| `build_ga71_0*.py` | 위 JSON 생성기(원문 표가 리터럴로 박혀 있고 합·항수 검산이 `assert` 다) |
| `ga71_validate.py` | 라이브 DB 를 읽기 전용으로만 여는 사전 검증기 |
| `ga71_t87_crop.png` · `ga71_t86_crop.png` | 책 Table 8.7(13항)·8.6(E0) 350 dpi 판독 크롭 |
| `ga71_t162_crop.png` · `ga71_t161_crop.png` · `ga71_ch16_wlf_crop.png` | 책 Table 16.2(15항)·16.1(Tg·CTE)·WLF 본문 크롭 |
| `ga71_sam_t3_crop.png` · `ga71_sam_t4_crop.png` | Samieian Table 3·4 크롭 |
| `ga71_park99_t1_crop.png` | **Park 1999 Table 1 — 숫자 전면 오염을 증명하는 크롭**(§4) |
| `ga71_chow_aT_t1_crop.png` · `ga71_chow_aT_t3_crop.png` | **Chowdhury 이동인자 14칸 — 다음 파동이 쓸 값의 렌더 확인**(§5) |

---

## 2. 가장 큰 문이라던 책 — **Prony 표 5개 중 실제로 쓸 수 있는 것은 2개였다**

FD 가 `snowball_papers/from_rel/2010 - Moisture Sensitivity of Plastic Packages of IC Devices` 를
**"Prony 표 5개, 가장 큰 미개봉 문"** 으로 넘겼다. 다섯 개를 전부 열었다.

| grep 적중 | 실제 정체 | 판정 |
|---|---|---|
| `table-29` = **Table 8.5** | *Parameters of the Prony series* — 3항, Gi/G0 = 0.2·0.2·0.2, τ = 100·1,000·10,000 s | ✗ **합성 검증예제** |
| `table-31` = **Table 8.7** | *Constants for viscoelastic model of NCP* — 13항 + WLF | ✓ **채굴** |
| `table-68` = **Table 16.2** | *Relaxation times and Prony coefficients of molding compound B* — 15항 | ✓ **채굴** |
| `table-121` | **책 뒤 색인 페이지**(`prony coefficients, 416`) | ✗ 표가 아니다 |
| `table-123` | **책 뒤 색인 페이지**(`Prony series, parameters of, 204`) | ✗ 표가 아니다 |

**Table 8.5 를 버린 이유** — 이 표는 재료 물성이 아니라 **ABAQUS 사용자 서브루틴을 검증하려고 지어낸 수치**다.
원문 문맥 verbatim: *"A closed-form solution of an annular polymer substrate encasing an inorganic solid bar …
is employed to verify the model … The polymer substrate is **treated as** a viscoelastic material while the inner
cylinder is **assumed to be** elastic."* 짝인 Table 8.4 의 제목도 `Material properties of **inner fiber and
coating layer**` 로 재료 정체가 없다. 가중치 셋이 전부 0.2 이고 τ 가 정확히 10년 간격인 것도 적합 결과가 아니라
격자를 손으로 놓은 흔적이다. **재료가 없는 값은 재료 카탈로그에 들어갈 자리가 없다.**

**책 뒤 색인 두 건** — FD 의 "표 5개" 는 `grep` 적중 파일 수였다. 실제로 표는 3개이고 그중 쓸 수 있는 것이 2개다.
`table-121`·`table-123` 은 `docling` 이 색인 2단 조판을 표로 오인해 만든 파일이다.
**다음 파동에 대한 교훈 — `tables/` 의 grep 적중 수는 표 수가 아니다.** 책·교과서에서는 색인이 항상 걸린다.

### 무엇을 넣었나

**(a) NCP — 비전도성 페이스트(8장, Jang & Han).** Tg 125 °C, EMC 블록 위에 부어 경화한 이중재 스트립.
인장 모드 응력완화로 얻은 **정규화 13항**이고 `E(t) = E0·[e∞ + Σ eᵢ exp(−t/τ)]`, τ 는 환산시간, 이동함수는 WLF 다.
**기준온도가 인쇄돼 있다 — T_ref = 298 K.**(= 24.85 °C. 저자가 25 °C 를 뜻한 것으로 보이지만 인쇄값은 298 K 이라 그대로 실었다.)
Table 8.6 의 `E0 = 3.25 GPa` 를 같이 넣었다 — **이 값이 없으면 무차원 eᵢ 는 차원이 없어 쓸 수 없다.**
포아송비 0.35 · CTE 65 ppm/°C · Tg 125 °C 도 같은 표에서 함께 실었다(3차원 해석에 최소한으로 필요한 짝이다).

**(b) molding compound B — BGA 오버몰드 EMC(16장, van Driel 외).** DMA + 시간-온도 중첩 마스터커브에
일반화 Maxwell 을 맞춘 **절대 15항**(Eₙ 이 MPa 로 인쇄돼 있다). **기준온도가 인쇄돼 있다 — T_ref = 25 °C.**
WLF C1 = 73.79 · C2 = 298.15 도 본문 인쇄값이다. Table 16.1 에서 Tg = 189 °C 와 CTE 두 분기를 함께 실었다.

---

## 3. 검산 — α 합 · E(0)/G(0) 재현

| 세트 | 항수 | 가중치 합 | 초기값 재현 |
|---|---:|---|---|
| **NCP 인장 13항** | 13 | **Σeᵢ = 0.9909, + e∞ 0.0091 = 1.000000 (오차 0)** | 정규화 급수라 합이 곧 재현이다 — E(0) = E0·1.000000 = **3.25 GPa**, Table 8.6 의 인쇄값과 정확히 같다 |
| **compound B 인장 15항** | 15 | (정규화 아님) | ΣEₙ = **28,022 MPa = 28.0 GPa**. **E∞ 가 인쇄되지 않아 E(0) 를 확정할 수 없다** — 급수만으로 얻는 것은 E(0) − E∞ 다 |
| **PVB 저율속 6항** | 6 | **Σgᵢ = 1.00000 → g∞ = 0** | G0 미인쇄. 순간응답은 축소다항 초탄성이 준다(같이 실었다) — 숫자로 되계산 불가 |
| **PVB 고율속 6항** | 6 | Σgᵢ = 0.96422 → g∞ = 0.03578 | 위와 같다 |

**NCP 의 합이 정확히 1.000000 으로 닫힌 것이 이번 파동에서 가장 강한 판독 증거다.** 13항 + e∞ 를 하나라도
잘못 읽었으면 소수 넷째 자리에서 어긋난다. FD 가 Chae 2010 에서 두 접근을 대조해 0.40 % 를 얻은 것과 같은 종류의
자기검산이고, 여기서는 오차가 0 이다.

**compound B 에는 두 번째 검산을 새로 세웠다 — 완화시간 축과 WLF 의 길이 대조.**
τ 가 1e−32 ~ 1e23 s 로 **55 십년**을 덮는데, 인쇄된 WLF(C1 = 73.79, C2 = 298.15, T_ref = 25 °C)로
`log a_T` 를 계산하면 Tg(189 °C)에서 −26.2, −40 °C 에서 +20.6 으로 **약 47 십년**을 움직인다.
두 축 길이가 같은 자릿수라 표와 상수가 서로 어긋나지 않는다. **원문이 이동인자표를 인쇄하지 않아
값 대 값 대조는 불가능하다** — 조건에 `checksum_vs_printed_shift_factors = NOT_POSSIBLE` 로 박았다.
(FD 가 Chowdhury 에서 `FAILED` 를 남긴 자리와 같은 칸이다. **FAILED 와 NOT_POSSIBLE 은 다르다** — 구분해서 적었다.)

**PVB 저율속 분기의 Σg = 1.000, 즉 g∞ = 0 은 오식이 아니라 인쇄된 값이다.** 두 항(g₂ = 0.898 · g₆ = 0.102)만
0 이 아니고 합이 자명하게 1 이다. 이 모형에서 PVB 는 장기에 강성이 0 으로 완전히 완화한다 — 폭발하중용
율속 모형이라 그럴 수 있으나, 장시간 해석에 그대로 쓰면 안 된다는 것을 notes 에 적었다.

---

## 4. 부호 유실을 렌더로 확인했는가 — **했다. 그리고 FD 가 본 것보다 나쁜 함정을 하나 더 찾았다**

**이번에 옮긴 표는 전부 300~350 dpi 로 렌더해 눈으로 대조했다.**

| 렌더 | 대상 | 추출 대비 |
|---|---|---|
| `ga71_t87_crop.png` | 책 Table 8.7 — NCP 13항 + WLF | **완전 일치.** 잃은 부호도 곱셈기호도 없다 |
| `ga71_t86_crop.png` | 책 Table 8.6 — E0 3.25 GPa, ν, CTE | **완전 일치.** `4.509 × 10⁻⁶` 의 ×·지수부호까지 살아 있다 |
| `ga71_t162_crop.png` | 책 Table 16.2 — 15항 | **완전 일치.** `1.00E−32` 의 마이너스가 그대로 있다 |
| `ga71_t161_crop.png` · `ga71_ch16_wlf_crop.png` | 책 Table 16.1 · WLF 본문 | **완전 일치** |
| `ga71_sam_t3_crop.png` · `ga71_sam_t4_crop.png` | Samieian Table 3·4 | **완전 일치.** `1 × 10⁻⁶` 지수 부호 살아 있다 |

**음수 Prony 항은 이번 파동에 하나도 없었다.** 40항 전부 양수이거나 인쇄된 0 이다.
(PVB 의 g₁·g₃·g₄·g₅ 는 **0 이 인쇄돼 있다** — 결측이 아니라 "이 격자점은 쓰지 않았다"는 뜻이고,
완화시간과 항수를 맞추려면 반드시 함께 실어야 해서 6항 전부를 넣었다.)

### 새 함정 — **Park 1999 는 부호를 잃는 게 아니라 숫자가 통째로 틀리게 나온다**

FD 가 찾은 함정(마이너스·곱셈기호 유실)은 **값이 모자라게** 나오는 것이라 눈에 띈다.
Park 1999 는 그보다 나쁘다 — **PDF 내장 폰트의 인코딩이 어긋나 있어 추출된 숫자가 조용히 다른 숫자로 바뀐다.**

| 항 | `docling`·`pdftotext` 가 준 값 | **350 dpi 렌더의 실제 인쇄값** |
|---|---|---|
| 표제 | `Table 0 … "from Schapery\ 0850#` | `Table 1 … (from Schapery, **1961**)` |
| τ₁ | `1E 91` | **`2E−02`** |
| E₁ | `0[83E 98` | **`1.94E+09`** |
| 단위 | `dynes:cm 1` | **`dynes/cm²`** |

규칙은 **숫자 d → d+1**, `[` → `.`, 지수 부호 → `9` 다. **모든 숫자가 1씩 밀려 나온다.**
`ga71_park99_t1_crop.png` 가 증거다. **이 문서에서 텍스트 추출값을 그대로 믿으면 전 항이 틀린다.**
다음 파동에 대한 규칙 — **Prony 표는 렌더로 대조한다**를 넘어, **표제·연도·단위가 이상하게 나오면 그 문서의 숫자는 전부 의심해라.**

### Park 1999 를 그럼에도 넣지 않은 세 이유

1. **재인용이다.** 표제가 `(from Schapery, 1961)` 이다. Table 1(PMMA 인장 11항 + Eₑ)·Table 3(폴리이소부틸렌 전단 컴플라이언스 10항)
   둘 다 Schapery 1961 의 값을 옮겨 실은 것이다.
2. **Table 2·4 는 이 논문의 역산 결과다.** 제목 verbatim: *"Prony series constants **computed** for the compliance
   functions"* — 모듈러스↔컴플라이언스 상호변환의 출력이고, 브리프 §2 의 **역산 금지**에 정면으로 걸린다.
3. **기준온도가 어디에도 없다.** 본문은 *"the tensile relaxation modulus E(t) of PMMA whose Prony series
   representation was given by Schapery (1961)"* 로 끝나고 온도를 한 번도 말하지 않는다.
   τ 가 2e−2 ~ 2e8 s 를 덮는 마스터커브인데 기준온도가 없으면 **어떤 온도의 곡선인지 알 수 없어 못 쓴다.**

---

## 5. 키가 없어 못 넣은 값 — **이동인자 `a_T` 14칸을 표로 남긴다**

브리프 지시대로 **JSON 에 넣지 않고 값과 조건을 여기 적는다.** 다음 파동이 키를 만들면 그대로 쓰면 된다.
FD 가 통째로 버렸다고 적은 Chowdhury 2019 의 두 표이고, **이번에 PDF 3쪽·7쪽을 350 dpi 로 렌더해
14칸 전부를 눈으로 확인했다**(`ga71_chow_aT_t1_crop.png` · `ga71_chow_aT_t3_crop.png`).
마이너스 부호 포함 인쇄값 그대로다.

**공통 조건** — 재료 = DB 재료 **738**(Chowdhury 2019 언더필). 출처 = `Characterization of Viscoelastic Response
of Underfill Materials`(ITherm 2019). **DB 에 이미 출처 3525 로 들어와 있고 doi 는 `10.1109/itherm.2019.8756500` 다** — 새로 만들지 말고 그 출처를 재사용해라. 무차원. tier 1(인쇄값), method = computed.
**기준온도 T₀ = 120 °C 로 두 표 모두 동일**하다.

### (a) Chowdhury Table 1 — **DMA 마스터커브의 이동인자 9칸**
붙일 Prony 세트: FD 가 넣은 `Table 2`(DMA 7쌍). 원문 캡션 verbatim:
`Table 1 - Calculated shift factor for a reference temperature of T0 = 120 °C`

| T (°C) | a(T) | log₁₀ a(T) |
|---:|---:|---:|
| 100 | 9643.91 | 3.98 |
| 105 | 964.45 | 2.98 |
| 110 | 96.45 | 1.98 |
| 115 | 9.99 | 0.99 |
| **120** | **1** | **0** |
| 125 | 0.18 | −0.75 |
| 130 | 0.036 | −1.44 |
| 135 | 0.0085 | −2.07 |
| 140 | 0.0025 | −2.59 |

### (b) Chowdhury Table 3 — **응력완화 마스터커브의 이동인자 5칸**
붙일 Prony 세트: FD 가 넣은 `Table 6/7`(완화 17쌍). 원문 본문이 *"The reference temperature were maintained as 120 °C"* 라 못박는다.

| T (°C) | a(T) | log₁₀ a(T) |
|---:|---:|---:|
| 100 | 501.18 | 2.7 |
| 110 | 50.12 | 1.7 |
| **120** | **1** | **0** |
| 130 | 0.1 | −1 |
| 140 | 0.032 | −1.5 |

**자체검산** — 두 표 모두 `log₁₀(a(T))` 열이 `a(T)` 열과 맞는다(예: log₁₀ 9643.91 = 3.984 ≈ 3.98,
log₁₀ 0.032 = −1.495 ≈ −1.5). **두 열이 서로를 검산하므로 이 14칸은 판독 오류가 아니다.**

**왜 이 값이 중요한가** — FD 가 확인했듯 이 논문의 WLF 상수 3벌은 인쇄된 이동인자를 **재현하지 못한다**
(`usable_for_shifting = false`). 그러면 **이 두 표가 이 재료의 마스터커브를 다른 온도로 옮기는 유일한 수단**이다.
17쌍·7쌍 Prony 세트가 DB 에 들어가 있는데 그것을 쓸 이동정보만 없는 상태다. **`wlf_c1/c2` 보다 이 키가 급하다는
FD 의 판단이 맞다.**

### 이번에 실제로 막힌 다른 값

| 없는 키 | 막힌 값 | 어디에 |
|---|---|---|
| **이동인자 `a_T`** | 위 14칸 | Chowdhury Table 1·3 |
| **시간축 완화계수 E(t)/G(t)** (Pa, 축 `reduced_time_s`) | Kenner 1995 Fig. 2 의 세 마스터커브(0.25 %·0.5 %·1.0 % 변형률, T_ref 100 °C) + 인쇄된 영시간계수 21.4 / 17.3 / 3.0 GPa | Prony 항이 아니라 곡선 자체 |
| **컴플라이언스 Prony(D/J 항)** | Park 1999 Table 2·4 의 PMMA·폴리이소부틸렌 컴플라이언스 급수 | 어차피 역산 결과라 키가 생겨도 못 넣는다 |

### `mechanical.relaxation_modulus_normalized` — **키는 열렸는데 첫 손님이 못 들어왔다**

브리프가 알려준 대로 DB 에 키가 실제로 생긴 것을 확인했다(`si_unit = 1`).
FD 가 1순위로 넘긴 대기 값 `out_ec/ec_baek2008_relaxation.csv` 30점(Fig. 1(a) 필름 11점 · Fig. 1(b) 기판 19점,
좌표·눈금 잔차까지 다 뽑혀 있다)을 열어 **곧바로 넣으려 했으나 넣지 않았다.**

**이유는 기준온도다.** 원문(Baek 2008, doi 10.1007/s12221-008-0117-y) 본문 verbatim:
*"Normalized **shear** relaxation moduli measured for the substrate and the film are shown in Figure 1 …
The relaxation moduli were measured by **varying the temperature from 25 to 100 °C** and the shifted
relaxation curves were assembled by the same procedure as reported in the literature [26]."*
— **시간-온도 중첩으로 조립한 마스터커브인데 어느 온도를 기준으로 옮겼는지 말하지 않는다.**
브리프 §2 의 규칙 그대로다: *"기준온도는 마스터커브의 필수 조건이다. 없으면 그 표는 못 쓴다 — 없다고 적어라."*

**해결 경로도 확인했다.** 조립 절차의 출처는 참고문헌 [26] = S. J. Hong 외, *Fiber. Polym.* **8**, 377 (2007),
doi 10.1007/BF02875826 이고, 같은 저자군의 선행연구 [20] = S. Y. Kim 외, *Polym. Eng. Sci.* **48**, 1840 (2008),
doi 10.1002/pen.21152 다. **둘 다 코퍼스에 없다.** 둘 중 하나를 확보해 기준온도를 확정하면
`ec_baek2008_relaxation.csv` 30점이 **그날 바로 들어간다** — 좌표는 이미 다 뽑혀 있고 자체검산도 끝나 있다
(x 잔차 0.006~0.009 decade · y 0.001, (a)의 처음 두 점이 정확히 (0.01, 1.000)·(0.1, 0.800)).
모드는 확정돼 있다 — **전단(shear)** 이다.

---

## 6. `source.doi` — **셋 다 채웠다. Crossref 로 확인했다**

70차에 DOI 없는 journal 출처 3건이 무결성 검사에 걸렸으므로 이번에는 넣기 전에 전부 조회했다.

| 출처 | DOI | Crossref 확인 |
|---|---|---|
| 책 8장 (Jang & Han) | `10.1007/978-1-4419-5719-1_8` | ✓ 제목·저자(Jang, Han)·수록서 일치 |
| 책 16장 (van Driel 외) | `10.1007/978-1-4419-5719-1_16` | ✓ 제목·저자 4인·연도 2010 일치 |
| Samieian 2019 | `10.1016/j.engfracmech.2019.04.006` | ✓ 제목·저자 7인·저널 일치 |

**책은 `kind = "book"` 으로 넣었고 장(chapter) 단위 DOI 를 썼다.** 책 전체 DOI(`10.1007/978-1-4419-5719-1`)를
쓰면 8장과 16장이 같은 출처로 합쳐져 **다른 저자가 다른 재료를 잰 두 표가 한 출처로 뭉친다.**
장 DOI 가 Crossref 에 실제로 등록돼 있어 그쪽을 썼다.

**§5 의 Chowdhury 는 우리가 넣는 행이 아니라 다음 파동을 위한 참고다** — 그 논문은 **이미 DB 출처 3525**
(`10.1109/itherm.2019.8756500`, ITherm 2019)로 들어와 있고 재료 738 에 붙어 있다. **새 출처를 만들지 말고 3525 를 재사용해라.**
(라이브 DB 조회로 확인했다 — 처음에 ECTC 로 짐작했다가 ITherm 이 맞는 것을 확인하고 고쳤다.)

---

## 7. 판단이 갈릴 수 있는 곳 — 넷을 미리 밝힌다

**(a) Samieian 의 PVB 값은 재인용이다.** 본문 verbatim: *"for the PVB a viscoelastic material model
**developed by Del-Linz** was used [25]"* — [25] = Del Linz 외, *Experimental Mechanics* **56**(9) 1501–1517 (2016),
doi 10.1007/s11340-016-0179-5. **원출처는 코퍼스에 없다.** FD 가 Wang 2021·Jia 2019 를 재인용이라 막은 것과
같은 상황이지만 **결정적 차이가 있다** — Wang·Jia 는 **같은 값을 서로 다르게 인쇄해 어느 쪽이 옳은지 우리가 고를 수 없었다**.
Samieian 은 충돌하는 짝이 없고, 우리가 직접 열어 350 dpi 로 대조한 인쇄값이다.
**출처는 우리가 실제로 읽은 문서(Samieian 2019)로 적고, 원출처를 `conditions.values_recited_from` 에 박았다.**
원출처를 확보하면 출처를 옮기고 값을 대조해라.

**(b) Samieian 의 Prony 에는 기준온도가 없다 — 그런데 넣었다.** 브리프 §2 의 "기준온도 없으면 못 쓴다"는
**마스터커브**에 대한 규칙이고, 이 급수는 마스터커브가 아니다. Del Linz 의 모형은 **온도 하나(20 °C)에서
율속 구간별로 두 벌**을 맞춘 것이고, 다른 온도는 시간-온도 중첩으로 **시험율속을 옮겨** 다룬다
(*"Time-temperature superposition was used to predict the behaviour of the PVB at a different temperature,
by shifting the test rate"*). 즉 **이 급수가 성립하는 온도는 알려져 있다.**
그래서 `reference_temperature_c` 대신 `temperature_c = 20` 과 `reference_temperature_printed = false` 를 함께 적었다.
Baek 2008(§5)은 반대다 — 마스터커브인데 기준이 없어서 **막았다**. 두 사례의 차이를 규칙으로 굳혀 두면 좋겠다.

**(c) compound B 의 CTE1/CTE2 라벨이 통상 규약과 반대다.** Table 16.1 의 인쇄 행 순서는 `CTE2 → Tg → CTE1` 이고,
compound B 는 CTE2 = 17, CTE1 = 62 ppm/K 다. 네 열(A 11/35 · B 17/62 · C 6/35 · 기판 z 51/239) 전부
`CTE2 < CTE1` 이며, **에폭시의 열팽창은 Tg 를 지나며 반드시 커지므로** `CTE2 = 유리상 · CTE1 = 고무상` 외의 해석은
물리적으로 불가능하다. 그 판단으로 `branch` 를 붙이되 **인쇄된 라벨 자체를 `conditions.printed_label` 에 남겨** 두었다.
값을 바꾼 것이 아니라 분기를 정한 것이고, 근거를 조건과 notes 에 통째로 실었다.

**(d) 이름이 비슷한 기존 재료가 하나 있다 — 합치지 마라.** DB 재료 **1056** 이
`Epoxy molding compound B (biphenyl, silica filler 88 wt%, Tg 128 C, **Groothuis 1995 TI**)` 다.
이번에 세우는 compound B 와 **이름은 닮았지만 다른 재료다** — 출처(Groothuis 1995 IRPS,
doi 10.1109/irps.1995.363340)도 Tg(128 vs **189** °C)도 다르다. 'compound B' 는 두 논문이
각자 익명 후보에 붙인 임시 이름일 뿐이다. **다음 중복정리 파동이 이름만 보고 합치지 않도록
여기 못을 박는다.** 같은 이유로 재료 1064~1069(`six-underfill moisture sensitivity study`)도
이 책이 아니라 별개 논문(doi 10.1109/tcapt.2008.921629)에서 온 것임을 확인했다 —
**이 책(`10.1007/978-1-4419-5719-1_*`)은 DB 에 단 한 행도 들어와 있지 않다.**

---

## 8. FD 가 센 "미채굴 8편" 이 맞았는가 — **문서 수는 맞고 채굴 가능 편수는 틀렸다**

FD 는 *"Prony 표가 실제로 있고 DB 에 없는 것이 최소 8편"* 이라고 적고 4편을 처리했다.
남은 것을 전수로 열어 본 결과는 이렇다.

- **채굴 가능했던 것 3편** — 책 8장 · 책 16장 · Samieian 2019. (책은 FD 가 1편으로 셌지만 **장이 다르면 저자·재료가 다르다** — 실질 2편이다.)
- **표가 아예 없던 것 3편** — Kenner 1995(Fig. 2 곡선뿐) · Brinson 2008(Fig. 7.19·7.21 막대그림) · Liu 2011(색인 페이지 오적중).
- **표는 있으나 넣으면 안 되는 것 1편** — Park 1999(재인용 + 역산 + 기준온도 없음 + 숫자 오염).
- **FD 가 이미 판정한 것 3편** — Haynes 2013 · Wang 2021 · Jia 2019.
- **솔버 매뉴얼 7편** — 표 적중이 있는 것은 OpenRadioss `RadiossRef_p0001 / p0501 / p1001` **3편뿐**이고,
  열어 보니 전부 **`/VISC/PRONY` 카드의 입력 서식표**(필드 이름·기본값·단위 예시)다. 재료값이 아니다.
  나머지 4편(LS-DYNA 이론서 · Radioss 이론서 · `RadiossUser_p0001` · `RadiossRef_p3501`)은 본문 적중뿐이다.

**정정된 판단** — FD 의 큰 결론(*"병목은 디지타이즈 능력이 아니라 인쇄된 Prony 표를 아무도 전수로 안 훑은 것"*)은 **맞았고,
이번 파동이 그 훑기를 끝냈다.** FD 의 61건에도, `Maxwell`·`relaxation time` 까지 넓힌 재-훑기에도
**Prony 항이 표로 인쇄돼 있고 DB 에 없는 문서는 이제 0 편이다**(아래 근거).
**다음 병목은 다른 데 있다 — 키(§5) · 그림(Kenner·Brinson) · 그리고 코퍼스 색인 자체(아래 ⚠)다.**

또 하나 정정 — FD 의 survey 표는 `grep` 적중 **파일 수**를 "Prony 행" 후보로 셌는데, 책·교과서에서는
**뒤 색인이 반드시 걸린다**(이번에 책에서 2건, Liu 2011 에서 1건). 다음 survey 는 색인 페이지를 먼저 걸러라.

**전수 재-grep 은 이렇게 끝냈다 — 그리고 도구 하나를 찾았다.**
코퍼스 전수 `grep` 을 두 번 시도했으나 둘 다 안 끝났다(`/data/paper_patent_corpus/structured` 가 **144 GB · 표 md 만 88,637개**다.
순차 grep 은 500 초에, `xargs -P 8` 병렬도 1,000 초에 못 끝냈다). 대신 **이 저장소에 이미 있는
`scripts/catalog/corpus_index.py` 의 FTS5 색인**(`/data/paper_patent_corpus/_index/corpus_fts.db`, 문서 20,692건)으로 **몇 초 만에** 끝냈다.

- **`prony` FTS 적중 57건 — 전부 FD 의 survey 61건 안에 있다. FD 가 빠뜨린 문서는 0 건이다.**
- **FD 의 survey 가 더 넓다(61 > 57).** 이유는 아래 색인 결함이다.

**그리고 §5 의 권고("`prony` 만 걸지 말고 `Maxwell`·`relaxation time` 도 걸어라")를 이번에 직접 실행했다.**
`"generalized Maxwell"` · `"relaxation times"` · `"Maxwell elements"` 로 **162건**이 걸렸고 그중
**`prony` 를 한 번도 안 쓰는 문서가 128건**이다. 그 128건의 `tables/*.md` 를 다시 걸어
완화시간류 표가 있는 것은 **8건**이었고, **여덟 건을 다 열어 본 결과 점탄성 Prony 표는 0 건이다** —
여섯 건이 **유전완화**(임피던스 분광·페라이트)이고, `Im 2019` 는 **NMR 스핀-스핀 완화시간(T₂)**,
`Halley 1996` 은 값 없는 **모형 서식표**다. 하나만 진짜 점탄성이었는데
(`Premi 2021` 쥐 뇌 LS-DYNA 카드 — Mooney-Rivlin + 전단완화계수) **생체조직이고 [43] 재인용**이라 대상이 아니다.
**따라서 "Prony 라는 단어를 안 쓰는 Prony 표"는 이 코퍼스에 없다.**

### ⚠ 그런데 그 FTS 색인이 **이번 파동 최대 수확을 통째로 놓치고 있다**

`corpus_fts.db` 에 **`2010 - Moisture Sensitivity of Plastic Packages of IC Devices` 가 아예 없다.**
같은 디렉터리(`snowball_papers/from_rel`)의 다른 문서 38건은 색인돼 있는데 이 책만 빠져 있다.
**이번 파동 99행 중 68행(재료 2종)이 나온 바로 그 문서다.** FD 의 파일 `grep` 은 잡았고 FTS 색인은 못 잡았다.

**다음 파동에 넘긴다 — `corpus_index.py build` 를 다시 돌려라.** 색인은 2026-08-15 자이고 문서 20,692건인데,
FD 의 헤더 주석은 "44,966개 md 중 고유 논문 16,007편" 이라 적는다. **책·대형 문서가 어떤 이유로 빠지는지 확인해야 한다.**
그 전까지는 **FTS 색인을 유일한 훑기 도구로 쓰면 안 된다** — 이번처럼 가장 큰 문을 놓친다.

---

## 9. 다음 배치에 넘길 것

1. **이동인자 `a_T` 키를 만들어라 — §5 에 값 14칸이 렌더 확인까지 끝난 채 표로 놓여 있다.**
   축은 `temperature_c` · `reference_temperature_c` · `set_id`(어느 Prony 세트의 이동인자인가). 무차원.
   두 파동 연속으로 같은 값이 막혔다.
2. **Baek 2008 30점의 기준온도를 확정해라.** doi `10.1007/BF02875826`(Hong 2007) 또는 `10.1002/pen.21152`(Kim 2008)를
   구하면 된다. 좌표는 `out_ec/ec_baek2008_relaxation.csv` 에 이미 있고 모드는 전단으로 확정돼 있다.
   **`mechanical.relaxation_modulus_normalized` 의 첫 손님이 이것이다.**
3. **시간축 완화계수 키(E(t)/G(t), Pa)를 만들면 Kenner 1995 가 열린다.** MP7100 몰딩컴파운드의
   마스터커브 3벌(변형률 0.25 %·0.5 %·1.0 %, T_ref 100 °C)이 Fig. 2 에 있고, **영시간계수 21.4 / 17.3 / 3.0 GPa 는
   본문에 인쇄돼 있다** — 디지타이즈 결과를 검산할 앵커가 있다는 뜻이다. 이동인자 그림(Fig. 3)도 있다.
4. **Brinson 2008 Fig. 7.19·7.21 은 Prony 계수 막대그림이다**(폴리이소부틸렌 30항 25 °C · 폴리카보네이트 28항).
   **디지타이즈하면 항 가중치가 직접 나오는 드문 그림**이지만, 원 데이터가 Catsiff & Tobolsky 1955 재인용이고
   교과서의 방법 시연이라 등급 판단이 먼저다. 손대기 전에 결정해라.
5. **책의 compound A·C 를 넣을지 정해라.** Table 16.1 에 Tg(155·108 °C)와 CTE 두 분기(11/35 · 6/35 ppm/K)가
   절대값으로 인쇄돼 있다(수분 물성은 전부 B 기준 정규화라 못 쓴다). **이번에는 Prony 가 없고 스칼라 3개뿐이라
   익명 재료를 둘 더 세우지 않았다.** 넣는다면 §7(c)의 CTE 분기 판단을 그대로 쓰면 된다.
6. **`corpus_index.py build` 를 다시 돌려라 — 색인이 이번 파동 최대 수확 문서를 놓치고 있다**(§8 ⚠).
   `corpus_fts.db` 는 2026-08-15 자 20,692건이고 `2010 - Moisture Sensitivity of Plastic Packages of IC Devices`
   가 통째로 빠져 있다. 이 색인은 **표 훑기의 유일한 실용 도구**다(전수 `grep` 은 144 GB·표 md 88,637개라 못 끝낸다).
   책·대형 문서가 왜 빠지는지 확인하고 다시 세워라.
7. **`FILMISH` 필터를 고쳐라** — EC 의 6번, FD 의 5번이 그대로 살아 있다. 세 파동째다.
8. **`digitize_curve.py` 77행(`np.linspace` → `np.geomspace`) 은 이번에도 검증하지 않았다.**
   이번 파동은 디지타이즈를 한 건도 하지 않았다(전부 인쇄된 표였다). 3·4번을 하는 배치가 확인해라.
