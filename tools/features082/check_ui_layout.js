'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.resolve(root,process.argv[2]||'BetaGwent/build/release082-rc3-ready');let checks=0;
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);let d=1,i=b+1;for(;d;i++){if(s[i]==='{')d++;if(s[i]==='}')d--;}
 return s.slice(a,i).replace(/:(?:Sprite|TextField|String|Object|void|int|Number|Array|Boolean|Event)\b(?=\s*[,)=;{])/g,'');}
function check(v,n){assert(v,n);checks++;}
for(const platform of ['nextgen','classic']){
 const s=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const c=vm.createContext({skin:3,ready:true,editingDeck:true,editorFlight:null,editorUndo:[{}],content:{},editorState:{total:25},BetaGwentFonts:{BODY:'body'},nodes:[],editorAction:()=>()=>{},requestEditorExit(){},openDeckExchange(){},undoEditorChange(){},betaFace(){},editorSummary:()=> 'Deck is ready to play.',
  text(parent,value,x,y,w,size){const n={value,x,y,w,h:size*1.6};Object.defineProperty(n,'height',{set(v){n.h=v;},get(){return n.h;}});c.nodes.push(n);return n;},
  editorBetaButton(parent,title,x,y,w,h){c.nodes.push({title,x,y,w,h});},betaWideButton(title,x,y,w){c.nodes.push({title,x,y,w,h:48});}});
 vm.runInContext(fn(s,'drawDeckExchangeButtons')+'\n'+fn(s,'drawEditorFeedback'),c);c.drawEditorFeedback();
 const status=c.nodes.find(n=>n.value),undo=c.nodes.find(n=>n.title);const viewport=s.match(/filtered.length,5,240,960,(\d+),editorScroll178/);
 check(306+Number(viewport[1])+16<=status.y,'status has a separate band below the card viewport');
 check(status.y+status.h+16<=934,'summary and collection counters have separate bands');check(status.multiline&&status.wordWrap&&status.h>=44,'long validation can wrap');
 check(undo.x-1473>=40&&1899-undo.x-undo.w>=40&&987-undo.y-undo.h>=32,'Undo has consistent panel insets');
 c.nodes=[];c.drawDeckExchangeButtons();let exchange=c.nodes;check(exchange.length===2&&exchange.every(n=>n.y===1002),'editor exchange belongs to the footer');
 const footer=[{x:474,w:240},{x:730,w:200},...exchange,{x:1418,w:240}].sort((a,b)=>a.x-b.x);
 check(footer.every((n,i)=>i===0||n.x>=footer[i-1].x+footer[i-1].w+16),'all editor footer buttons have at least 16 px separation');
 check(1054>=1002+48+4&&1054+26<=1080,'controller hint does not overlap actions or leave the screen');
 c.editingDeck=false;c.nodes=[];c.drawDeckExchangeButtons();check(c.nodes.length===1&&c.nodes[0].x===966,'deck selection import aligns with the other footer actions');
 const window={x:0,y:0,w:920,h:430},parts=[];
 Object.assign(c,{effectGallery:false,entryMode:0,selectingDecks:false,flags:0,WIDE_PAD:0,controllerMenuLayer:{},closeControllerMenu(){},clearPlacementGhost(){},panel(){},betaFrame:()=>window,controller:{focusTag(){}},send(){}});
 c.editorSmallButton=c.editorBetaButton;c.nodes=[];vm.runInContext(fn(s,'requestBoardClose'),c);c.requestBoardClose();
 for(const n of c.nodes)check(n.x>=64&&n.x+n.w<=window.w-64&&n.y>=48&&n.y+n.h<=window.h-64,'exit dialog content stays inside decorative frame');
}
const report={checks,actualActionScript:true,footerAndStatusSeparated:true,controllerHintsInBounds:true};fs.writeFileSync(path.join(build,'ui-layout-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
