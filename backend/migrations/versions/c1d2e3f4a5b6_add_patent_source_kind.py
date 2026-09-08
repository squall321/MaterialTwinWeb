# ck_source_kind 에 'patent' 추가 — 특허가 'other' 로 뭉개져 근거로 안 보이던 것을 고친다.
"""add patent to source kind vocabulary

Revision ID: c1d2e3f4a5b6
Revises: b3c4d5e6f7a8
Create Date: 2026-09-08

배경: 67차가 오버코트의 정체·실링재의 계열·적층 순서를 **특허로만** 확정했다.
그런데 어휘에 'patent' 가 없어 로더(KIND_MAP)가 'other' 로 매핑했고, 제목으로
특허를 골라 보니 19건이 other 12 / datasheet 5 / web 1 / database 1 로 흩어져
있었다. 같은 문서 갈래가 배치마다 다른 칸에 들어가면 **kind 로 근거를 뽑을 수
없다.** 특허는 벤더 시트도 논문도 아니다 — 심사를 거치지만 값을 재려고 쓴 글이
아니고, 조성·구조를 청구범위로 인쇄한다. 별도 어휘가 맞다.

주의: source 는 UNIQUE(content_hash)·UNIQUE(doi) 를 갖는다. SQLite 는 CHECK 를
제자리에서 못 바꿔 테이블을 재생성하므로 batch_alter_table 에 그 둘을 다시 준다
— 리플렉션이 그 둘을 그대로 옮기므로 table_args 로 다시 주면 중복 선언이 된다.
"""
from typing import Sequence, Union

from alembic import op

import app.db  # noqa: F401 - UTCDateTime 타입 로딩.

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW = ("kind IN ('journal','book','database','datasheet','computed',"
        "'standard','web','patent','other')")
_OLD = ("kind IN ('journal','book','database','datasheet','computed',"
        "'standard','web','other')")


def _swap(new: str, old: str) -> None:
    if op.get_bind().dialect.name == "sqlite":
        # table_args 로 UNIQUE 를 다시 주지 마라 — 리플렉션이 이미 잡아 오므로
        # `UNIQUE (doi)` 가 두 번 찍힌다(리허설에서 확인). 재생성만 맡긴다.
        with op.batch_alter_table("source") as b:
            b.drop_constraint("ck_source_kind", type_="check")
            b.create_check_constraint("ck_source_kind", new)
    else:
        op.drop_constraint("ck_source_kind", "source", type_="check")
        op.create_check_constraint("ck_source_kind", "source", new)


def upgrade() -> None:
    _swap(_NEW, _OLD)


def downgrade() -> None:
    # 되돌리기 전에 'patent' 를 'other' 로 되돌려야 새 CHECK 가 통과한다.
    op.execute("UPDATE source SET kind='other' WHERE kind='patent'")
    _swap(_OLD, _NEW)
