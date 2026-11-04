# Stage E — Stabilization & Feature Freeze Readiness

**Status:** readiness review **MERGED and verified** ([PR #46](https://github.com/milad-seify/IntentOS/pull/46); [post-merge main CI 41807465709](https://github.com/milad-seify/IntentOS/actions/runs/41807465709), 7/7 passed). Final Feature Freeze remains **PROPOSED / NOT YET EFFECTIVE** under D-028. Do not start Phase 8 from this report.  
**Audit date:** 2026-11-04. **Reviewed `main` source SHA:** `976db7ef888d26aca8804490147e384273cfa9b7`.  
**Exact main CI:** [run 41805348708](https://github.com/milad-seify/IntentOS/actions/runs/41805348708) — completed successfully, seven of seven jobs. No open PRs when the assessment began.

## Decision scope

Freeze the **currently accepted source and public contracts** after review; do not introduce a new product capability, public release or vendor integration. Stage A [PR #41](https://github.com/milad-seify/IntentOS/pull/41), B1 [PR #42](https://github.com/milad-seify/IntentOS/pull/42), B2 [PR #43](https://github.com/milad-seify/IntentOS/pull/43), C1 [PR #44](https://github.com/milad-seify/IntentOS/pull/44), and D1 [PR #45](https://github.com/milad-seify/IntentOS/pull/45) are merged. **B1 is internal-only; B2/C1/D1 implementations are deferred.** There is no mandate to fill those gaps before validation.

This is a **code and contract freeze**, not a claim of validated end-user adoption, successful downstream tasks, security certification, independent user studies, complete multilingual NLP or production-readiness.

## Evidence / gate inventory

| Gate | Evidence inspected | Judgment |
| --- | --- | --- |
| Immutable source and CI | Main commit above; [main CI 41805348708](https://github.com/milad-seify/IntentOS/actions/runs/41805348708): Python 3.11/3.12/3.13 on Ubuntu, Windows Python 3.13 regression, MCP protocol + real stdio parity, JS syntax smoke and wheel/sdist clean-install/distribution artifact check | **Pass for repository regression gate.** This is not new public-install/first-use evidence. |
| Stable Python surface | GitHub blob comparisons of all **19 shared** `src/intentos/*.py` modules between `v1.0.1` and this main source: **19/19 identical**. `src/intentos/__init__.py` exports the existing exact 15-name set; `tests/test_public_contract.py` guards exports and schema-1 fields | **No observed public-v1 behavior/code change** in the shared modules. The additional `compass.py` exists only on post-release source, not on the `v1.0.1` tag. |
| CLI/MCP/machine/run-record compatibility | Unchanged `cli.py`, `mcp_server.py`, `result_contract.py`, `records.py`, `pyproject.toml` against `v1.0.1`; contract tests and CI passed. MCP still exposes one `prepare_task` with **32 documents / 6000 characters**; JSON and run-record schemas remain **1** | **Pass for unchanged public contract.** No new MCP tool, JSON surface, CLI option or DB/agent integration. |
| VS Code public behavior | `extension.js`, `executable.js`, `package.json` and extension README compared against `vscode-v0.1.1`: **4/4 identical**. Existing extension escapes user-derived HTML, uses a nonce-based webview CSP, `execFile` and explicit Copy. Historic Extension Host workspace/no-workspace and Marketplace installation tests documented in [VSCODE_DOGFOODING.md](VSCODE_DOGFOODING.md) and [VSCODE_MARKETPLACE_RELEASE.md](VSCODE_MARKETPLACE_RELEASE.md) | **Unchanged published UX.** Current CI only executes `node --check`; it **does not rerun real VS Code Extension Host integration**. Earlier evidence must not be misrepresented as a fresh Stage E test. |
| B1 internal pilot and trust boundary | `src/intentos/compass.py`, 19 focused tests, [B1 review](B1_PROJECT_COMPASS_PILOT.md), accepted [PR #42](https://github.com/milad-seify/IntentOS/pull/42). Explicit caller-supplied Markdown; **32 documents / 36000 characters** *only for private B1*, source labels/lines, caller-designated authority flag, conservative `unknown`/unresolved/stale and `scope_review_required` | **Technically reviewable, not product-validated.** No filesystem/network actions, writes, agent execution or public `__all__`/CLI/MCP/VS Code integration. B1's authority flag is **not authenticated**, exact scope matching may miss drift, and user-document claims are not independently verified. |
| Security / privacy boundaries | Inspected B1, CLI, MCP adapter, context selection, run records and VS Code shell/webview boundary. IntentOS does not execute prepared agent tasks. `RunRecord` stores hashes of prompt and selected context plus user-supplied labels/metrics, not raw prompt/context; CLI reads only paths supplied by the caller; MCP receives supplied content | **No new execution or automated-write surface observed in this program.** This is a scoped code/contract review **not** a penetration test, dependency audit, secret scan, threat-model certification or proof all paths are safe. |
| Evidence and feature governance | [Phase 7C](PHASE_7C_EVIDENCE.md): 10 historical tasks; 3 prepared / 2 raw / 5 inconclusive, no repeated promotion need. B2/C1/D1 assessments record missing implementation evidence | **Pass for deferring unproven features.** Historical Phase 7C outcomes do not become new Phase 8 observations. |

## Two distinct version identities — important

1. **Published product used by Phase 8 8A first-use testing:** Core `intentos-engineering==1.0.1` from PyPI and published VS Code `milad-seyfi.intentos-vscode@0.1.1`. Verify installed versions and origin **outside the repository**, with no editable checkout masking installation defects. The public source components are unchanged against their release tags.
2. **Post-Phase-7 source candidate:** the reviewed main source SHA above includes private `intentos.compass` B1. B1 is not part of the published Core `1.0.1` artifact, and there is no public entry point to it. A locally rebuilt wheel from the current checkout still declares package version `1.0.1`, yet has **different contents** from the published `1.0.1` artifact. **Do not publish or call that rebuilt artifact the existing public release.** Any future distribution with B1 requires a separately approved compatible version bump/release and a user-facing evidence/contract decision.

**Consequence:** Phase 8 public-install testing of `1.0.1` cannot count as independent validation of B1. Conversely, manually importing B1 from a source checkout does not satisfy Phase 8 first-use public-install criteria. The complementary Idea-to-Production dogfood may use only separately authorized surfaces, with source/variant explicitly recorded.

## Remaining limitations / explicit non-blockers

- **B1:** narrow recognized headings; no semantic or multilingual scope inference; caller-asserted document authority/freshness, no independently verified approval or change history; not exposed through published UX. Must be described as an **internal prototype**, not as a shipping product feature.
- **B2/C1/D1:** no durable state-update lifecycle, verified milestone/launch gate, live provider metadata, token reserve, autonomous checkpoint/resume, or cross-agent execution. All deferred pending distinct evidence, not casually reclassified as incomplete releases.
- **Quality evidence:** existing CI verifies fixed behavior and package shapes; it does not establish improved downstream AI correctness, adoption, cost savings, availability, model quality or production readiness.
- **Additional external checks:** no fresh independent security assessment, user onboarding, real VS Code Extension Host run, Windows/public-install retest, deployment runbook validation or external agent-outcome session was conducted in **this** Stage E review. These may become separate prerequisites to a *future release* or Phase 8; do not label them passed here.

## Freeze acceptance checklist

A **formal Stage E feature freeze** may be recorded only after all of the following:

1. Review/accept this document's scope, factual evidence, and limits; no unreviewed source/runtime change in the freeze PR.
2. PR for this assessment changes **documentation only**; its **exact-head 7-job CI passes**.
3. Maintainer explicitly authorizes the freeze PR merge; merge completes; current main is verified; **post-merge main CI** passes and the final merge SHA is pinned. The source-code baseline for this review remains `976db7ef888d26aca8804490147e384273cfa9b7` unless implementation changes.
4. B1 is recorded as internal, B2/C1/D1 are deferred with their evidence decisions, stable v1/public tags are unchanged, and there is no new release publication.
5. Freeze decision and final code/merge SHA are accepted in the decision log/status. Any later material correctness/safety/public-contract fix needs a focused regression, independent approval, new pinned candidate and repeat freeze gate; new product features do not creep into Phase 8.

**Follow-up verdict (2026-11-04):** the readiness PR was merged and its post-merge CI passed on `28dc5c84ea4d154a99cf68c7446303648f076d52`. The **formal** [D-028 proposal](DECISIONS.md) must still pass its own approval, merge and final main-CI/pin gate. This document alone does not declare a freeze or authorize Phase 8.

## Phase 8 authorization remains separate

After feature freeze, request a **new explicit authorization** to start operational Phase 8 and a separately scoped Idea-to-Production dogfood. Retain the unchanged [Phase 8 protocol](PHASE_8_VALIDATION.md), including 8A **three observed sessions / at least two first-time users / Windows and POSIX / at least two independent completions**, and 8C **20 new distinct real tasks across at least two users (one non-maintainer) and three projects; target at least 12 controlled eligible pairs**. Preserve privacy, control of paired conditions, and correctness-first decisions; no retroactive Phase 7C counting.
