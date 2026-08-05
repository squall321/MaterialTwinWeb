# Alembic 마이그레이션 회귀 — upgrade/downgrade 왕복 + 모델-마이그레이션 드리프트 가드.
from __future__ import annotations

from pathlib import Path

import os
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


def test_migrated_db_accepts_relaxation_strain_source(db_url):
    # 마이그레이션 체인으로 만든 DB가 완화시험을 수용해야(f4c2a91d55e0 회귀).
    # c7b6cca38dc2가 CHECK를 안 고쳐 PG에서 CheckViolation이 났던 결함 —
    # alembic check는 CHECK 제약 드리프트를 감지하지 못하므로 INSERT로 직접 검증.
    import sqlite3

    cfg = _alembic_cfg(db_url)
    command.upgrade(cfg, "head")
    path = db_url.replace("sqlite:///", "")
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("INSERT INTO material (name, attributes, created_at, updated_at) "
                "VALUES ('m', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    con.execute("INSERT INTO specimen (material_id, label, geometry_type, gauge_length_m, "
                "width_m, thickness_m, area0_m2) VALUES (1,'S1','flat',0.05,0.0125,0.002,2.5e-5)")
    for src in ("extensometer", "crosshead", "relaxation"):
        con.execute("INSERT INTO test (specimen_id, test_type, strain_source, valid) "
                    "VALUES (1, 'relaxation', ?, 1)", (src,))
    con.commit()  # CheckViolation 없이 통과해야 함.

    # 체인 끝까지 AUTOINCREMENT 유지(f4c2a91d55e0의 batch 재생성이 지우면 안 됨).
    ddl = con.execute("SELECT sql FROM sqlite_master WHERE name='test'").fetchone()[0]
    assert "AUTOINCREMENT" in ddl


def _boot_init_db(db_url: str, data_dir: str) -> None:
    """깨끗한 서브프로세스에서 init_db 실행(모듈 리로드 오염 회피 — engine은 모듈 레벨)."""
    import os
    import subprocess
    import sys

    env = {**os.environ, "MATERIALTWIN_DATABASE_URL": db_url, "MATERIALTWIN_DATA_DIR": data_dir}
    subprocess.run([sys.executable, "-c", "from app.db import init_db; init_db()"],
                   env=env, check=True, cwd=str(_BACKEND))


def test_boot_migrates_old_versioned_db(db_url, tmp_path):
    # 부팅(init_db)이 구 버전 볼륨 DB를 head까지 마이그레이션해야 한다.
    # (배포 볼륨 스키마 드리프트 근절 — create_all은 기존 테이블을 ALTER 안 함.)
    import sqlite3

    command.upgrade(_alembic_cfg(db_url), "c7b6cca38dc2")  # relaxation CHECK 이전.
    path = db_url.replace("sqlite:///", "")
    old = sqlite3.connect(path).execute("SELECT sql FROM sqlite_master WHERE name='test'").fetchone()[0]
    assert "relaxation" not in old  # 구 스키마 확인.

    _boot_init_db(db_url, str(tmp_path))  # 부팅 → head까지 자동 마이그레이션.

    con = sqlite3.connect(path)
    test_sql = con.execute("SELECT sql FROM sqlite_master WHERE name='test'").fetchone()[0]
    spec_sql = con.execute("SELECT sql FROM sqlite_master WHERE name='specimen'").fetchone()[0]
    ver = con.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    assert "relaxation" in test_sql and "AUTOINCREMENT" in test_sql
    assert "uq_specimen_material_label" in spec_sql
    assert ver == "888056f1c5b8"  # head.


def test_boot_fresh_db_is_versioned_at_head(db_url, tmp_path):
    # 빈 DB 부팅 → 현재 스키마 + head로 스탬프(버전화 — 이후 마이그레이션 적용 가능).
    import sqlite3

    _boot_init_db(db_url, str(tmp_path))
    con = sqlite3.connect(db_url.replace("sqlite:///", ""))
    ver = con.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    sql = con.execute("SELECT sql FROM sqlite_master WHERE name='test'").fetchone()[0]
    assert ver == "888056f1c5b8" and "relaxation" in sql


def test_no_model_migration_drift(db_url):
    # 모델과 마이그레이션이 어긋나면(컬럼 추가 후 마이그레이션 누락 등) CommandError.
    cfg = _alembic_cfg(db_url)
    command.upgrade(cfg, "head")
    try:
        command.check(cfg)
    except CommandError as exc:
        pytest.fail(f"모델-마이그레이션 드리프트 감지: {exc}")


def test_mcp_stdio_entrypoint_migrates_schema(db_url, tmp_path, monkeypatch):
    """stdio MCP도 뜨기 전에 스키마를 맞춰야 한다.

    HTTP 앱만 init_db()를 부르고 mcp_server.py는 부르지 않아서, DATA_DIR 미설정 시 붙는
    개발 폴백 DB가 구 스키마에 멈춰 있었다. 그 상태로 list_materials를 부르면
    "no such table: property_definition"으로 죽는다.
    """
    import sqlite3

    command.upgrade(_alembic_cfg(db_url), "a72e1f3c8b90")   # property_definition 이전
    path = db_url.replace("sqlite:///", "")
    tables = {r[0] for r in sqlite3.connect(path).execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    assert "property_definition" not in tables, "구 스키마 전제가 깨졌다"

    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", db_url)
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path))
    import importlib

    import app.db as db_mod
    importlib.reload(db_mod)
    ran = []
    import mcp_server
    monkeypatch.setattr(mcp_server.mcp, "run", lambda *a, **k: ran.append(True))
    monkeypatch.setattr(mcp_server, "__name__", "__main__", raising=False)
    mcp_server.main()

    assert ran, "mcp.run이 호출되지 않았다"
    ver = sqlite3.connect(path).execute("SELECT version_num FROM alembic_version").fetchone()[0]
    assert ver == "888056f1c5b8", f"부팅이 스키마를 head로 올리지 않았다: {ver}"


def test_database_url_follows_data_dir(tmp_path, monkeypatch):
    """DATA_DIR만 지정해도 DB가 거기를 가리켜야 한다.

    예전엔 mcp_server가 DATA_DIR과 DATABASE_URL을 각각 backend/var/data로 고정 setdefault해서,
    DATA_DIR만 라이브로 준 경우 URL이 개발 경로로 먼저 박혀 DATA_DIR이 조용히 무시됐다.
    이 모듈을 import만 해도 그렇게 되므로, import하는 스크립트가 전부 개발 DB를 보게 된다 —
    실제로 수집 배치가 라이브 재료를 '재료 미지정'으로 오판했다.
    """
    import subprocess
    import sys as _sys
    from pathlib import Path as _P

    backend = _P(__file__).resolve().parents[1]
    env = {"PATH": os.environ.get("PATH", ""), "HOME": os.environ.get("HOME", ""),
           "MATERIALTWIN_DATA_DIR": str(tmp_path)}
    out = subprocess.run(
        [_sys.executable, "-c", "import mcp_server, os; print(os.environ['MATERIALTWIN_DATABASE_URL'])"],
        cwd=str(backend), env=env, capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, out.stderr[-800:]
    url = out.stdout.strip().splitlines()[-1]
    assert str(tmp_path) in url, f"DATA_DIR를 따르지 않는다: {url}"
