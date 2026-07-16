# MCP streamable HTTP 마운트(/mcp) 회귀 — 페더레이션 핸드셰이크 + 삭제 툴 게이팅.
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent

# 서브프로세스에서 app.main(create_app)로 /mcp 핸드셰이크 후 tools/list를 수행하고
# 결과를 JSON 한 줄로 출력한다. 모듈 리로드 오염 없이 삭제 게이팅 env를 격리해 검증.
_PROBE = r"""
import json, sys
from fastapi.testclient import TestClient
from app.main import create_app

HDR = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}


def _sse(text):
    for line in text.splitlines():
        if line.startswith("data: "):
            return json.loads(line[6:])
    return None


app = create_app()
with TestClient(app) as c:
    # no-slash "/mcp" (게이트웨이/클라이언트가 쓰는 경로) — 리다이렉트 없이 exact 매칭이어야.
    r = c.post("/mcp", headers=HDR, follow_redirects=False, json={
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "probe", "version": "0"}}})
    sid = r.headers.get("mcp-session-id")
    info = _sse(r.text)["result"]["serverInfo"]
    c.post("/mcp", headers={**HDR, "mcp-session-id": sid},
           json={"jsonrpc": "2.0", "method": "notifications/initialized"})
    r2 = c.post("/mcp", headers={**HDR, "mcp-session-id": sid},
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = [t["name"] for t in _sse(r2.text)["result"]["tools"]]
    print(json.dumps({"status": r.status_code, "session": bool(sid),
                      "server": info["name"], "tools": tools}))
"""


def _probe(tmp_path, **env_extra) -> dict:
    env = {**os.environ,
           "MATERIALTWIN_DATA_DIR": str(tmp_path / "data"),
           "MATERIALTWIN_DATABASE_URL": f"sqlite:///{tmp_path / 'p.db'}",
           **env_extra}
    out = subprocess.run([sys.executable, "-c", _PROBE], env=env, cwd=str(_BACKEND),
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-2000:]
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_http_initialize_and_tools_default_hides_deletes(tmp_path):
    # 기본(app.main이 ALLOW_DELETE=0 주입) — 핸드셰이크 성공 + 삭제 툴 미노출(페더레이션 안전).
    res = _probe(tmp_path)
    assert res["status"] == 200 and res["session"]
    assert res["server"] == "materialtwin"
    assert "list_materials" in res["tools"]          # 조회 노출.
    assert "register_tensile_test" in res["tools"]   # 등록 노출(사용자 워크플로).
    assert not [t for t in res["tools"] if "delete" in t]  # 삭제 미노출.


def test_http_deletes_visible_when_explicitly_allowed(tmp_path):
    # MATERIALTWIN_MCP_ALLOW_DELETE=1 명시 → HTTP에서도 삭제 툴 노출(운영자 opt-in).
    res = _probe(tmp_path, MATERIALTWIN_MCP_ALLOW_DELETE="1")
    assert res["status"] == 200
    assert {"delete_material", "delete_test"}.issubset(set(res["tools"]))
