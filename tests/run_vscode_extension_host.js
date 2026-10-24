const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const repository = path.resolve(__dirname, '..');
const extensionPath = path.join(repository, 'integrations', 'vscode');
const extensionTestsPath = path.join(extensionPath, 'test', 'extensionHost.test.js');
const timeoutMs = Number(process.env.INTENTOS_VSCODE_TEST_TIMEOUT_MS || 120000);
const noWorkspace = process.argv.includes('--no-workspace');

function findVSCodeExecutable() {
  const configured = process.env.VSCODE_EXECUTABLE;
  if (configured && fs.existsSync(configured)) {
    return { executable: configured };
  }

  if (process.platform === 'win32') {
    const result = spawnSync('where.exe', ['code'], { encoding: 'utf8', windowsHide: true });
    const commands = result.status === 0 ? result.stdout.split(/\r?\n/).filter(Boolean) : [];
    for (const command of commands) {
      if (/\.cmd$/i.test(command)) {
        const installDirectory = path.resolve(path.dirname(command), '..');
        const executable = path.join(installDirectory, 'Code.exe');
        if (fs.existsSync(executable)) {
          const wrapper = fs.readFileSync(command, 'utf8');
          const cliMatch = wrapper.match(/%~dp0\.\.\\([^"\r\n]+resources\\app\\out\\cli\.js)/i);
          if (!cliMatch) throw new Error(`Could not find the bundled VS Code CLI path in ${command}.`);
          const cliScript = path.join(installDirectory, cliMatch[1]);
          if (!fs.existsSync(cliScript)) throw new Error(`Bundled VS Code CLI does not exist: ${cliScript}`);
          return { executable, cliScript };
        }
      }
      if (/Code\.exe$/i.test(command) && fs.existsSync(command)) return { executable: command };
    }

    const roots = [process.env.LOCALAPPDATA, process.env.ProgramFiles, process.env['ProgramFiles(x86)']]
      .filter(Boolean);
    for (const root of roots) {
      const executable = path.join(root, 'Programs', 'Microsoft VS Code', 'Code.exe');
      if (fs.existsSync(executable)) return { executable };
    }
  } else {
    const result = spawnSync('which', ['code'], { encoding: 'utf8' });
    const executable = result.status === 0 ? result.stdout.trim() : '';
    if (executable && fs.existsSync(executable)) return { executable };
  }

  throw new Error('Could not locate an installed VS Code executable. Set VSCODE_EXECUTABLE to its path.');
}

function appendTail(current, chunk) {
  const maximum = 50000;
  return (current + chunk.toString()).slice(-maximum);
}

function waitForExit(child, milliseconds) {
  if (child.exitCode !== null || child.signalCode !== null) return Promise.resolve(true);
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      child.removeListener('exit', onExit);
      resolve(false);
    }, milliseconds);
    const onExit = () => {
      clearTimeout(timer);
      resolve(true);
    };
    child.once('exit', onExit);
  });
}

async function terminateProcessTree(child) {
  if (!child.pid || child.exitCode !== null || child.signalCode !== null) return;
  if (process.platform === 'win32') {
    spawnSync('taskkill.exe', ['/pid', String(child.pid), '/t', '/f'], {
      encoding: 'utf8',
      windowsHide: true,
    });
  } else {
    try {
      process.kill(-child.pid, 'SIGTERM');
    } catch {}
  }
  if (!(await waitForExit(child, 3000))) {
    if (process.platform === 'win32') {
      spawnSync('taskkill.exe', ['/pid', String(child.pid), '/t', '/f'], {
        encoding: 'utf8',
        windowsHide: true,
      });
    } else {
      try {
        process.kill(-child.pid, 'SIGKILL');
      } catch {}
    }
    await waitForExit(child, 3000);
  }
}

function terminateIsolatedVSCode(userDataDir) {
  if (process.platform === 'win32') {
    const encoded = Buffer.from(userDataDir, 'utf8').toString('base64');
    const script = [
      `$needle=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('${encoded}'))`,
      'Get-CimInstance Win32_Process -Filter "name=\'Code.exe\'" |',
      'Where-Object { $_.CommandLine -and $_.CommandLine.IndexOf($needle, [StringComparison]::OrdinalIgnoreCase) -ge 0 } |',
      'Select-Object -ExpandProperty ProcessId',
    ].join(' ');
    const result = spawnSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', script], {
      encoding: 'utf8',
      windowsHide: true,
    });
    if (result.status === 0) {
      for (const pid of result.stdout.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)) {
        spawnSync('taskkill.exe', ['/pid', pid, '/t', '/f'], { windowsHide: true });
      }
    }
    return;
  }

  const processes = spawnSync('ps', ['-eo', 'pid=,args='], { encoding: 'utf8' });
  if (processes.status === 0) {
    for (const line of processes.stdout.split(/\r?\n/)) {
      if (!line.includes(userDataDir)) continue;
      const pid = Number(line.trim().split(/\s+/, 1)[0]);
      if (Number.isInteger(pid) && pid !== process.pid) {
        try { process.kill(pid, 'SIGTERM'); } catch {}
      }
    }
  }
}

