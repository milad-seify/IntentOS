/* IntentOS local workbench: presentation and explicitly chosen inputs only. */
const csrf = document.querySelector('meta[name="intentos-csrf"]').content;
const navigation = document.getElementById('navigation');
const workspace = document.getElementById('workspace');
const result = document.getElementById('result');
const feedback = document.getElementById('feedback');
const ui = globalThis.IntentOSUI;
const drafts = new Map(), reviews = new Map();
let activeOperation = null;
let current = 'start';
let lastTask = '';
let projectFolder = '';
let preparedPrompt = '';
const themes=['system','light','dark'];let themeIndex=0;
document.getElementById('theme').addEventListener('click',()=>{themeIndex=(themeIndex+1)%themes.length;const theme=themes[themeIndex];document.documentElement.dataset.theme=theme==='system'?'':theme;document.getElementById('theme').textContent='Theme: '+theme[0].toUpperCase()+theme.slice(1)});

const pages = [
  {id:'start',label:'Start',title:'Prepare your next task',description:'Describe an outcome in your own words. Review the risks and boundaries before handing it to your AI tool.'},
  {id:'project',label:'Project',title:'See the project clearly',description:'Choose the documents IntentOS may read. Claims retain file and line provenance; missing or conflicting facts stay visible.'},
  {id:'governance',label:'Governance',title:'Keep decisions controlled',description:'Review status, decisions, scope and readiness against explicit evidence. Persistent changes need a separate approval.'},
  {id:'delegation',label:'Delegation',title:'Choose a safe handoff',description:'Review recommendations, create portable instructions and explicitly authorize any supported Codex dispatch.'},
  {id:'recovery',label:'Recovery',title:'Resume with context',description:'Save or review a checkpoint. A passing review never restarts an agent or grants execution permission.'},
  {id:'outcomes',label:'Outcomes',title:'Learn from observed results',description:'Record externally checked outcomes and compare controlled variants without filling in missing evidence.'},
];

function el(tag, className='', text) {
  const node=document.createElement(tag);
  if(className)node.className=className;
  if(text!==undefined)node.textContent=text;
  return node;
}

function heading(parent,title,description) {
  parent.append(el('h2','',title));
  if(description)parent.append(el('p','card-intro',description));
}

function field(form,name,label,type='text',options,help) {
  const id=form.dataset.action+'-'+name;
  const labelNode=el('label','',label);labelNode.htmlFor=id;form.append(labelNode);
  let input;
  if(type==='textarea')input=el('textarea');
  else if(type==='select'){
    input=el('select');
    for(const [value,caption] of options){const option=el('option','',caption);option.value=value;input.append(option)}
  }else{input=el('input');input.type=type==='upload'?'file':type}
  input.id=id;input.name=name;
  if(type==='upload'){input.accept='.json,application/json';if(name==='records')input.multiple=true}
  if(name==='root')input.value=projectFolder;
  if(name==='text'&&lastTask)input.value=lastTask;
  if(type==='checkbox'){labelNode.className='inline-label';labelNode.prepend(input)}else form.append(input);
  if(help)form.append(el('p','hint',help));
  return input;
}

function inform(text='',error=false,focus=false) {
  feedback.textContent=text;feedback.hidden=!text;feedback.className=text?'notice'+(error?' error':''):'';
  feedback.setAttribute('role',error?'alert':'status');
  if(focus&&text){feedback.focus({preventScroll:true});feedback.scrollIntoView({behavior:'instant',block:'nearest'})}
}

async function operate(container,handler) {
  if(activeOperation)return;
  activeOperation=container;
  container.insertBefore(feedback,container.querySelector('.actions')||null);
  container.setAttribute('aria-busy','true');container.setAttribute('aria-describedby','feedback');
  const locked=[...document.querySelectorAll('button,input,textarea,select')].map(button=>[button,button.disabled]);
  for(const [button]of locked)button.disabled=true;
  inform('Working locally…');result.hidden=container!==result&&!result.contains(container);
  try{await handler()}catch(error){inform((error.message||'The operation failed.')+' Review the inputs and try this action again.',true,true)}
  finally{container.setAttribute('aria-busy','false');for(const [button,disabled]of locked)if(button.isConnected)button.disabled=disabled;activeOperation=null}
}

