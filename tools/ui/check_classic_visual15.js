// Run actual AS methods against display-list bounds, not source-string mirrors.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),base=path.resolve(root,process.argv[2]||'BetaGwent/build/classic081-visual-fix15');
const read=n=>fs.readFileSync(path.join(base,'ui/src',n),'utf8');
const source=read('BetaGwentBoard.as'),hd=read('BetaGwentHDArt.as');
let checks=0;function check(v,label){assert(v,label);checks++;}
function extract(text,name){
 const start=text.indexOf('function '+name+'('),open=text.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end)
  .replace(/:(?:Sprite|BitmapData|Bitmap|Class|Object|Array|String|Number|Boolean|Rectangle|Matrix|TextField|Event|Error|void|int|uint)\b(?!\s*\()/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
  .replace(/ as (?:Sprite|BitmapData|Bitmap|Class|Array|TextField)\b/g,'')
  .replace(/sprite is TextField/g,'sprite instanceof TextField');
}
function Rectangle(x,y,w,h){Object.assign(this,{x,y,width:w,height:h});}
function Sprite(){Object.assign(this,{x:0,y:0,scaleX:1,scaleY:1,rotation:0,alpha:1,visible:true,children:[],scrollRect:null,
 graphics:{rect:null,lineStyle(){},beginFill(){},endFill(){},clear(){},drawRect(x,y,w,h){this.rect={x,y,width:w,height:h};}}});}
Sprite.prototype.addChild=function(c){this.children.push(c);c.parent=this;return c;};
Sprite.prototype.removeChild=function(c){this.children.splice(this.children.indexOf(c),1);c.parent=null;};
Object.defineProperties(Sprite.prototype,{
 width:{get(){const n=this.scrollRect?this.scrollRect.width:this.children.length?Math.max(...this.children.map(c=>c.x+c.width))-Math.min(...this.children.map(c=>c.x)):this.graphics.rect?.width||0;return Math.abs(this.scaleX)*n;}},
 height:{get(){const n=this.scrollRect?this.scrollRect.height:this.children.length?Math.max(...this.children.map(c=>c.y+c.height))-Math.min(...this.children.map(c=>c.y)):this.graphics.rect?.height||0;return Math.abs(this.scaleY)*n;}},
 numChildren:{get(){return this.children.length;}}
});
function Bitmap(w=128,h=128){Object.assign(this,{x:0,y:0,scaleX:1,scaleY:1,naturalW:w,naturalH:h,bitmapData:null});}
Object.defineProperties(Bitmap.prototype,{width:{get(){return this.naturalW*Math.abs(this.scaleX);}},height:{get(){return this.naturalH*Math.abs(this.scaleY);}}});
class BitmapData{};class Matrix{};class TextField{};
function runClip(text,route,w,h){
 const dims=route==='fragment'?[1024,96]:[3072,2655];
 const type=function(){return new Bitmap(...dims);};
 const c=vm.createContext({Math,Number,Object,Sprite,Bitmap,BitmapData,Matrix,Rectangle});
 Object.assign(c,{slots:{7:route==='fragment'?[19,0,0,1024,96]:[9,0,0,2048,708]},has:()=>true,
  shared:[],nativeUI:route==='native'?{9:true}:{},types:{9:type,19:type},lastError:'',reportAtlas:()=>{},
  BetaGwentClassicSubImages:{find:()=>route==='fragment'?type:null}});
 const methods=(text.includes('function unitView(')?extract(text,'unitView'):'')+extract(text,'clip');
 vm.runInContext(methods,c);const result=c.clip(7,w,h,0,0,route==='fragment'?1024:2048,route==='fragment'?96:708);
 assert(result,c.lastError);return result;
}
for(const route of ['fragment','native','fallback'])for(const [w,h] of [[1427,492.4],[904.5,118.1],[30,48],[1,1]]){
 const v=runClip(hd,route,w,h);
 check(v.scaleX===1&&v.scaleY===1,'public view has unit scale '+route+'/'+w);
 check(Math.abs(v.width-w)<.00001&&Math.abs(v.height-h)<.00001,'requested bounds preserved '+route+'/'+w);
 v.scaleX=-1;check(Math.abs(v.width-w)<.00001,'mirror preserves fitted width '+route+'/'+w);
 v.scaleX=1.7;v.scaleY=1.7;
 check(Math.abs(v.width-w*1.7)<.00001&&Math.abs(v.height-h*1.7)<.00001,'animation scale multiplies requested size '+route+'/'+w);
}
const prior=fs.readFileSync(path.join(root,'BetaGwent/build/classic081-geometry-effects-fix14/ui/src/BetaGwentHDArt.as'),'utf8');
const broken=runClip(prior,'fallback',1427,492.4);broken.scaleX=-1;
check(Math.abs(broken.width-1536)<.00001&&broken.width!==1427,'old mirror reproduces the wider board behind displaced score sockets');
// Native particle cells obey the same public contract at both unit and card size.
const effects=read('BetaGwentClassicEffects.as');
for(const [w,h] of [[1,1],[104,127],[400,118]]){
 const c=vm.createContext({Sprite,Bitmap,classes:{cell:function(){return new Bitmap(128,128);}}});
 vm.runInContext(extract(effects,'view'),c);const v=c.view('cell',w,h);
 check(v.scaleX===1&&v.scaleY===1&&v.width===w&&v.height===h,'particle view retains intrinsic fitting '+w);
}
// Simulate 900 ms spent constructing a frame: the displayed hit still gets its
// own 240 ms after construction, and a new weather birth follows the same clock.
const clock=vm.createContext({Math,Object,Sprite,TextField,getTimer:()=>1000});
const fresh={key:'2:1',start:100},persistent={key:'2:2',start:50},future={key:'2:4',start:2100};
Object.assign(clock,{animationStarted:100,frameDuration:930,frameDeadline:1030,playing:true,activeCue:null,
 weatherEffects:[fresh,persistent,future],weatherBirths:{'2:1':{start:100},'2:2':{start:50},'2:4':{start:2100}},reportClassicVisualState:()=>{},cueImpactDelay:()=>0});
vm.runInContext(extract(source,'finishClassicVisualRender'),clock);clock.finishClassicVisualRender();
check(clock.animationStarted===1000&&clock.frameDeadline===1930,'replay deadline excludes construction');
check(fresh.start===1000&&persistent.start===50&&future.start===3000,'only births in this rendered frame are rebased');
check(clock.weatherBirths['2:1'].start===1000&&clock.weatherBirths['2:2'].start===50,'birth cache stays consistent');
const p=new Sprite();Object.assign(clock,{getTimer:()=>1020,animationOffset:0,animationRate:1,frameAnimationTempo:1,
 animationBaseDuration:930,reducedMotion:false,pendingImpacts:[],targetPulses:[],placementMotions:[],placementGhostAt:0,
 hoverPreviewAt:0,updateAimPreview(){},updateActionPreview(){},tickUiMotions(){},
 animations:[{sprite:p,fromX:0,fromY:0,toX:10,toY:10,fade:true,duration:240}],classicVisualSampled:false});
vm.runInContext((source.includes('function classicMotionAlpha(')?extract(source,'classicMotionAlpha'):'')+extract(source,'animateCardsBody'),clock);clock.animateCardsBody(null);
check(p.alpha>0&&p.alpha<1&&!clock.animations[0].finished,'actual animation method shows short hit after slow construction');
// The same drawRows implementation must retain a bounded weather mask without
// submitting its atlas subtree through Classic's unreliable scrollRect route.
const layoutText=read('BetaGwentBoardLayout.as');const layout={};
for(const n of ['rowScore','rows'])layout[n]=JSON.parse(layoutText.match(new RegExp('const '+n+':Object=(\\{.*?\\});'))[1]);
const c=vm.createContext({Math,Object,String,Sprite,Rectangle,TextFormat:function(){},GlowFilter:function(){},int:v=>v|0});
Object.assign(c,{skin:3,content:new Sprite(),cards:[],weatherRows:[{side:2,zone:1,token:1,damage:2}],weatherBirths:{},weatherEffects:[],
 animationStarted:100,reducedMotion:false,activeCue:null,frameAnimationTempo:1,animationRate:1,focusedRow:0,focusedSide:0,
 playing:false,displayedCards:{},BetaGwentBoardLayout:layout,BetaGwentWeather107:{FROST_COVER:-1950},BetaGwentHDArt:{has:()=>true},
 BetaGwentFonts:{NUMBERS:'numbers',apply:()=>true},rowGeometry:(side,zone)=>{const a=layout.rows[side+':'+zone];return{x:a[0],y:a[1],w:a[2],h:a[3]};},
 rowEnabled:()=>false,halfCastSide:()=>0,attachRow(){},drawHalfCast(){},text:()=>({}),centerBetaNumber(){},
 prepareBetaWeather:fx=>{fx.nativeParts=[];}});
vm.runInContext(extract(source,'drawRows'),c);c.drawRows();
const row=c.weatherEffects[0].sprite;
check(row.scrollRect===null&&row.mask instanceof Sprite,'row weather uses a vector mask');
check(row.mask.graphics.rect.width===904.5&&row.mask.graphics.rect.height===118.1,'weather clipping remains the exact row rectangle');
const raw=fs.readFileSync(path.join(base,'ui/src/BetaGwentBoard.as'));
check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!raw.toString().replace(/\r\n/g,'').includes('\n'),'BOM and CRLF retained');
for(const d of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])check(raw.equals(fs.readFileSync(path.join(base,'ui',d,'BetaGwentBoard.as'))),'mirror '+d);
const report={checks,actualActionScriptMethods:true,publicArtUnitScale:true,mirrorRegressionReproduced:true,
 shortAnimationSurvivesConstruction:true,weatherBoundaryPreserved:true,nativeClassicVerified:false};
fs.writeFileSync(path.join(base,'visual-regression.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
