# API 통합 테스트 — health·재료/시편 생성·골든 업로드→물성 E·곡선 다운샘플·삭제 정리·FK CASCADE.
from __future__ import annotations

import importlib
import io

import pytest
from fastapi.testclient import TestClient

from tests.fixtures.golden_linear_powerlaw import make_golden


@pytest.fixture
def client(tmp_path, monkeypatch):
    """DATA_DIR/DATABASE_URL을 tmp로 격리하고 모듈 재로딩 후 TestClient를 만든다.

    config가 lru_cache라 캐시를 비우고 settings를 참조하는 하위 모듈을 재임포트한다.
    """
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{db_file}")

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

    # 라우터/메인은 위 재로딩된 모듈을 참조하도록 재임포트.
    import app.routers.materials as r_materials
    import app.routers.specimens as r_specimens
    import app.routers.uploads as r_uploads
    import app.routers.properties as r_properties
    import app.routers as routers_pkg
    import app.main as main_mod

    importlib.reload(r_materials)
    importlib.reload(r_specimens)
    importlib.reload(r_uploads)
    importlib.reload(r_properties)
    importlib.reload(routers_pkg)
    importlib.reload(main_mod)

    app = main_mod.create_app()
    with TestClient(app) as c:
        c._db = db_mod  # 파일 경로 검증용 핸들.
        yield c

    config_mod.get_settings.cache_clear()


def _golden_csv_bytes():
    g = make_golden()
    lines = ["Strain,Stress [MPa]"]
    for e, s in zip(g.strain, g.stress):
        lines.append(f"{e:.8f},{s / 1e6:.6f}")
    return ("\n".join(lines)).encode("utf-8"), g


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_full_flow_material_specimen_upload_properties(client):
    # 재료 생성.
    r = client.post(
        "/api/materials",
        json={"name": "GoldenSteel", "category": "metal", "attributes": {}},
    )
    assert r.status_code == 201, r.text
    mid = r.json()["id"]

    # 목록 q 검색.
    r = client.get("/api/materials", params={"q": "Golden"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1 and len(body["items"]) == 1

    # 시편 생성(area0 미입력 → 형상 산출).
    r = client.post(
        f"/api/materials/{mid}/specimens",
        json={
            "label": "S1",
            "geometry_type": "flat",
            "gauge_length_m": 0.050,
            "width_m": 0.0125,
            "thickness_m": 0.003,
        },
    )
    assert r.status_code == 201, r.text
    sid = r.json()["id"]
    assert abs(r.json()["area0_m2"] - 0.0125 * 0.003) < 1e-12

    # 골든 CSV 업로드 → 적재.
    csv_bytes, g = _golden_csv_bytes()
    r = client.post(
        f"/api/specimens/{sid}/uploads",
        files={"file": ("golden.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert r.status_code == 201, r.text
    up = r.json()
    assert up["computed"] is True, up
    tid = up["test_id"]

    # 시편의 시험 목록.
    r = client.get(f"/api/specimens/{sid}/tests")
    assert r.status_code == 200 and len(r.json()) == 1

    # GET properties → E 반환(±2%).
    r = client.get(f"/api/tests/{tid}/properties")
    assert r.status_code == 200, r.text
    E = r.json()["youngs_modulus_pa"]
    assert E is not None
    rel = abs(E - g.E_true_pa) / g.E_true_pa
    assert rel <= 0.02, f"E rel err {rel:.4%}"

    # 곡선 다운샘플 길이 확인.
    r = client.get(f"/api/tests/{tid}/curve", params={"kind": "nominal", "max_points": 500})
    assert r.status_code == 200, r.text
    curve = r.json()
    assert curve["n_returned"] <= 500
    assert curve["n_total"] > 1000
    assert len(curve["x"]) == curve["n_returned"]

    # CSV 다운로드 + Content-Disposition filename*.
    r = client.get(f"/api/tests/{tid}/curve.csv")
    assert r.status_code == 200
    cd = r.headers["content-disposition"]
    assert "filename*=UTF-8''" in cd
    assert "eng_stress_Pa" in r.text.splitlines()[0]

    # properties:compute 재계산(옵션 e_range).
    r = client.post(
        f"/api/tests/{tid}/properties:compute",
        json={"e_range": [0.0005, 0.0025], "offset": 0.002, "toe": True},
    )
    assert r.status_code == 200, r.text
    assert r.json()["youngs_modulus_pa"] is not None

    # PATCH valid 토글.
    r = client.patch(f"/api/tests/{tid}", json={"valid": False, "invalid_reason": "outlier"})
    assert r.status_code == 200 and r.json()["valid"] is False

    # DELETE test → Parquet도 삭제.
    import app.curve_store as cs

    cs_path = cs.curve_path(tid)
    assert cs_path.exists()
    r = client.delete(f"/api/tests/{tid}")
    assert r.status_code == 204
    assert not cs_path.exists()
    r = client.get(f"/api/tests/{tid}")
    assert r.status_code == 404


def test_parsers_and_sniff(client):
    r = client.get("/api/parsers")
    assert r.status_code == 200
    names = [p["name"] for p in r.json()["parsers"]]
    assert "generic_csv" in names
    assert "strain" in r.json()["roles"]

    csv_bytes, _ = _golden_csv_bytes()
    r = client.post(
        "/api/uploads/sniff",
        files={"file": ("golden.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert r.status_code == 200
    assert r.json()["confidence"] > 0.0
    assert r.json()["specimen"]["n_rows"] > 1000


def test_fk_cascade_material_delete(client):
    import app.curve_store as cs

    # 재료→시편→업로드까지 만든 뒤 재료 삭제 시 하위 전부 삭제 + 곡선 파일 정리.
    r = client.post("/api/materials", json={"name": "M", "category": "metal", "attributes": {}})
    mid = r.json()["id"]
    r = client.post(
        f"/api/materials/{mid}/specimens",
        json={
            "label": "S1",
            "geometry_type": "round",
            "gauge_length_m": 0.050,
            "diameter_m": 0.006,
        },
    )
    sid = r.json()["id"]
    csv_bytes, _ = _golden_csv_bytes()
    r = client.post(
        f"/api/specimens/{sid}/uploads",
        files={"file": ("g.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    tid = r.json()["test_id"]

    # 재료 삭제(cascade).
    r = client.delete(f"/api/materials/{mid}")
    assert r.status_code == 204

    # 하위 전부 사라짐.
    assert client.get(f"/api/materials/{mid}").status_code == 404
    assert client.get(f"/api/specimens/{sid}").status_code == 404
    assert client.get(f"/api/tests/{tid}").status_code == 404

    db = client._db
    with db.SessionLocal() as session:
        from app.models import ProcessedResult, RawCurveRef, Test

        assert session.get(Test, tid) is None
        assert session.query(RawCurveRef).filter_by(test_id=tid).one_or_none() is None
        assert session.query(ProcessedResult).filter_by(test_id=tid).one_or_none() is None
