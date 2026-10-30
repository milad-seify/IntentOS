"""Validate the identity and contents of a tagged VS Code Marketplace VSIX."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import sys
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "integrations" / "vscode" / "package.json"
EXPECTED_PUBLISHER = "milad-seify"
EXPECTED_NAME = "intentos-vscode"
REQUIRED_FILES = {
    "extension/changelog.md",
    "extension/license.txt",
    "extension/readme.md",
    "extension/executable.js",
    "extension/extension.js",
    "extension/package.json",
}
ALLOWED_FILES = REQUIRED_FILES | {"[content_types].xml", "extension.vsixmanifest"}


def validate(tag: str, vsix_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    match = re.fullmatch(r"vscode-v(\d+\.\d+\.\d+)", tag)
    if not match:
        raise ValueError(f"Unexpected Marketplace release tag: {tag}")
    if (manifest.get("publisher"), manifest.get("name")) != (
        EXPECTED_PUBLISHER,
        EXPECTED_NAME,
    ):
        raise ValueError("The VS Code extension identity does not match the release identity")
    if manifest.get("version") != match.group(1):
        raise ValueError("Marketplace release tag version does not match package.json")
    if vsix_path.name != f"{EXPECTED_NAME}-{match.group(1)}.vsix":
        raise ValueError("VSIX filename does not match the extension identity and version")

    with zipfile.ZipFile(vsix_path) as package:
        files = {name.lower(): name for name in package.namelist() if not name.endswith("/")}
        missing = REQUIRED_FILES - files.keys()
        if missing:
            raise ValueError(f"VSIX is missing required files: {sorted(missing)}")
        for name in files.values():
            item = PurePosixPath(name)
            if item.is_absolute() or ".." in item.parts:
                raise ValueError(f"Unsafe path in VSIX: {name}")
            lowered = name.lower()
            if (
                lowered.startswith(("extension/test/", "extension/tests/"))
                or "__pycache__" in item.parts
                or lowered.endswith((".pyc", ".pyo"))
                or item.name.lower() == ".env"
                or item.name.lower().startswith(".env.")
                or "node_modules" in item.parts
                or lowered.endswith(".vsix")
            ):
                raise ValueError(f"Unexpected development or sensitive file in VSIX: {name}")
        unexpected = files.keys() - ALLOWED_FILES
        if unexpected:
            raise ValueError(f"Unexpected files in VSIX: {sorted(unexpected)}")

        packaged_manifest = json.loads(package.read(files["extension/package.json"]))
        if (
            packaged_manifest.get("publisher"),
            packaged_manifest.get("name"),
            packaged_manifest.get("version"),
        ) != (EXPECTED_PUBLISHER, EXPECTED_NAME, match.group(1)):
            raise ValueError("Packaged extension manifest identity does not match the release")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: validate_vscode_marketplace_package.py <tag> <vsix>")
    try:
        validate(sys.argv[1], Path(sys.argv[2]))
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        raise SystemExit(str(error)) from error
    print("VS Code Marketplace VSIX identity and contents are valid.")
