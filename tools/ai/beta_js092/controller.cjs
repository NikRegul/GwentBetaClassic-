/* AIPlayer / AIModule_TreeSearch live turn coordinator. No worker/runtime
 * dependency: the caller supplies a clock and repeatedly calls step().
 * AIPlayer's MaxTimeAllowed delay is followed by the source module's 1s
 * force-fetch grace period. Completed searches need no artificial UI delay.
 * Source StripNodesByBattleRestrictions removes non-OK nodes before picking.
 */
'use strict';
const {BetaGameTree}=require('./actions.cjs');
const {BetaChoiceHandlers}=require('./choices.cjs');
const {BetaAlphaBetaSearch,Status}=require('./search.cjs');
const {BetaMiniMaxEvaluator,chooseBestCardForPersonality}=require('./core.cjs');
const {BetaPlayMaker}=require('./playmaker.cjs');
const {BetaActionReplay}=require('./replay.cjs');
class BetaTurnController {
 constructor(runtime,personality,{now}={}){
  if(typeof now!=='function')throw Error('Caller must supply cooperative controller clock');
  this.runtime=runtime;this.personality=personality;this.now=now;this.finished=true;
 }
 start(game){
  if(!this.finished)throw Error('Previous Beta turn still active');
  const p=this.personality;
  if(p.TreeSearchType!=='AlphaBeta'||p.EvaluatorType!=='MiniMax'||p.CardPickerType!=='BestCardForPersonality')
   throw Error('Source policy path not ported: '+p.name);
  this.live=game;this.startedAt=this.now();this.forceAfterMs=(Number(p.MaxTimeAllowed)+1)*1000;
  this.choices=new BetaChoiceHandlers(this.runtime,p);
  this.tree=new BetaGameTree(this.runtime,p,this.choices.hooks());
  const simulated=this.runtime.cloneSession(game);simulated.externalPolicyMask=3;
  this.root=this.tree.root(simulated);const evaluator=new BetaMiniMaxEvaluator(p);
  this.search=new BetaAlphaBetaSearch({tryPlayAction:n=>this.tree.tryPlayAction(n),score:n=>evaluator.evaluate(n),finished:n=>n.terminal});
  this.search.start(this.root,p,game.Snapshot().currentPlayerId);
  this.searchCallbacks=0;this.replay=null;this.finished=false;this.forceRequested=false;this.playmakerError=null;
 }
 choose(){
  // BaseSearchTree.RunPlayMakerDecision catches and logs its own exception.
  // In a forced partial search the original strategy can touch an unfinished
  // node. Preserve that behavior, retain the diagnostic, then perform the
  // source module's independent restriction/status filter. No policy fallback.
  try{this.strategy=new BetaPlayMaker().apply(this.root,this.personality);}
  catch(e){this.playmakerError=String(e.message);this.strategy={applied:false,error:this.playmakerError};}
  this.scoredNodes=this.root.children.filter(n=>n.status===Status.OK&&n.state);
  this.chosen=chooseBestCardForPersonality(this.scoredNodes);
  if(!this.chosen)throw Error('Original search produced no complete legal node; fallback module not ported');
  this.replay=new BetaActionReplay(this.runtime,this.personality,this.live,this.chosen);
 }
 step(){
  if(this.finished)return {finished:true,mutations:0};
  if(!this.search.finished){
   if(!this.forceRequested&&this.now()-this.startedAt>=this.forceAfterMs){this.search.requestStop();this.forceRequested=true;}
   const before=this.tree.mutations,r=this.search.step(1,32);this.searchCallbacks++;
   const mutations=this.tree.mutations-before;if(mutations>1||r.actionAttempts>1)throw Error('Beta search callback exceeded one action');
   return {finished:false,phase:'search',mutations};
  }
  if(!this.replay){this.choose();return {finished:false,phase:'pick',mutations:0};}
  const r=this.replay.step();this.finished=r.finished;
  return {...r,phase:'replay'};
 }
}
module.exports={BetaTurnController};
