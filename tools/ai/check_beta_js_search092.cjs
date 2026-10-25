/* Pure-JS cooperative search versus independent exhaustive finite-tree
 * answers. Battle rules/handlers are not supplied by these synthetic trees. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {BetaAlphaBetaSearch,BetaSearchNode,Status}=require('./beta_js092/search.cjs');
let checks=0,steps=0,peakAttempts=0,peakOperations=0;
function makeTree(seed,height=4){
 let id=0,rng=seed>>>0;
 function next(){rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng;}
 function make(depth,parent){
  const n=new BetaSearchNode(id++,depth,parent);n.executingPlayerId=depth%2===1?1:2;n.currentPlayerId=3-n.executingPlayerId;
  n.toyScore=next()%101;n.terminal=depth===height;
  if(depth===0){n.executingPlayerId=1;n.currentPlayerId=1;n.status=Status.OK;}
  if(!n.terminal)for(let i=0;i<3;i++)n.children.push(make(depth+1,n));
  return n;
 }
 return make(0,null);
}
function exhaustive(node,remaining){
 if(remaining===0||node.terminal)return node.toyScore;
 const values=node.children.map(c=>exhaustive(c,remaining-1));
 return node.currentPlayerId===1?Math.max(...values):Math.min(...values);
}
function job(root,depth,prune){
 let calls=0;
 const search=new BetaAlphaBetaSearch({tryPlayAction:n=>{calls++;n.status=Status.OK;return true;},score:n=>n.toyScore,finished:n=>n.terminal});
 search.start(root,{DepthOfChecking:depth,AllowPruning:prune},1);
 return {search,calls:()=>calls};
}
function oneStep(j){
 const before=j.calls(),p=j.search.step(1,32);assert(p.actionAttempts<=1);assert.equal(j.calls()-before,p.actionAttempts);
 assert(p.operations<=32);peakAttempts=Math.max(peakAttempts,p.actionAttempts);peakOperations=Math.max(peakOperations,p.operations);
 steps++;assert(steps<100000);return p;
}
let independentTrees=0;
for(let seed=1;seed<=24;seed++)for(let depth=1;depth<=4;depth++){
 const root=makeTree(seed),expected=root.children.map(c=>({id:c.id,score:exhaustive(c,depth-1)}));
 const j=job(root,depth,false);while(!j.search.finished)oneStep(j);
 for(const n of root.children){assert.equal(n.revisedScore,expected.find(e=>e.id===n.id).score);checks++;}
 assert.equal(j.search.completedDepth,depth-1);checks++;independentTrees++;
}
// Original Base has pruning disabled. Exercise inherited alpha/beta at depths
// before a previously pruned node can become a deeper iterative frontier.
let pruningTrees=0;
for(let seed=31;seed<=54;seed++)for(let depth=2;depth<=3;depth++){
 const root=makeTree(seed),expected=root.children.map(c=>({id:c.id,score:exhaustive(c,depth-1)}));
 const j=job(root,depth,true);while(!j.search.finished)oneStep(j);
 for(const n of root.children){assert.equal(n.revisedScore,expected.find(e=>e.id===n.id).score);checks++;}
 pruningTrees++;
}
// Stop halfway through a deeper iteration: last complete score buffer is
// restored, and subsequent steps never invoke another simulation action.
const root=makeTree(73),j=job(root,3,false);
while(j.search.completedDepth<0)oneStep(j);
const completed=new Map(root.children.map(n=>[n.id,n.revisedScore]));
while(j.search.rootIndex===0&&j.search.depth===1)oneStep(j);
assert.equal(j.search.completedDepth,0);assert.equal(j.search.depth,1);
j.search.requestStop();const callsBeforeStop=j.calls();while(!j.search.finished)oneStep(j);
assert.equal(j.calls(),callsBeforeStop);checks++;
for(const n of root.children){assert.equal(n.revisedScore,completed.get(n.id));checks++;}
assert.equal(j.search.finishReason,'stopped');checks++;
// Unlimited configured depth exits when the finite tree has no new actions.
const finite=job(makeTree(81,2),0,false);while(!finite.search.finished)oneStep(finite);
assert.equal(finite.search.finishReason,'no-new-nodes');checks++;
// Real actions can pause at several nested decisions. Score exactly once at
// the completed boundary, and preserve the frame across null continuations.
const pausedRoot=makeTree(91,1),continuations=new Map();let scored=0,pendingCallbacks=0;
const paused=new BetaAlphaBetaSearch({tryPlayAction:n=>{
 pendingCallbacks++;const count=(continuations.get(n)||0)+1;continuations.set(n,count);
 if(count<3)return null;n.status=Status.OK;return true;
},score:n=>{scored++;return n.toyScore;},finished:n=>n.terminal});
paused.start(pausedRoot,{DepthOfChecking:1,AllowPruning:false},1);
while(!paused.finished){const count=pendingCallbacks,r=paused.step(1,32);assert(pendingCallbacks-count<=1);assert(r.operations<=32);}
assert.equal(scored,3);checks++;assert.equal(pendingCallbacks,9);checks++;
for(const n of pausedRoot.children){assert.equal(n.revisedScore,n.toyScore);checks++;}
const report={schema:1,complete:true,checks,independentTrees,pruningTrees,steps,peakAttempts,peakOperations,
 nativeProcessesRequired:false,cooperative:true,fullAiPortComplete:false,fullMatchReady:false,notStrengthResult:true,
 scope:'Direct AlphaBeta iteration/bounds/buffering port with resumable frames; exhaustive synthetic-tree answers, one action callback per step, stop restoration and finite-tree completion.',
 pending:['Complete shared battle-action handler integration','PlayMaker','Target/choice handlers','Real mixed-policy match'],
 sourceBehavior:'Previously Pruned nodes stay skipped in later iterations, matching original TryPlayAction. Do not claim arbitrary-depth pruning optimality for that original behavior.'};
const out=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-search-proof.json');
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
