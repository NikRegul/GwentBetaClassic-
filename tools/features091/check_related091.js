// Execute the actual AS methods with the original generated catalogues.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');let checks=0;
function check(v,n){if(!v)throw Error(n);checks++;}
const base=path.resolve(process.argv[2]);
for(const platform of ['classic','nextgen']){
 const root=path.join(base,platform,'ui'),dirs=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'];
 const board=fs.readFileSync(path.join(root,'src/BetaGwentBoard.as'));
 check(board.subarray(0,3).equals(Buffer.from([239,187,191]))&&!board.toString().replaceAll('\r\n','').includes('\n'),'Board BOM and CRLF '+platform);
 for(const name of ['BetaGwentBoard.as','BetaGwentCardText.as','BetaGwentRelated091.as']){
  const files=dirs.map(d=>fs.readFileSync(path.join(root,d,name)));
  check(files.every(b=>b.equals(files[0])),'five identical copies '+platform+'/'+name);
 }
 const source=board.toString('utf8');
 function extract(name,code=source){
  const start=code.indexOf('function '+name+'(');check(start>=0,'actual AS method '+name);
  const open=code.indexOf('{',start);let depth=1,end=open+1;
  for(;depth;end++){if(code[end]==='{')depth++;if(code[end]==='}')depth--;}
  return code.slice(start,end).replace(/:(Object|int|Array|String|Boolean|void|Function|RegExp|Sprite|Number|TextField)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
 }
 const cards=[...fs.readFileSync(path.join(root,'src/BetaGwentFullCatalog.as'),'utf8').matchAll(/^\s*(\{"templateId":.+\})[,]?$/gm)].map(m=>JSON.parse(m[1]));
 const texts=Object.fromEntries([...fs.readFileSync(path.join(root,'src/BetaGwentCardText.as'),'utf8').matchAll(/values\[(\d+)\]=(.*);/g)].map(m=>[m[1],JSON.parse(m[2])]));
 const relatedSource=fs.readFileSync(path.join(root,'src/BetaGwentRelated091.as'),'utf8');
 const links=JSON.parse(relatedSource.match(/const LINKS:Object=(.*);/)[1]),extras=JSON.parse(relatedSource.match(/const EXTRA:Object=(.*);/)[1]);
 const painted=[],controls=[];
 class Sprite{constructor(){this.children=[];}addChild(child){this.children.push(child);}}
 const c=vm.createContext({LINKS:links,EXTRA:extras,Sprite,Rectangle:class{constructor(x,y,w,h){Object.assign(this,{x,y,w,h});}},BetaGwentFonts:{BODY:'body'},
  betaLabel(){return {};},paintBetaFace(tile,id,w,h){painted.push({tile,id,w,h});},betaPowerField(){},attachEditorClick(tile,fn){tile.click=fn;},controller:{registerControl(...args){controls.push(args);}},
  BetaGwentFullCatalog:{all:()=>cards,find:id=>cards.find(v=>v.templateId===id)},BetaGwentCardText:{find:id=>texts[id]},int:n=>n|0});
 vm.runInContext(['find','ids','all'].map(n=>extract(n,relatedSource)).join('\n')+'\nvar BetaGwentRelated091={find,ids,all};',c);
 vm.runInContext('var titleIndex=null,detailBack=[],opened=null;function openCardDetail(c,d,back){opened={c,d,back};}\n'+extract('relatedCard091')+'\n'+extract('relatedCards')+'\n'+extract('relatedOpener')+'\n'+extract('drawRelatedCards')+'\nArray.prototype.sortOn=function(key){return this.sort((a,b)=>a[key]-b[key]);};',c);
 for(const [id,options] of [[142202,[113305,113401,113301]],[162207,[113302,113401,200009]]]){
  for(const description of [texts[id].description,'Spawn Clear Skies or a spell.','']){
   const result=c.relatedCards(id,description);
   check(JSON.stringify(result.map(v=>v.templateId))===JSON.stringify(options),'all real options independent of language/declension '+id);
   for(const card of result){c.relatedOpener({templateId:id,side:2},{description},card)();check(c.opened.c.templateId===card.templateId&&c.opened.c.description===texts[card.templateId].description&&c.opened.back,'related card opens its real rules '+card.templateId);}
  }
  check(texts[id].glossary.includes('Создать: добавить карту в игру и сыграть ее.'),'Russian imperative has Spawn glossary '+id);
 }
 check(!cards.some(v=>v.templateId===113401)&&cards.length===479,'internal option does not enter collectible catalogue');
 check(c.relatedCards(113303,'Чистое небо')[0].templateId===113401,'other Clear Skies references can use the internal option');
 check(c.relatedCards(112202,'Призовите Эскеля и Ламберта.').some(v=>v.templateId===112204),'existing companion-name lookup remains available');
 check(c.relatedCards(112103,'Подкрепление').length===0,'keyword is not mistaken for a card');
 const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../../data/beta924/normalized/catalog.json'),'utf8'));
 const templateIds=new Set(catalog.templates.map(t=>t.templateId)),expected={};
 function references(node,hidden){hidden=node.attributes?.HideInTooltip??hidden;
  return [...(Number(node.attributes?.TemplateId)>0&&hidden!=='True'?[Number(node.attributes.TemplateId)]:[]),...(node.children||[]).flatMap(n=>references(n,hidden))];}
 for(const a of catalog.abilities){if(!templateIds.has(a.templateId))continue;
  const values=expected[a.templateId]??=[];
  for(const id of references(a.sourceTree))if(templateIds.has(id)&&id!==a.templateId&&!values.includes(id))values.push(id);}
 for(const id of Object.keys(expected))if(expected[id].length===0)delete expected[id];
 let reachable=new Set(cards.map(v=>v.templateId));
 while(true){const next=new Set([...reachable,...Object.entries(expected).filter(([id])=>reachable.has(Number(id))).flatMap(([,ids])=>ids)]);if(next.size===reachable.size)break;reachable=next;}
 for(const id of Object.keys(expected))if(!reachable.has(Number(id)))delete expected[id];
 const artSource=fs.readFileSync(path.join(root,'src/BetaGwentHDArt.as'),'utf8'),slots=JSON.parse(artSource.match(/slots:Object\s*=\s*(\{.*?\});/s)[1]);
 check(Object.keys(links).length===Object.keys(expected).length,'all original public tooltip sources are represented');
 let edgeCount=0;
 for(const [id,ids] of Object.entries(expected)){
  const result=c.relatedCards(Number(id),texts[id]?.description||'');
  check(JSON.stringify(result.map(v=>v.templateId).sort((a,b)=>a-b))===JSON.stringify([...ids].sort((a,b)=>a-b)),'all graph-related cards are available '+id);
  const box=new Sprite();painted.length=0;controls.length=0;
  c.drawRelatedCards(box,{templateId:Number(id),side:1},{},result);
  check(painted.length===ids.length&&controls.length===ids.length,'every related card is drawn and focusable '+id);
  for(const p of painted){
   check(slots[p.id]&&slots[p.id][3]>0&&slots[p.id][4]>0,'related card has an existing atlas illustration '+p.id);
   check(p.tile.x>=272&&p.tile.x+p.w<=1022&&p.tile.y+p.h+36<=971,'related art/name fits full-view strip '+id+'/'+p.id);
   p.tile.click();check(c.opened.c.templateId===p.id&&c.opened.c.description===texts[p.id].description,'every related tile opens its real rules '+p.id);
   edgeCount++;
  }
 }
 check(c.relatedCards(133302,texts[133302].description).length===8,'all eight Monster Nest options are accessible');
 check(c.relatedCards(112108,texts[112108].description).map(v=>v.templateId).join(',')==='112401,112402','Unicorn and Chironex are present');
 check(c.relatedCards(200102,texts[200102].description).map(v=>v.templateId).join(',')==='201717,201718','private exclusion list is not exposed as Hym choices');
 // Audit the full collectible catalogue, including cards using the preserved
 // descriptive-name fallback rather than an explicit public graph list.
 for(const card of cards){
  const result=c.relatedCards(card.templateId,texts[card.templateId]?.description||card.description||'');
  check(result.length<=8&&new Set(result.map(v=>v.templateId)).size===result.length&&!result.some(v=>v.templateId===card.templateId),'complete full-view related list is bounded and unique '+card.templateId);
  for(const related of result){
   check(texts[related.templateId]&&slots[related.templateId],'every displayed full-view hint has rules and artwork '+card.templateId+'/'+related.templateId);
   c.relatedOpener({templateId:card.templateId,side:1},{},related)();
   check(c.opened.c.templateId===related.templateId&&c.opened.c.description===texts[related.templateId].description,'full-view hint opens the correct rules '+card.templateId+'/'+related.templateId);
  }
 }
 // The full preview must also retain the original frame and faction for tokens
 // and mode cards that deliberately have no collectible-catalogue entry.
 const frames=[];
 Object.assign(c,{BetaGwentHDArt:{size(id){const p=slots[id];return p?[p[3],p[4]]:null;},clip(){return new Sprite();}},
  BetaGwentBanners090:{slot(faction,tier){return [faction,tier];},paint(){return true;}},leaderIds:[],attachLeaderMovie(){},trace(){},
  paintArt(parent,id){frames.push(id);return true;}});
 vm.runInContext(extract('paintBetaFace')+'\n'+extract('betaBannerRect'),c);
 for(const [id,entry] of Object.entries(extras)){
  frames.length=0;const face=c.paintBetaFace(new Sprite(),Number(id),104,146,0,false,false,true);
  check(frames.includes(entry.tier===8||entry.tier===1?-1602:entry.tier===4?-1601:-1600),'internal card gets original rarity frame '+id);
  check(face.slot[0]===entry.faction&&face.slot[1]===entry.tier,'full preview uses original faction and rarity '+id);
 }
 console.log(platform,JSON.stringify({collectiblesAudited:cards.length,graphSources:Object.keys(expected).length,graphLinks:edgeCount,internalCards:Object.keys(extras).length}));
 console.log(platform,'related-card and glossary checks passed');
}
console.log(JSON.stringify({checks,actualActionScript:true,nativeGameTested:false}));
