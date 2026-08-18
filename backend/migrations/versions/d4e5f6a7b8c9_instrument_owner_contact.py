"""instrument 담당자·연락처 — 보유만 알면 '누구에게 말하나'에서 멈춘다

owned 만으로는 시험을 걸 수 없다. 장비가 있다는 것과 그것을 쓸 수 있다는 것은 다르고,
그 사이를 잇는 것이 담당자다. 확인 시각도 함께 둔다 — 오래된 담당자 정보는 없는 것만 못하다.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("instrument", sa.Column("owner_name", sa.String(80), nullable=True))
    op.add_column("instrument", sa.Column("owner_contact", sa.String(160), nullable=True))
    op.add_column("instrument", sa.Column("owned_checked_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("instrument", "owned_checked_at")
    op.drop_column("instrument", "owner_contact")
    op.drop_column("instrument", "owner_name")
