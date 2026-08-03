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
