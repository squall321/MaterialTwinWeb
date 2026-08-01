# 카탈로그 물성 → LS-DYNA 키워드 카드 대량 생성(기계 *MAT_*, 열 *MAT_THERMAL_*). MCP·웹 공용 코어.
from __future__ import annotations

import difflib
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_compare import representative_numeric
from app.models import Material, PropertyValue
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

MECH_KEYS = (K_RHO, K_E, K_NU, K_SIGY, K_UTS, K_ELONG)
THERM_KEYS = (K_RHO, K_HC, K_TC, K_CTE)

_DEFAULT_NU = 0.3


def f_specific_heat(u: UnitSystem) -> float:
    """J/(kg*K) → 목표 단위. [비열]=length²/(time²·K)."""
    return u.time_s ** 2 / u.length_m ** 2


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


def _fit10(s: str) -> str:
    """LS-DYNA 고정폭(10칸)을 넘지 않게 보정 — 넘치면 유효자리를 줄여 재포맷.

    10칸 초과 시 덱 파싱이 깨지므로(필드 밀림) 반드시 통과시켜야 한다.
    """
    if len(s) <= 10:
        return s
    try:
        v = float(s)
    except ValueError:
        return s[:10]
    for p in (4, 3, 2, 1):
        t = f"{v:.{p}e}".replace("e-0", "e-").replace("e+0", "e+")
        if len(t) <= 10:
            return t
    return f"{v:.0e}"[:10]


def _card_field(*vals) -> str:
    """10칸 고정폭 필드 행(초과 값은 자동 보정)."""
    return "".join(f"{_fit10(str(v)):>10s}" for v in vals)


# "101, 재료이름" / "101:이름" / "101=이름" 한 행. 앞이 정수면 MID 지정으로 본다.
_ROW_RE = re.compile(r"^(\d+)\s*[,:=]\s*(.+)$")


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


def parse_items(items: list) -> tuple[list, list[int | None], list[str]]:
    """입력 항목에서 (재료토큰, 지정 MID) 쌍을 뽑는다. MID 미지정은 None.

    지원 형식 — "이름" / 12(카탈로그 id) / "101, 이름" / "101:이름" / "101=이름" /
    {"mid":101,"material":"이름"} / 여러 줄 문자열(표 붙여넣기).
    지정한 MID는 그대로 카드에 쓰인다.
    """
    toks: list = []
    mids: list[int | None] = []
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
            toks.append(t)
            continue
        s = str(it).strip()
        if not s:
            continue
        # "101, 이름" / "101:이름" / "101=이름" — 앞이 정수면 MID 지정으로 해석.
        m = _ROW_RE.match(s)
        if m:
            mids.append(int(m.group(1)))
            toks.append(m.group(2).strip())
        else:
            mids.append(None)
            toks.append(s)
    return toks, mids, errs


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
    toks, explicit, errs = parse_items(list(tokens or []))
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
    for tok, mid, exp in zip(toks, mid_list, explicit):
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
                     "query": s, "candidates": cands,
                     "unmatched": len(cands) == 0})
    return {"rows": rows, "errors": errs, "mid_warnings": warns}


