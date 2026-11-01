'use strict';
// Executes authoritative WS actions, rejects incomplete/private-policy fixtures.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),cp=require('child_process');
const {createRuntime}=require('./beta_js092/session.cjs'),p=require('./position_replay094.cjs');
const snapshot=path.resolve(process.argv[2]||''),out=process.argv[3]&&path.resolve(process.argv[3]);
const runtime=createRuntime(snapshot),g=runtime.newSession();
assert(g.InitializeWithPresets(54,54));g.recordVisuals=false;assert(g.FinishMulligan(g.requestId));
// Synthetic stable side-2 case, not a claim of a recorded human match.
g.match.currentPlayerId=2;
const fixture=p.makeFixture(runtime,snapshot,g,'synthetic never-swapped initial Hard position, presets 54/54'),json=v=>JSON.parse(JSON.stringify(v));
let checks=0;function ok(condition){assert(condition);checks++;}function rejects(fn,pattern){assert.throws(fn,pattern);checks++;}
ok(!Object.hasOwn(json(fixture.state),'mem'));
ok(p.digest(p.loadFixture(snapshot,json(fixture)).runtime.serialize(p.loadFixture(snapshot,json(fixture)).game))===fixture.stateSha256);
const actions=[{kind:'pass',side:2}],a=p.replay(snapshot,fixture,actions),b=p.replay(snapshot,json(fixture),actions);
ok(a.afterStateSha256===b.afterStateSha256);ok(a.after.passed[1]);ok(!a.hardChoiceMayDependOnHostTiming);
const direct=p.loadFixture(snapshot,fixture);assert(direct.game.Pass(2));ok(p.digest(direct.runtime.serialize(direct.game))===a.afterStateSha256);
ok(fixture.stateSha256===p.digest(fixture.state));
const hard=p.replay(snapshot,fixture);ok(hard.complete&&!hard.after.pending&&hard.hardChoiceMayDependOnHostTiming);ok(hard.notStrengthResult&&!hard.nativeGameplayVerified&&!hard.historicalRuntimeVerified);
rejects(()=>p.validatePacked({cards:[]}),/Complete packed state/);
const bad=json(fixture);bad.stateSha256='0'.repeat(64);rejects(()=>p.loadFixture(snapshot,bad),/checksum/);
const classic=json(fixture);classic.mode='classic';rejects(()=>p.loadFixture(snapshot,classic),/Only production Hard/);
const other=json(fixture);other.rules.fingerprint='0'.repeat(64);rejects(()=>p.loadFixture(snapshot,other),/identity/);
const missing=json(fixture);delete missing.state.nodes[missing.state.root.r].fields.match;missing.stateSha256=p.digest(missing.state);rejects(()=>p.loadFixture(snapshot,missing),/Incomplete\/noncanonical/);
const rng=json(fixture);delete rng.state.engineRandom;rng.stateSha256=p.digest(rng.state);rejects(()=>p.loadFixture(snapshot,rng),/host RNG/);
const dangling=json(fixture);dangling.state.root.r=dangling.state.nodes.length;dangling.stateSha256=p.digest(dangling.state);rejects(()=>p.loadFixture(snapshot,dangling),/Dangling/);
const unsafe=json(fixture);Object.defineProperty(unsafe.state.nodes[0].fields,'__proto__',{value:1,enumerable:true});unsafe.stateSha256=p.digest(unsafe.state);rejects(()=>p.loadFixture(snapshot,unsafe),/Unsafe/);
const external=json(fixture);external.state.nodes[external.state.root.r].fields.externalPolicyMask=3;external.stateSha256=p.digest(external.state);rejects(()=>p.loadFixture(snapshot,external),/External\/Classic/);
for(const flag of ['aiOpenInfoBench','aiSimulating']){const research=json(fixture);research.state.nodes[research.state.root.r].fields[flag]=true;research.stateSha256=p.digest(research.state);rejects(()=>p.loadFixture(snapshot,research),/Open-info\/simulated/);}
rejects(()=>p.replay(snapshot,fixture,[]),/Nonempty/);rejects(()=>p.replay(snapshot,fixture,[{kind:'pass',side:3}]),/Invalid action side/);rejects(()=>p.replay(snapshot,fixture,[{kind:'pass',side:2,hidden:true}]),/Unexpected action/);rejects(()=>p.replay(snapshot,fixture,[{kind:'play',side:2,card:999999,row:1}]),/rejected/);
rejects(()=>p.makeFixture(runtime,snapshot,g,''),/provenance/);
const report={schema:1,complete:true,checks,fingerprint:fixture.rules.fingerprint,recordedActionStateSha256:a.afterStateSha256,hardCallbacks:hard.callbacks,notStrengthResult:true,nativeGameplayVerified:false};
if(out){
 if(fs.existsSync(out))throw Error('Use a new test output directory');fs.mkdirSync(out,{recursive:true});
 fs.writeFileSync(path.join(out,'source-state.json'),JSON.stringify(fixture.state));fs.writeFileSync(path.join(out,'actions.json'),JSON.stringify(actions));
 const cli=path.join(__dirname,'position_replay094.cjs');
 function run(args,status=0){const result=cp.spawnSync(process.execPath,[cli,...args],{encoding:'utf8'});assert.equal(result.status,status,result.stderr);checks++;return result;}
 const output=path.join(out,'fixture.json');run(['capture',snapshot,path.join(out,'source-state.json'),output,'synthetic CLI never-swapped witness']);
 run(['replay',snapshot,output,path.join(out,'replay-actions.json'),path.join(out,'actions.json')]);
 run(['replay',snapshot,output,path.join(out,'replay-hard.json')]);
 ok(JSON.parse(fs.readFileSync(path.join(out,'replay-actions.json'),'utf8')).afterStateSha256===a.afterStateSha256);
 const before=fs.readFileSync(output);run(['capture',snapshot,path.join(out,'source-state.json'),output,'refuse overwrite'],1);ok(before.equals(fs.readFileSync(output)));
 fs.writeFileSync(path.join(out,'partial-log.json'),JSON.stringify({cards:[],position:{cardCount:0}}));run(['capture',snapshot,path.join(out,'partial-log.json'),path.join(out,'partial-rejected.json'),'incomplete'],1);ok(!fs.existsSync(path.join(out,'partial-rejected.json')));
 report.checks=checks;fs.writeFileSync(path.join(out,'checks.json'),JSON.stringify(report,null,2)+'\n');
}
console.log(JSON.stringify(report));
