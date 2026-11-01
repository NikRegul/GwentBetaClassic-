'use strict';
// Exercise the production tooltip lifecycle, translation and common pad geometry.
// The display mock checks layout invariants, not native font/raster equivalence.
const fs=require('fs'),path=require('path'),vm=require('vm');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const boardFile=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',board=fs.readFileSync(boardFile,'utf8');
let checks=0;const failures=[];function check(v,label){checks++;if(!v)failures.push(label);}
function extract(source,name){const start=source.indexOf('function '+name+'(');if(start<0)throw Error(name);const open=source.indexOf('{',start);let end=open+1,d=1;while(d){d+=(source[end]==='{')-(source[end]==='}');end++;}return source.slice(start,end).replace(/:\s*(?:Object|Array|int|uint|Number|Boolean|void|String|TextField|TextFormat)(?=\s*[,)=;{])/g,'');}
const texts=Object.fromEntries([...fs.readFileSync(process.env.ROOT+'/BetaGwent/ui/src/BetaGwentCardText.as','utf8').matchAll(/values\[(\d+)\]=(.*);/g)].map(m=>[m[1],JSON.parse(m[2])]));
Object.assign(c,{detailOpen:true,detailKeywordPane096:null,detailKeywordContent096:null,detailKeywordCard096:0,detailKeywordKey096:'',detailKeywordsHidden096:false,detailKeywordScroll096:0,detailKeywordMax096:0,
 padBar096:new c.Sprite(),skin:3,detailBack:[],controllerMenuOpen:false,pileOpen:false,nameOpen:false,selected:0,playing:false,
 enemyAmbush:()=>false,isAmbush:()=>false,ambushReading:()=>'',controllerContext:()=>({mode:c.mode}),controllerQuickSpecial:()=>false,isCaranthirChoice:()=>false,isMulliganHand:()=>false});
c.BetaGwentCardText.find=id=>texts[id];c.controller.active=true;
vm.runInContext(['clearDetailKeywords096','createDetailKeywords096','detailKeywordEntries096','updateDetailKeywords096','scrollDetailKeywords096','toggleDetailKeywords096',
 'cardReading','relatedCard091','padGlyph096','padIcon096','padLegendItems096','drawPadBox096','drawPadStrip096','glyphWidth096','padLabel096','placementSide','isSpyCard','betaWideButton','editorBetaButton'].map(n=>H.extract(n,board)).join('\n'),c);
