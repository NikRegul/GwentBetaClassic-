// The reply frontier must retain a legal winning pass after an opponent passes.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const cases=[],failures=[];
check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,waiting:g.waiting});}
function empty(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=0;
 g.aiStartingDeckOne=[112405];g.aiStartingDeckTwo.Clear();return g;}
let calls=0,peakActions=0;
const play=CBetaGwentDuelSession.prototype.AiSimPlay,pass=CBetaGwentDuelSession.prototype.Pass;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
CBetaGwentDuelSession.prototype.Pass=function(...args){calls++;return pass.apply(this,args);};
function run(g,first,own){
 const ids=own.map(c=>c.Snapshot().instanceId),values=own.map(c=>g.AiExactTempo(c));
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);
 const job=new CBetaGwentAIReplyTree097();job.Initialize(g,first.Snapshot().instanceId,ids,values,model);
 const before=state(g);let ticks=0;
 while(true){calls=0;const done=job.Step();peakActions=Math.max(peakActions,calls);
  check(calls<=1,'one simulated card or pass per callback');
  check(state(g)===before,'frontier preserves live match, cards, requests and RNG');
  if(done)break;if(++ticks>150)throw Error('frontier stalled');}
 return {job,ticks};
}
// Same legal winning settlement across difficulty/device budgets and revelation.
for(const strength of [2,3,4])for(const damp of [0,40,70])for(const revealed of [false,true]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=empty();g.aiSimDamp=damp;
 add(g,112405,1,0,2,20);add(g,112405,1,0,1,5);
 const burn=add(g,113309,8,0,2),first=add(g,112405,8,1,2,3),enemy=add(g,112405,8,0,1,10);
 if(revealed)enemy.AddTokens(64);
 const {job,ticks}=run(g,first,[burn,first]),winning=g.AiSimClone();winning.AiSimPlay(first.Snapshot().instanceId);
 check(winning.Pass(1)&&winning.Pass(2)&&winning.Snapshot().matchWinnerMask===2,'real rules confirm winning answering pass');
 if(strength>=3)check(job.shortRound,'higher levels exercise short-round frontier');
 if(revealed)check(job.branches===1,'revealed reply also resolves separately');
 check(job.passResult===30,'winning answering pass replaces forced self-Scorch');
 cases.push({strength,damp,revealed,passResult:job.passResult,result:job.result,ticks});
}
Host.strength=4;Host.matchStrength=[4,4];
// A loss/draw must still search the card that wins. A False Ciri on our
// board returns to the opponent on our pass, so a visible lead is insufficient.
for(const kind of ['behind','tied','false-ciri','optional-round']){
 const g=empty();add(g,112405,1,0,2,kind==='behind'?2:5);add(g,112405,1,0,1,kind==='behind'?20:8);
 if(kind==='false-ciri'){const spy=add(g,162212,1,1,2,12);spy.AddTokens(128);}
 if(kind==='optional-round'){g.match.roundNumber=1;g.match.playerOne.crowns=g.match.playerTwo.crowns=0;}
 const burn=add(g,113309,8,0,2),first=add(g,112405,8,1,2,3);add(g,112405,8,0,1,1).AddTokens(64);
 const {job,ticks}=run(g,first,[burn,first]);
 const settled=g.AiSimClone();settled.AiSimPlay(first.Snapshot().instanceId);settled.Pass(1);
 const visibleLead=settled.Score(2)-settled.Score(1);settled.Pass(2);
 check(settled.Snapshot().matchWinnerMask!==2,'negative control is not an immediate pass victory: '+kind);
 if(kind==='false-ciri')check(visibleLead>0&&settled.Snapshot().matchWinnerMask===1,'actual pass reaction reverses visible lead');
 check(job.follows>0&&job.branchBestId===burn.Snapshot().instanceId,'non-winning pass still evaluates the winning remaining card: '+kind);
 cases.push({kind,passResult:job.passResult,ticks});
}
// The new probe reads only an anonymized clone; unrevealed enemy identities
// and powers must not influence its branches or score.
function privateVariant(mutate){const g=empty();g.aiStartingDeckOne=[112405,113309];
 add(g,112405,1,0,2,20);add(g,112405,1,0,1,5);
 const burn=add(g,113309,8,0,2),first=add(g,112405,8,1,2,3),enemy=add(g,112405,8,0,1,10);
 const deck=add(g,112405,16,0,1,6);
 if(mutate)for(const c of [enemy,deck]){c.definition=BetaGwentDuelDefinition(113309);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(40,9);c.cardState.timerValue=7;}
 const {job}=run(g,first,[burn,first]);return {pass:job.passResult,result:job.result,scores:job.branchScores,templates:job.replyTemplates};}
check(JSON.stringify(privateVariant(false))===JSON.stringify(privateVariant(true)),'answering-pass probe ignores hidden enemy identities, powers and timers');
// A live public change while the added callback is pending invalidates it.
{
 const g=empty(),first=add(g,112405,8,0,2,3),burn=add(g,113309,8,1,2);add(g,112405,1,0,2,20);add(g,112405,1,0,1,5);add(g,112405,8,0,1,10);
 const ids=[first,burn].map(c=>c.Snapshot().instanceId),values=[first,burn].map(c=>g.AiExactTempo(c));
 const response=new CBetaGwentPublicResponseAI();response.Initialize(g,1);
 const job=new CBetaGwentAIReplyTree097();job.Initialize(g,ids[0],ids,values,response);
 let ticks=0;while(job.phase!==5&&!job.finished){job.Step();if(++ticks>150)throw Error('pending pass probe stalled');}
 if(!observe){check(job.phase===5,'winning pass has its own pending callback');first.ChangePower(1,false);
  check(job.Step()&&job.invalidated&&job.result===0,'changed source invalidates pending pass probe');}
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;CBetaGwentDuelSession.prototype.Pass=pass;
globalThis.result={checks,failures,cases,peakActions,actualWitcherScript:true,nativeGameplayVerified:false,observedBaseline:observe};
`,ctx,{timeout:120000});
const report={fingerprint:manifest.fingerprint,...ctx.result};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
if(report.failures.length)process.exitCode=1;
