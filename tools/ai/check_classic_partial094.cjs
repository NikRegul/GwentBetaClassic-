// Real stopped-search fixtures: safe strategy selection and JS/WS live parity.
'use strict';
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto');
const snapshot=path.resolve(process.argv[2]),output=process.argv[3];
const completeTrees=process.argv.includes('--complete-trees');
const modules=path.resolve(process.argv[4]||path.join(__dirname,'beta_js092'));
const {BetaTurnController}=require(path.join(modules,'controller.cjs'));
const {BetaPlayMaker}=require(path.join(modules,'playmaker.cjs'));
const {personality}=require(path.join(modules,'profiles.cjs'));
const {chooseBestCardForPersonality}=require(path.join(modules,'core.cjs'));
const {Status}=require(path.join(modules,'search.cjs'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
for(const [name,digest] of Object.entries(manifest.snapshotFiles))if(sha(path.join(snapshot,name))!==digest)throw Error('Frozen input changed '+name);
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n');
const codec=require('./comparison_bridge119.js').split('let active=null')[0].replace(/\brandomState\b/g,'rngState');
const make=new Function('tunes',source+String.raw`
 Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[tunes,tunes];Host.seatIndex=1;
 let rngState=1,stamp=-1900000000;
 Host.random=()=>{rngState^=rngState<<13;rngState>>>=0;rngState^=rngState>>>17;rngState>>>=0;rngState^=rngState<<5;rngState>>>=0;return rngState/4294967296;};
 `+codec+String.raw`
 const typedRuntime=new CBetaOriginalRuntime();
 return {externalPolicyHooks:true,host:Host,newSession:()=>new CBetaGwentDuelSession(),
  cloneSession:g=>new CBetaGwentCloner().CloneSession(g,++stamp),serialize:g=>pack(g,true),deserialize:unpack,
  typed:g=>{let p=new CBetaOriginalPersonality();if(!p.Initialize(4))throw Error('Profile');
   let c=new CBetaOriginalTurnController();if(!c.Start(g,typedRuntime,p))throw Error(c.error);return c;},
  invalidNode:()=>new CBetaOriginalNode(),maker:()=>new CBetaOriginalPlayMaker()};
 `);
const fixtures=[1,2].map(i=>JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures',`classic-partial-search094-0${i}.json.gz`)))));
let checks=0,peakMutations=0;const failures=[],records=[];
function check(value,name){checks++;if(!value)failures.push(name);}
const tuple=n=>[n.decision?.cardId||0,n.decision?.side||0,n.decision?.row||0,n.decision?.index||0];
const typedTuple=n=>[n.cardId,n.decisionSide,n.decisionRow,n.decisionIndex];
const liveSignature=g=>JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId});
function copyRoot(root,filter){const copy=Object.assign(Object.create(Object.getPrototypeOf(root)),root);copy.children=root.children.filter(filter).map(n=>Object.assign(Object.create(Object.getPrototypeOf(n)),n));return copy;}
for(const [index,f]of fixtures.entries())for(const budget of (completeTrees?[1,8,32,256,100000]:[1,8,32,256])){
 const rt=make(JSON.parse(fs.readFileSync(path.join(snapshot,'tunes.json'),'utf8'))),g=rt.deserialize(f.state),h=rt.deserialize(f.state);
 const p=personality(f.view.profile);let ticks=0,oracle=null,incomplete=0,valid=0;
 const js=new BetaTurnController(rt,p,{now:()=>ticks>=budget?1000000:0});js.start(g);const ws=rt.typed(h);
 const choose=js.choose;js.choose=function(){
  const root=copyRoot(this.root,n=>n.status===Status.OK&&n.state);
  incomplete=this.root.children.filter(n=>n.status!==Status.OK||!n.state).length;valid=root.children.length;
  new BetaPlayMaker().apply(root,p);oracle=chooseBestCardForPersonality(root.children);choose.call(this);
 };
 let error=null,steps=0,pick=null;
 try{while(!js.finished){
  if(ticks>150000)throw Error('Callback limit');
  const elapsed=ticks>=budget?1000000:0,before=liveSignature(g);
  const a=js.step(),b=ws.Step(elapsed);peakMutations=Math.max(peakMutations,a.mutations,b.mutations);
  check(!ws.failed,'typed controller remains valid');
  check(JSON.stringify([a.finished,a.phase,a.mutations])===JSON.stringify([b.finished,b.phase,b.mutations]),'same cooperative step');
  check(a.mutations<=1&&b.mutations<=1,'at most one battle action per callback');
  if(a.phase==='search'||a.phase==='pick')check(liveSignature(g)===before,'search/strategy preserves live state');
  if(a.phase==='pick'){
   check(!js.playmakerError&&!ws.playmakerError,'incomplete candidates do not abort PlayMaker');
   check(JSON.stringify(tuple(js.chosen))===JSON.stringify(typedTuple(ws.chosen)),'same selected JS/WS branch');
   check(JSON.stringify(tuple(js.chosen))===JSON.stringify(tuple(oracle)),'original strategy on eligible nodes is reference');
   pick=tuple(js.chosen);
   if(index===0&&budget>=8)check(pick[0]===1,'available non-detrimental Yennefer play is retained instead of pass');
  }
  ticks++;steps++;
 }}catch(e){error=String(e.stack);check(false,'execution '+index+'/'+budget+': '+e.message);}
 check(JSON.stringify(rt.serialize(g))===JSON.stringify(rt.serialize(h)),'exact full state after live replay');
 if(index===0&&budget===100000)check(js.search.finishReason==='depth-limit'&&incomplete===0,'complete-tree control explores all root candidates');
 // The fix must not turn an actually invalid completed state into a silent value.
 const invalid=rt.invalidNode(),maker=rt.maker();maker.OriginalDiff(invalid);check(maker.failed,'typed invalid-state diagnostic retained');
 let throws=false;try{new BetaPlayMaker().originalDiff({state:null});}catch{throws=true;}check(throws,'JS invalid-state diagnostic retained');
 records.push({index,sourceGame:f.view.sourceGame,side:f.view.side,budget,steps,incomplete,valid,finishReason:js.search.finishReason,playmakerError:js.playmakerError,typedPlaymakerError:ws.playmakerError,selected:pick,error});
 console.log(JSON.stringify(records.at(-1)));
}
const report={fingerprint:manifest.fingerprint,checks,failures,peakMutations,records,completeTreeControls:completeTrees,
 scope:'Exact historical game prefixes, deterministic research cutoffs; original per-turn search trees/budgets were not recorded. No whole-match strength claim.',modules,actualWitcherScript:true,nativeGameplayVerified:false};
if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures:failures.length,peakMutations,cases:records.length}));if(failures.length)process.exitCode=1;
