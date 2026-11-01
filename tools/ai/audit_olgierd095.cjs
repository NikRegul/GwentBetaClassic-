'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const a=cat.abilities.find(a=>a.templateId===112207),vars=a.sourceTree.children.find(p=>p.tag==='PersistentVariables');
assert.equal(vars.children.find(p=>p.attributes.Name==='Killed').attributes.V,'False');
assert(a.nodes.some(n=>n.type==='AfterMovedTrigger'&&n.sourceTree.children.some(p=>p.tag==='FromLocation'&&p.attributes.V==='32')));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
for(const side of [1,2])for(const scenario of ['grave','discard','killed','leave-grave','real-discard']){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.externalPolicyMask=3;
 const olgierd=add(g,112207,scenario==='grave'?32:['discard','real-discard'].includes(scenario)?8:2,0,side);
 if(scenario==='real-discard'){
  add(g,112405,16,0,side);const svanrige=add(g,152213,8,1,side);
  verify(g.Play(side,svanrige.Snapshot().instanceId,1),'Svanrige real play');
  verify(g.pendingIds.includes(olgierd.Snapshot().instanceId),'Olgierd is a real discard choice');
  verify(g.SelectTarget(g.requestId,olgierd.Snapshot().instanceId),'Svanrige discards Olgierd');
 }
 if(scenario==='discard')g.NilfDiscard(olgierd);
 if(scenario==='killed'||scenario==='leave-grave'){g.QueueDestroy(olgierd);g.FlushEffects();g.FlushDeaths();verify(olgierd.Snapshot().locationMask===32,'killed reaches grave');}
 if(scenario==='leave-grave'){g.NilfTake(olgierd,side);g.NilfDiscard(olgierd);}
 g.EndTurnWithEvents();g.FlushEffects();g.FlushDeaths();const s=olgierd.Snapshot();
 verify((s.locationMask&7)!==0?scenario==='killed':scenario!=='killed','Olgierd requires Killed since last grave exit '+side+'/'+scenario);
 verify(!g.IsFatal(),'Olgierd resolves');records.push({side,scenario,zone:s.locationMask,flag:olgierd.monsterOnce});
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,cases:report.records.length,failures:report.failures}));if(report.failures.length)process.exitCode=1;
