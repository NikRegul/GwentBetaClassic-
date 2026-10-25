'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const root=path.resolve(__dirname,'../..');
const draft=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const original=JSON.parse(fs.readFileSync(path.join(draft,'original-rosters.json'),'utf8'));
(async()=>{
  const deck=original.decks.find(d=>d.asset==='d_Nilfgaard_Practice');
  const side={mode:'external',deck:{faction:deck.faction,leader:deck.leader.templateId,cards:deck.cards}};
  const client=new OriginalBetaClient();
  try {
    let state=await client.request('init',{seed:923058201,first:1,players:[side,side]});
    while(state.requests[0]?.kind==='RequestMulliganAction')
      state=await client.request('action',{sequence:state.sequence,request:state.requests[0].id,kind:'mulligan-finish'});
    assert.equal(state.state,32);
    const before=await client.request('snapshot');
    const audit=await client.request('visibility-audit');
    assert.equal(audit.publicObservationUnchanged,true);
    assert.equal(audit.originalGameUnmodified,true);
    assert.equal(audit.loggerErrors,0);
    assert.deepEqual(await client.request('snapshot'),before,'Audit altered authoritative game');
    fs.writeFileSync(path.join(draft,'original-visibility-audit.json'),JSON.stringify(audit,null,2)+'\n');
    console.log(JSON.stringify(audit));
  } finally {await client.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
