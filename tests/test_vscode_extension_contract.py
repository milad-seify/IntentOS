from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXTENSION_DIR = ROOT / "integrations" / "vscode"


class VSCodeExtensionContractTests(unittest.TestCase):
    def run_input_box_request(self, workspace: Path | None, executable: str, extension_path: Path) -> dict[str, str]:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is required to exercise the VS Code adapter")

        script = r"""
const Module = require('module');
const originalLoad = Module._load;
let command;
let observed;
const vscode = {
  window: {
    activeTextEditor: undefined,
    showInputBox: async () => 'Codex: refactor the parser without changing behavior',
    withProgress: async (_options, callback) => callback(),
    createWebviewPanel: () => ({ webview: { html: '', onDidReceiveMessage() {} } }),
    showErrorMessage: (message) => { throw new Error(message); },
  },
  workspace: {
    workspaceFolders: process.argv[2] === 'none' ? [] : [{ uri: { fsPath: process.argv[2] } }],
    getConfiguration: () => ({ get: () => process.argv[3] }),
  },
  commands: {
    registerCommand: (_id, callback) => { command = callback; return { dispose() {} }; },
  },
  ProgressLocation: { Notification: 1 },
  ViewColumn: { Beside: 2 },
};
Module._load = function (request, parent, isMain) {
  if (request === 'vscode') return vscode;
  if (request === 'child_process') {
    return { execFile: (executable, _args, options, callback) => {
      observed = { executable, cwd: options.cwd };
      callback(null, JSON.stringify({ status: 'ready' }), '');
    } };
  }
  return originalLoad.call(this, request, parent, isMain);
};
require(process.argv[1]).activate({ subscriptions: [], extensionUri: { fsPath: process.argv[4] } });
command().then(() => process.stdout.write(JSON.stringify(observed)))
  .catch((error) => { console.error(error); process.exitCode = 1; });
"""
        result = subprocess.run(
            [node, "-e", script, str(EXTENSION_DIR / "extension.js"), str(workspace) if workspace else "none", executable, str(extension_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def test_manifest_exposes_only_prepare_task_command(self) -> None:
        manifest = json.loads((EXTENSION_DIR / "package.json").read_text(encoding="utf-8"))

        commands = manifest["contributes"]["commands"]
        self.assertEqual(
            commands,
            [{"command": "intentos.prepareTask", "title": "IntentOS: Prepare Task"}],
        )
        self.assertNotIn("views", manifest["contributes"])
        self.assertNotIn("viewsContainers", manifest["contributes"])
        self.assertNotIn("dependencies", manifest)
        self.assertNotIn("devDependencies", manifest)

    def test_extension_stays_a_thin_cli_adapter(self) -> None:
        source = (EXTENSION_DIR / "extension.js").read_text(encoding="utf-8")

        self.assertIn("execFile", source)
        self.assertIn("['optimize', request, '--json']", source)
        self.assertIn("payload?.status === 'error'", source)
        self.assertIn("createWebviewPanel", source)
        self.assertIn("clipboard.writeText", source)
        self.assertNotIn("readFile", source)
        self.assertNotIn("workspace.fs", source)
        self.assertNotIn("mcp", source.lower())

    def test_default_cli_resolution_prefers_workspace_virtual_environment(self) -> None:
        source = (EXTENSION_DIR / "executable.js").read_text(encoding="utf-8")

        self.assertIn("function resolveExecutable(executable, cwd, extensionPath, platform = process.platform)", source)
        self.assertIn("function formatSpawnError(executable, cwd, error, stderr = '')", source)
        self.assertIn("platform === 'win32' ? 'Scripts' : 'bin'", source)
        self.assertIn("platform === 'win32' ? 'intentos.exe' : 'intentos'", source)
        self.assertIn("path.resolve(extensionPath, '..', '..')", source)
        self.assertIn("if (fs.existsSync(workspaceExecutable))", source)
        self.assertIn("if (fs.existsSync(developmentExecutable))", source)
        self.assertIn("cwd || '(none)'", source)
        self.assertIn("error ${error.code || 'unknown'}", source)

    def test_input_box_request_without_editor_uses_workspace_virtual_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "workspace"
            scripts = workspace / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
            scripts.mkdir(parents=True)
            local_executable = scripts / ("intentos.exe" if sys.platform == "win32" else "intentos")
            local_executable.touch()

            development_repository = Path(temp_dir) / "development-repository"
            extension_path = development_repository / "integrations" / "vscode"
            extension_path.mkdir(parents=True)
            development_scripts = development_repository / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
            development_scripts.mkdir(parents=True)
            (development_scripts / ("intentos.exe" if sys.platform == "win32" else "intentos")).touch()
            observed = self.run_input_box_request(workspace, "intentos", extension_path)

        self.assertEqual(observed["executable"], str(local_executable))
        self.assertEqual(observed["cwd"], str(workspace))

    def test_custom_executable_takes_precedence_over_workspace_virtual_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            scripts = workspace / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
            scripts.mkdir(parents=True)
            (scripts / ("intentos.exe" if sys.platform == "win32" else "intentos")).touch()

            extension_path = workspace / "integrations" / "vscode"
            extension_path.mkdir(parents=True)
            observed = self.run_input_box_request(workspace, "custom-intentos", extension_path)

        self.assertEqual(observed["executable"], "custom-intentos")
        self.assertEqual(observed["cwd"], str(workspace))

    def test_no_workspace_uses_development_repository_virtual_environment(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            extension_path = repository / "integrations" / "vscode"
            extension_path.mkdir(parents=True)
            scripts = repository / ".venv" / ("Scripts" if sys.platform == "win32" else "bin")
            scripts.mkdir(parents=True)
            local_executable = scripts / ("intentos.exe" if sys.platform == "win32" else "intentos")
            local_executable.touch()
            observed = self.run_input_box_request(None, "intentos", extension_path)

        self.assertEqual(observed["executable"], str(local_executable))
        self.assertNotIn("cwd", observed)

    def test_missing_workspace_and_development_virtual_environments_fall_back_to_intentos(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            extension_path = Path(temp_dir) / "integrations" / "vscode"
            extension_path.mkdir(parents=True)
            observed = self.run_input_box_request(None, "intentos", extension_path)

        self.assertEqual(observed["executable"], "intentos")
        self.assertNotIn("cwd", observed)

    def test_repository_launch_config_runs_only_the_development_extension(self) -> None:
        launch = json.loads((ROOT / ".vscode" / "launch.json").read_text(encoding="utf-8"))

        self.assertEqual(len(launch["configurations"]), 1)
        config = launch["configurations"][0]
        self.assertEqual(config["type"], "extensionHost")
        self.assertEqual(config["request"], "launch")
        self.assertEqual(config["runtimeExecutable"], "${execPath}")
        self.assertEqual(
            config["args"],
            [
                "--extensionDevelopmentPath=${workspaceFolder}/integrations/vscode",
                "--disable-extension=pflannery.vscode-versionlens",
                "${workspaceFolder}",
            ],
        )
        self.assertNotIn("preLaunchTask", config)


if __name__ == "__main__":
    unittest.main()
