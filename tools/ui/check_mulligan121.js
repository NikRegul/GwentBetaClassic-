// Execute the actual AS slot-order function without a Flash renderer.
// Geometry and ordering evidence only; this does not claim native visual QA.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const start=source.indexOf('private function mulliganCardsInPlace()');
const end=source.indexOf('private function showMulliganCard(',start);
let code=source.slice(start,end).replace('private function','function').replace(/:(Array|Object|int|Number|String)\b/g,'');
code=code.replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
const context=vm.createContext({});
vm.runInContext('var mulliganSlots=[],requestCards=[],keyboardFocusId=0,mulliganPickedId=0;'+code,context);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
function run(ids){context.requestCards=ids.map(id=>({id}));return Array.from(context.mulliganCardsInPlace(),c=>c.id);}
const original=[10,9,8,7,6,5,4,3,2,1];
check(JSON.stringify(run(original))===JSON.stringify(original),'initial hand order');
check(JSON.stringify(run([...original].reverse()))===JSON.stringify(original),'frame order does not move cards');
context.keyboardFocusId=context.mulliganPickedId=7;
const next=original.filter(id=>id!==7).concat(999),result=run(next);
check(result[3]===999,'replacement remains in exchanged slot');
check(result.every((id,i)=>i===3||id===original[i]),'all other slots remain stable');
check(context.keyboardFocusId===999&&context.mulliganPickedId===999,'controller focus follows replacement');
for(const name of ['cycleHandSort','reverseHandSort']){
 const body=source.slice(source.indexOf('function '+name+'('),source.indexOf('function '+name+'(')+400);
 check(/if\([^;]*isMulliganHand\(\)\)return;/.test(body),'sort shortcut blocked during mulligan: '+name);
}
const aspectMatch=source.match(/BETA_CARD_ASPECT:Number\s*=\s*([^;]+);/);
if(!aspectMatch)throw Error('missing actual card aspect');
const aspect=vm.runInNewContext(aspectMatch[1]);
const count=10,rows=Math.ceil(count/5),cols=Math.ceil(count/rows),captionH=48;
const w=Math.floor(Math.min(240,(1380-(cols-1)*18)/cols,((704-(rows-1)*18)/rows-captionH)*aspect));
const h=Math.floor(w/aspect),bottom=190+(rows-1)*(h+captionH+18)+h+captionH;
check(rows===2&&cols===5,'ten cards use two rows of five');
check(bottom<978,'captions do not overlap the footer buttons');
const report={stage:121,checks,cols,rows,cardWidth:w,cardHeight:h,gridBottom:bottom,nativeVisualVerified:false};
fs.writeFileSync('docs/evidence/mulligan121.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
