// Execute the shipped ActionScript methods with a small display-list host.
// This verifies state transitions and geometry, not native Classic rendering.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const build=path.resolve(root,process.argv[2]||'BetaGwent/build/classic081-hand-fix13');
const raw=fs.readFileSync(path.join(build,'ui/src/BetaGwentBoard.as'));
const source=raw.toString('utf8');
const prior=fs.readFileSync(path.join(root,'BetaGwent/build/classic081-subimages-fix12/ui/src/BetaGwentBoard.as'),'utf8');
function extract(text,name){
 const start=text.indexOf('function '+name+'('),open=text.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end).replace(/:(?:Sprite|TextField|Matrix|Object|Array|String|Number|Boolean|void|int|uint)\b(?!\s*\()/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
  .replace(/ as (?:Sprite|TextField|Array)\b/g,'');
}
const layoutSource=fs.readFileSync(path.join(build,'ui/src/BetaGwentBoardLayout.as'),'utf8');
const layout={};for(const name of ['hand','ribbon','score','rowScore','presentation'])
 layout[name]=JSON.parse(layoutSource.match(new RegExp('const '+name+':Object=(\\{.*?\\});'))[1]);
let checks=0;function check(value,label){assert(value,label);checks++;}
function Sprite(){Object.assign(this,{children:[],x:0,y:0,width:104,height:127,scaleX:1,scaleY:1,alpha:1,visible:true,rotation:0,
 graphics:{lineStyle(){},drawRect(){}}});}
Sprite.prototype.addChild=function(c){if(c.parent){const i=c.parent.children.indexOf(c);if(i>=0)c.parent.children.splice(i,1);}this.children.push(c);c.parent=this;return c;};
Object.defineProperty(Sprite.prototype,'numChildren',{get(){return this.children.length;}});
const card=(id,zone=8,side=1)=>({id,zone,side,index:id-1,templateId:131101+id,power:5,normalPower:5,tokens:0,timer:-1,armor:0,canPlay:true});
function host(text,fixture={}){
 const c=vm.createContext({Math,Object,String,Number,Sprite,isFinite,int:x=>x|0,getTimer:()=>100});
 Object.assign(c,{skin:3,cards:[],cardSprites:{},displayedCards:{},previousPoses:{},departedPoses:{},departedOrder:[],
  consumedVisualIds:{},cardDetails:{},content:new Sprite(),animations:[],activeCue:null,BETA_CARD_ASPECT:17.64/21.46,
  BetaGwentBoardLayout:layout,selected:0,keyboardFocusId:0,dragging:false,dragId:0,playing:false,requestId:0,requestKind:0,rowRequest:false,
  playRules:{},handHoverId:0,selectingDecks:false,editingDeck:false,browsingCatalog:false,kegOpen:false,
  reducedMotion:false,connected:true,entryMode:2,revision:8,uiMotions:[],reports:[],classicHandReportKeys:{},classicHandLayoutState:'',...fixture});
 Object.assign(c,{
  sortedHand:v=>v.slice().sort((a,b)=>a.id-b.id),canPlacePending:()=>false,consumedTombstone:()=>false,
  isConsumeVictim:()=>false,rowGeometry:()=>({x:526,y:560,h:118}),rowLayout:()=>({x:526,w:104,step:108}),
  panel:(parent,x,y,w,h)=>{const p=new Sprite();Object.assign(p,{x,y,width:w,height:h});return parent.addChild(p);},
  paintBetaFace:p=>p.addChild(new Sprite()),paintArt:p=>p.addChild(new Sprite()),
  paintCardBack:p=>p.addChild(new Sprite()),betaPowerField:()=>({}),text:()=>({}),
  powerColor:()=>0,drawCardArmor080:()=>{},drawCardStatuses191:()=>{},attachInspect:()=>{},attachCard:()=>{},
  canAct:()=>false,canPlaceBefore:()=>false,canDirectTarget:()=>false,enemyAmbush:()=>false,
  betaDeckPoint:()=>[1701,926],cuePileOrigin:()=>null,reportClassicHandState:()=>{},
  uiTween:(sprite,property,to)=>c.uiMotions.push({sprite,property,to}),send:(...args)=>c.reports.push(args)
 });
 const names=['drawCards','setHandHover'];
 for(const name of ['finishHandLayoutMotion','classicBattleRibbon','classicHandLayout','classicHandX'])if(text.includes('function '+name+'('))names.push(name);
 vm.runInContext(names.map(n=>extract(text,n)).join('\n'),c);
 const ui=fs.readFileSync(path.join(build,'ui/src/BetaGwentUi138.as'),'utf8');
 vm.runInContext(extract(ui,'handOffsets'),c);c.BetaGwentUi138={handOffsets:c.handOffsets};
 return c;
}
// The old initial snapshot explicitly hides every card until an appear tick.
const baseline=host(prior,{cards:Array.from({length:10},(_,i)=>card(i+1))});baseline.drawCards();
check(Object.values(baseline.cardSprites).every(p=>p.alpha===0),'old snapshot reproduces initial invisible hand state');
for(const count of [1,2,10,20])for(const skin of [1,2,3]){
 const c=host(source,{skin,cards:Array.from({length:count},(_,i)=>card(i+1))});c.drawCards();
 check(Object.keys(c.cardSprites).length===count,'all received hand instances rendered '+count+'/'+skin);
 check(Object.values(c.cardSprites).every(p=>p.alpha===1&&Number.isFinite(p.x)&&Number.isFinite(p.y)),'initial hand immediately visible '+count+'/'+skin);
 check(c.animations.length===0,'snapshot has no fabricated draw flights '+count+'/'+skin);
 if(skin===3)check(Object.values(c.cardSprites).every(p=>p.x>=645.5-0.01&&p.x+p.width<=1433.2+0.01&&p.y+p.height<=1080),'hand remains inside viewport '+count);
 c.drawCards();check(Object.values(c.cardSprites).every(p=>p.alpha===1),'subsequent snapshot remains visible');
}
for(const fixture of [{cards:[card(1)],activeCue:{kind:14}},{cards:[card(1,1,2)]}]){
 const a=host(prior,fixture),b=host(source,fixture);a.drawCards();b.drawCards();
 const simplify=c=>JSON.parse(JSON.stringify(c.animations.map(m=>({...m,sprite:{x:m.sprite.x,y:m.sprite.y,alpha:m.sprite.alpha}}))));
 assert.deepStrictEqual(simplify(a),simplify(b),'actual draw and board arrival animation unchanged');checks++;
}
// A mouse/gamepad hover may arrive before an appearance tick, or mid-flight.
for(const alpha of [0,.35,1]){
 const cards=[card(1),card(2),card(3)],c=host(source,{cards});c.drawCards();
 for(const p of Object.values(c.cardSprites)){p.alpha=alpha;p.scaleX=.8;p.scaleY=.8;p.rotation=4;
  c.animations.push({sprite:p,appear:true,toX:p.x,toY:p.y,toScaleX:1,toScaleY:1,toRotation:0});}
 c.setHandHover(2);
 check(c.animations.every(m=>m.finished&&m.sprite.alpha===1&&m.sprite.scaleX===1&&m.sprite.scaleY===1&&m.sprite.rotation===0),'hover completes appearance at alpha '+alpha);
 check(c.uiMotions.length===6,'hover still queues layout tweens');
}
const oldHover=host(prior,{cards:[card(1)]});oldHover.drawCards();oldHover.setHandHover(1);
check(oldHover.animations.every(m=>m.finished)&&oldHover.cardSprites[1].alpha===0,'old hover reproduces stuck transparent card');
const c=host(source),original=JSON.stringify(layout.ribbon);
for(const faction of [0,1,2,3,4,99])for(const side of [1,2]){
 const r=c.classicBattleRibbon(faction,side),row=layout.rowScore[side+':2'],score=layout.score[side];
 check(r[0]+r[2]<=score[0]+score[2]+.001&&row[0]-(r[0]+r[2])>=40,'ribbon leaves middle row score gap '+faction+'/'+side);
 check(r[2]>0&&r[3]>0,'valid ribbon extent');
}
check(JSON.stringify(layout.ribbon)===original,'shared Beta layout not mutated');
const diagnostic=host(source,{cards:[card(1),card(2)]});diagnostic.drawCards();
vm.runInContext(extract(source,'reportClassicHandState'),diagnostic);diagnostic.reportClassicHandState('settled');
check(diagnostic.reports[0][1][3].includes('received=2 created=2 visible=2'),'actual diagnostics report hand sprite state');
if(source.includes('function classicHandLayout(')){
 const originalHand=layout.hand['1'];
 for(const area of [null,[NaN,910,Infinity,204],[-107374182.4,910,-1,204]]){
  layout.hand['1']=area;
  const bounded=host(source,{cards:Array.from({length:10},(_,i)=>card(i+1))});bounded.drawCards();
  const positions=Object.values(bounded.cardSprites).map(p=>p.x);
  check(positions.every(x=>Number.isFinite(x)&&x>=645.5&&x<=1330),'invalid layout cannot hide hand '+area);
  check(new Set(positions).size===10,'invalid layout retains distinct hand slots');
 }
 layout.hand['1']=originalHand;
 const bounded=host(source);check(bounded.classicHandX(2,{left:NaN,step:Infinity})===709.5,'non-finite X never reaches native display list');
 check(bounded.classicHandX(2,{left:-107374182.4,step:0})===709.5,'native INT_MIN/20 sentinel rejected');
}
check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!source.replace(/\r\n/g,'').includes('\n'),'BOM/CRLF retained');
for(const dir of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])
 check(raw.equals(fs.readFileSync(path.join(build,'ui',dir,'BetaGwentBoard.as'))),'five-copy parity '+dir);
const report={checks,actualActionScriptMethods:true,initialHandVisible:true,hoverCompletesAppearance:true,
 nativeClassicVerified:false};
fs.writeFileSync(path.join(build,'hand-regression.json'),JSON.stringify(report,null,2));
console.log(JSON.stringify(report));
