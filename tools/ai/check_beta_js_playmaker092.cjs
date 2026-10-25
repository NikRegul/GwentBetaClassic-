'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {BetaPlayMaker,SOURCE_ALL}=require('./beta_js092/playmaker.cjs');
const {BetaSearchNode,Status}=require('./beta_js092/search.cjs');
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs');
const {stepMulligan}=require('./beta_js092/mulligan.cjs');
const p=basePersonality();let checks=0;function eq(a,b,l){assert.deepEqual(a,b,l);checks++;}
// Explicit strategy table transcribed from the 30 DS_* methods. Dynamic cases
// use fixed neutral carry/card advantage, three hand cards, and turn 8.
const table={
 Round1:[['PassIfOpponentCantCatchUpIn1Card','PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard','PassIfStillWinningOrDrawingOtherwisePlayBestCard'],['PassIfStillWinningOtherwisePlayBestCard','PlayIfAbleToOvertakeInOneCard','PlayLowTempoCardIfAbleOtherwisePlayBest']],
 Round2WonFirstRound:[['PassIfOpponentCantCatchUpIn1Card','PlayLowTempoCardIfAbleOtherwisePass','PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass'],['PassIfStillWinningOrDrawingOtherwisePlayStrongestCard','PlayIfAbleToOvertakeInOneCard','PassIfStillWinningOrDrawingOtherwisePlayStrongestCard']],
 Round2LostFirstRound:[['PlayLowTempoCardIfAbleOtherwisePlayStrongest','PlayBestCard','PlayStrongestCard'],['PassIfStillWinningOtherwisePlayStrongestCard','PlayStrongestCard','PlayLowTempoCardIfAbleOtherwisePlayBest']],
 Round2DrewFirstRound:[['DontPassUnlessAllPlayActionsAreDetrimental','DontPassUnlessAllPlayActionsAreDetrimental','DontPassUnlessAllPlayActionsAreDetrimental'],['PassIfStillWinningOtherwisePlayBestCard','DontPassUnlessAllPlayActionsAreDetrimental','DontPassUnlessAllPlayActionsAreDetrimental']],
 Round3:[['DontPassUnlessAllPlayActionsAreDetrimental','PlayBestCard','PlayBestCard'],['PassIfStillWinningOtherwisePlayBestCard','DontPassUnlessAllPlayActionsAreDetrimental','PassIfStillWinningOtherwisePlayBestCard']]
};
for(const round of Object.keys(table))for(const [pi,passStatus]of ['OpponentStillPlaying','OpponentPassed','OpponentWillAutoPass'].entries())for(const [si,scoreStatus]of ['Ahead','Behind','Drawing'].entries()){
 const maker=Object.assign(new BetaPlayMaker(),{round,passStatus,scoreStatus,carryStatus:'Drawing',carryDiff:0,cardStatus:'Drawing',hand:3,turn:8,p});
 eq(maker.strategy(),table[round][pi===0?0:1][si],'source strategy '+[round,passStatus,scoreStatus]);
}
const m=Object.assign(new BetaPlayMaker(),{round:'Round1',passStatus:'OpponentStillPlaying',scoreStatus:'Drawing',carryStatus:'Drawing',cardStatus:'Drawing',hand:3,turn:1,p});
for(const turn of [1,2,3,4,5,6,7,8]){m.turn=turn;eq(m.strategy(),turn>=7?'PassIfStillWinningOrDrawingOtherwisePlayBestCard':'PlayBestCard','completed-own-turn threshold '+turn);}
m.carryStatus='Ahead';eq(m.strategy(),'PassIfStillWinningOrDrawingOtherwisePlayStrongestCard','carry lead');
m.carryStatus='Behind';eq(m.strategy(),'PlayStrongestCard','carry deficit');m.carryStatus='Drawing';m.cardStatus='Behind';eq(m.strategy(),'PlayBestCard','card deficit');
m.scoreStatus='Behind';m.hand=1;eq(m.strategy(),'PlayIfAbleToOvertakeInOneCard','last card overtaking');
m.round='Round2WonFirstRound';m.scoreStatus='Ahead';m.carryDiff=10;eq(m.strategy(),'PassIfStillWinningOtherwisePlayBestCard','ten carry cutoff');
m.scoreStatus='Drawing';m.turn=2;m.p={...p,CanDryPassOnRound2:false};eq(m.strategy(),'PlayLowTempoCardIfAbleOtherwisePass','early round2 no drypass');
m.turn=3;eq(m.strategy(),'PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass','later round2 drypass');
// Scored-node examples, mirrored by seat. Scores and tempo deliberately
// disagree: strategic correction must change only revised scores, no actions.
function build(side,diff=5){
 const state={roundId:1,roundIndex:0,roundTurnIndex:1,currentRoundWinner:0,passed:[false,false],rounds:[],players:[{score:0},{score:0}],cards:[]};
 state.players[side-1].score=diff;
 for(const actor of [1,2])for(let i=0;i<3;i++)state.cards.push({id:actor*100+i,side:actor,zone:8,playable:true,power:5,tokens:0,semanticTags:[]});
 const root=new BetaSearchNode(1,0);root.state=state;root.executingPlayerId=side;root.status=Status.OK;
 const nodes=[[null,20,diff],[side*100,10,diff+2],[side*100+1,8,diff+12],[side*100+2,7,diff+1]].map(([card,score,tempo],i)=>{
  const n=new BetaSearchNode(i+2,1,root);n.status=Status.OK;n.executingPlayerId=side;n.decision=card===null?null:{cardId:card};
  n.state=JSON.parse(JSON.stringify(state));n.state.players[side-1].score=tempo;n.revisedScore=score;return n;
 });
 nodes[3].state.cards.find(c=>c.id===side*100+2).semanticTags=[6];root.children=nodes.slice();return {root,nodes};
}
for(const side of [1,2]){
 for(const [strategy,winner]of [['Pass',0],['PlayBestCard',1],['PlayStrongestCard',2],['PlayLowTempoCardIfAbleOtherwisePlayBest',3],['PlayLowTempoCardIfAbleOtherwisePlayStrongest',3],['PlayLowTempoCardIfAbleOtherwisePass',3],['PassIfStillWinningOtherwisePlayBestCard',0],['PassIfStillWinningOrDrawingOtherwisePlayBestCard',0],['PassIfStillWinningOtherwisePlayStrongestCard',0],['PassIfStillWinningOrDrawingOtherwisePlayStrongestCard',0],['PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePlayBest',0],['PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePlayBest',0],['PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePlayStrongest',0],['PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePlayStrongest',0],['PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePass',0],['PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass',0],['DontPassUnlessAllPlayActionsAreDetrimental',1],['PassIfOpponentCantCatchUpIn1Card',1],['PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard',1],['PlayIfAbleToOvertakeInOneCard',1]]){
  const {root,nodes}=build(side),before=JSON.stringify(nodes.map(n=>n.state)),maker=new BetaPlayMaker();maker.determine(root,p);maker.implement(strategy);
  const best=root.children.slice().sort((a,b)=>b.revisedScore-a.revisedScore)[0];eq(best.id,nodes[winner].id,'strategy correction '+strategy+'/'+side);eq(JSON.stringify(nodes.map(n=>n.state)),before,'no simulated mutation');
 }
 for(const [turn,winning,expected]of [[1,true,13],[2,false,22],[3,true,10],[8,false,10]]){
  const maker=new BetaPlayMaker(),{root}=build(side);maker.determine(root,p);maker.turn=turn;eq(maker.threshold(winning),expected,'source threshold family');
 }
 const {root,nodes}=build(side),maker=new BetaPlayMaker();maker.determine(root,p);
 nodes[1].state.roundIndex=1;nodes[1].state.players[side-1].score=999;nodes[1].state.rounds=[{winnerMask:side,playerScores:side===1?[22,19]:[19,22]}];
 eq(maker.originalDiff(nodes[1]),3,'completed previous-round scores, not fresh board');
 root.state.roundId=2;root.state.roundIndex=1;root.state.rounds=[{winnerMask:3,playerScores:[0,0]}];for(const n of nodes)n.state.roundIndex=1;maker.determine(root,p);eq(maker.round,'Round2LostFirstRound','literal original All0x303 mismatch retained');
 root.state.rounds[0].winnerMask=SOURCE_ALL;maker.determine(root,p);eq(maker.round,'Round2DrewFirstRound','source All mask branch');
 root.state.passed[2-side]=true;nodes[0].state.currentRoundWinner=side;nodes[0].state.players[side-1].score=-1;eq(maker.winningAfterPass(false),false,'pass status computed only in determine');maker.determine(root,p);eq(maker.winningAfterPass(false),true,'drawn-first branch reads current round winner');
 nodes[0].state.currentRoundWinner=3;eq(maker.winningAfterPass(true),false,'common draw mask not silently substituted');nodes[0].state.currentRoundWinner=SOURCE_ALL;eq(maker.winningAfterPass(true),true,'source draw mask');
}
// Common production counter lifecycle and clone fidelity. This is a real
// three-round pass-only match; not an AI strength game.
const runtime=createRuntime(path.resolve(process.argv[2]),924020701),g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithPresets(54,54));
for(let round=1;round<=3;round++){
 while(g.mulligan)stepMulligan(g,p);
 eq(g.match.roundTurnIndex,1,'new round starts at original TurnIndex1');
 eq(runtime.cloneSession(g).match.roundTurnIndex,1,'production cloner copies counter');
 const stable=stateFromSession(g);eq(stable.roundTurnIndex,1,'read-only state exposes per-round counter');
 eq(stable.passed,[false,false],'round resets passed flags');
 if(round<3){const id={v:0};g.registry.Allocate(id);const card=runtime.newCard();card.Setup(g,id.v,112405,round,1,0);g.registry.Put(id.v,card);g.live.push(card);}
 assert(g.Pass(g.Snapshot().currentPlayerId));eq(g.match.roundTurnIndex,2,'second turn count');
 assert(g.Pass(g.Snapshot().currentPlayerId));
 if(round<3)assert(g.BeginNextRound());
}
const report={checks,fingerprint:runtime.fingerprint,sourceStrategies:21,sourceDecisionCases:30,mirroredSeats:true,nativeProcessesAllowed:false,
 scope:'All source strategy families, dynamic branches/thresholds, previous-round scores, literal draw-mask quirk, revised-only changes; actual shared per-round counter and clone across3 pass-only rounds. Not a full AI game.',fullMatchReady:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-playmaker-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
