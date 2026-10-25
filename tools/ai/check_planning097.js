'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const snapshot=path.resolve(process.argv[2]),{context:ctx,manifest}=load(snapshot);
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
check=(v,n)=>{if(!v)throw Error(n);checks++;};
function empty(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=0;return g;}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,waiting:g.waiting});}
// Independent arithmetic oracle: no WS evaluations, target heuristics or search jobs.
// Only plain bronze bodies and the global Scorch rule enter these authored cases.
function solve(s,memo=new Map()){
 const key=JSON.stringify(s);if(memo.has(key))return memo.get(key);
 if(s.p[0]&&s.p[1])return Math.sign(s.b[1].reduce((a,b)=>a+b,0)-s.b[0].reduce((a,b)=>a+b,0));
 let best=s.a===1?-2:2;
 for(let action=-1;action<s.h[s.a].length;action++){
  const n=JSON.parse(JSON.stringify(s));
  if(action<0)n.p[n.a]=true;
  else{const card=n.h[n.a].splice(action,1)[0];if(card==='S'){
    const max=Math.max(0,...n.b[0],...n.b[1]);n.b=n.b.map(b=>b.filter(p=>p!==max));
   }else n.b[n.a].push(card);}
  n.a=n.p[1-n.a]?n.a:1-n.a;const value=solve(n,memo);
  best=s.a===1?Math.max(best,value):Math.min(best,value);
 }
 memo.set(key,best);return best;
}
function moveValue(s,index){const n=JSON.parse(JSON.stringify(s));
 if(index<0)n.p[1]=true;else{const c=n.h[1].splice(index,1)[0];if(c==='S'){
  const max=Math.max(0,...n.b[0],...n.b[1]);n.b=n.b.map(b=>b.filter(p=>p!==max));
 }else n.b[1].push(c);}
 n.a=n.p[0]?1:0;return solve(n);}
function fromModel(s){const g=empty(),own=[];
 for(let side=0;side<2;side++){
  s.b[side].forEach((v,i)=>add(g,112405,1,i,side+1,v));
  s.h[side].forEach((v,i)=>{const c=add(g,v==='S'?113309:112405,8,i,side+1,v==='S'?undefined:v);
   if(side===0)c.AddTokens(64);else own.push(c.Snapshot().instanceId);});
 }
 return {g,own};}
const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peak=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return play.apply(this,a);};
function run(job){let ticks=0;while(true){calls=0;const done=job.Step();peak=Math.max(peak,calls);check(calls<=1,'one actual play per callback');if(done)break;if(++ticks>2000)throw Error('unbounded job');}return ticks;}
const completed={2:0,3:0,4:0},cutoffs={2:0,3:0,4:0};let positions=0,integrated=0;const integratedLevels={2:0,3:0,4:0};
let rng=2026102197;function rnd(n){rng^=rng<<13;rng^=rng>>>17;rng^=rng<<5;return (rng>>>0)%n;}
const models=[];
for(let i=0;i<48;i++)models.push({a:1,p:[false,false],b:[[1+rnd(15),1+rnd(12)],[1+rnd(15)]],
 h:[[i%3===0?'S':1+rnd(15),...(i%2?[1+rnd(12)]:[])],[i%2?'S':1+rnd(15),1+rnd(15),...(i%6===0?[1+rnd(10)]:[])]]});
