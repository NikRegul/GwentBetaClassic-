'use strict';
// Exercise the actual generated AS loader functions, including detached loads.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');let checks=0;
function check(ok,message){assert(ok,message);checks++;}
function fn(s,name){let a=s.indexOf('function '+name+'('),b=s.indexOf('{',a),n=1,i=b+1;assert(a>=0);
 for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|Event|TimerEvent|Function|Loader|Error)\b/g,'')
 .replace(/for each\(var (\w+) in (\w+)\)/g,'for(var $1 of $2)');}
class Dispatcher{constructor(){this.listeners={};}addEventListener(k,f){(this.listeners[k]??=[]).push(f);}removeEventListener(k,f){this.listeners[k]=(this.listeners[k]||[]).filter(x=>x!==f);}fire(k){for(const f of [...this.listeners[k]||[]])f({target:this,type:k});}}
class Sprite extends Dispatcher{constructor(){super();this.children=[];}addChild(c){this.children.push(c);c.parent=this;return c;}removeChild(c){this.children=this.children.filter(x=>x!==c);c.parent=null;c.fire('removed');}}
for(const platform of ['classic','nextgen']){
 const folder=path.join(root,'BetaGwent/build/'+(process.env.BG_UI||'release090-bannersUI'),platform,'ui');
 const source=fs.readFileSync(path.join(folder,'src/BetaGwentBanners090.as'),'utf8');
 const data=JSON.parse(source.match(/DATA:Object=(.*);/)[1]);
 check(Object.keys(data).length===18,'all 18 mesh variants');
 let loaders=[],unloads=0,inDispatch=false;
 class Loader extends Sprite{constructor(){super();this.contentLoaderInfo=new Dispatcher();loaders.push(this);}load(r){this.url=r.url;}unloadAndStop(force){check(!inDispatch&&!force,'deferred unload without forced collection');unloads++;}}
 class Timer extends Dispatcher{start(){}stop(){}}
 const c=vm.createContext({DATA:data,FACTIONS:{1:'Neutral',2:'Monsters',4:'Nilfgaard',8:'Northern',16:'Scoiatael',32:'Skellige'},live:0,retired:[],reaper:null,
  Sprite,Loader,Timer,URLRequest:function(url){this.url=url;},Event:{COMPLETE:'complete',REMOVED_FROM_STAGE:'removed'},TimerEvent:{TIMER:'timer'},IOErrorEvent:{IO_ERROR:'error'},SecurityErrorEvent:{SECURITY_ERROR:'security'},trace(){}});
 vm.runInContext(['key','paint','reap'].map(n=>fn(source,n)).join('\n'),c);
 for(const f of [1,2,4,8,16,32])for(const t of [1,2,4,8]){
  const key=c.key(f,t);check(!!data[key],'faction/tier exists');check(t!==1||key.endsWith('_Gold'),'leader uses Gold');check(t!==4||key.endsWith('_Silver'),'Silver stays Silver');}
 const parent=new Sprite();let fallback=0;
 check(c.paint(parent,2,8,468,670,()=>fallback++),'starts a native page');
 const holder=parent.children[0],d=data.Monsters_Gold;
 check(Math.abs(holder.scaleX*d[4]-d[2]*468)<1e-7&&Math.abs(holder.scaleY*d[5]-d[3]*670)<1e-7,'independent X/Y geometry matches mesh placement');
 check(loaders[0].url==='swf/betagwentbanners/'+(source.includes('name.toLowerCase()')?'monsters_gold':'Monsters_Gold')+'.swf','native depot URL');
 holder.fire('removed');c.reap(null);check(unloads===0&&c.live===1,'detached in-flight load is retained');
 inDispatch=true;loaders[0].contentLoaderInfo.fire('complete');inDispatch=false;
 check(unloads===0,'no unload in COMPLETE');c.reap(null);check(unloads===1&&c.live===0,'completed retired page released');
 for(let i=0;i<8;i++)check(c.paint(parent,1,4,100,140,()=>fallback++),'bounded request accepted');
 check(!c.paint(parent,1,4,100,140,()=>fallback++),'ninth in-flight page refused');
 const last=loaders.at(-1);inDispatch=true;last.contentLoaderInfo.fire('error');inDispatch=false;
 check(fallback===1&&unloads===1,'failure falls back once without synchronous unload');
 c.reap(null);check(c.live===7&&unloads===2,'failed page releases its allocation');
 for(const dir of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'])
  check(fs.readFileSync(path.join(folder,dir,'BetaGwentBanners090.as'),'utf8')===source,'five matching banner classes');
 const board=fs.readFileSync(path.join(folder,'src/BetaGwentBoard.as'),'utf8');
 check(board.includes('if(!big||!BetaGwentBanners090.paint')||board.includes('if(!big){paintArt(p,icon'),'small faces stay on existing atlas');
 check(board.includes('holder.scaleX=holder.scaleY')===false,'no blanket square scaling');
}
const result={uiBuild:process.env.BG_UI||'release090-bannersUI',checks,inGameVerified:false};
fs.writeFileSync(path.join(root,'docs/evidence/banners090-loader.json'),JSON.stringify(result,null,2));
console.log(JSON.stringify(result));
