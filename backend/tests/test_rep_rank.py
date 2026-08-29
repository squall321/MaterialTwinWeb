# 대표값 선택 순위 규칙의 회귀 고정 — 카드·Ashby·비교·조회가 전부 이 한 함수에 달려 있다.
#
# 이 파일이 있는 이유(50차 LA). `_rep_rank` 는 세 파동에서 같은 자리에 걸렸다 —
# §462 방향 · 47차 IA 율속 · §537 열처리. 매번 "순위에 축을 하나 더 넣자" 가 나왔고,
# 라이브 41,368행으로 재 보니 넣는 쪽이 개악이 더 많았다(method 26쌍 중 개선 2 ·
# 온도축 게이팅 67쌍 중 52쌍이 덜 적힌 행으로 뒤집힘). 그래서 **지금 순위를 못으로 박는다.**
# 바꾸려는 다음 파동은 이 테스트를 깨면서 왜 깨도 되는지를 숫자로 대야 한다.
from __future__ import annotations

from types import SimpleNamespace

from app import catalog_compare as CC


def _pv(pid, key="mechanical.youngs_modulus", tier=1, value=1.0,
        cond=None, method="measured"):
    """`_rep_rank` 가 보는 필드만 가진 가짜 행. ORM 없이 순위 규칙만 시험한다."""
    return SimpleNamespace(id=pid, property_key=key, quality_tier=tier,
                           value_num=value, conditions=cond, method=method)


# ── 순위 자리 하나씩 ────────────────────────────────────────────────────────
def test_rank_order_is_solid_tier_numeric_primary_condcount_id():
    """순위 튜플의 자리와 뜻이 바뀌지 않았는지."""
    r = CC._rep_rank(_pv(7, tier=2, cond={"temperature_C": 23.0}))
    assert r == (0, 2, 0, 0.0, 1, 7)


def test_non_solid_loses_to_solid():
    """용융·액체 값은 구조·열해석 대표가 될 수 없다 — 등급이 높아도 뒤로 간다."""
    melt = _pv(1, tier=1, cond={"state": "melt"})
    solid = _pv(2, tier=4, cond=None)
    assert CC._rep_rank(solid) < CC._rep_rank(melt)


def test_lower_tier_number_wins():
    assert CC._rep_rank(_pv(9, tier=1)) < CC._rep_rank(_pv(1, tier=2))


def test_numeric_beats_text_only():
    num = _pv(9, value=1.0)
    txt = _pv(1, value=None)
    assert CC._rep_rank(num) < CC._rep_rank(txt)


def test_room_temperature_beats_extreme_temperature():
    """온도 스윕 재료에서 -40 °C 유리상 값이 대표가 되면 안 된다(주석의 소프트 OCA 사고)."""
    rt = _pv(9, cond={"temperature_C": 25.0})
    cold = _pv(1, cond={"temperature_C": -40.0})
    assert CC._rep_rank(rt) < CC._rep_rank(cold)


def test_unspecified_temperature_sits_between_room_and_extreme():
    """미기재 벌점의 위치가 규칙의 핵심이다 — 상온 명시값보다 뒤, 고온값보다 앞.

    이 벌점을 없애면(50차 LA 의 B안) 조건을 **덜 적은 행**이 이긴다 —
    라이브에서 67쌍이 뒤집혔고 그중 52쌍이 조건이 더 적은 행으로 갔다.
    LiNbO3 유전율이 24.06(clamped eps33^S 명시)에서 조건이 하나도 없는 85.2 로 뒤집혔다.
    """
    rt = _pv(9, cond={"temperature_C": 23.0})
    unspec = _pv(1, cond=None)
    hot = _pv(2, cond={"temperature_C": 150.0})
    assert CC._rep_rank(rt) < CC._rep_rank(unspec) < CC._rep_rank(hot)
    assert CC._UNSPECIFIED_TEMP_PENALTY == 5.0


def test_kelvin_and_celsius_keys_are_both_read():
    for cond in ({"temperature_K": 296.15}, {"temperature_k": 296.15},
                 {"temperature_C": 23.0}, {"temperature_c": 23.0}):
        assert CC._temp_distance(cond) < 1.0, cond


