# 58차 TE — Maleki 1999 전수 채굴 (작업 기록)

표적 — `Thermal Properties of Lithium-Ion Battery and Components`, JES 146(3) 947-954,
doi `10.1149/1.1391704`. 56차 RA 인계. **DB 에 출처가 없던 완전 미채굴 논문**
(`mined_index.py --doi … --title …` → `null`, 폐기 대장에도 없다).

원본 — `/data/paper_patent_corpus/snowball_papers/from_expert/Maleki - 1999 - Thermal Properties of Lithium‐Ion Battery and Components.pdf` (9쪽)

## 0. 결과 한 줄

**재료 3종을 세우고 물성 51행을 넣었다.** 기각 2칸. 표 여섯을 전부 400 dpi 렌더로 다시 읽었다.
battery 계통 V5 는 6 → 6 으로 그대로다(새 코어 21칸 중 9칸 채움 · 12칸 V2 선언).

## 1. 첫째 산출물 — 재료를 세운다. `role='product'` · `subsystem='battery'`

**근거를 먼저 적고 실행했다.**

1. **상용품이다.** 원문 verbatim — 셀은 `the commercially available Sony US-18650 cylindrical
   lithium-ion cell, which has a nominal capacity of 1.35 Ah`, `retrieved from a double-battery pack
   used in Sony Camcorders, purchased in September, 1996, from the Sony Products Store`.
   **브리프 115 — "상용품을 논문이 측정한 것도 product 다."**
2. **evidence 지문에 하나도 안 걸린다**(브리프 115·193). 이름에 조성비도 시료 라벨도 없고,
   파라미터 시리즈의 한 점도 아니고, 실험실 배합도 대조군도 아니다.
   `out_of_scope`(다른 도메인의 실제 제품)도 아니다 — 스마트폰 배터리 열해석의 정중앙이다.
3. **활물질 분말이 아니라 적층 그 자체다**(브리프 160). 집전체 + 양면 합제층이고
   Table I 이 박 두께(Al 0.02 · Cu 0.018 mm)까지 인쇄한다.
4. **카탈로그에 이미 같은 계보가 서 있다**(브리프 612 — 이미 복제된 계보가 있으면 그 계보를 따른다).
   재료 2524·2525(18650 NCA 셀 분해 전극) · 2553·2554(40 Ah 파우치셀 합제층)가
   전부 `role=product` · `subsystem=battery` · `material_class="coated composite electrode …"` 다.
   2524 의 `role_reason` verbatim — *"상용 18650 셀에서 분해해 낸 실부품 전극. 활물질 분말이 아니라
   집전체+합제층 적층 그 자체다(브리프 160)"*.

세운 것 셋 —

| id | 이름 | 비고 |
|---|---|---|
| **2691** | Li-ion positive electrode, LiCoO2 on Al foil, dissected from Sony US-18650 cell (Maleki 1999) | |
| **2692** | Li-ion negative electrode, graphitic carbon on Cu foil, dissected from Sony US-18650 cell (Maleki 1999) | 원문 XRD — `moderate-range graphitic hard carbon`, 20~45 µm 플레이크 |
| **2693** | Li-ion PE/Sp/NE stacked layer assembly, dissected from Sony US-18650 cell (Maleki 1999) | `role_confidence: medium` |

**2693 만 confidence 를 낮춘 이유** — 단일 소재가 아니라 적층체의 **유효값**이다.
셀 수준 열해석 입력으로는 정당하지만 재료끼리 비교·순위·카드추출하면 틀린다
(방법론 §4.3 의 `소자 유효 열전도율을 재료 키에 담았다` 주의와 같은 갈래).
그 사실을 `attributes.verdict_effective_property_of_assembly` 에 박았다 — `verdict_` 접두어라 운영까지 간다.
**전해액 유무는 재료를 나누지 않고 조건축 `electrolyte` 로 갈랐다**(규칙 5) — 재료를 넷으로 쪼개면
코어 빈칸이 7칸 더 늘 뿐 값이 나아지지 않는다.

