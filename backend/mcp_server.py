# MaterialTwin MCP 서버 — 재료 DB·물성·곡선·구성방정식·LS-DYNA 카드 조회 + 물성 등록/수정/삭제 도구.
from __future__ import annotations

import os
import sys
from pathlib import Path

# 어느 cwd에서 실행되든 backend 디렉터리를 import 경로에 넣는다.
_BACKEND = Path(__file__).resolve().parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
# DB/DATA_DIR 기본값(미주입 시 backend/var/data). .mcp.json env가 우선.
#
# **DATABASE_URL은 DATA_DIR에서 유도한다.** 예전엔 둘 다 backend/var/data로 고정 setdefault해서,
# DATA_DIR만 라이브로 지정하면 URL이 개발 경로로 먼저 박혀 DATA_DIR이 조용히 무시됐다.
# 이 모듈을 import만 해도 그렇게 되므로, 이걸 import하는 스크립트(ingest_agent_json 등)가
# 전부 개발 DB(70종)를 보게 된다 — 실제로 수집 배치가 "재료 미지정"으로 오판했다.
os.environ.setdefault("MATERIALTWIN_DATA_DIR", str(_BACKEND / "var" / "data"))
os.environ.setdefault(
    "MATERIALTWIN_DATABASE_URL",
    f"sqlite:///{Path(os.environ['MATERIALTWIN_DATA_DIR']).resolve() / 'materialtwin.db'}")

import io
import numpy as np
import matplotlib
matplotlib.use("Agg")  # 헤드리스 렌더.
import matplotlib.pyplot as plt


def _use_korean_font() -> None:
    """그래프 한글이 □로 깨지지 않도록 설치된 CJK 폰트를 지정한다(없으면 무시)."""
    import matplotlib.font_manager as _fm
    avail = {f.name for f in _fm.fontManager.ttflist}
    for cand in ("NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR",
                 "Noto Sans CJK HK", "NanumSquare", "Malgun Gothic"):
        if cand in avail:
            matplotlib.rcParams["font.family"] = cand
            matplotlib.rcParams["axes.unicode_minus"] = False  # 한글 폰트의 마이너스 깨짐 방지
            return


_use_korean_font()
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image
from mcp.server.transport_security import TransportSecuritySettings
from sqlalchemy import func

from app import analysis, curve_store, fitting, insights, viscoelastic
from app.cards import lsdyna_mat024_card, lsdyna_mat098_card, poisson_from_attributes
from app.catalog_compare import (
    build_comparison,
    property_ranking,
    property_stats,
    resolve_material_ids,
    scatter_dataset,
)
from app.curve_synth import KIND_MEASURED, KIND_SYNTHETIC, synth_for_material
from app.dyna_export import build_cards as build_dyna_cards
from app.db import SessionLocal
from app.models import (
    ConstitutiveFit,
    Instrument,
    InstrumentCapability,
    Material,
    ProcessedResult,
    PropertyDefinition,
    PropertyValue,
    RawCurveRef,
    Source,
    Specimen,
    Test,
)
from app.routers.properties import _plastic_true
from app.unit_systems import get_system