def test_optical_ranks_by_wavelength_not_temperature():
    """광학의 지배조건은 파장이다 — 실리콘 소광계수가 400 nm 와 652 nm 사이에서 800배 벌어진다."""
    key = "optical.extinction_coefficient"
    near = _pv(9, key=key, cond={"wavelength_nm": 589.0})
    far = _pv(1, key=key, cond={"wavelength_nm": 5000.0})
    assert CC._rep_rank(near) < CC._rep_rank(far)
    # 온도를 적어도 파장 없는 행은 이기지 못한다.
    no_wl = _pv(2, key=key, cond={"temperature_C": 23.0})
    assert CC._rep_rank(near) < CC._rep_rank(no_wl)


def test_fewer_conditions_wins_when_primary_ties():
    a = _pv(9, cond={"temperature_C": 23.0})
    b = _pv(1, cond={"temperature_C": 23.0, "direction": "MD", "standard": "ISO 178"})
    assert CC._rep_rank(a) < CC._rep_rank(b)


def test_id_is_the_last_resort():
    a = _pv(1, cond={"temperature_C": 23.0})
    b = _pv(2, cond={"temperature_C": 23.0})
    assert CC._rep_rank(a) < CC._rep_rank(b)


# ── 일부러 안 보는 것 ──────────────────────────────────────────────────────
def test_method_is_deliberately_not_ranked():
    """`method` 를 순위에 넣지 않는다(50차 LA).

    `method` 는 등급과 다른 축이지만 이 DB 에서는 **품질 축이 아니다** — 같은
    `midpoint_of_range` 행 211개가 computed 124 · measured 63 · handbook 24 로 갈려 있다
    (451·472번 가드가 다시 쓴 결과다). 넣어 보니 라이브에서 26쌍이 뒤집혔는데
    실리콘 반사율이 550 nm 에서 **5,000 nm** 로, 프리프레그 CTE 가 면내에서 두께방향으로,
    Al2024-T3 의 피로상수가 **T351 에서 T4** 로 갔다. 개선은 2건뿐이다.
    그리고 §537 의 재료 36 은 **두 행이 다 `measured` 라 method 로는 갈리지도 않는다.**
    """
    measured = _pv(2, method="measured")
    estimated = _pv(1, method="estimated")
    # 같은 등급·같은 조건이면 method 와 무관하게 id 가 정한다.
    assert CC._rep_rank(estimated) < CC._rep_rank(measured)


# ── 동률 노출 ──────────────────────────────────────────────────────────────
def test_tie_key_drops_only_the_id():
    a, b = _pv(1), _pv(2)
    assert CC._tie_key(a) == CC._tie_key(b)
    assert CC._rep_rank(a) != CC._rep_rank(b)


def test_representative_ties_reports_arbitrary_picks(mcp_env):
    """순위가 같은데 값이 다른 후보가 있으면 드러내야 한다 — 자동으로 고르지 않는다(§462)."""
    M = mcp_env
    mid = M.register_material(name="TieSteel", category="metal")["material_id"]
    for val, src in ((2.00e11, "Ref A"), (1.60e11, "Ref B")):
        M.register_property(mid, "mechanical.youngs_modulus", value=val, unit="Pa",
                            quality_tier=1, source_title=src, source_kind="journal")
    from app.db import SessionLocal
    from app import catalog_compare as C
    with SessionLocal() as s:
        ties = C.representative_ties(s, ["mechanical.youngs_modulus"])
        rows = C.representative_rows(s, ["mechanical.youngs_modulus"])
    assert (mid, "mechanical.youngs_modulus") in ties
    rivals = ties[(mid, "mechanical.youngs_modulus")]
    assert len(rivals) == 1
    # 진 쪽은 대표로 뽑힌 행이 아니어야 한다.
    assert rivals[0].id != rows[(mid, "mechanical.youngs_modulus")].id


