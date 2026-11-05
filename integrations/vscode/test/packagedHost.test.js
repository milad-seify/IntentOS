const assert = require('assert');
const fs = require('fs');
const vscode = require('vscode');

async function run() {
  const resultFile = process.env.INTENTOS_EXTENSION_TEST_RESULT;
  try {
    const extension = vscode.extensions.getExtension('milad-seyfi.intentos-vscode');
    assert(extension, 'Installed VSIX extension was not discovered.');
    await extension.activate();
    assert(extension.isActive, 'Installed VSIX extension did not activate.');
    const commands = await vscode.commands.getCommands(true);
    assert(commands.includes('intentos.prepareTask'), 'Installed VSIX prepare command is missing.');
    assert(commands.includes('intentos.openWorkbench'), 'Installed VSIX workbench command is missing.');
    await vscode.commands.executeCommand('intentos.openWorkbench');
    for (let attempt = 0; attempt < 30; attempt += 1) {
      if (vscode.window.tabGroups.all.some((group) => group.tabs.some((tab) => tab.label === 'IntentOS Workbench'))) break;
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    assert(vscode.window.tabGroups.all.some((group) => group.tabs.some((tab) => tab.label === 'IntentOS Workbench')), 'Installed VSIX workbench did not open.');
    const result = { ok: true, mode: 'installed-vsix', extensionId: extension.id, extensionPath: extension.extensionUri.fsPath, workbench: 'opened' };
    fs.writeFileSync(resultFile, JSON.stringify(result));
    console.log(`INTENTOS_EXTENSION_HOST_TEST_RESULT=${JSON.stringify(result)}`);
    if (process.env.INTENTOS_EXTENSION_TEST_HOLD_MS) {
      await new Promise((resolve) => setTimeout(resolve, Number(process.env.INTENTOS_EXTENSION_TEST_HOLD_MS)));
    }
  } catch (error) {
    fs.writeFileSync(resultFile, JSON.stringify({ ok: false, error: error.stack || String(error) }));
    throw error;
  }
}

module.exports = { run };
