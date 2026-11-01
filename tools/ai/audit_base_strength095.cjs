'use strict';
// Independent follow-up of every supported BasePower reader. Release sources
// remain frozen: this script executes the same translated WS without modifying it.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const ids=[112104,112105,112213,122318,133301,142303,152106,162303,200031,200088,200534,201644,201656,201817];
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
for(const id of ids)assert(cat.abilities.find(a=>a.templateId===id).nodes.some(n=>n.type==='GetCardPowerNode'&&n.sourceTree.children.some(p=>p.tag==='PowerType'&&p.attributes.V==='1')),id+' source reads BasePower');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
c.testIds=ids;
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
function must(v,n){if(!v)throw Error('fixture: '+n);}
function empty(side){const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.externalPolicyMask=3;return g;}
function choose(g,card){must(g.IsPending(),'request exists for '+card.TemplateId());must(g.pendingIds.includes(card.Snapshot().instanceId),'target offered '+card.TemplateId()+' in '+JSON.stringify(g.pendingIds));must(g.SelectTarget(g.requestId,card.Snapshot().instanceId),'target accepted');}
function resolve(g){let n=0;while(g.IsPending()){
 must(++n<30,'bounded choices');let ok=false;
 if(g.pendingRow||g.pendingLeader||g.pendingRally){for(const s of [1,2])for(const r of [1,2,4])if(!ok&&g.CanSelectRow(g.requestId,s,r))ok=g.SelectRow(g.requestId,s,r);}
 else if(g.pendingChoice){for(const id of [...g.pendingIds])if(!ok)ok=g.SelectTemplateChoice(g.requestId,id);}
 else for(const id of [...g.pendingIds])if(!ok)ok=g.SelectTarget(g.requestId,id);
 if(!ok)ok=g.FinishTarget(g.requestId);must(ok,'resolve remaining request');
}g.FlushEffects();g.FlushDeaths();}
for(const side of [1,2])for(const base of [3,10])for(const delta of [-2,0,7])for(const id of testIds){
 const rec={side,base,delta,id};records.push(rec);
 try{
 const g=empty(side),enemy=add(g,112405,1,0,3-side,50);
 if(id===201817){
  const caster=add(g,id,2,0,side);caster.ChangeBasePower(base-caster.Snapshot().power.basePower,true);caster.power.SetCurrentPair(base+delta,0);caster.ChangeTimer(1,2);
  const enemies=[enemy,add(g,112405,2,0,3-side,50),add(g,112405,4,0,3-side,50)];
  g.EndTurnWithEvents(side);resolve(g);rec.actual=enemies.map(t=>t.Snapshot().power.currentPower);
  verify(rec.actual.every(p=>p===(delta===0?43:50)),'Ihuarraquax equal-to-base end-turn damage '+side+'/'+base+'/'+delta);
  verify(caster.Snapshot().timerValue===(delta===0?0:1),'Ihuarraquax consumes timer only at base');rec.ok=true;continue;
 }
 const caster=add(g,id,8,0,side),before=caster.Snapshot().power.currentPower;
 if(id===112213){caster.ChangeBasePower(base-caster.Snapshot().power.basePower,true);caster.power.SetCurrentPair(base+delta,0);
  must(g.Play(side,caster.Snapshot().instanceId,2),'Beggars King deploy');resolve(g);
  rec.actual=caster.Snapshot().power.basePower;rec.expected=15;verify(rec.actual===15,'Beggars King base cap '+side+'/'+base);rec.ok=true;continue;}
 const targetId=id===200534?200295:id===122318?122315:112405;
 const zone=[112105,152106,200088,200534].includes(id)?16:[201644,122318,112104].includes(id)?1:8;
 const targetSide=[112104,112105].includes(id)?3-side:side;
 const target=add(g,targetId,zone,1,targetSide);
 target.ChangeBasePower(base-target.Snapshot().power.basePower,true);
 const old=base+delta;target.power.SetCurrentPair(old,0);
 if(id===162303)target.SetRevealed(true);
 if(id===142303)add(g,122209,16,0,side);
 const friend=id===133301?add(g,112405,4,0,side,50):null;
 must(g.Play(side,caster.Snapshot().instanceId,2),'deploy '+id);
 if(id===201644&&delta>=0){verify(!g.pendingIds.includes(target.Snapshot().instanceId),'Joanna offers only wounded cards');resolve(g);rec.ok=true;continue;}
 if(id!==200088)choose(g,target);
 if([152106,200031,201656].includes(id))choose(g,enemy);
 if(id===133301)choose(g,friend);
 resolve(g);
 if([152106,200031,201656].includes(id)){rec.actual=enemy.Snapshot().power.currentPower;rec.expected=50-base;}
 else if(id===133301){rec.actual=friend.Snapshot().power.currentPower;rec.expected=50+base;}
 else if(id===201644){rec.actual=target.Snapshot().power.currentPower;rec.expected=Math.max(base,old)+Math.max(0,base-old);}
 else if(id===122318){rec.actual=target.Snapshot().power.currentPower;rec.expected=Math.max(base,old);}
 else{rec.actual=caster.Snapshot().power.currentPower;rec.expected=before+([112104,200088].includes(id)?Math.max(0,delta):base);}
 verify(rec.actual===rec.expected,'BasePower '+id+'/'+side+'/'+base+' expected='+rec.expected+' actual='+rec.actual);
 if([112104,200088].includes(id))verify(target.Snapshot().power.currentPower===Math.min(base,old),'drained boost reset '+id);
 verify(!g.IsFatal(),'no fatal '+id);rec.ok=true;
 }catch(e){rec.error=e.message;failures.push(id+'/'+side+'/'+base+': '+e.message);}
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result,scope:'Base-power formula branch checks after changing current and base strength; fixtures and source graph assertions, not complete nested-effect proof.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks:report.checks,cases:report.records.length,failures:report.failures}));if(report.failures.length)process.exitCode=1;
