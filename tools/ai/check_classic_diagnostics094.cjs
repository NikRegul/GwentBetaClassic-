'use strict';
const fs=require('fs'),zlib=require('zlib'),assert=require('node:assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs'),{BetaTurnController}=require('./beta_js092/controller.cjs');
const {personality}=require('./beta_js092/profiles.cjs'),{createRecorder}=require('./classic_diagnostics094.cjs');
const snapshot=process.argv[2],fixturePath=require('path').join(__dirname,'fixtures/classic-partial-search094-01.json.gz'),f=JSON.parse(zlib.gunzipSync(fs.readFileSync(fixturePath)));
const observer=createRecorder(BetaTurnController);let checks=0;const records=[];
function ok(value){assert(value);checks++;}
for(const budget of [1,8,32]){
 function play(){const rt=createRuntime(snapshot),g=rt.deserialize(JSON.parse(JSON.stringify(f.state)));let ticks=0,clockCalls=0;
  const c=new BetaTurnController(rt,personality(f.view.profile),{now:()=>{clockCalls++;return ticks>=budget?1000000:0;}});c.start(g);
  while(!c.finished){c.step();if(++ticks>10000)throw Error('Controller stalled');}
  return {state:rt.serialize(g),decision:c.chosen.decision,clockCalls,ticks};}
 const plain=play(),observed=observer.play(play),diagnostics=observed.betaDecisionDiagnostics;delete observed.betaDecisionDiagnostics;
 assert.deepEqual(observed,plain);checks++;
 ok(diagnostics.length===1);ok(diagnostics[0].forceAtCallback===budget);ok(diagnostics[0].playmakerError===null);
 ok(!diagnostics[0].position);ok(diagnostics[0].finishReason==='stopped');records.push({budget,...diagnostics[0],clockCalls:plain.clockCalls,ticks:plain.ticks});
}
observer.restore();
// A failed diagnostic must neither replace nor swallow the policy exception.
const originalError=new Error('original policy error');
class ThrowingController{step(){throw originalError;}}
for(const brokenSerializer of [false,true]){
 const recorder=createRecorder(ThrowingController),control=new ThrowingController();
 Object.assign(control,{live:{Snapshot:()=>({currentPlayerId:2,roundNumber:3})},personality:{name:'test'},search:{},searchCallbacks:3,
  runtime:{serialize(){if(brokenSerializer)throw Error('diagnostic serializer failure');return {publicWitness:true};}}});
 const result=recorder.play(()=>{try{control.step();}catch(error){ok(error===originalError);return {caught:true};}throw Error('Exception swallowed');});
 ok(result.caught&&result.betaDecisionDiagnostics.length===1);
 if(brokenSerializer)ok(result.betaDecisionDiagnostics[0].diagnosticError.includes('diagnostic serializer failure'));
 else ok(result.betaDecisionDiagnostics[0].positionPhase==='at-exception');
 recorder.restore();
}
const report={complete:true,checks,records,noClockCallsAdded:true,noRngCallsAdded:true,actualController:true};
const sha=p=>require('crypto').createHash('sha256').update(fs.readFileSync(p)).digest('hex');
report.observerSha256=sha(require('path').join(__dirname,'classic_diagnostics094.cjs'));
report.controllerSha256=sha(require('path').join(__dirname,'beta_js092/controller.cjs'));
report.manifestSha256=sha(require('path').join(snapshot,'manifest.json'));
report.fixtureSha256=sha(fixturePath);
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks,complete:true}));
