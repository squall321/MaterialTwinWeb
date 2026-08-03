# 물성 카탈로그 API — 재료×화·물리 물성값 조회(패싯·프로비넌스·커버리지). 웹 카탈로그 UI 백엔드.
from __future__ import annotations

from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.catalog_compare import (build_comparison, numeric_property_options,
                                 representative_numeric, scatter_dataset)
from app.dyna_export import build_cards, match_rows
from app.db import get_db
from app.models import (Material, ProcessedResult, PropertyDefinition, PropertyValue,
                        Source, Specimen, Test)
from app import curve_store, curve_synth

router = APIRouter(prefix="/api/catalog", tags=["catalog"])

_META_KEYS = ("manufacturer", "grade", "trade_name", "material_class", "process",
              "subsystem", "standard", "composition")


def _meta(mat: Material) -> dict:
    a = mat.attributes or {}
    return {k: a.get(k) for k in _META_KEYS}


def _domains_for(db: Session) -> dict[str, str]:
    """property_key → domain 매핑."""
    return {k: d for k, d in db.execute(
        select(PropertyDefinition.key, PropertyDefinition.domain)).all()}


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict:
    """카탈로그 총계 + 패싯(서브시스템·카테고리·제조사·도메인 카운트)."""
    key_domain = _domains_for(db)
    n_val = db.execute(select(func.count(PropertyValue.id))).scalar_one()
    n_src = db.execute(select(func.count(Source.id))).scalar_one()
    n_def = db.execute(select(func.count(PropertyDefinition.id))).scalar_one()
    covered = db.execute(select(func.count(func.distinct(PropertyValue.material_id)))).scalar_one()

    mats = db.execute(select(Material)).scalars().all()
    n_mat = len(mats)
    # 재료별 물성 수·도메인.
    val_rows = db.execute(select(PropertyValue.material_id, PropertyValue.property_key)).all()
    per_mat_domains: dict[int, set] = defaultdict(set)
    for mid, pk in val_rows:
        per_mat_domains[mid].add(key_domain.get(pk))

    sub_c: Counter = Counter()
    cat_c: Counter = Counter()
    mfr_c: Counter = Counter()
    cls_c: Counter = Counter()
    for m in mats:
        a = m.attributes or {}
        sub_c[a.get("subsystem") or "기타"] += 1
        cat_c[m.category or "기타"] += 1
        if a.get("manufacturer"):
            mfr_c[a["manufacturer"]] += 1
        if a.get("material_class"):
            cls_c[a["material_class"]] += 1

    dom_val_c = Counter(key_domain.get(pk) for _, pk in val_rows)
    dom_mat_c: Counter = Counter()
    for doms in per_mat_domains.values():
        for d in doms:
            dom_mat_c[d] += 1

    def _facet(counter: Counter, limit: int | None = None):
        items = sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))
        if limit:
            items = items[:limit]
        return [{"value": k, "count": v} for k, v in items if k]

    return {
        "totals": {"materials": n_mat, "values": n_val, "sources": n_src,
                   "definitions": n_def, "covered": covered,
                   "domains": len([d for d in dom_val_c if d])},
        "facets": {
            "subsystem": _facet(sub_c),
            "category": _facet(cat_c),
            "manufacturer": _facet(mfr_c, limit=40),
            "material_class": _facet(cls_c, limit=40),
            "domain": [{"value": d, "count": dom_val_c[d], "materials": dom_mat_c[d]}
                       for d, _ in sorted(dom_val_c.items(), key=lambda kv: -kv[1]) if d],
        },
    }


