"""70차 — 69차가 값을 손에 들고도 못 넣은 키 둘을 연다.

둘 다 **이미 읽은 원문에 인쇄돼 있는데 담을 칸이 없어** 배치가 보고서에만 적고
넘긴 것이다. 새로 캐지 않았다.

  electrical.withstand_voltage_surface        [V]  ← 69차 EA (Panasonic 특성일람표 `沿層耐電圧`)
  mechanical.relaxation_modulus_normalized    [1]  ← 69차 EC (Baek 2008 무차원 g(t) 30점)

**왜 기존 키로는 안 되는가 — 둘 다 차원이 다르다.**

① ``electrical.dielectric_strength`` 는 **전계**(V/m)다. 시편 두께로 나눈 값이라
   두께가 달라지면 같은 재료도 다른 숫자가 나온다. Panasonic 이 인쇄하는 `沿層耐電圧`
   (연면 내전압)은 **전압**(kV) 자체이고, 분모가 두께가 아니라 **표면을 따라 흐르는
   연면거리**다. 시험 형상이 규격에 고정돼 있어 전압으로 발표한다.
   EA 원문 — "9종 전부 인쇄돼 있으나 `dielectric_strength` 가 V/m 라 담을 수 없다".
   V/m 칸에 kV 를 부으면 자릿수가 통째로 어긋난다.

② ``mechanical.prony_relative_modulus`` 는 **Prony 급수의 항 가중치** g_i 다.
   항 번호와 완화시간이 쌍으로 붙어야 뜻이 서는 이산 파라미터다(검사기가
   `Prony 항에 항번호 없음` · `가중치·완화시간 항수 불일치` 로 잡는다).
   새 키는 **연속 완화곡선의 정규화 값** g(t) = G(t)/G0 이고, 시간축 위의 한 점이다.
   EC 원문 — "무차원 전단완화 곡선값 g(t) 30점을 뽑았지만 `prony_relative_modulus` 는
   Prony 항 가중치 칸이라 **범주 오류**다".
   같은 무차원이라 값 범위가 겹쳐 **더 위험하다** — 섞이면 Prony 적합에 곡선점이
   항 가중치로 들어가 항수 검사를 통과해 버린다.

**이관은 하지 않는다.** 두 키 모두 기존 행에 잘못 담긴 것이 없다 —
`dielectric_strength` 전 행이 V/m 로 일관하고, `prony_relative_modulus` 는
항번호 검사를 이미 통과한 행뿐이다. 정의만 연다.
"""
from typing import Sequence, Union
import json

import sqlalchemy as sa
from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
_DEFS = [
    ("electrical.withstand_voltage_surface", "electrical", "연면 내전압", "V_s", "V", "numeric",
     ["temperature_c", "medium", "creepage_distance_mm", "electrode_geometry", "frequency_hz"],
     "JIS C2110 / IEC 60243"),
    ("mechanical.relaxation_modulus_normalized", "mechanical", "정규화 완화탄성률", "g(t)", "1", "numeric",
     ["time_s", "temperature_c", "reference_temperature_c", "relaxation_mode", "strain_pct"],
     None),
]
_KEYS = [d[0] for d in _DEFS]


def _has_table(conn, name: str = "property_definition") -> bool:
    return sa.inspect(conn).has_table(name)


def _seed_defs(conn) -> None:
    for key, domain, name, symbol, unit, vtype, axes, std in _DEFS:
        if conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text(
            "insert into property_definition "
            "(key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard) "
            "values (:k, :d, :n, :sy, :u, :v, :a, :s)"),
            {"k": key, "d": domain, "n": name, "sy": symbol, "u": unit, "v": vtype,
             "a": json.dumps(axes, ensure_ascii=False) if axes else None, "s": std})


def upgrade() -> None:
    conn = op.get_bind()
    if _has_table(conn):
        _seed_defs(conn)


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
    # **값이 붙은 정의는 지우지 않는다** — 자식 행이 property_key 로 참조하므로
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다.
    for key in _KEYS:
        if _has_table(conn, "property_value"):
            n = conn.execute(sa.text(
                "select count(*) from property_value where property_key=:k"),
                {"k": key}).scalar()
            if n:
                continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
