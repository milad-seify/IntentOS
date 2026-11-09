# Graphical candidate — hardening verification

**2026-11-09: corrected candidate for owner acceptance in PR #66.** This is developer evidence under D-033, not an effective Feature Freeze, publication approval or Phase 8 observation. D-032's historical accepted core source is preserved.

## Original acceptance defects

| Defect | Cause and correction | Regression evidence |
| --- | --- | --- |
| Windows uploads rejected | UI validation rejected CR in CRLF. Normalize paired CRLF while retaining raw input limits; reject bare CR and unsafe controls. Preserve Unicode and source line references. | HTTP LF/CRLF preparation/provenance equality; CRLF model, gate, checkpoint and outcome uploads; real browser interactions. |
| Long result overflow | Generic technical values lacked wrapping. Cards, nested values and exact results now wrap; hashes remain in expandable details. | Real browser and editor Webview at 390px/320px; expanded routing JSON/fingerprint fits without document overflow. |
| Invisible operation feedback | Feedback sat after every form. Move the durable status/alert node beside the active action, focus errors, lock controls while busy, and recover afterward. | Visible progress, duplicate submission, malformed uploads, stale approvals, recovered controls and editor error/focus checks. |

## Additional improvements

- Unsent drafts and chosen files survive navigation **in tab/panel memory only**. Close/reload or Clear session drafts removes them. No browser storage, synchronization or database was added.
- Previous reviews are labeled and restored without approval tokens/digests. Navigation and edited inputs invalidate the graphical approval action; preview again against current sources.
- Semantic summaries explain status, routing limits, gates, recovery, comparison and lessons before exact technical details. Project claims retain nearby source/line/authority information.
- Portable handoffs show readable instructions with Copy alongside packet export. Native editor entry points and basic Prepare → Review → Copy remain available.
- Model/readiness/checkpoint/outcome examples explain required evidence. Their placeholders, unknown checks and unapproved defaults never represent actual approval or observations.
- Upload validation, actionable errors, visible focus, live announcements and reduced-motion support improve recovery and accessibility.
- The editor harness rejects disconnected/timed-out browser calls and terminates only its temporary profile. A missing PowerShell separator had previously prevented cleanup during longer interactive runs.

The adapters share one small mirrored presentation asset, with an equality contract test; no classifier, router, approval or evaluation logic moved into JavaScript. Core source remains `1.1.0`; the extension manifest remains `0.1.1`. Neither package was published.

## Verification scope

The [F01–F10 matrix](SIMPLE_UI.md#graphical-coverage-at-the-ui-candidate-revision) identifies each graphical entry point. The standalone real browser submits all six sections, downloads/reuses artifacts, and confines writes/approvals to a disposable Git project. Synthetic outcomes are explicitly developer test data. Real editor Webviews exercise task entry/selected text, Prepare/Review/Copy, all six sections, drafts, safe examples, routing fallback, associated error/focus/control recovery and narrow layouts.

Local gates: 258 Python tests run, OK with one existing skip; CLI prepare/Compass smoke; MCP smoke/stdio parity; JavaScript syntax/contracts; standalone browser acceptance; workspace and no-workspace Extension Hosts; and installed-VSIX activation/Webview checks. Distribution and VSIX validators inspect metadata, hygiene and clean installations, including UI assets. The final exact-SHA seven-job CI result is recorded on PR #66; local counts alone do not establish acceptance.

The actual local browser is Edge on Windows. Coverage includes light/dark, long Unicode, keyboard skip/focus basics, reduced motion and desktop/390px/320px layouts. No live agent was dispatched. Explicit approvals, revision/digest checks, high-risk workspace-write blocking, readiness-not-launch and missing metrics remain conservative. This is not a comprehensive security audit, screen-reader certification, physical-mobile test or non-Windows editor run. Full native file/save-dialog ergonomics are not automated by the editor checks.

## Genuine screenshots

- [CRLF source prepared successfully](evidence/simple-ui-crlf-context.png)
- [Progress beside the active action](evidence/simple-ui-active-feedback.png)
- [Expanded technical result at 320px](evidence/simple-ui-320-refined.png)
- [Editor inline error and recovered controls](evidence/vscode-workbench-inline-feedback.png)

Other temporary screenshots, package files and logs stay outside the repository. One-time launch URLs are excluded.

## Deliberately deferred

Full schema editors, automatic evidence capture, cloud persistence, additional provider adapters and autonomous execution would broaden the accepted product. The current examples and guided existing forms reduce friction within the existing contracts. Native dialog and assistive-technology review remains part of owner acceptance. A fresh integrated source acceptance is required before merge, publication or Phase 8 authorization.
