// Four-card mandatory fronts: preserve a winning body line, not self-Scorch.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');const {context:ctx,manifest}=load(path.resolve(process.argv[2]));ctx.observe=process.argv.includes('--observe');
const helper=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+helper+String.raw`
const failures=[],cases=[];check=(ok,name)=>{checks++;if(!ok){failures.push(name);if(!observe)throw Error(name);}};
function position(model,strength=4,damp=40){Host.strength=strength;Host.matchStrength=[strength,strength];const [power,gold,enemy,small,extra]=model,g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=damp;g.aiStartingDeckOne=[112405];
 const tall=add(g,112405,1,0,2,power);add(g,112103,2,0,2,gold);add(g,112405,1,0,1,enemy);
 const burn=add(g,113309,8,0,2),bodies=[add(g,112405,8,1,2,small),add(g,112405,8,2,2,extra),add(g,112405,8,3,2,extra)],reply=add(g,112405,8,0,1,power+gold+small-enemy);reply.AddTokens(64);return {g,tall,burn,bodies,reply};}
const models=[[19,1,5,3,1],[13,2,8,4,1],[26,3,11,2,2]];
const state=g=>JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()]});
const play=CBetaGwentDuelSession.prototype.AiSimPlay,pass=CBetaGwentDuelSession.prototype.Pass;let calls=0,peakActions=0,maxCallbacks=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
CBetaGwentDuelSession.prototype.Pass=function(...args){calls++;return pass.apply(this,args);};
for(const model of models)for(const strength of [3,4])for(const damp of [0,40,70])for(const staged of [false,true]){
 const {g,tall,burn,bodies,reply}=position(model,strength,damp);check(g.CountLocation(2,8)===4&&g.AiShortRoundPlanning()===(damp<50),'four-card whole-line comparison respects the normal/slow-device budget boundary');
 if(staged){const before=state(g);let ticks=0;while(true){calls=0;const ready=g.AiPreparationStep();peakActions=Math.max(peakActions,calls);
  check(calls<=1,'one simulated card/leader/pass action per preparation callback');check(state(g)===before,'four-card preparation preserves live match and RNG');
  if(ready)break;if(++ticks>2200)throw Error('Four-card preparation stalled');}maxCallbacks=Math.max(maxCallbacks,ticks);}
 check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'full policy chooses a legal opening');
 check(!g.aiEndgameComplete097,'gold board keeps this outside the separate exact bronze solver');
 check(!g.Snapshot().playerTwo.hasPassed&&burn.Snapshot().locationMask===8&&bodies.some(c=>c.Snapshot().locationMask!==8),'policy keeps Scorch and opens a body');
 check(g.Play(1,reply.Snapshot().instanceId,1),'actual revealed final opposing body is played');
 check(g.OpponentStep()&&!g.IsFatal()&&!g.IsPending(),'policy spends its available winning follow-up');
 check(g.Score(2)>g.Score(1)&&burn.Snapshot().locationMask===8&&tall.Snapshot().locationMask===1,'follow-up really wins on the board and preserves our tall unit');
 check(g.Pass(1)&&g.Pass(2)&&g.Snapshot().matchWinnerMask===2,'independent authoritative passes confirm the match win');
 cases.push({model,strength,damp,staged,winner:g.Snapshot().matchWinnerMask});
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;CBetaGwentDuelSession.prototype.Pass=pass;
// A direct destructive first move loses even after spending every other card.
for(const model of models){const {g,burn,bodies,reply}=position(model);check(g.Play(2,burn.Snapshot().instanceId,1),'negative witness Scorch is legal');
 check(g.Play(1,reply.Snapshot().instanceId,1),'negative witness opposing body is legal');
 check(g.Play(2,bodies[0].Snapshot().instanceId,1)&&g.Pass(1),'negative witness starts the remaining body sequence');
 for(const b of bodies.slice(1))check(g.Play(2,b.Snapshot().instanceId,1),'negative witness spends every remaining body');
 check(g.Pass(2)&&g.Snapshot().matchWinnerMask===1,'self-Scorch cannot recover the match even with all three bodies');}
const g=position(models[0]).g;add(g,112405,8,4,2,1);check(!g.AiShortRoundPlanning(),'larger hands keep the existing bounded fallback');
const h=position(models[0]).g;add(h,200164,64,0,1);check(!h.AiShortRoundPlanning(),'a remaining enemy leader prevents a short plain-hand assumption');
globalThis.result={checks,failures,cases,peakActions,maxCallbacks,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({fingerprint:report.fingerprint,checks:report.checks,failures:report.failures,peakActions:report.peakActions,cases:report.cases.length}));if(report.failures.length)process.exitCode=1;
