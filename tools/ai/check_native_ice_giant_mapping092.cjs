/* Inactive original Counter102 -> production WS one-shot flag. Active/unknown
 * values remain unsupported. Captured source models and RNG must stay intact. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {compile,inspectNativeModel,fingerprint}=require('./native_session_import092.cjs');
const {draft,reports}=require('./native_bridge_paths092.cjs');
const fixtures=JSON.parse(fs.readFileSync(path.join(draft,'native-ice-troll-abort-fixtures.json'),'utf8')).fixtures;
const probe=compile(String.raw`
const {g}=importOriginalSession(native,configs,options.actor,{memory:{},diagnosticAnalysis:true});
const source=g.FindCard(options.card),before=JSON.stringify(source.Snapshot()),randomBefore=JSON.stringify(g.random);
if(source.monsterOnce!==0)throw Error('Exhausted native counter not mapped');
g.monsters.FrostContact(source);g.monsters.FrostContact(source);
if(JSON.stringify(source.Snapshot())!==before||JSON.stringify(g.random)!==randomBefore||source.monsterOnce!==0)
 throw Error('Exhausted Ice Giant gained another frost boost');
return {power:source.Snapshot().power.currentPower,once:source.monsterOnce};
`);
let models=0,guards=0,contactChecks=0;
for(const f of fixtures)for(const card of f.beforePlay.cards.filter(c=>c.template===132212&&c.persistent?.length))for(const actor of [1,2]){
 const native=f.beforePlay,configs=[f.config,f.config],before=JSON.stringify(native),opts={actor,memory:{},diagnosticAnalysis:true};
 const mapped=inspectNativeModel(native,configs,opts).persistentMappings.find(c=>c.id===card.id);
 assert(mapped);assert.equal(mapped.variable,102);assert.equal(mapped.monsterOnce,0);
 assert.equal(probe(native,configs,{actor,card:card.id}).power,card.power);contactChecks+=2;
 assert.equal(JSON.stringify(native),before);
 for(const mutate of [v=>{v.id=103},v=>{v.name='Unknown'},v=>{v.type='GwentGameplay.BoolVar'},v=>{v.storedValue=1},
  v=>{v.storedValue=false},v=>{v.storedValue=-1},v=>{v.dynamicGetter=true},v=>{v.sourceVariable=1},v=>{v.encoding='unknown'}]){
  const bad=JSON.parse(before);mutate(bad.cards.find(c=>c.id===card.id).persistent[0]);
  assert.throws(()=>inspectNativeModel(bad,configs,opts),/Unmapped persistent/);guards++;
 }
 const named=JSON.parse(before);named.cards.find(c=>c.id===card.id).persistent[0].name='Counter';
 assert.equal(inspectNativeModel(named,configs,opts).persistentMappings.find(c=>c.id===card.id).monsterOnce,0);guards++;
 models++;
}
assert.equal(models,4);
const report={schema:1,complete:true,models,guards,contactChecks,fingerprint,fullMatchReady:false,notStrengthResult:true,
 scope:'Two captured exhausted Ice Giants, both actor orientations, original named/nameless clone contract; production FrostContact cannot spend another charge. All active or unknown values rejected.'};
fs.writeFileSync(path.join(reports,'native-ice-giant-mapping-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
