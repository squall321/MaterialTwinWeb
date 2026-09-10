"""73차 — 시간축 완화탄성률 키를 연다. 71차 GA·72차 HA 가 두 파동째 막혔다.

  mechanical.relaxation_modulus  [Pa]  ← Kenner 1995 등, E(t)/G(t) 의 **절대값**

**왜 기존 키로는 안 되는가 — 세 형제와 전부 다르다.**

  prony_tensile_modulus [Pa]          Prony 급수의 **항** E_i. 항번호·완화시간과 쌍이다
  relaxation_modulus_normalized [1]   무차원 g(t)=G(t)/G0. **곡선의 한 점이되 비율**이다
  youngs_modulus [Pa]                 t=0 의 순간탄성률. 시간축이 없다
  **relaxation_modulus [Pa]           곡선의 한 점의 절대값**

무차원 키(70차 신설)와 이 키는 **같은 곡선의 두 표기**다. 원문이 G0 를 안 찍으면
무차원으로 못 가고, 반대로 정규화만 인쇄한 논문은 절대값으로 못 간다 — **둘 사이
환산은 역산이라 금지**(G0 를 가정해 곱하면 안 된다). 그래서 두 칸이 다 필요하다.

**시간이 조건축의 머리다.** `time_s` 없이는 이 값이 뜻이 없다 — `youngs_modulus`
와 구별되는 것이 그 축뿐이다. 마스터커브면 `reference_temperature_c` 도 필수다
(71차 GA 가 세운 규칙 — 마스터커브는 T0 없이 뜻이 없고, 단일온도 모형은 필요 없다).
"""
from typing import Sequence, Union
import json

import sqlalchemy as sa
from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "2431c015a392"
down_revision: Union[str, Sequence[str], None] = "b7c6d5e4f3a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFS = [
    ("mechanical.relaxation_modulus", "mechanical", "완화탄성률", "E(t)", "Pa", "numeric",
     ["time_s", "temperature_c", "reference_temperature_c", "relaxation_mode",
      "curve_type", "strain_pct"],
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
    for key in _KEYS:
        if _has_table(conn, "property_value"):
            if conn.execute(sa.text("select count(*) from property_value where property_key=:k"),
                            {"k": key}).scalar():
                continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
