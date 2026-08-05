# DYNA 카드의 출처 표기 회귀 — 값과 출처가 같은 행에서 와야 하고, 참고문헌으로 추적 가능해야 한다.
from __future__ import annotations

import re

from app import dyna_export as D
from app.unit_systems import get_system


def test_unit_labels_are_derived_per_system():
    """열 물성 주석의 단위 라벨이 단위계마다 맞게 조립되는지."""
    assert D.hc_unit(get_system("ton_mm_s")) == "mm^2/(s^2*K)"
    assert D.tc_unit(get_system("ton_mm_s")) == "tonne*mm/(s^3*K)"
    assert D.hc_unit(get_system("kg_m_s")) == "m^2/(s^2*K)"
    assert D.tc_unit(get_system("g_mm_ms")) == "g*mm/(ms^3*K)"


def test_clip_does_not_cut_mid_word():
    s = "ASM Metals Handbook Properties and Selection Nonferrous Alloys"
    out = D._clip(s, 40)
    assert len(out) <= 41 and out.endswith("…")
    assert not out[:-1].endswith(" ")
    # 마지막 토큰이 온전한 단어여야 한다(잘린 조각이 아니라).
    assert out[:-1].split()[-1] in s.split()


def test_clip_collapses_whitespace():
    assert D._clip("PI Base Film   —  Kapton", 60) == "PI Base Film — Kapton"


def test_card_cites_references_and_lists_them(mcp_env):
    """주석의 [n]이 실제 참고문헌 항목을 가리켜야 한다 — 안 그러면 추적이 끊긴다."""
    M = mcp_env
    mid = M.register_material(name="TestSteel", category="metal")["material_id"]
    for key, val, unit, src in (
        ("physical.density", 7850.0, "kg/m^3", "Ref A"),
        ("mechanical.youngs_modulus", 2.0e11, "Pa", "Ref A"),
        ("mechanical.poisson_ratio", 0.3, "1", "Ref B"),
        ("thermal.specific_heat", 460.0, "J/(kg*K)", "Ref B"),
        ("thermal.conductivity", 50.0, "W/(m*K)", "Ref C"),
    ):
        M.register_property(mid, key, value=val, unit=unit, quality_tier=1,
                            source_title=src, source_kind="datasheet",
                            source_manufacturer="Vendor")
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        deck = DX.build_cards(s, ["1, TestSteel"], card="both", units="ton_mm_s")
    txt = deck["keyword"]
    cited = set(int(x) for x in re.findall(r"<- \[(\d+)\]", txt))
    listed = set(int(x) for x in re.findall(r"^\$ \[(\d+)\]", txt, re.M))
    assert cited, "출처 인용이 하나도 없다"
    assert cited <= listed, f"참고문헌에 없는 번호를 인용한다: {cited - listed}"


