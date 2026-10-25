// Recorded random-audit positions motivated by observed human card-preservation play.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const snapshot=path.resolve(process.argv[2]),out=process.argv[3],ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
ctx.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(snapshot,'tunes.json'),'utf8')));ctx.bridge.setStrength(4);
const fixtures=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/human_patterns094.json.gz'))));
let checks=0;const cases=[];function check(v,label){checks++;if(!v)throw Error(label);}
for(const f of fixtures.cases){
 function run(staged,mutate){ctx.bridge.load(f.state);ctx.mutate=mutate;const logs=[];ctx.bridge.setLog(s=>logs.push(s));
  vm.runInContext(`if(mutate)for(const c of active.live){const s=c.Snapshot();if(s.positionPlayerId===1&&(s.locationMask===8||s.locationMask===16)&&(s.tokenMask&64)===0){c.definition=BetaGwentDuelDefinition(122106);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(40,9);}}`,ctx);
  const draws=vm.runInContext('active.random.DrawCount()',ctx),before=ctx.bridge.view();
  if(staged){let ticks=0;while(!vm.runInContext('active.AiPreparationStep()',ctx))if(++ticks>500)throw Error('Preparation stalled');}
  try{if(staged){let attempts=0;while(!vm.runInContext('active.OpponentStep()',ctx)){
   if(++attempts>3||!vm.runInContext('active.aiPreparationStage>0&&!active.aiPreparationReady',ctx))throw Error('decision rejected');
   let ticks=0;while(!vm.runInContext('active.AiPreparationStep()',ctx))if(++ticks>500)throw Error('chase stalled');
  }}else ctx.bridge.step();}catch(e){throw Error(f.game+'/'+f.step+' staged='+staged+' hidden='+mutate+' '+e);}const after=ctx.bridge.view(),line=logs.find(s=>/event=SELECT\b/.test(s))||logs.find(s=>/event=PASS\b/.test(s));
  const template=Number(/template=(\d+)/.exec(line||'')?.[1]||0);
  return {before,after,line,template,draws,afterDraws:vm.runInContext('active.random.DrawCount()',ctx),logs};
 }
 const plain=run(false,false),staged=run(true,false),hidden=run(false,true);
 check(!plain.after.fatal&&!plain.after.pending,'complete recorded decision '+f.game+'/'+f.step);
 check(plain.template===staged.template,'same synchronous/cooperative choice '+f.game+'/'+f.step);
 check(plain.template===hidden.template,'closed opposing identities do not change choice '+f.game+'/'+f.step);
 if(f.game==='game-00094'){
  check(plain.template===200539,'Slyzard receives an exact trial and preserves Mourntart');
  check(plain.after.score[1]>plain.after.score[0],'the cheaper action really overtakes the passed opponent');
  check(vm.runInContext('active.live.some(c=>c.TemplateId()===132202&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8)',ctx),'finisher remains in hand');
  // Both views have a passed enemy, so no hidden opposing play can change this result.
  ctx.bridge.load(f.state);vm.runInContext('active.OpponentStep();active.Pass(2)',ctx);
  check(vm.runInContext('active.Snapshot().playerTwo.crowns>0&&!active.IsFatal()',ctx),'a real pass confirms the required round is won');
 }
 if(f.game==='game-00021'){
  check(plain.template===132409,'one duplicate Ekhidna catches the dry pass instead of spending gold Imlerith');
  check(plain.after.score[1]>plain.after.score[0],'the Bronze really takes the lead');
  check(vm.runInContext('active.live.some(c=>c.TemplateId()===201781&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8)',ctx),'Imlerith remains for the final');
  check(vm.runInContext('active.live.filter(c=>c.TemplateId()===132409&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).length===1',ctx),'one duplicate removal remains available');
 }
 cases.push({game:f.game,step:f.step,previousTemplate:f.picked.template,template:plain.template,selection:plain.line,stagedMatches:true,hiddenIndependent:true});
}
const report={checks,cases,source:fixtures.origin,actualWitcherScript:true,nativeGameTested:false};
if(out)fs.writeFileSync(out,JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
