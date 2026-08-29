# 대표값 옆 "다른 후보가 있다" 노출의 회귀 고정 — 목록·비교·Ashby·상세가 이 한 모듈에 달려 있다.
#
# 이 파일이 있는 이유(51차 MB). 선택기는 (재료,물성키)당 한 행만 낸다. 라이브 41,368행에서
# 후보가 둘 이상인 쌍이 6,330개이고 그중 3,642쌍은 순위가 같은데 값이 1% 넘게 다르다(§545).
# **값을 고치거나 순위를 더 만들지 않고**(§543·544) 진 쪽을 같이 내보내는 것이 이 코드의 일이다.
# 그래서 이 테스트가 지키는 것은 두 가지다 — **아무 행도 감추지 않는다** ·
# **기존 응답 필드를 하나도 빼지 않는다**.
from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest

from app import catalog_alternatives as CA


def _pv(pid, key="mechanical.youngs_modulus", tier=1, value=1.0, cond=None,
        method="measured", text=None, unit="Pa"):
    return SimpleNamespace(id=pid, material_id=1, property_key=key, quality_tier=tier,
                           value_num=value, value_text=text, unit=unit, conditions=cond,
                           method=method, source=None)


# ── 왜 갈렸는가 ────────────────────────────────────────────────────────────
def test_separated_by_names_the_rank_slot_that_decided():
    """진 이유는 순위 튜플이 처음 갈리는 자리다 — 등급·조건수·(아무것도 아님=적재 순서)."""
    rep = _pv(1, tier=1)
    assert CA.separated_by(rep, _pv(2, tier=3)) == "tier"
    assert CA.separated_by(rep, _pv(2, tier=1, cond={"direction": "z"})) == "n_conditions"
    # 순위가 완전히 같으면 남는 것은 id 뿐이다 — 즉 적재 순서.
    assert CA.separated_by(rep, _pv(2, tier=1)) == "load_order"


def test_separated_by_says_wavelength_for_optical_keys():
    """광학의 지배조건은 온도가 아니라 파장이다(`_rep_rank` 와 같은 갈래)."""
    rep = _pv(1, key="optical.refractive_index", cond={"wavelength_nm": 589.3})
    alt = _pv(2, key="optical.refractive_index", cond={"wavelength_nm": 1550.0})
    assert CA.separated_by(rep, alt) == "wavelength"
    rep2 = _pv(1, cond={"temperature_C": 23.0})
    alt2 = _pv(2, cond={"temperature_C": 200.0})
    assert CA.separated_by(rep2, alt2) == "temperature"


def test_condition_diff_reports_only_the_columns_that_differ():
    """사용자가 스스로 고르려면 "무엇이 다른가" 가 필요하다 — 같은 칸은 소음이다."""
    rep = _pv(1, cond={"direction": "in-plane", "temperature_C": 23.0})
    alt = _pv(2, cond={"direction": "through-thickness", "temperature_C": 23.0})
    d = CA.condition_diff(rep, alt)
    assert d == {"direction": {"rep": "in-plane", "alt": "through-thickness"}}


def test_condition_diff_clips_long_values_for_list_like_responses():
    rep = _pv(1, cond={"note": "x" * 200})
    alt = _pv(2, cond={"note": "y" * 200})
    d = CA.condition_diff(rep, alt, clip=40)
    assert len(d["note"]["rep"]) == 40 and d["note"]["rep"].endswith("…")


def test_alternative_payload_does_not_copy_the_whole_condition_dict():
    """조건 사본을 통째로 실으면 비교 응답이 +81% 로 뛴다 — 다른 칸만 싣는다."""
    rep = _pv(1, cond={"direction": "in-plane", "temperature_C": 23.0})
    alt = _pv(2, cond={"direction": "z", "temperature_C": 23.0})
    out = CA.alternative_payload(rep, alt)
    assert "conditions" not in out
    assert out["condition_diff"] == {"direction": {"rep": "in-plane", "alt": "z"}}
    assert out["value"] == 1.0 and out["tier"] == 1


# ── 동률의 갈래 ────────────────────────────────────────────────────────────
def test_tie_info_is_none_when_the_selector_did_its_job():
    """등급이 가르면 동률이 아니다. 반올림 쌍둥이도 동률로 세지 않는다."""
    assert CA.tie_info(CA.rank_group([_pv(1, tier=1, value=2e11), _pv(2, tier=4, value=1.6e11)])) is None
    assert CA.tie_info(CA.rank_group([_pv(1, value=7850.0), _pv(2, value=7855.0)])) is None


def test_tie_kind_condition_axis_when_the_rows_differ_in_a_condition():
    """라이브 동률 3,642쌍 중 3,213쌍이 이 갈래다 — 선택기에 그 축이 없는 것이다."""
    t = CA.tie_info(CA.rank_group([_pv(1, value=2.0e10, cond={"direction": "in-plane"}),
                                   _pv(2, value=2.0e9, cond={"direction": "z"})]))
    assert t["kind"] == "condition_axis"
    assert t["n_tied"] == 2 and t["condition_keys"] == ["direction"]
    assert t["max_rel_diff"] > 0.5


