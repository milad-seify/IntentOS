# Principles

IntentOS uses principles as decision aids, not dogma.

## 1. Intent before template

Understand the actual outcome before choosing a prompt structure or workflow.

## 2. Minimal sufficient context

Load only context that can materially change the result. Avoid dumping entire repositories or long histories into every request.

## 3. Smallest coherent change

Prefer the smallest change that fully solves the task. Before adding new code or dependencies, use the first sufficient option: skip unnecessary work, reuse existing project code, use standard-library or platform capabilities, reuse an already-installed dependency, then add only the minimum new code. Avoid opportunistic refactors, speculative abstractions, code golf, and unrelated cleanup.

## 4. Contextual engineering quality

Use Clean Code, SOLID, DRY, separation of concerns, and architectural patterns when they improve maintainability or reduce risk. Prefer KISS and YAGNI when extra structure does not pay for itself.

## 5. Preserve system boundaries

Respect existing architecture, public contracts, ownership boundaries, data models, and deployment assumptions unless changing them is part of the requested task.

## 6. Risk-proportionate process

A copy change, a local refactor, a database migration, and a security change should not receive the same workflow. Review depth, model capability, approvals, and verification should scale with risk.

## 7. Verifiable completion

Completion claims should be backed by evidence: tests, lint/type checks, build output, CI state, diff review, or domain-specific checks.

## 8. Reversible by default

Prefer changes that are easy to review, revert, migrate safely, and recover from.

## 9. Secure and operationally sane defaults

Apply least privilege, safe secret handling, explicit destructive-action boundaries, reproducibility, observability, and rollback-aware DevOps practices when relevant.

## 10. Cost is an engineering constraint

Use the lowest-cost model, context size, reasoning effort, and number of agent calls that can reliably meet the quality target.

## 11. Vendor-neutral core

Model- and tool-specific behavior belongs in profiles/adapters. Core concepts should survive provider churn.

## 12. Humans own irreversible decisions

External writes, destructive actions, purchases, production-impacting changes, material scope expansion, and ambiguous high-risk decisions should have explicit approval boundaries.

## 13. Learn from outcomes, not preferences alone

Prompt and workflow improvements should eventually be evaluated against measurable outcomes such as success rate, retries, tokens, latency, defects, and reviewer corrections.

## 14. Powerful for experts, simple enough for everyone

Ease of use is a product requirement. Everyday users should be able to describe an outcome in ordinary language without learning prompt engineering, model routing, MCP, or internal architecture. Advanced controls should be available through progressive disclosure rather than required up front.

## 15. One core, many access surfaces

CLI, Python API, MCP, VS Code, Agent Skills, and future simple user interfaces should adapt the same core decisions rather than reimplement task classification, context selection, policy, routing, or verification independently.
