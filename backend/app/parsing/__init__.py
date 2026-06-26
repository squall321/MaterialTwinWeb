# 파싱 서브시스템 공개 API(dispatch + 데이터모델 재노출).
from __future__ import annotations

from .base import (
    ColumnRole,
    ColumnSpec,
    ParsedSpecimen,
    ParseIssue,
    ParseResult,
    ParserBase,
)
from .registry import dispatch

__all__ = [
    "ColumnRole",
    "ColumnSpec",
    "ParsedSpecimen",
    "ParseIssue",
    "ParseResult",
    "ParserBase",
    "dispatch",
]
