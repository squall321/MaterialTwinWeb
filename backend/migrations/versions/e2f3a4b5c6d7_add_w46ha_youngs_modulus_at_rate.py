"""46차 HA — 율속별 영률 키를 연다. 형제 둘은 있는데 모듈러스만 없어 20행이 막혀 있었다.

45차 GB 가 Chhanda 2012(ITherm)의 Zymet X6-82-5LV50 언더필에서 Fig10(탄성계수)·
Fig11(UTS)의 **5온도 x 4변형률속도 격자**를 벡터 좌표까지 다 읽어 놓고,
UTS 20칸은 기존 ``mechanical.tensile_strength_at_rate`` 로 갈 수 있었지만
**모듈러스 20칸은 담을 키가 없어 notes 에만 남겼다**(브리프 468 —
키 부재는 값 하나가 아니라 갈래 전체를 막는다. 막힌 값의 수를 세어 보고해라).

**왜 새 키인가 — 기존 두 형제와 같은 자리다.**
``mechanical.yield_strength_at_rate`` · ``mechanical.tensile_strength_at_rate`` 는
"한 재료에서 같은 온도에 율속별로 여러 값이 서는 격자" 를 받으려고 이미 갈려 있다.
모듈러스만 ``mechanical.youngs_modulus``(조건축 temperature_k 하나)에 부으면
같은 그림 묶음(Fig10 E · Fig11 UTS)이 두 키로 흩어지고, 대표값 선택이 격자의
아무 칸이나 집는다. 이름·단위·조건축을 형제 둘에 **글자 단위로 맞췄다**(브리프 487).

  mechanical.youngs_modulus_at_rate  [Pa]  조건축 strain_rate_s · temperature_k

**새 조건축 이름을 만들지 않았다** — 운영 DB 실측으로 형제 둘의 율속 축은 전부
``strain_rate_s`` 다(yield 415행 · tensile 349행). 다른 표기(``strain_rate_1/s``)를
여기 끌어오면 어휘가 갈린다(브리프 419).

**왜 마이그레이션이 필요한가** — 개발 DB 는 부팅 시드가 정의를 넣지만 운영 DB 로 가는
경로는 병합 스크립트뿐이고 그건 값만 더한다. 정의 행이 없으면 그 값들이
"정의 없는 물성키" 로 무결성 검사에 걸린다(a8b9c0d1e2f3 · c0d1e2f3a4b5 와 같은 이유).

**전제를 두지 않는다**(b2c3d4e5f6a7 · 브리프 482 의 함정) — 키가 없으면 넣고, 있으면
지나간다. ``property_definition`` 테이블 자체가 없는 아주 오래된 DB 도 그냥 지나간다.
예행은 옛 리비전 운영 DB 사본(``888056f1c5b8``)으로 했다 — 개발 DB(이미 head)로만
돌리면 이 함정이 안 보인다.

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "e2f3a4b5c6d7"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
# app/property_taxonomy.py 의 46차 HA 블록과 **같은 내용**이어야 한다.
_DEFS = [
    ("mechanical.youngs_modulus_at_rate", "mechanical", "변형률속도별 영률", None, "Pa",
     "numeric", ["strain_rate_s", "temperature_k"], None),
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
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다(c0d1e2f3a4b5 와 같은 규율).
    conn = op.get_bind()
    if not _has_table(conn):
        return
    for key in _KEYS:
        if conn.execute(sa.text("select 1 from property_value where property_key=:k limit 1"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
