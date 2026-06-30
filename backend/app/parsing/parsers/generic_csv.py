# 범용 CSV/TXT 파서(인코딩 감지·delimiter/decimal 동시추정·헤더·수치테이블 인식). C5 graceful.
from __future__ import annotations

import io
import re
from pathlib import Path

import numpy as np
import pandas as pd

from ..base import (
    ERROR,
    INFO,
    WARN,
    ColumnRole,
    ParsedSpecimen,
    ParseResult,
    ParserBase,
)
from ..column_map import resolve_columns
from ..validate import validate_specimen

# 인코딩 깨짐 신호(움라우트/단위기호 모지바케). 감지 품질 점검용.
_MOJIBAKE = ("Ã", "Â", "�")

_DELIMS = [";", "\t", ",", "|"]


def _read_bytes(source: bytes | str) -> bytes:
    if isinstance(source, bytes):
        return source
    return Path(source).read_bytes()


def _decode(raw: bytes, result: ParseResult) -> str | None:
    """BOM → charset_normalizer → latin-1 폴백. 실패해도 None 아닌 latin-1 보장."""
    # BOM 우선.
    for bom, enc in (
        (b"\xef\xbb\xbf", "utf-8-sig"),
        (b"\xff\xfe", "utf-16-le"),
        (b"\xfe\xff", "utf-16-be"),
    ):
        if raw.startswith(bom):
            try:
                return raw.decode(enc)
            except Exception:
                break
    # charset_normalizer.
    try:
        from charset_normalizer import from_bytes

        best = from_bytes(raw).best()
        if best is not None:
            text = str(best)
            if not any(m in text for m in _MOJIBAKE):
                return text
            result.add(INFO, "encoding_suspect", "디코딩 결과에 모지바케 의심 문자 존재.")
            return text
    except Exception:
        pass
    # 폴백.
    try:
        return raw.decode("utf-8")
    except Exception:
        result.add(WARN, "encoding_fallback", "UTF-8 실패 → latin-1 폴백 디코딩.")
        return raw.decode("latin-1")


_NUM_TOKEN = re.compile(r"^[+\-]?[\d.,]+(?:[eE][+\-]?\d+)?$")


def _looks_numeric_row(cells: list[str]) -> bool:
    vals = [c for c in cells if c.strip() != ""]
    if len(vals) < 2:
        return False
    return all(_NUM_TOKEN.match(c.strip()) for c in vals)


def _guess_delim_decimal(lines: list[str], result: ParseResult) -> tuple[str, str]:
    """delimiter와 decimal_sep을 동시 추정(독일식 ';'+',' 케이스). 수치행 표본으로 판정.

    delimiter는 '여러 행에 걸쳐 일관된 컬럼수'를 만드는 것을 고른다(콤마 소수점이
    delimiter 후보로 오인되는 것을 차단). 동점이면 구조적 delimiter(;,tab,|)를 우선.
    """
    sample = "\n".join(lines)
    has_comma = "," in sample

    best_delim = ","
    best_score = -1.0
    # 구조적 delimiter(;,tab,|)는 콤마 소수점 오인을 피하기 위해 가중치를 준다.
    for d in (";", "\t", "|", ","):
        per_line = [len(ln.split(d)) for ln in lines if d in ln]
        per_line = [c for c in per_line if c >= 2]
        if len(per_line) < 2:
            continue
        # 최빈 컬럼수와 그 일관성(같은 컬럼수를 가진 행 비율).
        modal = max(set(per_line), key=per_line.count)
        consistency = per_line.count(modal) / len(per_line)
        weight = 1.0 if d == "," else 2.0
        # 일관성을 주축으로, 컬럼수와 구조적 가중치를 보조로.
        score = consistency * weight + 0.01 * modal
        if score > best_score:
            best_score = score
            best_delim = d

    # decimal 추정: 구조적 delimiter가 뽑혔고 ','가 따로 있으면 ','는 소수점.
    if best_delim in (";", "\t", "|") and has_comma:
        decimal = ","
    else:
        # ','가 delimiter면 decimal은 '.'. ','가 없으면 '.'.
        decimal = "."
    if decimal == ",":
        result.add(
            INFO,
            "decimal_comma",
            f"독일식 소수점 콤마 추정(delimiter={best_delim!r}).",
        )
    return best_delim, decimal


def _find_header_and_data(
    lines: list[str], delim: str
) -> tuple[int, int]:
    """헤더행 인덱스와 데이터 시작행 인덱스를 추정. (header_idx, data_start_idx)."""
    # 첫 수치테이블 블록의 시작.
    data_start = -1
    for i, ln in enumerate(lines):
        if _looks_numeric_row(ln.split(delim)):
            data_start = i
            break
    if data_start <= 0:
        return -1, data_start
    # 데이터 직전의 '연속된 비수치행 블록' 중 컬럼수가 맞는 가장 위 행을 헤더로 본다.
    # (헤더 아래 단위행이 끼는 testXpert 패턴 대응 — 중간행은 단위/서브헤더로 간주.)
    ncol = len([c for c in lines[data_start].split(delim)])
    header_idx = -1
    for j in range(data_start - 1, -1, -1):
        cells = lines[j].split(delim)
        if len(cells) == ncol and not _looks_numeric_row(cells):
            header_idx = j
            continue
        break
    return header_idx, data_start


