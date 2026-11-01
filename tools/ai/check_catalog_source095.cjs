'use strict';
// Full-catalog data/three history filters against independent Beta graph inputs.
// This does not claim equality of every card's complete ability graph.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const {context:c,manifest}=require('./diagnose_strategy096.js').load(path.resolve(process.argv[2]));
const file=path.join(__dirname,'../../data/beta924/normalized/catalog.json'),raw=fs.readFileSync(file),source=JSON.parse(raw);
let checks=0,cards=0;const failures=[];function check(ok,label){checks++;if(!ok)failures.push(label);}
const fields={power:'Power',armor:'Armor',typeMask:'Type',tierMask:'Tier',factionMask:'FactionId'};
const masks=[{card:200103,node:51,fn:(id)=>c.BetaGwentSkelligeCategory(id,8),name:'Beast'},
 {card:200080,node:null,fn:id=>c.BetaGwentNilfDwarf(id),name:'Dwarf'},
 {card:201601,node:307,fn:id=>c.BetaGwentNilfSpell(id),name:'Spell'}];
for(const m of masks){
 const graph=source.abilities.find(a=>a.templateId===m.card);
 const node=graph.nodes.find(n=>m.node?n.nodeId===m.node:n.type==='FilterCardCategoryNode');assert(node);
 const category=node.sourceTree.children.find(n=>n.tag==='CardCategory');
 m.words=category.children[0].children.map(n=>BigInt(n.attributes.V));
 m.sourceNid=graph.nid;m.node=node.nodeId;
 assert.equal(node.sourceTree.children.find(n=>n.tag==='Negate').attributes.V,'False');
 assert.equal(node.sourceTree.children.find(n=>n.tag==='CompareMethod').attributes.V,'1');
}
for(const t of source.templates){
 const id=t.templateId,d=c.BetaGwentDuelDefinition(id),active=d.header.templateId>0&&[2,4].includes(d.header.typeMask);if(!active)continue;cards++;
 for(const [key,src]of Object.entries(fields))check(d.header[key]===Number(t.fields[src]),id+'/'+key+' differs from Beta');
 for(const [key,src]of [['initialTimer','InitialTimer'],['tokens','Tokens']])check(d[key]===Number(t.fields[src]),id+'/'+key+' differs from Beta');
 const disloyal=d.header.typeMask===4&&Number(t.placement.OpponentSide)>0&&Number(t.placement.PlayerSide)===0;
 check(c.BetaGwentDuelSpying(id)===disloyal,id+'/opposing placement');
 for(const m of masks){const expected=t.categoryWords.some((w,i)=>(BigInt(w.decimal)&(m.words[i]||0n))!==0n);check(m.fn(id)===expected,id+'/'+m.name+' differs from source history category filter');}
}
check(cards===511,'all 511 engine cards included');
const report={checks,cards,failures,fingerprint:manifest.fingerprint,catalogSha256:crypto.createHash('sha256').update(raw).digest('hex'),sourceFilters:masks.map(({fn,words,...m})=>({...m,words:words.map(String)})),scope:'Printed data, timer, tokens, disloyal placement and Beast/Dwarf/Spell membership for every engine card; complete ability semantics remain a separate audit',nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks,cards,failures}));if(failures.length)process.exitCode=1;
