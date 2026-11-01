'use strict';
// Inspect the actual pass gates on a verified recorded-action reconstruction.
// The alternative branch is an experiment, not a prediction of the human reply.
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib'),crypto=require('crypto');
const [snapshot,replayDir,output]=process.argv.slice(2);if(!output||fs.existsSync(output))throw Error('snapshot verified-replay new-report');
const verification=JSON.parse(fs.readFileSync(path.join(replayDir,'report.json'),'utf8'));
if(!verification.complete)throw Error('Complete observable verification required');
const ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
vm.runInContext(String.raw`
const gates=[];
for(const name of ['BetaGwentAIRoundDecision','BetaGwentAIEarlyPass','BetaGwentAIInvestmentPass']){
 const original=eval(name);globalThis[name]=function(...args){const value=original(...args);gates.push({name,args,result:value});return value;};
}
function view(g){const m=g.Snapshot();return {round:m.roundNumber,current:m.currentPlayerId,score:[g.Score(1),g.Score(2)],hand:[g.CountLocation(1,8),g.CountLocation(2,8)],crowns:[m.playerOne.crowns,m.playerTwo.crowns],passed:[m.playerOne.hasPassed,m.playerTwo.hasPassed],fatal:g.IsFatal()};}
function decide(state,damp){active=unpack(state);active.aiSimDamp=damp;Host.log=null;gates.length=0;
 const before=view(active),passLead=active.AiPublicPassLead(true);let ticks=0;
 while(!active.AiPreparationStep()){if(++ticks>10000)throw Error('preparation stalled');}
 const logs=[];Host.log=s=>logs.push(s);let ok=active.OpponentStep();Host.log=null;
 return {damp,before,passLead,preparedCallbacks:ticks,committed:ok,gates:JSON.parse(JSON.stringify(gates)),after:view(active),logs:logs.filter(s=>/event=(SELECT|PASS|PLAN)|DUEL_AI_PASS/.test(s))};
}
function passExperiment(state){const g=unpack(state),before=view(g);if(!g.Pass(2))throw Error('AI pass rejected');const afterPass=view(g);
 if(!g.Pass(1))throw Error('human reply pass rejected');const afterBothPass=view(g);
 if(g.IsWaitingRound()&&!g.BeginNextRound())throw Error('next round rejected');
 return {assumedHumanReply:'pass',before,afterPass,afterBothPass,nextRound:view(g),morkvarg:g.live.filter(c=>c.TemplateId()===152209).map(c=>c.Snapshot())};
}
`,ctx);
const records=[];
for(const decision of [8,9,10,12,13]){
 const f=path.join(replayDir,`match-1-decision-${decision}.json.gz`);ctx.capture=JSON.parse(zlib.gunzipSync(fs.readFileSync(f)));
 records.push({decision,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'),
  decisions:[40,70].map(damp=>vm.runInContext(`decide(capture.state,${damp})`,ctx)),
  ...(decision===9?{alternative:vm.runInContext('passExperiment(capture.state)',ctx)}:{})});
}
const report={complete:true,records,notStrengthResult:true,nativeGameplayVerified:false,
 scope:'Same WS-to-JS engine, recorded-action states with every logged observable checked. Recomputed decisions use fresh preparation; private historical AI caches and host timing are not reproduced. The human pass branch is an explicit assumption.'};
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(records.map(r=>({decision:r.decision,...r.decisions[1]})),null,2));
