# 재료 CRUD + 시편 목록/생성 라우터(목록은 q·page·size, JSON 컬럼 검색 금지).
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Material, Specimen
from app.schemas import (
    MaterialIn,
    MaterialOut,
    MaterialPatch,
    SpecimenIn,
    SpecimenOut,
)
from app.units import area_from_geometry

router = APIRouter(prefix="/api", tags=["materials"])


def _get_material(db: Session, mid: int) -> Material:
    mat = db.get(Material, mid)
    if mat is None:
        raise HTTPException(status_code=404, detail="material not found")
    return mat


@router.get("/materials")
def list_materials(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    """재료 목록. q는 name/material_code(인덱스 컬럼)만 LIKE 검색(JSON 검색 금지)."""
    stmt = select(Material)
    count_stmt = select(func.count()).select_from(Material)
    if q:
        like = f"%{q}%"
        cond = or_(Material.name.ilike(like), Material.material_code.ilike(like))
        stmt = stmt.where(cond)
        count_stmt = count_stmt.where(cond)
    total = db.execute(count_stmt).scalar_one()
    rows = (
        db.execute(
            stmt.order_by(Material.id.desc()).offset((page - 1) * size).limit(size)
        )
        .scalars()
        .all()
    )
    return {
        "items": [MaterialOut.model_validate(r) for r in rows],
        "total": total,
        "page": page,
        "size": size,
    }


@router.post("/materials", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
def create_material(payload: MaterialIn, db: Session = Depends(get_db)) -> MaterialOut:
    mat = Material(
        name=payload.name,
        material_code=payload.material_code,
        category=payload.category,
        description=payload.description,
        attributes=payload.attributes,
    )
    db.add(mat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="material_code already exists")
    db.refresh(mat)
    return MaterialOut.model_validate(mat)


@router.get("/materials/{mid}", response_model=MaterialOut)
def get_material(mid: int, db: Session = Depends(get_db)) -> MaterialOut:
    return MaterialOut.model_validate(_get_material(db, mid))


@router.patch("/materials/{mid}", response_model=MaterialOut)
def patch_material(
    mid: int, payload: MaterialPatch, db: Session = Depends(get_db)
) -> MaterialOut:
    mat = _get_material(db, mid)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(mat, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="material_code already exists")
    db.refresh(mat)
    return MaterialOut.model_validate(mat)


@router.delete("/materials/{mid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(mid: int, db: Session = Depends(get_db)) -> None:
    mat = _get_material(db, mid)
    db.delete(mat)  # cascade: specimen→test→raw_curve_ref/processed_result.
    db.commit()


@router.get("/materials/{mid}/specimens", response_model=list[SpecimenOut])
def list_specimens(mid: int, db: Session = Depends(get_db)) -> list[SpecimenOut]:
    _get_material(db, mid)
    rows = (
        db.execute(
            select(Specimen).where(Specimen.material_id == mid).order_by(Specimen.id)
        )
        .scalars()
        .all()
    )
    return [SpecimenOut.model_validate(r) for r in rows]


@router.post(
    "/materials/{mid}/specimens",
    response_model=SpecimenOut,
    status_code=status.HTTP_201_CREATED,
)
def create_specimen(
    mid: int, payload: SpecimenIn, db: Session = Depends(get_db)
) -> SpecimenOut:
    """시편 생성. area0_m2 미입력 시 형상에서 산출(units.area_from_geometry)."""
    _get_material(db, mid)
    area0 = payload.area0_m2
    if area0 is None:
        try:
            area0 = area_from_geometry(
                payload.geometry_type,
                width_m=payload.width_m,
                thickness_m=payload.thickness_m,
                diameter_m=payload.diameter_m,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
    spec = Specimen(
        material_id=mid,
        label=payload.label,
        geometry_type=payload.geometry_type,
        gauge_length_m=payload.gauge_length_m,
        width_m=payload.width_m,
        thickness_m=payload.thickness_m,
        diameter_m=payload.diameter_m,
        area0_m2=area0,
        orientation=payload.orientation,
        standard=payload.standard,
    )
    db.add(spec)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"specimen constraint: {exc.orig}")
    db.refresh(spec)
    return SpecimenOut.model_validate(spec)
