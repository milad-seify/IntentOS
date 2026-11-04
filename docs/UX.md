# Usage and UX

IntentOS should be powerful enough for expert engineering workflows and simple enough for a user who does not know prompt engineering, model routing, MCP, or agent internals.

The product principle is:

> Powerful for experts, simple enough for everyone.

Ease of use is a product requirement, not a wrapper to add after the core is complete.

## Delegation control surface

The [Reliable AI Delegation vision](VISION.md) serves professionals across domains; software engineering and DevOps remain the currently implemented domain-policy support. Users should understand and control the delegation: goal, supplied context and provenance, assumptions, risk, permitted actions and human approval boundaries, target agent/capability, verification, and eventual outcome evidence.

The desired future UX organizes those decisions and evidence rather than adding another generic chat interface. This is a product direction, not a committed sidebar, screen layout, or new access surface. Phase 8 adoption evidence should inform the exact UX. Prepare → Review → Copy remains the accepted workflow; outcome evidence is supplied externally rather than automatically captured by the current editor UI.

Trust comes from understanding boundaries and checking outcomes. Ready means the request is ready for handoff, not that the downstream work is correct. Approval guidance does not grant an agent permission to act; the user and executing system retain that authority.

## One core, multiple surfaces

All user-facing surfaces should call the same IntentOS core rather than reimplementing routing, policy, context, or verification logic.

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

The surfaces are adapters. The core remains vendor-, IDE-, and transport-neutral.

## User levels

### Everyday user

The user should be able to state the desired outcome in ordinary language and receive useful guidance without understanding prompt frameworks, model families, context windows, engineering policies, or MCP.

Current accepted experience:

```text
Describe what you want
        ↓
IntentOS analyzes intent, risk, context, and target
        ↓
Review the delegation contract
        ↓
Copy Prepared Task
        ↓
Hand off to an external AI tool for execution
```

Advanced details remain available but are not required for common use.

### Developer

A developer should be able to use IntentOS directly in the editor, especially VS Code, without repeatedly leaving the development workflow.

Useful editor actions may include:

- refine or prepare the selected request
- prepare a task for Codex, Claude Code, or another connected agent
- preview task type, risk, selected context, and verification expectations
- inspect proposed `AGENTS.md` or related context updates
- copy the prepared contract for use in an external AI tool
- expose warnings before destructive, production, security, or migration work

The VS Code extension should remain a thin UX layer over the core.

### Power user / automation

Advanced users, CI systems, scripts, and other developer tools should use the CLI or Python API for deterministic and machine-readable access.

The CLI remains a first-class interface because it is portable, scriptable, testable, and independent of a specific IDE.

The development `intentos compass` CLI exposes the existing Project Compass reviewer through explicitly supplied local documents. It shows source file and line for each claim, including decision headings in a supplied `docs/DECISIONS.md`, distinguishes missing, stale, and unresolved state, and requires the caller to designate authoritative scope sources. Its scope result is advisory and never grants execution permission. The published Core 1.0.1 CLI does not include this command.

The development `intentos state` CLI previews exact status or decision changes before any write. A user must review the proposed diff and supply its content-bound approval digest in a second invocation. The writer checks the source revision and any related source fingerprints, serializes IntentOS writers with a local lock, and refuses unexpected targets or stale approvals. The digest is an explicit approval assertion, not independent proof of human review. An interrupted write may leave a lock that requires inspection before removal. This development command is also absent from Core 1.0.1.

The same development flow supports one bounded `docs/SCOPE.md` amendment at a time. It shows whether the task was unknown or explicitly out of scope, requires an owner approval reference, and records the change in that document's amendment history. Conflict, stale source, duplicate amendment ID, and unsupported Markdown layouts stop for review. A scope amendment is not a general permission grant; task risk and execution approval remain separate.

The development `intentos gates` command reads a caller-supplied JSON evidence file and produces a requirement-to-milestone/check report. It keeps proposed, claimed done, verified and owner-approved states distinct. Missing or failed checks block readiness; unreviewed evidence remains unresolved. Even when every supplied check passes, the result is only ready for owner review and never certifies a launch. The evidence references and approval flags are caller assertions, not independent verification by IntentOS.

