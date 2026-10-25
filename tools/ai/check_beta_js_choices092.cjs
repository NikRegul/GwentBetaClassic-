'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const {BetaAlphaBetaSearch}=require('./beta_js092/search.cjs'),{BetaMiniMaxEvaluator}=require('./beta_js092/core.cjs');
const {BetaActionReplay}=require('./beta_js092/replay.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924020401),p=basePersonality();
let checks=0,completeNodes=0,siblingNodes=0;function eq(a,b,l){assert.deepEqual(a,b,l);checks++;}
function add(g,t,z,i,side,power){const id={v:0};g.registry.Allocate(id);const c=runtime.newCard();c.Setup(g,id.v,t,side,z,i);if(power!==undefined)c.power.SetCurrentPair(power,0);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(side){
 const g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithPresets(54,54));
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
 g.match.currentPlayerId=side;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<3;i++){add(g,112405,8,i,side,8);add(g,112405,8,i,3-side,8);}return g;
}
const prototype=runtime.newSession().constructor.prototype;
for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])prototype[name]=()=>{throw Error('P19 selector forbidden: '+name);};
function prepare(g){const choices=new BetaChoiceHandlers(runtime,p),tree=new BetaGameTree(runtime,p,choices.hooks()),root=tree.root(g);return {choices,tree,root};}
function complete(tree,n){let count=0;while(true){const before=tree.mutations,r=tree.tryPlayAction(n);assert(tree.mutations-before<=1);if(r!==null)break;if(++count>30)throw Error('Single-choice continuation stalled');}completeNodes++;
 const live=runtime.cloneSession(n.parent.game),replay=new BetaActionReplay(runtime,p,live,n);let steps=0;
 while(!replay.finished){eq(replay.step().mutations,1,'one live mutation per callback');assert(++steps<35);}
 eq(stateFromSession(live),stateFromSession(n.game),'recorded live action matches complete simulated branch');
}
for(const side of [1,2]){
 const g=fixture(side),own=add(g,112101,1,0,side,12),plain=add(g,112101,1,0,3-side,12),resilient=add(g,112101,2,0,3-side,12);
 resilient.AddTokens(1);const spell=add(g,113301,8,3,side);
 const initial=stateFromSession(g),{tree,root}=prepare(g),node=root.children.find(n=>n.decision?.cardId===spell.Snapshot().instanceId);
 eq(tree.tryPlayAction(node),null,'damage yields for real target');
 complete(tree,node);
 eq(node.choiceRecords[0].hint,23,'source XML hint used');eq(node.choiceRecords[0].chosen[0].id,resilient.Snapshot().instanceId,'original summation targets enemy resilience');
 eq(node.game.FindCard(resilient.Snapshot().instanceId).Snapshot().power.currentPower,3,'actual nine damage');
 eq(node.game.FindCard(plain.Snapshot().instanceId).Snapshot().power.currentPower,12,'other foe untouched');
 eq(node.game.FindCard(own.Snapshot().instanceId).Snapshot().power.currentPower,12,'ally untouched');
 eq(node.handlerScore,6.5,'original tag/resilience propagated scores');
 eq(stateFromSession(g),initial,'live source state untouched by search');
 // Source PlayAll must add and replay siblings for every original target.
 const q=fixture(side),a=add(q,142305,1,0,3-side),b=add(q,142305,2,0,3-side),sweers=add(q,162206,8,3,side);
 add(q,142305,16,0,3-side);const built=prepare(q),n=built.root.children.find(n=>n.decision?.cardId===sweers.Snapshot().instanceId);
 eq(built.tree.tryPlayAction(n),null,'PlayAll target request');
 const pool=n.game.pendingIds.slice(),before=built.root.children.length;complete(built.tree,n);
 const siblings=built.root.children.slice(before);eq(siblings.length,pool.length-1,'all sibling target branches added');
 const results=[n.choiceRecords[0].chosen[0].id];
 for(const sibling of siblings){const count=built.root.children.length;complete(built.tree,sibling);eq(built.root.children.length,count,'stored choice replay does not rebranch');results.push(sibling.choiceRecords[0].chosen[0].id);}
 eq(results.slice().sort((a,b)=>a-b),pool.slice().sort((a,b)=>a-b),'each source target explored once');siblingNodes+=siblings.length;
}
// Run the actual search with dynamically added PlayAll siblings, not only
// manually executing a callback. Default Base depth1 keeps this test bounded.
for(const side of [1,2]){
 const g=fixture(side);add(g,142305,1,0,3-side);add(g,142305,2,0,3-side);add(g,142305,16,0,3-side);add(g,162206,8,3,side);
 const {tree,root}=prepare(g),e=new BetaMiniMaxEvaluator(p),search=new BetaAlphaBetaSearch({tryPlayAction:n=>tree.tryPlayAction(n),score:n=>e.evaluate(n),finished:n=>n.terminal});
 search.start(root,p,side);let callbacks=0;
 while(!search.finished){const before=tree.mutations,r=search.step(1,32);assert(tree.mutations-before<=1);assert(r.actionAttempts<=1);assert(++callbacks<300);}
 eq(root.children.every(n=>n.status!==0),true,'all dynamically created branches evaluated');assert(root.children.some(n=>n.choiceRecords.length));checks++;
 completeNodes+=search.explored;
}
for(const side of [1,2])for(const template of [113305,113312,113206,153301]){
 const g=fixture(side);add(g,112405,1,0,3-side,12);const c=add(g,template,8,3,side);
 const {tree,root}=prepare(g),n=root.children.find(n=>n.decision?.cardId===c.Snapshot().instanceId);
 eq(tree.tryPlayAction(n),null,'source location request yields');
 const sourceState=stateFromSession(g),poolCount=template===113206?2:template===153301?6:3,before=root.children.length;
 // Pool is inspected independently of default Random selection.
 const probes=new BetaChoiceHandlers(runtime,p);eq(probes.describe(n).items.length,poolCount,'source location pool size');
 complete(tree,n);const siblings=root.children.slice(before);eq(siblings.length,template===113305||template===113312?poolCount-1:0,'source location handler branch count');
 const chosen=n.choiceRecords[0].chosen.slice();
 for(const sibling of siblings){const before=root.children.length;complete(tree,sibling);eq(root.children.length,before,'location replay does not rebranch');chosen.push(sibling.choiceRecords[0].chosen[0]);}
 eq(new Set(chosen.map(x=>x.side+':'+x.row)).size,chosen.length,'all selected location branches unique');
 if(template!==153301)eq(chosen.every(x=>x.side===3-side),true,'source owner-opponent constraint');
 eq(stateFromSession(g),sourceState,'location exploration preserves source');siblingNodes+=siblings.length;
}
for(const side of [1,2]){
 const g=fixture(side),top=add(g,132304,16,0,side);add(g,142305,16,1,side);
 const joachim=add(g,162211,8,3,side),{choices,tree,root}=prepare(g),n=root.children.find(n=>n.decision?.cardId===joachim.Snapshot().instanceId);
 eq(tree.tryPlayAction(n),null,'forced source top-card acknowledgement');
 eq(choices.describe(n).kind,'forced','source has PlayCards and no choice request');
 const draws=choices.simulatorRandom.DrawCount();eq(tree.tryPlayAction(n),null,'fixed child proceeds to placement');
 eq(choices.simulatorRandom.DrawCount(),draws,'forced top acknowledgement consumes no policy RNG');
 eq(n.choiceRecords[0].chosen[0].id,top.Snapshot().instanceId,'fixed top eligible card retained');
 complete(tree,n);eq((n.game.FindCard(top.Snapshot().instanceId).Snapshot().locationMask&7)!==0,true,'fixed child actually played');
 eq(n.game.FindCard(top.Snapshot().instanceId).Snapshot().power.currentPower,13,'parent boost follows played child');
}
const report={checks,completeNodes,siblingNodes,fingerprint:runtime.fingerprint,nativeProcessLaunch:false,currentPolicySelectorsAllowed:false,
 scope:'Real shared-engine single-target source Summation/PlayAll, XML AIHint, float propagation, sibling AlphaBeta and recorded live-action replay without policy re-evaluation. Not a full game.',
 fullMatchReady:false,pending:['Cow Carcass child placement','Opposing reaction ownership','Shield source request order','Remaining non-Base handlers','High-difficulty mixed-policy full game']};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-choices-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
