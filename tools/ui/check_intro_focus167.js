'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8'),pad=fs.readFileSync('BetaGwent/ui/src/BetaGwentController.as','utf8');
function fn(src,name){const a=src.indexOf('function '+name+'(');assert(a>=0,name);const b=src.indexOf('{',a);let i=b+1,d=1;while(d){if(src[i]==='{')d++;if(src[i]==='}')d--;i++;}
 return src.slice(a,i).replace(/:(?:DisplayObject|Sprite|TextField|MouseEvent|Event|String|Function|Object|Rectangle|void|int|uint|Number|Array|Boolean|BetaGwentLeaderPreview)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))').replace(/ as TextField/g,'');}
class Sprite{constructor(){this.children=[];this.visible=true;this.alpha=1;this.live=true;this.graphics={clear(){}};}addChild(s){this.children.push(s);s.parent=this;}contains(s){return this===s||this.children.some(c=>c.contains(s));}removeChildAt(i){this.children.splice(i,1);}removeEventListener(){}get numChildren(){return this.children.length;}}
const rect=()=>({x:200,y:200,width:150,height:220,right:350,bottom:420,clone:rect});
const c=vm.createContext({Math,Number,String,Object,Sprite,int:v=>v|0,MouseEvent:{CLICK:'click'}});
vm.runInContext(`var now=100,introStart=1,introInputUntil=0,introFocusPending=false,introSkipAt=0,introAudioPending=false,introParts=[],introLeaderMovies=[],introSerial=1;
var introLayer=new Sprite(),content=new Sprite(),choiceLayer=new Sprite(),mulliganDialog=new Sprite(),nameLayer=new Sprite(),tutorialLayer=new Sprite(),detailLayer=new Sprite(),controllerMenuLayer=new Sprite(),pileLayer=new Sprite();content.addChild(choiceLayer);
var kegOpen=false,browsingCatalog=false,editingDeck=false,selectingDecks=false,flags=0,requestId=1,requestKind=1,rowRequest=false,selected=0,controllerInspectBoard=false,nameOpen=false,detailOpen=false,controllerMenuOpen=false,pileOpen=false,mulliganConfirm=false,tutorialPage=-1,controllerTyping=false,skin=3,ready=true,playing=false;
var BetaGwentUi138={helpLabels:true},owner={contains(s){return s.live;}},nodes=[],focus=null,autoPicked=false,currentMode='',saved={},lastKey='',lastRect=null,navigationColumn=NaN,dirty=true,pressed={136:true};
var actions=0,renders=0,events=[];function getTimer(){return now;}function send(){}function isMulliganHand(){return true;}function canPlaceSelected(){return false;}function canPlacePending(){return false;}function choiceTableHidden(){return false;}function canAct(){return false;}
function state(){return controllerContext();}function invoke(name,n){events.push(name);}function trace(){}function bodyBounds(){return rectangle();}
`+['controllerContext','skipIntro','finishIntro','restoreFocusAfterIntro','controllerMenuAction','controllerCommand'].map(n=>fn(board,n)).join('\n')+
 ['prune','registerControl','candidates','getFocus','select','focusTag','activate'].map(n=>fn(pad,n)).join('\n'),c);
c.rectangle=rect;c.controller={active:true,device:0,swap:false,focusTag:c.focusTag};c.render=()=>{c.renders++;for(const n of c.nodes)n.sprite.live=false;c.choiceLayer.children=[];const tile=new Sprite();c.choiceLayer.addChild(tile);c.registerControl(tile,'card',()=>c.actions++,{id:10},null,'target');};
let checks=0;const check=(v,n)=>{assert(v,n);checks++;};
c.render();check(c.nodes[0].scope==='intro'&&c.getFocus()===null,'reproduce cards registered under intro scope');
c.finishIntro();c.now=549;c.restoreFocusAfterIntro();check(c.renders===1&&c.introFocusPending,'skip-confirm guard does not rebuild into an actionable screen');
c.now=550;c.restoreFocusAfterIntro();check(c.renders===2&&c.introInputUntil===0&&!c.introFocusPending,'mulligan controls are rebuilt after intro guard');
check(c.getFocus()?.tag==='target'&&c.getFocus()?.card.id===10,'first mulligan card receives focus without a cancel dialog');
check(c.actions===0&&c.pressed[136]===true,'focus recovery does not replace a card or clear a held confirm latch');
c.activate();check(c.actions===1,'fresh confirmation can replace the focused card');
c.restoreFocusAfterIntro();check(c.renders===2,'focus recovery runs exactly once');
c.heldPileMask=0;c.canInspectPile=()=>true;let inspected=[];c.inspectPile=(...a)=>inspected.push(a);c.controllerCommand('pileHold',{mask:3});check(inspected[0].join(',')==='2,32,true','LT+RT opens the enemy graveyard');
c.closeControllerMenu=()=>{c.controllerMenuOpen=false;};c.controllerMenuOpen=true;c.controllerMenuAction('enemyGrave')();check(inspected.at(-1).slice(0,2).join(',')==='2,32','menu action opens the enemy graveyard after closing settings');
check(/id:"enemyGrave",title:"Сброс соперника"/.test(board),'enemy graveyard remains available in Actions menu');
console.log(JSON.stringify({checks,actualActionScript:true,nativeGameTested:false}));
