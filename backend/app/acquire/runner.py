# 획득 러너 — 커넥터 결과를 source+property_value로 프로비넌스 부착해 적재.
from __future__ import annotations

from sqlalchemy.orm import Session

from app.acquire import wikidata as _wd
from app.acquire.store import upsert_property_value, upsert_source


def acquire_from_wikidata(session: Session, *, material_id: int, search_term: str) -> dict:
    """search_term을 Wikidata 항목으로 해석해 매핑 물성을 적재. 요약 dict 반환.

    출처는 Wikidata 항목 URL(kind=database, CC0), 값은 handbook/tier2로 기록한다.
    """
    ent = _wd.resolve_entity(search_term)
    if not ent:
        return {"material_id": material_id, "resolved": None, "written": 0}
    vals = _wd.fetch_properties(ent["qid"])
    if not vals:
        return {"material_id": material_id, "resolved": ent, "written": 0}

    url = f"https://www.wikidata.org/wiki/{ent['qid']}"
    src = upsert_source(session, kind="database", title=f"Wikidata: {ent['label']}",
                        url=url, publisher="Wikidata", license="CC0")
    written = 0
    for v in vals:
        upsert_property_value(
            session, material_id=material_id, property_key=v["key"],
            value_num=v["value"], unit=v["unit"], conditions=v.get("conditions"),
            method="handbook", quality_tier=2, source=src, source_detail=v.get("wd_pid"),
            notes=f"Wikidata {ent['label']} ({ent['qid']}) — 대표(base) 물성",
        )
        written += 1
    session.commit()
    return {"material_id": material_id, "resolved": ent, "written": written,
            "keys": sorted({v["key"] for v in vals})}
