// Execute controller and overview methods extracted from the actual ActionScript.
'use strict';
const fs=require('fs'),vm=require('vm');
const controller=fs.readFileSync('BetaGwent/ui/src/BetaGwentController.as','utf8');
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(source,name){
 const start=source.indexOf('function '+name+'(');if(start<0)throw Error(name);
 const open=source.indexOf('{',start);let depth=1,end=open+1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(DisplayObject|String|Function|Object|Rectangle|void|int|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
const context=vm.createContext({Math,Number});
vm.runInContext(`var movementAt=-1000,dirty=false,nodes=[],focus=null,chosen=null;
function int(v){return v|0;}function getTimer(){return 1000;}function getFocus(){return focus;}function candidates(){return nodes;}
var currentMode='inspect',layers=[];function state(){return {mode:currentMode,baseMode:'choice',layers};}
function select(n){chosen=n;}function invoke(){}function prune(){}function bodyBounds(n){return n.sprite.rect;}
`+extract(controller,'navigate')+'\n'+extract(controller,'registerControl')+'\n'+extract(board,'overviewLayout'),context);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
function node(x,y,tag='card'){return {tag,rect:{x,y,width:110,height:130}};}
function move(from,options,dir,mode='inspect'){context.focus=from;context.nodes=[from,...options];context.chosen=null;context.currentMode=mode;context.movementAt=-1000;context.navigate(dir);return context.chosen;}
const top=node(900,100),middle=node(0,250),bottom=node(900,400);
check(move(top,[middle,bottom],40)===middle,'down reaches sparse middle row before aligned bottom row');
check(move(bottom,[top,middle],38)===middle,'up reaches sparse middle row before aligned top row');
const left=node(500,100),right=node(1030,100);
check(move(top,[middle,bottom,right,left],39)===right,'right moves within row');
const yes=node(720,550,'control'),no=node(1000,550,'control');
check(move(yes,[no],39,'confirm')===no,'confirmation buttons remain reachable horizontally');
check(move(no,[yes],37,'confirm')===yes,'confirmation returns to Yes');
context.nodes=[];const sprite={rect:{x:720,y:550,width:200,height:48}};
context.layers=[{root:{contains:()=>true},mode:'choice'},{root:{contains:()=>true},mode:'confirm'},{root:null,mode:'detail'}];
context.registerControl(sprite,'Yes');
check(context.nodes[0].scope==='confirm','nested mulligan confirmation registers in confirm scope');
context.layers=[{root:{contains:()=>false},mode:'choice'}];
context.registerControl({rect:{x:720,y:978,width:300,height:48}},'Return');
check(context.nodes[1].scope==='choice','ordinary control uses base scope');
const aspect=board.match(/BETA_CARD_ASPECT:Number\s*=\s*([^;]+);/)[1];
context.BETA_CARD_ASPECT=vm.runInNewContext(aspect);
for(let count=1;count<=10;count++){
 const l=context.overviewLayout(count,1380,704,5,240,48);
 check(l.cols<=5&&l.rows<=2&&190+l.blockH<932,'ability choice fits above footer count='+count);
 if(count===10)check(l.rows===2&&l.cols===5,'ten options are two rows of five');
}
const toggle=extract(board,'toggleChoiceTable');
check(/abilityHidden=!abilityHidden/.test(toggle)&&!/requestAction/.test(toggle),'peek toggles the view without resolving a pending ability');
const report={stage:123,checks,actualActionScript:true,nativeControllerTested:false};
fs.writeFileSync('docs/evidence/controller123.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
