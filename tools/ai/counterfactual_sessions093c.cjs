// Offline diagnosis uses the recorded full state; it is never production AI.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib');
const {createRuntime}=require('./beta_js092/session.cjs');
const [replays,snapshot,output]=process.argv.slice(2),out=path.resolve(output);
if(fs.existsSync(out))throw Error('Use a fresh counterfactual folder');fs.mkdirSync(out,{recursive:true});
const saved=JSON.parse(fs.readFileSync(path.join(replays,'replays.json'),'utf8')),runtime=createRuntime(snapshot),plan=[];
for(const game of saved.records){
 const candidates=game.decisions.filter(d=>!d.passed&&!d.enemyPassed&&d.hand[1]<=4);
 const selected=[candidates[0],candidates[candidates.length-2],candidates[candidates.length-1]].filter(Boolean);
 const seen=new Set();for(const d of selected){if(seen.has(d.file))continue;seen.add(d.file);plan.push({game:game.game,key:game.selected.key,file:d.file,round:d.round,score:d.score,hand:d.hand});}
}
fs.writeFileSync(path.join(out,'plan.json'),JSON.stringify({kind:'postmortem-full-state-development-only',snapshot:path.resolve(snapshot),positions:plan},null,2)+'\n');
const report={records:[],complete:false};
function load(f){return runtime.deserialize(JSON.parse(JSON.stringify(f.state)));}
function view(g){const m=g.Snapshot();return {winner:m.matchWinnerMask,crowns:[m.playerOne.crowns,m.playerTwo.crowns],score:[g.Score(1),g.Score(2)]};}
function finish(g){
 for(let step=0;!g.Snapshot().matchWinnerMask;step++){
  if(step>200||g.IsFatal())throw Error('Rollout failed '+g.GetMessage());
  if(g.mulligan){g.externalPolicyMask=3;const side=g.RequestDecisionSide();if(side===1)runtime.swap(g);g.AiMulligan(g.mulliganBudget);if(side===1)runtime.swap(g);g.RefreshMulligan();if(!g.FinishMulligan(g.requestId))throw Error('Mulligan rejected');continue;}
  if(g.waiting){g.externalPolicyMask=3;if(!g.BeginNextRound())throw Error('Round rejected');continue;}
  if(g.IsPending())throw Error('Pending rollout');g.externalPolicyMask=0;
  const side=g.Snapshot().currentPlayerId;if(side===1)runtime.swap(g);if(!g.OpponentStep())throw Error('Rollout decision rejected');if(side===1)runtime.swap(g);
 }
 return view(g);
}
for(const p of plan){
 const f=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(replays,p.file)))),start=load(f),options=[{kind:'policy'},{kind:'pass'}];
 for(const c of start.live){const s=c.Snapshot();if(s.positionPlayerId===2&&s.canBePlayed&&(s.locationMask===8||s.locationMask===64))options.push({kind:s.locationMask===64?'leader':'card',id:s.instanceId,template:c.TemplateId()});}
 const row={...p,options:[]};
 for(const option of options){const g=load(f);let ok=true;
  if(option.kind==='policy')ok=g.OpponentStep();
  else if(option.kind==='pass')ok=g.Pass(2);
  else if(option.kind==='leader')ok=g.UseLeader(2);
  else{const c=g.FindCard(option.id),d=c.Definition();let row=g.BestCardRow(2,d)||1,anchor=d.effect===23?g.BestVranAnchor(2):0;if(!anchor)anchor=g.AiPlacementAnchor(d);ok=anchor?g.PlayBefore(2,option.id,anchor):g.Play(2,option.id,row);}
  if(!ok||g.IsFatal()||g.IsPending()){row.options.push({...option,legal:false});continue;}
  row.options.push({...option,legal:true,immediate:view(g),result:finish(g)});
 }
 report.records.push(row);fs.writeFileSync(path.join(out,'counterfactuals.json'),JSON.stringify(report,null,2)+'\n');
 const normal=row.options[0],better=row.options.filter(o=>o.legal&&(o.result.winner===2||o.result.winner===3)&&o.result.winner!==normal.result.winner);
 console.log(JSON.stringify({position:p.file,key:p.key,baseline:normal.result.winner,better:better.map(o=>({kind:o.kind,template:o.template,winner:o.result.winner}))}));
}
report.complete=true;fs.writeFileSync(path.join(out,'counterfactuals.json'),JSON.stringify(report,null,2)+'\n');
