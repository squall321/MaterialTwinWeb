# 파서 레지스트리 — sniff 점수 디스패치(절대임계 아닌 상대 분리 규칙). C5.
from __future__ import annotations

from .base import INFO, WARN, ParseResult, ParserBase
from .parsers.generic_csv import GenericCsvParser
from .parsers.zwick_textxpert import ZwickTextXpertParser

# 표본으로 읽을 최대 바이트(sniff 비용 제한).
_SNIFF_BYTES = 64 * 1024

# placeholder, D2 후 ROC 보정 — 1등이 이만큼 앞서야 "유의분리"로 본다(상대 규칙).
SNIFF_MARGIN = 0.1  # placeholder, D2 후 ROC 보정
# placeholder, D2 후 ROC 보정 — 어떤 파서도 이 미만이면 필수 시그니처 미충족으로 간주.
MIN_SIGNATURE_SCORE = 0.5  # placeholder, D2 후 ROC 보정


def _registered() -> list[ParserBase]:
    # GenericCsv는 항상 best-effort 폴백으로 마지막에 둔다.
    return [ZwickTextXpertParser(), GenericCsvParser()]


def dispatch(source: bytes) -> tuple[ParserBase, ParseResult]:
    """표본으로 sniff → 디스패치. 상대 분리 실패/시그니처 미충족 시 GenericCsv 폴백."""
    sample = source[:_SNIFF_BYTES]
    parsers = _registered()
    scored = sorted(
        ((p.sniff(sample), p) for p in parsers), key=lambda t: t[0], reverse=True
    )
    top_score, top = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0

    fallback = next(p for p in parsers if isinstance(p, GenericCsvParser))

    # 규칙 1: 어떤 파서도 필수 시그니처 미충족 → 폴백 + 수동매핑.
    if top_score < MIN_SIGNATURE_SCORE:
        result = fallback.parse(source)
        result.needs_manual_mapping = True
        result.add(
            INFO,
            "low_sniff_fallback",
            f"최고 sniff 점수 {top_score:.2f} < {MIN_SIGNATURE_SCORE} — GenericCsv best-effort.",
        )
        return fallback, result

    # 규칙 2: 1등이 2등과 유의분리 안 됨 → 둘 다 generic 계열이면 그냥 진행,
    # 아니면 폴백 + 수동매핑(오디스패치 위험 회피).
    if (top_score - second_score) < SNIFF_MARGIN and not isinstance(top, GenericCsvParser):
        result = top.parse(source)
        result.add(
            WARN,
            "ambiguous_dispatch",
            f"파서 {top.name} 선택했으나 2등과 분리 미흡({top_score:.2f} vs {second_score:.2f}).",
        )
        return top, result

    return top, top.parse(source)
