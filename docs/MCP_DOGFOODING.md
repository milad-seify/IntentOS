# MCP Dogfooding

For a public installation, install the MCP extra with `python -m pip install "intentos-engineering[mcp]"`. For repository development, contributors can use `python -m pip install -e ".[mcp]"`.

## Goal

Validate the Phase 7A `prepare_task` adapter through the same local stdio process boundary used by desktop/IDE MCP hosts, without adding more tools or host-specific runtime code.

## Method

CI installs the optional MCP extra, launches the installed `intentos-mcp` console entry point as a subprocess, discovers tools through an MCP client, and calls `prepare_task` over stdio.

For each case, the complete structured MCP response is compared exactly with:

1. the shared Python preparation API, and
2. the CLI JSON result.

This tests transport/process parity rather than only importing the server in-process.

## Cases

The parity pass covers:

- documentation about a security topic that should remain lightweight
- high-risk production authentication/migration work
- project-context selection with authoritative and irrelevant context
- missing-target clarification

The MCP surface is also required to expose exactly one tool: `prepare_task`.

## Result

All four cases produced exact structured-result parity across MCP stdio, CLI, and Python API in CI.

No additional MCP tool or core abstraction was justified by this pass.

## Boundary

This evidence validates a real MCP stdio subprocess and the installed `intentos-mcp` entry point. It does **not** claim an authenticated Codex, VS Code, or Claude Code UI session was executed inside CI.

A local host only needs to launch the installed `intentos-mcp` command over stdio. Host-specific UI/configuration belongs outside the IntentOS core.

## Decision

Phase 7A parity is sufficient to begin the minimum Phase 7B editor UX. Additional MCP tools remain deferred until repeated real usage demonstrates a concrete need.
