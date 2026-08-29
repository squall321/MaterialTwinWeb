# 카탈로그 물성 → LS-DYNA 키워드 카드 대량 생성(기계 *MAT_*, 열 *MAT_THERMAL_*). MCP·웹 공용 코어.
from __future__ import annotations

import difflib
import json
import re
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.catalog_compare import (_rep_rank, is_non_solid, representative_numeric,
                                 representative_rows, representative_ties)
from app.models import Material, ProcessedResult, PropertyValue, Specimen, Test
from app.unit_systems import UnitSystem, get_system

# 카드에 쓰는 물성 키.
K_RHO = "physical.density"
K_E = "mechanical.youngs_modulus"
K_NU = "mechanical.poisson_ratio"


def _cond_dict(pv) -> dict:
    """행의 조건을 dict 로. 문자열로 저장된 경우(옛 적재분)도 받는다."""
    c = getattr(pv, "conditions", None)
    if isinstance(c, str):
        try:
            c = json.loads(c)
        except (TypeError, ValueError):
            return {}
    return c if isinstance(c, dict) else {}


def _direction(pv) -> str:
    """행의 방향 조건. 없으면 빈 문자열."""
    return str(_cond_dict(pv).get("direction") or "")


def _direction_clash(rows, mid) -> str | None:
    """탄성계수와 포아송비가 **서로 다른 방향**에서 뽑혔으면 그 사실을 낸다.

    대표값 선택(`representative_numeric`)은 등급만 보고 **방향을 안 본다.**
    이방성 재료에서는 면내 E 에 두께방향 nu 가 짝지어질 수 있다 —
    42차 DA 가 열분해 흑연(basal E 20 GPa · z nu 0.3 · basal nu -0.1)에서 짚었다.
    등방 카드는 한 방향의 짝으로만 성립하므로 섞이면 카드가 물리적으로 틀린다.
    """
    e_row, nu_row = rows.get((mid, K_E)), rows.get((mid, K_NU))
    if not e_row or not nu_row:
        return None
    de, dn = _direction(e_row), _direction(nu_row)
    if de and dn and de != dn:
        return f"E 는 `{de}`, PR 은 `{dn}` 에서 뽑혔다"
    return None


def _tie_note(ties: dict, mid: int, key: str, label: str, scale: float = 1.0) -> str | None:
    """그 칸의 대표값이 **동률에서 임의로 뽑혔으면** 진 후보를 카드에 적는다.

    `_direction_clash` 와 같은 방식이다 — 자동으로 고르지 않고 드러낸다(§462).
    선택기가 등급·지배조건·조건수까지 봐도 안 갈리면 마지막은 `id`(적재 순서)다.
    라이브에서 그런 (재료,물성키) 쌍이 3,975개이고 그중 2,510개는 값이 10% 넘게 다르다(50차 LA).
    """
    rivals = ties.get((mid, key))
    if not rivals:
        return None
    shown = ", ".join(f"{_fmt(r.value_num * scale)} #{r.id}{_cond_tag(r.conditions)}"
                      for r in rivals[:2])
    more = f" 외 {len(rivals) - 2}건" if len(rivals) > 2 else ""
    return (f"{label} 는 순위가 같은 후보 {len(rivals) + 1}개에서 적재 순서로 골랐다"
            f" (진 쪽 {shown}{more})")
K_SIGY = "mechanical.yield_strength"
K_UTS = "mechanical.tensile_strength"
K_ELONG = "mechanical.elongation_at_break"
K_HC = "thermal.specific_heat"
K_TC = "thermal.conductivity"
K_CTE = "thermal.expansion_linear"
K_CS_C = "mechanical.cowper_symonds_c"
K_CS_P = "mechanical.cowper_symonds_p"

K_JC_A = "mechanical.johnson_cook_a"
K_JC_B = "mechanical.johnson_cook_b"
K_JC_N = "mechanical.johnson_cook_n"
K_JC_C = "mechanical.johnson_cook_c"
K_SIGY_RATE = "mechanical.yield_strength_at_rate"

MECH_KEYS = (K_RHO, K_E, K_NU, K_SIGY, K_UTS, K_ELONG, K_CS_C, K_CS_P,
             K_JC_A, K_JC_B, K_JC_N, K_JC_C)
THERM_KEYS = (K_RHO, K_HC, K_TC, K_CTE)


# ── 후보 선택 — 카드 슬롯마다 "나머지 한쪽" 을 쓸 수 있게 연다 ─────────────────────
#
# 왜 있는가(51차 MC). 카드의 각 칸은 `representative_*` 가 고른 **한 행**만 썼다.
# 그런데 라이브 41,368행에서 대표값의 63%(3,975쌍)가 순위로 안 갈려 **적재 순서**로 정해지고,
# 그중 2,510쌍은 값이 10% 넘게 다르다(§545). 방향(§462)·율속(47차 IA)·열처리(§537)는
# 선택기에 없는 축이라 순위로는 영원히 못 가른다 — 그리고 §543·544 가 축을 더하는 두 시도를
# 전수로 재고 둘 다 버렸다(개악 26쌍 중 개선 4 · 67쌍 중 1).
#
# **그래서 순위를 고치지 않고 고를 수 있게 한다.** 기본 동작은 그대로 대표값이고,
# 고른 것은 카드 주석에 남으며, 없는 후보를 고르면 **대표값으로 떨어지지 않고 거부한다.**
#
# **슬롯마다 따로 고른다.** 라이브 실측이 그래야 한다고 말한다 — 카드 슬롯의 대표값 방향이
# 서로 갈린 재료 212종에서 가장 흔한 쌍이 (열전도율, 선팽창) 146종이고, (영률, 열전도율) 49 ·
# (영률, 선팽창) 42다. 한 재료에 방향을 하나로 강제하면 그 방향 값이 없는 칸이 통째로 빈다.


class ChoiceError(ValueError):
    """호출자가 지정한 후보를 못 찾았다. **조용히 대표값으로 떨어지지 않는다.**

    지정이 빗나갔는데 대표값이 나오면 카드는 서지만 해석자는 자기가 고른 값을 쓴 줄 안다 —
    §505 가 말한 "틀린 주의가 멀쩡한 값을 버린다" 의 반대 얼굴이다.
    """


# 고를 수 있는 슬롯. 카드에 실제로 박히는 칸만 연다.
CHOOSABLE_KEYS = tuple(sorted(set(MECH_KEYS + THERM_KEYS)))

# 카드에서 부르는 이름. 주석은 카드 문법의 필드명으로 읽히는 게 낫다.
_SLOT_LABEL = {K_RHO: "RO", K_E: "E", K_NU: "PR", K_SIGY: "SIGY", K_UTS: "UTS",
               K_ELONG: "FAIL", K_HC: "HC", K_TC: "TC", K_CTE: "CTE",
               K_CS_C: "C", K_CS_P: "p"}
# 열 카드에서 `$` 값 줄이 따로 나가는 칸 — 방향 후보 주석을 그 옆에 붙인다.
# (기계 카드 쪽은 동률 주석 루프가 같은 목록을 이미 돌고 있어 거기 얹었다.)
_THERM_SLOTS = (K_RHO, K_HC, K_TC, K_CTE)

_SEL_ID = re.compile(r"^#?(\d+)$")


def slot_scale(key: str, u: UnitSystem) -> tuple[float, str]:
    """슬롯의 SI→카드 단위 환산계수와 단위 표기. 주석 값을 카드와 같은 단위로 적기 위한 것."""
    if key == K_RHO:
        return u.f_density, u.density_unit
    if key in (K_E, K_SIGY, K_UTS, K_JC_A, K_JC_B):
        return u.f_stress, u.stress_unit
    if key == K_HC:
        return f_specific_heat(u), hc_unit(u)
    if key == K_TC:
        return f_conductivity(u), tc_unit(u)
    return 1.0, ""


def candidate_rows(db: Session, material_ids: list[int],
                   keys: tuple | list = CHOOSABLE_KEYS) -> dict[tuple, list]:
    """(재료,키) → 후보 행들, **대표값 순서**로. 질의 한 번.

    수치행만 본다 — 카드는 수치만 쓰고 `representative_numeric` 도 그렇게 고른다.
    맨 앞이 지금 카드에 들어가는 그 행이다.
    """
    if not material_ids:
        return {}
    rows = db.execute(select(PropertyValue).where(
        PropertyValue.material_id.in_(list(material_ids)),
        PropertyValue.property_key.in_(list(keys)),
        PropertyValue.value_num.isnot(None))).scalars().all()
    out: dict[tuple, list] = defaultdict(list)
    for pv in rows:
        out[(pv.material_id, pv.property_key)].append(pv)
    for v in out.values():
        v.sort(key=_rep_rank)
    return dict(out)


def parse_selector(sel) -> tuple[int | None, dict]:
    """후보 선택자 → (property_value.id, 조건 제약).

    받는 형태 —
      `4711` · `"#4711"`          그 행을 쓴다(가장 정확하다. 카드 주석이 이 번호를 적어 준다)
      `"direction=through-plane"` 조건이 그렇게 적힌 후보 중에서 대표 규칙으로 고른다
      `"direction=Z,temperature_C=23"` · `{"direction": "Z"}`
    """
    if isinstance(sel, bool):
        raise ChoiceError(f"선택자가 참/거짓이다: {sel!r}")
    if isinstance(sel, int):
        return sel, {}
    if isinstance(sel, dict):
        cons = {str(k): sel[k] for k in sel}
        if not cons:
            raise ChoiceError("빈 선택자")
        return None, cons
    s = str(sel).strip()
    if not s:
        raise ChoiceError("빈 선택자")
    m = _SEL_ID.match(s)
    if m:
        return int(m.group(1)), {}
    cons = {}
    for part in s.split(","):
        if "=" not in part:
            raise ChoiceError(f"알 수 없는 선택자 '{part.strip()}' — "
                              "'#행번호' 또는 '조건키=값' 형태여야 한다")
        k, _, v = part.partition("=")
        if not k.strip():
            raise ChoiceError(f"조건키가 비었다: '{part.strip()}'")
        cons[k.strip()] = v.strip()
    return None, cons


def parse_choice_query(text: str | None) -> dict:
    """질의문자열 한 줄 → `{물성키: 선택자}`. GET 진입점용.

    `"mechanical.poisson_ratio:#38167;thermal.conductivity:direction=through-plane"`
    키와 선택자는 `:` 로, 항목은 `;` 로 가른다 — 선택자 안에 `=` 와 `,` 가 들어가기 때문이다.
    """
    out: dict = {}
    for item in (text or "").split(";"):
        item = item.strip()
        if not item:
            continue
        if ":" not in item:
            raise ChoiceError(f"choose 항목 '{item}' 에 `:` 가 없다 — "
                              "'물성키:선택자' 형태여야 한다")
        k, _, v = item.partition(":")
        if not k.strip() or not v.strip():
            raise ChoiceError(f"choose 항목 '{item}' 이 비었다")
        out[k.strip()] = v.strip()
    return out


