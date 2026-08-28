"""45차 GC — 화학 내구성(침지 후 감소량) 두 키를 연다. 키 하나가 45칸을 막고 있었다.

44차 FE 가 유리 갈래 표 넷을 수확하면서 **두 표를 통째로 못 넣었다.**
값은 이미 확보돼 있고 담을 키만 없었다(브리프 468 — 키 부재는 값 하나가 아니라
갈래 전체를 막는다).

  AGY 2006 Table 3 `Durability (% weight loss)`  — 유리섬유 8계열 x 4매질 x 2노출
  NEG Powder Glass `Acid durability`             — 봉지 프릿 3등급 x 4조건

**왜 한 키가 아니라 두 키인가 — 차원이 정한다**(브리프 453).
AGY 는 시편 전체 질량에 대한 감소 **비율**(무차원)이고, NEG 는 **단위면적당 감소 질량**
(kg/m^2)이다. 물리적 의미("부식 침지 후 얼마나 줄었나")는 같지만 그것으로 키를 정하지
않는다 — taxonomy 는 키마다 si_unit 이 하나이고, 무결성 검사("단위가 정의와 다름")·
범위 가드·Ashby 축이 전부 그 하나를 읽는다. 둘을 잇는 환산은 시편의 비표면적이 필요한데
두 시트 다 안 찍는다. 41차 CA 의 Charpy(J 대 J/m^2)와 같은 자리다.

**이름은 나란히 지었다** — `chemical.durability_mass_loss_fraction` ·
`chemical.durability_mass_loss_per_area`. 같은 갈래임이 키 이름에서 드러나야
다음 배치가 둘 중 어느 쪽인지를 **차원으로** 고르게 된다.

**시험 규격은 두 시트 다 안 찍는다.** AGY 가 인용하는 ASTM 번호(C162 용어 · C693 밀도 ·
C338 연화점 · C336 서냉·변형점 · C598 · D696 CTE)는 전부 다른 물성의 것이다.
조건축 `test_standard` 는 열어 두되 이 배치에서는 비운다 — 지어내지 않는다.

**왜 마이그레이션이 필요한가** — 개발 DB 는 부팅 시드가 정의를 넣지만 운영 DB 로 가는
경로는 병합 스크립트뿐이고 그건 값만 더한다. 정의 행이 없으면 그 값들이
"정의 없는 물성키" 로 무결성 검사에 걸린다(a8b9c0d1e2f3 와 같은 이유).

**전제를 두지 않는다**(b2c3d4e5f6a7 · 482 의 함정) — 키가 없으면 넣고, 있으면 지나간다.
``property_definition`` 테이블 자체가 없는 아주 오래된 DB 도 그냥 지나간다.

Revision ID: c0d1e2f3a4b5
Revises: b9c0d1e2f3a4
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "c0d1e2f3a4b5"
down_revision = "b9c0d1e2f3a4"
branch_labels = None
depends_on = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
# app/property_taxonomy.py 의 45차 GC 블록과 **같은 내용**이어야 한다.
_AXES = ["medium", "duration_h", "temperature_c", "specimen_form", "test_standard"]
_DEFS = [
    ("chemical.durability_mass_loss_fraction", "chemical", "화학 내구성 중량감소율", None,
     "1", "numeric", _AXES, None),
    ("chemical.durability_mass_loss_per_area", "chemical", "화학 내구성 단위면적당 감소량", None,
     "kg/m^2", "numeric", _AXES, None),
]

_KEYS = [d[0] for d in _DEFS]


def _has_table(conn) -> bool:
    return sa.inspect(conn).has_table("property_definition")


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
             "a": json.dumps(axes, ensure_ascii=False) if axes else None, "s": std})


def downgrade() -> None:
    # **값이 붙은 정의는 지우지 않는다** — 자식 행이 property_key 로 참조하므로
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다(a8b9c0d1e2f3 와 같은 규율).
    conn = op.get_bind()
    if not _has_table(conn):
        return
    for key in _KEYS:
        if conn.execute(sa.text("select 1 from property_value where property_key=:k limit 1"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