# HTTP 모드(웹앱 /mcp 마운트)는 loopback 바인드 + 앞단 프록시(HEAXHub Caddy)가 신뢰 경계다.
# 프록시 체인이 Host를 포털 도메인으로 전달하므로 Host 검증(DNS rebinding 보호)은 끄고,
# 외부 노출 차단은 127.0.0.1 바인드가 담당한다 (laminate_analyzer_mcp와 동일 결정).
# stdio 모드에는 영향 없는 설정이다.
mcp = FastMCP(
    "materialtwin",
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

# 파괴적 삭제 툴 노출 정책. 기본은 노출(개인 stdio = 전체 신뢰).
# 페더레이션 HTTP 진입점(app.main)이 이 값을 "0"으로 기본 설정 → 중앙 게이트웨이에는 삭제 툴 미노출.
_ALLOW_DELETE = os.environ.get("MATERIALTWIN_MCP_ALLOW_DELETE", "1") == "1"


def _destructive_tool(fn):
    """MATERIALTWIN_MCP_ALLOW_DELETE=0이면 등록하지 않아 툴 목록에서 숨긴다(페더레이션 안전)."""
    return mcp.tool()(fn) if _ALLOW_DELETE else fn


def _mpa(v):
    return round(float(v) / 1e6, 2) if isinstance(v, (int, float)) else None


def _gpa(v):
    return round(float(v) / 1e9, 3) if isinstance(v, (int, float)) else None


@mcp.tool()
def list_materials(category: str | None = None, query: str | None = None, limit: int = 50) -> list[dict]:
    """재료 목록을 조회한다 — query 는 이름만 부분일치하며 material_code 는 검색되지 않는다('_'·'%' 는 SQL 와일드카드로 동작). 기본 50건·최대 200건을 id 오름차순으로 잘라 반환하고 총 건수·절단 여부를 알려주지 않는다(현재 재료 544건). 전체 건수는 database_summary, 200건을 넘는 열거는 find_materials_by_metadata(limit=1000), 코드로 찾을 때는 find_materials_by_metadata 를 쓴다.

    각 항목: id, name, category, mat_type, 대표 E(GPa)·UTS(MPa) 또는 점탄성 E0(MPa),
    그리고 n_properties·property_domains(보유한 화·물리 물성 수와 도메인 —
    thermal/electrical/optical/chemical/physical 등). 상세 값은 get_material 또는
    get_material_properties로 조회한다. limit는 최대 200으로 제한된다.
    """
    from sqlalchemy import and_

    limit = max(1, min(int(limit), 200))
    with SessionLocal() as s:
        # 재료당 대표 test·pr을 단일 outerjoin으로 수집(N+1 제거). 유효 시험 최소 id 선택.
        q = (s.query(Material, Test, ProcessedResult)
             .outerjoin(Specimen, Specimen.material_id == Material.id)
             .outerjoin(Test, and_(Test.specimen_id == Specimen.id, Test.valid == True))  # noqa: E712
             .outerjoin(ProcessedResult, ProcessedResult.test_id == Test.id))
        if category:
            q = q.filter(Material.category == category)
        if query:
            q = q.filter(Material.name.ilike(f"%{query}%"))
        picked: dict[int, tuple] = {}
        for mat, t, pr in q.order_by(Material.id, Test.id).all():
            cur = picked.get(mat.id)
            if cur is None or (cur[1] is None and t is not None):
                picked[mat.id] = (mat, t, pr)

        # 재료별 카탈로그 물성 수·도메인(1회 집계) — 기계 물성만 보이던 문제 해결.
        dom_by_key = dict(s.query(PropertyDefinition.key, PropertyDefinition.domain).all())
        n_props: dict[int, int] = {}
        doms: dict[int, set] = {}
        for m_id, p_key in s.query(PropertyValue.material_id, PropertyValue.property_key).all():
            n_props[m_id] = n_props.get(m_id, 0) + 1
            doms.setdefault(m_id, set()).add(dom_by_key.get(p_key))

        out = []
        for mat, t, pr in sorted(picked.values(), key=lambda x: x[0].id)[:limit]:
            row = {"id": mat.id, "name": mat.name, "category": mat.category,
                   "mat_type": (mat.attributes or {}).get("mat_type"),
                   "n_properties": n_props.get(mat.id, 0),
                   "property_domains": sorted(d for d in doms.get(mat.id, set()) if d)}
            if t:
                if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
                    row["kind"] = "viscoelastic"
                    row["E0_MPa"] = _mpa(pr.extra_metrics.get("E0_pa"))
                    row["Einf_MPa"] = _mpa(pr.extra_metrics.get("Einf_pa"))
                elif pr:
                    row["kind"] = "elastoplastic"
                    row["E_GPa"] = _gpa(pr.youngs_modulus_pa)
                    row["UTS_MPa"] = _mpa(pr.uts_pa)
                row["test_id"] = t.id
            out.append(row)
        return out


@mcp.tool()
def get_material(material_id: int) -> dict:
    """재료 상세: 메타데이터 + 시편·시험 물성 + 화·물리 물성 전체(도메인별).

    properties에 thermal·electrical·optical·chemical·physical·mechanical 등 모든 도메인의
    값(단위·조건·신뢰등급·출처·DOI)이 들어간다. 인장 시험이 없는 카탈로그 재료도
    이 필드로 물성을 볼 수 있다.
    """
    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": "재료를 찾을 수 없습니다."}
        specs = []
        for sp in s.query(Specimen).filter_by(material_id=material_id).all():
            tests = []
            for t in s.query(Test).filter_by(specimen_id=sp.id).all():
                pr = s.query(ProcessedResult).filter_by(test_id=t.id).one_or_none()
                # valid 플래그를 노출 — 웹에서 이상치로 제외(invalid)한 시험을 LLM이
                # 유효 물성으로 오인하지 않도록(list_materials·웹 상세와 정합).
                info = {"test_id": t.id, "test_type": t.test_type,
                        "valid": t.valid, "invalid_reason": t.invalid_reason}
                if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
                    info.update(kind="viscoelastic", E0_MPa=_mpa(pr.extra_metrics.get("E0_pa")),
                                Einf_MPa=_mpa(pr.extra_metrics.get("Einf_pa")),
                                tau_s=pr.extra_metrics.get("tau_s"))
                elif pr:
                    info.update(kind="elastoplastic", E_GPa=_gpa(pr.youngs_modulus_pa),
                                yield_MPa=_mpa(pr.yield_strength_pa), UTS_MPa=_mpa(pr.uts_pa),
                                elong_pct=round((pr.fracture_elongation or 0) * 100, 1))
                tests.append(info)
            specs.append({"specimen_id": sp.id, "label": sp.label,
                          "orientation": sp.orientation, "standard": sp.standard, "tests": tests})
        # 화·물리 물성(카탈로그)도 함께 — 기계 물성만 보이던 문제 해결.
        pv_rows = (s.query(PropertyValue, PropertyDefinition)
                   .join(PropertyDefinition, PropertyDefinition.key == PropertyValue.property_key)
                   .filter(PropertyValue.material_id == material_id)
                   .order_by(PropertyDefinition.domain, PropertyValue.quality_tier).all())
        props: dict[str, list] = {}
        for pv, d in pv_rows:
            src = pv.source
            props.setdefault(d.domain, []).append({
                "key": pv.property_key, "name": d.name,
                "value": pv.value_num if pv.value_num is not None else pv.value_text,
                "unit": pv.unit, "conditions": pv.conditions, "quality_tier": pv.quality_tier,
                "source": (src.publisher or src.title) if src else None,
                "doi": src.doi if src else None})
        return {"id": mat.id, "name": mat.name, "category": mat.category,
                "description": mat.description, "attributes": mat.attributes,
                "specimens": specs,
                "properties": props,                      # 도메인별 화·물리 물성
                "n_properties": len(pv_rows),
                "property_domains": sorted(props.keys())}


@mcp.tool()
def list_property_definitions(domain: str | None = None) -> list[dict]:
    """채울 수 있는 화·물리 물성 taxonomy(정의 레지스트리) 157종을 11개 도메인으로 반환한다 — 정의 목록일 뿐 각 key 에 값이 들어 있는지는 알려주지 않는다. 여기서 얻은 key 는 search_catalog_property·catalog_property_distribution·ashby_data·register_property 에 넣는다(get_material_properties 는 key 가 아니라 domain 만 받는다).

    도메인: mechanical·interface(접착·박리)·thermal·electrical·optical·chemical·physical·
    acoustic·magnetic·rheological·structure.
    각 항목의 key를 register_property/get_material_properties에 사용.
    """
    with SessionLocal() as s:
        q = s.query(PropertyDefinition)
        if domain:
            q = q.filter(PropertyDefinition.domain == domain)
        rows = q.order_by(PropertyDefinition.domain, PropertyDefinition.key).all()
        return [{"key": d.key, "domain": d.domain, "name": d.name, "symbol": d.symbol,
                 "unit": d.si_unit, "value_type": d.value_type, "standard": d.test_standard,
                 "conditions": d.condition_axes} for d in rows]


@mcp.tool()
def get_material_properties(material_id: int, domain: str | None = None) -> dict:
    """재료의 화·물리 물성값을 도메인별로 상한 없이 전부 반환한다(값·단위·조건·불확도·신뢰등급·출처). 정렬은 도메인 → quality_tier(1=측정 최상 … 5=추정) 순이라 같은 물성의 값 여러 건이 서로 떨어져 나온다. 상온·고체 우선 같은 대표값 선정 규칙은 적용하지 않으니 물성당 대표값 1개가 필요하면 compare_materials·search_catalog_property 를 쓴다. 물성이 많은 재료(최대 512건, 40만 자)는 반드시 domain 인자로 좁혀 호출한다 — property_key 인자는 없으며 넣어도 무시된다.

    한 물성에 출처·조건이 다른 값이 여러 개 공존할 수 있다(모두 반환, 등급 내림차순).
    """
    with SessionLocal() as s:
        if not s.get(Material, material_id):
            return {"error": "재료를 찾을 수 없습니다."}
        q = (s.query(PropertyValue, PropertyDefinition)
             .join(PropertyDefinition, PropertyDefinition.key == PropertyValue.property_key)
             .filter(PropertyValue.material_id == material_id))
        if domain:
            q = q.filter(PropertyDefinition.domain == domain)
        out: dict[str, list] = {}
        for pv, d in q.order_by(PropertyDefinition.domain, PropertyValue.quality_tier).all():
            src = pv.source
            out.setdefault(d.domain, []).append({
                "key": pv.property_key, "name": d.name,
                "value": pv.value_num if pv.value_num is not None else pv.value_text,
                "unit": pv.unit, "uncertainty": pv.uncertainty, "conditions": pv.conditions,
                "method": pv.method, "quality_tier": pv.quality_tier,
                "source": ({"title": src.title, "url": src.url, "doi": src.doi,
                            "manufacturer": src.publisher, "kind": src.kind,
                            "detail": pv.source_detail} if src else None)})
        return {"material_id": material_id, "domains": out,
                "n_values": sum(len(v) for v in out.values())}


@mcp.tool()
def find_materials_by_metadata(manufacturer: str | None = None, material_class: str | None = None,
                               subsystem: str | None = None, grade: str | None = None,
                               process: str | None = None, application: str | None = None,
                               category: str | None = None, limit: int = 100) -> list[dict]:
    """재료 attributes 메타데이터(제조사·재료계열·서브시스템·그레이드·공정·용도)로만 부분일치 검색한다 — 물성값으로는 검색하지 못한다(그건 search_catalog_property). 인자를 하나도 주지 않으면 전 재료를 돌려주고, 기본 limit 100 에서 총계 없이 조용히 잘린다. limit 에 상한이 없어 limit=1000 으로 전 재료 열거가 가능하다(list_materials 의 200건 상한을 넘는 유일한 경로).

    카탈로그 추론 지원: 예) manufacturer='Mitsui'(그 업체 재료), material_class='COC'(모든 COC
    그레이드), subsystem='battery'(배터리 재료), process='injection molding'. attributes에 저장된
    구조화 메타데이터를 조회한다. 결과에 물성 개수(n_properties)도 포함.
    """
    want = {k: v for k, v in {
        "manufacturer": manufacturer, "material_class": material_class, "subsystem": subsystem,
        "grade": grade, "process": process, "application": application}.items() if v}
    with SessionLocal() as s:
        q = s.query(Material)
        if category:
            q = q.filter(Material.category == category)
        out = []
        for m in q.order_by(Material.id).all():
            a = m.attributes or {}
            if all(str(v).lower() in str(a.get(k, "") or "").lower() for k, v in want.items()):
                n = s.query(func.count(PropertyValue.id)).filter_by(material_id=m.id).scalar()
                out.append({"id": m.id, "name": m.name, "code": m.material_code,
                            "category": m.category, "manufacturer": a.get("manufacturer"),
                            "grade": a.get("grade"), "material_class": a.get("material_class"),
                            "trade_name": a.get("trade_name"), "subsystem": a.get("subsystem"),
                            "n_properties": n})
        return out[:limit]


@mcp.tool()
def compare_materials(materials: list[str]) -> dict:
    """재료 2~12종을 카탈로그 물성값으로 나란히 비교한다 — materials 는 문자열 배열만 받으므로 id 도 ["73","68"] 처럼 문자열로 넘겨야 한다([73, 68] 은 스키마 검증 오류). 비교표는 카탈로그 물성(PropertyValue)만으로 만들고 인장·완화 시험 결과(E·UTS·항복·연신율)는 포함하지 않는다 — 시험값까지 보려면 get_material. 13개 이상 넘기면 앞 12개만 쓰고 나머지는 경고 없이 버린다.

    materials: 재료 이름 또는 id 리스트(예: ["APEL 5014CL", "Kapton PI Adhesive Tape"] 또는 [73, 68]).
    한 계열 전체(예: 동박 3종 + PI필름 3종)를 한 번에 넘겨 표로 훑을 수 있다.
    각 재료·물성은 신뢰등급 최상의 대표값 1개로 정렬되어, 웹 UI와 동일한 일관된 비교표를 반환한다.
    반환: materials(순서=컬럼), comparison(공통 물성 우선, 도메인·물성별 각 재료 값·신뢰등급·출처),
    highest/lowest(그 물성의 최대·최소 재료 — '우열'이 아니라 값의 크기), n_shared.
    """
    with SessionLocal() as s:
        ids, errors = resolve_material_ids(s, materials[:12])
        if len(ids) < 2:
            return {"error": "비교하려면 유효한 재료 2개 이상 필요", "resolution_errors": errors}
        data = build_comparison(s, ids)
        name_by_id = {m["id"]: m["name"] for m in data["materials"]}
        rows = []
        for dom in data["domains"]:
            for p in dom["properties"]:
                values = {}
                for c in p["cells"]:
                    if c is None:
                        continue
                    nm = name_by_id[c["material_id"]]
                    values[nm] = {
                        "value": c["value"] if c["value"] is not None else c["value_text"],
                        "unit": c["unit"], "tier": c["tier"], "method": c["method"],
                        "conditions": c["conditions"],
                        "source": (c["source"] or {}).get("manufacturer") or (c["source"] or {}).get("title"),
                    }
                rows.append({
                    "domain": p["domain"], "property": p["name"], "symbol": p["symbol"],
                    "unit": p["unit"], "standard": p["standard"], "values": values,
                    "highest": name_by_id.get(p["max_material_id"]),
                    "lowest": name_by_id.get(p["min_material_id"]),
                })
        return {
            "materials": [{"name": m["name"], "manufacturer": m.get("manufacturer"),
                           "grade": m.get("grade"), "material_class": m.get("material_class"),
                           "category": m["category"]} for m in data["materials"]],
            "n_properties": data["n_properties"], "n_shared": data["n_shared"],
            "rule": data["rule"], "comparison": rows,
            **({"resolution_errors": errors} if errors else {}),
        }


@mcp.tool()
def ashby_data(x_property: str = "physical.density",
               y_property: str = "mechanical.youngs_modulus") -> dict:
    """카탈로그 물성 임의 2축 Ashby 산점 좌표 데이터 — 157종 key 전 도메인 조합 가능(기본 밀도×영률 332점). 값은 신뢰등급 대표값의 SI 원단위 생값이고 point 수 제한이 없다(기본 조합 약 88KB). plot_ashby(인장 E–UTS 44건 이미지)와는 데이터원·축·단위가 다르며 그 데이터판이 아니다.

    x_property·y_property: property_key(예: 'physical.density', 'mechanical.youngs_modulus').
    후보 key는 list_property_definitions로 확인. x·y를 모두 가진 재료만, 각 재료의 대표값
    (신뢰등급 최상)으로 좌표를 만든다. 반환: x/y 축(이름·단위), points[{name,x,y,category,
    subsystem,manufacturer,material_class}], n_points. 재료 선택·아웃라이어 판단에 사용.
    """
    with SessionLocal() as s:
        data = scatter_dataset(s, x_property, y_property)
        if data is None:
            return {"error": f"알 수 없는 물성 key(x={x_property!r}, y={y_property!r}). "
                             "list_property_definitions로 key 확인."}
        return {"x": data["x"], "y": data["y"], "rule": data["rule"],
                "n_points": len(data["points"]), "points": data["points"]}


@mcp.tool()
def register_property(material_id: int, property_key: str, value: float | None = None,
                      value_text: str | None = None, unit: str | None = None,
                      conditions: dict | None = None, uncertainty: float | None = None,
                      method: str = "measured", quality_tier: int = 3,
                      source_doi: str | None = None, source_url: str | None = None,
                      source_title: str | None = None, source_kind: str = "journal",
                      source_manufacturer: str | None = None,
                      source_authors: str | None = None, source_year: int | None = None,
                      source_local_path: str | None = None,
                      notes: str | None = None) -> dict:
    """재료에 물성값 1건을 근거(출처)와 함께 등록 — list_property_definitions 의 157개 key 전 도메인이 대상이다(mechanical 54·optical 18·thermal 16·chemical 15·physical 13·electrical 11·interface 9·structure 7·magnetic 5·rheological 5·acoustic 4). 시험 데이터 없이 카탈로그 물성을 채우는 표준 경로다.

    property_key는 list_property_definitions의 key. 근거 없는 값은 저장하지 않으므로
    source_doi/source_url/source_title 중 하나는 필수. method: measured/handbook/datasheet/
    computed/estimated/**digitized**. quality_tier 1(측정)~5(추정).
    digitized: **그림에서 읽은 값**이다. 인쇄된 숫자가 아니므로 measured 로 넣으면 안 된다
    (40차 BF 가 Uddeholm 고온인장 곡선 95행을 넣으면서 드러났다 — 조건에는 남겼는데
    method 가 measured 로 정규화돼 인쇄 실측과 구별이 안 됐다). 온도·습도 등은 conditions에.
    source_manufacturer: 데이터시트면 업체명(예: "Mitsui Chemicals"·"3M") — 프로비넌스에
    업체를 1급으로 남겨 "어느 업체 값인지" 추론 가능하게 한다.
    source_authors/source_year: 저자·연도. **꼭 채워라** — 기채굴 조회(mined_index)가
    `성+연도` 인용키 축으로 중복을 잡는데, 이 둘이 비면 그 축을 **제목에서 역추출**할 수밖에 없어
    적중률이 떨어진다(36차 AQ 가 짚었다: 출처 2743건 중 2644건이 authors NULL).
    source_local_path: 코퍼스 원문 경로. **코퍼스에서 캔 값이면 반드시 채워라** —
    경로가 그 논문의 정확한 식별자라 제목 정규화(45자 절단·충돌)에 기대지 않아도 된다.
    지금 출처의 97%가 이 값이 비어 있어 기채굴 조회의 경로 축이 사실상 죽어 있다.
    """
    from app.acquire.store import upsert_property_value, upsert_source

    if value is None and value_text is None:
        return {"error": "value 또는 value_text 중 하나는 필요합니다."}
    if not (source_doi or source_url or source_title):
        return {"error": "출처(source_doi·source_url·source_title 중 하나)가 필요합니다(근거 필수)."}
    if method not in ("measured", "handbook", "datasheet", "computed", "estimated",
                      "digitized"):
        return {"error": "method는 measured/handbook/datasheet/computed/estimated 중 하나."}
    if not (1 <= quality_tier <= 5):
        return {"error": "quality_tier는 1~5."}
    with SessionLocal() as s:
        if not s.get(Material, material_id):
            return {"error": "재료를 찾을 수 없습니다."}
        src = upsert_source(s, kind=source_kind, doi=source_doi, url=source_url,
                            title=source_title, publisher=source_manufacturer,
                            authors=source_authors, year=source_year,
                            local_path=source_local_path)
        try:
            pv, created = upsert_property_value(
                s, material_id=material_id, property_key=property_key, value_num=value,
                value_text=value_text, unit=unit, uncertainty=uncertainty, conditions=conditions,
                method=method, quality_tier=quality_tier, source=src, notes=notes)
        except ValueError as exc:
            return {"error": str(exc)}
        s.commit()
        return {"property_value_id": pv.id, "material_id": material_id,
                "property_key": property_key, "created": created,
                "message": "등록 완료." if created else "기존 값 갱신(동일 출처·조건)."}


@mcp.tool()
def get_curve(test_id: int, kind: str = "nominal", max_points: int = 200) -> dict:
    """한 시험(test_id)의 곡선 포인트를 LTTB 다운샘플로 반환. kind: nominal(공칭 σ-ε)·true(진응력, necking 포함)·relaxation(점탄성 E(t)) — 이 3개 외의 값은 경고 없이 nominal 로 폴백하니 반드시 셋 중 하나를 써라. max_points(기본 200)는 목표 점수이며 원본보다 크게 줘도 원본 점수까지만 나온다."""
    with SessionLocal() as s:
        if not s.get(Test, test_id):
            return {"error": "시험을 찾을 수 없습니다."}
    try:
        df = curve_store.read_curve(test_id)
    except FileNotFoundError:
        return {"error": "곡선 파일이 없습니다(정리되었거나 미저장)."}
    if kind == "true":
        if "eng_strain" not in df.columns:
            return {"error": "이 시험은 인장 곡선이 없습니다(점탄성은 kind='relaxation' 사용)."}
        en = np.asarray(df["eng_strain"]); es = np.asarray(df["eng_stress_Pa"])
        from app import true_stress
        c = true_stress.true_curve_with_necking(en, es)
        x, y = np.asarray(c["true_strain"]), np.asarray(c["true_stress"])
        xl, yl = "true_strain", "true_stress_Pa"
        neck = c["necking"]
    else:
        cols = {"nominal": ("eng_strain", "eng_stress_Pa"), "relaxation": ("time_s", "relax_modulus_Pa")}
        xl, yl = cols.get(kind, cols["nominal"])
        if xl not in df.columns or yl not in df.columns:
            have = "relaxation" if "time_s" in df.columns else "nominal/true"
            return {"error": f"kind={kind!r} 곡선이 없습니다. 이 시험은 {have} 곡선만 있습니다."}
        x, y = np.asarray(df[xl], dtype=float), np.asarray(df[yl], dtype=float)
        neck = None
    xs, ys = curve_store.lttb_downsample(x[np.isfinite(x)], y[np.isfinite(y)], n_out=max_points)
    return {"kind": kind, "x_label": xl, "y_label": yl, "n": int(xs.size),
            "x": [round(float(v), 6) for v in xs], "y": [round(float(v), 3) for v in ys],
            "necking": neck}


@mcp.tool()
def get_fits(test_id: int) -> list[dict]:
    """인장 시험의 소성경화 구성방정식 피팅(Hollomon/Swift/Voce/Johnson-Cook)과 R²·파라미터 — 시험 73건 중 43건만 보유하며, 점탄성 시험과 존재하지 않는 test_id 는 구분 없이 빈 리스트를 돌려준다(점탄성 Prony 계수는 get_mat_card·get_material 참조)."""
    with SessionLocal() as s:
        rows = s.query(ConstitutiveFit).filter_by(test_id=test_id).order_by(ConstitutiveFit.r2.desc()).all()
        return [{"model": r.model, "r2": round(r.r2, 4) if r.r2 else None,
                 "params": r.params, "n_points": r.n_points} for r in rows]


@mcp.tool()
def get_mat_card(test_id: int, units: str = "ton_mm_s", model: str = "piecewise") -> str:
    """시험 1건(test_id)의 LS-DYNA 재료카드 텍스트 — 시험 보유 73건 한정이며, 카드 값은 그 시험의 물성만 쓴다(RO 7850 kg/m^3·PR 0.3 은 고정 기본값이라 카탈로그 밀도·포아송비를 반영하지 않음). 탄소성→*MAT_024(하강곡선 20점 재샘플)·johnson_cook(*MAT_098), 점탄성→*MAT_VISCOELASTIC. 재료 544건 전체를 카탈로그 밀도·PR·열물성·CTE·출처까지 넣어 덱으로 뽑으려면 export_dyna_cards 를 써라.

    units: ton_mm_s(기본)·kg_m_s·g_mm_ms·kg_mm_ms. model: piecewise·johnson_cook(탄소성만).
    """
    try:
        u = get_system(units)
    except ValueError as exc:
        return f"error: {exc}"
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            return "error: 시험을 찾을 수 없습니다."
        pr = s.query(ProcessedResult).filter_by(test_id=test_id).one_or_none()
        if pr is None:
            return "error: 물성이 아직 계산되지 않았습니다."
        mat = test.specimen.material
        if (pr.extra_metrics or {}).get("kind") == "viscoelastic":
            p = pr.extra_metrics.get("lsdyna_prony", {})
            rho_t = (mat.attributes or {}).get("prony_lsdyna", {}).get("RHO") or 1.1e-9
            # GI는 0(완전 완화)이 유효값 — falsy 폴백 금지(None일 때만 기본값).
            gi = p.get("GI")
            return viscoelastic.mat_viscoelastic_card(
                title=mat.name, rho_si=rho_t * 1.0e12,
                bulk_pa=(p.get("BULK") or 2000.0) * 1.0e6, G0_pa=(p.get("G0") or 1.0) * 1.0e6,
                Ginf_pa=(0.1 if gi is None else gi) * 1.0e6, beta=p.get("BETA") or 1.0, units=u)
        if not pr.youngs_modulus_pa or pr.youngs_modulus_pa <= 0:
            return "error: 유효한 영률이 없어 카드를 만들 수 없습니다(물성 재계산 필요)."
        try:
            df = curve_store.read_curve(test_id)
        except FileNotFoundError:
            return "error: 곡선 파일이 없습니다."
        ep, st = _plastic_true(df, pr.youngs_modulus_pa)
        gen = lsdyna_mat098_card if model == "johnson_cook" else lsdyna_mat024_card
        return gen(title=mat.name, E_pa=pr.youngs_modulus_pa,
                   yield_pa=pr.yield_strength_pa, plastic_strain=ep, true_stress=st, units=u,
                   nu=poisson_from_attributes(mat.attributes))


@mcp.tool()
def search_by_property(prop: str = "UTS_MPa", min_value: float = 0, max_value: float = 1e9,
                       limit: int = 30) -> list[dict]:
    """인장 시험 처리결과(ProcessedResult) 전용 검색 — prop 은 UTS_MPa·yield_MPa·E_GPa 3종뿐이고 모집단은 유효 인장시험 44건이다(재료 카탈로그 544건이 아님). 흡습률·CTE·유전율·열전도 등 전 도메인 물성과 카탈로그 기준 UTS/E(각 312·339건)는 search_catalog_property 를 써라. 기본 limit=30."""
    field = {"UTS_MPa": ProcessedResult.uts_pa, "yield_MPa": ProcessedResult.yield_strength_pa,
             "E_GPa": ProcessedResult.youngs_modulus_pa}.get(prop)
    if field is None:
        return [{"error": f"지원하지 않는 물성 '{prop}' — UTS_MPa·yield_MPa·E_GPa 중 하나."}]
    scale = 1e6 if "MPa" in prop else 1e9
    with SessionLocal() as s:
        # 유효 시험만 검색(웹·list_materials와 정합 — 제외된 이상치는 배제).
        rows = (s.query(Material.name, ProcessedResult)
                .join(Test, Test.id == ProcessedResult.test_id)
                .join(Specimen, Specimen.id == Test.specimen_id)
                .join(Material, Material.id == Specimen.material_id)
                .filter(Test.valid == True,  # noqa: E712
                        field.isnot(None), field >= min_value * scale, field <= max_value * scale)
                .order_by(field.desc()).limit(limit).all())
        return [{"name": nm, "test_id": pr.test_id, prop: round(getattr(pr, field.key) / scale, 2)}
                for nm, pr in rows]


@mcp.tool()
def plot_curve(test_id: int, kind: str = "auto") -> Image:
    """시험 1건(test_id)의 곡선을 PNG 로 렌더한다 — 시험 보유 73건 한정. kind='auto' 면 탄소성은 공칭+진응력 σ-ε(넥킹 마커), 점탄성은 완화 E(t) 로그곡선. 탄소성 시험만 'nominal'/'true' 강제가 유효하고 점탄성 시험은 kind 와 무관하게 항상 완화 곡선을 그린다. 여러 재료를 겹쳐 비교하려면 plot_curves.

    kind='auto'면 탄소성은 공칭+진응력 σ-ε(넥킹 마커), 점탄성은 완화 E(t) 로그곡선.
    'nominal'/'true'/'relaxation'으로 강제 지정도 가능.
    """
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            raise ValueError("시험을 찾을 수 없습니다.")
        pr = s.query(ProcessedResult).filter_by(test_id=test_id).one_or_none()
        mat = test.specimen.material
        is_visco = bool(pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic")
        name = mat.name
    try:
        df = curve_store.read_curve(test_id)
    except FileNotFoundError:
        raise ValueError("곡선 파일이 없습니다(정리되었거나 미저장).")
    # 곡선 종류와 실제 컬럼 불일치 방어(점탄성에 인장 요청 등).
    want_relax = is_visco or kind == "relaxation"
    if want_relax and "relax_modulus_Pa" not in df.columns:
        raise ValueError("완화 곡선이 없습니다(이 시험은 인장 곡선).")
    if not want_relax and "eng_strain" not in df.columns:
        raise ValueError("인장 곡선이 없습니다(이 시험은 완화 곡선 — kind='relaxation').")

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=120)
    fig.patch.set_facecolor("#0A0E14"); ax.set_facecolor("#070A0F")

    if is_visco or kind == "relaxation":
        t = np.asarray(df["time_s"], dtype=float); E = np.asarray(df["relax_modulus_Pa"], dtype=float) / 1e6
        ax.semilogx(t, E, color="#34D399", lw=2)
        ax.set_xlabel("time  t (s)"); ax.set_ylabel("relaxation modulus  E(t) (MPa)")
        ax.set_title(f"{name} — viscoelastic relaxation", color="#E6EBF2")
        if pr:
            em = pr.extra_metrics
            ax.axhline(em["Einf_pa"] / 1e6, color="#5E6B7D", ls="--", lw=1, label=f"E∞={em['Einf_pa']/1e6:.2f} MPa")
            ax.axhline(em["E0_pa"] / 1e6, color="#56B4E9", ls=":", lw=1, label=f"E₀={em['E0_pa']/1e6:.2f} MPa")
            ax.legend(loc="best", framealpha=0.2)
    else:
        en = np.asarray(df["eng_strain"], dtype=float); es = np.asarray(df["eng_stress_Pa"], dtype=float) / 1e6
        ax.plot(en, es, color="#56B4E9", lw=2, label="engineering σ")
        if kind in ("auto", "true"):
            from app import true_stress
            c = true_stress.true_curve_with_necking(np.asarray(df["eng_strain"]), np.asarray(df["eng_stress_Pa"]))
            ax.plot(c["true_strain"], np.asarray(c["true_stress"]) / 1e6, color="#34D399", lw=1.5, ls="--", label="true σ")
            nk = c["necking"]
            if nk and nk["strain"] is not None:
                ax.plot(nk["strain"], nk["stress"] / 1e6, "^", color="#F0A92C", ms=9,
                        label=f"necking ε_t={nk['strain']:.3f}")
        ax.set_xlabel("strain  ε"); ax.set_ylabel("stress  σ (MPa)")
        E = _gpa(pr.youngs_modulus_pa) if pr else None
        U = _mpa(pr.uts_pa) if pr else None
        ax.set_title(f"{name} — E={E} GPa, UTS={U} MPa", color="#E6EBF2")
        ax.legend(loc="best", framealpha=0.2)

    ax.grid(True, color="#1C2530", lw=0.6)
    for sp in ax.spines.values():
        sp.set_color("#26303D")
    fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return Image(data=buf.getvalue(), format="png")


_CURVE_PALETTE = ["#56B4E9", "#E69F00", "#34D399", "#CC79A7", "#F0A92C", "#8FA1B3", "#D55E00", "#9AA7B8"]


def _rep_test_for_material(s, material_id: int):
    """재료의 대표 시험 — 유효 시험 우선, id 오름차순 첫 건(없으면 None)."""
    return (s.query(Test)
            .join(Specimen, Specimen.id == Test.specimen_id)
            .filter(Specimen.material_id == material_id)
            .order_by(Test.valid.desc(), Test.id)
            .first())


@mcp.tool()
def plot_curves(materials: list | None = None, test_ids: list | None = None,
                kind: str = "nominal", max_points: int = 300) -> Image:
    """여러 재료·시험의 σ-ε 곡선을 한 그래프에 겹쳐 비교한다(PNG, 최대 12개이며 초과분은 그림에 표시 없이 잘림) — 인장 시험이 없는 재료는 제외하지 않고 카탈로그 스칼라(E·항복·UTS·연신율)에서 곡선을 합성해 점선으로 함께 그린다. 실선=실측, 점선=합성 근사이므로 반드시 구분해 해석하고, 실측 곡선만 필요하면 test_ids 로 시험을 직접 지정하라.

    materials: 재료 이름/ID 리스트 — 각 재료의 대표 유효 시험 곡선을 겹쳐 그린다.
    test_ids: 시험 ID로 직접 지정(materials 대신). kind: nominal(공칭 σ-ε)·true(진응력)·
    relaxation(점탄성 E(t)). 각 곡선은 다운샘플(기본 300점)로 로드해 대용량이어도 빠르다(최대 12개).
    카탈로그 물성만 있고 인장 곡선이 없는 재료는 명확히 알린다(멈추지 않음).
    """
    curves = []   # (label, x, y, kind, provenance)
    missing = []
    synth_targets = []   # 실측 곡선이 없어 합성으로 대체할 재료
    with SessionLocal() as s:
        pairs = []  # (label, test_id)
        pair_mid = {}   # test_id → material_id (합성 폴백용)
        if test_ids:
            for tid in list(test_ids)[:12]:
                t = s.get(Test, int(tid))
                if t is None:
                    missing.append(f"test {tid}")
                else:
                    pairs.append((f"{t.specimen.material.name} · {t.specimen.label}", t.id))
                    pair_mid[t.id] = t.specimen.material_id
        else:
            ids, errs = resolve_material_ids(s, list(materials or [])[:12])
            missing.extend(errs)
            for mid in ids:
                t = _rep_test_for_material(s, mid)
                nm = s.get(Material, mid).name
                if t is None:
                    synth_targets.append((nm, mid))     # 실측 없음 → 합성 시도
                else:
                    pairs.append((nm, t.id))
                    pair_mid[t.id] = mid

    want_relax = kind == "relaxation"
    # 시험 레코드는 있으나 곡선 파일이 없거나 종류가 다른 경우 → 합성 후보로 넘긴다.
    def _fallback(label, tid, why):
        mid = pair_mid.get(tid)
        if mid is not None and not want_relax:
            synth_targets.append((label, mid))
        else:
            missing.append(f"{label}({why})")

    for label, tid in pairs:
        try:
            df = curve_store.read_curve(tid)
        except FileNotFoundError:
            _fallback(label, tid, "곡선 파일 없음")
            continue
        if want_relax:
            if "relax_modulus_Pa" not in df.columns:
                missing.append(f"{label}(완화 곡선 아님)"); continue
            x = np.asarray(df["time_s"], dtype=float); y = np.asarray(df["relax_modulus_Pa"], dtype=float) / 1e6
        elif kind == "true":
            if "eng_strain" not in df.columns:
                _fallback(label, tid, "인장 곡선 아님"); continue
            from app import true_stress
            c = true_stress.true_curve_with_necking(np.asarray(df["eng_strain"]), np.asarray(df["eng_stress_Pa"]))
            x = np.asarray(c["true_strain"], dtype=float); y = np.asarray(c["true_stress"], dtype=float) / 1e6
        else:
            if "eng_strain" not in df.columns:
                _fallback(label, tid, "인장 곡선 아님"); continue
            x = np.asarray(df["eng_strain"], dtype=float); y = np.asarray(df["eng_stress_Pa"], dtype=float) / 1e6
        m = np.isfinite(x) & np.isfinite(y)
        xs, ys = curve_store.lttb_downsample(x[m], y[m], n_out=max(50, min(int(max_points), 2000)))
        curves.append((label, xs, ys, KIND_MEASURED, f"실측 인장시험(test {tid})"))

    # 실측이 없는 재료는 스칼라 물성에서 곡선을 합성한다(그래프에 '합성'으로 명시).
    if synth_targets and not want_relax:
        with SessionLocal() as s2:
            for nm, mid in synth_targets:
                c = synth_for_material(s2, mid)
                if c is None:
                    missing.append(f"{nm}(곡선·스칼라 모두 없음)")
                else:
                    curves.append((nm, np.asarray(c["strain"]),
                                   np.asarray(c["stress_pa"]) / 1e6, KIND_SYNTHETIC,
                                   c.get("provenance", "출처 미상")))
    elif synth_targets:
        missing.extend(f"{nm}(완화 곡선 없음)" for nm, _ in synth_targets)

    if not curves:
        raise ValueError("겹쳐 그릴 곡선이 없습니다 — " + (", ".join(missing) or "대상 없음")
                         + ". (카탈로그 물성만 있는 재료는 σ-ε 곡선이 없음. 인장 시험이 있는 재료를 지정하세요.)")

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(7.8, 5.0 + 0.18 * min(len(curves), 6)), dpi=120)
    fig.patch.set_facecolor("#0A0E14"); ax.set_facecolor("#070A0F")
    n_syn = sum(1 for c in curves if c[3] == KIND_SYNTHETIC)
    for i, (label, xs, ys, kind, prov) in enumerate(curves):
        col = _CURVE_PALETTE[i % len(_CURVE_PALETTE)]
        syn = kind == KIND_SYNTHETIC
        # 실측=실선, 합성=점선 + 라벨에 [합성] 명시(혼동 방지).
        (ax.semilogx if want_relax else ax.plot)(
            xs, ys, color=col, lw=1.8, ls=":" if syn else "-", alpha=0.9 if syn else 1.0,
            label=f"{label}  [합성]" if syn else f"{label}  [실측]")
    if want_relax:
        ax.set_xlabel("time  t (s)"); ax.set_ylabel("relaxation modulus  E(t) (MPa)")
        ax.set_title("재료 완화 곡선 비교", color="#E6EBF2")
    else:
        ax.set_xlabel("strain  ε"); ax.set_ylabel("stress  σ (MPa)")
        ax.set_title(f"재료 응력-변형률 비교 ({'true' if kind == 'true' else 'nominal'})", color="#E6EBF2")
    ax.legend(loc="best", framealpha=0.2, fontsize=8)
    ax.grid(True, color="#1C2530", lw=0.6)
    for sp in ax.spines.values():
        sp.set_color("#26303D")
    if n_syn:
        ax.text(0.01, 0.99,
                f"점선 = 스칼라 물성에서 합성한 근사 곡선({n_syn}건, 실측 아님)",
                transform=ax.transAxes, ha="left", va="top", fontsize=7, color="#F0A92C")
    # 출처(프로비넌스) 푸터 — 곡선마다 한 줄.
    prov_lines = [f"· {lb[:30]}: {pv}" for lb, _, _, _, pv in curves[:6]]
    if missing:
        ax.text(0.99, 0.01, "제외: " + ", ".join(missing[:4]) + ("…" if len(missing) > 4 else ""),
                transform=ax.transAxes, ha="right", va="bottom", fontsize=6.5, color="#8FA1B3")
    fig.tight_layout()
    if prov_lines:
        # tight_layout 이후에 하단 여백을 확보해야 축 라벨과 겹치지 않는다.
        pad = 0.030 * (len(prov_lines) + 1)
        fig.subplots_adjust(bottom=fig.subplotpars.bottom + pad)
        fig.text(0.012, 0.010, "출처(프로비넌스)\n" + "\n".join(prov_lines),
                 fontsize=6.0, color="#8FA1B3", va="bottom", ha="left", linespacing=1.5)
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return Image(data=buf.getvalue(), format="png")


