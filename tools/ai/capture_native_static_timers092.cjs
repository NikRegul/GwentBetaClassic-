'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {technicalAction}=require('./check_native_choice_adapter092.cjs');
const {draft}=require('./native_bridge_paths092.cjs');
(async()=>{
 const decks=JSON.parse(fs.readFileSync(path.join(draft,'final092-rosters.json'),'utf8')).decks;
 const cases=[],results=[];
 for(const [preset,template,initial]of [[56,132201,4],[68,200040,2],[70,200177,4]]){
  const d=decks.find(d=>d.presetId===preset),config={mode:'external',preset,deck:{faction:d.faction,leader:d.leader,cards:d.templateIds}};
  const client=new OriginalBetaClient();let s;const seen=new Set();
  try{
   s=await client.request('init',{seed:923058101,first:1,players:[config,config]});
   for(let i=0;i<350&&!s.winner;i++){
    const r=s.requests[0];
    if(r.kind==='RequestPlayCardAction'&&!r.details.forcedCard&&!s.cards.some(c=>c.inExecutionStack||c.beingPlayed||c.waitingToDie))
     for(const card of s.cards.filter(c=>c.template===template&&c.persistent?.length&&c.timer!==initial)){
      const key=JSON.stringify([card.position.zone,card.timer]);if(seen.has(key))continue;seen.add(key);
      cases.push({deck:'final092-'+preset,sequence:s.sequence,card,config,state:s});
     }
    s=await client.request('action',{sequence:s.sequence,request:r.id,...technicalAction(s)});
   }
   assert(s.winner);assert.equal(s.loggerFatalErrors,0);results.push({preset,template,finished:true,variants:seen.size});
  }finally{await client.close();}
 }
 const report={schema:1,complete:true,cases,results,notStrengthResult:true};
 fs.writeFileSync(path.join(draft,'native-static-timer-fixtures.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({results,cases:cases.length}));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
