# `conditions.temperature` 자유서술을 최소 정규어휘로 접고, 그 문자열이 온도를 실제로 인쇄했는지 답하는 어휘표.
"""온도 조건의 정규 어휘(63차 YA).

라이브 `conditions.temperature`(구식 문자열 키) 2,255행이 자유형식 **142종**이다.
`'room temperature'` · `'room temperature (no numeric value printed)'` ·
`'원문 미인쇄(실온)'` · `'RT'` 가 전부 따로 산다. 그런데 이 흔들림은 **값의 결함이 아니다** —
원문이 온도를 안 찍었다는 정직한 진술이고, 숫자로 바꾸면 없는 정밀도를 만든다(§43·451).
그래서 이 모듈은 **접기만 한다** — `direction_vocab` 이 `direction` 에 한 것과 같은 자리다.

두 갈래를 가른다. **둘 다 "원문에 숫자가 없다" 인데 주장이 다르다.**
  · `ROOM`         — 원문이 *상온에서 쟀다고 말한다*(room temperature · ambient · RT · 실온).
  · `NOT_REPORTED` — 원문이 *아무 말도 안 한다*(not printed · not stated · 미인쇄 · 미상).
섞으면 다음 파동이 "상온이라 안 적었나" 와 "아무도 안 봤나" 를 못 가른다(§609 의 갈래 규율).

**숫자가 인쇄된 문자열은 이 두 갈래 어디에도 안 넣는다.** `printed()`·`kelvin()` 이 그 갈래고,
거기서 나온 수는 `temperature_k` 로 옮길 값이다(단위 환산은 같은 양을 다른 눈금으로 옮기는
것이라 §43 의 역산 금지선 밖이다). 원문 표기는 `temperature_before_correction` 이 지킨다(§594).

판정 순서가 규율이다 — `direction_vocab` 의 순서를 그대로 쓴다.
  ① **머리절**(첫 괄호·엠대시·세미콜론·쉼표·슬래시 앞)이 그 행의 주장이다.
     `'not printed (해석 입력값 — 응력자유온도 298 K 기준 모델)'` 의 `298 K` 는 **모델의 기준온도**지
     이 측정의 온도가 아니다. 문자열 전체를 정규식으로 훑으면 그것을 시험온도로 만든다
     (`tie_verdicts.temp_c` 가 지금 그렇게 읽는다 — §551 과 같은 부류의 오탐이다).
  ② 머리절이 부재 진술이면 → `NOT_REPORTED`. 뒤에 `(실온)` 이 붙어 있어도 그렇다 —
     **머리절이 주장이고 괄호는 배치의 추정**이다(§505 — 확인하지 않은 것은 판정이 아니다).
  ③ 머리절이 상온 낱말이면 → `ROOM`.
  ④ 머리절이 **순수 온도 표기**(`20 degC` · `573 K` · `-200 degC`)면 정규값이 없다 —
     `printed()` 가 그 수를 돌려준다.
  ⑤ 그 밖은 `None` 이다. **`None` 은 "접지 않는다" 지 "비운다" 가 아니다** —
     `direction` 은 미배정을 `null` 로 비웠지만(§537) 여기서는 **원문이 진술이라 지우면 안 된다.**
     `'normal temperature and pressure'`(NTP 가 20 °C 인지 0 °C 인지 판이 갈린다) ·
     `'hot or cold'` · 구간 서술이 여기 있다.

**절대영도 이하는 값이 아니다.** `kelvin()` 이 `None` 을 돌린다 — 라이브에 `'-343 K'`·`'-573 K'`
두 행이 있고 그것은 옮길 값이 아니라 신고할 결함이다(§603).
"""
from __future__ import annotations

import re

ROOM = "room temperature"
NOT_REPORTED = "not reported"
CANONICAL = (ROOM, NOT_REPORTED)

