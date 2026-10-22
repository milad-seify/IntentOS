# Scope

This document defines what IntentOS accepts, improves, returns, and how users or agents may access it.

## Inputs

IntentOS may receive:

- a rough natural-language request
- target AI/tool, when known
- repository or project context
- project rules and agent files
- engineering preferences
- constraints and approval boundaries
- expected output or success criteria

Only relevant context should be loaded. More context is not automatically better.

## Core processing boundary

IntentOS may:

1. extract and normalize intent
2. identify missing critical information
3. classify task type and risk
4. select relevant project context
5. apply domain engineering policies contextually
6. adapt instructions to the target AI/tool/model family
7. optimize the prompt for clarity and token efficiency
8. generate execution workflow and approval boundaries
9. generate verification and Definition of Done
10. create or propose updates to agent-facing context files
11. compile portable Agent Skill artifacts
12. collect versioned evaluation/run metadata for future improvement

## Initial domains

### General AI prompting

Prompt generation, repair, adaptation, and optimization across supported AI tools.

### Software engineering

Contextual guidance may include Clean Code, SOLID, DRY, KISS, YAGNI, separation of concerns, maintainability, testability, compatibility, secure defaults, observability, and architecture fit.

These are decision principles, not mandatory patterns. Small tasks must remain small.

### DevOps and infrastructure

Contextual guidance may include reproducibility, idempotency, infrastructure as code, CI/CD, secrets handling, least privilege, observability, rollback, deployment safety, configuration management, and operational verification.

## Access surfaces

IntentOS is one core with multiple access surfaces for different users and environments.

### CLI and Python API

These are first-class interfaces for developers, scripts, CI, automation, and integrations. They should remain deterministic and machine-readable where practical.

### MCP adapter

A future MCP adapter may expose bounded IntentOS capabilities to compatible AI agents. MCP is an interoperability surface; IntentOS does not become a general MCP runtime.

### VS Code extension

A future VS Code extension may provide editor-native task preparation, risk/context preview, workspace proposals, and handoff to connected agents. It must remain a thin UI/integration layer over the core.

### Simple user interface

A future simple UI may expose outcome-first workflows for users who do not know prompt engineering, model routing, or agent internals. Advanced settings should be optional through progressive disclosure.

### Agent Skills

Portable `SKILL.md` artifacts provide reusable, on-demand agent guidance without coupling the core to one IDE or vendor.

No access surface should independently reimplement core policy, routing, context selection, or verification logic.

## Outputs

Depending on the request, IntentOS may return:

- optimized prompt
- portable Agent Skill artifact
- recommended AI/tool/model family or effort class
- task/risk classification
- selected context summary
- engineering constraints
- execution workflow
- approval boundaries
- verification commands/checks
- Definition of Done
- agent context-file creation/update plan
- versioned evaluation/run metadata

Not every request needs every output.

## Agent workspace maintenance

IntentOS may create, update, or recommend compact agent-facing files such as:

- `AGENTS.md`
- `STATUS.md`
- `ARCHITECTURE.md`
- `DECISIONS.md`
- `ROADMAP.md`
- task-specific context files

It must avoid duplicating source-of-truth documentation and must not let context files grow without bounds. Generated updates should preserve human decisions and distinguish facts from inferred recommendations.

## Out of scope for the core

IntentOS is not intended to become:

- an IDE
- an autonomous coding agent
- a model hosting platform
- a general MCP runtime
- a CI/CD service
- a project-management suite
- a replacement for source control
- a mandatory software architecture framework
- a universal orchestration platform for arbitrary autonomous agents
- a mandatory hosted/cloud service

Integrations may connect to these systems later without moving their responsibilities into the core.
