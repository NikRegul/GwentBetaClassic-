'use strict';
// Membership-table proof, deliberately separate from complete card abilities.
// Expectations are read from PRIMARY graph inputs, not recipes or generated WS.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {catalog,graph}=require('./source_graph095.cjs'),{context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const bindings=[];
const north=[[122309,333,30],[122312,158,58],[122301,507,144],[122310,167,70],[200170,540,517],[200132,162,71],[152302,531,17],[122103,93,32],[201624,268,87],[200033,54,26],[200237,101,32],[200044,168,17]];
const skellige=[[152211,109,103],[152306,110,87],[152302,531,17],[152310,126,115],[122309,333,30],[200081,324,17],[200046,143,27],[200103,199,51],[200044,168,17]];
for(const [prefix,refs]of [['BetaGwentNorthernCategory',north],['BetaGwentSkelligeCategory',skellige]])refs.forEach((ref,i)=>bindings.push({fn:prefix,kind:i+1,ref}));
for(const [name,ref]of [['Dwarf',[142201,62,27]],['Spell',[201601,404,307]],['Elf',[142101,174,163]],['Dryad',[142209,422,206]]])bindings.push({fn:'BetaGwentNilf'+name,ref});
for(const b of bindings){
 const g=graph(b.ref[0],b.ref[1]),n=g.node(b.ref[2],'FilterCardCategoryNode');g.value(b.ref[2],'CompareMethod',1);g.value(b.ref[2],'Negate','False');
 const words=n.sourceTree.children.find(x=>x.tag==='CardCategory').children[0].children;
 b.words=words.map(x=>BigInt(x.attributes.V));b.evidence=g.evidence(['FilterCardCategoryNode','ECategoryCompareMethod','CardCategory']);
}
const shared=graph(201662,catalog.abilities.find(a=>a.templateId===201662).nid);shared.value(137,'CompareMethod',1);shared.value(137,'Negate','False');shared.edge(144,'DV',137,'CardCategory');
const excludedWords=shared.node(144,'GetCardCategoryNode').sourceTree.children.find(x=>x.tag==='Exclude').children[0].children.map(x=>BigInt(x.attributes.V));
assert(!shared.raw.connections.some(e=>e.destinationPort.nodeId===144&&e.destinationPort.field==='Exclude'));
const templates=catalog.templates.filter(t=>{const d=c.BetaGwentDuelDefinition(t.templateId);return d.header.templateId>0&&[2,4].includes(d.header.typeMask);});assert.equal(templates.length,511);
let checks=0;const failures=[],records=[];const check=(v,label)=>{checks++;if(!v)failures.push(label);};
for(const b of bindings){let members=0;for(const t of templates){
 const expected=b.words.some((w,i)=>(w&BigInt(t.categoryWords[i]?.decimal||0))!==0n),actual=b.kind?c[b.fn](t.templateId,b.kind):c[b.fn](t.templateId);
 if(expected)members++;check(actual===expected,b.fn+'/'+(b.kind||'')+'/'+t.templateId);
 }records.push({function:b.fn,kind:b.kind,source:b.ref,words:b.words.map(String),members});}
let sharedTrue=0;for(const a of templates)for(const b of templates){
 const expected=a.categoryWords.some((w,i)=>(BigInt(w.decimal)&~(excludedWords[i]||0n)&BigInt(b.categoryWords[i]?.decimal||0))!==0n);
 if(expected)sharedTrue++;check(c.BetaGwentNilfSharedCategory(a.templateId,b.templateId)===expected,'sharedCategory/'+a.templateId+'/'+b.templateId);
}
const report={checks,failures,cards:templates.length,membershipFunctions:bindings.length,sharedCategoryPairs:templates.length**2,sharedTrue,sharedExcludedWords:excludedWords.map(String),records,fingerprint:manifest.fingerprint,
 sourceEvidence:[...bindings.map(b=>b.evidence),shared.evidence(['FilterCardCategoryNode','GetCardCategoryNode','ACardTagData'])],
 actualWitcherScript:true,semanticCoverageComplete:false,scope:'25 category membership predicates versus primary graph masks for all 511 supported templates, plus every ordered pair for shared-category intersection AFTER the original Exclude mask in Corpse Venom graph243/node144. This does NOT prove all predicate call sites, HasAll filters, dynamic category mutation, other target filters or event sequencing.'};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failureCount:failures.length,firstFailures:failures.slice(0,10),cards:templates.length,membershipFunctions:bindings.length,sharedCategoryPairs:report.sharedCategoryPairs,fingerprint:manifest.fingerprint}));if(failures.length)process.exitCode=1;
