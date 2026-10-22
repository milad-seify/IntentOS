# Hugging Face research pass

This note records ideas from the Hugging Face ecosystem that materially overlap with IntentOS. The goal is not to copy frameworks or add dependencies; it is to adopt proven interface and evaluation patterns where they strengthen IntentOS.

## Areas reviewed

- Hugging Face Agent Skills and the Agent Skills specification
- Hugging Face Context Course
- smolagents, including memory, final-answer checks, telemetry, and tool calling
- tiny-agents and MCP integration
- Gradio Spaces as MCP tools
- Transformers chat templates for tools/documents
- Hugging Face Inference Providers and provider-selection policies
- Lighteval / Evaluate
- Open Agent Leaderboard / Exgentic evaluation approach
- agent/tool-use trajectory datasets and failure benchmarks on the Hub

## Adopt now

### 1. Portable Agent Skill artifacts

Agent Skills turn repeated prompt/context knowledge into a reusable, discoverable `SKILL.md` artifact that can be loaded only when relevant and used across multiple coding-agent surfaces.

IntentOS should be able to compile a normalized execution policy into a portable Skill artifact without coupling the core to one vendor or writing to a repository automatically.

Why now:
- directly matches IntentOS context-hygiene goals
- avoids repeating large instructions in every prompt
- improves portability across Codex, Claude Code, Gemini CLI, Cursor, and future agents
- remains proposal-first and human-reviewable

### 2. Versioned execution/evaluation records

The Open Agent Leaderboard and agent-trajectory datasets evaluate complete systems rather than only model outputs. Reproducibility depends on recording the agent configuration, model/routing choice, context, task, result, quality metrics, and cost/latency signals.

IntentOS should emit a compact, versioned run record that external executors can populate and persist. The core should not own storage or tracing backends.

Why now:
- makes evaluation and A/B comparisons reproducible
- gives learning proposals evidence with provenance
- prepares future export to JSONL / Hub datasets / OpenTelemetry adapters
- keeps prompt quality separate from system quality

## Keep as extension points, not core dependencies

### Routing strategy and failover

Hugging Face Inference Providers exposes explicit policies such as fastest, cheapest, preferred provider, and automatic failover. IntentOS already separates capability and cost from model names. A future routing adapter can add latency/throughput/provider availability without changing core prompt compilation.

Do not add network provider discovery to the core yet.

### MCP/tool interoperability

Hugging Face exposes Hub resources and community Spaces through MCP, and Gradio Spaces can become MCP tools. IntentOS should eventually describe required/allowed tools and approval boundaries in a portable tool contract, but it should not become an MCP runtime.

### Observability

smolagents uses OpenTelemetry-compatible tracing and supports replayable run histories. IntentOS should define telemetry-friendly records and adapters later rather than adding an observability dependency now.

### Structured tool/document templates

Transformers chat templates standardize `tools` and `documents` inputs. IntentOS can later compile tool/document requirements into target adapters. The core should continue to model intent semantically instead of emitting one vendor's wire format.

### Final-answer checks

smolagents supports final-answer validation callbacks. IntentOS already has verification and Definition-of-Done semantics; a future executor adapter can convert those into machine-executable checks where possible.

## Evaluation ideas from Hub datasets

The Hub has a large and fast-growing set of agent/tool-use traces and failure benchmarks. Useful concepts for IntentOS regression fixtures include:

- tool-selection correctness
- argument/schema validity
- constraint following
- recovery from failed actions
- final-answer faithfulness
- full trajectory quality, not only final output
- quality/cost trade-offs
- standardized trajectory schemas across agent frameworks

These should inform future fixtures, but IntentOS should not vendor large external datasets into the repository.

## Non-goals from this research pass

- no smolagents/tiny-agents runtime dependency
- no Hugging Face SDK dependency in core
- no hosted service
- no model training/fine-tuning
- no automatic repository writes
- no full MCP client/server implementation
- no hardcoded provider catalog

## Decision

Before the independent audit, add two bounded capabilities:

1. a portable `SKILL.md` artifact compiler;
2. a versioned run/evaluation record suitable for JSON serialization and later telemetry/dataset adapters.

Everything else remains an explicit extension point until dogfooding demonstrates a concrete need.
