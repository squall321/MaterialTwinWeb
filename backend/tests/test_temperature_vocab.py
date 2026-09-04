# `app/temperature_vocab.py` 단위시험 — 라이브에 실재하는 표기 142종을 전부 넣어 접히는지 본다(63차 YA).
"""이 시험의 자료는 **라이브 DB 전수**다.

`conditions.temperature` 를 가진 2,255행에서 뽑은 서로 다른 표기 **142종**이고,
주석의 행수가 2026-09-04 라이브의 실측이다. 새 표기가 들어오면 이 목록에 없을 뿐
시험이 깨지지는 않으므로, **어휘를 고칠 때는 census 를 다시 돌려 목록을 갱신해라**
(`backend/scripts/catalog/out_ya/census_ya.py`).

갈래가 여섯이다.
  · `ROOM_SPELLINGS`     — 원문이 상온이라고 말한 51종 1,495행
  · `ABSENT_SPELLINGS`   — 원문이 안 찍었다고 말한 37종 492행
  · `NUMERIC_SPELLINGS`  — 숫자를 인쇄한 44종 196행. 접지 않고 `kelvin()` 이 수를 돌린다
  · `UNFOLDED_SPELLINGS` — 접을 수 없는 4종 53행. **`None` 은 "비워라" 가 아니라 "손대지 마라" 다**
  · `DEFECT_SPELLINGS`   — 절대영도 이하 2종 2행. 옮길 값이 아니라 신고할 결함이다
  · `BARE_SPELLINGS`     — 단위 없는 맨 숫자 4종 17행. 단위는 옆 칸이 답한다
"""
import pytest

from app.temperature_vocab import (
    NOT_REPORTED, ROOM, head, kelvin, normalize, printed)


ROOM_SPELLINGS = (
    'room temperature',  # 482행
    'room temperature (no numeric value printed)',  # 322행
    'room temperature (lab ambient; not stated in paper)',  # 295행
    '실온',  # 47행
    'room temperature (논문에 온도 미기재, 실험실 단축인장)',  # 40행
    '실온(측정)',  # 30행
    '실온(상온 측정)',  # 30행
    'room temperature (원문 표기; 수치 미인쇄)',  # 17행
    'RT',  # 15행
    'room temperature (논문에 온도 미기재)',  # 14행
    "room temperature (출처가 'at room temperature'로만 적고 숫자를 인쇄하지 않는다)",  # 14행
    'room temperature (수치 미인쇄)',  # 13행
    'ambient',  # 12행
    'room temperature (not numerically stated in source)',  # 12행
    "ambient (수치 미인쇄 - 원문이 'Ambient' 로만 인쇄한다)",  # 12행
    'room temperature (수치 미인쇄 — 등온 압축, 온도항 미사용)',  # 12행
    'room temperature — 온도항(m) 미피팅. 등온 낙하추 압축',  # 12행
    'room temperature (표 캡션)',  # 10행
    'ambient (not stated on TDS)',  # 8행
    'room temperature (not numerically stated)',  # 7행
    'room temperature, ambient air',  # 7행
    'room temperature(원문 인쇄)',  # 7행
    'ambient (표에 온도 명시 없음)',  # 6행
    'room temperature (8.5절 서두 표기)',  # 6행
    'room temperature (논문이 수치로 명시하지 않음)',  # 5행
    'room temperature (JC reference state)',  # 5행
    'ambient (not stated in catalog)',  # 4행
    'room temperature (not stated numerically)',  # 4행
    'RT (room temperature, 시트 표기)',  # 4행
    'isothermal room temperature (논문에 수치 미기재)',  # 4행
    "room temperature (원문 Table 1 캡션 verbatim 'Material properties at room temperature'; 구체 온도는 미인쇄)",  # 4행
    'room temperature (원문 미인쇄)',  # 4행
    'room temperature (not stated in TDS)',  # 3행
    'room temperature (as printed)',  # 3행
    "room temperature (표 캡션 'Typical room temperature properties of PG')",  # 3행
    "ambient (원문이 'ambient temperature' 로만 인쇄한다 — 구체 온도값 없음)",  # 3행
    'RT (room temperature, per TDS)',  # 2행
    "room temperature (출처가 'All properties are room temperature values'로만 표기, 수치 미인쇄)",  # 2행
    'room temperature (측정 온도 미인쇄 — 4점 프로브 상온 측정)',  # 2행
    'near room temperature (원문 표기 그대로 — 숫자 온도는 인쇄되지 않는다)',  # 2행
    'RT (원문 표기, 수치 미기재)',  # 1행
    'room temperature (not stated in PDS)',  # 1행
    'room temperature (원 데이터 COMMENTS 기재)',  # 1행
    'room temperature, no humidity control',  # 1행
    "room temperature (8.5절 서두 'At room temperature' 표기)",  # 1행
    "room temperature (8.5절 서두 'At room temperature' 표기, 수치 미인쇄)",  # 1행
    'room temperature, dry air',  # 1행
    'room temperature (as-deposited, no numeric value printed)',  # 1행
    "ambient (본문 verbatim 'under ambient conditions')",  # 1행
    "room temperature (표 캡션, 본문이 'at room temperature' 로 재확인)",  # 1행
    'room temperature (시험온도 미인쇄 — 상온 전단시험)',  # 1행
)

