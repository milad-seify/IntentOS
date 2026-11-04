# IntentOS Core 1.1.0 — UNPUBLISHED RELEASE CANDIDATE

**Status:** draft notes for the full-scope F01–F10 source candidate. **Not a GitHub Release, PyPI publication, tag, final Feature Freeze, or Phase 8 evidence.** The currently published Core remains `1.0.1`, and the separately distributed VS Code extension remains `0.1.1`.

## Additive capability access

- **Project Compass:** source-grounded read-only goal/current-state/scope guidance with explicit provenance and unresolved/stale handling.
- **Reviewed state changes:** revision-pinned proposals and content-bound human approval for local STATUS, DECISIONS and SCOPE amendments; safe replay and conflict detection.
- **Project governance:** requirement/milestone checks and reviewable launch readiness from caller-supplied evidence; no automatic launch authorization.
- **Routing:** caller-supplied model metadata, explanation, constraints and conservative fallback; no live provider price or availability guarantee.
- **Agent handoff:** portable reviewable handoff packets and explicit bounded Codex CLI dispatch (other agents use manual copy); completed agent turns are unverified until independently checked.
- **Checkpoint/resume:** pinned plans and context, duplicate-operation and approval checks, review-only restart recommendations; no autonomous resume.
- **Outcome evidence:** bounded records, paired comparisons and explicitly approved evidence-backed lesson proposals; no silent policy writes.

Existing F01/F02 preparation, risk and policy behavior remains in place and is covered by regressions.

## Compatibility, limitations and acceptance

The existing documented Python top-level exports, MCP `prepare_task` tool, preparation JSON schema v1, run-record schema v1, and VS Code Prepare → Review → Copy workflow are unchanged. This is a **Core minor-version candidate**, not a claim of a published end-user extension update.

All new route, evidence, operation-ledger and approval inputs must be treated as caller-supplied unless independently verified; approval hashes bind an explicit review but do not themselves prove human identity. No automatic agent execution beyond explicitly approved Codex dispatch, no guaranteed token budget, and no unverified task success or production launch claims.

The developer's consolidated pre-version-bump acceptance is recorded in [FULL_SCOPE_CANDIDATE.md](FULL_SCOPE_CANDIDATE.md). **Final exact-head PR CI, main-merge CI and full-source review remain required after this version metadata change.** Production release, final Feature Freeze, external user Phase 8 sessions and owner Dogfooding are separate explicitly authorized steps. Never republish different bytes under `1.0.1`.
