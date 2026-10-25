/* One normal policy proposal after a public technical-driver prefix.
 * Supplied memory is a synthetic checkpoint, not a reconstructed policy history.
 * Native legality/unchanged input only; this is NOT a mixed-policy strength test. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {technicalAction}=require('./check_native_choice_adapter092.cjs');
const {chooseNativeNormal,fingerprint}=require('./native_normal_adapter092.cjs');
const draft=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const {reports}=require('./native_bridge_paths092.cjs');
const decks=JSON.parse(fs.readFileSync(path.join(draft,'original-rosters.json'),'utf8')).decks;
async function run(name,first){
 const deck=decks.find(d=>d.asset===name);assert(deck);
 const config={mode:'external',deck:{faction:deck.faction,leader:deck.leader.templateId,cards:deck.cards}};
 const client=new OriginalBetaClient();let s;const rejected={};let turns=0;
 try{
  s=await client.request('init',{seed:923064101,first,players:[config,config]});
  for(let n=0;n<180&&s.winner===0;n++){
   const req=s.requests[0];assert(req);
   if(req.kind==='RequestPlayCardAction'&&req.details.forcedCard===0){
    if(turns++>=2){
     const before=JSON.stringify(s),memory={aiPublicTempo:14,aiEnemyRowPlays:[0,0,0]},start=performance.now();let p;
     try{p=chooseNativeNormal(s,[config,config],memory,s.sequence);}
     catch(e){
      if(!/Unmapped persistent ability state|Unmapped location token|history not mapped|placement/.test(e.message))throw e;
      rejected[e.message]=(rejected[e.message]||0)+1;
     }
     if(p){
      assert.equal(JSON.stringify(s),before);assert.equal(p.fullMatchReady,false);
      const again=chooseNativeNormal(s,[config,config],memory,s.sequence);assert.deepEqual(again.action,p.action);
      assert.throws(()=>chooseNativeNormal(s,[config,config],null,s.sequence),/memory/);
      assert.throws(()=>chooseNativeNormal(s,[config,config],memory,s.sequence-1),/checkpoint/);
      const after=await client.request('action',{sequence:s.sequence,request:req.id,...p.action});
      assert.equal(after.loggerErrors,0);assert.equal(after.sequence,s.sequence+1);
      assert.deepEqual(await client.request('snapshot'),after);
      return {deck:name,first,round:s.round,actor:req.player,prefixTurns:turns-1,cards:s.cards.length,
       action:p.action,guards:2,fullMatchReady:false,errors:0,rejected,milliseconds:performance.now()-start};
     }
    }
   }
   s=await client.request('action',{sequence:s.sequence,request:req.id,...technicalAction(s)});
   assert.equal(s.loggerErrors,0);
  }
  return {deck:name,first,blocked:true,rejected,fullMatchReady:false,errors:0};
 }catch(e){
  fs.writeFileSync(path.join(reports,'native-normal-adapter-failure.json'),JSON.stringify({deck:name,first,error:e.stack,state:s},null,2)+'\n');throw e;
 }finally{await client.close();}
}
if(require.main===module)(async()=>{
 const results=[];
 for(const name of ['d_Skellige_Practice_Easy','d_Nilfgaard_Practice','d_NorthernRealms_Practice',"d_Scoia'tael_Practice_Easy"])
  for(const first of [1,2]){const r=await run(name,first);results.push(r);console.log(JSON.stringify(r));}
 assert(results.some(r=>!r.blocked),'No normal policy seam exercised');
 const report={schema:1,complete:true,fingerprint,fullMatchReady:false,
  scope:'Ordinary-turn proposal legality on actual native states after technical prefixes, both orientations. Synthetic memory checkpoints; not reconstructed intent/ability parity and not a mixed-policy strength comparison.',results};
 fs.writeFileSync(path.join(reports,'native-normal-adapter-smoke.json'),JSON.stringify(report,null,2)+'\n');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
