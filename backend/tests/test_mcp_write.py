# MCP 쓰기 도구 검증 — 등록(인장·점탄성)·수정·삭제·재계산 왕복 + 검증 에러 경로.
from __future__ import annotations

import numpy as np
import pytest

from tests.fixtures.golden_linear_powerlaw import make_golden


# ── 재료 등록 ────────────────────────────────────────────────────────────────
def test_register_material_roundtrip(mcp_env):
    M = mcp_env
    r = M.register_material("MCP강재", category="metal", material_code="MCP-T1",
                            description="테스트")
    assert "error" not in r
    got = M.get_material(r["material_id"])
    assert got["name"] == "MCP강재" and got["category"] == "metal"


def test_register_material_validation(mcp_env):
    M = mcp_env
    assert "error" in M.register_material("", category="metal")
    assert "error" in M.register_material("x", category="unobtainium")
    M.register_material("a", material_code="DUP-1")
    assert "이미 존재" in M.register_material("b", material_code="DUP-1")["error"]


# ── 인장시험 등록: 골든 곡선 → 물성 정확도 + 피팅 + 카드 ────────────────────
def test_register_tensile_golden_accuracy(mcp_env):
    M = mcp_env
    g = make_golden(n_points=1000)
    mid = M.register_material("골든강", category="metal")["material_id"]
    r = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())
    assert "error" not in r, r
    p = r["properties"]
    assert p["E_GPa"] == pytest.approx(200.0, rel=0.01)
    assert p["UTS_MPa"] == pytest.approx(g.uts_true_pa / 1e6, rel=0.01)
    assert len(r["fits"]) >= 3  # Hollomon/Voce/JC 등 대부분 수렴.

    # 곡선 파일이 실제로 존재.
    assert M._test_curve_store.curve_path(r["test_id"]).exists()

    # 조회 왕복: 곡선·피팅·카드.
    c = M.get_curve(r["test_id"], kind="nominal", max_points=50)
    assert c["n"] > 10
    card = M.get_mat_card(r["test_id"])
    assert "*MAT_PIECEWISE_LINEAR_PLASTICITY" in card
    jc = M.get_mat_card(r["test_id"], model="johnson_cook")
    assert "*MAT_SIMPLIFIED_JOHNSON_COOK" in jc


def test_register_tensile_validation(mcp_env):
    M = mcp_env
    mid = M.register_material("검증용", category="metal")["material_id"]
    ok_strain = list(np.linspace(0, 0.1, 30))
    assert "없음" in M.register_tensile_test(999, ok_strain, [100.0] * 30)["error"]
    assert "길이" in M.register_tensile_test(mid, ok_strain, [100.0] * 29)["error"]
    assert "적습니다" in M.register_tensile_test(mid, [0.01] * 5, [100.0] * 5)["error"]
    # % 단위 착오(무차원이어야 함).
    assert "무차원" in M.register_tensile_test(mid, list(np.linspace(0, 15, 30)), [100.0] * 30)["error"]
    # NaN 방어.
    bad = ok_strain.copy(); bad[3] = float("nan")
    assert "NaN" in M.register_tensile_test(mid, bad, [100.0] * 30)["error"]


# ── 점탄성 등록: Prony 파라미터 모드 + 실측 곡선 모드 ────────────────────────
def test_register_relaxation_prony_mode(mcp_env):
    M = mcp_env
    mid = M.register_material("댐핑고무", category="rubber")["material_id"]
    G0, GI, beta, nu = 1.2, 0.3, 20.0, 0.45
    r = M.register_relaxation_test(mid, G0_mpa=G0, Ginf_mpa=GI, beta_per_s=beta, nu=nu,
                                   bulk_mpa=2000.0, rho_t_mm3=1.1e-9)
    assert "error" not in r, r
    # E = 2G(1+ν) 관계 검증.
    assert r["E0_MPa"] == pytest.approx(2 * G0 * (1 + nu), rel=0.01)
    assert r["Einf_MPa"] == pytest.approx(2 * GI * (1 + nu), rel=0.01)
    assert r["tau_s"] == pytest.approx(1.0 / beta, rel=0.01)

    card = M.get_mat_card(r["test_id"])
    assert "*MAT_VISCOELASTIC" in card
    c = M.get_curve(r["test_id"], kind="relaxation")
    assert c["n"] > 10

    # list_materials가 점탄성으로 분류.
    row = next(m for m in M.list_materials() if m["id"] == mid)
    assert row["kind"] == "viscoelastic"


