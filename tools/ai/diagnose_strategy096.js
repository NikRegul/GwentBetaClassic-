// Report resource frontiers for saved states; never executes a move in the game.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto'),zlib=require('zlib');
function load(snapshot){
  const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
  for(const [name,hash] of Object.entries(manifest.snapshotFiles)){
    if(crypto.createHash('sha256').update(fs.readFileSync(path.join(snapshot,name))).digest('hex')!==hash)throw Error('Changed snapshot '+name);
  }
  const context=vm.createContext({console});
  const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n');
  vm.runInContext(code+'\n'+require('./comparison_bridge119.js'),context);
  context.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(snapshot,'tunes.json'),'utf8')));
  context.bridge.setStrength(4);
  return {context,manifest};
}
function diagnose(snapshot,input,output){
  const {context,manifest}=load(snapshot);
  const bytes=fs.readFileSync(input),fixtures=JSON.parse((input.endsWith('.gz')?zlib.gunzipSync(bytes):bytes).toString('utf8'));
  if(!Array.isArray(fixtures.cases))throw Error('Expected {cases:[{name,state}]}');
  const report={fingerprint:manifest.fingerprint,policyEnabled:true,nativeGameplayVerified:false,
    scope:'Abilities, leader and pass resolved by actual rules. Integrated combo reserve uses three unordered own-deck forecasts and bounded public counterplay; not a full match tree.',cases:[]};
  for(const f of fixtures.cases){
    context.bridge.load(f.state);
    context.cap=64;
    const row=vm.runInContext(`(()=>{
      const probe=new CBetaGwentStrategyProbe096();probe.Initialize(active,cap);
      let steps=0;while(!probe.Step()){if(++steps>65)throw Error('Probe stalled');}
      return {before:probe.before,initialResources:probe.initialResources,candidateCount:probe.candidateCount,
        unsupportedCards:probe.unsupportedCards,truncated:probe.truncated,invalidated:probe.invalidated,results:probe.results};
    })()`,context);
    report.cases.push({name:f.name,...JSON.parse(JSON.stringify(row))});
  }
  fs.writeFileSync(output,JSON.stringify(report,null,2));
  console.log(JSON.stringify({cases:report.cases.length,output,policyEnabled:true}));
}
if(require.main===module){
  if(process.argv.length!==5)throw Error('Usage: node diagnose_strategy096.js SNAPSHOT FIXTURES.json[.gz] REPORT.json');
  diagnose(path.resolve(process.argv[2]),path.resolve(process.argv[3]),path.resolve(process.argv[4]));
}
module.exports={load,diagnose};
