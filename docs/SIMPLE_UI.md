# Local Simple UI (development candidate)

The source candidate includes a local browser interface. It is not in the published Core `1.0.1` package. Install the candidate in a clean environment, then run `intentos ui`. The command opens a one-time URL in your browser; `intentos ui --no-browser` prints that URL for an explicit local open. Keep the terminal running while using the UI, and press Ctrl+C to stop it. No cloud account, provider key or VS Code installation is needed for basic task preparation.

## First use

1. On **Start**, describe the outcome. Optionally choose an AI tool and specific project documents; no files are scanned automatically.
2. Choose **Prepare task**. If clarification is needed, revise the task and retry.
3. Review the interpreted goal, risk, approval boundaries, context/provenance, verification and prepared instructions. **Ready** means ready for handoff, not that the task is complete.
4. Choose **Copy Prepared Task**, then paste it into your own AI tool. Copy is explicit; IntentOS does not send or execute the task in this basic flow.

The navigation offers **Project**, **Governance**, **Delegation**, **Recovery** and **Outcomes**. Project Compass reads only the documents you select and shows missing, stale or conflicting information. Advanced operations require an existing Git project or caller-supplied JSON evidence as appropriate. A proposal is not a completed change: review the exact result, check the owner approval box where offered, and apply separately. The CLI remains the authoritative contract for required source layouts, evidence shapes and supported targets.

## Drafts, feedback and evidence files

Unsent fields, explicitly selected files and the latest review stay **in memory in this browser tab** while you navigate. They are not written to browser storage or synchronized. Closing/reloading the tab or choosing **Clear session drafts** removes them. Clearing drafts does not undo approved project writes or erase your system clipboard. A restored result is labeled as a previous review; it cannot restore approval authority. Preview again against current sources before approval.

Progress and errors appear next to the action you used. While an operation runs, controls are disabled to prevent duplicate submissions or changes to its inputs. Errors receive keyboard focus and an alert announcement. After an approval attempt fails, preview again rather than replaying the old approval. Results explain what the reported status means; exact hashes, paths and JSON remain available under **Advanced: exact result**.

Windows CRLF and LF documents are accepted without changing Unicode text or source line references. Bare carriage returns and embedded control characters are rejected. The local request limit remains 64 KB, with the existing per-document bounds; reduce selected content when a limit is reported.

**File format and example** offers downloadable JSON starting points for model metadata, readiness evidence, checkpoint specifications and external outcomes. They deliberately leave evidence unknown and approval references empty. Replace placeholders with actual externally checked facts; an example is never proof of approval, execution or correctness. Core validation still decides whether the supplied evidence is usable. Full schema editors, automatic evidence collection and provider queries are not part of this interface.

Portable handoff results show readable instructions with Copy alongside the downloadable packet. Checkpoint review explains missing approvals or stale sources without restarting an agent. Outcome comparison retains unknown measures, and saving a lesson proposal never changes runtime policy.

## Graphical coverage at the UI candidate revision

| Feature | VS Code workbench entry | Local UI entry | Shared operation / check |
| --- | --- | --- | --- |
| F01 intent preparation | Start → New task | Start → Prepare task | `optimize`; real Extension Host and browser prepare checks |
| F02 risk and approval boundaries | Task Review | Start → Review | shared preparation result; ready/clarification and high-risk regressions |
| F03 explainable routing | Delegate → Review a route | Delegation → Review a route | `route`; fallback browser check and CLI tests |
| F04 portable handoff | Delegate → Portable handoff / Codex dispatch | Delegation → Handoff / dispatch | `handoff prepare/dispatch`; digest and unsupported-target CLI checks |
| F05 Project Compass | Project → Review project direction | Project → Review direction | `compass`; explicit-source browser check and core tests |
| F06 status and decisions | Govern → Status / Decision | Governance → Status / Decision | `state`; preview, stale/replay approval tests |
| F07 scope guardrails | Govern → Scope amendment | Governance → Scope amendment | `state scope`; revision and approval tests |
| F08 requirement/readiness gates | Govern → Requirements and readiness | Governance → Readiness | `gates`; local UI HTTP and CLI contract tests |
| F09 checkpoints and recovery | Recover → Save / Review | Recovery → Save / Review | `checkpoint`; local UI HTTP and CLI contract tests |
| F10 outcomes and learning | Outcomes → Record / Compare / Learn | Outcomes → Record / Compare / Learn | `outcome`; local UI HTTP and CLI comparison tests |

The advanced screens are graphical entry points to existing contracts, not evidence collection automation. They do not fabricate outcomes, live model availability, approved decisions or Phase 8 observations. Caller-supplied evidence and approvals remain necessary. Codex dispatch is the only supported automatic target and requires its existing exact-packet approval; other targets use manual copy/export.

## Local security and limits

The server binds only to `127.0.0.1` on an ephemeral port. It requires its one-time launch URL, a session cookie, exact local Host and Origin, and a CSRF header for writes. CSP, no-store responses, request-size limits, named operations and explicit source selection prevent a general filesystem or command endpoint. Temporary evidence files are removed when the server stops. Run a separate instance for each local session; do not expose the loopback port through a proxy or network tunnel.

The UI uses no frontend framework or extra runtime dependency. Text is rendered as text, not HTML. Browser tests are developer checks and are not owner-led Phase 8 validation.

## Developer acceptance checks

Run `node tests/run_ui_browser.js` using Node 22+ and installed Edge/Chromium. It exercises all six sections through the real browser, with synthetic evidence and a disposable Git project for writes. It covers CRLF input, exact clipboard content, example/artifact downloads, stale approvals, draft/file retention, visible feedback, duplicate submission, reduced motion, themes and desktop/390px/320px layouts. Set `INTENTOS_UI_SCREENSHOTS_DIR` to an **external** directory for genuine screenshots. Keep the sensitive one-time launch URL out of logs and reports. These checks are not a full screen-reader audit or Phase 8 observations.

For real editor Webview checks, set `INTENTOS_VSCODE_UI_TEST=1` when running `node tests/run_vscode_extension_host.js` and its `--no-workspace` variant. This runs interaction assertions without requiring bitmap capture. `INTENTOS_VSCODE_SCREENSHOTS_DIR` enables the same interactions plus screenshots; screenshot transport failures fail that run explicitly. Test profiles, extension directories and process cleanup are isolated from the user's normal editor.