@mcp.tool()
def database_summary() -> dict:
    """DB 요약 — 재료 수·카테고리 분포와 인장/완화 시험·구성방정식 피팅 레코드 수만 반환한다. 화·물리 물성 카탈로그(11개 도메인·정의 157종, 재료당 수십~수백 건의 물성값)의 규모는 이 요약에 포함되지 않으므로, 여기 tests_by_type 만 보고 'DB 에 인장 물성뿐'이라 판단하면 안 된다. 물성 쪽 규모는 list_property_definitions(정의 157종)·list_materials 의 n_properties·catalog_property_distribution 으로 확인한다."""
    with SessionLocal() as s:
        from collections import Counter
        cats = Counter(x[0] for x in s.query(Material.category).all())
        ttypes = Counter(x[0] for x in s.query(Test.test_type).all())
        return {"materials": s.query(func.count(Material.id)).scalar(),
                "by_category": dict(cats), "tests_by_type": dict(ttypes),
                "constitutive_fits": s.query(func.count(ConstitutiveFit.id)).scalar()}


@mcp.tool()
def material_taxonomy() -> dict:
    """재료 '이름 정규식' 기반 클래스·계열 분포(544건 전체, 그중 344건은 'Other *' 미분류) + 구성모델 종류(탄소성 44·점탄성 29) — 시험유형 분포는 database_summary, 물성 taxonomy는 list_property_definitions."""
    with SessionLocal() as s:
        return insights.overview(s)


