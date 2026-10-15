# 데이터 허브 동기화용 내보내기 — 물성·조건·출처가 빠짐없이 나가는지, 페이지가 이어지는지.
from __future__ import annotations


def _export(page: int = 1, size: int = 200) -> dict:
    from app.db import SessionLocal
    from app.routers.hub_export import export_materials
    with SessionLocal() as s:
        return export_materials(page=page, size=size, db=s)


def test_export_carries_properties_conditions_and_source(mcp_env):
    """허브에 나가는 문서 하나가 그 재료의 완결된 물성 카드여야 한다.

    `/api/materials`는 목록이라 attributes가 {"source":"mcp"} 한 줄뿐이고, 그래서 허브에는
    재료 이름만 523건 쌓이고 물성값은 0건이었다. 값만 보내도 안 된다 — 조건이 없으면
    열전도율 0.35가 25 C인지 100 C인지, 면내인지 두께방향인지 모른 채 쓰인다.
    """
    M = mcp_env
    mid = M.register_material(name="HubExportMat", category="polymer")["material_id"]
    M.register_property(
        mid, "thermal.conductivity", value=0.35, unit="W/(m*K)", quality_tier=1,
        method="measured",
        conditions={"temperature_c": 25, "direction": "through-thickness",
                    "test_standard": "ASTM E1461 laser flash"},
        notes="Table 2 'Thermal conductivity' 열",
        source_title="Vendor TDS", source_kind="datasheet",
        source_url="https://example.com/tds.pdf")

    it = next(x for x in _export()["items"] if x["id"] == mid)

    assert it["n_properties"] == 1
    p = it["properties"][0]
    assert p["key"] == "thermal.conductivity"
    assert p["value"] == 0.35 and p["unit"] == "W/(m*K)"
    assert p["tier"] == 1
    # 조건 없는 값은 값이 아니다.
    assert p["conditions"]["temperature_c"] == 25
    assert p["conditions"]["direction"] == "through-thickness"
    assert p["method"] == "measured"
    assert p["conditions"]["test_standard"] == "ASTM E1461 laser flash"
    # 허브에서도 근거를 되짚을 수 있어야 한다.
    assert p["source"]["url"] == "https://example.com/tds.pdf"
    assert it["sources"] and it["sources"][0]["title"] == "Vendor TDS"

    # 허브의 전문검색 대상 — 구조만 보내면 JSON 인덱싱 방식에 의존하게 된다.
    body = it["body"]
    assert "0.35" in body and "W/(m*K)" in body
    assert "temperature_c=25" in body and "tier1" in body


def test_export_sends_every_value_not_a_representative(mcp_env):
    """한 재료가 같은 물성을 조건별로 여럿 가지면 전부 나가야 한다.

    Al6061-T6의 물 접촉각이 무처리 68.6도, 에탄올 세정 88.4도다. 대표값 하나만 보내면
    그 산포가 사라지는데, 표면 상태가 값을 지배하는 물성에서는 산포 자체가 정보다.
    """
    M = mcp_env
    mid = M.register_material(name="SpreadMat", category="metal")["material_id"]
    for ang, treat in ((68.6, "as-received"), (88.4, "ethanol-cleaned")):
        M.register_property(
            mid, "physical.contact_angle_water", value=ang, unit="deg", quality_tier=2,
            conditions={"surface_treatment": treat, "liquid": "water"},
            source_title="paper", source_kind="journal")

    it = next(x for x in _export()["items"] if x["id"] == mid)
    vals = sorted(p["value"] for p in it["properties"]
                  if p["key"] == "physical.contact_angle_water")
    assert vals == [68.6, 88.4], vals
    treats = {p["conditions"]["surface_treatment"] for p in it["properties"]}
    assert treats == {"as-received", "ethanol-cleaned"}


def test_export_emits_next_cursor_so_sync_does_not_stop_at_page_one(mcp_env):
    """허브 sync_svc는 응답에서 next_cursor를 찾고, 없으면 한 페이지에서 끝낸다.

    현 /api/materials가 {items,total,page,size}만 줘서 매 실행 100건에서 멈춰 있었다
    (sync_runs.fetched_count가 계속 100). 마지막 페이지에서만 null이어야 한다.
    """
    M = mcp_env
    for i in range(5):
        M.register_material(name=f"CursorMat{i}", category="metal")

    first = _export(page=1, size=2)
    assert first["next_cursor"] == "2", first["next_cursor"]

    seen, page = set(), 1
    while page:
        d = _export(page=page, size=2)
        seen.update(x["id"] for x in d["items"])
        page = int(d["next_cursor"]) if d["next_cursor"] else None
    assert len(seen) == first["total"], f"{len(seen)} != {first['total']}"


