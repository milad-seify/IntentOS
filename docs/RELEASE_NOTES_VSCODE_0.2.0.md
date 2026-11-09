# IntentOS for VS Code 0.2.0 — UNPUBLISHED RELEASE CANDIDATE

The current public Marketplace extension remains `0.1.1`. This is release preparation only; no `vscode-v0.2.0` tag or Marketplace publication is authorized.

## Changes

- Activity Bar IntentOS Workbench with **Start, Project, Govern, Delegate, Recover and Outcomes** views backed by the existing shared Core.
- Guided preparation, selected editor text, clarification, approvals, verification and explicit Copy, preserving the existing status-bar and Command Palette flow.
- Source-grounded Project Compass; reviewable state/scope proposals and milestone/readiness evidence; explainable routing and portable handoffs; approval-bound Codex dispatch; checkpoints; outcomes.
- Session-only draft/file retention without stored approval authority, accessible inline loading/errors, responsive long technical results, and conservative evidence JSON examples.

## Prerequisite and limits

**Advanced Workbench requires Core `intentos-engineering==1.1.0` or later**, installed separately and available as `intentos` in VS Code's environment. Public Core 1.0.1 supports basic Prepare → Review → Copy only. The extension is a review/control surface, does not silently execute agents, grant permissions, crawl repositories, collect outcome evidence or run a hosted service. Only existing explicit Codex dispatch is supported; other agents use manual handoff.

## Acceptance and publication

Source UI acceptance was recorded on [PR #66](https://github.com/milad-seify/IntentOS/pull/66) merged at `862c5be0b15125c9f7e3f0ff24de2580fad39a51`; [post-merge CI](https://github.com/milad-seify/IntentOS/actions/runs/42633513115) passed 7/7. See [UI acceptance](UI_ACCEPTANCE.md). Preparation changes need fresh CI and clean VSIX/installed Extension Host validation. Full screen-reader, physical mobile and non-Windows real Extension Host checks were not claimed.

Only after Core 1.1.0 is separately published and verified and the owner explicitly approves extension publication may an immutable `vscode-v0.2.0` tag trigger the protected Marketplace OIDC workflow. Verify its exact VSIX artifact digest, Marketplace listing and clean installed extension. No Phase 8 work is authorized by this release preparation.
