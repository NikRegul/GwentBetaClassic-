/* Complete offline position witnesses over the existing WS -> JS engine. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),zlib=require('zlib');
const {createRuntime}=require('./beta_js092/session.cjs');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function canonical(v){if(Array.isArray(v))return '['+v.map(canonical).join(',')+']';if(v&&typeof v==='object')return '{'+Object.keys(v).filter(k=>v[k]!==undefined).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';const s=JSON.stringify(v);if(s===undefined)throw Error('Unpacked undefined');return s;}
const digest=v=>sha(canonical(v)),copy=v=>JSON.parse(JSON.stringify(v));
function check(ok,message){if(!ok)throw Error(message);}
function identity(snapshot){
 const folder=path.resolve(snapshot),m=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'),'utf8'));
 check(m.schema===2&&/^[a-f0-9]{64}$/.test(m.fingerprint),'Unsupported rules manifest');
 const snapshotFiles={};for(const name of ['runtime.js','rules.js','harness.js','tunes.json']){snapshotFiles[name]=sha(fs.readFileSync(path.join(folder,name)));check(snapshotFiles[name]===m.snapshotFiles[name],'Frozen snapshot changed: '+name);}
 const toolFiles={};for(const name of ['beta_js092/session.cjs','comparison_bridge119.js','position_replay094.cjs'])toolFiles[name]=sha(fs.readFileSync(path.join(__dirname,name)));
 return {fingerprint:m.fingerprint,snapshotFiles,toolFiles};
}
function validatePacked(state){
 check(state&&Array.isArray(state.nodes)&&state.nodes.length>0,'Complete packed state required; AI_POSITION log rows are insufficient');
 check(Number.isInteger(state.engineRandom)&&state.engineRandom>0&&state.engineRandom<=0xffffffff,'Missing host RNG state');
 function value(v){if(v&&typeof v==='object'){const keys=Object.keys(v);check(keys.length===1&&(keys[0]==='r'||keys[0]==='u'),'Invalid packed value');if(keys[0]==='r')check(Number.isInteger(v.r)&&v.r>=0&&v.r<state.nodes.length,'Dangling state reference');else check(v.u===1,'Invalid undefined marker');}else check(v===null||typeof v==='string'||typeof v==='boolean'||typeof v==='number'&&Number.isFinite(v),'Invalid packed scalar');}
 value(state.root);check(state.root&&Number.isInteger(state.root.r),'Missing session root');check(state.nodes[state.root.r].type==='CBetaGwentDuelSession','Root must be duel session');
 for(const node of state.nodes){check(node&&(['Array','Object'].includes(node.type)||/^[SC]BetaGwent\w+$/.test(node.type)),'Unexpected packed class');check(node.fields&&typeof node.fields==='object'&&!Array.isArray(node.fields),'Missing packed fields');for(const [key,v]of Object.entries(node.fields)){check(!['__proto__','prototype','constructor'].includes(key),'Unsafe packed field');if(node.type==='Array')check(/^(0|[1-9]\d*)$/.test(key)&&Number(key)<1000000,'Invalid packed array index');value(v);}}
 if(state.mem!==undefined){check(state.mem&&typeof state.mem.rev==='boolean'&&Array.isArray(state.mem.slots)&&state.mem.slots.length===2,'Invalid seat memory');check(state.mem.slots.every(a=>Array.isArray(a)&&a.every(Number.isFinite)),'Invalid seat slots');}
}
function restore(runtime,state){validatePacked(state);const game=runtime.deserialize(copy(state));check(digest(runtime.serialize(game))===digest(state),'Incomplete/noncanonical state: defaults or context differ after restore');check(!game.IsFatal(),'Fatal state');check(game.externalPolicyMask===0,'External/Classic controller state is not a Hard fixture');check(!game.aiOpenInfoBench&&!game.aiSimulating,'Open-info/simulated state is not production Hard');return game;}
function makeFixture(runtime,snapshot,game,source){
 check(typeof source==='string'&&source.trim().length>0,'Explicit provenance required');check(runtime.host.strength===4&&runtime.host.matchStrength.every(v=>v===4),'Capture requires Hard host settings');const state=runtime.serialize(game);restore(runtime,state);
 return {schema:1,kind:'beta-complete-position',mode:'hard',information:'production-hard-hidden-information',provenance:{source,historicalRuntimeVerified:false},rules:identity(snapshot),stateSha256:digest(state),state};
}
function loadFixture(snapshot,fixture){
 check(fixture&&fixture.schema===1&&fixture.kind==='beta-complete-position','Unsupported fixture contract');check(fixture.mode==='hard'&&fixture.information==='production-hard-hidden-information','Only production Hard supported; Classic requires its controller');check(typeof fixture.provenance?.source==='string'&&fixture.provenance.source.trim(),'Missing provenance');check(digest(fixture.rules)===digest(identity(snapshot)),'Rules/tool identity differs');check(digest(fixture.state)===fixture.stateSha256,'Fixture checksum differs');const runtime=createRuntime(path.resolve(snapshot));return {runtime,game:restore(runtime,fixture.state)};
}
function view(g){const m=g.Snapshot();return {round:m.roundNumber,current:m.currentPlayerId,winner:m.matchWinnerMask,score:[g.Score(1),g.Score(2)],hand:[g.CountLocation(1,8),g.CountLocation(2,8)],crowns:[m.playerOne.crowns,m.playerTwo.crowns],passed:[m.playerOne.hasPassed,m.playerTwo.hasPassed],pending:!!g.IsPending(),waiting:!!g.IsWaitingRound(),rng:{seed:g.random.InitialSeed(),draws:g.random.DrawCount()}};}
const ACTIONS={play:['Play',['side','card','row']],playBefore:['PlayBefore',['side','card','anchor']],playTarget:['PlayOnTarget',['side','card','target']],playRow:['PlayOnRow',['side','card','targetSide','row']],leader:['UseLeader',['side']],pass:['Pass',['side']],nextRound:['BeginNextRound',[]],target:['SelectTarget',['request','item']],finishTarget:['FinishTarget',['request']],row:['SelectRow',['request','side','row']],template:['SelectTemplateChoice',['request','item']],mulligan:['SelectMulligan',['request','item']],finishMulligan:['FinishMulligan',['request']]};
function recordedAction(g,a){check(a&&Object.hasOwn(ACTIONS,a.kind),'Unknown recorded action');const [method,keys]=ACTIONS[a.kind];check(Object.keys(a).every(k=>k==='kind'||keys.includes(k)),'Unexpected action field');for(const key of keys){check(Number.isSafeInteger(a[key]),'Missing integer action field: '+key);if(key==='side'||key==='targetSide')check([1,2].includes(a[key]),'Invalid action side');if(key==='row')check([1,2,4].includes(a[key]),'Invalid action row');}check(g[method](...keys.map(k=>a[k])),'Recorded action rejected: '+a.kind);check(!g.IsFatal(),'Recorded action caused fatal: '+g.GetMessage());}
function replay(snapshot,fixture,actions=null){
 const {runtime,game}=loadFixture(snapshot,fixture),before=view(game),logs=[];runtime.host.log=s=>logs.push(s);let callbacks=0;
 try{if(actions===null){check(!game.IsPending()&&!game.IsWaitingRound()&&!game.Snapshot().matchWinnerMask&&game.Snapshot().currentPlayerId===2,'Hard decision requires stable side-2 turn');while(!game.AiPreparationStep()){if(++callbacks>20000)throw Error('AI preparation callback limit');}check(game.OpponentStep(),'Hard decision rejected: '+game.GetMessage());check(!game.IsFatal()&&!game.IsPending(),'Hard action incomplete');callbacks++;}else{check(Array.isArray(actions)&&actions.length>0,'Nonempty recorded action list required');for(const a of actions)recordedAction(game,a);}}finally{runtime.host.log=null;}
 const state=runtime.serialize(game);return {schema:1,complete:true,kind:actions===null?'current-hard-decision':'recorded-authoritative-actions',mode:'hard',rules:fixture.rules,fixtureStateSha256:fixture.stateSha256,before,after:view(game),callbacks,logs,afterStateSha256:digest(state),state,notStrengthResult:true,historicalRuntimeVerified:false,nativeGameplayVerified:false,hardChoiceMayDependOnHostTiming:actions===null};
}
function read(file){const b=fs.readFileSync(file);return JSON.parse((file.endsWith('.gz')?zlib.gunzipSync(b):b).toString('utf8'));}
function writeNew(file,data){fs.writeFileSync(file,JSON.stringify(data,null,2)+'\n',{flag:'wx'});}
function main(args){const [command,snapshot,input,output,...rest]=args;check(output,'Usage: position_replay094.cjs capture <rules> <state.json[.gz]> <new-fixture.json> <source-label> | replay <rules> <fixture.json> <new-report.json> [actions.json]');
 if(command==='capture'){check(rest.length===1,'Capture requires one provenance label');const runtime=createRuntime(path.resolve(snapshot)),raw=read(input),game=restore(runtime,raw.state||raw),fixture=makeFixture(runtime,snapshot,game,rest[0]);fixture.provenance.inputSha256=sha(fs.readFileSync(input));writeNew(output,fixture);console.log(JSON.stringify({complete:true,output,stateSha256:fixture.stateSha256,fingerprint:fixture.rules.fingerprint}));}
 else if(command==='replay'){check(rest.length<=1,'Replay accepts at most one action file');const r=replay(snapshot,read(input),rest.length?read(rest[0]):null);writeNew(output,r);console.log(JSON.stringify({complete:true,output,kind:r.kind,after:r.after,afterStateSha256:r.afterStateSha256,notStrengthResult:true}));}else throw Error('Unknown command: '+command);
}
module.exports={identity,validatePacked,restore,makeFixture,loadFixture,replay,recordedAction,digest};
if(require.main===module){try{main(process.argv.slice(2));}catch(e){console.error(e.message);process.exitCode=1;}}