function card(action,title,description,fields,buttonText,handler) {
  const form=el('form','card');form.dataset.action=action;heading(form,title,description);
  for(const spec of fields)field(form,...spec);
  const actions=el('div','actions');const submit=el('button','primary',buttonText);submit.type='submit';actions.append(submit);form.append(actions);
  form.addEventListener('submit',async(event)=>{event.preventDefault();await operate(form,()=>handler(form))});
  workspace.append(form);
  return form;
}

async function upload(input) {
  const files=[...input.files];
  if(!files.length)return null;
  const items=[];
  for(const file of files){if(file.size>100000)throw new Error('Choose a file smaller than 100 KB.');const content=await file.text();if(input.accept.includes('json')){try{const value=JSON.parse(content);if(!value||typeof value!=='object'||Array.isArray(value))throw Error()}catch{throw new Error(file.name+' must contain one valid JSON object. Open File format and example for guidance.')}}items.push({name:file.name,content})}
  return input.multiple?items:items[0];
}

async function values(form) {
  const out={};
  for(const input of form.querySelectorAll('[name]')){
    if(input.type==='file')out[input.name]=await upload(input);
    else if(input.type==='checkbox')out[input.name]=input.checked;
    else out[input.name]=input.value.trim();
  }
  if(out.root){projectFolder=out.root;for(const input of document.querySelectorAll('input[name=root]'))if(!input.value)input.value=projectFolder}
  if(out.text)lastTask=out.text;
  return out;
}

