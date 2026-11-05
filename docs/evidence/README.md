# Graphical UI candidate screenshots

These PNGs were captured from running interfaces on Windows on 2026-11-05. They are developer visual evidence for owner review, not Phase 8 user observations or release screenshots.

- `simple-ui-*.png`: local browser served by `intentos ui`, captured by `node tests/run_ui_browser.js` with `INTENTOS_UI_SCREENSHOTS_DIR=docs/evidence`. The real browser test checked keyboard navigation and focus, submitted a task, reviewed and copied its result, selected a Project Compass source, previewed a non-mutating status update, reviewed a route, visited Recovery, switched to light theme and checked a small-screen layout.
- `vscode-workbench-*.png`: isolated installed VS Code Extension Host, captured by `node tests/run_vscode_extension_host.js` with `INTENTOS_VSCODE_SCREENSHOTS_DIR=docs/evidence`. The real Webview imported selected editor text, submitted that task and displayed a ready review, then navigated Project, Govern, Delegate and Recover. The screenshots show a development host with other installed extensions disabled for isolation.

The VS Code package was also installed from its generated VSIX into a separate temporary extension directory and passed activation plus the same interactive Webview flow. The installed VSIX has not been published. Screenshots are point-in-time evidence only; final integrated acceptance still needs an exact-SHA CI and owner review.
