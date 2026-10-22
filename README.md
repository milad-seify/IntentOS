# IntentOS

**Engineering intent into reliable AI execution.**

IntentOS is an open-source intent engineering and workflow layer between humans and AI systems. It turns rough requests into context-aware, model-aware, engineering-aware instructions and execution plans that are easier to verify, cheaper to run, and safer to delegate.

It is designed for AI agents and assistants such as Codex, Claude Code, ChatGPT, Claude, Gemini, Cursor, and future tools without coupling the core to one vendor.

## Why

Most prompt tools stop after rewriting text. IntentOS goes further:

**Intent → Context → Risk → Engineering Policy → AI/Model Route → Optimized Prompt → Workflow → Verification → Learning**

For software and DevOps work, a good request is not only well-worded. It should also respect scope, architecture, maintainability, security, testing, deployment constraints, rollback, and cost.

## Core capabilities

- Prompt engineering and prompt repair
- Task and risk classification
- Contextual software-engineering and DevOps policies
- Project-aware context selection
- Agent workspace file planning and maintenance
- Capability/cost/effort-aware AI/model routing
- Workflow and approval-boundary generation
- Definition-of-Done and verification generation
- Token/cost/context hygiene
- Evaluation and reusable learning loops
- Pluggable profiles for new AI tools and engineering domains

## Engineering philosophy

IntentOS prefers minimal sufficient context, small coherent changes, KISS and YAGNI before abstraction, contextual SOLID/DRY/Clean Code, explicit scope, testable and reversible changes, secure defaults, reproducible DevOps workflows, evidence-backed completion, and the lowest-cost model that meets the quality bar.

Principles are applied contextually. IntentOS must not force Clean Architecture, microservices, extra abstractions, or heavyweight process onto small tasks.

## What IntentOS is not

IntentOS is not an IDE, an LLM or coding-agent replacement, a CI/CD platform, a project-management suite, a framework that forces one software architecture, or a giant prompt-template collection.

## Current API

```python
from intentos import (
    CapabilityClass,
    CostClass,
    IntentRequest,
    ModelMetadata,
    optimize_prompt,
)

models = (
    ModelMetadata(
        name="my-fast-model",
        provider="example",
        surfaces=("chatgpt",),
        capability=CapabilityClass.FAST,
        cost=CostClass.LOW,
    ),
)

result = optimize_prompt(
    IntentRequest("Write a short project announcement", target_tool="chatgpt"),
    models=models,
)

print(result.routing)
print(result.prompt)
```

Model metadata is supplied by callers/adapters. IntentOS intentionally does not hardcode volatile model names in the core. Without compatible metadata it returns a capability-level fallback such as fast, balanced, or strong plus an effort recommendation.

Project-aware prompting and workspace planning are also available through `optimize_project_prompt()` and `plan_agent_workspace()`.

## Development

Python 3.11+ is required. The runtime core currently has no third-party dependencies.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Status

**Phase 4 — AI / Model Routing**

Implemented: prompt engineering, task/risk classification, contextual engineering and DevOps policies, bounded project context, proposal-first workspace maintenance, target-tool profiles, and replaceable capability/cost/effort model routing with deterministic fallbacks.

Evaluation and integrations remain later phases by design. See [`docs/STATUS.md`](docs/STATUS.md) for the concise current handoff and [`docs/`](docs/) for the product foundation.

## License

MIT
