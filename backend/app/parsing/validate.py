# 물리 검증 + 오매핑 가드(단조성·채널상관·자릿수) + strain_source 결정. C5 핵심.
from __future__ import annotations

import numpy as np

from .base import (
    INFO,
    WARN,
    ColumnRole,
    ParsedSpecimen,
    ParseResult,
)


def _column(spec: ParsedSpecimen, role: ColumnRole) -> np.ndarray | None:
    idx = spec.role_index(role)
    if idx is None:
        return None
    col = spec.data[:, idx]
    finite = col[np.isfinite(col)]
    return finite if finite.size else None


def _is_monotonic(x: np.ndarray) -> bool:
    if x.size < 3:
        return False
    d = np.diff(x)
    return bool(np.all(d >= -1e-12))


def _normalized(x: np.ndarray) -> np.ndarray | None:
    rng = float(np.ptp(x))
    if rng <= 0:
        return None
    return (x - x.min()) / rng


def determine_strain_source(spec: ParsedSpecimen) -> str:
    """EXTENSION/STRAIN 있으면 extensometer, DISPLACEMENT만이면 crosshead(§5.4)."""
    has_ext = spec.role_index(ColumnRole.EXTENSION) is not None
    has_strain = spec.role_index(ColumnRole.STRAIN) is not None
    if has_ext or has_strain:
        return "extensometer"
    return "crosshead"


def validate_specimen(spec: ParsedSpecimen, result: ParseResult) -> None:
    """오매핑 가드 + 물리 일관성 검사. 결과는 result.issues에 누적, strain_source는 meta에 기록."""
    force = _column(spec, ColumnRole.FORCE)
    disp = _column(spec, ColumnRole.DISPLACEMENT)
    ext = _column(spec, ColumnRole.EXTENSION)

    # ── 오매핑 가드 1: 단조성 ──
    # force가 변위처럼 끝까지 단조증가만 하면 의심(인장 force는 보통 항복 후 변동/하강).
    if force is not None and _is_monotonic(force) and force.size >= 5:
        result.add(
            WARN,
            "force_monotonic_suspect",
            "FORCE 채널이 변위처럼 단조증가만 함 — 컬럼 오매핑 의심.",
        )

    # ── 오매핑 가드 2: 채널 상관(동일 신호면 오매핑) ──
    elong = disp if disp is not None else ext
    if force is not None and elong is not None:
        n = min(force.size, elong.size)
        if n >= 5:
            fn = _normalized(force[:n])
            en = _normalized(elong[:n])
            if fn is not None and en is not None:
                # 정규화 후 차이가 거의 0이면 동일 신호.
                max_abs_diff = float(np.max(np.abs(fn - en)))
                corr = float(np.corrcoef(force[:n], elong[:n])[0, 1])
                if max_abs_diff < 1e-6 or corr > 0.99999:
                    result.add(
                        WARN,
                        "force_disp_same_signal",
                        "FORCE와 변위 채널이 동일 신호로 보임 — 컬럼 오매핑 의심.",
                    )

    # ── 오매핑 가드 3: 자릿수(N인데 kN 의심) ──
    if force is not None:
        idx = spec.role_index(ColumnRole.FORCE)
        unit = (spec.columns[idx].unit or "").lower() if idx is not None else ""
        peak = float(np.nanmax(np.abs(force)))
        if "kn" not in unit and peak > 1e5:
            result.add(
                INFO,
                "force_unit_scale_suspect",
                f"FORCE 단위 미상인데 피크={peak:.3g} — kN/N 자릿수 확인 필요.",
            )

    # ── STRAIN % vs 무차원 모호성 ──
    strain = _column(spec, ColumnRole.STRAIN)
    if strain is not None:
        smax = float(np.nanmax(np.abs(strain)))
        if smax > 1.0:
            result.add(
                INFO,
                "strain_percent_suspect",
                f"STRAIN 최대={smax:.3g}>1 — % 단위(무차원 아님) 가능, 확인 필요.",
            )

    # ── strain_source 결정 ──
    spec.meta["strain_source"] = determine_strain_source(spec)
