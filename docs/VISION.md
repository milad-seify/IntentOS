# Vision

**Reliable AI Delegation**

**IntentOS makes AI delegation controlled, portable, and verifiable.**

Its long-term role is a vendor-neutral control and trust layer between human intent and AI execution. A user expresses a goal; IntentOS helps make the delegation explicit and reviewable; the selected AI tool or agent performs the work.

## North Star

A user should be able to express a goal in ordinary language and obtain the smallest sufficient, portable and reviewable contract for AI delegation **without needing to understand prompt engineering, model routing, MCP, or agent internals**.

The contract should preserve intent and make explicit what should be done, what context matters, which constraints apply, the risks, permitted autonomous actions, required human approval, the appropriate execution target/process, and the evidence needed to establish success.

IntentOS should be reachable from the environment appropriate to the user — terminal, code editor, compatible agent, or a simpler user interface — while all surfaces share the same core decisions.

## Durable responsibilities

These responsibilities guide the existing shared core; they are not a new module layout or a promise of additional runtime capabilities.

| Responsibility | Purpose |
| --- | --- |
| Intent Contract | Explicit interpretation, goal, scope, constraints, assumptions, and success criteria. |
| Context Governance | Relevant, bounded, traceable context with visible sources and limits; current context is explicitly supplied. |
| Risk & Approval Boundaries | Risk awareness, allowed actions, consequential human decisions, and process/capability guidance. |
| Verification Contract | Criteria and evidence required to establish completion. |
| Portable Agent Handoff | Reviewable prompts, Agent Skills, and machine contracts usable across execution tools. |
| Outcome Evidence / Learning | Externally observed results, privacy-minimal run records, and reviewable improvement proposals. |

Intent normalization, task/risk classification, context selection, contextual engineering policy, capability/effort routing, verification, and evaluation remain the underlying mechanics. Execution, filesystem/browser/computer access, project indexing, memory, MCP/tool use, planning, multi-agent execution, and model/provider capabilities belong to agents and execution platforms. IntentOS should use their capabilities without rebuilding a competing agent runtime.

## Trust through evidence

Trust must come from explicit interpretation, relevant and traceable context, visible assumptions, constraints, risk awareness, consequential human approval, verification criteria, and observed outcomes. Preparing a contract does not establish that an AI answer is correct or that the task was completed successfully.

The current classifier and approval guidance are advisory. People and execution systems enforce permissions and approval decisions; IntentOS does not grant execution authority or guarantee correctness.

## Users and domain boundary

The long-term audience includes developers, DevOps/platform engineers, architects, analysts, researchers, managers, designers, and domain specialists. Many will delegate professional work without understanding AI internals. The product should make the contract understandable and controllable for them.

Software engineering and DevOps remain the initial wedge, validation environment, and currently implemented domain-policy support. Broader professional use is a vision, not a claim of validated specialist policies or correctness in other domains. Domain expansion requires real-use evidence and separately scoped work.

## Adoption and future UX

The desired experience is a delegation control surface where users can understand goal, context, risk, approval boundaries, target/capability, verification, and eventual outcome. Exact UI design remains evidence-gated; the accepted current workflow is Prepare → Review → Copy.

[Phase 8 — Adoption & Outcome Validation](PHASE_8_VALIDATION.md) continues under its existing protocol and quantitative gate. Its evidence can test whether users understand and value this delegation role. This vision adds no UI, adapter, domain policy, or execution feature. Ease of use should come from good defaults, thin integrations, and progressive disclosure over one vendor-neutral core, with deterministic fallbacks when model metadata is unavailable.