@router.get("/materials")
def catalog_materials(
    q: str | None = Query(default=None),
    subsystem: str | None = Query(default=None),
    category: str | None = Query(default=None),
    manufacturer: str | None = Query(default=None),
    material_class: str | None = Query(default=None),
    domain: str | None = Query(default=None),
    prop: str | None = Query(default=None, description="물성 키로 거르기(예: structure.filler_content)"),
    prop_min: float | None = Query(default=None, description="prop의 대표값 하한(SI 단위)"),
    prop_max: float | None = Query(default=None, description="prop의 대표값 상한(SI 단위)"),
    sort: str = Query(default="properties"),  # properties | name | id | prop
    db: Session = Depends(get_db),
) -> dict:
    """재료 목록 + 메타데이터 + 물성 수·도메인. 패싯 필터·검색·정렬.

    prop/prop_min/prop_max로 **물성 값 범위** 검색을 지원한다. 이름 검색만으로는
    "GF 45% 사출재" 같은 질문에 답할 수 없다 — 함량은 이름이 아니라 물성에 들어 있다.
    """
    key_domain = _domains_for(db)
    # 재료별 물성 수·도메인 집계.
    val_rows = db.execute(select(PropertyValue.material_id, PropertyValue.property_key)).all()
    n_props: Counter = Counter()
    doms_by_mat: dict[int, set] = defaultdict(set)
    for mid, pk in val_rows:
        n_props[mid] += 1
        doms_by_mat[mid].add(key_domain.get(pk))

    stmt = select(Material)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Material.name.ilike(like), Material.material_code.ilike(like),
                             Material.description.ilike(like)))
    if category:
        stmt = stmt.where(Material.category == category)
    mats = db.execute(stmt).scalars().all()

    # 물성 값 범위 필터 — 대표값(신뢰등급 최상) 기준.
    prop_vals: dict[int, float] = {}
    if prop:
        if prop not in key_domain:
            raise HTTPException(status_code=400, detail=f"알 수 없는 물성 키: {prop}")
        prop_vals = representative_numeric(db, [prop]).get(prop, {})

    out = []
    for m in mats:
        if prop:
            pv = prop_vals.get(m.id)
            if pv is None:
                continue
            if prop_min is not None and pv < prop_min:
                continue
            if prop_max is not None and pv > prop_max:
                continue
        a = m.attributes or {}
        if subsystem and (a.get("subsystem") or "기타") != subsystem:
            continue
        if manufacturer and a.get("manufacturer") != manufacturer:
            continue
        if material_class and a.get("material_class") != material_class:
            continue
        mat_doms = sorted(d for d in doms_by_mat.get(m.id, set()) if d)
        if domain and domain not in mat_doms:
            continue
        row = {
            "id": m.id, "name": m.name, "material_code": m.material_code,
            "category": m.category, "n_properties": n_props.get(m.id, 0),
            "domains": mat_doms, **_meta(m),
        }
        if prop:
            row["prop_value"] = prop_vals.get(m.id)
        out.append(row)
    if sort == "name":
        out.sort(key=lambda x: (x["name"] or "").lower())
    elif sort == "id":
        out.sort(key=lambda x: x["id"])
    elif sort == "prop" and prop:
        out.sort(key=lambda x: (x.get("prop_value") is None, -(x.get("prop_value") or 0)))
    else:
        out.sort(key=lambda x: (-x["n_properties"], (x["name"] or "").lower()))
    return {"items": out, "total": len(out)}


@router.get("/definitions")
def definitions(db: Session = Depends(get_db)) -> dict:
    """물성 taxonomy — 도메인별 정의."""
    rows = db.execute(select(PropertyDefinition).order_by(
        PropertyDefinition.domain, PropertyDefinition.key)).scalars().all()
    by_domain: dict[str, list] = defaultdict(list)
    for d in rows:
        by_domain[d.domain].append({
            "key": d.key, "name": d.name, "symbol": d.symbol, "unit": d.si_unit,
            "value_type": d.value_type, "standard": d.test_standard,
            "conditions": d.condition_axes,
        })
    return {"domains": by_domain, "total": len(rows)}


@router.get("/materials/{mid}")
def catalog_material_detail(mid: int, db: Session = Depends(get_db)) -> dict:
    """재료 상세 — 메타데이터 + 도메인별 물성값(값·단위·조건·등급·프로비넌스)."""
    mat = db.get(Material, mid)
    if mat is None:
        raise HTTPException(status_code=404, detail="material not found")
    rows = (db.execute(
        select(PropertyValue, PropertyDefinition)
        .join(PropertyDefinition, PropertyDefinition.key == PropertyValue.property_key)
        .where(PropertyValue.material_id == mid)
        .order_by(PropertyDefinition.domain, PropertyDefinition.name, PropertyValue.quality_tier)
    ).all())
    domains: dict[str, list] = defaultdict(list)
    for pv, d in rows:
        src = pv.source
        domains[d.domain].append({
            "key": pv.property_key, "name": d.name, "symbol": d.symbol,
            "value": pv.value_num, "value_text": pv.value_text, "unit": pv.unit,
            "uncertainty": pv.uncertainty, "conditions": pv.conditions,
            "method": pv.method, "tier": pv.quality_tier, "standard": d.test_standard,
            "notes": pv.notes,
            "source": ({"title": src.title, "url": src.url, "doi": src.doi,
                        "manufacturer": src.publisher, "kind": src.kind,
                        "detail": pv.source_detail} if src else None),
        })
    return {
        "id": mat.id, "name": mat.name, "material_code": mat.material_code,
        "category": mat.category, "description": mat.description,
        "metadata": _meta(mat), "attributes": mat.attributes or {},
        "n_values": len(rows), "domains": domains,
    }


