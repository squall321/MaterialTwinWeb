# Pydantic v2 DTO(Material/Specimen/Test/Properties Out 중심) + ProcessingParams(params 직렬화 모델).
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ── 계산 파라미터(processed_result.params 직렬화 전용, 원시 dict 금지 — C10) ───
class ProcessingParams(BaseModel):
    """영률 등 산출에 쓰인 파라미터/추적 정보. params 컬럼은 이 모델로만 직렬화."""

    schema_version: int = 1
    e_range: tuple[float, float]  # 영률 회귀 변형률 구간 [ε_lo, ε_hi]
    offset: float = 0.002  # 항복 offset(무차원)
    toe: bool = True  # toe(발끝) 보정 적용 여부
    r2: float  # 영률 회귀 결정계수
    confidence: Literal["high", "ok", "low"]  # R² 등급(거부 아님 — C1)
    n_points: int  # 회귀에 사용된 점 수


# ── Material ────────────────────────────────────────────────────────────────
class MaterialIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    material_code: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = None
    attributes: dict = Field(default_factory=dict)


class MaterialPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    material_code: str | None = Field(default=None, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    description: str | None = None
    attributes: dict | None = None


class MaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    material_code: str | None
    category: str | None
    description: str | None
    attributes: dict
    created_at: datetime
    updated_at: datetime


# ── Specimen ──────────────────────────────────────────────────────────────
class SpecimenIn(BaseModel):
    """시편 입력(SI 단위). 편의 단위 변환은 라우터에서 units.py로 선처리."""

    label: str = Field(..., min_length=1, max_length=100)
    geometry_type: Literal["flat", "round"]
    gauge_length_m: float = Field(..., gt=0)
    width_m: float | None = Field(default=None, gt=0)
    thickness_m: float | None = Field(default=None, gt=0)
    diameter_m: float | None = Field(default=None, gt=0)
    area0_m2: float | None = Field(default=None, gt=0)  # 미입력 시 형상서 산출
    orientation: str | None = Field(default=None, max_length=20)
    standard: str | None = Field(default=None, max_length=30)


class SpecimenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    label: str
    geometry_type: str
    gauge_length_m: float
    width_m: float | None
    thickness_m: float | None
    diameter_m: float | None
    area0_m2: float
    orientation: str | None
    standard: str | None


# ── Test ──────────────────────────────────────────────────────────────────
class TestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    specimen_id: int
    test_type: str
    machine: str | None
    software: str | None
    source_format: str | None
    strain_source: str
    test_speed_m_s: float | None
    temperature_k: float | None
    tested_at: datetime | None
    valid: bool
    invalid_reason: str | None


class TestPatch(BaseModel):
    valid: bool | None = None
    invalid_reason: str | None = Field(default=None, max_length=200)


# ── Properties (processed_result) ─────────────────────────────────────────
class PropertiesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    test_id: int
    youngs_modulus_pa: float | None
    yield_strength_pa: float | None
    uts_pa: float | None
    uniform_elongation: float | None
    fracture_elongation: float | None
    reduction_of_area: float | None
    strain_hardening_n: float | None
    strength_coeff_k_pa: float | None
    params: dict
    extra_metrics: dict | None
    computed_at: datetime
