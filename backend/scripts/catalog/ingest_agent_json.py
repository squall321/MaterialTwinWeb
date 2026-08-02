#!/usr/bin/env python
# 에이전트가 수집한 데이터시트 JSON을 검증 후 카탈로그에 등록. 근거(출처·조건) 없는 값은 거부.
#
# 사용:
#   ingest_agent_json.py <dir|file...> [--apply]
#
# 검증 항목(하나라도 어기면 그 값은 건너뛰고 사유를 보고):
#   · property_key가 taxonomy에 존재하는가
#   · 단위가 정의 단위와 일치하는가
#   · 출처(url/doi/title)가 있는가 — 근거 없는 값은 저장 금지
#   · 물리적으로 가능한 범위인가(음수 밀도, PR 범위, 비율>1 등)
#   · 기존에 더 신뢰도 높은 값(tier 낮음)이 있으면 덮지 않는가
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import mcp_server as M  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import Material, PropertyDefinition, PropertyValue  # noqa: E402

# 물리적으로 불가능한 값 차단(키 → (최소, 최대)).
RANGE = {
    "physical.density": (1.0, 25000.0),
    "mechanical.youngs_modulus": (1e3, 1.5e12),
    "mechanical.poisson_ratio": (0.0, 0.5),
    "mechanical.tensile_strength": (1e3, 1e11),
    "mechanical.yield_strength": (1e3, 1e11),
    "mechanical.elongation_at_break": (0.0, 20.0),
    "thermal.conductivity": (0.0, 3000.0),
    "thermal.specific_heat": (10.0, 5000.0),
    "thermal.expansion_linear": (-1e-4, 5e-3),
    "electrical.dielectric_constant": (1.0, 1e5),
    "optical.refractive_index": (0.8, 5.0),   # EUV·X선은 n=1-delta<1 이 정상
    "optical.transmittance": (0.0, 1.0),
    "optical.haze": (0.0, 1.0),
    "optical.emissivity_total": (0.0, 1.0),
    "chemical.water_absorption_24h": (0.0, 1.0),
    "chemical.water_absorption_saturation": (0.0, 1.0),
    # 아래는 단위 오입력이 잦은 신규 키 — 범위 자체가 단위 검산 역할을 한다.
    "interface.peel_strength": (0.5, 5e5),              # N/m (N/mm로 넣으면 1000배 작아짐)
    "interface.lap_shear_strength": (1e4, 1e9),
    "interface.die_shear_strength": (1e4, 1e9),
    "physical.surface_energy": (1e-3, 1.0),   # J/m^2. mN/m 원값(15 등)이면 걸린다
    "electrical.shielding_effectiveness": (0.0, 150.0),
    "electrical.temperature_coefficient_resistance": (-1e-2, 1e-2),  # ppm/K 원값이면 걸린다
    "thermal.thermal_resistance": (1e-6, 1.0),
    "thermal.decomposition_time_t260": (1.0, 1e5),      # s (분 단위면 걸린다)
    "optical.abbe_number": (10.0, 120.0),
    "optical.birefringence": (-1.0, 1.0),   # 음의 1축 결정(사파이어 등)은 Δn<0
    "mechanical.surface_compressive_stress": (1e6, 5e9),  # Pa (MPa 원값이면 걸린다)
    "mechanical.depth_of_layer": (1e-9, 1e-3),            # m (µm 원값이면 걸린다)
}
# Material.category도 고정 어휘 — 에이전트 표기를 매핑한다.
CAT_OK = {"metal", "polymer", "rubber", "composite", "ceramic", "foam"}
CAT_MAP = {"ceramics": "ceramic", "glass": "ceramic", "semiconductor": "ceramic",
           "organic": "polymer", "plastic": "polymer", "resin": "polymer",
           "elastomer": "rubber", "alloy": "metal", "adhesive": "polymer",
           "film": "polymer", "laminate": "composite", "liquid": "polymer"}


def norm_cat(c: str | None) -> str:
    c = (c or "composite").strip().lower()
    return c if c in CAT_OK else CAT_MAP.get(c, "composite")


# Source.kind는 DB 제약(ck_source_kind)이 있는 고정 어휘 — 에이전트 표기를 매핑한다.
KIND_OK = {"journal", "book", "database", "datasheet", "computed", "standard", "web", "other"}
KIND_MAP = {"paper": "journal", "article": "journal", "publication": "journal",
            "handbook": "book", "textbook": "book", "spec": "standard",
            "specification": "standard", "brochure": "datasheet",
            "technical_data": "datasheet", "tds": "datasheet", "catalog": "datasheet",
            "website": "web", "webpage": "web", "patent": "other", "report": "other"}


def norm_kind(k: str | None) -> str:
    k = (k or "datasheet").strip().lower()
    return k if k in KIND_OK else KIND_MAP.get(k, "other")


# 비율 물성인데 1을 넘으면 퍼센트 오입력 의심(엘라스토머 연신율은 예외로 20까지 허용).
PCT_SUSPECT = {"chemical.water_absorption_24h", "chemical.water_absorption_saturation",
               "optical.transmittance", "optical.haze", "optical.emissivity_total"}


