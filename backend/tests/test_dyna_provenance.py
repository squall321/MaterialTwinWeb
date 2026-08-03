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
