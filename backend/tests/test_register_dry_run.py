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
    # **plain import 로는 모델이 등록되지 않는다** — 앞선 테스트가 `app.models` 를 이미
    # 임포트해 두면 sys.modules 에 있어 그 줄이 무의미하고, 클래스는 **옛 Base** 에 묶인 채
    # 남는다. `reload(_db)` 가 만든 새 Base 는 표가 0개라 `create_all` 이 아무것도 안 만들고
    # `no such table: material` 로 죽는다(단독 실행은 통과하고 전체 스위트에서만 깨졌다).
    # **낡은 Base 에 묶여 있을 때만** 다시 읽는다. 무조건 reload 하면 반대로 깨진다 —
    # 이 파일만 단독 실행하면 바로 위 import 가 새 Base 에 표를 갓 등록한 참이라
    # reload 가 같은 metadata 에 표를 두 번 정의하려다 죽는다.
    import app.models
    if app.models.Material.metadata is not _db.Base.metadata:
        importlib.reload(app.models)
    _db.Base.metadata.create_all(_db.engine)
    # mcp_server 도 옛 세션·옛 모델 클래스를 들고 있다. 새 임시 DB 를 보게 다시 읽는다.
    if "mcp_server" in sys.modules:
        importlib.reload(sys.modules["mcp_server"])
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
