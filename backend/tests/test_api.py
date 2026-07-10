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


def _make_material_specimen_test(client, mat_name="P2Steel", label="S1"):
    """재료+시편+골든 업로드 후 (mid, sid, tid) 반환. Phase2/3 엔드포인트 셋업용."""
    r = client.post("/api/materials", json={"name": mat_name, "category": "metal", "attributes": {}})
    mid = r.json()["id"]
    r = client.post(
        f"/api/materials/{mid}/specimens",
        json={"label": label, "geometry_type": "flat", "gauge_length_m": 0.05,
              "width_m": 0.0125, "thickness_m": 0.003},
    )
    sid = r.json()["id"]
    csv_bytes, _g = _golden_csv_bytes()
    r = client.post(
        f"/api/specimens/{sid}/uploads",
        files={"file": ("golden.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    return mid, sid, r.json()["test_id"]


def test_true_stress_curve_endpoint(client):
    _mid, _sid, tid = _make_material_specimen_test(client)
    r = client.get(f"/api/tests/{tid}/curve", params={"kind": "true", "max_points": 300})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "true"
    assert body["x_label"] == "true_strain"
    assert body["n_returned"] <= 300
    # 진응력 > 공칭응력(넥킹 전) 성질: 마지막 진응력 y가 양수.
    assert body["y"][-1] > 0
    assert "necking" in body


def test_fits_and_card_endpoints(client):
    _mid, _sid, tid = _make_material_specimen_test(client)
    # 물성 먼저 계산(카드 export 전제).
    client.post(f"/api/tests/{tid}/properties:compute", json={})

    # 피팅 계산.
    r = client.post(f"/api/tests/{tid}/fits:compute")
    assert r.status_code == 200, r.text
    fits = r.json()["fits"]
    models = {f["model"] for f in fits}
    assert {"hollomon", "swift", "voce", "johnson_cook"} == models

    # 조회.
    r = client.get(f"/api/tests/{tid}/fits")
    assert r.status_code == 200
    assert len(r.json()["fits"]) >= 1

    # LS-DYNA 카드 다운로드.
    r = client.get(f"/api/tests/{tid}/card.k")
    assert r.status_code == 200, r.text
    assert "*MAT_PIECEWISE_LINEAR_PLASTICITY" in r.text
    assert "filename*=UTF-8''" in r.headers["content-disposition"]


def test_card_units_and_johnson_cook(client):
    _mid, _sid, tid = _make_material_specimen_test(client)
    client.post(f"/api/tests/{tid}/properties:compute", json={})

    # 기본(ton_mm_s) 카드 파일명·단위계 확인.
    r = client.get(f"/api/tests/{tid}/card.k")
    assert r.status_code == 200, r.text
    assert "ton, mm, s" in r.text
    assert "ton_mm_s" in r.headers["content-disposition"]

    # SI 단위계 전환.
    r = client.get(f"/api/tests/{tid}/card.k?units=kg_m_s")
    assert r.status_code == 200
    assert "kg, m, s" in r.text
    assert "kg_m_s" in r.headers["content-disposition"]

    # Johnson-Cook(*MAT_098) 모델.
    r = client.get(f"/api/tests/{tid}/card.k?model=johnson_cook")
    assert r.status_code == 200, r.text
    assert "*MAT_SIMPLIFIED_JOHNSON_COOK" in r.text
    assert "MAT098_JC" in r.headers["content-disposition"]

    # 미지원 단위계·모델 → 422.
    assert client.get(f"/api/tests/{tid}/card.k?units=bogus").status_code == 422
    assert client.get(f"/api/tests/{tid}/card.k?model=bogus").status_code == 422


def test_card_rejects_invalid_youngs_modulus(client):
    # E가 유효하지 않으면(음수/NaN) 카드 export가 422로 거부(무효 솔버카드 방지).
    _mid, _sid, tid = _make_material_specimen_test(client)
    client.post(f"/api/tests/{tid}/properties:compute", json={})
    # processed_result.youngs_modulus_pa를 음수로 오염시켜 방어 확인.
    db = client._db
    with db.SessionLocal() as session:
        from app.models import ProcessedResult

        pr = session.query(ProcessedResult).filter_by(test_id=tid).one()
        pr.youngs_modulus_pa = -1.0e7
        session.commit()
    r = client.get(f"/api/tests/{tid}/card.k")
    assert r.status_code == 422, r.text


def test_material_stats_mean_std(client):
    # 같은 재료에 시편 2개 업로드 → 통계 n=2.
    mid, _sid1, _t1 = _make_material_specimen_test(client, mat_name="StatSteel", label="S1")
    # 두 번째 시편.
    r = client.post(
        f"/api/materials/{mid}/specimens",
        json={"label": "S2", "geometry_type": "flat", "gauge_length_m": 0.05,
              "width_m": 0.0125, "thickness_m": 0.003},
    )
    sid2 = r.json()["id"]
    csv_bytes, _g = _golden_csv_bytes()
    client.post(f"/api/specimens/{sid2}/uploads",
                files={"file": ("g2.csv", io.BytesIO(csv_bytes), "text/csv")})

    r = client.get(f"/api/materials/{mid}/stats")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["n_specimens"] == 2
    ym = body["stats"]["youngs_modulus_pa"]
    assert ym["n"] == 2 and ym["mean"] is not None
    # 동일 곡선 2개 → std ≈ 0.
    assert ym["std"] is not None and ym["std"] < ym["mean"] * 0.01


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
    assert cs.curve_path(tid).exists()

    # 재료 삭제(cascade).
    r = client.delete(f"/api/materials/{mid}")
    assert r.status_code == 204
    assert not cs.curve_path(tid).exists()  # Parquet 곡선 파일도 정리(C4).

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