def test_bulk_modulus_from_poisson_not_hardcoded(mcp_env):
    """점탄성 카드의 체적탄성률은 카탈로그 포아송비에서 산출해야 한다.

    저장된 BULK를 그대로 쓰면 폼·써멀패드가 비압축(nu≈0.5)으로 잡혀
    압축으로 쓰는 가스켓의 접촉압력이 통째로 틀리고, nu=0.5는 체적잠김도 일으킨다.
    """
    import numpy as np
    M = mcp_env
    mid = M.register_material(name="TestFoam", category="foam")["material_id"]
    M.register_property(mid, "physical.density", value=240.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref", source_kind="datasheet")
    M.register_property(mid, "mechanical.poisson_ratio", value=0.30, unit="1",
                        quality_tier=1, source_title="Ref", source_kind="datasheet")
    t = np.logspace(-3, 1, 40)
    E_mpa = 0.45 * (0.1 + 0.9 * np.exp(-t / 0.05))
    # 등록 시 nu를 0.49(비압축에 가깝게)로 줘도, 카드는 카탈로그의 0.30을 써야 한다.
    M.register_relaxation_test(material_id=mid, time_s=t.tolist(),
                               modulus_mpa=E_mpa.tolist(), nu=0.49)
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        deck = DX.build_cards(s, ["1, TestFoam"], card="mechanical", units="ton_mm_s")
    txt = deck["keyword"]
    assert "*MAT_VISCOELASTIC" in txt, "완화시험이 있으면 점탄성 카드여야 한다"
    assert "nu=0.3" in txt, "포아송비에서 산출했다는 근거가 카드에 남아야 한다"
    # K = 2G(1+nu)/(3(1-2nu)); nu=0.3이면 K/G = 2*1.3/(3*0.4) ≈ 2.167 — 비압축(수백 배)이 아니다.
    body = txt.splitlines()
    hdr = next(i for i, l in enumerate(body) if l.startswith("$#     mid       rho      bulk"))
    row = body[hdr + 1].split()
    bulk, g0 = float(row[2]), float(row[3])
    assert 1.5 < bulk / g0 < 3.0, f"압축성 폼인데 K/G={bulk/g0:.1f} — 비압축으로 잡혔다"


def test_fixed_width_fields_keep_a_separator(mcp_env):
    """필드가 10칸을 꽉 채우면 옆 값과 붙어 읽을 수 없고 자유형식에서 깨진다."""
    from app import dyna_export as DX
    assert len(DX._fit10("5.9000e-10")) <= 9
    assert len(DX._fit10("1.23456789e-10")) <= 9
    line = DX._card_field("201", "5.9000e-10", "0.4", "0.08")
    assert len(line.split()) == 4, f"필드가 붙었다: {line!r}"


def test_representative_conditions_appear_in_card(mcp_env):
    """율속·온도별 값이 여럿이면 어느 조건의 값이 실렸는지 카드에 보여야 한다."""
    M = mcp_env
    mid = M.register_material(name="RateFoam", category="foam")["material_id"]
    M.register_property(mid, "physical.density", value=405.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref", source_kind="journal", source_doi="10.1/x")
    for rate, E in ((0.001, 6.2e5), (1.0, 4.37e6), (4307.0, 9.2e7)):
        M.register_property(mid, "mechanical.youngs_modulus", value=E, unit="Pa",
                            quality_tier=1, conditions={"strain_rate_1/s": rate},
                            source_title="Ref", source_kind="journal", source_doi="10.1/x")
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        deck = DX.build_cards(s, ["1, RateFoam"], card="mechanical", units="ton_mm_s")
    e_line = [l for l in deck["keyword"].splitlines() if l.startswith("$   E ")][0]
    assert "ε̇" in e_line, f"어느 변형률속도의 값인지 안 나온다: {e_line}"


def test_viscoelastic_card_flags_unused_rate_data(mcp_env):
    """MAT_006에는 율속 항이 없다 — 데이터가 있으면 반영 안 된다고 알려야 한다."""
    import numpy as np
    M = mcp_env
    mid = M.register_material(name="RateTape", category="polymer")["material_id"]
    M.register_property(mid, "physical.density", value=590.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref", source_kind="datasheet")
    M.register_property(mid, "mechanical.cowper_symonds_c", value=0.0154, unit="1/s",
                        quality_tier=3, source_title="Ref", source_kind="journal", source_doi="10.1/y")
    M.register_property(mid, "mechanical.cowper_symonds_p", value=2.886, unit="1",
                        quality_tier=3, source_title="Ref", source_kind="journal", source_doi="10.1/y")
    t = np.logspace(-3, 1, 30)
    M.register_relaxation_test(material_id=mid, time_s=t.tolist(),
                               modulus_mpa=(0.24 * (0.1 + 0.9 * np.exp(-t / 0.04))).tolist())
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        deck = DX.build_cards(s, ["1, RateTape"], card="mechanical", units="ton_mm_s")
    txt = deck["keyword"]
    assert "*MAT_VISCOELASTIC" in txt
    assert "율속 경화 항이 없어" in txt, "율속 데이터가 무시된다는 경고가 없다"
    assert "LOW_DENSITY_FOAM" in txt, "대안 카드를 안내해야 한다"


def test_representative_prefers_room_temperature(mcp_env):
    """온도 스윕이 있으면 극단 온도값이 대표가 되면 안 된다.

    소프트 OCA의 영률이 -40 °C 유리상 값 1,666 MPa로 대표되던 사고가 있었다 —
    실제 상온 값은 0.065 MPa로 2만 배 차이난다.
    """
    M = mcp_env
    mid = M.register_material(name="SweepPoly", category="polymer")["material_id"]
    for tc, E in ((-40.0, 1.666e9), (125.0, 6.6e5), (85.0, 6.5e4), (25.0, 8.0e4)):
        M.register_property(mid, "mechanical.youngs_modulus", value=E, unit="Pa",
                            quality_tier=1, conditions={"temperature_C": tc},
                            source_title="DMA sweep", source_kind="journal", source_doi="10.1/z")
    from app.db import SessionLocal
    from app.catalog_compare import representative_numeric
    with SessionLocal() as s:
        rep = representative_numeric(s, ["mechanical.youngs_modulus"])["mechanical.youngs_modulus"][mid]
    assert rep == 8.0e4, f"상온(25 °C) 값이 아니라 {rep}가 뽑혔다"


def test_representative_ignores_temperature_when_absent(mcp_env):
    """온도 조건이 없는 값은 상온으로 보고 불이익을 주지 않는다."""
    M = mcp_env
    mid = M.register_material(name="PlainPoly", category="polymer")["material_id"]
    M.register_property(mid, "physical.density", value=1200.0, unit="kg/m^3", quality_tier=1,
                        source_title="TDS", source_kind="datasheet")
    M.register_property(mid, "physical.density", value=1190.0, unit="kg/m^3", quality_tier=1,
                        conditions={"temperature_C": 200.0},
                        source_title="TDS", source_kind="datasheet")
    from app.db import SessionLocal
    from app.catalog_compare import representative_numeric
    with SessionLocal() as s:
        rep = representative_numeric(s, ["physical.density"])["physical.density"][mid]
    assert rep == 1200.0, "온도 무표기 값이 200 °C 값에 밀렸다"


def test_conditions_none_stored_as_sql_null(tmp_path):
    """conditions=None이 문자열 'null'이 아니라 SQL NULL로 저장돼야 한다.

    SQLAlchemy JSON 타입은 기본적으로 파이썬 None을 JSON 'null'로 직렬화한다.
    그러면 정합성 검사의 '조건이 dict 아님'에 걸리고 조건 조회가 전부 빗나간다.
    """
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from app.models import Base, Material, PropertyValue

    eng = create_engine(f"sqlite:///{tmp_path}/t.db")
    Base.metadata.create_all(eng)
    with sessionmaker(bind=eng)() as s:
        m = Material(name="X", category="metal")
        s.add(m)
        s.flush()
        s.add(PropertyValue(material_id=m.id, property_key="physical.density",
                            value_num=1.0, unit="kg/m^3", conditions=None))
        s.commit()
        raw = s.execute(text("select conditions from property_value")).scalar()
    assert raw is None, f"conditions가 SQL NULL이 아니라 {raw!r}로 저장됨"


def test_representative_prefers_explicit_room_temp_over_unspecified(mcp_env):
    """온도를 '25 °C'라고 밝힌 측정값이, 온도 무표기 값보다 우선해야 한다.

    실제 사고: SAC305 영률이 시험법 미기재 제품시트의 6.9 GPa로 뽑혀 DYNA 카드에 실렸다.
    상온 인장 측정 27.83 GPa(conditions에 temperature_C=25)가 있었는데도, 무표기 값이
    '상온 거리 0'으로 계산돼 이겨 버렸다.
    """
    M = mcp_env
    mid = M.register_material(name="SolderLike", category="metal")["material_id"]
    M.register_property(mid, "mechanical.youngs_modulus", value=6.9e9, unit="Pa", quality_tier=1,
                        source_title="Preform product sheet", source_kind="datasheet")
    M.register_property(mid, "mechanical.youngs_modulus", value=27.83e9, unit="Pa", quality_tier=1,
                        conditions={"temperature_C": 25.0},
                        source_title="Mechanical characterization paper", source_kind="journal")
    from app.db import SessionLocal
    from app.catalog_compare import representative_numeric
    with SessionLocal() as s:
        rep = representative_numeric(s, ["mechanical.youngs_modulus"])["mechanical.youngs_modulus"][mid]
    assert rep == 27.83e9, "온도 명시 상온 측정값이 무표기 값에 밀렸다"


def test_optical_representative_uses_wavelength_not_temperature(mcp_env):
    """광학 물성의 대표값은 기준 파장(589.3 nm)에 가까운 것이어야 한다.

    실리콘 소광계수는 400 nm에서 0.387, 1000 nm에서 0.0005로 800배 벌어진다.
    온도 기준으로 고르면 어느 파장이 뽑힐지 알 수 없다.
    """
    M = mcp_env
    mid = M.register_material(name="SiLike", category="ceramic")["material_id"]
    for wl, k in ((400.0, 0.387), (589.0, 0.0304), (1000.0, 0.0005)):
        M.register_property(mid, "optical.extinction_coefficient", value=k, unit="1",
                            quality_tier=1, conditions={"wavelength_nm": wl, "temperature_C": 25.0},
                            source_title="n,k table", source_kind="journal")
    from app.db import SessionLocal
    from app.catalog_compare import representative_numeric
    with SessionLocal() as s:
        rep = representative_numeric(s, ["optical.extinction_coefficient"])["optical.extinction_coefficient"][mid]
    assert rep == 0.0304, f"기준 파장에 가장 가까운 값이 아니라 {rep}이 뽑혔다"


def test_lcsr_curve_and_sigy_consistency(mcp_env):
    """율속별 항복강도가 있으면 LCSR 곡선이 나오고, SIGY가 그 기준값으로 맞춰져야 한다.

    LCSR은 '배율' 곡선이라 기준(1.0배)이 율속 시험의 준정적 항복강도다.
    다른 출처의 SIGY를 그대로 두면 고율속 응력이 통째로 어긋난다
    (SAC305에서 실제로 22 MPa × 2.29 = 50 MPa가 나왔다 — 실측은 87 MPa).
    """
    M = mcp_env
    mid = M.register_material(name="RateSolder", category="metal")["material_id"]
    for k, v, u_ in (("physical.density", 7370.0, "kg/m^3"),
                     ("mechanical.youngs_modulus", 27.83e9, "Pa"),
                     ("mechanical.poisson_ratio", 0.35, "1"),
                     ("mechanical.yield_strength", 22e6, "Pa"),
                     ("mechanical.tensile_strength", 42e6, "Pa"),
                     ("mechanical.elongation_at_break", 0.49, "1")):
        M.register_property(mid, k, value=v, unit=u_, quality_tier=1,
                            source_title="base", source_kind="datasheet")
    for rate, sy in ((0.001, 38e6), (600.0, 73e6), (1800.0, 87e6)):
        M.register_property(mid, "mechanical.yield_strength_at_rate", value=sy, unit="Pa",
                            quality_tier=1, conditions={"strain_rate_s": rate},
                            source_title="SHPB paper", source_kind="journal")
    from app.db import SessionLocal
    from app.dyna_export import build_cards
    with SessionLocal() as s:
        deck = build_cards(s, [mid], card="mechanical")["keyword"]
    assert "*DEFINE_CURVE" in deck, "LCSR 곡선이 나오지 않았다"
    assert "2.28947" in deck, "87/38 = 2.289 배율 점이 없다"
    body = [ln for ln in deck.splitlines() if ln.strip().startswith(str(1))]
    assert any("38" in ln for ln in body), "SIGY가 LCSR 기준값 38 MPa로 맞춰지지 않았다"


def test_lcsr_source_appears_in_references(mcp_env):
    """LCSR 곡선의 출처가 참고문헌 목록에 실려야 한다.

    프로비넌스 수집 키에 yield_strength_at_rate가 빠져 있으면 곡선 주석이 '출처미상'이 된다.
    카드의 모든 숫자가 출처로 되짚어져야 한다는 원칙이 깨지는 지점이다.
    """
    M = mcp_env
    mid = M.register_material(name="RateProv", category="polymer")["material_id"]
    for k, v, u_ in (("physical.density", 1360.0, "kg/m^3"),
                     ("mechanical.youngs_modulus", 9.5e9, "Pa"),
                     ("mechanical.poisson_ratio", 0.35, "1"),
                     ("mechanical.yield_strength", 160e6, "Pa"),
                     ("mechanical.tensile_strength", 180e6, "Pa"),
                     ("mechanical.elongation_at_break", 0.035, "1")):
        M.register_property(mid, k, value=v, unit=u_, quality_tier=1,
                            source_title="base sheet", source_kind="datasheet")
    for rate, sy in ((0.0125, 131.08e6), (12.5, 174.26e6)):
        M.register_property(mid, "mechanical.yield_strength_at_rate", value=sy, unit="Pa",
                            quality_tier=1, conditions={"strain_rate_s": rate},
                            source_title="Strain rate study on PA6-GF30", source_kind="journal",
                            source_doi="10.3390/app152111454")
    from app.db import SessionLocal
    from app.dyna_export import build_cards
    with SessionLocal() as s:
        deck = build_cards(s, [mid], card="mechanical")["keyword"]
    assert "*DEFINE_CURVE" in deck, "LCSR 곡선이 없다"
    lcsr_line = [ln for ln in deck.splitlines() if "LCSR" in ln and ln.startswith("$")][0]
    assert "출처미상" not in lcsr_line, f"LCSR 출처가 미상으로 나왔다: {lcsr_line}"
    assert "Strain rate study" in deck, "율속 출처가 참고문헌에 없다"
