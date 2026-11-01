'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const snapshot=path.resolve(process.argv[2]),out=process.argv[3],ctx=vm.createContext({console});
ctx.observe=process.argv.includes('--observe');
ctx.fixtures=[7,8,10].map(d=>JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,`fixtures/weather-pass096/decision-${d}.json.gz`)))));
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
vm.runInContext(String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;
let checks=0,peakActions=0,calls=0,maxTicks=0;const failures=[],records=[];
function check(v,n){checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}}
const play=CBetaGwentDuelSession.prototype.AiSimPlay;
CBetaGwentDuelSession.prototype.AiSimPlay=function(id){calls++;return play.call(this,id);};
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,pending:g.IsPending()});}
function add(g,id,side,zone,power){const ref={v:0};check(g.registry.Allocate(ref),'allocate');const c=new CBetaGwentDuelCard();c.Setup(g,ref.v,id,side,zone,g.CountLocation(side,zone));
 if(power!==undefined)c.power.ResetTemplatePower(power,0);g.registry.Put(ref.v,c);g.live.push(c);return c;}
function blank(round=1){Host.random=()=>0.7;const g=new CBetaGwentDuelSession();check(g.InitializeWithPresets(98,81),'initialize');
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.recordVisuals=false;g.externalPolicyMask=0;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.turnActive=g.match.roundActive=true;g.match.roundNumber=round;
 g.match.playerOne.hasPassed=g.match.playerTwo.hasPassed=false;g.match.playerOne.crowns=g.match.playerTwo.crowns=round===3?1:0;
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.aiSimDamp=0;g.leaderTemplateTwo=200165;g.presetTwo=81;
 g.archetypeAI.Initialize(g,[],81,200165);return g;}
function prepare(g){const before=state(g);let ticks=0;while(true){calls=0;const done=g.AiPreparationStep();peakActions=Max(peakActions,calls);
 check(calls<=1,'at most one simulated play per preparation callback');check(state(g)===before,'preparation preserves match, requests and RNG');
 if(done)break;if(++ticks>4000)throw Error('preparation stalled');}maxTicks=Max(maxTicks,ticks);}
function act(g,staged){if(staged)prepare(g);const logs=[];Host.log=s=>logs.push(s);let ok;
 try{for(let i=0;i<4;i++){ok=g.OpponentStep();if(ok)break;prepare(g);}}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'decision resolves');return logs;}
function exchange(round=1){const g=blank(round),weak=add(g,112405,2,8,3),strong=add(g,112405,2,8,12),incoming=add(g,112405,2,16,18),leader=add(g,200165,2,64);
 g.archetypeAI.Refresh();return {g,weak,strong,incoming,leader};}
