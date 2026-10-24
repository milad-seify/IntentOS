const assert = require('assert');
const { execFile } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const vscode = require('vscode');
const { workspaceCwd, localExecutablePath, resolveExecutable, formatSpawnError } = require('../executable');

const extensionId = 'milad-seify.intentos-vscode';
const request = 'Codex: refactor the parser without changing behavior';

function normalizedPath(value) {
  const normalized = path.resolve(value);
  return process.platform === 'win32' ? normalized.toLowerCase() : normalized;
}

function writeResult(result) {
  const resultPath = process.env.INTENTOS_EXTENSION_TEST_RESULT;
  if (resultPath) {
    fs.writeFileSync(resultPath, JSON.stringify(result, null, 2));
  }
}

function runExecutable(executable, cwd) {
  return new Promise((resolve, reject) => {
    execFile(
      executable,
      ['optimize', request, '--json'],
      { cwd, windowsHide: true, maxBuffer: 2 * 1024 * 1024 },
      (error, stdout, stderr) => {
        if (error) {
          reject(
            new Error(
              formatSpawnError(executable, cwd, error, stderr)
            )
          );
          return;
        }
        resolve(stdout);
      }
    );
  });
}

async function run() {
  try {
    const repository = fs.realpathSync(path.resolve(__dirname, '..', '..', '..'));
    const folders = vscode.workspace.workspaceFolders || [];
    const folderPaths = folders.map((folder) => folder.uri.fsPath);
    assert(folders.length > 0, 'The Extension Host has no workspace folders.');
    assert(
      folderPaths.some((folder) => normalizedPath(folder) === normalizedPath(repository)),
      `The IntentOS repository is not open. Workspace folders: ${JSON.stringify(folderPaths)}`
    );

    const extension = vscode.extensions.getExtension(extensionId);
    assert(extension, `Development extension ${extensionId} is not present.`);
    await extension.activate();
    assert.strictEqual(extension.isActive, true, `${extensionId} did not activate.`);

    assert.strictEqual(typeof workspaceCwd, 'function', 'Production workspace resolver is unavailable.');
    assert.strictEqual(typeof resolveExecutable, 'function', 'Production executable resolver is unavailable.');

    const cwd = workspaceCwd(vscode, null);
    assert.strictEqual(
      normalizedPath(cwd),
      normalizedPath(repository),
      'No active editor should resolve to the repository workspace folder.'
    );

    const noWorkspaceApi = {
      window: { activeTextEditor: undefined },
      workspace: { workspaceFolders: [] },
    };
    const missingWorkspaceCwd = workspaceCwd(noWorkspaceApi, null);
    assert.strictEqual(missingWorkspaceCwd, undefined);
    const missingWorkspaceExecutable = resolveExecutable('intentos', missingWorkspaceCwd);
    assert.strictEqual(missingWorkspaceExecutable, 'intentos');

    const configuredExecutable = vscode.workspace
      .getConfiguration('intentos')
      .get('executable', 'intentos');
    assert.strictEqual(configuredExecutable, 'intentos', 'The isolated profile must use the default executable setting.');

    assert.strictEqual(
      localExecutablePath(repository, 'win32'),
      path.join(repository, '.venv', 'Scripts', 'intentos.exe'),
      'Windows local executable path is incorrect.'
    );
    assert.strictEqual(
      localExecutablePath(repository, 'linux'),
      path.join(repository, '.venv', 'bin', 'intentos'),
      'POSIX local executable path is incorrect.'
    );

    const executable = resolveExecutable(configuredExecutable, cwd);
    const expectedExecutable = localExecutablePath(repository, process.platform);
    assert.strictEqual(
      normalizedPath(executable),
      normalizedPath(expectedExecutable),
      `Production resolver selected "${executable}" instead of "${expectedExecutable}".`
    );
    assert(fs.existsSync(executable), `Resolved executable does not exist: ${executable}`);

    const customExecutable = 'custom-intentos-command';
    assert.strictEqual(
      resolveExecutable(customExecutable, repository),
      customExecutable,
      'A configured custom executable must take precedence.'
    );

    const emptyWorkspace = fs.mkdtempSync(path.join(os.tmpdir(), 'intentos-no-venv-'));
    try {
      assert.strictEqual(
        resolveExecutable('intentos', emptyWorkspace),
        'intentos',
        'Missing local virtual environment must fall back to intentos.'
      );
    } finally {
      fs.rmSync(emptyWorkspace, { recursive: true, force: true });
    }

    const stdout = await runExecutable(executable, cwd);
    const payload = JSON.parse(stdout);
    assert.strictEqual(payload.status, 'ready', `IntentOS returned status ${payload.status}.`);

    let missingWorkspaceEnoent = false;
    let missingWorkspaceSpawnError;
    try {
      await runExecutable(missingWorkspaceExecutable, missingWorkspaceCwd);
    } catch (error) {
      if (!String(error.message).includes('ENOENT')) throw error;
      assert.match(
        error.message,
        /executable "intentos" from workspace "\(none\)" \(error ENOENT\)/,
        'Spawn failures should identify the executable, workspace, and original error code.'
      );
      missingWorkspaceEnoent = true;
      missingWorkspaceSpawnError = error.message;
      console.log(`Missing-workspace control reproduced expected ENOENT: ${error.message}`);
    }

    const result = {
      ok: true,
      repository,
      workspaceFolders: folderPaths,
      extensionId: extension.id,
      executable,
      cwd,
      status: payload.status,
      missingWorkspaceEnoent,
      missingWorkspaceSpawnError,
    };
    writeResult(result);
    console.log(`INTENTOS_EXTENSION_HOST_TEST_RESULT=${JSON.stringify(result)}`);
  } catch (error) {
    writeResult({ ok: false, error: error.stack || String(error) });
    console.error(error.stack || error);
    throw error;
  }
}

module.exports = { run };