for(const strength of [2,3,4]){Host.strength=strength;Host.matchStrength=[strength,strength];
 for(const model of models){const {g,own}=fromModel(model),before=state(g),job=new CBetaGwentAIEndgame097();job.Initialize(g);
  check(job.supported,'plain public position supported');run(job);positions++;
  check(state(g)===before,'public search preserves real cards/match/RNG');check(job.nodes<=job.limit,'node budget respected');
  if(job.complete){completed[strength]++;check(job.result===solve(model),'complete result agrees with arithmetic oracle');
   const index=job.firstId===0?-1:own.indexOf(job.firstId);check(job.firstId===0||index>=0,'first action exists');
   check(moveValue(model,index)===job.result,'reported first action realizes minimax value');
   if(job.result>=0 && integratedLevels[strength]<3){check(g.OpponentStep()&&!g.IsPending()&&!g.IsFatal(),'integrated result executes');
    check(g.aiEndgameComplete097&&g.aiEndgameId097===job.firstId,'live policy uses completed public tree');integrated++;integratedLevels[strength]++;}
  }else cutoffs[strength]++;
 }
}
check(completed[4]>20,'maximum completes a useful range of public finals');
Host.strength=4;Host.matchStrength=[4,4];
for(const kind of ['hidden-hand','leader','hazard','hidden-board','round-two','active-engine']){
 const {g}=fromModel(models[1]);
 if(kind==='hidden-hand')g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8).SetRevealed(false);
 if(kind==='leader')add(g,200164,64,0,1);
 if(kind==='hazard')g.weather.hazards[0]=1;
 if(kind==='hidden-board')g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===1).AddTokens(8);
 if(kind==='round-two')g.match.roundNumber=2;
 if(kind==='active-engine')add(g,201624,1,5,2);
 const job=new CBetaGwentAIEndgame097();job.Initialize(g);check(job.finished&&!job.complete&&!job.supported,'unsupported state is not a proof: '+kind);
}
{
 const {g}=fromModel(models[1]),job=new CBetaGwentAIEndgame097();job.Initialize(g);job.limit=1;run(job);
 check(!job.complete,'truncated endgame is unknown');
 const stale=new CBetaGwentAIEndgame097();stale.Initialize(g);g.live.find(c=>c.Snapshot().locationMask===1).ChangePower(1,false);
 check(stale.Step()&&stale.invalidated&&!stale.complete,'changed visible position invalidates search');
}
// Large supported public finals exercise the combined presentation-time budget.
let maximumPreparationCallbacks=0;
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const model={a:1,p:[false,false],b:[[9,5],[7]],h:[['S',12,4],['S',8,3]]};
 const staged=fromModel(model).g,sync=fromModel(model).g;staged.aiSimDamp=sync.aiSimDamp=damp;
 const before=state(staged);let ticks=0;
 while(true){calls=0;const done=staged.AiPreparationStep();check(calls<=1,'whole preparation keeps one-play callback');
  check(state(staged)===before,'whole preparation preserves live state');ticks++;if(done)break;if(ticks>650)throw Error('combined preparation stalled');}
 maximumPreparationCallbacks=Math.max(maximumPreparationCallbacks,ticks);
 check(sync.OpponentStep()&&staged.OpponentStep(),'large public final executes in both modes');
 check(state(sync)===state(staged),'six-card public final sync/cooperative agreement');
 staged.aiPreparationEndgameJob097=new CBetaGwentAIEndgame097();staged.aiPreparationEndgameJob097.Initialize(staged);
 check(staged.AiSimClone().aiPreparationEndgameJob097===null,'disposable clone excludes recursive endgame job');
}
// A completed winning pass outranks spending another equally winning card.
for(const strength of [2,3,4])for(const staged of [false,true]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=empty();g.match.playerOne.hasPassed=true;
 const own=add(g,112405,1,0,2,30);add(g,112405,1,0,1,20);const burn=add(g,113309,8,0,2);add(g,112405,8,1,2,11);
 if(staged){let ticks=0;while(!g.AiPreparationStep())if(++ticks>200)throw Error('stalled winning pass preparation');}
 check(g.OpponentStep()&&g.Snapshot().matchWinnerMask===2,'winning pass ends actual match');
 check((own.Snapshot().locationMask&7)!==0&&burn.Snapshot().locationMask===8,'winning pass keeps own maximum and control');
}
Host.strength=4;Host.matchStrength=[4,4];
// Reply search must retain distinct best continuations, independently of reply order.
function replies(reverse){const g=empty();g.aiStartingDeckOne=[113309,112405];
 add(g,112405,1,0,2,15);add(g,112405,1,0,1,5);
 const body=add(g,112405,8,0,2,8),burn=add(g,113309,8,1,2),first=add(g,112405,8,2,2,3);
 // After Scorch, an 8-point body beats burning the remaining 5-point unit.
 // After a 20-point body, our own Scorch is the stronger continuation.
 add(g,113309,8,0,1).AddTokens(64);add(g,112405,8,1,1,20).AddTokens(64);
 const ids=[body,burn,first].map(c=>c.Snapshot().instanceId),values=[body,burn,first].map(c=>g.AiExactTempo(c));
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,2);
 if(reverse){model.templates.reverse();model.weights.reverse();if(model.knownIds)model.knownIds.reverse();}
 const job=new CBetaGwentAIReplyTree097();job.Initialize(g,first.Snapshot().instanceId,ids,values,model);const before=state(g);run(job);
 check(state(g)===before,'alternating replies preserve source state');check(job.branches===2&&job.follows>=4,'both replies have their own continuations');
 for(let i=0;i<job.replyTemplates.length;i++)check(job.continuationIds[i]===(job.replyTemplates[i]===113309?ids[0]:ids[1]),'resolved reply chooses the stronger actual continuation');
 return {result:job.result,templates:job.replyTemplates,continuations:job.continuationIds,scores:job.branchScores};}
