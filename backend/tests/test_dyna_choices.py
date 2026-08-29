# 카드 슬롯의 후보 선택(51차 MC) 회귀 — 기본은 대표값, 지정은 카드에 남고, 없는 후보는 거부.
#
# 왜 이 파일이 있는가. §462(방향) · 47차 IA(율속) · §537(열처리)은 전부 "선택기가 못 보는
# 조건축" 에서 갈렸고, §543·544 가 순위에 축을 더하는 두 시도를 라이브 전수로 재고 둘 다
# 버렸다(개선 4 대 개악 16 · 개선 1 대 개악 52). **그래서 순위를 고치지 않고 고를 수 있게 했다.**
# 여기서 못박는 계약은 셋이다 —
#   1) 안 고르면 지금과 **똑같다**(카드 수·값·주석이 안 변한다)
#   2) 고른 것은 **카드 주석에 남는다**(무엇을 왜 골랐는지 없으면 재현이 안 된다)
#   3) 없는 후보는 **거부한다**(조용히 대표값으로 떨어지면 해석자가 자기 값을 쓴 줄 안다)
from __future__ import annotations

import pytest

from app import dyna_export as D


# ── 선택자 문법 ────────────────────────────────────────────────────────────
def test_parse_selector_accepts_row_id_forms():
    assert D.parse_selector(4711) == (4711, {})
    assert D.parse_selector("4711") == (4711, {})
    assert D.parse_selector("#4711") == (4711, {})


def test_parse_selector_accepts_condition_forms():
    assert D.parse_selector("direction=in-plane") == (None, {"direction": "in-plane"})
    assert D.parse_selector("direction=Z,temperature_C=23") == (
        None, {"direction": "Z", "temperature_C": "23"})
    assert D.parse_selector({"direction": "Z"}) == (None, {"direction": "Z"})


def test_parse_selector_rejects_garbage():
    for bad in ("", "   ", "in-plane", {}, True):
        with pytest.raises(D.ChoiceError):
            D.parse_selector(bad)


def test_parse_choice_query_splits_on_semicolon_and_colon():
    got = D.parse_choice_query(
        "mechanical.poisson_ratio:#38167;thermal.conductivity:direction=through-plane")
    assert got == {"mechanical.poisson_ratio": "#38167",
                   "thermal.conductivity": "direction=through-plane"}
    assert D.parse_choice_query(None) == {}
    with pytest.raises(D.ChoiceError):
        D.parse_choice_query("mechanical.poisson_ratio")


def test_condition_match_is_substring_and_case_insensitive():
    """방향 문자열이 자유형식이라 정확일치는 못 쓴다 — 라이브에 255종이 산다."""
    pv = _fake_row(1, {"direction": "through-thickness (ASTM D5470, 3-omega)"})
    assert D._matches(pv, {"direction": "through"})
    assert D._matches(pv, {"direction": "THROUGH-THICKNESS"})
    assert not D._matches(pv, {"direction": "in-plane"})
    assert not D._matches(pv, {"temperature_C": "23"})     # 없는 조건키는 불일치


def _fake_row(pid, cond):
    from types import SimpleNamespace
    return SimpleNamespace(id=pid, conditions=cond, property_key="thermal.conductivity",
                           value_num=1.0, quality_tier=1, method="measured")


