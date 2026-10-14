'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function position(kind){
 const g=fixture();g.random.Initialize(7123);g.aiSimDamp=0;
 g.live.filter(c=>c.cardState.positionPlayerId===2&&c.cardState.locationMask===8).forEach(c=>c.Move(2,512,0));
 g.match.roundNumber=3;g.match.turnSequence=21;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;
 add(g,142317,1,0,1,8);add(g,132314,2,0,1,6);add(g,142317,4,0,2,7);
 const hand=kind===0?[152304,200296,113301,142317]:kind===1?[142106,201772,113319]:kind===2?[132202,201701,132305]:[142203,113201,113319];
 hand.forEach((t,i)=>add(g,t,8,i,2));
 for(let i=0;i<4;i++)add(g,[142317,132314,113301,132304][i],16,i,2);
 for(let i=0;i<3;i++)add(g,kind===1?113301:132304,32,i,2);
 if(kind===2){add(g,132305,1,0,2);add(g,132305,16,4,2);}
 if(kind===4)add(g,200169,64,0,2);
 if(kind===5){g.match.playerOne.hasPassed=true;g.match.playerOne.hasMadeInitialMoveForCurrentTurn=true;}
 return g;
}
function state(g){return JSON.stringify({match:g.match.Snapshot(),live:g.live.map(c=>c.Snapshot()),draws:g.random.DrawCount(),fatal:g.IsFatal(),pending:g.IsPending()});}
for(const strength of [1,2,3,4])for(const kind of [0,1,2,3,4,5]){
 Host.strength=strength;const sync=position(kind),staged=position(kind),initial=state(staged);
 let ticks=0;while(!staged.AiPreparationStep()){
  check(state(staged)===initial,'preparation does not play or consume live RNG '+strength+'/'+kind+'/'+ticks);
  if(++ticks>40)throw Error('preparation stalled');
 }
 check(staged.AiPreparationIsReady(),'preparation completes '+strength+'/'+kind);
 const original=staged.AiSimClone;let clones=0;staged.AiSimClone=function(){clones++;return original.call(this);};
 for(let i=0;i<staged.aiPreparedIds.length;i++)check(staged.AiExactTempo(staged.FindCard(staged.aiPreparedIds[i]))===staged.aiPreparedValues[i],'prepared exact result reused '+i);
 check(clones===0,'cached exact values do not repeat simulation '+strength+'/'+kind);
 const syncResult=sync.OpponentStep(),stagedResult=staged.OpponentStep();
 check(syncResult===stagedResult&&state(sync)===state(staged),'cooperative and synchronous decisions agree '+strength+'/'+kind);
 staged.match.turnSequence++;check(!staged.AiPreparationIsReady(),'next turn rejects stale preparation');
 staged.ClearAiPreparation();check(staged.aiPreparedIds.length===0&&!staged.aiPreparationReady,'reset releases search state');
}
Host.strength=4;
const g=position(0);while(!g.AiPreparationStep()){}
const clone=g.AiSimClone();check(!clone.aiPreparationReady&&clone.aiPreparedIds.length===0,'simulation clone excludes parent search cache');
const exhausted=position(0);exhausted.live.filter(c=>c.cardState.positionPlayerId===1&&c.cardState.locationMask===8).forEach(c=>c.Move(1,512,0));
exhausted.recordVisuals=true;exhausted.visualFrames=[];while(!exhausted.AiPreparationStep()){}
exhausted.PumpOpponent();
check(exhausted.match.playerOne.hasPassed||exhausted.waiting,'yielding visible AI actions still auto-passes an exhausted human hand');
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{timeout:120000});
console.log('PASS '+context.report.checks+' cooperative AI checks');
