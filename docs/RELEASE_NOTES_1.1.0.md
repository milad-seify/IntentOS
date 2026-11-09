# IntentOS Core 1.1.0 — UNPUBLISHED RELEASE CANDIDATE

Public Core is still `1.0.1`. This document is a draft for review, **not** a PyPI upload, GitHub Release, tag or permission to begin Phase 8.

## New capabilities

- **F03:** Explainable model/tool routing using caller-supplied capability, availability and relative-cost metadata; explicit safe fallback, no live-price claims.
- **F04:** Reviewable, portable agent handoff packets; approval-bound Codex CLI dispatch where supported; other agents use manual handoff.
- **F05:** Project Compass with explicit authoritative source selection, provenance and missing/stale/conflicting context.
- **F06–F07:** Revision-pinned status/decision and scope-amendment proposals, exact-digest approvals, stale and replay protection.
- **F08:** Requirement/milestone evidence and owner readiness gates, without launch authorization.
- **F09:** Portable checkpoint creation and continuation review, without autonomous restart.
- **F10:** Caller-supplied observed outcome records, eligible comparisons and reviewed learning proposals, without silent policy mutation.
- **Simple UI:** `intentos ui` launches a local-only browser interface for guided Prepare → Review → Copy and the existing F01–F10 workflows. Explicit sources, session/Origin/CSRF protections and reviewed mutation boundaries remain in force.

Existing F01–F02 preparation and risk behavior, stable Python API, MCP `prepare_task`, preparation JSON schema v1 and run-record schema v1 remain compatible.

## Install (after publication)

```bash
python -m pip install --upgrade intentos-engineering==1.1.0
intentos --help
intentos ui
```

The current public registry cannot yet install this candidate; use an accepted source checkout until publication is complete.

## Limits and trust boundaries

IntentOS prepares contracts and reviews evidence; it is not a universal agent runtime. Ready does not mean work was executed or verified. The caller supplies model facts, project context, operation ledgers and outcome evidence unless independently verified. Human approvals must be enforced by the user/executing system. No silent agent execution, repository crawl, hosted backend, automatic evidence capture or launch permission. A Codex receipt is not proof of task correctness.

## Verified source and required release controls

The owner-accepted source integrated [PR #66](https://github.com/milad-seify/IntentOS/pull/66) at `862c5be0b15125c9f7e3f0ff24de2580fad39a51`; [post-merge CI](https://github.com/milad-seify/IntentOS/actions/runs/42633513115) passed 7/7. [Acceptance evidence](UI_ACCEPTANCE.md) includes real Edge/Windows UI, VS Code Extension Hosts, isolated VSIX, and wheel/sdist checks. No comprehensive security audit, full screen-reader certification, physical mobile or non-Windows real Extension Host was claimed.

The release-preparation revision requires fresh CI. Only separately approved immutable `v1.1.0` tagging and the protected `pypi` Trusted Publisher may publish Core. Verify exact wheel/sdist digests, clean public installation including `intentos ui` and optional MCP before creating the GitHub Release. Phase 8 and Dogfooding remain separate.
