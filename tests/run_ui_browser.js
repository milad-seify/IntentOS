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
const downloads = path.join(scratch, 'downloads');
fs.mkdirSync(downloads);
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
function command(method, params={}, timeout=15000) {
  const id=++nextId;
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{pending.delete(id);reject(new Error('Browser command timed out: '+method))},timeout);
    pending.set(id,{resolve:value=>{clearTimeout(timer);resolve(value)},reject:error=>{clearTimeout(timer);reject(error)}});
    socket.send(JSON.stringify({id,method,params}));
  });
}
async function evaluate(expression) {
  const response=await command('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(response.result.exceptionDetails)throw new Error(response.result.exceptionDetails.exception?.description||response.result.exceptionDetails.text);
  return response.result.result.value;
}
async function screenshot(name) {
  const directory=process.env.INTENTOS_UI_SCREENSHOTS_DIR;
  if(!directory)return;
  fs.mkdirSync(directory,{recursive:true});
  await pause(250);
  const response=await command('Page.captureScreenshot',{format:'png',captureBeyondViewport:false},30000);
  fs.writeFileSync(path.join(directory,name),Buffer.from(response.result.data,'base64'));
}
async function chooseFile(selector,filename) {
  const document=await command('DOM.getDocument',{depth:1});
  const node=await command('DOM.querySelector',{nodeId:document.result.root.nodeId,selector});
  assert(node.result.nodeId,`Missing file input ${selector}`);
  await command('DOM.setFileInputFiles',{nodeId:node.result.nodeId,files:Array.isArray(filename)?filename:[filename]});
}
function fixture(name,data){const filename=path.join(scratch,name);fs.writeFileSync(filename,typeof data==='string'?data:JSON.stringify(data,null,2).replace(/\n/g,'\r\n'));return filename}
async function navigate(label){await evaluate(`[...document.querySelectorAll('#navigation button')].find(x=>x.textContent===${JSON.stringify(label)}).click();true`);await pause(80)}
async function submit(action,fields={},files={}){
  await evaluate(`(()=>{const form=document.querySelector('form[data-action=${action}]');for(const [key,value]of Object.entries(${JSON.stringify(fields)})){const input=form.querySelector('[name="'+key+'"]');if(input.type==='checkbox')input.checked=value;else input.value=value}window.__testResponse=null;return true})()`);
  for(const [key,file]of Object.entries(files))await chooseFile('#'+action+'-'+key,file);
  await evaluate(`document.querySelector('form[data-action=${action}]').requestSubmit();true`);
  await until(()=>evaluate('window.__testResponse'),'real response '+action);
  await until(()=>evaluate("document.querySelector('#feedback').textContent!=='Working locally…'"),'render '+action);
  return evaluate('window.__testResponse');
}
async function saveArtifact(){const before=new Set(fs.readdirSync(downloads));await evaluate("[...document.querySelectorAll('#result > button')].find(b=>b.textContent==='Download reviewable artifact').click();true");const name=await until(()=>fs.readdirSync(downloads).find(n=>!before.has(n)&&n.endsWith('.json')),'artifact download');return path.join(downloads,name)}
async function approve(reference){await evaluate(`(()=>{const box=document.querySelector('#result .approval');const input=box.querySelector('#approval-ref');if(input)input.value=${JSON.stringify(reference||'')};const check=box.querySelector('[type=checkbox]');check.checked=true;check.dispatchEvent(new Event('change'));window.__testResponse=null;box.querySelector('button').click();return true})()`);await until(()=>evaluate('window.__testResponse'),'approval');await until(()=>evaluate("document.querySelector('#feedback').textContent!=='Working locally…'"),'approval render');return evaluate('window.__testResponse')}
async function assertFits(width){await command('Emulation.setDeviceMetricsOverride',{width,height:844,deviceScaleFactor:1,mobile:false});await pause(80);const size=await evaluate('({width:innerWidth,page:document.documentElement.scrollWidth})');assert(size.page<=size.width+1,'Document overflow at '+width+': '+size.page)}
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
  await command('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
  await until(()=>evaluate("Boolean(document.querySelector('#prepare-text'))"),'rendered first-use form');
  assert.strictEqual(await evaluate('location.search'),'','Bootstrap query must be removed before screenshots');
  await evaluate("window.__testRequests=0;window.__browserErrors=[];window.addEventListener('unhandledrejection',e=>window.__browserErrors.push(String(e.reason)));const fetchOriginal=window.fetch;window.fetch=async(...args)=>{window.__testRequests++;const response=await fetchOriginal(...args);window.__testResponse={http:response.status,payload:await response.clone().json()};return response};true");
  await evaluate("document.querySelector('a.skip').focus();true");
  await command('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
  await command('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});
  assert.strictEqual(await evaluate("document.querySelector('#navigation').contains(document.activeElement)"),true,'Keyboard Tab must reach workflow navigation');
  assert.strictEqual(await evaluate("document.querySelector('#feedback').getAttribute('role')"),'status');
  await screenshot('simple-ui-start.png');

  await evaluate("document.querySelector('#prepare-text').value='Codex: Refactor this function without changing behavior.';document.querySelector('form[data-action=prepare]').requestSubmit();true");
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('Copy Prepared Task')"),'prepared review');
  assert.strictEqual(await evaluate("document.querySelector('#result').textContent.includes('Approval boundaries') && document.querySelector('#result').textContent.includes('Verification')"),true);
  await pause(200);
  await screenshot('simple-ui-review.png');
  await evaluate("document.querySelector('#result button.primary').click();true");
  await until(()=>evaluate("document.querySelector('#feedback').textContent.includes('copied') || document.querySelector('#feedback').textContent.includes('denied')"),'clipboard outcome');

  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Project').click();true");
  assert.strictEqual(await evaluate("document.activeElement.id"),'main','Workflow navigation must move focus to main content');
  await chooseFile('#compass-authoritative',path.join(project,'AGENTS.md'));
  await evaluate("document.querySelector('#compass-task').value='Review API';document.querySelector('form[data-action=compass]').requestSubmit();true");
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('Project Compass review')"),'project review');
  await pause(200);
  await screenshot('simple-ui-project.png');

  await evaluate("[...document.querySelectorAll('#navigation button')].find(x=>x.textContent==='Governance').click();true");
  await evaluate(`document.querySelector('#stateStatus-root').value=${JSON.stringify(project)};document.querySelector('#stateStatus-current_phase').value='Milestone 2';document.querySelector('#stateStatus-next_action').value='Run checks';document.querySelector('#stateStatus-evidence').value='Owner reviewed issue #12';document.querySelector('form[data-action=stateStatus]').requestSubmit();true`);
  await until(()=>evaluate("!document.querySelector('#result').hidden && document.querySelector('#result').textContent.includes('Exact proposed change')"),'reviewed status proposal');
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
  await assertFits(320);await command('Emulation.clearDeviceMetricsOverride');

  // All writes and approvals below are confined to this disposable Git project.
  fs.writeFileSync(path.join(project,'docs','DECISIONS.md'),'# Decisions\n\n## D-001 — Synthetic fixture\n\nDeveloper data only.\n');
  fs.writeFileSync(path.join(project,'docs','SCOPE.md'),'## In Scope\n- Review API\n\n## Out of Scope\n- Add Redis cache\n');
  const windowsContext=fixture('windows-context.md','## Current phase\r\nبررسی رابط کاربری\r\n\r\n## Next action\r\nReview UI\r\n');
  await navigate('Start');
  let response=await submit('prepare',{text:'Codex: Review UI accessibility without changing code',authority:true},{context:windowsContext});
  assert.strictEqual(response.payload.status,'ready');assert(response.payload.prompt.includes('بررسی رابط کاربری'));
  await command('Browser.grantPermissions',{origin:await evaluate('location.origin'),permissions:['clipboardReadWrite','clipboardSanitizedWrite']});
  await evaluate("document.querySelector('#result > button.primary').click();true");await until(()=>evaluate("document.querySelector('#feedback').textContent.includes('copied')"),'copy success');
  assert.strictEqual((await evaluate('navigator.clipboard.readText()')).replace(/\r\n/g,'\n'),response.payload.prompt);
  await screenshot('simple-ui-windows-context.png');
  response=await submit('prepare',{text:'Fix it'});assert.strictEqual(response.payload.status,'clarification');
  await evaluate("document.querySelector('#result button.secondary').click();true");
  assert.strictEqual(await evaluate("document.querySelector('#prepare-context').files[0].name"),'windows-context.md','Clarification must preserve selected context');
  response=await submit('prepare',{text:'Codex: Review UI accessibility without changing code'});assert.strictEqual(response.payload.status,'ready');
  await navigate('Project');response=await submit('compass',{task:'Review UI'},{authoritative:windowsContext});assert.strictEqual(response.http,200);

  await navigate('Governance');
  await evaluate("document.querySelector('#stateDecision-title').value='Unsent decision draft';true");
  await navigate('Project');await navigate('Governance');assert.strictEqual(await evaluate("document.querySelector('#stateDecision-title').value"),'Unsent decision draft');
  const before=fs.readFileSync(statusFile,'utf8');
  response=await submit('stateStatus',{root:project,current_phase:'Synthetic review',next_action:'Verify findings',evidence:'DEVELOPER TEST ONLY'});
  assert.strictEqual(response.payload.status,'update');assert.strictEqual(fs.readFileSync(statusFile,'utf8'),before);
  await navigate('Project');await navigate('Governance');assert.strictEqual(await evaluate("Boolean(document.querySelector('#result .approval'))"),false,'Restored reviews must not restore approval authority');
  response=await submit('stateDecision',{root:project,decision_id:'D-002',title:'Synthetic review boundary',body:'DEVELOPER TEST ONLY',approval_ref:'DEVELOPER TEST ONLY'});assert.strictEqual(response.payload.status,'update');assert(!fs.readFileSync(path.join(project,'docs','DECISIONS.md'),'utf8').includes('D-002'));
  response=await submit('stateScope',{root:project,amendment_id:'S-001',task:'Add Redis cache',reason:'Synthetic fixture only',approval_ref:'DEVELOPER TEST ONLY'});assert.strictEqual(response.payload.status,'update');
  response=await submit('stateStatus',{root:project,current_phase:'Synthetic review',next_action:'Verify findings',evidence:'DEVELOPER TEST ONLY'});
  fs.appendFileSync(statusFile,'\nExternally changed fixture\n');response=await approve();assert.strictEqual(response.http,400);assert.strictEqual(await evaluate("document.activeElement.id"),'feedback');assert(await evaluate("document.querySelector('#feedback').getBoundingClientRect().top<innerHeight"));
  fs.writeFileSync(statusFile,before);await submit('stateStatus',{root:project,current_phase:'Synthetic review',next_action:'Verify findings',evidence:'DEVELOPER TEST ONLY'});response=await approve();assert.strictEqual(response.payload.status,'applied');

  // Progress stays beside the initiating control; a duplicate submit cannot start another request.
  await command('Network.enable');await command('Network.emulateNetworkConditions',{offline:false,latency:600,downloadThroughput:-1,uploadThroughput:-1});
  const count=await evaluate('window.__testRequests');
  await evaluate("document.querySelector('form[data-action=stateStatus] button[type=submit]').scrollIntoView({behavior:'instant',block:'center'});document.querySelector('form[data-action=stateStatus]').requestSubmit();document.querySelector('form[data-action=stateStatus]').requestSubmit();true");
  await until(()=>evaluate("document.querySelector('#feedback').textContent==='Working locally…'"),'visible progress');
  assert(await evaluate("(()=>{const r=document.querySelector('#feedback').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&document.querySelector('form[data-action=stateStatus]').getAttribute('aria-busy')==='true'})()"));
  await screenshot('simple-ui-visible-progress.png');
  await until(async()=>(await evaluate('window.__testRequests'))===count+1,'one request');
  await command('Network.emulateNetworkConditions',{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});
  await until(()=>evaluate("document.querySelector('form[data-action=stateStatus]').getAttribute('aria-busy')==='false'"),'controls recovered');

  const gates=fixture('gates.json',{schema_version:1,requirements:[{key:'R01',outcome:'Synthetic check passes',checks:['check'],accepted_by_owner:true,approval_ref:'DEVELOPER TEST ONLY'}],milestones:[{key:'M01',requirement_keys:['R01'],state:'approved',approval_ref:'DEVELOPER TEST ONLY'}],evidence:[{requirement_key:'R01',check:'check',passed:true,source_ref:'DEVELOPER TEST ONLY',source_revision:'fixture-base',independently_reviewed:true}]});
  response=await submit('gates',{}, {evidence:gates});assert.strictEqual(response.payload.launch_approved,false);
  await screenshot('simple-ui-readiness.png');

  await navigate('Delegation');const models=fixture('models.json',{schema_version:1,models:[{name:'SYNTHETIC-MODEL',provider:'developer-fixture',surfaces:['codex'],capability:'balanced',cost:'low',available:true,verified:true}]});
  response=await submit('route',{text:'Codex: Refactor the parser',target:'codex'},{models});assert.strictEqual(response.payload.selected_model,'SYNTHETIC-MODEL');
  await evaluate("document.querySelector('#result details').open=true;true");
  for(const width of [390,320]){await assertFits(width);if(width===320)await evaluate("(()=>{const pre=document.querySelector('#result details pre');pre.scrollIntoView({behavior:'instant',block:'start'});pre.scrollTop=Math.max(0,pre.textContent.slice(0,pre.textContent.indexOf('catalog_sha256')).split('\\n').length*parseFloat(getComputedStyle(pre).lineHeight)-80);return true})()");await screenshot('simple-ui-route-'+width+'.png')}
  await command('Emulation.clearDeviceMetricsOverride');
  await navigate('Recovery');await navigate('Delegation');assert.strictEqual(await evaluate("document.querySelector('#route-models').files[0].name"),'models.json');
  response=await submit('handoffPrepare',{root:project,text:'Codex: Review UI accessibility without changes',target:'codex',task_id:'synthetic-task',context_file:'AGENTS.md'});assert.strictEqual(response.payload.status,'saved');assert(await evaluate("document.querySelector('#result').innerText.includes('Portable prepared instructions')"));
  const packet=await saveArtifact();assert(fs.existsSync(packet));await evaluate("[...document.querySelectorAll('#result button')].find(b=>b.textContent==='Copy handoff instructions').click();true");await until(()=>evaluate("document.querySelector('#feedback').textContent.includes('copied')"),'handoff copy');assert.strictEqual((await evaluate('navigator.clipboard.readText()')).replace(/\r\n/g,'\n'),JSON.parse(fs.readFileSync(packet,'utf8')).handoff.prepared_prompt);await screenshot('simple-ui-portable-handoff.png');

  await navigate('Recovery');const spec=fixture('checkpoint-spec.json',{task_id:'synthetic-task',next_step_id:'verify',approved_plan:[{step_id:'review',action:'Review UI'},{step_id:'verify',action:'Verify findings'}],plan_approval_ref:'DEVELOPER TEST ONLY',state_summary:'Synthetic review awaits verification',state_evidence_ref:'DEVELOPER TEST ONLY',completed:[{step_id:'review',evidence_ref:'Synthetic evidence',accepted_by_owner:true}],operation_ids:[],required_approval_ids:['owner-verify'],estimated_remaining_tokens:100});
  response=await submit('checkpointCreate',{root:project,context_file:'AGENTS.md'},{spec});assert.strictEqual(response.payload.status,'saved');const checkpoint=await saveArtifact();
  response=await submit('checkpointReview',{root:project,context_file:'AGENTS.md',ledger_reviewed:true},{checkpoint});assert.strictEqual(response.payload.status,'blocked');
  response=await submit('checkpointReview',{root:project,context_file:'AGENTS.md',ledger_reviewed:true,accepted_approval:'owner-verify'},{checkpoint});assert.strictEqual(response.payload.approved_to_execute,false);
  await screenshot('simple-ui-continuation.png');

  await navigate('Outcomes');const source=(task,variant,passed,lesson='')=>({schema_version:1,task_id:task,variant,conditions:{executor:'SYNTHETIC TEST',model:'synthetic',effort:'high',base_revision:'fixture-base',context:'same',permissions:'read-only',environment:'developer-test'},checks:[{name:'synthetic check',passed,evidence_ref:'DEVELOPER TEST ONLY'}],execution_success:passed,metrics:{input_tokens:null},source_ref:'DEVELOPER TEST ONLY '+task+variant,friction:'Synthetic data',rework:'',context_gap:'',verification_gap:'',lesson_hint:lesson});
  response=await submit('outcomeRecord',{}, {evidence:fixture('raw.json',source('pair','raw',false))});assert.strictEqual(response.payload.status,'recorded');const raw=await saveArtifact();
  response=await submit('outcomeRecord',{}, {evidence:fixture('prepared.json',source('pair','prepared',true))});assert.strictEqual(response.payload.status,'recorded');const prepared=await saveArtifact();
  response=await submit('outcomeCompare',{}, {raw,prepared});assert.strictEqual(response.payload.comparison.winner,'prepared');assert.strictEqual(response.payload.comparison.input_tokens_delta,null);
  await screenshot('simple-ui-paired-outcomes.png');
  const repeated=[];for(const id of ['failed-one','failed-two']){await submit('outcomeRecord',{}, {evidence:fixture(id+'.json',source(id,'raw',false,'Preserve verification evidence'))});repeated.push(await saveArtifact())}
  response=await submit('outcomeLearn',{}, {records:repeated});assert.strictEqual(response.payload.status,'proposal');response=await approve('DEVELOPER TEST ONLY');assert.strictEqual(response.payload.runtime_policy_changed,false);
  await screenshot('simple-ui-learning-review.png');

  await chooseFile('#outcomeRecord-evidence',fixture('invalid.json','{broken'));
  await evaluate("document.querySelector('form[data-action=outcomeRecord]').requestSubmit();true");await until(()=>evaluate("document.querySelector('#feedback').getAttribute('role')==='alert'"),'accessible upload error');
  assert(await evaluate("document.querySelector('#feedback').textContent.includes('valid JSON')"));assert.strictEqual(await evaluate("document.activeElement.id"),'feedback');
  await screenshot('simple-ui-upload-error.png');
  // Templates download real files but never fabricate approved evidence.
  const templateBefore=new Set(fs.readdirSync(downloads));await evaluate("document.querySelector('form[data-action=outcomeRecord] .input-guide').open=true;document.querySelector('form[data-action=outcomeRecord] .input-guide button').click();true");
  const example=await until(()=>fs.readdirSync(downloads).find(n=>!templateBefore.has(n)&&n.endsWith('.json')),'example download');const exampleData=JSON.parse(fs.readFileSync(path.join(downloads,example),'utf8'));assert.strictEqual(exampleData.execution_success,null);assert.strictEqual(exampleData.checks[0].passed,null);
  for(const width of [390,320])await assertFits(width);await command('Emulation.clearDeviceMetricsOverride');
  await evaluate("document.querySelector('#theme').click();true");assert.strictEqual(await evaluate('document.documentElement.dataset.theme'),'dark');
  await screenshot('simple-ui-dark-refined.png');
  await command('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});assert.strictEqual(await evaluate("getComputedStyle(document.documentElement).scrollBehavior"),'auto');
  assert.deepStrictEqual(await evaluate('window.__browserErrors'),[]);
  console.log('Real browser acceptance passed: all six areas, CRLF documents/JSON, clarification/context retention, exact clipboard, templates/downloads, read-only previews and isolated approvals, duplicate-submit protection, visible errors/progress, draft/file retention, safe restored reviews, dark/light, reduced motion, and desktop/390/320 layouts. No external agent was dispatched.');
} finally {
  try{socket?.close()}catch{}
  stop(browser);stop(server);
  await pause(1000);
  removeScratch();
}
}

run().catch((error)=>{console.error(error.stack||error);process.exitCode=1});
