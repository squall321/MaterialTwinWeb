# 화·물리 물성 확장 회귀 — taxonomy 시드·property_value 프로비넌스·MCP 조회/등록.
from __future__ import annotations


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
