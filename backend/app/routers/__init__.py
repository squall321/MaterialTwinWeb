# 모든 /api/* 라우터를 묶는 최상위 APIRouter(하위 라우터 include).
from __future__ import annotations

from fastapi import APIRouter

from app.routers import (
    catalog,
    health,
    hub_export,
    insights,
    materials,
    metrology,
    properties,
    specimens,
    uploads,
)

api_router = APIRouter(prefix="")
api_router.include_router(health.router)
api_router.include_router(materials.router)
api_router.include_router(specimens.router)
api_router.include_router(uploads.router)
api_router.include_router(properties.router)
api_router.include_router(insights.router)
api_router.include_router(catalog.router)
api_router.include_router(metrology.router)
api_router.include_router(hub_export.router)
