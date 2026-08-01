# 화·물리 물성 확장 회귀 — taxonomy 시드·property_value 프로비넌스·MCP 조회/등록.
from __future__ import annotations

import pytest


def test_taxonomy_seeded_on_init(mcp_env):
    M = mcp_env
    defs = M.list_property_definitions()
    keys = {d["key"] for d in defs}
    assert len(defs) >= 85
    # 도메인 대표 물성 존재.
    for k in ("thermal.conductivity", "optical.emissivity_total",
              "chemical.moisture_absorption_equilibrium", "electrical.dielectric_constant"):
        assert k in keys
    # 도메인 필터.
    thermal = M.list_property_definitions(domain="thermal")
    assert thermal and all(d["domain"] == "thermal" for d in thermal)


def test_register_property_with_provenance(mcp_env):
    M = mcp_env
    mid = M.register_material("흡습성폴리머", category="polymer")["material_id"]
    r = M.register_property(
        mid, "chemical.moisture_absorption_equilibrium", value=0.012, unit="1",
        conditions={"humidity_rh": 50, "temperature_k": 296}, method="measured",
        quality_tier=1, source_doi="10.1000/example", source_title="Kim et al. 2020",
        notes="RH50 평형 함수율")
    assert r.get("created") is True, r
    got = M.get_material_properties(mid)
    assert got["n_values"] == 1
    chem = got["domains"]["chemical"][0]
    assert chem["value"] == 0.012 and chem["quality_tier"] == 1
    assert chem["conditions"]["humidity_rh"] == 50
    assert chem["source"]["doi"] == "10.1000/example"


def test_register_property_requires_source_and_valid_key(mcp_env):
    M = mcp_env
    mid = M.register_material("검증재", category="metal")["material_id"]
    # 출처 없음 → 거부.
    assert "error" in M.register_property(mid, "thermal.conductivity", value=1.0)
    # 미정의 key → 거부.
    assert "error" in M.register_property(mid, "thermal.bogus", value=1.0,
                                          source_title="x")
    # 값 없음 → 거부.
    assert "error" in M.register_property(mid, "thermal.conductivity",
                                          source_title="x")


def test_register_property_idempotent(mcp_env):
    M = mcp_env
    mid = M.register_material("멱등재", category="metal")["material_id"]
    a = M.register_property(mid, "thermal.conductivity", value=15.0, unit="W/(m*K)",
                            source_doi="10.1/x", source_title="src")
    b = M.register_property(mid, "thermal.conductivity", value=16.0, unit="W/(m*K)",
                            source_doi="10.1/x", source_title="src")
    assert a["created"] is True and b["created"] is False  # 동일 출처·조건 → 갱신.
    got = M.get_material_properties(mid, domain="thermal")
    assert got["n_values"] == 1 and got["domains"]["thermal"][0]["value"] == 16.0


def test_compare_materials_aligns_and_ranks(mcp_env):
    M = mcp_env
    a = M.register_material("비교재A", category="metal")["material_id"]
    b = M.register_material("비교재B", category="metal")["material_id"]
    # 공통 물성(값 다름) + A 전용 물성.
    M.register_property(a, "thermal.conductivity", value=15.0, unit="W/(m*K)", source_title="srcA")
    M.register_property(b, "thermal.conductivity", value=45.0, unit="W/(m*K)", source_title="srcB")
    M.register_property(a, "physical.density", value=7800, unit="kg/m^3", source_title="srcA")

    r = M.compare_materials(["비교재A", "비교재B"])
    assert [m["name"] for m in r["materials"]] == ["비교재A", "비교재B"]  # 요청 순서 유지.
    assert r["n_properties"] == 2 and r["n_shared"] == 1 and r["rule"]

    shared = [row for row in r["comparison"] if set(row["values"]) == {"비교재A", "비교재B"}]
    assert len(shared) == 1
    row = shared[0]
    assert row["highest"] == "비교재B" and row["lowest"] == "비교재A"  # 값 크기(우열 아님).
    assert row["values"]["비교재A"]["value"] == 15.0 and row["values"]["비교재B"]["value"] == 45.0
    # A 전용 행 — B는 values에 없다.
    a_only = [row for row in r["comparison"] if set(row["values"]) == {"비교재A"}]
    assert any(row["values"]["비교재A"]["value"] == 7800 for row in a_only)


