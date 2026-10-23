from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXTENSION_DIR = ROOT / "integrations" / "vscode"


class VSCodeExtensionContractTests(unittest.TestCase):
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
        source = (EXTENSION_DIR / "extension.js").read_text(encoding="utf-8")

        self.assertIn("function resolveExecutable(executable, cwd)", source)
        self.assertIn("process.platform === 'win32' ? 'Scripts' : 'bin'", source)
        self.assertIn("process.platform === 'win32' ? 'intentos.exe' : 'intentos'", source)
        self.assertIn("fs.existsSync(localExecutable) ? localExecutable : executable", source)

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
            ],
        )
        self.assertNotIn("preLaunchTask", config)


if __name__ == "__main__":
    unittest.main()
