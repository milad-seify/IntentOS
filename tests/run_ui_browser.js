// Dependency-free real browser smoke for the local UI. Run with Node 22+ and Edge/Chrome.
const assert = require('assert');
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const root = path.resolve(__dirname, '..');
const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'intentos-ui-browser-'));
const browserProfile = path.join(scratch, 'browser');
const project = path.join(scratch, 'project');
fs.mkdirSync(browserProfile);
fs.mkdirSync(path.join(project, 'docs'), { recursive: true });
const statusFile = path.join(project, 'docs', 'STATUS.md');
const originalStatus = '## Current phase\nMVP\n\n## Next action\nReview API\n';
fs.writeFileSync(statusFile, originalStatus);
fs.writeFileSync(path.join(project, 'AGENTS.md'), '# Project goal\nBuild a reliable tool.\n\n## In Scope\n- Review API\n');
for (const args of [['init', '-q'], ['add', '.'], ['-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'base']]) {
  const run = spawnSync('git', args, { cwd: project, encoding: 'utf8' });
  assert.strictEqual(run.status, 0, run.stderr);
}

function browserPath() {
  if (process.env.INTENTOS_UI_BROWSER) return process.env.INTENTOS_UI_BROWSER;
  if (process.platform === 'win32') {
    const candidates = [
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    ];
    const found = candidates.find((candidate) => fs.existsSync(candidate));
    if (found) return found;
  }
  for (const name of ['chromium', 'chromium-browser', 'google-chrome']) {
    const found = spawnSync(process.platform === 'win32' ? 'where.exe' : 'which', [name], { encoding: 'utf8' });
    if (found.status === 0) return found.stdout.trim().split(/\r?\n/)[0];
  }
  throw new Error('No installed Chromium browser found. Set INTENTOS_UI_BROWSER.');
}

const python = process.env.INTENTOS_UI_PYTHON || path.join(root, '.venv', process.platform === 'win32' ? 'Scripts' : 'bin', process.platform === 'win32' ? 'python.exe' : 'python');
const pause = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
async function until(check, label, timeout=15000) {
  const deadline = Date.now() + timeout;
  while (Date.now() < deadline) {
    const value = await check();
    if (value) return value;
    await pause(100);
  }
  throw new Error(`Timed out waiting for ${label}`);
}

let server, browser, socket;
let nextId=0;
const pending=new Map();
function command(method, params={}) {
  const id=++nextId;
  return new Promise((resolve,reject)=>{
    pending.set(id,{resolve,reject});
    socket.send(JSON.stringify({id,method,params}));
  });
}
async function evaluate(expression) {
  const response=await command('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(response.exceptionDetails)throw new Error(response.exceptionDetails.text);
  return response.result.result.value;
}
async function screenshot(name) {
  const directory=process.env.INTENTOS_UI_SCREENSHOTS_DIR;
  if(!directory)return;
  fs.mkdirSync(directory,{recursive:true});
  const response=await command('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(directory,name),Buffer.from(response.result.data,'base64'));
}
async function chooseFile(selector,filename) {
  const document=await command('DOM.getDocument',{depth:1});
  const node=await command('DOM.querySelector',{nodeId:document.result.root.nodeId,selector});
  assert(node.result.nodeId,`Missing file input ${selector}`);
  await command('DOM.setFileInputFiles',{nodeId:node.result.nodeId,files:[filename]});
}
function stop(child) {
  if(!child?.pid)return;
  if(process.platform==='win32')spawnSync('taskkill.exe',['/pid',String(child.pid),'/t','/f'],{windowsHide:true});
  else {try{process.kill(-child.pid,'SIGTERM')}catch{try{child.kill('SIGTERM')}catch{}}}
}
function removeScratch() {
  const target=path.resolve(scratch), parent=path.resolve(os.tmpdir())+path.sep;
  if(!target.startsWith(parent))throw new Error('Temporary cleanup escaped the system temp directory');
  for(let attempt=0;attempt<10;attempt++){
    try{fs.rmSync(target,{recursive:true,force:true});return}catch(error){if(attempt===9)throw error;spawnSync(process.platform==='win32'?'ping':'sleep',process.platform==='win32'?['-n','2','127.0.0.1']:['1'])}
  }
}

async function run() {
  try {
  server=spawn(python,['-u','-m','intentos','ui','--no-browser'],{cwd:root,windowsHide:true,stdio:['ignore','pipe','pipe'],detached:process.platform!=='win32'});
  let serverText='';server.stdout.on('data',(chunk)=>{serverText+=chunk.toString()});
  let serverError='';server.stderr.on('data',(chunk)=>{serverError+=chunk.toString()});
  const launch=await until(()=>serverText.match(/http:\/\/127\.0\.0\.1:\d+\/\?session=[A-Za-z0-9_-]+/)?.[0],'local UI URL');
  browser=spawn(browserPath(),[
    '--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
    '--remote-debugging-port=0','--remote-allow-origins=*',`--user-data-dir=${browserProfile}`,
    '--window-size=1440,900',launch,
  ],{windowsHide:true,stdio:'ignore',detached:process.platform!=='win32'});
  const activePort=path.join(browserProfile,'DevToolsActivePort');
  const port=await until(()=>fs.existsSync(activePort)?fs.readFileSync(activePort,'utf8').split(/\r?\n/)[0]:null,'browser debugging port');
  const targets=await until(async()=>{
    try {const response=await fetch(`http://127.0.0.1:${port}/json/list`);const list=await response.json();return list.find((item)=>item.type==='page'&&item.url.startsWith('http://127.0.0.1:'))}
    catch{return null}
  },'local browser page');
  socket=new WebSocket(targets.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true})});
  socket.addEventListener('message',(event)=>{
    const packet=JSON.parse(event.data);if(!packet.id)return;
    const entry=pending.get(packet.id);if(!entry)return;pending.delete(packet.id);
    if(packet.error)entry.reject(new Error(packet.error.message));else entry.resolve(packet);
  });
  await command('Runtime.enable');await command('Page.enable');await command('DOM.enable');
  await until(()=>evaluate("Boolean(document.querySelector('#prepare-text'))"),'rendered first-use form');
  await screenshot('simple-ui-start.png');

  await evaluate("document.querySelector('#prepare-text').value='Codex: Refactor this function without changing behavior.';document.querySelector('form[data-action=prepare]').requestSubmit();true");
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('Copy Prepared Task')"),'prepared review');
  assert.strictEqual(await evaluate("document.querySelector('#result').textContent.includes('Approval boundaries') && document.querySelector('#result').textContent.includes('Verification')"),true);
  await pause(200);
  await screenshot('simple-ui-review.png');
  await evaluate("document.querySelector('#result button.primary').click();true");
  await until(()=>evaluate("document.querySelector('#feedback').textContent.includes('copied') || document.querySelector('#feedback').textContent.includes('denied')"),'clipboard outcome');

  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Project').click();true");
  await chooseFile('#compass-authoritative',path.join(project,'AGENTS.md'));
  await evaluate("document.querySelector('#compass-task').value='Review API';document.querySelector('form[data-action=compass]').requestSubmit();true");
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('Project Compass review')"),'project review');
  await pause(200);
  await screenshot('simple-ui-project.png');

  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Governance').click();true");
  await evaluate(`document.querySelector('#stateStatus-root').value=${JSON.stringify(project)};document.querySelector('#stateStatus-current_phase').value='Milestone 2';document.querySelector('#stateStatus-next_action').value='Run checks';document.querySelector('#stateStatus-evidence').value='Owner reviewed issue #12';document.querySelector('form[data-action=stateStatus]').requestSubmit();true`);
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('diff preview')"),'reviewed status proposal');
  assert.strictEqual(fs.readFileSync(statusFile,'utf8'),originalStatus,'Preview must not mutate project state');
  await pause(200);
  await screenshot('simple-ui-governance.png');

  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Delegation').click();document.querySelector('#route-text').value='Codex: review this parser without changes';document.querySelector('form[data-action=route]').requestSubmit();true");
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('fallback')"),'route review');
  await pause(200);
  await screenshot('simple-ui-delegation.png');
  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Recovery').click();true");
  await screenshot('simple-ui-recovery.png');
  await evaluate("document.getElementById('theme').click();true");
  assert.strictEqual(await evaluate("document.documentElement.dataset.theme"),'light');
  await evaluate("window.scrollTo(0,0);true");
  await screenshot('simple-ui-light.png');
  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Start').click();true");
  await command('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:false});
  await pause(200);
  assert.strictEqual(await evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),true,'Small viewport has horizontal overflow');
  assert.strictEqual(await evaluate("[...document.querySelectorAll('#navigation button')].some(x=>x.textContent==='Start')"),true);
  await screenshot('simple-ui-small-screen.png');
  console.log('Real browser passed: first-use prepare/review, clipboard outcome, selected-source Compass, non-mutating governance preview, route review, recovery navigation, light theme, and small-screen layout.');
} finally {
  try{socket?.close()}catch{}
  stop(browser);stop(server);
  await pause(1000);
  removeScratch();
}
}

run().catch((error)=>{console.error(error.stack||error);process.exitCode=1});
