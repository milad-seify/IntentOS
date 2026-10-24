const fs = require('fs');
const path = require('path');

function workspaceCwd(vscode, editor = vscode.window.activeTextEditor) {
  if (!editor) {
    return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
  }
  const folder = vscode.workspace.getWorkspaceFolder(editor.document.uri);
  return folder?.uri.fsPath || vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
}

function localExecutablePath(cwd, platform = process.platform) {
  if (!cwd) {
    return undefined;
  }
  return path.join(
    cwd,
    '.venv',
    platform === 'win32' ? 'Scripts' : 'bin',
    platform === 'win32' ? 'intentos.exe' : 'intentos'
  );
}

function resolveExecutable(executable, cwd, extensionPath, platform = process.platform) {
  if (executable !== 'intentos') {
    return executable;
  }
  if (cwd) {
    const workspaceExecutable = localExecutablePath(cwd, platform);
    if (fs.existsSync(workspaceExecutable)) {
      return workspaceExecutable;
    }
  }
  if (extensionPath) {
    const developmentRepository = path.resolve(extensionPath, '..', '..');
    const developmentExecutable = localExecutablePath(developmentRepository, platform);
    if (fs.existsSync(developmentExecutable)) {
      return developmentExecutable;
    }
  }
  return executable;
}

function formatSpawnError(executable, cwd, error, stderr = '') {
  const detail = (stderr || error.message || '').trim();
  return (
    `Could not spawn IntentOS executable "${executable}" from workspace "${cwd || '(none)'}" ` +
    `(error ${error.code || 'unknown'}): ${detail || 'No additional error details.'}`
  );
}

module.exports = { workspaceCwd, localExecutablePath, resolveExecutable, formatSpawnError };