def test_tie_kind_multi_term_when_one_key_holds_several_terms():
    """Prony·Anand·JC 파괴상수는 한 키에 여러 항이 산다 — 대표값 자체가 뜻이 없다(§545)."""
    t = CA.tie_info(CA.rank_group([_pv(1, value=0.02, cond={"term": "D1"}),
                                   _pv(2, value=16.9, cond={"term": "D2"})]))
    assert t["kind"] == "multi_term"


def test_tie_kind_indistinguishable_is_the_only_true_load_order_pick():
    """조건 차이조차 없을 때만 "적재 순서로 골랐다" 가 맞는 말이다 — 라이브에서 35쌍뿐이다."""
    t = CA.tie_info(CA.rank_group([_pv(1, value=2.0e11), _pv(2, value=1.6e11)]))
    assert t["kind"] == "indistinguishable"


# ── 엔드포인트 ─────────────────────────────────────────────────────────────
@pytest.fixture
def cat(mcp_env):
    """mcp_env 가 app.models 를 재로딩하므로 카탈로그 라우터도 다시 묶어야 한다."""
    import app.routers.catalog as rc

    importlib.reload(rc)
    return rc


def _three_rival_moduli(M, name="대안재"):
    mid = M.register_material(name, category="metal")["material_id"]
    for val, direction, src in ((2.0e10, "in-plane", "Ref A"),
                                (2.0e9, "through-thickness", "Ref B"),
                                (1.5e10, "45deg", "Ref C")):
        M.register_property(mid, "mechanical.youngs_modulus", value=val, unit="Pa",
                            quality_tier=1, conditions={"direction": direction},
                            source_title=src, source_kind="journal")
    return mid


def test_detail_marks_the_representative_and_hides_no_row(mcp_env, cat):
    """상세는 전 행을 그대로 낸다 — 빠져 있던 것은 "어느 것이 대표값인가" 였다."""
    from app.db import SessionLocal

    mid = _three_rival_moduli(mcp_env)
    with SessionLocal() as s:
        d = cat.catalog_material_detail(mid, s)
    rows = [r for r in d["domains"]["mechanical"] if r["key"] == "mechanical.youngs_modulus"]
    assert len(rows) == 3, "값을 한 행도 감추면 안 된다"
    assert sum(1 for r in rows if r["representative"]) == 1
    assert {r["n_candidates"] for r in rows} == {3}
    losers = [r for r in rows if not r["representative"]]
    assert all(r["separated_by"] == "load_order" for r in losers)
    assert d["alternatives"]["keys"] == 1 and d["alternatives"]["ties"] == 1


def test_detail_puts_the_tie_only_on_the_representative_row(mcp_env, cat):
    """같은 경고를 형제 행마다 반복하면 소음이 된다(49차 KA) — 대표행에만 붙인다."""
    from app.db import SessionLocal

    mid = _three_rival_moduli(mcp_env)
    with SessionLocal() as s:
        d = cat.catalog_material_detail(mid, s)
    rows = [r for r in d["domains"]["mechanical"] if r["key"] == "mechanical.youngs_modulus"]
    tied = [r for r in rows if r["tie"]]
    assert len(tied) == 1 and tied[0]["representative"]
    assert tied[0]["tie"]["kind"] == "condition_axis"
    assert tied[0]["tie"]["condition_keys"] == ["direction"]


def test_detail_keeps_the_old_row_fields(mcp_env, cat):
    """필드를 더하되 빼지 마라 — 프런트가 쓰고 있다."""
    from app.db import SessionLocal

    mid = _three_rival_moduli(mcp_env)
    with SessionLocal() as s:
        d = cat.catalog_material_detail(mid, s)
    r = d["domains"]["mechanical"][0]
    for k in ("key", "name", "symbol", "value", "value_text", "unit", "uncertainty",
              "conditions", "method", "tier", "standard", "notes", "source"):
        assert k in r


def test_compare_cell_carries_the_alternatives_and_why(mcp_env, cat):
    from app.db import SessionLocal

    M = mcp_env
    a = _three_rival_moduli(M, "대안재A")
    b = M.register_material("대안재B", category="metal")["material_id"]
    M.register_property(b, "mechanical.youngs_modulus", value=7.0e10, unit="Pa",
                        quality_tier=1, source_title="Ref D", source_kind="journal")
    with SessionLocal() as s:
        c = cat.compare(f"{a},{b}", s)
    cell = next(cell for dom in c["domains"] for p in dom["properties"]
                if p["key"] == "mechanical.youngs_modulus"
                for cell in p["cells"] if cell and cell["material_id"] == a)
    assert cell["n_candidates"] == 3
    assert len(cell["alternatives"]) == 2
    assert cell["tie"]["kind"] == "condition_axis"
    alt = cell["alternatives"][0]
    assert alt["separated_by"] == "load_order"
    assert "direction" in alt["condition_diff"]
    # 기존 칸 필드는 그대로다.
    for k in ("material_id", "value", "value_text", "unit", "tier", "method",
              "conditions", "source"):
        assert k in cell


