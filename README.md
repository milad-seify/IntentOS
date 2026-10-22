# IntentOS

**Engineering intent into reliable AI execution.**

IntentOS is an open-source intent engineering and workflow layer between humans and AI systems. It turns rough requests into context-aware, model-aware, engineering-aware instructions and execution plans that are easier to verify, cheaper to run, and safer to delegate.

It is designed for AI agents and assistants such as Codex, Claude Code, ChatGPT, Gemini, Cursor, and future tools without coupling the core to one vendor.

## Why

Most prompt tools stop after rewriting text. IntentOS goes further:

**Intent → Context → Risk → Engineering Policy → AI/Model Route → Optimized Prompt → Workflow → Verification → Learning**

For software and DevOps work, a good request is not only well-worded. It should also respect scope, architecture, maintainability, security, testing, deployment constraints, rollback, and cost.

## Core capabilities

- Prompt engineering and prompt repair
- Task and risk classification
- Contextual software-engineering and DevOps policies
- AI/tool and model-aware routing
- Project-aware context selection
- Agent workspace file creation and maintenance
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

## Initial product boundary

### Inputs

A user request plus optional project context, target AI/tool, repository state, engineering preferences, constraints, and desired output.

### Outputs

Depending on the task, IntentOS may produce an optimized prompt, task/risk metadata, engineering and DevOps guardrails, recommended AI/model/effort, execution workflow and approval boundaries, relevant context selection, agent context files or updates, verification steps and Definition of Done, and evaluation metadata.

## Current API

The current implementation stays small and dependency-free. It normalizes rough intent, detects critical ambiguity, classifies task/risk, applies contextual engineering policy, selects a target-tool profile, and compiles a deterministic execution prompt.

```python
from intentos import IntentRequest, optimize_prompt

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
    print(result.prompt)
```

Initial target profiles are intentionally narrow: generic, Codex, Claude Code, and ChatGPT. Unsupported tools fall back to the generic profile until a dedicated profile is justified.

## Development

Python 3.11+ is required. The runtime core currently has no third-party dependencies.

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Status

**Phase 2 — Engineering + Risk Profiles**

Implemented: intent schema, ambiguity handling, prompt normalization, initial target profiles, deterministic task/risk classification, contextual software-engineering and DevOps policy generation, approval boundaries, Definition-of-Done generation, and focused tests.

Repository context management, model routing, evaluation, and integrations remain later phases by design.

See [`docs/`](docs/) for the product foundation and roadmap.

## License

MIT
