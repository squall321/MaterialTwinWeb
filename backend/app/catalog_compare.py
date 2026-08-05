# 재료 간 물성 비교 코어 — 대표값 정렬 매트릭스(도메인·물성별, 프로비넌스 포함). 웹 /compare·MCP 공용.
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Material, PropertyDefinition, PropertyValue

# 도메인 표시 순서(기계→열→전기→물리→…). 정의 외 도메인은 뒤로.
_DOMAIN_ORDER = ["mechanical", "interface", "thermal", "electrical", "physical", "optical",
                 "magnetic", "chemical", "acoustic", "rheological", "structure"]
_META_KEYS = ("manufacturer", "grade", "trade_name", "material_class", "process",
              "subsystem", "standard", "composition")

# 대표값 선택 규칙(재료·물성당 1개) — UI/MCP 공통. 응답에 그대로 노출해 투명하게 한다.
REPRESENTATIVE_RULE = "각 재료·물성은 신뢰등급이 가장 높은(측정>핸드북>데이터시트>계산>추정) 대표값 1개로 정렬"


def _meta(mat: Material) -> dict:
    a = mat.attributes or {}
    return {k: a.get(k) for k in _META_KEYS}


# 상온 기준. 온도 스윕이 있는 재료에서 극단 온도값이 대표로 뽑히면 안 된다 —
# 소프트 OCA의 영률이 -40 °C 유리상 값 1,666 MPa로 대표되던 사고가 있었다.
_ROOM_TEMP_C = 23.0


# 온도를 밝히지 않은 값에 매기는 거리. 상온 명시값(|ΔT| 몇 도)보다는 뒤,
# 고온·저온값보다는 앞이 되도록 잡는다.
#
# 이게 0이면 무표기 값이 "상온 거리 0"으로 계산돼 **25 °C라고 명시한 측정값을 이긴다.**
# 실제로 SAC305 영률이 이 때문에 뒤집혔다 — 시험법 미기재 제품시트의 6.9 GPa가
# 상온 인장 측정 27.83 GPa를 밀어내고 DYNA 카드에 실렸다.
_UNSPECIFIED_TEMP_PENALTY = 5.0


def _temp_distance(cond) -> float:
    """조건의 온도가 상온에서 얼마나 먼지(°C). 온도 조건이 없으면 약간의 불이익."""
    if not isinstance(cond, dict):
        return _UNSPECIFIED_TEMP_PENALTY
    for key, to_c in (("temperature_C", lambda v: v), ("temperature_c", lambda v: v),
                      ("temperature_K", lambda v: v - 273.15), ("temperature_k", lambda v: v - 273.15)):
        v = cond.get(key)
        if isinstance(v, (int, float)):
            return abs(to_c(float(v)) - _ROOM_TEMP_C)
    return _UNSPECIFIED_TEMP_PENALTY


# 광학 물성의 지배 조건은 온도가 아니라 파장이다. 기준은 나트륨 D선 589.3 nm —
# 굴절률 n_d와 아베수의 정의 파장이고 가시광 중심에 가깝다.
#
# 이게 없으면 실리콘 소광계수가 400 nm(0.387)와 652 nm(0.016) 사이에서 임의로 뽑힌다.
# 파장에 따라 800배까지 벌어지므로 온도 기준으로 고르면 아무 의미가 없다.
_REF_WAVELENGTH_NM = 589.3
_UNSPECIFIED_WL_PENALTY = 1e4


def _wavelength_distance(cond) -> float:
    """조건의 파장이 기준(589.3 nm)에서 얼마나 먼지(nm). 없으면 큰 불이익."""
    if not isinstance(cond, dict):
        return _UNSPECIFIED_WL_PENALTY
    for key, to_nm in (("wavelength_nm", lambda v: v), ("wavelength_um", lambda v: v * 1000.0)):
        v = cond.get(key)
        if isinstance(v, (int, float)):
            return abs(to_nm(float(v)) - _REF_WAVELENGTH_NM)
    return _UNSPECIFIED_WL_PENALTY


# 고체가 아닌 상태(용융·액체)의 값은 구조·열해석의 대표값이 될 수 없다.
# 벤더 시트가 사출 충전 해석용으로 `Thermal conductivity of melt` · `Spec. heat capacity melt`를
# 싣는데, 수치대가 고체와 비슷해 그냥 넣으면 열전달 카드를 조용히 오염시킨다.
# 실제로 Stanyl TE250F6의 용융 k = 0.344 W/(m·K)는 고체값과 구분이 안 된다.
# 값을 버리지는 않는다 — 사출 워피지에는 그 값이 맞다. 대표값 선택에서만 뒤로 보낸다.
_NON_SOLID_STATES = ("melt", "molten", "liquid", "용융", "액체")


