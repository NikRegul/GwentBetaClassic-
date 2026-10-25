// Development-only historical Hard-vs-Hard replay; never mutates tournament files.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto');
const {createRuntime}=require('./beta_js092/session.cjs');
const [analysisFolder,snapshot,output]=process.argv.slice(2),analysis=JSON.parse(fs.readFileSync(path.join(analysisFolder,'sessions-analysis.json'),'utf8'));
const root=analysis.source,out=path.resolve(output);if(fs.existsSync(out))throw Error('Use a fresh replay folder');fs.mkdirSync(out,{recursive:true});
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),byKey=new Map(read(path.join(root,'entrants.json')).map(e=>[e.key,e]));
const report={schema:1,kind:'development-evidence',snapshot:path.resolve(snapshot),records:[]};
for(const selected of analysis.selected.slice(0,Number(process.argv[5]||analysis.selected.length))){
 const historical=read(path.join(root,'games',selected.game+'.json')),left=byKey.get(historical.left),right=byKey.get(historical.right),runtime=createRuntime(snapshot,historical.seed);
 const g=runtime.newSession();g.externalPolicyMask=3;let logs=[];runtime.host.log=s=>{if(/AI_REASON |DUEL_AI_/.test(s))logs.push(s);};
 if(process.argv.includes('--all-short-sequences')){
  // Research-only upper-budget control; never mistaken for a shipped WS port.
  const proto=g.constructor.prototype,cap=proto.AiSimCap;
  proto.AiSimCap=function(tune){const n=cap.call(this,tune),hand=this.CountLocation(2,8);return tune===9&&hand<=4&&this.aiSimDamp<50?Math.max(n,hand):n;};
 }
 if(!g.InitializeWithDecks(left.templateIds,right.templateIds,left.leader,right.leader,left.basePreset??left.presetId,right.basePreset??right.presetId))throw Error('Initialization rejected');
 g.recordVisuals=false;g.aiSimDamp=40;const row={game:selected.game,selected,trace:[],decisions:[]};
 for(let turn=0;!g.Snapshot().matchWinnerMask;turn++){
  if(turn>=500||g.IsFatal())throw Error('Replay failed '+g.GetMessage());
  if(g.mulligan){g.externalPolicyMask=3;const side=g.RequestDecisionSide();if(side===1)runtime.swap(g);g.AiMulligan(g.mulliganBudget);if(side===1)runtime.swap(g);g.RefreshMulligan();if(!g.FinishMulligan(g.requestId))throw Error('Mulligan failed');continue;}
  if(g.waiting){g.externalPolicyMask=3;if(!g.BeginNextRound())throw Error('Round transition failed');continue;}
  if(g.IsPending())throw Error('Unowned pending');
  g.externalPolicyMask=0;const side=g.Snapshot().currentPlayerId,round=g.Snapshot().roundNumber;
  if(side===1)runtime.swap(g);
  const before=side===selected.side?runtime.serialize(g):null,m=g.Snapshot();
  const view={round,side,score:[g.Score(1),g.Score(2)],hand:[g.CountLocation(1,8),g.CountLocation(2,8)],crowns:[m.playerOne.crowns,m.playerTwo.crowns],enemyPassed:m.playerOne.hasPassed,leader:Boolean(g.LeaderAvailable(2))};
  logs=[];if(!g.OpponentStep())throw Error('Policy turn failed '+g.GetMessage());
  if(before){const file=selected.game+'-t'+row.trace.length+'.json.gz';
   fs.writeFileSync(path.join(out,file),zlib.gzipSync(JSON.stringify({sourceGame:selected.game,sourceSnapshot:path.resolve(snapshot),view,state:before})));
   row.decisions.push({...view,file,afterScore:[g.Score(1),g.Score(2)],afterHand:g.CountLocation(2,8),passed:g.Snapshot().playerTwo.hasPassed,logs:logs.slice()});}
  if(side===1)runtime.swap(g);
  row.trace.push({side,round,policy:'092',score:[g.Score(1),g.Score(2)]});
 }
 row.winner=g.Snapshot().matchWinnerMask;row.crowns=[g.Snapshot().playerOne.crowns,g.Snapshot().playerTwo.crowns];
 row.finalStateSha256=crypto.createHash('sha256').update(JSON.stringify(runtime.serialize(g))).digest('hex');
 fs.writeFileSync(path.join(out,selected.game+'-final.json.gz'),zlib.gzipSync(JSON.stringify(runtime.serialize(g))));
 row.traceMatchesHistorical=JSON.stringify(row.trace)===JSON.stringify(historical.trace);row.finalStateMatchesHistorical=row.finalStateSha256===historical.finalStateSha256;
 row.winnerMatchesHistorical=row.winner===historical.winner;
 report.records.push(row);fs.writeFileSync(path.join(out,'replays.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({game:row.game,turns:row.trace.length,decisions:row.decisions.length,winner:row.winner,traceMatches:row.traceMatchesHistorical,stateMatches:row.finalStateMatchesHistorical}));
}
report.complete=true;fs.writeFileSync(path.join(out,'replays.json'),JSON.stringify(report,null,2)+'\n');
