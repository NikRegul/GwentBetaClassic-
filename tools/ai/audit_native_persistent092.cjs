/* Collect raw original persistent variables at settled turn boundaries.
 * Technical driver only. These authoritative internal fixtures contain hidden
 * cards; they are never passed directly to an ordinary policy observation. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {technicalAction}=require('./check_native_choice_adapter092.cjs');
const draft=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const decks=JSON.parse(fs.readFileSync(path.join(draft,'original-rosters.json'),'utf8')).decks;
const finalMode=process.argv.includes('--final092');
const betaOpponent=process.argv.includes('--beta-opponent');
const diagnosticReplay=process.argv.includes('--diagnostic-replay');
const traceOriginalActions=process.argv.includes('--trace-original-actions');
const presetArg=process.argv.indexOf('--preset'),onlyPreset=presetArg>=0?Number(process.argv[presetArg+1]):null;
const work=(finalMode?JSON.parse(fs.readFileSync(path.join(draft,'final092-rosters.json'),'utf8')).decks.map(d=>({
 asset:'final092-'+d.presetId,preset:d.presetId,faction:d.faction,leader:{templateId:d.leader},cards:d.templateIds
})):decks.filter(d=>['d_Skellige_Practice_Easy','d_Nilfgaard_Practice','d_NorthernRealms_Practice',"d_Scoia'tael_Practice_Easy"].includes(d.asset))).filter(d=>onlyPreset===null||d.preset===onlyPreset);
(async()=>{
 const cases=[],results=[];
 for(const d of work){
  const name=d.asset,config={mode:'external',preset:d.preset,deck:{faction:d.faction,leader:d.leader.templateId,cards:d.cards}};
  let diagnostic='';const client=new OriginalBetaClient({onDiagnostic:t=>{diagnostic=(diagnostic+t).slice(-24000);}});const seen=new Set(),timeline=[];let boundaries=0,s,lastAction;
  try{
   s=await client.request('init',{seed:923058101,first:1,diagnosticReplayContinuation:diagnosticReplay,traceOriginalActions,
     players:[config,betaOpponent?{...config,mode:'beta',profile:'Base'}:config]});
   for(let step=0;step<350&&s.winner===0;step++){
    const r=s.requests[0];assert(r);
    if(r.kind==='RequestPlayCardAction'&&!r.details.forcedCard&&!s.cards.some(c=>c.inExecutionStack||c.beingPlayed||c.waitingToDie)){
     boundaries++;
     for(const c of s.cards.filter(c=>c.persistent?.length)){
      const key=JSON.stringify([c.template,c.position.zone,c.persistent]);if(seen.has(key))continue;seen.add(key);
      cases.push({deck:name,seed:923058101,sequence:s.sequence,round:s.round,card:c,config,state:s});
      console.log(JSON.stringify({deck:name,template:c.template,zone:c.position.zone,persistent:c.persistent}));
     }
    }
    lastAction={sequence:s.sequence,request:r.id,...technicalAction(s)};
    timeline.push({round:s.round,turn:s.turn,current:s.current,request:r,action:lastAction,
      template:lastAction.card?s.cards.find(c=>c.id===lastAction.card)?.template:undefined});
    s=await client.request('action',lastAction);assert.equal(s.loggerFatalErrors??s.loggerErrors,0);
   }
   assert.notEqual(s.winner,0);results.push({deck:name,boundaries,cases:seen.size,errors:0,
    originalLoggerErrors:s.loggerErrors,originalHandledFallbacks:s.loggerHandledFallbacks??0,
    diagnosticReplayErrors:s.loggerDiagnosticReplayErrors??0,diagnosticOnly:s.diagnosticOnly??false,ratingPermitted:s.ratingPermitted??false,
    replayContexts:s.loggerReplayContexts??[]});
   console.log(JSON.stringify({deck:name,complete:true,boundaries,cases:seen.size,
    originalLoggerErrors:s.loggerErrors,originalHandledFallbacks:s.loggerHandledFallbacks??0}));
  }catch(e){
   if(!finalMode)throw e;
   let failedState;try{failedState=await client.request('snapshot');}catch{}
   results.push({deck:name,boundaries,cases:seen.size,error:e.stack,diagnostic,lastAction,timeline,beforeFailure:s,failedState,errors:1});
   console.log(JSON.stringify({deck:name,complete:false,error:e.message}));
  }finally{await client.close();}
 }
 const out=path.join(draft,finalMode?'native-persistent-audit-final092'+(onlyPreset===null?'':'-'+onlyPreset)+(betaOpponent?'-beta':'')+(diagnosticReplay?'-diagnostic-replay':'')+(traceOriginalActions?'-trace':'')+'.json':'native-persistent-audit.json');
 fs.writeFileSync(out,JSON.stringify({schema:1,complete:true,diagnosticReplay,notStrengthResult:true,
  scope:'Raw persistent variable mapping research; technical driver, not strength',results,cases},null,2)+'\n');
 console.log(JSON.stringify({out,cases:cases.length,results:results.map(({deck,boundaries,cases,errors,error})=>({deck,boundaries,cases,errors,error:error?.split('\n')[0]}))}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
