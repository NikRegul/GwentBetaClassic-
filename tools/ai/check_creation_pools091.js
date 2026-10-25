// Execute both creation paths, checking their choices against the original Beta graphs.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
function ids(node){return [...(Number(node.attributes?.TemplateId)>0?[Number(node.attributes.TemplateId)]:[]),...(node.children||[]).flatMap(ids)];}
const expected={};
for(const id of [142202,162207])expected[id]=ids(catalog.abilities.find(a=>a.type==='CardAbility'&&a.templateId===id).sourceTree).sort((a,b)=>a-b);
context.expected=expected;
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const template of [142202,162207]){
 const pool={v:[]};BetaGwentNilfPool(template,pool);
 check(JSON.stringify([...pool.v].sort((a,b)=>a-b))===JSON.stringify(expected[template]),'generated pool matches the original graph '+template);
 for(const selected of expected[template]){
  const g=fixture(1),caster=add(g,template,8,4,1);add(g,112101,1,0,2,50);
  check(g.Play(1,caster.Snapshot().instanceId,1),'play creator '+template+'/'+selected);
  check(g.pendingChoice&&JSON.stringify([...g.pendingIds].sort((a,b)=>a-b))===JSON.stringify(expected[template]),'actual deploy offers all three exact options '+template);
  const request=g.requestId;
  const invalid=template===142202?113312:200023;
  check(!g.SelectTemplateChoice(request,invalid)&&g.requestId===request&&g.pendingChoice,'old wrong option is rejected');
  check(!g.SelectTemplateChoice(request-1,selected),'stale request is rejected');
  const before=new Set(g.live.map(c=>c.Snapshot().instanceId));
  check(g.SelectTemplateChoice(request,selected),'choose valid special '+selected);
  check(g.live.some(c=>!before.has(c.Snapshot().instanceId)&&c.TemplateId()===selected),'the selected special is actually created '+selected);
  let steps=0;while(g.IsPending()&&steps++<20)check(__pending(g),'resolve created special '+selected);
  check(!g.IsFatal()&&!g.IsPending(),'created special completes safely '+template+'/'+selected);
 }
}
globalThis.report={checks,expected,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'creation-pools091.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify(context.report));
