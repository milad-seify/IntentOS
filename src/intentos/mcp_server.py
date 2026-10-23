from __future__ import annotations

import sys
from typing import Any

from .models import ContextDocument, IntentRequest
from .project import optimize_project_prompt
from .result_contract import result_dict
from .service import optimize_prompt


MAX_PROJECT_CONTEXT_CHARS = 6000
MAX_PROJECT_CONTEXT_DOCUMENTS = 32
_AUTHORITATIVE_NAMES = {"AGENTS.md", "STATUS.md", "DECISIONS.md", "ARCHITECTURE.md"}


def _context_documents(
    project_context: list[dict[str, str]] | None,
) -> tuple[ContextDocument, ...]:
    if not project_context:
        return ()
    if len(project_context) > MAX_PROJECT_CONTEXT_DOCUMENTS:
        raise ValueError(
            f"project_context supports at most {MAX_PROJECT_CONTEXT_DOCUMENTS} documents"
        )

    documents: list[ContextDocument] = []
    total_chars = 0
    for index, item in enumerate(project_context, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"project_context[{index}] must be an object")

        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"project_context[{index}].path must be a non-empty string")
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f"project_context[{index}].content must be a non-empty string")

        clean_path = path.strip()
        total_chars += len(content)
        if total_chars > MAX_PROJECT_CONTEXT_CHARS:
            raise ValueError(
                f"project_context exceeds {MAX_PROJECT_CONTEXT_CHARS} characters"
            )

        filename = clean_path.replace("\\", "/").rsplit("/", 1)[-1]
        documents.append(
            ContextDocument(
                path=clean_path,
                content=content,
                authoritative=filename in _AUTHORITATIVE_NAMES,
            )
        )

    return tuple(documents)


def prepare_task(
    request: str,
    target_tool: str | None = None,
    constraints: list[str] | None = None,
    success_criteria: list[str] | None = None,
    project_context: list[dict[str, str]] | None = None,
    output_format: str | None = None,
    audience: str | None = None,
) -> dict[str, object]:
    """Prepare one bounded AI execution contract without executing or mutating anything."""
    documents = _context_documents(project_context)
    intent_request = IntentRequest.from_values(
        request,
        target_tool=target_tool,
        output_format=output_format,
        constraints=constraints or (),
        audience=audience,
        success_criteria=success_criteria or (),
    )
    result = (
        optimize_project_prompt(
            intent_request,
            documents,
            max_context_chars=MAX_PROJECT_CONTEXT_CHARS,
        )
        if documents
        else optimize_prompt(intent_request)
    )
    return result_dict(result)


def build_mcp_server() -> Any:
    """Build the optional MCP v2 stdio server without making MCP a core dependency."""
    try:
        from mcp.server import MCPServer
    except ModuleNotFoundError as error:  # pragma: no cover - exercised by packaging/use
        raise RuntimeError(
            'MCP support is optional. Install it with: pip install "intentos[mcp]"'
        ) from error

    server = MCPServer(
        "IntentOS",
        instructions=(
            "Use prepare_task to turn a user request into a reviewable execution contract. "
            "Preparation does not authorize execution or mutate the workspace."
        ),
    )
    server.tool()(prepare_task)
    return server


def main() -> int:
    try:
        server = build_mcp_server()
    except RuntimeError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    # stdio is the MCP SDK default and is the intended local agent/IDE transport.
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