def test_compare_materials_resolves_names_and_requires_two(mcp_env):
    M = mcp_env
    a = M.register_material("단독재", category="metal")["material_id"]
    M.register_property(a, "thermal.conductivity", value=10.0, unit="W/(m*K)", source_title="s")
    # 1개만 → 에러.
    assert "error" in M.compare_materials(["단독재"])
    # 없는 이름 → 해석 실패도 에러.
    assert "error" in M.compare_materials(["단독재", "존재하지않는재료XYZ"])
    # id 정수로도 해석.
    b = M.register_material("상대재", category="metal")["material_id"]
    M.register_property(b, "thermal.conductivity", value=20.0, unit="W/(m*K)", source_title="s")
    r = M.compare_materials([a, b])
    assert len(r["materials"]) == 2 and r["n_shared"] == 1


def test_ashby_data_pairs_and_filters(mcp_env):
    M = mcp_env
    a = M.register_material("애쉬비A", category="metal")["material_id"]
    b = M.register_material("애쉬비B", category="polymer")["material_id"]
    M.register_property(a, "physical.density", value=7800, unit="kg/m^3", source_title="s")
    M.register_property(a, "mechanical.youngs_modulus", value=2.0e11, unit="Pa", source_title="s")
    M.register_property(b, "physical.density", value=1200, unit="kg/m^3", source_title="s")  # b: y 없음.

    r = M.ashby_data("physical.density", "mechanical.youngs_modulus")
    names = {p["name"] for p in r["points"]}
    assert "애쉬비A" in names and "애쉬비B" not in names  # 두 축 모두 있는 재료만.
    pa = next(p for p in r["points"] if p["name"] == "애쉬비A")
    assert pa["x"] == 7800 and pa["y"] == 2.0e11 and pa["category"] == "metal"
    # 잘못된 key → 에러.
    assert "error" in M.ashby_data("physical.density", "bogus.key")


def test_search_catalog_property_ranks_all_domains(mcp_env):
    """흡습률 등 전 도메인 물성으로 검색·랭킹 + 출처(프로비넌스) 노출."""
    M = mcp_env
    a = M.register_material("저흡습재", category="polymer")["material_id"]
    b = M.register_material("고흡습재", category="polymer")["material_id"]
    M.register_property(a, "chemical.water_absorption_24h", value=0.0002, unit="1",
                        source_title="Vendor A datasheet", source_kind="datasheet",
                        source_manufacturer="VendorA", quality_tier=3)
    M.register_property(b, "chemical.water_absorption_24h", value=0.018, unit="1",
                        source_title="Vendor B datasheet", source_kind="datasheet",
                        source_manufacturer="VendorB", quality_tier=3)

    desc = M.search_catalog_property("chemical.water_absorption_24h")
    assert desc["property"]["domain"] == "chemical" and desc["count"] == 2
    assert [r["name"] for r in desc["results"]] == ["고흡습재", "저흡습재"]  # 기본 내림차순.
    assert desc["results"][0]["source"]["manufacturer"] == "VendorB"  # 프로비넌스 노출.

    asc = M.search_catalog_property("chemical.water_absorption_24h", order="asc")
    assert asc["results"][0]["name"] == "저흡습재"
    # 범위 필터.
    only_low = M.search_catalog_property("chemical.water_absorption_24h", max_value=0.001)
    assert [r["name"] for r in only_low["results"]] == ["저흡습재"]
    assert "error" in M.search_catalog_property("bogus.key")


def test_catalog_property_distribution_stats(mcp_env):
    """CTE 등 전 도메인 물성의 재료 간 분포 통계."""
    M = mcp_env
    for name, cte in (("저CTE재", 5e-6), ("중CTE재", 1.7e-5), ("고CTE재", 1.2e-4)):
        mid = M.register_material(name, category="polymer")["material_id"]
        M.register_property(mid, "thermal.expansion_linear", value=cte, unit="1/K",
                            source_title="CTE 기술자료", source_kind="datasheet")
    d = M.catalog_property_distribution("thermal.expansion_linear")
    assert d["n"] == 3 and d["min"] == 5e-6 and d["max"] == 1.2e-4
    assert d["median"] == 1.7e-5
    assert d["highest"][0]["name"] == "고CTE재" and d["lowest"][-1]["name"] == "저CTE재"
    assert "error" in M.catalog_property_distribution("bogus.key")


def test_plot_curves_errors_clearly_without_curves(mcp_env):
    """카탈로그 물성만 있는(곡선 없는) 재료는 멈추지 않고 명확히 알린다."""
    M = mcp_env
    a = M.register_material("곡선없는재A", category="metal")["material_id"]
    M.register_material("곡선없는재B", category="metal")
    M.register_property(a, "physical.density", value=8900, unit="kg/m^3",
                        source_title="handbook", source_kind="book")
    with pytest.raises(ValueError) as e:
        M.plot_curves(materials=["곡선없는재A", "곡선없는재B"])
    assert "인장 곡선 없음" in str(e.value)
