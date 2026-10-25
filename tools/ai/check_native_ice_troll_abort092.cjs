/* Original-runtime diagnosis. Trace-on/off runs must produce identical
 * states/RNG. Separate cleanup audit preserves fatal/poisoned state forever;
 * no normal continuation or rating is allowed. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {technicalAction}=require('./check_native_choice_adapter092.cjs');
const root=path.resolve(__dirname,'../..'),draft=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const canonical=s=>{
 const {originalActionTrace,loggerNoRequestContexts,...model}=s;
 return JSON.stringify(model);
};
async function capture(preset,trace){
 const d=JSON.parse(fs.readFileSync(path.join(draft,'final092-rosters.json'),'utf8')).decks.find(d=>d.presetId===preset);
 const config={mode:'external',preset,deck:{faction:d.faction,leader:d.leader,cards:d.templateIds}};
 const client=new OriginalBetaClient();let s,beforePlay,sourceId,failure,after;const states=[];
 try{
  s=await client.request('init',{seed:923058101,first:1,diagnosticReplayContinuation:true,traceOriginalActions:trace,players:[config,config]});
  for(let i=0;i<100;i++){
   states.push(sha(canonical(s)));
   const second=await client.request('snapshot');assert.equal(JSON.stringify(second),JSON.stringify(s),'Snapshot read changed source');
   const r=s.requests[0],a=technicalAction(s),c=s.cards.find(c=>c.id===a.card);
   if(a.kind==='play'&&c?.template===200502&&r.details.forcedCard===0){beforePlay=s;sourceId=c.id;}
   try{s=await client.request('action',{sequence:s.sequence,request:r.id,...a});}
   catch(e){failure=e.message;after=await client.request('snapshot');break;}
  }
  assert.equal(failure,'Original runtime logged an unhandled error; no rating permitted');
  assert(beforePlay&&after);assert.equal(after.loggerFatalErrors,1);assert.equal(after.loggerDiagnosticReplayErrors,0);
  assert.equal(after.ratingPermitted,false);
  if(trace){
   const context=after.loggerNoRequestContexts[0];assert.equal(after.loggerNoRequestContexts.length,1);
   assert.equal(context.card,sourceId);assert.equal(context.template,200502);assert.equal(context.playedBy,2);
   assert.equal(context.beingPlayed,true);assert.equal(context.inExecutionStack,true);
   assert.equal(context.context.instance,null);assert.equal(context.context.requests.length,0);
   const entries=after.originalActionTrace;
   const plays=entries.map((e,i)=>({e,i})).filter(({e})=>e.action==='PlayCardAction'&&e.text===`[PlayCardAction ${sourceId}]`);
   assert.equal(plays.length,2);
   const [first,duplicate]=plays;
   assert.equal(first.e.fireTriggers,true);assert.equal(first.e.instance.sent,true);assert.equal(first.e.instance.forced,false);
   assert(first.e.requests.some(r=>r.type==='RequestPlayCardAction'&&r.forcedCard===sourceId&&!r.fulfilled));
   assert.equal(duplicate.e.fireTriggers,false);assert.equal(duplicate.e.instance,null);assert.equal(duplicate.e.requests.length,0);
   const removal=entries.slice(first.i+1,duplicate.i).find(e=>e.action==='RemoveAbility'&&e.owner===sourceId);
   assert(removal);assert.equal(removal.type,'PlayedAbilityInstance');assert.equal(removal.state,'Aborted');
   assert.equal(removal.power,0);assert.equal(removal.playedBy,2);assert.equal(removal.sent,true);
   assert.equal(removal.hasAddedActions,true);assert.equal(removal.forced,false);
  }else {assert.equal(after.originalActionTrace.length,0);assert.equal(after.loggerNoRequestContexts.length,0);}
  let afterDrain;
  if(trace){
   afterDrain=await client.request('diagnostic-drain-failed');
   assert.equal(afterDrain.loggerFatalErrors,1);assert.equal(afterDrain.ratingPermitted,false);
   assert.equal(afterDrain.diagnosticDrainPerformed,true);
   await assert.rejects(client.request('advance'),/Game failed/);
   await assert.rejects(client.request('diagnostic-drain-failed'),/not permitted/);
  }else await assert.rejects(client.request('diagnostic-drain-failed'),/not permitted/);
  return {preset,trace,states,finalStateSha256:sha(canonical(after)),config,beforePlay,after,afterDrain,sourceId,failure};
 }finally{await client.close();}
}
(async()=>{
 const cases=[],fixtures=[];
 for(const preset of [78,85]){
  const off=await capture(preset,false),on=await capture(preset,true);
  assert.deepEqual(on.states,off.states,'Tracing changed original boundary state/RNG');
  assert.equal(on.finalStateSha256,off.finalStateSha256,'Tracing changed fatal boundary/RNG');
  fixtures.push(on);
  cases.push({preset,boundaries:on.states.length,sourceId:on.sourceId,traceStateParity:true,
   snapshotReadOnly:true,unhandledErrors:on.after.loggerFatalErrors,diagnosticReplayErrors:0,
   firstPlayConsumedRequest:true,duelKillsSource:true,abortedInstanceAlreadySentPlay:true,
   originalDestroyQueuesSecondPlayWithoutTriggers:true,secondPlayHasNoRootRequest:true,
   strictFatalPreserved:true,diagnosticCleanupSettled:on.afterDrain.diagnosticDrainPerformed,
   poisonedAndFatalPreservedAfterDrain:true,ratingPermitted:false});
 }
 const sourceFiles=['native-host/Program.cs','native-host/BridgeProtocol.cs','native-host/bin/Release/net6.0/OriginalBetaHost.dll',
  'original-csharp/GwentGameplay/AbilityInstance.cs','original-csharp/GwentGameplay/PlayedAbilityInstance.cs'];
 const hashes=Object.fromEntries(sourceFiles.map(f=>[f,sha(fs.readFileSync(path.join(draft,f)))]));
 const assembly=sha(fs.readFileSync(path.join(root,'Gwent 0.9.24.3.432/Gwent_Data/Managed/Assembly-CSharp.dll')));
 assert.equal(assembly,'0f77d0b7ac9d00445a47c2921f6e003f7f0aaab081a47d2f2706a21c10d5b42f');
 fs.writeFileSync(path.join(draft,'native-ice-troll-abort-fixtures.json'),JSON.stringify({schema:1,fixtures,notStrengthResult:true},null,2)+'\n');
 const report={schema:1,complete:true,cases,hashes,assembly,notStrengthResult:true,fullMatchReady:false,
  diagnosis:'Original AbilityInstance.Destroy queues another PlayCardAction when a PlayedTrigger aborts after adding actions, even if the subclass already sent its initial play. In both Ice Troll duels the first play consumed the root request before Troll died; the second has FireTriggers=false and no request. No classification exception added.',
  unresolved:'Fatal remains and normal advance stays refused. An explicitly diagnostic one-shot cleanup audit settles only this known dead-Ice-Troll failure without reclassification. See separate native-ice-troll-projection-proof.json for two verified human-choice rule cases; no general continuation or full match equivalence. Forced-replay classifier remains unchanged.'};
 fs.writeFileSync(path.join(draft,'native-ice-troll-abort-proof.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
