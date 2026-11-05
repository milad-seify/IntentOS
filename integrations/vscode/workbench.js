const { randomBytes } = require('crypto');

function nonce() {
  return randomBytes(16).toString('hex');
}

function sidebarHtml() {
  const key = nonce();
  return `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'nonce-${key}'; script-src 'nonce-${key}';"><meta name="viewport" content="width=device-width,initial-scale=1"><style nonce="${key}">
    body{font-family:var(--vscode-font-family);color:var(--vscode-foreground);padding:18px;line-height:1.5}
    h1{font-size:18px;margin:0 0 8px}p{color:var(--vscode-descriptionForeground)}
    button{display:block;width:100%;margin:12px 0;padding:10px;border:0;border-radius:4px;cursor:pointer;background:var(--vscode-button-background);color:var(--vscode-button-foreground)}
    button.secondary{background:var(--vscode-button-secondaryBackground);color:var(--vscode-button-secondaryForeground)}
    button:focus-visible{outline:2px solid var(--vscode-focusBorder);outline-offset:2px}
  </style></head><body><h1>IntentOS</h1><p>Prepare a clear task, review its boundaries, then choose how to hand it off.</p><button id="open">Open workbench</button><button class="secondary" id="selection">Prepare selected text</button><script nonce="${key}">
    const vscode=acquireVsCodeApi();document.getElementById('open').onclick=()=>vscode.postMessage({type:'open'});document.getElementById('selection').onclick=()=>vscode.postMessage({type:'selection'});
  </script></body></html>`;
}