## 2. 세우지 않은 것 — 그리고 값을 어디에 남겼나

전부 재료 2693 의 `attributes.verdict_unregistered_printed_values` 에 표 위치·값과 함께 적었다
(브리프 609·623 — 판정은 자리·독자·전파가 있어야 한다. `verdict_` 는 전파된다).

| 안 세운 것 | 인쇄된 값 | 사유 |
|---|---|---|
| **Sony US-18650 셀 전체** | Table III — Cp 1.04 ± 0.034(OCV 3.75 V) · 0.96 ± 0.018(2.75 V) J/(g·K), 단열열량계 9회 | 셀은 재료가 아니라 **소자**다. 세우면 코어 7칸 중 넷(E·ν·UTS·CTE)이 영원히 빈다 |
| **분리막** | Table I — 질량 1.28 g · 1192.0 x 59.2 x 0.025 mm | **Table IVa·IVb 에 분리막 행이 없다.** ρ·Cp·k 가 인쇄되지 않아 코어 0/7 로 서게 된다. 치수로 밀도를 내면 역산이다(규칙 2) |
| **교정 기준시편 2종** | Table II — Al Cp_av 0.92 · type 416 SS Cp_av 0.46 J/(g·K) (CRC 0.900·0.460 대조) | 열량계 교정용 기준시편이고 두 재료가 카탈로그에 없다 |
| **Table V 의 Chen·Kanari 열** | PE 2.920/1.134/2.18 · 1.410/1.184/1.40 등 | **2차 인용**(규칙 4) |
| **Table V 의 `This Work` 열** | PE 3.115/0.601/2.49 · NE 1.622/0.623/1.20 | Table IVa 의 OCV 3.75 V 두께방향과 **글자까지 같다.** 비교표의 재인쇄라 중복이다(브리프 456 — 611 의 "장이 달라 다시 인쇄한 선언" 이 아니다) |

## 3. 표별로 무엇을 넣었나 (51행)

**Table I**(치수·질량) → `structure.layer_thickness` 5행.
PE 총두께 0.185 mm · Al 박 0.02 mm · NE 총두께 0.198 mm · Cu 박 0.018 mm · 적층 0.42 mm(본문 `ca.`).
질량은 재료 물성이 아니라 안 넣었다. **이 표는 렌더가 아니면 한 칸도 못 읽는다**(4절).

**Table II**(교정) → 0행. 2절 참조.

**Table III**(셀 Cp) → 0행. 2절 참조. 표 자체는 검산했다 — 4회 평균 1.039 → 인쇄 1.04 ✔ ·
5회 평균 0.9644 → 인쇄 0.96 ✔.

**Table IVa(두께방향) · IVb(면내)** → 46행.

| 열 | 키 | tier · method | 근거 |
|---|---|---|---|
| ρ | `physical.density` | **3 · computed** | 이 논문의 실측이 아니다 — 5절 |
| Cp | `thermal.specific_heat` | **3 · computed** | 〃 |
| α | `thermal.diffusivity` | **1 · measured** | 크세논 플래시(Oak Ridge HTML) 직접 측정. 이 논문의 유일한 실측 열 |
| k | `thermal.conductivity` | **1 · computed** | 초록 verbatim `k was calculated from k ≡ αρCp`. 이 시편에 대해 인쇄된 실험 결과라 tier1, 계산이라 computed(브리프 622) |

조건축 — `direction`(through-thickness / in-plane, 카탈로그 어휘) + `direction_verbatim`(cross-plane / in-plane, 원문) ·
`open_circuit_voltage_v`(2.45 / 3.75) · `electrolyte`(2693 만) · `specimen`(Fig. 6b 면내 육면체 / Fig. 6c 원판) ·
`measurement_table` · `uncertainty_printed` · `test_method`.
**ρ·Cp 를 표마다 따로 넣은 이유** — IVa 와 IVb 는 시편이 다르다(면내용 육면체 대 두께방향용 원판).
PE 3.115 대 3.121 · NE 1.622 대 1.620 처럼 값이 다르게 인쇄되므로 별개 측정이다.

