<!-- 75차 KB 수집 배치 보고서 — Elite Material 카드 없는 34등급을 로컬 43장 전수에서 세운다 -->

# 75차 KB — 카드 없이 앉아 있던 34등급을 전부 세웠고, 이 벤더의 열린 코어7 칸은 0 이 됐다

**한 줄 답: 74차 JB 가 내려받아 두고 카드로 세우지 않은 Elite Material 34등급을 전부 세웠다. 코어7 68칸이 값으로 차고 170칸이 부재판정으로 닫혀 이 벤더의 열린 칸은 43종 전부에서 0 이다. 새로 받은 문서는 0건 — 전부 로컬에 있었다.**

**수확: 신규 카드 34장 · 물성 1,011행** — 전부 **t1 / measured**, t2·t3·t4 **0건** · 자체검증 신규 이상 **0**
**판정 170칸**(34장 × 다섯 키, 태어날 때부터 박음)
**라이브 DB 쓰기 0** — 읽기는 `mode=ro` URI 로만, 적재 리허설은 `snapshot_db.py` 사본에서만 했다(라이브 재료 2,784 · 물성값 46,709 · 출처 3,129 는 배치 전후로 바뀌지 않았다)

| | 값 |
|---|---:|
| 연 문서 | **43건** (전부 로컬 · **신규 다운로드 0**) |
| 그중 값을 낸 문서 | **34건** |
| 인쇄값 역검산 | **843토막 / 불일치 0** (JSON 의 `원문 verbatim` 을 원문 텍스트에 다시 대조) |
| 적재 리허설 | `ok 1011 / new_mat 34`, 실패 0 · 유실 0 |
| 무결성 | 사전 **이상 1개** → 사후 **이상 1개** (**신규 0**; 남은 1개는 이 배치 이전의 「물성값 0인 재료 2종」) |

---

## 0. 격자가 어떻게 움직였는가 — 실측

`role=product` 이면서 이름이 `Elite Material` 로 시작하는 카드만 센 수다.

| | 재료 | 코어7 칸 | 채운 칸 | 판정된 칸 | **열린 칸** |
|---|---:|---:|---:|---:|---:|
| **이전** | 9 | 63 | 28 (44 %) | 35 | **0** |
| **이후** | **43** | **301** | **96** (32 %) | **205** | **0** |

**채움 %가 44 → 32 로 내려간 것을 감추지 않는다.** 신규 34장이 코어7 칸을 238개 더하는데 그중 값으로 차고 태어나는 것은 **68칸(34 × 2)** 뿐이다 — 이 벤더 시트가 코어7 중 인쇄하는 것은 **열전도율과 CTE 둘뿐**이기 때문이다. 나머지 다섯은 43장 어디에도 없어 판정으로 닫았다.

**대신 「진짜 남은 것」은 43종 전부에서 0 이 됐다.** 다음 파동이 이 벤더를 다시 표적으로 셀 자리가 없다.

---

## 1. 카드가 몇 장 섰는가 — **0 장이다. 왜인지 적는다**

브리프가 정의한 「카드」(밀도 + 영률 + 포아송비 세 칸이 다 찬 것)는 **한 장도 서지 않았다.** 예고된 결과이고, 이유는 벤더에 있다.

```
$ grep -lio "density|gravity|Young|Poisson|tensile|specific heat" *.txt   # 43장, 낱말 단위
density 0장 · gravity 0장 · specific heat 0장 · Young 0장 · tensile 0장 · Poisson 0장
```

**이 벤더는 밀도를 인쇄하지 않는다.** 68차 DC 가 다섯 등급에서, 74차 JB 가 43장 전수로 확인했고, 75차 KB 가 같은 43장을 다시 낱말 단위로 훑어 같은 결과를 얻었다. 영률·포아송비·비열·인장강도도 같다. **동장적층판 데이터시트의 관례 자체가 그렇다** — 72차 HD 가 Sumitomo 에서 세운 「동박을 붙이면 밀도 행이 사라진다」와 같은 자리다.

그래서 이 배치의 수확은 카드 수가 아니라 **코어7 68칸 + 판정 170칸**이다. 34장 전부가 **2/7 로 태어나고 나머지 5/7 에 사유가 박힌 완결된 카드**다.

---

## 2. 신형 등급에서 Flexural Strength 밖의 강도축을 만났는가 — **만났다. 다만 강도가 아니라 탄성률이다**

브리프의 질문에 숫자로 답한다. **43장 전수의 기계축은 셋뿐이다.**

