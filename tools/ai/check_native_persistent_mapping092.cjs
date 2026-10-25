'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {inspectNativeModel,fingerprint}=require('./native_session_import092.cjs');
const {draft,reports}=require('./native_bridge_paths092.cjs');
const source=JSON.parse(fs.readFileSync(path.join(draft,'native-persistent-audit.json'),'utf8'));
let models=0,guards=0;
for(const c of source.cases)for(const actor of [1,2]){
 const before=JSON.stringify(c.state),configs=[c.config,c.config],options={actor,memory:{}};
 const model=inspectNativeModel(c.state,configs,options);assert.equal(JSON.stringify(c.state),before);
 const mapped=model.persistentMappings.find(p=>p.id===c.card.id);assert(mapped);
 assert.equal(mapped.variable,c.card.persistent[0].id);assert.equal(mapped.inactive,true);
 if(c.card.template===112207)assert.equal(mapped.monsterOnce,0);
 for(const mutate of [v=>{v.id++},v=>{v.name='unknown'},v=>{v.type='GwentGameplay.IntVar'},
   v=>{v.storedValue=true},v=>{v.dynamicGetter=true},v=>{v.sourceVariable=1},v=>{v.encoding='unknown'}]){
  const bad=JSON.parse(before);mutate(bad.cards.find(x=>x.id===c.card.id).persistent[0]);
  assert.throws(()=>inspectNativeModel(bad,configs,options),/Unmapped persistent/);guards++;
 }
 models++;
}
assert.equal(models,8);
const report={schema:1,complete:true,models,guards,fingerprint,fullMatchReady:false,
 scope:'Observed inactive Ciri354/Olgierd348 flags only, both actor orientations; active/unknown variables explicitly rejected. Not complete ability mapping.'};
fs.writeFileSync(path.join(reports,'native-persistent-mapping-smoke.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
