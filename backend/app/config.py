# 앱 전역 설정(pydantic-settings): DATABASE_URL, DATA_DIR, MAX_UPLOAD_MB 단일 소스.
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("materialtwin.config")

# DATA_DIR 미주입 시 폴백 기본값(개발 전용). 배포 시 절대경로 주입 필수(C7).
_DEV_FALLBACK_DATA_DIR = Path(__file__).resolve().parent.parent / "var" / "data"


class Settings(BaseSettings):
    """환경변수 MATERIALTWIN_* 로 주입되는 전역 설정."""

    model_config = SettingsConfigDict(
        env_prefix="MATERIALTWIN_",
        env_file=".env",
        extra="ignore",
    )

    # DATA_DIR 미설정 시 None으로 받아 폴백 여부를 검증 단계에서 판별(C7 경고용).
    data_dir: Path | None = Field(default=None)
    database_url: str | None = Field(default=None)
    max_upload_mb: int = Field(default=50)

    @model_validator(mode="after")
    def _resolve_paths(self) -> "Settings":
        # DATA_DIR 폴백 + 기동 시 WARNING(C7).
        if self.data_dir is None:
            logger.warning(
                "MATERIALTWIN_DATA_DIR 미설정 — 개발 전용 폴백 경로(%s) 사용. "
                "배포 시 절대경로 주입 필수.",
                _DEV_FALLBACK_DATA_DIR,
            )
            self.data_dir = _DEV_FALLBACK_DATA_DIR
        self.data_dir = self.data_dir.resolve()

        # DATABASE_URL 미설정 시 DATA_DIR 하위 SQLite 파일로 기본 구성.
        if self.database_url is None:
            db_path = self.data_dir / "materialtwin.db"
            self.database_url = f"sqlite:///{db_path}"
        return self

    @property
    def curves_dir(self) -> Path:
        return self.data_dir / "curves"

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
