'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const cat=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
const graph=cat.abilities.find(a=>a.templateId===132101),nodes=graph.nodes;
assert(nodes.some(n=>n.type==='GetCardsNode'&&n.sourceTree.children.some(p=>p.tag==='LocationId'&&p.attributes.V==='32')));
assert(nodes.some(n=>n.type==='IntMinusNode'&&n.sourceTree.children.some(p=>p.tag==='A'&&p.attributes.V==='8')));
assert.equal(nodes.find(n=>n.type==='TransformCardsNode').sourceTree.children.find(p=>p.tag==='ResetMode').attributes.V,'255');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const target=cat.templates.find(t=>t.templateId===200457);c.expected={power:target.fields.Power,armor:target.fields.Armor,tokens:target.fields.Tokens&1792,timer:target.fields.InitialTimer};
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],records=[];function verify(v,n){checks++;if(!v)failures.push(n);}
for(const side of [1,2])for(const row of [1,2,4])for(const occupied of [0,4,8])for(const count of [0,1,5,12]){
 const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.externalPolicyMask=3;g.random.Initialize(9527111);
 for(let i=0;i<occupied;i++)add(g,112405,row,i,side);
 const graves=[];for(let i=0;i<count;i++){const t=add(g,112405,32,i,side);t.ChangeBasePower(5,true);t.power.SetCurrentPair(19,9);t.AddTokens(4);graves.push({card:t,before:t.Snapshot()});}
 const special=add(g,113301,32,count,side),enemy=add(g,112405,32,0,3-side),caster=add(g,132101,8,0,side);
 verify(g.Play(side,caster.Snapshot().instanceId,row),'Draug deploy');verify(!g.IsFatal()&&!g.IsPending(),'Draug completes');
 const raised=graves.filter(t=>(t.card.Snapshot().locationMask&7)!==0),number=Math.min(count,8-occupied);
 verify(raised.length===number,'source capacity '+side+'/'+row+'/'+occupied+'/'+count);
 verify(g.CountLocation(side,row)===occupied+1+number,'only the Draug row fills');
 for(const {card,before}of graves){const s=card.Snapshot();
  verify(s.instanceId===before.instanceId&&s.ownerId===before.ownerId,'resurrect existing instance');
  if((s.locationMask&7)!==0){verify(card.TemplateId()===200457&&s.locationMask===row,'Draugir in caster row');
   verify(s.power.basePower===expected.power&&s.power.currentPower===expected.power&&s.power.armor===expected.armor,'transform resets power and armor');
   verify(s.tokenMask===expected.tokens&&s.timerValue===expected.timer,'transform resets lock and timer');}
  else verify(s.locationMask===32&&card.TemplateId()===112405&&s.power.currentPower===before.power.currentPower&&s.tokenMask===before.tokenMask,'unselected grave instance unchanged');
 }
 verify(special.Snapshot().locationMask===32&&enemy.Snapshot().locationMask===32,'specials and enemy graves excluded');
 records.push({side,row,occupied,count,raised:raised.length});
}
globalThis.result={checks,records,failures,actualWitcherScript:true,nativeGameplayVerified:false};
`,c,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...c.result,scope:'Draug source population, row capacity, all-reset and identity. Exact random stream correspondence and nested external movement triggers are not proven.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,cases:report.records.length,failures:report.failures}));if(report.failures.length)process.exitCode=1;
