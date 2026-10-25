/* Source-backed shared-rule fixes, not a second rules implementation. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,basePersonality,stateFromSession}=require('./beta_js092/session.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs'),{BetaActionReplay}=require('./beta_js092/replay.cjs');
const {BetaHandler}=require('./beta_js092/handlers.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924021001),p=basePersonality();let checks=0,completedNodes=0;
function eq(a,b,l){assert.deepEqual(a,b,l);checks++;}
function add(g,t,z,i,side,power){const id={v:0};g.registry.Allocate(id);const c=runtime.newCard();c.Setup(g,id.v,t,side,z,i);if(power!==undefined)c.power.SetCurrentPair(power,0);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(side){const g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithPresets(54,54));g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.mulligan=false;g.waiting=false;g.pendingCard=null;g.pendingLeader=null;g.recordVisuals=false;g.match.currentPlayerId=side;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=1;g.match.roundTurnIndex=1;for(const s of [g.match.playerOne,g.match.playerTwo]){s.hasPassed=false;s.hasMadeInitialMoveForCurrentTurn=false;}for(let i=0;i<3;i++){add(g,112405,8,i,side);add(g,112405,8,i,3-side);add(g,112405,16,i,side);}return g;}
const proto=runtime.newSession().constructor.prototype;
for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])proto[name]=()=>{throw Error('P19 selector forbidden: '+name);};
function prepare(g,c){const choices=new BetaChoiceHandlers(runtime,p),tree=new BetaGameTree(runtime,p,choices.hooks()),root=tree.root(g);return {choices,tree,root,node:root.children.find(n=>n.decision?.cardId===c.Snapshot().instanceId)};}
function complete(b,n=b.node){let count=0;while(true){const before=b.tree.mutations,r=b.tree.tryPlayAction(n);eq(b.tree.mutations-before<=1,true,'one source callback action');if(r!==null)break;assert(++count<70);}completedNodes++;}
for(const owner of [1,2])for(const current of [1,2])for(const t of [162301,162306]){
 const g=fixture(current),card=add(g,t,8,3,owner);g.NilfReveal(card,true);
 eq(g.nilfJobs.length,owner===current?1:0,'source reveal requires owner turn '+[t,owner,current]);
 if(owner===current)eq(g.nilfJobs[0].kind,t===162301?2:1,'correct original reactive effect');
}
// These two source graphs MOVE to a random last position. They are not play
// requests, so neither policy handlers nor deployment effects may choose a row.
for(const side of [1,2])for(const [t,zone,kind]of [[162301,8,2],[142313,16,6]]){
 const g=fixture(side),card=add(g,t,zone,4,side),draws=g.random.DrawCount();
 for(const row of [1,2])for(let i=0;i<9;i++)add(g,112405,row,i,side);
 g.NilfQueueReaction(card,kind,side);eq(g.NilfNextReaction(),false,'automatic source move has no decision');
 const s=card.Snapshot();eq(s.locationMask,4,'only non-full source location');eq(s.locationIndex,0,'last index in selected row');
 eq(g.random.DrawCount()>draws,true,'uses battle RNG, no policy row heuristic');eq(g.IsFatal(),false,'automatic move remains legal');
}
for(const side of [1,2])for(const [parent,child]of [[162302,162402],[142304,143301]]){
 const g=fixture(side);add(g,112405,1,0,3-side);add(g,112405,1,1,3-side);const creator=add(g,parent,8,3,side),b=prepare(g,creator);
 eq(b.tree.tryPlayAction(b.node),null,'creator yields for actual child placement');
 const q=b.node.game;eq(q.pendingRally.TemplateId(),child,'original created child template');eq(q.pendingRow,false,'not parent location-target request');
 const original=b.choices.handler.bind(b.choices);
 // Explicit source PlayAll fixture override exercises every insertion slot;
 // production Base retains its own association/default Random selection.
 b.choices.handler=(type,t,hint,exact)=>type==='PlayCardAssociations'&&t===child?new BetaHandler('PlayAll'):original(type,t,hint,exact);
 eq(q.MonsterCreationAllowed(q.pendingCard,child),true,'specific source spawn allowed');eq(q.MonsterCreationAllowed(q.pendingCard,112101),false,'unrelated creation remains forbidden');
 const before=b.root.children.length;complete(b);const siblings=b.root.children.slice(before);eq(siblings.length,4,'source child positions: three rows plus two insertion slots');
 for(const n of [b.node,...siblings]){
  if(n!==b.node)complete(b,n);
  const cows=n.game.live.filter(c=>c.TemplateId()===child);eq(cows.length,1,'one created child');
  const s=cows[0].Snapshot();eq(s.positionPlayerId,3-side,'source disloyal placement');eq((s.tokenMask&128)!==0,true,'spying applied');eq(s.timerValue,child===162402?2:1,'source child timer');
  const pos=n.choiceRecords[0].chosen[0];eq([s.locationMask,s.locationIndex],[pos.row,pos.index],'exact source insertion choice applied');
  const live=runtime.cloneSession(g),replay=new BetaActionReplay(runtime,p,live,n);while(!replay.finished)replay.step();eq(stateFromSession(live),stateFromSession(n.game),'cow live replay matches branch');
 }
}
for(const side of [1,2])for(const template of [133301,201656]){
 const g=fixture(side),own=add(g,112405,1,0,side,40),enemy=add(g,112405,1,0,3-side,40),spell=add(g,template,8,3,side),b=prepare(g,spell);
 eq(b.tree.tryPlayAction(b.node),null,'source hand choice is FIRST');
 eq(b.node.game.pendingHandPower,true,'first hand phase exposed');eq(b.choices.describe(b.node).kind,'choices','source kind37 is card choices');eq(b.choices.describe(b.node).hint,37,'source hand AIHint37');
 const handIds=b.node.game.pendingIds.slice();eq(handIds.every(id=>b.node.game.FindCard(id).Snapshot().locationMask===8),true,'hand pool only');
 complete(b);const records=b.node.choiceRecords;eq(records.map(r=>r.kind),['choices','targets'],'original hand -> field order');
 eq(records.map(r=>r.hint),[37,template===133301?31:23],'original source hint sequence');
 const hand=records[0].chosen[0],target=records[1].chosen[0],actual=b.node.game.FindCard(target.id).Snapshot();
 eq(actual.power.currentPower,40+(template===133301?hand.basePower:-hand.basePower),'actual selected hand base power determines effect');
 eq(b.node.game.FindCard(hand.id).Snapshot().locationMask,8,'hand card stays in hand');
 const live=runtime.cloneSession(g),replay=new BetaActionReplay(runtime,p,live,b.node);while(!replay.finished)replay.step();eq(stateFromSession(live),stateFromSession(b.node.game),'hand/board live replay matches');
}
const report={checks,completedNodes,fingerprint:runtime.fingerprint,nativeProcessesAllowed:false,currentPolicySelectorsAllowed:false,
 scope:'Both seats: source owner-turn reveal guards, automatic random-last MoveCards reactions (no policy request), Cow Carcass and Incinerating Trap actual child creation/positions/timer, Shield/Spear hand-before-board and live stored replay.',fullMatchReady:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-source-requests-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
