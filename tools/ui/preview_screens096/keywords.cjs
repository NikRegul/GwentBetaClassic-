'use strict';
// Recorded production full-view and controller layouts; not a game screenshot.
const fs=require('fs'),path=require('path'),vm=require('vm');
process.env.ROOT=path.resolve(__dirname,'../../..');
const H=require('./harness.cjs'),c=H.ctx,UI=process.env.ROOT+'/BetaGwent/ui/src/';
const texts=Object.fromEntries([...fs.readFileSync(UI+'BetaGwentCardText.as','utf8').matchAll(/values\[(\d+)\]=(.*);/g)].map(m=>[m[1],JSON.parse(m[2])]));
const related=fs.readFileSync(UI+'BetaGwentRelated091.as','utf8');
const links=JSON.parse(related.match(/const LINKS:Object=(.*);/)[1]),extras=JSON.parse(related.match(/const EXTRA:Object=(.*);/)[1]);
Object.assign(c,{skin:3,detailOpen:false,detailLayer:new c.Sprite(),previewLayer:new c.Sprite(),detailBack:[],detailNav:null,detailNavCard:null,
 detailKeywordPane096:null,detailKeywordContent096:null,detailKeywordCard096:0,detailKeywordKey096:'',detailKeywordsHidden096:false,detailKeywordScroll096:0,detailKeywordMax096:0,
 numChildren:5,leaderIds:[],leaderOptions:[],padMouseOnly096:[],titleIndex:null,collectionNew:{},editingDeck:false,browsingCatalog:false,detailBody:null,padBar096:null,pileOpen:false,nameOpen:false,controllerMenuOpen:false,playing:false,selected:0,
 clearDrag(){},clearPlacementGhost(){},setChildIndex(){},enemyAmbush:()=>false,isAmbush:()=>false,ambushReading:()=>'',
 controllerContext:()=>({mode:c.mode}),controllerQuickSpecial:()=>false,isCaranthirChoice:()=>false,isMulliganHand:()=>false});
c.BetaGwentCardText.find=id=>texts[id];
c.BetaGwentRelated091={find:id=>H.byId[id]||extras[id],ids:id=>links[id],all:()=>H.all};
vm.runInContext('Object.getPrototypeOf([]).sortOn=function(key){return this.sort((a,b)=>a[key]-b[key]);};',c);
vm.runInContext(['openCardDetail','closeCardDetail','cardReading','clearDetailKeywords096','createDetailKeywords096','detailKeywordEntries096','updateDetailKeywords096','scrollDetailKeywords096','toggleDetailKeywords096',
 'relatedCard091','relatedCards','drawRelatedCards','relatedOpener','detailArrow','stepCardDetail','padGlyph096','padIcon096','padLegendItems096','drawPadBox096','drawPadStrip096','glyphWidth096','padLabel096','mouseOnly096'].map(n=>H.extract(n)).join('\n'),c);
const lang=fs.readFileSync(UI+'BetaGwentTextLanguage.as','utf8');
function extract(name){const a=lang.indexOf('function '+name+'('),b=lang.indexOf('{',a);let d=1,i=b+1;while(d){d+=(lang[i]==='{')-(lang[i]==='}');i++;}return lang.slice(a,i).replace(/:\s*(?:Object|Array|int|uint|Number|Boolean|void|String|TextField|TextFormat)(?=\s*[,)=;{])/g,'');}
vm.runInContext(extract('layoutButton'),c);
c.BetaGwentTextLanguage.fitButton=(field,size,minimum,height,originY=0,padding=4,align='center')=>c.layoutButton(field,{buttonFit:{size,minimum,height,originY,padding,align}});
const scenes={};
for(const id of [201781,201572,133302]){
 c.detailLayer=new c.Sprite();c.detailLayer.isRoot=true;c.padMouseOnly096=[];
 const def=H.byId[id]||extras[id],text=texts[id];
 c.openCardDetail({...def,side:1,zone:0,tokens:0},{description:text.description},false,true);
 scenes['keywords-'+id]=H.dump(c.detailLayer);
}
for(const device of [0,1]){
 c.controller.active=true;c.controller.device=device;c.padBar096=new c.Sprite();c.padBar096.isRoot=true;c.mode='battle';
 c.detailOpen=false;c.drawPadBox096(c.padLegendItems096('battle'));scenes['pad-'+device]=H.dump(c.padBar096);
 c.padBar096=new c.Sprite();c.padBar096.isRoot=true;c.drawPadStrip096(c.padLegendItems096('editor'));scenes['pad-editor-'+device]=H.dump(c.padBar096);
}
fs.writeFileSync(process.argv[2],JSON.stringify(scenes));console.log(Object.keys(scenes));
