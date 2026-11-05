const vscode = require('vscode');
const { execFile } = require('child_process');
const { randomBytes } = require('crypto');
const { workspaceCwd, resolveExecutable, formatSpawnError } = require('./executable');
const { sidebarHtml, workbenchHtml } = require('./workbench');

let workbenchPanel;
let lastTextEditor;

function selectedRequest() {
  for (const editor of [vscode.window.activeTextEditor, lastTextEditor]) {
    if (editor && !editor.selection.isEmpty) {
      return editor.document.getText(editor.selection);
    }
  }
  return '';
}

function runIntentOS(request, extensionPath, options = {}) {
  const configuredExecutable = vscode.workspace
    .getConfiguration('intentos')
    .get('executable', 'intentos');
  const cwd = workspaceCwd(vscode);
  const executable = resolveExecutable(configuredExecutable, cwd, extensionPath);

  return new Promise((resolve, reject) => {
    const args = ['optimize', request, '--json'];
    if (options.target) args.push('--target', options.target);
    if (options.contextFile) args.push('--context-file', options.contextFile);
    execFile(
      executable,
      args,
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

function runCli(args, extensionPath, json = true) {
  const configured = vscode.workspace.getConfiguration('intentos').get('executable', 'intentos');
  const cwd = workspaceCwd(vscode);
  const executable = resolveExecutable(configured, cwd, extensionPath);
  return new Promise((resolve, reject) => {
    execFile(executable, json ? [...args, '--json'] : args, {
      cwd, windowsHide: true, maxBuffer: 2 * 1024 * 1024,
    }, (error, stdout, stderr) => {
      if (error && error.code !== 2) {
        reject(new Error(formatSpawnError(executable, cwd, error, stderr)));
        return;
      }
      if (!json) { resolve(stdout); return; }
      try {
        const payload = JSON.parse(stdout);
        if (payload?.status === 'error') throw new Error(payload.error?.message || 'IntentOS returned an error.');
        resolve(payload);
      } catch (parseError) { reject(parseError); }
    });
  });
}

const actionFields = {
  prepare: ['text', 'target', 'context_file'],
  compass: ['authoritative_document', 'document', 'task'],
  stateStatus: ['current_phase', 'next_action', 'evidence'],
  stateDecision: ['decision_id', 'title', 'body', 'approval_ref'],
  stateScope: ['amendment_id', 'task', 'reason', 'approval_ref'],
  gates: ['file'], route: ['text', 'target', 'models_file'],
  handoffPrepare: ['text', 'target', 'task_id', 'context_file', 'output'],
  handoffDispatch: ['file', 'sandbox', 'model'],
  checkpointCreate: ['spec', 'context_file', 'output'],
  checkpointReview: ['checkpoint', 'context_file', 'ledger_reviewed', 'executed_operation', 'accepted_approval', 'remaining_budget_tokens'],
  outcomeRecord: ['file', 'output'], outcomeCompare: ['raw', 'prepared'],
  outcomeLearn: ['record1', 'record2', 'approval_ref', 'output'],
};
const fileFields = new Set(['context_file', 'authoritative_document', 'document', 'file', 'models_file', 'spec', 'output', 'checkpoint', 'raw', 'prepared', 'record1', 'record2']);
const saveActions = new Set(['handoffPrepare-output', 'checkpointCreate-output', 'outcomeRecord-output', 'outcomeLearn-output']);
const projectActions = new Set(['stateStatus', 'stateDecision', 'stateScope', 'handoffPrepare', 'handoffDispatch', 'checkpointCreate', 'checkpointReview']);

function validatedFields(action, supplied, selectedFiles) {
  const allowed = Object.hasOwn(actionFields, action) ? actionFields[action] : undefined;
  if (!allowed || !supplied || typeof supplied !== 'object' || Array.isArray(supplied)) throw new Error('Unsupported workbench action.');
  if (Object.keys(supplied).some((name) => !allowed.includes(name))) throw new Error('Unexpected workbench field.');
  const fields = {};
  for (const name of allowed) {
    const value = supplied[name];
    if (name === 'ledger_reviewed') {
      if (typeof value !== 'boolean') throw new Error('Review confirmation must be true or false.');
      fields[name] = value;
    } else if (typeof value !== 'string' || value.length > 36000 || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(value)) {
      throw new Error('A workbench field is invalid or too long.');
    } else if (fileFields.has(name)) {
      if (value && selectedFiles.get(`${action}-${name}`) !== value) throw new Error('Choose files with the file picker.');
      fields[name] = value;
    } else fields[name] = value.trim();
  }
  return fields;
}

function required(value, label) {
  if (!value) throw new Error(`${label} is required.`);
  return value;
}

function projectRoot(action) {
  const root = workspaceCwd(vscode);
  if (projectActions.has(action) && !root) throw new Error('Open a Git project workspace to use this project workflow. Task preparation works without a workspace.');
  return root;
}

function commandFor(action, fields, root) {
  switch (action) {
    case 'compass': {
      if (!fields.authoritative_document && !fields.document) throw new Error('Choose at least one project source.');
      return ['compass', ...(fields.authoritative_document ? ['--authoritative-document', fields.authoritative_document] : []), ...(fields.document ? ['--document', fields.document] : []), ...(fields.task ? ['--task', fields.task] : [])];
    }
    case 'stateStatus': return ['state', 'status', '--root', root, '--current-phase', required(fields.current_phase, 'Current phase'), '--next-action', required(fields.next_action, 'Next action'), '--evidence', required(fields.evidence, 'Evidence reference')];
    case 'stateDecision': return ['state', 'decision', '--root', root, '--decision-id', required(fields.decision_id, 'Decision ID'), '--title', required(fields.title, 'Title'), '--body', required(fields.body, 'Decision text'), '--approval-ref', required(fields.approval_ref, 'Approval reference')];
    case 'stateScope': return ['state', 'scope', '--root', root, '--amendment-id', required(fields.amendment_id, 'Amendment ID'), '--task', required(fields.task, 'Task'), '--reason', required(fields.reason, 'Reason'), '--approval-ref', required(fields.approval_ref, 'Approval reference')];
    case 'gates': return ['gates', '--file', required(fields.file, 'Evidence file')];
    case 'route': return ['route', required(fields.text, 'Task'), ...(fields.target ? ['--target', fields.target] : []), ...(fields.models_file ? ['--models-file', fields.models_file] : [])];
    case 'handoffPrepare': return ['handoff', 'prepare', required(fields.text, 'Task'), '--root', root, '--target', required(fields.target, 'Agent'), '--task-id', required(fields.task_id, 'Task ID'), '--output', required(fields.output, 'Output file'), ...(fields.context_file ? ['--context-file', fields.context_file] : [])];
    case 'handoffDispatch': return ['handoff', 'dispatch', '--root', root, '--file', required(fields.file, 'Handoff packet'), '--sandbox', fields.sandbox === 'workspace-write' ? 'workspace-write' : 'read-only', ...(fields.model ? ['--model', fields.model] : [])];
    case 'checkpointCreate': return ['checkpoint', 'create', '--root', root, '--spec', required(fields.spec, 'Checkpoint specification'), '--context-file', required(fields.context_file, 'Context file'), '--output', required(fields.output, 'Output file')];
    case 'checkpointReview': return ['checkpoint', 'review', '--root', root, '--checkpoint', required(fields.checkpoint, 'Checkpoint file'), '--context-file', required(fields.context_file, 'Context file'), ...(fields.ledger_reviewed ? ['--ledger-reviewed'] : []), ...(fields.executed_operation ? ['--executed-operation', fields.executed_operation] : []), ...(fields.accepted_approval ? ['--accepted-approval', fields.accepted_approval] : []), ...(fields.remaining_budget_tokens ? ['--remaining-budget-tokens', fields.remaining_budget_tokens] : [])];
    case 'outcomeRecord': return ['outcome', 'record', '--file', required(fields.file, 'Outcome evidence'), '--output', required(fields.output, 'Output file')];
    case 'outcomeCompare': return ['outcome', 'compare', '--raw', required(fields.raw, 'Raw record'), '--prepared', required(fields.prepared, 'Prepared record')];
    case 'outcomeLearn': return ['outcome', 'learn', '--record', required(fields.record1, 'First record'), '--record', required(fields.record2, 'Second record')];
    default: throw new Error('Unsupported workbench action.');
  }
}

function openWorkbench(extensionPath) {
  if (workbenchPanel) { workbenchPanel.reveal(vscode.ViewColumn.One); return; }
  const panel = vscode.window.createWebviewPanel('intentos.workbench', 'IntentOS Workbench', vscode.ViewColumn.One, { enableScripts: true, retainContextWhenHidden: true });
  workbenchPanel = panel;
  panel.onDidDispose?.(() => { if (workbenchPanel === panel) workbenchPanel = undefined; });
  panel.webview.html = workbenchHtml();
  const selectedFiles = new Map();
  let pending;
  let latestPrompt;
  let latestRequest;
  panel.webview.onDidReceiveMessage(async (message) => {
    if (!message || typeof message !== 'object' || Array.isArray(message)) return;
    try {
      if (message.type === 'pickFile') {
        const field = message.field;
        if (typeof field !== 'string' || !/^[A-Za-z]+-[a-z_0-9]+$/.test(field)) return;
        const split = field.indexOf('-');
        const action = field.slice(0, split), name = field.slice(split + 1);
        if (!actionFields[action]?.includes(name) || !fileFields.has(name) || Boolean(message.save) !== saveActions.has(field)) return;
        const uri = message.save
          ? await vscode.window.showSaveDialog({ filters: { 'JSON files': ['json'] } })
          : (await vscode.window.showOpenDialog({ canSelectFiles: true, canSelectFolders: false, canSelectMany: false }))?.[0];
        if (!uri) return;
        selectedFiles.set(field, uri.fsPath);
        await panel.webview.postMessage({ type: 'picked', field, path: uri.fsPath });
        return;
      }
      if (message.type === 'useSelection') {
        await panel.webview.postMessage({ type: 'selection', text: selectedRequest() });
        return;
      }
      if (message.type === 'copyPreparedTask') {
        if (!latestPrompt) return;
        await vscode.env.clipboard.writeText(latestPrompt);
        void vscode.window.showInformationMessage('IntentOS prepared task copied.');
        return;
      }
      if (message.type === 'retry') {
        if (!latestRequest) return;
        const revised = await vscode.window.showInputBox({ title: 'Answer clarification and retry', prompt: 'Revise the task to answer the questions shown in Review.', value: latestRequest, ignoreFocusOut: true });
        if (!revised?.trim()) return;
        latestRequest = revised;
        const payload = await runIntentOS(revised, extensionPath);
        latestPrompt = payload.prompt || undefined;
        await panel.webview.postMessage({ type: 'result', action: 'prepare', payload });
        return;
      }
      if (message.type === 'apply') {
        if (!pending) return;
        const candidate = pending;
        pending = undefined;
        const prompt = candidate.action === 'handoffDispatch'
          ? 'Dispatch this exact reviewed packet to Codex? Completion will still need verification.'
          : candidate.action === 'outcomeLearn'
            ? 'Save this exact reviewed learning proposal? Runtime policy will not change.'
            : 'Apply this exact reviewed project update?';
        const answer = await vscode.window.showWarningMessage(prompt, { modal: true }, 'Approve exact change');
        if (answer !== 'Approve exact change') return;
        const approvalArgs = candidate.action === 'outcomeLearn'
          ? ['--approval-ref', candidate.approvalRef, '--output', candidate.output]
          : [];
        const payload = await runCli([...candidate.args, '--approve-digest', candidate.digest, ...approvalArgs], extensionPath);
        await panel.webview.postMessage({ type: 'result', action: candidate.action, payload });
        return;
      }
      if (message.type !== 'run' || typeof message.action !== 'string') return;
      pending = undefined;
      const action = message.action;
      const fields = validatedFields(action, message.fields, selectedFiles);
      const root = projectRoot(action);
      if (action === 'prepare') {
        latestRequest = required(fields.text, 'Task');
        const payload = await runIntentOS(latestRequest, extensionPath, { target: fields.target, contextFile: fields.context_file });
        latestPrompt = payload.prompt || undefined;
        await panel.webview.postMessage({ type: 'result', action, payload });
        return;
      }
      const args = commandFor(action, fields, root);
      const payload = await runCli(args, extensionPath);
      if (action.startsWith('state') && payload.approval_digest) {
        payload.diff_preview = await runCli(args, extensionPath, false);
      }
      if ((action.startsWith('state') || action === 'handoffDispatch' || action === 'outcomeLearn') && payload.approval_digest) {
        pending = { action, args, digest: payload.approval_digest,
          ...(action === 'outcomeLearn' ? { approvalRef: required(fields.approval_ref, 'Owner approval reference'), output: required(fields.output, 'Output file') } : {}) };
        payload.next_action = 'Review the exact proposal, then explicitly approve it in this workbench.';
      }
      await panel.webview.postMessage({ type: 'result', action, payload });
    } catch (error) {
      const detail = error instanceof Error ? error.message : 'Unknown error';
      const hint = detail.includes('ENOENT') ? ' Install the local IntentOS CLI, or set intentos.executable to its full path in VS Code settings.' : '';
      await panel.webview.postMessage({ type: 'error', message: `IntentOS: ${detail}${hint}` });
    }
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
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'nonce-${nonce}'; script-src 'nonce-${nonce}';">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style nonce="${nonce}">
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
  ${questions.length ? '<button id="retry">Answer and retry</button>' : ''}

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
    document.getElementById('retry')?.addEventListener('click', () => {
      vscode.postMessage({ type: 'retryClarification' });
    });
  </script>
</body>
</html>`;
}

function showReviewPanel(initialPayload, initialRequest, extensionPath) {
  let payload = initialPayload;
  let request = initialRequest;
  const panel = vscode.window.createWebviewPanel(
    'intentos.review',
    'IntentOS Review',
    vscode.ViewColumn.Beside,
    { enableScripts: true }
  );

  panel.webview.html = renderReview(payload);
  panel.webview.onDidReceiveMessage(async (message) => {
    if (message?.type === 'retryClarification' && payload.needs_clarification) {
      const revised = await vscode.window.showInputBox({
        title: 'Answer clarification and retry',
        prompt: 'Revise the task to answer the questions shown in Review.',
        value: request,
        ignoreFocusOut: true,
      });
      if (!revised?.trim()) return;
      try {
        const next = await runIntentOS(revised, extensionPath);
        request = revised;
        payload = next;
        panel.webview.html = renderReview(next);
      } catch (error) {
        void vscode.window.showErrorMessage(`IntentOS: ${error instanceof Error ? error.message : String(error)}`);
      }
      return;
    }
    if (message?.type !== 'copyPreparedTask' || !payload.prompt) return;
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
    showReviewPanel(payload, request, extensionPath);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    void vscode.window.showErrorMessage(`IntentOS: ${message}`);
  }
}

function activate(context) {
  const extensionPath = context.extensionUri.fsPath;
  lastTextEditor = vscode.window.activeTextEditor;
  if (vscode.window.onDidChangeActiveTextEditor) {
    context.subscriptions.push(vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) lastTextEditor = editor;
    }));
  }
  if (vscode.workspace?.onDidCloseTextDocument) {
    context.subscriptions.push(vscode.workspace.onDidCloseTextDocument((document) => {
      if (lastTextEditor?.document === document) lastTextEditor = undefined;
    }));
  }
  context.subscriptions.push(
    vscode.commands.registerCommand('intentos.prepareTask', () => prepareTask(extensionPath))
  );
  context.subscriptions.push(
    vscode.commands.registerCommand('intentos.openWorkbench', () => openWorkbench(extensionPath))
  );
  if (vscode.window.registerWebviewViewProvider) {
    context.subscriptions.push(vscode.window.registerWebviewViewProvider('intentos.start', {
      resolveWebviewView(view) {
        view.webview.options = { enableScripts: true };
        view.webview.html = sidebarHtml();
        view.webview.onDidReceiveMessage((message) => {
          if (message?.type === 'open') openWorkbench(extensionPath);
          if (message?.type === 'selection') {
            const request = selectedRequest();
            if (request) void prepareTask(extensionPath);
            else openWorkbench(extensionPath);
          }
        });
      },
    }));
  }

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