def test_register_relaxation_curve_mode(mcp_env):
    M = mcp_env
    mid = M.register_material("실측고무", category="polymer")["material_id"]
    t = np.logspace(-3, 2, 40)
    Et = 30 + 270 * np.exp(-t / 0.5)  # MPa
    r = M.register_relaxation_test(mid, time_s=t.tolist(), modulus_mpa=Et.tolist())
    assert "error" not in r, r
    assert r["prony_r2"] > 0.95
    assert "*MAT_VISCOELASTIC" in M.get_mat_card(r["test_id"])


def test_register_relaxation_validation(mcp_env):
    M = mcp_env
    mid = M.register_material("검증고무", category="rubber")["material_id"]
    assert "입력 부족" in M.register_relaxation_test(mid)["error"]
    assert "error" in M.register_relaxation_test(mid, G0_mpa=0.3, Ginf_mpa=1.2, beta_per_s=10)  # G0<GI
    assert "error" in M.register_relaxation_test(mid, G0_mpa=1.0, Ginf_mpa=0.1, beta_per_s=10, nu=0.7)


# ── 곡선 kind 불일치 — 예외가 아니라 error dict(정찰 회귀 케이스) ────────────
def test_get_curve_wrong_kind_error_dict(mcp_env):
    M = mcp_env
    g = make_golden(n_points=200)
    mid = M.register_material("종류검증", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    r = M.get_curve(tid, kind="relaxation")
    assert "error" in r  # KeyError 크래시가 아니어야 함.


# ── 수정·삭제·재계산 ─────────────────────────────────────────────────────────
def test_update_material(mcp_env):
    M = mcp_env
    mid = M.register_material("수정전", category="metal")["material_id"]
    r = M.update_material(mid, name="수정후", description="d")
    assert r["name"] == "수정후"
    assert "error" in M.update_material(mid, category="bogus")
    M.register_material("코드보유", material_code="CODE-X")
    assert "이미 존재" in M.update_material(mid, material_code="CODE-X")["error"]


def test_delete_material_confirm_and_parquet_cleanup(mcp_env):
    M = mcp_env
    g = make_golden(n_points=200)
    mid = M.register_material("삭제대상", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    path = M._test_curve_store.curve_path(tid)
    assert path.exists()

    # confirm 없으면 미리보기만 — 아무것도 안 지워짐.
    prev = M.delete_material(mid)
    assert "preview" in prev and path.exists()

    r = M.delete_material(mid, confirm=True)
    assert r["tests_removed"] == 1
    assert not path.exists()  # Parquet 정리 확인.
    assert "error" in M.get_material(mid)


def test_delete_test_parquet_cleanup(mcp_env):
    M = mcp_env
    g = make_golden(n_points=200)
    mid = M.register_material("시험삭제", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    path = M._test_curve_store.curve_path(tid)
    assert "preview" in M.delete_test(tid)
    M.delete_test(tid, confirm=True)
    assert not path.exists()
    # 재료는 남아 있어야 함.
    assert "error" not in M.get_material(mid)


# ── 적대적 리뷰 회귀 케이스 ──────────────────────────────────────────────────
def test_relaxation_ginf_zero_card_not_distorted(mcp_env):
    # GI=0(완전 완화)이 falsy 폴백(or 0.1)에 잡혀 카드가 왜곡되면 안 됨.
    M = mcp_env
    mid = M.register_material("맥스웰고무", category="rubber")["material_id"]
    r = M.register_relaxation_test(mid, G0_mpa=1.0, Ginf_mpa=0.0, beta_per_s=10.0)
    assert "error" not in r, r
    card = M.get_mat_card(r["test_id"])
    data = [ln for ln in card.splitlines() if ln.strip() and not ln.startswith(("$", "*"))][0]
    gi = float(data.split()[4])
    assert gi == pytest.approx(0.0, abs=1e-12)  # 0.1로 둔갑하면 실패.


def test_relaxation_non_decaying_curve_rejected(mcp_env):
    # 증가형 곡선(비감쇠)은 크래시가 아니라 한국어 error dict.
    M = mcp_env
    mid = M.register_material("비감쇠", category="polymer")["material_id"]
    t = [0.0] * 6 + list(np.linspace(1, 5, 5))
    Et = list(np.linspace(10, 100, 11))  # 증가형
    r = M.register_relaxation_test(mid, time_s=t, modulus_mpa=Et)
    assert "error" in r and "완화 거동" in r["error"]


def test_tensile_rubber_large_strain_allowed(mcp_env):
    # 엘라스토머는 연신 200% 초과가 정상 — 카테고리별 상한.
    M = mcp_env
    mid = M.register_material("고연신고무", category="rubber")["material_id"]
    en = np.linspace(0, 4.0, 60)  # 400% 연신
    st = 0.5 + 2.0 * en  # MPa
    r = M.register_tensile_test(mid, en.tolist(), st.tolist())
    assert "error" not in r, r
    # 금속은 같은 곡선이 거부되어야 함.
    mid2 = M.register_material("금속검증", category="metal")["material_id"]
    assert "무차원" in M.register_tensile_test(mid2, en.tolist(), st.tolist())["error"]


def test_recompute_half_window_rejected(mcp_env):
    M = mcp_env
    g = make_golden(n_points=200)
    mid = M.register_material("반쪽창", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    r = M.recompute_properties(tid, e_min=0.0005)  # e_max 누락 — 조용히 무시 금지.
    assert "error" in r and "함께" in r["error"]


def test_tensile_sparse_curve_correction_guarded(mcp_env):
    # 성긴 곡선(500점)에서 저항복 자동보정이 좁은 창 2점 회귀로 E를 망치면 안 됨(PG 검증 회귀).
    M = mcp_env
    g = make_golden(n_points=500)
    mid = M.register_material("성긴곡선", category="metal")["material_id"]
    r = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())
    assert r["properties"]["E_GPa"] == pytest.approx(200.0, rel=0.01), r
    assert len(r["fits"]) >= 3


def test_write_curve_failure_rolls_back_specimen(mcp_env, monkeypatch):
    # 곡선 저장 실패 시 자동 생성 시편이 고아로 남으면 안 됨.
    M = mcp_env
    g = make_golden(n_points=200)
    mid = M.register_material("롤백검증", category="metal")["material_id"]
    monkeypatch.setattr(M.curve_store, "write_curve",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("disk full")))
    r = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())
    assert "error" in r and "곡선 저장 실패" in r["error"]
    got = M.get_material(mid)
    assert got["specimens"] == []  # 시편·시험 모두 롤백.


# ── 동시성 회귀 (라운드5) ────────────────────────────────────────────────────
def test_specimen_label_unique_and_retry(mcp_env):
    # (material_id,label) UNIQUE + _add_specimen 재시도로 라벨이 항상 유일해야 한다.
    M = mcp_env
    g = make_golden(n_points=200)
    mid = M.register_material("라벨경합", category="metal")["material_id"]
    for _ in range(4):
        r = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())
        assert "error" not in r
    got = M.get_material(mid)
    labels = [sp["label"] for sp in got["specimens"]]
    assert len(labels) == len(set(labels)) == 4  # 중복 없음.

    # 직접 UNIQUE 위반 시도 → IntegrityError(조용한 중복 아님).
    from sqlalchemy.exc import IntegrityError
    from app.models import Specimen
    with M._test_db.SessionLocal() as s:
        s.add(Specimen(material_id=mid, label=labels[0], geometry_type="flat",
                       gauge_length_m=0.05, width_m=0.0125, thickness_m=0.002, area0_m2=2.5e-5))
        raised = False
        try:
            s.commit()
        except IntegrityError:
            raised = True
        assert raised


def test_recompute_upsert_no_pr_idempotent(mcp_env):
    # 곡선은 있으나 pr이 없는 test에 recompute — INSERT 경로가 UNIQUE 경합에도 안전.
    M = mcp_env
    g = make_golden(n_points=300)
    mid = M.register_material("업서트", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    # pr 삭제해 INSERT 경로 강제.
    from app.models import ProcessedResult
    with M._test_db.SessionLocal() as s:
        s.query(ProcessedResult).filter_by(test_id=tid).delete()
        s.commit()
    r = M.recompute_properties(tid)
    assert "error" not in r and r["properties"]["E_GPa"] is not None


def test_recompute_properties_window(mcp_env):
    M = mcp_env
    g = make_golden(n_points=500)
    mid = M.register_material("재계산", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    r = M.recompute_properties(tid, e_min=0.0004, e_max=0.0012)
    assert "error" not in r
    assert r["properties"]["E_GPa"] == pytest.approx(200.0, rel=0.01)
    assert "error" in M.recompute_properties(tid, e_min=0.5, e_max=0.1)  # 역전 범위.
