# 얇은 create_app(): init_db→부팅 reaper(C4)→api_router include→MCP(/mcp)→StaticFiles 마운트.
from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import SessionLocal, init_db
from app.routers import api_router

# mcp_server.py는 backend 루트 모듈(app 패키지 밖) — cwd와 무관하게 import 경로 보장.
_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# 페더레이션(HTTP /mcp 마운트) 기본 정책: 파괴적 삭제 툴 비노출.
# 개인 stdio(python mcp_server.py)는 이 진입점을 거치지 않아 기본이 없어 전체 툴을 노출한다.
# HTTP에서도 삭제를 열려면 MATERIALTWIN_MCP_ALLOW_DELETE=1을 명시 주입한다.
# 반드시 mcp_server import 전에 설정해야 한다(임포트 시점에 삭제 툴 등록 여부가 결정됨).
os.environ.setdefault("MATERIALTWIN_MCP_ALLOW_DELETE", "0")

from mcp_server import mcp as materialtwin_mcp  # noqa: E402  (삭제 정책 env 설정 후 임포트)


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    # 마운트된 MCP 서브앱의 세션 매니저는 자동 기동되지 않으므로 직접 구동한다.
    async with materialtwin_mcp.session_manager.run():
        yield


def create_app() -> FastAPI:
    app = FastAPI(title="MaterialTwinWeb", version="0.1.0", lifespan=_lifespan)
    init_db()  # alembic 관리 스키마 + DATA_DIR/curves 보장.

    # 부팅 정합성: 고아 .tmp/미참조 Parquet 정리, 누락 파일 missing 마킹(C4).
    from app.curve_store import reaper

    with SessionLocal() as session:
        reaper(session)

    # 모든 /api/* 는 StaticFiles 마운트보다 먼저 등록.
    app.include_router(api_router)

    # MCP streamable HTTP — 웹과 동일 DB·계산 경로를 공유하는 도구(stdio와 동일 인스턴스).
    # session_manager는 인스턴스에 캐시되고 run()은 1회용이라, create_app 호출마다 리셋해
    # 이 앱 전용 매니저를 새로 만든다(테스트가 create_app을 반복 호출해도 lifespan이 안전).
    # HWAXMcpGateway가 HEAXHub 레지스트리(manifest mcp.expose)로 /apps/<slug>/mcp를 흡수한다.
    materialtwin_mcp._session_manager = None
    app.mount("/mcp", materialtwin_mcp.streamable_http_app(), name="mcp")

    # Starlette Mount는 슬래시 없는 정확일치("/mcp")를 매칭하지 않아 요청이 마지막
    # StaticFiles로 떨어져 405가 난다. 게이트웨이·클라이언트는 슬래시 없는 URL을 쓰므로
    # 앞단에서 "/mcp" → "/mcp/"로 정규화한다. (순수 ASGI — SSE 스트리밍 안전,
    # BaseHTTPMiddleware는 스트리밍을 버퍼링하므로 금지)
    class _McpBarePathFix:
        def __init__(self, app):  # add_middleware가 (next_app)으로 인스턴스화
            self._next = app

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                rp = scope.get("root_path", "")
                if scope.get("path") in ("/mcp", f"{rp}/mcp"):
                    scope = {**scope, "path": scope["path"] + "/"}
            await self._next(scope, receive, send)

    app.add_middleware(_McpBarePathFix)

    # 정적 프런트엔드는 항상 마지막에 "/"로 마운트(있을 때만).
    dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")
    return app


app = create_app()  # entrypoint 객체명/경로 불변(app.main:app).
