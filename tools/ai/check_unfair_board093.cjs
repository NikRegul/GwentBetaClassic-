'use strict';
// Exercise the actual WS menu coordinator with captured Flash calls. No game
// installation and no approximation of the new policy or request projector.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const rules=path.resolve(process.argv[2]),contract=path.resolve(process.argv[3]);
const manifest=JSON.parse(fs.readFileSync(path.join(contract,'manifest.json'),'utf8'));
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n')+'\n'+fs.readFileSync(path.join(contract,'board.js'),'utf8');
const makeRuntime=new Function('fields',source+String.raw`
 let time=0,difficulty=4,seed=924044001;const calls={},logs=[];
 Host.random=()=>{seed^=seed<<13;seed>>>=0;seed^=seed>>>17;seed>>>=0;seed^=seed<<5;seed>>>=0;return seed/4294967296;};
 Host.strength=4;Host.matchStrength=[4,4];Host.log=s=>logs.push(s);
 const theGame={GetEngineTimeAsSeconds:()=>time};
 function FlashArgInt(x){return x;}function FlashArgUInt(x){return x;}function FlashArgBool(x){return x;}function FlashArgString(x){return x;}
 function BetaGwentDifficultyLevel(){return difficulty;}
 const board=new CR4BetaGwentBoardMenu();board.configured=true;board.selectingDecks=true;board.ownPreset=54;board.enemyPreset=65;
 board.ownLeader=BetaGwentDuelPreset(54).leaderTemplateId;board.enemyLeader=BetaGwentDuelPreset(65).leaderTemplateId;
 board.duel=new CBetaGwentDuelSession();board.session=board.duel;board.requestFlow=new CBetaGwentDevelopmentRequestFlow();
 board.deckLibrary={Resolve:(id,cards,leader)=>{leader.v=BetaGwentDuelPreset(id).leaderTemplateId;return BetaGwentDuelPresetDeck(id,cards);},
 ResolveOpponent:(id,cards,leader)=>{leader.v=BetaGwentDuelPreset(id).leaderTemplateId;return BetaGwentDuelPresetDeck(id,cards);}};
 board.audio={Cancel(){},IsVoiceActive:()=>false,CurrentTime:()=>time};
 for(const field of fields){calls[field]=[];board[field]=new Proxy({},{get:(_,name)=>(...args)=>calls[field].push({name,args})});}
 return {board,calls,logs,clock:dt=>time+=dt,clear:()=>{for(const k in calls)calls[k].length=0;},setDifficulty:d=>difficulty=d,
 setOpponent:preset=>{board.enemyPreset=preset;board.enemyLeader=BetaGwentDuelPreset(preset).leaderTemplateId;}};`);
