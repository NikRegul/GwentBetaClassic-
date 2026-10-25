'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {chooseOpening,fingerprint}=require('./native_opening_adapter092.cjs');
const root=path.resolve(__dirname,'../..');const draft=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const {reports}=require('./native_bridge_paths092.cjs');
const presets=JSON.parse(fs.readFileSync(path.join(draft,'final092-rosters.json'),'utf8')).decks;
(async()=>{
  const results=[];
  for(const preset of [54,58,73,96]) {
    const d=presets.find(d=>d.presetId===preset);assert(d);
    const side={mode:'external',preset,deck:{faction:d.faction,leader:d.leader,cards:d.templateIds}};
    for(const first of [1,2]) {
      const client=new OriginalBetaClient();
      try {
        let s=await client.request('init',{seed:923058301,first,players:[side,side]});
        while(s.requests[0]?.kind==='RequestMulliganAction')
          s=await client.request('action',{sequence:s.sequence,request:s.requests[0].id,kind:'mulligan-finish'});
        const before=JSON.stringify(s),started=performance.now();
        const proposed=chooseOpening(s,[side,side]);
        assert.equal(JSON.stringify(s),before,'WS modified source native observation');
        const req=s.requests[0];
        const after=await client.request('action',{sequence:s.sequence,request:req.id,...proposed.action});
        assert.equal(after.sequence,s.sequence+1);assert.equal(after.loggerErrors,0);
        results.push({preset,first,cardsImported:proposed.cardsImported,action:proposed.action,
          milliseconds:performance.now()-started,nextRequest:after.requests[0]?.kind,errors:0});
      } finally {await client.close();}
    }
  }
  const report={schema:1,scope:'Frozen WS first action from exact original empty-board opening state, validated and applied by native engine. NOT full mixed match or general adapter.',fingerprint,complete:true,results};
  fs.writeFileSync(path.join(reports,'native-opening-adapter-smoke.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