**Table V** → 0행. 2절 참조.

## 4. 렌더에서만 잡힌 손상 — RA 가 인계한 한 칸 말고 더 있었다

**표 여섯 전부를 400 dpi(`pdftoppm -png -r 400`) 로 열었다.** 결과 —

| 표 | 렌더에서만 잡힌 것 |
|---|---|
| **Table I** | **16칸 전부가 깨져 있다.** `115.211`=15.2 · `119.101`=9.10 · `1011.281`=1.28 · `1192.010`=1192.0 · `1059.210`=59.2 · `0110.025`=0.025 · `110.185`=0.185 · `110.021`=0.02 · `113.911`=13.9 · `117.351`=7.35 … |
| **Table II** | `198.52`=**98.52** · `194.51`=**94.51** — **이 줄에는 `±` 가 없다** |
| Table III | 깨짐 없음(추출과 렌더가 일치) |
| Table IVa | 깨짐 없음 |
| **Table IVb** | NE 면내 k `18.72`=**8.72**(RA 인계분) · ρ `2.781`=**2.78** · α `10.115`·`10.090`·`10.058` = `0.115`·`0.090`·`0.058` |
| Table V | 깨짐 없음 |

**RA 가 넘긴 한 칸(8.72) 말고도 Table I 16칸과 Table II 2칸이 더 있었다.**
그리고 **원인 귀속이 틀려 있었다.** RA 는 앞자리 `1` 을 `±` 글리프 손상으로 읽었는데,
Table II 의 `198.52`·`194.51` 은 그 줄에 `±` 가 없고 Table I 은 표 전체에 `±` 가 없다.
실제 대응은 **`1` = 정렬 공백 · `+`** 이고 `±` 는 따로 **`6`**, `=` 는 **`5`** 다
(`PE/Sp/NE 1 electrolyte` = `PE/Sp/NE + electrolyte`, `OCV 5 2.45 V` = `OCV = 2.45 V`,
`13.45 6 0.1` = `13.45 ± 0.1`).
→ **오른쪽 정렬된 숫자 열 전체가 용의자다.** BRIEF_DRAFT 첫 절.

## 5. ρ·Cp 열의 계보 — 이 논문의 실측이 아니다

6쪽 `Thermal conductivity, method 2, from thermal diffusivity measurement` 절 verbatim —

> the thermal conductivity may be calculated from the product of α with the effective density ρ and
> the effective Cp. **The latter may be calculated from mass-fraction-weighted values of Cp and ρ for
> each component (PE, NE, and/or Sp, taken from Ref. 3 and 8)** as shown in Eq. 6

Ref. 3 = Chen & Evans, Ref. 8 = Kanari(둘 다 Table V 의 비교 대상이다).
**즉 ρ·Cp 는 2차 인용 성분값을 질량분율로 섞은 저자 계산값이다** → 규칙 4 대로 **tier3 · computed**.
표 머리글에도 캡션에도 이 말이 없고, 항등식이 닫히니 네 열이 다 실측처럼 보인다.
**항등식은 내부 정합만 증명하지 계보를 증명하지 않는다.**

## 6. 검산 — `k = α·ρ·Cp` 16칸 전수

```
tab  mat           dir         OCV     k_calc  k_print     dev%     a_back
IVa  PE            cross-plane 2.45     2.321     2.33    -0.37
IVa  PE            cross-plane 3.75     2.490     2.49    -0.00
IVa  NE            cross-plane 2.45     0.889     0.89    -0.08
IVa  NE            cross-plane 3.75     1.203     1.20     0.21
IVa  PE/Sp/NE      cross-plane 2.45     1.895     1.90    -0.25
IVa  PE/Sp/NE      cross-plane 3.75     2.369     2.36     0.39
IVa  PE/Sp/NE+el   cross-plane 2.45     3.396     3.39     0.18
IVa  PE/Sp/NE+el   cross-plane 3.75     3.430     3.40     0.89
IVb  PE            in-plane    2.45    21.607    21.57     0.17
IVb  PE            in-plane    3.75    21.795    21.75     0.20
IVb  NE            in-plane    2.45     8.719     8.72    -0.01   <- 8.72 확정(18.72 아님)
IVb  NE            in-plane    3.75    15.113    15.11     0.02
IVb  PE/Sp/NE      in-plane    2.45     1.770    17.69   -90.00   <- a 칸 10배 오식(기각)
IVb  PE/Sp/NE      in-plane    3.75    24.677    24.66     0.07
IVb  PE/Sp/NE+el   in-plane    2.45    20.606    20.06     2.72   <- a 칸 기각, k 유지
IVb  PE/Sp/NE+el   in-plane    3.75    28.067    28.05     0.06
```

