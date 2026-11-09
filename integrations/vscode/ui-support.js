/* Shared presentation only. Mirrored into the VSIX; a contract test checks equality. */
globalThis.IntentOSUI = (() => {
  const examples = {
    models: {title:'Model metadata',help:'Replace the example with metadata you checked. Keep verified and available false until you have evidence; no provider is queried.',value:{schema_version:1,models:[{name:'REPLACE_WITH_MODEL',provider:'REPLACE_WITH_PROVIDER',surfaces:['codex'],capability:'balanced',cost:'low',available:false,verified:false}]}},
    gates: {title:'Requirements and readiness',help:'Describe real acceptance checks and their evidence references. Unknown checks stay null. Approval fields must reflect an actual owner decision.',value:{schema_version:1,requirements:[{key:'R01',outcome:'REPLACE_WITH_REQUIRED_OUTCOME',checks:['focused-check'],accepted_by_owner:false,approval_ref:''}],milestones:[{key:'M01',requirement_keys:['R01'],state:'proposed',approval_ref:''}],evidence:[{requirement_key:'R01',check:'focused-check',passed:null,source_ref:'',source_revision:'',independently_reviewed:false}]}},
    checkpoint: {title:'Checkpoint specification',help:'List the plan actually approved by the owner, cite the observed state, and name the next step. Empty approval references must be completed before saving. Do not invent completed work.',value:{task_id:'REPLACE_WITH_TASK_ID',approved_plan:[{step_id:'review',action:'Review the agreed change'},{step_id:'verify',action:'Run the agreed checks'}],plan_approval_ref:'',state_summary:'REPLACE_WITH_OBSERVED_STATE',state_evidence_ref:'',completed:[],next_step_id:'review',operation_ids:[],required_approval_ids:['owner-review'],estimated_remaining_tokens:null}},
    outcome: {title:'External outcome evidence',help:'Use one real task and its actual execution conditions. Checks and measures stay null until observed. For comparison, keep both arms on identical conditions. This template is not outcome evidence.',value:{schema_version:1,task_id:'REPLACE_WITH_TASK_ID',variant:'raw',conditions:{executor:'',model:'',effort:'',base_revision:'',context:'',permissions:'',environment:''},checks:[{name:'REPLACE_WITH_ACCEPTANCE_CHECK',passed:null,evidence_ref:''}],execution_success:null,metrics:{input_tokens:null,output_tokens:null},source_ref:'',friction:'',rework:'',context_gap:'',verification_gap:'',lesson_hint:''}}
  };
  function node(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=String(text);return e}
  function block(parent,title,value){if(value===undefined||value===null||value==='')return;const box=node('section','section');box.append(node('h3','',title));for(const item of Array.isArray(value)?value:[value]){box.append(node('p','',typeof item==='object'?JSON.stringify(item):item))}parent.append(box)}
  function facts(parent,items){const grid=node('div','summary-facts');for(const [label,value]of items){if(value===undefined)continue;const box=node('div','fact');box.append(node('small','',label),node('strong','',value===null||value===''?'Not supplied':value));grid.append(box)}parent.append(grid)}
  const explanations={ready:'Ready for review and handoff. The downstream work has not been performed or verified.',clarification:'Add the requested detail, then prepare again.',blocked:'Review the missing evidence or approvals below before trying again.',needs_review:'Resolve the review items before requesting approval.',ready_for_owner_review:'Evidence is ready for an owner decision. This does not authorize execution or launch.',update:'Proposed change only. No project file has been changed.',applied:'The exact approved proposal was applied. Review the changed file before continuing.',saved:'A reviewable artifact was saved. Saving does not execute an agent.',recorded:'The supplied observation was recorded. IntentOS has not independently verified its source.',proposal:'Repeated supplied evidence suggests a lesson. Review it before saving; runtime policy is unchanged.',approved_proposal:'The approved lesson proposal was saved. Runtime policy is unchanged.',inconclusive:'The supplied evidence does not establish a winner.',unavailable:'This operation is unavailable. Use the documented manual handoff instead.'};
  function explanation(status){return explanations[status]||'Review the supplied evidence and exact result before choosing the next action.'}
  function summarize(parent,action,payload){
    parent.append(node('p','result-guidance',explanation(payload.status)));
    if(action==='compass'){
      for(const [name,field]of Object.entries(payload.fields||{})){
        block(parent,name.replaceAll('_',' '),field.value||'No supported claim was supplied.');
        facts(parent,[['Evidence state',field.status]]);
        for(const source of field.evidence||[])block(parent,source.path+':'+source.line,source.text+' · '+(source.authoritative?'Owner-designated source':'Supporting source')+(source.stale?' · Stale — review required':''));
      }
      block(parent,'Scope review',payload.task_scope?.explanation);facts(parent,[['Scope state',payload.task_scope?.status]]);
    }else if(action==='route'){
      facts(parent,[['AI tool',payload.target_tool],['Risk',payload.risk_level],['Capability',payload.required_capability],['Effort',payload.effort],['Recommended model',payload.selected_model],['Fallback',payload.fallback?'Yes — no verified selection':'No']]);
      block(parent,'Recommendation and limits',payload.reason);block(parent,'Metadata source',payload.metadata_source);
      const candidates=payload.candidates||[];for(const item of candidates){block(parent,item.name,item.reasons||item.reason||[item.eligible?'Eligible in the supplied catalog':'Not eligible in the supplied catalog'])}
    }else if(action.startsWith('state')){
      block(parent,'Review before approval',payload.reason||payload.next_action);block(parent,'Evidence reference',payload.evidence_ref||payload.approval_ref);
      if(payload.diff_preview){parent.append(node('h3','','Exact proposed change'),node('pre','diff',payload.diff_preview))}else block(parent,'Review items',payload.blockers||payload.reasons);
    }else if(action==='handoffPrepare'){
      facts(parent,[['AI tool',payload.target_tool],['Risk',payload.risk_level]]);block(parent,'Approval boundaries',payload.approval_boundaries);
      let packet=payload.packet_preview;try{packet=packet||JSON.parse(payload.download?.content||'null')}catch{}
      const prompt=packet?.handoff?.prepared_prompt;if(prompt){parent.append(node('h3','','Portable prepared instructions'),node('pre','prepared',prompt));const copy=node('button','secondary','Copy handoff instructions');copy.type='button';copy.onclick=()=>parent.dispatchEvent(new CustomEvent('copy-handoff',{bubbles:true,detail:prompt}));parent.append(copy)}
      block(parent,'Next step','Save the packet for later review, or copy its instructions into your chosen AI tool. Preparation never starts an agent.');
    }else if(action==='handoffDispatch'){
      block(parent,'Dispatch review',payload.reason||payload.next_action);block(parent,'Approval boundaries',payload.approval_boundaries);block(parent,'Execution evidence is separate','Approve only this exact packet and sandbox. A completed agent turn does not prove the task is correct.');
    }else if(action==='checkpointCreate'||action==='checkpointReview'){
      facts(parent,[['Task',payload.task_id],['Next step',payload.next_step_id],['Execution authorized',payload.approved_to_execute===false?'No':undefined]]);
      block(parent,'Review items',payload.blockers||payload.reasons||payload.reason);block(parent,'Suggested continuation',payload.continuation||payload.next_action);
      block(parent,'Next step','Keep the checkpoint with your task evidence. Resolve stale context, ledger entries and required approvals before an owner reviews continuation. No agent is restarted.');
    }else if(action==='gates'){
      block(parent,'Launch is not approved','This report organizes supplied checks for owner review. It does not authorize launch.');block(parent,'Review items',payload.blockers||payload.reasons||payload.reason);
      const rows=payload.requirements||payload.requirement_reviews||[];if(Array.isArray(rows))for(const item of rows){block(parent,item.key||item.requirement_key||'Requirement',item.status||item.state||item.outcome)}
      for(const finding of payload.findings||[])block(parent,finding.key+' — '+finding.status,[finding.reason,...(finding.evidence_ref?[finding.evidence_ref]:[])]);
    }else if(action==='outcomeCompare'){
      const comparison=payload.comparison||{};facts(parent,[['Verdict',comparison.winner||payload.status]]);block(parent,'Reason',payload.reason||comparison.reason);
      block(parent,'How to read this result','Correctness takes priority. Missing measures stay unknown; inconclusive means the evidence does not support a winner.');
      const metrics=Object.entries(comparison).filter(([key])=>key.endsWith('_delta'));if(metrics.length)facts(parent,metrics.map(([key,value])=>[key.replaceAll('_',' '),value]));
    }else if(action==='outcomeLearn'){
      for(const proposal of payload.proposals||[]){block(parent,'Proposed lesson',proposal.rule||proposal.recommendation);block(parent,'Observed task references',proposal.evidence_cases);block(parent,'Evidence sources',proposal.source_refs)}block(parent,'Review items',payload.reason||payload.reasons);
      block(parent,'Policy boundary','Saving a lesson proposal records a reviewed suggestion. It never changes runtime policy.');
    }else if(action==='outcomeRecord'){
      let record;try{record=JSON.parse(payload.download?.content||'null')}catch{}
      if(record){facts(parent,[['Task',record.task_id],['Variant',record.variant],['Reported execution',record.execution_success===null?'Not observed':record.execution_success?'Succeeded':'Failed']]);for(const check of record.checks||[])block(parent,check.name,(check.passed===null?'Unverified':check.passed?'Passed':'Failed')+(check.evidence_ref?' · '+check.evidence_ref:''));block(parent,'External source',record.source_ref)}
      block(parent,'Next step','Save this normalized record. Compare it only with the other arm of the same task under identical execution conditions.');
    }
  }
  function addExample(parent,key,onSave){const sample=examples[key];if(!sample)return;const details=node('details','input-guide');details.append(node('summary','','File format and example: '+sample.title),node('p','',sample.help),node('p','hint','Example only. Replace placeholders with actual evidence; never treat example approvals or measurements as facts.'),node('pre','',JSON.stringify(sample.value,null,2)));const button=node('button','secondary','Save example JSON');button.type='button';button.onclick=()=>onSave({filename:'intentos-'+key+'-example.json',content:JSON.stringify(sample.value,null,2)+'\n'});details.append(button);parent.append(details)}
  function reviewOnly(payload){const copy={...payload};delete copy.approval_token;delete copy.approval_digest;return copy}
  return {examples,explanation,summarize,addExample,reviewOnly};
})();
if(typeof module!=='undefined'&&module.exports)module.exports=globalThis.IntentOSUI;
