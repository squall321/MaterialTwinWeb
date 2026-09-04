# 63차 YA 컨텍스트 노트 — 왜 이렇게 했나

작업 중 내린 결정과 근거를 누적한다. 다음 파동이 같은 자리에서 같은 고민을 처음부터 하지 않게.

## 결정 1 — 어휘표를 세울지, 검사기만 고칠지

`direction_vocab.py` 가 선례다. 그것과 다른 점 하나가 설계를 정했다 —
**`direction` 은 배정 못 한 값을 `null` 로 비웠지만(§537) 여기서는 비우면 안 된다.**
`direction` 의 자유서술은 우리가 못 읽은 축이지만, `temperature` 의 `room temperature` ·
`not printed` 는 **원문이 온도를 안 찍었다는 진술**이라 지우면 정보가 사라진다.
그래서 `normalize()` 의 `None` 이 뜻하는 것도 다르다 — `direction_vocab` 에서는 "비워라",
여기서는 **"손대지 마라"** 다. 모듈 머리말에 그 차이를 못박았다.

## 결정 2 — 정규값 자리를 어디로 둘까(`temperature_verbatim` 을 안 만든 이유)

`direction` 은 `direction` = 정규값 · `direction_verbatim` = 원문으로 갈랐다. 그대로 따라
`temperature_verbatim` 을 만들면 **`_condition_axis_count` 가 그 칸을 센다** —
`_NOT_A_CONDITION` 에 `direction_verbatim` 만 들어 있어서다. 접히는 행에만 칸이 하나 늘면
`_rep_rank` 다섯째 자리가 흔들려 §548 이 겪은 사고가 그대로 재현된다.
공유 도구(`catalog_compare.py`)를 고치면 해결되지만 **채굴/정리 배치는 공유 도구를 안 고친다**(§468).

**그래서 원문을 `temperature_before_correction` 에 뒀다.** 얻는 것이 셋이다 —
① `_condition_axis_count` 가 `_before_correction` 을 이미 안 센다 ②§594 가 요구하는 되돌리기
표시가 바로 그 칸이라 병합기의 정정 전파가 그대로 돈다 ③ 적재기가 **자동으로** 채우므로
내가 손으로 쓸 칸이 없다. 라이브에 이미 88행이 그 칸을 갖고 있어 새 어휘도 아니다.

## 결정 3 — 숫자 196행 중 86행을 안 옮긴 이유 (이 배치에서 가장 중요한 판단)

지시서는 *"숫자가 문자열 키에 앉아 있다. `temperature_k` 로 옮겨라"* 였다. 149행(둘 다 가진
32행·TEMP_VALUED 15행 제외)을 **전수로 열어 `detail`·`notes` 를 읽으니 69행이 시험온도가 아니었다.**

| 무엇이었나 | 행 | 지문 |
|---|---:|---|
| 등급명 Tg | 23 | `Isola 370HR, high-Tg (180 degC) … laminate` — 같은 행이 시험을 `IPC-TM-650 2.6.2.1A 흡습` 으로 밝히고 둘은 `296 K (as-received)` 라고 따로 적어 두었다 |
| 공정온도 | 18 | `annealed 160 degC for 50 min; **measured at room temperature (~298 K)**` · `ALD at 200 degC` · `sputtered … at 25 degC; TCR over 298-398 K` |
| 구간의 끝 | 17 | `alpha -30 to +70 degC` 의 70 · `alpha +20 to +300 degC` 의 300 · NdFeB `20-200 degC` 가 `-200 degC` 로 남은 것 |
| 다른 축 혼재 | 11 | `23 C / 50 %RH` · `200 degC, held 30 min` |

여기에 `property_key` 가 TEMP_VALUED 인 15행(값 자신의 재기재 `Tg = 683 degC` · 승온 상한
`heating 22 to 120 degC` · 승온율 `10 degC/min`)을 더해 **86행**이다.

**옮기면 값은 안 바뀌지만 `_temp_distance` 가 그것을 시험온도로 읽는다** — 대표값 선택이
뒤집히고 DYNA 카드 주석에 `T 453.15K` 가 찍힌다. 그리고 TEMP_VALUED 15행은
`integrity_check` 의 「온도가 값인데 시험온도 조건」에 **신규 위반**을 낸다.
**지시서의 "220행" 은 표기 수이지 표적 수가 아니었다**(§659 의 68 → 41 → 11 과 같은 모양).

가른 기준을 한 줄로 적어 둔다 — **그 행의 `detail`·`notes` 가 그 수를 *잰* 온도라고 말하는가.**
말 안 하면 안 옮긴다. 사유는 `migrate_temperature_ya.SKIP` 에 pv 번호까지 박았다(§648).

## 결정 4 — 다른 축이 섞인 11행을 안 옮긴 이유