def _matches(pv, cons: dict) -> bool:
    """조건 제약을 만족하는가. **부분일치·대소문자 무시**다.

    방향 문자열이 자유형식이라 정확일치는 못 쓴다 — 라이브의 카드 슬롯 9칸에 `direction`
    값이 **255종**이고 그중 54종은 40자가 넘는 산문이다
    (`'through-thickness (basis measured cross-plane by the 3-omega method on a …'`).
    `direction=through` 로 그 행을 집을 수 있어야 쓸모가 있다.
    """
    c = _cond_dict(pv)
    for k, want in cons.items():
        got = c.get(k)
        if got is None:
            return False
        if str(want).strip().lower() not in str(got).strip().lower():
            return False
    return True


def _avail(cands: list, u: UnitSystem, limit: int = 6) -> str:
    """거부 메시지에 붙일 후보 목록 — 무엇을 고를 수 있었는지 말해 주지 않으면 못 고친다."""
    f, unit = slot_scale(cands[0].property_key, u) if cands else (1.0, "")
    bits = [f"#{pv.id} {_fmt((pv.value_num or 0) * f)}{(' ' + unit) if unit else ''}"
            f"{_cond_tag(pv.conditions)}" for pv in cands[:limit]]
    more = f" 외 {len(cands) - limit}건" if len(cands) > limit else ""
    return (" · ".join(bits) + more) if bits else "(후보 없음)"


def resolve_choice(cands: list, key: str, sel, u: UnitSystem, where: str):
    """선택자 → 실제 행. 못 찾으면 `ChoiceError` — 대표값으로 떨어지지 않는다."""
    pid, cons = parse_selector(sel)
    if not cands:
        raise ChoiceError(f"{where}: `{key}` 에 수치 후보가 하나도 없다 — 고를 것이 없다")
    if pid is not None:
        hit = [pv for pv in cands if pv.id == pid]
        if not hit:
            raise ChoiceError(f"{where}: `{key}` 에 행 #{pid} 가 없다. 후보 — {_avail(cands, u)}")
        return hit[0]
    hit = [pv for pv in cands if _matches(pv, cons)]
    if not hit:
        shown = ", ".join(f"{k}={v}" for k, v in cons.items())
        raise ChoiceError(f"{where}: `{key}` 에 `{shown}` 를 만족하는 후보가 없다. "
                          f"후보 — {_avail(cands, u)}")
    return hit[0]          # 좁힌 안에서 다시 대표 규칙(cands 가 이미 그 순서다)


def choice_note(key: str, pv, default_pv, sel, u: UnitSystem) -> str:
    """고른 것을 카드에 남긴다 — **무엇을 왜 골랐는지가 카드에 있어야 재현된다.**"""
    f, unit = slot_scale(key, u)
    lab = _SLOT_LABEL.get(key, key)
    unit_s = f" {unit}" if unit else ""
    was = (f"기본 {_fmt(default_pv.value_num * f)}{unit_s} #{default_pv.id}"
           if default_pv is not None else "기본 대표값 없음")
    return (f"{lab} ← `{_clip(str(sel), 46)}` : {_fmt(pv.value_num * f)}{unit_s} "
            f"#{pv.id} ({was})")


def direction_options(cands: list, chosen, u: UnitSystem, limit: int = 2) -> str | None:
    """같은 칸에 **방향이 다른 후보**가 있으면 값과 손잡이(#행번호)를 낸다.

    §462 는 E 와 PR 의 방향이 어긋났을 때 경고를 박았다. 그런데 라이브에서 그 검사가
    걸리는 39종 중 방향이 **실제로 다른 것은 1종뿐**이다(2361 열분해 흑연: 면내 basal E 대
    두께방향 c축 PR). 나머지 38종은 같은 방향을 다르게 적은 것이다 —
    `'MD'` 대 `'in-plane (biaxially oriented film; MD/TD not distinguished by the source)'`,
    `'not stated in source (bulk)'` 대 `'not stated in source (bulk, isotropic assumption)'`.
    255종의 자유형식 문자열을 분류하는 대신 **후보를 그대로 보여준다** — 판단은 해석자가 한다.
    """
    if chosen is None:
        return None
    mine = _direction(chosen).strip().lower()
    alts = [pv for pv in cands
            if pv.id != chosen.id and _direction(pv).strip().lower() != mine
            and _differs_rel(chosen.value_num, pv.value_num)]
    if not alts:
        return None
    f, unit = slot_scale(chosen.property_key, u)
    unit_s = f" {unit}" if unit else ""
    bits = [f"`{_clip(_direction(pv) or '(방향 미표기)', 30)}` "
            f"{_fmt((pv.value_num or 0) * f)}{unit_s} #{pv.id}" for pv in alts[:limit]]
    more = f" 외 {len(alts) - limit}건" if len(alts) > limit else ""
    return " · ".join(bits) + more


# 방향 후보를 셀 때 반올림 쌍둥이는 세지 않는다(`catalog_compare._TIE_REL_TOL` 과 같은 잣대).
_ALT_REL_TOL = 0.01


def _differs_rel(a, b) -> bool:
    if a is None or b is None:
        return a is not b
    m = max(abs(a), abs(b))
    return m > 0 and abs(a - b) / m > _ALT_REL_TOL


def choice_catalog(cands: dict[tuple, list], material_ids: list[int],
                   u: UnitSystem, limit: int = 8) -> dict:
    """후보가 둘 이상인 칸만 골라 (재료 → 슬롯 → 후보목록)으로 낸다.

    **덱을 뽑은 그 호출이 "무엇을 더 고를 수 있었는지" 를 같이 돌려준다** — 그래야
    새 조회 경로 없이 두 걸음(기본으로 뽑고 → 후보를 보고 → 지정해 다시 뽑기)이 닫힌다.
    """
    out: dict[str, dict] = {}
    for mid in material_ids:
        slots: dict[str, list] = {}
        for key in CHOOSABLE_KEYS:
            rows = cands.get((mid, key)) or []
            if len(rows) < 2:
                continue
            f, unit = slot_scale(key, u)
            slots[key] = [{
                "id": pv.id, "slot": _SLOT_LABEL.get(key, key),
                "value_si": pv.value_num, "value_card": pv.value_num * f,
                "unit_card": unit or pv.unit, "tier": pv.quality_tier,
                "method": pv.method, "conditions": pv.conditions,
                "representative": pv.id == rows[0].id,
                "select": f"#{pv.id}",
            } for pv in rows[:limit]]
        if slots:
            out[str(mid)] = slots
    return out


_DEFAULT_NU = 0.3
# 점탄성 카드에서 포아송비도 저장 BULK도 없을 때. 엘라스토머 기준(폼이면 더 낮다).
_DEFAULT_NU_VISCO = 0.45
# CTE 상수 곡선의 온도 범위(K) — 상온 해석 범위를 넉넉히 덮는다.
CTE_CURVE_T_MIN, CTE_CURVE_T_MAX = 173.15, 673.15
# *DEFINE_CURVE LCID 시작번호(기존 모델 곡선과 충돌 피하려 큰 번호 사용).
CTE_LCID_BASE = 990001


def f_specific_heat(u: UnitSystem) -> float:
    """J/(kg*K) → 목표 단위. [비열]=length²/(time²·K)."""
    return u.time_s ** 2 / u.length_m ** 2


def _base_symbols(u: UnitSystem) -> tuple[str, str, str]:
    """(질량, 길이, 시간) 기호. density_unit("tonne/mm^3")과 key에서 뽑는다."""
    mass, _, rest = u.density_unit.partition("/")
    length = rest.split("^")[0]
    time = u.key.rsplit("_", 1)[-1]
    return mass, length, time


def hc_unit(u: UnitSystem) -> str:
    """비열의 목표 단위 표기. [비열]=length²/(time²·K)."""
    _, L, T = _base_symbols(u)
    return f"{L}^2/({T}^2*K)"


def tc_unit(u: UnitSystem) -> str:
    """열전도율의 목표 단위 표기. [열전도]=mass·length/(time³·K)."""
    M, L, T = _base_symbols(u)
    return f"{M}*{L}/({T}^3*K)"


def f_conductivity(u: UnitSystem) -> float:
    """W/(m*K) → 목표 단위. [열전도]=mass·length/(time³·K)."""
    return u.time_s ** 3 / (u.mass_kg * u.length_m)


def resolve_materials_fuzzy(db: Session, tokens: list) -> tuple[list[dict], list[str]]:
    """이름/ID 토큰 → 재료 목록. 정확→부분→유사(difflib) 순으로 매칭한다.

    반환: ([{id,name,matched_by,query}], 미해결 메시지 리스트). 이름만 줘도 유사검색으로 찾는다.
    """
    all_mats = db.execute(select(Material)).scalars().all()
    by_name = {m.name: m for m in all_mats}
    lower = {m.name.lower(): m for m in all_mats}
    out: list[dict] = []
    errors: list[str] = []
    seen: set[int] = set()

    def _add(m: Material, how: str, q: str):
        if m.id not in seen:
            seen.add(m.id)
            out.append({"id": m.id, "name": m.name, "matched_by": how, "query": q})

    for tok in tokens:
        s = str(tok).strip()
        if not s:
            continue
        if s.isdigit():
            m = db.get(Material, int(s))
            _add(m, "id", s) if m else errors.append(f"id {s}: 재료 없음")
            continue
        if s in by_name:
            _add(by_name[s], "exact", s)
            continue
        if s.lower() in lower:
            _add(lower[s.lower()], "exact", s)
            continue
        sub = [m for m in all_mats if s.lower() in m.name.lower()]
        if len(sub) == 1:
            _add(sub[0], "substring", s)
            continue
        if len(sub) > 1:
            # 부분일치 다수 → 가장 유사한 것 채택(질의가 모호해도 진행).
            best = max(sub, key=lambda m: difflib.SequenceMatcher(
                None, s.lower(), m.name.lower()).ratio())
            _add(best, f"substring({len(sub)}건 중 최유사)", s)
            continue
        # 유사 검색(오타·약칭 대응).
        names = [m.name for m in all_mats]
        cand = difflib.get_close_matches(s, names, n=1, cutoff=0.5)
        if cand:
            _add(by_name[cand[0]], "fuzzy", s)
        else:
            errors.append(f"'{s}': 유사한 재료 없음")
    return out, errors


def _fmt(v: float) -> str:
    """LS-DYNA 필드용 수치 포맷(10자 폭에 맞춘 유효자리)."""
    if v == 0:
        return "0.0"
    a = abs(v)
    if a >= 1e5 or a < 1e-3:
        return f"{v:.4e}".replace("e-0", "e-").replace("e+0", "e+")
    return f"{v:.6g}"