def _to_float(token: str, decimal: str) -> float:
    t = token.strip()
    if decimal == ",":
        t = t.replace(".", "").replace(",", ".")
    if t == "" or t in ("-", "+"):
        return np.nan
    try:
        return float(t)
    except ValueError:
        return np.nan


class GenericCsvParser(ParserBase):
    """범용 CSV/TXT 파서. 텍스트 표 형식이면 best-effort로 항상 결과를 만든다."""

    name = "generic_csv"

    def __init__(self, aliases=None):
        # zwick wrapper가 독일어 별칭 프리셋을 주입할 수 있게 한다(C12).
        self._aliases = aliases

    def sniff(self, sample: bytes) -> float:
        result = ParseResult()
        text = _decode(sample, result)
        if not text:
            return 0.0
        lines = [ln for ln in text.splitlines() if ln.strip() != ""]
        if len(lines) < 2:
            return 0.0
        delim, _ = _guess_delim_decimal(lines, result)
        header_idx, data_start = _find_header_and_data(lines, delim)
        score = 0.0
        if data_start >= 0:
            score += 0.5  # 수치테이블 존재.
        if header_idx >= 0:
            score += 0.3  # 헤더 인식.
        if delim in (";", "\t"):
            score += 0.1
        return min(score, 0.95)

    def parse(self, source: bytes | str) -> ParseResult:
        result = ParseResult()
        try:
            raw = _read_bytes(source)
        except Exception as exc:  # 파일 읽기 실패도 graceful(C5).
            result.add(ERROR, "read_failed", f"입력 읽기 실패: {exc!r}")
            return result

        text = _decode(raw, result)
        if not text:
            result.add(ERROR, "decode_failed", "디코딩 실패.")
            return result

        result.raw_preview = "\n".join(text.splitlines()[:50])
        lines = [ln for ln in text.splitlines() if ln.strip() != ""]
        if len(lines) < 2:
            result.add(ERROR, "empty_table", "수치 테이블을 찾지 못함(행 부족).")
            return result

        delim, decimal = _guess_delim_decimal(lines, result)
        header_idx, data_start = _find_header_and_data(lines, delim)
        if data_start < 0:
            result.add(ERROR, "no_numeric_table", "수치 데이터 블록 미검출.")
            result.needs_manual_mapping = True
            return result

        if header_idx < 0:
            # 헤더 없음 → 일반 열이름 생성 + 수동매핑 필요.
            ncol = len(lines[data_start].split(delim))
            headers = [f"col{i}" for i in range(ncol)]
            result.add(WARN, "no_header", "헤더행 미검출 → 자동 열이름 생성.")
            result.needs_manual_mapping = True
        else:
            headers = [h.strip() for h in lines[header_idx].split(delim)]

        # 단위행 흡수(★BUG-1): 헤더와 데이터 사이의 비수치행을 단위행으로 보고 셀 단위를
        # 각 컬럼에 매핑한다(헤더 인라인 단위가 없을 때만 채워짐). 여러 비수치행이면
        # 데이터에 가장 가까운(마지막) 행을 단위행으로 본다(서브헤더 위, 단위 아래 패턴).
        unit_row: list[str] | None = None
        if header_idx >= 0:
            for j in range(data_start - 1, header_idx, -1):
                cells = lines[j].split(delim)
                if not _looks_numeric_row(cells):
                    unit_row = [c.strip() for c in cells]
                    break

        data_lines = lines[data_start:]

        # 수치 파싱.
        rows: list[list[float]] = []
        ncol = len(headers)
        for ln in data_lines:
            cells = ln.split(delim)
            if not _looks_numeric_row(cells):
                continue
            vals = [_to_float(c, decimal) for c in cells[:ncol]]
            while len(vals) < ncol:
                vals.append(np.nan)
            rows.append(vals)

        if not rows:
            result.add(ERROR, "no_data_rows", "수치 행 파싱 결과 0건.")
            return result

        data = np.asarray(rows, dtype=float)
        columns = resolve_columns(headers, self._aliases, units=unit_row)

        # 단위행에서 흡수한 단위를 INFO로 노출(자동변환 전 사용자 확인 — §5.3).
        absorbed = [
            f"{c.header}={c.unit}"
            for c in columns
            if c.unit and unit_row is not None
        ]
        if absorbed:
            result.add(
                INFO,
                "units_from_unit_row",
                f"단위행에서 단위 흡수: {', '.join(absorbed)}.",
            )

        # 매핑 신뢰도 종합.
        mapped = [c for c in columns if c.role is not ColumnRole.UNKNOWN]
        if not mapped:
            result.add(WARN, "no_roles_mapped", "어떤 컬럼도 역할 매핑 안 됨.")
            result.needs_manual_mapping = True

        specimen = ParsedSpecimen(
            columns=columns,
            data=data,
            meta={"delimiter": delim, "decimal_sep": decimal, "source_format": "generic_csv"},
        )

        # 물리 검증 + 오매핑 가드(C5).
        validate_specimen(specimen, result)

        result.specimens.append(specimen)

        # 구조 파싱 자신도(파싱 성공 != 계산 허가).
        conf = 0.4
        if header_idx >= 0:
            conf += 0.2
        avg_map_conf = (
            sum(c.confidence for c in mapped) / len(mapped) if mapped else 0.0
        )
        conf += 0.4 * avg_map_conf
        result.confidence = round(min(conf, 1.0), 3)
        if result.needs_manual_mapping:
            result.confidence = min(result.confidence, 0.4)

        return result