def test_representative_ties_ignores_rounding_twins(mcp_env):
    """7.85 대 7.8 같은 반올림 쌍둥이까지 주의로 세면 소음이 된다."""
    M = mcp_env
    mid = M.register_material(name="TwinSteel", category="metal")["material_id"]
    for val, src in ((7850.0, "Ref A"), (7855.0, "Ref B")):
        M.register_property(mid, "physical.density", value=val, unit="kg/m^3",
                            quality_tier=1, source_title=src, source_kind="journal")
    from app.db import SessionLocal
    from app import catalog_compare as C
    with SessionLocal() as s:
        ties = C.representative_ties(s, ["physical.density"])
    assert (mid, "physical.density") not in ties


def test_representative_ties_empty_when_tier_separates(mcp_env):
    """등급이 가르면 동률이 아니다 — 선택기가 제 할 일을 한 것이다."""
    M = mcp_env
    mid = M.register_material(name="TierSteel", category="metal")["material_id"]
    for val, tier, src in ((2.00e11, 1, "Ref A"), (1.60e11, 4, "Ref B")):
        M.register_property(mid, "mechanical.youngs_modulus", value=val, unit="Pa",
                            quality_tier=tier, method="estimated" if tier == 4 else "measured",
                            conditions={"assumption": True} if tier == 4 else None,
                            source_title=src, source_kind="journal")
    from app.db import SessionLocal
    from app import catalog_compare as C
    with SessionLocal() as s:
        ties = C.representative_ties(s, ["mechanical.youngs_modulus"])
    assert (mid, "mechanical.youngs_modulus") not in ties


def test_card_marks_the_tie_instead_of_hiding_it(mcp_env):
    """동률로 뽑힌 칸은 카드 주석에 드러나야 한다 — 방향 경고와 같은 방식이다."""
    M = mcp_env
    mid = M.register_material(name="TieCardSteel", category="metal")["material_id"]
    M.register_property(mid, "physical.density", value=7850.0, unit="kg/m^3",
                        quality_tier=1, source_title="Ref D", source_kind="journal")
    for val, src in ((2.00e11, "Ref A"), (1.60e11, "Ref B")):
        M.register_property(mid, "mechanical.youngs_modulus", value=val, unit="Pa",
                            quality_tier=1, source_title=src, source_kind="journal")
    from app.db import SessionLocal
    from app import dyna_export as DX
    with SessionLocal() as s:
        deck = DX.build_cards(s, [str(mid)], card="mechanical", units="ton_mm_s")
    txt = deck["keyword"]
    assert "*MAT_ELASTIC" in txt, "카드는 그대로 서야 한다 — 주의는 카드를 막지 않는다"
    assert "대표값이 동률이다" in txt
    assert "E 는" in txt


# ── 51차 MA: 판정을 조건에 적는 것이 순위를 흔들지 않는다는 불변식 ──────────────
def test_uniform_condition_keys_within_a_group_preserve_order():
    """한 (재료,키) 군의 **모든 행에 같은 수의 조건 칸**을 더하면 군 안의 순서가 그대로다.

    51차 MA 가 동률 판정(`verdict_tie_axis`·`verdict_tie_note`)을 `conditions` 에 적었다.
    순위 5번째 자리가 `len(conditions)` 라, **일부 행에만** 칼럼을 더하면 그 행이 조건 많은
    행에 밀려 **대표값이 조용히 바뀐다.** 그래서 군의 모든 행에 같은 수를 더했고,
    라이브 41,368행에서 대표값 변동 0 을 실측했다. 이 불변식이 그 실측의 근거다.
    """
    rows = [_pv(3, tier=1, cond={"direction": "z"}),
            _pv(1, tier=1, cond={"direction": "x"}),
            _pv(2, tier=1, cond={"direction": "y", "standard": "ASTM"})]
    before = [pv.id for pv in sorted(rows, key=CC._rep_rank)]
    for pv in rows:                       # 군 전체에 같은 수(2칸)를 더한다
        pv.conditions = dict(pv.conditions, verdict_tie_axis="a", verdict_tie_note="b")
    assert [pv.id for pv in sorted(rows, key=CC._rep_rank)] == before


