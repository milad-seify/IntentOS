# Architecture

Phase 0 defines a conceptual architecture only. Implementation technology is intentionally deferred until the interfaces and first use cases are validated.

## Pipeline

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
Prompt + Workflow Compiler
   ↓
Verification Contract
   ↓
Output / Agent Handoff
   ↓
Evaluation Feedback
```

## Core components

### Intent Normalizer

Extracts the goal, inputs, expected output, constraints, ambiguity, audience, and success criteria from a rough request.

### Task + Risk Classifier

Classifies work such as writing, research, coding, bugfix, refactor, architecture, security, infrastructure, or operations and assigns a risk level sufficient to control process depth.

### Context Selector

Chooses the smallest relevant subset of project state, repository guidance, decisions, and user-provided context. It should prefer authoritative sources and avoid stale duplication.

### Policy Engine

Applies domain profiles such as software engineering and DevOps. Policies are contextual and composable; they must not mechanically inject every best practice into every task.

### AI / Model Router

Adapts behavior to the target tool/model family and may recommend an appropriate capability/cost class. Provider-specific facts belong in replaceable profiles, not the core.

### Prompt + Workflow Compiler

Produces the execution contract: optimized instructions, scope, constraints, allowed actions, approval boundaries, workflow, and expected reporting.

### Verification Contract

Defines what evidence proves completion: tests, builds, CI, security checks, diff review, operational checks, or output-format validation.

### Workspace Context Manager

Creates or proposes bounded updates to agent-facing context files. It should preserve source-of-truth ownership and detect stale or bloated context.

### Evaluation Layer

Captures comparable outcome signals so prompts, profiles, and routing decisions can improve based on evidence.

## Extensibility

Profiles/adapters should be independently versionable and replaceable:

```text
core/
profiles/
  ai/
  engineering/
  devops/
workflows/
evaluators/
integrations/
```

This is a direction, not a committed filesystem or implementation language.

## Architectural constraints

- Core logic must not depend on one AI vendor.
- Project files must remain human-readable and reviewable.
- Generated context should be bounded and traceable.
- High-risk recommendations must expose assumptions and approval boundaries.
- Routing must have deterministic fallbacks when tool/model metadata is unavailable.
- The first implementation should be a modular monolith or similarly simple structure unless evidence requires more complexity.
