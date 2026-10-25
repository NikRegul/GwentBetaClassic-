'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {personality}=require('./beta_js092/profiles.cjs'),{BetaTurnController}=require('./beta_js092/controller.cjs');
const {stepMulligan}=require('./beta_js092/mulligan.cjs');
const stage=path.resolve(process.argv[2]),rules=path.resolve(process.argv[3]),out=path.resolve(process.argv[4]);assert(!fs.existsSync(out),'Fresh output required');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const manifestFile=path.join(rules,'manifest.json'),frozenManifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
for(const [file,digest] of Object.entries(frozenManifest.snapshotFiles))assert.equal(sha(path.join(rules,file)),digest,'Immutable parity input '+file);
const moduleRoot=path.join(__dirname,'beta_js092'),inputFiles=[__filename,manifestFile,...['runtime.js','rules.js','harness.js'].map(n=>path.join(rules,n)),
 ...fs.readdirSync(moduleRoot).filter(n=>n.endsWith('.cjs')).map(n=>path.join(moduleRoot,n)),
 ...fs.readdirSync(path.join(moduleRoot,'data')).filter(n=>n.endsWith('.json')).map(n=>path.join(moduleRoot,'data',n))];
const inputDigests=Object.fromEntries(inputFiles.map(file=>[file,sha(file)]));
const commonSource=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const source=commonSource+(commonSource.includes('class CBetaOriginalNode ')?'':'\n'+fs.readFileSync(path.join(stage,'ws-stage.js'),'utf8'));
const codec=require('./comparison_bridge119.js').split('let active=null')[0].replace(/\brandomState\b/g,'rngState');
const make=new Function('seed','useDeckMapping',source+String.raw`
 Host.strength=4;Host.matchStrength=[4,4];let rngState=seed>>>0||1,stamp=-1500000000;
 Host.random=()=>{rngState^=rngState<<13;rngState>>>=0;rngState^=rngState>>>17;rngState>>>=0;rngState^=rngState<<5;rngState>>>=0;return rngState/4294967296;};
 `+codec+String.raw`
 const rt=new CBetaOriginalRuntime();return {externalPolicyHooks:true,newSession:()=>new CBetaGwentDuelSession(),definition:BetaGwentDuelDefinition,
 cloneSession:g=>new CBetaGwentCloner().CloneSession(g,++stamp),serialize:g=>pack(g,true),
 profile:(f,preset)=>{let p=new CBetaOriginalPersonality();if(!(useDeckMapping?p.InitializeForDeck(preset,f):p.Initialize(f)))throw Error('profile '+preset);return p;},
 mulligan:(g,p)=>{let m=new CBetaOriginalMulligan();m.personality=p;return m.Step(g);},
 controller:(g,p)=>{let c=new CBetaOriginalTurnController();if(!c.Start(g,rt,p))throw Error(c.error);return c;}};`);
