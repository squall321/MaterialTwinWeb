# Alembic 마이그레이션 회귀 — upgrade/downgrade 왕복 + 모델-마이그레이션 드리프트 가드.
from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError

_BACKEND = Path(__file__).resolve().parent.parent


def _alembic_cfg(db_url: str) -> Config:
    cfg = Config(str(_BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND / "migrations"))
    # env.py가 settings.database_url을 읽으므로 그대로 두되, 명시 URL도 주입.
    cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


@pytest.fixture
def db_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'mig.db'}"
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", url)
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path))
    from app import config as config_mod

    config_mod.get_settings.cache_clear()
    yield url
    config_mod.get_settings.cache_clear()


def test_upgrade_creates_all_tables(db_url):
    import sqlite3

    cfg = _alembic_cfg(db_url)
    command.upgrade(cfg, "head")

    path = db_url.replace("sqlite:///", "")
    tables = {
        r[0]
        for r in sqlite3.connect(path).execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    expected = {
        "material",
        "specimen",
        "test",
        "raw_curve_ref",
        "processed_result",
        "constitutive_fit",
    }
    assert expected.issubset(tables), tables - expected


def test_upgrade_downgrade_roundtrip(db_url):
    cfg = _alembic_cfg(db_url)
    command.upgrade(cfg, "head")
    command.downgrade(cfg, "base")  # 예외 없이 역방향 완료.


def test_no_model_migration_drift(db_url):
    # 모델과 마이그레이션이 어긋나면(컬럼 추가 후 마이그레이션 누락 등) CommandError.
    cfg = _alembic_cfg(db_url)
    command.upgrade(cfg, "head")
    try:
        command.check(cfg)
    except CommandError as exc:
        pytest.fail(f"모델-마이그레이션 드리프트 감지: {exc}")
