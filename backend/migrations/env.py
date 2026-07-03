# Alembic 환경 — app.db.Base 메타데이터 + settings.database_url을 사용해 마이그레이션 실행.
from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 앱 설정·모델을 로드(메타데이터 autogenerate 대상).
from app.config import get_settings
from app.db import Base
from app import models  # noqa: F401  — 모든 테이블을 Base.metadata에 등록.

config = context.config

# 로깅 설정(alembic.ini). 없으면 스킵.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# DATABASE_URL은 앱 설정을 단일 진실원천으로 사용(alembic.ini 값 무시).
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인(URL만) 모드 — SQL 스크립트 생성용."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인(엔진 연결) 모드 — 실제 DB에 적용."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # SQLite는 ALTER 제약이 많아 batch 모드로 렌더(render_as_batch).
        is_sqlite = connection.dialect.name == "sqlite"
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=is_sqlite,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