function workbenchHtml() {
  const key = nonce();
  return `<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'nonce-${key}'; script-src 'nonce-${key}';"><meta name="viewport" content="width=device-width,initial-scale=1"><style nonce="${key}">
    :root{color-scheme:light dark}*{box-sizing:border-box}body{margin:0;color:var(--vscode-foreground);background:var(--vscode-editor-background);font:13px/1.5 var(--vscode-font-family)}
    .shell{max-width:1100px;margin:auto;padding:24px clamp(16px,3vw,36px)}header{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;margin-bottom:24px}
    h1{font-size:24px;line-height:1.2;margin:0 0 4px}h2{font-size:17px;margin:0 0 5px}main h2:focus{outline:none}h3{font-size:14px;margin:16px 0 5px}p{margin:0 0 14px;color:var(--vscode-descriptionForeground)}
    .eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--vscode-descriptionForeground);font-weight:700}
    nav{display:flex;gap:6px;flex-wrap:wrap;border-bottom:1px solid var(--vscode-panel-border);margin-bottom:24px;padding-bottom:8px}
    nav button{background:transparent;color:var(--vscode-foreground);border:1px solid transparent}nav button.active{border-color:var(--vscode-focusBorder);background:var(--vscode-list-activeSelectionBackground);color:var(--vscode-list-activeSelectionForeground)}
    button{font:inherit;border:0;border-radius:4px;cursor:pointer;padding:8px 12px;background:var(--vscode-button-background);color:var(--vscode-button-foreground)}button:hover{background:var(--vscode-button-hoverBackground)}button.secondary{background:var(--vscode-button-secondaryBackground);color:var(--vscode-button-secondaryForeground)}button:disabled{opacity:.55;cursor:default}
    button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--vscode-focusBorder);outline-offset:2px}
    .panel{border:1px solid var(--vscode-panel-border);border-radius:8px;padding:20px;background:var(--vscode-sideBar-background)}
    .workflow{border:1px solid var(--vscode-panel-border);border-radius:7px;padding:18px;margin:14px 0;background:var(--vscode-editor-background)}
    label{display:block;font-weight:600;margin:12px 0 5px}input,textarea,select{width:100%;font:inherit;color:var(--vscode-input-foreground);background:var(--vscode-input-background);border:1px solid var(--vscode-input-border,var(--vscode-panel-border));border-radius:4px;padding:9px;min-height:36px}textarea{min-height:96px;resize:vertical}input[type=checkbox]{width:auto;min-height:0;margin-right:6px}
    .file{display:flex;gap:7px}.file input{min-width:0;flex:1}.file button{white-space:nowrap}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:17px}.result{margin-top:22px}.result[hidden],section[hidden]{display:none}
    .notice{border-left:3px solid var(--vscode-focusBorder);padding:10px 13px;background:var(--vscode-editorWidget-background);margin:14px 0}.notice.error{border-color:var(--vscode-errorForeground)}.notice.warn{border-color:var(--vscode-editorWarning-foreground)}
    .facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:16px 0}.fact{border:1px solid var(--vscode-panel-border);border-radius:5px;padding:11px}.fact b{display:block;font-size:11px;color:var(--vscode-descriptionForeground);font-weight:500}.fact span{font-weight:600;overflow-wrap:anywhere}
    .item{border-top:1px solid var(--vscode-panel-border);padding:12px 0}.item:first-child{border-top:0}.item strong{display:block}.item small{color:var(--vscode-descriptionForeground)}
    pre{white-space:pre-wrap;overflow-wrap:anywhere;background:var(--vscode-textCodeBlock-background);padding:14px;border-radius:5px;max-height:480px;overflow:auto}details{margin-top:14px}summary{cursor:pointer;font-weight:600}
    @media(max-width:680px){.shell{padding:16px}header{display:block}.panel{padding:14px}.file{flex-wrap:wrap}.file button{width:100%}}
  </style></head><body><div class="shell"><header><div><div class="eyebrow">Reliable AI delegation</div><h1>IntentOS workbench</h1><p>Prepare, review, and hand off with clear boundaries. Your AI tool performs the work.</p></div><span class="eyebrow">Local CLI</span></header><nav id="nav" aria-label="Workbench sections"></nav><main id="main"></main><div id="feedback" role="status" aria-live="polite"></div><section id="result" class="panel result" aria-live="polite" hidden></section></div><script nonce="${key}">
  const vscode=acquireVsCodeApi();
  const sections=[
    {id:'start',label:'Start',title:'Prepare a task',intro:'Describe the outcome. IntentOS will show its interpretation, risk, approvals, and what to verify.',forms:[
      {action:'prepare',title:'New task',description:'No provider account is required. Select project context only when you want IntentOS to use it.',fields:[['text','What do you want to achieve?','textarea'],['target','AI tool (optional)','select','', ['','codex','claude-code','chatgpt','cursor']],['context_file','Project context file (optional)','file']],button:'Prepare task'}]},
    {id:'project',label:'Project',title:'Project Compass',intro:'Review only the project documents you choose. Missing and conflicting facts stay visible.',forms:[
      {action:'compass',title:'Review project direction',description:'Mark a source authoritative only when you know it is approved. File and line provenance will be shown.',fields:[['authoritative_document','Approved project source','file'],['document','Additional source (optional)','file'],['task','Task to check against scope (optional)','text']],button:'Review project'}]},
    {id:'governance',label:'Govern',title:'Project governance',intro:'Preview changes and evidence before any persistent update. A digest is an approval assertion, not proof of identity.',forms:[
      {action:'stateStatus',title:'Status update',description:'Propose one current phase and next action. Approval is a separate step.',fields:[['current_phase','Current phase','text'],['next_action','Next action','text'],['evidence','Evidence reference','text']],button:'Preview status'},
      {action:'stateDecision',title:'Decision',description:'Record an externally approved decision after reviewing the exact diff.',fields:[['decision_id','Decision ID','text'],['title','Decision title','text'],['body','Decision text','textarea'],['approval_ref','Owner approval reference','text']],button:'Preview decision'},
      {action:'stateScope',title:'Scope amendment',description:'A scope amendment does not authorize agent execution.',fields:[['amendment_id','Amendment ID','text'],['task','Exact task','textarea'],['reason','Reason','text'],['approval_ref','Owner approval reference','text']],button:'Preview amendment'},
      {action:'gates',title:'Requirements and readiness',description:'Choose an existing evidence file. Ready means ready for owner review, never launch approval.',fields:[['file','Requirements and check evidence (.json)','file']],button:'Review gates'}]},
    {id:'delegate',label:'Delegate',title:'Agent and routing',intro:'Recommendations use supplied metadata. IntentOS does not check live prices or provider availability.',forms:[
      {action:'route',title:'Review a route',description:'Without a model catalogue, IntentOS explains the safe capability and effort fallback.',fields:[['text','Task','textarea'],['target','AI tool (optional)','select','',['','codex','claude-code','chatgpt','cursor']],['models_file','Model metadata (.json, optional)','file']],button:'Review recommendation'},
      {action:'handoffPrepare',title:'Portable handoff',description:'Save a reviewable packet. Preparation never runs an agent.',fields:[['text','Task','textarea'],['target','AI tool','select','codex',['codex','claude-code','chatgpt','cursor']],['task_id','Task ID','text'],['context_file','Project context (optional)','file'],['output','Save packet as','save']],button:'Prepare handoff'},
      {action:'handoffDispatch',title:'Codex dispatch',description:'Preview an existing packet first. Read-only is the default; completion remains unverified.',fields:[['file','Saved handoff packet','file'],['sandbox','Sandbox','select','read-only',['read-only','workspace-write']],['model','Explicit model (optional)','text']],button:'Preview dispatch'}]},
    {id:'recovery',label:'Recover',title:'Checkpoints and recovery',intro:'Review source revision, selected context and external operation evidence. Resume never executes automatically.',forms:[
      {action:'checkpointCreate',title:'Save a checkpoint',description:'Select the approved plan/state specification and at least one context file.',fields:[['spec','Approved plan and state (.json)','file'],['context_file','Project context','file'],['output','Save checkpoint as','save']],button:'Save checkpoint'},
      {action:'checkpointReview',title:'Review continuation',description:'If you checked the external operation ledger, record already executed operations and approvals.',fields:[['checkpoint','Saved checkpoint','file'],['context_file','Project context','file'],['ledger_reviewed','I checked the external operation ledger','checkbox'],['executed_operation','Already executed operation ID (optional)','text'],['accepted_approval','Accepted approval ID (optional)','text'],['remaining_budget_tokens','Remaining token budget (optional)','text']],button:'Review continuation'}]},
    {id:'outcomes',label:'Outcomes',title:'Outcome evidence',intro:'Record only externally observed results. Missing checks stay unknown and comparisons can be inconclusive.',forms:[
      {action:'outcomeRecord',title:'Record an outcome',description:'Choose a caller-supplied evidence file and a new output path.',fields:[['file','Outcome evidence (.json)','file'],['output','Save normalized record as','save']],button:'Record outcome'},
      {action:'outcomeCompare',title:'Compare task variants',description:'Both records must describe the same task and controlled conditions.',fields:[['raw','Raw arm record','file'],['prepared','Prepared arm record','file']],button:'Compare variants'},
      {action:'outcomeLearn',title:'Review repeated lessons',description:'Repeated external failures may produce a proposal. Saving it needs an exact approval and never changes runtime policy.',fields:[['record1','Outcome record 1','file'],['record2','Outcome record 2','file'],['approval_ref','Owner approval reference','text'],['output','Save approved proposal as','save']],button:'Review lessons'}]}
  ];
  const nav=document.getElementById('nav'),main=document.getElementById('main'),result=document.getElementById('result'),feedback=document.getElementById('feedback');
  const fileFields=new Set();let current='start';
  function element(tag,cls,text){const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node}
  function renderSection(id){current=id;nav.replaceChildren();main.replaceChildren();result.hidden=true;feedback.textContent='';fileFields.clear();
    for(const section of sections){const button=element('button',section.id===id?'active':'',section.label);button.type='button';button.setAttribute('aria-current',section.id===id?'page':'false');button.onclick=()=>renderSection(section.id);nav.append(button)}
    const section=sections.find(item=>item.id===id);const heading=element('h2','',section.title);heading.tabIndex=-1;main.append(heading,element('p','',section.intro));
    for(const formSpec of section.forms){const form=element('form','workflow');form.dataset.action=formSpec.action;form.append(element('h3','',formSpec.title),element('p','',formSpec.description));
      for(const [name,label,type,initial,options] of formSpec.fields){const fieldId=formSpec.action+'-'+name;const caption=element('label','',label);caption.htmlFor=fieldId;form.append(caption);let input;
        if(type==='textarea')input=element('textarea');else if(type==='select'){input=element('select');for(const option of options){const item=element('option','',option||'Detect from task');item.value=option;input.append(item)}input.value=initial||''}
        else{input=element('input');input.type=type==='checkbox'?'checkbox':'text'}
        input.id=fieldId;input.name=name;if(initial&&type!=='select')input.value=initial;
        if(type==='file'||type==='save'){input.readOnly=true;fileFields.add(fieldId);const wrap=element('div','file');const pick=element('button','secondary',type==='save'?'Choose location':'Choose file');pick.type='button';pick.onclick=()=>vscode.postMessage({type:'pickFile',field:fieldId,save:type==='save'});wrap.append(input,pick);form.append(wrap)}else form.append(input);
      }
      const actions=element('div','actions');const submit=element('button','',formSpec.button);submit.type='submit';actions.append(submit);if(formSpec.action==='prepare'){const selected=element('button','secondary','Use selected editor text');selected.type='button';selected.onclick=()=>vscode.postMessage({type:'useSelection'});actions.append(selected)}form.append(actions);
      form.onsubmit=(event)=>{event.preventDefault();const fields={};for(const input of form.querySelectorAll('[name]'))fields[input.name]=input.type==='checkbox'?input.checked:input.value;feedback.textContent='Working locally…';result.hidden=true;vscode.postMessage({type:'run',action:formSpec.action,fields})};main.append(form);
    }
    window.scrollTo(0,0);heading.focus({preventScroll:true});
  }
  function addValue(parent,label,value){const row=element('div','item');row.append(element('strong','',label));if(Array.isArray(value)){if(!value.length)row.append(element('small','','None supplied'));for(const item of value)addValue(row,'',item)}else if(value&&typeof value==='object'){for(const [key,item] of Object.entries(value))addValue(row,key.replaceAll('_',' '),item)}else row.append(element('span','',value===null||value===undefined?'Unknown':String(value)));parent.append(row)}
  function showResult(action,payload){feedback.textContent='';result.hidden=false;result.replaceChildren();result.append(element('div','eyebrow',action.replace(/([A-Z])/g,' $1')));result.append(element('h2','',payload.status==='ready'?'Ready for review':payload.needs_clarification?'Needs clarification':String(payload.status||'Review')));
    if(action==='prepare'){const intent=payload.intent||{};const facts=element('div','facts');for(const [label,value] of [['Goal',intent.goal],['Risk',payload.risk_level],['Task',payload.task_type],['Agent',intent.target_tool]]){const card=element('div','fact');card.append(element('b','',label),element('span','',value||'Not specified'));facts.append(card)}result.append(facts);
      result.append(element('p','','Risk describes the consequence of a wrong or unsafe handoff. Approval boundaries name actions to confirm before execution.'));
      for(const [label,value] of [['Clarification questions',payload.questions],['Approval boundaries',payload.approval_boundaries],['Project context and source reasons',payload.context?.selected],['Verification',payload.done_criteria],['Engineering guidance',payload.engineering_rules]]){if(label==='Clarification questions'&&!value?.length)continue;const heading=element('h3','',label);result.append(heading);addValue(result,'',value||[])}
      if(payload.routing?.reason){result.append(element('h3','','Agent and capability guidance'),element('p','',payload.routing.reason))}
      if(payload.prompt){result.append(element('h3','','Prepared task'),element('pre','',payload.prompt));const copy=element('button','','Copy Prepared Task');copy.onclick=()=>vscode.postMessage({type:'copyPreparedTask'});result.append(copy)}
      if(payload.needs_clarification){const retry=element('button','','Answer and retry');retry.onclick=()=>vscode.postMessage({type:'retry'});result.append(retry)}
    }else{for(const [name,value] of Object.entries(payload)){if(name==='schema_version')continue;addValue(result,name.replaceAll('_',' '),value)}
      if(payload.approval_digest&&(action.startsWith('state')||action==='handoffDispatch'||action==='outcomeLearn')){const approve=element('button','','Approve exact reviewed action');approve.onclick=()=>vscode.postMessage({type:'apply'});result.append(approve)}
    }
    const details=element('details');details.append(element('summary','','Advanced: exact CLI result'),element('pre','',JSON.stringify(payload,null,2)));result.append(details);result.scrollIntoView({behavior:'smooth',block:'start'});
  }
  window.addEventListener('message',(event)=>{const message=event.data;if(!message||typeof message!=='object')return;
    if(message.type==='picked'){const input=document.getElementById(message.field);if(input&&fileFields.has(message.field))input.value=message.path||''}
    if(message.type==='selection'){const input=document.getElementById('prepare-text');if(input){input.value=message.text||'';input.focus()}}
    if(message.type==='result')showResult(message.action,message.payload);
    if(message.type==='error'){feedback.textContent=message.message;feedback.className='notice error'}
  });renderSection('start');
  </script></body></html>`;
}

module.exports = { sidebarHtml, workbenchHtml };
