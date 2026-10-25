// A slow-device budget must retain bounded counterplay in a mandatory short round.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function position(count,damp){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=damp;
 g.aiStartingDeckOne=[113309,112405,112405];
 add(g,112405,1,0,2,9);add(g,112405,1,0,1,5);
 [113309,112405,112405,112405].slice(0,count).forEach((t,i)=>add(g,t,8,i,2,t===113309?undefined:8-i));
 add(g,112405,8,0,1,12);add(g,113309,8,1,1);return g;}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount(),request:g.requestId});}
const play=CBetaGwentDuelSession.prototype.AiSimPlay,step=CBetaGwentAIReplyTree097.prototype.Step;
let calls=0,treeCalls=0,peak=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return play.apply(this,a);};
CBetaGwentAIReplyTree097.prototype.Step=function(){treeCalls++;return step.call(this);};
const cases=[];
for(const strength of [2,3,4])for(const damp of [65,70])for(const count of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const sync=position(count,damp),staged=position(count,damp),before=state(staged);
 treeCalls=0;check(sync.OpponentStep(),'synchronous decision completes');const synchronousTrees=treeCalls;
 let ticks=0;treeCalls=0;while(true){calls=0;const ready=staged.AiPreparationStep();peak=Math.max(peak,calls);
  check(calls<=1,'one simulated play per preparation callback');check(state(staged)===before,'preparation preserves live state and RNG');
  ticks++;if(ready)break;if(ticks>650)throw Error('short-round preparation stalled');}
 const preparedTrees=treeCalls;check(staged.OpponentStep(),'prepared decision completes');
 check(state(sync)===state(staged),'synchronous and prepared decisions agree');
 if(count<=3)check(synchronousTrees>0&&preparedTrees>0,'critical short round retains public-reply search at reduced budget');
 else check(synchronousTrees===0&&preparedTrees===0,'large-hand reduced budget keeps existing fallback');
 cases.push({strength,damp,count,synchronousTrees,preparedTrees,ticks});
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;CBetaGwentAIReplyTree097.prototype.Step=step;
globalThis.result={checks,cases,peakSearchPlays:peak,actualWitcherScript:true};
`,ctx,{timeout:240000});
const report={fingerprint:manifest.fingerprint,...ctx.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));
