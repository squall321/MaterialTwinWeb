"""instrument.owned — 카탈로그 보유와 장비 보유를 구분한다

이 표는 '우리가 가진 장비'가 아니라 '카탈로그를 찾을 수 있는 장비' 218대다. 그 구분이
없어서 "사내 장비로 잴 수 있다"는 틀린 답이 나갈 수 있었다(2026-08-19 지적).

기본값 False — 확인되지 않은 것을 보유로 세면 시험 계획이 있지도 않은 장비를 전제한다.
실제 보유가 확인된 것만 나중에 True 로 올린다.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("instrument",
                  sa.Column("owned", sa.Boolean(), nullable=False, server_default="0"))
    op.add_column("instrument", sa.Column("owned_note", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("instrument", "owned_note")
    op.drop_column("instrument", "owned")