def test_adding_keys_to_only_some_rows_does_flip_the_representative():
    """반대 방향의 못 — **일부 행에만** 더하면 실제로 뒤집힌다. 그래서 전부에 더해야 한다."""
    head = _pv(1, tier=1, cond={"direction": "x"})
    other = _pv(2, tier=1, cond={"direction": "y", "standard": "ASTM"})
    assert CC._rep_rank(head) < CC._rep_rank(other)
    head.conditions = dict(head.conditions, verdict_tie_axis="a", verdict_tie_note="b")
    assert CC._rep_rank(other) < CC._rep_rank(head)   # 조건 2개 → 4개가 되며 밀린다


# ── 52차 NA: 되돌리기 표시는 조건이 아니다 ────────────────────────────────────
def test_correction_trail_is_not_counted_as_a_condition():
    """정정 경로(§521)가 남기는 표시를 조건으로 세면 **정정한 행이 밀린다.**

    `<칸>_before_correction`·`correction_reason`·`corrected_by` 는 값을 되돌리기 위한
    감사 흔적이지 시험 조건이 아니다. 세면 §548 이 배치에 지운 제약("군의 모든 행에 같은
    수를 더해라")이 생기는데, 정정이 바꾸는 칸 수가 행마다 다르면 그 제약은 지킬 수 없다.
    실측(52차 NA, 라이브 41,368행) — 세면 102군의 대표행이 바뀌고, 안 세면 0군이다.
    """
    a = _pv(9, tier=1, cond={"temperature_c": 23.0})
    b = _pv(1, tier=1, cond={"temperature_c": 23.0, "direction": "MD"})
    assert CC._rep_rank(a) < CC._rep_rank(b)          # 조건 1칸 대 2칸
    a.conditions = dict(a.conditions, temperature_C_before_correction=23.0,
                        temperature_c_before_correction=None,
                        correction_reason="조건 어휘 통일", corrected_by="52차 NA")
    assert CC._rep_rank(a) < CC._rep_rank(b)          # 표시를 4칸 더해도 그대로다


def test_verdict_keys_are_still_counted():
    """`verdict_*` 는 계속 센다 — 51차 MA·MC 가 **군 전체에 같은 수**로 달아 둔 것이라
    지금 상태가 정합적이다. 빼면 재료255 가 뒤집힌다(전수로 재고 안 넣었다)."""
    a = _pv(1, tier=1, cond={"direction": "x"})
    b = _pv(2, tier=1, cond={"direction": "y", "standard": "ASTM"})
    assert CC._rep_rank(a) < CC._rep_rank(b)
    a.conditions = dict(a.conditions, verdict_tie_axis="a", verdict_tie_note="b")
    assert CC._rep_rank(b) < CC._rep_rank(a)


# ── 53차 OA: 이동 표시도 조건이 아니다 ───────────────────────────────────────
def test_move_trail_is_not_counted_as_a_condition():
    """이동 표시(`moved_from_material`·`moved_from_source`)를 조건으로 세면 **옮긴 행이 밀린다.**

    §536 의 재료 이동과 53차 OA 의 출처 병합이 되돌리기·전파용으로 남기는 흔적이지 시험
    조건이 아니다. 그리고 §563 이 값 중복군에서 쓴 "한쪽에만 더한다" 는 여기서 못 쓴다 —
    출처 병합이 옮기는 193행은 중복군이 아니라 DB 전역에 흩어져 있다.
    실측(53차 OA, 라이브 41,368행 · 20,041군) — 세면 **대표 20군이 뒤집히고 6군은 값까지
    바뀐다**(Zeonex 굴곡강도 120 → 115 MPa). 안 세면 0군이다.
    """
    a = _pv(9, tier=1, cond={"temperature_c": 23.0})
    b = _pv(1, tier=1, cond={"temperature_c": 23.0, "direction": "MD"})
    assert CC._rep_rank(a) < CC._rep_rank(b)          # 조건 1칸 대 2칸
    a.conditions = dict(a.conditions,
                        moved_from_source={"kind": "datasheet", "title": "옛 시트"},
                        moved_from_material="Carbon Steel 45")
    assert CC._rep_rank(a) < CC._rep_rank(b)          # 표시를 2칸 더해도 그대로다
