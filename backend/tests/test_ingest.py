# 적재 오케스트레이션 통합 테스트 — 골든 CSV→물성 ±2%·Parquet 실재·reaper 고아삭제(C4·C2).
from __future__ import annotations

import importlib
import uuid

import numpy as np
import pytest

from tests.fixtures.golden_linear_powerlaw import make_golden


@pytest.fixture
def app_env(tmp_path, monkeypatch):
    """DATA_DIR/DATABASE_URL을 tmp_path로 격리하고 모듈을 재로딩한다.

    config는 lru_cache라 환경변수 주입 후 캐시를 비우고 db/모델을 재임포트한다.
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{db_file}")

    from app import config as config_mod

    config_mod.get_settings.cache_clear()

    # config를 참조하는 하위 모듈을 새 설정으로 재로딩.
    import app.db as db_mod
    import app.models as models_mod
    import app.curve_store as curve_mod
    import app.ingest as ingest_mod

    db_mod = importlib.reload(db_mod)
    models_mod = importlib.reload(models_mod)
    curve_mod = importlib.reload(curve_mod)
    ingest_mod = importlib.reload(ingest_mod)

    db_mod.init_db()

    yield {
        "db": db_mod,
        "models": models_mod,
        "curve_store": curve_mod,
        "ingest": ingest_mod,
        "tmp_path": tmp_path,
    }

    config_mod.get_settings.cache_clear()


def _golden_csv_bytes() -> tuple[bytes, "make_golden"]:
    """골든 곡선을 Strain,Stress[MPa] CSV로 직렬화."""
    g = make_golden()
    lines = ["Strain,Stress [MPa]"]
    for e, s in zip(g.strain, g.stress):
        lines.append(f"{e:.8f},{s / 1e6:.6f}")
    return ("\n".join(lines)).encode("utf-8"), g


def _make_specimen(models, db):
    """flat 시편 1개 생성(area0는 stress 컬럼 경로라 결과에 영향 없음)."""
    with db.SessionLocal() as session:
        mat = models.Material(name="GoldenSteel", category="metal", attributes={})
        session.add(mat)
        session.commit()
        spec = models.Specimen(
            material_id=mat.id,
            label="S1",
            geometry_type="flat",
            gauge_length_m=0.050,
            width_m=0.0125,
            thickness_m=0.003,
            area0_m2=0.0125 * 0.003,
        )
        session.add(spec)
        session.commit()
        return spec.id


def test_ingest_golden_youngs_within_2pct(app_env):
    db = app_env["db"]
    models = app_env["models"]
    ingest = app_env["ingest"]

    spec_id = _make_specimen(models, db)
    csv_bytes, g = _golden_csv_bytes()

    with db.SessionLocal() as session:
        specimen = session.get(models.Specimen, spec_id)
        res = ingest.ingest_upload(session, specimen, csv_bytes, "golden.csv")

        assert res.computed, [i.code for i in res.issues]
        assert res.processed_result is not None
        E = res.processed_result.youngs_modulus_pa
        assert E is not None
        rel = abs(E - g.E_true_pa) / g.E_true_pa
        assert rel <= 0.02, f"E 상대오차 {rel:.4%} (E={E:.3e})"

        # raw_curve_ref.file_path 존재 + Parquet 파일 실재.
        ref = res.raw_curve_ref
        assert ref is not None and ref.file_path
        abs_path = db.settings.data_dir / ref.file_path
        assert abs_path.exists(), abs_path
        assert ref.storage == "parquet_fs"


def test_ingest_writes_parquet_with_schema(app_env):
    db = app_env["db"]
    models = app_env["models"]
    ingest = app_env["ingest"]
    curve_store = app_env["curve_store"]

    spec_id = _make_specimen(models, db)
    csv_bytes, _g = _golden_csv_bytes()

    with db.SessionLocal() as session:
        specimen = session.get(models.Specimen, spec_id)
        res = ingest.ingest_upload(session, specimen, csv_bytes, "golden.csv")
        test_id = res.test.id

    df = curve_store.read_curve(test_id)
    expected = {
        "time",
        "force_N",
        "disp_m",
        "extenso_strain",
        "eng_stress_Pa",
        "eng_strain",
    }
    assert expected.issubset(set(df.columns))
    assert len(df) > 1000


def test_reaper_deletes_orphan_tmp(app_env):
    db = app_env["db"]
    models = app_env["models"]
    ingest = app_env["ingest"]
    curve_store = app_env["curve_store"]

    spec_id = _make_specimen(models, db)
    csv_bytes, _g = _golden_csv_bytes()

    with db.SessionLocal() as session:
        specimen = session.get(models.Specimen, spec_id)
        res = ingest.ingest_upload(session, specimen, csv_bytes, "golden.csv")
        good_path = db.settings.data_dir / res.raw_curve_ref.file_path

    # 고아 .tmp 파일 + 미참조 .parquet 파일 인공 생성.
    curves_dir = db.settings.curves_dir
    orphan_tmp = curves_dir / f"99.parquet.tmp.{uuid.uuid4().hex}"
    orphan_tmp.write_bytes(b"garbage")
    orphan_parquet = curves_dir / "99999.parquet"
    orphan_parquet.write_bytes(b"garbage")

    assert orphan_tmp.exists() and orphan_parquet.exists()

    with db.SessionLocal() as session:
        stats = curve_store.reaper(session)

    # 고아 둘 다 삭제, 정상 파일은 보존.
    assert not orphan_tmp.exists()
    assert not orphan_parquet.exists()
    assert good_path.exists()
    assert stats["deleted_files"] >= 2


def test_reaper_marks_missing_when_file_deleted(app_env):
    db = app_env["db"]
    models = app_env["models"]
    ingest = app_env["ingest"]
    curve_store = app_env["curve_store"]

    spec_id = _make_specimen(models, db)
    csv_bytes, _g = _golden_csv_bytes()

    with db.SessionLocal() as session:
        specimen = session.get(models.Specimen, spec_id)
        res = ingest.ingest_upload(session, specimen, csv_bytes, "golden.csv")
        ref_id = res.raw_curve_ref.id
        good_path = db.settings.data_dir / res.raw_curve_ref.file_path

    # DB 포인터는 남기고 실제 파일만 삭제 → reaper가 missing 마킹.
    good_path.unlink()

    with db.SessionLocal() as session:
        stats = curve_store.reaper(session)
        ref = session.get(models.RawCurveRef, ref_id)
        assert ref.storage == "missing"
    assert stats["marked_missing"] >= 1
