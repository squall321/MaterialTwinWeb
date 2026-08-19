"""압전상수 키를 성분 중립으로 일반화한다 — d33 전용 키에 d31 이 들어올 자리가 없었다.

41차 CA. 40차 BE 의 로크웰 선례(``hardness_rockwell_c`` → ``hardness_rockwell`` + ``scale``)와
같은 판단이다.

* ``electrical.piezoelectric_d33`` → ``electrical.piezoelectric_charge_coefficient``
  + ``conditions.component='33'``

d31·d33·d15 는 **같은 3계 텐서 d_ij 의 성분**이라 단위가 전부 C/N 로 같고 측정도 같다.
성분마다 키를 열면 무한히 늘고 "이 재료에 압전상수가 있나"를 키 합집합으로 물어야 한다.

개발 DB 는 배치가 SQL 로 옮길 수 있지만 **운영(cae00) DB 에는 그 경로가 없다** —
병합 스크립트는 더하기만 하므로 옛 키 행이 그대로 남는다. 그래서 마이그레이션으로 옮긴다.

``migrated_from`` 을 조건에 남겨 되돌릴 수 있게 한다(브리프 162).

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None

_OLD = "electrical.piezoelectric_d33"
_NEW = "electrical.piezoelectric_charge_coefficient"
_EXTRA = {"component": "33"}


def upgrade() -> None:
    conn = op.get_bind()
    if not conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": _OLD}).fetchone():
        return
    # 새 키 정의가 아직 없을 수 있다 — 마이그레이션은 앱 부팅 시드보다 먼저 돈다.
    # 없으면 옛 정의 행의 key 를 개명한다(FK 가 key 를 참조하므로 자식 행이 따라온다).
    if not conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": _NEW}).fetchone():
        conn.execute(sa.text("update property_definition set key=:nk where key=:ok"),
                     {"nk": _NEW, "ok": _OLD})
    rows = conn.execute(sa.text(
        "select id, conditions from property_value where property_key=:k"), {"k": _OLD}).fetchall()
    for pid, cond in rows:
        try:
            d = json.loads(cond) if cond else {}
        except (TypeError, ValueError):
            d = {}
        if not isinstance(d, dict):
            d = {}
        d.update(_EXTRA)
        d.setdefault("migrated_from", _OLD)
        conn.execute(sa.text(
            "update property_value set property_key=:nk, conditions=:c where id=:i"),
            {"nk": _NEW, "c": json.dumps(d, ensure_ascii=False), "i": pid})
    conn.execute(sa.text(
        "update instrument_capability set property_key=:nk where property_key=:ok"),
        {"nk": _NEW, "ok": _OLD})
    conn.execute(sa.text("delete from property_definition where key=:k"), {"k": _OLD})


def downgrade() -> None:
    # 되돌리기는 `migrated_from` 표시가 있는 행만 대상으로 한다.
    conn = op.get_bind()
    rows = conn.execute(sa.text(
        "select id from property_value where property_key=:nk and conditions like :pat"),
        {"nk": _NEW, "pat": f'%"migrated_from": "{_OLD}"%'}).fetchall()
    if not rows:
        return
    conn.execute(sa.text(
        "insert into property_definition (key, domain, name, si_unit) "
        "select :k, domain, name, si_unit from property_definition where key=:nk"),
        {"k": _OLD, "nk": _NEW})
    for (pid,) in rows:
        conn.execute(sa.text("update property_value set property_key=:ok where id=:i"),
                     {"ok": _OLD, "i": pid})
