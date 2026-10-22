# Vision

IntentOS exists to make delegation to AI systems more reliable and easier to use.

Humans often express goals informally. AI tools, especially agents that can edit code, run commands, browse systems, or change infrastructure, work better when intent is translated into explicit context, scope, constraints, risk boundaries, and verifiable outcomes.

IntentOS is the layer that performs that translation.

## North Star

A user should be able to express a rough goal in natural language and receive the smallest sufficient execution contract for the selected AI system **without needing to understand prompt engineering, model routing, MCP, or agent internals**.

That contract should preserve the user's intent while adding only the engineering structure needed to execute safely and successfully.

IntentOS should be reachable from the environment appropriate to the user — terminal, code editor, compatible agent, or a simpler user interface — while all surfaces share the same core decisions.

## Product thesis

Better AI work comes from more than better wording.

Reliable delegation combines:

1. intent extraction
2. relevant context selection
3. task and risk classification
4. domain-aware engineering policy
5. AI/model-aware prompt construction
6. explicit action and approval boundaries
7. verification and Definition of Done
8. feedback from real outcomes
9. an access experience appropriate to the user's expertise and environment

IntentOS should make these capabilities reusable across AI vendors, project types, and user surfaces.

## Long-term direction

IntentOS should evolve into an open, extensible intent-to-execution layer with a small core and pluggable profiles/adapters for:

- AI tools and model families
- software engineering domains
- DevOps and infrastructure workflows
- security-sensitive workflows
- project/repository conventions
- evaluation strategies
- CLI, MCP, editor, agent, and simple-user access surfaces

The core must remain vendor-neutral and should degrade gracefully when model-specific information is unavailable. Ease of use should come from good defaults, thin integrations, and progressive disclosure rather than duplicated logic or hidden unsafe behavior.
