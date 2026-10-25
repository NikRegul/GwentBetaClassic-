'use strict';
// Compare the typed WS port to the tested source-derived JS on ONE rules
// implementation. This does not enable the unfinished mode in the game.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {personality}=require('./beta_js092/profiles.cjs');
const {stateFromSession,templates}=require('./beta_js092/session.cjs');
const {BetaMiniMaxEvaluator,BetaSemanticMulliganPicker,chooseLowestPowerMulligan}=require('./beta_js092/core.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs');
const {BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const root=path.resolve(__dirname,'../..'),rules=path.resolve(process.argv[2]),stage=path.resolve(process.argv[3]);
const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const [n,h]of Object.entries(manifest.snapshotFiles))assert.equal(sha(path.join(rules,n)),h);
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n')+'\n'+fs.readFileSync(path.join(stage,'ws-stage.js'),'utf8');
const make=new Function('seed',source+String.raw`
 Host.strength=4;Host.matchStrength=[4,4];let state=seed>>>0||1,stamp=-1900000000;
 Host.random=()=>{state^=state<<13;state>>>=0;state^=state>>>17;state>>>=0;state^=state<<5;state>>>=0;return state/4294967296;};
 return {newSession:()=>new CBetaGwentDuelSession(),newCard:()=>new CBetaGwentDuelCard(),definition:id=>BetaGwentDuelDefinition(id),
  externalPolicyHooks:true,cloneSession:g=>new CBetaGwentCloner().CloneSession(g,++stamp),
  profile:f=>{let p=new CBetaOriginalPersonality();if(!p.Initialize(f))throw Error('faction');return p;},
  node:()=>{let n=new CBetaOriginalNode();n.Initialize();return n;},
  evaluator:p=>{let e=new CBetaOriginalMiniMax();e.personality=p;return e;},
  mulligan:p=>{let m=new CBetaOriginalMulligan();m.personality=p;return m;},template:BetaOriginalTemplate,
  best:BetaOriginalBestNode,tokenType:BetaOriginalTokenType};`);
