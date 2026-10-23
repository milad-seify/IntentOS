# IntentOS VS Code integration

This is the minimum Phase 7B editor surface. It remains a thin adapter over the existing IntentOS CLI/core.

## Current workflow

1. Install IntentOS so the `intentos` executable is available to VS Code.
2. Open this directory as an extension development host or install/package it with your normal VS Code extension workflow.
3. Run `IntentOS: Prepare Task` from the Command Palette.
4. If text is selected in the active editor, that selection is used as the request. Otherwise IntentOS asks for the request.
5. Review the temporary panel and choose **Copy Prepared Task** when ready.

The panel shows the interpretation, consequential risk/approval boundaries, selected context summary, verification criteria, and the prepared task. Advanced routing/context details stay collapsed by default.

## Configuration

`intentos.executable` defaults to `intentos`. Change it only when the executable is not on the extension host PATH, for example when using a specific virtual environment.

## Deliberate limits

This first slice does not add:

- a permanent sidebar or activity-bar view
- automatic filesystem/context discovery
- agent-specific send/execute actions
- model/provider configuration
- MCP client logic inside the extension
- background services or telemetry

The extension invokes `intentos optimize ... --json`, so task/risk/context/policy/routing behavior stays in the shared core rather than being reimplemented in JavaScript.
