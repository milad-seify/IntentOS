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

- **Prompt engineering, not prompt inflation** — normalize and sharpen intent instead of adding boilerplate.
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
- **Agent Skills** — portable, reusable `SKILL.md` guidance.

Planned after the independent audit validates the boundaries:

- **MCP adapter** — standard connection for compatible AI agents.
- **VS Code extension** — editor-native task preparation, risk/context preview, and agent handoff.
- **Simple UI** — outcome-first experience for users who should not need CLI or prompt-engineering knowledge.

Advanced controls should use **progressive disclosure**: everyday users see simple outcome-first actions, while experts can inspect and control context, risk, policy, routing, cost, approvals, and verification.

See [`docs/UX.md`](docs/UX.md) for the product usage and UX contract.

## Quick start

Requires Python 3.11+.

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

Plan agent workspace maintenance without writing files:

```bash
intentos workspace \
  --phase "Stabilization and dogfooding" \
  --document AGENTS.md \
  --document docs/STATUS.md
```

`workspace` and `skill` are **proposal-first**: they emit reviewable artifacts; they do not silently mutate or install anything in your repository.

You can also run the CLI as a module:

```bash
python -m intentos optimize "Fix the failing parser test" --target codex
```

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
- an MCP runtime
- a telemetry backend
- a CI/CD platform
- a project-management suite
- a framework that forces one software architecture
- a giant prompt-template collection

## Development

The core currently has no third-party runtime dependencies.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

GitHub Actions runs the suite on Python 3.11, 3.12, and 3.13 plus a CLI smoke test.

## Project status

The initial Phase 0–6 roadmap is implemented. The project is now in **stabilization, real-world dogfooding, usage-architecture validation, and independent-audit preparation** before locking a stable v1 contract.

Current baseline: **45 unit tests + CLI smoke**, verified by GitHub Actions on Python 3.11, 3.12, and 3.13.

See [`docs/STATUS.md`](docs/STATUS.md) for the concise handoff, [`docs/DOGFOODING.md`](docs/DOGFOODING.md) for real-world findings, [`docs/HUGGINGFACE_RESEARCH.md`](docs/HUGGINGFACE_RESEARCH.md) for the ecosystem research pass, [`docs/UX.md`](docs/UX.md) for usage/access principles, [`docs/INDEPENDENT_AUDIT.md`](docs/INDEPENDENT_AUDIT.md) for the external review package, and [`docs/ROADMAP.md`](docs/ROADMAP.md) for the roadmap.

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