def is_non_solid(cond) -> bool:
    if not isinstance(cond, dict):
        return False
    s = str(cond.get("state") or cond.get("phase") or "").lower()
    return any(w in s for w in _NON_SOLID_STATES)


def _rep_rank(pv: PropertyValue) -> tuple:
    """대표값 우선순위: 고체 우선 → 신뢰등급↑ → 수치 보유 → **지배 조건에 가까움** → 조건 적음 → id.

    지배 조건은 물성마다 다르다. 광학은 파장, 그 외는 온도(상온)를 본다.
    """
    key = pv.property_key or ""
    primary = (_wavelength_distance(pv.conditions) if key.startswith("optical.")
               else _temp_distance(pv.conditions))
    return (1 if is_non_solid(pv.conditions) else 0,
            pv.quality_tier or 9, 0 if pv.value_num is not None else 1,
            primary, len(pv.conditions or {}), pv.id)


def resolve_material_ids(db: Session, tokens: list) -> tuple[list[int], list[str]]:
    """이름 또는 id 토큰 리스트 → (material_id 리스트, 에러 메시지 리스트).

    정수/정수문자열은 id로, 그 외는 이름 정확일치→부분일치(단일해)로 해석.
    """
    ids: list[int] = []
    errors: list[str] = []
    for tok in tokens:
        s = str(tok).strip()
        if not s:
            continue
        if s.isdigit():
            m = db.get(Material, int(s))
            if m is None:
                errors.append(f"id {s}: 재료 없음")
            else:
                ids.append(m.id)
            continue
        exact = db.execute(select(Material).where(Material.name == s)).scalars().all()
        if len(exact) == 1:
            ids.append(exact[0].id)
            continue
        like = db.execute(
            select(Material).where(Material.name.ilike(f"%{s}%"))).scalars().all()
        if len(like) == 1:
            ids.append(like[0].id)
        elif not like:
            errors.append(f"'{s}': 일치하는 재료 없음")
        else:
            names = ", ".join(m.name for m in like[:6])
            errors.append(f"'{s}': 모호함({len(like)}건: {names}…) — 정확한 이름/​id 지정")
    # 중복 id 제거(순서 유지).
    seen: set[int] = set()
    uniq = [i for i in ids if not (i in seen or seen.add(i))]
    return uniq, errors


def representative_numeric(db: Session, keys: list[str]) -> dict[str, dict[int, float]]:
    """주어진 property_key들에 대해 재료별 대표 수치값 → {key: {material_id: value_num}}."""
    best: dict[tuple, PropertyValue] = {}
    for pv in db.execute(
        select(PropertyValue).where(
            PropertyValue.property_key.in_(keys), PropertyValue.value_num.isnot(None))
    ).scalars().all():
        k = (pv.material_id, pv.property_key)
        if k not in best or _rep_rank(pv) < _rep_rank(best[k]):
            best[k] = pv
    out: dict[str, dict[int, float]] = {k: {} for k in keys}
    for (mid, key), pv in best.items():
        out[key][mid] = pv.value_num
    return out


def representative_rows(db: Session, keys: list[str],
                        material_ids: list[int] | None = None) -> dict[tuple, PropertyValue]:
    """대표값으로 뽑힌 **행 자체**를 돌려준다 — 값과 출처를 반드시 같은 행에서 가져오려면 필요하다.

    representative_numeric()이 값만 주다 보니, 호출부가 출처를 따로 조회하면서
    값은 대표값인데 출처는 다른 행을 다는 사고가 났다(DYNA 카드 주석).
    """
    stmt = select(PropertyValue).where(
        PropertyValue.property_key.in_(keys), PropertyValue.value_num.isnot(None))
    if material_ids is not None:
        stmt = stmt.where(PropertyValue.material_id.in_(material_ids))
    best: dict[tuple, PropertyValue] = {}
    for pv in db.execute(stmt).scalars().all():
        k = (pv.material_id, pv.property_key)
        if k not in best or _rep_rank(pv) < _rep_rank(best[k]):
            best[k] = pv
    return best


def numeric_property_options(db: Session) -> list[dict]:
    """Ashby 축 후보 — 수치값을 가진 물성 목록(재료 수 내림차순). {key,name,unit,domain,symbol,n_materials}."""
    defs = {d.key: d for d in db.execute(select(PropertyDefinition)).scalars().all()}
    n_mat: dict[str, set] = defaultdict(set)
    for mid, key in db.execute(
        select(PropertyValue.material_id, PropertyValue.property_key)
        .where(PropertyValue.value_num.isnot(None))
    ).all():
        n_mat[key].add(mid)
    opts = []
    for key, mids in n_mat.items():
        d = defs.get(key)
        if d is None:
            continue
        opts.append({"key": key, "name": d.name, "symbol": d.symbol, "unit": d.si_unit,
                     "domain": d.domain, "n_materials": len(mids)})
    opts.sort(key=lambda o: (-o["n_materials"], o["name"]))
    return opts