const names={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
let checks=0,positions=0,actions=0,mulligans=0,maximumDifference=0;
const equal=(a,b,n)=>{assert.deepEqual(JSON.parse(JSON.stringify(a)),JSON.parse(JSON.stringify(b)),n);checks++;};
const near=(a,b,n)=>{const d=Math.abs(a-b);maximumDifference=Math.max(maximumDifference,d);assert(d<.00003,n+': '+a+' != '+b);checks++;};
const runtime=make(924041001);
for(const [faction,name]of Object.entries(names)){
 const js=personality(name),ws=runtime.profile(Number(faction));
 for(const key of Object.keys(js))if(!['name','semanticTags','associations'].includes(key)){
  if(key==='ExplorationConstant')near(ws[key],js[key],'Unused MCTS double -> WS float');else equal(ws[key],js[key],'Inherited '+key);
 }
 equal(ws.semanticTags,js.semanticTags,'Ordered semantic tags');
 // Selected source mulligan weights are integral: WS float vs original double
 // addition cannot change their bounded integer scores on these profiles.
 for(const tag of js.semanticTags)assert(Number.isInteger(tag.weight));
}
for(const t of Object.values(templates)){
 const ws=runtime.template(t.id);equal([ws.id,ws.linkedTemplateId,ws.printedPower,ws.typeMask,ws.tierMask,ws.placementOwn,ws.placementEnemy,ws.semanticTags,ws.categories],
 [t.id,t.linkedTemplateId,t.power,t.type,t.tier,t.placement?.player||0,t.placement?.opponent||0,t.semanticTags,t.categories],'Metadata '+t.id);
}
for(let token=0;token<8192;token++){
 const b=(token&384)!==0,h=(token&7807)!==0;equal(runtime.tokenType(token),b&&h?0:b?1:h?2:0,'Weather flags');
}
const decks=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
function compare(node,p){
 const ws=runtime.node();ws.game=node.game;ws.parentGame=node.parent?.game||node.game;ws.executingPlayerId=node.executingPlayerId;
 ws.cardId=node.decision?.cardId||0;ws.decisionSide=node.decision?.side||0;ws.decisionRow=node.decision?.row||0;
 ws.handlerScore=node.handlerScore||0;ws.hasFirstLocationSet=node.locationChoices.length>0;ws.firstLocations=node.locationChoices[0]||[];
 const expected=new BetaMiniMaxEvaluator(p).details(node);
 const profile=runtime.profile(Number(Object.keys(names).find(f=>names[f]===p.name))),result=runtime.evaluator(profile).Details(ws);
 equal(result.valid,true,'Valid typed evaluation');equal(result.terminal,expected.terminal,'Terminal branch');
 for(const key of ['score','ownValue','oppValue','semantic','handler','generic','stacking','row','preference','round','handMultiplier','carryMultiplier'])if(expected[key]!==undefined)near(result[key],expected[key],key);
 return ws;
}
for(let i=0;i<decks.length;i++){
 const d=decks[i],g=runtime.newSession();g.externalPolicyMask=3;
 assert(g.InitializeWithDecks(d.templateIds,d.templateIds,d.leader,d.leader,d.presetId,d.presetId));g.recordVisuals=false;
 while(g.mulligan){
  const side=g.RequestDecisionSide(),p=personality(names[d.faction]),ws=runtime.mulligan(runtime.profile(d.faction));
  const hand=g.live.filter(c=>{const s=c.Snapshot();return s.positionPlayerId===side&&s.locationMask===8&&s.canBePlayed;}).sort((a,b)=>a.Snapshot().locationIndex-b.Snapshot().locationIndex||a.Snapshot().instanceId-b.Snapshot().instanceId);
  const cards=stateFromSession(g).cards.filter(c=>c.side===side&&c.zone===8&&c.playable),picker=new BetaSemanticMulliganPicker();
  for(const c of hand){const card=cards.find(x=>x.id===c.Snapshot().instanceId);near(ws.SemanticScore(c,hand),picker.score(card,p,cards),'Source mulligan score');}
  const expected=picker.choose(cards,p),selected=ws.Choose(hand);equal(selected?.Snapshot().instanceId||0,expected?.id||0,'Source semantic choice');
  const low=runtime.profile(d.faction);low.MulliganPickerType='LowestPower';const lowPicker=runtime.mulligan(low),expectedLow=chooseLowestPowerMulligan(cards);
  equal(lowPicker.Choose(hand)?.Snapshot().instanceId||0,expectedLow?.id||0,'Lowest current power / printed threshold');
  assert(ws.Step(g));checks++;mulligans++;
 }
 for(const side of [1,2]){
  const base=runtime.cloneSession(g);if(base.match.currentPlayerId!==side)base.match.currentPlayerId=side;
  const p=personality(names[d.faction]),tree=new BetaGameTree(runtime,p,new BetaChoiceHandlers(runtime,p).hooks()),r=tree.root(base);
  compare(r,p);positions++;
  const selected=[r.children[0],...r.children.filter(n=>n.decision).slice(0,3)],wsNodes=[];
  for(const n of selected){let done=null;for(let j=0;done===null&&j<300;j++)done=tree.tryPlayAction(n);assert.equal(done,true,'Real WS battle node');
   n.score=new BetaMiniMaxEvaluator(p).evaluate(n);wsNodes.push(compare(n,p));actions++;
  }
  for(let j=0;j<wsNodes.length;j++){wsNodes[j].score=selected[j].score;wsNodes[j].revised=selected[j].score;}
  const expected=selected.reduce((a,b)=>b.score>a.score?b:a),best=runtime.best(wsNodes);equal(best.cardId,expected.decision?.cardId||0,'Best card strict first tie');
 }
}
const report={checks,positions,realActions:actions,mulliganRequests:mulligans,metadataTemplates:698,profiles:5,maximumDifference,
  scope:'Typed WS data/evaluator/pickers against direct original JS on common rules; staged only. Search/handlers/PlayMaker/recorded replay and live difficulty integration remain pending.',
  nativeProcessesAllowed:false,nativeCompiled:false,wsTranspilerFloatArithmetic:'Typed Beta module uses float32 operations; native compiler/game acceptance still required. MCTS ExplorationConstant is unused in selected AlphaBeta profiles.',fingerprint:manifest.fingerprint};
fs.writeFileSync(path.join(stage,'core-parity.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