ABSENT_SPELLINGS = (
    'not printed',  # 120행
    '원문 미인쇄(실온)',  # 86행
    'not cited',  # 71행
    'not stated in source',  # 52행
    'not stated on sheet (ambient)',  # 20행
    '원문 미인쇄(실온 시험)',  # 20행
    '원문 미인쇄 — 시트가 시험온도를 적지 않는다(템퍼링온도 곡선)',  # 19행
    '**미인쇄** — 실온으로 추정되나 논문이 적지 않아 tier2 로 둔다',  # 18행
    'not reported',  # 13행
    '미인쇄',  # 12행
    'not stated in source — 시트/표에 측정온도가 인쇄되지 않았다(상온 물성표)',  # 9행
    '원문 미인쇄 — 시트의 `Mechanical data` 블록이 시험온도를 적지 않는다',  # 6행
    '미상 — 논문이 시험 온도·습도를 미기재',  # 4행
    'not printed (ambient, tested within 72 h of coating)',  # 4행
    'not stated in source (room-temperature UNAT/Berkovich indentation)',  # 4행
    '원문 미인쇄 — 성형·후경화가 모두 175 C',  # 4행
    '논문에 미인쇄(상온)',  # 3행
    '미상 — 인용 문장에 미기재',  # 2행
    '논문에 미인쇄',  # 2행
    'not stated in Table 2',  # 2행
    'not explicitly stated for the loss factor; the paired storage-modulus values in the same paragraph are quoted at 27.6 C',  # 2행
    'not stated numerically (room temperature)',  # 2행
    '원문 미인쇄 — 표가 시험온도를 적지 않는다',  # 2행
    'not stated in source (room temperature test)',  # 2행
    '미상 — 초록에 미기재, 본문 유료(IOP)',  # 1행
    'not reported (contact angles measured with Kruss DSA II)',  # 1행
    '미상 — 원문이 ASTM F1249만 명시하고 시험 온도/습도를 미기재',  # 1행
    '미상 — 원문이 WVTR 시험 온도를 미기재',  # 1행
    'not stated in RN table (ambient)',  # 1행
    'not stated in Table 1 (동일 계열 Film 2 는 Table 4 에서 121 C 기준으로 2.0 로 인쇄)',  # 1행
    'not stated in Table 1',  # 1행
    'not stated in Table 2 (Table 4 의 동급품은 25 C 에서 0.8 uohm*m)',  # 1행
    'not stated in Table 2 (Table 4 의 동급품은 121 C 에서 10.0)',  # 1행
    'not printed (해석 입력값 — 응력자유온도 298 K 기준 모델)',  # 1행
    'not printed (해석 입력값, 233-398 K 열충격 해석에 단일값으로 사용)',  # 1행
    'not stated in source — Table 1 은 상온 물성표다',  # 1행
    '미기재 — 시험 온도가 인쇄돼 있지 않다. 같은 TDS 같은 칸에서 온 영률 행(pv12194)도 같은 이유로 온도를 비워 두었다.',  # 1행
)

