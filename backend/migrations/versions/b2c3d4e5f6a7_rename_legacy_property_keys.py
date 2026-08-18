"""옛 물성키 둘을 새 키로 옮긴다 — 스케일·온도를 조건축으로 올린 결과를 배포본에도 반영한다.

40차 BE 와 39차 BA 가 키를 **일반화**했다.

* ``mechanical.hardness_rockwell_c`` → ``mechanical.hardness_rockwell`` + ``conditions.scale='C'``
  로크웰은 한 시험의 **스케일 파라미터**(압자·하중만 다르다)라 C·B·R·M 마다 키를 열면
  무한히 늘고 "이 재료에 로크웰이 있나" 를 키 합집합으로 물어야 한다. 스케일 간 환산식은 없다.
* ``thermal.decomposition_time_t260`` → ``thermal.time_to_delamination`` + ``conditions.temperature_c=260``
  IPC-TM-650 2.4.24.1 의 시험 이름이 ``Time to Delamination`` 이고 **유지온도는 파라미터**다.
  시트가 T-260·T-288·T-300 을 같은 블록에 인쇄하므로 온도마다 키를 열면 같은 물리량이 셋으로 갈린다.

개발 DB 에서는 배치가 SQL 로 옮겼지만 **운영(cae00) DB 에는 그 경로가 없다** —
병합 스크립트는 더하기만 하므로 옛 키 행이 그대로 남아 새 키 행과 공존한다(실측: 14행 + 15행).
그래서 마이그레이션으로 옮긴다. 부팅 때 자동으로 돈다.

``migrated_from`` 을 조건에 남겨 되돌릴 수 있게 한다.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

# (옛 키, 새 키, 조건에 추가할 것)
_MOVES = [
    ("mechanical.hardness_rockwell_c", "mechanical.hardness_rockwell", {"scale": "C"}),
    ("thermal.decomposition_time_t260", "thermal.time_to_delamination", {"temperature_c": 260}),
]


def _move(conn, old_key: str, new_key: str, extra: dict) -> int:
    # 옛 키가 없으면 할 일이 없다(이미 옮겼거나 애초에 없던 DB).
    if not conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": old_key}).fetchone():
        return 0
    # **새 키 정의가 아직 없을 수 있다** — 정의는 앱 부팅 시드나 병합으로 오는데
    # 마이그레이션은 그보다 먼저 돈다(실측: 운영 DB 예행에서 이 조건 때문에 통째로 건너뛰었다).
    # 없으면 **옛 정의 행의 key 를 그대로 개명**한다. FK 가 key 를 참조하므로 자식 행이 따라온다.
    if not conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": new_key}).fetchone():
        conn.execute(sa.text("update property_definition set key=:nk where key=:ok"),
                     {"nk": new_key, "ok": old_key})
    rows = conn.execute(sa.text(
        "select id, conditions from property_value where property_key=:k"), {"k": old_key}).fetchall()
    for pid, cond in rows:
        try:
            d = json.loads(cond) if cond else {}
        except (TypeError, ValueError):
            d = {}
        if not isinstance(d, dict):
            d = {}
        d.update(extra)
        d.setdefault("migrated_from", old_key)
        conn.execute(sa.text(
            "update property_value set property_key=:nk, conditions=:c where id=:i"),
            {"nk": new_key, "c": json.dumps(d, ensure_ascii=False), "i": pid})
    # 능력행도 같은 키를 참조한다(시험장비 카탈로그).
    conn.execute(sa.text(
        "update instrument_capability set property_key=:nk where property_key=:ok"),
        {"nk": new_key, "ok": old_key})
    # 개명이 아니라 병합(새 키가 이미 있던 경우)이면 옛 정의를 지운다.
    conn.execute(sa.text("delete from property_definition where key=:k"), {"k": old_key})
    return len(rows)


def upgrade() -> None:
    conn = op.get_bind()
    for old_key, new_key, extra in _MOVES:
        _move(conn, old_key, new_key, extra)


def downgrade() -> None:
    # 되돌리기는 `migrated_from` 표시가 있는 행만 대상으로 한다 — 새로 들어온 행은 건드리지 않는다.
    conn = op.get_bind()
    for old_key, new_key, _extra in _MOVES:
        rows = conn.execute(sa.text(
            "select id, conditions from property_value "
            "where property_key=:nk and conditions like :pat"),
            {"nk": new_key, "pat": f'%"migrated_from": "{old_key}"%'}).fetchall()
        if not rows:
            continue
        conn.execute(sa.text(
            "insert into property_definition (key, domain, name, si_unit) "
            "select :k, domain, name, si_unit from property_definition where key=:nk"),
            {"k": old_key, "nk": new_key})
        for pid, _cond in rows:
            conn.execute(sa.text(
                "update property_value set property_key=:ok where id=:i"),
                {"ok": old_key, "i": pid})
