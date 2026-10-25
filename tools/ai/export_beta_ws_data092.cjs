'use strict';
// Resolve the already source-checked inheritance once for static WS tables.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {personality,scalarSchema}=require('./beta_js092/profiles.cjs');
const {BetaHandler}=require('./beta_js092/handlers.cjs');
const names=['p_Monster_Practice','p_Nilfgaard_Practice','p_NorthernRealms_Practice',"p_Scoia'tael_Practice",'p_Skellige_Practice'];
let deckBindings=[];
if(process.argv[3]){
 const mapping=JSON.parse(fs.readFileSync(path.resolve(process.argv[3]),'utf8'));
 const technical=process.argv.includes('--technical')&&mapping.scope==='technical-candidate-profiles';
 if(mapping.validated!==true&&!technical)throw Error('Shipping deck/profile mapping must have completed validation');
 deckBindings=technical?[]:mapping.assignments;
 if(!Array.isArray(deckBindings)||new Set(deckBindings.map(x=>x.presetId)).size!==deckBindings.length)throw Error('Unique preset bindings required');
 for(const name of technical?mapping.profiles:deckBindings.map(x=>x.profile)){const p=personality(name);
  if(p.TreeSearchType!=='AlphaBeta'||p.EvaluatorType!=='MiniMax'||p.CardPickerType!=='BestCardForPersonality')throw Error('Unported selected path '+name);
  if(!names.includes(name))names.push(name);
 }
}
const templates=require('./beta_js092/data/templates.json');
const out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});
const inputs={};for(const f of ['profiles.cjs','handlers.cjs','data/profile-scalars.json','data/personalities.json','data/templates.json','data/summations.json','data/request-hints.json','data/request-template-info.json'])inputs[f]=crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'beta_js092',f))).digest('hex');
const profiles=names.map(n=>personality(n)),handlerDefinitions=[],seen=new Map();
function register(h){
 const children=h.children.map(register),entries=h.sheet?.entries.map(e=>({weight:e.weight,scoring:e.scoring,rounds:e.rounds}))||[];
 const d={kind:h.kind,settings:h.settings,propagate:h.propagate,hasSheet:h.sheet!==null,children,entries},key=JSON.stringify(d);
 if(seen.has(key))return seen.get(key);const id=handlerDefinitions.length+1;handlerDefinitions.push({id,...d});seen.set(key,id);return id;
}
for(const p of profiles)for(const a of Object.values(p.associations).flat())a.handlerDefinitionId=register(new BetaHandler(a.attributes.Handler,a.settings,Number(a.attributes.ScoreToPropagate??0)));
const requestHints=require('./beta_js092/data/request-hints.json'),requestTemplateInfo=require('./beta_js092/data/request-template-info.json');
fs.writeFileSync(path.join(out,'source-data.json'),JSON.stringify({schema:1,inputs,scalarSchema,profiles,templates,handlerDefinitions,requestHints,requestTemplateInfo,deckBindings},null,2)+'\n');
console.log(JSON.stringify({profiles:names.length,templates:Object.keys(templates).length,out}));
