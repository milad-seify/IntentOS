# IntentOS VS Code integration

This is the minimum Phase 7B editor surface. It remains a thin adapter over the existing IntentOS CLI/core.

## Current workflow

The editable package installation below is for local extension development. IntentOS 1.0.0 is available on PyPI as `intentos-engineering`.

1. Install IntentOS from the repository root so the `intentos` executable is available to VS Code:

   ```bash
   python -m pip install -e .
   ```

2. Open the repository root in desktop VS Code and press `F5` (or run **Debug: Start Debugging**).
3. Choose `IntentOS: Run VS Code Extension`. The repository `.vscode/launch.json` opens a standard Extension Development Host with this directory loaded via `--extensionDevelopmentPath`.
4. In the Extension Development Host, run `IntentOS: Prepare Task` from the Command Palette.
5. If text is selected in the active editor, that selection is used as the request. Otherwise IntentOS asks for the request.
6. Review the temporary panel and choose **Copy Prepared Task** when ready.

The panel shows the interpretation, consequential risk/approval boundaries, selected context summary, verification criteria, and the prepared task. Advanced routing/context details stay collapsed by default.

See [`../../docs/VSCODE_DOGFOODING.md`](../../docs/VSCODE_DOGFOODING.md) for the four-case real-UI acceptance protocol.

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
