# 시편 상세/수정/삭제 + 시편의 시험 목록 라우터.
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Specimen, Test
from app.schemas import SpecimenIn, SpecimenOut, TestOut
from app.units import area_from_geometry

router = APIRouter(prefix="/api", tags=["specimens"])


def _get_specimen(db: Session, sid: int) -> Specimen:
    spec = db.get(Specimen, sid)
    if spec is None:
        raise HTTPException(status_code=404, detail="specimen not found")
    return spec


@router.get("/specimens/{sid}", response_model=SpecimenOut)
def get_specimen(sid: int, db: Session = Depends(get_db)) -> SpecimenOut:
    return SpecimenOut.model_validate(_get_specimen(db, sid))


@router.patch("/specimens/{sid}", response_model=SpecimenOut)
def patch_specimen(
    sid: int, payload: SpecimenIn, db: Session = Depends(get_db)
) -> SpecimenOut:
    """시편 전체 갱신(SpecimenIn). area0 미입력 시 형상에서 재산출."""
    spec = _get_specimen(db, sid)
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
    spec.label = payload.label
    spec.geometry_type = payload.geometry_type
    spec.gauge_length_m = payload.gauge_length_m
    spec.width_m = payload.width_m
    spec.thickness_m = payload.thickness_m
    spec.diameter_m = payload.diameter_m
    spec.area0_m2 = area0
    spec.orientation = payload.orientation
    spec.standard = payload.standard
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"specimen constraint: {exc.orig}")
    db.refresh(spec)
    return SpecimenOut.model_validate(spec)


@router.delete("/specimens/{sid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_specimen(sid: int, db: Session = Depends(get_db)) -> None:
    spec = _get_specimen(db, sid)
    db.delete(spec)  # cascade: test→raw_curve_ref/processed_result.
    db.commit()


@router.get("/specimens/{sid}/tests", response_model=list[TestOut])
def list_tests(sid: int, db: Session = Depends(get_db)) -> list[TestOut]:
    _get_specimen(db, sid)
    rows = (
        db.execute(select(Test).where(Test.specimen_id == sid).order_by(Test.id))
        .scalars()
        .all()
    )
    return [TestOut.model_validate(r) for r in rows]
