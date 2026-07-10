# 앱 전역 설정(pydantic-settings): DATABASE_URL, DATA_DIR, MAX_UPLOAD_MB 단일 소스.
from __future__ import annotations

import logging
import os
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
        # DATA_DIR 우선순위: MATERIALTWIN_DATA_DIR > HEAX_DATA_DIR(런처 영속 볼륨, D1) > 개발 폴백.
        # 빈 문자열(MATERIALTWIN_DATA_DIR="")은 pydantic이 Path('.')(=CWD)로 강제하므로
        # None과 동일하게 '미설정'으로 취급해 폴백을 태운다(빈 env 오설정이 CWD로 새는 것 방지).
        if self.data_dir is None or str(self.data_dir) in ("", "."):
            heax = (os.environ.get("HEAX_DATA_DIR") or "").strip()
            if heax:
                logger.info("HEAX_DATA_DIR 사용(런처 영속 볼륨): %s", heax)
                self.data_dir = Path(heax)
            else:
                logger.warning(
                    "MATERIALTWIN_DATA_DIR 미설정 — 개발 전용 폴백 경로(%s) 사용. "
                    "배포 시 절대경로 주입 필수.",
                    _DEV_FALLBACK_DATA_DIR,
                )
                self.data_dir = _DEV_FALLBACK_DATA_DIR
        self.data_dir = self.data_dir.resolve()

        # DATABASE_URL 미설정/빈 문자열 시 DATA_DIR 하위 SQLite 파일로 기본 구성.
        if not self.database_url:
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