**14/16 이 0.9% 안에서 재현된다.** 기각 2칸은 아래.

**초록 배수 서술 대조** — `the in-plane k value is nearly one order of magnitude higher than the cross-plane k`.
PE 9.26·8.73 · **NE 9.80**·12.59 · 적층 9.31·10.45 · 전해액 5.92·8.25.
NE 면내를 18.72 로 읽으면 **21배**라 초록이 깨진다 — 8.72 를 본문이 확정한다(브리프 60·105).

**Table I 로 본 밀도 독립 검산** — PE 15.2 g/(521.1×52.9×0.185 mm) = 2.98 g/cm³(인쇄 3.115, −4.5%) ·
NE 9.10 g/(534.0×56.0×0.198) = 1.54(인쇄 1.622, −5.2%). **둘이 같은 방향이라 계통 차이**이고
XFT 시편이 압축 상태로 측정되기 때문이다. 한 칸의 손상이 아니다.

**혼합률 검산(Eq. 6 을 행 사이에 건다)** — 본문 두께(PE·NE 0.19, Sp 0.020 mm) 기준.
`ρ` 는 분리막 0.8 g/cm³ 에서 2.290 이 정확히 재현된다(**닫힌다**).
`Cp` 는 이 논문 자신의 PE 0.601·NE 0.623 으로 상한이 0.64 인데 인쇄가 1.089 다 —
**인쇄값을 내려면 분리막 Cp 가 25 J/(g·K) 여야 해서 불가능하다.**
Table III 셀 전체 Cp 0.96~1.04 와 Table V 의 Chen·Kanari 넷이 다 PE·NE 값보다 높고
저자도 `Our Cp values are lower than their values` 라 적는다.
**어느 칸이 오염인지 우리가 고르지 않았다**(브리프 443) — 인쇄값을 두고 tier3 으로 내린 뒤
모든 Cp·k 행 notes 에 이 모순과 `k 가 같은 편향을 물려받는다` 를 적었다.

## 7. 기각한 칸 둘 — 재료 2693 `attributes.verdict_rejected_printed_cells`

**둘 다 `thermal.diffusivity` 의 면내 OCV 2.45 V 칸이고, 같은 행의 ρ·Cp·k 는 살렸다**(브리프 141).

- **전해액 없음** — 인쇄 `0.0071 ± 0.0040 cm²/s`. 항등식이 k = 1.77 을 내는데 인쇄 k 는 17.69 다(정확히 10배).
  **렌더로 확인했으므로 추출 손상이 아니라 원문 자체의 소수점 오식**이다.
  `±` 가 이것을 지지한다 — 0.0040 은 0.0071 의 56% 이고 0.071 의 5.6% 인데,
  형제 행은 3.5%·1.9%·1.7% 다. **56% 오차를 붙여 발표하는 표는 없다.**
  그래도 0.071 을 집어넣지 않았다(규칙 1·2).
- **전해액 채움** — 인쇄 `0.058 ± 0.0010`. 항등식이 20.61 인데 인쇄 k 는 20.06(2.7%).
  같은 재료 OCV 3.75 V 행이 0.06% 로 닫혀 ρ = 2.78 · Cp = 1.278 은 확정이므로 용의자는 α 와 k 둘인데
  항등식으로는 못 가른다. **본문이 갈랐다** — `increases … but only by 13%, and similarly for a cell at
  OCV = 3.75 V (Table IVb)` 에서 20.06/17.69 = 13.4% · 28.05/24.66 = 13.7% 로 `similarly` 가 성립하고,
  α = 0.058 이 맞다면 16.5% 가 돼 문장이 깨진다(브리프 60 의 비율판). **k 를 살리고 α 만 버렸다.**

