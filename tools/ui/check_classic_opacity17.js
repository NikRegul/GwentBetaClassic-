// Execute real opacity/particle methods, comparing all source recipes to fix16.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),base=path.resolve(root,process.argv[2]||'BetaGwent/build/classic081-opacity-fix17');
const read=n=>fs.readFileSync(path.join(base,'ui/src',n),'utf8');
const old=fs.readFileSync(path.join(root,'BetaGwent/build/classic081-effect-state-fix16/ui/src/BetaGwentElement164.as'),'utf8');
let checks=0;function check(v,s){assert(v,s);checks++;}
function extract(s,name){
 const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let i=b+1,d=1;
 for(;d;i++){if(s[i]==='{')d++;if(s[i]==='}')d--;}
 return s.slice(a,i).replace(/:(?:Event|Sprite|TextField|String|Object|void|int|uint|Number|Array|Boolean|ColorTransform)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/:\*/g,'').replace(/ as (?:Sprite|Array)\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))')
 .replace(/(\w+) is Number/g,"(typeof $1==='number')");
}
const engine=read('BetaGwentElement164.as'),data=read('BetaGwentElementData164.as');
const recipes=JSON.parse(fs.readFileSync(path.join(base,'ui/assets/elements164/recipes.json'),'utf8'));
const names=['random','sample','pick','rotate','colorKey','gradientValue','plan','spawn','packet','decoration'];
function model(source,extra=''){
 const c=vm.createContext({Math,Number,Object,String,Array,int:v=>v|0,uint:v=>v>>>0});
 vm.runInContext(extra+names.map(n=>extract(source,n)).join('\n'),c);return c;
}
const prior=model(old),current=model(engine,extract(engine,'classicChannel'));
for(const [name,preset] of Object.entries(recipes.presets)){
 const a=prior.plan(preset,173,64,preset.projectile?.38:0,120);
 const b=current.plan(preset,173,64,preset.projectile?.38:0,120);
 check(JSON.stringify(a)===JSON.stringify(b),'emission and movement retained '+name);
 for(let i=0;i<a.particles.length;i++)for(let t=0;t<a.duration;t+=.047){
  const before=prior.packet(a.particles[i],t,{}),after=current.packet(b.particles[i],t,{});
  check(JSON.stringify(before)===JSON.stringify(after),'all particle channels and poses retained '+name);
 }
}
function ColorTransform(...v){check(v.length===8,'all native constructor arguments explicit');
 [this.redMultiplier,this.greenMultiplier,this.blueMultiplier,this.alphaMultiplier,this.redOffset,this.greenOffset,this.blueOffset,this.alphaOffset]=v;}
const c=vm.createContext({Number,ColorTransform});vm.runInContext(extract(engine,'classicParticleColor'),c);
for(const alpha of [0,.01,.35,1])for(const strength of [.25,.45,.55,1])for(const small of [false,true])for(const progress of [0,.4,1]){
 const color=c.classicParticleColor({r:2,g:.5,b:.1,a:alpha},strength,small,progress);
 check(color.redMultiplier===2&&color.greenMultiplier===.5&&color.blueMultiplier===.1,'original RGB multipliers retained');
 const expected=small?alpha*strength*.45*(1-progress):alpha*strength;
 check(color.alphaMultiplier===expected,'source alpha and reduced mode retained');
 check(color.redOffset===0&&color.greenOffset===0&&color.blueOffset===0&&color.alphaOffset===0,'no added colour or alpha');
}
const board=read('BetaGwentBoard.as');
const w=vm.createContext({Math,Number,Object,int:v=>v|0,BetaGwentUi138:{intensity:1},BetaGwentBetaMotion:{sample:(n,p)=>p*p},getTimer:()=>5000,
 weatherFades:[],weatherEffects:[],reducedMotion:false,weatherRedrawAt:0,
 BetaGwentVisualTimings:{FROST_INTRO:.9333333373069763,FOG_INTRO:1.2000000476837158,RAIN_INTRO:1.1666666269302368},
 advanceWeatherTextures(){},drawBetaWeatherAccents(){}});
vm.runInContext(extract(board,'classicWeatherOpacity')+extract(board,'animateWeatherBody'),w);
for(const intensity of [.25,.55,1])for(const token of [1,2,4])for(const start of [0,4950,5100]){
 const operations=[],sprite={alpha:0,visible:false,graphics:{clear(){operations.push('clear');sprite.alpha=0;}}};
 w.BetaGwentUi138.intensity=intensity;w.weatherRedrawAt=0;
 const fx={sprite,token,start,nativeParts:[],beta:true};w.weatherEffects=[fx];w.animateWeatherBody(null);
 let expected=0;
 if(start<=5000){const intro=token===1?w.BetaGwentVisualTimings.FROST_INTRO:token===2?w.BetaGwentVisualTimings.FOG_INTRO:w.BetaGwentVisualTimings.RAIN_INTRO;
  expected=token===1?intensity:intensity*Math.pow(Math.min(1,(5000-start)/1000/intro),2);}
 check(sprite.alpha===expected,'weather opacity after graphics clear '+intensity+'/'+token+'/'+start);
 check(sprite.visible===(start<=5000),'future weather remains hidden');
 if(start<=5000)check(fx.expectedAlpha===expected,'expected opacity available to native diagnostics');
}
for(const name of ['BetaGwentBoard.as','BetaGwentElement164.as']){
 const raw=fs.readFileSync(path.join(base,'ui/src',name));
 check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!raw.toString().replace(/\r\n/g,'').includes('\n'),'BOM/CRLF '+name);
 for(const folder of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])
  check(raw.equals(fs.readFileSync(path.join(base,'ui',folder,name))),'five copies '+name+'/'+folder);
}
const report={checks,actualActionScript:true,particleRecipesCompared:Object.keys(recipes.presets).length,
 allParticlePosesAndChannelsPreserved:true,explicitTransformConstructor:true,weatherAlphaAssignedAfterClear:true,nativeClassicVerified:false};
fs.writeFileSync(path.join(base,'opacity-regression.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