async function request(path,body) {
  const encoded=JSON.stringify(body);
  if(new TextEncoder().encode(encoded).length>64000)throw new Error('Selected text and files exceed the 64 KB local request limit. Choose smaller evidence files.');
  try{
    const response=await fetch(path,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-IntentOS-CSRF':csrf},body:encoded});
    const payload=await response.json();
    if(!response.ok)throw new Error(payload.error||'The local operation could not be completed.');
    inform();return payload;
  }catch(error){throw new Error(error.message||'The local operation failed. Keep the launcher terminal running and retry.')}
}

function list(parent,items,empty='None supplied') {
  if(!Array.isArray(items)||!items.length){parent.append(el('p','subtle',empty));return}
  for(const item of items){const row=el('div','item');row.append(el('span','',typeof item==='string'?item:JSON.stringify(item)));parent.append(row)}
}

function section(parent,title,content,empty) {
  const container=el('section','section');container.append(el('h3','',title));
  if(Array.isArray(content))list(container,content,empty);
  else container.append(el('p','',content||empty||'Not supplied'));
  parent.append(container);
}

function facts(parent,entries) {
  const grid=el('div','fact-grid');
  for(const [label,value] of entries){const card=el('div','fact');card.append(el('small','',label),el('strong','',value===null||value===undefined||value===''?'Unknown':String(value)));grid.append(card)}
  parent.append(grid);
}

function generic(parent,key,value,depth=0) {
  if(depth>5)return;
  const box=el('div','item');
  if(key)box.append(el('strong','',key.replaceAll('_',' ')));
  if(Array.isArray(value)){
    if(!value.length)box.append(el('small','','None supplied'));
    else for(const item of value)generic(box,'',item,depth+1);
  }else if(value&&typeof value==='object'){
    for(const [name,item] of Object.entries(value))generic(box,name,item,depth+1);
  }else box.append(el('span','',value===null||value===undefined?'Unknown':String(value)));
  parent.append(box);
}

function download(data) {
  const blob=new Blob([data.content],{type:'application/json;charset=utf-8'});
  const url=URL.createObjectURL(blob);const anchor=el('a');anchor.href=url;anchor.download=data.filename||'intentos-result.json';document.body.append(anchor);anchor.click();anchor.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function show(action,payload,restored=false) {
  if(!restored)reviews.set(current,{action,payload:ui.reviewOnly(payload)});
  if(result.contains(feedback))document.getElementById('main').append(feedback);
  result.replaceChildren();result.hidden=false;
  const top=el('div','result-top');const title=el('h2','',action==='prepare'?'Review your prepared task':action==='compass'?'Project Compass review':'Review the result');
  const status=el('span','status-pill',String(payload.status||'review').replaceAll('_',' '));
  if(payload.needs_clarification||payload.status==='blocked'||payload.status==='unavailable')status.classList.add('warn');
  title.id='result-title';title.tabIndex=-1;result.setAttribute('aria-labelledby',title.id);
  top.append(title,status);result.append(top);
  if(restored)result.append(el('div','notice warning','Previous review from this tab. Sources may have changed. Preview again before requesting approval.'));
  if(action==='prepare'){
    const intent=payload.intent||{};
    facts(result,[['Interpreted goal',intent.goal],['Risk',payload.risk_level],['Task type',payload.task_type],['AI tool',intent.target_tool]]);
    result.append(el('p','muted','Risk describes the consequence of a wrong handoff. Approval boundaries identify actions to confirm before execution.'));
    if(payload.needs_clarification){
      const note=el('div','notice warning');note.append(el('strong','','More detail is needed. Answer these questions in your task, then prepare again.'));list(note,payload.questions);result.append(note);
      const revise=el('button','secondary','Revise task');revise.onclick=()=>{navigate('start');const input=document.getElementById('prepare-text');input.value=lastTask;input.focus()};result.append(revise);
    }
    section(result,'Approval boundaries',payload.approval_boundaries,'No consequential approval boundary was identified.');
    section(result,'Verification',payload.done_criteria,'No additional criterion supplied.');
    section(result,'Engineering guidance',payload.engineering_rules,'No additional engineering rule was needed.');
    section(result,'Context used',payload.context?.selected_paths,'No project document was supplied.');
    if(payload.routing?.reason)section(result,'AI tool and capability guidance',payload.routing.reason,'');
    if(payload.prompt){preparedPrompt=payload.prompt;result.append(el('h3','','Prepared instructions'));const pre=el('pre','prepared',payload.prompt);result.append(pre);const copy=el('button','primary','Copy Prepared Task');copy.onclick=()=>copyText(payload.prompt,copy);result.append(copy)}
  }else if(action==='compass'){
    for(const [name,value] of Object.entries(payload.fields||{})){
      const block=el('section','section');block.append(el('h3','',name.replaceAll('_',' ')));
      facts(block,[['Evidence state',value.status],['Current claim',value.value]]);
      for(const item of value.evidence||[])section(block,item.path+':'+item.line,item.text+' · '+(item.authoritative?'Owner-designated source':'Supporting source')+(item.stale?' · Stale — review required':''));
      result.append(block);
    }
    section(result,'Scope review',payload.task_scope?.explanation,'No task was supplied.');
    facts(result,[['Scope state',payload.task_scope?.status],['Further review required',payload.task_scope?.scope_review_required]]);
  }else{
    ui.summarize(result,action,payload);
  }
  if(payload.download){const save=el('button','secondary','Download reviewable artifact');save.onclick=()=>download(payload.download);result.append(save)}
  if(payload.approval_token){const box=el('div','approval');box.append(el('h3','','Explicit approval required'),el('p','','Review the full result above. Approval applies only to this exact preview; stale source and replay checks remain active.'));
    if(action==='outcomeLearn'){const label=el('label','','Owner approval reference');label.htmlFor='approval-ref';const input=el('input');input.id='approval-ref';input.required=true;input.placeholder='Issue, decision, or review reference';box.append(label,input)}
    const label=el('label','inline-label');const check=el('input');check.type='checkbox';label.append(check,el('span','','I reviewed this exact proposal and authorize this action.'));box.append(label);
    const button=el('button','primary',action==='handoffDispatch'?'Dispatch approved packet':'Apply approved proposal');button.disabled=true;check.onchange=()=>{button.disabled=!check.checked};
    let token=payload.approval_token;
    button.onclick=async()=>{const reference=box.querySelector('#approval-ref');if(reference&&!reference.reportValidity())return;if(!token||activeOperation)return;const exactToken=token;token=null;await operate(box,async()=>{const approved=await request('/api/approve',{approval_token:exactToken,approval_ref:reference?.value||''});show(action,approved)});button.disabled=true;check.disabled=true;if(button.isConnected)button.textContent='Preview again before another approval'};box.append(button);result.append(box);
  }
  const exact={...payload};delete exact.approval_token;
  const details=el('details');details.append(el('summary','','Advanced: exact result'),el('pre','',JSON.stringify(exact,null,2)));result.append(details);
  if(!restored){result.scrollIntoView({behavior:'instant',block:'start'});title.focus({preventScroll:true})}
}

async function copyText(text,button){result.insertBefore(feedback,button);try{await navigator.clipboard.writeText(text);inform('Prepared task copied. Paste it into your chosen AI tool; review its work afterward.')}catch{inform('Clipboard access was denied. Select and copy the prepared text above.',true,true)}}
result.addEventListener('copy-handoff',event=>copyText(event.detail,event.target.querySelector('button')));
workspace.addEventListener('input',()=>{const approval=result.querySelector('.approval');if(approval){approval.remove();result.append(el('p','notice warning','Inputs changed. Preview this workflow again before approval.'))}});

async function runAction(action,form) {
  const payload=await request('/api/action',{action,fields:await values(form)});show(action,payload);
}

function rootField(){return ['root','Git project folder','text',undefined,'Enter the exact root of a project you chose. IntentOS reads or writes only the supported project files.']}
function contextField(){return ['context_file','Project context path (relative to root)','text',undefined,'Only this explicit file is pinned; no repository scan is performed.']}

function renderStart(){
  const flow=el('div','flow');for(const item of ['Describe','Review','Copy','Handoff'])flow.append(el('span','',item));workspace.append(flow);
  const form=card('prepare','What would you like an AI tool to do?','A normal sentence is enough. You can revise it if IntentOS needs clarification.',[
    ['text','Your task','textarea'],['target','AI tool (optional)','select',[['','Detect from task'],['codex','Codex'],['claude-code','Claude Code'],['chatgpt','ChatGPT'],['cursor','Cursor']]],
    ['context','Project document (optional)','file',undefined,'Select a file only if you want its text included as context. No files are read automatically.'],
    ['authority','This is an owner-approved project source','checkbox',undefined,'Mark this only when the project owner accepted the document as authoritative.'],
  ],'Prepare task',async(form)=>{
    const v=await values(form);const file=form.querySelector('[name=context]').files[0];const documents=file?[{name:file.name,content:await file.text(),authoritative:v.authority}]:[];
    const payload=await request('/api/prepare',{text:v.text,target:v.target,documents});show('prepare',payload);
  });
  form.querySelector('[name=text]').placeholder='Codex: Refactor this function without changing behavior.';
  const note=el('div','notice');note.append(el('strong','','Before you hand off'),el('p','','Ready means the instructions are prepared. Your AI tool still needs the permissions you choose, and its result still needs verification.'));workspace.append(note);
}

function renderProject(){
  card('compass','Review selected project sources','Mark only genuinely approved sources as authoritative. The review does not change files.',[
    ['authoritative','Approved source (optional)','file'],['supporting','Additional source (optional)','file'],['task','Task to compare with scope (optional)','textarea'],
  ],'Review project',async(form)=>{
    const v=await values(form);const approved=form.querySelector('[name=authoritative]').files[0];const supporting=form.querySelector('[name=supporting]').files[0];const documents=[];
      if(approved)documents.push({name:approved.name,content:await approved.text(),authoritative:true});
      if(supporting)documents.push({name:supporting.name,content:await supporting.text(),authoritative:false});
    const payload=await request('/api/compass',{documents,task:v.task});show('compass',payload);
  });
}

const advanced={
  governance:[
    ['stateStatus','Propose a status update','Shows the exact proposed change before approval.',[rootField(),['current_phase','Current phase','text'],['next_action','Next action','text'],['evidence','Evidence or review reference','text']],'Preview status'],
    ['stateDecision','Record an approved decision','The owner reference and content are bound to the reviewed proposal.',[rootField(),['decision_id','Decision ID','text'],['title','Decision title','text'],['body','Decision text','textarea'],['approval_ref','Owner approval reference','text']],'Preview decision'],
    ['stateScope','Amend approved scope','One bounded amendment at a time. This never grants execution permission.',[rootField(),['amendment_id','Amendment ID','text'],['task','Exact task','textarea'],['reason','Reason','text'],['approval_ref','Owner approval reference','text']],'Preview amendment'],
    ['gates','Review requirements and readiness','Select an explicit evidence file. Ready means ready for owner review, not launch approval.',[['evidence','Requirement, milestone and check evidence (.json)','upload']],'Review gates'],
  ],
  delegation:[
    ['route','Review a model or tool recommendation','No provider is queried. Availability and cost metadata must come from a source you trust.',[['text','Task','textarea'],['target','AI tool (optional)','text'],['models','Supplied model metadata (.json, optional)','upload']],'Review route'],
    ['handoffPrepare','Prepare a portable handoff','Creates a downloadable packet. Preparation never starts an agent.',[rootField(),['text','Task','textarea'],['target','Target agent','select',[['codex','Codex'],['claude-code','Claude Code'],['chatgpt','ChatGPT'],['cursor','Cursor']]],['task_id','Task ID','text'],contextField()],'Prepare handoff'],
    ['handoffDispatch','Review Codex dispatch','Only Codex supports automatic dispatch. Read-only is the default; approval is separate.',[rootField(),['packet','Saved handoff packet (.json)','upload'],['sandbox','Sandbox','select',[['read-only','Read only'],['workspace-write','Workspace write']]],['model','Explicit Codex model (optional)','text']],'Preview dispatch'],
  ],
  recovery:[
    ['checkpointCreate','Save a checkpoint','Use an approved plan/state specification and one explicit context file.',[rootField(),['spec','Approved checkpoint specification (.json)','upload'],contextField()],'Create checkpoint'],
    ['checkpointReview','Review a continuation','Check the external ledger and approvals before relying on a resume review.',[rootField(),['checkpoint','Saved checkpoint (.json)','upload'],contextField(),['ledger_reviewed','I checked the external operation ledger','checkbox'],['executed_operation','Already executed operation ID (optional)','text'],['accepted_approval','Accepted approval ID (optional)','text'],['remaining_budget_tokens','Remaining token budget (optional)','text']],'Review continuation'],
  ],
  outcomes:[
    ['outcomeRecord','Record an externally checked result','Missing measures remain missing. Download the normalized record for later comparison.',[['evidence','Outcome evidence (.json)','upload']],'Record outcome'],
    ['outcomeCompare','Compare controlled task variants','Only comparable raw and prepared records can support a verdict.',[['raw','Raw arm record (.json)','upload'],['prepared','Prepared arm record (.json)','upload']],'Compare variants'],
    ['outcomeLearn','Review repeated evidence','Only repeated evidence can yield a lesson proposal. Saving it requires owner approval.',[['records','Two to eight outcome records (.json)','upload']],'Review lessons'],
  ],
};

function renderAdvanced(id){
  const note=el('div','notice warning');note.append(el('strong','','Advanced, evidence-based workflows'),el('p','','These operations use the existing Core 1.1 CLI contracts. Select files explicitly. JSON evidence is supplied by you; IntentOS does not attest its source.'));workspace.append(note);
  for(const [action,title,description,fields,button] of advanced[id]){
    const form=card(action,title,description,fields,button,(form)=>runAction(action,form));
    const example={route:'models',gates:'gates',checkpointCreate:'checkpoint',outcomeRecord:'outcome'}[action];
    if(example)ui.addExample(form,example,download);
  }
}

function navigate(id,moveFocus=false){
  if(activeOperation)return;
  document.getElementById('main').append(feedback);inform();
  if(workspace.childNodes.length)drafts.set(current,[...workspace.childNodes]);
  current=id;workspace.replaceChildren();result.replaceChildren();result.hidden=true;navigation.replaceChildren();
  const page=pages.find(item=>item.id===id)||pages[0];
  document.getElementById('eyebrow').textContent=page.label;document.getElementById('page-title').textContent=page.title;document.getElementById('page-description').textContent=page.description;
  for(const item of pages){const button=el('button',item.id===id?'active':'',item.label);button.type='button';button.setAttribute('aria-current',item.id===id?'page':'false');button.onclick=()=>navigate(item.id,true);navigation.append(button)}
  if(drafts.has(id))workspace.append(...drafts.get(id));
  else if(id==='start')renderStart();else if(id==='project')renderProject();else renderAdvanced(id);
  for(const input of workspace.querySelectorAll('input[name=root]'))if(!input.value)input.value=projectFolder;
  if(reviews.has(id)){const prior=reviews.get(id);show(prior.action,prior.payload,true)}
  window.scrollTo({top:0,behavior:'instant'});
  if(moveFocus)document.getElementById('main').focus({preventScroll:true});
}

document.getElementById('clear-session').onclick=()=>{if(activeOperation)return;if(!confirm('Clear drafts, selected files and reviews in this tab? This does not undo approved changes.'))return;drafts.clear();reviews.clear();workspace.replaceChildren();lastTask='';projectFolder='';preparedPrompt='';navigate('start',true)};

navigate('start');