NUMERIC_SPELLINGS = (
    ('20 degC', 293.15),  # 25행
    ('23 C', 296.15),  # 21행
    ('180 degC', 453.15),  # 19행
    ('150 degC', 423.15),  # 11행
    ('100 C', 373.15),  # 11행
    ('80 C', 353.15),  # 10행
    ('90 C', 363.15),  # 10행
    ('70 degC', 343.15),  # 7행
    ('300 degC', 573.15),  # 7행
    ('25 degC', 298.15),  # 7행
    ('200 degC, held 30 min', 473.15),  # 6행
    ('23 C / 50 %RH', 296.15),  # 5행
    ('25 C', 298.15),  # 4행
    ('573 K', 573.0),  # 4행
    ('550 degC', 823.15),  # 4행
    ('25 °C', 298.15),  # 4행
    ('300 K', 300.0),  # 3행
    ('70 C', 343.15),  # 2행
    ('65 C', 338.15),  # 2행
    ('120 degC', 393.15),  # 2행
    ('200 degC', 473.15),  # 2행
    ('160 degC', 433.15),  # 2행
    ('298 K', 298.0),  # 2행
    ('-200 degC', 73.15),  # 2행
    ('26 degC', 299.15),  # 2행
    ('23 degC', 296.15),  # 2행
    ('80 degC', 353.15),  # 2행
    ('177 C', 450.15),  # 2행
    ('200 C', 473.15),  # 1행
    ('683 degC', 956.15),  # 1행
    ('629 degC', 902.15),  # 1행
    ('699 degC', 972.15),  # 1행
    ('493 degC', 766.15),  # 1행
    ('530 degC', 803.15),  # 1행
    ('411 degC', 684.15),  # 1행
    ('402 degC', 675.15),  # 1행
    ('21 degC', 294.15),  # 1행
    ('10 degC', 283.15),  # 1행
    ('50C', 323.15),  # 1행
    ('20 C', 293.15),  # 1행
    ('125 degC', 398.15),  # 1행
    ('40 degC', 313.15),  # 1행
    ('50 degC', 323.15),  # 1행
    ('25 C (ambient)', 298.15),  # 1행
)

UNFOLDED_SPELLINGS = (
    'normal temperature and pressure',  # 48행
    'ISO 291 – 23/50 (표준상태, 원문 절 머리글)',  # 3행
    'hot or cold',  # 1행
    "논문이 -40~120 C 등온선을 재지만 10^6 Hz M'' 피크가 어느 등온선인지 명시하지 않는다",  # 1행
)

DEFECT_SPELLINGS = (
    '-343 K',  # 1행
    '-573 K',  # 1행
)

# 맨 숫자 — 문자열이 아니라 수가 그대로 앉아 있다. 단위를 문자열이 안 들고 있다.
BARE_SPELLINGS = (
    300,  # 8행
    298.15,  # 6행
    293.15,  # 2행
    296.15,  # 1행
)

# ── 갈래별 전수 ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("raw", ROOM_SPELLINGS)
def test_room_spellings_fold_to_one(raw):
    """상온 진술 51종이 정규값 하나로 접힌다. 숫자는 안 나온다."""
    assert normalize(raw) == ROOM
    assert kelvin(raw) is None
    assert printed(raw) is None


@pytest.mark.parametrize("raw", ABSENT_SPELLINGS)
def test_absent_spellings_fold_to_one(raw):
    """부재 진술 37종이 정규값 하나로 접힌다. **뒤에 숫자가 있어도 안 읽는다.**"""
    assert normalize(raw) == NOT_REPORTED
    assert kelvin(raw) is None
    assert printed(raw) is None


@pytest.mark.parametrize("raw,expect_k", NUMERIC_SPELLINGS)
def test_numeric_spellings_convert(raw, expect_k):
    """숫자 표기 44종이 켈빈으로 환산된다. **접지는 않는다** — 진술이 아니라 값이다."""
    assert kelvin(raw) == expect_k
    assert normalize(raw) is None


@pytest.mark.parametrize("raw", UNFOLDED_SPELLINGS)
def test_unfolded_spellings_stay(raw):
    """접을 수 없는 4종. `None` 은 **손대지 말라**는 뜻이지 비우라는 뜻이 아니다."""
    assert normalize(raw) is None
    assert kelvin(raw) is None


@pytest.mark.parametrize("raw", DEFECT_SPELLINGS)
def test_absolute_zero_is_not_a_value(raw):
    """절대영도 이하는 옮길 값이 아니다 — `printed()` 는 읽되 `kelvin()` 은 거절한다."""
    assert printed(raw) is not None
    assert kelvin(raw) is None


