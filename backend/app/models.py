# ORM 테이블(material/specimen/test/raw_curve_ref/processed_result/constitutive_fit) — PLAN §4.3·§6.3.
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, UTCDateTime


class Material(Base):
    __tablename__ = "material"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    material_code: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # 자유 메타(검색 금지). JSON 컬럼은 WHERE/ORDER BY 대상 아님.
    attributes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # owner_id: 멀티테넌시 슬롯(Phase 1 미사용).
    owner_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        UTCDateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    specimens: Mapped[list["Specimen"]] = relationship(
        back_populates="material",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Specimen(Base):
    __tablename__ = "specimen"
    __table_args__ = (
        CheckConstraint(
            "geometry_type IN ('flat','round')", name="ck_specimen_geometry_type"
        ),
        CheckConstraint(
            "(geometry_type = 'flat' AND width_m IS NOT NULL AND thickness_m IS NOT NULL)"
            " OR (geometry_type = 'round' AND diameter_m IS NOT NULL)",
            name="ck_specimen_geometry_dims",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    material_id: Mapped[int] = mapped_column(
        ForeignKey("material.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    geometry_type: Mapped[str] = mapped_column(String(20), nullable=False)
    gauge_length_m: Mapped[float] = mapped_column(Float, nullable=False)
    width_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    thickness_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    diameter_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    area0_m2: Mapped[float] = mapped_column(Float, nullable=False)
    orientation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    standard: Mapped[str | None] = mapped_column(String(30), nullable=True)

    material: Mapped["Material"] = relationship(back_populates="specimens")
    tests: Mapped[list["Test"]] = relationship(
        back_populates="specimen",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Test(Base):
    __tablename__ = "test"
    __table_args__ = (
        CheckConstraint(
            "strain_source IN ('extensometer','crosshead')",
            name="ck_test_strain_source",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    specimen_id: Mapped[int] = mapped_column(
        ForeignKey("specimen.id", ondelete="CASCADE"), nullable=False
    )
    test_type: Mapped[str] = mapped_column(
        String(30), nullable=False, default="tensile"
    )
    machine: Mapped[str | None] = mapped_column(String(100), nullable=True)
    software: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_format: Mapped[str | None] = mapped_column(String(20), nullable=True)
    strain_source: Mapped[str] = mapped_column(String(20), nullable=False)
    test_speed_m_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_k: Mapped[float | None] = mapped_column(Float, nullable=True)
    tested_at: Mapped[datetime | None] = mapped_column(
        UTCDateTime, nullable=True
    )
    valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    invalid_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)

    specimen: Mapped["Specimen"] = relationship(back_populates="tests")
    raw_curve_ref: Mapped["RawCurveRef | None"] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    processed_result: Mapped["ProcessedResult | None"] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    constitutive_fits: Mapped[list["ConstitutiveFit"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RawCurveRef(Base):
    __tablename__ = "raw_curve_ref"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(
        ForeignKey("test.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    storage: Mapped[str] = mapped_column(
        String(20), nullable=False, default="parquet_fs"
    )
    # DATA_DIR 기준 상대경로만 저장(절대경로 금지).
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    n_points: Mapped[int] = mapped_column(Integer, nullable=False)
    channels: Mapped[list] = mapped_column(JSON, nullable=False)
    inline_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    test: Mapped["Test"] = relationship(back_populates="raw_curve_ref")


class ProcessedResult(Base):
    __tablename__ = "processed_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(
        ForeignKey("test.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    youngs_modulus_pa: Mapped[float | None] = mapped_column(Float, nullable=True)
    yield_strength_pa: Mapped[float | None] = mapped_column(Float, nullable=True)
    uts_pa: Mapped[float | None] = mapped_column(Float, nullable=True)
    uniform_elongation: Mapped[float | None] = mapped_column(Float, nullable=True)
    fracture_elongation: Mapped[float | None] = mapped_column(Float, nullable=True)
    reduction_of_area: Mapped[float | None] = mapped_column(Float, nullable=True)
    strain_hardening_n: Mapped[float | None] = mapped_column(Float, nullable=True)
    strength_coeff_k_pa: Mapped[float | None] = mapped_column(Float, nullable=True)
    # params: ProcessingParams 직렬화 dict(원시 dict 금지, C10). 추적성 필수.
    params: Mapped[dict] = mapped_column(JSON, nullable=False)
    extra_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    computed_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, server_default=func.now()
    )

    test: Mapped["Test"] = relationship(back_populates="processed_result")


class ConstitutiveFit(Base):
    __tablename__ = "constitutive_fit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(
        ForeignKey("test.id", ondelete="CASCADE"), nullable=False
    )
    # hollomon / swift / voce / johnson_cook.
    model: Mapped[str] = mapped_column(String(30), nullable=False)
    # 모델 파라미터 dict(K_pa,n 등). SI. 검색 대상 아니라 JSON.
    params: Mapped[dict] = mapped_column(JSON, nullable=False)
    r2: Mapped[float | None] = mapped_column(Float, nullable=True)
    rmse_pa: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fitted_at: Mapped[datetime] = mapped_column(
        UTCDateTime, nullable=False, server_default=func.now()
    )

    test: Mapped["Test"] = relationship(back_populates="constitutive_fits")