**자리를 한 번 옮겼다.** 처음에 `core_rejected_printed_value` 에 적었더니 `verdicts_check.py` 가
*"선언했는데 값이 있다"* 로 잡았다. 맞는 지적이다 — 기각은 **조건이 다른 8칸 중 2칸**이고
`thermal.diffusivity` 는 CORE7 이 아니라 커버리지가 세지도 않는다.
`te02_alpha_reject_verdict.json` 으로 `verdict_rejected_printed_cells` 로 옮겼다
(`core_rejected_printed_value_before_correction` 에 옛 값이 남는다 — 브리프 594).

## 8. 코어 빈칸 판정 — 새 재료 3종의 E·ν·UTS·CTE 12칸

`core_absent_from_vendor_sheet`(V2). 근거는 둘을 겹쳤다.
① **붙일 벤더 시트가 원리적으로 없다** — 분해품이라 제조사·등급 비공개(브리프 58).
② **그 시편을 잰 유일한 문헌 전권 낱말 검색이 0건**(브리프 613) —
`Young` 0 · `modulus` 0 · `Poisson` 0 · `tensile` 0 · `strength` 0 · `elastic` 0 · `stress` 0 · `hardness` 0,
`expansion` 1건은 `expansion of the c lattice parameter` 라 선팽창이 아니다.

**신규 재료라 `apply_core_verdicts.py` 를 안 거쳤다** — `new_material.attributes` 에 넣으면
적재기가 그대로 쓴다(브리프 610 의 캐시 덮어쓰기 자리를 아예 안 지난다).

## 9. 검사 (적용 전 스냅샷 대 적용 후 라이브)

- `integrity_check.py` — **두 출력이 카운트 줄 하나만 다르다**(재료 2660→2663 · 물성값 41703→41754 ·
  출처 2960→2961). **신규 위반 0.** `이상 1개` 는 선재고(물성값 0인 재료 2종).
- `verdicts_check.py` — **이상 0개.** 7절의 어긋남 1건을 고쳐 내 것은 0이 됐다
  (남은 1건은 재료 229 Doosan — 다른 배치 것이라 손대지 않았다).
- `pytest -q` — **366 passed, 1 skipped**(기준선).
- `coverage_report.subsystem_core()` battery — 전 `n_mat 38 · filled 130 · cells 266 · V2 63 · V5 6`,
  후 `n_mat 41 · filled 139 · cells 287 · V2 75 · V5 6`.
  **선언 12칸 = 집계 증가 12칸**(브리프 610 의 대조). **V5 는 전체도 738 → 738 로 그대로다.**

## 10. 신고만 한 것 (고치지 않았다)

- **56차 RA 인계문의 한 낱말이 틀렸다** — *"PE·NE·분리막·적층을 직접 잰"* 이라 적혔는데
  **Table IVa·IVb 에 분리막 행이 없다.** 경로·표 검산은 정확했다(브리프 592).
- **§603 곁가지의 원인 귀속이 틀렸다** — 앞자리 `1` 은 `±` 손상이 아니라 공백·`+` 손상이다(4절).
  브리프 본문은 조정자가 고칠 자리라 여기 적기만 한다.
- `normalize_tiers.py` 는 돌리지 않았다 — 공유 도구이고 이 배치의 tier3·computed 행을
  건드릴 이유가 없다(승격 조건이 `method=measured` 다).

## 11. 산출물

```
backend/scripts/catalog/out_te/te01_maleki1999_sony18650.json   재료 3 · 물성 51행
backend/scripts/catalog/out_te/te02_alpha_reject_verdict.json   판정 자리 이동 1종
backend/scripts/catalog/out_te/BRIEF_DRAFT.md                   교훈 초안 7절(번호 비움)
backend/scripts/catalog/out_te/context-notes.md                 이 파일
```