The development `intentos route` review shows why a caller-supplied model is eligible, excluded, or selected for a task's required capability and effort. It uses relative cost classes, includes a catalog fingerprint for reproducibility, and falls back when compatible verified metadata is missing or names conflict. `available` and `verified` are caller assertions; the review does not query providers or claim live prices.

The development `intentos checkpoint` command saves a bounded, versioned approved plan, cited project-state summary, completed-step evidence and next action for an interrupted task. The CLI pins the actual Git HEAD and fingerprints only explicitly supplied local context files. A fresh process can review the checkpoint against current revision/context and caller-checked operation/approval records. Changed state, duplicate operation IDs or missing approvals block review. Even a passing check is only ready for owner review; it does not restart an agent or authorize execution. The command is not in Core 1.0.1.

### AI agent

Agents should be able to consume IntentOS capabilities through an interoperability layer such as MCP rather than requiring custom integration with every agent product.

The implemented MCP adapter exposes exactly one `prepare_task` tool over local stdio. Additional operations remain candidates subject to demonstrated demand; the product direction does not approve broader MCP scope.

MCP is an integration surface; IntentOS should not become a general MCP runtime.

## Progressive disclosure

The default UI should expose only the information needed for the current decision.

For example, an everyday user may initially see:

```text
Request: Refactor this function without changing behavior
Risk: Medium
Target: Codex
[Review] [Copy Prepared Task]
```

An advanced view may reveal:

- normalized intent
- task and risk classification
- context sources
- engineering rules
- approval boundaries
- model/capability recommendation
- token/cost considerations
- verification and Definition of Done
- run/evaluation metadata

Complexity should be available, not mandatory.

## UX principles

### Outcome-first language

Prefer user goals such as `Prepare this task`, `Review risk`, or `Copy Prepared Task` over internal terms such as compiler passes, policies, routing metadata, or prompt frameworks.

### Safe defaults

Common low-risk requests should work with minimal configuration. High-risk or irreversible actions should surface the relevant warning and approval boundary without turning every request into a security ceremony.

### Preview before mutation

Workspace edits, generated Skills, configuration changes, and other persistent actions should be reviewable before they are applied.

### Explain recommendations briefly

When IntentOS recommends a capability, workflow, context file, or stronger verification level, the user should be able to see a short reason.

### Consistent behavior across surfaces

The same request should produce semantically equivalent task/risk/policy decisions whether it enters through CLI, VS Code, MCP, Python API, or a future simple UI.

### No prompt-engineering prerequisite

Users should not need to learn prompt frameworks or memorize special syntax to obtain a good result.

### Escape hatches for experts

Advanced users should be able to inspect, override, export, or automate decisions where safe, without forcing that complexity onto everyone else.

### Local-first where practical

Project context and generated contracts should remain inspectable and controllable by the user. Hosted services may be added later only where they provide clear value.

## Surface responsibilities

| Surface | Primary audience | Responsibility |
| --- | --- | --- |
| CLI | developers, automation | deterministic portable access |
| Python API | integrations, tooling | programmatic core access |
| MCP adapter | AI agents | standard agent/tool interoperability |
| VS Code extension | developers | editor-native workflow and visualization |
| Simple UI | everyday users | low-friction outcome-first experience |
| Agent Skills | reusable agent context | portable on-demand guidance |

No surface should fork or duplicate core decision logic.

## Delivery order

The preferred evolution is:

1. Core + CLI + Python API — current foundation
2. MCP adapter — standard agent connection
3. VS Code extension — editor-native ease of use
4. simple end-user UI — only after core workflows and terminology are validated
5. additional agent/IDE adapters — based on demonstrated adoption

This order keeps the architecture reusable while progressively lowering the barrier to entry.

## Non-goals

Ease of use does not mean IntentOS should become:

- an IDE replacement
- a full autonomous-agent runtime
- a general desktop automation platform
- a mandatory cloud service
- a separate implementation for every AI vendor

The goal is one reliable core with multiple appropriate ways to reach it.