`23 C / 50 %RH` 에서 온도만 떼면 습도가 **보이는 키에서** 사라진다(원문은 남지만
`formatConditions` 가 `_before_correction` 을 뒤로 던진다). `normalize_condition_keys.NOT_MERGED` 가
`thickness("37.5 um") ↔ thickness_um` 에 내린 판단과 같은 자리다 —
**갈라 넣는 것은 정정이 아니라 채굴이다.** 표적으로 남겼다.

## 결정 5 — 맨 숫자 17행의 단위는 어휘표가 아니라 이관표가 정한다

`kelvin(298.15)` 은 `None` 이다. 문자열이 단위를 안 들고 있으면 어휘표는 단위를 지어내지
않는다(§443). 단위를 답한 것은 **행 자신**이다 — 8행은 같은 조건 dict 의 `temperature_unit: "K"`,
9행은 `.15` 소수(298.15/296.15/293.15 = 25/23/20 °C 정확히)다. 후자는 섭씨로 읽으면
액체 전해액 밀도 1243 kg/m³ @ 293.15 °C 가 되어 물질이 성립하지 않는다.
근거를 행마다 정정 사유에 적었다.

## 결정 6 — 막힌 행을 군 단위로 뺄까 행 단위로 뺄까

`normalize_condition_keys` 는 **군 전체**를 뺐다. 그 사유가 *"막힌 행 하나만 빼면 그 행만 조건
칸이 안 늘어 `_rep_rank` 의 `len(conditions)` 자리에서 대표값이 뒤집힌다"* 다.
**이 배치는 조건 칸 수를 안 바꾸므로 그 사유가 없다** — `temperature` 하나가 나가고
`temperature_k` 하나가 들어오며, 접기는 이름도 안 바꾼다. 그래서 **행 단위로만** 뺐고,
`verify_readers_ya.py` 가 "조건 칸 수가 바뀐 행 0" 으로 그것을 증명한다.

## 결정 7 — 대표값 7군이 뒤집히는 것을 그대로 뒀다

이 배치가 유일하게 흔들 수 있는 자리가 `_rep_rank` 넷째 자리(`_temp_distance`)다.
전수 대조에서 **7군이 뒤집혔고 그중 5군은 대표값 숫자가 달라진다.** 전부 t1 → t1 이고
방향이 하나다 — **온도를 인쇄한 행이 온도를 안 적은 행을 이긴다.**

그것이 `_UNSPECIFIED_TEMP_PENALTY = 5.0` 의 설계 의도다(그 상수의 주석 verbatim:
*"이게 0이면 무표기 값이 '상온 거리 0'으로 계산돼 25 °C라고 명시한 측정값을 이긴다"*).
숨기려면 옮긴 온도를 선택기에서만 안 보이게 해야 하는데 그건 정규화의 반대다.

다만 **재료111 밀도는 0.15 K 차이가 3% 값 차이를 가른다**(pv3864 `temperature_k 293` 거리 3.15
대 pv1066 `293.15` 거리 3.00). 둘 다 t1 실측 20 °C 다 — 선택기가 사실상 못 가르는 자리를
소수점이 가른 것이라 **표적으로 신고한다**(§551 의 "분류하지 말고 보여줘라" 자리다).

## 결정 8 — `not cited` 를 부재 진술에 넣은 근거

71행 전부 AccuDyne 접촉각 표에서 왔고 원문 verbatim 이 `θWY = 70o; **no temp cited**` 다.
`notes` 가 그 문장을 그대로 인용해 두어 열어 볼 필요도 없었다(§658 — 가장 싼 문은 우리 `notes` 다).

## 안 한 것과 그 이유

- **`normal temperature and pressure` 48행을 상온으로 안 접었다.** NTP 는 판마다 20 °C 와 0 °C 로
  갈린다. 접으면 우리가 판을 고른 것이 된다.
- **`ISO 291 – 23/50` 3행을 안 건드렸다.** 표준상태 코드이고 23 °C/50 %RH 를 뜻하지만
  그것을 풀어 쓰는 것은 결정 4 와 같은 갈래다.
- **`tie_verdicts.temp_c` 를 안 고쳤다.** 이 함수는 문자열 **전체**를 정규식으로 훑어
  `'not printed (… 응력자유온도 298 K …)'` 에서 24.85 °C 를 읽는다. 공유 도구라 안 고쳤고(§468)
  고칠 자리를 브리프 초안에 적었다 — `temperature_vocab.head()` 를 앞에 한 줄 걸면 된다.
- **`catalog_compare._temp_distance` 에 `temperature`(문자열)를 안 더했다.** 같은 이유다.
  그리고 지금은 더할 필요도 없다 — 숫자는 전부 `temperature_k` 로 갔고 남은 것은 진술이라
  **무표기 불이익 5.0 이 맞는 답**이다.
