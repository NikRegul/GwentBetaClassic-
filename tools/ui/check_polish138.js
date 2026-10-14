// Execute production ActionScript methods against a bounded display-list fixture.
'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const draft='BetaGwent/drafts/ui-polish138',src=process.env.BG_UI138_SOURCE||'BetaGwent/ui/src';
const board=fs.readFileSync(path.join(src,'BetaGwentBoard.as'),'utf8');
const helpers=fs.readFileSync(path.join(src,'BetaGwentUi138.as'),'utf8');
function extract(source,name){
 const start=source.indexOf('function '+name+'(');assert(start>=0,name);
 const open=source.indexOf('{',start);let end=open+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end)
  .replace(/:(String|Object|void|int|uint|Number|Array|Boolean|Event|MouseEvent|Sprite|TextField|Function|TextFormat)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/\s+as (Sprite|TextField|Array)\b/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
let checks=0;function check(value,name){assert(value,name);checks++;}
const c=vm.createContext({Math,String,Number,Object,int:n=>n|0,console});
c.editorNewOnly=false;c.editorScroll178=0;c.deckScroll178=0;c.editorFeedbackOrigin178=null;c.editorFeedbackPoint178=()=>({x:0,y:0});
const helperNames=['sceneDuration','publicCard','view','stateLines','effect','deckReasons','missingCost','handOffsets'];
vm.runInContext(`var flashes=true,shake=true,scenes=1,chains=true,filters={};`+
 helperNames.map(n=>extract(helpers,n)).join('\n')+
 `\nvar BetaGwentUi138={${helperNames.map(n=>n+':'+n).join(',')},filters};`,c);
const card=(id,zone=1,side=1)=>({id,templateId:id,title:'Card '+id,power:8,normalPower:8,armor:0,tokens:0,timer:-1,zone,side});
for(const hidden of [null,{...card(1),hidden:true},{...card(1,1,2),tokens:8},card(1,8,2),card(1,16,2),{...card(0),templateId:0}])
 check(c.view(hidden)===null,'hidden identity is never retained');
check(c.publicCard({...card(2,8,2),tokens:64}),'revealed enemy hand is public');
check(c.publicCard(card(2,32,2)),'enemy graveyard is public');
const snapshot=c.view(card(3));check(snapshot.templateId===3&&snapshot!==card(3),'history takes a detached public snapshot');
const state=c.stateLines({...card(3),power:12,normalPower:10,armor:2,tokens:512},{power:8,typeMask:4});
check(state.includes('Базовая сила: 8')&&state.includes('Нормальная сила: 10')&&state.includes('Текущая сила: 12'),'base, normal and current strength stay distinct');
check(state.includes('+2')&&state.includes('Броня: 2')&&state.includes('Обречённость'),'only known live stats are displayed');
check(!state.includes('повреждения')&&!state.includes('усиление'),'net strength is not presented as an invented damage/boost breakdown');
check(c.stateLines({...card(1,1,2),tokens:8},{power:9,typeMask:4})==='','hidden stats stay hidden');
for(const [kind,expected] of [[12,'banish'],[11,'consume'],[13,'deathwish'],[16,'create']])check(c.effect({kind},null,null)===expected,'effect '+expected);
check(c.effect({kind:15,title:'Возвращение из сброса'},null,null)==='resurrect','resurrection has a separate presentation');
check(c.effect({kind:15,title:'Из колоды призван'},null,null)!=='resurrect','deck summon is not mislabeled resurrection');
check(c.effect({kind:2},{power:4,normalPower:8,armor:0},{power:7,normalPower:8,armor:0})==='recovery','recovery stays below unchanged normal strength');
check(c.effect({kind:2},{power:7,normalPower:8,armor:0},{power:10,normalPower:8,armor:0})==='boost','crossing normal strength is boost');
check(c.effect({kind:2},{power:8,armor:2},{power:8,armor:1})==='damage','armour-only damage stays damage');
check(c.sceneDuration(false)===700&&c.sceneDuration(true)===0,'short scenes and reduced motion');
c.scenes=2;check(c.sceneDuration(false)===1200,'full scenes');c.scenes=0;check(c.sceneDuration(false)===0,'scenes can be disabled');
check(c.deckReasons(23,5,7).length===3,'separate deck validation reasons');
check(c.deckReasons(41,4,6)[0].includes('1'),'excess deck count');
check(c.missingCost([{templateId:1,copies:3},{templateId:2,copies:1}],{1:1,2:1},()=>30)===60,'craft cost counts missing COPIES only');
for(let count=1;count<=20;count++){
 const hand=Array.from({length:count},(_,i)=>({id:i+1}));
 const offsets=c.handOffsets(hand,Math.ceil(count/2),10);
 check(Object.keys(offsets).length===count&&Object.values(offsets).every(x=>Math.abs(x)<=10),'bounded hand layout '+count);
 check(offsets[1]===0&&offsets[count]===0,'outer hand cards remain inside their slots '+count);
 check(Object.values(c.handOffsets(hand,0,10)).every(x=>x===0),'hover exit restores slots '+count);
}
vm.runInContext(`var clock=100,reducedMotion=false,uiMotions=[],buttonFeedback=[],animations=[],handHoverId=0;
 function getTimer(){return clock;}
 var controller={active:false,getFocus(){return null;}};
 var actionHistory=[],historyScores=[0,0],cards=[],displayedCards={},departedPoses={};
 var BetaGwentFullCatalog={find(id){return id>0?{templateId:id,title:'Public '+id,power:8}:null;}};
 var editorState={slot:1,faction:2,total:25,golds:4,silvers:6,valid:true,status:''},editorCards=[],editorById={};
 var editorUndo=[],editorPending=null,editorUndoPending=false,editorFlight=null,ready=true,editingDeck=true,revision=7;
 var editorSearch='',editorTier=0,editorType=0,editorPosition=0,editorStrength=0,editorFactionOnly=false,editorOwnedOnly=false,editorPage=0;
 var sent=[];function send(name,args){sent.push({name,args});}var editorName='Deck';
 var kegPhase=1,kegAutomatic=[{}, {}, {}, {}],kegRevealed=[false,false,false,false],renders=0;
 function uiSound(){}function render(){renders++;}
 `+['uiTween','tickUiMotions','safeHistoryCard','recordHistoryDetails','noteHistory','historyLine',
     'editorCounts','settleEditorUndo','undoEditorChange','editorAction','rememberEditorFilters',
     'restoreEditorFilters','kegRevealAll'].map(n=>extract(board,n)).join('\n'),c);
const sprite={stage:{},alpha:0};c.uiTween(sprite,'alpha',1);c.clock=170;c.tickUiMotions(170);
check(sprite.alpha>0&&sprite.alpha<1,'hover interpolates');
for(let i=0;i<100;i++)c.uiTween(sprite,'alpha',i%2);
check(c.uiMotions.length===1,'rapid hover replaces old motion rather than accumulating');
c.clock=400;c.tickUiMotions(400);check(c.uiMotions.length===0,'completed hover motions are released');
c.uiTween({stage:null,alpha:0},'alpha',1);c.tickUiMotions(401);check(c.uiMotions.length===0,'detached sprites are released');
c.reducedMotion=true;c.uiTween(sprite,'alpha',.7);check(sprite.alpha===.7&&c.uiMotions.length===0,'reduced motion snaps to final state');
c.reducedMotion=false;
c.displayedCards={1:card(1),2:card(2),3:card(3)};
c.noteHistory({kind:1,source:1,target:1,templateId:1,title:'Play'},[8,0],[card(1)]);
c.noteHistory({kind:2,source:1,target:2,templateId:1,title:'Sweep',attackCount:2},[8,12],[card(1),{...card(2),power:6},{...card(3),power:6}]);
check(c.actionHistory.length===1,'trigger chain stays with its root play');
check(c.actionHistory[0].events.some(e=>e.target?.id===2)&&c.actionHistory[0].events.some(e=>e.target?.id===3),'mass effect records every publicly changed target');
c.noteHistory({kind:2,source:2,target:2,templateId:2,title:'Boost'},[10,12],[card(1),{...card(2),power:9,armor:2},card(3)]);
check(c.actionHistory[0].events.at(-1).change==='Сила: 6 → 9 · Броня: 0 → 2','history records the public before/after values for each reaction');
c.noteHistory({kind:2,source:0,target:3,row:1,title:'Weather'},[8,10],[card(3)]);
check(c.actionHistory.length===2,'weather starts a separate history group');
c.noteHistory({kind:1,source:9,target:9,templateId:0,title:'Ambush'},[8,10],[{...card(9,1,2),tokens:8}]);
check(c.actionHistory[0].actor==null&&c.actionHistory[0].events.every(e=>!e.actor&&!e.target),'concealed ambush does not leak art into history');
for(let i=0;i<80;i++)c.noteHistory({kind:1,title:'Play '+i},[i,0],[]);
check(c.actionHistory.length===64,'history memory is bounded');
for(let i=0;i<160;i++)c.noteHistory({kind:2,title:'Hit'},[i,0],[]);
check(c.actionHistory[0].events.length===128,'history event memory is bounded');
c.editorCards=[{templateId:1,copies:1,canAdd:true}];c.editorById={1:c.editorCards[0]};
c.editorAction('OnBetaGwentDeckEditorChange',1,1)();
check(!c.ready&&c.editorUndo.length===0&&c.editorPending.before[1]===1,'undo waits for native acknowledgement');
c.editorCards[0].copies=2;c.settleEditorUndo();c.ready=true;
check(c.editorUndo.length===1&&c.editorFlight.amount===1,'accepted change becomes undoable');
c.undoEditorChange();check(c.sent.at(-1).args[2]===-1&&c.editorUndoPending,'undo submits inverse through revision-guarded native event');
c.editorCards[0].copies=1;c.settleEditorUndo();c.ready=true;
check(c.editorUndo.length===0,'acknowledged undo is removed');
c.editorAction('OnBetaGwentDeckEditorChange',1,1)();c.settleEditorUndo();c.ready=true;
check(c.editorUndo.length===0,'rejected edit is never undoable');
c.editorAction('OnBetaGwentDeckEditorChange',1,1)();c.editorCards[0].copies=2;c.editorState.faction=4;c.settleEditorUndo();c.ready=true;
check(c.editorUndo.length===0&&c.editorPending===null,'faction switch invalidates pending undo');
c.editorState.faction=2;c.editorSearch='spy';c.editorTier=4;c.rememberEditorFilters();c.editorSearch='';c.editorTier=0;c.restoreEditorFilters(2);
check(c.editorSearch==='spy'&&c.editorTier===4,'editor filters survive editor reopen in this menu session');
const beforeSent=c.sent.length;c.kegRevealAll();
check(c.kegRevealed.every(Boolean)&&c.kegPhase===2&&c.renders===1,'reveal all proceeds to explicit fifth-card selection');
check(c.sent.length===beforeSent,'reveal all sends no inventory, choice or purchase command');
c.kegRevealAll();check(c.renders===1,'reveal all is idempotent outside reveal phase');
// Exercise real history navigation with an inspectable display list. Card detail itself
// is represented by a stub; return routing and both history screens are production AS.
class Sprite {
 constructor(){this.children=[];this.events={};this.x=0;this.y=0;this.scaleX=1;this.scaleY=1;this.alpha=1;
  this.graphics=new Proxy({},{get:()=>()=>{}});}
 get numChildren(){return this.children.length;}
 addChild(child){child.parent=this;this.children.push(child);return child;}
 removeChildAt(i){const child=this.children.splice(i,1)[0];child.parent=null;return child;}
 addEventListener(name,fn){this.events[name]=fn;}
}
c.Sprite=Sprite;c.MouseEvent={CLICK:'click'};c.Rectangle=class{constructor(x,y,w,h){Object.assign(this,{x,y,width:w,height:h});}};
c.BetaGwentFonts={TITLE:'title',BODY:'body'};
vm.runInContext(`var detailLayer=new Sprite(),controllerMenuOpen=false,detailOpen=false,detailBody=null,detailBack=[],tutorialPage=-1,tutorialReturn=-1,tutorialFirstRun=false;
 var tutorialLayer=new Sprite(),historyReturnPage=-1,historyReturnEntry=-1,historyEntryIndex=-1,historyPage=0,historyEventPage=0;
 var WIDE_PAD=0,numChildren=8,buttons=[],opened=null,templateDetails={};
 function closeControllerMenu(){controllerMenuOpen=false;}function clearDrag(){}function clearPlacementGhost(){}function setChildIndex(){}
 function panel(parent,x,y,w,h){var s=new Sprite();s.x=x;s.y=y;s.w=w;s.h=h;parent.addChild(s);return s;}
 function betaWindow(parent,x,y,w,h){return panel(parent,x,y,w,h);}
 function betaLabel(parent,value,x,y,w,size,color){var s=panel(parent,x,y,w,30);s.text=value;return s;}
 function paintBetaFace(){}function openCardDetail(card){opened=card;while(detailLayer.numChildren)detailLayer.removeChildAt(0);}
 function editorBetaButton(parent,title,x,y,w,h,enabled,action){var s=panel(parent,x,y,w,h);s.title=title;s.action=action;s.enabled=enabled;buttons.push(s);return s;}
 controller.registerControl=function(p,label,action){p.action=action;};
 `+['historyCardButton','historyEntryAction','openHistory','openHistoryEntry','closeCardDetail'].map(n=>extract(board,n)).join('\n'),c);
c.actionHistory=[{title:'Chain',kind:1,start:[0,0],end:[5,0],actor:card(1),
 events:Array.from({length:20},(_,i)=>({title:'Effect '+i,actor:card(1),target:card(i+2)}))}];
c.openHistory();check(c.detailOpen&&c.detailLayer.numChildren===2,'history opens in isolated detail modal');
const detailButton=c.buttons.find(b=>b.title==='Подробности');detailButton.action();
check(c.historyEntryIndex===0&&c.historyEventPage===0,'details expand the actual trigger chain');
c.openHistoryEntry(0,2);check(c.historyEventPage===2,'chain supports more than the first six effects');
// Click an actual card control, then back: return to the SAME chain and page.
const box=c.detailLayer.children[1],cardControl=box.children.find(s=>s.action);
cardControl.action();check(c.historyReturnEntry===0&&c.opened!=null,'chain card can be inspected');
c.closeCardDetail();check(c.historyEntryIndex===0&&c.historyEventPage===2,'card inspection returns to the same chain page');
c.closeCardDetail();check(c.historyEntryIndex===-1&&c.detailOpen,'back from chain returns to history');
c.closeCardDetail();check(!c.detailOpen&&c.detailLayer.numChildren===0,'back from history returns control to the game');
const report={stage:138,checks,actualActionScript:true,nativeGameTested:false,
 sources:Object.fromEntries(['BetaGwentBoard.as','BetaGwentController.as','BetaGwentUi138.as'].map(name=>
  [name,crypto.createHash('sha256').update(fs.readFileSync(path.join(src,name))).digest('hex')]))};
fs.mkdirSync(path.join(draft,'evidence'),{recursive:true});
fs.writeFileSync(path.join(draft,'evidence/checks.json'),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync('docs/evidence/polish138.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
