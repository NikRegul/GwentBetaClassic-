// Exercise production initialization, weather opacity, particle limits and frames.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.join(root,'BetaGwent/build/classic081-effect-state-fix16');
const read=n=>fs.readFileSync(path.join(build,'ui/src',n),'utf8');let checks=0;
function check(v,s){assert(v,s);checks++;}
function extract(text,name){
 const start=text.indexOf('function '+name+'('),open=text.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end).replace(/:(?:Sprite|Bitmap|Class|Object|Array|String|Number|Boolean|Event|void|int|uint)\b(?!\s*\()/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
  .replace(/ as (?:Bitmap|Class|Sprite)\b/g,'');
}
function Sprite(){Object.assign(this,{children:[],x:0,y:0,scaleX:1,scaleY:1,alpha:1,visible:true,
 graphics:{clear(){},beginFill(){},endFill(){},drawRect(){}}});}
Sprite.prototype.addChild=function(c){this.children.push(c);c.parent=this;return c;};
Sprite.prototype.removeChild=function(c){this.children.splice(this.children.indexOf(c),1);c.parent=null;};
function state(initial){
 const c=vm.createContext({Math,Object,String,isFinite,Sprite,int:v=>v|0,uint:v=>v>>>0});
 Object.assign(c,{intensity:0,scenes:0,flashes:false,shake:false,chains:false,helpLabels:false,dynamicLeaders:false,classicInitialized:false,...initial});
 vm.runInContext(extract(read('BetaGwentUi138.as'),'initializeClassic'),c);return c;
}
// Match the native trace's zero opacity, even if multiple trait defaults start unset.
for(const initial of [{},{intensity:1,scenes:1,flashes:true}]){
 const c=state(initial),before=c.initializeClassic();
 check(c.intensity===1&&c.scenes===1&&c.flashes&&c.shake&&c.chains&&c.helpLabels&&c.dynamicLeaders,'explicit first initialization sets presentation defaults');
 check(c.classicInitialized&&before.includes(' -> intensity=1'),'initial state is diagnosable');
 c.intensity=.25;c.scenes=2;c.dynamicLeaders=false;c.flashes=false;c.initializeClassic();
 check(c.intensity===.25&&c.scenes===2&&!c.dynamicLeaders&&!c.flashes,'subsequent initialization preserves player choices and native settings');
}
const source=read('BetaGwentBoard.as');
const c=state();const weather=new Sprite();
Object.assign(c,{getTimer:()=>3000,weatherFades:[],weatherEffects:[{sprite:weather,token:1,start:1000,nativeParts:[],beta:true}],
 reducedMotion:false,weatherRedrawAt:0,BetaGwentUi138:c,BetaGwentVisualTimings:{FROST_INTRO:.9333333373069763,FOG_INTRO:1.2000000476837158,RAIN_INTRO:1.1666666269302368},advanceWeatherTextures(){},drawBetaWeatherAccents(){}});
vm.runInContext(extract(source,'animateWeatherBody'),c);c.animateWeatherBody(null);
check(weather.alpha===0,'observed zero setting reproduces invisible persistent frost');
c.initializeClassic();c.animateWeatherBody(null);
check(weather.alpha===1&&weather.visible,'same actual weather method displays frost after initialization');
c.intensity=.55;c.animateWeatherBody(null);check(weather.alpha===.55,'weather retains supported quieter brightness');
// Check the actual constructor guards without relying on the native slot/default parser.
const element=read('BetaGwentElement164.as');
for(const [strength,limit,expectedStrength,expectedLimit] of [[0,0,1,55],[NaN,NaN,1,55],[-1,-1,1,55],[.25,35,.25,35],[1,55,1,55]]){
 const children=[],preset={method:0,extent:[22,22],static:[]};
 const e=vm.createContext({Math,Object,isFinite,int:v=>v|0,Sprite,ColorTransform:function(){},
  BetaGwentElementData164:{preset:()=>preset},BetaGwentElementArt164:{cell:()=>new Sprite()},BetaGwentElementBlend173:{additive:()=>true},
  plan:()=>({duration:.6,particles:[{e:{tile:[0,0],id:1}}],preset}),cells:[],render(){},addChild:p=>children.push(p)});
 vm.runInContext(extract(element,'BetaGwentElement164')+extract(element,'classicMaxUnits'),e);
 e.BetaGwentElement164('PowerDirectPhysical',104,127,1,100,0,0,false,strength,limit);
 check(e.intensity===expectedStrength&&e.maxUnits===expectedLimit,'invalid particle strength/limit recovered; valid values preserved '+strength+'/'+limit);
 check(e.particleCount===1&&children[0].blendMode==='add','particle creation and material choice preserved');
 check(e.classicMaxUnits()===55,'max units initialized by executable code');
}
// All frames render with BitmapData deliberately unavailable, including page wrap.
const leader=fs.readFileSync(path.join(root,'tools/ui/leaders060/BetaLeaderMovieClassic.as'),'utf8');
function Bitmap(index){Object.assign(this,{index,width:192,height:234,parent:null});}
const frames=Array.from({length:24},(_,i)=>function(){return new Bitmap(i);});
const page=vm.createContext({Bitmap,Math,frames,previous:-1,shown:null,children:[],atlasLink:null});
page.addChild=p=>{page.children.push(p);p.parent=page;};page.removeChild=p=>{page.children.splice(page.children.indexOf(p),1);p.parent=null;};
vm.runInContext(extract(leader,'renderAt')+extract(leader,'release'),page);
for(const frame of [0,0,1,23,24,47,-1,48]){
 page.renderAt(frame);check(page.children.length===1&&page.shown.index===((frame%24)+24)%24,'native frame selection/wrap '+frame);
 check(page.shown.width===192&&page.shown.height===234,'native portrait dimensions');
}
page.release();check(page.children.length===0&&page.shown===null&&page.previous===-1,'leader releases references without disposing engine pixels');
check(!leader.includes('bitmapData')&&!leader.includes('beginBitmapFill')&&!leader.includes('scrollRect'),'leader frames need no unavailable pixel getter or atlas clipping');
for(const n of ['BetaGwentBoard.as','BetaGwentUi138.as','BetaGwentElement164.as']){
 const raw=fs.readFileSync(path.join(build,'ui/src',n));check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!raw.toString().replace(/\r\n/g,'').includes('\n'),'BOM/CRLF '+n);
 for(const d of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])check(raw.equals(fs.readFileSync(path.join(build,'ui',d,n))),'five copies '+n+'/'+d);
}
const report={checks,actualActionScript:true,zeroOpacityReproduced:true,explicitDefaultsVerified:true,validUserChoicesPreserved:true,
 nativeFramePlaybackWithoutBitmapData:true,nativeClassicVerified:false};
fs.writeFileSync(path.join(build,'effect-state-regression.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
