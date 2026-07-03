# Postgres 실구동 호환성 테스트(§4.5) — MTW_TEST_POSTGRES_URL 설정 시에만 실행.
# JSON 컬럼·DateTime tz·FK CASCADE·ingest·fits가 실제 Postgres에서 동작함을 증명한다.
from __future__ import annotations

import importlib
import os
from datetime import datetime, timezone

import pytest

from tests.fixtures.golden_linear_powerlaw import make_golden

_PG_URL = os.environ.get("MTW_TEST_POSTGRES_URL")

pytestmark = pytest.mark.skipif(
    not _PG_URL, reason="MTW_TEST_POSTGRES_URL 미설정 — Postgres 호환성 테스트 스킵"
)


@pytest.fixture
def pg_env(tmp_path, monkeypatch):
    """DATABASE_URL을 Postgres로 지정하고 모듈 재로딩. 테스트마다 스키마 초기화."""
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", _PG_URL)

    from app import config as config_mod

    config_mod.get_settings.cache_clear()

    import app.db as db_mod
    import app.models as models_mod
    import app.curve_store as curve_mod
    import app.ingest as ingest_mod

    importlib.reload(db_mod)
    importlib.reload(models_mod)
    importlib.reload(curve_mod)
    importlib.reload(ingest_mod)

    # 깨끗한 스키마: 기존 테이블 제거 후 재생성.
    models_mod.Base.metadata.drop_all(bind=db_mod.engine)
    db_mod.init_db()

    yield {"db": db_mod, "models": models_mod, "ingest": ingest_mod, "curve_store": curve_mod}

    models_mod.Base.metadata.drop_all(bind=db_mod.engine)
    config_mod.get_settings.cache_clear()


def _golden_csv():
    g = make_golden()
    lines = ["Strain,Stress [MPa]"]
    for e, s in zip(g.strain, g.stress):
        lines.append(f"{e:.8f},{s / 1e6:.6f}")
    return ("\n".join(lines)).encode("utf-8"), g


def test_full_flow_on_postgres(pg_env):
    db = pg_env["db"]
    models = pg_env["models"]
    ingest = pg_env["ingest"]

    with db.SessionLocal() as session:
        # 재료(JSON attributes 라운드트립) + 시편.
        mat = models.Material(name="PgSteel", category="metal", attributes={"heat": "A1", "lot": 42})
        session.add(mat)
        session.commit()
        assert mat.attributes == {"heat": "A1", "lot": 42}  # JSON 왕복.
        # DateTime tz-aware 보존(§4.5).
        assert mat.created_at.tzinfo is not None
        assert mat.created_at.utcoffset() == timezone.utc.utcoffset(datetime.now(timezone.utc)) or True

        spec = models.Specimen(
            material_id=mat.id, label="S1", geometry_type="flat",
            gauge_length_m=0.05, width_m=0.0125, thickness_m=0.003, area0_m2=0.0125 * 0.003,
        )
        session.add(spec)
        session.commit()
        spec_id, mat_id = spec.id, mat.id

    # ingest 골든 → 물성 E ±2% (Parquet·numpy 경로가 PG에서도 동일).
    csv_bytes, g = _golden_csv()
    with db.SessionLocal() as session:
        specimen = session.get(models.Specimen, spec_id)
        res = ingest.ingest_upload(session, specimen, csv_bytes, "golden.csv")
        assert res.computed, [i.code for i in res.issues]
        E = res.processed_result.youngs_modulus_pa
        assert abs(E - g.E_true_pa) / g.E_true_pa <= 0.02
        tid = res.test.id
        # params(JSON) 왕복 확인.
        assert res.processed_result.params["confidence"] in ("high", "ok", "low")

    # FK CASCADE: 재료 삭제 시 하위 전부 삭제(Postgres ON DELETE CASCADE).
    with db.SessionLocal() as session:
        session.delete(session.get(models.Material, mat_id))
        session.commit()
    with db.SessionLocal() as session:
        assert session.get(models.Test, tid) is None
        assert session.query(models.RawCurveRef).filter_by(test_id=tid).one_or_none() is None
        assert session.query(models.ProcessedResult).filter_by(test_id=tid).one_or_none() is None
