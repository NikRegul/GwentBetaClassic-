// Resolve the public last opposing action before pricing our remaining cards.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],cases=[];check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
function position(strength=4,damp=40,kind='ordinary'){Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=damp;
 g.aiStartingDeckOne=[113301];g.aiStartingDeckTwo.Clear();
 const tall=add(g,112405,1,0,2,20);add(g,112405,1,0,1,5);
 const burn=add(g,113309,8,0,2),body=add(g,112405,8,1,2,3),reply=add(g,113301,8,0,1);
 if(kind==='extra-card')add(g,112405,8,1,1,4);
 if(kind==='leader')add(g,200164,64,0,1);
 if(kind==='false-ciri'){tall.Move(2,512,0);add(g,112405,1,0,2,5);add(g,162212,1,1,2,12).AddTokens(128);}
 if(kind==='optional-round'){g.match.roundNumber=1;g.match.playerOne.crowns=g.match.playerTwo.crowns=0;}
 return {g,tall,burn,body,reply};}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,waiting:g.waiting});}
function treeFor(p){const {g,burn,body}=p,own=[burn,body];
 const ids=own.map(c=>c.Snapshot().instanceId),values=own.map(c=>g.AiExactTempo(c));
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);
 const tree=new CBetaGwentAIReplyTree097();tree.Initialize(g,ids[1],ids,values,model);return tree;}
let calls=0,peakActions=0,maximumCallbacks=0;
const play=CBetaGwentDuelSession.prototype.AiSimPlay,pass=CBetaGwentDuelSession.prototype.Pass;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
CBetaGwentDuelSession.prototype.Pass=function(...args){calls++;return pass.apply(this,args);};
function run(p){const tree=treeFor(p),before=state(p.g);let ticks=0;
 while(true){calls=0;const done=tree.Step();peakActions=Math.max(peakActions,calls);
  check(calls<=1,'one simulated card or pass per callback');
  check(state(p.g)===before,'reply preparation preserves the live cards, match and RNG');
  if(done)break;if(++ticks>150)throw Error('frontier stalled');}
 maximumCallbacks=Math.max(maximumCallbacks,ticks);return tree;}
// Public reply hypothesis: one hidden card becomes zero after Thunder.
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 const p=position(strength,damp),tree=run(p);
 check(tree.branches===1,'public last-card reply is modeled');
 if(strength===4)check(tree.replyTemplates[0]===113301,'hard models the actual public Thunder hypothesis');
 check(tree.branchScores[0]===30&&tree.continuationIds[0]===0,'exhausted enemy makes the winning pass a complete continuation');
 cases.push({strength,damp,templates:tree.replyTemplates,branchScores:tree.branchScores,continuations:tree.continuationIds});
}
// Exercise the actual policy, not just the helper, in both execution modes.
// No exact public endgame is available: the opposing hand is unrevealed.
for(const strength of [3,4])for(const damp of [0,40,70])for(const staged of [false,true]){
 const p=position(strength,damp),{g,tall,burn,body}=p,before=state(g);
 if(staged){let ticks=0;while(true){calls=0;const ready=g.AiPreparationStep();peakActions=Math.max(peakActions,calls);
   check(calls<=1,'one simulated action throughout integrated preparation');
   check(state(g)===before,'integrated preparation preserves the actual game');
   if(ready)break;if(++ticks>650)throw Error('integrated preparation stalled');}}
 const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'full policy completes');
 check(!g.aiEndgameComplete097,'hidden hand does not become an exact public proof');
 check(body.Snapshot().locationMask!==8&&burn.Snapshot().locationMask===8,'full policy plays the small body and preserves Scorch');
 check(tall.Snapshot().locationMask===1,'full policy preserves its own 20-point unit');
 cases.push({strength,damp,staged,selected:logs.filter(s=>/event=(OPTION|SELECT|PASS)/.test(s))});
}
// Exhausted hand with a usable leader, another card, a public pass reaction,
// or only a won optional round must not be treated as a won match.
for(const kind of ['extra-card','leader','false-ciri','optional-round']){
 const p=position(4,40,kind),tree=run(p);
 check(tree.branches>=1,'negative control retains its real reply: '+kind);
 check(tree.continuationIds.every(id=>id===p.burn.Snapshot().instanceId)&&tree.follows>0,'non-settled line retains its card continuation: '+kind);
 cases.push({kind,branchScores:tree.branchScores,continuations:tree.continuationIds});
}
function variant(mutate){const p=position(),{g,reply}=p;const hidden=add(g,112405,16,0,1,6);
 if(mutate)for(const c of [reply,hidden]){c.definition=BetaGwentDuelDefinition(113309);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(40,9);c.cardState.timerValue=7;}
 const tree=run(p);return {result:tree.result,scores:tree.branchScores,ids:tree.continuationIds,templates:tree.replyTemplates};}
check(JSON.stringify(variant(false))===JSON.stringify(variant(true)),'only public hand count and leader availability authorize settlement, never hidden identities');
// Invalidate between our pass and the separate forced opposing pass.
if(!observe){const p=position(),tree=treeFor(p);let ticks=0;
 while(tree.phase!==6&&!tree.finished){tree.Step();if(++ticks>150)throw Error('forced-pass stage not reached');}
 check(tree.phase===6,'forced opposing pass has its own callback');p.body.ChangePower(1,false);
 check(tree.Step()&&tree.invalidated&&tree.result===0&&tree.passProbe===null,'stale settlement is discarded before it can affect the decision');}
CBetaGwentDuelSession.prototype.AiSimPlay=play;CBetaGwentDuelSession.prototype.Pass=pass;
// Independent outcome witnesses: direct Play/SelectTarget/Pass only, without
// AiSimPlay, the reply model, a search score, or hidden-card inference.
const witnesses=[];
for(const target of ['pass','tall','small']){
 const {g,tall,burn,body,reply}=position();check(g.Play(2,body.Snapshot().instanceId,1),'native body opener executes');
 if(target==='pass')check(g.Pass(1),'native opposing pass executes');
 else{check(g.Play(1,reply.Snapshot().instanceId,1),'native Thunder reply executes');
  check(g.IsPending(),'native Thunder exposes its real target request');
  const victim=target==='tall'?tall:body;check(g.pendingIds.includes(victim.Snapshot().instanceId),'requested target is legal');
  check(g.SelectTarget(g.requestId,victim.Snapshot().instanceId),'native Thunder target resolves');}
 check(g.Pass(2),'native answering pass executes');
 if(g.Snapshot().matchWinnerMask===0)check(g.Pass(1),'exhausted opponent performs its only legal remaining action');
 check(g.Snapshot().matchWinnerMask===2&&burn.Snapshot().locationMask===8,'native line wins without spending Scorch');
 witnesses.push({opposingReply:target,winner:g.Snapshot().matchWinnerMask,score:[g.Score(1),g.Score(2)]});
}
{
 const {g,burn,body}=position();check(g.Play(2,burn.Snapshot().instanceId,1),'old self-Scorch opener executes');
 check(g.Pass(1)&&g.Play(2,body.Snapshot().instanceId,1)&&g.Pass(2),'opponent can defeat the old opener even after our best remaining card');
 check(g.Snapshot().matchWinnerMask===1,'old selected opener has a concrete losing continuation');
}
globalThis.result={checks,failures,cases,witnesses,peakActions,maximumCallbacks,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:120000});
const report={fingerprint:manifest.fingerprint,...ctx.result};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(report.failures.length)process.exitCode=1;