# 해석 결과를 좌우하는 조건만 골라 짧게 붙인다(전부 붙이면 주석이 못 읽게 길어진다).
# 율속 축은 표기가 둘이다 — `strain_rate_s` 를 빠뜨려 SAC105 카드가 10/s 값을 율속 표시
# 없이 싣고 있었다(47차 IA). 카탈로그 실측 어휘는 `strain_rate_s` 쪽이 더 많다.
# `direction` 이 빠져 있었다(51차 MC). 카드 슬롯 9칸의 조건 중 `direction` 이 1,546행으로
# 온도(temperature_c 1,569) 다음이고 `axis`(983)보다 많은데, 출처 태그에도 동률 주석에도
# 안 나갔다 — §462 가 경고를 박은 바로 그 축이 정작 카드에서 안 보였다.
_COND_SHOW = (("strain_rate_1/s", "ε̇", "/s"), ("strain_rate_s", "ε̇", "/s"),
              ("temperature_C", "T", "°C"),
              ("temperature_K", "T", "K"), ("temperature_k", "T", "K"),
              ("direction", "", ""),
              ("axis", "", ""), ("regime", "", ""), ("grade", "", ""))


def _cond_tag(cond) -> str:
    """대표값의 핵심 조건을 " (ε̇ 0.001/s, T 23°C)" 형태로."""
    if isinstance(cond, str):
        try:
            cond = json.loads(cond)
        except Exception:
            return ""
    if not isinstance(cond, dict):
        return ""
    bits = []
    for k, label, unit in _COND_SHOW:
        if k in cond and cond[k] is not None:
            v = cond[k]
            bits.append(f"{label} {v}{unit}".strip() if label else _clip(str(v), 24))
        if len(bits) >= 3:
            break
    return f"  ({', '.join(bits)})" if bits else ""


def _clip(s: str, n: int) -> str:
    """n자로 자르되 단어 중간에서 끊지 않는다. 잘렸으면 …를 붙여 잘림을 드러낸다."""
    s = " ".join((s or "").split())
    if len(s) <= n:
        return s
    cut = s[:n]
    sp = cut.rfind(" ")
    return (cut[:sp] if sp > n * 0.6 else cut).rstrip(" ,;-") + "…"


def _fit10(s: str) -> str:
    """LS-DYNA 고정폭(10칸)에 맞추되 **9자 이하**로 줄여 항상 구분 공백을 남긴다.

    10칸 초과는 필드가 밀려 덱 파싱이 깨진다. 딱 10자면 파싱은 되지만 옆 필드와 붙어
    ("       2015.9000e-10") 사람이 읽을 수 없고, 자유형식으로 옮기면 실제로 깨진다.
    """
    if len(s) <= 9:
        return s
    try:
        v = float(s)
    except ValueError:
        return s[:9]
    for p in (4, 3, 2, 1):
        t = f"{v:.{p}e}".replace("e-0", "e-").replace("e+0", "e+")
        if len(t) <= 9:
            return t
    return f"{v:.0e}"[:9]


def _card_field(*vals) -> str:
    """10칸 고정폭 필드 행(초과 값은 자동 보정)."""
    return "".join(f"{_fit10(str(v)):>10s}" for v in vals)


# "101, 재료이름" / "101:이름" / "101=이름" 한 행. 앞이 정수면 MID 지정으로 본다.
_ROW_RE = re.compile(r"^(\d+)\s*[,:=]\s*(.+)$")
# "101, 5, 재료이름" / "101, 5;6;7, 이름" — MID, PID(들), 이름 3열. PID는 CTE 카드에 쓰인다.
_ROW3_RE = re.compile(r"^(\d+)\s*[,:=]\s*([\d;\s]+?)\s*[,:=]\s*(.+)$")


def _parse_pids(s) -> list[int]:
    """PID 표기('5' / '5;6;7' / [5,6])를 정수 리스트로."""
    if s is None:
        return []
    if isinstance(s, (list, tuple)):
        out = []
        for x in s:
            try:
                out.append(int(x))
            except (TypeError, ValueError):
                pass
        return out
    return [int(p) for p in re.split(r"[;\s,]+", str(s).strip()) if p.isdigit()]


def _rows(items) -> list:
    """입력을 행 단위로 펼친다 — 여러 줄 붙여넣기(표)와 리스트를 모두 받는다.

    문자열에 줄바꿈이 있으면 행으로 분리하고, 'MID, 이름' 형태가 아닌 행은
    콤마로 나눠 이름 여러 개로 본다("A,B,C" 처럼 이름만 나열한 경우).
    """
    out: list = []
    seq = items if isinstance(items, (list, tuple)) else [items]
    for it in seq:
        if isinstance(it, dict):
            out.append(it)
            continue
        s = str(it)
        for line in s.splitlines():
            line = line.strip().lstrip("﻿")
            if not line or line.startswith("#"):
                continue
            if _ROW_RE.match(line):
                out.append(line)            # "101, 이름" — 통째로 한 행.
            elif "," in line:
                out.extend(p.strip() for p in line.split(",") if p.strip())
            else:
                out.append(line)
    return out


def parse_items(items: list) -> tuple[list, list[int | None], list[list[int]], list[dict], list[str]]:
    """입력 항목에서 (재료토큰, 지정 MID, PID 목록, 후보 지정)을 뽑는다. 미지정은 None/빈 것.

    지원 형식 — "이름" / 12(카탈로그 id) / "101, 이름" / "101:이름" / "101=이름" /
    "101, 5, 이름"(MID·PID·이름) / "101, 5;6;7, 이름"(여러 PID) /
    {"mid":101,"pid":5,"material":"이름"} / 여러 줄 문자열(표 붙여넣기).
    지정한 MID는 그대로 카드에 쓰이고, PID가 있으면 CTE(*MAT_ADD_THERMAL_EXPANSION)를 만든다.

    **후보 지정은 dict 항목에만 붙는다** — `{"material": 73, "choices": {"mechanical.
    youngs_modulus": "direction=in-plane"}}`. 붙여넣기 텍스트에는 문법을 만들지 않았다:
    행 문법("101, 5;6;7, 이름")에 조건식을 끼우면 재료 이름의 콤마와 구별이 안 된다.
    여러 재료에 같은 지정을 걸려면 `build_cards(choices=…)` 를 쓴다.
    """
    toks: list = []
    mids: list[int | None] = []
    pids: list[list[int]] = []
    chs: list[dict] = []
    errs: list[str] = []
    for it in _rows(items):
        if isinstance(it, dict):
            m = it.get("mid", it.get("MID"))
            t = it.get("material", it.get("name", it.get("id")))
            if t is None:
                errs.append(f"{it}: material 키가 없음")
                continue
            try:
                mids.append(int(m) if m is not None else None)
            except (TypeError, ValueError):
                errs.append(f"{it}: mid가 정수가 아님")
                continue
            ch = it.get("choices") or {}
            if not isinstance(ch, dict):
                raise ChoiceError(f"{t}: choices 는 {{물성키: 선택자}} 형태여야 한다 — {ch!r}")
            pids.append(_parse_pids(it.get("pids", it.get("pid", it.get("PID")))))
            chs.append(dict(ch))
            toks.append(t)
            continue
        s = str(it).strip()
        if not s:
            continue
        # "101, 5, 이름" — MID·PID·이름 3열 우선 검사.
        m3 = _ROW3_RE.match(s)
        if m3:
            mids.append(int(m3.group(1)))
            pids.append(_parse_pids(m3.group(2)))
            chs.append({})
            toks.append(m3.group(3).strip())
            continue
        # "101, 이름" / "101:이름" / "101=이름" — 앞이 정수면 MID 지정으로 해석.
        m = _ROW_RE.match(s)
        if m:
            mids.append(int(m.group(1)))
            pids.append([])
            chs.append({})
            toks.append(m.group(2).strip())
        else:
            mids.append(None)
            pids.append([])
            chs.append({})
            toks.append(s)
    return toks, mids, pids, chs, errs


def assign_mids(explicit: list[int | None], mid_start: int) -> tuple[list[int], list[str]]:
    """지정 MID는 그대로 두고, 미지정은 mid_start부터 빈 번호를 채운다(중복 금지)."""
    used = {m for m in explicit if m is not None}
    warns: list[str] = []
    seen: set[int] = set()
    for m in explicit:
        if m is not None:
            if m in seen:
                warns.append(f"MID {m} 중복 지정 — LS-DYNA는 고유 MID를 요구합니다")
            seen.add(m)
    out: list[int] = []
    nxt = int(mid_start)
    for m in explicit:
        if m is not None:
            out.append(m)
        else:
            while nxt in used:
                nxt += 1
            used.add(nxt)
            out.append(nxt)
            nxt += 1
    return out, warns


def match_rows(db: Session, tokens: list, mid_start: int = 1, limit: int = 6) -> dict:
    """붙여넣은 행 → 행마다 후보 재료 목록(매칭도·물성보유 포함). 사용자가 고르게 하는 프리뷰용.

    반환: {rows:[{mid, mid_source, query, candidates:[{material_id,name,score,matched_by,
    manufacturer,n_properties,has_mechanical,has_thermal}]}], errors}
    """
    toks, explicit, pid_lists, _chs, errs = parse_items(list(tokens or []))
    mid_list, warns = assign_mids(explicit, mid_start)
    all_mats = db.execute(select(Material)).scalars().all()

    # 물성 보유 여부(카드 생성 가능성)를 미리 계산.
    reps = representative_numeric(db, list(sorted(set(MECH_KEYS + THERM_KEYS))))
    n_props: dict[int, int] = {}
    for mid_, key in db.execute(select(PropertyValue.material_id, PropertyValue.property_key)).all():
        n_props[mid_] = n_props.get(mid_, 0) + 1

    def _info(m: Material, score: float, how: str) -> dict:
        a = m.attributes or {}
        has_mech = reps.get(K_RHO, {}).get(m.id) is not None and reps.get(K_E, {}).get(m.id) is not None
        has_th = all(reps.get(k, {}).get(m.id) is not None for k in (K_RHO, K_HC, K_TC))
        return {"material_id": m.id, "name": m.name, "score": round(score, 3),
                "matched_by": how, "manufacturer": a.get("manufacturer"),
                "grade": a.get("grade"), "category": m.category,
                "n_properties": n_props.get(m.id, 0),
                "has_mechanical": has_mech, "has_thermal": has_th}

    rows = []
    for tok, mid, exp, pl in zip(toks, mid_list, explicit, pid_lists):
        s = str(tok).strip()
        cands: list[dict] = []
        if s.isdigit():
            m = db.get(Material, int(s))
            if m:
                cands = [_info(m, 1.0, "id")]
        else:
            sl = s.lower()
            scored = []
            for m in all_mats:
                nl = m.name.lower()
                if nl == sl:
                    sc, how = 1.0, "exact"
                elif sl in nl:
                    # 부분일치는 이름 길이 대비 비중으로 점수화.
                    sc, how = 0.75 + 0.2 * (len(sl) / max(len(nl), 1)), "substring"
                else:
                    r = difflib.SequenceMatcher(None, sl, nl).ratio()
                    if r < 0.45:
                        continue
                    sc, how = r * 0.9, "fuzzy"
                scored.append((sc, how, m))
            scored.sort(key=lambda x: (-x[0], x[2].name))
            cands = [_info(m, sc, how) for sc, how, m in scored[:limit]]
        rows.append({"mid": mid, "mid_source": "지정" if exp is not None else "자동",
                     "pids": pl, "query": s, "candidates": cands,
                     "unmatched": len(cands) == 0})
    return {"rows": rows, "errors": errs, "mid_warnings": warns}