const runtime=makeRuntime(manifest.flashFields);
let checks=0;const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
const {board,calls}=runtime;
eq(board.StartSelectedDuel(),true,'Actual menu starts Unfair');eq(board.originalOpponent,true,'Fourth difficulty selects original controller');eq(board.duel.externalPolicyMask,2,'External decisions only for opponent');
eq(board.duel.RequestDecisionSide(),2,'Source original owns initial opponent mulligan');
eq(calls.pushRequestCard.length,0,'Opponent hand exchanges never sent to human Flash');
eq(calls.setRequestHeader.at(-1).args.slice(1,4),[0,0,0],'No opponent request exposed');
eq(calls.setRequestSource.at(-1).args.slice(1),[0,0],'No opponent aim source exposed');eq(calls.setPlacementCard.at(-1).args[1],0,'No opponent placement prompt');
eq(board.OriginalDifficultyChangeAllowed(1),false,'Cannot replace Unfair midway through active match');eq(board.OriginalDifficultyChangeAllowed(4),false,'Policy boundary stays fixed');
let policyCalls=0;board.duel.PumpOpponent=()=>{policyCalls++;throw Error('Current policy inside Unfair');};
board.duel.AiMulligan=()=>{policyCalls++;throw Error('Current mulligan inside Unfair');};
let mulligans=0;
while(board.duel.mulligan&&board.duel.RequestDecisionSide()===2){runtime.clock(.016);board.ResumeOriginalOpponent();assert(!board.originalFailure);assert(++mulligans<8);}
eq(board.duel.RequestDecisionSide(),1,'Human receives own mulligan after Beta finishes');runtime.clear();board.Publish(board.duel.GetMessage(),true);
assert(calls.pushRequestCard.length>0);checks++;eq(calls.setRequestHeader.at(-1).args[2],1,'Only human request projected');
assert(board.duel.FinishMulligan(board.duel.requestId));
let humanPasses=0,callbacks=0,searchCallbacks=0;
while(!board.duel.Snapshot().matchWinnerMask){
 if(board.duel.waiting){assert(board.duel.BeginNextRound());board.Publish(board.duel.GetMessage(),true);}
 else if(board.duel.mulligan&&board.duel.RequestDecisionSide()===1){assert(board.duel.FinishMulligan(board.duel.requestId));board.Publish(board.duel.GetMessage(),true);}
 else if(board.OriginalNeedsStep()){
  const searching=board.originalController&&!board.originalController.search.finished;
  runtime.clear();runtime.clock(.016);board.ResumeOriginalOpponent();assert(!board.originalFailure,board.duel.message);callbacks++;assert(callbacks<5000,'Cooperative callback ceiling');
  if(searching){searchCallbacks++;eq(calls.beginVisualBatch.length,0,'Speculative search never publishes live Flash frames');}
  if(board.OriginalPrivateRequest()){
   eq(calls.setRequestHeader.at(-1).args[1],0,'Every private replay request remains hidden');eq(calls.pushRequestCard.length,0,'No private candidates in Flash');
  }
 }else{assert.equal(board.duel.match.currentPlayerId,1);assert(board.duel.Pass(1));humanPasses++;board.Publish(board.duel.GetMessage());}
 board.visualBusy=false;runtime.clear();
}
eq(policyCalls,0,'No current-policy turns or exchanges in Unfair');eq(board.OriginalDifficultyChangeAllowed(1),true,'May change mode after match');
assert(searchCallbacks>0);checks++;
assert(runtime.logs.some(s=>s.startsWith('ORIGINAL_BETA_TURN')));checks++;
// Existing policy1..3 is still routed through the unchanged preparation/pump.
board.originalOpponent=false;board.originalFailure=false;board.deferredOpponent=true;board.visualBusy=false;
let preparation=0,pump=0;board.duel.AiPreparationStep=()=>{preparation++;return true;};board.duel.PumpOpponent=()=>{pump++;return true;};board.duel.aiPreparationStage=0;
board.ResumeOpponentAfterVoice();eq([preparation,pump],[1,1],'Existing difficulty path retained');
// A replay publish skips PumpOpponent. Exhausted human turns must still be
// scheduled through the next audio/visual callback for either policy.
for(const level of [3,4])for(const leaderReady of [false,true]){
 const r=makeRuntime(manifest.flashFields),b=r.board;r.setDifficulty(level);assert(b.StartSelectedDuel());
 const g=b.duel;g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.pendingChoice=false;g.pendingRow=false;g.waiting=false;
 for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&s.locationMask===8)c.Move(1,512,0);}
 const leader=g.Leader(1);assert(leader);if(!leaderReady)leader.SetPlayable(false);
 g.match.currentPlayerId=1;g.match.turnActive=true;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 b.deferredOpponent=false;b.originalController=null;b.originalFailure=false;g.visualFrames.Clear();b.Publish(g.GetMessage(),true);
 eq(b.deferredOpponent,!leaderReady,'Empty hand schedules next callback only after leader is spent: '+level);
 if(!leaderReady){b.visualBusy=false;b.ResumeOpponentAfterVoice();eq(g.Snapshot().playerOne.hasPassed,true,'Replay boundary auto-passes exhausted human: '+level);}
 else{eq(g.Snapshot().playerOne.hasPassed,false,'Unused leader remains playable: '+level);}
 // An unresolved exchange is never replaced by the automatic turn pass.
 g.match.currentPlayerId=1;g.match.turnActive=true;g.match.playerOne.hasPassed=false;g.waiting=false;g.match.matchWinnerMask=0;g.mulligan=true;
 eq(b.EmptyHandPassWaiting(),false,'Pending request blocks automatic pass: '+level+'/'+leaderReady);
}
let selectedProfileStartCases=0;
const mappingPath=path.resolve(__dirname,'../../data/beta924/design/beta_ai_profiles093.json');
if(fs.existsSync(mappingPath)){
 const mapping=JSON.parse(fs.readFileSync(mappingPath,'utf8'));assert(mapping.validated);
 for(const preset of [24,65,107]){
  const r=makeRuntime(manifest.flashFields);r.setOpponent(preset);
  eq(r.board.StartSelectedDuel(),true,'Actual menu starts mapped deck '+preset);
  eq(r.board.originalPersonality.profileName,mapping.assignments.find(a=>a.presetId===preset).profile,'Actual menu uses selected source profile '+preset);
  selectedProfileStartCases++;
 }
}
const report={checks,initialBetaMulliganCallbacks:mulligans,betaCallbacks:callbacks,searchCallbacks,humanPasses,policyCalls,privateRequestsProjected:false,emptyHandPassCases:4,selectedProfileStartCases,
 scope:'Actual WS board start/scheduling/private-request projection and original-vs-existing policy routing. Captured Flash boundary; no native gameplay acceptance.',nativeGameTested:false};
fs.writeFileSync(path.join(contract,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
