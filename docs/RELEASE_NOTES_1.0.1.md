# IntentOS 1.0.1

Patch release preparation. Tagging and publication require separate maintainer authorization; 1.0.0 remains the published Core release until then.

## Review-only classification and policy correction

- Packages the correction from [PR #38](https://github.com/milad-seify/IntentOS/pull/38), discovered during a real Phase 8 smoke attempt.
- Recognizes bounded English review, analysis, inspection, evaluation, recommendation, and proposal requests without treating technical subject matter or negated implementation instructions as coding intent.
- Uses the existing `general` task type with read-only guidance and evidence-based completion criteria. Codex and Claude Code prompts no longer add change-oriented defaults for these requests.
- Mixed review and implementation requests retain normal classification. Existing security, concurrency, and high-risk checks remain in place.

The distribution remains `intentos-engineering`. Public APIs and machine JSON/run-record schemas remain unchanged at schema version `1`. No new capability, dependency, MCP tool, routing architecture, or UX is added. Phase 8 validation gates are unchanged.

The independently released VS Code extension remains `milad-seyfi.intentos-vscode` version `0.1.1`.
