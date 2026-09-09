"""71차 — 이동인자 a_T 키를 연다. 70차 FD·71차 GA 가 값을 손에 들고도 못 넣었다.

  mechanical.tts_shift_factor  [1]  ← Chowdhury 2019 Table 1(9칸)·Table 3(5칸), 둘 다 T0 = 120 °C

**왜 기존 키로는 안 되는가.**

`wlf_c1`·`wlf_c2` 는 **이동인자를 만들어 내는 식의 계수**이고, a_T 는 **그 식이 내놓는
온도별 값 자체**다. 하나는 모형이고 하나는 자료점이다. 둘은 대체재가 아니다 —
70차 FD 가 실측했다: *"그 논문의 WLF 상수 3벌이 **전부 검산에 실패**한다(원문 Table 3
재현 불가). a_T 표가 유일하게 쓸 수 있는 이동 정보인데 넣을 칸이 없다."*
**모형이 깨져도 자료점은 산다.** 그것이 이 키가 필요한 이유다.

WLF 를 아예 안 쓰는 문서도 있다 — 70차 FD 가 Park 2011·Chae 2010 에서 다항·Arrhenius
이동함수를 봤다. 그런 문서의 이동 정보도 a_T 표로만 들어온다.

**단위는 무차원 1 이다.** 원문이 `a_T` 를 찍든 `log10 a_T` 를 찍든 **DB 에는 a_T 를
넣는다** — 로그를 그대로 넣으면 부호와 밑이 조건에 숨어 같은 칸에 두 가지 양이 섞인다
(브리프 471 — 이름이 아니라 정의식이 키를 정한다). 원문 표기는 조건축
`printed_as`(`a_T`/`log10_a_T`/`ln_a_T`)와 `value_printed` 에 보존한다.

**기준온도는 필수 조건이다.** a_T 는 T0 없이는 뜻이 없다 — 71차 GA 가 같은 이유로
Baek 2008 의 g(t) 30점을 막았다(`relaxation_modulus_normalized` 의 첫 손님이 될 뻔했으나
원문에 T0 가 없었다). 조건축에 `reference_temperature_c` 를 둔다.
"""
from typing import Sequence, Union
import json

import sqlalchemy as sa
from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "b7c6d5e4f3a2"
down_revision: Union[str, Sequence[str], None] = "a9b8c7d6e5f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFS = [
    ("mechanical.tts_shift_factor", "mechanical", "시간-온도 이동인자", "a_T", "1", "numeric",
     ["temperature_c", "reference_temperature_c", "printed_as", "value_printed",
      "relaxation_mode", "shift_function"],
     None),
]
_KEYS = [d[0] for d in _DEFS]


def _has_table(conn, name: str = "property_definition") -> bool:
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
    for key, domain, name, symbol, unit, vtype, axes, std in _DEFS:
        if conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text(
            "insert into property_definition "
            "(key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard) "
            "values (:k, :d, :n, :sy, :u, :v, :a, :s)"),
            {"k": key, "d": domain, "n": name, "sy": symbol, "u": unit, "v": vtype,
             "a": json.dumps(axes, ensure_ascii=False), "s": std})


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
    # 값이 붙은 정의는 지우지 않는다 — 자식 행이 참조하면 "정의 없는 물성키" 가 된다.
    for key in _KEYS:
        if _has_table(conn, "property_value"):
            if conn.execute(sa.text("select count(*) from property_value where property_key=:k"),
                            {"k": key}).scalar():
                continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
