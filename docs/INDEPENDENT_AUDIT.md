# Independent Audit Package

Use this after the stabilization branch is merged and before declaring the public API stable.

## Reviewer goal

Review IntentOS as an independent senior software engineer, AI-agent workflow reviewer, and product-integration reviewer. Do not assume the existing architecture is correct. Look for product gaps, unsafe assumptions, over-engineering, under-engineering, brittle heuristics, API design problems, misleading documentation, missing tests, and adoption/UX boundaries that would make the product difficult to use in practice.

## Read first

1. `README.md`
2. `AGENTS.md`
3. `docs/SCOPE.md`
4. `docs/ARCHITECTURE.md`
5. `docs/UX.md`
6. `docs/PRINCIPLES.md`
7. `docs/DECISIONS.md`
8. `docs/STATUS.md`
9. `docs/DOGFOODING.md`
10. `docs/HUGGINGFACE_RESEARCH.md`
11. implementation under `src/intentos/`
12. tests under `tests/`

## Audit dimensions

Evaluate:

- product scope and differentiation from prompt optimizers
- architecture boundaries and vendor neutrality
- public API clarity and future compatibility
- task/risk classification quality and failure modes
- engineering/DevOps policy proportionality
- context selection and agent-workspace safety
- model-routing assumptions and stale-metadata behavior
- evaluation/learning design and risk of self-reinforcing bad rules
- CLI ergonomics and automation suitability
- proposed MCP boundary and whether it can remain a thin interoperability adapter
- proposed VS Code boundary and whether editor UX can reuse core behavior without duplication
- ease of use for non-expert users and whether progressive disclosure is realistic
- semantic consistency across CLI, API, MCP, IDE, Agent Skills, and future simple UI surfaces
- whether the Phase 7 delivery order is the smallest practical route to adoption
- security and unsafe write/destructive-action boundaries
- maintainability, KISS/YAGNI, SOLID/DRY where useful
- test quality, missing edge cases, and regression coverage
- open-source contributor experience, onboarding, documentation accuracy, and likely adoption friction

## Required output

Return:

1. **Verdict** — ready for v1, needs stabilization, or requires redesign.
2. **Critical findings** — correctness/security/API issues that should block v1.
3. **High-value improvements** — prioritized by impact versus complexity.
4. **Over-engineering / unnecessary complexity** — things to simplify or delete.
5. **Missing tests / dogfood cases** — concrete fixtures to add.
6. **Public API risks** — contracts that should not be frozen yet.
7. **Usage/UX risks** — friction, duplication, integration, or accessibility issues across planned surfaces.
8. **OSS readiness** — README, contribution, naming, packaging, release and onboarding gaps.
9. **Recommended next milestone** — smallest coherent milestone after the audit.

For every finding, cite the exact file/function/contract that supports it. Separate confirmed defects from preferences. Do not propose large rewrites when a smaller fix is sufficient.

## Execution instruction for Work / Codex

Inspect the repository and run the relevant tests. Do not modify files during the first audit pass. Produce evidence-backed findings first. If fixes are requested afterward, implement them in priority order on a separate branch with focused tests and full CI.