# method는 고정 어휘다. 에이전트가 시험법 서술("wire tensile test")을 넣는 일이 잦은데,
# 그 서술은 버리기 아까우므로 conditions.test_method로 옮기고 method는 어휘로 정규화한다.
METHOD_OK = {"measured", "handbook", "computed", "estimated"}
METHOD_MAP = {"datasheet": "measured", "experiment": "measured", "experimental": "measured",
              "test": "measured", "derived": "computed", "calculated": "computed",
              "simulated": "computed", "simulation": "computed", "estimate": "estimated",
              "typical": "measured", "spec": "measured", "book": "handbook",
              "literature": "handbook", "database": "handbook"}


def norm_method(raw) -> tuple[str, str | None]:
    """(정규화된 method, 원문 서술 또는 None)."""
    s = (str(raw) if raw is not None else "").strip()
    if not s:
        return "measured", None
    low = s.lower()
    if low in METHOD_OK:
        return low, None
    if low in METHOD_MAP:
        return METHOD_MAP[low], None
    # 자유 서술 — 계산임을 밝히면 computed, 아니면 측정으로 보고 서술은 보존한다.
    m = "computed" if re.search(r"comput|calcul|simulat|derived|추정|계산", low) else "measured"
    return m, s


def norm_tier(raw) -> int:
    """'tier3' · '3' · 3 을 모두 받는다. 범위 밖은 3(데이터시트급)으로."""
    m = re.search(r"[1-5]", str(raw if raw is not None else 3))
    return int(m.group(0)) if m else 3


def as_cond(raw) -> dict:
    """조건을 dict로. 서술 문자열이면 detail 필드에 담는다."""
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str) and raw.strip():
        try:
            d = json.loads(raw)
            return dict(d) if isinstance(d, dict) else {"detail": raw.strip()}
        except Exception:
            return {"detail": raw.strip()}
    return {}


def cond_sig(cond) -> str:
    """조건을 비교 가능한 서명으로. 표기 순서·타입 차이를 흡수한다.

    조건이 서술 문자열로 오는 경우가 잦은데(에이전트가 dict 대신 문장을 넣는다),
    이때 빈 서명으로 뭉개면 서로 다른 측정이 같은 조건으로 판정돼 덮어쓰기가 난다.
    """
    if isinstance(cond, str):
        s = cond.strip()
        try:
            cond = json.loads(s)
        except Exception:
            return s          # 서술 문자열 자체를 서명으로 쓴다
    if not isinstance(cond, dict) or not cond:
        return ""
    return json.dumps({k: str(v) for k, v in sorted(cond.items())}, ensure_ascii=False)


