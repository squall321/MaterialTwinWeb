# 파싱 서브시스템 회귀 테스트 — 합성 픽스처(콤마소수점/세미콜론/움라우트/단위행/오매핑). C5·C12.
from __future__ import annotations

import numpy as np

from app.parsing import ColumnRole, ParseResult, dispatch
from app.parsing.base import ERROR
from app.parsing.column_map import resolve_columns
from app.parsing.parsers.generic_csv import GenericCsvParser
from app.parsing.validate import validate_specimen


# ── 합성 픽스처 ────────────────────────────────────────────────────────────
def _german_semicolon_comma() -> bytes:
    # 독일식: ';' delimiter + ',' 소수점 + 움라우트 헤더 + 단위행.
    lines = [
        "Standardweg;Kraft;Verlängerung",
        "mm;kN;mm",  # 단위행(헤더 아래 비수치행)
    ]
    for i in range(20):
        d = i * 0.1
        f = i * 0.5  # kN
        e = i * 0.09
        lines.append(f"{d:.3f};{f:.3f};{e:.3f}".replace(".", ","))
    return ("\n".join(lines)).encode("utf-8")


def _english_comma_csv() -> bytes:
    lines = ["Displacement [mm],Force [N],Stress [MPa]"]
    for i in range(20):
        lines.append(f"{i*0.1:.4f},{i*50.0:.2f},{i*5.0:.2f}")
    return ("\n".join(lines)).encode("utf-8")


def _broken_encoding() -> bytes:
    # latin-1로 인코딩한 움라우트 — utf-8로 보면 깨짐.
    text = "Verlängerung;Kraft\n" + "\n".join(
        f"{i*0.1:.2f};{i*0.3:.2f}".replace(".", ",") for i in range(15)
    )
    return text.encode("latin-1")


def _mismapped_force_equals_disp() -> bytes:
    # FORCE와 DISPLACEMENT가 동일 신호(오매핑 가드 트리거).
    lines = ["Force [N],Displacement [mm]"]
    for i in range(15):
        v = i * 1.0
        lines.append(f"{v:.3f},{v:.3f}")
    return ("\n".join(lines)).encode("utf-8")


# ── parse는 예외 0건 + 이슈 수집(C5) ────────────────────────────────────────
def test_parse_never_raises_over_all_fixtures():
    fixtures = [
        _german_semicolon_comma(),
        _english_comma_csv(),
        _broken_encoding(),
        _mismapped_force_equals_disp(),
        b"",  # 빈 입력
        b"\x00\x01\x02\x03garbage",  # 바이너리 쓰레기
        b"just one line no table",
    ]
    for raw in fixtures:
        # dispatch/parse 어느 것도 예외를 던지면 안 된다.
        _parser, result = dispatch(raw)
        assert isinstance(result, ParseResult)
        # ParseResult는 항상 issues 리스트를 가진다.
        assert isinstance(result.issues, list)


def test_empty_and_garbage_yield_error_issue():
    for raw in (b"", b"\x00\x01\x02garbage", b"one line"):
        _p, result = dispatch(raw)
        assert result.has_error(), "비정상 입력은 ERROR 이슈를 남겨야 함"
        assert not result.specimens


# ── 독일식 소수점/세미콜론 정확 파싱 ────────────────────────────────────────
def test_german_semicolon_comma_decimal():
    _p, result = dispatch(_german_semicolon_comma())
    assert result.specimens, result.issues
    spec = result.specimens[0]
    assert spec.meta["delimiter"] == ";"
    assert spec.meta["decimal_sep"] == ","
    # 소수점이 콤마였어도 float로 정확히 복원.
    assert spec.data.shape[0] == 20
    # Kraft→force, Standardweg→displacement, Verlängerung→extension 매핑.
    roles = {c.role for c in spec.columns}
    assert ColumnRole.FORCE in roles
    assert ColumnRole.DISPLACEMENT in roles
    assert ColumnRole.EXTENSION in roles
    # EXTENSION 존재 → extensometer.
    assert spec.meta["strain_source"] == "extensometer"
    # decimal_comma INFO 이슈 수집.
    assert any(i.code == "decimal_comma" for i in result.issues)


def test_unit_row_skipped_values_correct():
    _p, result = dispatch(_german_semicolon_comma())
    spec = result.specimens[0]
    fidx = spec.role_index(ColumnRole.FORCE)
    # 두 번째 데이터행 Kraft = 0.5 (단위행 'kN'이 값으로 들어가지 않았는지).
    col = spec.data[:, fidx]
    assert np.isfinite(col).all()
    assert abs(col[1] - 0.5) < 1e-9


def test_unit_row_absorbed_into_columns():
    # ★BUG-1 회귀: 헤더 아래 단위행("mm;kN;mm")이 각 컬럼 unit으로 흡수돼야 한다.
    _p, result = dispatch(_german_semicolon_comma())
    spec = result.specimens[0]
    by_role = {c.role: c for c in spec.columns}
    assert by_role[ColumnRole.FORCE].unit == "kN"
    assert by_role[ColumnRole.DISPLACEMENT].unit == "mm"
    assert by_role[ColumnRole.EXTENSION].unit == "mm"


# ── 깨진 인코딩 graceful ─────────────────────────────────────────────────────
def test_broken_encoding_graceful():
    _p, result = dispatch(_broken_encoding())
    # 예외 없이 파싱 결과를 만들거나, 최소한 이슈로 보고.
    assert isinstance(result, ParseResult)
    if result.specimens:
        spec = result.specimens[0]
        assert ColumnRole.FORCE in {c.role for c in spec.columns}


# ── 오매핑 가드(C5) ────────────────────────────────────────────────────────
def test_mismapping_guard_force_equals_disp():
    _p, result = dispatch(_mismapped_force_equals_disp())
    assert result.specimens
    codes = {i.code for i in result.issues}
    # force가 단조 또는 동일신호 → 가드 중 하나라도 발화해야 함.
    assert (
        "force_disp_same_signal" in codes or "force_monotonic_suspect" in codes
    ), codes


def test_strain_source_crosshead_when_only_displacement():
    raw = b"Displacement [mm],Force [N]\n" + b"\n".join(
        f"{i*0.1:.3f},{(i*i)%7 * 1.0:.3f}".encode() for i in range(12)
    )
    _p, result = dispatch(raw)
    spec = result.specimens[0]
    assert spec.meta["strain_source"] == "crosshead"


# ── column_map 단위 분리 ────────────────────────────────────────────────────
def test_resolve_columns_unit_split():
    specs = resolve_columns(["Force [kN]", "Time (s)", "Weird"])
    assert specs[0].role is ColumnRole.FORCE
    assert specs[0].unit == "kN"
    assert specs[1].role is ColumnRole.TIME
    assert specs[1].unit == "s"
    assert specs[2].role is ColumnRole.UNKNOWN
