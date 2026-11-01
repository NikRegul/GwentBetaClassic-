'use strict';
// 152209 graph: halve BASE while in grave -> current power >0 -> move.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const graph=cat.abilities.find(a=>a.templateId===152209),node=id=>graph.nodes.find(n=>n.nodeId===id),v=(id,f)=>node(id).sourceTree.children.find(x=>x.tag===f).attributes.V;
const edge=(a,f,b)=>graph.connections.some(c=>c.sourcePort.nodeId===a&&c.sourcePort.field===f&&c.destinationPort.nodeId===b);
assert.equal(v(5,'Operation'),'3');assert.equal(v(5,'TargetedPower'),'1');assert.equal(v(5,'IgnoreArmor'),'True');
assert.equal(v(265,'Op'),'3');assert.equal(v(265,'B'),'0');assert(edge(5,'FlowOut',271)&&edge(271,'FlowOutTrue',201));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],records=[];function verify(v,n){checks++;if(!v)failures.push(n);}
for(const side of [1,2])for(const base of [1,2,3,4,9])for(const full of [false,true]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const axeman=add(g,201646,1,0,3-side),before=axeman.Snapshot().power.currentPower;
 if(full)for(const row of [1,2,4])for(let i=0;i<9;i++)add(g,112405,row,i,side);
 const mork=add(g,152209,32,0,side);mork.power.SetBasePowerAndArmor(base,0);mork.power.SetCurrentPair(base,0);
 const resurrect=g.NorthResurrect;let moves=0;g.NorthResurrect=function(...args){moves++;return resurrect.apply(this,args);};
 g.monsters.skellige.ReviveMorkvarg(mork,0,-3);g.FlushEffects();g.FlushDeaths();
 const s=mork.Snapshot(),expected=Math.floor(base/2);
 verify(s.power.basePower===expected,'halve even if board has no space '+side+'/'+base+'/'+full);
 verify(expected===0?s.locationMask===512:(s.locationMask&7)!==0?!full:s.locationMask===32,'zero-base inactive Mork banishes; non-placeable positive Mork stays in grave');
 verify(expected>0?full?s.locationMask===32:(s.locationMask&7)!==0:s.locationMask===512,'exact source destination');
 verify(moves===(expected>0?1:0),'no attempted revival at zero current power');
 verify(axeman.Snapshot().power.currentPower===before,'grave weakening does not damage an on-board enemy');
 verify(!g.IsFatal(),'revival resolves');records.push({side,base,full,expected,actual:s.power.basePower,zone:s.locationMask,moves});
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failures:report.failures}));if(report.failures.length)process.exitCode=1;
