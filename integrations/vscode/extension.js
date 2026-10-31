const vscode = require('vscode');
const { execFile } = require('child_process');
const { randomBytes } = require('crypto');
const { workspaceCwd, resolveExecutable, formatSpawnError } = require('./executable');

function selectedRequest() {
  const editor = vscode.window.activeTextEditor;
  if (!editor || editor.selection.isEmpty) {
    return '';
  }
  return editor.document.getText(editor.selection);
}

function runIntentOS(request, extensionPath) {
  const configuredExecutable = vscode.workspace
    .getConfiguration('intentos')
    .get('executable', 'intentos');
  const cwd = workspaceCwd(vscode);
  const executable = resolveExecutable(configuredExecutable, cwd, extensionPath);

  return new Promise((resolve, reject) => {
    execFile(
      executable,
      ['optimize', request, '--json'],
      {
        cwd,
        windowsHide: true,
        maxBuffer: 2 * 1024 * 1024,
      },
      (error, stdout, stderr) => {
        if (error && error.code !== 2) {
          reject(new Error(formatSpawnError(executable, cwd, error, stderr)));
          return;
        }

        try {
          const payload = JSON.parse(stdout);
          if (payload?.status === 'error') {
            reject(new Error(payload.error?.message || 'IntentOS returned an error.'));
            return;
          }
          resolve(payload);
        } catch (parseError) {
          reject(
            new Error(
              `IntentOS returned invalid JSON: ${parseError.message}`
            )
          );
        }
      }
    );
  });
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function listHtml(items, emptyText = 'None') {
  if (!Array.isArray(items) || items.length === 0) {
    return `<p class="muted">${escapeHtml(emptyText)}</p>`;
  }
  return `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
}

function renderReview(payload) {
  const nonce = randomBytes(16).toString('hex');
  const ready = payload.status === 'ready';
  const intent = payload.intent || {};
  const routing = payload.routing || {};
  const context = payload.context || {};
  const prompt = payload.prompt || '';
  const questions = payload.questions || [];
  const approvals = payload.approval_boundaries || [];
  const doneCriteria = payload.done_criteria || [];
  const selectedPaths = context.selected_paths || [];

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}';">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); padding: 20px; max-width: 980px; }
    h1 { font-size: 20px; margin: 0 0 18px; }
    h2 { font-size: 14px; margin-top: 22px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }
    .card { border: 1px solid var(--vscode-panel-border); border-radius: 6px; padding: 10px 12px; }
    .label { color: var(--vscode-descriptionForeground); font-size: 12px; margin-bottom: 4px; }
    .value { font-weight: 600; }
    .muted { color: var(--vscode-descriptionForeground); }
    pre { white-space: pre-wrap; word-break: break-word; background: var(--vscode-textCodeBlock-background); padding: 12px; border-radius: 6px; }
    button { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 8px 12px; border-radius: 3px; cursor: pointer; }
    button:hover { background: var(--vscode-button-hoverBackground); }
    button:disabled { opacity: .55; cursor: default; }
    details { margin-top: 18px; }
    code { font-family: var(--vscode-editor-font-family); }
  </style>
</head>
<body>
  <h1>IntentOS Review</h1>

  <div class="grid">
    <div class="card"><div class="label">Status</div><div class="value">${ready ? 'Ready' : 'Needs clarification'}</div></div>
    <div class="card"><div class="label">Risk</div><div class="value">${escapeHtml(payload.risk_level || '—')}</div></div>
    <div class="card"><div class="label">Target</div><div class="value">${escapeHtml(intent.target_tool || '—')}</div></div>
  </div>

  <h2>Interpretation</h2>
  <p>${escapeHtml(intent.goal || '')}</p>

  ${questions.length ? `<h2>Clarification</h2>${listHtml(questions)}` : ''}

  <h2>Approval boundaries</h2>
  ${listHtml(approvals, 'No consequential approval boundary for this task.')}

  <h2>Context</h2>
  ${listHtml(selectedPaths, 'No project context selected.')}

  <h2>Verification</h2>
  ${listHtml(doneCriteria, 'No additional verification criteria.')}

  <h2>Prepared task</h2>
  <button id="copy" ${prompt ? '' : 'disabled'}>Copy Prepared Task</button>
  <pre>${escapeHtml(prompt || 'No prepared prompt until clarification is resolved.')}</pre>

  <details>
    <summary>Advanced details</summary>
    <pre>${escapeHtml(JSON.stringify({
      task_type: payload.task_type,
      routing,
      context,
      engineering_rules: payload.engineering_rules || [],
    }, null, 2))}</pre>
  </details>

  <script nonce="${nonce}">
    const vscode = acquireVsCodeApi();
    document.getElementById('copy').addEventListener('click', () => {
      vscode.postMessage({ type: 'copyPreparedTask' });
    });
  </script>
</body>
</html>`;
}

function showReviewPanel(payload) {
  const panel = vscode.window.createWebviewPanel(
    'intentos.review',
    'IntentOS Review',
    vscode.ViewColumn.Beside,
    { enableScripts: true }
  );

  panel.webview.html = renderReview(payload);
  panel.webview.onDidReceiveMessage(async (message) => {
    if (message?.type !== 'copyPreparedTask' || !payload.prompt) {
      return;
    }
    await vscode.env.clipboard.writeText(payload.prompt);
    void vscode.window.showInformationMessage('IntentOS prepared task copied.');
  });
}

async function prepareTask(extensionPath) {
  let request = selectedRequest();
  if (!request.trim()) {
    request = await vscode.window.showInputBox({
      title: 'IntentOS: Prepare Task',
      prompt: 'Describe the outcome you want. Name the target tool if it is not obvious.',
      placeHolder: 'Codex: refactor the parser without changing behavior',
      ignoreFocusOut: true,
    });
  }

  if (!request || !request.trim()) {
    return;
  }

  try {
    const payload = await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'IntentOS: preparing task…',
        cancellable: false,
      },
      () => runIntentOS(request, extensionPath)
    );
    showReviewPanel(payload);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    void vscode.window.showErrorMessage(`IntentOS: ${message}`);
  }
}

function activate(context) {
  const extensionPath = context.extensionUri.fsPath;
  context.subscriptions.push(
    vscode.commands.registerCommand('intentos.prepareTask', () => prepareTask(extensionPath))
  );

  const launcher = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  launcher.text = '$(sparkle) IntentOS';
  launcher.tooltip = 'Prepare a task with IntentOS';
  launcher.command = 'intentos.prepareTask';
  launcher.show();
  context.subscriptions.push(launcher);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
