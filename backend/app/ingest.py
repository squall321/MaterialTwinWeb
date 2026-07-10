# 업로드 적재 오케스트레이션 — 파서 디스패치→SI정규화→Parquet선기록→짧은 커밋(C2·C4·C5).
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app import analysis, curve_store
from app.models import ProcessedResult, RawCurveRef, Specimen, Test
from app.parsing import ColumnRole, ParsedSpecimen, dispatch
from app.parsing.base import ParseIssue

# 파싱 자신도가 이 미만이면 계산 보류(파싱 성공 != 계산 허가 — C5).
MIN_COMPUTE_CONFIDENCE = 0.5


@dataclass
class IngestResult:
    """ingest_upload 결과. test는 항상 생성되며, 저신뢰면 processed_result=None(C5)."""

    test: Test
    processed_result: ProcessedResult | None = None
    raw_curve_ref: RawCurveRef | None = None
    issues: list[ParseIssue] = field(default_factory=list)
    computed: bool = False


# ── 단위 → SI 배율(원본 표기 소문자 기준) ──────────────────────────────────────
# μ는 MICRO SIGN(U+00B5)과 GREEK SMALL MU(U+03BC)를 모두 등록(장비·키보드별 상이).
_FORCE_FACTOR = {"n": 1.0, "kn": 1e3, "mn": 1e6, "": 1.0, None: 1.0}
_LEN_FACTOR = {
    "m": 1.0, "cm": 1e-2, "mm": 1e-3,
    "µm": 1e-6, "μm": 1e-6, "um": 1e-6,  # U+00B5 / U+03BC / ASCII
    "": 1.0, None: 1.0,
}
# N/mm² = MPa (독일 DIN·Zwick testXpert 표준 응력 단위). 표기 변형 다수 등록.
_STRESS_FACTOR = {
    "pa": 1.0, "kpa": 1e3, "mpa": 1e6, "gpa": 1e9,
    "n/mm²": 1e6, "n/mm2": 1e6, "n/mm^2": 1e6, "nmm-2": 1e6,
    "kn/mm²": 1e9, "kn/mm2": 1e9,
    "": 1.0, None: 1.0,
}


def _unit_key(unit: str | None) -> str | None:
    return unit.strip().lower() if isinstance(unit, str) else unit


def _col_si(
    spec: ParsedSpecimen, role: ColumnRole, factor_map: dict,
    issues: list[ParseIssue] | None = None,
) -> np.ndarray | None:
    """역할 컬럼을 SI로 변환해 반환. 컬럼 없으면 None.

    단위가 존재하는데 미등록이면 배율 1.0으로 두되 WARN을 수집한다(무음 자릿수
    오류 방지 — docstring 계약 이행). 무단위('')는 정상으로 간주.
    """
    idx = spec.role_index(role)
    if idx is None:
        return None
    raw = np.asarray(spec.data[:, idx], dtype=float)
    unit = _unit_key(spec.columns[idx].unit)
    if unit not in factor_map:
        if issues is not None and unit not in ("", None):
            issues.append(ParseIssue(
                "WARN", "unknown_unit",
                f"'{role.value}' 컬럼의 단위 '{spec.columns[idx].unit}'를 인식하지 못해 "
                "무변환(배율 1.0) 처리 — SI 자릿수를 확인하세요.",
            ))
        return raw
    return raw * factor_map[unit]


def _strain_si(
    spec: ParsedSpecimen, large_strain: bool = False,
    issues: list[ParseIssue] | None = None,
) -> np.ndarray | None:
    """STRAIN 컬럼을 무차원으로. 단위 '%'면 /100(명시). 무단위 %추정은 카테고리별 임계.

    무단위인데 최대값이 임계를 넘으면 %로 추정해 /100 하고 INFO를 남긴다(무음 금지).
    임계는 대변형 재료(고무·폼·폴리머)에서 높인다 — 파단연신 200%(=비 2.0)를 % 오인해
    100배 축소하던 결함 방지. 명시 단위 '%'는 언제나 신뢰한다.
    """
    idx = spec.role_index(ColumnRole.STRAIN)
    if idx is None:
        return None
    raw = np.asarray(spec.data[:, idx], dtype=float)
    unit = _unit_key(spec.columns[idx].unit)
    if unit in ("%", "percent"):
        return raw / 100.0
    finite = raw[np.isfinite(raw)]
    # 소변형 재료(금속 등) 변형률 비는 ~0.5 미만 → 1.5 초과는 %가 확실.
    # 대변형 재료는 비 2~10이 정상이므로 임계를 크게(15) 잡아 오변환을 막는다.
    threshold = 15.0 if large_strain else 1.5
    if finite.size and float(np.nanmax(np.abs(finite))) > threshold:
        if issues is not None:
            issues.append(ParseIssue(
                "INFO", "strain_autoscaled_percent",
                f"무단위 변형률 최대 {float(np.nanmax(np.abs(finite))):.3g} > {threshold} — "
                "%로 추정해 /100 변환했습니다.",
            ))
        return raw / 100.0
    return raw