| 기계축 | 43장 | 이 배치의 34장 |
|---|---:|---:|
| `Flexural Strength` (MPa) | 31 | 25 |
| `Flexural Modulus` (GPa) | 10 | 7 |
| **굽힘 행 자체가 없음** | **2** | **2** |

- **`Flexural Modulus` 를 인쇄하는 것은 저손실·IC기판 신형 등급 열 장**이다 — `EM-526` · `EM-528` · `EM-528K`(JB 가 이미 담음) · **`EM-A50` · `EM-S370(Z)` · `EM-S376` · `EM-S526` · `EM-S530` · `EM-S530K` · `EM-S570`**(이 배치). 68차 DC 의 *"이 벤더의 강도축은 Flexural Strength 하나다"* 는 이 등급들에 대해 **성립하지 않는다.**
- **그래도 영률 칸은 못 채운다.** 열 장 전부 시험법 칸이 `IPC-TM-650 2.4.4`(3점 굽힘)다. **굽힘탄성률을 `mechanical.youngs_modulus` 로 옮기지 않았고**, 전부 `mechanical.flexural_modulus` 에 `test_standard`·`test_mode`·`strength_property` 를 박아 넣었다. 68차 DC 가 Panasonic 여섯 등급에서 굽힘값을 영률 칸에 넣었다가 진짜 인장값과 12~23 % 어긋나 열두 행을 되돌린 자리다.
- **`EM-S570` 은 `Warp` 한 행만 인쇄한다**(30~32 GPa). `Fill` 열이 아예 없다 — 형제 등급의 Fill 값을 옮기지 않았다.
- **굽힘 행이 아예 없는 두 장은 `EM-A70K` 와 `EM-S532K`** 다. 둘 다 `Preliminary` 표기이고, 이 카드들의 기계축은 `Peel Strength` 하나뿐이다. 카드 `attributes.vendor_sheet_missing_flexural_rows` 에 박았다.

**강도축으로 오해하기 쉬운 것 하나를 갈라 둔다** — 43장 중 열 장이 `Electric Strength | >40 | kV/mm` 를 인쇄한다. 이름에 `Strength` 가 들었지만 **절연파괴 전계(IPC-TM-650 2.5.6.2)**이지 기계 강도가 아니다. `electrical.dielectric_strength` 에 `bound: lower` 로 담았다(이 배치 8장 · 4.0e7 V/m).

---

## 3. 이 배치가 실제로 잡은 함정 셋

### 3-1. **`pdftotext` 가 위첨자를 납작하게 떨어뜨린다 — `>1010` 은 `>10¹⁰` 이다**

74차 JB 가 남긴 「구(句) 검색이 거짓 음성을 낸다」와 **같은 도구의 다른 실패**다. 이번 것은 거짓 음성이 아니라 **거짓 값**이라 더 나쁘다.

```
$ pdftotext -layout EMC_EM-285_Datasheet_20240716.pdf -
    Volume Resistivity      >1010    MΩ-cm    C-96/35/90    2.5.17.1
    Surface Resistivity      >109     MΩ      C-96/35/90    2.5.17.1
```

**`1010` 과 `109` 를 값으로 읽으면 각각 일곱·여덟 자릿수가 틀린다.** `-bbox-layout` 으로 기하를 보면 정체가 드러난다.

```xml
<word yMin="577.900" yMax="589.900">&gt;10</word>   ← 본문 (높이 12.0)
<word yMin="576.910" yMax="584.950">10</word>       ← 위첨자 (높이 8.0, 0.99 위로 올라감)
```

43장 전부 같은 꼴이고 지수도 전부 같다(체적 10¹⁰ MΩ·cm · 표면 10⁹ MΩ). **32장에서 64행을 회수했다** — 환산은 1e10 MΩ·cm × 1e6 = 1e16 Ω·cm = **1e14 Ω·m**, 1e9 MΩ = **1e15 Ω**. 부등호 하한이라 전부 `bound: lower` 다.

> **규칙으로 남긴다 — `pdftotext -layout` 에서 지수처럼 생긴 붙은 숫자를 보면 `-bbox-layout` 으로 y 좌표와 글자높이를 봐라.** 68차 DC·74차 JB 가 이 벤더 43장을 두 번 훑고도 저항률 두 행을 못 담은 것이 이 탓이다.

### 3-2. **`attributes` 이름에 `absent` 를 쓰면 집계가 그것을 판정으로 읽는다**

첫 리허설에서 **「집계가 못 읽는 판정 속성 5건」**이 새로 떴다. 원인은 내가 붙인 메모 이름이다 — `resistivity_rows_absent` · `flexural_rows_absent` · `water_absorption_row_absent`.