def scatter_dataset(db: Session, x_key: str, y_key: str) -> dict | None:
    """Ashby 산점도 데이터 — x·y 물성을 모두 가진 재료의 (대표값) 좌표 + 메타(색상 facet용).

    반환: {x:{axis}, y:{axis}, points:[{material_id,name,category,subsystem,manufacturer,
    material_class,x,y}], rule}. x_key/y_key가 정의에 없으면 None.
    """
    defs = {d.key: d for d in db.execute(
        select(PropertyDefinition).where(PropertyDefinition.key.in_([x_key, y_key]))
    ).scalars().all()}
    if x_key not in defs or y_key not in defs:
        return None
    reps = representative_numeric(db, list({x_key, y_key}))
    xv, yv = reps.get(x_key, {}), reps.get(y_key, {})
    common = set(xv) & set(yv)
    mats = {m.id: m for m in db.execute(
        select(Material).where(Material.id.in_(common))).scalars().all()} if common else {}
    points = []
    for mid in common:
        m = mats.get(mid)
        if m is None:
            continue
        a = m.attributes or {}
        points.append({
            "material_id": mid, "name": m.name, "category": m.category,
            "subsystem": a.get("subsystem"), "manufacturer": a.get("manufacturer"),
            "material_class": a.get("material_class"), "x": xv[mid], "y": yv[mid],
        })
    points.sort(key=lambda p: p["name"])

    def _axis(k: str) -> dict:
        d = defs[k]
        return {"key": k, "name": d.name, "symbol": d.symbol, "unit": d.si_unit, "domain": d.domain}

    return {"x": _axis(x_key), "y": _axis(y_key), "points": points, "rule": REPRESENTATIVE_RULE}


def property_ranking(db: Session, key: str, min_value: float | None = None,
                     max_value: float | None = None, order: str = "desc",
                     limit: int | None = 30) -> dict | None:
    """한 물성(key)으로 재료를 대표값 랭킹 — 흡습률·CTE·유전율 등 카탈로그 전 물성 공용.

    반환: {property:{key,name,symbol,unit,domain}, count, results:[{material_id,name,
    category,manufacturer,value,unit,tier,method,conditions,source}]}. key 미정의면 None.
    """
    d = db.execute(select(PropertyDefinition).where(PropertyDefinition.key == key)).scalar_one_or_none()
    if d is None:
        return None
    best: dict[int, PropertyValue] = {}
    for pv in db.execute(
        select(PropertyValue).where(PropertyValue.property_key == key,
                                    PropertyValue.value_num.isnot(None))
    ).scalars().all():
        if pv.material_id not in best or _rep_rank(pv) < _rep_rank(best[pv.material_id]):
            best[pv.material_id] = pv
    mats = {m.id: m for m in db.execute(
        select(Material).where(Material.id.in_(best.keys()))).scalars().all()} if best else {}
    rows = []
    for mid, pv in best.items():
        v = pv.value_num
        if min_value is not None and v < min_value:
            continue
        if max_value is not None and v > max_value:
            continue
        m = mats.get(mid)
        if m is None:
            continue
        a = m.attributes or {}
        src = pv.source
        rows.append({
            "material_id": mid, "name": m.name, "category": m.category,
            "manufacturer": a.get("manufacturer"), "grade": a.get("grade"),
            "value": v, "unit": pv.unit, "tier": pv.quality_tier, "method": pv.method,
            "conditions": pv.conditions,
            "source": ({"title": src.title, "url": src.url, "doi": src.doi,
                        "manufacturer": src.publisher, "kind": src.kind} if src else None),
        })
    rows.sort(key=lambda r: r["value"], reverse=(order != "asc"))
    return {
        "property": {"key": d.key, "name": d.name, "symbol": d.symbol,
                     "unit": d.si_unit, "domain": d.domain},
        "count": len(rows), "results": rows if limit is None else rows[:limit],
    }


def property_stats(db: Session, key: str) -> dict | None:
    """한 물성(key)의 재료 간 분포 통계 — n·min·max·mean·median + 상·하위 재료."""
    import statistics
    rk = property_ranking(db, key, order="desc", limit=None)
    if rk is None:
        return None
    rows = rk["results"]
    vals = [r["value"] for r in rows]
    if not vals:
        return {"property": rk["property"], "n": 0}
    return {
        "property": rk["property"], "n": len(vals),
        "min": min(vals), "max": max(vals),
        "mean": statistics.fmean(vals), "median": statistics.median(vals),
        "highest": [{"name": r["name"], "value": r["value"]} for r in rows[:3]],
        "lowest": [{"name": r["name"], "value": r["value"]} for r in rows[-3:]],
    }


