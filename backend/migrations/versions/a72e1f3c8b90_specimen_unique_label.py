# specimen(material_id,label) UNIQUE — 동시 등록의 조용한 중복 라벨을 IntegrityError로 표면화.
"""specimen unique material_id+label

Revision ID: a72e1f3c8b90
Revises: f4c2a91d55e0
Create Date: 2026-07-11
"""
from typing import Sequence, Union

from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "a72e1f3c8b90"
down_revision: Union[str, Sequence[str], None] = "f4c2a91d55e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        # 리플렉션은 AUTOINCREMENT를 못 잡으므로 재생성 시 명시(e1a9d40b77c1 유지 — test 무관하나
        # specimen 테이블엔 AUTOINCREMENT가 없어 kwargs 불필요).
        with op.batch_alter_table("specimen") as b:
            b.create_unique_constraint("uq_specimen_material_label", ["material_id", "label"])
    else:
        op.create_unique_constraint("uq_specimen_material_label", "specimen", ["material_id", "label"])


def downgrade() -> None:
    if op.get_bind().dialect.name == "sqlite":
        with op.batch_alter_table("specimen") as b:
            b.drop_constraint("uq_specimen_material_label", type_="unique")
    else:
        op.drop_constraint("uq_specimen_material_label", "specimen", type_="unique")
