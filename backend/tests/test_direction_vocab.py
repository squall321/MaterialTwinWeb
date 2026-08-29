# `direction` 정규 어휘와 면(plane) 비교를 못박는다 — 52차 NA.
"""이 어휘가 흔들리면 두 가지가 동시에 깨진다.

① `_direction_clash`(§462) 가 **같은 면의 다른 표기**를 방향 충돌로 오인한다(§551 의 38종).
② 조건 정규화가 원문이 인쇄하지 않은 방향을 지어낸다(§537 이 금지한 것).

그래서 못박는 것은 셋이다 — **정규값의 최소 어휘** · **억지 배정 금지** · **면 비교**.
"""
import pytest

from app.direction_vocab import CANONICAL, normalize, plane


@pytest.mark.parametrize("raw,want", [
    # 면내 — 안쪽 방향을 안 가른 표기
    ("in-plane", "in-plane"),
    ("in-plane (biaxially oriented film; MD/TD not distinguished by the source)", "in-plane"),
    ("in-plane (warp/fill, orthogonal plain weave — identical by symmetry)", "in-plane"),
    ("X", "in-plane"), ("Y", "in-plane"), ("x-y (in-plane)", "in-plane"),
    # 두께방향
    ("through-plane", "through-thickness"),
    ("cross-plane (3-omega on film)", "through-thickness"),
    ("Z", "through-thickness"), ("Z-axis", "through-thickness"),
    ("through plate thickness (1-D)", "through-thickness"),
    # 면내의 특정 방향 — MD/TD 는 **합치지 않는다**(Kapton 은 MD 와 TD 가 실제로 다르다)
    ("MD", "MD"), ("MD (machine direction)", "MD"), ("length (warp)", "MD"),
    ("0 deg to mold flow", "MD"), ("flow", "MD"),
    ("TD", "TD"), ("cross (fill)", "TD"), ("90 deg to mold flow", "TD"),
    ("CMD (cross-machine direction)", "TD"), ("cross-flow (transverse)", "TD"),
    # 시트가 아닌 기하
    ("longitudinal (extruded tube axis)", "axial"),
    ("RD (radial direction of the extruded billet)", "radial"),
    ("circumferential", "circumferential"),
    ("isotropic (벌크 엘라스토머)", "isotropic"),
])
def test_normalize_assigns(raw, want):
    assert normalize(raw) == want
    assert want in CANONICAL


@pytest.mark.parametrize("raw", [
    # 원문이 방향을 안 적었다 — 지어내지 않는다
    "not printed", "not stated in source (bulk)", "not stated in source (bulk, isotropic assumption)",
    "미인쇄", "unspecified (원문 미기재)", "not directional (스칼라량)",
    # 이 여덟 어휘로 표현되지 않는 축 — 배정하지 않는다
    "short transverse", "L-T", "ST-2 direction",
    "along the orientation (easy) axis", "parallel to orientation (C∥)",
    "parallel to c-axis (E || c)", "45 deg to mold flow",
    "DD (diagonal direction, 45 deg to rolling direction)",
    "anisotropic (oriented)", "normal", "parallel", "average",
])
def test_normalize_refuses(raw):
    assert normalize(raw) is None


def test_leading_clause_is_what_the_row_claims():
    """뒤쪽 서술이 **다른 행**을 가리키는 경우가 실재한다 — 머리절이 그 행의 주장이다."""
    assert normalize("in-plane (nu12) — 두께방향 nu13은 값이 다르다") == "in-plane"
    assert normalize("isotropic (벌크 아크릴, TDS에 방향 미표기)") == "isotropic"
    assert normalize("not stated; 사출·압출 LCP는 유동방향 ν12로 보는 것이 타당하다") is None


def test_plane_folds_in_plane_directions_but_not_thickness():
    """§551 의 오탐 38종이 여기서 사라진다 — MD 와 면내(미분해)는 같은 면이다."""
    assert plane("MD") == plane("TD") == plane("in-plane") == "in-plane"
    assert plane("through-thickness") == "through-thickness"
    assert plane("in-plane") != plane("through-thickness")
    # 면을 못 정하는 것은 비교하지 않는다
    for v in ("isotropic", "axial", "radial", "circumferential", None, ""):
        assert plane(v) is None


def test_plane_also_folds_raw_text():
    """정정이 막힌 군(§548)은 아직 자유서술이다 — 거기서도 참 양성을 잃으면 안 된다."""
    assert plane("through-plane") == "through-thickness"
    assert plane("in-plane (MD/TD 구분 없음)") == "in-plane"
    assert plane("MD (machine direction)") == "in-plane"


def test_direction_clash_uses_plane(monkeypatch):
    from app import dyna_export as D

    class R:
        def __init__(self, d):
            self.conditions = {"direction": d}

    def rows(e, nu):
        return {(1, D.K_E): R(e), (1, D.K_NU): R(nu)}

    # 같은 면 — 경고 없다(§551 의 38종)
    assert D._direction_clash(rows("MD", "in-plane"), 1) is None
    assert D._direction_clash(rows("TD", "MD"), 1) is None
    # 다른 면 — 경고한다(재료2361 열분해 흑연, 참 양성 1종)
    assert D._direction_clash(rows("in-plane", "through-thickness"), 1) is not None
    # 면을 못 정하면 비교하지 않는다
    assert D._direction_clash(rows("isotropic", "through-thickness"), 1) is None


# ── 조건 키 통일표 ──────────────────────────────────────────────────────────
def _rename_map():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "catalog"))
    import normalize_condition_keys as N
    return N.RENAME


def test_rename_map_has_no_chains():
    """정본이 다시 남의 옛 이름이면 적용 순서가 결과를 바꾼다 — 사슬을 금지한다."""
    m = _rename_map()
    assert not (set(m.values()) & set(m)), sorted(set(m.values()) & set(m))


def test_rename_map_never_converts_units():
    """단위가 이름에 들어 있으면 **양쪽 단위가 같아야** 한다. 다르면 그건 채굴이다."""
    import re
    m = _rename_map()
    unit = re.compile(r"_(k|c|f|hz|khz|mhz|ghz|pa|kpa|mpa|gpa|n|mn|v|s|min|h|hr|um|nm|mm|m|"
                      r"pct|percent|deg|per_s|per_min)$", re.I)
    for a, b in m.items():
        ua = (unit.search(a).group(1).lower() if unit.search(a) else None)
        ub = (unit.search(b).group(1).lower() if unit.search(b) else None)
        if ua is None or ub is None:
            continue
        same = {("percent", "pct"), ("hr", "h"), ("per_s", "s"), ("per_min", "min")}
        assert ua == ub or (ua, ub) in same or (ub, ua) in same, f"{a} → {b}: {ua} ≠ {ub}"
