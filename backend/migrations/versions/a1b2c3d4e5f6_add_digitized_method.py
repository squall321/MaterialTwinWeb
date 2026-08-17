"""method 에 digitized 를 추가한다 — 그림에서 읽은 값을 인쇄 실측과 구별한다.

40차 BF 가 Uddeholm 금형강의 고온인장·템퍼링 곡선 95행을 디지타이즈해 넣으면서 드러났다.
BF 는 `conditions` 에 `digitized` 와 `figure`(어느 그림인지)를 제대로 남겼는데,
`method` 는 허용값에 없어 `measured` 로 정규화됐다 — **조건을 안 펴 보면 인쇄 실측과 구별이 안 된다.**

로더가 `assumed → estimated` 를 갈라 놓은 것과 같은 이유다
(그 주석: "'assumed'가 measured로 들어가면 논문이 '측정하지 않았다'고 밝힌 값이 실측으로 둔갑한다").

Revision ID: a1b2c3d4e5f6
Revises: 9d623ccf6364
"""
from __future__ import annotations

from alembic import op

revision = "a1b2c3d4e5f6"
down_revision = "9d623ccf6364"
branch_labels = None
depends_on = None

_OLD = "method IN ('measured','handbook','datasheet','computed','estimated')"
_NEW = "method IN ('measured','handbook','datasheet','computed','estimated','digitized')"


def upgrade() -> None:
    # SQLite 는 CHECK 를 제자리에서 못 바꾼다 — batch 가 표를 다시 만든다.
    with op.batch_alter_table("property_value") as b:
        b.drop_constraint("ck_propval_method", type_="check")
        b.create_check_constraint("ck_propval_method", _NEW)


def downgrade() -> None:
    # 되돌리기 전에 digitized 를 measured 로 되돌린다 — 안 그러면 CHECK 에 걸려 실패한다.
    op.execute("update property_value set method='measured' where method='digitized'")
    with op.batch_alter_table("property_value") as b:
        b.drop_constraint("ck_propval_method", type_="check")
        b.create_check_constraint("ck_propval_method", _OLD)
