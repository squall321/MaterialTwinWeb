# 파서 공용 데이터모델/추상 베이스(ColumnRole·ParseResult·ParserBase, parse는 예외 무던짐 — C5).
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class ColumnRole(str, Enum):
    """원본 컬럼이 표현하는 물리 채널 역할."""

    TIME = "time"
    FORCE = "force"
    DISPLACEMENT = "displacement"  # crosshead(Standardweg)
    EXTENSION = "extension"  # 신율계(Verlängerung)
    STRAIN = "strain"
    STRESS = "stress"
    UNKNOWN = "unknown"


@dataclass
class ColumnSpec:
    """한 컬럼의 매핑 결과. unit은 원본 표기 그대로(SI 변환은 units.py가 ingest에서 1회 수행)."""

    index: int
    header: str
    role: ColumnRole
    unit: str | None = None
    # 헤더→역할 휴리스틱 신뢰도(0~1). 낮으면 needs_manual_mapping 유도.
    confidence: float = 1.0


@dataclass
class ParseIssue:
    """파싱/검증 중 수집되는 단일 이슈. parse()는 예외 대신 이것을 쌓는다(C5)."""

    level: str  # "ERROR" | "WARN" | "INFO"
    code: str
    message: str


ERROR = "ERROR"
WARN = "WARN"
INFO = "INFO"


@dataclass
class ParsedSpecimen:
    """한 시편의 컬럼 매핑 + 수치 데이터(행=샘플, 열=ColumnSpec 순서)."""

    columns: list[ColumnSpec]
    data: np.ndarray
    meta: dict[str, Any] = field(default_factory=dict)

    def role_index(self, role: ColumnRole) -> int | None:
        for c in self.columns:
            if c.role is role:
                return c.index
        return None


@dataclass
class ParseResult:
    """parse()의 graceful 반환. specimens가 비어도 issues로 사유를 전달한다."""

    specimens: list[ParsedSpecimen] = field(default_factory=list)
    issues: list[ParseIssue] = field(default_factory=list)
    # 구조 파싱 자신도(0~1). 파싱 성공 != 계산 허가 — 낮으면 계산 보류(C5).
    confidence: float = 0.0
    needs_manual_mapping: bool = False
    # 미지 형식일 때 프론트 수동 매핑용 원본 앞부분(텍스트).
    raw_preview: str | None = None

    def add(self, level: str, code: str, message: str) -> None:
        self.issues.append(ParseIssue(level=level, code=code, message=message))

    def has_error(self) -> bool:
        return any(i.level == ERROR for i in self.issues)


class ParserBase(ABC):
    """파서 어댑터 추상 베이스. sniff로 점수, parse로 graceful 결과."""

    name: str = "base"

    @abstractmethod
    def sniff(self, sample: bytes) -> float:
        """이 파서가 표본을 처리할 자신도(0~1)."""

    @abstractmethod
    def parse(self, source: bytes | str) -> ParseResult:
        """파싱. 절대 예외를 던지지 않고 ParseResult.issues로 모든 실패를 보고한다(C5)."""
