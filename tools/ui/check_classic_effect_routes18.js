'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),base=path.resolve(root,process.argv[2]||'BetaGwent/build/classic081-effect-routes-fix18');
const previous=path.join(root,'BetaGwent/build/classic081-opacity-fix17');
const read=(b,n)=>fs.readFileSync(path.join(b,'ui/src',n),'utf8');let checks=0;
function check(v,s){assert(v,s);checks++;}
function extract(s,name){
 const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let i=b+1,d=1;
 for(;d;i++){if(s[i]==='{')d++;if(s[i]==='}')d--;}
 return s.slice(a,i).replace(/:(?:Event|Sprite|TextField|String|Object|void|int|uint|Number|Array|Boolean|ColorTransform|Bitmap|Class)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/:\*/g,'').replace(/ as (?:Sprite|Array|Bitmap|Class|TextField)\b/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
 .replace(/sprite is TextField/g,'sprite instanceof TextField')
 .replace(/BetaGwent(?:Element164|Status191|Burn143|Dissolve144)\(motion\.(\w+)\)/g,'motion.$1');
}
class Sprite{constructor(){Object.assign(this,{x:0,y:0,scaleX:1,scaleY:1,rotation:0,alpha:1,visible:true,children:[],transform:{}});}addChild(c){this.children.push(c);c.parent=this;return c;}removeChild(c){this.children.splice(this.children.indexOf(c),1);c.parent=null;}}
class TextField{}
const board=read(base,'BetaGwentBoard.as'),oldBoard=read(previous,'BetaGwentBoard.as');
function replay(s){
 const c=vm.createContext({Math,Number,Object,Sprite,TextField,getTimer:()=>0,
  reducedMotion:false,playing:true,animationStarted:0,animationOffset:0,animationRate:1,frameAnimationTempo:1,animationBaseDuration:1200,
  targetPulses:[],placementMotions:[],pendingImpacts:[],placementGhostAt:0,hoverPreviewAt:0,classicVisualSampled:true,
  updateAimPreview(){},updateActionPreview(){},tickUiMotions(){}});
 vm.runInContext((s.includes('function classicMotionAlpha(')?extract(s,'classicMotionAlpha'):'')+extract(s,'animateCardsBody'),c);return c;
}
const a=replay(oldBoard),b=replay(board);
for(let flags=0;flags<64;flags++)for(const reduced of [false,true])for(const time of [0,80,179,180,300,579,580,900]){
 const sprites=[];
 for(const c of [a,b]){
  const parent=new Sprite(),sprite=new Sprite();sprite.alpha=.63;parent.addChild(sprite);
  const motion={sprite,fromX:10,fromY:20,toX:90,toY:150,duration:400,delay:180,remove:true};
  if(flags&1){motion.fade=true;motion.fromAlpha=.72;}if(flags&2)motion.appear=true;
  if(flags&4)motion.scene=true;if(flags&8)motion.hideBeforeDelay=true;
  if(flags&16)motion.element164={render(p){this.progress=p;}};
  if(flags&32)motion.status191={render(p){this.progress=p;}};
  c.animations=[motion];c.reducedMotion=reduced;c.getTimer=()=>time;c.animateCardsBody(null);
  sprites.push({x:sprite.x,y:sprite.y,alpha:sprite.alpha,scaleX:sprite.scaleX,scaleY:sprite.scaleY,
   attached:!!sprite.parent,finished:!!motion.finished});
 }
 check(JSON.stringify(sprites[0])===JSON.stringify(sprites[1]),'shared replay appearance and lifecycle retained '+flags+'/'+reduced+'/'+time);
}
const engine=read(base,'BetaGwentElement164.as'),oldEngine=read(previous,'BetaGwentElement164.as');
function staticRenderer(s){const c=vm.createContext({Math,Number,Sprite,model:{duration:1},shafts:null,cells:[],intensity:1,travelPx:300});
 vm.runInContext((s.includes('function classicStaticTick(')?extract(s,'classicStaticTick'):'')+extract(s,'render'),c);return c;}
const sa=staticRenderer(oldEngine),sb=staticRenderer(engine);
for(const physical of [false,true])for(const trail of [false,true])for(const intensity of [.25,.45,.55,1])for(const alpha of [0,.2,1])for(const p of [0,.01,.08,.2,.5,.9,1]){
 const results=[];
 for(const c of [sa,sb]){const sprite=new Sprite();c.intensity=intensity;c.cells=[{sprite,static:{alpha},trail,physical,layout:{w:150}}];c.render(p);results.push({alpha:sprite.alpha,x:sprite.x,scaleX:sprite.scaleX});}
 check(JSON.stringify(results[0])===JSON.stringify(results[1]),'static arrow/mesh alpha and growing trail retained');
}
// The concrete tint helper used by impacts, stars, weather casts and frames.
function ColorTransform(...args){this.args=args;this.alphaMultiplier=args[3];}
const tint=vm.createContext({Sprite,ColorTransform,BetaGwentCardArt:{view:()=>new Sprite()}});
vm.runInContext(extract(board,'betaVisual'),tint);
for(const color of [0,0xFFFFFF,0x80A020]){const v=tint.betaVisual(1,80,100,color),args=v.transform.colorTransform.args;
 check(args.length===8&&args[3]===1&&args.slice(4).every(v=>v===0),'native tint keeps explicit full opacity');
 check(args[0]===((color>>16)&255)/255&&args[1]===((color>>8)&255)/255&&args[2]===(color&255)/255,'tint colour retained');}
const killSource=read(base,'BetaGwentKillArt144.as');
const kill=vm.createContext({Math,Number,String,Sprite,ColorTransform,ADDITIVE:JSON.parse(killSource.match(/ADDITIVE:Object=(\{[^;]+\});/)[1].replace(/(\d+):/g,'"$1":')),
 BetaGwentClassicEffects:{view:()=>new Sprite()}});
vm.runInContext(extract(killSource,'additive')+extract(killSource,'cell'),kill);
for(let index=0;index<48;index++)for(const light of [-1,0,1])for(const alpha of [0,.35,1]){
 const v=kill.cell(index,80,100,0x80A020,alpha,light);
 check(v.transform.colorTransform.args.length===8&&v.transform.colorTransform.alphaMultiplier===alpha,'kill effect retains explicit source alpha');
 check((v.blendMode==='add')===(light<0?kill.additive(index):light>0),'additive/alpha material choice retained for kill cells');
}
const banish=vm.createContext({Math,Number,Sprite,ColorTransform,HIT:0,BetaGwentClassicEffects:{view:()=>new Sprite()}});
vm.runInContext(extract(read(base,'BetaGwentBanish160.as'),'cell'),banish);
for(const kind of [0,1])for(let index=0;index<12;index++){
 const v=banish.cell(kind,index,80,100,.2,.4,.8,.3);
 check(v.transform.colorTransform.args.length===8&&v.transform.colorTransform.alphaMultiplier===1,'banish multiplier keeps explicit full alpha');
 check(v.children[0].x===-24&&v.children[0].y===-50&&v.blendMode!=='add','banish keeps pivot and AlphaBlended material');
}
let constructors=0;
for(const name of fs.readdirSync(path.join(base,'ui/src')).filter(n=>n.endsWith('.as'))){
 const s=read(base,name),marker='new ColorTransform(';let at=0;
 while((at=s.indexOf(marker,at))>=0){let d=1,n=0,i=at+marker.length,start=i;
  for(;d;i++){if(s[i]==='(')d++;else if(s[i]===')')d--;else if(s[i]===','&&d===1)n++;}
  const count=s.slice(start,i-1).trim()?n+1:0;check(count===8,'all native colour constructor arguments explicit '+name);constructors++;at=i;
 }
}
const entries=JSON.parse(fs.readFileSync(path.join(base,'subimages.json'),'utf8')).entries;
const priorEntries=JSON.parse(fs.readFileSync(path.join(previous,'subimages.json'),'utf8')).entries;
check(JSON.stringify(entries.slice(0,priorEntries.length))===JSON.stringify(priorEntries),'all existing native fragments retained');
const extra=entries.slice(priorEntries.length);check(extra.length===59,'28 lightning and 31 spell fragments');
const atlas={lightning_beta_png:'special144/lightning_beta.png',fire_png:'special143/fire.png',frame_png:'special143/frame.png',lightning_png:'special143/lightning.png',sparks_png:'special143/sparks.png'};
for(const row of extra){const png=fs.readFileSync(path.join(base,'ui/assets',atlas[row.atlas]));
 check(row.x>=0&&row.y>=0&&row.x+row.width<=png.readUInt32BE(16)&&row.y+row.height<=png.readUInt32BE(20),'native effect crop remains inside original pixels');}
const routes=[];
const native=vm.createContext({Math,Number,Sprite,int:v=>v|0,Bitmap:function(){throw Error('Unexpected legacy bitmap path');},BetaGwentClassicEffects:{view:(key,w,h)=>{routes.push(key);return new Sprite();}}});
vm.runInContext(extract(read(base,'BetaGwentLightning144.as'),'cell'),native);
for(let kind=0;kind<7;kind++)for(let frame=0;frame<4;frame++){
 const v=native.cell(kind,frame,80,120);check(v.scaleX===1&&v.scaleY===1&&v.children[0].x===-40&&v.children[0].y===-60,'approved lightning keeps centered unit-scale native view');
 check(routes.at(-1)==='lightning:'+kind+':'+frame,'exact lightning cell selected');
}
vm.runInContext(extract(read(base,'BetaGwentSpellArt143.as'),'clip'),native);
for(const [name,count] of [['fire',25],['frame',1],['lightning',1],['sparks',4]])for(let frame=0;frame<count;frame++){
 check(native.clip(name,90,130,frame) instanceof Sprite&&routes.at(-1)==='spell:'+name+':'+frame,'spell frame avoids atlas scrollRect');
}
// Preserve the accepted weather implementation, status curves and dissolve.
for(const name of ['classicWeatherOpacity','animateWeatherBody','advanceWeatherTextures','drawLightning143'])
 check(extract(board,name)===extract(oldBoard,name),'accepted method retained '+name);
for(const name of ['BetaGwentDissolve144.as','BetaGwentDissolveData144.as','BetaGwentStatus191.as','BetaGwentElementData164.as','BetaGwentElementBlend173.as'])
 check(fs.readFileSync(path.join(base,'ui/src',name)).equals(fs.readFileSync(path.join(previous,'ui/src',name))),'accepted data/source unchanged '+name);
const audit=fs.existsSync(path.join(base,'route-source-audit.json'))?base:path.join(root,'BetaGwent/build/classic081-effect-routes-fix18');
const changed=JSON.parse(fs.readFileSync(path.join(audit,'route-source-audit.json'),'utf8')).changedExistingSources;
for(const name of changed){const raw=fs.readFileSync(path.join(base,'ui/src',name));
 check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!raw.toString().replace(/\r\n/g,'').includes('\n'),'BOM/CRLF '+name);
 for(const folder of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])check(raw.equals(fs.readFileSync(path.join(base,'ui',folder,name))),'five copies '+name+'/'+folder);}
const report={checks,actualActionScript:true,explicitColorConstructorSites:constructors,replayFlagCombinations:64,staticProjectileParity:true,nativeLightningAndSpellRoutes:true,
 acceptedWeatherLightningMotionAndDissolveRetained:true,nativeClassicVerified:false};
fs.writeFileSync(path.join(base,'effect-routes-regression.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