def build_comparison(db: Session, material_ids: list[int]) -> dict:
    """재료들을 물성별로 정렬 비교. 요청 순서를 컬럼 순서로 유지.

    반환: {materials, domains:[{domain, properties:[{key,name,symbol,unit,standard,
    present,numeric,min_material_id,max_material_id,cells:[cell|null …]}]}],
    n_properties, n_shared, rule}. cell: {material_id,value,value_text,unit,tier,
    method,conditions,source,rel}. rel = value/max(0..1, 전부 비음수일 때만).
    """
    mats = [m for m in (db.get(Material, mid) for mid in material_ids) if m is not None]
    if len(mats) < 2:
        return {"materials": [{"id": m.id, "name": m.name} for m in mats],
                "domains": [], "n_properties": 0, "n_shared": 0,
                "rule": REPRESENTATIVE_RULE, "error": "비교하려면 유효한 재료 2개 이상 필요"}

    mids = [m.id for m in mats]
    defs = {d.key: d for d in db.execute(select(PropertyDefinition)).scalars().all()}

    # (material_id, property_key) → 대표 PropertyValue.
    best: dict[tuple, PropertyValue] = {}
    for pv in db.execute(
        select(PropertyValue).where(PropertyValue.material_id.in_(mids))
    ).scalars().all():
        k = (pv.material_id, pv.property_key)
        if k not in best or _rep_rank(pv) < _rep_rank(best[k]):
            best[k] = pv

    keys_by_mat: dict[str, set] = defaultdict(set)
    for (mid, key) in best:
        keys_by_mat[key].add(mid)
    dom_keys: dict[str, list] = defaultdict(list)
    for key in keys_by_mat:
        d = defs.get(key)
        if d is not None:
            dom_keys[d.domain].append(key)

    def _cell(mid: int, key: str):
        pv = best.get((mid, key))
        if pv is None:
            return None
        src = pv.source
        return {
            "material_id": mid, "value": pv.value_num, "value_text": pv.value_text,
            "unit": pv.unit, "tier": pv.quality_tier, "method": pv.method,
            "conditions": pv.conditions,
            "source": ({"title": src.title, "url": src.url, "doi": src.doi,
                        "manufacturer": src.publisher, "kind": src.kind,
                        "detail": pv.source_detail} if src else None),
        }

    n = len(mats)
    domains_out = []
    for dom in sorted(dom_keys,
                      key=lambda d: (_DOMAIN_ORDER.index(d) if d in _DOMAIN_ORDER else 99, d)):
        props = []
        for key in dom_keys[dom]:
            d = defs[key]
            cells = [_cell(m.id, key) for m in mats]
            nums = [(c["material_id"], c["value"]) for c in cells
                    if c and c["value"] is not None]
            present = sum(1 for c in cells if c is not None)
            min_mid = max_mid = None
            if len(nums) >= 2:
                vals = [v for _, v in nums]
                mn, mx = min(vals), max(vals)
                if mx != mn:
                    min_mid = next(mid for mid, v in nums if v == mn)
                    max_mid = next(mid for mid, v in nums if v == mx)
                    # 상대 막대: 전부 비음수 & max>0일 때만(음수 물성은 막대 무의미).
                    if all(v >= 0 for v in vals) and mx > 0:
                        for c in cells:
                            if c and c["value"] is not None:
                                c["rel"] = c["value"] / mx
            props.append({
                "key": key, "name": d.name, "symbol": d.symbol, "unit": d.si_unit,
                "standard": d.test_standard, "domain": dom,
                "present": present, "numeric": len(nums) >= 1,
                "min_material_id": min_mid, "max_material_id": max_mid, "cells": cells,
            })
        # 전 재료 공통 물성을 위로, 그다음 보유 수·이름순.
        props.sort(key=lambda p: (-(p["present"] == n), -p["present"], p["name"]))
        domains_out.append({"domain": dom, "properties": props})

    n_shared = sum(1 for key in keys_by_mat if len(keys_by_mat[key]) == n)
    return {
        "materials": [{"id": m.id, "name": m.name, "material_code": m.material_code,
                       "category": m.category, **_meta(m)} for m in mats],
        "domains": domains_out,
        "n_properties": len(keys_by_mat), "n_shared": n_shared,
        "rule": REPRESENTATIVE_RULE,
    }
