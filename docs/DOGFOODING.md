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

## Next real-world coverage

Before v1, collect examples from:

- multi-file Codex implementation work
- security-sensitive auth changes
- infrastructure changes with explicit approval boundaries
- repository context selection on medium/large repos
- model-routing decisions using externally supplied current metadata
- repeated prompt failures suitable for the learning-proposal layer
