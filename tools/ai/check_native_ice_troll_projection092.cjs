/* Independent production WS effect projection for the two captured original
 * Ice Troll failures. Native cleanup is explicitly diagnostic, fatal remains;
 * these are human-choice rule cases, not mixed-policy games or ratings. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {compile,fingerprint,inspectNativeModel}=require('./native_session_import092.cjs');
const {draft,reports}=require('./native_bridge_paths092.cjs');
const projection=compile(String.raw`
const {g,flip}=importOriginalSession(native,configs,3-native.current,{memory:{},diagnosticAnalysis:true});
const source=g.FindCard(options.source),p=source.Snapshot();
if(source.TemplateId()!==200502||p.locationMask!==8)throw Error('Expected captured Ice Troll in hand');
const row=g.live.filter(c=>c.cardState.positionPlayerId===1&&c.cardState.locationMask===1)
 .sort((a,b)=>a.cardState.locationIndex-b.cardState.locationIndex);
const played=row.length?g.PlayBefore(1,options.source,row[0].Snapshot().instanceId):g.Play(1,options.source,1);
if(!played)throw Error('WS Ice Troll placement failed');
if(!g.IsPending()||g.pendingCard?.Snapshot().instanceId!==options.source||!g.pendingIds.includes(options.target))
 throw Error('WS Ice Troll target request mismatch');
if(!g.SelectTarget(g.requestId,options.target)||g.IsPending()||g.IsFatal())throw Error('WS Ice Troll duel failed');
return {cards:g.live.map(c=>{const s=c.Snapshot();return {id:s.instanceId,template:c.TemplateId(),side:flip(s.positionPlayerId),
 zone:s.locationMask,index:s.locationIndex,power:s.power.currentPower,basePower:s.power.basePower,permanentPower:s.power.permanentPower,
 armor:s.power.armor,tokens:s.tokenMask,timer:s.timerValue,inExecutionStack:s.isInExecutionStack,waitingToDie:s.isWaitingToDie};}),
 current:flip(g.match.currentPlayerId),scores:[g.Score(flip(1)),g.Score(flip(2))],
 random:{words:g.random.words.map(x=>x>>>0),cursor:g.random.cursor>>>0,remaining:g.random.remaining,
 reseedValue:g.random.reseedValue>>>0,initialSeed:g.random.initialSeed,draws:g.random.draws>>>0}};
`);
const cases=[];
for(const f of JSON.parse(fs.readFileSync(path.join(draft,'native-ice-troll-abort-fixtures.json'),'utf8')).fixtures){
 const target=f.preset===78?18:4;
 assert(f.after.originalActionTrace.some(a=>a.action==='AskSelectTargetCardAction'&&a.text.includes(`Id: ${target}], Select: True`)));
 assert.equal(f.afterDrain.loggerFatalErrors,1);assert.equal(f.afterDrain.ratingPermitted,false);
 assert.throws(()=>inspectNativeModel(f.afterDrain,[f.config,f.config],{actor:1,memory:{},diagnosticAnalysis:true}),/Invalid original authoritative model/);
 const ws=projection(f.beforePlay,[f.config,f.config],{source:f.sourceId,target}),native=f.afterDrain,differences=[];
 for(const c of native.cards){
  const actual=ws.cards.find(x=>x.id===c.id),expected={id:c.id,template:c.template,side:c.position.side,zone:c.position.zone,index:c.position.index,
   power:c.power,basePower:c.basePower,permanentPower:c.permanentPower,armor:c.armor,tokens:c.tokens,timer:c.timer,
   inExecutionStack:c.inExecutionStack,waitingToDie:c.waitingToDie};
  if(JSON.stringify(actual)!==JSON.stringify(expected))differences.push({id:c.id,expected,actual});
 }
 const {encoding,...nativeRandom}=native.random;
 cases.push({preset:f.preset,source:f.sourceId,target,cards:native.cards.length,differences,
  randomEqual:JSON.stringify(ws.random)===JSON.stringify(nativeRandom),scoresEqual:JSON.stringify(ws.scores)===JSON.stringify(native.players.map(p=>p.score)),
  currentEqual:ws.current===native.current,nativeFatalPreserved:1,ratingPermitted:false});
}
const report={schema:1,complete:true,fingerprint,cases,fullMatchReady:false,notStrengthResult:true,
 scope:'Two fixed original Ice Troll human choices through production WS Play/SelectTarget versus separate native failed-game cleanup audit. Native fatal/poisoned state is retained and rejected by policy importer.'};
fs.writeFileSync(path.join(reports,'native-ice-troll-projection-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
for(const c of cases){assert.equal(c.differences.length,0);assert(c.randomEqual&&c.scoresEqual&&c.currentEqual);}
