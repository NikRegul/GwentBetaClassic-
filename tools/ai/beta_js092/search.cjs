/* AlphaBetaSearch.RunTree(true) / RunAlphaBetaSearch direct algorithm port.
 * Recursion and worker threads are replaced with explicit resumable frames for
 * WS. Battle actions are supplied through hooks; the source PlayMaker runs
 * separately after this search. Request/profile coverage is still incomplete. */
'use strict';
const F=Math.fround,LOW=-3.4028234663852886e38,HIGH=3.4028234663852886e38;
const Status={Uninitialised:0,OK:1,Pruned:2,Error:3};
class BetaSearchNode {
 constructor(id,depth,parent=null){
  this.id=id;this.depth=depth;this.parent=parent;this.status=Status.Uninitialised;
  this.score=0;this.propagatedScore=0;this.revised=LOW;this.children=[];
  this.executingPlayerId=0;this.currentPlayerId=0;this.terminal=false;
 }
 get revisedScore(){return this.revised!==LOW?this.revised:F(this.score+this.propagatedScore);}
 set revisedScore(value){this.revised=F(value);}
}
// Original Node.ReorderChildNodes, including its asymmetric error ordering.
function reorderChildren(node,origin){
 const children=node.children;if(children.length<2||children[0].status===Status.Uninitialised)return;
 const maximize=children[0].executingPlayerId===origin;
 children.sort((x,y)=>{
  if(x.status===y.status)return maximize?y.revisedScore-x.revisedScore:x.revisedScore-y.revisedScore;
  return maximize?(x.status===Status.Error?1:-1):(x.status!==Status.Error?1:-1);
 });
}
class BetaAlphaBetaSearch {
 constructor(hooks){this.hooks=hooks;this.frames=[];this.buffers=[[],[]];this.finalQueue=[];this.finished=true;}
 start(root,personality,origin){
  if(!this.finished)throw Error('Search already running');
  this.root=root;this.personality=personality;this.origin=origin;
  this.depthLimit=personality.DepthOfChecking<=0?2147483647:personality.DepthOfChecking;
  this.depth=-1;this.completedDepth=-1;this.explored=0;this.furthest=0;
  this.currentBuffer=0;this.buffers=[[],[]];this.frames=[];this.finalQueue=[];
  this.rootIndex=0;this.iterationActive=false;this.phase='begin';this.stopRequested=false;this.finished=false;
 }
 requestStop(){this.stopRequested=true;}
 store(node,value){
  const buffer=this.buffers[this.currentBuffer];
  for(let i=0;i<buffer.length;i++)if(buffer[i].node===node){buffer[i].value=F(value);return;}
  buffer.push({node,value:F(value)});
 }
 beginFinish(reason){
  this.finishReason=reason;
  if(this.iterationActive){
   this.currentBuffer=1-this.currentBuffer;
   const previous=this.buffers[this.currentBuffer];
   for(let i=0;i<previous.length;i++)previous[i].node.revisedScore=previous[i].value;
  }
  this.frames=[];this.finalQueue=[this.root];this.finalHead=0;this.phase='finalize';
 }
 returnFrame(value){
  this.lastResult=F(value);const frame=this.frames.pop();this.lastNode=frame.node;
  if(this.frames.length===0){
   // RunTree stores the returned value on each initial child separately from
   // the inherited alpha/beta bound stored by the recursive call itself.
   frame.node.revisedScore=value;this.store(frame.node,value);this.rootIndex++;
  }
 }
 step(maxActionAttempts=1,maxOperations=256){
  if(this.finished)return {finished:true,actionAttempts:0,operations:0};
  let attempts=0,operations=0;
  while(!this.finished&&operations<maxOperations){
   if(this.phase==='finalize'){
    if(this.finalHead>=this.finalQueue.length){this.finished=true;break;}
    const n=this.finalQueue[this.finalHead++];reorderChildren(n,this.origin);
    for(let i=0;i<n.children.length;i++)if(n.children[i].children.length)this.finalQueue.push(n.children[i]);
    operations++;continue;
   }
   if(this.stopRequested){this.beginFinish('stopped');operations++;continue;}
   if(this.phase==='begin'){
    this.depth++;if(this.depth>=this.depthLimit){this.beginFinish('depth-limit');operations++;continue;}
    reorderChildren(this.root,this.origin);this.iterationActive=true;this.nodesBefore=this.explored;
    this.rootIndex=0;this.phase='search';operations++;continue;
   }
   if(this.frames.length===0){
    if(this.rootIndex>=this.root.children.length){
     this.currentBuffer=1-this.currentBuffer;this.iterationActive=false;this.completedDepth=this.depth;
     if(this.nodesBefore===this.explored)this.beginFinish('no-new-nodes');else this.phase='begin';
     operations++;continue;
    }
    this.frames.push({node:this.root.children[this.rootIndex],depth:this.depth,alpha:LOW,beta:HIGH,stage:0});
   }
   const frame=this.frames[this.frames.length-1],node=frame.node;
   if(frame.stage===0){
    if(node.status===Status.Uninitialised){
     if(attempts>=maxActionAttempts)break;
     attempts++;const played=this.hooks.tryPlayAction(node);
     // A shared-engine action may yield at a target/row/mulligan request.
     // null means one cooperative continuation was executed, not an error or
     // a completed node. Never score/skip the partially resolved action.
     if(played===null){operations++;break;}
     if(played){
      this.explored++;if(node.depth>this.furthest)this.furthest=node.depth;
      node.propagatedScore=node.parent===null?0:node.parent.propagatedScore;
      node.score=F(this.hooks.score(node));
     }
    }
    if(node.status!==Status.OK){this.returnFrame(node.revisedScore);operations++;continue;}
    if(frame.depth===0||this.stopRequested||this.hooks.finished(node)){
     this.returnFrame(node.revisedScore);operations++;continue;
    }
    reorderChildren(node,node.executingPlayerId);
    frame.maximize=node.currentPlayerId===this.origin;frame.best=frame.maximize?LOW:HIGH;
    frame.index=0;frame.stage=1;
   }else if(frame.stage===1){
    if(frame.index>=node.children.length){
     const bound=frame.maximize?frame.alpha:frame.beta;node.revisedScore=bound;this.store(node,bound);
     this.returnFrame(frame.best);
    }else{
     frame.stage=2;
     this.frames.push({node:node.children[frame.index],depth:frame.depth-1,alpha:frame.alpha,beta:frame.beta,stage:0});
    }
   }else{
    if(this.lastNode.status!==Status.Error){
     if(frame.maximize){frame.best=Math.max(frame.best,this.lastResult);frame.alpha=Math.max(frame.alpha,frame.best);}
     else{frame.best=Math.min(frame.best,this.lastResult);frame.beta=Math.min(frame.beta,frame.best);}
     if(frame.beta<=frame.alpha&&this.personality.AllowPruning){node.status=Status.Pruned;frame.index=node.children.length;}
     else frame.index++;
    }else frame.index++;
    frame.stage=1;
   }
   operations++;
  }
  return {finished:this.finished,actionAttempts:attempts,operations,explored:this.explored,
   furthestDepth:this.furthest,completedDepth:this.completedDepth};
 }
}
module.exports={BetaAlphaBetaSearch,BetaSearchNode,Status,reorderChildren};
