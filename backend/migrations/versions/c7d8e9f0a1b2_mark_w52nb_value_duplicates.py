"""52차 NB — 중복 적재로 확인된 물성값 63행에 **중복 표시**를 세운다. 한 행도 지우지 않는다.

## 무엇을 찾았나 — 조건 키 이름에 안 휘둘리는 검출

§547 이 짚은 자리다. 같은 시트를 두세 번 적재했는데 **조건 키 이름이 달라 자연키가 안 걸렸다.**
`backend/scripts/catalog/value_duplicates.py` 가 조건 키 이름·단위·값 표기를 정규화한 뒤
(재료·물성키·출처·값) 으로 묶어 전수로 갈랐다(라이브 41,368행).

| 부류 | 군 | 여분행 | 뜻 |
|---|---|---|---|
| **확실** | 61 | **63** | 정규화만으로 조건이 글자까지 같아진다 — 같은 측정의 재적재 |
| 의심 | 430 | 445 | 값 표기를 주물러야 같아지거나 한쪽에만 조건이 적혔다 — 손확인 몫 |
| 정당한 반복 | 1,391 | 1,945 | 반복 시편·통계량·세트 항·등급이 실제로 갈린다(§435) |

**인계 둘을 직접 검증했다**(§479·505).

- Kapton 150EN-A MD 0.85 **세 행 맞다** — 다만 pv3172 는 출처 행이 다르다(src1740).
  1740 과 2016 은 **같은 DuPont 시트**(EI-10172 = QE-10172)가 URL 만 달라 두 번 등록된 것이다(§185).
  같은 출처인 pv6044·pv12746 만 확실로 잡고, 출처가 갈린 쪽은 **의심으로 남긴다**
  (§456 — 계보를 확인하기 전에는 근거의 세기로 읽지 않는다).
- Rogers RO4350B CTE x/y/z **두 벌 맞다** — axis 판(pv3581~3583)과 direction 판(pv3977~3979),
  둘 다 src1773 이고 세 축이 정확히 짝지어진다. 여기서 확실 3군이 나왔다.

## 왜 지우지 않고 표시하나

**지우면 되돌릴 수 없고, 병합기가 운영에서 그 행을 되살린다.** 병합은 비파괴라 dev 에서 지운
행이 운영에서는 그대로 남는다 — 즉 삭제는 **dev 에서만 사라지고 운영에는 영원히 남는** 최악의
형태가 된다. §435 가 재료 중복에서 자동 병합을 금지한 것과 같은 자리이고, 옛
`dedupe_values.py` 가 실제로 지우던 것을 여기서는 하지 않는다.

## 무엇을 표시하나 — **정본을 id 로 가리킬 수 없다**

§535 가 재료 묘비에서 배운 것이 그대로 걸린다 — id 는 정수 autoincrement 라 dev/cae00 에서
같은 id 가 다른 행일 수 있다. 그런데 중복군 안의 행들은 **정의상 값·출처·재료가 같아서**
행을 가리킬 자연축이 조건 밖에 없다. 그래서 정본을 **원문 조건 지문**으로 가리킨다.

    verdict_duplicate_of   = "axis=\"x\" | standard=\"IPC-TM-650 2.4.41\" | temperature_range_C=\"-55 to 288\""
    verdict_duplicate_note = "52차 NB — 같은 출처의 같은 측정을 두 번 적재했다(조건 키 표기만 달랐다)"

- **정규화 지문은 못 쓴다.** 중복군의 모든 행이 **정의상 같은 정규화 지문**을 갖는다 —
  그게 중복의 정의다. 그래서 지문은 **원문 조건**(키 표기까지 그대로)이어야 정본만 가리킨다.
  첫 판에서 정규화 지문을 넣었다가 실측으로 잡았다: 61군 전부에서 정본을 특정하지 못했다.
  원문 조건으로 바꾸니 61군 전부 유일하다.

- **중복 쪽에만 단다. 정본은 한 칸도 안 건드린다.** `_rep_rank` 다섯째 자리가 조건 수
  오름차순이라, 중복에 두 칸을 더하면 **정본이 자동으로 이긴다** — §543·544 가 두 번 재고
  버린 *순위 변경* 없이 순위 **안에서** 풀린다.
- **라이브 전수로 재 봤다** — 대표 행이 바뀐 (재료,키) **1쌍**, 대표 **값**이 바뀐 것 **0**.
  그 1쌍은 재료 255 의 CTE 인데 새 대표도 같은 1.92e-5 다.
  정본에도 달면 8쌍이 뒤집히고 그중 하나는 값까지 바뀐다(49.0 ksi 의 환산 쌍둥이).
  **한쪽에만 다는 쪽이 옳다** — §548 의 "군의 모든 행에 같은 수를 더해라" 는 값이 다른
  동률군의 규칙이고, 값이 같은 중복군에는 반대 답이 나온다.

## 운영까지 가는가 — **병합기를 고쳤다**(§464·522·536 의 네 번째 얼굴)

조건은 `property_value` 자연키 안에 있다. 그래서 판정 한 칸만 더해도 자연키가 깨져 운영에
**사본**이 생긴다. 정정 경로(§521)로는 우회할 수 없다 — 그 경로는 (재료·키·출처·옛 값)이
유일해야 도는데 **중복군은 정의상 유일하지 않다.** 51차 MA 가 그 이유로 128군을 포기했다(§548).

→ 병합기(HEAXHub/deploy/apptainer/_materialtwin_merge.py)에 **verdict_ 접두어 조건 키를
자연키에서 빼는 분기**를 넣었다. 빼고 남은 것으로 대응행을 찾아 **판정 키만 얹는다.**
실측 — 정정 탐색키는 4,265행·1,832군이 유일하지 않은데, **판정 키를 뺀 축은 41,368행 전부
유일하다.** 그래서 §548 의 **128군이 전부 열린다**(113 + 8 + 7).

## 되돌리기

downgrade 는 같은 행에서 두 키만 뺀다. 조건의 나머지 칸은 글자 그대로 보존된다.
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "c7d8e9f0a1b2"
down_revision = "b6c7d8e9f0a1"
branch_labels = None
depends_on = None

# 판정 키 — verdict_ 접두어는 병합기가 자연키에서 빼고 운영에 얹는 축이다(51차 MA 의 동률 판정과 같다).
K_OF = "verdict_duplicate_of"
K_NOTE = "verdict_duplicate_note"
NOTE = ("52차 NB — 같은 출처의 같은 측정을 두 번 적재했다(조건 키 표기만 달랐다). "
        "값은 지우지 않고 표시만 한다")

# **id 로 걸지 않는다**(§466·480·535) — 운영 id 는 dev 와 다르다. 재료 이름·출처 제목·값·단위·
# method·조건 전체로 건다. 실측으로 이 축이 라이브 41,368행에서 63행 전부 유일함을 확인했다.
# dev_pv·canon_dev_pv 는 사람이 추적하라고 적어 둘 뿐 매칭에 쓰지 않는다.
ROWS = [{'material': 'PI Base Film — Kapton 150MT+ (DuPont)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.44,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'DuPont™ Kapton® MT+ Thermally Conductive Polyimide Film — Data Sheet (EI-10218 '
                  '/ QE-10218)',
  'conditions': {'test_standard': 'ASTM D882', 'thickness_um': 38},
  'canonical': 'standard="ASTM D882" | thickness_um=38',
  'dev_pv': 12750,
  'canon_dev_pv': 3185},
 {'material': 'PI Base Film — Taimide TH-025 (Taimide)',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 284400000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'Properties of Taimide TH Polyimide Film (TH type data sheet)',
  'conditions': {'temperature': '23 C', 'test': 'ASTM D882', 'thickness': '25 um'},
  'canonical': 'standard="ASTM D882" | temperature_C=23 | thickness_um=25',
  'dev_pv': 6065,
  'canon_dev_pv': 3221},
 {'material': 'PI Base Film — Taimide TH-025 (Taimide)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.92,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Properties of Taimide TH Polyimide Film (TH type data sheet)',
  'conditions': {'temperature': '23 C', 'test': 'ASTM D882', 'thickness': '25 um'},
  'canonical': 'standard="ASTM D882" | temperature_C=23 | thickness_um=25',
  'dev_pv': 6066,
  'canon_dev_pv': 3222},
 {'material': 'PI Base Film — Taimide TL-025 (Taimide)',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 294200000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'Properties of Taimide TL Polyimide Film (TL type data sheet)',
  'conditions': {'temperature': '23 C', 'test': 'ASTM D882', 'thickness': '25 um'},
  'canonical': 'standard="ASTM D882" | temperature_C=23 | thickness_um=25',
  'dev_pv': 6067,
  'canon_dev_pv': 3225},
 {'material': 'PI Base Film — Taimide TL-025 (Taimide)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.78,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Properties of Taimide TL Polyimide Film (TL type data sheet)',
  'conditions': {'temperature': '23 C', 'test': 'ASTM D882', 'thickness': '25 um'},
  'canonical': 'standard="ASTM D882" | temperature_C=23 | thickness_um=25',
  'dev_pv': 6068,
  'canon_dev_pv': 3226},
 {'material': 'PI Base Film — Taimide BK-025 Low Gloss (Taimide)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.67,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Properties of Taimide BK(Low Gloss) Polyimide Film (BK type data sheet)',
  'conditions': {'temperature': '23 C', 'test': 'ASTM D882', 'thickness': '25 um'},
  'canonical': 'standard="ASTM D882" | temperature_C=23 | thickness_um=25',
  'dev_pv': 6070,
  'canon_dev_pv': 3230},
 {'material': 'Isola 370HR High-Tg Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.177,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': '370HR Industry Leading, Standard Loss, Thermally Robust Epoxy Laminate and '
                  'Prepreg (Rev C, 2021-04-15)',
  'conditions': {'direction': 'length (warp)', 'test': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 6083,
  'canon_dev_pv': 3358},
 {'material': 'Isola 370HR High-Tg Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.171,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': '370HR Industry Leading, Standard Loss, Thermally Robust Epoxy Laminate and '
                  'Prepreg (Rev C, 2021-04-15)',
  'conditions': {'direction': 'cross (fill)', 'test': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 6084,
  'canon_dev_pv': 3359},
 {'material': 'Isola IS400 Mid-Tg Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.183,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'IS400 Lead Free, Mid Tg Epoxy Laminate and Prepreg (Rev C, 2021-04-15)',
  'conditions': {'direction': 'length (warp)', 'test': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 6098,
  'canon_dev_pv': 3384},
 {'material': 'Isola IS400 Mid-Tg Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.151,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'IS400 Lead Free, Mid Tg Epoxy Laminate and Prepreg (Rev C, 2021-04-15)',
  'conditions': {'direction': 'cross (fill)', 'test': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 6099,
  'canon_dev_pv': 3385},
 {'material': 'Isola I-Tera MT40 Low-Loss Laminate',
  'property_key': 'mechanical.flexural_strength',
  'value_num': 490000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)',
  'conditions': {'direction': 'length (warp)', 'test': 'IPC-TM-650 2.4.4B'},
  'canonical': 'direction="length (LW)" | standard="IPC-TM-650 2.4.4B"',
  'dev_pv': 6115,
  'canon_dev_pv': 3404},
 {'material': 'Isola I-Tera MT40 Low-Loss Laminate',
  'property_key': 'mechanical.flexural_strength',
  'value_num': 400000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)',
  'conditions': {'direction': 'cross (fill)', 'test': 'IPC-TM-650 2.4.4B'},
  'canonical': 'direction="cross (CW)" | standard="IPC-TM-650 2.4.4B"',
  'dev_pv': 6116,
  'canon_dev_pv': 3405},
 {'material': 'Isola I-Tera MT40 Low-Loss Laminate',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 269000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)',
  'conditions': {'axis': 'length (warp)', 'standard': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 11133,
  'canon_dev_pv': 3406},
 {'material': 'Isola I-Tera MT40 Low-Loss Laminate',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 241000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)',
  'conditions': {'axis': 'cross (fill)', 'standard': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 11134,
  'canon_dev_pv': 3407},
 {'material': 'Isola I-Tera MT40 Low-Loss Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.234,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)',
  'conditions': {'axis': 'length (warp)', 'standard': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 11127,
  'canon_dev_pv': 3410},
 {'material': 'Isola I-Tera MT40 Low-Loss Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.222,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)',
  'conditions': {'axis': 'cross (fill)', 'standard': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 11128,
  'canon_dev_pv': 3411},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.flexural_strength',
  'value_num': 337843093.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'direction': 'length', 'standard': 'IPC-TM-650 2.4.4B'},
  'canonical': 'direction="length (LW)" | standard="IPC-TM-650 2.4.4B"',
  'dev_pv': 4188,
  'canon_dev_pv': 3430},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.flexural_strength',
  'value_num': 268895523.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'direction': 'cross', 'standard': 'IPC-TM-650 2.4.4B'},
  'canonical': 'direction="cross (CW)" | standard="IPC-TM-650 2.4.4B"',
  'dev_pv': 4189,
  'canon_dev_pv': 3431},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 213737467.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'direction': 'length', 'standard': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 4190,
  'canon_dev_pv': 3432},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 165474168.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'direction': 'cross', 'standard': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 4191,
  'canon_dev_pv': 3433},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.183,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'direction': 'length', 'standard': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 4192,
  'canon_dev_pv': 3434},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.183,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'axis': 'length (warp)', 'standard': 'ASTM D3039'},
  'canonical': 'direction="length (LW)" | standard="ASTM D3039"',
  'dev_pv': 11125,
  'canon_dev_pv': 3434},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.182,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'direction': 'cross', 'standard': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 4193,
  'canon_dev_pv': 3435},
 {'material': 'Isola Astra MT77 Very Low Loss RF/MW Laminate',
  'property_key': 'mechanical.poisson_ratio',
  'value_num': 0.182,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)',
  'conditions': {'axis': 'cross (fill)', 'standard': 'ASTM D3039'},
  'canonical': 'direction="cross (CW)" | standard="ASTM D3039"',
  'dev_pv': 11126,
  'canon_dev_pv': 3435},
 {'material': 'ITEQ IT-968 Ultra-Low-Loss Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.2e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'IT-968 High Tg / Lead Free / Ultra Low Loss Laminate & Prepreg (DRAFT REV '
                  '1.0-17)',
  'conditions': {'axis': 'x', 'temperature_range_C': '40-125', 'standard': 'IPC-TM-650 2.4.24'},
  'canonical': 'axis="in-plane" | direction="x" | range="40C to 125C, below Tg" | test="IPC-TM-650 '
               '2.4.24"',
  'dev_pv': 3463,
  'canon_dev_pv': 6151},
 {'material': 'ITEQ IT-968 Ultra-Low-Loss Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.4e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'IT-968 High Tg / Lead Free / Ultra Low Loss Laminate & Prepreg (DRAFT REV '
                  '1.0-17)',
  'conditions': {'axis': 'y', 'temperature_range_C': '40-125', 'standard': 'IPC-TM-650 2.4.24'},
  'canonical': 'axis="in-plane" | direction="y" | range="40C to 125C, below Tg" | test="IPC-TM-650 '
               '2.4.24"',
  'dev_pv': 3464,
  'canon_dev_pv': 6152},
 {'material': 'Rogers RO4003C High-Frequency Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 4.6e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'direction': 'Z',
                 'temperature_range_c': '-55 to 288',
                 'standard': 'IPC-TM-650 2.4.41'},
  'canonical': 'axis="z" | standard="IPC-TM-650 2.4.41" | temperature_range_C="-55 to 288"',
  'dev_pv': 3960,
  'canon_dev_pv': 3561},
 {'material': 'Rogers RO4003C High-Frequency Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.1e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'direction': 'X',
                 'temperature_range_c': '-55 to 288',
                 'standard': 'IPC-TM-650 2.4.41'},
  'canonical': 'axis="x" | standard="IPC-TM-650 2.4.41" | temperature_range_C="-55 to 288"',
  'dev_pv': 3958,
  'canon_dev_pv': 3562},
 {'material': 'Rogers RO4003C High-Frequency Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.4e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'direction': 'Y',
                 'temperature_range_c': '-55 to 288',
                 'standard': 'IPC-TM-650 2.4.41'},
  'canonical': 'axis="y" | standard="IPC-TM-650 2.4.41" | temperature_range_C="-55 to 288"',
  'dev_pv': 3959,
  'canon_dev_pv': 3563},
 {'material': 'Rogers RO4003C High-Frequency Laminate',
  'property_key': 'thermal.conductivity',
  'value_num': 0.71,
  'value_text': None,
  'unit': 'W/(m*K)',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'temperature_c': 80, 'standard': 'ASTM C518'},
  'canonical': 'standard="ASTM C518" | temperature_C=80',
  'dev_pv': 3963,
  'canon_dev_pv': 3564},
 {'material': 'Rogers RO4003C High-Frequency Laminate',
  'property_key': 'physical.density',
  'value_num': 1790.0,
  'value_text': None,
  'unit': 'kg/m^3',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'temperature_c': 23, 'standard': 'ASTM D792'},
  'canonical': 'standard="ASTM D792" | temperature_C=23',
  'dev_pv': 3965,
  'canon_dev_pv': 3578},
 {'material': 'Rogers RO4350B High-Frequency Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 3.2e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'direction': 'Z',
                 'temperature_range_c': '-55 to 288',
                 'standard': 'IPC-TM-650 2.4.41'},
  'canonical': 'axis="z" | standard="IPC-TM-650 2.4.41" | temperature_range_C="-55 to 288"',
  'dev_pv': 3979,
  'canon_dev_pv': 3581},
 {'material': 'Rogers RO4350B High-Frequency Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 9.999999999999999e-06,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'direction': 'X',
                 'temperature_range_c': '-55 to 288',
                 'standard': 'IPC-TM-650 2.4.41'},
  'canonical': 'axis="x" | standard="IPC-TM-650 2.4.41" | temperature_range_C="-55 to 288"',
  'dev_pv': 3977,
  'canon_dev_pv': 3582},
 {'material': 'Rogers RO4350B High-Frequency Laminate',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.2e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'direction': 'Y',
                 'temperature_range_c': '-55 to 288',
                 'standard': 'IPC-TM-650 2.4.41'},
  'canonical': 'axis="y" | standard="IPC-TM-650 2.4.41" | temperature_range_C="-55 to 288"',
  'dev_pv': 3978,
  'canon_dev_pv': 3583},
 {'material': 'Rogers RO4350B High-Frequency Laminate',
  'property_key': 'thermal.conductivity',
  'value_num': 0.69,
  'value_text': None,
  'unit': 'W/(m*K)',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'temperature_c': 80, 'standard': 'ASTM C518'},
  'canonical': 'standard="ASTM C518" | temperature_C=80',
  'dev_pv': 3982,
  'canon_dev_pv': 3584},
 {'material': 'Rogers RO4350B High-Frequency Laminate',
  'property_key': 'physical.density',
  'value_num': 1860.0,
  'value_text': None,
  'unit': 'kg/m^3',
  'method': 'measured',
  'source_title': 'RO4000 Series High Frequency Circuit Materials Data Sheet (RO4003C / RO4350B, '
                  '2018)',
  'conditions': {'temperature_c': 23, 'standard': 'ASTM D792'},
  'canonical': 'standard="ASTM D792" | temperature_C=23',
  'dev_pv': 3984,
  'canon_dev_pv': 3598},
 {'material': 'OCA Double-Coated w/ PET Carrier 75um (3M 8173KCL)',
  'property_key': 'optical.haze',
  'value_num': 0.01,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': '3M Optically Clear Adhesive 8173KCL Technical Data (Display Materials & Systems '
                  'Division, 2015)',
  'conditions': {'test': 'ASTM D1003-92'},
  'canonical': 'test_standard="ASTM D1003-92"',
  'dev_pv': 6214,
  'canon_dev_pv': 3839},
 {'material': 'Rogers ULTRALAM 3908 LCP Bonding Film',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.7e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'ULTRALAM 3908 Bondply (LCP prepreg), Data Sheet Pub #92-126',
  'conditions': {'direction': 'X', 'temperature_range_c': '30-150', 'standard': 'IPC 2.4.41.3'},
  'canonical': 'axis="in-plane" | direction="x" | range="30 to 150C" | test="IPC 2.4.41.3"',
  'dev_pv': 3925,
  'canon_dev_pv': 6155},
 {'material': 'Rogers ULTRALAM 3908 LCP Bonding Film',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.7e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'ULTRALAM 3908 Bondply (LCP prepreg), Data Sheet Pub #92-126',
  'conditions': {'direction': 'Y', 'temperature_range_c': '30-150', 'standard': 'IPC 2.4.41.3'},
  'canonical': 'axis="in-plane" | direction="y" | range="30 to 150C" | test="IPC 2.4.41.3"',
  'dev_pv': 3926,
  'canon_dev_pv': 6156},
 {'material': 'Rogers ULTRALAM 3908 LCP Bonding Film',
  'property_key': 'thermal.expansion_linear',
  'value_num': 0.00015,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'ULTRALAM 3908 Bondply (LCP prepreg), Data Sheet Pub #92-126',
  'conditions': {'direction': 'Z', 'temperature_range_c': '30-150', 'standard': 'IPC 2.4.41.3'},
  'canonical': 'axis="through-plane" | direction="z" | range="30 to 150C" | test="IPC 2.4.41.3"',
  'dev_pv': 3927,
  'canon_dev_pv': 6157},
 {'material': 'Rogers RO4835 Oxidation-Resistant Hydrocarbon-Ceramic Laminate',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 136000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'RO4835 Laminates Data Sheet Pub #92-160',
  'conditions': {'temperature_C': 23, 'test_standard': 'ASTM D638'},
  'canonical': 'standard="ASTM D638" | temperature_c=23',
  'dev_pv': 13189,
  'canon_dev_pv': 3998},
 {'material': 'Rogers CLTE-XT Ceramic-PTFE Woven Glass Laminate',
  'property_key': 'mechanical.flexural_strength',
  'value_num': 40000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'CLTE and CLTE-XT Series Laminates Data Sheet',
  'conditions': {'temperature_C': 25,
                 'direction': 'CMD (cross-machine)',
                 'test_standard': 'ASTM D790'},
  'canonical': 'direction="CMD" | standard="ASTM D790" | temperature_c=25',
  'dev_pv': 13194,
  'canon_dev_pv': 4014},
 {'material': 'Rogers CLTE-AT Ceramic-PTFE Woven Glass Laminate',
  'property_key': 'mechanical.tensile_strength',
  'value_num': 30000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'CLTE-AT Series Laminates Data Sheet',
  'conditions': {'direction': 'CMD (cross-machine)', 'test_standard': 'IPC TM-650 2.4.18.3'},
  'canonical': 'direction="CMD" | standard="IPC TM-650 2.4.18.3"',
  'dev_pv': 13195,
  'canon_dev_pv': 4054},
 {'material': 'Rogers CLTE-AT Ceramic-PTFE Woven Glass Laminate',
  'property_key': 'mechanical.flexural_strength',
  'value_num': 54000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'CLTE-AT Series Laminates Data Sheet',
  'conditions': {'direction': 'CMD (cross-machine)', 'test_standard': 'IPC TM-650 2.4.4'},
  'canonical': 'direction="CMD" | standard="IPC TM-650 2.4.4"',
  'dev_pv': 13196,
  'canon_dev_pv': 4056},
 {'material': 'Rogers RT/duroid 5880 Glass-Microfiber PTFE Laminate',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.06,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'RT/duroid 5870 - 5880 High Frequency Laminates Data Sheet',
  'conditions': {'temperature_k': 296.15, 'test_standard': 'ASTM D638', 'direction': 'X'},
  'canonical': 'direction="X" | standard="ASTM D638" | temperature_c=23',
  'dev_pv': 13074,
  'canon_dev_pv': 4074},
 {'material': 'Rogers RT/duroid 5880 Glass-Microfiber PTFE Laminate',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.049,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'RT/duroid 5870 - 5880 High Frequency Laminates Data Sheet',
  'conditions': {'temperature_k': 296.15, 'test_standard': 'ASTM D638', 'direction': 'Y'},
  'canonical': 'direction="Y" | standard="ASTM D638" | temperature_c=23',
  'dev_pv': 13076,
  'canon_dev_pv': 4075},
 {'material': 'Taconic TLY-5 (PTFE/woven glass RF laminate)',
  'property_key': 'thermal.expansion_linear',
  'value_num': 2.6e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'TLY-5 Avionics & aerospace grade very low DK base material, Technical Data '
                  'Sheet (2024-03)',
  'conditions': {'direction': 'X (in-plane)',
                 'temperature_range_C': '25-260',
                 'standard': 'ASTM D 3386 (TMA)'},
  'canonical': 'direction="X" | standard="ASTM D 3386 (TMA)" | temperature_range_c="25-260"',
  'dev_pv': 5375,
  'canon_dev_pv': 4090},
 {'material': 'Taconic TLY-5 (PTFE/woven glass RF laminate)',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.5e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'TLY-5 Avionics & aerospace grade very low DK base material, Technical Data '
                  'Sheet (2024-03)',
  'conditions': {'direction': 'Y (in-plane)',
                 'temperature_range_C': '25-260',
                 'standard': 'ASTM D 3386 (TMA)'},
  'canonical': 'direction="Y" | standard="ASTM D 3386 (TMA)" | temperature_range_c="25-260"',
  'dev_pv': 5376,
  'canon_dev_pv': 4091},
 {'material': 'Taconic TLY-5 (PTFE/woven glass RF laminate)',
  'property_key': 'thermal.expansion_linear',
  'value_num': 0.000217,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'TLY-5 Avionics & aerospace grade very low DK base material, Technical Data '
                  'Sheet (2024-03)',
  'conditions': {'direction': 'Z (through-plane)',
                 'temperature_range_C': '25-260',
                 'standard': 'ASTM D 3386 (TMA)'},
  'canonical': 'direction="Z" | standard="ASTM D 3386 (TMA)" | temperature_range_c="25-260"',
  'dev_pv': 5377,
  'canon_dev_pv': 4092},
 {'material': 'Taconic TLY-5 (PTFE/woven glass RF laminate)',
  'property_key': 'chemical.outgassing_tml',
  'value_num': 0.0001,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'TLY-5 Avionics & aerospace grade very low DK base material, Technical Data '
                  'Sheet (2024-03)',
  'conditions': {'standard': 'NASA outgassing'},
  'canonical': 'standard="NASA Outgassing"',
  'dev_pv': 5384,
  'canon_dev_pv': 4099},
 {'material': 'Taconic TLY-5 (PTFE/woven glass RF laminate)',
  'property_key': 'chemical.outgassing_cvcm',
  'value_num': 0.0001,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'TLY-5 Avionics & aerospace grade very low DK base material, Technical Data '
                  'Sheet (2024-03)',
  'conditions': {'standard': 'NASA outgassing'},
  'canonical': 'standard="NASA Outgassing"',
  'dev_pv': 5385,
  'canon_dev_pv': 4100},
 {'material': 'TAIFLEX 2L FCCL 2UPDR2010JD (adhesiveless polyimide)',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.92e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'TAIFLEX 2L FCCL (Two Layer Flexible Copper Clad Laminate) Data Sheet',
  'conditions': {'direction': 'MD', 'temperature_range_c': '25-200'},
  'canonical': 'axis="in-plane" | direction="MD" | range="25-200C"',
  'dev_pv': 4207,
  'canon_dev_pv': 6164},
 {'material': 'TAIFLEX 2L FCCL 2UPDR2010JD (adhesiveless polyimide)',
  'property_key': 'thermal.expansion_linear',
  'value_num': 1.8e-05,
  'value_text': None,
  'unit': '1/K',
  'method': 'measured',
  'source_title': 'TAIFLEX 2L FCCL (Two Layer Flexible Copper Clad Laminate) Data Sheet',
  'conditions': {'direction': 'TD', 'temperature_range_c': '25-200'},
  'canonical': 'axis="in-plane" | direction="TD" | range="25-200C"',
  'dev_pv': 4208,
  'canon_dev_pv': 6165},
 {'material': 'Taconic TLX-8 (PTFE/woven glass RF laminate)',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 11238000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'TLX-8 Technical Data Sheet (AGC Multi Material)',
  'conditions': {'direction': 'MD (machine direction)', 'test': 'ASTM D 3039'},
  'canonical': 'direction="MD" | standard="ASTM D 3039"',
  'dev_pv': 6355,
  'canon_dev_pv': 5413},
 {'material': 'Taconic TLX-8 (PTFE/woven glass RF laminate)',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 6757000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': 'TLX-8 Technical Data Sheet (AGC Multi Material)',
  'conditions': {'direction': 'MD (machine direction)', 'test': 'ASTM D 902'},
  'canonical': 'direction="MD" | standard="ASTM D 902"',
  'dev_pv': 6353,
  'canon_dev_pv': 5414},
 {'material': 'PI Base Film — Kapton 150EN-C (DuPont)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.8,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Kapton® EN-A, EN-C and EN-Z Polyimide Film — Technical Data Sheet (QE-10172)',
  'conditions': {'direction': 'MD', 'test_standard': 'JIS K 7161', 'thickness_um': 37.5},
  'canonical': 'direction="MD" | test="JIS K 7161" | thickness="37.5 um"',
  'dev_pv': 12744,
  'canon_dev_pv': 6035},
 {'material': 'PI Base Film — Kapton 150EN-A (DuPont)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.85,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Kapton® EN-A, EN-C and EN-Z Polyimide Film — Technical Data Sheet (QE-10172)',
  'conditions': {'direction': 'MD', 'test_standard': 'JIS K 7161', 'thickness_um': 37.5},
  'canonical': 'direction="MD" | test="JIS K 7161" | thickness="37.5 um"',
  'dev_pv': 12746,
  'canon_dev_pv': 6044},
 {'material': 'PI Base Film — Kapton 140EN-Z (DuPont)',
  'property_key': 'mechanical.elongation_at_break',
  'value_num': 0.7,
  'value_text': None,
  'unit': '1',
  'method': 'measured',
  'source_title': 'Kapton® EN-A, EN-C and EN-Z Polyimide Film — Technical Data Sheet (QE-10172)',
  'conditions': {'direction': 'MD', 'test_standard': 'JIS K 7161', 'thickness_um': 35.0},
  'canonical': 'direction="MD" | test="JIS K 7161" | thickness="35.0 um"',
  'dev_pv': 12748,
  'canon_dev_pv': 6053},
 {'material': 'ITEQ IT-968 Ultra-Low-Loss Laminate',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 18000000000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'measured',
  'source_title': "IT-968 High Tg / Lead Free / Ultra Low Loss Laminate & Prepreg — 'Laminate "
                  "properties'",
  'conditions': {'temperature_C': 23,
                 'method_detail': 'ASTM D3039 인장, 경화 라미네이트 warp/fill 동일값',
                 'direction': 'warp=fill (동일값)'},
  'canonical': 'method_detail="ASTM D3039 인장, 경화 라미네이트 warp/fill 동일값" | orientation="warp=fill" | '
               'temperature_C=23',
  'dev_pv': 13237,
  'canon_dev_pv': 13180},
 {'material': 'NBR nitrile rubber (Íñiguez-Macedo et al. 2019 inverse-analysis characterization)',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 2144000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'computed',
  'source_title': 'Finite Element Model Updating Combined with Multi-Response Optimization for '
                  'Hyper-Elastic Materials Characterization',
  'conditions': {'temperature_C': 23,
                 'method_detail': 'Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 1827 전단·ISO 7743 '
                                  '압축·평면응력·체적압축 5종 표준시험의 힘-변위 곡선을 MSC Marc 파라메트릭 FE 모델로 재현하고 '
                                  'MRS+desirability로 역해석 동정한 값',
                 'model': 'Gent',
                 'standard': 'ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편은 ISO 471:1995 조건화)'},
  'canonical': 'method_detail="Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 18 | model="Gent" | '
               'temperature_C=23 | test_standard="ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편',
  'dev_pv': 13238,
  'canon_dev_pv': 13181},
 {'material': 'PUR polyurethane rubber (Íñiguez-Macedo et al. 2019 inverse-analysis '
              'characterization)',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 2982000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'computed',
  'source_title': 'Finite Element Model Updating Combined with Multi-Response Optimization for '
                  'Hyper-Elastic Materials Characterization',
  'conditions': {'temperature_C': 23,
                 'method_detail': 'Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 1827 전단·ISO 7743 '
                                  '압축·평면응력·체적압축 5종 표준시험의 힘-변위 곡선을 MSC Marc 파라메트릭 FE 모델로 재현하고 '
                                  'MRS+desirability로 역해석 동정한 값',
                 'model': 'Gent',
                 'standard': 'ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편은 ISO 471:1995 조건화)'},
  'canonical': 'method_detail="Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 18 | model="Gent" | '
               'temperature_C=23 | test_standard="ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편',
  'dev_pv': 13239,
  'canon_dev_pv': 13182},
 {'material': 'EVA ethylene-vinyl acetate elastomer (Íñiguez-Macedo et al. 2019 inverse-analysis '
              'characterization)',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 2237000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'computed',
  'source_title': 'Finite Element Model Updating Combined with Multi-Response Optimization for '
                  'Hyper-Elastic Materials Characterization',
  'conditions': {'temperature_C': 23,
                 'method_detail': 'Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 1827 전단·ISO 7743 '
                                  '압축·평면응력·체적압축 5종 표준시험의 힘-변위 곡선을 MSC Marc 파라메트릭 FE 모델로 재현하고 '
                                  'MRS+desirability로 역해석 동정한 값',
                 'model': 'Gent',
                 'standard': 'ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편은 ISO 471:1995 조건화)'},
  'canonical': 'method_detail="Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 18 | model="Gent" | '
               'temperature_C=23 | test_standard="ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편',
  'dev_pv': 13240,
  'canon_dev_pv': 13183},
 {'material': 'SBR styrene-butadiene rubber (Íñiguez-Macedo et al. 2019 inverse-analysis '
              'characterization)',
  'property_key': 'mechanical.youngs_modulus',
  'value_num': 1899000.0,
  'value_text': None,
  'unit': 'Pa',
  'method': 'computed',
  'source_title': 'Finite Element Model Updating Combined with Multi-Response Optimization for '
                  'Hyper-Elastic Materials Characterization',
  'conditions': {'temperature_C': 23,
                 'method_detail': 'Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 1827 전단·ISO 7743 '
                                  '압축·평면응력·체적압축 5종 표준시험의 힘-변위 곡선을 MSC Marc 파라메트릭 FE 모델로 재현하고 '
                                  'MRS+desirability로 역해석 동정한 값',
                 'model': 'Gent',
                 'standard': 'ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편은 ISO 471:1995 조건화)'},
  'canonical': 'method_detail="Gent 초탄성 모델 상수 E (미소변형 인장탄성률). ISO 37 인장·ISO 18 | model="Gent" | '
               'temperature_C=23 | test_standard="ISO 37:2017 / ISO 1827:2007 / ISO 7743:2017 (시편',
  'dev_pv': 13241,
  'canon_dev_pv': 13184}]


def _find(conn, r):
    """내용으로 대응행을 찾는다. 유일하지 않거나 없으면 None."""
    mid = conn.execute(sa.text("select id from material where name=:n"),
                       {"n": r["material"]}).fetchall()
    sid = conn.execute(sa.text("select id from source where title=:t"),
                       {"t": r["source_title"]}).fetchall()
    if len(mid) != 1 or len(sid) != 1:
        return None
    hits = []
    for pid, cond in conn.execute(sa.text(
            "select id, conditions from property_value where material_id=:m and property_key=:k "
            "and value_num is :vn and value_text is :vt and unit is :u and method=:me "
            "and source_id=:s"),
            {"m": mid[0][0], "k": r["property_key"], "vn": r["value_num"],
             "vt": r["value_text"], "u": r["unit"], "me": r["method"], "s": sid[0][0]}):
        try:
            d = json.loads(cond) if cond else {}
        except (TypeError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        # 판정 키를 뺀 나머지가 계획과 같아야 한다 — 그래서 재실행에 멱등하다.
        if {k: v for k, v in d.items() if k not in (K_OF, K_NOTE)} == r["conditions"]:
            hits.append((pid, d))
    return hits[0] if len(hits) == 1 else None


def upgrade() -> None:
    conn = op.get_bind()
    hit = miss = 0
    for r in ROWS:
        f = _find(conn, r)
        if not f:
            miss += 1
            continue
        pid, cond = f
        new = dict(cond)
        new[K_OF] = r["canonical"]
        new[K_NOTE] = NOTE
        if new != cond:
            conn.execute(sa.text("update property_value set conditions=:c where id=:i"),
                         {"c": json.dumps(new, ensure_ascii=False), "i": pid})
        hit += 1
    print(f"[w52nb] 중복 표시 {hit}행 · 대응행 못 찾음 {miss}행")


def downgrade() -> None:
    conn = op.get_bind()
    back = 0
    for r in ROWS:
        f = _find(conn, r)
        if not f:
            continue
        pid, cond = f
        new = {k: v for k, v in cond.items() if k not in (K_OF, K_NOTE)}
        if new != cond:
            conn.execute(sa.text("update property_value set conditions=:c where id=:i"),
                         {"c": json.dumps(new, ensure_ascii=False), "i": pid})
            back += 1
    print(f"[w52nb] 중복 표시 제거 {back}행")