`integrity_check.py:unreadable_verdict_attrs()` 는 이름에 `absent|not_applicable|rejected_printed|no_public` 이 든 속성을 **전부 판정으로 읽고** 허용 넷(`core_not_applicable` · `core_absent_from_vendor_sheet` · `core_rejected_printed_value` · `core_no_public_document`)이 아니면 「집계가 모르는 이름」으로 센다. **판정이 아닌 메모가 판정 자리에 앉은 것**이다.

셋을 `vendor_sheet_missing_*` 로 바꿔 0건이 됐고, **생성기에 같은 정규식으로 자기검사를 박아** 다음 파동이 되풀이하지 않게 했다(`kb75_gen.py` 의 `VERDICT_LIKE` 검사 — 걸리면 생성이 멈춘다).

### 3-3. **한 벤더가 피일강도를 단위 셋으로 인쇄한다**

`lb/in` 59행 · `kg/cm` 8행 · `kN/m` 1행. 섞어 쓰면 **1000배·5.6배 사고**가 난다.

- `lb/in` — 표준 CCL 등급 전부. × 175.126835
- `kg/cm` — **IC 기판용 `EM-S` 계열만**(`EM-S370(Z)` · `EM-S376` · `EM-S526` · `EM-S530` · `EM-S530K` · `EM-S570`). kgf 기준이라 9.80665 N / 0.01 m = **× 980.665**
- `kN/m` — **`EM-S532K` 한 장뿐.** × 1000

전부 `notes` 에 원값·환산식·역산 검산을 적었다.

---

## 4. 담은 것 — 34장 1,011행의 구성

| 물성키 | 행 | 비고 |
|---|---:|---|
| `thermal.expansion_linear` | 204 | **코어7.** X/Y 두 행 + Z 의 <Tg·>Tg 를 각각 `bound` 두 행 |
| `thermal.conductivity` | 34 | **코어7.** 전부 ASTM D5470 |
| `electrical.dielectric_constant` | 119 | 주파수 × 수지함량(50/55/70 %) × 시험법(Cavity·SPC) 로 갈라 각 행 |
| `electrical.dissipation_factor` | 119 | 〃 |
| `mechanical.flexural_strength` | 100 | 25장 · 인쇄 구간을 `bound` 두 행 |
| `thermal.glass_transition` | 78 | TMA·DMA 두 행 + DSC 값이 인쇄된 10장 |
| `interface.peel_strength` | 68 | 포일·조건별. 단위 셋(§3-3) |
| `thermal.time_to_delamination` | 62 | T288, 전부 부등호 하한 |
| `thermal.flammability_ul94` | 34 | V-0 |
| `thermal.decomposition_temp` | 34 | Td (TGA 5 % W.L) |
| `chemical.water_absorption_24h` | 33 | `EM-S570` 은 행 자체가 없다 |
| `electrical.resistivity_volume` | 32 | **위첨자 회수**(§3-1) |
| `electrical.surface_resistivity` | 32 | 〃 |
| `thermal.expansion_total` | 28 | Z-axis Expansion. `EM-S` 계열 6장은 행이 없다 |
| `mechanical.flexural_modulus` | 26 | 7장 |
| `electrical.dielectric_strength` | 8 | **이 벤더에서 처음 담는 행**(§2) |

**규율 점검 넷.**

1. **인쇄 구간은 전부 두 행이다.** `35~40`·`510~570`·`24~26` 전부 `bound: lower`/`upper` 두 행이고 **평균·중앙값 0건**이다.
2. **부등호는 전부 하한 한 행이다.** `>60 min.`·`>10¹⁰`·`>40 kV/mm` 에 상한 행을 만들지 않았다.
3. **`Tg(DSC)` 가 `N/A` 로 인쇄된 22장은 DSC 행을 만들지 않았다.** DSC 행 자체가 없는 2장(`EM-285`·`EM-S570`)도 같다. TMA·DMA 는 서로 다른 시험이라 두 행으로 갈랐다.
4. **역산 0건.** 모든 값이 인쇄 칸 하나에서 단위환산만 거쳐 나왔고, `notes` 에 원값·환산식·되돌림 검산이 적혀 있다. **843토막을 원문 텍스트에 다시 대조해 불일치 0** 을 확인했다.

**시험모드는 판정 창 안에 적었다** — `test_standard`·`test_mode`·`method_detail`·`test_geometry`·`strength_property`·`test_condition` 을 썼다(73차 IA 가 실측한 대표값 선택기의 창).

---

## 5. 판정 170칸을 어떻게 냈는가 — **JB 의 사유문 생성기를 그대로 불러 썼다**