def test_every_live_spelling_is_covered():
    """142종이 여섯 갈래로 남김없이 갈린다 — 겹치지도 빠지지도 않는다."""
    groups = (ROOM_SPELLINGS, ABSENT_SPELLINGS, tuple(r for r, _ in NUMERIC_SPELLINGS),
              UNFOLDED_SPELLINGS, DEFECT_SPELLINGS, BARE_SPELLINGS)
    allv = [r for g in groups for r in g]
    assert len(allv) == len(set(allv)) == 142


# ── 판정 순서(머리절 규율) ────────────────────────────────────────────────────

def test_head_clause_wins_over_trailing_number():
    """§551 부류의 오탐을 막는 규율 — 뒤쪽 숫자는 **다른 것의 온도**다.

    `tie_verdicts.temp_c` 는 문자열 전체를 정규식으로 훑어 이 셋에서 숫자를 읽는다.
    """
    for raw in ('not printed (해석 입력값 — 응력자유온도 298 K 기준 모델)',
                'not explicitly stated for the loss factor; the paired storage-modulus '
                'values in the same paragraph are quoted at 27.6 C',
                'not stated in Table 2 (Table 4 의 동급품은 25 C 에서 0.8 uohm*m)',
                '원문 미인쇄 — 성형·후경화가 모두 175 C'):
        assert normalize(raw) == NOT_REPORTED
        assert kelvin(raw) is None


def test_head_clause_absence_beats_trailing_room_word():
    """`'원문 미인쇄(실온)'` 의 주장은 머리절이다 — 괄호는 배치의 추정이지 원문이 아니다."""
    assert normalize('원문 미인쇄(실온)') == NOT_REPORTED
    assert normalize('not stated numerically (room temperature)') == NOT_REPORTED
    # 반대 방향 — 머리절이 상온이면 괄호가 부재를 말해도 상온 진술이다.
    assert normalize('ambient (not stated on TDS)') == ROOM
    assert normalize('room temperature (no numeric value printed)') == ROOM


def test_partial_number_is_not_a_temperature():
    """머리절 **전체**가 온도 표기여야 읽는다. 부분일치는 표준코드를 온도로 만든다."""
    assert kelvin('ISO 291 – 23/50 (표준상태, 원문 절 머리글)') is None
    assert kelvin('hot or cold') is None
    assert kelvin('normal temperature and pressure') is None


def test_head_splits_on_the_axes_that_share_this_key():
    """이 키에만 있는 모양 — 온도 뒤에 다른 축이 붙는다. 머리절이 온도를 건진다."""
    assert head('23 C / 50 %RH') == '23 C'
    assert head('200 degC, held 30 min') == '200 degC'
    assert head('25 C (ambient)') == '25 C'


# ── 단위 환산 ────────────────────────────────────────────────────────────────

def test_unit_conversion_is_a_scale_change_not_a_new_value():
    """섭씨·켈빈·화씨 셋을 같은 눈금으로 옮긴다(§43 의 역산 금지선 밖이다)."""
    assert kelvin('25 C') == 298.15
    assert kelvin('25 degC') == 298.15
    assert kelvin('25 °C') == 298.15
    assert kelvin('50C') == 323.15
    assert kelvin('300 K') == 300.0
    assert kelvin('-200 degC') == 73.15          # 극저온은 정당한 값이다
    assert kelvin('32 F') == 273.15
    assert printed('20 degC') == (20.0, 'C')
    assert printed('573 K') == (573.0, 'K')


def test_bare_number_has_no_unit_so_it_is_not_read():
    """맨 숫자는 단위를 모른다 — 어휘표가 단위를 지어내지 않는다(§443).

    라이브의 맨 숫자 17행 중 8행은 옆 칸 `temperature_unit: "K"` 가 단위를 답한다.
    그 판단은 행마다 근거를 적는 이관 스크립트의 몫이다.
    """
    for raw in BARE_SPELLINGS:
        assert kelvin(raw) is None
        assert normalize(raw) is None


def test_empty_and_none_are_silent():
    for raw in (None, '', '   ', True, False):
        assert normalize(raw) is None
        assert kelvin(raw) is None
