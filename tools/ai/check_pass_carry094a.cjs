'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const {createRuntime}=require('./beta_js092/session.cjs');
const snapshot=path.resolve(process.argv[2]),out=process.argv[3];
const runtime=createRuntime(snapshot),records=[],failures=[];let checks=0;
function check(ok,name){checks++;if(!ok)failures.push(name);}
const view=g=>JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId,waiting:g.waiting});
function prepare(g){let ticks=0;while(!g.AiPreparationStep())if(++ticks>10000)throw Error('prepare stalled');return ticks;}
function act(g){const logs=[];runtime.host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{runtime.host.log=null;}return {ok,logs};}
// A permanent fixture is generated only from the completely checked recorded
// action replay. It contains full engine state, not guessed logged card fields.
const base=path.join(__dirname,'fixtures/pass-carry094a');
for(const decision of [9,10,12])for(const damp of [0,40,70])for(const staged of [false,true]){
 const capture=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(base,`decision-${decision}.json.gz`))));
 const g=runtime.deserialize(capture.state);g.aiSimDamp=damp;runtime.host.strength=4;runtime.host.matchStrength=[4,4];
 const hand=g.CountLocation(2,8),leader=Boolean(g.LeaderAvailable(2));if(staged)prepare(g);
 const result=act(g),m=g.Snapshot();
 check(result.ok&&!g.IsFatal()&&!g.IsPending(),'human decision completes '+decision+'/'+damp+'/'+staged);
 check(m.playerTwo.hasPassed,'preserve hand instead of another optional play '+decision+'/'+damp+'/'+staged);
 check(g.CountLocation(2,8)===hand&&Boolean(g.LeaderAvailable(2))===leader,'pass preserves cards and leader '+decision+'/'+damp+'/'+staged);
 records.push({decision,damp,staged,logs:result.logs.filter(s=>/event=(ROUND_TRANSITION|PASS|SELECT)/.test(s))});
}
// Create positions through the real runtime, with explicit base power. Carry
// expectations come from cleanup rules, not the forecast implementation.
function blank(round=1){const g=runtime.newSession();if(!g.InitializeWithPresets(54,54))throw Error('init');
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
 g.match.currentPlayerId=2;g.match.roundNumber=round;g.match.roundActive=true;g.match.turnActive=true;
 g.match.playerOne.crowns=0;g.match.playerTwo.crowns=round===2?1:0;
 g.aiRoundHandTwo=10;g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();return g;}
function add(g,id,side,zone,basePower,tokens=0,current=basePower){const slot={v:0};g.registry.Allocate(slot);const c=runtime.newCard();
 c.Setup(g,slot.v,id,side,zone,g.CountLocation(side,zone));c.power.ResetTemplatePower(basePower,0);c.power.SetCurrentPair(current,0);c.cardState.tokenMask=tokens;g.registry.Put(slot.v,c);g.live.push(c);return c;}
for(const [name,id,basePower,tokens,current,expected]of [
 ['morkvarg',152209,9,0,15,4],['weak-morkvarg',152209,1,0,1,0],['locked-morkvarg',152209,9,4,9,0],
 ['resilient-morkvarg',152209,9,1,15,9],['resilience',112405,8,1,15,8],['damaged-resilience',112405,8,1,4,4],['plain',112405,8,0,15,0]])for(const side of [1,2]){
 const g=blank();add(g,id,side,1,basePower,tokens,current);add(g,112405,3-side,2,20);add(g,112405,1,8,8);add(g,112405,2,8,8);
 const before=view(g),forecast=g.AiNextRound094a();
 check(forecast.valid&&forecast.winner===0,'forecast available '+name+'/'+side);
 check((side===1?forecast.enemyScore:forecast.ownScore)===expected,'independent carry expectation '+name+'/'+side);
 check(view(g)===before,'forecast does not change live state or RNG '+name+'/'+side);
 const actual=runtime.deserialize(runtime.serialize(g));
 check(actual.Pass(2)&&actual.Pass(1)&&actual.BeginNextRound(),'real next round resolves '+name+'/'+side);
 check(actual.Score(1)===forecast.enemyScore&&actual.Score(2)===forecast.ownScore,'forecast matches real cleanup '+name+'/'+side);
 check(actual.Snapshot().startingPlayerId===forecast.starter,'initiative matches actual winner '+name+'/'+side);
}
for(const zone of [8,16]){
 const results=[];
 for(const id of [112405,152209]){const g=blank();add(g,id,1,zone,9);add(g,112405,2,1,20);add(g,112405,2,8,8);results.push(g.AiNextRound094a());}
 check(JSON.stringify(results[0])===JSON.stringify(results[1]),'hidden Morkvarg identity cannot affect carry forecast in zone '+zone);
}
{const g=blank();add(g,142205,1,1,8,8);check(!g.AiNextRound094a().valid,'concealed trap refuses a precise carry forecast');}
{const g=blank();const before=view(g);g.waiting=true;check(!g.BeginNextRound(true),'board-only boundary cannot be called in the live game');g.waiting=false;check(view(g)===before,'rejected live forecast boundary leaves state intact');}
for(const deciding of [false,true]){
 const f=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(base,'decision-9.json.gz')))),g=runtime.deserialize(f.state);
 g.match.roundNumber=deciding?3:2;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=deciding?1:0;
 const lead=g.AiPublicPassLead(true),r=act(g);check(r.ok&&!g.IsFatal(),'mandatory round decision completes');
 check(!r.logs.some(s=>/reason=optional_(short_hand|bleed)_preserve_initiative/.test(s)),'optional initiative gates never run in a mandatory round');
 check(!g.Snapshot().playerTwo.hasPassed||lead>0,'mandatory round never concedes merely to change initiative');
}
// Enough resources to pressure the optional second round: carryover is not
// an unconditional surrender trigger.
{const g=blank(2);add(g,152209,1,1,4);for(let i=0;i<4;i++)add(g,112405,1,8,8);for(let i=0;i<6;i++)add(g,112405,2,8,10);g.aiRoundHandTwo=6;
 const r=act(g);check(r.ok&&!g.IsFatal(),'resource-backed pressure completes');check(!g.Snapshot().playerTwo.hasPassed,'balanced strong hand may push through opposing carry');}
// Independent point/risk contracts: the same lead can be passed or contested
// according to public response risk and resource cost, without a 26-point floor.
const pure=vm.createContext({console});vm.runInContext(['runtime.js','rules.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n'),pure);
for(const [args,expected,label]of [
 [[1,0,0,12,4,4,5,4,false,false,0,5,0],1,'low public reply tempo permits a lead below 26'],
 [[1,0,0,19,2,4,13,19,false,true,1,14,0],0,'same score remains contested without resource opportunity'],
 [[1,0,0,19,2,4,13,19,false,true,1,14,33],1,'card deficit and carry response cost can justify passing'],
 [[2,0,1,19,2,4,13,19,false,true,1,14,33],0,'resource discount cannot concede a mandatory round']]){
 pure.args=args;check(vm.runInContext('BetaGwentAIRoundDecision(...args)',pure)===expected,label);
}
const report={checks,failures,records,fingerprint:runtime.fingerprint,actualWitcherScript:true,nativeGameplayVerified:false,notStrengthResult:true};
if(out)fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks,failures,cases:records.length}));if(failures.length)process.exitCode=1;
