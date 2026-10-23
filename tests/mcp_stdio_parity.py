from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters

from intentos.models import ContextDocument, IntentRequest
from intentos.project import optimize_project_prompt
from intentos.result_contract import result_dict
from intentos.service import optimize_prompt


_AUTHORITATIVE_NAMES = {"AGENTS.md", "STATUS.md", "DECISIONS.md", "ARCHITECTURE.md"}


CASES: tuple[dict[str, Any], ...] = (
    {
        "name": "documentation-security-topic",
        "request": "Update documentation for the login flow",
        "target_tool": "codex",
    },
    {
        "name": "high-risk-production-auth",
        "request": "Deploy the authentication migration to production",
        "target_tool": "codex",
        "constraints": ["No new dependencies"],
        "success_criteria": ["Relevant tests pass"],
    },
    {
        "name": "project-context-selection",
        "request": "Refactor parser token validation",
        "target_tool": "codex",
        "project_context": [
            {
                "path": "AGENTS.md",
                "content": "Parser token validation changes must preserve behavior.",
            },
            {
                "path": "notes.md",
                "content": "Unrelated release notes for the marketing site.",
            },
        ],
    },
    {
        "name": "clarification-without-target",
        "request": "Summarize this design",
    },
)


def _api_payload(case: dict[str, Any]) -> dict[str, object]:
    request = IntentRequest.from_values(
        case["request"],
        target_tool=case.get("target_tool"),
        output_format=case.get("output_format"),
        constraints=case.get("constraints", ()),
        audience=case.get("audience"),
        success_criteria=case.get("success_criteria", ()),
    )
    documents = tuple(
        ContextDocument(
            path=item["path"],
            content=item["content"],
            authoritative=Path(item["path"]).name in _AUTHORITATIVE_NAMES,
        )
        for item in case.get("project_context", ())
    )
    result = optimize_project_prompt(request, documents) if documents else optimize_prompt(request)
    return result_dict(result)


def _cli_payload(case: dict[str, Any]) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temp_dir:
        cwd = Path(temp_dir)
        command = [
            sys.executable,
            "-m",
            "intentos",
            "optimize",
            case["request"],
            "--json",
        ]
        if case.get("target_tool"):
            command.extend(("--target", case["target_tool"]))
        if case.get("output_format"):
            command.extend(("--output-format", case["output_format"]))
        if case.get("audience"):
            command.extend(("--audience", case["audience"]))
        for constraint in case.get("constraints", ()):
            command.extend(("--constraint", constraint))
        for success in case.get("success_criteria", ()):
            command.extend(("--success", success))
        for item in case.get("project_context", ()):
            path = cwd / item["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(item["content"], encoding="utf-8")
            command.extend(("--context-file", item["path"]))

        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode not in {0, 2}:
            raise AssertionError(
                f"CLI failed for {case['name']}: rc={completed.returncode} stderr={completed.stderr!r}"
            )
        return json.loads(completed.stdout)


async def _run() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "intentos.mcp_server"],
    )
    async with Client(server, raise_exceptions=True) as client:
        tools = await client.list_tools()
        names = [tool.name for tool in tools.tools]
        if names != ["prepare_task"]:
            raise AssertionError(f"unexpected MCP tools: {names}")

        for case in CASES:
            arguments = {key: value for key, value in case.items() if key != "name"}
            mcp_result = await client.call_tool("prepare_task", arguments)
            if mcp_result.is_error:
                raise AssertionError(
                    f"MCP failed for {case['name']}: {mcp_result.content!r}"
                )
            mcp_payload = mcp_result.structured_content
            if not isinstance(mcp_payload, dict):
                raise AssertionError(
                    f"MCP returned non-object for {case['name']}: {mcp_payload!r}"
                )

            api_payload = _api_payload(case)
            cli_payload = _cli_payload(case)
            if mcp_payload != api_payload:
                raise AssertionError(
                    f"MCP/API parity failed for {case['name']}:\n"
                    f"MCP={mcp_payload!r}\nAPI={api_payload!r}"
                )
            if mcp_payload != cli_payload:
                raise AssertionError(
                    f"MCP/CLI parity failed for {case['name']}:\n"
                    f"MCP={mcp_payload!r}\nCLI={cli_payload!r}"
                )


if __name__ == "__main__":
    asyncio.run(_run())
