# register_* dry_run 이 실경로와 동치이고 저장하지 않음을 강제한다.
# 이 테스트가 깨지면 dry_run 분기 로직이 실경로와 드리프트한 것이다(둘은 같은 물리를 써야 한다).
import sys
from pathlib import Path

import numpy as np
import pytest

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path))
    import importlib
    import app.config as cfg
    importlib.reload(cfg)
    import app.db as _db
    importlib.reload(_db)
    import app.models  # noqa: F401 — 모델 등록
    _db.Base.metadata.create_all(_db.engine)
    return _db


def _rows(db):
    from app.models import Material, Test
    with db.SessionLocal() as s:
        return s.query(Material).count(), s.query(Test).count()


def _synthetic_tensile():
    E, sy = 200e3, 250.0
    en = np.linspace(0, 0.15, 300)
    sp = np.where(en < sy / E, E * en, sy + 400 * (en - sy / E) ** 0.5)
    return en.tolist(), sp.tolist()


def test_register_material_dry_run_persists_nothing(db):
    import mcp_server as M
    before = _rows(db)
    r = M.register_material("dry재료", "polymer", dry_run=True)
    assert r.get("dry_run") is True and r.get("error") is None
    assert _rows(db) == before


def test_tensile_dry_run_equals_real_and_no_write(db):
    import mcp_server as M
    mid = M.register_material("검증재료", "metal")["material_id"]
    strain, stress = _synthetic_tensile()
    before = _rows(db)
    dry = M.register_tensile_test(mid, strain, stress, dry_run=True)
    assert _rows(db) == before  # dry_run 은 저장하지 않는다
    real = M.register_tensile_test(mid, strain, stress, dry_run=False)
    norm = lambda r: (r.get("properties"), r.get("fits"), r.get("warnings"))
    assert norm(dry) == norm(real)  # 물성·피팅·경고 완전 일치
    assert "test_id" not in dry


def test_relaxation_dry_run_equals_real_and_no_write(db):
    import mcp_server as M
    mid = M.register_material("점탄성재료", "rubber")["material_id"]
    t = np.linspace(0.01, 100, 60)
    Et = 200 + 800 * np.exp(-t / 10.0)
    before = _rows(db)
    dry = M.register_relaxation_test(mid, time_s=t.tolist(), modulus_mpa=Et.tolist(), dry_run=True)
    assert _rows(db) == before
    real = M.register_relaxation_test(mid, time_s=t.tolist(), modulus_mpa=Et.tolist(), dry_run=False)
    key = lambda r: (r.get("E0_MPa"), r.get("Einf_MPa"), r.get("tau_s"), r.get("prony_r2"))
    assert key(dry) == key(real)
