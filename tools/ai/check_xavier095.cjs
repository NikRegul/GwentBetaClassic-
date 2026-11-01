'use strict';
// 200080/290: latest other Dwarf -> GetCardDefinition -> template power,
// not the mutable base strength after Strengthen/Weaken.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const graph=cat.abilities.find(a=>a.templateId===200080);assert.equal(graph.nid,290);
const type=id=>graph.nodes.find(n=>n.nodeId===id).type;
assert.equal(type(188),'GetCardDefinitionNode');assert.equal(type(192),'CardDefinitionGetPowerNode');
const edge=(a,b)=>graph.connections.some(c=>c.sourcePort.nodeId===a&&c.destinationPort.nodeId===b);
assert(edge(183,188)&&edge(188,192)&&edge(192,196));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
for(const side of [1,2])for(const delta of [-4,0,7])for(const repeatSelf of [false,true]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const old=add(g,142212,32,0,side);g.monsters.ScoiaHistory(old);
 const last=add(g,142317,1,0,side);g.monsters.ScoiaHistory(last);
 const printed=last.Definition().header.power;last.ChangeBasePower(delta,true);
 const xavier=add(g,200080,8,0,side),before=xavier.Snapshot().power.currentPower;
 if(repeatSelf)g.monsters.ScoiaHistory(xavier);
 verify(g.Play(side,xavier.Snapshot().instanceId,2),'Xavier legal deploy');
 const expected=before+printed,actual=xavier.Snapshot().power.currentPower;
 verify(expected===actual,'template power after base delta '+side+'/'+delta+'/'+repeatSelf+' expected='+expected+' actual='+actual);
 verify(!g.IsFatal()&&!g.IsPending(),'Xavier resolves');records.push({side,delta,repeatSelf,printed,expected,actual});
}
// Beta history selects the turn player, including a card played on the other
// side (for example by an effect playing from the opponent's deck).
for(const side of [1,2])for(const boardSide of [1,2])for(const turnSide of [1,2]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const prior=add(g,142317,1,0,boardSide);g.match.currentPlayerId=turnSide;g.monsters.ScoiaHistory(prior);
 g.match.currentPlayerId=side;const xavier=add(g,200080,8,0,side),before=xavier.Snapshot().power.currentPower;
 verify(g.Play(side,xavier.Snapshot().instanceId,2),'history ownership deploy');
 const expected=before+(turnSide===side?prior.Definition().header.power:0);
 verify(xavier.Snapshot().power.currentPower===expected,'history follows turn '+side+'/'+boardSide+'/'+turnSide);
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failures:report.failures}));if(report.failures.length)process.exitCode=1;
