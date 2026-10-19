// Compare complete production enemy-hand rendering before/after tracer isolation.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'../..');
const raw=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentBoard.as'));
const source=raw.toString('utf8');
const prior=fs.readFileSync(path.join(root,'BetaGwent/build/stage198/common/ui/src/BetaGwentBoard.as'),'utf8');
function extract(text,name){
 const start=text.indexOf('function '+name+'('),open=text.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end).replace(/:(?:Sprite|Object|Array|String|Number|Boolean|void|int|uint)\b/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');
}
let checks=0;function check(value,label){assert(value,label);checks++;}
function Sprite(){this.children=[];this.x=0;this.y=0;this.scaleX=1;this.scaleY=1;this.alpha=1;}
Sprite.prototype.addChild=function(child){this.children.push(child);};
function run(text,fixture,fixed){
 const c=vm.createContext({Math,Object,String,Sprite,JSON});
 Object.assign(c,JSON.parse(JSON.stringify(fixture)),{BETA_CARD_ASPECT:22/30,content:new Sprite(),animations:[],calls:[]});
 vm.runInContext(`
 function paintBetaFace(p,id,w,h,side){calls.push(['face',id,w,h,side]);}
 function betaPowerField(p,power,w,h,color){calls.push(['power',power,w,h,color]);}
 function powerColor(c){return c.power>4?1:2;}
 function paintChoiceArt(p,id,w,h){calls.push(['choice',id,w,h]);}
 function text(p,power,x,y,w,h,color){calls.push(['text',power,x,y,w,h,color]);}
 function attachInspect(p,c,detail,w,h){calls.push(['inspect',c.id,detail,w,h]);}
 function paintCardBack(p,w,h,side){calls.push(['back',w,h,side]);}
 function betaDeckPoint(side){return [310,426];}
 function drawCardStatuses191(p,before,after,w,h){calls.push(['status',before||null,after,w,h]);}
 `+(fixed?['enemyHandView191','drawEnemyHandStatuses191'].map(n=>extract(text,n)).join('\n'):'')+extract(text,'drawBacks'),c);
 c.drawBacks();
 return JSON.parse(JSON.stringify({calls:c.calls,cache:c.enemyHandStatuses191,children:c.content.children,animations:c.animations}));
}
const card=(id,index,tokens=0)=>({id,index,tokens,templateId:132308,power:4,side:2,zone:8,timer:2});
const fixtures=[
 {enemyHand:0,cards:[]},
 {enemyHand:1,cards:[card(1,0)]},
 {enemyHand:1,cards:[card(1,0,64|1)]},
 {enemyHand:1,cards:[card(1,0,64)],enemyHandStatuses191:{1:card(1,0,0)}},
 {enemyHand:1,cards:[card(1,0)],enemyHandStatuses191:{1:card(1,0,64)},activeCue:{kind:8,target:1}},
 {enemyHand:1,cards:[],enemyHandStatuses191:{1:card(1,0,64)},activeCue:{kind:8,target:1}},
 {enemyHand:1,cards:[],enemyHandStatuses191:{1:card(1,4,64)},activeCue:{kind:8,target:1}},
 {enemyHand:1,cards:[],enemyHandStatuses191:{1:card(1,0,64)},activeCue:{kind:2,target:1}},
 {enemyHand:3,cards:[{...card(9,0,64),side:1},{...card(8,1,64),zone:16},card(3,2,128)]},
 ...[1,2,10,20].flatMap(count=>[
  {enemyHand:count,cards:Array.from({length:count},(_,i)=>card(i+1,i,i%3===0?64|1:0))},
  {enemyHand:count,cards:Array.from({length:count},(_,i)=>card(i+1,i)),previousEnemyHand:Math.max(0,count-2),activeCue:{kind:14}}
 ])
];
for(const skin of [1,2,3])for(const reducedMotion of [false,true])for(const [i,item] of fixtures.entries()){
 const fixture={skin,reducedMotion,enemyHand:0,previousEnemyHand:0,cards:[],enemyHandStatuses191:{},activeCue:null,cardDetails:{},...item};
 assert.deepStrictEqual(run(source,fixture,true),run(prior,fixture,false),'render/cache parity '+skin+'/'+reducedMotion+'/'+i);checks++;
}
const body=extract(source,'drawBacks');
check((body.match(/Object.values\(cards/g)||[]).length===1,'drawBacks retains only the original exposed-card loop');
check(!body.includes('break')&&!body.includes('var enemyView')&&!body.includes('var priorHand191'),'optional lookup and break no longer belong to drawBacks');
check(!extract(source,'enemyHandView191').includes('break'),'lookup uses small guarded returns');
check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!source.replace(/\r\n/g,'').includes('\n'),'BOM and CRLF preserved');
for(const folder of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])check(raw.equals(fs.readFileSync(path.join(root,'BetaGwent/ui',folder,'BetaGwentBoard.as'))),'mirror '+folder);
console.log(JSON.stringify({stage:200,checks,completeRenderParity:true,actualActionScript:true,nativeGameTested:false}));