@router.get("/compare")
def compare(
    ids: str = Query(..., description="비교할 material_id CSV(2~12개)"),
    db: Session = Depends(get_db),
) -> dict:
    """재료 비교 — 물성별 대표값 정렬 매트릭스(도메인·조건·신뢰등급·출처). 웹/MCP 공용 코어."""
    try:
        mids = [int(x) for x in ids.split(",") if x.strip()][:12]
    except ValueError:
        raise HTTPException(status_code=400, detail="ids는 정수 CSV여야 합니다")
    if len(mids) < 2:
        raise HTTPException(status_code=400, detail="비교하려면 재료 2개 이상 필요")
    data = build_comparison(db, mids)
    if len(data["materials"]) < 2:
        raise HTTPException(status_code=404, detail="유효한 재료가 2개 미만입니다")
    return data


@router.get("/axes")
def axes(db: Session = Depends(get_db)) -> dict:
    """Ashby 축 후보 — 수치 물성 목록(재료 수 내림차순)."""
    return {"options": numeric_property_options(db)}


@router.get("/ashby")
def ashby(
    x: str = Query(default="physical.density"),
    y: str = Query(default="mechanical.youngs_modulus"),
    db: Session = Depends(get_db),
) -> dict:
    """Ashby 물성공간 산점도 — x·y 물성을 모두 가진 재료의 대표값 좌표 + 색상 facet."""
    data = scatter_dataset(db, x, y)
    if data is None:
        raise HTTPException(status_code=400, detail="알 수 없는 물성 key(x 또는 y)")
    return data


class DynaMatchIn(BaseModel):
    """붙여넣은 행 텍스트('101, SUS304' 여러 줄) + MID 시작번호."""
    rows: str
    mid_start: int = 1


@router.post("/dyna/match")
def dyna_match(body: DynaMatchIn, db: Session = Depends(get_db)) -> dict:
    """행 붙여넣기 → 행마다 후보 재료(매칭도·물성보유). 사용자가 고르는 프리뷰 단계."""
    if not (body.rows or "").strip():
        raise HTTPException(status_code=400, detail="rows가 비었습니다")
    return match_rows(db, [body.rows], mid_start=body.mid_start)


class DynaBuildIn(BaseModel):
    """확정된 (MID, material_id) 쌍으로 덱 생성."""
    picks: list[dict]            # [{"mid":101,"material_id":73}, ...]
    card: str = "mechanical"
    units: str = "ton_mm_s"


@router.post("/dyna/build")
def dyna_build(body: DynaBuildIn, db: Session = Depends(get_db)) -> dict:
    """사용자가 확인한 매칭으로 LS-DYNA 덱을 일괄 생성."""
    if body.card not in ("mechanical", "thermal", "both"):
        raise HTTPException(status_code=400, detail="card는 mechanical|thermal|both")
    items = []
    for p in body.picks:
        mid, mat = p.get("mid"), p.get("material_id")
        if mid is None or mat is None:
            continue
        # pids를 함께 넘겨야 CTE(*MAT_ADD_THERMAL_EXPANSION)가 생성된다.
        items.append({"mid": int(mid), "material": int(mat), "pids": p.get("pids") or []})
    if not items:
        raise HTTPException(status_code=400, detail="선택된 재료가 없습니다")
    return build_cards(db, items, card=body.card, units=body.units)


