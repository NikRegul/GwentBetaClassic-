'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {BetaHandler,decision}=require('./beta_js092/handlers.cjs');
const {personality}=require('./beta_js092/profiles.cjs');
const templates=require('./beta_js092/data/templates.json');
const stage=path.resolve(process.argv[2]),rules=path.resolve(process.argv[3]);
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n')+'\n'+fs.readFileSync(path.join(stage,'ws-stage.js'),'utf8');
const ws=new Function(source+`return {handler:id=>BetaOriginalCreateHandler(id,null),item:()=>new SBetaOriginalItem(),request:()=>new SBetaOriginalRequest(),
 context:()=>new CBetaOriginalHandlerContext(),row:()=>new SBetaOriginalRow(),node:()=>new CBetaOriginalNode(),
 profile:(f,name)=>{let p=new CBetaOriginalPersonality();if(name&&typeof p.InitializeNamed==='function'){if(!p.InitializeNamed(name))throw Error('Named source profile '+name);}else p.Initialize(f);return p;}};`)();
const data=JSON.parse(fs.readFileSync(path.join(stage,'source-data.json'),'utf8'));
let checks=0,filters=0,decisions=0;
const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;},near=(a,b,n)=>{assert(Math.abs(a-b)<.0001,n+': '+a+' != '+b);checks++;};
function rng(seed){let value=seed>>>0,calls=0;return {calls:()=>calls,next:n=>{assert(n>0);calls++;value=(Math.imul(value,1664525)+1013904223)>>>0;return value%n;}};}
const list=Object.values(templates).filter(t=>t.type===4||t.type===2||t.type===8);
function card(t,i,template=false){const side=i%2+1,zone=[1,2,4,8,16,32,64,128][Math.floor(i/2)%8];
 return {id:template?t.id:i+1,templateId:t.id,side,zone,index:Math.floor(i/16),power:Math.max(0,t.power+(i%5)-2),basePower:t.power,
  templateTier:t.tier,type:t.type,tokens:t.tokens|(i%3===0?8:0)|(i%4===0?1:0),visibleToBoth:i%3!==0,inExecution:i%7===0,
  semanticTags:t.semanticTags,categories:t.categories,placement:t.placement};}
