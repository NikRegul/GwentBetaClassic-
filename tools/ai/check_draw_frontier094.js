// A resolved drawing pass must remain available while seeking a winning card.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],cases=[];check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
const models=[[19,1,5,3],[13,2,8,4],[26,3,11,2]];
function position(model=models[0],strength=4,damp=40){Host.strength=strength;Host.matchStrength=[strength,strength];
 const [power,gold,enemy,small]=model,g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=damp;g.aiStartingDeckOne=[112405];
 add(g,112405,1,0,2,power);add(g,112103,2,0,2,gold);add(g,112405,1,0,1,enemy);
 const burn=add(g,113309,8,0,2),body=add(g,112405,8,1,2,small);
 const reply=add(g,112405,8,0,1,power+gold+small-enemy);reply.AddTokens(64);
 return {g,burn,body,reply};}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,waiting:g.waiting});}
let calls=0,peakActions=0,maximumCallbacks=0;
const play=CBetaGwentDuelSession.prototype.AiSimPlay,pass=CBetaGwentDuelSession.prototype.Pass;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
CBetaGwentDuelSession.prototype.Pass=function(...args){calls++;return pass.apply(this,args);};
function run(p){const {g,burn,body}=p,own=[burn,body],ids=own.map(c=>c.Snapshot().instanceId),values=own.map(c=>g.AiExactTempo(c));
 const response=new CBetaGwentPublicResponseAI();response.Initialize(g,1);
 const tree=new CBetaGwentAIReplyTree097();tree.Initialize(g,ids[1],ids,values,response);
 const before=state(g);let ticks=0;while(true){calls=0;const done=tree.Step();peakActions=Math.max(peakActions,calls);
  check(calls<=1,'drawing/continuation settlement has at most one action per callback');
  check(state(g)===before,'drawing probe preserves the real match and RNG');
  if(done)break;if(++ticks>150)throw Error('frontier stalled');}
 maximumCallbacks=Math.max(maximumCallbacks,ticks);return tree;}
for(const model of models)for(const strength of [3,4])for(const damp of [0,40,70]){
 const p=position(model,strength,damp),tree=run(p),{g,burn,body}=p;
 check(tree.branchScores[0]===0&&tree.continuationIds[0]===0,'actual drawing pass floors the losing forced-card continuation');
 const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'actual policy completes');
 check(!g.aiEndgameComplete097,'gold board is outside the separate exact plain-bronze solver');
 check(body.Snapshot().locationMask!==8&&burn.Snapshot().locationMask===8,'policy preserves the available drawing line');
 cases.push({model,strength,damp,scores:tree.branchScores,continuations:tree.continuationIds,selected:logs.filter(s=>/event=SELECT/.test(s))});
}
// Do not stop at a draw when the remaining Scorch wins after the same reply.
{
 const p=position([5,8,10,3]),tree=run(p);
 check(tree.branchScores[0]===30&&tree.continuationIds[0]===p.burn.Snapshot().instanceId,'resolved winning continuation outranks the drawing pass, regardless of raw uplift');
 cases.push({kind:'win-instead-of-draw',scores:tree.branchScores,continuations:tree.continuationIds});
}
// Integrated cooperative execution must use the same complete-line contract.
for(const model of models){const p=position(model),{g,burn,body}=p,before=state(g);let ticks=0;
 while(true){calls=0;const ready=g.AiPreparationStep();peakActions=Math.max(peakActions,calls);
  check(calls<=1,'integrated drawing preparation respects the one-action budget');
  check(state(g)===before,'integrated drawing preparation preserves live state');
  if(ready)break;if(++ticks>650)throw Error('drawing preparation stalled');}
 check(g.OpponentStep()&&!g.IsPending()&&!g.IsFatal(),'cooperative policy completes');
 check(body.Snapshot().locationMask!==8&&burn.Snapshot().locationMask===8,'cooperative policy chooses the drawing line');}
CBetaGwentDuelSession.prototype.AiSimPlay=play;CBetaGwentDuelSession.prototype.Pass=pass;
// Independent outcome witnesses use only actual actions of the shared rules.
const witnesses=[];
for(const model of models){
 const {g,burn,body,reply}=position(model);
 check(g.Play(2,body.Snapshot().instanceId,1)&&g.Play(1,reply.Snapshot().instanceId,1),'native drawing sequence executes');
 check(g.Score(1)===g.Score(2)&&g.Pass(2)&&g.Pass(1),'actual equal score settles via the only remaining opposing action');
 check(g.Snapshot().matchWinnerMask===3&&burn.Snapshot().locationMask===8,'native result is a draw with Scorch retained');
 const old=position(model);
 check(old.g.Play(2,old.burn.Snapshot().instanceId,1)&&old.g.Pass(1)&&old.g.Play(2,old.body.Snapshot().instanceId,1)&&old.g.Pass(2),'native old opener has a legal opposing winning reply');
 check(old.g.Snapshot().matchWinnerMask===1,'self-Scorch loses where the alternative draws');
 witnesses.push({model,candidateResult:3,oldResult:1});
}
{
 const {g,burn,body,reply}=position([5,8,10,3]);
 check(g.Play(2,body.Snapshot().instanceId,1)&&g.Play(1,reply.Snapshot().instanceId,1)&&g.Play(2,burn.Snapshot().instanceId,1)&&g.Pass(1)&&g.Pass(2),'native win-seeking continuation executes');
 check(g.Snapshot().matchWinnerMask===2,'continuing beyond the available draw really wins');
}
globalThis.result={checks,failures,cases,witnesses,peakActions,maximumCallbacks,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:120000});
const report={fingerprint:manifest.fingerprint,...ctx.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(report.failures.length)process.exitCode=1;
