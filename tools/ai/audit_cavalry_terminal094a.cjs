'use strict';
// Hypothesis audit: enumerate real legal cavalry targets at the end of round 3.
// Only compare choices from the identical state; no continuation oracle.
const fs=require('fs'),path=require('path'),vm=require('vm');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];let serial=-1740000000;
function verify(ok,label){checks++;if(!ok)failures.push(label);}
function terminal(g){
 verify(!g.IsFatal()&&!g.IsPending(),'resolved terminal target');
 if(!g.Snapshot().matchWinnerMask)verify(g.Pass(2),'terminal pass');
 const m=g.Snapshot();return {winner:m.matchWinnerMask,score:[g.Score(1),g.Score(2)]};
}
for(const ownArmor of [5,10,20,30])for(const enemyArmor of [1,8])for(const hidden of [false,true]){
 const g=fixture();for(const card of g.live)card.Move(card.Snapshot().positionPlayerId,512,0);
 g.random.Initialize(174031);g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
 const own=add(g,112101,1,0,2,11);own.power.SetCurrentPair(11,ownArmor);
 const enemy=add(g,112101,4,0,1,27);enemy.power.SetCurrentPair(27,enemyArmor);
 add(g,hidden?122106:112101,8,0,1,hidden?99:1);
 const cavalry=add(g,122314,8,0,2);g.archetypeAI.Refresh();g.aiSimDamp=40;
 const start=new CBetaGwentCloner().CloneSession(g,--serial);start.externalPolicyMask=3;
 verify(start.Play(2,cavalry.Snapshot().instanceId,4),'explicit cavalry deploy');
 verify(start.IsPending()&&start.pendingIds.length>1,'real target pool includes competing targets');
 const options=[];
 for(const target of start.pendingIds){
  const h=new CBetaGwentCloner().CloneSession(start,--serial);h.externalPolicyMask=3;
  const draws=h.random.DrawCount();verify(h.SelectTarget(h.requestId,target),'enumerated target accepted');
  const result=terminal(h);verify(h.random.DrawCount()===draws,'deterministic oracle');
  options.push({target,result});
 }
 const best=Math.max(...options.map(o=>o.result.score[1]-o.result.score[0]));
 let ticks=0;while(!g.AiPreparationStep())if(++ticks>5000)throw Error('Preparation limit');
 let attempts=0;while(!g.OpponentStep()){
  if(++attempts>5||g.IsFatal()||g.IsPending())throw Error('Policy rejected');
  while(!g.AiPreparationStep())if(++ticks>5000)throw Error('Preparation limit');
 }
 const chosen=terminal(g),optimal=chosen.score[1]-chosen.score[0]===best;
 records.push({ownArmor,enemyArmor,hidden,options,best,chosen,optimal});
}
globalThis.result={checks,failures,records,suboptimalChoices:records.filter(r=>!r.optimal).length,actualWitcherScript:true,independentOracle:'All legal targets from identical full state, actual current end-turn and final-round resolution',notStrengthResult:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};
if(process.argv[3]){if(fs.existsSync(process.argv[3]))throw Error('Use a fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({checks:report.checks,failures:report.failures,cases:report.records.length,suboptimalChoices:report.suboptimalChoices}));
if(report.failures.length)process.exitCode=1;
