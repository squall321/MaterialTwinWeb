"""AE44 마그네슘 합금의 category 와 Lazar PET 기재의 두께 주석을 바로잡는다.

45차 GD·GB 가 각각 보고만 하고 안 고친 둘이다. **마이그레이션으로 내는 이유가 있다** —
병합기(`_materialtwin_merge.py`)는 `CURATION_KEYS`(role·subsystem 계열)만 기존 재료에
반영한다. `category` 와 `attributes.note` 는 그 목록에 없어 dev 에서 고쳐도 cae00 에 안 간다.

① **AE44 4종이 `composite` 다.** Mg-4Al-4RE 다이캐스팅 합금이라 `metal` 이 맞다.
   형제가 반례다 — 34 AZ91D · 2557 AM60B · 2558 AM50A 가 전부 `metal` 이고 AE44 만 혼자 다르다.
   `category` 는 화면 필터와 Ashby 축을 가르는 값이라 틀리면 금속 격자에서 통째로 빠진다.

② **`Bare PET film (Lazar 2019 …)` 의 주석이 "두께가 논문에 인쇄되지 않았다" 인데 인쇄돼 있다.**
   45차 GB 가 원문을 열어 verbatim 을 냈다 — *"the 175 µm thick PET substrate was corona treated"*.
   두께 미인쇄는 이 갈래에서 **값을 버리는 사유**로 쓰이므로(§328·373) 틀린 주석이 다음 파동을
   막는다. 주석만 고치고 값은 넣지 않는다 — 두께를 조건에 박는 것은 채굴 배치 몫이다.

**id 가 아니라 `name` 으로 찾는다.** 병합이 id 를 다시 매기므로 운영 DB 에서는 번호가 다르다.
`name` 은 병합기의 재료 자연키이고 실측 유일성 2,645/2,645 다.

Revision ID: d1e2f3a4b5c6
Revises: c0d1e2f3a4b5
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "d1e2f3a4b5c6"
down_revision = "c0d1e2f3a4b5"
branch_labels = None
depends_on = None

_AE44_LIKE = "Die-cast AE44 magnesium alloy%"
_PET_LIKE = "Bare PET film (Lazar 2019%"
_NOTE_OLD = "LbL 코팅 전 기재 PET — 두께가 논문에 인쇄되지 않았다"
_NOTE_NEW = ("LbL 코팅 전 기재 PET — 논문 실험절이 두께를 인쇄한다"
             "(verbatim: \"the 175 µm thick PET substrate was corona treated\").")


def _set_note(conn, new: str, old: str) -> None:
    rows = conn.execute(sa.text(
        "select id, attributes from material where name like :p"), {"p": _PET_LIKE}).fetchall()
    for mid, attrs in rows:
        try:
            a = json.loads(attrs) if attrs else {}
        except (TypeError, ValueError):
            continue
        if not isinstance(a, dict) or a.get("note") != old:
            continue                                   # 이미 고쳤거나 다른 주석이면 두 번 안 만진다
        a["note"] = new
        conn.execute(sa.text("update material set attributes=:a where id=:i"),
                     {"a": json.dumps(a, ensure_ascii=False), "i": mid})


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "update material set category='metal' where name like :p and category<>'metal'"),
        {"p": _AE44_LIKE})
    _set_note(conn, _NOTE_NEW, _NOTE_OLD)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "update material set category='composite' where name like :p and category='metal'"),
        {"p": _AE44_LIKE})
    _set_note(conn, _NOTE_OLD, _NOTE_NEW)