@mcp.tool()
def property_distribution() -> dict:
    """인장시험 피팅 물성 4종(E·UTS·항복·연신율)만의 분포 — 인장 해석 완료 재료 44건 한정(전체 544건 아님). 카탈로그 전 물성(157종·11도메인) 분포는 catalog_property_distribution(property_key)."""
    with SessionLocal() as s:
        return insights.property_stats(s)


@mcp.tool()
def coverage_gaps() -> list[dict]:
    """재료 '계열' 보유량 갭 — 하드코딩된 기대 계열 15종 대비 재료 개수(>=5 rich·1~4 sparse·0 missing). 물성 커버리지가 아니고 계열은 이름 정규식 분류라 근사값이며, 지식그래프(nodes/edges)는 반환하지 않는다."""
    with SessionLocal() as s:
        return insights.coverage_gaps(s)["coverage"]


@mcp.tool()
def find_materials_in_property_range(
    E_min_gpa: float = 0, E_max_gpa: float = 1e9,
    uts_min_mpa: float = 0, uts_max_mpa: float = 1e9, limit: int = 30,
) -> list[dict]:
    """E(GPa)–UTS(MPa) 2축 고정 Ashby 박스 검색 — 축 변경 불가이며 모집단은 인장시험이 있는 44건뿐이다(전체 재료 544건이 아님). 다른 물성 축이나 전 도메인 범위 검색은 search_catalog_property(단일 key + min/max)를 써라. 기본 limit=30."""
    with SessionLocal() as s:
        pts = insights.property_space(s)["points"]
    out = [p for p in pts if E_min_gpa <= p["E_gpa"] <= E_max_gpa
           and uts_min_mpa <= p["uts_mpa"] <= uts_max_mpa]
    out.sort(key=lambda p: -p["uts_mpa"])
    return [{"name": p["name"], "id": p["id"], "cls": p["cls"],
             "E_gpa": p["E_gpa"], "uts_mpa": p["uts_mpa"], "test_id": p["test_id"]}
            for p in out[:limit]]