const forward=replies(false),backward=replies(true);
check(JSON.stringify(forward.templates)===JSON.stringify([...backward.templates].reverse()),'reply-order test actually reverses both native public replies');
check(forward.result===backward.result,'all-public reply order does not change conservative result');
check(new Set(forward.continuations).size===2,'different replies can require different best next cards');
// The earlier full-policy hidden-information test has an ambush on the board,
// which deliberately disables this frontier. Exercise the new path without it.
function unknownReplies(strength,mutate){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=empty();g.aiStartingDeckOne=[113309,112405,112101,122106];
 add(g,112405,1,0,2,15);add(g,112405,1,0,1,5);
 const own=[add(g,112405,8,0,2,8),add(g,113309,8,1,2),add(g,112405,8,2,2,3)];
 add(g,112405,8,0,1,7);add(g,112101,8,1,1,4);add(g,122106,16,0,1);
 if(mutate)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId!==1||![8,16].includes(s.locationMask))continue;
  c.definition=BetaGwentDuelDefinition(113309);c.cardState.runtimeTemplate=c.definition.header;c.cardState.originTemplateId=c.TemplateId();c.power.SetCurrentPair(40,9);c.cardState.timerValue=7;
 }
 const before=state(g),ids=own.map(c=>c.Snapshot().instanceId),values=own.map(c=>g.AiExactTempo(c));
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,g.AiReplyLimit097());
 const job=new CBetaGwentAIReplyTree097();job.Initialize(g,ids[2],ids,values,model);run(job);
 check(!job.knownHand&&job.branches>0&&job.follows>0,'unknown-hand test exercises alternating frontier');
 check(state(g)===before,'unknown-hand frontier preserves live state and RNG');
 const explanation=[];Host.log=s=>explanation.push(s);check(g.OpponentStep(),'unknown-hand full decision executes');Host.log=null;
 return {result:job.result,templates:job.replyTemplates,continuations:job.continuationIds,scores:job.branchScores,
  choices:explanation.filter(s=>/event=(OPTION|REJECT|SELECT|PASS)\b/.test(s))};
}
for(const strength of [2,3,4])check(JSON.stringify(unknownReplies(strength,false))===JSON.stringify(unknownReplies(strength,true)),
 'new frontier and final choice ignore hidden enemy identities, powers and timers on level '+strength);
CBetaGwentDuelSession.prototype.AiSimPlay=play;
globalThis.planningReport={checks,positions,completed,cutoffs,integrated,integratedLevels,publicModels:models,maximumPreparationCallbacks,peakSearchPlays:peak,replyExample:forward,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:240000});
const report={fingerprint:manifest.fingerprint,...ctx.planningReport};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
