# 점탄성 분석·시드러 회귀 — Prony 완화·피팅·카드 + KooRemapper 재구성 적재.
from __future__ import annotations

import importlib
from pathlib import Path

import numpy as np
import pytest

from app import viscoelastic


# ── 점탄성 모듈 ────────────────────────────────────────────────────────────
def test_shear_relaxation_endpoints():
    # G(0)=G0, G(∞)→Ginf.
    assert abs(viscoelastic.shear_relaxation(5.0, 0.1, 5.0, np.array([0.0]))[0] - 5.0) < 1e-9
    assert abs(viscoelastic.shear_relaxation(5.0, 0.1, 5.0, np.array([100.0]))[0] - 0.1) < 1e-6


def test_youngs_from_shear():
    # E=2G(1+ν). ν=0.5 → E=3G.
    assert abs(viscoelastic.youngs_from_shear(10.0, 0.5) - 30.0) < 1e-9


def test_relaxation_curve_and_prony_fit():
    rc = viscoelastic.relaxation_curve_from_lsdyna(G0=5.0, Ginf=0.1, beta=5.0, nu=0.45)
    assert rc["E0_pa"] > rc["Einf_pa"] > 0
    fit = viscoelastic.fit_prony(rc["time_s"], rc["E_pa"], n_terms=3)
    assert fit["E_inf_pa"] is not None
    assert fit["r2"] > 0.9  # 완화곡선을 잘 적합.
    assert len(fit["terms"]) >= 1


def test_mat_viscoelastic_card():
    txt = viscoelastic.mat_viscoelastic_card("Rubber", 1.1e-9, 2000.0, 5.0, 0.1, 5.0)
    assert "*MAT_VISCOELASTIC" in txt
    assert "*END" in txt
    assert "Rubber" in txt


# ── 시드러 (실제 KooRemapper DB가 있을 때만) ───────────────────────────────
_DB_JSON = Path("/home/koopark/claude/KooRemapper/materials/material_db.json")


@pytest.mark.skipif(not _DB_JSON.exists(), reason="KooRemapper material_db.json 없음")
def test_seed_reconstructs_real_materials(tmp_path, monkeypatch):
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{tmp_path / 't.db'}")
    from app import config as c
    c.get_settings.cache_clear()
    import app.db as db, app.models as m, app.curve_store as cs, app.ingest as ing, app.seed as seed
    for mod in (db, m, cs, ing, seed):
        importlib.reload(mod)
    db.init_db()

    with db.SessionLocal() as s:
        r = seed.run(s, _DB_JSON, max_elastoplastic=6, max_viscoelastic=4)
        assert r["elastoplastic"] >= 3
        assert r["viscoelastic"] >= 2
        # 탄소성: E가 원본 E_GPa와 근접(재구성 곡선에서 역산).
        t = s.query(m.Test).filter_by(test_type="tensile").first()
        pr = s.query(m.ProcessedResult).filter_by(test_id=t.id).one()
        orig = t.specimen.material.attributes.get("E_GPa")
        if orig:
            assert abs(pr.youngs_modulus_pa / 1e9 - orig) / orig < 0.05
        # 피팅이 저장됨.
        assert s.query(m.ConstitutiveFit).filter_by(test_id=t.id).count() >= 1
        # 점탄성: extra_metrics.kind == viscoelastic.
        vt = s.query(m.Test).filter_by(test_type="relaxation").first()
        vpr = s.query(m.ProcessedResult).filter_by(test_id=vt.id).one()
        assert vpr.extra_metrics["kind"] == "viscoelastic"
        assert vpr.extra_metrics["E0_pa"] > vpr.extra_metrics["Einf_pa"] > 0
    c.get_settings.cache_clear()