@mcp.tool()
def export_dyna_cards(materials: list, card: str = "mechanical",
                      units: str = "ton_mm_s", mid_start: int = 1,
                      lcid_start: int = 990001) -> dict:
    """재료 리스트를 LS-DYNA 재료카드 덱으로 대량 출력한다 — 이름만 줘도 유사검색+MID 자동배정, 시험이 없고 카탈로그 물성만 있는 재료까지 포함해 재료 544건 전체가 대상이다. card='mechanical' 은 보유 물성에 따라 *MAT_ELASTIC(001)·*MAT_PIECEWISE_LINEAR_PLASTICITY(024, SIGY+ETAN 이선형 근사로 측정 곡선 LCSS 는 넣지 않음)·*MAT_VISCOELASTIC(006)·*MAT_GENERAL_VISCOELASTIC(076)을 자동 선택한다. 측정 σ-ε 곡선을 그대로 담은 단일 카드는 get_mat_card.

    materials: 재료 이름 또는 ID 리스트(수십 개 한 번에 가능). 이름은 정확→부분→유사(오타)
      순으로 매칭하며, 매칭 근거를 matched_by로 돌려준다.
      MID 지정: "101, 이름" / "101:이름" / {"mid":101,"material":"이름"} — 지정하면 그대로 쓴다.
      PART 지정: "101, 5, 이름"(MID·PID·이름) 또는 "101, 5;6;7, 이름"(여러 PART) —
      PID를 주면 CTE(*MAT_ADD_THERMAL_EXPANSION + *DEFINE_CURVE)까지 만든다.
      여러 줄 문자열(표 붙여넣기)도 그대로 받는다.
    card: 'mechanical'(*MAT_ELASTIC 또는 항복 보유 시 *MAT_PIECEWISE_LINEAR_PLASTICITY) ·
      'thermal'(*MAT_THERMAL_ISOTROPIC — 밀도·비열·열전도율) · 'both'.
    units: ton_mm_s(기본, MPa) · kg_m_s(SI) · g_mm_ms · kg_mm_ms.
    mid_start: MID/TMID 시작번호(1,2,3… 순차 자동 배정).

    lcid_start: CTE 곡선 LCID 시작번호(기존 모델 곡선과 충돌 피하려 큰 번호 기본).
    반환: keyword(붙여넣기 가능한 전체 덱), materials(MID↔재료 매핑표), parts(PID↔MID↔LCID↔CTE),
    skipped(물성 부족으로 생성 못한 것과 사유), resolution_errors.
    각 물성 값 옆에 출처를 $ 주석으로 남긴다.
    """
    if card not in ("mechanical", "thermal", "both"):
        return {"error": "card는 mechanical|thermal|both 중 하나"}
    with SessionLocal() as s:
        return build_dyna_cards(s, list(materials or []), card=card, units=units,
                                mid_start=int(mid_start), lcid_start=int(lcid_start))


@mcp.tool()
def search_catalog_property(property_key: str, min_value: float | None = None,
                            max_value: float | None = None, order: str = "desc",
                            limit: int = 30) -> dict:
    """화·물리 전 도메인 카탈로그 물성(정의 157 key·데이터 보유 148 key, 11개 도메인)으로 재료 544건을 검색·랭킹 — 흡습률·CTE·유전율·열전도·광학·자성·접착 등. 인장 3종 전용 search_by_property 와 달리 카탈로그 기준 UTS/E/연신율도 여기서 조회한다. limit 기본 30·상한 200(총 매칭 수는 count).

    property_key: list_property_definitions의 key(예: chemical.water_absorption_24h,
    thermal.expansion_linear, electrical.dielectric_constant). min_value/max_value로 범위 필터,
    order='desc'|'asc'. 각 재료의 대표값(신뢰등급 최상)과 단위·신뢰등급·업체·출처(프로비넌스)를 반환.
    (인장 E/UTS 전용 search_by_property와 달리 전 도메인 물성 조회 가능.)
    """
    with SessionLocal() as s:
        rk = property_ranking(s, property_key, min_value=min_value, max_value=max_value,
                              order=order, limit=max(1, min(int(limit), 200)))
        if rk is None:
            return {"error": f"알 수 없는 property_key '{property_key}'. "
                             "list_property_definitions로 key 확인."}
        return rk


@mcp.tool()
def catalog_property_distribution(property_key: str) -> dict:
    """카탈로그 물성 1종의 재료 간 분포 — property_key 필수, 11개 도메인 157종 전부 지원(역학·전기·광학·음향 포함). n·min·max·평균·중앙 + 상위 3·하위 3 재료를 SI 원단위 생값으로 반환(히스토그램 없음). 인장 4종 전용판은 property_distribution.

    property_key: list_property_definitions의 key. 인장 전용 property_distribution과 달리
    흡습률·CTE·유전율 등 카탈로그 전 물성의 분포를 본다.
    """
    with SessionLocal() as s:
        st = property_stats(s, property_key)
        if st is None:
            return {"error": f"알 수 없는 property_key '{property_key}'. "
                             "list_property_definitions로 key 확인."}
        return st


@mcp.tool()
def plot_ashby() -> Image:
    """인장시험 피팅 완료 재료 44건(사실상 금속 전용, 전체 544건 아님)의 E–UTS 로그-로그 Ashby 산점도 이미지 — 축 고정·인자 없음. 임의 물성 2축과 폴리머·세라믹·복합재까지 보려면 ashby_data(x_property, y_property)."""
    with SessionLocal() as s:
        pts = insights.property_space(s)["points"]
    fam_color = {"steel": "#56B4E9", "aluminum": "#E69F00", "titanium": "#CC79A7",
                 "magnesium": "#009E73", "nickel": "#F0A92C", "copper": "#D55E00",
                 "refractory": "#8FA1B3", "metal": "#9AA7B8"}
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(7.6, 5.2), dpi=120)
    fig.patch.set_facecolor("#0A0E14"); ax.set_facecolor("#070A0F")
    fams = sorted({p["family"] for p in pts})
    for fam in fams:
        fp = [p for p in pts if p["family"] == fam]
        ax.scatter([p["E_gpa"] for p in fp], [p["uts_mpa"] for p in fp],
                   s=[30 + 12 * (p.get("density") or 3) for p in fp],
                   c=fam_color.get(fam, "#9AA7B8"), alpha=0.8, edgecolors="black",
                   linewidths=0.4, label=fam)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Young's modulus  E (GPa)"); ax.set_ylabel("UTS  (MPa)")
    ax.set_title("Ashby material property space  (E–UTS)", color="#E6EBF2")
    ax.legend(loc="lower right", framealpha=0.2, fontsize=8, ncol=2)
    ax.grid(True, which="both", color="#1C2530", lw=0.5)
    for sp in ax.spines.values():
        sp.set_color("#26303D")
    fig.tight_layout()
    buf = io.BytesIO(); fig.savefig(buf, format="png", facecolor=fig.get_facecolor())
    plt.close(fig)
    return Image(data=buf.getvalue(), format="png")


# ════════════════════════════════════════════════════════════════════════════
# 쓰기 도구 — 재료 등록/시험 등록/수정/삭제. 웹 API와 동일 검증·저장 경로(C2·C4).
# ════════════════════════════════════════════════════════════════════════════

# 시드와 동일한 명목 시편 치수(mm 입력 기본값). 물성은 응력-변형률에서 나오므로 무관.
_DEF_GAUGE_MM, _DEF_WIDTH_MM, _DEF_THICK_MM = 50.0, 12.5, 2.0
_VALID_CATEGORIES = ("metal", "polymer", "rubber", "composite", "ceramic", "foam")


def _next_label(s, material_id: int) -> str:
    """해당 재료의 다음 시편 라벨(S1, S2, …)."""
    n = s.query(func.count(Specimen.id)).filter(Specimen.material_id == material_id).scalar() or 0
    return f"S{n + 1}"


def _add_specimen(s, material_id: int, label: str | None = None, **kwargs) -> "Specimen":
    """시편을 생성·커밋한다. (material_id,label) UNIQUE 경합 시 라벨을 재계산해 재시도.

    동시 등록이 COUNT 기반 라벨을 경합해도 조용한 중복 대신 유일 라벨을 보장한다.
    label 명시 시 충돌하면 접미사(-2, -3…)를 붙인다.
    """
    from sqlalchemy.exc import IntegrityError

    base = label
    for attempt in range(8):
        lbl = (label or _next_label(s, material_id)) if attempt == 0 else \
            (f"{base}-{attempt + 1}" if base else _next_label(s, material_id))
        spec = Specimen(material_id=material_id, label=lbl, **kwargs)
        s.add(spec)
        try:
            s.commit()
            return spec
        except IntegrityError:
            s.rollback()
    raise RuntimeError("시편 라벨 생성 재시도 초과")


def _validate_arrays(x: list[float], y: list[float], xname: str, yname: str,
                     min_points: int = 20) -> str | None:
    """배열 쌍 공통 검증. 문제 있으면 한국어 사유, 없으면 None."""
    if not isinstance(x, (list, tuple)) or not isinstance(y, (list, tuple)):
        return f"{xname}/{yname}는 숫자 배열이어야 합니다."
    if len(x) != len(y):
        return f"{xname}({len(x)})와 {yname}({len(y)}) 길이가 다릅니다."
    if len(x) < min_points:
        return f"점이 너무 적습니다({len(x)} < {min_points}). 물성 계산에 최소 {min_points}점 필요."
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if not (np.all(np.isfinite(xa)) and np.all(np.isfinite(ya))):
        return "NaN/Inf 값이 포함되어 있습니다."
    return None


@mcp.tool()
def register_material(name: str, category: str = "metal", material_code: str | None = None,
                      description: str | None = None, attributes: dict | None = None) -> dict:
    """새 재료를 등록한다. category: metal/polymer/rubber/composite/ceramic/foam. material_code 는 전사 고유코드(중복 시 에러), attributes 로 자유형 JSON(포아송비 nu 등)을 함께 저장한다. 등록 후 카탈로그 물성은 register_property 로 붙이고(시험 없이도 가능), 곡선 시험이 있으면 register_tensile_test/register_relaxation_test 를 쓴다.

    material_code는 전사 고유코드(중복 시 에러). attributes로 자유형 JSON(포아송비 nu,
    전단탄성계수 G_MPa 등 수동 상수)을 함께 저장할 수 있다. 등록 후 register_tensile_test
    또는 register_relaxation_test로 시험 데이터를 붙인다.
    """
    name = (name or "").strip()
    if not name or len(name) > 200:
        return {"error": "name은 1~200자 필수입니다."}
    if category not in _VALID_CATEGORIES:
        return {"error": f"category는 {'/'.join(_VALID_CATEGORIES)} 중 하나여야 합니다."}
    if attributes is not None and not isinstance(attributes, dict):
        return {"error": "attributes는 객체(dict)여야 합니다."}
    attrs = {"source": "mcp", **(attributes or {})}
    from sqlalchemy.exc import IntegrityError
    with SessionLocal() as s:
        mat = Material(name=name, material_code=material_code or None, category=category,
                       description=(description or None),
                       attributes=attrs)
        s.add(mat)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return {"error": f"material_code '{material_code}'가 이미 존재합니다."}
        return {"material_id": mat.id, "name": mat.name, "category": mat.category,
                "message": "등록 완료. register_tensile_test/register_relaxation_test로 시험을 추가하세요."}


