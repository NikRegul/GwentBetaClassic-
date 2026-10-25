'use strict';
// Real common-engine actions: typed WS request wiring vs the direct JS port.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {personality}=require('./beta_js092/profiles.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs');
const {BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const {BetaMiniMaxEvaluator}=require('./beta_js092/core.cjs');
const {stateFromSession}=require('./beta_js092/session.cjs');
const stage=path.resolve(process.argv[2]),rules=path.resolve(process.argv[3]);
const commonSource=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const source=commonSource+(commonSource.includes('class CBetaOriginalNode ')?'':'\n'+fs.readFileSync(path.join(stage,'ws-stage.js'),'utf8'));
const runtime=new Function(source+String.raw`
 Host.strength=4;Host.matchStrength=[4,4];let state=924042001,stamp=-1700000000;
 Host.random=()=>{state^=state<<13;state>>>=0;state^=state>>>17;state>>>=0;state^=state<<5;state>>>=0;return state/4294967296;};
 const rt=new CBetaOriginalRuntime();
 return {externalPolicyHooks:true,newSession:()=>new CBetaGwentDuelSession(),newCard:()=>new CBetaGwentDuelCard(),definition:BetaGwentDuelDefinition,
 cloneSession:g=>new CBetaGwentCloner().CloneSession(g,++stamp),
 profile:f=>{let p=new CBetaOriginalPersonality();if(!p.Initialize(f))throw Error('faction');return p;},
 mulligan:(g,p)=>{let m=new CBetaOriginalMulligan();m.personality=p;return m.Step(g);},
 tree:(g,p)=>{let t=new CBetaOriginalGameTree(),c=new CBetaOriginalChoiceHandlers(),e=new CBetaOriginalMiniMax();
 c.runtime=rt;c.p=p;t.runtime=rt;t.p=p;t.choices=c;t.evaluator=e;e.personality=p;return {tree:t,root:t.Root(g)};}};`)();
const names={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
const root=path.resolve(__dirname,'../..'),decks=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
const out=path.resolve(process.argv[4]);assert(!fs.existsSync(out),'Fresh output required');
let checks=0,actions=0,callbacks=0,peakActions=0;
const report={scope:'Typed WS real actions/request phases vs direct JS; no full live WS controller game yet',records:[],complete:false,nativeCompiled:false};
const save=()=>fs.writeFileSync(out,JSON.stringify({...report,checks,actions,callbacks,peakActions},null,2)+'\n');
function eq(a,b,n){assert.deepEqual(JSON.parse(JSON.stringify(a)),JSON.parse(JSON.stringify(b)),n);checks++;}
function score(a,b,n){assert(Math.abs(a-b)<.00005,n+': '+a+' != '+b);checks++;}
const cardId=n=>n.decision?.cardId||0;
function key(n){return [cardId(n),n.decision?.side||0,n.decision?.row||0,n.decision?.index||0];}
function typedKey(n){return [n.cardId,n.decisionSide,n.decisionRow,n.decisionIndex];}
function records(n,typed){return n.choiceRecords.map(r=>[r.kind,r.source,typed?r.sourceHint:r.hint,r.sourceFallback,r.chosen.map(c=>(r.kind==='play'?[c.side,c.row,c.index]:r.kind==='locations'?[c.side,c.row]:c.id))]);}
try{
 for(const d of decks){
  const g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithDecks(d.templateIds,d.templateIds,d.leader,d.leader,d.presetId,d.presetId));g.recordVisuals=false;
  while(g.mulligan)assert(runtime.mulligan(g,runtime.profile(d.faction)));
  const p=personality(names[d.faction]),a=new BetaGameTree(runtime,p,new BetaChoiceHandlers(runtime,p).hooks()),r=a.root(runtime.cloneSession(g)),b=runtime.tree(runtime.cloneSession(g),runtime.profile(d.faction));
  assert(!b.tree.failed,b.tree.error);eq(b.root.children.map(typedKey),r.children.map(key),'Root children '+d.presetId);
  let count=0;
  for(let i=0;i<r.children.length;i++){
   assert(i<2000,'Root branch limit');const js=r.children[i],ws=b.root.children[i];eq(typedKey(ws),key(js),'Source sibling identity');
   let done=null;
   for(let step=0;done===null;step++){
    assert(step<1000,'Nested callback limit');const beforeA=a.mutations,beforeB=b.tree.mutations;
    done=a.tryPlayAction(js);const result=b.tree.TryPlayAction(ws);assert(!b.tree.failed,b.tree.error);
    eq(result,done===null?-1:done?1:0,'One actual continuation result');eq(b.tree.mutations-beforeB,a.mutations-beforeA,'Same battle mutation count');
    assert(b.tree.mutations-beforeB<=1);peakActions=Math.max(peakActions,b.tree.mutations-beforeB);callbacks++;
   }
   assert.equal(done,true);eq(stateFromSession(ws.game),stateFromSession(js.game),'Exact resulting common state '+d.presetId+'/'+i);
   eq(records(ws,true),records(js,false),'Exact stored source decisions');eq(b.root.children.map(typedKey),r.children.map(key),'Same dynamically forked siblings');
   score(ws.handlerScore,js.handlerScore,'Source propagated score');score(b.tree.Score(ws),new BetaMiniMaxEvaluator(p).evaluate(js),'Original MiniMax score');
   eq(ws.firstLocations.map(x=>[x.side,x.row]),(js.locationChoices[0]||[]).map(x=>[x.side,x.row]),'First source location set');
   actions++;count++;
  }
  report.records.push({preset:d.presetId,actions:count,status:'complete'});save();console.log(JSON.stringify(report.records.at(-1)));
 }
 report.complete=true;save();
}catch(e){report.error=String(e.stack);save();throw e;}
