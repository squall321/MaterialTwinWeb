"""44차 FD — 유리 점도 기준온도 키를 연다. 세 배치가 이 하나에 막혀 있었다.

44차 FA(커버글라스 8종) · FB(디스플레이 기판·몰딩 광학유리 16종) · FC(유리섬유)가
**값을 손에 쥐고도 담을 키가 없어** 변형점·서냉점·리틀턴 연화점·작업점을 버렸다.
이건 등급 하나의 결손이 아니라 **갈래 전체의 표제 물성**이다(브리프 468).

**넷을 한 키로 담은 근거는 차원이다**(브리프 453). 넷 다 K 이고 정의가 하나다 —
"전단점도가 지정된 값이 되는 온도". 다른 것은 지정 점도값뿐이라 파라미터이고,
파라미터는 조건축으로 올린다(40차 로크웰 스케일 · 39차 T-260 유지온도 · 41차 d31/d33 성분).

``conditions.viscosity_log10_poise`` 가 어느 기준점인지 정한다 —
14.5 변형점 · 13.0 서냉점 · 7.6 리틀턴 연화점 · 4.0 작업점.
(시트가 P 와 dPa*s 를 섞어 쓰는데 1 P = 1 dPa*s 라 수가 같다.)

**``thermal.dilatometric_softening_point``(새그온도 Ts)와는 합치지 않았다** —
그건 팽창계가 관측한 온도지 점도로 *정의된* 값이 아니다. 원문이 둘을 같은 표에
나란히 인쇄하므로(OHARA `Yield Point At` 대 `Softening Point SP`,
SCHOTT `AT` 대 `T10^7.6`) 한 키에 넣으면 그 쌍이 깨진다. 44차 FC 가 정확히 짚었다.

**왜 마이그레이션이 필요한가** — 개발 DB 는 부팅 시드(``seed_property_definitions``)가
새 정의를 넣지만, 운영(cae00) DB 로 가는 경로는 병합 스크립트뿐이고 그건 **값만 더한다.**
정의 행이 없으면 그 값들이 "정의 없는 물성키" 로 무결성 검사에 걸린다.

**b2c3d4e5f6a7 이 겪은 함정** — 마이그레이션이 *다른* 행의 존재를 전제하면 운영 DB 에서
조용히 건너뛴다. 여기서는 전제를 두지 않는다: 키가 없으면 넣고, 있으면 지나간다.
``property_definition`` 테이블 자체가 없는 아주 오래된 DB 도 그냥 지나간다.

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "a8b9c0d1e2f3"
down_revision = "f7a8b9c0d1e2"
branch_labels = None
depends_on = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
# app/property_taxonomy.py 의 44차 FD 블록과 **같은 내용**이어야 한다.
_DEFS = [
    ("thermal.viscosity_reference_temperature", "thermal", "점도 기준온도", None, "K",
     "numeric", ["viscosity_log10_poise", "test_standard", "determination"], "ASTM C338"),
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
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다(f7a8b9c0d1e2 와 같은 규율).
    conn = op.get_bind()
    if not _has_table(conn):
        return
    for key in _KEYS:
        if conn.execute(sa.text("select 1 from property_value where property_key=:k limit 1"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