# 머리절 구분자. `direction_vocab._HEAD_SPLIT` 에 쉼표·슬래시를 더했다 —
# `'23 C / 50 %RH'` · `'200 degC, held 30 min'` 처럼 **온도 뒤에 다른 축이 붙는 표기**가
# 이 키에만 있다. `'room temperature, ambient air'` 도 같은 모양이라 손해가 없다.
_HEAD_SPLIT = re.compile(r"\(|—|;|,|/|\s--\s|\s-\s")

# 마크다운 강조·따옴표는 낱말이 아니다(`'**미인쇄** — …'` 가 라이브에 18행 있다).
_STRIP = re.compile(r"[*`\"'‘’“”]+")

_UNKNOWN = re.compile(
    r"not printed|not stated|not reported|not cited|not specified|not given|"
    r"not explicitly stated|not recorded|unspecified|unstated|no numeric|"
    r"미인쇄|미기재|미표기|미상|미제시|없음", re.I)
_ROOM = re.compile(
    r"room temperature|room-temperature|\bambient\b|\bRT\b|\b상온\b|\b실온\b", re.I)

# 순수 온도 표기 — 머리절 **전체**가 이것이어야 한다. 부분일치로 읽으면
# `'ISO 291 – 23/50'` 의 `23` 이나 서술 안의 `27.6 C` 가 시험온도가 된다.
_PURE_TEMP = re.compile(
    r"^(?P<num>[-+]?\d+(?:\.\d+)?)\s*(?:°\s*|deg\s*|degrees?\s*)?(?P<unit>[CKF])$", re.I)

_TO_K = {"C": lambda v: v + 273.15,
         "K": lambda v: v,
         "F": lambda v: (v - 32.0) / 1.8 + 273.15}


def _clean(raw) -> str:
    if raw is None or isinstance(raw, bool):
        return ""
    return " ".join(_STRIP.sub("", str(raw)).split())


def head(raw) -> str:
    """그 행의 주장이 실린 머리절. 판정도 신고도 이것만 읽는다."""
    s = _clean(raw)
    return _HEAD_SPLIT.split(s, 1)[0].strip() if s else ""


def normalize(raw) -> str | None:
    """원문 → 정규값(`ROOM`·`NOT_REPORTED`). 접을 수 없으면 `None`.

    **`None` 은 원문을 지우라는 뜻이 아니다** — 접지 않고 그대로 둔다는 뜻이다.
    숫자를 인쇄한 문자열도 `None` 이다(그쪽은 `kelvin()` 이 답한다).
    """
    h = head(raw)
    if not h:
        return None
    if _UNKNOWN.search(h):
        return NOT_REPORTED
    if _PURE_TEMP.match(h):
        return None
    if _ROOM.search(h):
        return ROOM
    return None


def printed(raw) -> tuple[float, str] | None:
    """원문 → (인쇄된 수, 인쇄된 단위 `C`·`K`·`F`). 순수 온도 표기가 아니면 `None`.

    **머리절만 본다.** 부재 진술·상온 진술이 머리절이면 뒤에 숫자가 있어도 `None` 이다 —
    그 숫자는 이 측정의 온도가 아니라 다른 것의 온도다.
    """
    h = head(raw)
    if not h or _UNKNOWN.search(h) or _ROOM.search(h):
        return None
    m = _PURE_TEMP.match(h)
    if not m:
        return None
    return float(m.group("num")), m.group("unit").upper()


def kelvin(raw) -> float | None:
    """원문 → 켈빈. 못 읽으면 `None`. **절대영도 이하도 `None`** — 결함이지 값이 아니다.

    맨 숫자(`298.15`)는 단위를 모르므로 `None` 이다. 그 행의 단위는 **옆 칸**이 답한다
    (라이브 8행이 `temperature_unit: "K"` 를 같이 갖고 있다) — 그 판단은 이관 스크립트가
    행마다 근거를 적어서 한다. 어휘표가 단위를 지어내지는 않는다(§443).
    """
    p = printed(raw)
    if p is None:
        return None
    v, u = p
    k = _TO_K[u](v)
    return None if k <= 0 else round(k, 4)
