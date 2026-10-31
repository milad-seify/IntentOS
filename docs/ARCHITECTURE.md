# Architecture

IntentOS uses a small vendor-neutral core with replaceable profiles and integration surfaces. Product access may expand, but core decision logic should remain shared.

The product role is the control and trust layer described in [VISION.md](VISION.md). The existing pipeline supports intent/context governance, risk and approval boundaries, portable handoff, verification, and outcome evidence; these responsibilities do not require a new architecture.

## Core pipeline

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
Prompt / Skill + Workflow Compiler
   ↓
Verification Contract
   ↓
Output / Agent Handoff
   ↓
Evaluation + Run Record
```

## Delegation and execution boundary

IntentOS prepares a reviewable delegation contract and receives externally supplied outcome evidence. The AI tool or agent executes the work and owns its filesystem/browser access, indexing, memory, tools, planning, and execution runtime.

Approval guidance states boundaries; it is not a permission-enforcement mechanism. Humans and the execution system enforce consequential approvals. A prepared verification contract specifies what must be checked; it does not certify that checks ran or guarantee a correct result. The current CLI/MCP/VS Code preparation surfaces do not execute or send tasks to agents.

## Usage architecture

IntentOS should expose the same core through multiple user-appropriate surfaces:

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

The diagram describes responsibility, not process topology. CLI, VS Code, MCP, and UI layers are adapters around the core. They must not fork task classification, context selection, engineering policy, routing, or verification behavior.

Agent Skills are another portable output/interface: the core may compile reusable `SKILL.md` guidance that agent surfaces can load on demand.

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

### Prompt / Skill + Workflow Compiler

Produces execution artifacts such as optimized instructions, portable Skills, scope, constraints, allowed actions, approval boundaries, workflow, and expected reporting.

### Verification Contract

Defines what evidence proves completion: tests, builds, CI, security checks, diff review, operational checks, or output-format validation.

### Workspace Context Manager

Creates or proposes bounded updates to agent-facing context files. It should preserve source-of-truth ownership and detect stale or bloated context.

### Evaluation Layer

Captures comparable outcome signals and versioned provenance so prompts, profiles, routing decisions, and workflows can improve based on evidence.

## Integration components

### CLI / Python API

The baseline portable interfaces. These provide deterministic access for users, scripts, CI systems, and other integrations.

### MCP adapter

A bounded interoperability adapter for compatible AI agents. It may expose IntentOS operations as tools but should not own generic agent orchestration, transport policy, or MCP runtime responsibilities beyond the adapter.

### VS Code extension

An editor-native thin client over the same core. It may visualize task type, risk, selected context, approval boundaries, model/capability recommendations, verification, and workspace proposals, and may hand prepared tasks to connected agents.

### Simple UI

A low-friction surface for users who should not need CLI, prompt-engineering, or MCP knowledge. It should use outcome-first language and progressive disclosure of advanced details.

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
  cli/
  mcp/
  vscode/
  ui/
```

This is a conceptual responsibility split, not a committed filesystem layout.

## Architectural constraints

- Core logic must not depend on one AI vendor, IDE, transport, or UI surface.
- All access surfaces should produce semantically consistent core decisions.
- UI/IDE/MCP adapters must not duplicate core policy or routing logic.
- Project files must remain human-readable and reviewable.
- Generated context should be bounded and traceable.
- High-risk recommendations must expose assumptions and approval boundaries.
- Routing must have deterministic fallbacks when tool/model metadata is unavailable.
- Ease of use should be achieved through adapters and progressive disclosure, not by weakening safety or duplicating logic.
- The implementation should remain a modular monolith or similarly simple structure unless evidence requires more complexity.