_RATE_COND = "strain_rate_s"
_TEMP_COND = ("temperature_C", "temperature_c", "temperature_K", "temperature_k")
_ROOM_C = 25.0
_NO_TEMP_PENALTY = 5.0      # 무표기가 상온 명시값을 이기면 안 된다(catalog_compare와 같은 규칙)


def _cond_temp_c(cond: dict):
    """조건의 온도를 °C 하나로 모은다. C/K 표기가 섞여 들어오기 때문이다."""
    for key, to_c in (("temperature_C", lambda v: v), ("temperature_c", lambda v: v),
                      ("temperature_K", lambda v: v - 273.15),
                      ("temperature_k", lambda v: v - 273.15)):
        v = cond.get(key)
        if isinstance(v, (int, float)):
            return round(float(to_c(float(v))), 1)
    return None


# 계열을 가르지 **않는** 조건 — 재료의 상태가 아니라 측정을 서술하는 것들.
#   crosshead_speed_mm_min: 율속을 다른 단위로 다시 쓴 것뿐이다(PA6-GF30 6점이 이것 때문에 갈렸다).
#   test / loading: 시험 방법. 율속 곡선은 준정적 인장 + SHPB를 잇는 것이 표준 구성이라
#     여기서 끊으면 SAC305가 정적 앵커(38 MPa)를 잃고 압축 구간만 남는다.
#     다만 인장·압축이 섞이면 카드 주석에 그 사실을 적는다 — 폼·폴리머는 비대칭이 크다.
#
# **반복시험(replicate)·시편묶음(specimen_group)은 여기 넣지 않는다.** 넣으면 같은 율속에
# 점이 둘씩 생겨 가로축이 중복되고 곡선이 지그재그가 된다(Ti Grade1 Test-1/Test-2 8점).
# 평균을 내면 원문에 인쇄되지 않은 숫자가 되므로, 한 계열만 골라 쓴다.
# `test_method`·`instrument`·`procedure`도 여기다. 율속 스윕은 원래 **장비를 갈아타며** 만든다 —
# 준정적은 만능시험기, 동적은 SHPB다. 장비가 계열을 가르면 5데케이드짜리 스윕이 두 토막 난다.
# (E-44 에폭시가 실제로 그랬다. 같은 Φ5x5 시편·같은 25 °C·같은 논문인데 3점+3점으로 갈렸다.)
# 계열을 정하는 것은 **하중 모드**(인장/압축/전단)이지 장비가 아니다. 모드가 섞이면
# rate_series_modes()가 카드 주석에 그 사실을 적는다 — 막지 않고 드러낸다.
_DESCRIPTIVE_COND = frozenset((
    "crosshead_speed_mm_min", "apparatus", "test", "loading", "temperature_stated",
    "test_method", "instrument", "procedure", "test_standard"))
_MODE_COND = ("test", "loading", "test_method")


def _series_key(cond: dict, drop_replicate: bool = False) -> tuple:
    """율속과 측정 서술을 뺀 **나머지 조건 전부**가 하나의 곡선을 정한다.

    온도만 볼 수는 없다. Kapton HN은 같은 298 K에서 ID·TD 두 방향을 재고, 금속은 같은 온도에서
    열처리·결정립이 갈린다. 이것들을 한 곡선에 섞으면 가로축이 중복되고 배율이 1.0 → 0.94로
    거꾸로 가는 *DEFINE_CURVE가 나온다. 축을 열거하는 대신 나머지를 통째로 비교한다.
    """
    skip = set(_DESCRIPTIVE_COND) | ({"replicate"} if drop_replicate else set())
    rest = tuple(sorted(
        (k, json.dumps(v, sort_keys=True, ensure_ascii=False))
        for k, v in cond.items()
        if k != _RATE_COND and k not in _TEMP_COND and k not in skip))
    return (_cond_temp_c(cond), rest)


# 전단 항복(비틀림 시험 τ_0max)은 *MAT_024의 SIGY가 아니다. LCSR은 배율 곡선이라 비만 쓰면
# 될 것 같지만, 코드가 SIGY를 곡선 기준값으로 **다시 맞추기** 때문에 전단값이 인장 SIGY 자리에
# 그대로 들어간다. PMMA는 τ 74.1 MPa인데 von Mises로 σ ≈ 128 MPa라 그럴듯해 보여 더 위험하다.
# 값은 카탈로그에 남기되 LCSR 계열에서는 뺀다.
_SHEAR_WORDS = ("torsion", "shear", "비틀림", "전단")


def _is_shear_yield(cond: dict) -> bool:
    if not isinstance(cond, dict):
        return False
    s = " ".join(str(cond.get(k) or "") for k in
                 ("test", "loading", "stress_definition", "definition")).lower()
    return any(w in s for w in _SHEAR_WORDS)


def rate_series_modes(rows: list) -> list[str]:
    """고른 계열이 몇 가지 시험 방법을 섞고 있는지 — 카드 주석에 적기 위한 것."""
    modes = {str(r.conditions.get(k)) for r in rows
             for k in _MODE_COND
             if isinstance(r.conditions, dict) and r.conditions.get(k)}
    return sorted(modes)


# ── 카탈로그 Prony → *MAT_GENERAL_VISCOELASTIC (076) ────────────────────────────────
# 076은 Prony 급수를 **최대 18항**까지 직접 받는다(LS-DYNA Keyword Manual Vol II, MAT_076:
# "a general viscoelastic Maxwell model having up to 18 terms in the prony series expansion").
# 카드는 GI(전단 완화계수 Pa) · BETAI(전단 감쇠상수 1/s) · KI(체적 완화계수 Pa) · BETAKI 네 열이고,
# "The number of terms for the shear behavior may differ from that for the bulk behavior:
#  simply insert zero if a term is not included."
#
# 단일항 *MAT_VISCOELASTIC(006)은 업로드된 완화시험만 소비한다. 문헌에서 모은 11~25항 세트는
# 여기로 나가야 한다.
K_PR_TAU = "mechanical.prony_relaxation_time"
K_PR_G = "mechanical.prony_shear_modulus"
K_PR_GREL = "mechanical.prony_relative_modulus"
K_PR_E = "mechanical.prony_tensile_modulus"
K_PR_K = "mechanical.prony_bulk_modulus"
K_PR_KREL = "mechanical.prony_relative_bulk_modulus"
K_G0 = "mechanical.shear_modulus"
K_K0 = "mechanical.bulk_modulus"
PRONY_MAX_TERMS = 18

_TERM_NUM = re.compile(r"(\d+)$")


def _term_index(cond: dict):
    """항 번호. term_index가 우선이고, 없으면 term 문자열 끝의 숫자('tau3' → 3)를 쓴다."""
    if isinstance(cond.get("term_index"), int):
        return cond["term_index"]
    m = _TERM_NUM.search(str(cond.get("term") or ""))
    return int(m.group(1)) if m else None


def _prony_set_key(cond: dict) -> str:
    """어느 세트에 속하는가. set_id가 있으면 그것, 없으면 항 표기를 뺀 조건 전체.

    VHB 4910은 한 재료에 **서로 경쟁하는 구성모델이 7개** 들어 있다(generalized Maxwell M1/M2,
    Kelvin-Voigt M1/M2, eight-chain 계열 …). 이걸 한 카드에 섞으면 물리적으로 무의미하다.
    """
    if cond.get("set_id"):
        return str(cond["set_id"])
    rest = {k: v for k, v in cond.items() if k not in ("term", "term_index")}
    return json.dumps(rest, sort_keys=True, ensure_ascii=False)


