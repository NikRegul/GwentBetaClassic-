'use strict';
// CardAbility 122314/487: save GetCardArmor in var256, set target armor to 0,
// then add var256 to the owner's current power. No multiplier in the source.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const assert=require('node:assert/strict'),catalogFile=path.join(__dirname,'../../data/beta924/normalized/catalog.json');
const graph=JSON.parse(fs.readFileSync(catalogFile,'utf8')).abilities.find(a=>a.templateId===122314);
assert(graph&&graph.nid===487);
const node=id=>graph.nodes.find(n=>n.nodeId===id),value=(id,field)=>node(id).sourceTree.children.find(c=>c.tag===field).attributes.V;
assert.equal(node(215).type,'GetCardArmorNode');assert.equal(node(324).attributes.VarId,'256');assert.equal(node(474).attributes.VarId,'256');
assert.equal(value(224,'Operation'),'1');assert.equal(value(224,'Armor'),'0');assert.equal(value(239,'Operation'),'0');
assert(graph.connections.some(c=>c.sourcePort.nodeId===215&&c.destinationPort.nodeId===324&&c.destinationPort.field==='In'));
assert(graph.connections.some(c=>c.sourcePort.nodeId===474&&c.destinationPort.nodeId===239&&c.destinationPort.field==='Power'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];
function verify(value,label){checks++;if(!value)failures.push(label);}
for(const side of [1,2])for(const targetSide of [1,2])for(const armor of [1,5,9,30]){
 const g=fixture(side);for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 const target=add(g,122209,1,0,targetSide,11);target.power.SetCurrentPair(11,armor);
 const cavalry=add(g,122314,8,0,side),before=cavalry.Snapshot().power.currentPower;
 verify(g.Play(side,cavalry.Snapshot().instanceId,2),'legal cavalry deploy '+side+'/'+targetSide+'/'+armor);
 if(g.IsPending())verify(g.SelectTarget(g.requestId,target.Snapshot().instanceId),'explicit legal human target');
 verify(!g.IsPending()&&!g.IsFatal(),'armor conversion resolves');
 verify(target.Snapshot().power.armor===0,'target armor is set to zero');
 verify(target.Snapshot().power.currentPower===11,'armor drain does not damage target power');
 verify(cavalry.Snapshot().power.currentPower===before+armor,'one-to-one saved armor boost '+side+'/'+targetSide+'/'+armor);
 records.push({side,targetSide,armor,expected:before+armor,actual:cavalry.Snapshot().power.currentPower});
}
globalThis.result={checks,failures,records,actualWitcherScript:true,sourceAbility:'CardAbility template122314 NId487, GetCardArmor -> var256 -> ChangeArmor Set0 -> ChangePower Add var256',nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};
report.sourceGraphSha256=crypto.createHash('sha256').update(JSON.stringify(graph)).digest('hex');
report.catalogSha256=crypto.createHash('sha256').update(fs.readFileSync(catalogFile)).digest('hex');
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failures:report.failures,cases:report.records.length}));
if(report.failures.length)process.exitCode=1;
