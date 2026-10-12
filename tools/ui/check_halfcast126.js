'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);let n=1,end=open+1;for(;n;end++){if(source[end]==='{')n++;if(source[end]==='}')n--;}
 return source.slice(start,end).replace(/:(Object|int|Boolean|Array|void)\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');}
const c=vm.createContext({Math});
vm.runInContext(`var playRules={},selected=1,requestId=0,revision=42,mouseX=0,mouseY=0,cards=[],cardDetails={},focusedSide=0,focusedRow=0,keyboardFocusId=0,skin=3,requestKind=0;
var ready=true,events=[],rendered=0;function int(v){return v|0;}function canAct(){return ready&&requestId===0;}
function rowGeometry(side,zone){var i=zone===1?0:zone===2?1:2;return {x:500,y:side===1?550+i*140:410-i*140,w:1000,h:130};}
function submitBoard(name,args){events.push({name,args});}function placementSide(){return 1;}function canSelectRow(side,zone){return side===2&&zone===2;}
function render(){rendered++;}function isMulliganHand(){return false;}function uiSound(){}
`+['halfCastSide','halfGeometry','halfCastTarget','canPlayRow','rowEnabled','chooseRow','cycleRowFocus'].map(extract).join('\n'),c);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
for(const side of [1,2]){
 c.playRules={1:{kind:3,side,rowMask:7}};c.events=[];
 check(c.halfCastSide()===side,'cast half respects authoritative side '+side);
 const g=c.halfGeometry(side);check(g.h===410,'whole half includes row gaps '+side);
 for(const y of [g.y+1,g.y+135,g.y+280,g.y+g.h-1]){c.mouseX=900;c.mouseY=y;check(c.halfCastTarget()?.side===side,'half hit surface includes y='+y);}
 c.mouseY=g.y-1;check(c.halfCastTarget()===null,'outside half is not a target');
 c.chooseRow(side,4);check(c.events[0].name==='OnBetaGwentBoardPlay'&&c.events[0].args[2]===1,'half cast sends canonical non-row placement '+side);
 c.focusedRow=0;c.cycleRowFocus(1);check(c.focusedSide===side&&c.focusedRow===1,'keyboard has one half choice '+side);
 c.cycleRowFocus(1);check(c.focusedRow===1,'keyboard does not cycle through three equivalent rows '+side);
}
c.playRules={1:{kind:2,side:2,rowMask:7}};c.events=[];c.chooseRow(2,4);
check(c.halfCastSide()===0&&c.events[0].name==='OnBetaGwentBoardPlayRowTarget'&&c.events[0].args[3]===4,'weather and true row abilities keep their row');
c.playRules={1:{kind:1,side:2}};check(c.halfCastSide()===0,'unit-target spells keep their target request');
c.requestId=10;c.events=[];c.chooseRow(2,2);check(c.events[0].name==='OnBetaGwentDuelRowTarget','pending row choice retains its native request');
check(source.includes('if(halfCastSide()>0)return halfCastTarget();'),'dragging shares full half target');
check(source.includes('attachRow(hit,side,zone,halfCastSide()==0)'),'controller suppresses duplicate row controls during half casts');
check(source.includes('drawHalfCast();'),'real row renderer creates the half surface');
console.log('PASS half-cast UI',checks);fs.writeFileSync('docs/evidence/halfcast126.json',JSON.stringify({checks,actualActionScript:true,nativeGameTested:false},null,2)+'\n');
