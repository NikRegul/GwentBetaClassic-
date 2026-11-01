'use strict';
// End-of-turn ships still trigger on the action played after an enemy pass.
// Oracle: real legal insertion positions and round resolution, no policy formula.
const fs=require('fs'),path=require('path'),vm=require('vm');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],records=[];let serial=-1670000000;
function verify(ok,name){checks++;if(!ok)failures.push(name);}
function buildShip(id,counts,enemy,hidden=false){
 const g=fixture();for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.random.Initialize(3129701);g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
 for(const [row,n]of [[1,counts[0]],[2,counts[1]],[4,counts[2]]])for(let i=0;i<n;i++)add(g,112101,row,i,2,5);
 add(g,112101,4,0,1,enemy);
 if(hidden)add(g,122106,8,0,1,99);else add(g,112101,8,0,1,1);
 const card=add(g,id,8,0);g.archetypeAI.Refresh();g.aiSimDamp=40;return {g,card};
}
function finish(g){verify(!g.IsPending()&&!g.IsFatal(),'resolved ship action');
 if(!g.Snapshot().matchWinnerMask)verify(g.Pass(2),'final pass accepted');
 return {winner:g.Snapshot().matchWinnerMask,score:[g.Score(1),g.Score(2)]};}
for(const id of [152109,152309])for(const counts of [[4,1,0],[0,4,1],[1,0,4]]){
 const first=buildShip(id,counts,0),options=[];
 for(const row of [1,2,4])for(let index=0;index<=first.g.CountLocation(2,row);index++){
  const h=new CBetaGwentCloner().CloneSession(first.g,--serial),draws=h.random.DrawCount();
  verify(h.PlayAtIndex(2,first.card.Snapshot().instanceId,row,index),'explicit legal ship insertion');
  const result=finish(h);verify(h.random.DrawCount()===draws,'no random-outcome hindsight');options.push({row,index,own:result.score[1]});
 }
 const best=Math.max(...options.map(x=>x.own)),worst=Math.min(...options.map(x=>x.own));
 verify(best>worst,'position exposes a real insertion difference');
 const enemy=best-1,choices=[];
 for(const hidden of [false,true]){
  const {g,card}=buildShip(id,counts,enemy,hidden),logs=[];Host.log=s=>logs.push(s);
  let ticks=0;try{
   while(!g.AiPreparationStep())if(++ticks>5000)throw Error('Preparation limit');
   let attempts=0;while(!g.OpponentStep()){
    if(++attempts>5||g.IsFatal()||g.IsPending())throw Error('Decision rejected');
    while(!g.AiPreparationStep())if(++ticks>5000)throw Error('Preparation limit');
   }
  }finally{Host.log=null;}
  const state=card.Snapshot(),result=finish(g);
  verify(result.winner===2,'ship takes the available final-round win '+id+'/'+counts+'/'+hidden);
  verify(result.score[1]===best,'ship realizes best deterministic terminal material '+id+'/'+counts+'/'+hidden);
  choices.push([state.locationMask,state.locationIndex,result.winner,result.score[1]]);
  records.push({id,counts,hidden,enemy,best,worst,chosen:choices[choices.length-1],result,options,logs});
 }
 verify(JSON.stringify(choices[0])===JSON.stringify(choices[1]),'hidden opposing identities do not affect the result');
}
globalThis.result={checks,failures,records,actualWitcherScript:true,independentOracle:'All legal insertions, actual end-turn effects and final round winner',notStrengthResult:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks:report.checks,failures:report.failures,cases:report.records.length}));if(report.failures.length)process.exitCode=1;
