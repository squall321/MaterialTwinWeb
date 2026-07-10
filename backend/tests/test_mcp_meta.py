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


def test_taxonomy_resource_reflects_db(mcp_env):
    M = mcp_env
    M.register_material("분류검증강", category="metal")

    async def main():
        async with create_connected_server_and_client_session(M.mcp._mcp_server) as client:
            r = await client.read_resource("materialtwin://taxonomy")
            assert "1종" in r.contents[0].text  # 방금 등록한 재료가 분포에 반영.

    anyio.run(main)
