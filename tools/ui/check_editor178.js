'use strict';
// Run production AS helpers and the native creation event, with host shims.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const shelf=fs.readFileSync('BetaGwent/ui/src/BetaGwentVirtualShelf178.as','utf8');
const native=fs.readFileSync('BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws','utf8');
const pad=fs.readFileSync('BetaGwent/ui/src/BetaGwentController.as','utf8');
function fn(src,name,event=false){
 let start=src.indexOf((event?'event ':'function ')+name+'('),open=src.indexOf('{',start),i=open+1,d=1;assert(start>=0,name);
 while(d){if(src[i]==='{')d++;if(src[i]==='}')d--;i++;}
 return src.slice(start,i).replace(/^event /,'function ').replace(/:\s*(?:array<[^>]+>|String|Function|Object|void|int|uint|bool|Boolean|Number|Array|Sprite|Point|Rectangle|TextField|Event|MouseEvent|SBetaGwentDuelDefinition|W3PlayerWitcher)(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))').replace(/\(W3PlayerWitcher\)thePlayer/g,'thePlayer');
}
let checks=0;function check(v,n){assert(v,n);checks++;}
const c=vm.createContext({Math,String,Number,Object,Array,int:v=>v|0});
vm.runInContext(['window','ensure','card','position'].map(n=>fn(shelf,n)).join('\n'),c);
for(const count of [0,1,5,6,25,478])for(const offset of [-100,0,318,800,100000]){
 const w=c.window(count,5,318,636,offset);
 check(w.offset>=0&&w.offset<=w.max&&w.first<=w.end&&w.end<=count,'bounded visible window');
 check(w.end-w.first<=15,'at most three rows instantiated');
 for(let index=0;index<count;index++){
  const next=c.window(count,5,318,636,c.ensure(index,5,318,636,w.offset));
  check(index>=next.first&&index<next.end,'requested card instantiated');
  const top=Math.floor(index/5)*318;
  check(top>=next.offset&&top+318<=next.offset+636,'requested row fully visible');
 }
}
const original={templateId:42,copies:1},view=c.card(original,'deck',0,46,428,372,480);
view.copies=2;check(original.copies===1&&view.viewKey==='deck42'&&view.shelfClip.h===480,'view identity and clip do not mutate collection');
check(c.position(7,4,4)&&!c.position(1,4,4)&&c.position(0,2,5)&&!c.position(0,1,5),'shared placement filters');
vm.runInContext(`var shelves178={collection:window(40,5,318,636,0)},shelfCards178={collection:Array.from({length:40},(_,i)=>({templateId:100+i}))};
var ready=true,detailOpen=false,nameOpen=false,controllerMenuOpen=false,editorScroll178=0,catalogScroll178=0,deckScroll178=0,redraws=0;
var BetaGwentVirtualShelf178={ensure},controller={focusKey(k){this.key=k;},focusTag(){}};
function redrawEditorCollection(){redraws++;shelves178.collection=window(40,5,318,636,editorScroll178);}function redrawCatalogGrid(){}function redrawDeckList178(){}
`+['scrollShelf178','shelfSelect178'].map(n=>fn(board,n)).join('\n'),c);
c.shelfSelect178('collection',35);check(c.editorScroll178===1908&&c.controller.key==='editor:card:cardcollection135','offscreen controller selection scrolls and restores stable key');
c.detailOpen=true;c.scrollShelf178('collection',0);check(c.editorScroll178===1908,'overlay blocks background scrolling');c.detailOpen=false;
vm.runInContext(`var createDeckOpen178=false,selectingDecks=true,createFaction178=0,createLeader178=0,entryMode=1,ownedCopies={11:1,12:0},revision=7,events=[],renders=0;
function render(){renders++;}function send(n,a){events.push([n,a]);}function cardFaction(id){return id===11||id===12?2:4;}
function editorFactionAvailable(f){return f===2;}function leadersForFaction(){return [{id:11}];}
`+['beginDeckCreator178','backDeckCreator178','createFactionAction178','createLeaderAction178','confirmDeckCreator178'].map(n=>fn(board,n)).join('\n'),c);
c.beginDeckCreator178();check(c.createDeckOpen178&&c.events.length===0,'opening creator allocates no native slot');
c.createFactionAction178(4)();check(c.createFaction178===0,'forced unavailable faction blocked');
c.createFactionAction178(2)();check(c.createLeader178===11,'faction selects first available leader');
c.createLeaderAction178(12)();check(c.createLeader178===11,'unowned leader blocked');
c.backDeckCreator178();check(c.createDeckOpen178&&c.createFaction178===0&&c.events.length===0,'back returns to factions without mutating draft');
c.createFactionAction178(2)();c.confirmDeckCreator178();c.confirmDeckCreator178();check(c.events.length===1&&c.events[0].join('|')==='OnBetaGwentDeckCreate|7,11','confirm sends selected leader exactly once');
// Native validation cannot be bypassed by forged UI input.
const n=vm.createContext({LogChannel(){}});
vm.runInContext(`var configured=true,selectingDecks=true,deckDraft=null,revision=9,libraryOnly=true,npcMatch=false,forcedBetaFaction=0,editorPublishedFaction=6,edits=0,published=0;
var thePlayer={BetaGwentOwned(id){return id===11?1:0;}},deckClearHistory={Clear(){}},deckLibrary={Edit(){edits++;return {cards:[]};}};
function BetaGwentDuelIsLeader(id){return id===11||id===12;}function BetaGwentDuelDefinition(id){return {header:{factionMask:2}};}
function PublishDeckSelection(){published++;}function PublishDeckEditor(){published++;}
`+fn(native,'OnBetaGwentDeckCreate',true),n);
check(!n.OnBetaGwentDeckCreate(8,11)&&n.edits===0,'native rejects stale revision');
check(!n.OnBetaGwentDeckCreate(9,12)&&n.edits===0,'native rejects unowned leader');
n.npcMatch=true;n.forcedBetaFaction=4;check(!n.OnBetaGwentDeckCreate(9,11)&&n.edits===0,'quest faction enforced before allocating slot');
n.forcedBetaFaction=2;check(n.OnBetaGwentDeckCreate(9,11)&&n.deckDraft.leader===11&&n.deckDraft.faction===2&&n.edits===1,'native draft starts with chosen faction and leader');
check(!n.OnBetaGwentDeckCreate(9,11)&&n.edits===1,'repeat cannot allocate second draft');
// Drag target and drop execute the real guard and dispatch functions.
vm.runInContext(`var editingDeck=true,editorDragId178=42,editorDragAmount178=1,editorDragRevision178=7,editorDragging178=true,mouseX=200,mouseY=600,editorFeedbackOrigin178=null,editorClickUntil178=0;
var editorById={42:{copies:1,canAdd:true}},drops=[];function getTimer(){return 1000;}function clearEditorDrag178(){editorDragId178=0;editorDragging178=false;}
function editorAction(event,id,amount){return function(){drops.push([id,amount]);};}
`+['editorDragTarget178','endEditorDrag178'].map(nm=>fn(board,nm)).join('\n'),c);
c.ready=true;check(!!c.editorDragTarget178(),'collection can drop on deck');
c.mouseX=1800;check(c.editorDragTarget178()===null,'outside panes cancels drop');
c.mouseX=200;c.revision=8;check(c.editorDragTarget178()===null,'stale drag rejected');c.revision=7;
c.endEditorDrag178({stopImmediatePropagation(){}});check(c.drops.length===1&&c.drops[0].join(',')==='42,1'&&c.editorClickUntil178===1250,'one drop and click suppression');
c.editorDragId178=42;c.editorDragAmount178=-1;c.mouseX=800;check(!!c.editorDragTarget178(),'deck card can return to collection');
c.editorById[42].copies=0;check(!c.editorDragTarget178(),'cannot remove absent copy');
// Native GFx can omit CLICK through a masked body. A stationary mouse release
// adds/removes once; leaving the body, inspection and stale revisions cancel it.
Object.assign(c,{Point:class Point{constructor(x,y){this.x=x;this.y=y;}},isInspectMouse:e=>!!e.right,
 editorDragTile178:{stage:{},globalToLocal:p=>p},editorDragBounds178:{contains:(x,y)=>x>=0&&x<=164&&y>=0&&y<=200}});
