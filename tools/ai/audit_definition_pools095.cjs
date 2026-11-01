'use strict';
// Static source oracle for EVERY GetCardsDefinitionsNode in supported cards.
// Read C# CardDefinitionHelper.FilterDefinitions / EnumExtensions / BitArray;
// compare the resulting sets with the real translated WS pool functions.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const root=path.resolve(__dirname,'../..'),raw=fs.readFileSync(path.join(root,'data/beta924/normalized/catalog.json')),cat=JSON.parse(raw);
const pools=['BetaGwentMonsterTemplates','BetaGwentNorthernPool','BetaGwentNilfPool','BetaGwentScoiaPool','BetaGwentSkelligePool','BetaGwentNeutralPool'];
let checks=0;const failures=[],records=[],unsupported=[];
function verify(v,label){checks++;if(!v)failures.push(label);}
const flatten=x=>[...(x.attributes?.TemplateId?[Number(x.attributes.TemplateId)]:[]),...(x.children||[]).flatMap(flatten)];
for(const a of cat.abilities){
 if(!c.BetaGwentDuelDefinition(a.templateId).header.templateId)continue;
 const queries=a.nodes.filter(n=>n.type==='GetCardsDefinitionsNode');
 for(const q of queries){
  const p=Object.fromEntries(q.sourceTree.children.map(x=>[x.tag,x]));
  const number=(key,def=0)=>Number(p[key]?.attributes.V??def);
  const words=key=>(p[key]?.children[0]?.children||[]).map(n=>BigInt(n.attributes.V));
  const availability=words('Availability'),category=words('Category');
  const categoryActive=category.some(n=>n!==0n);
  // HasAll calls query.And(template), exactly as the source does; HasAny is
  // symmetric. Most current queries use HasAny, but retain the actual direction.
  let expected=cat.templates.filter(t=>{
   const f=t.fields;
   if(availability.some(n=>n!==0n)){const n=Number(t.attributes.Availability);if(((availability[Math.floor(n/64)]||0n)&(1n<<BigInt(n%64)))===0n)return false;}
   for(const [key,field]of [['Faction','FactionId'],['Tier','Tier'],['Type','Type'],['Kind','Kind'],['Tokens','Tokens']]){const mask=number(key);if(mask&&(mask&Number(f[field]))===0)return false;}
   for(const [key,field]of [['PlayerSide','PlayerSide'],['OpponentSide','OpponentSide']]){const mask=number(key);if(mask&&mask!==-1&&(mask&Number(t.placement[field]))===0)return false;}
   if(categoryActive){const tw=t.categoryWords.map(w=>BigInt(w.decimal));
    if(number('CategoryCompare',1)===0){if(tw.slice(0,category.length).some((w,i)=>((category[i]||0n)&w)!==w))return false;}
    else if(!category.some((w,i)=>(w&(tw[i]||0n))!==0n))return false;
   }
   return true;
  }).map(t=>t.templateId);
  const vars=new Map(a.sourceTree.children.filter(n=>n.tag.endsWith('Variables')).flatMap(n=>n.children).map(n=>[Number(n.attributes.Id),n]));
  const removed=[];
  for(const n of a.nodes.filter(n=>n.type==='CardDefinitionListRemoveNode')){
   const link=a.connections.find(x=>x.destinationPort.nodeId===n.nodeId&&x.destinationPort.field==='Element');
   const source=a.nodes.find(x=>x.nodeId===link?.sourcePort.nodeId);
   if(source?.type!=='GetVarNode'){unsupported.push({id:a.templateId,node:n.nodeId,reason:'nonconstant removal'});continue;}
   const ids=flatten(vars.get(Number(source.attributes.VarId))||{});
   if(ids.length!==1){unsupported.push({id:a.templateId,node:n.nodeId,reason:'nonconstant definition'});continue;}
   removed.push(ids[0]);
  }
  expected=expected.filter(id=>!removed.includes(id)).sort((a,b)=>a-b);
  const outputs=[];
  for(const name of pools){const out={v:require('vm').runInContext('[]',c)};c[name](a.templateId,out);if(out.v.length)outputs.push({name,ids:Array.from(out.v).sort((a,b)=>a-b)});}
  verify(outputs.length===1,a.templateId+' exactly one pool owner');
  const actual=outputs[0]?.ids||[],missing=expected.filter(n=>!actual.includes(n)),extra=actual.filter(n=>!expected.includes(n));
  verify(!missing.length&&!extra.length,a.templateId+' full definition pool matches Beta filters and removals');
  records.push({id:a.templateId,title:cat.localization.ru_ru[a.templateId+'_name'],nid:a.nid,queryNode:q.nodeId,pool:outputs[0]?.name,sourceCount:expected.length,actualCount:actual.length,removed,missing,extra});
 }
}
const report={checks,failures,unsupported,records,fingerprint:manifest.fingerprint,catalogSha256:crypto.createHash('sha256').update(raw).digest('hex'),scope:'Source definition query sets and constant removals; random-three distribution, choices and effect execution are separate checks',allCardSemanticComparisonComplete:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length||unsupported.length)process.exitCode=1;
