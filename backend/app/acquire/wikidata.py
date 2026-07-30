# Wikidata 커넥터 — 무인증 공개 소스에서 물성값+출처 취득(SI 정규화, 오단위 skip).
"""Wikidata SPARQL/검색으로 재료 물성을 긁는다.

검증된 property만 매핑(오매핑으로 DB 오염 방지). 값은 정규 SI로 변환하고, 기대 단위가
아니면 해당 값을 버린다. 출처는 Wikidata 항목 URL(kind=database, tier=2 handbook).
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

_UA = "MaterialTwinWeb/1.0 (mxcaegroup@gmail.com; materials research)"
_SPARQL = "https://query.wikidata.org/sparql"
_API = "https://www.wikidata.org/w/api.php"


def _get(url: str, params: dict, accept: str = "application/json") -> dict:
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}", headers={"User-Agent": _UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


# ── 단위 변환기: (amount, unit_label) → SI 값 또는 None(기대 단위 아님 → skip) ──────
def _density(a: float, u: str) -> float | None:  # → kg/m^3
    u = u.lower()
    if "cubic centim" in u or "g/cm" in u:
        return a * 1000.0
    if "cubic met" in u or "kg/m" in u:
        return a
    return None


def _thermal_cond(a: float, u: str) -> float | None:  # → W/(m*K)
    u = u.lower()
    return a if ("watt" in u and "kelvin" in u) or "w/(m" in u else None


def _temp_K(a: float, u: str) -> float | None:  # → K (섭씨/켈빈만, 화씨 skip)
    u = u.lower()
    if "celsius" in u:
        return a + 273.15
    if "kelvin" in u:
        return a
    return None


def _dimensionless(a: float, u: str) -> float | None:  # 굴절률 등(단위 없음/1)
    return a if 0 < a < 100 else None


# Wikidata PID → (taxonomy key, target_unit, converter, condition)
_MAP: dict[str, tuple] = {
    "P2054": ("physical.density", "kg/m^3", _density, None),
    "P2068": ("thermal.conductivity", "W/(m*K)", _thermal_cond, {"temperature_k": 293.0}),
    "P2101": ("thermal.melting_point", "K", _temp_K, None),
    "P1109": ("optical.refractive_index", "1", _dimensionless, None),
}


def resolve_entity(name: str) -> dict | None:
    """이름 → Wikidata 항목{qid,label,description}. 첫 후보 반환(없으면 None)."""
    try:
        d = _get(_API, {"action": "wbsearchentities", "search": name, "language": "en",
                        "format": "json", "type": "item", "limit": 1})
    except Exception:
        return None
    hits = d.get("search") or []
    if not hits:
        return None
    h = hits[0]
    return {"qid": h["id"], "label": h.get("label", name), "description": h.get("description", "")}


def fetch_properties(qid: str) -> list[dict]:
    """QID의 매핑된 물성값을 SI로 정규화해 반환. 각 항목: key·value·unit·conditions·wd_pid."""
    props = " ".join(f"p:{p}" for p in _MAP)
    query = f"""SELECT ?p ?amount ?unitLabel WHERE {{
      VALUES ?p {{ {props} }}
      wd:{qid} ?p ?st .
      ?prop wikibase:claim ?p ; wikibase:statementValue ?psv .
      ?st ?psv ?vn .
      ?vn wikibase:quantityAmount ?amount ; wikibase:quantityUnit ?unit .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". ?unit rdfs:label ?unitLabel. }}
    }}"""
    try:
        d = _get(_SPARQL, {"query": query, "format": "json"},
                 accept="application/sparql-results+json")
    except Exception:
        return []
    out: list[dict] = []
    for b in d.get("results", {}).get("bindings", []):
        pid = b["p"]["value"].rsplit("/", 1)[-1]  # .../prop/P2054 → P2054
        spec = _MAP.get(pid)
        if not spec:
            continue
        key, unit, conv, cond = spec
        try:
            amount = float(b["amount"]["value"])
        except (KeyError, ValueError):
            continue
        val = conv(amount, b.get("unitLabel", {}).get("value", ""))
        if val is None:
            continue
        out.append({"key": key, "value": val, "unit": unit, "conditions": cond, "wd_pid": pid})
    return out
