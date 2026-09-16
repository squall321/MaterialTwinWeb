"""76차 — 유전율 온도계수(TCDk) 키를 연다. 75차 KC 가 5벤더·19등급에서 찾았다.

  electrical.temperature_coefficient_dielectric_constant  [1/K]

RF 적층판 시트가 Dk 옆에 **ppm/℃** 로 찍는다. 형제 키
`electrical.temperature_coefficient_resistance`(TCR) 와 같은 모양이다 — 1/K 이고
온도 **구간**이 조건이다. ℃ 차이당 계수라 ℃⁻¹ = K⁻¹, 환산은 ×1e-6 뿐이다.

**키를 만들 때 챙길 것 — 75차 KC 의 실사에서 나왔다.**
  · **음수가 정상이다.** 19칸 중 9칸이 음수, 최저는 RO3010 의 −395 ppm/℃ 다.
    적재기 범위 가드는 ±1e-3 1/K 로 둔다 — 음수를 막지 않으면서 ppm 원값(−395)을
    1/K 칸에 그대로 넣는 오입력은 잡는다(TCR 가드와 같은 설계).
  · **측정 구간이 시트마다 다르다** — 표준 −50~150 이지만 CLTE-AT 0~100,
    S7136H −55~85, Shengyi 계 −40~150. `temperature_range_c` 없이는 수를 나란히 못 놓는다.
  · **시험법이 넷이다** — IPC-TM-650 2.5.5.5 / 2.5.5.13 / 2.5.5.15 / IEC 61189-2-721.
  · **방향을 찍는 시트가 있다** — RO4003C·RO4350B·RT/duroid·S7136H 는 Z축.
  · **부호를 안 찍는 시트가 있다** — CLTE(6)·NP-730/822/826. `sign_printed` 로 남긴다.

`app/property_taxonomy.py` 의 76차 블록과 **같은 내용**이어야 한다.
"""
from typing import Sequence, Union
import json

import sqlalchemy as sa
from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "ce8fbafef7ef"
down_revision: Union[str, Sequence[str], None] = "2431c015a392"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFS = [
    ("electrical.temperature_coefficient_dielectric_constant", "electrical",
     "유전율 온도계수(TCDk)", "TCDk", "1/K", "numeric",
     ["temperature_range_c", "frequency_hz", "direction", "test_standard", "sign_printed"],
     "IPC-TM-650 2.5.5.5"),
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
    for key in _KEYS:
        if _has_table(conn, "property_value"):
            if conn.execute(sa.text("select count(*) from property_value where property_key=:k"),
                            {"k": key}).scalar():
                continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
