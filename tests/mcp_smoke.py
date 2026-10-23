from __future__ import annotations

import asyncio

from mcp import Client

from intentos.mcp_server import build_mcp_server


async def _run() -> None:
    server = build_mcp_server()
    async with Client(server, raise_exceptions=True) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools.tools]
        if names != ["prepare_task"]:
            raise AssertionError(f"unexpected MCP tools: {names}")

        result = await client.call_tool(
            "prepare_task",
            {
                "request": "Codex: refactor the parser without changing behavior",
                "constraints": ["No new dependencies"],
                "success_criteria": ["Relevant tests pass"],
            },
        )
        if result.is_error:
            raise AssertionError(f"prepare_task returned an MCP tool error: {result.content}")
        payload = result.structured_content
        if not isinstance(payload, dict) or payload.get("status") != "ready":
            raise AssertionError(f"unexpected prepare_task payload: {payload!r}")
        if payload.get("task_type") != "refactor":
            raise AssertionError(f"unexpected task classification: {payload!r}")


if __name__ == "__main__":
    asyncio.run(_run())
