# IntentOS

**Engineering intent into reliable AI execution.**

[![CI](https://github.com/milad-seify/IntentOS/actions/workflows/ci.yml/badge.svg)](https://github.com/milad-seify/IntentOS/actions/workflows/ci.yml)

IntentOS is an open-source engineering layer between **human intent** and **AI execution**. It turns rough requests into bounded, context-aware, engineering-aware execution contracts for AI assistants and agents such as Codex, Claude Code, ChatGPT, Claude, Gemini, Cursor, and future tools.

It is not just another prompt rewriter.

```text
Intent
  → Normalize / clarify
  → Task + risk
  → Relevant project context
  → Engineering / DevOps policy
  → AI / model route
  → Optimized execution prompt / portable Skill
  → Verification contract
  → Evaluation + versioned run record
  → Learning
```

## Why IntentOS?

A well-worded prompt is not enough for serious engineering work.

A coding or DevOps agent also needs the right scope, project context, risk controls, approval boundaries, engineering expectations, model capability, verification criteria, and a way to learn from repeated failures without endlessly growing the prompt.

IntentOS makes those concerns explicit and composable.

### What makes it different

- **Prompt engineering, not prompt inflation** — preserve and sharpen intent instead of adding boilerplate.
- **Context-aware engineering** — KISS/YAGNI by default; SOLID, DRY, Clean Code, security, and DevOps guidance only when the task actually benefits from them.
- **Risk-aware delegation** — production, security, schema, destructive, and persistent changes get stronger approval boundaries.
- **Minimal project context** — rank, deduplicate, and budget repository context instead of dumping the whole repo into the agent.
- **Portable agent context** — compile reusable `SKILL.md` artifacts instead of repeating the same instructions in every conversation.
- **Agent workspace hygiene** — detect missing, stale, duplicate, or bloated agent-facing files and propose safe updates.
- **Future-proof model routing** — route by capability, effort, availability, surface compatibility, and relative cost without hardcoding today's model names into the core.
- **Evidence over intuition** — regression assertions, A/B ranking, token/latency/retry metrics, versioned privacy-minimal run records, and repeated-failure learning proposals.
- **Ease of use by design** — common workflows should not require prompt-engineering, model-routing, MCP, or internal architecture knowledge.
- **Vendor-neutral core** — provider-specific behavior lives behind profiles/adapters.

## How people should use IntentOS

IntentOS is designed as **one shared core with multiple access surfaces** so different users can work in the environment that fits them.

```text
                         IntentOS Core
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
       Simple UI          VS Code UX          CLI / API
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                             MCP
                              │
                  Compatible AI agents/tools
```

Current surfaces:

- **CLI** — portable use from the terminal and scripts.
- **Python API** — programmatic access for integrations and automation.
- **MCP adapter** — optional local stdio connection exposing one bounded `prepare_task` tool.
- **VS Code extension (minimum slice)** — one `IntentOS: Prepare Task` command with temporary review and Copy Prepared Task.
- **Agent Skills** — portable, reusable `SKILL.md` guidance.

Deferred candidate surface:

- **Simple UI** — an outcome-first experience for users who should not need CLI or prompt-engineering knowledge. Phase 7C evidence did not justify starting it; any future work remains evidence-gated.

Broader VS Code handoff/execution features remain gated by editor dogfooding rather than being assumed up front.

Advanced controls should use **progressive disclosure**: everyday users see simple outcome-first actions, while experts can inspect and control context, risk, policy, routing, cost, approvals, and verification.

See [`docs/UX.md`](docs/UX.md) for the product usage and UX contract.

## Quick start

Requires Python 3.11+.

### Stable release installation

IntentOS 1.0.0 is the current stable release. Install it without cloning the repository:

```bash
python -m pip install intentos-engineering
intentos --help
intentos optimize "Refactor the parser" --target codex
```

The Python distribution is named `intentos-engineering`; its import package and CLI remain `intentos`. A clean public installation of version 1.0.0 was verified.

### Development checkout

```bash
git clone https://github.com/milad-seify/IntentOS.git
cd IntentOS
python -m pip install -e .
```

Optimize a request for Codex:

```bash
intentos optimize "Refactor the auth module without changing behavior" \
  --target codex \
  --constraint "No new dependencies" \
  --success "Relevant tests pass"
```

If the target is named in the request, the CLI can detect it:

```bash
intentos optimize "Codex: refactor the parser without changing behavior"
```

Use project context:

```bash
intentos optimize "Refactor the parser" \
  --target codex \
  --context-file AGENTS.md \
  --context-file docs/ARCHITECTURE.md
```

Compile the same engineering contract into a portable Agent Skill without writing files:

```bash
intentos skill "Refactor the parser" \
  --target codex \
  --name parser-refactor
```

Machine-readable output:

```bash
intentos optimize "Review this architecture" --target claude --json
```

JSON mode returns the versioned machine contract documented in [`docs/PUBLIC_CONTRACT.md`](docs/PUBLIC_CONTRACT.md). Schema versioning is independent from the Python package version. The v1 contract is frozen; package version `1.0.0` is the current stable release.

Plan agent workspace maintenance without writing files:

```bash
intentos workspace \
  --phase "Phase 7B — minimum VS Code UX" \
  --document AGENTS.md \
  --document docs/STATUS.md
```

`workspace` and `skill` are **proposal-first**: they emit reviewable artifacts; they do not silently mutate or install anything in your repository.

You can also run the CLI as a module:

```bash
python -m intentos optimize "Fix the failing parser test" --target codex
```

## MCP adapter

MCP support is optional so the standard-library core remains lightweight.

Install the MCP extra without cloning:

```bash
python -m pip install "intentos-engineering[mcp]"
```

For development, contributors can install the extra from a repository checkout with `python -m pip install -e ".[mcp]"`.

A compatible local MCP host can launch:

```bash
intentos-mcp
```

The server uses stdio and exposes exactly one tool: `prepare_task`.

`prepare_task` accepts the user request, optional target tool, constraints, success criteria, output format/audience, and bounded caller-supplied project context. Project context entries contain only `path` labels and `content`; IntentOS does **not** read those paths from the filesystem. The first slice accepts at most 32 context documents and 6000 characters total.

The MCP result uses the same versioned machine contract as the CLI: ready/clarification status, prepared prompt, task/risk decision, engineering and approval boundaries, routing, context diagnostics, and verification criteria.

MCP preparation does not execute the task, authorize a risky action, mutate the repository, expose workspace/Skill/run-record operations, or turn IntentOS into a general MCP runtime.

## VS Code extension

Install the [IntentOS extension from the Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=milad-seyfi.intentos-vscode). First install the local CLI:

```bash
python -m pip install intentos-engineering
```

Then install the extension from the Marketplace and use this flow:

```text
Request
→ IntentOS preparation
→ Review
→ Copy Prepared Task
→ hand off to Codex / ChatGPT / Claude / Gemini / Cursor / another AI tool
```

The extension uses the editable package installation only for local development. IntentOS 1.0.0 is also available as the stable public package.

The first editor slice lives in `integrations/vscode` and intentionally has no npm runtime dependencies or build pipeline.

Current flow:

1. make sure the `intentos` CLI is available to the VS Code extension host
2. select request text in an editor, or leave nothing selected
3. run `IntentOS: Prepare Task` from the Command Palette
4. if needed, type the request into the small input box
5. review interpretation, risk/approval boundaries, context summary, verification, and the prepared prompt
6. use **Copy Prepared Task** when ready

Advanced routing/context details stay collapsed by default. The extension invokes `intentos optimize ... --json`; it does not duplicate IntentOS classification, policy, context, or routing logic in JavaScript.

`intentos.executable` defaults to `intentos` and can be changed when VS Code needs a specific virtual-environment executable path.

This first slice intentionally does not include a permanent sidebar, automatic project-file discovery, agent-specific Send/Execute wiring, telemetry, or a background service. See [`integrations/vscode/README.md`](integrations/vscode/README.md).

## Python API

```python
from intentos import (
    IntentRequest,
    RunMetrics,
    build_run_record,
    build_skill_artifact,
    optimize_prompt,
)

result = optimize_prompt(
    IntentRequest.from_values(
        "Refactor the auth module without changing behavior",
        target_tool="codex",
        constraints=["No new dependencies"],
        success_criteria=["Relevant tests pass"],
    )
)

if result.needs_clarification:
    print(result.questions)
else:
    print(result.policy.task_type, result.policy.risk_level)
    print(result.routing.required_capability, result.routing.effort)
    print(result.prompt)

    skill = build_skill_artifact(result.intent, result.policy)
    record = build_run_record(
        result,
        metrics=RunMetrics(success=True, quality_score=0.9),
    )
    print(skill.content)
    print(record.to_json())
```

For project-aware prompting, use `optimize_project_prompt()`. For model selection, pass replaceable `ModelMetadata` entries. IntentOS intentionally does not hardcode volatile model names in the core.

Run records intentionally avoid storing raw prompts by default. They use fingerprints and compact metadata so future telemetry/dataset adapters can be added without making raw private agent traces a core requirement.

The deterministic task/risk classifier is an **advisory preparation mechanism**, not a security authorization boundary.

## Engineering philosophy

IntentOS prefers:

- minimal sufficient context
- small coherent changes
- KISS and YAGNI before abstraction
- contextual SOLID / DRY / Clean Code
- explicit scope and approval boundaries
- secure defaults and least privilege
- reproducible and recoverable DevOps changes
- evidence-backed completion
- the lowest-overhead model that still meets the quality bar
- simple defaults with expert controls available when needed

It should **not** force Clean Architecture, microservices, extra abstractions, heavyweight process, or expert-only UX onto small tasks.

## Architecture

The conceptual pipeline is:

```text
User Intent
   ↓
Intent Normalizer
   ↓
Task + Risk Classifier
   ↓
Context Selector
   ↓
Policy Engine
   ↓
AI / Model Router
   ↓
Prompt / Skill Compiler
   ↓
Verification Contract
   ↓
Evaluation + Run Record
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/UX.md`](docs/UX.md), [`docs/DECISIONS.md`](docs/DECISIONS.md), [`docs/EVALUATION.md`](docs/EVALUATION.md), and [`docs/HUGGINGFACE_RESEARCH.md`](docs/HUGGINGFACE_RESEARCH.md).

## What IntentOS is not

IntentOS is not:

- an IDE
- an LLM or coding-agent replacement
- a general autonomous-agent framework
- a general MCP runtime
- a telemetry backend
- a CI/CD platform
- a project-management suite
- a framework that forces one software architecture
- a giant prompt-template collection

## Development

The core currently has no third-party runtime dependencies. MCP support is an optional extra rather than a core dependency. The minimum VS Code extension uses plain JavaScript and built-in VS Code/Node APIs.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

GitHub Actions runs the full core suite on Ubuntu with Python 3.11, 3.12, and 3.13, focused Windows/Python 3.13 regression coverage, CLI smoke checks, MCP protocol/stdio parity checks, and a dependency-free VS Code extension syntax check.

## Project status

The initial Phase 0–6 roadmap and independent-audit stabilization gate are complete. **Phase 7 is complete:** MCP parity was proven, VS Code is publicly distributed with a visible status-bar launcher, and the accepted workflow remains Prepare → Review → Copy. The evidence gate did not justify additional adapters or execution capabilities.

Current baseline: **113 Python unit tests + CLI smoke + MCP protocol/stdio parity checks + VS Code contract, syntax, and package checks**, with Linux and Windows CI coverage. CI also builds and inspects wheel/sdist artifacts, then installs and smoke-tests each from clean environments without publishing.

The v1 public compatibility contract is frozen in `docs/PUBLIC_CONTRACT.md`. IntentOS `1.0.0` is the current stable core release; VS Code extension `0.1.1` is published. Phase 7D was intentionally deferred and closed without implementation because no additional adapter demand met the evidence threshold. Phase 7 is formally complete. [Phase 8 — Adoption & Outcome Validation](docs/PHASE_8_VALIDATION.md) is in progress at the validation-protocol stage; no new runtime capability is approved. See the [release notes](docs/RELEASE_NOTES_1.0.0.md) and [release procedure](docs/RELEASING.md).

See [`docs/STATUS.md`](docs/STATUS.md) for the concise handoff, [`docs/DOGFOODING.md`](docs/DOGFOODING.md) for real-world findings, [`docs/MCP_DOGFOODING.md`](docs/MCP_DOGFOODING.md) for MCP parity evidence, [`docs/HUGGINGFACE_RESEARCH.md`](docs/HUGGINGFACE_RESEARCH.md) for the ecosystem research pass, [`docs/UX.md`](docs/UX.md) for usage/access principles, [`docs/INDEPENDENT_AUDIT.md`](docs/INDEPENDENT_AUDIT.md) for the review contract, and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the roadmap.

## Contributing

Contributions are welcome, especially:

- real-world failure/regression fixtures
- target-tool profiles where generic behavior is demonstrably insufficient
- provider/model metadata adapters
- context-selection improvements backed by tests
- evaluation and workflow improvements with measurable evidence
- portable Agent Skills and integration adapters that preserve the vendor-neutral core
- usability improvements that reduce friction without duplicating core behavior

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a PR.

## License

MIT
