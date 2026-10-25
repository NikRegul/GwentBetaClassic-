/* Compare one forced replay with the production WS battle rules using the SAME
 * explicit human target choices. Original native continuation is diagnostic only
 * and remains prohibited for ratings. No AI decision/strength result. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {technicalAction}=require('./check_native_choice_adapter092.cjs');
const {compile,fingerprint}=require('./native_session_import092.cjs');
const {draft,reports}=require('./native_bridge_paths092.cjs');
const projection=compile(String.raw`
if(options.action.kind!=='play'||native.cards.find(c=>c.id===options.action.card)?.template!==122318)
 throw Error('Forced replay oracle requires the captured human-side122318 play');
const {g,flip}=importOriginalSession(native,configs,3-native.current,{memory:{},diagnosticAnalysis:true});
const a=options.action,p=a.position;
const row=g.live.filter(c=>c.cardState.positionPlayerId===flip(p.side)&&c.cardState.locationMask===p.zone)
 .sort((x,y)=>x.cardState.locationIndex-y.cardState.locationIndex);
const ok=p.index<0||p.index>=row.length?g.Play(1,a.card,p.zone):g.PlayBefore(1,a.card,row[p.index].Snapshot().instanceId);
if(!ok||g.IsFatal())throw Error('Production WS replay parent failed');
for(const c of options.choices){
 if(c.kind!=='targets'||c.cards.length!==1||!g.IsPending()||g.pendingCard?.Snapshot().instanceId!==c.requester)
  throw Error('Native/WS replay request order differs');
 if(!g.pendingIds.includes(c.cards[0])||!g.SelectTarget(g.requestId,c.cards[0])||g.IsFatal())
  throw Error('Production WS rejects native replay target');
}
if(g.IsPending())throw Error('WS has additional replay choices');
return {cards:g.live.map(c=>{const s=c.Snapshot();return {id:s.instanceId,template:c.TemplateId(),side:flip(s.positionPlayerId),
 zone:s.locationMask,index:s.locationIndex,power:s.power.currentPower,armor:s.power.armor,tokens:s.tokenMask,timer:s.timerValue,
 inExecutionStack:s.isInExecutionStack,waitingToDie:s.isWaitingToDie};}),
 current:flip(g.match.currentPlayerId),scores:[g.Score(flip(1)),g.Score(flip(2))],
 random:{words:g.random.words.map(x=>x>>>0),cursor:g.random.cursor>>>0,remaining:g.random.remaining,
 reseedValue:g.random.reseedValue>>>0,initialSeed:g.random.initialSeed,draws:g.random.draws>>>0}};
`);
(async()=>{
 const decks=JSON.parse(fs.readFileSync(path.join(draft,'final092-rosters.json'),'utf8')).decks;
 const preset=Number(process.argv[2]||57),d=decks.find(d=>d.presetId===preset),config={mode:'external',preset,deck:{faction:d.faction,leader:d.leader,cards:d.templateIds}};
 let diagnostics='';const client=new OriginalBetaClient({onDiagnostic:s=>{diagnostics+=s}});let s,before,action,after;
 const choices=[],fixtures=[];let skippedForcedParents=0;
 try{
  s=await client.request('init',{seed:923058101,first:1,diagnosticReplayContinuation:true,players:[config,config]});
  for(let step=0;step<160&&s.winner===0;step++){
   const r=s.requests[0],a=technicalAction(s);
   if(before&&r.kind==='RequestPlayCardAction'){
    if(s.loggerDiagnosticReplayErrors>before.loggerDiagnosticReplayErrors&&s.round===before.round){
     after=s;fixtures.push({config,before,action,choices:choices.slice(),after,notStrengthResult:true});
    }
    before=null;action=null;choices.length=0;
   }
   if(before&&s.round!==before.round){before=null;action=null;choices.length=0;}
   const parent=r.kind==='RequestPlayCardAction'&&s.cards.find(c=>c.id===a.card)?.template===122318;
   if(parent&&r.details.forcedCard!==0)skippedForcedParents++;
   if(!before&&parent&&r.details.forcedCard===0){before=s;action=a;}
   else if(before){
    choices.push({...a,requester:r.details.requester,graph:r.ability?.graph,node:r.ability?.currentNode});
   }
   s=await client.request('action',{sequence:s.sequence,request:r.id,...a});assert.equal(s.loggerFatalErrors,0);
  }
  assert(fixtures.length>0);assert.equal(s.ratingPermitted,false);
 }finally{await client.close();}
 fs.writeFileSync(path.join(reports,'native-forced-replay-fixtures-'+preset+'.json'),JSON.stringify({schema:1,fixtures,diagnostics,skippedForcedParents,notStrengthResult:true},null,2)+'\n');
 const cases=[];
 for(const {before,action,choices,after}of fixtures){
 const ws=projection(before,[config,config],{action,choices}),differences=[];
 for(const c of after.cards){
  const actual=ws.cards.find(x=>x.id===c.id),expected={id:c.id,template:c.template,side:c.position.side,zone:c.position.zone,index:c.position.index,
   power:c.power,armor:c.armor,tokens:c.tokens,timer:c.timer,inExecutionStack:c.inExecutionStack,waitingToDie:c.waitingToDie};
  if(JSON.stringify(actual)!==JSON.stringify(expected))differences.push({id:c.id,expected,actual});
 }
 const {encoding,...nativeRandom}=after.random;
 const randomEqual=JSON.stringify(ws.random)===JSON.stringify(nativeRandom),scoresEqual=JSON.stringify(ws.scores)===JSON.stringify(after.players.map(p=>p.score));
 const report={schema:1,complete:true,fingerprint,cards:after.cards.length,choices,diagnosticReplayErrors:after.loggerDiagnosticReplayErrors,
  fullMatchReady:false,notStrengthResult:true,differences,randomEqual,scoresEqual,currentEqual:ws.current===after.current};
 cases.push(report);
 }
 fs.writeFileSync(path.join(reports,'native-forced-replay-projection-'+preset+'.json'),JSON.stringify({schema:1,preset,fingerprint,complete:true,cases,skippedForcedParents,notStrengthResult:true,fullMatchReady:false},null,2)+'\n');
 console.log(JSON.stringify({preset,cases:cases.length,skippedForcedParents,differences:cases.reduce((n,c)=>n+c.differences.length,0),allBoundariesEqual:cases.every(c=>c.randomEqual&&c.scoresEqual&&c.currentEqual),notStrengthResult:true}));
 for(const report of cases){const {differences,randomEqual,scoresEqual}=report;
 assert.equal(differences.length,0,'Native/WS replay card state differs');assert(randomEqual&&scoresEqual&&report.currentEqual,'Native/WS replay boundary differs');
 }
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
