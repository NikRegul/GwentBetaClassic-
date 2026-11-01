'use strict';
// Adapt a verified full-game replay to the existing hindsight counterfactual
// inspector. Hard captures are already normalized to actor side 2.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib'),assert=require('node:assert/strict');
const [replayDir,analysisFile,output]=process.argv.slice(2);if(!output)throw Error('verified-replay analysis.json fresh-output');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const replay=path.resolve(replayDir),out=path.resolve(output),verification=read(path.join(replay,'verification.json')),analysis=read(analysisFile);
assert(!fs.existsSync(out),'Use a fresh adapter output');assert(verification.complete&&verification.exactFinalStateAndTrace&&verification.hardDecisions>0);
const selection=analysis.selected.hard.find(r=>r.game===verification.game);assert(selection,'Selected Hard loss required');
assert.equal(analysis.planSha256,verification.planSha256);
const source=analysis.source,plan=read(path.join(source,'plan.json'));
assert.equal(sha(path.join(source,'plan.json')),verification.planSha256);
for(const [name,digest]of Object.entries(plan.codeFiles))assert.equal(sha(path.join(source,'frozen',name)),digest);
const {createRuntime}=require(path.join(source,'frozen/tools/ai/beta_js092/session.cjs')),runtime=createRuntime(plan.current),decisions=[],files=[];
for(const item of verification.positions){
 const input=path.join(replay,item.file);assert.equal(sha(input),item.sha256);
 const capture=JSON.parse(zlib.gunzipSync(fs.readFileSync(input)));
 if(capture.mode!=='hard'||capture.sideInRecordedGame!==selection.side)continue;
 assert.equal(capture.normalizedActorSide,2);assert(Number.isSafeInteger(capture.index));
 const g=runtime.deserialize(JSON.parse(JSON.stringify(capture.state))),m=g.Snapshot();assert.equal(m.currentPlayerId,2);assert(!g.IsFatal()&&!g.IsPending());
 const file=verification.game+'-t'+capture.index+'.json.gz';
 decisions.push({file,round:m.roundNumber,score:[g.Score(1),g.Score(2)],hand:[g.CountLocation(1,8),g.CountLocation(2,8)],passed:m.playerTwo.hasPassed,enemyPassed:m.playerOne.hasPassed});
 files.push({input,file,sha256:item.sha256});
}
assert(decisions.length);fs.mkdirSync(out,{recursive:true});
for(const file of files)fs.copyFileSync(file.input,path.join(out,file.file));
const result={schema:1,kind:'verified-replay-development-only',planSha256:verification.planSha256,commonFingerprint:verification.commonFingerprint,
 sourceVerificationSha256:sha(path.join(replay,'verification.json')),originalSide:selection.side,normalizedActorSide:2,
 records:[{game:verification.game,selected:{key:selection.key},decisions}],notStrengthResult:true,fullStateHindsight:true};
fs.writeFileSync(path.join(out,'replays.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({game:verification.game,key:selection.key,positions:decisions.length}));
