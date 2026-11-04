# F01–F10 feature candidate — developer acceptance record

**Status:** Feature-complete *candidate* on the stacked development branch. The consolidated developer gate passed on code revision `709fc4a388665187d59d5d51c3db87f39e9500ae`; final documentation and GitHub CI remain subject to review. This document does not enact a Feature Freeze, release, operational Phase 8 session, or deployment. The *published* Core `1.0.1` and VS Code `0.1.1` remain unchanged. The **source candidate** is proposed as Core `1.1.0` (minor, additive/compatible CLI features), with **no publication or tag**. Exact-head CI and an accepted merge are required before final source Freeze.

The source of truth for scope is [D-031](DECISIONS.md) and the [finite delivery program](DELIVERY_PROGRAM.md). All new access is development CLI; existing MCP and VS Code public contracts are preserved. External references, model metadata, operation ledgers, approvals and outcome checks remain caller assertions unless an independent source is cited. IntentOS never equates an agent turn, passing checklist, or matching digest with task verification or launch authorization.

| Feature | Working access and acceptance evidence | Boundary |
| --- | --- | --- |
| F01 task preparation | `intentos optimize` and existing VS Code Prepare → Review → Copy; prompt, CLI and integrated access tests | Clarification remains explicit |
| F02 risk/policy | Shared classifier and policy on CLI/MCP/VS Code; high-risk and read-only regressions, integrated high-risk case | Approval guidance is not permission; high-risk automatic workspace-write is blocked |
| F03 routing | `intentos route` with caller-supplied catalog, candidate exclusions and fallback; selected model can be passed explicitly to dispatch | No live price, availability or capability attestation |
| F04 agent handoff | `intentos handoff prepare` creates a target-specific packet; digest-approved Codex CLI dispatch returns an unverified receipt; other targets get portable manual handoff | No implicit run, unrestricted sandbox, or fabricated agent result |
| F05 Project Compass | `intentos compass` with explicit source authority and file/line provenance; missing/stale/conflict tests | Unknown scope never becomes in-scope automatically |
| F06 durable state | `intentos state status/decision` preview, content-bound approval and revision-checked local write; fresh-process tests | Only known project documents and reviewed proposals |
| F07 scope guard | `intentos state scope` previews a single amendment and records owner reference/history; conflicting or stale source tests | Scope amendment does not authorize execution |
| F08 requirements and launch gates | `intentos gates` traces accepted requirements, milestone lifecycle and external check evidence; blocked/ready cases | Ready means ready for owner review; `launch_approved` stays false |
| F09 checkpoint/recovery | `intentos checkpoint create/review` stores approved plan/state/evidence and pins Git revision/context; cross-process, replay, approval and budget tests | External operation ledger and budget are caller supplied; resume is never self-approved |
| F10 outcome learning | `intentos outcome record/compare/learn` stores bounded external checks/metrics, reuses the paired comparator, and saves only digest-approved repeated proposals | Unknown checks are inconclusive; no silent policy mutation or synthetic Phase 8 evidence |

## Final gate to record on the exact candidate

- Full Python unit and integrated tests on Windows plus Linux CI Python 3.11–3.13.
- CLI smoke, MCP protocol/stdio parity and VS Code syntax/contract checks.
- Real local VS Code Extension Host workspace and no-workspace checks.
- Wheel/sdist build, artifact and clean-install validation; no publication.
- Security/privacy and failure review: bounded inputs, explicit approvals, no raw stderr or secrets in receipts, replay/stale-source rejection, safe local document writes, and no automatic launch claim.
- Final diff review, `git diff --check`, clean working tree, and all GitHub CI jobs green.

## Developer gate result

- Windows/Python 3.13 local suite: **243 run, 242 passed, one Windows symlink test skipped**; F01–F10 integrated CLI flow passed. CLI read-only review smoke reached `ready`.
- Real installed VS Code Extension Host: **workspace and no-workspace passed**. Both activated `milad-seyfi.intentos-vscode`, resolved the repository `.venv` executable and returned CLI `ready` in isolated user-data directories. JavaScript syntax checks passed.
- An earlier F04 synthetic read-only Codex CLI dispatch in a temporary Git project completed with exit code 0 and a `completed_unverified` receipt. This is developer adapter verification, not task correctness or Phase 8 evidence.
- Local wheel and sdist built from Git-archived code revision `709fc4a3`; artifact hygiene and metadata checks passed for `intentos_engineering-1.0.1-py3-none-any.whl` and `intentos_engineering-1.0.1.tar.gz`. No artifact was published.
- [Candidate CI](https://github.com/milad-seify/IntentOS/pull/65) passed **7/7** jobs on that code revision: Python 3.11/3.12/3.13, Windows regression, MCP protocol/stdio parity, VS Code syntax, and clean wheel/sdist installation/validation.
- Local MCP scripts could not start because the development virtual environment lacked the existing optional `mcp` extra and pip could not resolve `files.pythonhosted.org` while installing it. The GitHub CI MCP and distribution jobs passed; no product or dependency change was made for this local DNS failure.
- `git diff --check` passed and the candidate source tree was clean after commit. The review found no raw stderr/credential echo in Codex receipts, no automatic high-risk workspace-write, no silent governance document write, and no automatic launch approval. The external executor, caller-provided evidence and owner sign-off remain explicit trust boundaries.

After the gate, the owner still decides whether to accept and merge the stacked PRs, how to version these development capabilities, and whether to record a new Feature Freeze. Operational Phase 8A/8B/8C and owner-led dogfooding remain separately authorized and unstarted.
