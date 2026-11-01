'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const cases=[[113320,113403,3],[113320,113404,-3],[200223,201562,6],[200223,201563,-6],[122211,0,0],[162204,0,3],[200233,0,0],[200132,0,0],[201523,0,0],[113205,0,0],[201644,0,0],[201598,201703,3]];
for(const [id]of cases.filter(x=>x[0]!==201644&&x[0]!==201598))assert(cat.abilities.find(a=>a.templateId===id).nodes.some(n=>n.type==='ResetCardsNode'&&n.sourceTree.children.some(p=>p.tag==='ResetMode'&&p.attributes.V==='1')));
const mandrake=cat.abilities.find(a=>a.templateId===200223);assert(mandrake.nodes.some(n=>n.type==='FilterCardPowerStateNode'&&n.sourceTree.children.some(p=>p.tag==='PowerState'&&p.attributes.V==='1')));
c.testCases=cases;
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
function must(v,n){if(!v)throw Error('fixture: '+n);}
for(const side of [1,2])for(const delta of [-3,0,7])for(const [id,choice,amount]of testCases){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.externalPolicyMask=3;
 const target=add(g,112405,1,0,side);target.ChangeBasePower(12-target.Snapshot().power.basePower,true);target.power.SetCurrentPair(12+delta,7);
 const caster=add(g,id,8,0,side),rec={side,delta,id,choice};records.push(rec);
 try{
 must(g.Play(side,caster.Snapshot().instanceId,2),'play '+id);
 if(choice)must(g.SelectTemplateChoice(g.requestId,choice),'select original branch');
 if(id===201523||id===113205){must(g.CanSelectRow(g.requestId,side,1),'source row offered');must(g.SelectRow(g.requestId,side,1),'row accepted');}
 else if(id===201644&&delta>=0){verify(!g.pendingIds.includes(target.Snapshot().instanceId),'Yoana does not offer an unwounded ally '+side+'/'+delta);continue;}
 else{must(g.pendingIds.includes(target.Snapshot().instanceId),'source card offered');must(g.SelectTarget(g.requestId,target.Snapshot().instanceId),'target accepted');}
 g.FlushEffects();g.FlushDeaths();const s=target.Snapshot();rec.actual=s.power;
 // Dimeritium Bomb: FilterCardPowerState(Boosted) feeds ResetCards(Power); wounded units stay.
 // Yoana: valid targets are wounded allies; ChangePower(Restore) by base-current, then
 // ChangePower(Add) of the same amount on the SAME target (both Targets = SelectedTargets).
 // Bone Talisman heal branch: ChangePower(Restore, 99) then ChangePower(Add, BasePower, var Strengthen=3).
 const expected=id===201598?(delta<0?12:12+delta)+3:id===113205?(delta>0?12:12+delta):id===201644?12-delta:(id===200223&&choice===201562?Math.max(12,12+delta):12)+amount;
 if(id===201644)verify(caster.Snapshot().power.currentPower===6,'Yoana herself is not boosted '+side+'/'+delta);
 verify(s.power.currentPower===expected,'source Reset(Power) '+id+'/'+side+'/'+delta+' expected '+expected+' actual '+s.power.currentPower);
 verify(s.power.basePower===12+amount,'reset preserves instance base before explicit strengthen/weaken '+id);
 verify(s.power.armor===7,'power reset preserves armor '+id);verify(!g.IsFatal(),'reset action resolves');
 }catch(e){rec.error=e.message;failures.push(id+'/'+side+'/'+delta+': '+e.message);}
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result,scope:'Source ResetCards(Power) branches; distinct base/current strength and armor, Mandrake wounded-only positive branch. Witch Hunter uses a non-Mage target; nested tutors and adventure choices are separate.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,cases:report.records.length,failures:report.failures}));if(report.failures.length)process.exitCode=1;
