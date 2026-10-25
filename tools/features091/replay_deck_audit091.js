// Reproduce a diagnostic turn, then finish the real match after alternative plays.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib'),crypto=require('crypto');
const input=path.resolve(process.argv[2]||''),step=Number(process.argv[3]);
if(!fs.existsSync(input)||!Number.isInteger(step))throw Error('Usage: replay_deck_audit091.js trace.json.gz step [output.json]');
const run=path.dirname(path.dirname(input)),config=JSON.parse(fs.readFileSync(path.join(run,'config.json'),'utf8'));
const trace=JSON.parse(zlib.gunzipSync(fs.readFileSync(input))),manifest=JSON.parse(fs.readFileSync(path.join(config.snapshot,'manifest.json'),'utf8'));
for(const name of ['runtime.js','rules.js','harness.js','tunes.json'])if(crypto.createHash('sha256').update(fs.readFileSync(path.join(config.snapshot,name))).digest('hex')!==manifest.snapshotFiles[name])throw Error('Changed snapshot: '+name);
const ctx=vm.createContext({console});vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(config.snapshot,n),'utf8')).join('\n')+'\n'+require('../ai/comparison_bridge119.js'),ctx);
ctx.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(config.snapshot,'tunes.json'),'utf8')));ctx.bridge.setStrength(4);
vm.runInContext(String.raw`
function auditView(){return {view:bridge.view(),preset:active.presetTwo,crowns:[active.Snapshot().playerOne.crowns,active.Snapshot().playerTwo.crowns],cards:active.live.filter(c=>[1,2,4,8,32,64].includes(c.Snapshot().locationMask)).map(c=>{
 const s=c.Snapshot();return {id:s.instanceId,template:c.TemplateId(),title:c.Definition().title,side:s.positionPlayerId,zone:s.locationMask,power:s.power.currentPower,timer:s.timerValue,tokens:s.tokenMask,reserve:active.AiReserveCost(c.Definition()),canPlay:Boolean(s.locationMask===64?active.LeaderAvailable(s.positionPlayerId):s.canBePlayed)};})};}
function auditForce(id){__context(active);const c=active.FindCard(id),s=c.Snapshot(),d=c.Definition();if(s.locationMask===64)return active.UseLeader(2);
 let row=active.BestCardRow(2,d)||1,anchor=d.effect===23?active.BestVranAnchor(2):0;if(!anchor)anchor=active.AiPlacementAnchor(d);
 return anchor?active.PlayBefore(2,id,anchor):active.Play(2,id,row);}
function auditFinish(){const decisions=[];for(let i=0;i<500;i++){
 let v=bridge.view();if(v.fatal)throw Error(v.message);if(v.winner){let winner=v.winner;if(v.reversed)winner=((winner&1)<<1)|((winner&2)>>1);return {winner,steps:i,final:auditView(),decisions};}
 if(!v.mulligan&&!v.pending&&!v.waiting&&v.current===1)bridge.swap();
 const start=analysisLogs.length;bridge.step();decisions.push({view:bridge.view(),logs:analysisLogs.slice(start)});
 }throw Error('Decision limit');}
`,ctx);
let logs=[];ctx.analysisLogs=logs;ctx.bridge.setLog(s=>logs.push(s));
const saved=trace.suspects.find(s=>s.step===step);
if(saved)ctx.bridge.load(saved.state);else{
 ctx.bridge.load(trace.initial);ctx.bridge.initialMulligan();
 for(let i=0;i<step;i++)ctx.bridge.step();
 const v=ctx.bridge.view();if(!v.mulligan&&!v.pending&&!v.waiting&&v.current===1)ctx.bridge.swap();
}
const state=ctx.bridge.dump(),before=vm.runInContext('auditView()',ctx),original=trace.decisions.find(d=>d.step===step);
if(!original||before.preset!==original.before.preset||JSON.stringify(before.view.score)!==JSON.stringify(original.before.score))throw Error('Position did not reproduce');
const candidates=before.cards.filter(c=>c.side===2&&[8,64].includes(c.zone)&&c.canPlay),results=[];
for(const card of [null,'pass-now',...candidates]){
 ctx.bridge.load(state);logs=[];ctx.analysisLogs=logs;ctx.bridge.setLog(s=>logs.push(s));ctx.candidateId=card?.id;
 try{const ok=card==='pass-now'?vm.runInContext('active.Pass(2)',ctx):card?vm.runInContext('auditForce(candidateId)',ctx,{timeout:300000}):(ctx.bridge.step(),true);if(!ok)throw Error('Play rejected');
  const after=vm.runInContext('auditView()',ctx),actionLogs=logs.slice(),continuation=vm.runInContext('auditFinish()',ctx,{timeout:300000});
  results.push({card:card||'original-ai-decision',after,actionLogs,...continuation});
 }catch(e){results.push({card:card||'original-ai-decision',error:String(e.stack||e)});}
}
const baseline=results[0],originalReproduced=baseline.winner===trace.winner&&JSON.stringify([...(baseline.actionLogs||[]),...(baseline.decisions||[]).flatMap(d=>d.logs)])===JSON.stringify(trace.logs.filter(l=>l.step>=step).map(l=>l.text));
const result={trace:input,step,task:trace.task,before,original,originalReproduced,results,limitation:'Alternative full matches use actual hidden decks for rules execution and the same AI for both seats. Changed draw order can change both hands; results diagnose a line, not policy strength.'};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(result,null,2));
console.log(JSON.stringify({step,originalReproduced,preset:before.preset,round:before.view.round,score:before.view.score,original:original.selection||original.pass,results:results.map(r=>({card:r.card,winner:r.winner,error:r.error,afterScore:r.after?.view.score,afterHand:r.after?.view.hand,steps:r.steps,firstLogs:r.actionLogs?.filter(s=>/SELECT|PASS|NO_TARGET/.test(s)).slice(0,5)}))},null,1));
if(!originalReproduced)process.exitCode=1;
