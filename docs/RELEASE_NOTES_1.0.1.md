# IntentOS 1.0.1

Published Core patch release ([v1.0.1](https://github.com/milad-seify/IntentOS/releases/tag/v1.0.1)) on PyPI as `intentos-engineering==1.0.1`. [Release workflow](https://github.com/milad-seify/IntentOS/actions/runs/41685995740) passed; a clean Windows/Python 3.13 installation verified the CLI and read-only review behavior.

## Review-only classification and policy correction

- Packages the correction from [PR #38](https://github.com/milad-seify/IntentOS/pull/38), discovered during a real Phase 8 smoke attempt.
- Recognizes bounded English review, analysis, inspection, evaluation, recommendation, and proposal requests without treating technical subject matter or negated implementation instructions as coding intent.
- Uses the existing `general` task type with read-only guidance and evidence-based completion criteria. Codex and Claude Code prompts no longer add change-oriented defaults for these requests.
- Mixed review and implementation requests retain normal classification. Existing security, concurrency, and high-risk checks remain in place.

The distribution remains `intentos-engineering`. Public APIs and machine JSON/run-record schemas remain unchanged at schema version `1`. No new capability, dependency, MCP tool, routing architecture, or UX is added. Phase 8 validation gates are unchanged.

The independently released VS Code extension remains `milad-seyfi.intentos-vscode` version `0.1.1`.
