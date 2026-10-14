// Execute production mouse timing, menu navigation, burn and consume presentation.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const controller=fs.readFileSync('BetaGwent/ui/src/BetaGwentController.as','utf8');
const burn=fs.readFileSync('BetaGwent/ui/src/BetaGwentBurn143.as','utf8');
function extract(source,name){
 const at=source.indexOf('function '+name+'(');assert(at>=0,name);const start=source.indexOf('{',at);let end=start+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(Sprite|TextField|Event|MouseEvent|String|Function|Object|Rectangle|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/\s+as Sprite\b/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
class Sprite{constructor(){this.children=[];this.transform={};this.graphics=new Proxy({},{get:()=>()=>{}});this.alpha=1;this.visible=true;this.listeners={};}addChild(s){s.parent=this;this.children.push(s);return s;}removeChildAt(i){const s=this.children.splice(i,1)[0];s.parent=null;}get numChildren(){return this.children.length;}contains(s){return this===s||this.children.some(c=>c===s||c.contains?.(s));}addEventListener(n,f){this.listeners[n]=f;}}
let checks=0;function check(v,label){assert(v,label);checks++;}
const c=vm.createContext({Math,Object,Number,String,Sprite,int:v=>v|0,Rectangle:class{},MouseEvent:{MOUSE_DOWN:'down',ROLL_OVER:'over'},ColorTransform:class{constructor(...v){this.values=v;}}});
vm.runInContext(`var playing=true,controllerMenuOpen=false,detailOpen=false,pileOpen=false,nameOpen=false,mulliganConfirm=false;
var mouseReplayHeld=false,mouseReplayBoosted=false,mouseReplayAt=0,now=0,fastReplay=false,FAST_REPLAY_SCALE=.25,scales=[],skips=0,replayHint=null;
function getTimer(){return now;}function isInspectMouse(e){return e.right;}function retimeReplay(s){scales.push(s);}function skipReplay(){skips++;}
`+['replayMouse','updateReplayMouse','releaseReplayMouse','onReplayMouseUp','accelerateReplay','collapseMourntart'].map(n=>extract(board,n)).join('\n'),c);
const event=type=>({type,right:true,preventDefault(){},stopImmediatePropagation(){}});
for(let i=0;i<12;i++){
 c.fastReplay=false;c.playing=true;c.scales=[];c.now=i*1000;
 c.replayMouse(event('down'));c.now+=100;c.updateReplayMouse(c.now);c.onReplayMouseUp(event('up'));c.replayMouse(event('click'));
 check(c.scales.length===0&&!c.fastReplay,'short RMB click never accelerates or skips');
 c.now+=200;c.replayMouse(event('down'));c.now+=180;c.updateReplayMouse(c.now);c.updateReplayMouse(c.now+50);
 check(c.scales.join(',')==='.25'.replace(/^\./,'0.'),'one temporary speed multiplier per hold');
 c.onReplayMouseUp(event('up'));c.onReplayMouseUp(event('up'));
 check(c.scales.join(',')==='0.25,4'&&!c.mouseReplayBoosted,'release restores tempo exactly once');
}
c.now+=1000;c.replayMouse(event('down'));c.now+=200;c.updateReplayMouse(c.now);c.controllerMenuOpen=true;c.updateReplayMouse(c.now);
check(!c.mouseReplayHeld&&!c.mouseReplayBoosted&&c.scales.at(-1)===4,'opening a modal cancels temporary acceleration');c.controllerMenuOpen=false;
c.fastReplay=true;c.scales=[];c.replayMouse(event('down'));c.now+=200;c.updateReplayMouse(c.now);c.onReplayMouseUp(event('up'));
check(c.fastReplay&&c.scales.length===0,'mouse hold does not multiply or cancel controller acceleration');
c.fastReplay=false;c.mouseReplayBoosted=true;c.scales=[];c.accelerateReplay();c.releaseReplayMouse();
check(c.fastReplay&&c.scales.length===0,'controller A during a mouse hold retains the existing multiplier');
vm.runInContext(`var cards=[],histories=[];function noteHistory(cue){histories.push(cue);}`+extract(board,'noteFrameHistory'),c);
const card=(id,power,zone=1)=>({id,power,armor:0,side:1,zone});
for(let count=2;count<=40;count++){
 let state=[card(1,3),card(2,2)];c.cards=state;const inputs=[];
 for(let i=0;i<count;i++){
  inputs.push({cue:{kind:11,source:1,target:100+i,templateId:132202,targetView:{templateId:1000+i,zone:32}},cards:state});
  state=state.map(x=>({...x,power:x.id===2?x.power+1:x.power}));inputs.push({cue:{kind:2,source:2,target:2,templateId:132305},cards:state});
 }
 state=state.map(x=>({...x,power:x.id===1?x.power+count:x.power}));inputs.push({cue:{kind:2,source:1,target:1,templateId:132202},cards:state});
 const before=JSON.stringify(inputs),group=c.collapseMourntart(inputs);
 check(group.length===2&&group[0].cue.massTargets.length===count,'Mourntart swallows all actual victims together '+count);
 check(group[1].cards===inputs.at(-1).cards&&group[1].cue.massConsumeBoost&&JSON.stringify(inputs)===before,'consume then boost uses exact final snapshot without mutating inputs '+count);
 c.histories=[];for(const f of group)c.noteFrameHistory(f);check(c.histories.length===count*2+1,'every consume and boost remains in history '+count);
 const barrier={cue:{kind:3,source:1,target:9,templateId:132202},cards:state};
 const separated=c.collapseMourntart([...inputs,barrier,...inputs]);
 const swallows=separated.map((f,i)=>f.cue.kind===11?i:-1).filter(i=>i>=0),death=separated.findIndex(f=>f.cue.kind===3);
 check(swallows.length===2&&swallows[0]<death&&death<swallows[1],'deaths remain causal barriers '+count);
 const other=inputs.map(f=>({...f,cue:{...f.cue,templateId:132301}}));check(c.collapseMourntart(other).length===other.length,'ordinary consumers retain their individual actions '+count);
}
// Exercise the menu's actual item construction and navigation, including disabled entries.
vm.runInContext(`var controllerMenuTab=0,controllerMenuFocus='',controllerMenuHelp=null,controllerMenuLayer=new Sprite();
var WIDE_PAD=120,animationTempo=1.5,reducedMotion=false,leaderOne=true,ready=false,entryMode=2,serverRevision=1;
var browsingCatalog=false,editingDeck=false,selectingDecks=false,kegOpen=false;
var soundEnabled=true,voiceEnabled=true,betaAudioAvailable=false,dragId=0,handSortMode=3,handSortReverse=false;
var BetaGwentUi138={intensity:.55,dynamicLeaders:true,flashes:true,shake:true,chains:true,scenes:1};
var BetaGwentTextLanguage={assign(f,s){f.text=s;},label(){return 'RU';}};
var menuNodes=[],picked='',calls=[];
var controller={getFocus(){},focusKey(k){picked=k;},focusTag(){},registerControl(p,label,action,card,detail){let n=menuNodes.find(n=>n.sprite===p);if(!n){n={sprite:p};menuNodes.push(n);}Object.assign(n,{label,action,detail});},menuControl(p,id,row,column){const n=menuNodes.find(n=>n.sprite===p);Object.assign(n,{key:'menu:'+id,menuRow:row,menuColumn:column});}};
function panel(p){return p.addChild(new Sprite());}function betaFrame(p){return p.addChild(new Sprite());}function text(p,s){return {text:s};}
function editorBetaButton(p,title,x,y,w,h,enabled,callback){let b=p.addChild(new Sprite());if(enabled)controller.registerControl(b,title,callback);return b;}
function canAct(){return !playing;}function canInspectPile(){return !playing;}function clearPlacementGhost(){}
function cycleTempo(){animationTempo=2;}function toggleMotion(){}function toggleLeaderMotion(){}function changePresentationOption(){return function(){};}
function toggleSound(){}function toggleVoice(){}function cycleAiPause(){}function cycleDifficulty(){}function cycleHandSort(){}function reverseHandSort(){}function cycleTextLanguage(){}
function handSortName(){return 'порядок добора';}function aiPauseName(){return 'нет';}function difficultyName(){return 'высокая';}
function requestBoardClose(){}function controllerCommand(){}function openHistory(){}function openTutorial(){}function submitBoard(){}
`+['menuItem','menuTabAction','selectControllerMenuTab','controllerMenuAction','closeControllerMenu','openControllerMenu'].map(n=>extract(board,n)).join('\n')+'\n'+extract(controller,'menuNeighbor'),c);
for(const playing of [false,true])for(let tab=0;tab<4;tab++){
 c.playing=playing;c.controllerMenuOpen=false;c.controllerMenuTab=tab;c.controllerMenuLayer=new Sprite();c.menuNodes=[];c.openControllerMenu();
 const nodes=Array.from(c.menuNodes);check(nodes.every(n=>n.key&&n.action),'every visible menu entry registers a stable controller action');
 const visited=new Set([nodes[0]]),queue=[nodes[0]];
 for(const n of queue)for(const dir of [37,38,39,40]){const next=c.menuNeighbor(nodes,n,dir);if(next&&!visited.has(next)){visited.add(next);queue.push(next);}}
 check(visited.size===nodes.length,'every menu entry is reachable from the tabs, including disabled entries '+tab+'/'+playing);
 if(tab===1){const brightness=nodes.find(n=>n.key==='menu:brightness');brightness.action();check(c.picked==='menu:brightness','changing an effect retains focus on that setting');}
 if(tab===2&&playing){const sort=nodes.find(n=>n.key==='menu:sort');sort.action();check(c.controllerMenuHelp.text.includes('Сортировка'),'disabled entry explains its reason without executing');}
}
// Real dissolve geometry remains stationary and consumes the whole card by the end.
const d=vm.createContext({Math,int:v=>v|0,ColorTransform:c.ColorTransform});
vm.runInContext('var w=100,h=120,frame={alpha:1},flames={alpha:1},face={transform:{}},frames=Array.from({length:25},()=>({visible:true})),rects=[];'+
 'var cut={graphics:{clear(){rects=[];},beginFill(){},drawRect(...a){rects.push(a);},endFill(){}}},edge={graphics:{clear(){},beginFill(){},drawRect(){},endFill(){}}};'+extract(burn,'render'),d);
let previous=Infinity;
for(let i=0;i<=100;i++){d.render(i/100);const area=d.rects.reduce((a,r)=>a+r[2]*r[3],0);check(area<=previous+1e-6,'burn progressively removes card area');previous=area;}
check(previous===0&&!d.flames.visible,'burn ends with no surviving card or persistent flame');
check(board.includes('if(activeCue.kind==1&&!origin&&activeCue.source>0'),'special portrait is drawn only for its play announcement');
check(board.includes('drawFireDestroy(fx,cx,cy,w,h,style==3?')&&!board.includes('fire?[0xFFF4B0'),'burn uses the fire dissolve art, not the generic destruction hit');
check(board.includes('BetaGwentHud104.KEY_RC,null'),'mouse replay hint has no click acceleration action');
check(controller.includes('hint.x=sideHint?1500:36')&&board.includes('controller.active?88:330'),'side hints reserve space beside the field and description');
check(board.includes('if(!previewParent&&!browsingCatalog&&!pileOpen)inspection=body;'),'right stick is bound to the visible battle description');
vm.runInContext(`var animations=[],activeCue={massGrouped:true,massTargets:Array.from({length:10},(_,i)=>({id:i+1,view:{templateId:i+1,side:1}}))},previousPoses={},displayedCards={},cardSprites={},consumedVisualIds={},CONSUME_TOMBSTONE_MS=900;
function paintArt(){}var bloods=[];function getTimer(){return 0;}function drawBloodConsume(fx,pose,d){bloods.push(d);}function consumePilePose(v){return {templateId:v.templateId};}var BETA_CARD_ASPECT=17.64/21.46;`+extract(board,'drawMassConsume'),c);
c.reducedMotion=false;c.drawMassConsume(new Sprite(),{x:500,y:500,width:80,height:100});
check(c.bloods.length===10&&c.bloods.every(d=>d===0)&&Object.keys(c.consumedVisualIds).length===10,'Mourntart victims start together, with no stagger');
const layout=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoardLayout.as','utf8');
const ownPiles=['deck','grave'].map(name=>JSON.parse(layout.match(new RegExp('const '+name+':Object=(\\{[^;]+\\});'))[1])['1']);
for(const pile of ownPiles)check(764+94<pile[1],'side hints remain above the native deck and graveyard');
check(662+88<764&&764+94<866,'description, side hints and action buttons have separate vertical space');
vm.runInContext(`var flags=0,requestId=0,requestKind=0,selected=0,rowRequest=false,controllerInspectBoard=false,controllerTyping=false,tutorialPage=-1,skin=3,introStart=0;
var content=new Sprite(),choiceLayer=new Sprite(),mulliganDialog=new Sprite(),nameLayer=new Sprite(),tutorialLayer=new Sprite(),detailLayer=new Sprite(),pileLayer=new Sprite();
function canPlaceSelected(){return false;}function canPlacePending(){return false;}function choiceTableHidden(){return false;}function isCaranthirChoice(){return false;}
function state(){return controllerContext();}function getFocus(){return menuNodes.find(n=>n.key===picked);}function trace(){}var owner={};
function invoke(name){if(name==='fast')calls.push(name);}
`+extract(board,'controllerContext')+'\n'+extract(controller,'activate')+'\n'+extract(board,'controllerCommand'),c);
c.playing=true;c.controllerMenuOpen=false;c.controllerMenuTab=1;c.menuNodes=[];c.openControllerMenu();c.picked='menu:tempo';c.animationTempo=1.5;c.activate();
check(c.animationTempo===2&&!c.calls.includes('fast'),'A changes a menu setting during replay instead of accelerating');
check(!c.controllerContext().replay&&c.controllerContext().root===c.controllerMenuLayer,'open settings own replay input and focus');
const skippedBefore=c.skips;c.controllerCommand('back');check(!c.controllerMenuOpen&&c.skips===skippedBefore,'B closes settings during replay without skipping');
vm.runInContext(`var artNames=[],bursts=[];var BetaGwentSpellArt143={clip(name){artNames.push(name);return new Sprite();}};
var cells=[];var BetaGwentLightning144={BOLT:0,SHOCK:1,SPARK:2,RIM:3,CORE:4,FLARE:5,SMOKE:6,cell(kind){cells.push(kind);return new Sprite();}};
function betaBurst(...a){bursts.push(a);}function GlowFilter(){}`+['lightningTimeAt','drawLightningImpact144','drawLightning143','drawSpecialProjectile'].map(n=>extract(board,n)).join('\n'),c);
for(const delay of [180,380]){c.animations=[];c.artNames=[];c.cells=[];c.drawSpecialProjectile(new Sprite(),960,414,600,280,{element:64,method:1},0xB1CFFF,delay,0);
check(c.artNames.length===0&&c.cells.includes(0)&&c.cells.includes(1)&&c.cells.includes(3),'Alzur uses the lightning atlas (bolt, shock, rim) instead of Crow layers');
const orb=c.animations.find(a=>a.betaFlight),impact=c.animations.filter(a=>!a.betaFlight&&a.toX===600&&a.toY===280);
check(orb&&orb.duration===delay&&impact.length>0&&Math.min(...impact.map(a=>a.delay))===delay,'lightning travel and impact share the same arrival instant');}
const report={stage:143,checks,passed:true,nativeGameTested:false};
fs.writeFileSync(process.argv[2]||'docs/evidence/fixes143.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
