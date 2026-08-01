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