const cards=list.filter((t,i)=>i%7===0).slice(0,64).map((t,i)=>card(t,i));
const rows=[1,2].flatMap(side=>[1,2,4].map((row,i)=>({side,row,token:[0,128,1][(i+side)%3]})));
function typed(x){return Object.assign(ws.item(),x,{typeMask:x.type||0,row:x.row||0});}
function key(x,k){return k==='play'?`${x.side}:${x.row}:${x.index}`:k==='locations'?`${x.side}:${x.row}`:x.id;}
function check(js,target,p,typedP,kind,actor,min,max,seed,label){
 const nextA=rng(seed),nextB=rng(seed),raw=kind==='play'?[1,2].flatMap(side=>[1,2,4].flatMap(row=>[0,1,2,3].map(index=>({side,row,index})))):
  kind==='locations'?rows.map(({side,row})=>({side,row})):kind==='templates'?list.slice(20,44).map((t,i)=>card(t,i,true)):cards.slice(0,24);
 const node={},ctx={node,actor,personality:p,state:{cards,rows,roundIndex:seed%3},next:(a,b)=>a+nextA.next(b-a)},request={kind,items:raw,min,max};
 const context=ws.context();context.node=ws.node();context.p=typedP;context.actor=actor;context.roundIndex=seed%3;
 context.cards=cards.map(typed);context.rows=rows.map(r=>Object.assign(ws.row(),r));context.random={NextBounded:n=>nextB.next(n)};
 const req=ws.request();req.kind=kind;req.minimum=min;req.maximum=max;req.items=raw.map(typed);
 const a=js.filter(ctx,request),b=target.Filter(context,req);assert(!context.failed,label+': '+context.error);
 eq(b.valid,a!==null,label+' filter presence');eq(b.items.map(x=>key(x,kind)),a?.map(x=>key(x,kind))||[],label+' filter order');filters++;
 const c=decision(js,ctx,request),d=target.Decision(context,req);assert(!context.failed,label+': '+context.error);
 eq(d.chosen.map(x=>key(x,kind)),c.chosen.map(x=>key(x,kind)),label+' selected');
 eq(d.branches.map(x=>key(x,kind)),c.branches.map(x=>key(x[0],kind)),label+' siblings');
 eq(d.sourceFallback,c.sourceFallback,label+' original request-order repair');near(d.propagated,c.propagated,label+' propagated score');
 eq(nextB.calls(),nextA.calls(),label+' exact SimulatorRandom consumption');decisions++;
}
for(const [pi,sourceP]of data.profiles.entries()){
 const faction=[2,4,8,16,32][pi],p=personality(sourceP.name),typedP=ws.profile(faction,sourceP.name);
 eq(typedP.profileName,sourceP.name,'Exact named source profile');
 for(const key of Object.keys(data.scalarSchema)){
  if(key==='ExplorationConstant')near(typedP[key],p[key],'Unused MCTS double represented by native float');
  else eq(typedP[key],p[key],'Named profile scalar '+sourceP.name+'/'+key);
 }
 eq(typedP.semanticTags.map(t=>[t.id,t.usage,t.rounds,t.weight]),p.semanticTags.map(t=>[t.id,t.usage,t.rounds,t.weight]),'Named semantic tags and original order');
 const expected=Object.values(sourceP.associations).flatMap((items,i)=>items.map(a=>[i+1,Number(a.attributes.TemplateId),Number(a.attributes.AIHIntId??1),a.handlerDefinitionId]));
 eq(typedP.associations.map(a=>[a.kind,a.templateId,a.sourceHint,a.handlerId]),expected,'Exact four source association lists');
 for(const a of Object.values(sourceP.associations).flat()){
  const js=new BetaHandler(a.attributes.Handler,a.settings,Number(a.attributes.ScoreToPropagate??0)),target=ws.handler(a.handlerDefinitionId);
  for(const [k,v]of Object.entries(js.settings))eq(target[k],v,'Normalized source setting '+k);
  for(const kind of ['play','locations','targets','choices','templates'])for(const actor of [1,2])for(const [min,max]of [[0,0],[1,1],[0,3],[2,3]])
   check(js,target,p,typedP,kind,actor,min,max,900+filters,sourceP.name+'/'+a.attributes.Handler+'/'+kind);
 }
}
// Families/settings not selected by the five Practice profiles still need to
// retain the source algorithms when instantiated explicitly.
const settings=[['Preference',{}],['Occurrence',{}],['OccurrenceRange',{MinRange:1,MaxRange:3}],['OccurrenceRange',{}],['Occurrence',{Destination:'Deck'}],
 ['Wedge',{WedgeType:'InBetween'}],['Wedge',{WedgeType:'RightOf',SemanticTagId:3,Negate:true}],['PowerRange',{MinRange:2,MaxRange:0}],
 ['Health',{Health:2}],['UnitOrEvent',{UnitOrEvent:4}],['Location',{Location:8,LocationAction:'IsAtLocation'}],['TemplateId',{TemplateId:cards[0].templateId,PlayerType:'Same',Negate:true}],
 ['Random',{PlayerType:'Opposite'}],['RowWithCeiling',{SortOrder:'Lowest'}]];
const p=personality(data.profiles[0].name),typedP=ws.profile(2);
for(const [kind,s]of settings){const js=new BetaHandler(kind,s),target=ws.handler(0);target.kind=kind;Object.assign(target,s);
 for(const requestKind of ['play','locations','targets','choices','templates'])for(const actor of [1,2])check(js,target,p,typedP,requestKind,actor,1,1,800+filters,'Explicit '+kind);}
const report={checks,filters,decisions,profiles:data.profiles.length,handlerDefinitions:data.handlerDefinitions.length,
 scope:'Typed WS handler algorithms/settings/association order vs direct original JS, exact RNG consumption, propagated scores and source fallback; live WS action/replay wiring pending',nativeCompiled:false};
fs.writeFileSync(path.join(stage,'handlers-parity.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
