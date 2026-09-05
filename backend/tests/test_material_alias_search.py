# 규격 표기(별칭)로도 재료가 찾아지는지 — 64차 ZC 가 잰 97개 중 92개 미스를 막는 회귀시험.
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """DATA_DIR/DATABASE_URL 을 tmp 로 격리하고 모듈 재로딩 후 TestClient 를 만든다."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{db_file}")

    from app import config as config_mod

    config_mod.get_settings.cache_clear()

    import app.db as db_mod
    import app.models as models_mod

    importlib.reload(db_mod)
    importlib.reload(models_mod)

    import app.routers.materials as r_materials
    import app.routers as routers_pkg
    import app.main as main_mod

    importlib.reload(r_materials)
    importlib.reload(routers_pkg)
    importlib.reload(main_mod)

    app = main_mod.create_app()
    with TestClient(app) as c:
        c._db, c._models = db_mod, models_mod
        yield c

    config_mod.get_settings.cache_clear()


def _add(client, name: str, attributes: dict) -> int:
    m = client._models.Material(name=name, category="metal", attributes=attributes)
    with client._db.SessionLocal() as s:
        s.add(m)
        s.commit()
        return m.id


def _ids(client, q: str) -> list[int]:
    r = client.get("/api/materials", params={"q": q})
    assert r.status_code == 200
    return [x["id"] for x in r.json()["items"]]


def test_alias_finds_material_whose_name_uses_another_notation(client):
    """이름에 없는 규격 표기로도 찾아야 한다.

    실사용에서 `7075-T651` 로 찾아 값 4개짜리 레코드에 걸리고 값 53개짜리를 놓쳤다.
    """
    mid = _add(client, "Al7075-T6 Bilinear", {"aliases": ["7075-T651", "AA7075-T651"]})

    assert _ids(client, "7075-T651") == [mid]
    assert _ids(client, "AA7075-T651") == [mid]
    assert _ids(client, "Al7075-T6") == [mid]          # 이름 경로도 그대로 산다


def test_alias_match_does_not_leak_into_other_attribute_keys(client):
    """attributes 를 통째로 훑으면 안 된다 — 판정문 산문이 걸린다.

    `core_absent_from_vendor_sheet` 같은 사유는 긴 한국어 문장이라 등급명을 그대로 담는다.
    그것까지 잡히면 "이 재료에 그 값이 없다" 는 문장이 "그 재료다" 로 뒤집힌다.
    """
    _add(client, "Some Other Laminate",
         {"core_absent_from_vendor_sheet": {"physical.density": "7075-T651 시트에는 이 열이 없다"}})

    assert _ids(client, "7075-T651") == []


def test_alias_absent_is_not_an_error(client):
    """별칭이 없는 재료가 대부분이다 — json_extract 가 NULL 이어도 죽지 않아야 한다."""
    mid = _add(client, "Plain Material", {})

    assert _ids(client, "Plain") == [mid]
    assert _ids(client, "없는이름") == []
