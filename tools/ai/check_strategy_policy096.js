'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const snapshot=path.resolve(process.argv[2]),{context:ctx,manifest}=load(snapshot);
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function empty(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiStartingDeckOne=[];return g;}
function make(counter=false){
 const g=empty(),engine=add(g,162308,1,0,2,15),payoff=add(g,162315,8,0,2,0),body=add(g,112405,8,1,2,3);
 add(g,112405,8,2,2,2);add(g,112405,1,0,1,5);
 if(counter){const burn=add(g,113309,8,0,1);burn.SetRevealed(true);g.aiStartingDeckOne=[113309];}
 else{add(g,112405,8,0,1,2);g.aiStartingDeckOne=[112405];}
 return {g,engine,payoff,body};
}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),request:g.requestId,
 draws:g.random.DrawCount(),seed:g.random.InitialSeed(),hazards:g.weather.hazards,starting:g.aiStartingDeckOne});}
function analyze(g,id){
 const before=state(g),job=new CBetaGwentStrategyResourceJob096();job.Initialize(g);
 if(!job.finished)job.ids=[id];
 const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peak=0,ticks=0;
 CBetaGwentDuelSession.prototype.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
 try{while(true){calls=0;const done=job.Step();peak=Math.max(peak,calls);if(done)break;if(++ticks>160)throw Error('unbounded strategy');}}
 finally{CBetaGwentDuelSession.prototype.AiSimPlay=play;}
 check(peak<=1,'bounded actual play count per callback');check(state(g)===before,'resource search preserves live match/cards/RNG');
 return {penalty:job.penalties[0]||0,replies:job.replyCounts[0]||0,job};
}
const cases=[];
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const {g,body}=make(true),r=analyze(g,body.Snapshot().instanceId);
 check(r.replies>0&&r.penalty>0,'revealed Scorch can break the remaining engine package '+strength);
 check(r.penalty<=8,'counter is a bounded ordering cost '+strength);cases.push({name:'revealed-control',strength,penalty:r.penalty,replies:r.replies});
 const safe=make(false);if(strength===4)check(analyze(safe.g,safe.body.Snapshot().instanceId).penalty===0,'known list without removal adds no invented loss');
 for(const mandatory of [true,false]){
  const f=make(true);f.g.match.roundNumber=mandatory?2:3;if(mandatory)f.g.match.playerOne.crowns=1;
  check(analyze(f.g,f.body.Snapshot().instanceId).penalty===0,'survival/final does not reserve for a future round '+strength+'/'+mandatory);
 }
}
Host.strength=4;Host.matchStrength=[4,4];
// Forced consumption of the last persistent setup is different from a payoff
// whose setup remains available. The mixed-faction position is synthetic.
{
 const {g,engine}=make(false);g.match.playerOne.hasPassed=true;engine.power.SetCurrentPair(1,0);
 const consume=add(g,201701,8,3,2,20);const r=analyze(g,consume.Snapshot().instanceId);
 check(r.penalty>0,'consuming the only persistent setup costs remaining payoffs');
 add(g,162308,8,4,2,2);check(analyze(g,consume.Snapshot().instanceId).penalty===0,'a held replacement preserves the dependency');
 cases.push({name:'forced-consumption',penalty:r.penalty});
}
{
 const {g,payoff}=make(false);g.match.playerOne.hasPassed=true;
 check(analyze(g,payoff.Snapshot().instanceId).penalty===0,'played payoff is not counted as a lost remaining payoff');
 const observer=new CBetaGwentStrategyObserve096(),hand=new CBetaGwentStrategyHand096();
 const f=empty();add(f,152205,1,0,2);add(f,152310,8,0,2);
 check(hand.PersistentLinks(observer.Capture(f,2,true),0)===0,'Draig is one-shot preparation, not a live dependency');
}
// Generic ability plays now appear in saved-position diagnostics, not just pass.
{
 const g=empty();add(g,112405,1,0,1,10);add(g,113309,8,0,2);
 const p=new CBetaGwentStrategyProbe096();p.Initialize(g,64);while(!p.Step()){}
 const burn=p.results.find(r=>r.action.kind===4);
 check(burn&&burn.status===1&&burn.scoreChange===10,'actual Scorch ability is simulated');
 add(g,200164,64,0,2);const leader=new CBetaGwentStrategyProbe096();leader.Initialize(g,64);while(!leader.Step()){}
 check(leader.results.some(r=>r.action.kind===3&&r.status!==4),'leader is a separate real action');
}
// Staging and direct execution must produce the same whole decision.
function act(staged){const {g}=make(true),logs=[];Host.log=s=>logs.push(s);
 try{if(staged){let ticks=0;while(!g.AiPreparationStep())if(++ticks>300)throw Error('stalled preparation');}
  check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'integrated policy resolves action');}
 finally{Host.log=null;}
 return {state:state(g),choice:logs.find(s=>/event=(SELECT|PASS)\b/.test(s)),costs:logs.filter(s=>s.includes('event=STRATEGY_RESOURCE'))};}
const direct=act(false),staged=act(true);
check(direct.state===staged.state&&direct.choice===staged.choice,'staged and synchronous policy agree');
check(direct.costs.length>0,'new resource cost reaches the live candidate evaluation');
// Planning jobs are not copied recursively into each trial position.
{
 const {g}=make(true);g.aiStrategyJob096=new CBetaGwentStrategyResourceJob096();g.aiStrategyJob096.Initialize(g);
 const clone=g.AiSimClone();check(clone.aiStrategyJob096===null,'disposable clone excludes live search job');
}
globalThis.policyResult={checks,cases,policyEnabled:true,nativeGameplayVerified:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.policyResult};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));
console.log(JSON.stringify(report));
