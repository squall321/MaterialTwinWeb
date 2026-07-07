# 인사이트 회귀 — 재료 클래스 분류·통계·Ashby 물성공간·커버리지 갭·지식그래프.
from __future__ import annotations

import importlib

import pytest

from app import insights


# ── 분류기 ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("name,cat,expected_family", [
    ("SUS304_annealed Bilinear", "metal", "steel"),
    ("SUS_17-4PH_H900 Bilinear", "metal", "steel"),
    ("Al7075-T6 Bilinear", "metal", "aluminum"),
    ("Ti6Al4V_Grade5 Bilinear", "metal", "titanium"),
    ("Mg_AZ31B_H24 Bilinear", "metal", "magnesium"),
    ("Inconel_718_aged Bilinear", "metal", "nickel"),
    ("C36000_Brass Bilinear", "metal", "copper"),
    ("Tungsten_99pct Bilinear", "metal", "refractory"),
    ("NBR Cushion Rubber", "polymer", "elastomer"),
    ("PORON SR-S Soft Foam", "polymer", "foam"),
    ("OCA Rigid Standard", "polymer", "adhesive"),
    ("EAR Isodamp C-1002", "polymer", "damping"),
])
def test_classify(name, cat, expected_family):
    _cls, family = insights.classify(name, cat)
    assert family == expected_family


# ── 집계 (시드된 DB 필요) ──────────────────────────────────────────────────
def _seed(tmp_path, monkeypatch, n_ep=10, n_vi=6):
    """test_ingest와 동일한 재로딩 패턴 + insights도 재로딩(모델 참조 갱신)."""
    from pathlib import Path
    dbj = Path("/home/koopark/claude/KooRemapper/materials/material_db.json")
    if not dbj.exists():
        pytest.skip("material_db.json 없음")
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{tmp_path / 't.db'}")
    from app import config as c
    c.get_settings.cache_clear()
    import app.db as db, app.models as m, app.curve_store as cs, app.ingest as ing
    import app.seed as seed, app.insights as ins
    for mod in (db, m, cs, ing, seed, ins):
        importlib.reload(mod)
    db.init_db()
    with db.SessionLocal() as s:
        seed.run(s, dbj, max_elastoplastic=n_ep, max_viscoelastic=n_vi)
    return db, ins, c


def test_overview_and_stats(tmp_path, monkeypatch):
    db, ins, c = _seed(tmp_path, monkeypatch)
    with db.SessionLocal() as s:
        ov = ins.overview(s)
        assert ov["total_materials"] >= 10
        assert "Stainless Steel" in ov["by_class"] or "Aluminum Alloy" in ov["by_class"]
        st = ins.property_stats(s)
        assert st["E_gpa"]["n"] >= 5
        assert st["E_gpa"]["min"] <= st["E_gpa"]["max"]
        assert len(st["uts_mpa"]["hist"]) == 12
    c.get_settings.cache_clear()


def test_property_space_and_coverage(tmp_path, monkeypatch):
    db, ins, c = _seed(tmp_path, monkeypatch)
    with db.SessionLocal() as s:
        ps = ins.property_space(s)
        assert len(ps["points"]) >= 5
        assert all("E_gpa" in p and "uts_mpa" in p for p in ps["points"])
        cg = ins.coverage_gaps(s)
        assert any(c_["status"] == "rich" for c_ in cg["coverage"])
        # 지식그래프: root + 카테고리 + 계열 노드.
        assert len(cg["graph"]["nodes"]) >= 3
        assert len(cg["graph"]["edges"]) >= 2
        assert any(n["id"] == "root" for n in cg["graph"]["nodes"])
    c.get_settings.cache_clear()
