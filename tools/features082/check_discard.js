'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const root=path.resolve(__dirname,'../..'),build=path.join(root,'BetaGwent/build/release082-rc1');
let checks=0;const check=(v,n)=>{assert(v,n);checks++;};
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let d=1,i=b+1;for(;d;i++){if(s[i]==='{')d++;if(s[i]==='}')d--;}
 return s.slice(a,i).replace(/:(?:int|Number|Object|Sprite|void|Boolean|Array)\b(?=\s*[,)=;{])/g,'');}
class Sprite{addChild(s){s.parent=this;return s;}}
for(const platform of ['classic','nextgen']){
 const s=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const c=vm.createContext({Sprite,int:v=>v|0,skin:3,incoming:{destinations:{}},activeCue:{target:17,targetView:{templateId:113101}},cardDestinations082:{},animations:[],paintPlacementCard(){},betaPilePoint:(side,grave)=>{assert(grave);return side===1?[1560,810]:[1560,120];}});
 vm.runInContext(fn(s,'pushCardDestination')+'\n'+fn(s,'drawResolvedSpecial082'),c);
 for(const side of [1,2]){
  c.pushCardDestination(17,side,32);c.cardDestinations082=c.incoming.destinations;c.animations=[];c.drawResolvedSpecial082(new Sprite());
  const a=c.animations[0];check(c.animations.length===1&&a.toX===1560&&a.toY===(side===1?810:120),'own graveyard for each player');
  check(a.duration===400&&a.toScaleX===80/136&&a.toScaleY===110/204,'card arrives at pile size');
 }
 for(const zone of [512,8,16,64,256]){
  c.incoming.destinations={};c.pushCardDestination(17,1,zone);c.cardDestinations082=c.incoming.destinations;c.animations=[];c.drawResolvedSpecial082(new Sprite());
  check(c.animations.length===0,'only a resolved special in actual graveyard flies to discard');
  if(zone!==512)check(!c.cardDestinations082[17],'hidden hand/deck destinations rejected');
 }
 c.activeCue.targetView=null;c.cardDestinations082={17:{side:1,zone:32}};c.animations=[];c.drawResolvedSpecial082(new Sprite());check(!c.animations.length,'missing target never invents a card');
 const raw=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'));
 for(const directory of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])check(raw.equals(fs.readFileSync(path.join(build,platform,'ui',directory,'BetaGwentBoard.as'))),'five matching platform mirrors');
 check(raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'BOM CRLF preserved');
 // The accepted dissolve, weather and lightning methods must remain byte-for-byte equal.
 if(platform==='classic'){
  const old=fs.readFileSync(path.join(root,'BetaGwent/build/classic081-effect-routes-fix18/ui/src/BetaGwentBoard.as'),'utf8');
  for(const name of ['drawDissolveDeparture','drawBanishDeparture','animateWeather','classicMotionAlpha','classicCueOpacity'])check(fn(s,name)===fn(old,name),'accepted '+name+' unchanged');
 }
}
const report={checks,actualActionScript:true,gameplayVerified:false};
fs.writeFileSync(path.join(build,'discard-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
