# SQLAlchemy 엔진/세션/Base + SQLite PRAGMA(FK ON/WAL/busy_timeout) 리스너와 init_db.
from __future__ import annotations

from collections.abc import Generator
from datetime import timezone

from sqlalchemy import DateTime, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.types import TypeDecorator

from app.config import get_settings

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


def init_db() -> None:
    """테이블 생성 + DATA_DIR/curves 디렉터리 보장."""
    # 모델 등록을 위해 import(순환 회피용 지연 import).
    from app import models  # noqa: F401

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.curves_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
