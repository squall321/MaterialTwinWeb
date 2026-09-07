# 66차 BC — 코어 밖 해석 격자 빈칸의 물성별 수확률

기준 DB `MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web`.
측정 시점의 해석 격자 빈칸 **5,875칸**(coverage_report 의 유효채움 잔여와 같은 수).

## 1. 5,875칸을 물성키(택일군 포함)로 갈랐다

`coverage_report.ANALYSES` 를 그대로 돌면서 구조적 부재를 뺀 빈칸을 물성키별로 셌다.
격자는 택일군을 **칸 1개**로 세므로 아래 표의 단위도 그 칸이다.

| 물성키 / 택일군 | 격자칸 | 유일 재료 | 코어7 |
|---|---:|---:|:--:|
| thermal.specific_heat | 927 | 349 | ● |
| physical.density | 841 | 116 | ● |
| thermal.conductivity | 647 | 254 | ● |
| mechanical.youngs_modulus | 621 | 155 | ● |
| mechanical.poisson_ratio | 598 | 185 | ● |
| **율속** cowper_symonds_c \| _p \| dynamic_increase_factor \| yield_strength_at_rate \| johnson_cook_c | **437** | 437 | |
| **젖음** contact_angle_water \| surface_energy | **428** | 428 | |
| **피로** fatigue_strength_coefficient \| _ductility_ \| darveaux \| morrow \| stromeyer | **312** | 312 | |
| **소성** yield_strength \| (tensile_strength + elongation_at_break) | **290** | 290 | 일부 |
| **전기** dielectric_constant \| resistivity_volume \| dissipation_factor | **232** | 232 | |
| thermal.expansion_linear | 160 | 160 | ● |
| **Prony** prony_relaxation_time \| _tensile_ \| _shear_ \| _relative_ \| shear_modulus | **154** | 154 | |
| **투습** water_vapor_transmission \| gas_permeability_h2o \| diffusion_coefficient \| water_absorption_24h \| _saturation \| moisture_absorption_equilibrium | **142** | 142 | |
| **접착** peel_strength \| lap_shear_strength \| die_shear_strength | **65** | 65 | |
| **산소** gas_permeability_o2 \| gas_solubility | 13 | 13 | |
| **산소소광** excited_state_lifetime \| stern_volmer \| bimolecular_quenching | 5 | 5 | |
| **초탄성** hyperelastic_coefficient \| _exponent | 3 | 3 | |
| **합계** | **5,875** | | |

코어7 몫 **3,794칸**(다른 배치 표적) · **코어 밖 2,081칸**이 이 배치의 표적이다.

## 2. 표본이 아니라 전수로 수확률을 쟀다 — 로컬 사본이 이미 있었다

§659 는 표적이 쓰는 출처를 **내려받아** 낱말로 거르는 통과였고 61차 WC 는 902건 다운로드에 40분을 썼다.
이번에는 내려받기 전에 `source.local_path` 가 실제로 디스크에 있는 비율을 먼저 셌다 —
**표적 물성마다 45~80% 가 이미 디스크에 있었다.** 그래서 표본 20~30건이 아니라 **전수**를 그대로 돌렸다
(pdftotext + md/html 캐시 포함 6분).

| 물성 | 표적 재료 | 그 재료가 tier≤3 으로 쓰는 출처 | 로컬 텍스트 확보 | 낱말 적중 | **수확률(확보 대비)** | 수확률(출처 전체 대비) |
|---|---:|---:|---:|---:|---:|---:|
| **접착** | 65 | 83 | 37 | 19 | **51.4%** | 22.9% |
| **투습** | 142 | 123 | 74 | 27 | **36.5%** | 22.0% |
| **소성** | 290 | 284 | 199 | 64 | **32.2%** | 22.5% |
| **전기** | 232 | 195 | 139 | 20 | **14.4%** | 10.3% |
| **율속** | 437 | 401 | 306 | 38 | **12.4%** | 9.5% |
| **피로** | 312 | 290 | 209 | 26 | **12.4%** | 9.0% |
| **젖음** | 428 | 395 | 318 | 18 | **5.7%** | 4.6% |
| **Prony** | 154 | 195 | 130 | 6 | **4.6%** | 3.1% |

비교 기준(§669) — 포아송비 7.5%(61차 WC) · 전방사율 0.7%(62차 XB).

### §658 — 우리 DB 의 `notes` 를 물성 낱말로 건 결과(30초)

| 물성 | 표적 재료 | notes 적중 행 / 종 |
|---|---:|---|
| 율속 | 437 | 734행 / 33종 (대부분 `fill_dyna_gaps` 정형문구 — §667 의 오탐) |
| 소성 | 290 | 59행 / 14종 |
| 전기 | 232 | 24행 / 16종 |
| 피로 | 312 | 13행 / 8종 |
| 투습 | 142 | 7행 / 4종 |
| 접착 | 65 | 4행 / 4종 |
| 젖음 | 428 | **2행 / 2종** |
| Prony | 154 | **1행 / 1종** |

`notes` 문은 §659 통과보다 훨씬 싸지만 이 여덟 물성에서는 §667 의 오탐률이 다시 지배했다 —
율속 734행은 거의 전부 `fill_dyna_gaps_*.py` 가 남긴 정형문구다.

## 3. 결론 — 어디를 캤고 어디는 왜 안 캤나

- **캔 곳** — 접착(51.4%) · 투습(36.5%) · 소성(32.2%). 셋 다 포아송비 7.5% 의 **네 배 이상**이다.
- **안 캔 곳** — 젖음(5.7%) · Prony(4.6%). 전방사율(0.7%)만큼 낮진 않지만 **문의 종류가 다르다**:
  - **젖음(접촉각·표면에너지, 428칸)** — 벤더 시트도 재료 논문도 이 열을 안 찍는다.
    이 물성이 사는 문서는 **표면처리·플라즈마/코로나 장비 벤더의 응용노트**와 **잉크·라미네이션 공정 규격**이다.
    재료의 물성이 아니라 **공정의 결과**로 발표되기 때문이다.
  - **Prony(154칸)** — 완화 스펙트럼은 표가 아니라 **그림(마스터커브)**으로 발표된다.
    적중 6건 중 표로 상수를 찍은 것은 없었다. 이 표적의 문은 새 문서가 아니라 **§652 의 디지타이즈**다.
  - **율속(437칸)·피로(312칸)** — 12.4% 로 중간이다. 적중의 대부분이 "이 논문이 율속을 언급한다" 이지
    "이 등급의 상수를 찍는다" 가 아니다. 이 둘은 **§659 통과가 아니라 모델상수 전용 논문 표적화**(§664)가 맞다.