@mcp.tool()
def register_tensile_test(material_id: int, strain: list[float], stress_mpa: list[float],
                          specimen_label: str | None = None,
                          gauge_length_mm: float = _DEF_GAUGE_MM,
                          width_mm: float = _DEF_WIDTH_MM,
                          thickness_mm: float = _DEF_THICK_MM,
                          strain_source: str = "extensometer",
                          orientation: str | None = None) -> dict:
    """인장시험 곡선(공칭 변형률[무차원]·공칭 응력[MPa])을 등록하고 물성·피팅까지 자동 계산.

    시편을 자동 생성(치수 mm)하고 곡선 저장 → E·항복·UTS·연신 계산 →
    Hollomon/Swift/Voce/Johnson-Cook 피팅까지 수행한다. 저항복 재료는 탄성창을 자동 보정.
    orientation: 시편 방위(예: "0"/"90"/"45", "RD"/"TD") — 이방성·적층 해석용, 선택.
    """
    err = _validate_arrays(strain, stress_mpa, "strain", "stress_mpa")
    if err:
        return {"error": err}
    if strain_source not in ("extensometer", "crosshead"):
        return {"error": "strain_source는 extensometer 또는 crosshead여야 합니다."}
    en = np.asarray(strain, dtype=float)
    sp_mpa = np.asarray(stress_mpa, dtype=float)
    if float(np.nanmax(sp_mpa)) > 1e5:
        return {"error": "stress_mpa 값이 비정상적으로 큽니다 — MPa 단위인지 확인하세요(Pa 아님)."}
    if not (gauge_length_mm > 0 and width_mm > 0 and thickness_mm > 0):
        return {"error": "시편 치수는 모두 양수(mm)여야 합니다."}
    stress_pa = sp_mpa * 1e6
    L0, W0, T0 = gauge_length_mm * 1e-3, width_mm * 1e-3, thickness_mm * 1e-3
    A0 = W0 * T0

    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": f"material_id {material_id} 없음. register_material 먼저."}
        # 변형률 단위 착오 검사 — 엘라스토머류는 연신 200% 초과가 정상이라 카테고리별 상한.
        strain_cap = {"rubber": 10.0, "foam": 10.0, "polymer": 5.0}.get(mat.category or "", 2.0)
        if float(np.nanmax(en)) > strain_cap:
            return {"error": f"strain 최대값 {np.nanmax(en):.3g} > {strain_cap}"
                             f"({mat.category or 'metal'} 상한) — 무차원 변형률이어야 합니다(% 아님)."}
        spec = _add_specimen(s, material_id, label=specimen_label,
                             geometry_type="flat", gauge_length_m=L0, width_m=W0, thickness_m=T0,
                             area0_m2=A0, standard="mcp", orientation=orientation)
        test = Test(specimen_id=spec.id, test_type="tensile", strain_source=strain_source,
                    source_format="mcp", valid=True)
        s.add(test); s.commit()  # test.id 확정(C2).

        # 곡선 저장 — ingest와 동일 6컬럼 고정 스키마, 트랜잭션 밖 원자적 쓰기(C4).
        import pandas as pd
        n = en.size
        df = pd.DataFrame({"time": np.full(n, np.nan), "force_N": stress_pa * A0,
                           "disp_m": en * L0, "extenso_strain": en,
                           "eng_stress_Pa": stress_pa, "eng_strain": en})
        try:
            rel_path = curve_store.write_curve(test.id, df)
        except Exception as exc:
            # 자동 생성한 시편까지 롤백(delete-orphan cascade로 test도 함께 정리).
            s.delete(spec); s.commit()
            return {"error": f"곡선 저장 실패: {exc}"}
        s.add(RawCurveRef(test_id=test.id, storage="parquet_fs", file_path=rel_path,
                          n_points=int(n), channels=["force", "displacement", "strain", "stress"]))

        # 탄성 회귀: 기본창이 성긴 곡선에서 소성점을 물면 r²가 무너진다 —
        # 점차 좁은 창으로 재시도해 r²≥0.995인 첫 결과를 채택(전부 미달이면 최고 r²).
        metrics = None
        best = None
        for e_range in ((0.0005, 0.0025), (0.0002, 0.0015), (0.0001, 0.001)):
            m = analysis.compute_all(en, stress_pa, A0=A0, e_range=e_range, category=mat.category)
            r2 = getattr(m["params"], "r2", None)
            if best is None or ((r2 or 0) > (getattr(best["params"], "r2", None) or 0)):
                best = m
            if m["youngs_modulus_pa"] and r2 is not None and r2 >= 0.995:
                metrics = m
                break
        if metrics is None:
            metrics = best
        pr = ProcessedResult(
            test_id=test.id,
            youngs_modulus_pa=metrics["youngs_modulus_pa"],
            yield_strength_pa=metrics["yield_strength_pa"],
            uts_pa=metrics["uts_pa"],
            uniform_elongation=metrics["uniform_elongation"],
            fracture_elongation=metrics["fracture_elongation"],
            strain_hardening_n=metrics["strain_hardening_n"],
            strength_coeff_k_pa=metrics["strength_coeff_k_pa"],
            params=metrics["params"].model_dump(),
            extra_metrics=metrics["extra_metrics"],
        )
        s.add(pr); s.commit()

        # 저항복 보정: εy=σy/E < 기본창 상한이면 탄성창을 [0.15εy, 0.7εy]로 재계산(seed._fix_modulus).
        warnings = []
        E, sy = pr.youngs_modulus_pa, pr.yield_strength_pa
        if E and sy and np.isfinite(E) and np.isfinite(sy) and E > 0:
            ey = sy / E
            if ey < 0.0036:
                lo, hi = max(1e-4, 0.15 * ey), max(2e-4, 0.7 * ey)
                # 좁은 창에 점이 부족하면(성긴 곡선) 회귀가 무의미 — 보정 생략.
                # 2점 회귀는 R²=1이라 R²로는 못 거르고 점 수로 가드한다.
                n_win = int(np.sum((en >= lo) & (en <= hi)))
                m2 = (analysis.compute_all(en, stress_pa, A0=A0, e_range=(lo, hi), category=mat.category)
                      if n_win >= 5 else {"youngs_modulus_pa": None})
                E2 = m2["youngs_modulus_pa"]
                # 정당한 보정은 1차 추정과 같은 자릿수(0.5~2배) — 벗어나면 성긴 데이터 아티팩트.
                if (E2 and np.isfinite(E2) and abs(E2 - E) / E > 0.005
                        and 0.5 <= E2 / E <= 2.0):
                    pr.youngs_modulus_pa = E2
                    pr.yield_strength_pa = m2["yield_strength_pa"]
                    pr.strain_hardening_n = m2["strain_hardening_n"]
                    pr.strength_coeff_k_pa = m2["strength_coeff_k_pa"]
                    pr.params = m2["params"].model_dump()
                    s.commit()
                    warnings.append("저항복 재료 — 탄성창을 항복변형률 기준으로 자동 보정했습니다.")

        # 구성방정식 피팅.
        fit_summary = []
        if pr.youngs_modulus_pa and pr.youngs_modulus_pa > 0:
            dfc = curve_store.read_curve(test.id)
            ep, st = _plastic_true(dfc, pr.youngs_modulus_pa)
            for r in fitting.fit_all(ep, st):
                if r.get("params") is None:
                    continue
                s.add(ConstitutiveFit(test_id=test.id, model=r["model"], params=r["params"],
                                      r2=r.get("r2"), rmse_pa=r.get("rmse_pa"),
                                      n_points=r.get("n_points")))
                fit_summary.append({"model": r["model"], "r2": round(r["r2"], 4) if r.get("r2") else None})
            s.commit()
        else:
            warnings.append("영률 계산 실패 — 탄성 구간 데이터가 부족합니다. 카드 생성 불가.")

        return {"material_id": material_id, "specimen_id": spec.id, "test_id": test.id,
                "properties": {"E_GPa": _gpa(pr.youngs_modulus_pa), "yield_MPa": _mpa(pr.yield_strength_pa),
                               "UTS_MPa": _mpa(pr.uts_pa),
                               "elong_pct": round((pr.fracture_elongation or 0) * 100, 1)},
                "fits": fit_summary, "warnings": warnings,
                "message": "등록 완료. get_mat_card(test_id)로 LS-DYNA 카드를 뽑을 수 있습니다."}