const lang=fs.readFileSync(process.env.ROOT+'/BetaGwent/ui/src/BetaGwentTextLanguage.as','utf8');
vm.runInContext(extract(lang,'layoutButton'),c);
c.BetaGwentTextLanguage.fitButton=(field,size,minimum,height,originY=0,padding=4,align='center')=>c.layoutButton(field,{buttonFit:{size,minimum,height,originY,padding,align}});
// Split only after whole-string translation, deduplicate and support CJK punctuation.
const original=texts[201781].glossary;
let translations={};c.BetaGwentTextLanguage.translate=s=>translations[s]||s;
check(c.detailKeywordEntries096(201781).length===3,'three separate source glossary tips');
translations[original]='Duel: alternate damage.\n\nEnemy: opposing side.\n\nDuel: alternate damage.';
check(c.detailKeywordEntries096(201781).join('|')==='Duel: alternate damage.|Enemy: opposing side.','whole glossary translated then deduplicated');
translations[original]='決鬥：交替造成傷害。\n\n護甲：吸收傷害。';
check(c.detailKeywordEntries096(201781).length===2,'CJK glossary retains entries');
check(c.detailKeywordEntries096(201817).length===0,'no fabricated tips for a card without glossary');translations={};
for(const [id,entry] of Object.entries(texts)){
 const card={templateId:+id,title:'Card',zone:0,tokens:0,power:entry.power};
 const plain=c.cardReading(card,{},true,true,false,false,false);
 check(!entry.glossary||!plain.includes(entry.glossary),'full preview excludes appended glossary '+id);
 check(c.cardReading(card,{},true,true,false,false,true).includes(entry.description),'original ability retained '+id);
}
const root=new c.Sprite();c.createDetailKeywords096(root,201781);
check(root.numChildren===1&&c.detailKeywordContent096.numChildren===3,'tooltip pane has exactly source entries');
const pane=c.detailKeywordPane096;c.toggleDetailKeywords096();check(!pane.visible,'stick click hides glossary');
c.toggleDetailKeywords096();check(pane.visible,'stick click restores glossary');
translations[original]=Array.from({length:30},(_,i)=>'Term '+i+': description').join('\n\n');c.updateDetailKeywords096();
check(c.detailKeywordMax096>0,'overflow has a scroll range');c.scrollDetailKeywords096(1e6);
check(c.detailKeywordScroll096===c.detailKeywordMax096&&c.detailKeywordContent096.y===-c.detailKeywordMax096,'scroll clamps to last tooltip');
c.scrollDetailKeywords096(-1e6);check(c.detailKeywordScroll096===0,'scroll clamps to first tooltip');
c.clearDetailKeywords096();check(root.numChildren===0&&c.detailKeywordPane096===null&&c.detailKeywordMax096===0,'close clears tooltip nodes and stale state');translations={};
for(const y of [996,1002]){
 const p=new c.Sprite(),button=c.editorBetaButton(p,'Back',0,y,200,52,true,()=>{});
 check(button.y+52===1032,'full preview footer clears pad strip '+y);
 c.content=new c.Sprite();c.betaWideButton('Back',0,y,200,true,()=>{});
 check(c.content.children[0].y+48===1032,'all wide footer buttons clear pad strip '+y);
}
// Layout includes pairs, every mode, both families and swapped accept/cancel.
  for(const device of [0,1,6])for(const swap of [false,true])for(const mode of ['battle','inspect','placement','target','rows','choice','detail','history','editor','catalog','name','tutorial','result','pile','gallery','actions']){
 c.controller.device=device;c.controller.swap=swap;c.mode=mode;c.padBar096=new c.Sprite();const items=c.padLegendItems096(mode);
 const battle=['battle','inspect','placement','target','rows'].includes(mode);
 if(battle)c.drawPadBox096(items);else c.drawPadStrip096(items);
 const cells=battle?c.padBar096.children:c.padBar096.children[0].children;
 const labels=cells.map(cell=>cell.children.find(n=>n.isText&&n.text===String(items[cells.indexOf(cell)][1]).toUpperCase()));
 check(labels.every(Boolean),'one label per cell '+device+'/'+swap+'/'+mode);
 if(battle){
  check(cells.every((cell,i)=>cell.x===1492+i%2*204&&cell.y===748+Math.floor(i/2)*42),'fixed grid '+device+'/'+mode);
  check(new Set(labels.map(n=>n.x)).size===1,'same label origin even with paired triggers '+device+'/'+mode);
 }
 check(labels.every(n=>Math.abs(n.y+(n.textHeight+4)/2-18)<=.5),'common glyph/text centre within pixel rounding '+device+'/'+mode);
 check(labels.every(n=>n.align==='left'),'translation keeps left alignment '+device+'/'+mode);
}
// Independently compare every supported unit placement side with Beta templates,
// for a hand card and for a pending created child absent from the collection.
const cat=JSON.parse(fs.readFileSync(process.env.ROOT+'/data/beta924/normalized/catalog.json','utf8'));
Object.assign(c,{playRules:{},selected:1,cards:[],pending:false,canPlacePending:()=>c.pending});let units=0;
for(const t of cat.templates.filter(t=>Number(t.fields.Type)===4)){
 if(!texts[t.templateId])continue;units++;const expected=Number(t.placement.OpponentSide)>0&&Number(t.placement.PlayerSide)===0?2:1;
 c.placementCard={templateId:t.templateId};c.cards=[{id:1,templateId:t.templateId}];
 for(const pending of [false,true]){c.pending=pending;check(c.placementSide()===expected,'Beta placement '+t.templateId+'/'+pending);}
}
c.pending=true;c.placementCard={templateId:201572};check(c.placementSide()===2,'Cow Carcass from Plague Carrier goes to enemy');
c.playRules={1:{kind:3,side:1}};check(c.placementSide()===1,'explicit placement rule takes precedence');
const report={checks,failures,sourceSha256:require('crypto').createHash('sha256').update(fs.readFileSync(boardFile)).digest('hex'),unitTemplates:units,actualActionScript:true,sourcePlacementCompared:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
