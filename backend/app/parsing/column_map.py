# 헤더 문자열 → ColumnRole 매핑(별칭 yaml + 휴리스틱, 단위 추출 포함).
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from .base import ColumnRole, ColumnSpec

_ALIASES_PATH = Path(__file__).parent / "config" / "column_aliases.yaml"

# yaml의 roles 키 ↔ ColumnRole 매핑.
_ROLE_BY_NAME = {
    "time": ColumnRole.TIME,
    "force": ColumnRole.FORCE,
    "displacement": ColumnRole.DISPLACEMENT,
    "extension": ColumnRole.EXTENSION,
    "strain": ColumnRole.STRAIN,
    "stress": ColumnRole.STRESS,
}

# 별칭이 비었을 때를 대비한 명백한 보편 폴백(영문/SI 표준). yaml이 우선.
_FALLBACK_ALIASES: dict[ColumnRole, list[str]] = {
    ColumnRole.TIME: ["time", "zeit"],
    ColumnRole.FORCE: ["force", "load", "kraft"],
    ColumnRole.DISPLACEMENT: ["displacement", "crosshead", "stroke", "standardweg", "weg"],
    ColumnRole.EXTENSION: ["extension", "elongation", "verlängerung", "verlangerung"],
    ColumnRole.STRAIN: ["strain", "dehnung"],
    ColumnRole.STRESS: ["stress", "spannung"],
}


@lru_cache(maxsize=1)
def load_aliases() -> dict[ColumnRole, list[str]]:
    """yaml 별칭을 로드해 role→소문자별칭리스트로 반환. yaml 누락 시 폴백."""
    out: dict[ColumnRole, list[str]] = {r: [] for r in _ROLE_BY_NAME.values()}
    try:
        raw = yaml.safe_load(_ALIASES_PATH.read_text(encoding="utf-8")) or {}
        roles = raw.get("roles", {}) or {}
        for name, role in _ROLE_BY_NAME.items():
            entries = roles.get(name) or []
            out[role] = [str(e).strip().lower() for e in entries if str(e).strip()]
    except Exception:
        out = {r: [] for r in _ROLE_BY_NAME.values()}
    # 폴백 병합(yaml 우선, 중복 제거).
    for role, fb in _FALLBACK_ALIASES.items():
        merged = list(dict.fromkeys(out.get(role, []) + fb))
        out[role] = merged
    return out


_UNIT_RE = re.compile(r"[\[\(]\s*([^\]\)]+?)\s*[\]\)]")


def _split_unit(header: str) -> tuple[str, str | None]:
    """헤더에서 '[mm]'/'(kN)' 형태 단위를 분리. 반환 (정리된 헤더, 단위 or None)."""
    m = _UNIT_RE.search(header)
    unit = m.group(1).strip() if m else None
    name = _UNIT_RE.sub("", header).strip()
    return name, unit


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def resolve_columns(
    headers: list[str], aliases: dict[ColumnRole, list[str]] | None = None
) -> list[ColumnSpec]:
    """헤더 리스트 → ColumnSpec 리스트. 별칭 부분일치 휴리스틱."""
    aliases = aliases or load_aliases()
    specs: list[ColumnSpec] = []
    for idx, raw_header in enumerate(headers):
        name, unit = _split_unit(raw_header)
        key = _norm(name)
        role = ColumnRole.UNKNOWN
        conf = 0.0
        best_len = 0
        for r, alist in aliases.items():
            for alias in alist:
                if not alias:
                    continue
                # 정확일치 우선, 그다음 부분일치(가장 긴 별칭 우승).
                if key == alias:
                    if 1.0 > conf or len(alias) > best_len:
                        role, conf, best_len = r, 1.0, len(alias)
                elif alias in key:
                    cand = 0.7
                    if cand > conf or (cand == conf and len(alias) > best_len):
                        role, conf, best_len = r, cand, len(alias)
        specs.append(
            ColumnSpec(index=idx, header=raw_header, role=role, unit=unit, confidence=conf)
        )
    return specs