def _best_length(s: pd.Series, n: int) -> np.ndarray:
    return np.asarray(s, dtype=float)[:n]


def ingest_upload(
    session: Session,
    specimen: Specimen,
    file_bytes: bytes,
    filename: str,
    mapping: dict | None = None,
) -> IngestResult:
    """업로드 1건을 적재한다. parse는 예외를 안 던지므로 graceful(C5).

    저신뢰/실패: test.valid=False + processed_result 미생성, issues 반환.
    성공: SI 정규화→eng_stress/strain 계산→Parquet 선기록(트랜잭션 밖)→
    test/raw_curve_ref INSERT→compute_all→processed_result INSERT, 짧은 커밋(C2).
    """
    parser, parsed = dispatch(file_bytes)
    # 수동 매핑 재파싱(4·5단계): header→role 오버라이드 적용 후 재검증(C5).
    if mapping and parsed.specimens:
        _apply_mapping(parsed, mapping)
    issues = list(parsed.issues)
    source_format = None
    if parsed.specimens:
        source_format = parsed.specimens[0].meta.get("source_format")

    # ── 파싱 실패/저신뢰 → test만 invalid 생성, 계산 보류(C5) ──
    blocked = (
        not parsed.specimens
        or parsed.has_error()
        or parsed.needs_manual_mapping
        or parsed.confidence < MIN_COMPUTE_CONFIDENCE
    )
    if blocked:
        reason = _block_reason(parsed)
        test = Test(
            specimen_id=specimen.id,
            test_type="tensile",
            source_format=source_format,
            strain_source="crosshead",
            valid=False,
            invalid_reason=reason,
        )
        session.add(test)
        session.commit()
        return IngestResult(test=test, issues=issues, computed=False)

    spec = parsed.specimens[0]
    strain_source = spec.meta.get("strain_source", "crosshead")
    # 대변형 재료(고무·폼·폴리머)는 무단위 변형률 % 추정 임계를 높인다(오변환 방지).
    _cat = specimen.material.category if specimen.material else None
    large_strain = _cat in ("rubber", "foam", "polymer")

    # ── SI 정규화(미지 단위·% 추정은 issues로 보고) ──
    n = spec.data.shape[0]
    time = _col_si(spec, ColumnRole.TIME, {"s": 1.0, "": 1.0, None: 1.0}, issues)
    force_n = _col_si(spec, ColumnRole.FORCE, _FORCE_FACTOR, issues)
    disp_m = _col_si(spec, ColumnRole.DISPLACEMENT, _LEN_FACTOR, issues)
    ext_m = _col_si(spec, ColumnRole.EXTENSION, _LEN_FACTOR, issues)
    extenso_strain = _strain_si(spec, large_strain=large_strain, issues=issues)

    # 신율계 변형률: STRAIN 우선, 없으면 EXTENSION/gauge_length.
    if extenso_strain is None and ext_m is not None:
        extenso_strain = ext_m / specimen.gauge_length_m

    # ── 공칭 응력/변형률 계산 ──
    eng_stress_pa = None
    if force_n is not None and specimen.area0_m2:
        eng_stress_pa = force_n / specimen.area0_m2
    else:
        # STRESS 컬럼이 직접 있으면 사용(force 미존재 폴백).
        eng_stress_pa = _col_si(spec, ColumnRole.STRESS, _STRESS_FACTOR, issues)

    if extenso_strain is not None:
        eng_strain = extenso_strain
    elif disp_m is not None:
        eng_strain = disp_m / specimen.gauge_length_m
    else:
        eng_strain = None

    # 계산 불가(응력/변형률 결핍) → 저장만 하고 계산 보류(C5).
    if eng_stress_pa is None or eng_strain is None:
        test = Test(
            specimen_id=specimen.id,
            test_type="tensile",
            source_format=source_format,
            strain_source=strain_source,
            valid=False,
            invalid_reason="응력/변형률 채널 결핍 — 확인 필요.",
        )
        session.add(test)
        session.commit()
        issues.append(
            ParseIssue("WARN", "insufficient_channels", "stress 또는 strain 채널 결핍.")
        )
        return IngestResult(test=test, issues=issues, computed=False)

    # ── 곡선 DataFrame 구성(고정 컬럼 스키마) ──
    df = pd.DataFrame(
        {
            "time": time if time is not None else np.full(n, np.nan),
            "force_N": force_n if force_n is not None else np.full(n, np.nan),
            "disp_m": disp_m if disp_m is not None else np.full(n, np.nan),
            "extenso_strain": extenso_strain
            if extenso_strain is not None
            else np.full(n, np.nan),
            "eng_stress_Pa": eng_stress_pa,
            "eng_strain": eng_strain,
        }
    )

    # ── 1) Parquet 먼저 기록(DB 트랜잭션 밖, C2·C4) — test_id가 필요하므로 먼저 test INSERT ──
    test = Test(
        specimen_id=specimen.id,
        test_type="tensile",
        source_format=source_format,
        strain_source=strain_source,
        valid=True,
    )
    session.add(test)
    session.commit()  # test.id 확정(짧은 커밋, C2).

    file_path = curve_store.write_curve(test.id, df)  # 트랜잭션 밖 원자적 쓰기(C4).

    # ── 2) raw_curve_ref + 물성 계산 → processed_result, 짧은 커밋 ──
    channels = [c.role.value for c in spec.columns if c.role is not ColumnRole.UNKNOWN]
    ref = RawCurveRef(
        test_id=test.id,
        storage="parquet_fs",
        file_path=file_path,
        n_points=int(n),
        channels=channels,
        inline_data=None,
    )

    category = specimen.material.category if specimen.material else None
    metrics = analysis.compute_all(
        df["eng_strain"].to_numpy(),
        df["eng_stress_Pa"].to_numpy(),
        A0=specimen.area0_m2,
        category=category,
    )
    pr = ProcessedResult(
        test_id=test.id,
        youngs_modulus_pa=metrics["youngs_modulus_pa"],
        yield_strength_pa=metrics["yield_strength_pa"],
        uts_pa=metrics["uts_pa"],
        uniform_elongation=metrics["uniform_elongation"],
        fracture_elongation=metrics["fracture_elongation"],
        strain_hardening_n=metrics["strain_hardening_n"],
        strength_coeff_k_pa=metrics["strength_coeff_k_pa"],
        params=metrics["params"].model_dump(),
        extra_metrics=metrics["extra_metrics"],
    )
    session.add(ref)
    session.add(pr)
    session.commit()  # 짧은 커밋(C2).

    return IngestResult(
        test=test,
        processed_result=pr,
        raw_curve_ref=ref,
        issues=issues,
        computed=True,
    )


