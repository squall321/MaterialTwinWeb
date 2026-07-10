# test 테이블 SQLite AUTOINCREMENT 적용 — 삭제된 test_id 재사용으로 인한 곡선 파일 오삭제 경합 차단.
"""test sqlite autoincrement

Revision ID: e1a9d40b77c1
Revises: c7b6cca38dc2
Create Date: 2026-07-10
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "e1a9d40b77c1"
down_revision: Union[str, Sequence[str], None] = "c7b6cca38dc2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return  # Postgres 시퀀스는 id를 재사용하지 않음 — 변경 불필요.
    # batch 재생성으로 AUTOINCREMENT 반영(행·FK는 유지, sqlite_sequence는 기존 max id로 시드됨).
    with op.batch_alter_table(
        "test", recreate="always", table_kwargs={"sqlite_autoincrement": True}
    ):
        pass


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        return
    with op.batch_alter_table("test", recreate="always"):
        pass
