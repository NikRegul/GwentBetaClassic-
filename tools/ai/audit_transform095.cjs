'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const ids=[132101,152107,152301,200053,201625];
for(const id of ids)assert.equal(cat.abilities.find(a=>a.templateId===id).nodes.find(n=>n.type==='TransformCardsNode').sourceTree.children.find(p=>p.tag==='ResetMode').attributes.V,'255');
const knight=cat.abilities.find(a=>a.templateId===201625);assert(knight.nodes.some(n=>n.type==='ResetCardsNode'&&n.sourceTree.children.some(p=>p.tag==='ResetMode'&&p.attributes.V==='255')));
c.original=Object.fromEntries(cat.templates.map(t=>[t.templateId,{power:t.fields.Power,armor:t.fields.Armor,timer:t.fields.InitialTimer,tokens:t.fields.Tokens,tier:t.fields.Tier}]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const records=[],failures=[];function verify(v,n){checks++;if(!v)failures.push(n);}
function must(v,n){if(!v)throw Error('fixture: '+n);}
function empty(side){const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.externalPolicyMask=3;return g;}
function checkReset(t,expected,old,tag){const s=t.Snapshot(),o=original[expected];
 verify(t.TemplateId()===expected,tag+' definition');verify(s.instanceId===old.instanceId&&s.ownerId===old.ownerId&&s.controllerId===old.controllerId&&s.positionPlayerId===old.positionPlayerId,tag+' identity and side');
 verify(s.power.basePower===o.power,tag+' template base');verify(s.power.currentPower===o.power,tag+' template current');
 verify(s.power.armor===o.armor,tag+' template armor');verify(s.tokenMask===(o.tokens&1792),tag+' reset tokens');verify(s.timerValue===o.timer,tag+' reset timer');
}
for(const side of [1,2])for(const id of [152107,200053,201625])for(const same of [false,true]){
 const g=empty(side),targetId=id===201625?(same?201625:152301):112405;
 const target=add(g,targetId,1,0,id===201625?side:3-side);
 target.ChangeBasePower(4,true);target.power.SetCurrentPair(target.Snapshot().power.basePower-2,7);target.AddTokens(4);target.ChangeTimer(3,2);
 const old=target.Snapshot(),caster=add(g,id,8,0,side),tag=id+'/'+side+'/'+same;
 try{must(g.Play(side,caster.Snapshot().instanceId,2),'play '+tag);must(g.pendingIds.includes(old.instanceId),'target offered '+tag);must(g.SelectTarget(g.requestId,old.instanceId),'select '+tag);g.FlushEffects();g.FlushDeaths();
 checkReset(target,id===201625?201625:200307,old,tag);verify(!g.IsFatal()&&!g.IsPending(),tag+' resolves');records.push({id,side,same,actual:target.Snapshot()});
 }catch(e){failures.push(tag+': '+e.message);records.push({id,side,same,error:e.message});}
}
for(const side of [1,2])for(const armor of [0,3])for(const locked of [false,true]){
 const g=empty(side),target=add(g,152301,1,0,side);if(locked)target.AddTokens(4);target.power.SetCurrentPair(6,armor);
 const old=target.Snapshot();g.MonsterPower(target,target,-1);g.FlushEffects();g.FlushDeaths();const expected=locked||armor?152301:152405;
 verify(target.TemplateId()===expected,'Berserker change-power trigger '+side+'/'+armor+'/'+locked);
 if(expected===152405)checkReset(target,expected,old,'Berserker transform');records.push({id:152301,side,armor,locked,result:target.TemplateId()});
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result,scope:'All-reset transform branches for Coral, Compression, Cursed Knight and damaged Berserker; Draug population/placement is separate.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,cases:report.records.length,failures:report.failures}));if(report.failures.length)process.exitCode=1;