def test_compare_leaves_single_candidate_cells_untouched(mcp_env, cat):
    """후보가 하나뿐인 칸에 `n_candidates:1` 을 깔면 12종 비교가 눈에 띄게 무거워진다."""
    from app.db import SessionLocal

    M = mcp_env
    a = M.register_material("단일재A", category="metal")["material_id"]
    b = M.register_material("단일재B", category="metal")["material_id"]
    for mid, v in ((a, 7850.0), (b, 2700.0)):
        M.register_property(mid, "physical.density", value=v, unit="kg/m^3",
                            quality_tier=1, source_title="Ref", source_kind="journal")
    with SessionLocal() as s:
        c = cat.compare(f"{a},{b}", s)
    cells = [cell for dom in c["domains"] for p in dom["properties"]
             for cell in p["cells"] if cell]
    assert cells and all("n_candidates" not in cell for cell in cells)


def test_ashby_point_flags_candidates_only_when_there_is_a_choice(mcp_env, cat):
    from app.db import SessionLocal

    M = mcp_env
    a = _three_rival_moduli(M, "애쉬비재A")
    M.register_property(a, "physical.density", value=7850.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref", source_kind="journal")
    b = M.register_material("애쉬비재B", category="metal")["material_id"]
    for key, v, u in (("physical.density", 2700.0, "kg/m^3"),
                      ("mechanical.youngs_modulus", 7.0e10, "Pa")):
        M.register_property(b, key, value=v, unit=u, quality_tier=1,
                            source_title="Ref", source_kind="journal")
    with SessionLocal() as s:
        data = cat.ashby("physical.density", "mechanical.youngs_modulus", s)
    pa = next(p for p in data["points"] if p["material_id"] == a)
    pb = next(p for p in data["points"] if p["material_id"] == b)
    assert pa["y_candidates"] == 3 and pa["y_tie"] is True
    assert "x_candidates" not in pa and "x_tie" not in pa
    assert "y_candidates" not in pb and "y_tie" not in pb


def test_material_list_reports_candidate_count_but_not_values(mcp_env, cat):
    """목록은 **수만** 낸다 — 2,654행 응답에 값까지 실으면 배로 뛴다."""
    from app.db import SessionLocal

    mid = _three_rival_moduli(mcp_env)
    with SessionLocal() as s:
        out = cat.catalog_materials(
            q=None, subsystem=None, category=None, manufacturer=None, material_class=None,
            domain=None, prop="mechanical.youngs_modulus", prop_min=None, prop_max=None,
            sort="properties", db=s)
    row = next(r for r in out["items"] if r["id"] == mid)
    assert row["prop_candidates"] == 3 and row["prop_tie"] is True
    assert "alternatives" not in row and "prop_alternatives" not in row


def test_mcp_compare_shows_alternatives_and_keeps_plain_cells_plain(mcp_env):
    """MCP 비교도 같은 사실을 봐야 한다 — 다만 평범한 칸의 형태는 그대로 둔다."""
    M = mcp_env
    a = _three_rival_moduli(M, "MCP대안재A")
    b = M.register_material("MCP대안재B", category="metal")["material_id"]
    M.register_property(a, "physical.density", value=7850.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref", source_kind="journal")
    M.register_property(b, "physical.density", value=2700.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref", source_kind="journal")
    M.register_property(b, "mechanical.youngs_modulus", value=7.0e10, unit="Pa",
                        quality_tier=1, source_title="Ref", source_kind="journal")
    r = M.compare_materials(["MCP대안재A", "MCP대안재B"])
    e = next(row for row in r["comparison"] if row["property"].startswith("영률")
             or "modulus" in row["property"].lower() or row["symbol"] == "E")
    assert e["values"]["MCP대안재A"]["candidates"] == 3
    assert e["values"]["MCP대안재A"]["tie"]["kind"] == "condition_axis"
    rho = next(row for row in r["comparison"] if row["domain"] == "physical")
    assert "candidates" not in rho["values"]["MCP대안재B"]


def test_mcp_property_search_counts_candidates_without_shipping_values(mcp_env):
    M = mcp_env
    mid = _three_rival_moduli(M, "MCP검색재")
    r = M.search_catalog_property("mechanical.youngs_modulus")
    row = next(x for x in r["results"] if x["material_id"] == mid)
    assert row["n_candidates"] == 3 and row["tie"] is True
    assert "alternatives" not in row
