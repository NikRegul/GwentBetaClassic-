/* Original immutable/unused declarations are not mutable turn counters.
 * Validate exact XML contracts plus full captured imports in both seats,
 * including spent CardData.Timer and the entire RNG checkpoint. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {inspectNativeModel,compile,fingerprint}=require('./native_session_import092.cjs');
const {draft,reports}=require('./native_bridge_paths092.cjs');
const contracts={132201:{id:345,value:4,reads:1,semantics:'immutable-timer-config'},
 200040:{id:37,value:2,reads:2,semantics:'immutable-timer-config'},
 200177:{id:184,value:4,reads:0,semantics:'unused-timer-declaration'},
 200022:{id:578,value:{premium:false,template:0},reads:0,semantics:'unused-declaration'},
 201601:{id:232,value:{premium:false,template:0},reads:0,semantics:'unused-declaration'},
 201776:{id:72,value:false,reads:0,semantics:'unused-declaration'}};
const original=JSON.parse(fs.readFileSync(path.join(draft,'native-persistent-contracts-original.json'),'utf8'));
const definitions=compile('return [132201,200040,200177].map(id=>({id,timer:BetaGwentDuelDefinition(id).initialTimer}));')(null,null);
for(const [template,contract]of Object.entries(contracts)){
 const o=original.templates.find(t=>t.template===Number(template));assert(o);assert.equal(o.abilities.length,1);
 const a=o.abilities[0];assert.equal(a.variables.length,1);assert.equal(a.variables[0].Id,String(contract.id));
 assert.equal(a.accesses.filter(n=>n.node.Type==='SetVarNode').length,0,'Original writes supposedly immutable declaration');
 assert.equal(a.accesses.filter(n=>n.node.Type==='GetVarNode').length,contract.reads);
 assert(!new RegExp(`(?:SrcId|DstId)="${contract.id}"`).test(a.xml),'Persistent declaration directly connected');
 if(typeof contract.value==='number'){
  assert.equal(Number(a.variables[0].V),contract.value);
  assert.equal(definitions.find(d=>d.id===Number(template)).timer,contract.value);
 }else if(typeof contract.value==='boolean')assert.equal(a.variables[0].V,'False');
}
const audit=JSON.parse(fs.readFileSync(path.join(draft,'native-persistent-audit-final092.json'),'utf8'));
const timerFixtures=JSON.parse(fs.readFileSync(path.join(draft,'native-static-timer-fixtures.json'),'utf8'));
let models=0,guards=0,cardsCompared=0,rngWordsCompared=0,skipped=0;
const covered=new Set(),spentTimers=new Set(),details=[];
for(const c of [...audit.cases,...timerFixtures.cases]){
 const contract=contracts[c.card.template];if(!contract)continue;
 const native=c.state,configs=[c.config,c.config],before=JSON.stringify(native);
 for(const actor of [1,2]){
  let model;
  try{model=inspectNativeModel(native,configs,{actor,memory:{}});}
  catch(e){if(e.message==='Unmapped persistent ability state'){skipped++;continue;}throw e;}
  assert.equal(JSON.stringify(native),before,'Import mutated original model');
  const mapping=model.persistentMappings.find(m=>m.id===c.card.id);
  assert(mapping);assert.equal(mapping.semantics,contract.semantics);assert.equal(mapping.timer,c.card.timer);
  if(typeof contract.value==='number'&&c.card.timer!==contract.value)spentTimers.add(c.card.template);
  for(const card of native.cards){const m=model.cards.find(x=>x.id===card.id);assert(m);
   assert.equal(m.template,card.template);assert.equal(m.side,card.position.side);assert.equal(m.zone,card.position.zone);
   assert.equal(m.index,card.position.index);assert.equal(m.power,card.power);assert.equal(m.armor,card.armor);
   assert.equal(m.timer,card.timer);assert.equal(m.tokens,card.tokens);cardsCompared++;
  }
  const {encoding,...rng}=native.random;assert.deepEqual(model.random,rng);rngWordsCompared+=rng.words.length;
  const mutators=[v=>{v.id++},v=>{v.name='unmapped'},v=>{v.type='GwentGameplay.UnknownVar'},
   v=>{v.dynamicGetter=true},v=>{v.sourceVariable=1},v=>{v.encoding='unknown'},
   v=>{v.storedValue=typeof contract.value==='number'?contract.value+1:typeof contract.value==='boolean'?true:{premium:false,template:112101}}];
  if(typeof contract.value==='object')mutators.push(v=>{v.storedValue={premium:true,template:0}},v=>{v.storedValue={premium:false,template:0,extra:1}});
  for(const mutate of mutators){
   const bad=JSON.parse(before);mutate(bad.cards.find(x=>x.id===c.card.id).persistent[0]);
   assert.throws(()=>inspectNativeModel(bad,configs,{actor,memory:{}}),/Unmapped persistent/);guards++;
  }
  covered.add(c.card.template);models++;details.push({template:c.card.template,deck:c.deck,sequence:c.sequence,actor,timer:c.card.timer});
 }
}
assert.equal(covered.size,6);assert(spentTimers.has(200040)&&spentTimers.has(200177));
const report={schema:1,complete:true,fingerprint,models,guards,cardsCompared,rngWordsCompared,
 covered:[...covered],spentTimers:[...spentTimers],skippedDueToOtherUnmappedPersistent:skipped,details,
 fullMatchReady:false,notStrengthResult:true,scope:'Six exact immutable/unused original XML declarations. Mutable timers are imported independently without resetting their remaining charge. Original future-graph structure has no writes; imports/guards do not prove complete rule or policy parity.'};
fs.writeFileSync(path.join(reports,'native-static-persistent-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,details:undefined}));
