# 단위 정규화·strain 추정·미지단위 보고·빈입력·remap 데이터보존 회귀(적대적 리뷰 라운드3).
from __future__ import annotations

import importlib

import numpy as np
import pytest


@pytest.fixture
def app_env(tmp_path, monkeypatch):
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    from app import config as config_mod
    config_mod.get_settings.cache_clear()
    import app.db as db_mod
    import app.models as models_mod
    import app.curve_store as curve_mod
    import app.ingest as ingest_mod
    db_mod = importlib.reload(db_mod)
    models_mod = importlib.reload(models_mod)
    curve_mod = importlib.reload(curve_mod)
    ingest_mod = importlib.reload(ingest_mod)
    db_mod.init_db()
    yield {"db": db_mod, "models": models_mod, "curve": curve_mod, "ingest": ingest_mod}
    config_mod.get_settings.cache_clear()


def _specimen(models, db, category="metal", w0=0.0125, t0=0.002):
    with db.SessionLocal() as s:
        mat = models.Material(name="X", category=category, attributes={})
        s.add(mat); s.commit()
        spec = models.Specimen(material_id=mat.id, label="S1", geometry_type="flat",
                               gauge_length_m=0.05, width_m=w0, thickness_m=t0, area0_m2=w0 * t0)
        s.add(spec); s.commit()
        return spec.id


# ── #3: N/mm²(=MPa) 정규화 — Zwick/DIN 표준 응력 단위 ────────────────────────
def test_stress_n_per_mm2_is_mpa(app_env):
    ing, models, db = app_env["ingest"], app_env["models"], app_env["db"]
    sid = _specimen(models, db)
    # Strain(무단위 소변형) + Stress(N/mm²) 컬럼 직접.
    lines = ["Strain,Stress", ",N/mm²"]
    for e in np.linspace(0, 0.02, 60):
        lines.append(f"{e:.6f},{200000 * e:.4f}")  # E=200000 MPa 기울기
    with db.SessionLocal() as s:
        spec = s.get(models.Specimen, sid)
        res = ing.ingest_upload(s, spec, "\n".join(lines).encode(), "s.csv")
        assert res.computed, [i.code for i in res.issues]
        E = res.processed_result.youngs_modulus_pa
        # N/mm²가 MPa로 인식되면 E≈2e11 Pa. factor=1.0이면 2e5로 1e6배 축소.
        assert 1.9e11 < E < 2.1e11, f"E={E:.3e} (N/mm²→MPa 변환 실패)"


# ── #3: 미지 단위는 WARN으로 보고(무음 금지) ─────────────────────────────────
def test_unknown_unit_reported(app_env):
    ing, models, db = app_env["ingest"], app_env["models"], app_env["db"]
    sid = _specimen(models, db)
    lines = ["Strain,Stress", ",furlong"]  # 미등록 단위
    for e in np.linspace(0, 0.02, 60):
        lines.append(f"{e:.6f},{200000 * e:.4f}")
    with db.SessionLocal() as s:
        spec = s.get(models.Specimen, sid)
        res = ing.ingest_upload(s, spec, "\n".join(lines).encode(), "s.csv")
        assert any(i.code == "unknown_unit" for i in res.issues), [i.code for i in res.issues]


# ── #2: 고무 대변형(비 2.0)을 %로 오변환하지 않음 ─────────────────────────────
def test_rubber_large_strain_not_downscaled(app_env):
    ing, models, db = app_env["ingest"], app_env["models"], app_env["db"]
    sid = _specimen(models, db, category="rubber")
    # 무단위 strain 최대 2.0(=200% 연신), stress MPa.
    strains = np.linspace(0, 2.0, 80)
    lines = ["Strain,Stress", ",MPa"]
    for e in strains:
        lines.append(f"{e:.6f},{5.0 * e:.4f}")
    with db.SessionLocal() as s:
        spec = s.get(models.Specimen, sid)
        res = ing.ingest_upload(s, spec, "\n".join(lines).encode(), "r.csv")
        df = app_env["curve"].read_curve(res.test.id)
        # /100 오변환되면 최대 변형률이 0.02가 됨 — 2.0에 가까워야 정상.
        assert float(np.nanmax(df["eng_strain"])) > 1.5


def test_metal_percent_strain_still_autoscaled(app_env):
    # 금속은 무단위 %추정(>1.5)이 유지돼야 한다(회귀 방지).
    ing, models, db = app_env["ingest"], app_env["models"], app_env["db"]
    sid = _specimen(models, db, category="metal")
    lines = ["Strain,Stress", ",MPa"]
    for e in np.linspace(0, 20, 60):  # 0~20(%로 기록)
        lines.append(f"{e:.6f},{e * 10:.4f}")
    with db.SessionLocal() as s:
        spec = s.get(models.Specimen, sid)
        res = ing.ingest_upload(s, spec, "\n".join(lines).encode(), "m.csv")
        df = app_env["curve"].read_curve(res.test.id)
        assert float(np.nanmax(df["eng_strain"])) < 1.0  # 20% → 0.2
        assert any(i.code == "strain_autoscaled_percent" for i in res.issues)


# ── #4: compute_all 빈 입력 graceful ─────────────────────────────────────────
def test_compute_all_empty_graceful():
    from app import analysis
    m = analysis.compute_all(np.array([]), np.array([]))
    assert m["youngs_modulus_pa"] is None
    assert m["uts_pa"] is None
    assert m["extra_metrics"]["yield_reason"] == "no_data"


# ── #1: remap 실패 시 원본 데이터 보존 ───────────────────────────────────────
def test_remap_failure_preserves_original(app_env):
    from fastapi.testclient import TestClient
    import app.routers.uploads as up
    import app.routers.materials as rm
    import app.routers.specimens as rs
    import app.routers.properties as rp
    import app.routers as pkg
    import app.main as main_mod
    for m in (up, rm, rs, rp, pkg, main_mod):
        importlib.reload(m)
    ing, models, db, curve = app_env["ingest"], app_env["models"], app_env["db"], app_env["curve"]

    sid = _specimen(models, db)
    # 유효한 원본 적재.
    lines = ["Strain,Stress [MPa]"]
    for e in np.linspace(0, 0.02, 80):
        lines.append(f"{e:.6f},{200000 * e:.4f}")
    with db.SessionLocal() as s:
        spec = s.get(models.Specimen, sid)
        res = ing.ingest_upload(s, spec, "\n".join(lines).encode(), "orig.csv")
        tid = res.test.id
        assert res.computed
    assert curve.curve_path(tid).exists()

    client = TestClient(main_mod.create_app())
    # 쓰레기 파일 + 아무 매핑으로 remap → 실패해야 하고 원본은 살아있어야 함.
    r = client.post(f"/api/uploads/{tid}/mapping",
                    files={"file": ("junk.csv", b"\x00\x01garbage\xff", "text/csv")},
                    data={"mapping": "{}"})
    assert r.status_code == 422, r.text
    # 원본 test·곡선 보존.
    with db.SessionLocal() as s:
        assert s.get(models.Test, tid) is not None
    assert curve.curve_path(tid).exists()
