# Local Simple UI (development candidate)

The source candidate includes a local browser interface. It is not in the published Core `1.0.1` package. Install the candidate in a clean environment, then run `intentos ui`. The command opens a one-time URL in your browser; `intentos ui --no-browser` prints that URL for an explicit local open. Keep the terminal running while using the UI, and press Ctrl+C to stop it. No cloud account, provider key or VS Code installation is needed for basic task preparation.

## First use

1. On **Start**, describe the outcome. Optionally choose an AI tool and specific project documents; no files are scanned automatically.
2. Choose **Prepare task**. If clarification is needed, revise the task and retry.
3. Review the interpreted goal, risk, approval boundaries, context/provenance, verification and prepared instructions. **Ready** means ready for handoff, not that the task is complete.
4. Choose **Copy Prepared Task**, then paste it into your own AI tool. Copy is explicit; IntentOS does not send or execute the task in this basic flow.

The navigation offers **Project**, **Governance**, **Delegation**, **Recovery** and **Outcomes**. Project Compass reads only the documents you select and shows missing, stale or conflicting information. Advanced operations require an existing Git project or caller-supplied JSON evidence as appropriate. A proposal is not a completed change: review the exact result, check the owner approval box where offered, and apply separately. The CLI remains the authoritative contract for required source layouts, evidence shapes and supported targets.

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