`kb75_gen.py` 는 `jb74_gen.em_absent_reason()` 을 **import 해서 호출한다**(복붙이 아니다). 그 위에 KB 가 **등급별 실측 행 구성**을 덧댄다 — JB 의 사유문은 이 벤더의 *표준* 행 목록을 쓰는데, 실제로는 등급마다 행이 다르기 때문이다(Z-axis Expansion 없는 6장, 저항률 없는 2장, 굽힘 없는 2장, 흡수율 없는 1장, Electric Strength 있는 8장).

**판정은 `{물성키: 사유}` dict 로 `core_absent_from_vendor_sheet` 에 넣었고, 신규 카드라 `new_material.attributes` 에 태어날 때 실린다.** 별도 판정 JSON 을 내지 않은 이유는 하나다 — **`apply_core_verdicts.py` 는 `material_id` 를 요구하는데 이 34종은 아직 라이브에 없다.** 사본 리허설의 id(2815~2848)를 파일에 적으면 라이브 적재 순서가 한 칸만 달라도 **엉뚱한 재료에 판정이 박힌다.** 적재기가 `attributes` 를 그대로 넣는 것을 사본에서 확인했다(34종 × 5칸 = 170칸 병합, 누락 0).

**브리프가 금지한 산문 판정은 넣지 않았다** — JB 의 `core7_absent_from_vendor_sheet` 문자열 키는 이 배치 카드에 **없다**(생성기 자기검사로 강제).

---

## 6. 못 넣은 것 — 셋으로 갈라 적는다

### (가) 형식에 그 항목이 없었다 — **문서를 열었고 행이 없음을 확인** (판정 170칸)

**34등급 × 다섯 키** — `physical.density` · `mechanical.youngs_modulus` · `mechanical.poisson_ratio` · `thermal.specific_heat` · `mechanical.tensile_strength`.

근거는 두 겹이다. **① 자기 시트** — 각 등급의 `Basic Laminate Property` 표가 한 쪽에 전부 인쇄되고 다섯 행의 자리 자체가 없다(사유문에 등급별 실측 행 목록을 그대로 적었다). **② 벤더 전수** — 43장 낱말 단위 토큰 검사에서 여섯 낱말 전부 0장이다.

**「자리가 없다」와 「칸이 비었다」를 갈랐다** — 이 벤더는 `N/A` 를 실제로 인쇄할 줄 안다(Tg DSC 칸 22장). 코어7 다섯은 `N/A` 조차 없이 **행이 통째로 없다.** 재지 않거나 공개하지 않는 것이다.

### (나) 문서를 못 열었다 — **이 배치에는 0건**

- **43장이 전부 로컬에 있었다.** 74차 JB 가 27건을 코퍼스에 넣어 둔 덕이다. 새로 받은 것이 없으므로 못 연 문서도 없다.
- **로케일을 바꿔 새 문서를 찾지 않았다** — 68차 DC·74차 JB 가 `zh-TW`·`zh-CN`·`en-global` 세 목록의 PDF URL 43개가 완전히 같다는 것을 URL diff 로 증명했다. 브리프의 지시대로 시간을 쓰지 않았다.
- **SDS 경로는 두드리지 않았다.** 고체 물품(article)인 적층판에는 SDS 의무가 없고, 같은 이유로 72차 HD 가 Sumitomo 에서 헛걸음한 자리다. **다만 이 벤더에 대해 확인한 것은 아니다 — 「없다」고 적지 않는다.**

### (다) 키가 없거나 등급이 안 맞았다

- **`Dielectric Breakdown | >45 kV`**(8장, 일부 >40 kV) — **두께가 없는 절대 파괴전압**이라 우리 분류에 맞는 키가 없다. `electrical.dielectric_strength` 는 V/m 이고 `electrical.withstand_voltage_surface` 는 다른 측정이다. 값을 버리지 않도록 카드 `attributes.dielectric_breakdown_printed` 에 verbatim 으로 남겼다.
- **`Flexural Modulus`(2.4.4) → `mechanical.youngs_modulus`** — 옮기지 않았다(§2).
- **형제 등급의 값을 옮기지 않았다.** `EM-892K2(A)`·`EM-S532K` 의 저항률, `EM-A70K`·`EM-S532K` 의 굽힘, `EM-S570` 의 흡수율·Fill 굽힘 — 형제 시트에는 있지만 **이 등급 시트에 없는 것은 없는 것**이다. 각각 카드 attributes 에 그 구분을 적었다.
- **이미 카드가 선 9등급**(2433·2434·2435·2517·2518·2809~2812) — **값도 판정도 한 행 건드리지 않았다.** DC·JB 의 판정이 이 배치의 재독과 같은 결론이라 덮으면 `_before_correction` 잡음만 남는다.