# ── 카드 경로 ──────────────────────────────────────────────────────────────
def _anisotropic(M):
    """면내/두께방향이 갈린 재료 하나. §462 의 열분해 흑연을 축소한 것이다."""
    mid = M.register_material(name="AnisoSheet", category="composite")["material_id"]
    M.register_property(mid, "physical.density", value=2200.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref D", source_kind="journal")
    # `_fmt` 가 1e5 이상을 지수표기로 바꾸므로 카드에 그대로 읽히는 대역을 쓴다.
    for val, direction in ((7.0e10, "in-plane"), (1.0e10, "through-thickness")):
        M.register_property(mid, "mechanical.youngs_modulus", value=val, unit="Pa",
                            quality_tier=1, conditions={"direction": direction},
                            source_title=f"Ref E {direction}", source_kind="journal")
    for val, direction in ((300.0, "in-plane"), (2.0, "through-thickness")):
        M.register_property(mid, "thermal.conductivity", value=val, unit="W/(m*K)",
                            quality_tier=1, conditions={"direction": direction},
                            source_title=f"Ref K {direction}", source_kind="journal")
    M.register_property(mid, "thermal.specific_heat", value=800.0, unit="J/(kg*K)",
                        quality_tier=1, source_title="Ref D", source_kind="journal")
    return mid


def _deck(mid, **kw):
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        return DX.build_cards(s, [{"mid": 101, "material": mid}],
                              card="both", units="ton_mm_s", **kw)


def test_default_is_unchanged_by_the_new_parameter(mcp_env):
    """**안 고르면 지금과 똑같아야 한다** — 이 파동의 회귀 기준선이다."""
    mid = _anisotropic(mcp_env)
    assert _deck(mid)["keyword"] == _deck(mid, choices={})["keyword"]
    txt = _deck(mid)["keyword"]
    assert "*MAT_ELASTIC" in txt and "*MAT_THERMAL_ISOTROPIC" in txt
    assert "$   E   70000 MPa" in txt   # 대표값은 면내 E(등급 동률 → 적재 순서)
    assert "후보 지정" not in txt        # 안 골랐으면 지정 주석도 없다


def test_choice_by_row_id_changes_value_and_source(mcp_env):
    """값만 바꾸고 출처를 그대로 두면 값과 출처가 어긋난다 — 둘이 같이 가야 한다."""
    mid = _anisotropic(mcp_env)
    base = _deck(mid)
    from app.db import SessionLocal
    from app.models import PropertyValue
    from sqlalchemy import select
    with SessionLocal() as s:
        alt = s.execute(select(PropertyValue).where(
            PropertyValue.material_id == mid,
            PropertyValue.property_key == "mechanical.youngs_modulus",
            PropertyValue.value_num == 1.0e10)).scalars().one()
        alt_id, alt_src = alt.id, alt.source.title
    got = _deck(mid, choices={"mechanical.youngs_modulus": f"#{alt_id}"})
    txt = got["keyword"]
    assert "$   E   10000 MPa" in txt, txt
    assert "$   E   70000 MPa" in base["keyword"]
    # 출처도 고른 행의 것이어야 한다 — 참고문헌 목록에 그 제목이 있어야 한다.
    assert alt_src in txt
    assert "※ 후보 지정 — E ←" in txt
    assert "기본 70000 MPa" in txt       # 무엇 대신 골랐는지가 카드에 있어야 재현된다
    assert got["materials"][0]["choices"]["mechanical.youngs_modulus"]["id"] == alt_id


def test_choice_by_condition_picks_the_other_direction(mcp_env):
    mid = _anisotropic(mcp_env)
    txt = _deck(mid, choices={"mechanical.youngs_modulus": "direction=through"})["keyword"]
    assert "$   E   10000 MPa" in txt
    assert "`direction=through`" in txt


def test_slots_are_chosen_independently(mcp_env):
    """E 는 면내, 열전도는 두께방향 — **슬롯마다 따로 골라야 한다.**

    라이브 실측이 그래야 한다고 말한다: 카드 슬롯의 대표값 방향이 갈린 재료 212종에서
    가장 흔한 쌍이 (열전도율, 선팽창) 146종이다. 재료 하나에 방향을 강제하면 그 방향
    값이 없는 칸이 통째로 빈다.
    """
    mid = _anisotropic(mcp_env)
    txt = _deck(mid, choices={"thermal.conductivity": "direction=through"})["keyword"]
    assert "$   E   70000 MPa" in txt                        # 면내 그대로
    assert "(= 2 W/(m*K))" in txt                            # 열전도만 두께방향
    assert "※ 후보 지정 — TC ←" in txt


def test_same_material_twice_can_take_different_choices(mcp_env):
    """등방 카드 둘로 이방을 근사하는 쓰임 — 항목마다 지정이 따로 걸려야 한다."""
    mid = _anisotropic(mcp_env)
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        deck = DX.build_cards(s, [
            {"mid": 101, "material": mid},
            {"mid": 102, "material": mid,
             "choices": {"mechanical.youngs_modulus": "direction=through"}},
        ], card="mechanical", units="ton_mm_s")["keyword"]
    assert "$   E   70000 MPa" in deck and "$   E   10000 MPa" in deck
    # 뒤 항목의 지정이 앞 항목으로 새면 안 된다.
    assert deck.index("$ --- MID 101") < deck.index("$   E   70000 MPa")
    assert deck.index("$ --- MID 102") < deck.index("$   E   10000 MPa")


def test_missing_candidate_is_rejected_not_silently_defaulted(mcp_env):
    """**조용히 대표값으로 떨어지면 안 된다** — 거부하고 실제 후보를 알려준다."""
    mid = _anisotropic(mcp_env)
    with pytest.raises(D.ChoiceError) as e:
        _deck(mid, choices={"mechanical.youngs_modulus": "direction=radial"})
    msg = str(e.value)
    assert "후보" in msg and "in-plane" in msg and "through-thickness" in msg
    with pytest.raises(D.ChoiceError):
        _deck(mid, choices={"mechanical.youngs_modulus": "#999999"})


def test_non_slot_key_is_rejected(mcp_env):
    """카드에 안 박히는 키를 고르라고 하면 거부한다 — 고른 줄 알고 있으면 안 된다."""
    mid = _anisotropic(mcp_env)
    with pytest.raises(D.ChoiceError) as e:
        _deck(mid, choices={"mechanical.shear_modulus": "#1"})
    assert "카드 슬롯이 아니다" in str(e.value)


def test_card_still_stands_after_choosing(mcp_env):
    """카드 수·종류는 줄지 않는다 — 후보를 고른다고 카드가 사라지면 안 된다."""
    mid = _anisotropic(mcp_env)
    base = _deck(mid)
    got = _deck(mid, choices={"thermal.conductivity": "direction=through"})
    assert got["materials"][0]["cards"] == base["materials"][0]["cards"]
    assert got["skipped"] == base["skipped"]


def test_direction_alternatives_are_disclosed_without_choosing(mcp_env):
    """고르지 않아도 **다른 방향 후보가 있다는 사실과 손잡이**는 카드에 나와야 한다.

    §462 의 `_direction_clash` 는 E 와 PR 의 방향 문자열이 다를 때만 경고한다. 라이브에서
    그 경고가 걸리는 39종 중 방향이 실제로 다른 것은 **1종뿐**이고(2361 열분해 흑연),
    나머지 38종은 같은 방향을 다르게 적은 것이다('MD' 대 'in-plane (biaxially oriented
    film; MD/TD not distinguished by the source)'). 자유형식 255종을 분류하는 대신
    **후보를 그대로 보여준다** — 판단은 해석자가 한다.
    """
    mid = _anisotropic(mcp_env)
    txt = _deck(mid)["keyword"]
    assert "※ E 의 다른 방향 후보" in txt
    assert "through-thickness" in txt and "10000 MPa #" in txt
    assert "※ TC 의 다른 방향 후보" in txt
    assert "#" in txt                     # 손잡이(행번호)가 있어야 고를 수 있다


def test_listed_candidates_can_actually_be_chosen(mcp_env):
    """`list_choices` 가 준 `select` 를 그대로 넣으면 그 값이 카드에 들어가야 한다.

    두 걸음(기본으로 뽑고 → 후보를 보고 → 지정해 다시 뽑기)이 새 조회 경로 없이 닫힌다.
    """
    mid = _anisotropic(mcp_env)
    got = _deck(mid, list_choices=True)
    cands = got["candidates"][str(mid)]
    assert set(cands) == {"mechanical.youngs_modulus", "thermal.conductivity"}
    loser = next(c for c in cands["mechanical.youngs_modulus"] if not c["representative"])
    txt = _deck(mid, choices={"mechanical.youngs_modulus": loser["select"]})["keyword"]
    assert f"#{loser['id']}" in txt
    assert D._fmt(loser["value_card"]) + " MPa" in txt


def test_tie_note_carries_the_row_id_handle(mcp_env):
    """동률 주석에 **행번호**가 있어야 진 쪽을 고를 수 있다 — 값만 적으면 못 고른다."""
    M = mcp_env
    mid = M.register_material(name="TieHandleSteel", category="metal")["material_id"]
    M.register_property(mid, "physical.density", value=7850.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref D", source_kind="journal")
    for val, src in ((2.00e11, "Ref A"), (1.60e11, "Ref B")):
        M.register_property(mid, "mechanical.youngs_modulus", value=val, unit="Pa",
                            quality_tier=1, source_title=src, source_kind="journal")
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        txt = DX.build_cards(s, [str(mid)], card="mechanical", units="ton_mm_s")["keyword"]
    assert "대표값이 동률이다" in txt
    import re as _re
    assert _re.search(r"진 쪽 [\d.e+-]+ #\d+", txt), txt


# ── MCP 진입점 ─────────────────────────────────────────────────────────────
def test_mcp_export_accepts_choices_and_reports_rejection(mcp_env):
    """MCP 툴도 같은 계약을 지켜야 한다 — 지정은 먹고, 없는 후보는 error 로 나온다."""
    M = mcp_env
    mid = _anisotropic(M)
    ok = M.export_dyna_cards([mid], card="mechanical",
                             choices={"mechanical.youngs_modulus": "direction=through"})
    assert "$   E   10000 MPa" in ok["keyword"]
    assert "※ 후보 지정 — E ←" in ok["keyword"]

    bad = M.export_dyna_cards([mid], card="mechanical",
                              choices={"mechanical.youngs_modulus": "direction=radial"})
    assert "error" in bad and "keyword" not in bad, bad
    assert "in-plane" in bad["error"]        # 무엇을 고를 수 있었는지 알려준다
