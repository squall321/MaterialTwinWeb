# 카탈로그 물성 → LS-DYNA 키워드 카드 대량 생성(기계 *MAT_*, 열 *MAT_THERMAL_*). MCP·웹 공용 코어.
from __future__ import annotations

import difflib
import json
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_compare import representative_numeric, representative_rows
from app.models import Material, ProcessedResult, PropertyValue, Specimen, Test
from app.unit_systems import UnitSystem, get_system

# 카드에 쓰는 물성 키.
K_RHO = "physical.density"
K_E = "mechanical.youngs_modulus"
K_NU = "mechanical.poisson_ratio"
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
_COND_SHOW = (("strain_rate_1/s", "ε̇", "/s"), ("temperature_C", "T", "°C"),
              ("temperature_K", "T", "K"), ("temperature_k", "T", "K"),
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


def parse_items(items: list) -> tuple[list, list[int | None], list[list[int]], list[str]]:
    """입력 항목에서 (재료토큰, 지정 MID, PID 목록)을 뽑는다. 미지정은 None/빈 리스트.

    지원 형식 — "이름" / 12(카탈로그 id) / "101, 이름" / "101:이름" / "101=이름" /
    "101, 5, 이름"(MID·PID·이름) / "101, 5;6;7, 이름"(여러 PID) /
    {"mid":101,"pid":5,"material":"이름"} / 여러 줄 문자열(표 붙여넣기).
    지정한 MID는 그대로 카드에 쓰이고, PID가 있으면 CTE(*MAT_ADD_THERMAL_EXPANSION)를 만든다.
    """
    toks: list = []
    mids: list[int | None] = []
    pids: list[list[int]] = []
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
            pids.append(_parse_pids(it.get("pids", it.get("pid", it.get("PID")))))
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
            toks.append(m3.group(3).strip())
            continue
        # "101, 이름" / "101:이름" / "101=이름" — 앞이 정수면 MID 지정으로 해석.
        m = _ROW_RE.match(s)
        if m:
            mids.append(int(m.group(1)))
            pids.append([])
            toks.append(m.group(2).strip())
        else:
            mids.append(None)
            pids.append([])
            toks.append(s)
    return toks, mids, pids, errs


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
    toks, explicit, pid_lists, errs = parse_items(list(tokens or []))
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
_DESCRIPTIVE_COND = frozenset((
    "crosshead_speed_mm_min", "apparatus", "test", "loading", "temperature_stated"))
_MODE_COND = ("test", "loading")


def _series_key(cond: dict) -> tuple:
    """율속과 측정 서술을 뺀 **나머지 조건 전부**가 하나의 곡선을 정한다.

    온도만 볼 수는 없다. Kapton HN은 같은 298 K에서 ID·TD 두 방향을 재고, 금속은 같은 온도에서
    열처리·결정립이 갈린다. 이것들을 한 곡선에 섞으면 가로축이 중복되고 배율이 1.0 → 0.94로
    거꾸로 가는 *DEFINE_CURVE가 나온다. 축을 열거하는 대신 나머지를 통째로 비교한다.
    """
    rest = tuple(sorted(
        (k, json.dumps(v, sort_keys=True, ensure_ascii=False))
        for k, v in cond.items()
        if k != _RATE_COND and k not in _TEMP_COND and k not in _DESCRIPTIVE_COND))
    return (_cond_temp_c(cond), rest)


def rate_series_modes(rows: list) -> list[str]:
    """고른 계열이 몇 가지 시험 방법을 섞고 있는지 — 카드 주석에 적기 위한 것."""
    modes = {str(r.conditions.get(k)) for r in rows
             for k in _MODE_COND
             if isinstance(r.conditions, dict) and r.conditions.get(k)}
    return sorted(modes)


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
    buckets: dict[tuple, list[tuple[float, float, object]]] = {}
    for pv in rows:
        cond = pv.conditions if isinstance(pv.conditions, dict) else {}
        rate = cond.get(_RATE_COND)
        if not isinstance(rate, (int, float)) or rate <= 0:
            continue
        buckets.setdefault(_series_key(cond), []).append(
            (float(rate), float(pv.value_num), pv))
    # 곡선이 되려면 서로 다른 율속이 둘 이상이어야 한다.
    usable = {k: v for k, v in buckets.items() if len({p[0] for p in v}) >= 2}
    if not usable:
        return [], 0.0, None, []

    def _pick(k: tuple) -> tuple:
        t = k[0]
        return (_NO_TEMP_PENALTY if t is None else abs(t - _ROOM_C), -len(usable[k]))

    pts = sorted(usable[min(usable, key=_pick)], key=lambda x: x[0])
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
                lcid_start: int = CTE_LCID_BASE) -> dict:
    """재료 리스트 → LS-DYNA 키워드 덱. card: mechanical|thermal|both.

    MID는 mid_start부터 순차 자동 배정. 각 카드에 출처(프로비넌스)를 $ 주석으로 남긴다.
    필수 물성이 없어 카드를 만들 수 없으면 조용히 기본값으로 채우지 않고 skipped에 보고한다.
    """
    u = get_system(units)
    toks, explicit, pid_lists, parse_errs = parse_items(list(tokens or []))
    # 토큰별 개별 해석 — 같은 재료를 다른 MID로 중복 지정하는 경우를 허용(순서·중복 보존).
    mats: list[dict] = []
    keep_mid: list[int | None] = []
    keep_pids: list[list[int]] = []
    errors: list[str] = list(parse_errs)
    for t, em, pl in zip(toks, explicit, pid_lists):
        got, errs = resolve_materials_fuzzy(db, [t])
        errors.extend(errs)
        if got:
            mats.append(got[0])
            keep_mid.append(em)
            keep_pids.append(pl)
    if not mats:
        return {"error": "해석할 재료가 없습니다", "resolution_errors": errors,
                "keyword": "", "materials": [], "skipped": []}
    mid_list, mid_warns = assign_mids(keep_mid, mid_start)
    explicit_set = {m for m in keep_mid if m is not None}

    ids = [m["id"] for m in mats]
    # LCSR 곡선의 원자료도 프로비넌스에 넣어야 한다 — 빠지면 곡선 출처가 '출처미상'으로 나온다.
    keys = sorted(set(MECH_KEYS + THERM_KEYS + (K_SIGY_RATE,)))
    reps = representative_numeric(db, list(keys))
    # 출처(프로비넌스) — 반드시 **대표값으로 뽑힌 그 행**의 출처를 쓴다.
    # (예전엔 아무 행이나 먼저 걸린 것을 달아, 값과 출처가 어긋날 수 있었다.)
    rep_rows = representative_rows(db, list(keys), material_ids=ids)
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
    for (mid_, key_), pv in rep_rows.items():
        src = pv.source
        if src is None:
            prov[(mid_, key_)] = "출처미상"
            continue
        if src.id not in ref_no:
            ref_no[src.id] = len(refs) + 1
            refs.append({"n": len(refs) + 1, "publisher": src.publisher,
                         "title": src.title, "doi": src.doi, "url": src.url,
                         "kind": src.kind})
        short = (src.publisher or src.title or "").strip()
        tag = f"[{ref_no[src.id]}] {_clip(short, 40)}" if short else f"[{ref_no[src.id]}]"
        cond_tag = _cond_tag(pv.conditions)
        prov[(mid_, key_)] = f"{tag}{cond_tag}"

    def val(mid: int, key: str):
        return reps.get(key, {}).get(mid)

    want_mech = card in ("mechanical", "both")
    want_therm = card in ("thermal", "both")

    lines: list[str] = ["*KEYWORD",
                        "$" + "=" * 78,
                        "$ MaterialTwinWeb — LS-DYNA 재료카드 자동 생성",
                        f"$ 단위계: {u.label}  (응력 {u.stress_unit}, 밀도 {u.density_unit})",
                        f"$ 카드종류: {card}",
                        "$ 각 물성 아래 $ 주석은 출처(프로비넌스)입니다.",
                        "$" + "=" * 78]
    table: list[dict] = []
    skipped: list[dict] = []
    parts: list[dict] = []
    lcid_next = [int(lcid_start)]
    lcid_by_mat: dict[int, int] = {}
    for m, mid, pids in zip(mats, mid_list, keep_pids):
        i = m["id"]
        rho, E, nu = val(i, K_RHO), val(i, K_E), val(i, K_NU)
        sigy, uts, elong = val(i, K_SIGY), val(i, K_UTS), val(i, K_ELONG)
        hc, tc, cte = val(i, K_HC), val(i, K_TC), val(i, K_CTE)
        made: list[str] = []
        title = " ".join(re.sub(r"[^\x20-\x7E가-힣]", " ", m["name"]).split())[:70]

        # ── 기계 카드 ──
        if want_mech and i in visco and rho is not None:
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
        elif want_mech:
            if rho is None or E is None:
                skipped.append({"material": m["name"], "card": "mechanical",
                                "reason": "밀도 또는 영률 없음(카드 생성 불가)"})
            else:
                nu_v = nu if nu is not None else _DEFAULT_NU
                lines.append("$")
                lines.append(f"$ --- MID {mid}: {title} ---")
                lines.append(f"$   RO  {_fmt(rho * u.f_density)} {u.density_unit}"
                             f" (= {_fmt(rho)} kg/m^3)   <- {prov.get((i, K_RHO), '출처미상')}")
                lines.append(f"$   E   {_fmt(E * u.f_stress)} {u.stress_unit}   <- {prov.get((i, K_E), '출처미상')}")
                if nu is None:
                    lines.append(f"$   PR  {nu_v} (기본값 — 포아송비 미보유)")
                else:
                    lines.append(f"$   PR  {nu_v}   <- {prov.get((i, K_NU), '출처미상')}")
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
                skipped.append({"material": m["name"], "card": "thermal",
                                "reason": f"{'·'.join(miss)} 없음(카드 생성 불가)"})
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
            table.append({"mid": mid, "material_id": i, "name": m["name"],
                          "matched_by": m["matched_by"], "query": m["query"],
                          "mid_source": "지정" if mid in explicit_set else "자동",
                          "pids": pids, "cards": made})

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
    return {
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
