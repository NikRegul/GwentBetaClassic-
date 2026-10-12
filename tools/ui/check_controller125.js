// Exercise the controller's real ActionScript methods without exporting a menu.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentController.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'(');if(start<0)throw Error(name);
 const open=source.indexOf('{',start);let depth=1,end=open+1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(DisplayObject|String|Function|Object|Rectangle|void|int|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
const c=vm.createContext({Math,Number,console});
vm.runInContext(`var now=1000,movementAt=-1000,navigationColumn=NaN,dirty=false,nodes=[],focus=null;
var currentMode='',mode='inspect',saved={},lastRect=null,lastKey='',axis=0,events=[],accepts=0;
var pressed={},repeats={},inputCode=0,swap=false,yStarted=0,yCommitted=false,yCanPass=false;
function int(v){return v|0;} function getTimer(){return now;}
function candidates(){return nodes;} function state(){return {mode,preferred:mode==='battle'?'hand':'card',typing:false,pass:false};}
function invoke(name,node){events.push({name,key:node?node.key:null});} function trace(){} function activate(){accepts++;}
`+['getFocus','select','navigationLane','navigate','focusTag','restoreFocus','focusPlacementRow','stickDirection','direction','press','release'].map(extract).join('\n'),c);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
function rect(x,y,w=110,h=130){return {x,y,width:w,height:h,clone(){return rect(this.x,this.y,this.width,this.height);}};}
function node(key,x,y,tag='card',side=0,zone=0){const n={key,tag,rect:rect(x,y)};if(side)n.card={side,zone};return n;}
function setup(nodes,selected,mode='inspect') {c.nodes=nodes;c.focus=selected;c.mode=mode;c.currentMode=mode;c.navigationColumn=NaN;c.saved={};c.lastRect=null;c.lastKey=selected?.key||'';c.events=[];}
function move(dir){c.now+=100;c.navigate(dir);return c.focus;}
const top=node('top',900,100,'card',2,4),middle=node('middle',0,250,'card',2,2),bottomLeft=node('bottomLeft',0,400,'card',2,1),bottom=node('bottom',900,400,'card',2,1);
setup([top,middle,bottomLeft,bottom],top);
check(move(40)===middle,'down visits sparse adjacent row');
check(move(40)===bottom,'vertical navigation preserves original column across sparse row');
check(move(38)===middle&&move(38)===top,'reverse movement returns along the original column');
setup([top,middle,bottomLeft,bottom],bottom);
check(move(39)===bottom,'right edge cannot jump into a different board row');
check(move(37)===bottomLeft,'left stays within logical row');
check(move(38)===middle&&move(38)===top,'horizontal movement resets column to its new position');
const empty=node('empty',0,250,'row');empty.rect=rect(0,250,1100,130);empty.row={side:2,zone:2,rowOnly:true};
setup([top,empty,bottom],top);
check(move(40)===empty&&move(40)===bottom,'empty row is a navigable stop and preserves the column');
const target=node('rowButton',1020,205,'row');target.rect=rect(1020,205,176,28);target.row={side:2,zone:4,rowOnly:true};
setup([top,target,middle],top,'target');top.tag='target';middle.tag='target';
check(move(40)===middle,'a short row button in the same lane does not steal Down');top.tag='card';middle.tag='card';
const positions=[node('siege',900,100,'position'),node('ranged',0,250,'position'),node('melee',900,400,'position')];
positions.forEach((n,i)=>n.placement={side:2,zone:[4,2,1][i]});
setup(positions,positions[2],'placement');c.now+=100;c.focusPlacementRow(-1);
check(c.focus===positions[1],'LB moves visually up on the reversed opponent half');c.now+=100;c.focusPlacementRow(-1);
check(c.focus===positions[0],'LB preserves the column on the next row');c.now+=100;c.focusPlacementRow(-1);
check(c.focus===positions[0],'shoulder navigation stops at the board edge');
const grid=Array.from({length:10},(_,i)=>node('choice'+i,100+(i%5)*220,250+Math.floor(i/5)*300,'target'));
setup(grid,grid[3],'choice');check(move(40)===grid[8]&&move(38)===grid[3],'two-row choice grid retains its column');
setup(grid,grid[4],'choice');check(move(39)===grid[4],'right edge does not wrap into the next choice row');
const collectionTop=node('collectionTop',900,250),collectionBottom=node('collectionBottom',900,580),deckRow=node('deckRow',100,400);deckRow.rect=rect(100,400,300,34);
setup([collectionTop,collectionBottom,deckRow],collectionTop,'editor');
check(move(40)===collectionBottom,'editor grid navigation does not fall into the other deck pane');
const a=node('handA',100,950,'hand'),b=node('handB',800,950,'hand'),placement=node('slot',400,550,'position');
setup([a,b],b,'battle');c.mode='placement';c.nodes=[placement];c.getFocus();
const returnedA=node('handA',100,950,'hand'),returnedB=node('handB',800,950,'hand');
c.mode='battle';c.nodes=[returnedA,returnedB];c.restoreFocus('hand');
check(c.focus===returnedB,'cancel placement restores the selected hand instance after render');
c.mode='inspect';c.nodes=[top,middle,bottom];c.getFocus();c.mode='battle';c.nodes=[returnedA,returnedB];c.restoreFocus('hand');
check(c.focus===returnedB,'return from board inspection restores the previous hand card');
setup([top,middle,bottom],middle);c.mode='detail';c.nodes=[node('close',0,800,'control')];c.getFocus();
const rebuiltMiddle=node('middle',100,250,'card',2,2);c.mode='inspect';c.nodes=[top,rebuiltMiddle,bottom];
check(c.getFocus()===rebuiltMiddle,'closing card detail restores instance focus despite changed coordinates');
c.axis=39;check(c.stickDirection(.71,.72)===39,'diagonal jitter keeps held axis');
check(c.stickDirection(-.72,.71)===37,'reversing stick direction is not mistaken for diagonal jitter');
check(c.stickDirection(.1,.8)===38,'deliberate vertical change works without neutral');
check(c.stickDirection(.2,.2)===0,'stick releases inside neutral threshold');
c.axis=0;check(c.stickDirection(.4,.1)===0,'stick drift below entry threshold does not navigate');
c.axis=40;check(c.stickDirection(.1,-.4)===40,'hysteresis does not repeatedly release a held direction');
c.mode='battle';c.press(136);c.press(136);check(c.accepts===1,'held confirm activates once across duplicate input events');
c.release(136);c.press(136);check(c.accepts===2,'release re-arms confirm');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
check(board.includes('if(!occupied)')&&board.includes('"row",{rowOnly:true,side:side,zone:zone}'),'board registers inspection stops for empty rows');
check(board.includes('controller.restoreFocus("hand")'),'board cancellation uses remembered hand focus');
const report={stage:125,checks,actualActionScript:true,nativeControllerTested:false,releaseBuildStarted:false};
fs.writeFileSync('docs/evidence/controller125.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
