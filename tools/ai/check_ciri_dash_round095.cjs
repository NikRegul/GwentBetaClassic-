'use strict';
// Beta 112110: AfterRound -> filter SELF Resilient -> FAIL -> strengthen/return.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const graph=cat.abilities.find(a=>a.templateId===112110),node=id=>graph.nodes.find(n=>n.nodeId===id);
assert.equal(node(177).type,'AfterRoundTrigger');assert.equal(node(209).type,'FilterCardTokensNode');
assert.equal(node(209).sourceTree.children.find(x=>x.tag==='Tokens').attributes.V,'1');
assert(graph.connections.some(c=>c.sourcePort.nodeId===195&&c.sourcePort.field==='FlowFail'&&c.destinationPort.nodeId===21));
assert(!graph.connections.some(c=>c.sourcePort.nodeId===195&&c.sourcePort.field==='FlowSuccess'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
for(const side of [1,2])for(const row of [1,2,4])for(const resilient of [false,true])for(const locked of [false,true]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const dash=add(g,112110,row,0,side),base=dash.Snapshot().power.basePower;
 if(resilient)dash.AddTokens(1);if(locked)dash.AddTokens(4);
 const carry=(dash.Snapshot().tokenMask&1)!==0,lock=(dash.Snapshot().tokenMask&4)!==0;
 verify(g.Pass(g.Snapshot().currentPlayerId)&&g.Pass(g.Snapshot().currentPlayerId),'two real passes');
 const s=dash.Snapshot();verify(s.locationMask===(carry||lock?row:16),'AfterRound resilience gate '+side+'/'+row+'/'+resilient+'/'+locked);
 verify(s.power.basePower===base+(carry||lock?0:3),'strengthen only on source FAIL branch');
 verify(!g.IsFatal(),'round resolves');records.push({side,row,resilient,locked,carry,lock,zone:s.locationMask,base:s.power.basePower});
 if(carry){verify(g.BeginNextRound(),'next round starts');verify((dash.Snapshot().locationMask&7)!==0,'resilient Dash remains on board through cleanup');verify((dash.Snapshot().tokenMask&1)===0,'carry consumes resilience');}
}
// Reachable through the actual Adrenaline Rush action, not just a test token.
{
 const g=fixture(1);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const dash=add(g,112110,1,0,1),spell=add(g,113307,8,0,1);
 verify(g.Play(1,spell.Snapshot().instanceId,1),'real Adrenaline Rush deploy');
 if(g.IsPending())verify(g.SelectTarget(g.requestId,dash.Snapshot().instanceId),'real target selection');
 verify((dash.Snapshot().tokenMask&1)!==0,'real spell gives Dash resilience');
 verify(g.Pass(g.Snapshot().currentPlayerId)&&g.Pass(g.Snapshot().currentPlayerId),'real spell then passes');
 verify(dash.Snapshot().locationMask===1,'real spell prevents round-end deck return');
}
globalThis.result={checks,failures,records,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failures:report.failures}));if(report.failures.length)process.exitCode=1;
