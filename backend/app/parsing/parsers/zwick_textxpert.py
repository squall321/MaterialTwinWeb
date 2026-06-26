# Zwick testXpert 텍스트 파서 — GenericCsv + 독일어 별칭 프리셋의 얇은 wrapper(C12).
from __future__ import annotations

import re

from ..base import WARN, ParseResult, ParserBase
from ..column_map import load_aliases
from .generic_csv import GenericCsvParser, _decode

# testXpert 텍스트에서 자주 보이는 독일어/장비 표지 토큰(sniff 가산점용).
# 정확한 메타블록/단위행 위치는 # ASSUMPTION, needs D2 sample.
_ZWICK_HINTS = ("zwick", "testxpert", "kraft", "standardweg", "verlängerung", "spannung")

# 한 파일 다중시편 표지(수평 접미 _1/_2 또는 반복 헤더). 분기는 P1 제거 — WARN만.
_MULTI_HINT = re.compile(r"(prüfung|specimen|probe|serie)\s*\d+", re.IGNORECASE)


class ZwickTextXpertParser(ParserBase):
    """독립 structure 휴리스틱 없이 GenericCsv를 재사용하고 독일어 별칭만 주입한다(C12)."""

    name = "zwick_textxpert"

    def __init__(self):
        # 독일어 별칭은 yaml의 보편 엔트리에 이미 포함. 동일 alias dict 재사용.
        self._inner = GenericCsvParser(aliases=load_aliases())

    def sniff(self, sample: bytes) -> float:
        result = ParseResult()
        text = _decode(sample, result)
        if not text:
            return 0.0
        low = text.lower()
        base = self._inner.sniff(sample)
        hint_hits = sum(1 for h in _ZWICK_HINTS if h in low)
        # 독일어/장비 표지가 보이면 generic보다 살짝 우위.
        bonus = min(0.05 * hint_hits, 0.2)
        return min(base + bonus, 0.98)

    def parse(self, source: bytes | str) -> ParseResult:
        result = self._inner.parse(source)
        result.specimens = result.specimens  # 그대로
        for s in result.specimens:
            s.meta["source_format"] = "zwick_textxpert"
        # 다중시편 표지 감지 시: 파일분리만 지원(P1) → WARN.
        if result.raw_preview and _MULTI_HINT.search(result.raw_preview):
            result.add(
                WARN,
                "multi_specimen_in_file",
                "multi-specimen-in-file not yet supported, split externally.",
            )
        return result
