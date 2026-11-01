'use strict';
// Read-only replay of a newly frozen tournament game. Reproduce the recorded
// force-stop callback rather than guessing wall-clock samples or changing AI.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('node:assert/strict'),zlib=require('zlib');
const [folder,id,destination]=process.argv.slice(2);if(!destination||!/^g\d+-r\d+-s\d+-p\d+-m[01]$/.test(id))throw Error('tournament game-id fresh-output-directory');
const source=path.resolve(folder),out=path.resolve(destination),read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(fs.existsSync(out))throw Error('Use a fresh replay output directory');
const plan=read(path.join(source,'plan.json')),gamePath=path.join(source,'games',id+'.json'),game=read(gamePath);
assert.equal(game.planSha256,sha(path.join(source,'plan.json')));assert.equal(game.status,'complete');
assert.equal(game.id,id);
const seriesPath=path.join(source,'series',game.series+'.json'),series=read(seriesPath);
assert.equal(series.planSha256,game.planSha256);
assert.equal(series.games.find(g=>g.id===id)?.sha256,sha(gamePath),'Completed series must authenticate the game');
const parts=/^g(\d+)-r(\d+)-s(\d+)-p(\d+)-m([01])$/.exec(id).slice(1).map(Number);
for(const [index,key]of ['grid','round','slot','pair','mirror'].entries())assert.equal(game[key],parts[index],key);
const mix=n=>{n=Math.imul(n^(n>>>16),0x7feb352d);n=Math.imul(n^(n>>>15),0x846ca68b);return (n^(n>>>16))>>>0;};
assert.equal(game.seed,mix(plan.masterSeed+(((game.grid*8+game.round)*128+game.slot)*8+game.pair)),'Frozen schedule seed');
assert.equal(game.commonFingerprint,plan.commonFingerprint);assert(Array.isArray(game.betaDecisionDiagnostics),'Recorded search cutoffs required');
for(const [file,digest]of Object.entries(plan.codeFiles))assert.equal(sha(path.join(source,'frozen',file)),digest,file);
assert.equal(sha(path.join(source,'entrants.json')),plan.rosterSha256);
assert.equal(sha(path.join(plan.current,'manifest.json')),plan.commonManifestSha256);
const entrants=new Map(read(path.join(source,'entrants.json')).map(e=>[e.key,e]));
const modules=path.join(source,'frozen/tools/ai'),{BetaTurnController}=require(path.join(modules,'beta_js092/controller.cjs'));
const recorder=require(path.join(modules,'classic_diagnostics094.cjs')).createRecorder(BetaTurnController);
const original=BetaTurnController.prototype.start,captures=[];let cursor=0,hardCursor=0;
const hardTrace=game.trace.filter(t=>t.policy!=='beta'),sessions=require(path.join(modules,'beta_js092/session.cjs')),create=sessions.createRuntime;
sessions.createRuntime=function(...args){
 const runtime=create(...args),newSession=runtime.newSession;
 runtime.newSession=function(){
  const live=newSession(),prototype=live.constructor.prototype,step=prototype.OpponentStep;
  prototype.OpponentStep=function(...params){
   if(this===live&&!this.aiSimulating){
    const expected=hardTrace[hardCursor],m=this.Snapshot();assert(expected&&m.currentPlayerId===2);assert.equal(m.roundNumber,expected.round);
    captures.push({mode:'hard',index:hardCursor++,sideInRecordedGame:expected.side,normalizedActorSide:2,round:m.roundNumber,state:runtime.serialize(this)});
   }
   return step.apply(this,params);
  };
  return live;
 };
 return runtime;
};
const {playMatch}=require(path.join(modules,'beta_js092/matches.cjs'));
sessions.createRuntime=create;
BetaTurnController.prototype.start=function(g){
 const expected=game.betaDecisionDiagnostics[cursor++];assert(expected&&!expected.exception&&!expected.diagnosticError,'Complete recorded decision required');
 const m=g.Snapshot();assert.equal(m.currentPlayerId,expected.side);assert.equal(m.roundNumber,expected.round);assert.equal(this.personality.name,expected.profile);
 const index=expected.forceAtCallback;
 assert(index===null||Number.isSafeInteger(index)&&index>=0);
 this.now=()=>index!==null&&Number.isSafeInteger(this.searchCallbacks)&&this.searchCallbacks>=index?1000000:0;
 captures.push({mode:'classic',index:cursor-1,side:m.currentPlayerId,round:m.roundNumber,profile:this.personality.name,state:this.runtime.serialize(g)});
 return original.call(this,g);
};
let replay;
try{replay=recorder.play(playMatch,{current:plan.current},entrants.get(game.left),entrants.get(game.right),game.seed);}
finally{BetaTurnController.prototype.start=original;recorder.restore();}
assert.equal(cursor,game.betaDecisionDiagnostics.length);
assert.equal(hardCursor,hardTrace.length);
for(const name of ['status','winner','commonFingerprint','finalStateSha256','crowns','trace','betaForcedSearches','betaPlaymakerErrors','betaSearchCallbacks'])assert.deepEqual(replay[name],game[name],name);
const decisionView=d=>({side:d.side,round:d.round,profile:d.profile,searchCallbacks:d.searchCallbacks,forceAtCallback:d.forceAtCallback,finishReason:d.finishReason,completedDepth:d.completedDepth,decision:d.decision,playmakerError:d.playmakerError});
assert.deepEqual(replay.betaDecisionDiagnostics.map(decisionView),game.betaDecisionDiagnostics.map(decisionView));
fs.mkdirSync(out,{recursive:true});fs.copyFileSync(__filename,path.join(out,'runner.cjs'));
const positions=[];
for(const capture of captures){const name=capture.mode+'-decision-'+capture.index+'.json.gz',file=path.join(out,name);fs.writeFileSync(file,zlib.gzipSync(JSON.stringify(capture)));positions.push({file:name,sha256:sha(file)});}
fs.writeFileSync(path.join(out,'replayed-game.json'),JSON.stringify(replay,null,2)+'\n');
const result={complete:true,game:id,sourceGameSha256:sha(gamePath),planSha256:game.planSha256,commonFingerprint:plan.commonFingerprint,
 sourceSeriesSha256:sha(seriesPath),exactFinalStateAndTrace:true,recordedCutoffsReproduced:true,classicDecisions:cursor,hardDecisions:hardCursor,positions,nativeGameplayVerified:false,notStrengthResult:true};
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({...result,positions:positions.length}));
