'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'BetaGwent/build/'+(process.env.BG_UI||'release090-ui9'));let checks=0;
function check(ok,msg){assert(ok,msg);checks++;}
function fn(s,name){let a=s.indexOf('function '+name+'('),b=s.indexOf('{',a),n=1,i=b+1;assert(a>=0,name);for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|MouseEvent|TimerEvent|Function|Loader|Error)\b/g,'').replace(/for each\(var (\w+) in (\w+)\)/g,'for(var $1 of $2)');}
class Dispatcher{constructor(){this.listeners={};}addEventListener(k,f){(this.listeners[k]??=[]).push(f);}removeEventListener(k,f){this.listeners[k]=(this.listeners[k]||[]).filter(x=>x!==f);}fire(k){for(const f of [...this.listeners[k]||[]])f({target:this,type:k});}}
class Sprite extends Dispatcher{constructor(){super();this.children=[];this.visible=true;this.scaleX=this.scaleY=1;}addChild(c){this.children.push(c);c.parent=this;return c;}removeChild(c){this.children=this.children.filter(x=>x!==c);c.parent=null;c.fire('removed');}}
for(const platform of ['classic','nextgen']){
 const folder=path.join(base,platform,'ui/src'),source=fs.readFileSync(path.join(folder,'BetaGwentBoard.as'),'utf8'),banner=fs.readFileSync(path.join(folder,'BetaGwentBanners090.as'),'utf8');
 const DATA=JSON.parse(banner.match(/DATA:Object=(.*);/)[1]),SLOTS=JSON.parse(banner.match(/SLOTS:Object=(.*);/)[1]);
 function host(faction=2,tier=2){
  let loaders=[],mode='pending';
  class Loader extends Sprite{constructor(){super();this.contentLoaderInfo=new Dispatcher();this.content={width:512,height:1024};loaders.push(this);}load(r){this.url=r.url;if(mode==='throw')throw Error('native load failed');if(mode==='sync')this.contentLoaderInfo.fire('complete');}unloadAndStop(){}}
  class Timer extends Dispatcher{start(){}stop(){}}
  const native=vm.createContext({DATA,SLOTS,FACTIONS:{1:'Neutral',2:'Monsters',4:'Nilfgaard',8:'Northern',16:'Scoiatael',32:'Skellige'},live:0,retired:[],reaper:null,Sprite,Loader,Timer,URLRequest:function(url){this.url=url;},Event:{COMPLETE:'complete',REMOVED_FROM_STAGE:'removed',ENTER_FRAME:'enterFrame'},lastError:'',TimerEvent:{TIMER:'timer'},IOErrorEvent:{IO_ERROR:'error'},SecurityErrorEvent:{SECURITY_ERROR:'security'},trace(){}});
  vm.runInContext(['key','slot','paint','reap'].map(n=>fn(banner,n)).join('\n'),native);
  const c=vm.createContext({trace(){},Sprite,int:Number,uint:Number,BETA_LARGE_CARD_ASPECT:15.85574533/22.7377556,selectingDecks:false,editingDeck:false,browsingCatalog:false,TextFormat:function(){},GlowFilter:function(){},BETA_CARD_ASPECT:17.64/21.46,leaderIds:[1,1],
   BetaGwentHDArt:{size(){return null;}},BetaGwentFullCatalog:{find(){return {faction,tier};}},BetaGwentCardText:{find(){return {typeMask:4};}},
   BetaGwentFonts:{NUMBERS:'Gwent Numbers',apply(field,face,size,color){field.fontSize=size;field.color=color;field.embedFonts=true;return true;}},
   paintArt(parent,id,w,h,x=0,y=0){const a=new Sprite();Object.assign(a,{id,width:w,height:h,x,y});parent.addChild(a);},attachLeaderMovie(){},cardFaction(){return 8;},
   BetaGwentBanners090:{slot(f,t){return native.slot(f,t);},paint(...args){return native.paint(...args);},get lastError(){return native.lastError;}},text(parent,text,x,y,width,size,color){const f={text,x,y,width,fontSize:size,color,scaleX:1};parent.addChild(f);return f;},
   centerBetaNumber(field,x,y,size){field.centerX=x;field.centerY=y;field.fontSize=size;},powerColor(){return 0x7df07d;},paintStaticCardState(){throw Error('side face complete');}});
  vm.runInContext(['betaBannerRect','paintBetaFace','betaPowerField','layoutBigPower090','betaBigPowerField','drawBetaSidePreview'].map(n=>fn(source,n)).join('\n'),c);
  return {c,native,loaders,setMode(value){mode=value;}};
 }
 for(const faction of [1,2,4,8,16,32])for(const tier of [1,2,4,8]){
  const h=host(faction,tier),p=new Sprite(),face=h.c.paintBetaFace(p,1,468,671,1,false,false,true);
  const power=h.c.betaBigPowerField(p,'17',468,671,0x7df07d,face),flag=p.children.at(-3),holder=p.children.at(-2);
  check(!face.large&&flag.visible&&!holder.visible,'pending native load keeps complete small face');
  check(power.x+power.width/2>468*.10&&power.x+power.width/2<468*.16,'pending number is on small flag');
  h.loaders[0].contentLoaderInfo.fire('complete');
  check(face.large&&!flag.visible&&holder.visible,'banner swaps only after real content is ready');
  const sl=h.native.slot(faction,tier);check(Math.abs(power.centerX-468*sl[0])<1e-9&&Math.abs(power.centerY-671*sl[1])<1e-9,'power moves onto the banner slot with it');
  if(faction===4)check(sl[0]<-0.03&&sl[1]>0.05,'Nilfgaard sun disc slot');
  check(p.children.indexOf(power)>p.children.indexOf(holder),'power remains above asynchronously loaded banner');
  check(power.text==='17'&&power.color===0x7df07d,'live power and boost colour preserved');
 }
 {const h=host(),p=new Sprite(),face=h.c.paintBetaFace(p,1,468,671,1,false,false,true),power=h.c.betaBigPowerField(p,'3',468,671,0xffffff,face);
  const holder=p.children.at(-2);h.loaders[0].content={width:0,height:0};h.loaders[0].contentLoaderInfo.fire('complete');
  check(!face.large&&!holder.visible,'unmeasured COMPLETE waits instead of failing');
  holder.fire('enterFrame');check(!face.large,'still waiting');h.loaders[0].content={width:512,height:1024};holder.fire('enterFrame');
  check(face.large&&holder.visible&&Math.abs(power.centerX-468*h.native.slot(2,2)[0])<1e-9,'late native texture swaps banner and power together');
  check(!(holder.listeners.enterFrame||[]).length,'poll listener removed after success');}
 {const h=host(),p=new Sprite(),face=h.c.paintBetaFace(p,1,468,671,1,false,false,true),power=h.c.betaBigPowerField(p,'3',468,671,0xffffff,face);
  const flag=p.children.at(-3),holder=p.children.at(-2);h.loaders[0].content={width:0,height:0};h.loaders[0].contentLoaderInfo.fire('complete');
  for(let i=0;i<90;i++)holder.fire('enterFrame');
  check(!face.large&&holder.parent==null&&h.native.lastError==='timeout Monsters_Bronze','timeout falls back with a reason');
  check(!flag.children.some(x=>String(x.text).startsWith('banner: ')),'no visible banner diagnostics');
  check(p.children.at(-1)===power,'diagnostic text never covers power');}
 for(const mode of ['error','security','empty','throw','limit','sync']){
  const h=host(),p=new Sprite();if(mode==='throw'||mode==='sync')h.setMode(mode);if(mode==='limit')h.native.live=8;
  const face=h.c.paintBetaFace(p,1,468,671,1,false,false,true),power=h.c.betaBigPowerField(p,'7',468,671,0xffffff,face);
  if(mode==='empty'){h.loaders[0].content=null;h.loaders[0].contentLoaderInfo.fire('complete');}
  if(mode==='error'||mode==='security')h.loaders[0].contentLoaderInfo.fire(mode);
  if(mode==='sync')check(face.large&&Math.abs(power.centerX-468*h.native.slot(2,2)[0])<1e-9,'synchronous completion before power creation handled');
  else{check(!face.large&&power.centerX===undefined,'failed/unavailable native banner never leaves big power position: '+mode);check(!p.children.some(c=>c.children&&c.children.some(x=>String(x.text).startsWith('banner: '))),'no failure text: '+mode);check(p.children.at(-1)===power,'fallback cannot append a flag on top of power: '+mode);}
 }
 const h=host(),p=new Sprite(),face=h.c.paintBetaFace(p,1,468,671,1,false,false,true);
 const power=h.c.betaBigPowerField(p,'5',468,671,0xffffff,face),holder=p.children.at(-2);holder.fire('removed');h.loaders[0].contentLoaderInfo.fire('complete');
 check(!face.large&&!holder.visible,'retired request cannot update closed card');h.native.reap(null);check(h.native.live===0,'retired completed load released');
 const battle=host(),parent=new Sprite();try{battle.c.drawBetaSidePreview({templateId:1,power:10,side:1},null,parent);}catch(e){assert(e.message==='side face complete',e.stack);}
 const card=parent.children[0],number=card.children.at(-1);
 check(!battle.loaders.length,'battle side preview no longer starts full-inspection banner loads');
 check(card.y===572-Math.round(312/(17.64/21.46)),'accepted side-preview card proportions restored');
 check(number.text==='10'&&number.x+number.width/2>312*.10,'battle power stays on visible blue/red flag');
 check(number.color===0x7df07d,'battle live power colour retained');
 check(source.includes('var face:Object=paintBetaFace(picture')&&source.includes('0xFFFFFF,face);'),'inspection wires the returned loading state to its power');
 {const deck=host();deck.c.selectingDecks=true;const parent=new Sprite();try{deck.c.drawBetaSidePreview({templateId:1,power:10,side:1},null,parent);}catch(e){assert(e.message==='side face complete',e.stack);}
  check(deck.loaders.length===1,'deck screen preview loads the big banner');deck.loaders[0].contentLoaderInfo.fire('complete');
  const n2=parent.children[0].children.find(x=>x.text==='10');check(n2&&n2.centerX!==undefined,'deck preview power follows the banner');}
 const canonical=fs.readFileSync(path.join(folder,'BetaGwentBoard.as'));
 for(const copy of ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']){
  const data=fs.readFileSync(path.join(base,platform,'ui',copy,'BetaGwentBoard.as'));
  check(data.equals(canonical)&&data.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(data.toString()),'BOM/CRLF mirror '+platform+'/'+copy);
 }
}
const report={checks,actualAS:true,asyncStates:['pending','complete','error','security','empty','throw','limit','sync','retired'],battlePreviewRestored:true,tolerantComplete:true,failureReason:true,inGameVerified:false};
fs.writeFileSync(path.join(base,'ui7-banner-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