def load(paths: list[str]) -> list[tuple[str, dict]]:
    out = []
    for p in paths:
        pp = Path(p)
        files = sorted(pp.glob("*.json")) if pp.is_dir() else [pp]
        for f in files:
            if f.name in ("property_keys.json", "materials.json"):
                continue
            try:
                out.append((f.name, json.loads(f.read_text())))
            except Exception as e:
                print(f"  ✗ {f.name}: JSON 파싱 실패 {e}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    with SessionLocal() as s:
        defs = {d.key: d for d in s.query(PropertyDefinition).all()}
        by_name = {m.name: m.id for m in s.query(Material).all()}
        existing = {}
        # 같은 (재료, 물성)이라도 조건이 다르면 별개 측정이므로, 조건 집합도 함께 들고 있는다.
        existing_cond: dict[tuple[int, str], set[str]] = {}
        for mid, k, t, cond in s.query(PropertyValue.material_id, PropertyValue.property_key,
                                       PropertyValue.quality_tier,
                                       PropertyValue.conditions).all():
            existing[(mid, k)] = min(existing.get((mid, k), 9), t)
            existing_cond.setdefault((mid, k), set()).add(cond_sig(cond))

    stats = {"ok": 0, "no_source": 0, "bad_key": 0, "bad_unit": 0, "out_of_range": 0,
             "pct_suspect": 0, "kept_better": 0, "new_mat": 0, "no_mat": 0, "cond_clash": 0}
    # 적재는 (재료·물성·출처·조건)에 멱등이다. 조건이 같은데 값이 다르면 나중 것이
    # 앞의 것을 조용히 덮어 측정 하나가 사라진다(3M 112P02/112P05가 그렇게 사라졌다).
    seen_cond: dict[tuple, float] = {}
    for fname, doc in load(a.paths):
        print(f"\n=== {fname} ===")
        for entry in doc.get("materials", []):
            src = entry.get("source") or {}
            if not (src.get("url") or src.get("doi") or src.get("title")):
                stats["no_source"] += len(entry.get("properties", []))
                print("  ✗ 출처 없음 — 항목 전체 건너뜀")
                continue
            name = entry.get("match_name")
            mid = by_name.get(name) if name else None
            if mid is None:
                nm = entry.get("new_material")
                if isinstance(nm, str):        # 이름만 문자열로 준 경우도 수용
                    nm = {"name": nm}
                if not nm or not nm.get("name"):
                    stats["no_mat"] += 1
                    print(f"  ✗ 재료 미지정: {name}")
                    continue
                if nm["name"] in by_name:
                    mid = by_name[nm["name"]]
                elif a.apply:
                    r = M.register_material(name=nm["name"], category=norm_cat(nm.get("category")),
                                            attributes=nm.get("attributes"))
                    if "error" in r:
                        print(f"  ✗ 재료 등록 실패 {nm['name']}: {r['error']}")
                        continue
                    mid = r["material_id"]
                    by_name[nm["name"]] = mid
                    stats["new_mat"] += 1
                    print(f"  + 신규 재료 [{mid}] {nm['name']}")
                else:
                    stats["new_mat"] += 1
                    print(f"  + (dry) 신규 재료 {nm['name']}")
                    mid = -1          # dry-run: 가상 id로 물성 검증은 계속 수행

            for pr in entry.get("properties", []):
                key, val, unit = pr.get("key"), pr.get("value"), pr.get("unit")
                # 에이전트가 value_text 필드를 따로 쓰는 경우도 받는다.
                if pr.get("value_text") and (val is None or str(val).lower() in ("none", "null", "")):
                    val = pr["value_text"]
                if isinstance(unit, str) and unit.lower() in ("none", "null", ""):
                    unit = None
                d = defs.get(key)
                if d is None:
                    stats["bad_key"] += 1
                    print(f"    ✗ 미정의 key {key}")
                    continue
                if val is None:
                    continue
                # UL94 등급처럼 문자 값은 value_text로 저장(숫자 검증 건너뜀).
                is_text = isinstance(val, str)
                if is_text:
                    if a.apply:
                        meth, detail = norm_method(pr.get("method"))
                        cond = as_cond(pr.get("conditions"))
                        if detail:
                            cond["test_method"] = detail
                        r = M.register_property(
                            mid, key, value_text=val, method=meth,
                            quality_tier=norm_tier(pr.get("tier")),
                            conditions=cond or None, notes=pr.get("note"),
                            source_title=src.get("title"), source_url=src.get("url"),
                            source_doi=src.get("doi"),
                            source_kind=norm_kind(src.get("kind")),
                            source_manufacturer=src.get("manufacturer"))
                        if "error" in r:
                            print(f"    ✗ {key}: {r['error']}")
                            continue
                    stats["ok"] += 1
                    continue
                if d.si_unit and unit and unit != d.si_unit:
                    stats["bad_unit"] += 1
                    print(f"    ✗ 단위 불일치 {key}: {unit} ≠ {d.si_unit}")
                    continue
                lo, hi = RANGE.get(key, (None, None))
                if lo is not None and not (lo <= float(val) <= hi):
                    stats["out_of_range"] += 1
                    print(f"    ✗ 범위 밖 {key}={val} (허용 {lo}~{hi})")
                    continue
                if key in PCT_SUSPECT and float(val) > 1.0:
                    stats["pct_suspect"] += 1
                    print(f"    ✗ 퍼센트 오입력 의심 {key}={val} (비율이어야 함)")
                    continue
                sig = (mid, key, src.get("doi") or src.get("url") or src.get("title"),
                       cond_sig(pr.get("conditions")))
                prev = seen_cond.get(sig)
                if prev is not None and abs(prev - float(val)) > 1e-12:
                    stats["cond_clash"] += 1
                    print(f"    ✗ 조건 충돌 {key}: {prev} vs {val} — 조건이 같아 뒤엣것이 앞엣것을 "
                          f"덮는다. 그레이드·방향 등 구분 조건을 conditions에 넣을 것")
                    continue
                seen_cond[sig] = float(val)
                # 기존 tier1 실측 보존 — 단 조건이 다르면 별개 측정이므로 통과시킨다.
                if (mid > 0 and existing.get((mid, key), 9) <= 1
                        and cond_sig(pr.get("conditions")) in existing_cond.get((mid, key), set())):
                    stats["kept_better"] += 1
                    continue
                if a.apply:
                    meth, detail = norm_method(pr.get("method"))
                    cond = as_cond(pr.get("conditions"))
                    if detail:
                        cond["test_method"] = detail
                    r = M.register_property(
                        mid, key, value=float(val), unit=unit or d.si_unit,
                        method=meth, quality_tier=norm_tier(pr.get("tier")),
                        conditions=cond or None, notes=pr.get("note"),
                        source_title=src.get("title"), source_url=src.get("url"),
                        source_doi=src.get("doi"),
                        source_kind=norm_kind(src.get("kind")),
                        source_manufacturer=src.get("manufacturer"))
                    if "error" in r:
                        print(f"    ✗ {key}: {r['error']}")
                        continue
                stats["ok"] += 1
    print(f"\n{'[APPLY]' if a.apply else '[DRY-RUN]'} " +
          " / ".join(f"{k} {v}" for k, v in stats.items() if v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
