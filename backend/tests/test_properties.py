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


def test_ratio_properties_stay_dimensionless(mcp_env):
    """무차원(1) 물성은 비율로 저장 — 퍼센트 오입력(예: 72 대신 0.72) 방지 가드.

    실제로 파단연신율에 %값이 섞여 비교표·Ashby가 100배 왜곡된 사고가 있었다.
    금속·플라스틱 연신율이 1.5(=150%)를 넘으면 단위 오입력을 의심해야 한다.
    """
    M = mcp_env
    mid = M.register_material("연신율재", category="metal")["material_id"]
    M.register_property(mid, "mechanical.elongation_at_break", value=0.39, unit="1",
                        source_title="ASM Handbook", source_kind="book", quality_tier=2)
    got = M.search_catalog_property("mechanical.elongation_at_break")
    v = got["results"][0]["value"]
    assert 0 < v <= 1.5, f"금속 연신율이 비율 범위를 벗어남(퍼센트 오입력 의심): {v}"
    # 정의 단위가 무차원인지도 함께 확인.
    assert got["property"]["unit"] == "1"


def test_export_dyna_cards_bulk_and_units(mcp_env):
    """재료 리스트 → LS-DYNA 덱: MID 자동배정·유사매칭·단위변환·고정폭 불변식."""
    M = mcp_env
    a = M.register_material("덱강재", category="metal")["material_id"]
    src = dict(source_title="ASM Handbook", source_kind="book", quality_tier=2, method="handbook")
    M.register_property(a, "physical.density", value=7850, unit="kg/m^3", **src)
    M.register_property(a, "mechanical.youngs_modulus", value=2.0e11, unit="Pa", **src)
    M.register_property(a, "mechanical.poisson_ratio", value=0.3, unit="1", **src)
    M.register_property(a, "mechanical.yield_strength", value=2.5e8, unit="Pa", **src)
    M.register_property(a, "thermal.specific_heat", value=460, unit="J/(kg*K)", **src)
    M.register_property(a, "thermal.conductivity", value=45, unit="W/(m*K)", **src)
    b = M.register_material("덱폴리머", category="polymer")["material_id"]
    M.register_property(b, "physical.density", value=1200, unit="kg/m^3", **src)
    M.register_property(b, "mechanical.youngs_modulus", value=3.0e9, unit="Pa", **src)

    r = M.export_dyna_cards(["덱강재", "덱폴리머"], card="both", units="ton_mm_s")
    assert [t["mid"] for t in r["materials"]] == [1, 2]          # MID 순차 자동배정.
    kw = r["keyword"]
    assert "*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE" in kw        # 항복 있음 → 024.
    assert "*MAT_ELASTIC_TITLE" in kw                            # 항복 없음 → 001.
    assert "*MAT_THERMAL_ISOTROPIC_TITLE" in kw
    assert "ASM Handbook" in kw                                  # 출처 주석.
    # 단위변환: ton_mm_s에서 밀도 7850 kg/m^3 → 7.85e-9, E 200 GPa → 2.0e5 MPa.
    assert "7.8500e-9" in kw and "2.0000e+5" in kw
    # 열: 비열 460 J/(kg*K) → 4.6e8 (mm^2/s^2/K), 열전도 45 → 45 유지.
    assert "4.6000e+8" in kw

    # 물성 부족은 조용히 기본값으로 채우지 않고 보고한다.
    assert any(s["material"] == "덱폴리머" and s["card"] == "thermal" for s in r["skipped"])

    # 고정폭 불변식 — 데이터 행의 모든 필드는 정확히 10칸.
    for line in kw.splitlines():
        if line and not line.startswith(("$", "*")) and line.startswith(" "):
            assert len(line) % 10 == 0, f"10칸 배수 아님: {line!r}"

    # SI 단위계로 바꾸면 E가 Pa 원값으로 나온다.
    si = M.export_dyna_cards(["덱강재"], card="mechanical", units="kg_m_s")
    assert "2.0000e+11" in si["keyword"]


def test_export_dyna_cards_cte_with_part_ids(mcp_env):
    """PID를 주면 CTE 카드(*MAT_ADD_THERMAL_EXPANSION + *DEFINE_CURVE)를 만든다."""
    M = mcp_env
    a = M.register_material("팽창재", category="metal")["material_id"]
    src = dict(source_title="ASM Handbook", source_kind="book", quality_tier=2, method="handbook")
    M.register_property(a, "physical.density", value=7850, unit="kg/m^3", **src)
    M.register_property(a, "mechanical.youngs_modulus", value=2.0e11, unit="Pa", **src)
    M.register_property(a, "thermal.expansion_linear", value=1.2e-5, unit="1/K", **src)

    # MID 101, PART 5·6·7이 같은 재료를 쓰는 경우.
    r = M.export_dyna_cards(["101, 5;6;7, 팽창재"], card="mechanical")
    kw = r["keyword"]
    assert kw.count("*MAT_ADD_THERMAL_EXPANSION") == 3      # PART마다 1장.
    assert kw.count("*DEFINE_CURVE_TITLE") == 1             # 곡선은 재료당 1개 공유.
    assert [p["pid"] for p in r["parts"]] == [5, 6, 7]
    assert len({p["lcid"] for p in r["parts"]}) == 1        # 동일 LCID 공유.
    assert all(p["cte"] == 1.2e-5 for p in r["parts"])
    assert "1.2000e-5" in kw                                # CTE는 1/K이라 단위변환 없음.

    # PID 없으면 CTE 카드도 없다(PART 단위 카드이므로).
    r2 = M.export_dyna_cards(["101, 팽창재"], card="mechanical")
    assert "*MAT_ADD_THERMAL_EXPANSION" not in r2["keyword"]
    assert r2["parts"] == []

    # CTE 물성이 없는 재료에 PID를 주면 조용히 넘기지 않고 보고한다.
    b = M.register_material("팽창미상재", category="metal")["material_id"]
    M.register_property(b, "physical.density", value=1000, unit="kg/m^3", **src)
    M.register_property(b, "mechanical.youngs_modulus", value=1.0e9, unit="Pa", **src)
    r3 = M.export_dyna_cards(["102, 9, 팽창미상재"], card="mechanical")
    assert any(s["card"] == "thermal_expansion" for s in r3["skipped"])


def test_export_dyna_cards_fuzzy_name_and_mid_start(mcp_env):
    """이름만 줘도 유사검색으로 찾고, mid_start부터 번호를 매긴다."""
    M = mcp_env
    mid = M.register_material("SUS304_annealed Bilinear", category="metal")["material_id"]
    src = dict(source_title="handbook", source_kind="book", quality_tier=2, method="handbook")
    M.register_property(mid, "physical.density", value=8000, unit="kg/m^3", **src)
    M.register_property(mid, "mechanical.youngs_modulus", value=1.93e11, unit="Pa", **src)

    r = M.export_dyna_cards(["SUS304"], card="mechanical", mid_start=101)
    assert r["materials"][0]["mid"] == 101
    assert r["materials"][0]["name"] == "SUS304_annealed Bilinear"
    assert r["materials"][0]["matched_by"].startswith(("substring", "fuzzy"))
    # 없는 이름은 정직하게 보고.
    r2 = M.export_dyna_cards(["존재하지않는재료XYZ"], card="mechanical")
    assert "error" in r2 or r2["resolution_errors"]


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