def _apply_mapping(parsed, mapping: dict) -> None:
    """parsed 첫 시편 컬럼 역할을 {header: role} 오버라이드로 갱신·재검증(C5).

    유효 role 문자열만 반영. 매핑 후 needs_manual_mapping을 풀고 신뢰도를 보정한다.
    """
    from app.parsing.validate import validate_specimen

    spec = parsed.specimens[0]
    valid_roles = {r.value for r in ColumnRole}
    by_header = {c.header: c for c in spec.columns}
    applied = False
    for header, role_str in mapping.items():
        col = by_header.get(header)
        if col is None or role_str not in valid_roles:
            continue
        col.role = ColumnRole(role_str)
        col.confidence = 1.0  # 수동 확정.
        applied = True
    if not applied:
        return
    # 매핑 반영 후 이전 검증 이슈를 비우고 재검증.
    parsed.issues = [i for i in parsed.issues if i.code != "no_roles_mapped"]
    validate_specimen(spec, parsed)
    parsed.needs_manual_mapping = False
    parsed.confidence = max(parsed.confidence, MIN_COMPUTE_CONFIDENCE)


def _block_reason(parsed) -> str:
    if not parsed.specimens:
        return "파싱 실패 — 확인 필요."
    if parsed.has_error():
        return "파싱 오류 — 확인 필요."
    if parsed.needs_manual_mapping:
        return "수동 컬럼 매핑 필요 — 확인 필요."
    return f"파싱 신뢰도 낮음({parsed.confidence:.2f}) — 확인 필요."