def build_cards(db: Session, tokens: list, card: str = "mechanical",
                units: str = "ton_mm_s", mid_start: int = 1) -> dict:
    """재료 리스트 → LS-DYNA 키워드 덱. card: mechanical|thermal|both.

    MID는 mid_start부터 순차 자동 배정. 각 카드에 출처(프로비넌스)를 $ 주석으로 남긴다.
    필수 물성이 없어 카드를 만들 수 없으면 조용히 기본값으로 채우지 않고 skipped에 보고한다.
    """
    u = get_system(units)
    toks, explicit, parse_errs = parse_items(list(tokens or []))
    # 토큰별 개별 해석 — 같은 재료를 다른 MID로 중복 지정하는 경우를 허용(순서·중복 보존).
    mats: list[dict] = []
    keep_mid: list[int | None] = []
    errors: list[str] = list(parse_errs)
    for t, em in zip(toks, explicit):
        got, errs = resolve_materials_fuzzy(db, [t])
        errors.extend(errs)
        if got:
            mats.append(got[0])
            keep_mid.append(em)
    if not mats:
        return {"error": "해석할 재료가 없습니다", "resolution_errors": errors,
                "keyword": "", "materials": [], "skipped": []}
    mid_list, mid_warns = assign_mids(keep_mid, mid_start)
    explicit_set = {m for m in keep_mid if m is not None}

    ids = [m["id"] for m in mats]
    keys = sorted(set(MECH_KEYS + THERM_KEYS))
    reps = representative_numeric(db, list(keys))
    # 출처(프로비넌스) 조회 — 카드 주석용.
    prov: dict[tuple, str] = {}
    for pv in db.execute(select(PropertyValue).where(
            PropertyValue.material_id.in_(ids), PropertyValue.property_key.in_(keys))).scalars().all():
        src = pv.source
        if src is None:
            continue
        tag = src.publisher or src.title or ""
        if src.doi:
            tag = f"{tag} (DOI {src.doi})" if tag else f"DOI {src.doi}"
        prov.setdefault((pv.material_id, pv.property_key), tag[:70])

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
    for m, mid in zip(mats, mid_list):
        i = m["id"]
        rho, E, nu = val(i, K_RHO), val(i, K_E), val(i, K_NU)
        sigy, uts, elong = val(i, K_SIGY), val(i, K_UTS), val(i, K_ELONG)
        hc, tc, cte = val(i, K_HC), val(i, K_TC), val(i, K_CTE)
        made: list[str] = []
        title = re.sub(r"[^\x20-\x7E가-힣]", "", m["name"])[:70]

        # ── 기계 카드 ──
        if want_mech:
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
                    lines.append("*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE")
                    lines.append(title)
                    if elong:
                        lines.append(f"$   FAIL {_fmt(elong)} — 총 파단연신율을 파괴 유효소성변형률로 근사")
                    lines.append("$#     mid        ro         e        pr      sigy      etan      fail      tdel")
                    lines.append(_card_field(mid, _fmt(rho * u.f_density), _fmt(E * u.f_stress),
                                             _fmt(nu_v), _fmt(sigy * u.f_stress),
                                             _fmt(etan * u.f_stress),
                                             _fmt(elong) if elong else "0.0", "0.0"))
                    lines.append("$#       c         p      lcss      lcsr        vp")
                    lines.append(_card_field("0.0", "0.0", 0, 0, "0.0"))
                    made.append("*MAT_PIECEWISE_LINEAR_PLASTICITY (024)")
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
                lines.append(f"$   TRO {_fmt(rho)} kg/m^3   <- {prov.get((i, K_RHO), '출처미상')}")
                lines.append(f"$   HC  {_fmt(hc)} J/(kg*K)   <- {prov.get((i, K_HC), '출처미상')}")
                lines.append(f"$   TC  {_fmt(tc)} W/(m*K)   <- {prov.get((i, K_TC), '출처미상')}")
                if cte is not None:
                    lines.append(f"$   (참고) CTE {_fmt(cte)} 1/K   <- {prov.get((i, K_CTE), '출처미상')}")
                lines.append("*MAT_THERMAL_ISOTROPIC_TITLE")
                lines.append(title)
                lines.append("$#    tmid       tro     tgrlc    tgmult      tlat     hlat")
                lines.append(_card_field(mid, _fmt(rho * u.f_density), "0.0", "0.0", "0.0", "0.0"))
                lines.append("$#      hc        tc")
                lines.append(_card_field(_fmt(hc * f_specific_heat(u)), _fmt(tc * f_conductivity(u))))
                made.append("*MAT_THERMAL_ISOTROPIC (T01)")

        if made:
            table.append({"mid": mid, "material_id": i, "name": m["name"],
                          "matched_by": m["matched_by"], "query": m["query"],
                          "mid_source": "지정" if mid in explicit_set else "자동",
                          "cards": made})

    lines.append("*END")
    return {
        "keyword": "\n".join(lines),
        "units": {"key": u.key, "label": u.label, "stress": u.stress_unit,
                  "density": u.density_unit},
        "card": card,
        "materials": table,
        "n_materials": len(table),
        "skipped": skipped,
        "resolution_errors": errors,
        "mid_warnings": mid_warns,
    }
