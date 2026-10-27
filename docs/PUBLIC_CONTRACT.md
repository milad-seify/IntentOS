# Stable-v1 public contract

This document defines the public compatibility surfaces prepared for IntentOS v1. The source currently declares package version 0.1.0; stable 1.0.0 has not been published. Internal modules and implementation details are not public contracts.

## Python API

The supported top-level imports are exactly the names exported by `intentos.__all__`:

- Types: `CapabilityClass`, `ContextDocument`, `CostClass`, `EffortLevel`, `IntentRequest`, `ModelMetadata`, `PromptResult`, `RunMetrics`, `RunRecord`, and `SkillArtifact`.
- Functions: `build_run_record`, `build_skill_artifact`, `optimize_project_prompt`, `optimize_prompt`, and `plan_agent_workspace`.

Documented call patterns, including `IntentRequest.from_values`, `optimize_prompt`, and run/Skill builders, are supported. The explicit exports and documented call behavior are stable surfaces; private modules are not. Dataclass layouts or attributes not documented as part of behavior may gain compatible additions. Removing or renaming an export, changing a documented call incompatibly, or changing its meaning requires a major package version.

## CLI

The supported entry points are `intentos` and the equivalent `python -m intentos` invocation:

- `optimize <text>` supports `--target`, repeatable `--constraint` and `--success`, plus `--context-file`, `--output-format`, `--audience`, and `--json`.
- `skill <text>` supports the optimize options plus `--name`, `--description`, and `--json`.
- `workspace` supports required `--phase`, repeatable `--document`, and `--json`.
- With the optional MCP extra installed, `intentos-mcp` starts the local stdio adapter.

A ready command returns exit code `0`. A clarification, handled input error, or invalid CLI invocation returns non-zero (currently `2`). JSON mode distinguishes ready, clarification, and error; human-readable wording is not a compatibility surface. Documented command names and flags cannot be removed or silently repurposed in a compatible release.

## Machine-readable JSON

The `schema_version` value is independent of the Python distribution version. Ready and clarification results from optimize and MCP use schema `1` and retain these top-level fields:

`schema_version`, `status`, `needs_clarification`, `questions`, `intent`, `prompt`, `task_type`, `risk_level`, `engineering_rules`, `approval_boundaries`, `done_criteria`, `routing`, `context`, and `context_paths`.

`status` is `ready` or `clarification` for these result shapes. `context_paths` is retained as a schema-v1 compatibility alias and must equal `context.selected_paths`. A handled CLI error uses a compact schema-1 object with `status` and `error.type`/`error.message`; it is distinct from a prepared result. Skill JSON success retains `schema_version`, `status`, `name`, `description`, and `content`; skill clarification uses the optimize result shape. Workspace JSON retains `schema_version`, `status`, `changes`, and `warnings`.

Compatible schema-v1 releases may add fields without changing the meaning or type of existing fields. Removing, renaming, retyping, or changing the meaning of a documented field requires a new machine schema version. The package version and each machine schema version remain independently managed.

## Run records

`RunRecord.to_dict()` and `RunRecord.to_json()` emit run-record schema `1`, independently of package version. The serialized fields are:

`schema_version`, `intentos_version`, `prompt_sha256`, `target_tool`, `task_type`, `risk_level`, `required_capability`, `effort`, `selected_model`, `routing_fallback`, `context_paths`, `context_fingerprints`, `metrics`, and `tags`.

Metrics contain `success`, `quality_score`, `input_tokens`, `output_tokens`, `latency_ms`, and `retries`. A context fingerprint contains a path label and SHA-256 digest. Raw prompts and context contents are not stored in the record. Schema-v1 additions may be additive; incompatible serialized-shape changes require a new run-record schema version.

## MCP

MCP is an optional `intentos-engineering[mcp]` extra. It exposes exactly one tool, `prepare_task`, over local stdio and calls the shared IntentOS core. Context must be caller-supplied content, limited to 32 documents and 6000 characters. The adapter does not discover or read arbitrary files, authorize execution, mutate a workspace, or expose additional tools. These boundaries are part of the v1 MCP contract.

## Package compatibility policy

After stable v1:

- Patch releases contain backwards-compatible fixes.
- Minor releases may add backwards-compatible capabilities and fields.
- Major releases may remove, rename, or incompatibly change a documented public surface.

Machine schemas keep their own version identifiers and advance when their documented compatibility rules require it.
