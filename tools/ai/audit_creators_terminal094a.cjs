'use strict';
// Unlike the earlier derived witness, every option and live decision below
// starts from the identical position, with the same enemy power and RNG.
// Judge both final scores and the match winner, not own material in isolation.
const fs=require('fs'),path=require('path'),vm=require('vm');
const [snapshot,destination]=process.argv.slice(2);if(fs.existsSync(destination))throw Error('Use a fresh report');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(snapshot));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];let serial=-1720000000;
function verify(ok,label){checks++;if(!ok)failures.push(label);}
function finish(g){
 if(g.IsFatal()||g.IsPending())return {complete:false};
 if(!g.Snapshot().matchWinnerMask&&!g.Pass(2))return {complete:false};
 return {complete:!!g.Snapshot().matchWinnerMask,score:[g.Score(1),g.Score(2)],winner:g.Snapshot().matchWinnerMask};
}
for(const id of [112109,122108])for(const counts of [[4,1,0],[0,4,1],[1,0,4]])for(const enemyPower of [10,13,16]){
 const hiddenResults=[];
 for(const hidden of [false,true]){
  const g=fixture();for(const card of g.live)card.Move(card.Snapshot().positionPlayerId,512,0);
  g.random.Initialize(3129701);g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
  for(const [row,n]of [[1,counts[0]],[2,counts[1]],[4,counts[2]]])for(let i=0;i<n;i++)add(g,112101,row,i,2,5);
  for(const row of [1,2,4])add(g,112101,row,0,1,enemyPower);
  add(g,hidden?122106:112101,8,0,1,hidden?99:1);
  const card=add(g,id,8,0);g.archetypeAI.Refresh();g.aiSimDamp=40;const options=[];
  for(const row of [1,2,4])for(let index=0;index<=g.CountLocation(2,row);index++){
   const h=new CBetaGwentCloner().CloneSession(g,--serial),draws=h.random.DrawCount();
   if(!h.PlayAtIndex(2,card.Snapshot().instanceId,row,index)){options.push({complete:false});continue;}
   options.push({row,index,...finish(h),draws:h.random.DrawCount()-draws});
  }
  const deterministic=options.every(o=>o.complete&&o.draws===0);
  let ticks=0;while(!g.AiPreparationStep())if(++ticks>5000)throw Error('Preparation limit');
  let attempts=0;while(!g.OpponentStep()){
   if(++attempts>5||g.IsFatal()||g.IsPending())throw Error('Decision rejected');
   while(!g.AiPreparationStep())if(++ticks>5000)throw Error('Preparation limit');
  }
  const actual=finish(g),winning=options.some(o=>o.complete&&o.winner===2),missed=deterministic&&winning&&actual.winner!==2;
  verify(actual.complete,'complete actual terminal creator turn');
  records.push({id,counts,enemyPower,hidden,deterministic,options,actual,availableWinMissed:missed});
  hiddenResults.push(JSON.stringify(actual));
 }
 verify(hiddenResults[0]===hiddenResults[1],'hidden passed-opponent hand does not change terminal result');
}
globalThis.result={checks,failures,records,eligible:records.filter(r=>r.deterministic).length,
 missedWins:records.filter(r=>r.availableWinMissed).length,actualWitcherScript:true,
 independentOracle:'All real legal placements on the same position, both final scores and actual final-round winner; no changed enemy score calibration',
 notStrengthResult:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};fs.writeFileSync(destination,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks:report.checks,failures:report.failures,cases:report.records.length,eligible:report.eligible,missedWins:report.missedWins}));
if(report.failures.length)process.exitCode=1;
