# VS Code Dogfooding

This is the acceptance protocol for the first VS Code slice. It is intentionally manual and small: the goal is to validate the real Extension Development Host UX before adding more editor features.

## Prerequisite

The extension uses the repository-local virtual environment executable when the default `intentos` setting is in use:

- Windows: `.venv\Scripts\intentos.exe`
- POSIX: `.venv/bin/intentos`

If that executable is not present, install the current IntentOS package so `intentos` is available to the Extension Host:

```bash
python -m pip install -e .
```

To use a different CLI executable, set `IntentOS: Executable` (`intentos.executable`) to its command or full path.

## Launch

Open the IntentOS repository in desktop VS Code and press `F5` (or run **Debug: Start Debugging**). Choose:

`IntentOS: Run VS Code Extension`

VS Code should open a new Extension Development Host window with the repository workspace open and `integrations/vscode` loaded as the development extension. This uses the standard `--extensionDevelopmentPath` flow and does not require npm install or a build step.

In the Extension Development Host, open the Command Palette and run:

`IntentOS: Prepare Task`

## Acceptance cases

### 1. Ready / selected text

Put this text in an editor and select it:

```text
Codex: refactor the parser without changing behavior
```

Run `IntentOS: Prepare Task`.

Expected:

- no request input box because selected text is used
- a temporary `IntentOS Review` panel opens
- status is `Ready`
- interpretation preserves the request
- prepared task is visible
- `Copy Prepared Task` copies the prepared prompt
- Advanced details remain collapsed by default

### 2. Clarification

Run the command with no selected text and enter:

```text
Summarize this design
```

Expected:

- the review panel opens rather than showing an execution error
- status is `Needs clarification`
- clarification questions are visible
- no misleading ready state is shown

### 3. High-risk task

Run:

```text
Codex: deploy the authentication migration to production
```

Expected:

- the review panel opens
- risk is high
- consequential approval boundaries are visible without opening Advanced details
- the UI does not offer an Execute/Deploy action

### 4. Executable error

Temporarily set `intentos.executable` to a nonexistent command such as:

```text
intentos-does-not-exist
```

Run `IntentOS: Prepare Task` again.

Expected:

- no review panel is shown for the failed invocation
- a clear `IntentOS:` error notification is shown
- the error is not displayed as clarification

Restore `intentos.executable` afterwards.

## Pass gate

Phase 7B UX dogfooding passes when all four cases behave as expected in a real desktop VS Code Extension Development Host.

Do not add a sidebar, agent-specific execution bridge, automatic context discovery, or additional settings in response to preference alone. Promote only observed failures/friction into focused regressions or the smallest reversible UX change.

## Evidence to record

For each case, record only:

- pass/fail
- unexpected behavior, if any
- whether the default panel showed enough information to decide the next action

Screenshots are optional; no telemetry or automated capture is required.
