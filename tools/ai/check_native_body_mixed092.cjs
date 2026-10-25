/* Deliberately synthetic transport fixture with duplicate vanilla units and no
 * leaders. It cannot rate decks or establish an AI strength improvement. */
'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {chooseBody,fingerprint}=require('./native_body_adapter092.cjs');
const root=path.resolve(__dirname,'../..'),draft=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
(async()=>{
 const results=[];
 for(const first of [1,2]){
  const side={mode:'external',leaderEnabled:false,deck:{faction:32,leader:200161,cards:Array(25).fill(112103)}};
  const client=new OriginalBetaClient();const started=performance.now();const decisions=[];let memory={},s;
  try{
   s=await client.request('init',{seed:923058401,first,players:[side,{...side,mode:'beta',profile:'Base'}]});
   for(let step=0;s.winner===0&&step<100;step++){
    const r=s.requests[0];assert(r);
    let action;
    if(r.kind==='RequestMulliganAction')action={kind:'mulligan-finish'}; // All copies identical; identity exchange is neutral.
    else{
     const proposal=chooseBody(s,memory,923058401+step);memory=proposal.memory;action=proposal.action;
     decisions.push({round:s.round,turn:s.turn,action,reason:proposal.logs.filter(x=>x.includes('AI_REASON '))});
    }
    s=await client.request('action',{sequence:s.sequence,request:r.id,...action});assert.equal(s.loggerErrors,0);
   }
   assert.notEqual(s.winner,0,'Body mixed fixture did not finish');assert.equal(s.state,512);
   const result={first,complete:true,seconds:(performance.now()-started)/1000,winner:s.winner,rounds:s.round,
     errors:s.loggerErrors,policyDecisions:decisions.length,decisions};results.push(result);console.log(JSON.stringify(result));
  }catch(e){fs.writeFileSync(path.join(draft,'native-body-mixed-failure.json'),JSON.stringify({first,error:String(e),state:s,decisions},null,2));throw e;}
  finally{await client.close();}
 }
 fs.writeFileSync(path.join(draft,'native-body-mixed-smoke.json'),JSON.stringify({schema:1,fingerprint,
  scope:'Synthetic duplicate-vanilla-unit transport fixture: original Beta AI versus unchanged P16 decisions across rounds, disabled leaders. NOT real-roster match, NOT fair-strength evaluation.',
  complete:true,results},null,2)+'\n');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