def prony_series(db: Session, mid: int) -> dict | None:
    """카탈로그 Prony → 076용 항 목록. 만들 수 없으면 사유를 담은 dict를 돌려준다.

    반환 {"terms": [(GI, BETAI, KI, BETAKI)], "note": [...], "set": str, "n_src": int}
    또는 {"reason": "..."} — 카드를 못 만드는 이유.
    """
    keys = (K_PR_TAU, K_PR_G, K_PR_GREL, K_PR_E, K_PR_K, K_PR_KREL)
    rows = db.execute(select(PropertyValue).where(
        PropertyValue.material_id == mid,
        PropertyValue.property_key.in_(keys),
        PropertyValue.value_num.isnot(None))).scalars().all()
    if not rows:
        return None
    sets: dict[str, dict[str, dict[int, float]]] = {}
    for pv in rows:
        cond = pv.conditions if isinstance(pv.conditions, dict) else {}
        i = _term_index(cond)
        if i is None:
            continue
        sets.setdefault(_prony_set_key(cond), {}).setdefault(
            pv.property_key, {})[i] = float(pv.value_num)

    rep = representative_numeric(db, [K_G0, K_K0, K_NU, K_E])
    g0 = rep.get(K_G0, {}).get(mid)
    k0 = rep.get(K_K0, {}).get(mid)
    nu = rep.get(K_NU, {}).get(mid)

    # G0가 인쇄돼 있지 않은 재료가 많다. 등방 정의식 G=E/2(1+ν)로 채운다 —
    # 아래 E_i/2(1+ν) 경로, BULK의 K=E/(3(1-2ν)) 경로와 같은 근거다.
    # DB에는 이렇게 만든 값을 저장하지 않는다(역산 금지). 카드에서만 쓰고 주석에 남긴다.
    g0_why = "G0 실측"
    if g0 is None and nu is not None and nu < 0.5:
        e_inst = rep.get(K_E, {}).get(mid)
        if e_inst:
            g0 = e_inst / (2.0 * (1.0 + nu))
            g0_why = f"G0=E/(2(1+ν)), E={_fmt(e_inst / 1e9)} GPa, ν={nu:g}"

    # 전단항을 만드는 경로 — 절대값이 있으면 그대로, 없으면 정의식으로 환산한다.
    # 환산은 그 모델의 정의(G_i = g_i·G0, G_i = E_i/2(1+ν))를 적용하는 것이지 역산이 아니다.
    # 다만 어느 경로를 썼는지 카드 주석에 반드시 남긴다.
    best = None
    for skey, d in sets.items():
        tau = d.get(K_PR_TAU) or {}
        if not tau:
            continue
        for src, conv, why in (
                (K_PR_G, (lambda v: v), "G_i 직접"),
                (K_PR_GREL, (lambda v: v * g0) if g0 else None,
                 "g_i × G0" if g0_why == "G0 실측" else f"g_i × G0 ({g0_why})"),
                (K_PR_E, (lambda v: v / (2.0 * (1.0 + nu))) if nu is not None else None,
                 "E_i / 2(1+ν)")):
            if conv is None or src not in d:
                continue
            shared = sorted(set(tau) & set(d[src]))
            if len(shared) < 2:
                continue
            cand = (len(shared), skey, src, conv, why, shared, d, tau)
            if best is None or cand[0] > best[0]:
                best = cand
            break                      # 한 세트에서는 우선순위가 높은 경로 하나만 쓴다
    if best is None:
        # 왜 못 만드는지 정확히 말한다. "Prony가 없다"와 "G0 하나가 없다"는 전혀 다른 문제고,
        # 후자는 숫자 하나만 채우면 카드가 열린다.
        have = {k for d in sets.values() for k in d}
        if K_PR_GREL in have and not g0:
            why = "상대계수 g_i는 있는데 **G0(shear_modulus)가 없어** 절대 전단항을 못 만든다"
        elif K_PR_E in have and nu is None:
            why = "인장항 E_i는 있는데 **포아송비가 없어** G_i로 환산할 수 없다"
        elif not any(k in have for k in (K_PR_G, K_PR_GREL, K_PR_E)):
            why = "완화시간 τ만 있고 대응하는 완화계수 항이 없다"
        else:
            why = "τ와 짝이 맞는 완화계수 항이 2개 미만이다(항번호 기준)"
        return {"reason": why}

    _, skey, src, conv, why, shared, d, tau = best
    notes = [f"전단항 경로: {why}"]
    if len(shared) > PRONY_MAX_TERMS:
        return {"reason": f"{len(shared)}항인데 *MAT_076의 상한은 {PRONY_MAX_TERMS}항이다 — "
                          "항을 버리면 완화 스펙트럼이 달라지므로 자동 절삭하지 않는다. "
                          "LCID(완화곡선) 경로로 내보내려면 별도 구현이 필요하다."}

    kabs, krel = d.get(K_PR_K) or {}, d.get(K_PR_KREL) or {}
    terms = []
    for i in shared:
        gi = conv(d[src][i])
        beta = 1.0 / tau[i] if tau[i] > 0 else 0.0
        if i in kabs:
            ki = kabs[i]
        elif i in krel and k0:
            ki = krel[i] * k0
        else:
            ki = 0.0                   # 매뉴얼: "simply insert zero if a term is not included"
        terms.append((gi, beta, ki, beta if ki else 0.0))
    if kabs:
        notes.append("체적항 K_i 직접")
    elif krel and k0:
        notes.append("체적항 k_i × K0")
    else:
        notes.append("체적항 없음 — KI·BETAKI를 0으로 둔다(매뉴얼 지시)")
    return {"terms": terms, "note": notes, "set": skey, "n_src": len(shared),
            "g0": g0, "k0": k0, "nu": nu}


def rate_scale_points(db: Session, mid: int) -> tuple[list[tuple[float, float]], float, object, list]:
    """율속별 항복강도 → LS-DYNA LCSR용 (변형률속도, 응력배율) 점 목록.

    LCSR은 변형률속도에 대한 **항복응력 배율** 곡선이다. 가장 느린 속도의 값을 1.0으로 잡고
    나머지를 그에 대한 비로 만든다. 온도·방향 등이 섞이면 율속 효과와 뒤엉키므로
    **조건이 완전히 같은 계열 하나만** 쓴다 — 상온에 가장 가까운 계열을 고른다.

    솔더처럼 T/Tm이 높은 재료는 이 곡선이 없으면 정적 항복만으로 충격을 풀게 되고,
    소성변형이 폭주해 요소가 뒤집힌다.
    """
    rows = db.execute(select(PropertyValue).where(
        PropertyValue.material_id == mid,
        PropertyValue.property_key == K_SIGY_RATE,
        PropertyValue.value_num.isnot(None))).scalars().all()
    if not rows:
        return [], 0.0, None, []
    # replicate가 무엇을 뜻하는지는 데이터가 정한다.
    #   Ti Grade1의 'Test-1'/'Test-2'는 **각각 전 율속을 도는 스윕**이라 계열을 갈라야 한다.
    #   Nickel 200의 'HO 4790'~'HO 4797'은 **시편 ID**로 각각 한 율속뿐이라, 계열을 가르면
    #   1점짜리 조각 9개가 되어 5데케이드짜리 스윕이 통째로 사라진다.
    # 판별 기준은 하나다 — **한 replicate 라벨이 여러 율속을 덮으면 스윕, 아니면 시편 ID.**
    _reps: dict[str, set] = {}
    for pv in rows:
        cond = pv.conditions if isinstance(pv.conditions, dict) else {}
        r, rate = cond.get("replicate"), cond.get(_RATE_COND)
        if r is not None and isinstance(rate, (int, float)):
            _reps.setdefault(str(r), set()).add(float(rate))
    rep_is_sweep = any(len(v) >= 2 for v in _reps.values())

    buckets: dict[tuple, list[tuple[float, float, object]]] = {}
    for pv in rows:
        cond = pv.conditions if isinstance(pv.conditions, dict) else {}
        rate = cond.get(_RATE_COND)
        if not isinstance(rate, (int, float)) or rate <= 0:
            continue
        if _is_shear_yield(cond):
            continue
        key = _series_key(cond, drop_replicate=not rep_is_sweep)
        buckets.setdefault(key, []).append((float(rate), float(pv.value_num), pv))
    # 곡선이 되려면 서로 다른 율속이 둘 이상이어야 한다.
    usable = {k: v for k, v in buckets.items() if len({p[0] for p in v}) >= 2}
    if not usable:
        return [], 0.0, None, []

    def _pick(k: tuple) -> tuple:
        t = k[0]
        return (_NO_TEMP_PENALTY if t is None else abs(t - _ROOM_C), -len(usable[k]))

    pts = sorted(usable[min(usable, key=_pick)], key=lambda x: x[0])
    # 같은 율속에 점이 둘 이상이면 *DEFINE_CURVE의 가로축이 중복돼 성립하지 않는다.
    # 평균을 내면 원문에 없는 숫자가 되므로, **인쇄된 값 중 최솟값 하나를 고른다.**
    # 모든 율속에 같은 규칙을 적용하므로 곡선 내부는 일관되고, 선택 사실은 카드에 적는다.
    dup = len(pts) != len({p[0] for p in pts})
    if dup:
        picked: dict[float, tuple] = {}
        for t in pts:
            if t[0] not in picked or t[1] < picked[t[0]][1]:
                picked[t[0]] = t
        pts = [picked[r] for r in sorted(picked)]
    base = pts[0][1]
    if base <= 0:
        return [], 0.0, None, []
    # 배율이 감소해도 곡선을 버리지 않는다 — Al2024-T3·Al5083-H116은 동적변형시효로
    # **음의 율속민감도(NSRS)** 를 실제로 보인다. 버리면 참값을 버리는 것이다.
    # 대신 카드 주석에 감소 사실을 적어 시편 산포와 구분해 판단하게 한다.
    # 기준 응력과 그 행을 함께 돌려준다 — 카드의 SIGY를 이 값으로 맞춰야 배율이 성립한다.
    return [(r, s / base) for r, s, _ in pts], base, pts[0][2], [p[2] for p in pts]

