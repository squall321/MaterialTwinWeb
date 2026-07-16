# SQLAlchemy 엔진/세션/Base + SQLite PRAGMA(FK ON/WAL/busy_timeout) 리스너와 init_db.
from __future__ import annotations

import logging
from collections.abc import Generator
from datetime import timezone
from pathlib import Path

from sqlalchemy import DateTime, create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.config import get_settings

logger = logging.getLogger("materialtwin.db")

settings = get_settings()

_is_sqlite = settings.database_url.startswith("sqlite")

# SQLite는 스레드 간 커넥션 공유 허용(FastAPI 의존성 패턴) 위해 check_same_thread=False.
_connect_args = {"timeout": 5} if _is_sqlite else {}
if _is_sqlite:
    _connect_args["check_same_thread"] = False

engine: Engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)


class UTCDateTime(TypeDecorator):
    """tz-aware UTC 강제 타입. 쓰기 시 UTC 변환, 읽기 시 UTC tzinfo 부착.

    SQLite는 tzinfo를 보존하지 못해 naive로 돌아오므로 읽기에서 UTC로 표지한다.
    Postgres는 native timestamptz라 그대로 통과한다.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class Base(DeclarativeBase):
    """모든 ORM 모델의 선언적 베이스."""


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, _connection_record) -> None:
    # SQLite 연결마다 PRAGMA 강제(C2). Postgres 등은 스킵.
    if not _is_sqlite:
        return
    cursor = dbapi_conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
    finally:
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성: 요청 단위 세션 제공."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _alembic_config():
    """backend/alembic.ini 기반 Config. script_location=%(here)s/migrations 자동 해석."""
    from alembic.config import Config

    ini = Path(__file__).resolve().parent.parent / "alembic.ini"
    cfg = Config(str(ini))
    cfg.set_main_option("sqlalchemy.url", settings.database_url)
    cfg.attributes["configure_logger"] = False  # 앱 로깅 유지.
    return cfg


def _apply_schema() -> None:
    """스키마를 alembic로 관리해 볼륨 지속 시 스키마 드리프트를 없앤다.

    - 빈 DB: create_all + stamp head(현재 모델로 생성 후 버전 고정 — 빠르고 정확).
    - 버전 DB: upgrade head(누적 마이그레이션 적용 — 구 배포 볼륨을 최신화).
    - 레거시(테이블 有·버전 無): create_all(누락 보완) + stamp head + 경고.
    create_all이 기존 테이블을 ALTER하지 않아 발생하던 배포 볼륨 스키마 드리프트 해소.
    """
    from alembic import command

    insp = inspect(engine)
    tables = set(insp.get_table_names())
    cfg = _alembic_config()

    if "alembic_version" in tables:
        command.upgrade(cfg, "head")
    elif "material" not in tables:
        Base.metadata.create_all(bind=engine)
        command.stamp(cfg, "head")
    else:
        logger.warning(
            "create_all 출신 DB(버전 없음) 감지 — head로 stamp(스키마가 head와 일치 가정). "
            "구 스키마라면 재생성 필요."
        )
        Base.metadata.create_all(bind=engine)
        command.stamp(cfg, "head")


def init_db() -> None:
    """스키마 적용(alembic 관리) + DATA_DIR/curves 디렉터리 보장."""
    # 모델 등록을 위해 import(순환 회피용 지연 import).
    from app import models  # noqa: F401

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.curves_dir.mkdir(parents=True, exist_ok=True)
    _apply_schema()
