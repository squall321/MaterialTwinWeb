# 외부 데이터 허브(AIDataHub) 동기화용 내보내기 — 재료 하나가 물성·조건·출처를 다 안고 나간다.
#
# 왜 별도 엔드포인트인가
#   `/api/materials`는 목록이라 attributes가 {"source":"mcp"} 한 줄뿐이고, 허브에는 재료 이름만
#   쌓이고 있었다(실측: records 523건, 물성값 0건). 재료별 상세를 544번 부르는 길도 있지만
#   허브의 max_rps=2.0이면 5분이 걸리고, 무엇보다 **허브가 받는 문서 하나가 그 재료의 완결된
#   물성 카드**여야 검색·에이전트가 쓸 수 있다.
#
# next_cursor를 우리가 내보내는 이유
#   허브 sync_svc._fetch_page는 응답에서 next_cursor / cursor / meta.next_offset 중 하나를
#   찾고, 없으면 한 페이지에서 종료한다. 그래서 매 실행 100건에서 멈춰 있었다.
#   허브는 여러 소스를 받는 공용 부품이니 우리가 규약에 맞춘다.
from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Material, PropertyDefinition, PropertyValue, Source

router = APIRouter(prefix="/api/export", tags=["hub-export"])

# 허브 문서 하나가 지나치게 커지지 않게 body 렌더는 잘라낸다. 구조 데이터(properties)는 안 자른다.
_BODY_MAX_CHARS = 60_000


def _fmt(v: float) -> str:
    """검색 가능한 형태로 — 지수표기가 필요하면 그대로 두되 0.35가 0.35로 보이게."""
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:g}"


def _cond_text(cond: Any) -> str:
    if not isinstance(cond, dict) or not cond:
        return ""
    parts = []
    for k, v in cond.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        parts.append(f"{k}={v}")
    return ", ".join(parts)


def _render_body(name: str, category: str | None, props: list[dict]) -> str:
    """허브의 전문검색 대상. 물성명·값·단위·조건·tier·출처를 한 줄씩 편다.

    구조(properties)만 보내면 허브가 JSON 내부를 어떻게 인덱싱하는지에 의존하게 된다.
    사람이 읽는 텍스트를 따로 실어 검색이 확실히 걸리게 한다.
    """
    lines = [f"{name}" + (f" [{category}]" if category else ""), ""]
    for p in props:
        val = _fmt(p["value"]) if p["value"] is not None else (p.get("value_text") or "-")
        seg = [f"{p['name']} ({p['key']}) = {val}"]
        if p.get("unit"):
            seg.append(p["unit"])
        row = " ".join(seg)
        extra = []
        if p.get("tier") is not None:
            extra.append(f"tier{p['tier']}")
        ct = _cond_text(p.get("conditions"))
        if ct:
            extra.append(f"조건: {ct}")
        if p.get("method"):
            extra.append(f"방법: {p['method']}")
        src = p.get("source") or {}
        if src.get("title"):
            extra.append(f"출처: {src['title']}")
        if extra:
            row += " · " + " · ".join(extra)
        lines.append(row)
        if p.get("notes"):
            lines.append(f"    비고: {p['notes']}")
    text = "\n".join(lines)
    if len(text) > _BODY_MAX_CHARS:
        text = text[:_BODY_MAX_CHARS] + "\n… (본문 절단 — 전체는 content.properties 참조)"
    return text


@router.get("/materials")
def export_materials(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    """재료 + 그 재료의 **모든** 물성값·조건·tier·출처.

    대표값 하나가 아니라 전량을 보낸다 — 한 재료가 같은 물성을 조건별로 여럿 갖고
    (Al6061-T6의 접촉각이 무처리 68.6도, 에탄올 세정 88.4도), 그 산포 자체가 정보다.
    """
    total = db.execute(select(func.count()).select_from(Material)).scalar_one()
    mats = (
        db.execute(
            select(Material).order_by(Material.id).offset((page - 1) * size).limit(size)
        )
        .scalars()
        .all()
    )
    ids = [m.id for m in mats]

    # 페이지 내 재료의 물성·정의·출처를 한 번에 — 재료마다 조회하면 N+1이다.
    pvs: dict[int, list[PropertyValue]] = {i: [] for i in ids}
    defs: dict[str, PropertyDefinition] = {}
    srcs: dict[int, Source] = {}
    if ids:
        rows = (
            db.execute(select(PropertyValue).where(PropertyValue.material_id.in_(ids)))
            .scalars()
            .all()
        )
        for pv in rows:
            pvs[pv.material_id].append(pv)
        keys = {pv.property_key for pv in rows}
        if keys:
            for d in (
                db.execute(select(PropertyDefinition).where(PropertyDefinition.key.in_(keys)))
                .scalars()
                .all()
            ):
                defs[d.key] = d
        sids = {pv.source_id for pv in rows if pv.source_id}
        if sids:
            for s in (
                db.execute(select(Source).where(Source.id.in_(sids))).scalars().all()
            ):
                srcs[s.id] = s

    items = []
    for m in mats:
        props = []
        used_sources: dict[int, dict] = {}
        for pv in sorted(pvs[m.id], key=lambda p: (p.property_key, p.id)):
            d = defs.get(pv.property_key)
            s = srcs.get(pv.source_id) if pv.source_id else None
            sd = None
            if s is not None:
                sd = {
                    "id": s.id, "title": s.title, "url": s.url, "doi": s.doi,
                    "kind": s.kind, "year": s.year, "authors": s.authors,
                    "publisher": s.publisher,
                }
                used_sources[s.id] = sd
            props.append({
                "key": pv.property_key,
                "name": d.name if d else pv.property_key,
                "domain": d.domain if d else None,
                "si_unit": d.si_unit if d else None,
                "value": pv.value_num,
                "value_text": pv.value_text,
                "unit": pv.unit,
                "uncertainty": pv.uncertainty,
                "tier": pv.quality_tier,
                "method": pv.method,
                # 조건은 반드시 함께 나간다 — 이 카탈로그의 원칙이 "조건 없는 값은 값이 아니다"다.
                "conditions": pv.conditions,
                "notes": pv.notes,
                "source": sd,
            })
        items.append({
            "id": m.id,
            "name": m.name,
            "material_code": m.material_code,
            "category": m.category,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            "n_properties": len(props),
            "n_sources": len(used_sources),
            "body": _render_body(m.name, m.category, props),
            "properties": props,
            "sources": list(used_sources.values()),
        })

    has_more = page * size < total
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        # 허브 규약 — 없으면 한 페이지에서 종료한다.
        "next_cursor": str(page + 1) if has_more else None,
    }
