# VS Code Marketplace 0.1.0 release preparation

IntentOS core 1.0.0 remains released and stable. Marketplace preparation covers only the existing Phase 7B VS Code Prepare → Review → Copy workflow. It does not start Phase 7D or add extension capabilities.

The extension manifest is `integrations/vscode/package.json`; its independent version is `0.1.0`. The future release tag is `vscode-v0.1.0`. This preparation change does not create that tag or publish the extension.

## Configure Trusted Publishing after merge

In the Visual Studio Marketplace publisher management page, configure a Trusted Publishing policy with these separate identities: the Marketplace publisher is `milad-seyfi`, while the GitHub repository owner remains `milad-seify`.

| Field | Value |
| --- | --- |
| Marketplace Publisher | `milad-seyfi` |
| Repository owner | `milad-seify` |
| Repository | `IntentOS` |
| Workflow | `vscode-marketplace.yml` |
| Environment | `vscode-marketplace` |

In GitHub repository Settings → Environments, create `vscode-marketplace` with:

- Required reviewer: **on**.
- Prevent self-review: **off** if Milad is the only reviewer.
- Administrator bypass: **off**.
- Deployment tag restriction: tags matching `vscode-v*`.
- Secrets: **none**.

Do not add a Marketplace PAT, `VSCE_PAT`, or npm authentication token. The publishing job exchanges its GitHub Actions OIDC identity for a short-lived Marketplace credential. Its OIDC grant is limited to the protected environment.

## Future release sequence

1. Merge the release-preparation PR.
2. Create or verify the `milad-seyfi` Marketplace publisher.
3. Configure Marketplace Trusted Publishing and the protected GitHub environment above.
4. Recheck that `milad-seyfi.intentos-vscode` is available before release.
5. Create an annotated `vscode-v0.1.0` tag on an accepted `main` commit and push only that tag.
6. Review the workflow's build-and-verify result and approve the protected publish job.
7. Confirm that the workflow publishes the exact verified VSIX.
8. Verify the Marketplace page and clean-install the extension from Marketplace.
9. Complete post-release documentation housekeeping.

The workflow packages with pinned `@vscode/vsce` 4.1.0, verifies the tag, identity, archive contents, and accepted `main` ancestry, and uploads the VSIX. Publishing downloads that artifact with digest-mismatch enforcement and publishes it with OIDC; it does not rebuild the package.

The tag workflow runs the extension contract and JavaScript syntax checks. It does not start a real Extension Host because GitHub-hosted runners do not include an installed VS Code executable; run the workspace and no-workspace Extension Host checks during local development instead.