// Independently known ordinary bodies: exchange the three, preserve the twelve,
// receive eighteen plus three. The leader's board tempo remains exactly seven.
for(const damp of [0,40,70]){
 const {g,weak,strong,incoming,leader}=exchange();g.aiSimDamp=damp;const before=state(g),tempo=g.AiExactTempo(leader),future=g.aiLastStrategicValue;
 check(state(g)===before,'exchange evaluation preserves original state');check(tempo===7,'exchange is not immediate card play or catch-up points');
 check(future===18,'banked improvement is 21 minus 3, including boost once');
 check(g.UseLeader(2)&&!g.IsFatal()&&!g.IsPending(),'real exchange resolves');
 check(weak.Snapshot().locationMask===16&&strong.Snapshot().locationMask===8,'return lower-value card and preserve stronger hand card');
 check(incoming.Snapshot().locationMask===8&&incoming.Snapshot().power.currentPower===21,'chosen incoming card receives actual boost');
 check(g.Score(2)===7&&g.CountLocation(2,8)===2,'leader adds only its body and preserves hand size');
}
// A targetless removal is a better exchange than sacrificing a useful body.
{
 const g=blank(),junk=add(g,113301,2,8),keep=add(g,112405,2,8,12),incoming=add(g,112405,2,16,8);add(g,200165,2,64);g.archetypeAI.Refresh();
 check(g.UseLeader(2)&&!g.IsPending(),'reactive exchange resolves');check(junk.Snapshot().locationMask===16&&keep.Snapshot().locationMask===8,'replace currently dead removal');
}
// The supplied deck has two situational answers. Public weather changes which
// one is useful; no special card ID is imposed by the exchange implementation.
for(const weather of [false,true]){
 const g=blank(),junk=add(g,112405,2,8,1),body=add(g,112405,2,16,2),clear=add(g,113401,2,16);add(g,200165,2,64);
 for(const row of [1,2,4]){add(g,112405,2,row,12);if(weather)g.weather.ApplyHazard(2,row,32);}
 g.archetypeAI.Refresh();const choices=[];Host.log=s=>choices.push(s);check(g.UseLeader(2)&&!g.IsPending(),'situational exchange resolves');Host.log=null;records.push({kind:'weather-exchange',weather,choices:choices.filter(s=>/event=TARGET/.test(s))});
 check((weather?clear:body).Snapshot().locationMask===8,'incoming choice follows public weather need');
}
// A useful exchange must be available before playing the last ordinary card.
for(const staged of [false,true]){
 const {g,incoming,leader}=exchange();const logs=act(g,staged);
 check(leader.Snapshot().locationMask!==64&&incoming.Snapshot().locationMask===8,'use valuable leader while the exchange is still possible');records.push({kind:'leader',staged,logs:logs.filter(s=>/event=(LEADER_OPTION|SELECT)/.test(s))});
}
// Opposing hidden hand/deck identities cannot affect our exchange or timing.
{
 const choices=[];
 for(const hidden of [112405,113301]){
  const {g,incoming,leader}=exchange();add(g,hidden,1,8);add(g,hidden,1,16);g.aiStartingDeckOne=[112405];
  const logs=act(g,true);choices.push(logs.filter(s=>/event=(LEADER_OPTION|SELECT)/.test(s)));
  check(leader.Snapshot().locationMask!==64&&incoming.Snapshot().locationMask===8,'closed-data exchange still completes usefully');
 }
 check(JSON.stringify(choices[0])===JSON.stringify(choices[1]),'exchange and timing are independent of real opposing hidden identities');
}
// R3 witness: only the newly received body can win after a leader. The old
// source hand cannot catch 25; a source-ID-only continuation loses this line.
{
 const {g,weak,strong,incoming,leader}=exchange(3);strong.power.ResetTemplatePower(4,0);add(g,112405,1,1,25);g.archetypeAI.Refresh();
 const ids=[weak,strong].map(c=>c.Snapshot().instanceId),values=[weak,strong].map(c=>g.AiExactTempo(c));
 const response=new CBetaGwentPublicResponseAI();response.Initialize(g,1);const tree=new CBetaGwentAIReplyTree097();tree.Initialize(g,leader.Snapshot().instanceId,ids,values,response);
 const before=state(g);let ticks=0;while(true){calls=0;const done=tree.Step();peakActions=Max(peakActions,calls);check(calls<=1,'new continuation obeys callback budget');check(state(g)===before,'new continuation search preserves live state');if(done)break;if(++ticks>1000)throw Error('frontier stalled');}
 check(tree.ids.Contains(incoming.Snapshot().instanceId),'newly acquired instance enters continuation set');
 check(tree.continuationIds.Contains(incoming.Snapshot().instanceId)||tree.branchBestId===incoming.Snapshot().instanceId,'frontier actually resolves winning new card');
 const h=g.AiSimClone();check(h.AiSimPlay(leader.Snapshot().instanceId)===7,'witness leader executes');
 check(h.Pass(1)&&h.AiSimPlay(incoming.Snapshot().instanceId)!==-2147483647&&h.Pass(2),'actual new-card continuation settles');
 check(h.Snapshot().matchWinnerMask===2,'actual resulting match is won');
}
// Retail positions with a balanced hand: mature optional pressure under three
// harmful rows should preserve the hand. Passing is conditional, not a forced win.
for(const capture of fixtures.slice(0,2))for(const damp of [0,40,70])for(const staged of [false,true]){
 const g=unpack(capture.state);g.aiSimDamp=damp;const hand=g.CountLocation(2,8),logs=act(g,staged);
 check(g.Snapshot().playerTwo.hasPassed&&g.CountLocation(2,8)===hand,'weather pressure preserves retail balanced hand '+capture.begin.decision);
 records.push({kind:'retail-pass',decision:capture.begin.decision,damp,staged,logs:logs.filter(s=>/event=(ROUND_TRANSITION|PASS|SELECT)/.test(s))});
}
// Closed enemy identities/order must not change that decision. No added crown,
// useful spy, safe armour or early setup may become an automatic weather pass.
const retail=fixtures[0];
for(const kind of ['hidden','mandatory','no-weather','armour','opening','advantage']){
 const g=unpack(retail.state);g.aiSimDamp=40;
 if(kind==='hidden')for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&[8,16].includes(s.locationMask)&&(s.tokenMask&64)===0){c.definition=BetaGwentDuelDefinition(112405);c.cardState.runtimeTemplate=c.definition.header;c.power.ResetTemplatePower(40,9);c.cardState.locationIndex=99-s.locationIndex;}}
 if(kind==='mandatory'){g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;}
 if(kind==='no-weather')for(const row of [1,2,4])g.weather.ClearRow(2,row);
 if(kind==='armour')for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===2&&(s.locationMask&7)!==0)c.power.SetCurrentPair(s.power.currentPower,99);}
 if(kind==='opening')for(const c of g.live){const s=c.Snapshot();if(s.ownerId===1&&(s.locationMask&39)!==0)c.createdCopy=true;}
 if(kind==='advantage')add(g,112405,2,8,12);
 const logs=act(g,true);check(g.Snapshot().playerTwo.hasPassed===(kind==='hidden'),'weather pass gates '+kind);records.push({kind,logs:logs.filter(s=>/event=(ROUND_TRANSITION|PASS|SELECT)/.test(s))});
}
// Winning first round at the early exit preserves resources on either answer:
// the adversary can spend a card to take it, or concede without our extra play.
for(const reply of ['pass','play']){const g=unpack(retail.state),hand=g.CountLocation(2,8);check(g.Pass(2),'counterfactual optional pass executes');
 if(reply==='play'){const card=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8&&c.TemplateId()===152105);check(Boolean(card)&&g.Play(1,card.Snapshot().instanceId,2),'real opposing response executes');}
 else check(g.Pass(1),'opposing answering pass executes');
 check(g.CountLocation(2,8)===hand,'optional exit preserves hand against both legal responses');}
globalThis.result={checks,failures,records,peakActions,maxTicks,actualWitcherScript:true,nativeGameplayVerified:false,notStrengthResult:true};
`,ctx,{timeout:180000});
const report={fingerprint:JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8')).fingerprint,...ctx.result};
if(out)fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failures:report.failures,peakActions:report.peakActions,maxTicks:report.maxTicks}));if(report.failures.length)process.exitCode=1;
