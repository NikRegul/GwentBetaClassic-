/* Replay the ORIGINAL chosen node's decisions into the one live shared game.
 * No policy handler may run during replay; missing records are technical errors.
 * Round/mulligan boundaries belong to live controllers, not to the search's
 * speculative next-round initialization and other-seat simulated finish. */
'use strict';
const {BetaGameTree}=require('./actions.cjs'),{BetaChoiceHandlers}=require('./choices.cjs');
class BetaActionReplay {
 constructor(runtime,personality,game,chosen){
  if(game.IsPending()||game.waiting||game.IsFatal())throw Error('Live replay needs stable turn');
  this.tree=new BetaGameTree(runtime,personality);this.game=game;this.finished=false;this.callbacks=0;
  this.node={game,decision:chosen.decision===null?null:{...chosen.decision},started:false,awaitingInitialPlacement:false,
   executingPlayerId:game.Snapshot().currentPlayerId,choiceCursor:0,handlerScore:0,locationChoices:[],
   choiceRecords:chosen.choiceRecords.map(r=>({...r,chosen:r.chosen.map(c=>({...c}))}))};
  this.choices=new BetaChoiceHandlers(runtime,personality);
  this.choices.handler=()=>{throw Error('Live replay must use stored source decisions');};
  this.choices.next=()=>{throw Error('Live replay must not draw policy RNG');};
  this.choices.fork=()=>{throw Error('Live replay must not create search branches');};
 }
 step(){
  if(this.finished)return {finished:true,mutations:0};
  const g=this.game,n=this.node;
  if(!n.started){n.started=true;this.tree.performInitial(n);}
  else if(n.awaitingInitialPlacement)this.tree.placeInitialLeader(n);
  else if(g.IsPending()&&!g.mulligan){
   if(!n.activeChoice&&n.choiceCursor>=n.choiceRecords.length)throw Error('Selected source node lacks live request record');
   this.choices.request(n);
  }else throw Error('Live replay continuation requested outside action');
  this.callbacks++;
  if(g.IsFatal())throw Error('Fatal during source action replay: '+g.GetMessage());
  if(g.waiting||g.mulligan||!g.IsPending()){
   if(n.activeChoice)throw Error('Live action ended before whole chosen set');
   if(n.choiceCursor!==n.choiceRecords.length)throw Error('Selected source node has unused live decision records');
   this.finished=true;
  }
  return {finished:this.finished,mutations:1,callbacks:this.callbacks};
 }
}
module.exports={BetaActionReplay};
