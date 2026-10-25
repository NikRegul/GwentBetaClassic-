/* Executes actual original game rules through JSON transport. No WS-policy
 * comparison or AI-strength verdict is made by this test driver. */
'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const root=path.resolve(__dirname,'../..');
const draft=path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const rosters=JSON.parse(fs.readFileSync(path.join(draft,'original-rosters.json'),'utf8'));
const results=[];
const fixtures={};
async function play(name,{beta=false,checkInvalid=false}={}) {
  const deck=rosters.decks.find(d=>d.asset===name);assert(deck,'Original roster missing');
  const profile=deck.players[0].personality;
  const client=new OriginalBetaClient({onDiagnostic:s=>{throw new Error('Unexpected native diagnostic: '+s);}});
  const config={deck:{faction:deck.faction,leader:deck.leader.templateId,cards:deck.cards},mode:'external'};
  const started=performance.now();let s,decisions=0,invalidRejected=0;
  const trace=[];
  const kinds={};
  try {
    s=await client.request('init',{seed:923058101,first:1,players:[config,beta?{...config,mode:'beta',profile}:config]});
    const storedTest=await client.request('stored-variable-selftest');assert.equal(storedTest.passed,true);assert.equal(storedTest.getterCalls,0);
    assert.equal(s.kind,'original-authoritative-state-not-policy-observation');
    assert.equal(s.cards.filter(c=>c.position.zone===8&&c.position.side===1).length,10);
    if(checkInvalid) {
      const before=await client.request('snapshot');
      await assert.rejects(client.request('action',{sequence:-1,request:s.requests[0].id,kind:'pass'}),/Stale state/);invalidRejected++;
      assert.deepEqual(await client.request('snapshot'),before,'Rejected action mutated original game');
      await assert.rejects(client.request('action',{sequence:s.sequence,request:-999,kind:'pass'}),/Stale or wrong request/);invalidRejected++;
      assert.deepEqual(await client.request('snapshot'),before,'Wrong request mutated original game');
    }
    while(s.winner===0 && decisions<350) {
      const req=s.requests[0];assert(req,'No external request before game end');
      if(!fixtures[req.kind])fixtures[req.kind]={deck:name,config,seed:923058101,state:JSON.parse(JSON.stringify(s))};
      kinds[req.kind]=(kinds[req.kind]||0)+1;
      const d=req.details;let action;
      switch(req.kind) {
        case 'RequestMulliganAction': action={kind:'mulligan-finish'};break;
        case 'RequestPlayCardAction': {
          const cards=new Map(s.cards.map(c=>[c.id,c]));
          const moves=d.moves.slice().sort((a,b)=>(cards.get(b.card)?.power||0)-(cards.get(a.card)?.power||0));
          if(!moves.length) {assert(d.canPass); action={kind:'pass'};}
          else action={kind:'play',...moves[0]};
          break;
        }
        case 'RequestCardTargetsAction': action={kind:'targets',cards:d.valid.slice(0,d.max)};break;
        case 'RequestCardChoicesAction':
          assert(d.originalChoices.length===0||d.originalChoices.length===d.choices.length,'Choice-source mapping size mismatch');
          assert(d.originalChoices.every(id=>s.cards.some(c=>c.id===id)),'Choice refers to missing source instance');
          action={kind:'choices',cards:d.choices.slice(0,d.max).map(c=>c.id)};break;
        case 'RequestLocationTargetsAction': action={kind:'locations',locations:d.valid.slice(0,d.max)};break;
        default:throw new Error('Uncovered original request '+req.kind);
      }
      const before=s.sequence;
      s=await client.request('action',{sequence:before,request:req.id,...action});
      if(!beta)assert.deepEqual(await client.request('snapshot'),s,'Diagnostic snapshot mutated paused native state');
      trace.push({sequence:before,request:req.id,type:req.kind,action,nextRequest:s.requests[0]?.id,nextType:s.requests[0]?.kind,state:s.state,round:s.round});
      assert.equal(s.sequence,before+1);assert.equal(s.loggerErrors,0);decisions++;
      for(const player of s.players) {
        // Original Location.GetScore excludes nonpublic and execution-stack cards.
        const score=s.cards.filter(c=>c.position.side===player.id&&(c.position.zone&7)!==0&&c.visibility===3&&!c.inExecutionStack).reduce((n,c)=>n+c.power,0);
        assert.equal(player.score,score,'Native snapshot board score inconsistent');
      }
    }
    assert.notEqual(s.winner,0,'Game failed to finish');assert.equal(s.state,512);
    const result={deck:name,originalBeta:beta,profile:beta?profile:null,decisions,kinds,invalidRejected,storedGetterTest:storedTest,
      pausedSnapshotEqualityChecks:beta?0:decisions,
      seconds:(performance.now()-started)/1000,winner:s.winner,errors:s.loggerErrors,round:s.round};
    results.push(result);console.log(JSON.stringify(result));
  } catch(error) {
    fs.writeFileSync(path.join(draft,'native-protocol-failure-state.json'),JSON.stringify({deck:name,error:String(error),kinds,state:s,trace},null,2)+'\n');
    throw error;
  } finally { await client.close(); }
}
(async()=>{
  const mixed=process.argv.includes('--with-beta');
  await play('d_Skellige_Practice_Easy',{checkInvalid:true,beta:mixed});
  if(!mixed) {
    await play('d_Nilfgaard_Practice');
    await play('d_NorthernRealms_Practice');
    await play('d_Scoia\'tael_Practice_Easy');
  }
  const report={schema:1,scope:'Original engine protocol integration, external legal-action driver; not our WS AI and not strength comparison',
    complete:true,results};
  fs.writeFileSync(path.join(draft,mixed?'native-protocol-beta-smoke.json':'native-protocol-external-smoke.json'),JSON.stringify(report,null,2)+'\n');
  if(!mixed)fs.writeFileSync(path.join(draft,'native-protocol-fixtures.json.gz'),require('zlib').gzipSync(JSON.stringify({schema:1,
    scope:'Original native authoritative paused states, all five request kinds; internal fixtures contain hidden cards and are NOT policy observations.',fixtures})));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