# ---------------------------------------------------------------------------
# 본문을 절로 나눠 내보낸다(HWAX 요청서 10-15 K3-9 가). 예전에는 body 를 6만 자에서 자르고
# 「본문 절단 — 전체는 content.properties 참조」 표지를 붙였고, 허브는 그 body 를 한 절로만 실어
# 긴 재료 카드(material-twin-analyst 앞 300장 중 52장)는 뒤를 볼 길이 없었다.
# 절 하나의 크기 한도는 MATERIALTWIN_HUB_SECTION_MAX_CHARS(기본 60,000자).
# ---------------------------------------------------------------------------
def _limit(monkeypatch, n: int) -> None:
    from app import config as config_mod

    monkeypatch.setenv("MATERIALTWIN_HUB_SECTION_MAX_CHARS", str(n))
    config_mod.get_settings.cache_clear()


def _joined(it: dict) -> str:
    return "".join(s["content_text"] for s in it.get("sections") or [])


def test_export_sections_carry_the_whole_render_without_the_cut_marker(mcp_env, monkeypatch):
    import app.routers.hub_export as hx

    M = mcp_env
    mid = M.register_material(name="LongMat", category="polymer")["material_id"]
    for i in range(30):
        M.register_property(mid, "thermal.conductivity", value=0.3, unit="W/(m*K)",
                            quality_tier=2, conditions={"temperature_c": 100 + i},
                            source_title=f"src{i}", source_kind="datasheet")
    monkeypatch.setattr(hx, "_BODY_MAX_CHARS", 500)   # 옛 body 는 여기서 잘린다
    _limit(monkeypatch, 400)

    it = next(x for x in _export()["items"] if x["id"] == mid)
    full = _joined(it)
    assert "본문 절단" in it["body"]                   # 옛 판 호환 필드는 그대로
    assert "본문 절단" not in full and len(full) > 500  # 절은 자르지 않은 전체
    assert full.startswith(it["body"].split("\n…")[0])
    for i in range(30):
        assert f"temperature_c={100 + i}" in full
    secs = it["sections"]
    assert len(secs) > 1 and all(len(s["content_text"]) <= 400 for s in secs)
    assert [s["section_id"] for s in secs] == [str(i) for i in range(1, len(secs) + 1)]
    assert all(s["level"] == 1 for s in secs)
    assert [s["title"] for s in secs] == [f"본문 ({i}/{len(secs)})" for i in range(1, len(secs) + 1)]
    # 줄 경계에서 나눈다 — 물성 한 줄이 두 절에 걸치지 않는다.
    assert all(s["content_text"].endswith("\n") for s in secs[:-1])


def test_export_cuts_a_line_longer_than_the_limit(mcp_env, monkeypatch):
    M = mcp_env
    mid = M.register_material(name="NoteMat", category="metal")["material_id"]
    M.register_property(mid, "thermal.conductivity", value=1.0, unit="W/(m*K)", quality_tier=1,
                        notes="가" * 1000, source_title="paper", source_kind="journal")
    _limit(monkeypatch, 300)

    it = next(x for x in _export()["items"] if x["id"] == mid)
    assert _joined(it) == it["body"]  # 짧은 카드라 옛 body 도 전체다
    assert all(len(s["content_text"]) <= 300 for s in it["sections"])


def test_a_short_body_is_one_section_shaped_like_the_hub_fallback(mcp_env):
    """한도 안이면 절 하나 — 허브가 body 로 만들던 절과 같은 모양이라 본문 해시가 그대로다
    (재료 수천 장이 다시 임베딩되지 않는다)."""
    M = mcp_env
    mid = M.register_material(name="ShortMat", category="metal")["material_id"]
    M.register_property(mid, "thermal.conductivity", value=1.0, unit="W/(m*K)", quality_tier=1,
                        source_title="paper", source_kind="journal")

    it = next(x for x in _export()["items"] if x["id"] == mid)
    assert it.get("sections") == [{"section_id": "1", "level": 1, "title": "본문",
                                   "content_text": it["body"]}]


def test_hub_section_max_chars_default_and_env(monkeypatch):
    from app.config import Settings

    monkeypatch.delenv("MATERIALTWIN_HUB_SECTION_MAX_CHARS", raising=False)
    assert getattr(Settings(), "hub_section_max_chars", None) == 60_000
    monkeypatch.setenv("MATERIALTWIN_HUB_SECTION_MAX_CHARS", "1000")
    assert getattr(Settings(), "hub_section_max_chars", None) == 1000
