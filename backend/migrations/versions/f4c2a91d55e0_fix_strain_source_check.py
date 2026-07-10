# ck_test_strain_source에 'relaxation' 포함 — c7b6cca38dc2가 nullable만 바꾸고 CHECK를 안 고친 결함 수정.
"""fix strain_source check to include relaxation

Revision ID: f4c2a91d55e0
Revises: e1a9d40b77c1
Create Date: 2026-07-10

배경: c7b6cca38dc2는 alter_column(nullable)만 수행해 Postgres에는 초기 스키마의
CHECK('extensometer','crosshead')가 그대로 남았다(SQLite는 개발 DB가 create_all
출신이라 증상이 가려짐). 완화시험(strain_source='relaxation') INSERT가 PG에서
CheckViolation — 제약을 드롭 후 'relaxation' 포함으로 재생성한다.
"""
from typing import Sequence, Union

from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "f4c2a91d55e0"
down_revision: Union[str, Sequence[str], None] = "e1a9d40b77c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CK = "strain_source IS NULL OR strain_source IN ('extensometer','crosshead','relaxation')"
# downgrade는 초기 스키마(c0fac20ef805)가 만든 원본 CHECK와 문자 그대로 일치시킨다
# (IS NULL OR 접두 없음 — NULL IN(...)=UNKNOWN이라 기능은 동일하나 DDL 드리프트 방지).
_CK_OLD = "strain_source IN ('extensometer','crosshead')"


def upgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        # 리플렉션은 AUTOINCREMENT를 못 잡으므로 재생성 시 명시(e1a9d40b77c1 유지).
        with op.batch_alter_table(
            "test", table_kwargs={"sqlite_autoincrement": True}
        ) as b:
            b.drop_constraint("ck_test_strain_source", type_="check")
            b.create_check_constraint("ck_test_strain_source", _CK)
    else:
        op.drop_constraint("ck_test_strain_source", "test", type_="check")
        op.create_check_constraint("ck_test_strain_source", "test", _CK)


def downgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table(
            "test", table_kwargs={"sqlite_autoincrement": True}
        ) as b:
            b.drop_constraint("ck_test_strain_source", type_="check")
            b.create_check_constraint("ck_test_strain_source", _CK_OLD)
    else:
        op.drop_constraint("ck_test_strain_source", "test", type_="check")
        op.create_check_constraint("ck_test_strain_source", "test", _CK_OLD)
