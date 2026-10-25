/* Direct PlayMaker.cs port. Strategy names, thresholds, source quirks and
 * float32 RevisedScore changes are retained. Reads completed search nodes;
 * never runs a battle simulation or invokes another policy. */
'use strict';
const {Status,reorderChildren}=require('./search.cjs');
const F=Math.fround,LOW=-3.4028234663852886e38,SOURCE_ALL=0x303;
const sign=n=>n===0?'Drawing':n>0?'Ahead':'Behind';
const isPass=n=>n.decision===null||n.decision?.cardId===0;
function handCount(state,side){return state.cards.filter(c=>c.side===side&&c.zone===8&&c.playable).length;}
function carryover(state,side){return state.cards.filter(c=>c.side===side&&(c.zone&7)!==0&&(c.tokens&1)!==0).reduce((n,c)=>n+c.power,0);}
function scoreDiff(state,side){return state.players[side-1].score-state.players[2-side].score;}
class BetaPlayMaker {
 determine(root,personality){
  this.root=root;this.p=personality;this.side=root.executingPlayerId;this.opponent=3-this.side;
  const s=root.state;
  if(!Number.isInteger(s.roundTurnIndex))throw Error('PlayMaker needs authoritative per-round turn index');
  this.turn=s.roundTurnIndex;this.diff=scoreDiff(s,this.side);this.scoreStatus=sign(this.diff);
  this.carryDiff=carryover(s,this.side)-carryover(s,this.opponent);this.carryStatus=sign(this.carryDiff);
  this.hand=handCount(s,this.side);this.cardStatus=sign(this.hand-handCount(s,this.opponent));
  this.passStatus=s.passed[this.opponent-1]?'OpponentPassed':handCount(s,this.opponent)===0?'OpponentWillAutoPass':'OpponentStillPlaying';
  const first=s.rounds[0]?.winnerMask;
  this.round=s.roundId===1?'Round1':s.roundId===3?'Round3':first===this.side?'Round2WonFirstRound':first===SOURCE_ALL?'Round2DrewFirstRound':'Round2LostFirstRound';
  this.pass=null;this.best=null;this.strongest=null;let tempo=-2147483648;
  for(const n of root.children){
   if(n.status!==Status.OK||!n.state)continue;
   if(isPass(n)){if(this.pass===null)this.pass=n;continue;}
   if(this.best===null)this.best=n;
   const value=this.originalDiff(n)-this.diff;
   if(value>tempo){this.strongest=n;tempo=value;}
  }
  return this.strategy();
 }
 originalDiff(node){
  const s=node.state;if(!s)throw Error('PlayMaker cannot read incomplete node');
  if(s.roundIndex===this.root.state.roundIndex)return scoreDiff(s,this.side);
  const scores=s.rounds[s.rounds.length-1]?.playerScores;
  if(!scores)throw Error('PlayMaker needs completed original-round scores');
  return scores[this.side-1]-scores[2-this.side];
 }
 strategy(){
  const playing=this.passStatus==='OpponentStillPlaying',score=this.scoreStatus,round=this.round;
  if(round==='Round1'){
   if(playing){
    if(score==='Ahead')return 'PassIfOpponentCantCatchUpIn1Card';
    if(score==='Behind')return this.hand===1?'PlayIfAbleToOvertakeInOneCard':'PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard';
    if(this.carryStatus==='Ahead')return 'PassIfStillWinningOrDrawingOtherwisePlayStrongestCard';
    if(this.carryStatus==='Behind')return 'PlayStrongestCard';
    if(this.cardStatus==='Behind')return 'PlayBestCard';
    const turns=this.turn%2!==1?Math.trunc(this.turn/2)-1:Math.trunc((this.turn-1)/2);
    return turns>=this.p.FirstRoundTurnsNeededBeforePassingWhenDrawingAndHavingSameCarryover?'PassIfStillWinningOrDrawingOtherwisePlayBestCard':'PlayBestCard';
   }
   if(score==='Ahead')return 'PassIfStillWinningOtherwisePlayBestCard';
   if(score==='Behind')return 'PlayIfAbleToOvertakeInOneCard';
   return this.cardStatus==='Behind'?'PassIfStillWinningOrDrawingOtherwisePlayBestCard':this.cardStatus==='Ahead'?'PlayBestCard':'PlayLowTempoCardIfAbleOtherwisePlayBest';
  }
  if(round==='Round2WonFirstRound'){
   if(!playing)return score==='Behind'?'PlayIfAbleToOvertakeInOneCard':'PassIfStillWinningOrDrawingOtherwisePlayStrongestCard';
   if(score==='Ahead')return this.carryDiff>=10?'PassIfStillWinningOtherwisePlayBestCard':'PassIfOpponentCantCatchUpIn1Card';
   if(score==='Behind')return 'PlayLowTempoCardIfAbleOtherwisePass';
   return this.turn>2||this.p.CanDryPassOnRound2?'PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass':'PlayLowTempoCardIfAbleOtherwisePass';
  }
  if(round==='Round2LostFirstRound'){
   if(playing)return score==='Ahead'?'PlayLowTempoCardIfAbleOtherwisePlayStrongest':score==='Behind'?'PlayBestCard':'PlayStrongestCard';
   return score==='Ahead'?'PassIfStillWinningOtherwisePlayStrongestCard':score==='Behind'?'PlayStrongestCard':'PlayLowTempoCardIfAbleOtherwisePlayBest';
  }
  if(round==='Round2DrewFirstRound')return !playing&&score==='Ahead'?'PassIfStillWinningOtherwisePlayBestCard':'DontPassUnlessAllPlayActionsAreDetrimental';
  if(round==='Round3'){
   if(playing)return score==='Ahead'?'DontPassUnlessAllPlayActionsAreDetrimental':'PlayBestCard';
   return score==='Behind'?'DontPassUnlessAllPlayActionsAreDetrimental':'PassIfStillWinningOtherwisePlayBestCard';
  }
  return 'Default';
 }
 threshold(isWinning){
  const prefix=this.round==='Round1'?(this.turn<=2?'VeryFirstTurn':'FirstRound'):'';
  return this.p[prefix+(isWinning?'Win':'Lose')+'PointDiffBeforePassingThreshold'];
 }
 winningAfterPass(includeDrawing){
  if(!this.pass)return false;
  const s=this.pass.state;
  if(this.passStatus==='OpponentPassed'){
   const winner=this.round!=='Round3'&&this.round!=='Round2DrewFirstRound'?s.rounds[s.rounds.length-1]?.winnerMask:s.currentRoundWinner;
   return winner===this.side||(includeDrawing&&winner===SOURCE_ALL);
  }
  const diff=scoreDiff(s,this.side);return includeDrawing?diff>=0:diff>0;
 }
 setBest(node){
  if(!node)return;
  const pass=this.pass?.revisedScore??LOW,best=this.best?.revisedScore??LOW,winner=pass>=best?this.pass:this.best;
  if(node!==winner&&winner)node.revisedScore=F(winner.revisedScore+1);
  reorderChildren(this.root,this.side);
 }
 lowTempo(){
  let chosen=null,value=2147483647;
  for(const n of this.root.children){
   if(isPass(n)||!n.state)continue;
   const card=n.state.cards.find(c=>c.id===n.decision.cardId);
   if(!card?.semanticTags.includes(6))continue;
   const diff=this.originalDiff(n);if(diff>=this.diff&&diff<value){chosen=n;value=diff;}
  }
  return chosen;
 }
 implement(strategy){
  if(strategy==='Default')return;
  if(strategy==='Pass'){
   if(this.pass&&this.best&&this.best.revisedScore>=this.pass.revisedScore)this.pass.revisedScore=F(this.best.revisedScore+1);
   return;
  }
  if(strategy==='PlayBestCard'){
   if(this.pass&&this.best&&this.pass.revisedScore>=this.best.revisedScore)this.pass.revisedScore=F(this.best.revisedScore-1);
   return;
  }
  if(strategy==='PlayStrongestCard'){if(this.strongest)this.setBest(this.strongest);else this.implement('PlayBestCard');return;}
  if(strategy.startsWith('PassIfStillWinning')){
   const drawing=strategy.startsWith('PassIfStillWinningOrDrawing'),split=strategy.indexOf('Otherwise');
   this.implement(this.winningAfterPass(drawing)?'Pass':strategy.slice(split+9));return;
  }
  if(strategy.startsWith('PlayLowTempoCardIfAbleOtherwise')){
   const low=this.lowTempo();if(low)this.setBest(low);
   else this.implement({PlayBest:'PlayBestCard',PlayStrongest:'PlayStrongestCard',Pass:'Pass'}[strategy.slice(31)]);return;
  }
  if(strategy==='DontPassUnlessAllPlayActionsAreDetrimental'){
   let highest=-2147483648,chosen=null;
   for(const n of this.root.children){
    if(isPass(n))continue;const diff=this.originalDiff(n);
    if(diff>=this.diff){if(n!==this.best){this.setBest(n);this.best=n;}this.implement('PlayBestCard');return;}
    if(diff>highest){highest=diff;chosen=n;}
   }
   if(this.pass&&chosen&&highest>this.originalDiff(this.pass)){this.setBest(chosen);this.best=chosen;this.implement('PlayBestCard');return;}
   this.implement('Pass');return;
  }
  if(strategy==='PassIfOpponentCantCatchUpIn1Card'){
   if(this.pass)this.implement(this.originalDiff(this.pass)<this.threshold(this.scoreStatus==='Ahead')?'PlayBestCard':'Pass');return;
  }
  if(strategy==='PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard'){
   if(!this.best)return;
   const limit=this.threshold(this.scoreStatus==='Ahead'),able=n=>{const v=this.originalDiff(n);return v>0||Math.abs(v)<=limit;};
   this.implement(able(this.best)?'PlayBestCard':this.strongest&&this.strongest!==this.best&&able(this.strongest)?'PlayStrongestCard':'Pass');return;
  }
  if(strategy==='PlayIfAbleToOvertakeInOneCard'){
   this.implement(this.best&&this.originalDiff(this.best)>0?'PlayBestCard':this.strongest&&this.originalDiff(this.strongest)>0?'PlayStrongestCard':'Pass');return;
  }
  throw Error('Unported PlayMaker strategy: '+strategy);
 }
 apply(root,personality){
  if(!personality.UsePlayMakerSystemAfterTreeSearch||!root?.children?.length)return {applied:false};
  const strategy=this.determine(root,personality);this.implement(strategy);reorderChildren(root,this.side);
  return {applied:true,strategy,round:this.round,scoreStatus:this.scoreStatus,passStatus:this.passStatus};
 }
}
module.exports={BetaPlayMaker,handCount,carryover,scoreDiff,SOURCE_ALL};