function stationary(amount,event={stageX:40,stageY:50,stopImmediatePropagation(){}}){
 c.editorDragId178=42;c.editorDragAmount178=amount;c.editorDragRevision178=c.revision;c.editorDragging178=false;c.editorClickUntil178=0;
 c.endEditorDrag178(event);
}
let beforeDrops=c.drops.length;stationary(1);check(c.drops.length===beforeDrops+1&&c.drops.at(-1)[1]===1&&c.editorClickUntil178===1250,'stationary release adds once and suppresses following CLICK');
stationary(-1);check(c.drops.at(-1)[1]===-1,'stationary release removes');
beforeDrops=c.drops.length;stationary(1,{stageX:300,stageY:50,stopImmediatePropagation(){}});check(c.drops.length===beforeDrops,'release outside original card cancels click');
stationary(1,{stageX:40,stageY:50,right:true,stopImmediatePropagation(){}});check(c.drops.length===beforeDrops,'right button never adds');
c.editorDragRevision178=1;c.editorDragId178=42;c.editorDragging178=false;c.endEditorDrag178({stageX:40,stageY:50});check(c.drops.length===beforeDrops,'stale release never adds');
// The accepted 0.9.x toolbar reduces the viewport to 552; row pitch stays 240.
const geometry=board.match(/new BetaGwentVirtualShelf178\(filtered.length,5,(\d+),(\d+),(\d+),editorScroll178\)/);
check(geometry&&Number(geometry[1])===240&&Number(geometry[2])===960&&Number(geometry[3])===552&&board.includes('tile.y=int(i/5)*240-editorScroll178'),'collection rows use accepted compact geometry');
// Production controller requests the next offscreen row; no phantom focus.
vm.runInContext(`var movementAt=0,dirty=false,invoked=[];function getFocus(){return {card:{shelfPane:'collection',shelfIndex:5},rect:{x:500,y:240,width:164,height:216}};}function candidates(){return [];}function state(){return {mode:'editor',shelves:{collection:{columns:5,count:40,rowHeight:240,offset:0,height:552}}};}function invoke(n,a){invoked.push([n,a]);}`+fn(pad,'editorFooter')+'\n'+fn(pad,'navigate'),c);
c.navigate(40);check(c.invoked.length===1&&c.invoked[0][0]==='shelfSelect'&&c.invoked[0][1].index===10,'D-pad down enters next virtual row');
for(const dir of ['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])for(const name of ['BetaGwentBoard.as','BetaGwentVirtualShelf178.as','BetaGwentController.as']){
 const raw=fs.readFileSync('BetaGwent/ui/'+dir+'/'+name);check(raw.equals(fs.readFileSync('BetaGwent/ui/src/'+name))&&raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'five mirrors BOM CRLF');
}
const report={stage:178,checks,actualActionScript:true,actualNativeEvent:true,nativeGameTested:false};
fs.writeFileSync('docs/evidence/editor178.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
