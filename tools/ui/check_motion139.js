// Run the production animation loop at several frame rates and replay speeds.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),assert=require('assert');
const file='BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
function extract(text,name){
 const start=text.indexOf('function '+name+'('),open=text.indexOf('{',start);assert(start>=0,name);
 let depth=1,end=open+1;for(;depth;end++){if(text[end]==='{')depth++;if(text[end]==='}')depth--;}
 return text.slice(start,end).replace(/:(Sprite|TextField|Event|String|Object|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))').replace(/sprite is TextField/g,'sprite instanceof TextField').replace(/sprite as TextField/g,'sprite');
}
class Sprite{constructor(){Object.assign(this,{x:0,y:0,scaleX:1,scaleY:1,rotation:0,alpha:1,children:[],graphics:new Proxy({},{get:()=>()=>{}})});}
 addChild(s){s.parent=this;this.children.push(s);return s;}
 removeChild(s){s.parent=null;this.children=this.children.filter(x=>x!==s);}}
class TextField extends Sprite{}
const c=vm.createContext({console,Math,Number,String,Object,Sprite,TextField,int:x=>x|0,getTimer:()=>c.now});
const curves=fs.readFileSync('BetaGwent/ui/src/BetaGwentBetaMotion.as','utf8');
const arrays=[...curves.matchAll(/private static const (\w+):Array=(\[[^;]+\]);/g)].map(m=>'var '+m[1]+'='+m[2]+';').join('\n');
vm.runInContext(arrays+extract(curves,'sample')+extract(curves,'duration')+`
var BetaGwentBetaMotion={sample,duration},BetaGwentUi138={shake:true},BetaGwentVisualTimings={FROST_INTRO:1,FOG_INTRO:1,RAIN_INTRO:1};
var now=0,animations=[],pendingImpacts=[],targetPulses=[],placementMotions=[],placementGhostAt=0,hoverPreviewAt=0;
var reducedMotion=false,playing=true,animationOffset=0,animationStarted=0,animationRate=1,frameAnimationTempo=1,animationTempo=1,animationBaseDuration=900,activeCue={kind:1};
function updateAimPreview(){}function updateActionPreview(){}function tickUiMotions(){}function showHoverPreview(){}function centerBetaNumber(){}
var weatherRows=[],previousPoses={},BetaGwentFullCatalog={find(){return null;}};function drawElement164(fx,name,x,y,w,h,delay){bursts.push([name,0,0,0,0,0,delay]);animations.push({sprite:new Sprite(),delay,duration:400});}function betaBurst(...a){bursts.push(a);}var bursts=[];function poseX(p){return p.x+p.width/2;}function poseY(p){return p.y+p.height/2;}function poseW(p){return p.width;}function poseH(p){return p.height;}
`+['queueCardFlip','animateCardsBody','cueImpactDelay','cueImpactTime','cueMinimumDuration','landingPrefab178','drawPresentation178','drawLandingCue','drawSummonCue'].map(n=>extract(source,n)).join('\n'),c);
let checks=0;function check(v,n){assert(v,n);checks++;}
for(const fps of [30,60,144])for(const tempo of [1,1.5,2])for(const rate of [1,4]){
 c.animations=[];c.reducedMotion=false;c.animationRate=rate;c.frameAnimationTempo=c.animationTempo=tempo;
 c.animationBaseDuration=900/tempo;c.animationStarted=0;c.animationOffset=0;c.now=0;
 const parent=new Sprite(),old=parent.addChild(new Sprite()),fresh=parent.addChild(new Sprite());fresh.x=old.x=400;fresh.y=old.y=200;
 c.queueCardFlip(old,fresh,100);
 for(let t=0;t<=450/(tempo*rate)+1000/fps;t+=1000/fps){
  c.now=t;c.animateCardsBody(null);
  check(Math.abs(fresh.x+fresh.scaleX*50-450)<1e-8,'flip center is stable');
  check(fresh.scaleX>0&&fresh.scaleX<=1,'flip scale stays positive');
  check(!(old.parent&&fresh.alpha>0),'new face stays hidden until old face closes');
 }
 c.now=1000;c.animateCardsBody(null);
 check(!old.parent&&fresh.x===400&&fresh.scaleX===1&&fresh.alpha===1,'flip ends at canonical pose '+fps+'/'+tempo+'/'+rate);
 // Summon ring, burst, sound and card arrival share a clock even in accelerated replay.
 for(const kind of [15,16]){
  c.now=0;c.activeCue={kind,source:1,target:2};c.animations=[];c.bursts=[];
  c.drawSummonCue(new Sprite(),{x:20,y:20,width:80,height:100},{x:400,y:200,width:80,height:100,zone:1,side:1,templateId:132308});
  const sound=c.cueImpactDelay(),arrival=420/(tempo*rate);
  check(Math.abs(sound-arrival)<1e-8,'summon sound at resolved flight arrival');
  check(c.animations.every(m=>Math.abs(m.delay/tempo/rate-arrival)<1e-8),'summon effects at arrival');
  check(Math.abs(c.bursts[0][6]/tempo/rate-arrival)<1e-8,'summon burst at arrival');
 }
}
c.reducedMotion=true;c.animations=[];c.now=0;c.animationStarted=0;c.animationRate=1;
const old=new Sprite(),fresh=new Sprite(),parent=new Sprite();parent.addChild(old);parent.addChild(fresh);fresh.x=300;
c.queueCardFlip(old,fresh,100);c.now=100;c.animateCardsBody(null);
check(fresh.x===300&&fresh.scaleX===1&&fresh.alpha===1&&!old.parent,'reduced motion finishes without leaving a narrow face');
check(c.cueImpactDelay()===0,'reduced motion has no delayed sound');
check(extract(source,'drawCards').includes('paintPlacementCard(fading,previous,'),'departures preserve complete public face or concealed back');
check(extract(source,'drawCards').includes('betaFlight:flight||relocation'),'row and ownership changes use curved movement');
check(extract(source,'drawCards').includes('drawPresentation178(content,"AmbushEffect",nextCards[c.id],180,48)'),'ambush particles use canonical layout before flip pivot offset');
const report={stage:139,checks,actualActionScript:true,nativeGameTested:false,sourceSha256:crypto.createHash('sha256').update(source).digest('hex')};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
