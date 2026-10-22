# Adoption notes

This file captures the two Hugging Face-inspired patterns adopted before the independent audit.

## Portable Skill artifact

IntentOS can compile an already-normalized intent and execution policy into a reviewable `SKILL.md`-compatible artifact.

The core does not install or write the artifact automatically. Agent-specific placement, plugin packaging, and marketplace publishing remain integration concerns.

## Versioned run record

IntentOS can produce a compact JSON-serializable run record with:

- schema version
- prompt fingerprint rather than raw prompt content
- target tool
- task/risk classification
- routing requirements and selected model when known
- selected context paths
- externally supplied quality/token/latency/retry metrics
- caller-defined tags

This record is deliberately storage-agnostic. It can later feed JSONL datasets, telemetry adapters, evaluation dashboards, or Hub uploads without coupling the core to any of them.

## Privacy / context hygiene

The record intentionally stores a SHA-256 prompt fingerprint instead of the full prompt. Raw prompts, source files, tool outputs, secrets, and conversation histories should only be persisted by an executor when the user/project policy explicitly allows it.
