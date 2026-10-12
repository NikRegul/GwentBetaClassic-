// Run the production tutorial/modal/controller routing against a small display-list stub.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const boardPath='BetaGwent/ui/src/BetaGwentBoard.as',controllerPath='BetaGwent/ui/src/BetaGwentController.as';
const source=fs.readFileSync(boardPath,'utf8');
function extract(text,name){
 const start=text.indexOf('function '+name+'(');if(start<0)throw Error(name);
 const open=text.indexOf('{',start);let depth=1,end=open+1;
 for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end)
  .replace(/:(String|Object|void|int|uint|Number|Array|Boolean|Event|MouseEvent|Sprite|TextField|Function|TextFormat)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/\s+as (Array|TextField)/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
class Sprite {
 constructor(){this.children=[];this.parent=null;this.x=0;this.y=0;this.alpha=1;this.visible=true;this.mouseChildren=true;this.filters=[];this.graphics=new Proxy({},{get:()=>()=>{}});}
 get numChildren(){return this.children.length;}
 get stage(){return this.parent?this.parent.stage:this.isRoot?{}:null;}
 addChild(c){if(c.parent)c.parent.removeChild(c);this.children.push(c);c.parent=this;return c;}
 addChildAt(c,i){this.addChild(c);this.children.splice(this.children.indexOf(c),1);this.children.splice(i,0,c);return c;}
 removeChild(c){this.children.splice(this.children.indexOf(c),1);c.parent=null;return c;}
 removeChildAt(i){return this.removeChild(this.children[i]);}
 setChildIndex(c,i){this.children.splice(this.children.indexOf(c),1);this.children.splice(i,0,c);}
 contains(c){return c===this||this.children.some(n=>n.contains&&n.contains(c));}
 addEventListener(){} removeEventListener(){}
}
class TextField extends Sprite {
 constructor(){super();this.text='';this.defaultTextFormat={font:'body'};this.maxScrollV=1;this.scrollV=1;}
 setTextFormat(){}
}
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
const c=vm.createContext({Sprite,TextField,Math,Number,String,console,
 Rectangle:class{constructor(x,y,width,height){Object.assign(this,{x,y,width,height});}},
 BlurFilter:class{constructor(x,y,quality){Object.assign(this,{x,y,quality});}},GlowFilter:class{},TextFormat:class{constructor(font,size,color){Object.assign(this,{font,size,color});}},
 Event:{ENTER_FRAME:1},MouseEvent:{CLICK:1,MOUSE_WHEEL:2},BetaGwentFonts:{BODY:'body',TITLE:'title'},
 BetaGwentFullCatalog:{all(){return cards;},find(id){return cards.find(c=>c.templateId===id);}},
 BetaGwentCardText:{find(id){return cards.find(c=>c.templateId===id);}},BetaGwentCardTags:{text(){return '';}}
});
const cards=JSON.parse(fs.readFileSync('data/beta924/duel/slice.json','utf8')).cards.map(n=>({...n,power:n.fields.Power,typeMask:n.fields.Type,glossary:[],flavor:''}));
vm.runInContext(`
var root=new Sprite();root.isRoot=true;
var content=new Sprite(),tutorialLayer=new Sprite(),detailLayer=new Sprite(),previewLayer=new Sprite(),controller=new Sprite();
[content,tutorialLayer,detailLayer,previewLayer,controller].forEach(n=>root.addChild(n));
var nodes=[],focused=null,sent=[],buttons=[],clock=100,uiSounds=0;
var TUTORIAL=null,tutorialPage=-1,tutorialReturn=-1,tutorialFirstRun=false,tutorialBody=null,detailBody=null,detailBack=[],detailOpen=false;
var WIDE_PAD=0,skin=3,kegOpen=false,browsingCatalog=false,editingDeck=false,selectingDecks=true,flags=0,requestId=0,requestKind=0,controllerInspectBoard=false;
var rowRequest=false,selected=0,nameOpen=false,controllerMenuOpen=false,pileOpen=false,mulliganConfirm=false,controllerTyping=false,ready=true,playing=false;
var choiceLayer=new Sprite(),mulliganDialog=new Sprite(),nameLayer=new Sprite(),controllerMenuLayer=new Sprite(),pileLayer=new Sprite();
var DEMO_W=92,DEMO_H=128;
function int(v){return v|0;}function getTimer(){return clock;}
function setChildIndex(n,i){root.setChildIndex(n,i);}
function clearDrag(){}function clearPlacementGhost(){}function canPlaceSelected(){return false;}function canPlacePending(){return false;}function canAct(){return false;}function isCaranthirChoice(){return false;}
function panel(parent,x,y,w,h){var n=new Sprite();Object.assign(n,{x,y,w,h});parent.addChild(n);return n;}
function betaFrame(parent,x,y,w,h){return panel(parent,x,y,w,h);}
function text(parent,value,x,y,w,size,color){var t=new TextField();Object.assign(t,{text:value,x,y,width:w,size,color});parent.addChild(t);return t;}
function betaLabel(parent,value,x,y,w,size,color){return text(parent,value,x,y,w,size,color);}
function editorBetaButton(parent,title,x,y,w,h,enabled,callback){
 var n=panel(parent,x,y,w,h);n.label=title;n.action=callback;buttons.push(n);
 if(enabled)controller.registerControl(n,title,callback,null,null,'control');return n;
}
function attachEditorClick(){}function paintBetaFace(){}function betaPowerField(){}function paintSpyRibbon(){}function paintCardBack(){}
function isSpyCard(id){return id===162210;}function readableText(s){return s;}function send(name,args){sent.push({name,args});}
function editorFactionIndex(){return 1;}function sideFaction(){return 1;}function relatedCards(){return [];}function cardReading(c){return c.description;}
controller.device=0;controller.swap=false;
controller.registerControl=function(sprite,label,action,card,detail,tag){
 var state=controllerContext(),scope=state.baseMode;
 for(var layer of state.layers)if(layer.root.contains(sprite))scope=layer.mode;
 nodes.push({sprite,label,action,tag,scope});
};
controller.getFocus=function(){var s=controllerContext();var valid=nodes.filter(n=>s.root.contains(n.sprite)&&n.scope===s.mode);if(!valid.includes(focused))focused=valid[0]||null;return focused;};
controller.focusTag=function(){focused=null;return controller.getFocus();};
Array.NUMERIC=1;Array.prototype.sortOn=function(key){this.sort((a,b)=>a[key]-b[key]);};
`+['controllerContext','tutorialPages','catalogByTitle','openTutorial','tutorialDemo','tutorialCardOpener','openCardDetail','closeCardDetail'].map(n=>extract(source,n)).join('\n'),c);
Object.defineProperty(c,'numChildren',{get(){return c.root.numChildren;}});
for(let page=0;page<7;page++){
 c.buttons=[];c.openTutorial(page);
 check(c.controllerContext().mode==='tutorial','tutorial has its own controller mode '+page);
 check(c.root.children.at(-1)===c.controller,'controller focus is visible above tutorial '+page);
 const footer=c.buttons.filter(b=>b.y===768);
 check(footer.length===3&&footer.every(b=>b.h===52),'footer buttons share a baseline '+page);
 check(footer[0].x===56&&footer.at(-1).x+footer.at(-1).w===1384,'footer shares content margins '+page);
 const demo=c.buttons.find(b=>b.label==='Попробовать');
 check(demo.x+demo.w/2===872+512/2,'demo action is centred '+page);
 check(c.controller.getFocus()?.action!=null,'controller can activate tutorial controls '+page);
}
c.openTutorial(4);
check(c.tutorialPages()[4].cards.includes('Кантарелла'),'draw spy has a card example');
check(c.tutorialPages()[4].body.includes('Кантарелла'),'draw spy is explained');
check(!c.tutorialPages()[5].body.includes('решает последний раунд'),'leader page has no mandatory last-round advice');
const retained=c.tutorialLayer.children[1],savedBody=c.detailBody;
const open=c.tutorialCardOpener(cards.find(n=>n.templateId===162210),4);open();
check(c.tutorialLayer.children.includes(retained),'card preview retains the tutorial behind it');
check(c.tutorialLayer.filters.length===1&&!c.tutorialLayer.mouseChildren,'retained tutorial is blurred and cannot receive input');
check(c.controllerContext().mode==='detail','card detail isolates controller input');
c.closeCardDetail();
check(c.tutorialPage===4&&c.tutorialLayer.children.includes(retained)&&c.detailBody===savedBody,'close returns to the same tutorial instance and page');
check(c.tutorialLayer.filters.length===0&&c.tutorialLayer.mouseChildren,'return restores tutorial controls');
c.closeCardDetail();check(!c.detailOpen&&c.tutorialLayer.numChildren===0,'closing tutorial clears modal state');
// Exercise actual command routing without invoking the other battle handlers.
vm.runInContext(`var introStart=100,skips=0;function skipIntro(){skips++;}function uiSound(){uiSounds++;}`,c);
vm.runInContext(extract(source,'controllerCommand'),c);
c.controllerCommand('device');c.controllerCommand('focus',{});c.controllerCommand('mouse');
check(c.skips===0,'device, focus and pointer updates cannot skip leader speech');
c.controllerCommand('back');check(c.skips===1,'explicit back can skip leader speech');
c.introStart=0;c.openTutorial(0);const first=c.controller.getFocus();let called=0;first.action=()=>called++;
c.controllerCommand('inspect',first);check(called===1&&c.tutorialPage===0,'inspect activates tutorial example instead of closing tutorial');
check(source.includes('betaWideButton("Обучение",1513,888,333'),'selection tutorial button fits the preview panel');
check(source.includes('if(restoreBoard)controller.focusNearestCard("card",960,800);'),'completed play focuses board rather than nearest graveyard control');
const report={stage:135,checks,actualActionScript:true,nativeGameTested:false,
 sources:Object.fromEntries([boardPath,controllerPath].map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]))};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
