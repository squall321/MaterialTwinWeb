# 시험장비 API — "이 물성을 무엇으로 어떻게 재는가"에 답한다(장비·능력·측정공백).
from __future__ import annotations

from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import (Instrument, InstrumentCapability, PropertyDefinition,
                        PropertyValue, Source)

router = APIRouter(prefix="/api/metrology", tags=["metrology"])


def _cap_dict(c: InstrumentCapability) -> dict:
    return {
        "id": c.id,
        "property_key": c.property_key,
        "technique": c.technique,
        "standard": c.standard,
        "range_min": c.range_min,
        "range_max": c.range_max,
        "range_unit": c.range_unit,
        "resolution": c.resolution,
        "accuracy": c.accuracy,
        "temperature_min_k": c.temperature_min_k,
        "temperature_max_k": c.temperature_max_k,
        "specimen": c.specimen,
        "mapping_confidence": c.mapping_confidence,
        "source_detail": c.source_detail,
        "notes": c.notes,
    }


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    """장비 총계 + 분류 패싯 + 측정 가능 물성 수."""
    n_inst = db.execute(select(func.count(Instrument.id))).scalar_one()
    n_cap = db.execute(select(func.count(InstrumentCapability.id))).scalar_one()
    n_key = db.execute(
        select(func.count(func.distinct(InstrumentCapability.property_key)))
    ).scalar_one()
    n_def = db.execute(select(func.count(PropertyDefinition.id))).scalar_one()
    by_cat = dict(
        db.execute(
            select(Instrument.category, func.count(Instrument.id)).group_by(Instrument.category)
        ).all()
    )
    by_vendor = dict(
        db.execute(
            select(Instrument.vendor, func.count(Instrument.id))
            .group_by(Instrument.vendor)
            .order_by(func.count(Instrument.id).desc())
        ).all()
    )
    # ⚠ instruments 는 '카탈로그를 확보한 장비 수' 이지 보유 대수가 아니다. 이 구분이
    # MCP 도구에서는 01bcaa5 로 바로잡혔는데 REST/웹 UI 는 그대로여서, 같은 숫자가 화면에서
    # 여전히 '보유 역량' 으로 읽혔다. 이름과 보유 대수를 함께 내 오해를 없앤다.
    n_owned = db.scalar(
        select(func.count(Instrument.id)).where(Instrument.owned.is_(True))) or 0
    return {
        "instruments": n_inst,
        "catalog_instruments": n_inst,   # 이름으로 뜻을 분명히 한다
        "owned_instruments": n_owned,
        "ownership_note": ("장비 표는 카탈로그를 확보한 목록이지 보유 목록이 아니다. "
                           "사내 보유는 owned_instruments 만 센다."),
        "capabilities": n_cap,
        "measurable_properties": n_key,
        "total_properties": n_def,
        "by_category": by_cat,
        "by_vendor": by_vendor,
    }


@router.get("/instruments")
def instruments(
    category: str | None = Query(None),
    property_key: str | None = Query(None),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    """장비 목록. `property_key`를 주면 그 물성을 재는 장비만."""
    stmt = select(Instrument)
    if category:
        stmt = stmt.where(Instrument.category == category)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Instrument.vendor.ilike(like)) | (Instrument.model.ilike(like)))
    if property_key:
        stmt = stmt.where(
            Instrument.id.in_(
                select(InstrumentCapability.instrument_id).where(
                    InstrumentCapability.property_key == property_key
                )
            )
        )
    rows = db.execute(stmt.order_by(Instrument.vendor, Instrument.model)).scalars().all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": i.id,
                "vendor": i.vendor,
                "model": i.model,
                "category": i.category,
                "technique": i.technique,
                "description": i.description,
                "doc_path": i.doc_path,
                "notes": i.notes,
                "capabilities": [_cap_dict(c) for c in i.capabilities],
            }
            for i in rows
        ],
    }


