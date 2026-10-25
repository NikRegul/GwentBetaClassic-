'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {BetaAlphaBetaSearch,BetaSearchNode,Status}=require('./beta_js092/search.cjs');
const stage=path.resolve(process.argv[2]);
const code=fs.readFileSync(path.resolve(__dirname,'jshost/runtime.js'),'utf8')+'\n'+fs.readFileSync(path.join(stage,'ws-stage.js'),'utf8');
const ws=new Function(code+`
return {node:()=>{let n=new CBetaOriginalNode();n.Initialize();return n;},
 search:(root,depth,prune,play,score)=>{let s=new CBetaOriginalAlphaBeta(),h=new CBetaOriginalTreeHooks(),p=new CBetaOriginalPersonality();
 h.TryPlayAction=play;h.Score=score;s.hooks=h;p.DepthOfChecking=depth;p.AllowPruning=prune;s.Start(root,p,1);return s;}};`)();
let checks=0,steps=0,peakAttempts=0,peakOperations=0;
const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
function tree(seed,height=4,typed=false){let id=0,rng=seed>>>0;
 const next=()=>rng=(Math.imul(rng,1664525)+1013904223)>>>0;
 function make(depth,parent){const n=typed?ws.node():new BetaSearchNode(id,depth,parent);n.id=id++;n.depth=depth;if(typed)n.parentNode=parent;else n.parent=parent;
  n.executingPlayerId=depth%2===1?1:2;n.currentPlayerId=3-n.executingPlayerId;n.toyScore=next()%101;n.terminal=depth===height;
  if(depth===0){n.executingPlayerId=1;n.currentPlayerId=1;n.status=Status.OK;}
  if(!n.terminal)for(let i=0;i<3;i++)n.children.push(make(depth+1,n));return n;}
 return make(0,null);
}
function exhaustive(n,depth){if(depth===0||n.terminal)return n.toyScore;const v=n.children.map(c=>exhaustive(c,depth-1));return n.currentPlayerId===1?Math.max(...v):Math.min(...v);}
function run(seed,depth,prune,{height=4,pause=1,stopAfter=null}={}){
 const a=tree(seed,height),b=tree(seed,height,true),expected=new Map(a.children.map(c=>[c.id,exhaustive(c,Math.max(0,depth-1))]));
 let callsA=0,callsB=0;const countsA=new Map(),countsB=new Map();
 const play=(n,counts,typed)=>{const count=(counts.get(n.id)||0)+1;counts.set(n.id,count);if(typed)callsB++;else callsA++;
  if(count<pause)return typed?-1:null;n.status=Status.OK;return typed?1:true;};
 const source=new BetaAlphaBetaSearch({tryPlayAction:n=>play(n,countsA,false),score:n=>n.toyScore,finished:n=>n.terminal});source.start(a,{DepthOfChecking:depth,AllowPruning:prune},1);
 const target=ws.search(b,depth,prune,n=>play(n,countsB,true),n=>n.toyScore);
 for(let i=0;!source.finished;i++){
  if(stopAfter!==null&&i===stopAfter){source.requestStop();target.RequestStop();}
  const beforeA=callsA,beforeB=callsB,r=source.step(1,32),t=target.Step(1,32);steps++;
  for(const key of ['finished','actionAttempts','operations','explored','furthestDepth','completedDepth'])eq(t[key],r[key],'Cooperative '+key);
  eq(callsA-beforeA,callsB-beforeB,'Action callback count');assert(callsB-beforeB<=1);assert(t.operations<=32);
  peakAttempts=Math.max(peakAttempts,t.actionAttempts);peakOperations=Math.max(peakOperations,t.operations);assert(i<100000);
 }
 eq(target.finished,true,'Both finished');eq(target.finishReason,source.finishReason,'Same finish reason');
 eq(a.children.map(n=>[n.id,n.revisedScore,n.status]),b.children.map(n=>[n.id,n.RevisedScore(),n.status]),'Same scores/order/status');
 if(stopAfter===null&&depth>0)for(const n of b.children)eq(n.RevisedScore(),expected.get(n.id),'Independent exhaustive answer');
 return {source,target};
}
let trees=0,pruningTrees=0;
for(let seed=1;seed<=24;seed++)for(let depth=1;depth<=4;depth++){run(seed,depth,false);trees++;}
for(let seed=31;seed<=54;seed++)for(let depth=2;depth<=3;depth++){run(seed,depth,true);pruningTrees++;}
run(73,3,false,{stopAfter:10});run(81,0,false,{height:2});run(91,1,false,{height:1,pause:3});
// A forced stop before the first completed action leaves no invented score.
run(97,2,false,{stopAfter:0});
const report={checks,steps,trees,pruningTrees,peakAttempts,peakOperations,cooperative:true,
 scope:'Typed WS AlphaBeta vs direct JS and independent finite-tree answers, including pause/force/buffer restoration; live WS battle hooks still pending',nativeCompiled:false};
fs.writeFileSync(path.join(stage,'search-parity.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
