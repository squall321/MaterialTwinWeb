# 공용 fixture — tmp 격리 env 주입 + 모듈 재로딩(mcp_server 직접 호출 테스트용).
from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def mcp_env(tmp_path, monkeypatch):
    """DATA_DIR/DATABASE_URL을 tmp로 격리하고 mcp_server까지 재로딩해 반환한다.

    mcp_server는 임포트 시점에 SessionLocal 등을 이름 바인딩하므로,
    env 주입 → settings 캐시 클리어 → app.db/models/curve_store 재로딩 →
    mcp_server 재로딩 순서를 지켜야 격리 DB를 본다(테스트 정찰 노트).
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{db_file}")

    from app import config as config_mod

    config_mod.get_settings.cache_clear()

    import app.db as db_mod
    import app.models as models_mod
    import app.curve_store as curve_mod
    import app.ingest as ingest_mod
    import app.insights as insights_mod
    import app.routers.properties as r_properties

    importlib.reload(db_mod)
    importlib.reload(models_mod)
    importlib.reload(curve_mod)
    importlib.reload(ingest_mod)
    importlib.reload(insights_mod)  # 모델 클래스 재바인딩(taxonomy 리소스가 사용).
    importlib.reload(r_properties)

    import mcp_server as mcp_mod

    importlib.reload(mcp_mod)
    db_mod.init_db()

    mcp_mod._test_db = db_mod  # 검증용 핸들(SessionLocal 재조회).
    mcp_mod._test_curve_store = curve_mod
    yield mcp_mod

    config_mod.get_settings.cache_clear()
