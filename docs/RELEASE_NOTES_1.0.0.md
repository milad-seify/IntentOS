# IntentOS 1.0.0

IntentOS prepares bounded engineering contracts between human intent and AI execution.

## Core

- Intent normalization and clarification, with deterministic task/risk classification.
- Engineering and DevOps policy preparation, explicit approval boundaries, and bounded project-context selection.
- Model capability/effort routing and verification contracts over a vendor-neutral core.

## Outputs and reusable artifacts

- Optimized execution prompts and portable Agent Skills.
- Privacy-minimal versioned run records and task-local evaluation primitives.

## Access surfaces

- Python API and `intentos` CLI, also available through `python -m intentos`.
- Optional MCP stdio adapter (`intentos-mcp`) with exactly one `prepare_task` tool.
- Minimum VS Code Prepare → Review → Copy integration.

The distribution is `intentos-engineering`. Machine JSON and run-record schemas remain at version `1`, independently of package version `1.0.0`.

## Reliability and validation

Phase 7C completed with 10 real tasks: 3 paired outcomes favored preparation, 2 favored raw requests, and 5 were inconclusive. This did not establish that preparation consistently beats raw prompts or justify a new capability.

The stable public contract is defined and the Windows Unicode CLI regression is fixed. Established checks cover Python 3.11–3.13 CI, wheel/sdist hygiene and clean installations, MCP parity, VS Code syntax, and real Extension Host workspace/no-workspace integration behavior.

## Explicit boundaries

Version 1.0.0 does not include autonomous agent execution, Send-to-Agent, automatic filesystem context discovery, extra MCP tools, a hosted backend, a telemetry service, a standalone simple UI, or Phase 7D work. Classification advises preparation; it does not authorize execution.