---

## 7. 산출물

| 파일 | 내용 |
|---|---|
| `kb75_01_elite_material_uncarded_grades.json` | 신규 카드 **34** · 물성 **1,011행**(전부 t1/measured) · 카드에 박은 판정 **170칸** |
| `kb75_gen.py` | 위를 만든 생성기. **값이 코드에 verbatim 으로 박혀 재현된다.** `jb74_gen.em_absent_reason()` 을 import 해 사유문을 재사용하고, 판정 오인 이름 자기검사(`VERDICT_LIKE`)를 박았다 |

**적재 리허설 결과**(`snapshot_db.py` 사본, 라이브 원본 무변경 확인):

```
ingest_agent_json.py --apply  →  ok 1011 / new_mat 34,  실패 0 · 유실 0
integrity_check.py            →  사전 이상 1개 → 사후 이상 1개  (신규 0)
                                 전체 리포트 diff = 요약 한 줄(재료·값·출처 수)뿐
```

**인쇄값 역검산** — JSON 의 `원문 verbatim` 토막에서 숫자 843개를 뽑아 원문 텍스트에 다시 대조했다. **불일치 0.**

---

## 8. 다음 배치에 넘길 것

### 8-1. **Elite Material 은 닫혔다 — 이 제품군에서 더 팔 자리가 없다**

- 벤더가 공개하는 데이터시트 **43장 = 카드 43장**. 코어7 **열린 칸 0**.
- 남은 것은 벤더가 **재지 않거나 공개하지 않는 다섯 물성**이고, 그것은 문서를 더 두드려서 나올 것이 아니다. **다음에 여는 문은 다른 벤더이거나 다른 층(규격·학술)이어야 한다.**
- **다만 이 벤더의 두 카드에 작은 보완거리가 있다** — `EM-370(Z)`(2433) · `EM-370(5)`(2434) 시트가 `Electric Strength >40 kV/mm` 와 `Dielectric Breakdown >45 kV` 를 인쇄하는데 68차 DC 가 담지 않았다. 코어7 은 아니지만 **인쇄된 값이 두 칸 비어 있다.**

### 8-2. **도구 — `integrity_check.k_missing_direction()` 이 `axis` 를 못 본다**

이 검사는 「CTE 는 방향이 갈렸는데 열전도율은 스칼라 하나」인 재료를 잡는 것인데, **조건 키를 `direction`·`orientation` 두 이름으로만 읽는다.** 우리 카탈로그의 CTE 행 중 **`axis` 를 쓰는 것이 799행**이다(`direction`/`orientation` 은 1,015행).

**이 벤더 43종이 정확히 그 표적인데 한 건도 안 걸린다** — CTE 는 X/Y/Z 로 갈라 인쇄되고 열전도율은 스칼라 하나다. 검사에 `axis` 를 더하면 다음 파동이 이 공백을 볼 수 있다. (**이 배치는 `axis` 를 바꾸지 않았다** — 기존 Elite 9장과 JB 생성기가 `axis` 를 쓰고 있어, 같은 벤더 안에서 조건 어휘를 쪼개면 대표값 선택기가 더 나빠진다.)

### 8-3. **정리거리 — 중복 PDF 다섯 쌍이 아직 있다**

`EliteMaterial_*.pdf` 5장과 `EMC_*.pdf` 5장이 **md5 동일**이다(재확인했다).

```
9b6b7fb5… EM-370Z   9df4602e… EM-370-5   a54f6fd4… EM-888   cb210f1e… EM-890   d46448db… EM-891
```

74차 JB 가 만든 중복이 아니고 이 배치도 아니다(68차 DC 와 그 뒤 배치가 두 이름으로 받았다). **지울지 판단해라.**

### 8-4. **전사 규율로 남길 것 둘**

1. **`pdftotext -layout` 은 위첨자를 본문 숫자에 붙여 버린다**(§3-1). 지수처럼 생긴 것을 보면 `-bbox-layout` 으로 y 좌표와 글자높이를 봐라. 붙여 읽은 `1010` 은 값이 아니다.
2. **`attributes` 이름에 `absent`·`not_applicable`·`rejected_printed`·`no_public` 을 쓰지 마라**(§3-2). 판정이 아닌 메모라도 집계가 판정으로 읽고 「모르는 이름」으로 센다. 메모는 `vendor_sheet_missing_*` 같은 이름으로 가라.
