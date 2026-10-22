# Contributing to IntentOS

Thanks for helping improve IntentOS.

## Before you start

Read:

- `README.md`
- `AGENTS.md`
- `docs/SCOPE.md`
- `docs/ARCHITECTURE.md`
- `docs/STATUS.md`

IntentOS is intentionally small at the core. New features should solve a demonstrated problem without turning the project into a general autonomous-agent platform.

## Development

Requirements:

- Python 3.11+
- no runtime dependencies are currently required

Run the suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Or install editable and test the CLI:

```bash
python -m pip install -e .
intentos optimize "Refactor the parser" --target codex
```

## Pull requests

Keep PRs focused and explain:

1. the user/problem outcome
2. the smallest coherent change made
3. tests or evaluation evidence
4. any new dependency, persistent contract, or architecture decision
5. remaining risks or follow-up work

Avoid unrelated refactors.

## Adding AI/model support

Do not hardcode volatile model claims into the core. Tool behavior belongs in target profiles; current model metadata belongs in replaceable adapters/catalogs.

A new profile should include tests showing why generic behavior is insufficient.

## Adding engineering policies

Policies must be contextual. Do not globally inject SOLID, Clean Architecture, security, DevOps, or other practices into tasks that do not need them.

## Learning from failures

Prefer regression cases and repeated evidence. A one-off failure should not become a permanent prompt rule without broader evidence.

## Safety and repository writes

Core workspace maintenance is proposal-first. Integrations that apply changes must preserve approval boundaries for destructive, persistent, security-sensitive, or external writes.
