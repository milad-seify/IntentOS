# VS Code Marketplace releases

## 0.1.0 publication complete

The first public extension release is `0.1.0`, published as `milad-seyfi.intentos-vscode` from tag `vscode-v0.1.0`. IntentOS core `1.0.0` remains independently versioned and released on PyPI.

The final Trusted Publishing identity boundary is:

| Field | Value |
| --- | --- |
| Marketplace publisher | `milad-seyfi` |
| GitHub repository owner | `milad-seify` |
| Repository | `IntentOS` |
| Workflow | `vscode-marketplace.yml` |
| Environment | `vscode-marketplace` |
| Published tag | `vscode-v0.1.0` |

The Marketplace publication succeeded through GitHub Actions Trusted Publishing / OIDC. The workflow published the exact VSIX artifact it had built and verified. A real installation from the Marketplace was manually tested through the Prepare → Review → Copy workflow, including clarification, Ready state, Codex target detection, risk classification, approval boundaries, verification guidance, prepared task, and Copy Prepared Task.

The accepted user flow remains:

```text
Request → IntentOS preparation → Review → Copy Prepared Task → hand off to an AI tool
```

The extension does not execute or send tasks to an agent. Phase 7D has not started.

## Trusted Publishing configuration

Keep Marketplace identity distinct from GitHub ownership when maintaining the publisher's Trusted Publishing policy:

- Marketplace publisher: `milad-seyfi`
- GitHub repository owner: `milad-seify`
- Repository: `IntentOS`
- Workflow: `vscode-marketplace.yml`
- Environment: `vscode-marketplace`

The protected GitHub environment should retain its required reviewer, disabled administrator bypass, `vscode-v*` tag restriction, and no secrets. Do not add a Marketplace PAT, `VSCE_PAT`, or npm authentication token. The publishing job exchanges its GitHub Actions OIDC identity for a short-lived Marketplace credential.

## Future extension release sequence

1. Update only the VS Code extension version and changelog for the approved release.
2. Review the publisher identity and exact-artifact workflow in `.github/workflows/vscode-marketplace.yml`.
3. Create an annotated `vscode-v<version>` tag on an accepted `main` commit and push only that tag.
4. Review the workflow's build-and-verify result and approve the protected publish job.
5. Confirm the workflow publishes the exact verified VSIX artifact; it must not rebuild during publishing.
6. Verify the Marketplace listing and install the release from the Marketplace.
7. Record the completed release in the status documentation.

The tag workflow validates release identity, package contents, and accepted `main` ancestry, and runs extension contract and JavaScript syntax checks. It does not start a real Extension Host because GitHub-hosted runners do not include an installed VS Code executable. Run workspace and no-workspace Extension Host checks during local development.