def build_cards(db: Session, tokens: list, card: str = "mechanical",
                units: str = "ton_mm_s", mid_start: int = 1,
                lcid_start: int = CTE_LCID_BASE, choices: dict | None = None,
                list_choices: bool = False) -> dict:
    """재료 리스트 → LS-DYNA 키워드 덱. card: mechanical|thermal|both.

    MID는 mid_start부터 순차 자동 배정. 각 카드에 출처(프로비넌스)를 $ 주석으로 남긴다.
    필수 물성이 없어 카드를 만들 수 없으면 조용히 기본값으로 채우지 않고 skipped에 보고한다.

    **후보 지정**(51차 MC) — `choices={물성키: 선택자}` 는 이 호출의 **모든 재료**에 걸리고,
    항목 dict 의 `"choices"` 는 그 재료에만 걸리며 앞의 것을 덮는다.
    선택자는 `"#4711"`(행번호) 또는 `"direction=in-plane"`(조건 부분일치)이다.
    **안 주면 지금과 똑같이 대표값을 쓴다.** 없는 후보를 주면 `ChoiceError` 로 거부한다 —
    대표값으로 조용히 떨어지지 않는다. 고른 것은 카드 주석(`※ 후보 지정`)에 남는다.

    지정은 **카드에 박히는 슬롯**(`CHOOSABLE_KEYS`)에만 건다. Prony(076)가 G0·K0 를
    유도할 때 쓰는 `shear_modulus`·`bulk_modulus` 는 대상이 아니다.

    `list_choices=True` 면 응답에 `candidates`(재료 → 슬롯 → 후보목록)를 함께 낸다 —
    기본으로 한 번 뽑고, 후보를 보고, 지정해 다시 뽑는 두 걸음이 새 조회 경로 없이 닫힌다.
    """
    u = get_system(units)
    toks, explicit, pid_lists, item_choices, parse_errs = parse_items(list(tokens or []))
    # 토큰별 개별 해석 — 같은 재료를 다른 MID로 중복 지정하는 경우를 허용(순서·중복 보존).
    mats: list[dict] = []
    keep_mid: list[int | None] = []
    keep_pids: list[list[int]] = []
    keep_choices: list[dict] = []
    errors: list[str] = list(parse_errs)
    for t, em, pl, ch in zip(toks, explicit, pid_lists, item_choices):
        got, errs = resolve_materials_fuzzy(db, [t])
        errors.extend(errs)
        if got:
            mats.append(got[0])
            keep_mid.append(em)
            keep_pids.append(pl)
            keep_choices.append({**(choices or {}), **ch})
    if not mats:
        return {"error": "해석할 재료가 없습니다", "resolution_errors": errors,
                "keyword": "", "materials": [], "skipped": []}
    mid_list, mid_warns = assign_mids(keep_mid, mid_start)
    explicit_set = {m for m in keep_mid if m is not None}

    ids = [m["id"] for m in mats]
    # LCSR 곡선의 원자료도 프로비넌스에 넣어야 한다 — 빠지면 곡선 출처가 '출처미상'으로 나온다.
    keys = sorted(set(MECH_KEYS + THERM_KEYS + (K_SIGY_RATE, K_PR_TAU, K_PR_G,
                                                 K_PR_GREL, K_PR_E, K_PR_K, K_PR_KREL)))
    reps = representative_numeric(db, list(keys))
    # 출처(프로비넌스) — 반드시 **대표값으로 뽑힌 그 행**의 출처를 쓴다.
    # (예전엔 아무 행이나 먼저 걸린 것을 달아, 값과 출처가 어긋날 수 있었다.)
    rep_rows = representative_rows(db, list(keys), material_ids=ids)
    # 카드에 실제로 박히는 네 칸만 동률을 본다 — 전 키를 훑으면 비용만 늘고 카드에 안 쓰인다.
    rep_ties = representative_ties(db, [K_RHO, K_E, K_NU, K_SIGY], material_ids=ids)
    # 완화시험이 있는 재료는 *MAT_VISCOELASTIC이 맞다 — 테이프·접착제를 탄성으로 내보내면
    # 하중률 의존이 통째로 빠진다. Prony 피팅 결과(lsdyna_prony)를 그대로 쓴다.
    visco: dict[int, dict] = {}
    for sp_mid, extra in db.execute(
            select(Specimen.material_id, ProcessedResult.extra_metrics)
            .join(Test, Test.specimen_id == Specimen.id)
            .join(ProcessedResult, ProcessedResult.test_id == Test.id)
            .where(Specimen.material_id.in_(ids))).all():
        em = extra or {}
        if em.get("kind") == "viscoelastic" and em.get("lsdyna_prony"):
            visco.setdefault(sp_mid, em)
    refs: list[dict] = []              # 덱 끝에 붙일 번호 매긴 참고문헌
    ref_no: dict[int, int] = {}        # source.id → 번호
    prov: dict[tuple, str] = {}        # (mid, key) → "[n] 업체" 짧은 태그

    def _prov_tag(pv) -> str:
        """그 행의 출처를 참고문헌에 등록하고 짧은 태그를 만든다."""
        src = pv.source
        if src is None:
            return "출처미상"
        if src.id not in ref_no:
            ref_no[src.id] = len(refs) + 1
            refs.append({"n": len(refs) + 1, "publisher": src.publisher,
                         "title": src.title, "doi": src.doi, "url": src.url,
                         "kind": src.kind})
        short = (src.publisher or src.title or "").strip()
        tag = f"[{ref_no[src.id]}] {_clip(short, 40)}" if short else f"[{ref_no[src.id]}]"
        return f"{tag}{_cond_tag(pv.conditions)}"

    for (mid_, key_), pv in rep_rows.items():
        prov[(mid_, key_)] = _prov_tag(pv)

    # 후보 목록 — 지정을 해석하고, 방향이 갈린 칸을 카드에 드러내는 데 둘 다 쓴다(질의 한 번).
    cands: dict[tuple, list] = candidate_rows(db, ids)
    # 지정을 실제 행으로 해석한다. 항목마다 따로 — 같은 재료를 두 MID로 넣고
    # 한쪽은 면내, 한쪽은 두께방향으로 뽑는 쓰임이 실재한다(등방 카드 둘로 이방을 근사).
    picked: list[dict] = []
    for m, ch in zip(mats, keep_choices):
        one: dict = {}
        for key, sel in (ch or {}).items():
            if key not in CHOOSABLE_KEYS:
                raise ChoiceError(
                    f"{m['name']}: `{key}` 는 카드 슬롯이 아니다 — 고를 수 있는 키는 "
                    + ", ".join(CHOOSABLE_KEYS))
            pv = resolve_choice(cands.get((m["id"], key)) or [], key, sel, u, m["name"])
            one[key] = {"pv": pv, "selector": sel,
                        "default": rep_rows.get((m["id"], key))}
        picked.append(one)

    def val(mid: int, key: str):
        pv = cur_choice.get(key)
        return pv["pv"].value_num if pv else reps.get(key, {}).get(mid)

    def slot_notes(i: int, key: str) -> list[str]:
        """한 칸에 붙는 주석 — 고른 것(지정)과 **방향이 다른 후보**를 드러낸다.

        둘 다 자동으로 고르지 않는다(§462 와 같은 방식). 카드는 그대로 선다.
        """
        if key in noted:
            return []            # card="both" 면 RO 가 두 카드에 다 나온다 — 주석은 한 번만
        noted.add(key)
        out: list[str] = []
        ent = cur_choice.get(key)
        if ent is not None:
            out.append("$   ※ 후보 지정 — " + choice_note(key, ent["pv"], ent["default"],
                                                       ent["selector"], u))
        alt = direction_options(cands.get((i, key)) or [], rep_rows.get((i, key)), u)
        if alt:
            out.append(f"$   ※ {_SLOT_LABEL.get(key, key)} 의 다른 방향 후보 — {alt}")
        return out

    want_mech = card in ("mechanical", "both")
    want_therm = card in ("thermal", "both")

    lines: list[str] = ["*KEYWORD",
                        "$" + "=" * 78,
                        "$ MaterialTwinWeb — LS-DYNA 재료카드 자동 생성",
                        f"$ 단위계: {u.label}  (응력 {u.stress_unit}, 밀도 {u.density_unit})",
                        f"$ 카드종류: {card}",
                        "$ 각 물성 아래 $ 주석은 출처(프로비넌스)입니다.",
                        "$ 후보가 여럿인 칸은 `※` 주석에 다른 후보와 행번호(#id)를 적었습니다 —",
                        "$ 그 후보로 다시 뽑으려면 choices 에 {'mechanical.youngs_modulus': '#4711'}"
                        " 처럼 지정하세요.",
                        "$" + "=" * 78]
    table: list[dict] = []
    skipped: list[dict] = []
    parts: list[dict] = []
    lcid_next = [int(lcid_start)]
    lcid_by_mat: dict[int, int] = {}
    cur_choice: dict = {}
    noted: set = set()
    prov_restore: list[tuple] = []
    for m, mid, pids, cur_choice in zip(mats, mid_list, keep_pids, picked):
        i = m["id"]
        noted = set()
        # 앞 항목의 지정을 되돌린다 — 같은 재료가 다른 지정으로 두 번 올 수 있다.
        for _k, _p, _r in prov_restore:
            if _p is None:
                prov.pop(_k, None)
            else:
                prov[_k] = _p
            if _r is None:
                rep_rows.pop(_k, None)
            else:
                rep_rows[_k] = _r
        prov_restore = []
        # 고른 행이 값·출처·방향 검사 **전부**의 원천이 되게 갈아 끼운다.
        # 값만 바꾸고 출처를 그대로 두면 값과 출처가 어긋나는 옛 사고가 재발한다.
        for _key, _ent in cur_choice.items():
            prov_restore.append(((i, _key), prov.get((i, _key)), rep_rows.get((i, _key))))
            prov[(i, _key)] = _prov_tag(_ent["pv"])
            rep_rows[(i, _key)] = _ent["pv"]
        rho, E, nu = val(i, K_RHO), val(i, K_E), val(i, K_NU)
        sigy, uts, elong = val(i, K_SIGY), val(i, K_UTS), val(i, K_ELONG)
        hc, tc, cte = val(i, K_HC), val(i, K_TC), val(i, K_CTE)
        # 용융 상태 값은 열해석 카드에 쓸 수 없다. 벤더가 사출 충전 해석용으로 싣는 값이라
        # 수치대가 고체와 비슷해(Stanyl TE250F6 용융 k=0.344) 그대로 나가면 조용히 틀린다.
        # 대표값 순위에서 이미 뒤로 보내지만, 고체값이 아예 없으면 그래도 뽑히므로 여기서 끊는다.
        melt_dropped: list[str] = []
        for _k, _name in ((K_HC, "비열"), (K_TC, "열전도율")):
            _row = rep_rows.get((i, _k))
            if _row is not None and is_non_solid(_row.conditions):
                melt_dropped.append(_name)
                if _k == K_HC:
                    hc = None
                else:
                    tc = None
        made: list[str] = []
        title = " ".join(re.sub(r"[^\x20-\x7E가-힣]", " ", m["name"]).split())[:70]

        # ── 기계 카드 ──
        # 카탈로그 Prony(문헌에서 모은 다항 세트)가 먼저다. 업로드된 완화시험은 단일항이라
        # *MAT_VISCOELASTIC(006)으로밖에 못 나가지만, 11~18항 세트는 076으로 온전히 담긴다.
        cat_prony = prony_series(db, i) if want_mech else None
        if want_mech and cat_prony and "terms" in cat_prony and rho is not None:
            ts = cat_prony["terms"]
            g0c, k0c, nuc = cat_prony["g0"], cat_prony["k0"], cat_prony["nu"]
            bulk = k0c
            bulk_why = "K0 실측"
            if bulk is None and g0c and nuc is not None and nuc < 0.5:
                bulk = 2.0 * g0c * (1.0 + nuc) / (3.0 * (1.0 - 2.0 * nuc))
                bulk_why = f"K=2G0(1+ν)/(3(1-2ν)), ν={nuc:g}"
            # 전단항을 E_i/2(1+ν)로 만드는 경로가 이미 있는데 체적 쪽만 없었다. 같은 등방관계이므로
            # 순간 영률이 있으면 K=E/(3(1-2ν))도 같은 근거로 쓴다. 이 한 줄이 MEMS 다이어태치
            # 에폭시(E0 2.7448 GPa · ν 0.37 → K0 3.52 GPa)의 카드를 연다.
            if bulk is None and nuc is not None and nuc < 0.5:
                e_inst = representative_numeric(db, [K_E]).get(K_E, {}).get(i)
                if e_inst:
                    bulk = e_inst / (3.0 * (1.0 - 2.0 * nuc))
                    bulk_why = f"K=E/(3(1-2ν)), E={_fmt(e_inst / 1e9)} GPa, ν={nuc:g}"
            if bulk is None:
                skipped.append({"material": m["name"], "card": "mechanical",
                                "reason": f"Prony {len(ts)}항은 있으나 체적탄성률(K0)도 "
                                          "포아송비도 없어 *MAT_076의 BULK를 채울 수 없다"})
            else:
                lines.append("$")
                lines.append(f"$ --- MID {mid}: {title} (점탄성 다항) ---")
                lines.append(f"$   카탈로그 Prony {len(ts)}항 — g(t)=Σ G_i·exp(-BETA_i·t)")
                lines.append(f"$   세트: {_clip(str(cat_prony['set']), 84)}")
                for nt in cat_prony["note"]:
                    lines.append(f"$   {nt}")
                lines.append(f"$   BULK {_fmt(bulk * u.f_stress)} {u.stress_unit} — {bulk_why}")
                lines.append(f"$   RO   {_fmt(rho * u.f_density)} {u.density_unit}"
                             f" (= {_fmt(rho)} kg/m^3)   <- {prov.get((i, K_RHO), '출처미상')}")
                lines += slot_notes(i, K_RHO)
                lines.append(f"$   출처 {prov.get((i, K_PR_TAU), '출처미상')}")
                lines.append("*MAT_GENERAL_VISCOELASTIC_TITLE")
                lines.append(title)
                lines.append("$#     mid       rho      bulk       pcf        ef      tref         a         b")
                lines.append(_card_field(str(mid), _fmt(rho * u.f_density),
                                         _fmt(bulk * u.f_stress), "0.0", "0.0", "0.0", "0.0", "0.0"))
                # 매뉴얼: "Insert a blank card here if constants are defined on cards 3,4,... below."
                lines.append("$ (blank card 2 — 계수를 아래 카드로 직접 준다)")
                lines.append("")
                lines.append("$#      gi     betai        ki    betaki")
                for gi, beta, ki, betak in ts:
                    lines.append(_card_field(_fmt(gi * u.f_stress), _fmt(beta * u.f_rate),
                                             _fmt(ki * u.f_stress), _fmt(betak * u.f_rate)))
                made.append(f"*MAT_GENERAL_VISCOELASTIC (076, {len(ts)}항)")
        elif want_mech and i in visco and rho is not None:
            em = visco[i]
            pr_ = em["lsdyna_prony"]          # 이미 MPa·1/s 기준(ton_mm_s)으로 저장돼 있다
            si = {k: (pr_[k] * 1e6 if k in ("G0", "GI", "BULK") else pr_[k]) for k in pr_}
            # 체적탄성률은 저장값을 믿지 않고 **카탈로그의 포아송비로 매번 산출**한다.
            # 저장된 BULK가 폼·써멀패드까지 비압축(nu≈0.5)으로 잡고 있어, 압축으로 쓰는
            # 가스켓의 접촉압력이 통째로 틀린다. nu=0.5는 체적잠김도 일으킨다.
            nu_k = min(float(nu), 0.499) if nu is not None else None   # 0.5는 특이점(체적잠김)
            if nu_k is None and si.get("BULK") is None:
                nu_k = _DEFAULT_NU_VISCO       # 저장값도 포아송비도 없으면 기본값으로 산출
            if nu_k is not None:
                si["BULK"] = 2.0 * si["G0"] * (1.0 + nu_k) / (3.0 * (1.0 - 2.0 * nu_k))
                bulk_note = (f"nu={nu_k:g}에서 산출 K=2G(1+nu)/(3(1-2nu))" if nu is not None
                             else f"포아송비·저장 BULK 모두 없어 기본 nu={nu_k:g}로 산출 — 폼이면 낮춰야 한다")
            else:
                bulk_note = "저장값"
            lines.append("$")
            lines.append(f"$ --- MID {mid}: {title} (점탄성) ---")
            lines.append("$   완화시험 Prony 피팅 — G(t)=GI+(G0-GI)·exp(-BETA·t)")
            lines.append(f"$   BULK {_fmt(si['BULK'] * u.f_stress)} {u.stress_unit} — {bulk_note}"
                         + (f"   <- {prov.get((i, K_NU), '출처미상')}" if nu is not None else
                            " (포아송비 미보유 — 저장값 그대로. 폼·패드면 비압축으로 과대평가될 수 있다)"))
            lines.append(f"$   RO   {_fmt(rho * u.f_density)} {u.density_unit}"
                         f" (= {_fmt(rho)} kg/m^3)   <- {prov.get((i, K_RHO), '출처미상')}")
            for _k in (K_RHO, K_NU):
                if val(i, _k) is not None:
                    lines += slot_notes(i, _k)
            lines.append(f"$   G0   {_fmt(si['G0'] * u.f_stress)} {u.stress_unit}"
                         f"   GI {_fmt(si['GI'] * u.f_stress)} {u.stress_unit}"
                         f"   BETA {_fmt(si['BETA'] * u.f_rate)} 1/{u.key.rsplit('_', 1)[-1]}")
            cs_c, cs_p = val(i, K_CS_C), val(i, K_CS_P)
            if cs_c and cs_p:
                lines.append(f"$   ※ 변형률속도 데이터 보유: C {_fmt(cs_c / u.f_rate)} 1/"
                             f"{u.key.rsplit('_', 1)[-1]}  p {_fmt(cs_p)}"
                             f"   <- {prov.get((i, K_CS_C), '출처미상')}")
                lines.append("$     *MAT_VISCOELASTIC(006)에는 율속 경화 항이 없어 반영되지 않는다. "
                             "충격·낙하 해석이면 *MAT_LOW_DENSITY_FOAM(057)이나 "
                             "*MAT_024+C/p로 바꿔 쓰세요.")
            r2 = (em.get("prony_fit") or {}).get("r2")
            if r2 is not None:
                lines.append(f"$   Prony 피팅 R² {r2:.4f} — 완화곡선 실측에서 유도")
            lines.append("*MAT_VISCOELASTIC_TITLE")
            lines.append(title)
            lines.append("$#     mid       rho      bulk        g0        gi      beta")
            lines.append(_card_field(str(mid), _fmt(rho * u.f_density),
                                     _fmt(si["BULK"] * u.f_stress), _fmt(si["G0"] * u.f_stress),
                                     _fmt(si["GI"] * u.f_stress), _fmt(si["BETA"] * u.f_rate)))
            made.append("*MAT_VISCOELASTIC (006)")
        elif want_mech:  # 탄성·소성 경로
            if rho is None or E is None:
                # 카탈로그에 Prony 계수가 있는데 못 쓰고 있으면 그 사실을 드러낸다.
                # 지금 점탄성 카드는 업로드된 완화시험(단일항 *MAT_VISCOELASTIC 006)만 낸다.
                # 문헌에서 모은 11~14항 세트는 *MAT_GENERAL_VISCOELASTIC(076)이라야 담기는데
                # 아직 구현이 없다. 조용히 "밀도 없음"으로만 보고하면 이 공백이 안 보인다.
                miss = [n for n, v in (("밀도", rho), ("영률", E)) if v is None]
                reason = f"{'·'.join(miss)} 없음(카드 생성 불가)"
                # Prony가 있는데 못 쓰는 경우, 무엇 하나가 막고 있는지 정확히 말한다.
                # "밀도 없음"으로만 보고하면 11~18항 세트가 놀고 있다는 사실이 안 보인다.
                if cat_prony:
                    if "terms" in cat_prony:
                        # 076은 영률을 쓰지 않는다(BULK와 Prony 항만 필요). 막는 건 밀도뿐이므로
                        # "밀도·영률만 채우면"이라고 적으면 필요한 일을 두 배로 알려주는 셈이다.
                        reason += (f" · **Prony {len(cat_prony['terms'])}항이 준비돼 있다** —"
                                   " *MAT_076은 영률을 쓰지 않으니 **밀도만** 채우면 바로 나온다")
                    else:
                        reason += f" · Prony는 있으나 {cat_prony.get('reason', '')}"
                skipped.append({"material": m["name"], "card": "mechanical", "reason": reason})
            else:
                nu_v = nu if nu is not None else _DEFAULT_NU
                lines.append("$")
                lines.append(f"$ --- MID {mid}: {title} ---")
                # 탄성·소성 카드로 빠지면서 Prony를 못 쓰는 경우가 있다. 카드가 만들어졌으니
                # skipped에도 안 잡혀 공백이 통째로 안 보인다 — 여기서 드러낸다.
                if cat_prony and "reason" in cat_prony:
                    lines.append(f"$   ※ 이 재료는 카탈로그에 점탄성 Prony 계수가 있으나 쓰지 못했다 — "
                                 f"{_clip(cat_prony['reason'], 96)}")
                    lines.append("$     하중률 의존이 중요한 해석이면 *MAT_GENERAL_VISCOELASTIC(076)이 맞다.")
                lines.append(f"$   RO  {_fmt(rho * u.f_density)} {u.density_unit}"
                             f" (= {_fmt(rho)} kg/m^3)   <- {prov.get((i, K_RHO), '출처미상')}")
                lines.append(f"$   E   {_fmt(E * u.f_stress)} {u.stress_unit}   <- {prov.get((i, K_E), '출처미상')}")
                if nu is None:
                    lines.append(f"$   PR  {nu_v} (기본값 — 포아송비 미보유)")
                else:
                    lines.append(f"$   PR  {nu_v}   <- {prov.get((i, K_NU), '출처미상')}")
                    _clash = _direction_clash(rep_rows, i)
                    if _clash:
                        lines.append(f"$   **주의: 방향이 섞였다** — {_clash}.")
                        lines.append("$     등방 카드는 한 방향의 짝으로만 성립한다. "
                                     "이방성 재료면 *MAT_ORTHOTROPIC 계열을 쓰거나 방향을 정해서 다시 뽑아라.")
                # 선택기가 못 가른 칸을 드러낸다 — 자동으로 고르지 않는다(§462 와 같은 방식).
                for _k, _lab, _v, _sc in ((K_RHO, "RO", rho, u.f_density), (K_E, "E", E, u.f_stress),
                                          (K_NU, "PR", nu, 1.0), (K_SIGY, "SIGY", sigy, u.f_stress)):
                    if _v is not None:
                        lines += slot_notes(i, _k)
                    _tie = _tie_note(rep_ties, i, _k, _lab, _sc) if _v is not None else None
                    if _tie:
                        lines.append(f"$   **주의: 대표값이 동률이다** — {_tie}.")
                        lines.append("$     선택기가 등급·조건까지 봐도 안 갈렸다는 뜻이다. "
                                     "값이 중요하면 조회에서 조건을 보고 직접 골라라.")
                if sigy is not None:
                    # 항복 있으면 탄소성(*MAT_024). ETAN은 UTS·연신율로 근사(없으면 0=완전소성).
                    etan = 0.0
                    if uts is not None and elong is not None and elong > 0 and uts > sigy:
                        ep_f = max(elong - sigy / E, 1e-6)   # 소성 변형률 근사
                        etan = (uts - sigy) / ep_f
                    lines.append(f"$   SIGY {_fmt(sigy * u.f_stress)} {u.stress_unit}   <- {prov.get((i, K_SIGY), '출처미상')}")
                    if etan:
                        lines.append(f"$   ETAN {_fmt(etan * u.f_stress)} {u.stress_unit} (UTS·연신율로 근사)")
                    _pts_pre, _base_pre, _row_pre, _ = rate_scale_points(db, i)
                    if len(_pts_pre) >= 2 and _base_pre > 0 and abs(_base_pre - sigy) / max(sigy, 1e-30) > 0.05:
                        lines.append(f"$   ※ SIGY를 {_fmt(sigy * u.f_stress)} → {_fmt(_base_pre * u.f_stress)} "
                                     f"{u.stress_unit}로 바꿔 씁니다 — LCSR 배율의 기준(1.0배)이 "
                                     f"율속 시험의 준정적 항복강도라, 다른 출처의 SIGY를 그대로 두면 "
                                     f"고율속 응력이 어긋납니다.")
                        sigy = _base_pre
                        etan = max((uts - sigy) / max(elong, 1e-6), 0.0) if (uts and elong) else etan
                    lines.append("*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE")
                    lines.append(title)
                    if elong:
                        lines.append(f"$   FAIL {_fmt(elong)} — 총 파단연신율을 파괴 유효소성변형률로 근사")
                    lines.append("$#     mid        ro         e        pr      sigy      etan      fail      tdel")
                    lines.append(_card_field(mid, _fmt(rho * u.f_density), _fmt(E * u.f_stress),
                                             _fmt(nu_v), _fmt(sigy * u.f_stress),
                                             _fmt(etan * u.f_stress),
                                             _fmt(elong) if elong else "0.0", "0.0"))
                    # Cowper-Symonds 변형률속도 항 — 있으면 채운다. 테이프·접착제·폼은
                    # 이 항이 없으면 충격 해석에서 강성을 크게 과소평가한다.
                    cs_c, cs_p = val(i, K_CS_C), val(i, K_CS_P)
                    # 율속별 항복강도가 있으면 LCSR(응력배율 곡선)이 Cowper-Symonds보다 낫다 —
                    # 실측 점을 그대로 쓰므로 2상수 근사에 끼워 맞출 필요가 없다.
                    rate_pts, rate_base, rate_row, rate_rows = rate_scale_points(db, i)
                    lcsr_id = 0
                    if len(rate_pts) >= 2:
                        lcsr_id = lcid_next[0]
                        lcid_next[0] += 1
                        rate_src = "출처미상"
                        if rate_row is not None and rate_row.source_id in ref_no:
                            rate_src = f"[{ref_no[rate_row.source_id]}]"
                        lines.append(f"$   LCSR {lcsr_id} — 변형률속도별 항복응력 배율 "
                                     f"({len(rate_pts)}점, {_fmt(rate_pts[0][0])}~{_fmt(rate_pts[-1][0])} 1/s)"
                                     f"   <- {rate_src}")
                        if rate_pts[-1][1] < 1.0:
                            lines.append("$     주의: 배율이 감소한다 — 음의 율속민감도(NSRS)이거나 "
                                         "시편 산포다. 원문을 확인하고 쓸 것.")
                        modes = rate_series_modes(rate_rows)
                        if len(modes) > 1:
                            lines.append("$     주의: 이 곡선은 시험 방법이 섞여 있다 — "
                                         + " / ".join(_clip(m, 34) for m in modes))
                            lines.append("$     인장·압축 비대칭이 큰 폼·폴리머라면 그대로 쓰지 말 것.")
                    if cs_c and cs_p:
                        lines.append(f"$   C {_fmt(cs_c / u.f_rate)} 1/{u.key.rsplit('_', 1)[-1]}"
                                     f"   p {_fmt(cs_p)} — Cowper-Symonds 변형률속도 경화"
                                     f"   <- {prov.get((i, K_CS_C), '출처미상')}")
                    elif not lcsr_id:
                        lines.append("$   (변형률속도 항 없음 — C·p 미보유. 충격·낙하 해석이면 "
                                     "율속 데이터를 넣어야 강성을 과소평가하지 않는다)")
                    lines.append("$#       c         p      lcss      lcsr        vp")
                    lines.append(_card_field(_fmt(cs_c / u.f_rate) if (cs_c and cs_p) else "0.0",
                                             _fmt(cs_p) if (cs_c and cs_p) else "0.0", 0, lcsr_id, "0.0"))
                    made.append("*MAT_PIECEWISE_LINEAR_PLASTICITY (024)")
                    if lcsr_id:
                        # LCSR 곡선 본체. 배율이므로 단위계와 무관하지만 가로축(변형률속도)은 환산한다.
                        lines.append("*DEFINE_CURVE_TITLE")
                        lines.append(f"{title} — LCSR (변형률속도 → 항복응력 배율)")
                        lines.append("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp")
                        lines.append(_card_field(lcsr_id, 0, "1.0", "1.0", "0.0", "0.0", 0))
                        lines.append("$#                a1                  o1")
                        for r_, s_ in rate_pts:
                            lines.append(f"{_fmt(r_ / u.f_rate):>20s}{_fmt(s_):>20s}")
                        made.append("*DEFINE_CURVE (LCSR)")
                else:
                    lines.append("*MAT_ELASTIC_TITLE")
                    lines.append(title)
                    lines.append("$#     mid        ro         e        pr        da        db  not used")
                    lines.append(_card_field(mid, _fmt(rho * u.f_density), _fmt(E * u.f_stress),
                                             _fmt(nu_v), "0.0", "0.0", "0.0"))
                    made.append("*MAT_ELASTIC (001)")

        # ── 열 카드 ──
        if want_therm:
            if rho is None or hc is None or tc is None:
                miss = [n for n, v in (("밀도", rho), ("비열", hc), ("열전도율", tc)) if v is None]
                reason = f"{'·'.join(miss)} 없음(카드 생성 불가)"
                if melt_dropped:
                    reason += (f" · {'·'.join(melt_dropped)}은 **용융 상태 값뿐**이라 쓰지 않았다"
                               " — 사출 충전 해석용이고 고체 열해석 입력이 아니다")
                skipped.append({"material": m["name"], "card": "thermal", "reason": reason})
            else:
                lines.append("$")
                lines.append(f"$ --- TMID {mid}: {title} (thermal) ---")
                lines.append(f"$   TRO {_fmt(rho * u.f_density)} {u.density_unit}"
                             f" (= {_fmt(rho)} kg/m^3)   <- {prov.get((i, K_RHO), '출처미상')}")
                lines.append(f"$   HC  {_fmt(hc * f_specific_heat(u))} {hc_unit(u)}"
                             f" (= {_fmt(hc)} J/(kg*K))   <- {prov.get((i, K_HC), '출처미상')}")
                lines.append(f"$   TC  {_fmt(tc * f_conductivity(u))} {tc_unit(u)}"
                             f" (= {_fmt(tc)} W/(m*K))   <- {prov.get((i, K_TC), '출처미상')}")
                if cte is not None:
                    lines.append(f"$   (참고) CTE {_fmt(cte)} 1/K   <- {prov.get((i, K_CTE), '출처미상')}")
                for _k in _THERM_SLOTS:
                    if val(i, _k) is not None:
                        lines += slot_notes(i, _k)
                lines.append("*MAT_THERMAL_ISOTROPIC_TITLE")
                lines.append(title)
                lines.append("$#    tmid       tro     tgrlc    tgmult      tlat     hlat")
                lines.append(_card_field(mid, _fmt(rho * u.f_density), "0.0", "0.0", "0.0", "0.0"))
                lines.append("$#      hc        tc")
                lines.append(_card_field(_fmt(hc * f_specific_heat(u)), _fmt(tc * f_conductivity(u))))
                made.append("*MAT_THERMAL_ISOTROPIC (T01)")

        # ── CTE(열팽창) — PART 단위 카드라 PID가 있어야 만들 수 있다 ──
        if pids:
            if cte is None:
                skipped.append({"material": m["name"], "card": "thermal_expansion",
                                "reason": "선팽창계수(CTE) 없음(카드 생성 불가)"})
            else:
                # 곡선은 재료당 1개만 정의하고 여러 PART가 공유한다(중복 곡선 방지).
                lcid = lcid_by_mat.get(i)
                if lcid is None:
                    lcid = lcid_next[0]
                    lcid_next[0] += 1
                    lcid_by_mat[i] = lcid
                    lines.append("$")
                    lines.append(f"$ --- CTE 곡선 (LCID {lcid}): {title} ---")
                    lines.append(f"$   CTE {_fmt(cte)} 1/K   <- {prov.get((i, K_CTE), '출처미상')}")
                    lines += slot_notes(i, K_CTE)
                    lines.append("$   (온도 무관 상수 — 2점 곡선. 온도의존 CTE는 이 곡선을 교체하세요)")
                    lines.append("*DEFINE_CURVE_TITLE")
                    lines.append(f"CTE {title}"[:70])
                    lines.append("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp")
                    lines.append(_card_field(lcid, 0, "1.0", "1.0", "0.0", "0.0", 0))
                    lines.append("$#                a1                  o1")
                    for t_k in (CTE_CURVE_T_MIN, CTE_CURVE_T_MAX):
                        lines.append(f"{_fit10(_fmt(t_k)):>20s}{_fit10(_fmt(cte)):>20s}")
                for pid in pids:
                    lines.append(f"$ PID {pid} ← {title} 열팽창(LCID {lcid})")
                    lines.append("*MAT_ADD_THERMAL_EXPANSION")
                    lines.append("$#     pid      lcid      mult")
                    lines.append(_card_field(pid, lcid, "1.0"))
                    made.append(f"*MAT_ADD_THERMAL_EXPANSION (PID {pid})")
                    parts.append({"pid": pid, "mid": mid, "lcid": lcid,
                                  "material": m["name"], "cte": cte})

        if made:
            row = {"mid": mid, "material_id": i, "name": m["name"],
                   "matched_by": m["matched_by"], "query": m["query"],
                   "mid_source": "지정" if mid in explicit_set else "자동",
                   "pids": pids, "cards": made}
            if cur_choice:
                row["choices"] = {k: {"selector": e["selector"], "id": e["pv"].id,
                                      "value_si": e["pv"].value_num,
                                      "default_id": e["default"].id if e["default"] else None}
                                  for k, e in cur_choice.items()}
            table.append(row)

    if refs:
        lines += ["$", "$" + "=" * 78,
                  "$ 참고문헌 — 위 주석의 [n]이 이 목록을 가리킵니다.",
                  "$" + "=" * 78]
        for r in refs:
            head = f"$ [{r['n']}] "
            pub = (r["publisher"] or "").strip()
            lines.append(head + _clip(f"{pub} — {r['title']}" if pub else (r["title"] or "제목없음"), 74))
            loc = f"DOI {r['doi']}" if r["doi"] else (r["url"] or "")
            if loc:
                lines.append("$      " + loc)        # URL·DOI는 자르지 않는다(복사해 열어야 한다)
    lines.append("*END")
    out = {
        "keyword": "\n".join(lines),
        "units": {"key": u.key, "label": u.label, "stress": u.stress_unit,
                  "density": u.density_unit},
        "card": card,
        "materials": table,
        "n_materials": len(table),
        "parts": parts,
        "skipped": skipped,
        "resolution_errors": errors,
        "mid_warnings": mid_warns,
    }
    if list_choices:
        out["candidates"] = choice_catalog(cands, ids, u)
    return out
