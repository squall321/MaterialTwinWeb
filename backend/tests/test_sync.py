# 데이터 번들 export/병합 import 회귀 — 운영 추가분 보존·중복 방지·라운드트립 손실 없음.
from __future__ import annotations

import importlib

import numpy as np
import pytest


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{tmp_path / 'a.db'}")
    from app import config as config_mod
    config_mod.get_settings.cache_clear()
    import app.db as db_mod
    import app.models as models_mod
    import app.curve_store as curve_mod
    import app.ingest as ingest_mod
    import app.sync as sync_mod
    for m in (db_mod, models_mod, curve_mod, ingest_mod, sync_mod):
        importlib.reload(m)
    db_mod.init_db()
    import mcp_server as M
    importlib.reload(M)
    yield {"db": db_mod, "models": models_mod, "sync": sync_mod, "mcp": M, "tmp": tmp_path}
    config_mod.get_settings.cache_clear()


def _register(M, name, code=None, n=200, sigy=350e6):
    from tests.fixtures.golden_linear_powerlaw import make_golden
    g = make_golden(sigma_y=sigy, n_points=n)  # sigy로 곡선을 구분(content-hash 상이).
    mid = M.register_material(name, category="metal", material_code=code)["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    return mid, tid


def _counts(db):
    from app.models import Material, Test
    with db.SessionLocal() as s:
        return s.query(Material).count(), s.query(Test).count()


def test_export_import_roundtrip(env):
    M, sync, db, tmp = env["mcp"], env["sync"], env["db"], env["tmp"]
    _register(M, "강A", code="A1", sigy=350e6)
    _register(M, "강B", code="B1", sigy=520e6)
    with db.SessionLocal() as s:
        summ = sync.export_bundle(s, tmp / "b.tar.gz")
    assert summ["materials"] == 2 and summ["tests"] == 2 and summ["curves"] == 2

    # 같은 DB에 재임포트 → 전부 중복이라 아무것도 추가 안 됨(멱등).
    with db.SessionLocal() as s:
        st = sync.import_bundle(s, tmp / "b.tar.gz")
    assert st["tests_added"] == 0 and st["tests_skipped"] == 2
    assert _counts(db) == (2, 2)  # 변화 없음.


def test_merge_preserves_operational_additions(env):
    """A에서 번들 만들고, B(운영)에 새 재료 추가 후 병합 → B의 추가분이 보존돼야."""
    M, sync, db, tmp = env["mcp"], env["sync"], env["db"], env["tmp"]
    # 초기 상태(공유): 강A.
    _register(M, "강A", code="A1")
    with db.SessionLocal() as s:
        sync.export_bundle(s, tmp / "shared.tar.gz")

    # '운영'에서 새 재료 강운영 추가(번들엔 없음).
    _register(M, "강운영", code="OP1")
    assert _counts(db) == (2, 2)

    # 공유 번들을 병합 → 강A는 중복 skip, 강운영은 그대로 보존.
    with db.SessionLocal() as s:
        st = sync.import_bundle(s, tmp / "shared.tar.gz")
    assert st["tests_skipped"] >= 1  # 강A 중복.
    n_mat, n_test = _counts(db)
    assert n_mat == 2 and n_test == 2  # 강운영 삭제 안 됨.
    # 강운영이 실제로 남아있는지 확인.
    from app.models import Material
    with db.SessionLocal() as s:
        assert s.query(Material).filter_by(material_code="OP1").one_or_none() is not None


def test_merge_adds_new_material_from_bundle(env):
    """번들에만 있는 재료는 대상에 추가돼야(union)."""
    M, sync, db, tmp = env["mcp"], env["sync"], env["db"], env["tmp"]
    _register(M, "강A", code="A1")
    _register(M, "강신규", code="NEW1")
    with db.SessionLocal() as s:
        sync.export_bundle(s, tmp / "full.tar.gz")

    # 강신규 삭제(대상엔 강A만).
    with db.SessionLocal() as s:
        from app.models import Material
        m = s.query(Material).filter_by(material_code="NEW1").one()
        M.delete_material(m.id, confirm=True)
    assert _counts(db)[0] == 1

    # 병합 → 강신규 복원(추가), 강A는 skip.
    with db.SessionLocal() as s:
        st = sync.import_bundle(s, tmp / "full.tar.gz")
    assert st["materials_added"] == 1 and st["tests_added"] == 1
    assert _counts(db) == (2, 2)


def test_merge_adds_new_test_to_existing_material(env):
    """같은 재료에 번들이 새 시험을 가져오면 기존 시험 유지 + 새 시험 추가."""
    M, sync, db, tmp = env["mcp"], env["sync"], env["db"], env["tmp"]
    mid, _ = _register(M, "강A", code="A1")
    # 두 번째 시험(다른 곡선) 추가 후 export.
    from tests.fixtures.golden_linear_powerlaw import make_golden
    g2 = make_golden(sigma_y=500e6, n_points=250)
    M.register_tensile_test(mid, g2.strain.tolist(), (g2.stress / 1e6).tolist())
    with db.SessionLocal() as s:
        sync.export_bundle(s, tmp / "two.tar.gz")
    assert _counts(db) == (1, 2)

    # 두 번째 시험만 삭제.
    from app.models import Test
    with db.SessionLocal() as s:
        t2 = s.query(Test).order_by(Test.id.desc()).first()
        M.delete_test(t2.id, confirm=True)
    assert _counts(db) == (1, 1)

    # 병합 → 삭제된 두 번째 시험 복원, 첫 번째는 skip.
    with db.SessionLocal() as s:
        st = sync.import_bundle(s, tmp / "two.tar.gz")
    assert st["tests_added"] == 1 and st["tests_skipped"] == 1
    assert _counts(db) == (1, 2)


def test_property_values_roundtrip_and_idempotent(env):
    """물성값(v2)이 번들 export/import에 포함되고, 재임포트는 멱등(중복 없음)."""
    M, sync, db, tmp = env["mcp"], env["sync"], env["db"], env["tmp"]
    mid, _ = _register(M, "물성강", code="P1")
    r = M.register_property(mid, "thermal.conductivity", value=16.2, unit="W/(m*K)",
                            conditions={"temperature_k": 373}, method="handbook",
                            quality_tier=2, source_doi="10.1000/azom304",
                            source_title="AZoM: SS 304")
    assert r.get("created") is True

    from app.models import PropertyValue
    with db.SessionLocal() as s:
        summ = sync.export_bundle(s, tmp / "p.tar.gz")
    assert summ["property_values"] == 1 and summ["sources"] >= 1
    assert summ["property_definitions"] >= 85  # taxonomy 동봉.

    # 같은 DB 재임포트 → 동일 (material,key,source,conditions) 갱신, 중복 생성 없음.
    with db.SessionLocal() as s:
        st = sync.import_bundle(s, tmp / "p.tar.gz")
        assert st["property_values_added"] == 0 and st["property_values_updated"] == 1
        assert st["sources_added"] == 0  # DOI로 dedup.
        assert s.query(PropertyValue).count() == 1


def test_merge_preserves_operational_property_additions(env, tmp_path, monkeypatch):
    """A 번들(물성 포함)을 B에 병합해도 B의 운영 추가 물성값이 보존된다(union)."""
    M, sync = env["mcp"], env["sync"]
    mid, _ = _register(M, "합금X", code="X1")
    M.register_property(mid, "physical.density", value=8000, unit="kg/m^3",
                        method="handbook", quality_tier=2, source_title="AZoM X")
    with env["db"].SessionLocal() as s:
        sync.export_bundle(s, env["tmp"] / "a.tar.gz")

    # B: 같은 재료(안정키 동일)에 운영이 다른 물성을 추가한 상태로 병합.
    M.register_property(mid, "thermal.conductivity", value=16.2, unit="W/(m*K)",
                        method="handbook", quality_tier=2, source_title="운영추가")
    from app.models import PropertyValue
    with env["db"].SessionLocal() as s:
        before = s.query(PropertyValue).count()
        sync.import_bundle(s, env["tmp"] / "a.tar.gz")
        after = s.query(PropertyValue).count()
        keys = {pv.property_key for pv in s.query(PropertyValue).filter_by(material_id=mid).all()}
    # 번들의 density(재갱신) + 운영추가 conductivity 둘 다 존재(손실 없음).
    assert "physical.density" in keys and "thermal.conductivity" in keys
    assert after >= before  # 운영 추가분 절대 삭제 안 됨.
