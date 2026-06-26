# 얇은 create_app(): init_db→부팅 reaper(C4)→api_router include→StaticFiles 마운트만.
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import SessionLocal, init_db
from app.routers import api_router


def create_app() -> FastAPI:
    app = FastAPI(title="MaterialTwinWeb", version="0.1.0")
    init_db()  # create_all + DATA_DIR/curves 보장.

    # 부팅 정합성: 고아 .tmp/미참조 Parquet 정리, 누락 파일 missing 마킹(C4).
    from app.curve_store import reaper

    with SessionLocal() as session:
        reaper(session)

    # 모든 /api/* 는 StaticFiles 마운트보다 먼저 등록.
    app.include_router(api_router)

    # 정적 프런트엔드는 항상 마지막에 "/"로 마운트(있을 때만).
    dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")
    return app


app = create_app()  # entrypoint 객체명/경로 불변(app.main:app).