async function removeTemporaryRoot(directory) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    try {
      fs.rmSync(directory, { recursive: true, force: true });
      return;
    } catch (error) {
      if (attempt === 19) throw error;
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
}

async function run() {
  const { executable, cliScript } = findVSCodeExecutable();
  const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'intentos-vscode-extension-test-'));
  const userDataDir = path.join(temporaryRoot, 'user-data');
  const extensionsDir = path.join(temporaryRoot, 'extensions');
  const resultFile = path.join(temporaryRoot, 'result.json');
  fs.mkdirSync(userDataDir);
  fs.mkdirSync(extensionsDir);

  const args = [
    ...(cliScript ? [cliScript] : []),
    `--user-data-dir=${userDataDir}`,
    `--extensions-dir=${extensionsDir}`,
    '--disable-extensions',
    '--disable-updates',
    '--disable-workspace-trust',
    '--skip-welcome',
    '--skip-release-notes',
    '--new-window',
    `--extensionDevelopmentPath=${extensionPath}`,
    `--extensionTestsPath=${extensionTestsPath}`,
    ...(!noWorkspace ? [repository] : []),
  ];
  const child = spawn(executable, args, {
    env: {
      ...process.env,
      ...(cliScript ? { ELECTRON_RUN_AS_NODE: '1' } : {}),
      INTENTOS_EXTENSION_TEST_RESULT: resultFile,
      INTENTOS_EXPECT_NO_WORKSPACE: noWorkspace ? '1' : '0',
    },
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
    detached: process.platform !== 'win32',
  });
  let stdout = '';
  let stderr = '';
  let launchError;
  child.stdout.on('data', (chunk) => { stdout = appendTail(stdout, chunk); });
  child.stderr.on('data', (chunk) => { stderr = appendTail(stderr, chunk); });
  child.once('error', (error) => { launchError = error; });

  console.log(`VS Code executable: ${executable}`);
  console.log(`Extension Development Path: ${extensionPath}`);
  console.log(`Extension Tests Path: ${extensionTestsPath}`);
  console.log(noWorkspace ? 'Repository workspace: none' : `Repository workspace: ${repository}`);
  console.log('VS Code user data and extensions are isolated under a temporary directory.');

  let testResult;
  let failure;
  const deadline = Date.now() + timeoutMs;
  try {
    while (Date.now() < deadline) {
      if (launchError) throw launchError;
      if (fs.existsSync(resultFile)) {
        testResult = JSON.parse(fs.readFileSync(resultFile, 'utf8'));
        if (!testResult.ok) throw new Error(testResult.error || 'Extension Host integration assertions failed.');
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
    if (!testResult) throw new Error(`Timed out after ${timeoutMs} ms waiting for Extension Host integration tests.`);

    const exitedNaturally = await waitForExit(child, 2500);
    if (exitedNaturally && child.exitCode !== 0) {
      throw new Error(`VS Code test process exited with code ${child.exitCode}.`);
    }
    console.log('Test assertions completed; closing the isolated VS Code process tree.');
    terminateIsolatedVSCode(userDataDir);
    await terminateProcessTree(child);

    console.log(`Extension Host integration test passed: ${JSON.stringify(testResult)}`);
    if (stdout.trim()) console.log(stdout.trim());
    if (stderr.trim()) console.error(stderr.trim());
  } catch (error) {
    failure = error;
    terminateIsolatedVSCode(userDataDir);
    await terminateProcessTree(child);
    console.error(`Extension Host integration test failed: ${error.stack || error}`);
    if (stdout.trim()) console.error(`VS Code stdout:\n${stdout.trim()}`);
    if (stderr.trim()) console.error(`VS Code stderr:\n${stderr.trim()}`);
    if (fs.existsSync(resultFile)) {
      console.error(`Extension Host result:\n${fs.readFileSync(resultFile, 'utf8')}`);
    }
  } finally {
    await removeTemporaryRoot(temporaryRoot);
  }

  if (failure) process.exitCode = 1;
}

run().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