@mcp.tool()
def register_relaxation_test(material_id: int,
                             G0_mpa: float | None = None, Ginf_mpa: float | None = None,
                             beta_per_s: float | None = None,
                             time_s: list[float] | None = None,
                             modulus_mpa: list[float] | None = None,
                             nu: float = 0.45, bulk_mpa: float | None = None,
                             rho_t_mm3: float | None = None) -> dict:
    """점탄성 완화시험을 등록한다. 두 입력 모드 중 하나를 사용.

    (A) Prony 파라미터: G0_mpa·Ginf_mpa·beta_per_s (LS-DYNA *MAT_VISCOELASTIC 정의,
        G(t)=Ginf+(G0-Ginf)e^{-βt}) — 완화 영률 곡선을 생성해 저장.
    (B) 실측 곡선: time_s[초]·modulus_mpa[완화 영률 E(t), MPa] — Prony 3항 피팅 후 저장.
    등록 후 get_mat_card로 *MAT_VISCOELASTIC 카드를 도출할 수 있다.
    """
    mode_a = all(isinstance(v, (int, float)) for v in (G0_mpa, Ginf_mpa, beta_per_s))
    mode_b = time_s is not None and modulus_mpa is not None
    if not mode_a and not mode_b:
        return {"error": "입력 부족 — (A) G0_mpa·Ginf_mpa·beta_per_s 또는 (B) time_s·modulus_mpa 필요."}
    if mode_a and (G0_mpa <= 0 or Ginf_mpa < 0 or beta_per_s <= 0 or G0_mpa <= Ginf_mpa):
        return {"error": "G0>Ginf≥0, beta>0 이어야 합니다(단위: MPa, 1/s)."}
    if not (0.0 <= nu < 0.5):
        return {"error": "nu(포아송비)는 [0, 0.5) 범위여야 합니다."}

    if mode_a:
        rc = viscoelastic.relaxation_curve_from_lsdyna(G0_mpa, Ginf_mpa, beta_per_s, nu)
        t, E_t = np.asarray(rc["time_s"]), np.asarray(rc["E_pa"])
        E0_pa, Einf_pa, tau_s = rc["E0_pa"], rc["Einf_pa"], rc["tau_s"]
        prony_src = {"G0": G0_mpa, "GI": Ginf_mpa, "BETA": beta_per_s, "BULK": bulk_mpa}
    else:
        err = _validate_arrays(time_s, modulus_mpa, "time_s", "modulus_mpa", min_points=8)
        if err:
            return {"error": err}
        t = np.asarray(time_s, dtype=float)
        E_t = np.asarray(modulus_mpa, dtype=float) * 1e6
        if np.any(t < 0) or np.any(E_t <= 0):
            return {"error": "time_s는 0 이상, modulus_mpa는 양수여야 합니다."}
        order = np.argsort(t)
        t, E_t = t[order], E_t[order]
        # 완화곡선은 시간에 따라 감소해야 한다 — 초기 대비 뚜렷이 감소하지 않으면 무효 입력.
        head = float(np.mean(E_t[: max(1, E_t.size // 5)]))
        tail = float(np.mean(E_t[-max(1, E_t.size // 5):]))
        if tail >= 0.98 * head:
            return {"error": "완화 거동이 감지되지 않습니다 — 시간에 따라 감소하는 modulus 곡선이 필요합니다."}
        E0_pa = float(np.max(E_t))
        Einf_pa = float(np.min(E_t))

    fit = viscoelastic.fit_prony(t[t > 0] if mode_b else t, E_t[t > 0] if mode_b else E_t, n_terms=3)
    if fit.get("reason"):
        return {"error": f"Prony 피팅 실패: {fit['reason']} — 시간 범위·점수를 확인하세요."}

    if mode_b:
        # 곡선 모드: 지배항 τ로 1항 등가 Prony를 유도해 카드 생성 경로를 살린다.
        Einf_pa = float(fit.get("E_inf_pa") or Einf_pa)
        terms = fit.get("terms") or []
        if not terms:
            # 지수항 0개 = 감쇠 없음(증가·평탄 곡선) — 물리적으로 완화시험이 아님.
            return {"error": "완화 거동이 감지되지 않습니다 — 시간에 따라 감소하는 modulus 곡선이 필요합니다."}
        dom = max(terms, key=lambda x: x[0])
        tau_s = float(dom[1])
        if tau_s <= 0:
            return {"error": "유효한 완화시간을 추정할 수 없습니다 — 시간 배열을 확인하세요."}
        g_div = 2.0 * (1.0 + nu)
        prony_src = {"G0": E0_pa / g_div / 1e6, "GI": Einf_pa / g_div / 1e6,
                     "BETA": 1.0 / tau_s, "BULK": bulk_mpa}

    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": f"material_id {material_id} 없음. register_material 먼저."}
        pl = {k: v for k, v in prony_src.items() if v is not None}
        if rho_t_mm3:
            pl["RHO"] = rho_t_mm3

        spec = _add_specimen(s, material_id,
                             geometry_type="flat", gauge_length_m=_DEF_GAUGE_MM * 1e-3,
                             width_m=_DEF_WIDTH_MM * 1e-3, thickness_m=_DEF_THICK_MM * 1e-3,
                             area0_m2=_DEF_WIDTH_MM * _DEF_THICK_MM * 1e-6, standard="relaxation")
        test = Test(specimen_id=spec.id, test_type="relaxation", strain_source="relaxation",
                    source_format="mcp", valid=True)
        s.add(test); s.commit()

        import pandas as pd
        df = pd.DataFrame({"time_s": t, "relax_modulus_Pa": E_t})
        try:
            rel_path = curve_store.write_curve(test.id, df)
        except Exception as exc:
            # 자동 생성한 시편까지 롤백(delete-orphan cascade로 test도 함께 정리).
            s.delete(spec); s.commit()
            return {"error": f"곡선 저장 실패: {exc}"}
        s.add(RawCurveRef(test_id=test.id, storage="parquet_fs", file_path=rel_path,
                          n_points=int(t.size),
                          channels=[{"name": "time_s", "unit_si": "s"},
                                    {"name": "relax_modulus_Pa", "unit_si": "Pa"}]))
        # 카드 생성이 참조하는 attributes.prony_lsdyna 갱신 — 곡선 저장 성공 이후에만
        # 커밋해 실패 시 백킹 시험 없는 Prony 파라미터가 남지 않게 한다.
        attrs = dict(mat.attributes or {})
        attrs["prony_lsdyna"] = {**attrs.get("prony_lsdyna", {}), **pl}
        attrs.setdefault("source", "mcp")
        mat.attributes = attrs
        pr = ProcessedResult(
            test_id=test.id, params={"schema_version": 1, "kind": "viscoelastic"},
            youngs_modulus_pa=E0_pa,
            extra_metrics={"kind": "viscoelastic", "E0_pa": E0_pa, "Einf_pa": Einf_pa,
                           "tau_s": tau_s,
                           "prony_fit": {"E_inf_pa": fit.get("E_inf_pa"), "terms": fit.get("terms"),
                                         "r2": fit.get("r2"), "n_terms": fit.get("n_terms")},
                           "lsdyna_prony": pl},
        )
        s.add(pr); s.commit()
        return {"material_id": material_id, "specimen_id": spec.id, "test_id": test.id,
                "E0_MPa": _mpa(E0_pa), "Einf_MPa": _mpa(Einf_pa), "tau_s": round(tau_s, 6),
                "prony_r2": round(fit["r2"], 4) if fit.get("r2") is not None else None,
                "message": "점탄성 등록 완료. get_mat_card(test_id)로 *MAT_VISCOELASTIC 카드를 뽑을 수 있습니다."}


@mcp.tool()
def update_material(material_id: int, name: str | None = None, category: str | None = None,
                    description: str | None = None, material_code: str | None = None,
                    attributes: dict | None = None) -> dict:
    """재료 메타데이터를 부분 수정한다(전달한 필드만 갱신).

    attributes: 자유형 JSON을 기존 값에 얕은 병합(키 단위 덮어쓰기). 단축인장에서
    나오지 않는 상수(포아송비 nu, 전단탄성계수 G_MPa 등)나 방위·출처 메모를 저장한다.
    """
    if category is not None and category not in _VALID_CATEGORIES:
        return {"error": f"category는 {'/'.join(_VALID_CATEGORIES)} 중 하나여야 합니다."}
    if attributes is not None and not isinstance(attributes, dict):
        return {"error": "attributes는 객체(dict)여야 합니다."}
    from sqlalchemy.exc import IntegrityError
    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": "material not found"}
        if name is not None:
            if not name.strip() or len(name) > 200:
                return {"error": "name은 1~200자여야 합니다."}
            mat.name = name.strip()
        if category is not None:
            mat.category = category
        if description is not None:
            mat.description = description or None
        if material_code is not None:
            mat.material_code = material_code or None
        if attributes is not None:
            # JSON 컬럼은 새 dict 재대입으로 변경을 감지시킨다(in-place 변경은 누락 위험).
            mat.attributes = {**(mat.attributes or {}), **attributes}
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return {"error": f"material_code '{material_code}'가 이미 존재합니다."}
        return {"material_id": mat.id, "name": mat.name, "category": mat.category,
                "material_code": mat.material_code, "attributes": mat.attributes,
                "message": "수정 완료."}


@_destructive_tool
def delete_material(material_id: int, confirm: bool = False) -> dict:
    """재료와 하위 시편·시험·곡선을 삭제한다(파괴적 — confirm=True 필요).

    confirm=False면 삭제 대상 미리보기만 반환한다.
    """
    with SessionLocal() as s:
        mat = s.get(Material, material_id)
        if not mat:
            return {"error": "material not found"}
        tids = [t.id for t in s.query(Test).join(Specimen)
                .filter(Specimen.material_id == material_id).all()]
        n_spec = s.query(func.count(Specimen.id)).filter(Specimen.material_id == material_id).scalar()
        if not confirm:
            return {"preview": {"material": mat.name, "specimens": n_spec, "tests": len(tids)},
                    "message": "삭제하려면 confirm=True로 다시 호출하세요."}
        name = mat.name
        s.delete(mat)  # cascade: specimen→test→ref/pr/fit.
        s.commit()
    for tid in tids:  # Parquet 곡선 파일 정리(DB cascade는 파일을 안 지움).
        curve_store.curve_path(tid).unlink(missing_ok=True)
    return {"deleted": name, "tests_removed": len(tids), "message": "삭제 완료."}


@_destructive_tool
def delete_test(test_id: int, confirm: bool = False) -> dict:
    """시험 1건과 곡선·물성·피팅을 삭제한다(파괴적 — confirm=True 필요)."""
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            return {"error": "test not found"}
        mat_name = test.specimen.material.name if test.specimen and test.specimen.material else "?"
        if not confirm:
            return {"preview": {"test_id": test_id, "material": mat_name, "type": test.test_type},
                    "message": "삭제하려면 confirm=True로 다시 호출하세요."}
        s.delete(test)
        s.commit()
    curve_store.curve_path(test_id).unlink(missing_ok=True)
    return {"deleted_test": test_id, "material": mat_name, "message": "삭제 완료."}


@mcp.tool()
def recompute_properties(test_id: int, e_min: float | None = None, e_max: float | None = None) -> dict:
    """인장시험 1건의 처리결과(E·항복·UTS·균일연신율·파단연신율·n·K)를 재계산하고 구성방정식 피팅을 교체한다(탄성 회귀창 e_min~e_max 무차원 지정 가능) — 카탈로그 물성(property_value)은 건드리지 않으며 반환값에는 E·항복·UTS 만 표시된다. 점탄성 시험은 대상이 아니다.

    영률이 이상하게 나온 경우 탄성 구간을 좁혀 재계산할 때 사용한다(변형률 무차원).
    """
    with SessionLocal() as s:
        test = s.get(Test, test_id)
        if not test:
            return {"error": "test not found"}
        pr = s.query(ProcessedResult).filter_by(test_id=test_id).one_or_none()
        if pr and (pr.extra_metrics or {}).get("kind") == "viscoelastic":
            return {"error": "점탄성 시험은 재계산 대상이 아닙니다(완화곡선은 등록 시 피팅됨)."}
        try:
            df = curve_store.read_curve(test_id)
        except FileNotFoundError:
            return {"error": "곡선 파일이 없습니다."}
        if "eng_strain" not in df.columns:
            return {"error": "인장 곡선이 아닙니다."}
        en = np.asarray(df["eng_strain"], dtype=float)
        st_pa = np.asarray(df["eng_stress_Pa"], dtype=float)
        A0 = test.specimen.area0_m2 if test.specimen else None
        cat = test.specimen.material.category if test.specimen and test.specimen.material else None
        if (e_min is None) != (e_max is None):
            return {"error": "e_min과 e_max는 함께 지정해야 합니다(하나만 주면 무시되지 않고 거부)."}
        kwargs = {}
        if e_min is not None and e_max is not None:
            if not (0 <= e_min < e_max):
                return {"error": "0 ≤ e_min < e_max 이어야 합니다."}
            kwargs["e_range"] = (e_min, e_max)
        metrics = analysis.compute_all(en, st_pa, A0=A0, category=cat, **kwargs)

        def _fill(p):
            p.youngs_modulus_pa = metrics["youngs_modulus_pa"]
            p.yield_strength_pa = metrics["yield_strength_pa"]
            p.uts_pa = metrics["uts_pa"]
            p.uniform_elongation = metrics["uniform_elongation"]
            p.fracture_elongation = metrics["fracture_elongation"]
            p.strain_hardening_n = metrics["strain_hardening_n"]
            p.strength_coeff_k_pa = metrics["strength_coeff_k_pa"]
            p.params = metrics["params"].model_dump()
            p.extra_metrics = metrics["extra_metrics"]

        from sqlalchemy.exc import IntegrityError
        if pr is None:
            # 동시 재계산 경합: test_id UNIQUE 위반 시 rollback→재조회→UPDATE.
            pr = ProcessedResult(test_id=test_id)
            _fill(pr)
            s.add(pr)
            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                pr = s.query(ProcessedResult).filter_by(test_id=test_id).one()
                _fill(pr)
                s.commit()
        else:
            _fill(pr)
            s.commit()

        # 피팅 교체(기존 삭제 후 재계산 — 웹 fits:compute와 동일).
        s.query(ConstitutiveFit).filter_by(test_id=test_id).delete()
        fit_summary = []
        if pr.youngs_modulus_pa and pr.youngs_modulus_pa > 0:
            ep, st = _plastic_true(df, pr.youngs_modulus_pa)
            for r in fitting.fit_all(ep, st):
                if r.get("params") is None:
                    continue
                s.add(ConstitutiveFit(test_id=test_id, model=r["model"], params=r["params"],
                                      r2=r.get("r2"), rmse_pa=r.get("rmse_pa"),
                                      n_points=r.get("n_points")))
                fit_summary.append({"model": r["model"], "r2": round(r["r2"], 4) if r.get("r2") else None})
        s.commit()
        return {"test_id": test_id,
                "properties": {"E_GPa": _gpa(pr.youngs_modulus_pa), "yield_MPa": _mpa(pr.yield_strength_pa),
                               "UTS_MPa": _mpa(pr.uts_pa)},
                "e_range_used": (pr.params or {}).get("e_range"),
                "fits": fit_summary, "message": "재계산 완료."}


# ════════════════════════════════════════════════════════════════════════════
# 리소스·프롬프트 — LLM 클라이언트가 서버 사용법·데이터 규약을 스스로 발견하게.
# ════════════════════════════════════════════════════════════════════════════


@mcp.resource("materialtwin://guide")
def guide() -> str:
    """MaterialTwin MCP 사용 가이드 — 도구 지도·단위 규약·전형적 워크플로."""
    return """# MaterialTwin MCP 가이드

쯔윅 인장/완화 시험 기반 물성 DB. 조회 13종 + 등록/수정/삭제 7종 도구.

## 단위 규약
- 입력 곡선: strain 무차원(% 아님), stress MPa. 완화시험은 time_s[s]·modulus MPa.
- Prony 파라미터: G0/Ginf MPa, beta 1/s (LS-DYNA ton·mm·s 관례).
- LS-DYNA 카드 단위계: ton_mm_s(기본, MPa)·kg_m_s(SI)·g_mm_ms·kg_mm_ms.

## 전형적 워크플로
1) 탐색: database_summary → list_materials / search_by_property /
   find_materials_in_property_range(E·UTS 범위) → get_material(상세)
2) 시각화: plot_curve(test_id) · plot_ashby()
3) 카드 도출: get_mat_card(test_id, units=, model=piecewise|johnson_cook)
   — 탄소성은 *MAT_024(실측 테이블)/*MAT_098(J-C), 점탄성은 *MAT_VISCOELASTIC.
4) 등록: register_material → register_tensile_test(strain[], stress_mpa[])
   또는 register_relaxation_test(Prony 파라미터 or 실측 E(t) 곡선).
   물성·구성방정식 피팅까지 자동 계산됨.
5) 정정: recompute_properties(test_id, e_min, e_max) — 탄성창 지정 재계산.
6) 삭제: delete_material/delete_test — confirm=False면 미리보기, True로 확정.

## 주의
- 등록 시 곡선 최소 20점, NaN 금지. strain 상한: 금속 2.0 / polymer 5 / rubber·foam 10.
- get_material의 시험 목록은 valid 플래그를 포함한다 — valid=false는 웹에서 제외한
  이상치이므로 대표 물성으로 쓰지 말 것(list_materials·search_by_property는 유효 시험만 반환).
- 오류 표기: dict 반환 도구는 {"error": "한국어 사유"}, 카드 텍스트 도구(get_mat_card)는
  "error: 한국어 사유" 문자열, 이미지 도구(plot_*)는 한국어 예외로 알린다.
"""


@mcp.resource("materialtwin://taxonomy")
def taxonomy_resource() -> str:
    """재료 분류 체계(카테고리·계열)와 현재 DB 분포."""
    with SessionLocal() as s:
        rows = insights._material_rows(s)
    from collections import Counter
    by_cls = Counter(r["cls"] for r in rows)
    lines = ["# 재료 분류 체계",
             "",
             "카테고리: metal / polymer / rubber / composite / ceramic / foam",
             "",
             "## 현재 DB 분포(클래스별)"]
    for cls, n in by_cls.most_common():
        lines.append(f"- {cls}: {n}종")
    return "\n".join(lines)


@mcp.prompt()
def find_material(requirements: str) -> str:
    """요구조건(용도·강성·강도·경량화 등)에 맞는 재료를 찾아 카드까지 도출하는 절차."""
    return f"""다음 요구조건에 맞는 재료를 MaterialTwin DB에서 찾아주세요.

요구조건: {requirements}

절차:
1. database_summary와 material_taxonomy로 DB 범위를 파악한다.
2. 요구조건을 E(GPa)·UTS(MPa) 범위로 번역해 find_materials_in_property_range로 후보를 뽑는다.
   경량화가 언급되면 밀도·비강도(plot_ashby의 계열 분리)도 함께 고려한다.
3. 상위 후보 2~3종을 get_material·get_fits로 비교하고 plot_curve로 곡선을 보여준다.
4. 최종 추천 재료의 LS-DYNA 카드를 get_mat_card로 도출한다(해석 단위계 확인).
5. 후보·트레이드오프·추천 근거를 표로 정리한다."""


@mcp.prompt()
def register_test_data(description: str) -> str:
    """시험 데이터를 DB에 등록하는 절차(인장/완화 자동 판별 포함)."""
    return f"""다음 시험 데이터를 MaterialTwin DB에 등록해주세요.

데이터 설명: {description}

절차:
1. 재료가 이미 있는지 list_materials(query=)로 확인한다. 없으면 register_material
   (category: metal/polymer/rubber/composite/ceramic/foam)으로 생성한다.
2. 데이터 종류를 판별한다 — 응력-변형률이면 register_tensile_test
   (strain 무차원·stress MPa), 시간-모듈러스면 register_relaxation_test
   (time_s·modulus_mpa 또는 G0/Ginf/beta Prony 파라미터).
3. 반환된 물성(E·항복·UTS·연신)과 피팅 R²를 검토하고, 영률이 이상하면
   recompute_properties로 탄성창을 지정해 재계산한다.
4. get_mat_card로 카드를 뽑아 결과를 요약한다."""


# ── 시험장비 카탈로그 ────────────────────────────────────────────────────────
# REST(/api/metrology/*)에는 있었으나 MCP 에는 없었다 — 그래서 웹에서는 보이는 장비가
# 챗에서는 "검색이 안 되는" 상태였다. 도구가 없으면 에이전트는 그 데이터의 존재조차 모른다.
# REST 라우터(app/routers/metrology.py)와 같은 질의를 쓰되, 반환은 챗이 읽을 크기로 줄인다.


def _inst_brief(i: Instrument) -> dict:
    return {"id": i.id, "vendor": i.vendor, "model": i.model,
            "category": i.category, "technique": i.technique}


@mcp.tool()
def instrument_summary() -> dict:
    """보유 시험장비 총계 — 몇 대를 어떤 분류·제조사로 갖고 있고 몇 가지 물성을 잴 수 있는가.

    "장비 뭐 있어" 류 질문의 첫 답이다. 개별 장비 열거는 list_instruments,
    특정 물성의 측정 수단은 how_to_measure 를 쓴다.
    """
    with SessionLocal() as s:
        n_inst = s.query(func.count(Instrument.id)).scalar()
        n_cap = s.query(func.count(InstrumentCapability.id)).scalar()
        n_key = s.query(func.count(func.distinct(InstrumentCapability.property_key))).scalar()
        by_cat = dict(s.query(Instrument.category, func.count(Instrument.id))
                      .group_by(Instrument.category).all())
        by_vendor = dict(s.query(Instrument.vendor, func.count(Instrument.id))
                         .group_by(Instrument.vendor)
                         .order_by(func.count(Instrument.id).desc()).limit(15).all())
    return {"instruments": n_inst, "capabilities": n_cap,
            "measurable_properties": n_key,
            "by_category": by_cat, "by_vendor_top15": by_vendor}


@mcp.tool()
def list_instruments(query: str | None = None, category: str | None = None,
                     property_key: str | None = None, limit: int = 40) -> dict:
    """시험장비를 찾는다 — 제조사·모델 부분일치(query), 분류(category), 잴 수 있는 물성(property_key).

    category 는 instrument_summary 의 by_category 키를 쓴다
    (mechanical/thermal/chemical/surface/particle/optical/electrical/ndt/reliability).
    property_key 를 주면 그 물성을 재는 장비만 남는다 — 다만 '어떻게 재는가'가 궁금하면
    기법으로 묶어 주는 how_to_measure 쪽이 답에 가깝다.
    총 건수(total)와 잘렸는지(truncated)를 함께 낸다 — 몇 건인지 모르면 답이 틀린다.
    """
    limit = max(1, min(int(limit), 200))
    with SessionLocal() as s:
        q = s.query(Instrument)
        if category:
            q = q.filter(Instrument.category == category)
        if query:
            like = f"%{query}%"
            q = q.filter((Instrument.vendor.ilike(like)) | (Instrument.model.ilike(like)))
        if property_key:
            q = q.filter(Instrument.id.in_(
                s.query(InstrumentCapability.instrument_id)
                 .filter(InstrumentCapability.property_key == property_key)))
        total = q.count()
        rows = q.order_by(Instrument.vendor, Instrument.model).limit(limit).all()
        items = []
        for i in rows:
            caps = [{"property_key": c.property_key, "technique": c.technique,
                     "standard": c.standard}
                    for c in i.capabilities]
            items.append({**_inst_brief(i), "n_capabilities": len(caps),
                          "measures": caps[:8]})
    return {"total": total, "returned": len(items),
            "truncated": total > len(items), "items": items}


@mcp.tool()
def how_to_measure(property_key: str) -> dict:
    """이 물성을 무엇으로 어떻게 재는가 — 장비가 아니라 **기법**으로 묶어 낸다.

    같은 기법을 하는 장비 여럿은 서로 다른 답이 아니라 선택지다. 규격(standard)은
    능력행마다 다를 수 있어 모아서 낸다 — 하나로 뭉치면 거짓이 된다.
    잴 수단이 아예 없으면 techniques 가 빈 목록이다(그 사실이 곧 답이다).
    property_key 는 list_property_definitions 로 찾는다.
    """
    with SessionLocal() as s:
        d = s.query(PropertyDefinition).filter(PropertyDefinition.key == property_key).first()
        rows = (s.query(InstrumentCapability, Instrument)
                 .join(Instrument, Instrument.id == InstrumentCapability.instrument_id)
                 .filter(InstrumentCapability.property_key == property_key)
                 .order_by(Instrument.vendor, Instrument.model).all())
        n_val = (s.query(func.count(PropertyValue.id))
                  .filter(PropertyValue.property_key == property_key).scalar())
        groups: dict[str, list] = {}
        for c, i in rows:
            groups.setdefault(c.technique, []).append({
                "instrument": _inst_brief(i), "standard": c.standard,
                "range": [c.range_min, c.range_max, c.range_unit],
                "temperature_k": [c.temperature_min_k, c.temperature_max_k],
                "resolution": c.resolution, "accuracy": c.accuracy,
                "specimen": c.specimen, "confidence": c.mapping_confidence,
            })
    return {
        "property": ({"key": d.key, "name": d.name, "domain": d.domain,
                      "si_unit": d.si_unit, "test_standard": d.test_standard}
                     if d else {"key": property_key, "note": "미정의 물성 key"}),
        "values_in_catalog": n_val,
        "techniques": [
            {"technique": t,
             "standards": sorted({x["standard"] for x in items if x["standard"]}),
             "instruments": items}
            for t, items in sorted(groups.items())
        ],
        "note": ("잴 수단이 등록돼 있지 않다 — 외주·신규 도입 대상이다."
                 if not groups else None),
    }


@mcp.tool()
def measurement_gaps(limit: int = 40) -> dict:
    """**잴 장비가 없는 물성**을 낸다 — 카탈로그에 값은 있는데 측정 수단이 없는 것들.

    '문헌에만 있는 물성'을 드러내는 질문이다. 시험 계획에서 외주·신규 도입 후보가 되고,
    해석에 쓰는 값이 사내에서 검증 불가능하다는 뜻이기도 하다.
    values 가 많을수록 (많이 쓰는데 못 재는) 우선순위가 높다.
    """
    limit = max(1, min(int(limit), 200))
    with SessionLocal() as s:
        measurable = {k for (k,) in s.query(
            func.distinct(InstrumentCapability.property_key)).all()}
        used = dict(s.query(PropertyValue.property_key, func.count(PropertyValue.id))
                     .group_by(PropertyValue.property_key).all())
        defs = {d.key: d for d in s.query(PropertyDefinition).all()}
    gaps = [{"property_key": k, "values": n,
             "name": getattr(defs.get(k), "name", None),
             "domain": getattr(defs.get(k), "domain", None)}
            for k, n in used.items() if k not in measurable]
    gaps.sort(key=lambda g: -g["values"])
    return {"n_measurable": len(measurable), "n_used": len(used),
            "n_gaps": len(gaps), "gaps": gaps[:limit],
            "note": "values = 카탈로그에 쌓인 값 개수. 많은데 못 재면 우선순위가 높다."}


def main() -> None:
    """stdio MCP 진입점. **스키마를 맞춘 뒤에 뜬다.**

    HTTP 앱(app/main.py)은 init_db()로 alembic 스키마를 맞추는데 이 진입점은 그러지 않아,
    DATA_DIR 미설정 시 붙는 개발 폴백 DB가 구 스키마(a72e1f3c8b90)에 멈춰 있었다.
    실제로 list_materials가 "no such table: property_definition"으로 죽었다.
    두 진입점이 같은 부팅을 거치게 한다.
    """
    from app.db import init_db
    init_db()
    mcp.run()


if __name__ == "__main__":
    main()
