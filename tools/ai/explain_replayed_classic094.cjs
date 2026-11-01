'use strict';
// Explain recorded Classic searches without replaying a live action or changing
// frozen policy. Each decision and callback count must match the verified game.
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto'),assert=require('node:assert/strict');
const [tournament,replayDir,output]=process.argv.slice(2);
if(!output)throw Error('tournament verified-replay fresh-report.json');
const root=path.resolve(tournament),replay=path.resolve(replayDir),read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
assert(!fs.existsSync(output),'Use a fresh report');
const plan=read(path.join(root,'plan.json')),proof=read(path.join(replay,'verification.json'));
assert(proof.complete&&proof.exactFinalStateAndTrace&&proof.recordedCutoffsReproduced);
assert.equal(proof.planSha256,sha(path.join(root,'plan.json')));
assert.equal(proof.sourceGameSha256,sha(path.join(root,'games',proof.game+'.json')));
for(const [file,digest]of Object.entries(plan.codeFiles))assert.equal(sha(path.join(root,'frozen',file)),digest,file);
const recorded=read(path.join(replay,'replayed-game.json'));
const modules=path.join(root,'frozen/tools/ai/beta_js092');
const {createRuntime}=require(path.join(modules,'session.cjs')),{personality}=require(path.join(modules,'profiles.cjs'));
const {BetaTurnController}=require(path.join(modules,'controller.cjs')),{BetaPlayMaker}=require(path.join(modules,'playmaker.cjs'));
const {BetaMiniMaxEvaluator}=require(path.join(modules,'core.cjs')),{Status}=require(path.join(modules,'search.cjs'));
const runtime=createRuntime(plan.current),results=[];
for(const item of proof.positions){
 const input=path.join(replay,item.file);assert.equal(sha(input),item.sha256);
 const capture=JSON.parse(zlib.gunzipSync(fs.readFileSync(input)));if(capture.mode!=='classic')continue;
 const expected=recorded.betaDecisionDiagnostics[capture.index],g=runtime.deserialize(capture.state),p=personality(capture.profile);
 let controller;const cutoff=expected.forceAtCallback;
 controller=new BetaTurnController(runtime,p,{now:()=>cutoff!==null&&Number.isSafeInteger(controller?.searchCallbacks)&&controller.searchCallbacks>=cutoff?1000000:0});
 controller.start(g);
 while(!controller.search.finished){controller.step();assert(controller.searchCallbacks<=expected.searchCallbacks,'Recorded callback budget');}
 assert.equal(controller.searchCallbacks,expected.searchCallbacks);assert.equal(controller.search.completedDepth,expected.completedDepth);
 assert.equal(controller.search.finishReason,expected.finishReason);
 const maker=new BetaPlayMaker(),strategy=maker.determine(controller.root,p),evaluator=new BetaMiniMaxEvaluator(p);
 const viable=controller.root.children.filter(n=>n.status===Status.OK&&n.state);
 const nodes=viable.map(n=>({decision:n.decision,scoreBefore:n.revisedScore,originalRoundDiff:maker.originalDiff(n),details:evaluator.details(n)}));
 controller.choose();assert.deepEqual(controller.chosen.decision||null,expected.decision);assert.equal(controller.playmakerError,expected.playmakerError);
 nodes.forEach((row,i)=>{row.scoreAfter=viable[i].revisedScore;row.chosen=viable[i]===controller.chosen;});
 const m=g.Snapshot();results.push({index:capture.index,side:capture.side,round:capture.round,profile:p.name,
  before:{score:[g.Score(1),g.Score(2)],hand:[g.CountLocation(1,8),g.CountLocation(2,8)],crowns:[m.playerOne.crowns,m.playerTwo.crowns]},
  settings:{DepthOfChecking:p.DepthOfChecking,MaxIterationsAllowed:p.MaxIterationsAllowed,MaxTimeAllowed:p.MaxTimeAllowed},
  strategy,passStatus:maker.passStatus,scoreStatus:maker.scoreStatus,originalDiff:maker.diff,threshold:maker.threshold(maker.scoreStatus==='Ahead'),
  passDiff:maker.pass?maker.originalDiff(maker.pass):null,searchCallbacks:controller.searchCallbacks,completedDepth:controller.search.completedDepth,
  forceAtCallback:cutoff,chosen:expected.decision,nodes});
}
assert.equal(results.length,proof.classicDecisions);
const original=path.resolve(__dirname,'../../BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay.AI/PlayMaker.cs');
const report={complete:true,game:proof.game,planSha256:proof.planSha256,verificationSha256:sha(path.join(replay,'verification.json')),
 sourcePlayMakerSha256:sha(original),policyUnchanged:true,decisionsExactlyMatch:true,notStrengthResult:true,nativeGameplayVerified:false,results};
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({complete:true,game:report.game,decisions:results.length,passes:results.filter(r=>!r.chosen).map(({index,round,before,strategy,originalDiff,threshold,passDiff})=>({index,round,before,strategy,originalDiff,threshold,passDiff}))}));
