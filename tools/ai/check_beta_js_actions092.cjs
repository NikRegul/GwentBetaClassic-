/* Source Node actions/search connected to actual common battle rules.
 * Deliberately scoped fixtures: unported nested handlers must fail closed. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');
for(const n of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[n]=()=>{throw Error('Native process forbidden');};
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs');
const {BetaGameTree,availablePositions,UnsupportedBetaPort}=require('./beta_js092/actions.cjs');
const {BetaAlphaBetaSearch,Status}=require('./beta_js092/search.cjs');
const {BetaMiniMaxEvaluator}=require('./beta_js092/core.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924020301),p=basePersonality();
let checks=0,mutations=0,searchSteps=0,realNodes=0;
function eq(a,b,label){assert.deepEqual(a,b,label);checks++;}
function rngState(g){return JSON.stringify(g.random,(k,v)=>k==='bgCloneEpoch'||k==='bgCloneRef'?undefined:v);}
function add(g,t,zone,index,side,power){
 const id={v:0};g.registry.Allocate(id);const c=runtime.newCard();c.Setup(g,id.v,t,side,zone,index);
 if(power!==undefined)c.power.SetCurrentPair(power,0);g.registry.Put(id.v,c);g.live.push(c);return c;
}
function fixture(side){
 const g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithPresets(54,54));
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.match.currentPlayerId=side;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 add(g,112405,8,0,side,8);add(g,112405,8,1,side,12);add(g,112101,8,2,side,6);
 add(g,112405,8,0,3-side,8);add(g,112101,8,1,3-side,6);
 add(g,112405,1,0,side,3);add(g,112405,1,1,side,4);add(g,112405,2,0,3-side,9);return g;
}
// Prototype guards also affect production clones; instance monkey-patches are
// not sufficient because generated CloneSession copies WS fields, not JS closures.
const prototype=runtime.newSession().constructor.prototype;
for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow',
 'BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow',
 'AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])
 prototype[name]=()=>{throw Error('Current policy selector forbidden: '+name);};
for(const side of [1,2]){
 const g=fixture(side),before=stateFromSession(g),rng=rngState(g),tree=new BetaGameTree(runtime,p),root=tree.root(g);
 eq(root.children[0].decision,null,'pass child first');eq(root.children.length,11,'distinct templates, all insertion positions');
 eq(root.children.filter(n=>n.decision!==null&&n.decision.cardId===g.live.filter(c=>c.Snapshot().locationMask===8&&c.Snapshot().positionPlayerId===side)[1].Snapshot().instanceId).length,0,'duplicate-template body not enumerated');
 eq(root.children.slice(1,6).map(n=>[n.decision.row,n.decision.index]),[[1,0],[1,1],[1,2],[2,0],[4,0]],'source row/index order');
 for(const n of root.children.slice(1)){
  const previous=tree.mutations;eq(tree.tryPlayAction(n),true,'real body action completes');eq(tree.mutations-previous,1,'one real play per callback');
  eq(n.status,Status.OK,'node initialized');eq(n.executingPlayerId,side,'actor retained after turn');eq(n.currentPlayerId,3-side,'next actor');
  const placed=n.state.cards.find(c=>c.id===n.decision.cardId);eq([placed.side,placed.zone,placed.index],[n.decision.side,n.decision.row,n.decision.index],'actual chosen insertion');realNodes++;
 }
 eq(stateFromSession(g),before,'source position unchanged');eq(rngState(g),rng,'source RNG unchanged');
 const event=add(g,113301,8,3,side);
 eq(availablePositions(g,event),[{side,row:32,index:-3}],'event original Graveyard/LAST_INDEX position');
 // The incomplete port must reject a real nested target instead of calling P19.
 const blockedTree=new BetaGameTree(runtime,p),blockedRoot=blockedTree.root(g);
 const damage=blockedRoot.children.find(n=>n.decision?.cardId===event.Snapshot().instanceId);
 eq(blockedTree.tryPlayAction(damage),null,'pending target yields cooperatively');
 assert.throws(()=>blockedTree.tryPlayAction(damage),UnsupportedBetaPort);checks++;
}
// Full row: original count==9 excludes the entire row, not its occupied slots.
{
 const g=fixture(1);for(let i=2;i<9;i++)add(g,112405,1,i,1,4);
 const c=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);
 eq(availablePositions(g,c).map(x=>x.row),[2,4],'full row excluded');
}
// Complete a depth-two search and compare all initial-child values against an
// independent exhaustive recursion using real action effects and source formula.
for(const side of [1,2]){
 const g=fixture(side),tree=new BetaGameTree(runtime,p),root=tree.root(g),e=new BetaMiniMaxEvaluator(p);
 function score(n){return e.evaluate(n);}
 const oracle=new BetaGameTree(runtime,p),oracleRoot=oracle.root(runtime.cloneSession(g));
 function oracleComplete(n){let budget=0;while(oracle.tryPlayAction(n)===null)assert(++budget<20);n.score=score(n);}
 const want=oracleRoot.children.map(n=>{
  oracleComplete(n);if(n.terminal)return n.score;
  const v=n.children.map(c=>{oracleComplete(c);return c.score;});return n.currentPlayerId===side?Math.max(...v):Math.min(...v);
 });
 const expectedByDecision=new Map(oracleRoot.children.map((n,i)=>[JSON.stringify(n.decision),want[i]]));
 const search=new BetaAlphaBetaSearch({tryPlayAction:n=>tree.tryPlayAction(n),score,finished:n=>n.terminal});
 search.start(root,{...p,DepthOfChecking:2,AllowPruning:false},side);
 while(!search.finished){const before=tree.mutations,r=search.step(1,32);assert(tree.mutations-before<=1);assert(r.actionAttempts<=1);assert(r.operations<=32);assert(++searchSteps<10000);}
 for(const n of root.children)eq(n.revisedScore,expectedByDecision.get(JSON.stringify(n.decision)),'real two-ply exhaustive answer');
 eq(search.completedDepth,1,'depth two complete');mutations+=tree.mutations;realNodes+=search.explored;
 eq(tree.root(g).children[1].game,undefined,'new tree starts with lazy clone');
 const one=runtime.cloneSession(g),two=runtime.cloneSession(g);assert.notEqual(one,two);assert.notEqual(one.live[0],two.live[0]);checks+=2;
}
// Original search skips the other player's simulated mulligan, while its own
// exchanges are recorded for replay. Live controllers choose both seats.
for(const side of [1,2]){
 const g=fixture(side);(side===1?g.match.playerTwo:g.match.playerOne).hasPassed=true;
 for(let i=0;i<8;i++){add(g,113301,16,i,1);add(g,113301,16,i,2);}
 const tree=new BetaGameTree(runtime,p),root=tree.root(g),pass=root.children[0];let calls=0;
 while(tree.tryPlayAction(pass)===null)assert(++calls<15);
 eq(pass.state.roundId,2,'pass continuation reaches next round');
 eq(pass.mulliganChoices.every(c=>c.side===side),true,'only source executing seat simulated mulligan recorded');
 assert(pass.mulliganChoices.length>0);checks++;
 eq(pass.status,Status.OK,'round continuation reaches stable node');realNodes++;
}
const report={checks,realNodes,mutations,searchSteps,fingerprint:runtime.fingerprint,maxMutationsPerSearchStep:1,
 nativeProcessesAllowed:false,currentPolicySelectorsAllowed:false,fullAiPortComplete:false,fullMatchReady:false,
 scope:'Source Node generic generation/execution with actual shared WS actions; exact placement/dedup/pass order, original event position, source/RNG isolation, two-ply exhaustive search on small battle fixtures. Unported nested handlers fail explicitly.'};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-actions-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
