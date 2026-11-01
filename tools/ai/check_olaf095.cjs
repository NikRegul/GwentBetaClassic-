'use strict';
// Independent source graph 200103/199: played history -> Beast AND not this
// Card.Id -> count <=4 -> damage 10-count*2; >=5 has no damage branch.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto'),assert=require('assert/strict');
const catalogFile=path.join(__dirname,'../../data/beta924/normalized/catalog.json');
const graph=JSON.parse(fs.readFileSync(catalogFile,'utf8')).abilities.find(a=>a.templateId===200103);
const node=id=>graph.nodes.find(n=>n.nodeId===id),val=(id,f)=>node(id).sourceTree.children.find(c=>c.tag===f).attributes.V;
assert.equal(graph.nid,199);assert.equal(node(122).type,'GetMatchingPlayedCardsNode');
assert.equal(val(122,'RoundId'),'-1');assert.equal(val(122,'TurnId'),'-1');
assert.equal(val(62,'Negate'),'True');assert.equal(node(57).type,'GetCardIdNode');
assert.equal(val(144,'B'),'4');assert.equal(val(18,'IgnoreArmor'),'False');
const edge=(a,f,b,g)=>graph.connections.some(c=>c.sourcePort.nodeId===a&&c.sourcePort.field===f&&c.destinationPort.nodeId===b&&c.destinationPort.field===g);
assert(edge(119,'Out',57,'DS')&&edge(57,'DV',62,'CardId'));
assert(edge(139,'DV',175,'A')&&edge(139,'DV',175,'B'));
assert(!graph.connections.some(c=>c.sourcePort.nodeId===144&&c.sourcePort.field==='FlowOutBigger'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];
function verify(v,label){checks++;if(!v)failures.push(label);}
for(const side of [1,2])for(const n of [0,1,2,3,4,5,6])for(const priorSelf of [0,1,2]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const olaf=add(g,200103,8,0,side);
 // History entries represent real Played events, not merely presence on board.
 for(let i=0;i<priorSelf;i++)g.monsters.ScoiaHistory(olaf);
 for(let i=0;i<n;i++){const beast=add(g,152405,32,i,side);g.monsters.ScoiaHistory(beast);}
 const enemy=add(g,152405,32,0,3-side);g.match.currentPlayerId=3-side;g.monsters.ScoiaHistory(enemy);g.match.currentPlayerId=side;
 const before=olaf.Snapshot().power.currentPower;
 verify(g.Play(side,olaf.Snapshot().instanceId,1),'legal Olaf deploy');
 const expected=before-Math.max(0,10-2*n),actual=olaf.Snapshot().power.currentPower;
 verify(actual===expected,'Olaf '+side+' beasts='+n+' priorSelf='+priorSelf+' expected='+expected+' actual='+actual);
 verify(!g.IsFatal()&&!g.IsPending(),'deploy resolves');records.push({side,n,priorSelf,expected,actual});
}
// Another copy has a different Card.Id and must count, across round boundaries.
for(const side of [1,2]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const other=add(g,200103,32,0,side);g.monsters.ScoiaHistory(other);g.match.roundNumber=2;
 const olaf=add(g,200103,8,0,side);verify(g.Play(side,olaf.Snapshot().instanceId,1),'second copy legal');
 verify(olaf.Snapshot().power.currentPower===12,'different Olaf instance counts across rounds');
}
// The beta filter reads OriginalCard's CURRENT category. A transformed beast
// therefore stops counting; a previously played non-beast turned bear counts.
for(const side of [1,2])for(const wasBeast of [false,true])for(const reverse of [false,true]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 const prior=add(g,wasBeast?152405:112101,1,0,side);g.monsters.ScoiaHistory(prior);
 verify(prior.TransformFigurine(wasBeast?200457:152405),'real category-changing transform');
 const olaf=add(g,200103,8,0,side);
 const clone=new CBetaGwentCloner().CloneSession(g,95103+checks,reverse),actor=reverse?3-side:side;
 verify(clone.Play(actor,olaf.Snapshot().instanceId,2),'AI cloned deploy');
 verify(clone.FindCard(olaf.Snapshot().instanceId).Snapshot().power.currentPower===(wasBeast?10:12),'live category / seat-reversed history preserved');
 verify(olaf.Snapshot().power.currentPower===20,'AI simulation does not mutate real Olaf');
}
for(const side of [1,2])for(const armor of [0,3,15]){
 const g=fixture(side),olaf=add(g,200103,8,0,side);olaf.power.SetCurrentPair(20,armor);
 verify(g.Play(side,olaf.Snapshot().instanceId,1),'armored Olaf deploy');
 verify(olaf.Snapshot().power.currentPower===20-Math.max(0,10-armor),'source damage uses armor');
 verify(olaf.Snapshot().power.armor===Math.max(0,armor-10),'armor absorbed once');
}
globalThis.result={checks,failures,records,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result,sourceGraphSha256:crypto.createHash('sha256').update(JSON.stringify(graph)).digest('hex')};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks:report.checks,failures:report.failures,cases:report.records.length}));if(report.failures.length)process.exitCode=1;