@router.get("/dyna")
def dyna_cards(
    materials: str = Query(..., description="재료 이름 또는 ID를 콤마로 구분(대량 가능)"),
    card: str = Query(default="mechanical", description="mechanical|thermal|both"),
    units: str = Query(default="ton_mm_s"),
    mid_start: int = Query(default=1),
    db: Session = Depends(get_db),
) -> dict:
    """재료 리스트 → LS-DYNA 재료카드 덱(MID 자동배정·출처 주석). 웹/MCP 공용 코어."""
    if card not in ("mechanical", "thermal", "both"):
        raise HTTPException(status_code=400, detail="card는 mechanical|thermal|both")
    toks = [t.strip() for t in materials.split(",") if t.strip()]
    if not toks:
        raise HTTPException(status_code=400, detail="materials가 비었습니다")
    return build_cards(db, toks, card=card, units=units, mid_start=mid_start)


@router.get("/coverage")
def coverage(db: Session = Depends(get_db)) -> dict:
    """커버리지 매트릭스 — 서브시스템 × 도메인 물성 수."""
    key_domain = _domains_for(db)
    mat_sub = {m.id: ((m.attributes or {}).get("subsystem") or "기타")
               for m in db.execute(select(Material)).scalars().all()}
    cell: dict[tuple, int] = Counter()
    for mid, pk in db.execute(select(PropertyValue.material_id, PropertyValue.property_key)).all():
        d = key_domain.get(pk)
        if d:
            cell[(mat_sub.get(mid, "기타"), d)] += 1
    subs = sorted({s for s, _ in cell})
    doms = sorted({d for _, d in cell})
    matrix = [{"subsystem": s, "cells": [{"domain": d, "count": cell.get((s, d), 0)} for d in doms]}
              for s in subs]
    return {"subsystems": subs, "domains": doms, "matrix": matrix}


@router.get("/materials/{mid}/curve")
def material_curve(mid: int, n_points: int = Query(default=80, ge=20, le=400),
                   db: Session = Depends(get_db)) -> dict:
    """재료의 σ-ε 곡선. 인장시험이 있으면 실측을, 없으면 스칼라에서 합성한 곡선을 준다.

    동박·솔더처럼 시험은 없지만 스칼라 물성은 갖춘 재료가 대부분이라, 합성이라도 보여줘야
    한다. 실측/합성은 kind로 구분하고, 합성이면 입력 스칼라의 출처를 함께 반환한다.
    """
    mat = db.get(Material, mid)
    if mat is None:
        raise HTTPException(status_code=404, detail="material not found")

    # 실측 곡선이 있으면 그쪽이 우선.
    tid = db.execute(
        select(Test.id).join(Specimen, Specimen.id == Test.specimen_id)
        .where(Specimen.material_id == mid, Test.valid.is_(True),
               Test.test_type == "tensile").order_by(Test.id)
    ).scalars().first()
    if tid is not None:
        pr = db.execute(select(ProcessedResult).where(ProcessedResult.test_id == tid)).scalars().first()
        if pr is not None:
            df = curve_store.read_curve(tid)
            xcol = next((c for c in ("eng_strain", "strain_nominal", "extenso_strain", "strain") if c in df.columns), None)
            ycol = next((c for c in ("eng_stress_Pa", "stress_nominal_pa", "stress_pa") if c in df.columns), None)
            if xcol and ycol and len(df) > 2:
                xs, ys = curve_store.lttb_downsample(df[xcol].to_numpy(), df[ycol].to_numpy(), n_out=n_points)
                xs, ys = [float(v) for v in xs], [float(v) for v in ys]
                return {"material_id": mid, "name": mat.name, "kind": curve_synth.KIND_MEASURED,
                        "test_id": tid, "strain": xs, "stress_pa": ys,
                        "model": "measured tensile test", "note": None, "sources": None}

    out = curve_synth.synth_for_material(db, mid, n_points=n_points)
    if out is None:
        raise HTTPException(status_code=404,
                            detail="곡선을 만들 스칼라 물성이 부족합니다(영률 필수, 항복 또는 인장강도 필요)")
    return {"material_id": mid, "name": mat.name, "kind": out["kind"],
            "test_id": None,
            "strain": [float(v) for v in out["strain"]],
            "stress_pa": [float(v) for v in out["stress_pa"]],
            "model": out["model"], "note": out.get("note"),
            "inconsistent": out.get("inconsistent", False),
            "inputs": out.get("inputs"), "sources": out.get("sources"),
            "provenance": out.get("provenance")}