const names={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
const root=path.resolve(__dirname,'../..'),ours=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
const original=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/ai/validation093/beta-rosters-audit.json'),'utf8')).eligible;
const mappingArg=process.argv.indexOf('--mapping'),mapping=mappingArg<0?null:JSON.parse(fs.readFileSync(path.resolve(process.argv[mappingArg+1]),'utf8'));
for(const file of [path.join(__dirname,'comparison_bridge119.js'),
 path.join(root,'data/beta924/ai/validation093/final092-rosters.json'),
 path.join(root,'data/beta924/ai/validation093/beta-rosters-audit.json'),
 ...(mapping?[path.resolve(process.argv[mappingArg+1]),path.join(root,'data/beta924/ai/validation093/profile-confirmation-plan.json')]:[])])inputDigests[file]=sha(file);
let namedDecks=null;
if(mapping){
 assert.equal(mapping.validated,true,'Completed source-profile validation required');
 const planPath=path.join(root,'data/beta924/ai/validation093/profile-confirmation-plan.json'),bytes=fs.readFileSync(planPath);
 assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),mapping.confirmation.planSha256,'Mapping schedule provenance');
 namedDecks=JSON.parse(bytes).units;
 assert.equal(new Set(mapping.assignments.map(a=>a.presetId)).size,109,'All ready deck/NPC aliases must be mapped');
}
const expectedProfile=d=>mapping?mapping.assignments.find(a=>a.presetId===d.presetId)?.profile:names[d.faction];
const allSchedules=namedDecks?namedDecks.map((d,i)=>[d,namedDecks[(i+11)%namedDecks.length]]):[...ours.map((d,i)=>[d,ours[(i+11)%ours.length]]),...original.map((d,i)=>[d,ours[(i*7)%ours.length]])];
const limit=process.argv[5]&&!process.argv[5].startsWith('--')?Number(process.argv[5]):allSchedules.length;
assert(Number.isInteger(limit)&&limit>0&&limit<=allSchedules.length,'Valid whole-game count');
const schedules=allSchedules.slice(0,limit);
let checks=0;const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
const report={fingerprint:frozenManifest.fingerprint,inputDigests,sourceSha256:crypto.createHash('sha256').update(source).digest('hex'),scope:'Whole matches: typed cooperative WS original Beta vs direct JS decisions on identical common states. Not strength games or a native-game acceptance.',profileScope:mapping?'Validated per-deck named original profiles':'Five faction Practice profiles',mappingPresets:mapping?.assignments.length||0,total:schedules.length,records:[],complete:false,nativeProcessesAllowed:false,nativeCompiled:false,peakActionsPerCallback:0,peakCallbackMs:0};
const save=()=>fs.writeFileSync(out,JSON.stringify({...report,checks,lastActivity:new Date().toISOString()},null,2)+'\n');save();
try{
 if(mapping){
  const bindingsRuntime=make(924043000,true);
  for(const binding of mapping.assignments){
   const deck=namedDecks.find(d=>d.key===binding.composition);assert(deck,'Known composition');
   eq(bindingsRuntime.profile(deck.faction,binding.presetId).profileName,binding.profile,'Actual InitializeForDeck binding '+binding.presetId);
  }
  report.bindingChecks=mapping.assignments.length;save();
 }
 for(let i=0;i<schedules.length;i++){
  const [left,right]=schedules[i],runtime=make(924043001+i,!!mapping),g=runtime.newSession();g.externalPolicyMask=3;report.current={index:i,phase:'initialize'};save();
  assert(g.InitializeWithDecks(left.templateIds,right.templateIds,left.leader,right.leader,left.presetId,right.presetId));g.recordVisuals=false;
  const a=runtime.cloneSession(g),b=runtime.cloneSession(g),decks=[null,left,right];let turns=0,callbacks=0;
  while(!a.Snapshot().matchWinnerMask){
   assert(turns<400,'Match turn limit');report.current={index:i,turns,phase:a.mulligan?'mulligan':a.waiting?'round':'turn'};save();eq(runtime.serialize(b),runtime.serialize(a),'Whole state before next decision');
   if(a.mulligan){const side=a.RequestDecisionSide(),p=personality(expectedProfile(decks[side]));stepMulligan(a,p);assert(runtime.mulligan(b,runtime.profile(decks[side].faction,decks[side].presetId)));continue;}
   if(a.waiting){assert(a.BeginNextRound());assert(b.BeginNextRound());continue;}
   assert(!a.IsPending());const side=a.match.currentPlayerId,p=personality(expectedProfile(decks[side]));
   let elapsed=0;const js=new BetaTurnController(runtime,p,{now:()=>elapsed}),ws=runtime.controller(b,runtime.profile(decks[side].faction,decks[side].presetId));js.start(a);const turnStart=Date.now();
   let count=0;while(!js.finished){elapsed=Date.now()-turnStart;const r=js.step(),before=Date.now(),s=ws.Step(elapsed);report.peakCallbackMs=Math.max(report.peakCallbackMs,Date.now()-before);
    assert(!ws.failed,ws.error);
    if(r.phase==='pick') {
     const key=n=>[n.decision?.cardId||0,n.decision?.side||0,n.decision?.row||0,n.decision?.index||0],typedKey=n=>[n.cardId,n.decisionSide,n.decisionRow,n.decisionIndex];
     report.lastChosen={source:key(js.chosen),typed:typedKey(ws.chosen),sourceMakerError:js.playmakerError,typedMakerError:ws.playmakerError,forced:js.forceRequested,callbacks:count};
     if(JSON.stringify(report.lastChosen.source)!==JSON.stringify(report.lastChosen.typed)) {
      report.divergence={source:js.root.children.map(n=>[n.id,n.status,n.score,n.revisedScore,...key(n)]),typed:ws.root.children.map(n=>[n.id,n.status,n.score,n.RevisedScore(),...typedKey(n)])};save();
     }
     eq(report.lastChosen.typed,report.lastChosen.source,'Source chosen branch before live replay');
    }
    eq([s.finished,s.mutations,s.phase],[r.finished,r.mutations,r.phase],'Same cooperative controller step');assert(s.mutations<=1);
    report.peakActionsPerCallback=Math.max(report.peakActionsPerCallback,s.mutations);callbacks++;assert(++count<100000,'Controller callback limit');
    if(count%100===0){report.current={index:i,turns,side,phase:s.phase,count,elapsed};save();}}
   eq(ws.finished,true,'Typed controller completed');
   const d=js.chosen.decision;eq([ws.chosen.cardId,ws.chosen.decisionSide,ws.chosen.decisionRow,ws.chosen.decisionIndex],[d?.cardId||0,d?.side||0,d?.row||0,d?.index||0],'Identical chosen source action');
   eq(runtime.serialize(b),runtime.serialize(a),'Exact full state after stored replay');turns++;
  }
  eq(runtime.serialize(b),runtime.serialize(a),'Identical completed match');report.records.push({index:i,left:left.asset||left.presetId,right:right.presetId,leftProfile:expectedProfile(left),rightProfile:expectedProfile(right),turns,callbacks,winner:a.Snapshot().matchWinnerMask,status:'complete'});save();console.log(JSON.stringify(report.records.at(-1)));
 }
 for(const [file,digest] of Object.entries(inputDigests))assert.equal(sha(file),digest,'Parity input changed during run: '+file);
 report.complete=true;save();
}catch(e){report.error=String(e.stack);save();throw e;}
