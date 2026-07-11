# MCP 리소스·프롬프트 노출 검증 — 인메모리 프로토콜 왕복.
from __future__ import annotations

import anyio
from mcp.shared.memory import create_connected_server_and_client_session


def test_resources_and_prompts_exposed(mcp_env):
    M = mcp_env

    async def main():
        async with create_connected_server_and_client_session(M.mcp._mcp_server) as client:
            res = await client.list_resources()
            uris = {str(r.uri) for r in res.resources}
            assert "materialtwin://guide" in uris
            assert "materialtwin://taxonomy" in uris

            guide = await client.read_resource("materialtwin://guide")
            text = guide.contents[0].text
            assert "단위 규약" in text and "register_tensile_test" in text

            prompts = await client.list_prompts()
            names = {p.name for p in prompts.prompts}
            assert {"find_material", "register_test_data"} <= names

            got = await client.get_prompt("find_material", {"requirements": "경량 고강도"})
            assert "경량 고강도" in got.messages[0].content.text

    anyio.run(main)


def test_get_material_exposes_valid_flag(mcp_env):
    # 웹에서 제외한 이상치(valid=False)를 LLM이 구분할 수 있어야 한다(웹↔MCP 정합).
    M = mcp_env
    import numpy as np
    from tests.fixtures.golden_linear_powerlaw import make_golden
    g = make_golden(n_points=300)
    mid = M.register_material("정합검증강", category="metal")["material_id"]
    tid = M.register_tensile_test(mid, g.strain.tolist(), (g.stress / 1e6).tolist())["test_id"]
    # 시험을 invalid로 표시(웹 이상치 제외 미러).
    with M._test_db.SessionLocal() as s:
        from app.models import Test
        s.get(Test, tid).valid = False
        s.commit()
    got = M.get_material(mid)
    t = got["specimens"][0]["tests"][0]
    assert t["valid"] is False and t["invalid_reason"] is not None or t["valid"] is False
    # search_by_property는 유효 시험만 반환하므로 이 재료가 안 나와야 한다.
    hits = M.search_by_property("E_GPa", 100, 300, 50)
    assert all(h.get("test_id") != tid for h in hits if isinstance(h, dict))


def test_mcp_error_messages_korean(mcp_env):
    M = mcp_env
    assert "찾을 수 없" in M.get_material(999999)["error"]
    assert "찾을 수 없" in M.get_curve(999999)["error"]
    assert M.get_mat_card(999999).startswith("error:")
    assert "찾을 수 없" in M.get_mat_card(999999)
    assert "지원하지 않는" in M.search_by_property("BOGUS")[0]["error"]


def test_taxonomy_resource_reflects_db(mcp_env):
    M = mcp_env
    M.register_material("분류검증강", category="metal")

    async def main():
        async with create_connected_server_and_client_session(M.mcp._mcp_server) as client:
            r = await client.read_resource("materialtwin://taxonomy")
            assert "1종" in r.contents[0].text  # 방금 등록한 재료가 분포에 반영.

    anyio.run(main)