@router.get("/by-property/{property_key:path}")
def by_property(property_key: str, db: Session = Depends(get_db)) -> dict:
    """한 물성을 재는 방법 — **기법으로 묶어서** 낸다.

    사용자의 질문은 "어느 장비가 있나"가 아니라 "어떻게 재나"다.
    같은 기법을 하는 장비 여럿은 선택지이지 서로 다른 답이 아니다.
    """
    d = db.execute(
        select(PropertyDefinition).where(PropertyDefinition.key == property_key)
    ).scalars().first()
    if d is None:
        raise HTTPException(404, f"미정의 물성 key: {property_key}")

    caps = db.execute(
        select(InstrumentCapability, Instrument)
        .join(Instrument, Instrument.id == InstrumentCapability.instrument_id)
        .where(InstrumentCapability.property_key == property_key)
        .order_by(Instrument.vendor, Instrument.model)
    ).all()

    groups: dict[str, list] = defaultdict(list)
    for c, i in caps:
        groups[c.technique].append(
            {**_cap_dict(c), "instrument": {
                "id": i.id, "vendor": i.vendor, "model": i.model,
                "category": i.category, "doc_path": i.doc_path}}
        )

    n_val = db.execute(
        select(func.count(PropertyValue.id)).where(PropertyValue.property_key == property_key)
    ).scalar_one()

    return {
        "property": {
            "key": d.key, "name": d.name, "domain": d.domain,
            "si_unit": d.si_unit, "test_standard": d.test_standard,
            "condition_axes": d.condition_axes,
        },
        "values_in_catalog": n_val,
        "techniques": [
            {
                "technique": t,
                # 규격은 능력행마다 다를 수 있어 **모아서** 낸다(하나로 뭉치면 거짓이 된다).
                "standards": sorted({x["standard"] for x in items if x["standard"]}),
                "instruments": items,
            }
            for t, items in sorted(groups.items())
        ],
    }


@router.get("/coverage")
def coverage(db: Session = Depends(get_db)) -> dict:
    """**잴 장비가 없는 물성**을 낸다 — 이 기능의 핵심 질문이다.

    카탈로그에 값이 있는데 측정 수단이 없는 물성은 '문헌에만 있는 물성'이다.
    값도 없고 장비도 없으면 그 칸은 지금 구조로는 못 채운다.
    """
    # 물성마다 **장비가 몇 대인가**까지 센다 — 화면 좌측 목록이 이 한 번의 호출로 완성된다.
    cap_n = dict(
        db.execute(
            select(InstrumentCapability.property_key,
                   func.count(func.distinct(InstrumentCapability.instrument_id)))
            .group_by(InstrumentCapability.property_key)
        ).all()
    )
    measurable = set(cap_n)
    val_count = dict(
        db.execute(
            select(PropertyValue.property_key, func.count(PropertyValue.id))
            .group_by(PropertyValue.property_key)
        ).all()
    )
    defs = db.execute(select(PropertyDefinition).order_by(
        PropertyDefinition.domain, PropertyDefinition.key)).scalars().all()

    by_domain: dict[str, dict] = defaultdict(lambda: {"total": 0, "measurable": 0})
    gaps, covered = [], []
    for d in defs:
        by_domain[d.domain]["total"] += 1
        if d.key in measurable:
            by_domain[d.domain]["measurable"] += 1
            covered.append({
                "key": d.key, "name": d.name, "domain": d.domain, "si_unit": d.si_unit,
                "instruments": cap_n[d.key], "values_in_catalog": val_count.get(d.key, 0),
            })
        else:
            gaps.append({
                "key": d.key, "name": d.name, "domain": d.domain,
                "si_unit": d.si_unit, "values_in_catalog": val_count.get(d.key, 0),
            })
    # 값이 많은데 장비가 없는 것부터 — **그게 가장 시급한 공백**이다.
    gaps.sort(key=lambda g: -g["values_in_catalog"])
    covered.sort(key=lambda g: -g["instruments"])
    return {
        "measurable": len(measurable),
        "total": len(defs),
        "by_domain": {k: v for k, v in sorted(by_domain.items())},
        "covered": covered,
        "gaps": gaps,
    }


@router.get("/catalogs")
def catalogs(db: Session = Depends(get_db)) -> dict:
    """편입된 카탈로그 PDF 목록(출처 기준). **파일은 재배포하지 않는다** — 경로만 낸다."""
    rows = db.execute(
        select(Source).where(Source.kind == "datasheet", Source.local_path.is_not(None))
        .order_by(Source.title)
    ).scalars().all()
    return {
        "count": len(rows),
        "items": [{"id": s.id, "title": s.title, "local_path": s.local_path} for s in rows],
    }
