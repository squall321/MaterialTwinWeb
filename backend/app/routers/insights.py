# 인사이트 라우터 — 대시보드용 집계(overview·물성공간·통계·커버리지 갭·지식그래프).
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import insights
from app.db import get_db

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)) -> dict:
    """헤드라인 통계 — 총계·카테고리·재료 클래스·시험유형 분포."""
    return insights.overview(db)


@router.get("/property-space")
def get_property_space(db: Session = Depends(get_db)) -> dict:
    """Ashby 물성공간 산점 데이터(E–UTS, 밀도·클래스)."""
    return insights.property_space(db)


@router.get("/property-stats")
def get_property_stats(db: Session = Depends(get_db)) -> dict:
    """물성 분포 통계 — E·UTS·yield·연신율 범위·히스토그램."""
    return insights.property_stats(db)


@router.get("/coverage")
def get_coverage(db: Session = Depends(get_db)) -> dict:
    """커버리지 갭 + taxonomy 지식그래프(노드·엣지)."""
    return insights.coverage_gaps(db)
