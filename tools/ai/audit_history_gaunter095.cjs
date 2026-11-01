'use strict';
// Follow-up source checks; standalone while the release inputs stay frozen.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const gaunter=cat.abilities.find(a=>a.templateId===132215),yen=cat.abilities.find(a=>a.templateId===201601);
for(const id of [224,387,641])assert.equal(gaunter.nodes.find(n=>n.nodeId===id).sourceTree.children.find(n=>n.tag==='B').attributes.V,'6');
assert.equal(gaunter.nodes.find(n=>n.nodeId===574).type,'CardDefinitionGetPowerNode');
assert.equal(yen.nodes.find(n=>n.nodeId===313).sourceTree.children.find(n=>n.tag==='Tier').attributes.V,'6');
assert.equal(yen.nodes.find(n=>n.nodeId===322).sourceTree.children.find(n=>n.tag==='I').attributes.V,'0');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
c.original=Object.fromEntries(cat.templates.map(t=>[t.templateId,{power:t.fields.Power,tier:t.fields.Tier,spell:(BigInt(t.categoryWords[0].decimal)&1048576n)!==0n}]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],gaunterCases=[],yenCases=[];function verify(v,n){checks++;if(!v)failures.push(n);}
function empty(side){const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.externalPolicyMask=3;return g;}
for(const side of [1,2])for(const guess of [200176,201770,200175])for(let seed=1;seed<=24;seed++){
 const g=empty(side);g.random.Initialize(9527000+seed);const caster=add(g,132215,8,0,side);
 verify(g.Play(side,caster.Snapshot().instanceId,1),'Gaunter legal play');
 verify(g.pendingChoice&&g.pendingIds.includes(guess),'three original guesses');
 verify(g.SelectTemplateChoice(g.requestId,guess),'choose guess');
 verify(g.pendingChoice&&g.pendingIds.length===1,'one original random definition is shown');
 const shown=g.pendingIds[0],printed=original[shown].power;
 const correct=guess===200176?printed<6:guess===201770?printed===6:printed>6;
 const before=new Set(g.live.map(x=>x.Snapshot().instanceId));
 verify(g.SelectTemplateChoice(g.requestId,shown),'acknowledge displayed card');
 const spawned=g.live.filter(x=>!before.has(x.Snapshot().instanceId)&&x.TemplateId()===shown);
 verify((spawned.length>0)===correct,'source template-power threshold '+side+'/'+guess+'/'+seed+'/'+printed);
 verify(!g.IsFatal(),'Gaunter branch is not fatal');gaunterCases.push({side,guess,seed,shown,printed,correct,created:spawned.length>0});
}
function turn(g,side){g.match.currentPlayerId=side;g.match.turnActive=g.match.roundActive=true;g.waiting=false;
 for(const p of [g.match.playerOne,g.match.playerTwo]){p.hasPassed=false;p.hasMadeInitialMoveForCurrentTurn=false;}}
function resolve(g){let steps=0;while(g.IsPending()){
 if(++steps>30)throw Error('request bound');let ok=false;
 if(g.pendingRow||g.pendingLeader||g.pendingRally){for(const side of [1,2])for(const row of [1,2,4])if(!ok&&g.CanSelectRow(g.requestId,side,row))ok=g.SelectRow(g.requestId,side,row);}
 else if(g.pendingChoice){for(const id of [...g.pendingIds])if(!ok)ok=g.SelectTemplateChoice(g.requestId,id);}
 else for(const id of [...g.pendingIds])if(!ok)ok=g.SelectTarget(g.requestId,id);
 if(!ok)ok=g.FinishTarget(g.requestId);if(!ok)throw Error('unresolved request');
}g.FlushEffects();g.FlushDeaths();}
const sequences=[[],[[0,113301]],[[0,113301],[0,113204]],[[0,113204],[1,113301]],[[0,113204],[0,113319]],[[0,113204],[0,113101]]];
for(const side of [1,2])for(let k=0;k<sequences.length;k++){
 const g=empty(side);for(const s of [1,2])add(g,112405,1,0,s,50);let expected=0;
 for(const [other,id]of sequences[k]){
  const actor=other?3-side:side;turn(g,actor);const card=add(g,id,8,g.CountLocation(actor,8),actor);
  verify(g.Play(actor,card.Snapshot().instanceId,1),'history spell accepted '+id);resolve(g);
  if(actor===side&&original[id].spell&&(original[id].tier&6)!==0)expected=id;
  verify(!g.IsFatal(),'history play resolves');
 }
 turn(g,side);g.match.roundNumber=2;
 verify(g.NilfLastSpell(side)===expected,'last eligible own spell persists across round index');
 const caster=add(g,201601,8,g.CountLocation(side,8),side),before=new Set(g.live.map(x=>x.Snapshot().instanceId));
 verify(g.Play(side,caster.Snapshot().instanceId,2),'Yennefer legal play');
 const created=g.live.filter(x=>!before.has(x.Snapshot().instanceId));
 verify(expected?created.some(x=>x.TemplateId()===expected):created.length===0,'copy latest bronze/silver own Spell '+side+'/'+k);
 verify(!g.IsFatal(),'Yennefer branch not fatal');yenCases.push({side,sequence:sequences[k],expected,created:created.map(x=>x.TemplateId())});
}
globalThis.result={checks,failures,gaunterCases,yenCases,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result,scope:'Gaunter printed-power branches over sampled random outcomes; Yennefer completed-play history, other player, tier/category and round persistence. Not a proof of all nested effects.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failures:report.failures,gaunterCases:report.gaunterCases.length,yenCases:report.yenCases.length}));if(report.failures.length)process.exitCode=1;
