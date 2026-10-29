# Dogfooding

IntentOS should be tested against real delegation patterns before a stable v1 contract is declared.

## Current scenarios

The stabilization suite covers representative workflows:

- Codex refactor with behavior-preservation constraints
- DevOps change against a production environment with rollback expectations
- architecture review with explicit trade-offs
- documentation-only architecture updates
- general writing that must not receive software-engineering noise
- target detection for Codex and Claude Code from Persian-language requests

## Findings from the first pass

### 1. English-only heuristics were too narrow

The first classifier relied on English task/risk terms. Real usage can mix natural-language instructions with English technical vocabulary, so Persian starter terms and target aliases were added.

This is intentionally **not** presented as full multilingual NLP support. The core remains deterministic and dependency-free; future language packs or adapters should be evidence-driven and independently testable.

### 2. Documentation-only work was over-engineered

A request such as “documentation only: update the architecture docs” could be classified as architecture work and receive implementation-oriented SOLID, dependency, and approval guidance.

Documentation-only signals now lower risk and produce a bounded documentation policy instead of implementation noise.

## Dogfooding rule

A real failure should become a regression fixture before it becomes a new general rule. Avoid growing global prompts or keyword lists from one-off preferences without evidence.

## Phase 7C evidence status

The Phase 7C target is complete: 10/10 distinct real tasks were collected and reviewed. No additional sample is required by that evidence gate. See PHASE_7C_EVIDENCE.md and Issue #21 for the aggregate outcome and detailed task evidence. The stable-v1 readiness gate passed, and IntentOS 1.0.0 has since been released. See RELEASING.md for future release procedures.
