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
    # 빈 문자열은 값이 아니라 "없음"이다. 그대로 두면 doi=''가 저장되고, DOI UNIQUE 제약이
    # 걸려 **두 번째 무DOI 출처부터 인제스트가 통째로 죽는다**(실제로 76행짜리 배치가 중간에
    # 끊겼다). 파이썬에선 ''가 falsy라 dedup 조회도 건너뛰어 아무도 못 잡는다.
    doi = (doi or "").strip() or None
    isbn = (isbn or "").strip() or None
    url = (url or "").strip() or None
    content_hash = (content_hash or "").strip() or None
    found = None
    if doi:
        found = session.execute(select(Source).where(Source.doi == doi)).scalar_one_or_none()
    if found is None and content_hash:
        found = session.execute(
            select(Source).where(Source.content_hash == content_hash)
        ).scalar_one_or_none()
    if found is None and url and not doi:
        found = session.execute(select(Source).where(Source.url == url)).scalar_one_or_none()
    # **식별자가 하나도 없으면 제목으로라도 dedup 한다.**
    # 23차에 DOI·URL 없는 논문 한 편이 **출처 295개**를 만들었다(값 하나에 하나씩).
    # 제목은 약한 키라 동명이인 논문을 합칠 위험이 있지만(브리프 22번),
    # 식별자가 아예 없는 경우에만 쓰므로 그 위험보다 중복 폭발이 훨씬 크다.
    # kind 까지 같아야 합친다 — 같은 제목의 논문과 데이터시트는 다른 것이다.
    if found is None and title and not (doi or url or isbn or content_hash):
        found = session.execute(
            select(Source).where(
                Source.title == title, Source.kind == kind,
                Source.doi.is_(None), Source.url.is_(None),
                Source.isbn.is_(None), Source.content_hash.is_(None),
            )
        ).scalars().first()
    if found is not None:
        # **찾은 출처의 빈 칸은 채운다**(37차 AS). 브리프 407번이 배치에게
        # `authors`·`year`·`local_path` 를 의무로 지웠는데, 그 셋은 **출처가 새로 만들어질 때만**
        # 저장되고 있었다 — 같은 URL 의 출처가 이미 있으면 인자가 통째로 버려진다.
        # 앞 파동이 URL 만 넣고 만든 출처는 다음 파동이 경로를 넘겨도 영영 NULL 로 남는다
        # (지금 local_path 가 2,671/2,675 NULL 인 이유의 일부다).
        # **비어 있는 칸만 채우고 이미 값이 있는 칸은 절대 덮지 않는다** — 덮으면 앞 파동의
        # 확인된 서지가 뒤 파동의 오타로 바뀐다.
        for _f, _v in (("title", title), ("authors", authors), ("year", year),
                       ("publisher", publisher), ("license", license),
                       ("local_path", local_path), ("content_hash", content_hash),
                       ("doi", doi), ("url", url), ("isbn", isbn)):
            if _v and getattr(found, _f, None) is None:
                setattr(found, _f, _v)
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
