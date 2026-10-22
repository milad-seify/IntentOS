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
- AI/tool and model-aware routing
- Task and risk classification
- Software engineering and DevOps policy profiles
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

Depending on the task, IntentOS may produce an optimized prompt, recommended AI/model/effort, execution workflow and approval boundaries, engineering constraints, relevant context selection, agent context files or updates, verification steps and Definition of Done, and evaluation metadata.

## Status

**Phase 0 — Foundation**

The initial work defines vision, scope, principles, architecture, contributor-facing agent rules, and the roadmap before implementation begins.

See [`docs/`](docs/) for the design foundation.

## License

License selection is intentionally deferred until the project foundation is reviewed.
