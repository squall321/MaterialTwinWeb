# 시험장비 API 테스트 — 빈 상태·능력 등록·기법 묶음·측정공백·적재기 거부규칙.
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{db_file}")

    from app import config as config_mod

    config_mod.get_settings.cache_clear()

    import app.db as db_mod
    import app.models as models_mod

    importlib.reload(db_mod)
    importlib.reload(models_mod)

    import app.routers.metrology as r_metrology
    import app.routers as routers_pkg
    import app.main as main_mod

    importlib.reload(r_metrology)
    importlib.reload(routers_pkg)
    importlib.reload(main_mod)

    app = main_mod.create_app()
    with TestClient(app) as c:
        c._dbfile = db_file
        yield c

    config_mod.get_settings.cache_clear()


def test_empty_state(client):
    """장비가 없어도 엔드포인트가 살아 있고, 모든 물성이 '잴 장비 없음'으로 나온다."""
    s = client.get("/api/metrology/summary").json()
    assert s["instruments"] == 0 and s["total_properties"] > 100

    cov = client.get("/api/metrology/coverage").json()
    assert cov["measurable"] == 0
    assert cov["total"] == s["total_properties"]
    assert len(cov["gaps"]) == cov["total"]


def test_by_property_unknown_key_404(client):
    assert client.get("/api/metrology/by-property/thermal.nonexistent").status_code == 404


def _insert(dbfile, caps):
    import sqlite3

    c = sqlite3.connect(dbfile)
    c.execute(
        "insert into instrument(vendor,model,category,technique) "
        "values('NETZSCH','LFA 457','thermal','레이저 플래시법')"
    )
    iid = c.execute("select last_insert_rowid()").fetchone()[0]
    for k, tech, std in caps:
        c.execute(
            "insert into instrument_capability(instrument_id,property_key,technique,"
            "standard,mapping_confidence) values(?,?,?,?,'high')",
            (iid, k, tech, std),
        )
    c.commit()
    return iid


def test_techniques_are_grouped(client):
    """같은 물성을 두 기법으로 재면 **기법으로 묶여** 나온다 — 장비 목록이 아니라 방법이 답이다."""
    _insert(client._dbfile, [
        ("thermal.conductivity", "레이저 플래시법", "ASTM E1461"),
        ("thermal.conductivity", "핫디스크(TPS)법", "ISO 22007-2"),
        ("thermal.diffusivity", "레이저 플래시법", "ASTM E1461"),
    ])
    r = client.get("/api/metrology/by-property/thermal.conductivity").json()
    techs = {t["technique"] for t in r["techniques"]}
    assert techs == {"레이저 플래시법", "핫디스크(TPS)법"}
    for t in r["techniques"]:
        assert t["standards"]  # 규격은 모아서 낸다.

    cov = client.get("/api/metrology/coverage").json()
    assert cov["measurable"] == 2
    assert all(g["key"] != "thermal.conductivity" for g in cov["gaps"])


def test_instruments_filter_by_property(client):
    _insert(client._dbfile, [("thermal.diffusivity", "레이저 플래시법", "ASTM E1461")])
    assert client.get(
        "/api/metrology/instruments", params={"property_key": "thermal.diffusivity"}
    ).json()["count"] == 1
    assert client.get(
        "/api/metrology/instruments", params={"property_key": "mechanical.poisson_ratio"}
    ).json()["count"] == 0


# ── 적재기 거부 규칙 — 값 수집과 같은 규율이 장비 사양에도 걸린다 ──────────────
def _run_ingest(dbfile, doc, tmp_path):
    f = tmp_path / "chunk_01.json"
    f.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    script = Path(__file__).resolve().parents[1] / "scripts/catalog/ingest_instrument_json.py"
    out = subprocess.run(
        [sys.executable, str(script), str(f)],
        capture_output=True, text=True, env={"MATERIALTWIN_DB": str(dbfile), "PATH": "/usr/bin:/bin"},
    )
    return out.stdout


def _doc(cap: dict) -> dict:
    return {"instruments": [{
        "vendor": "V", "model": "M", "category": "thermal",
        "capabilities": [{"property_key": "thermal.conductivity",
                          "technique": "레이저 플래시법", **cap}],
    }]}


def test_ingest_rejects_range_without_unit(client, tmp_path):
    """**범위는 단위와 함께가 아니면 값이 아니다.**"""
    out = _run_ingest(client._dbfile, _doc({"range_min": 0.1, "range_max": 2000}), tmp_path)
    assert "범위에 단위 없음" in out and "능력 0" in out


def test_ingest_rejects_inverted_range(client, tmp_path):
    out = _run_ingest(
        client._dbfile, _doc({"range_min": 100, "range_max": 1, "range_unit": "W/(m*K)"}), tmp_path
    )
    assert "범위 역전" in out


def test_ingest_accepts_open_upper_bound(client, tmp_path):
    """`up to 1100 °C` 처럼 **상한만** 인쇄된 것은 정상이다 — 하한을 지어내지 않는다."""
    out = _run_ingest(client._dbfile, _doc({"range_max": 2000, "range_unit": "W/(m*K)"}), tmp_path)
    assert "능력 1" in out and "거부 0" in out


def test_ingest_rejects_unknown_property_key(client, tmp_path):
    doc = _doc({})
    doc["instruments"][0]["capabilities"][0]["property_key"] = "thermal.made_up"
    assert "미정의 키" in _run_ingest(client._dbfile, doc, tmp_path)
