# 획득 저장 계층 — source dedup + property_value 멱등 upsert(값마다 프로비넌스 필수).
from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PropertyDefinition, PropertyValue, Source


def upsert_source(
    session: Session,
    *,
    kind: str,
    title: str | None = None,
    url: str | None = None,
    doi: str | None = None,
    isbn: str | None = None,
    authors: str | None = None,
    year: int | None = None,
    publisher: str | None = None,
    license: str | None = None,
    local_path: str | None = None,
    content_hash: str | None = None,
) -> Source:
    """출처를 dedup 후 반환. 우선순위 doi > content_hash > url."""
    found = None
    if doi:
        found = session.execute(select(Source).where(Source.doi == doi)).scalar_one_or_none()
    if found is None and content_hash:
        found = session.execute(
            select(Source).where(Source.content_hash == content_hash)
        ).scalar_one_or_none()
    if found is None and url and not doi:
        found = session.execute(select(Source).where(Source.url == url)).scalar_one_or_none()
    if found is not None:
        return found

    src = Source(
        kind=kind, title=title, url=url, doi=doi, isbn=isbn, authors=authors, year=year,
        publisher=publisher, license=license, local_path=local_path, content_hash=content_hash,
        retrieved_at=datetime.now(timezone.utc),
    )
    session.add(src)
    session.flush()
    return src


def _cond_key(conditions: dict | None) -> str:
    return json.dumps(conditions or {}, sort_keys=True, ensure_ascii=False)


def upsert_property_value(
    session: Session,
    *,
    material_id: int,
    property_key: str,
    value_num: float | None = None,
    value_text: str | None = None,
    unit: str | None = None,
    uncertainty: float | None = None,
    conditions: dict | None = None,
    method: str = "measured",
    quality_tier: int = 3,
    source: Source | None = None,
    source_detail: str | None = None,
    notes: str | None = None,
) -> tuple[PropertyValue, bool]:
    """물성값을 멱등 적재. 같은 (material, key, source, conditions)면 갱신, 아니면 삽입.

    반환: (row, created). property_key는 property_definition에 존재해야 함(FK RESTRICT).
    """
    known = session.execute(
        select(PropertyDefinition.key).where(PropertyDefinition.key == property_key)
    ).scalar_one_or_none()
    if known is None:
        raise ValueError(f"미정의 물성 key: {property_key} (property_definition에 먼저 등록 필요)")

    src_id = source.id if source is not None else None
    ck = _cond_key(conditions)
    rows = session.execute(
        select(PropertyValue).where(
            PropertyValue.material_id == material_id,
            PropertyValue.property_key == property_key,
            PropertyValue.source_id.is_(src_id) if src_id is None else PropertyValue.source_id == src_id,
        )
    ).scalars().all()
    for pv in rows:
        if _cond_key(pv.conditions) == ck:
            pv.value_num = value_num
            pv.value_text = value_text
            pv.unit = unit
            pv.uncertainty = uncertainty
            pv.method = method
            pv.quality_tier = quality_tier
            pv.source_detail = source_detail
            pv.notes = notes
            return pv, False

    pv = PropertyValue(
        material_id=material_id, property_key=property_key, value_num=value_num,
        value_text=value_text, unit=unit, uncertainty=uncertainty, conditions=conditions,
        method=method, quality_tier=quality_tier, source_id=src_id,
        source_detail=source_detail, notes=notes,
    )
    session.add(pv)
    session.flush()
    return pv, True
