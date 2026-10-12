// Execute production AS functions with deterministic Flash stubs.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
let checks=0;function check(value,label){if(!value)throw Error(label);checks++;}
function extract(source,name){
 const at=source.indexOf('function '+name+'(');if(at<0)throw Error(name);
 const start=source.indexOf('{',at);let end=start+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(?:String|Object|void|int|Number|Array|Boolean|TextField|TextFormat|Event|TimerEvent|Sprite|BetaGwentLeaderPreview|Error|Loader)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)').replace(/\b([A-Za-z]+) as TextField\b/g,'$1');
}
const textPath='BetaGwent/ui/src/BetaGwentTextLanguage.as',text=fs.readFileSync(textPath,'utf8');
const codes=['','ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw'];
const en={};for(const row of fs.readFileSync('BetaGwent/ui/src/BetaGwentTextData.as','utf8').matchAll(/o\[("(?:\\.|[^"\\])*")\]=("(?:\\.|[^"\\])*");/g)){const key=JSON.parse(row[1]);if(!Object.hasOwn(en,key))en[key]=JSON.parse(row[2]);}
class EventSource{addEventListener(){}removeEventListener(){}}
let requests=[],unloads=0;
class Loader{constructor(){this.contentLoaderInfo=new EventSource();this.content={};}load(request){this.url=request.url;requests.push(this);}close(){}unloadAndStop(){unloads++;}}
const common={Loader,Object,URLRequest:class{constructor(url){this.url=url;}},Event:{COMPLETE:'complete'},IOErrorEvent:{IO_ERROR:'io'},SecurityErrorEvent:{SECURITY_ERROR:'security'},
 BetaGwentFonts:{BODY:'PF Din Text Cond Pro',TITLE:'Halis GR',NUMBERS:'Gwent Numbers'}};
const c=vm.createContext({...common,console,trace(){}});
vm.runInContext('var DEFAULT_LANGUAGE=1,language=1,pendingLanguage=0,fields={},maps,groups,protectedNames={},caches=[],cacheCount=0,resourceLoader=null,pendingLoader=null,bodyFont=null,titleFont=null,fontCharacters="",changed=null;var CODES='+JSON.stringify(codes)+',LABELS='+JSON.stringify(codes)+';'+
 ['initialize','indexLanguage','longest','word','translate','protect','track','forget','update','font','hasGlyphs','refresh','select','languageLoaded','languageFailed','label','search'].map(n=>extract(text,n)).join('\n'),c);
for(let id=1;id<=13;id++){
 const locale=codes[id];let data=id===1?{}:id===2?en:JSON.parse(fs.readFileSync('BetaGwent/build/languages137/ui/'+locale+'.json','utf8'));
 data={...data,...Object.fromEntries(Object.entries(data).map(([k,v])=>[k.toUpperCase(),v.toUpperCase()]))};
 c.select(id);const loading=c.pendingLoader;
 check(loading.url==='swf/betagwenttext/'+locale+'.swf','selected locale path '+locale);
 const built=fs.readFileSync('BetaGwent/build/text137/'+locale+'/BetaLocale137.as','utf8');
 loading.content={dictionary:()=>data,bodyFont:'Body_'+locale,titleFont:'Title_'+locale,characters:JSON.parse(built.match(/public var characters:String=("(?:\\.|[^"\\])*");/)[1])};
 c.languageLoaded({currentTarget:loading.contentLoaderInfo});
 check(c.translate('Выбрать карту')===(data['Выбрать карту']||'Выбрать карту'),'actual translation '+locale);
 check(c.translate('Выбрать карту · 12')===(data['Выбрать карту']||'Выбрать карту')+' · 12','translated dynamic count '+locale);
 check(c.translate('XВыбрать картуZ')==='XВыбрать картуZ','word boundary '+locale);
 const field={text:'Выбрать карту',type:'dynamic',stage:true,embedFonts:false,scrollV:3,toString:()=>locale,
  getTextFormat(){return this.format||{font:'Halis GR',size:24,color:1};},setTextFormat(f){this.format=f;}};
 c.track(field);
 check(field.text===(data['Выбрать карту']||'Выбрать карту'),'field translation '+locale);
 check(field.format.font==='Title_'+locale&&field.format.bold&&field.scrollV===3,'font/format/scroll '+locale);
 check(Object.keys(c.maps).filter(k=>Number(k)!==id).every(k=>Object.keys(c.maps[k]).length===0),'only selected dictionary retained '+locale);
 check(c.search('Выбрать карту',field.text.toLowerCase()),'localized search '+locale);
 c.forget(field);
}
c.protect('Выбрать карту');check(c.translate('«Выбрать карту» · 12')==='«Выбрать карту» · 12','opaque saved names');
const input={type:'input',text:'Выбрать карту'};c.track(input);check(input.text==='Выбрать карту','input unchanged');
c.select(3);const stale=c.pendingLoader;c.select(5);const current=c.pendingLoader;
c.languageLoaded({currentTarget:stale.contentLoaderInfo});check(c.pendingLoader===current,'stale async language completion ignored');
check(c.language===13,'selection stays atomic while loading');
c.languageFailed({currentTarget:current.contentLoaderInfo});check(c.pendingLoader===null&&c.language===13&&c.pendingLanguage===0,'missing language resource retains actual selection');
check(unloads>=12,'old language resources unloaded');
const bridge=fs.readFileSync('BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws','utf8');
check(bridge.includes('if(language<1||language>13)return false;')&&bridge.includes('FactsSet("bg_text_language",language)'),'13-language setting saved with Bool guard');

const previewPath='BetaGwent/ui/src/BetaGwentLeaderPreview.as',preview=fs.readFileSync(previewPath,'utf8');
function playback(){
 let time=7500,loads=[],disposed=0,closed=0,rendered=[];
 class Page extends Loader{constructor(){super();this.content={renderAt:f=>rendered.push(f),release(){}};}load(r){loads.push(this);this.url=r.url;}close(){closed++;}unloadAndStop(){disposed++;}}
 class Timer extends EventSource{start(){}stop(){}}
 const ctx=vm.createContext({...common,Loader:Page,Timer,TimerEvent:{TIMER_COMPLETE:'timer'},int:Math.trunc,getTimer:()=>time,
  Event:{ENTER_FRAME:'tick',ADDED_TO_STAGE:'added',REMOVED_FROM_STAGE:'removed',COMPLETE:'complete'},
  BetaGwentLeaderCatalog:{info:()=>({duration:17,frames:408,pages:17}),path:(id,page)=>'leader/'+page},
  stage:{},parent:null,addEventListener(){},removeEventListener(){},addChild(l){l.parent={removeChild(){}};}});
 vm.runInContext('var cardId=0,metadata=null,slots={},failedPages={},shown=null,delay=null,disposed=false,started=false,portraitWidth=0,portraitHeight=0,scaleX=1,scaleY=1,graveyard=[],reaper=null,livePages=0,MAX_LIVE_PAGES=12;'+
 ['BetaGwentLeaderPreview','resize','frameAt','stopDelay','begin','added','removed','request','tick','entryFor','loaded','failed','releasePage','dispose','retire','reap'].map(n=>extract(preview,n)).join('\n'),ctx);
 return {ctx,loads,rendered,time:t=>{time=t;},disposed:()=>disposed,closed:()=>closed};
}
{
 const p=playback(),x=p.ctx;x.BetaGwentLeaderPreview(131101,312,380);check(p.loads.length===0,'lazy hover delay');x.begin(null);
 const first=p.loads[0];x.loaded({currentTarget:first.contentLoaderInfo});check(p.rendered.length===0&&p.disposed()===0,'loader event never renders or unloads');x.tick(null);
 check(p.rendered.at(-1)===180,'loaded page resumes menu clock, not frame zero');
 check(Object.keys(x.slots).length===2,'current and next pages only');
 const next=p.loads[1];x.loaded({currentTarget:next.contentLoaderInfo});p.time(8200);x.tick(null);
 check(p.rendered.at(-1)===196&&Object.keys(x.slots).length===2,'seamless page advance');
 const before=p.loads.length;x.removed(null);x.added(null);check(p.loads.length===before&&p.rendered.at(-1)===196,'reparenting keeps resources and phase');
 for(let time=8300;time<37000;time+=200){p.time(time);x.tick(null);for(const l of [...p.loads])x.loaded({currentTarget:l.contentLoaderInfo});x.reap(null);check(Object.keys(x.slots).length<=2,'bounded stream through multiple loops');}
 x.dispose();x.dispose();check(Object.keys(x.slots).length===0,'complete idempotent release');x.reap(null);check(p.disposed()>0&&x.graveyard.length===0,'deferred unload after release');
 const q=playback(),y=q.ctx;y.BetaGwentLeaderPreview(131101,312,380);y.begin(null);const inflight=q.loads[0];y.dispose();y.reap(null);
 check(q.closed()===0&&q.disposed()===0&&y.graveyard.length===1,'in-flight page is never cancelled or unloaded');
 y.graveyard[0].finish({});y.reap(null);check(q.disposed()===1&&y.graveyard.length===0,'in-flight page unloaded after its load ends, outside its event');
 const failed=playback(),z=failed.ctx;z.BetaGwentLeaderPreview(131101,312,380);z.begin(null);
 z.failed({currentTarget:failed.loads[0].contentLoaderInfo});check(failed.disposed()===0,'error callback does not unload itself');
 for(let n=0;n<100;n++)z.tick(null);
 check(failed.loads.length===1,'failed native page is not retried every frame');z.reap(null);
 check(failed.disposed()===1&&z.graveyard.length===0,'failed page released outside its error callback');
 const limited=playback(),v=limited.ctx;v.BetaGwentLeaderPreview(131101,312,380);v.livePages=12;v.begin(null);
 check(limited.loads.length===0,'retired pages count toward global resource cap');v.livePages=0;v.tick(null);
 check(limited.loads.length===1&&v.livePages===1,'loading resumes when capacity is available');
 v.dispose();for(let n=0;n<400;n++)v.reap(null);
 check(v.livePages===1&&v.graveyard.length===1,'stuck load remains counted and is not cancelled on a timeout');
 v.graveyard[0].finish({});v.reap(null);check(v.livePages===0,'completed retired page returns its capacity');
}
{
 const a=playback(),b=playback();for(const p of [a,b]){p.ctx.BetaGwentLeaderPreview(131101,100,122);p.ctx.begin(null);p.ctx.loaded({currentTarget:p.loads[0].contentLoaderInfo});p.ctx.tick(null);}
 check(a.rendered[0]===b.rendered[0]&&a.rendered[0]!==0,'recreated hover owner preserves playback phase');
}
const boardPath='BetaGwent/ui/src/BetaGwentBoard.as',board=fs.readFileSync(boardPath,'utf8');
class Owner{constructor(id){this.cardId=id;this.used=false;}resize(){}dispose(){this.disposed=true;if(this.parent)this.parent.removeChild(this);}}
const b=vm.createContext({BetaGwentLeaderPreview:Owner,BetaGwentLeaderCatalog:{info:id=>id>0?{}:null}});
vm.runInContext('var leaderPreview=null,boardLeaderMovies=[],reducedMotion=false,selectingDecks=false,editingDeck=false,browsingCatalog=false,kegOpen=false,pileOpen=false,tutorialPage=-1,detailOpen=false;'+
 ['clearLeaderPreview','clearLeaderMovies','beginLeaderRender','finishLeaderRender','canAnimateLeader','attachLeaderMovie'].map(n=>extract(board,n)).join('\n'),b);
const parent={addChild(m){m.parent=this;},removeChild(m){m.parent=null;}};
for(let id=1;id<=3;id++)b.attachLeaderMovie(parent,id,100,122);
const originals=[...b.boardLeaderMovies];b.beginLeaderRender();for(let id=1;id<=3;id++)b.attachLeaderMovie(parent,id,100,122);b.finishLeaderRender();
check(originals.every((o,i)=>o===b.boardLeaderMovies[i]&&!o.disposed),'board redraw retains all leader owners');
b.attachLeaderMovie(parent,4,100,122);check(b.boardLeaderMovies.length===3,'three board owners maximum');
b.attachLeaderMovie(parent,1,312,380,true);check(b.leaderPreview&&b.boardLeaderMovies.length===3,'separate fourth hover owner');
b.reducedMotion=true;b.beginLeaderRender();check(b.boardLeaderMovies.length===0&&!b.leaderPreview,'reduced motion releases all pages');
check(!fs.readFileSync('tools/ui/leaders060/BetaLeaderMovie137.as','utf8').includes('getTimer'),'page movie cannot reset its own clock');
for(const locale of ['fr_fr','es_es','es_mx']){
 const map=JSON.parse(fs.readFileSync('BetaGwent/build/languages137/ui/'+locale+'.json','utf8'));
 const values=JSON.parse(fs.readFileSync('data/beta924/design/ui-overrides137.json','utf8'))[locale];
 ['Ваш ближний ряд','Ваш дальний ряд','Ваш осадный ряд','Вражеский ближний ряд','Вражеский дальний ряд','Вражеский осадный ряд'].forEach((k,i)=>{map[k]??=values[i];});
 const r=vm.createContext({});vm.runInContext(extract(board,'rowLabel'),r);
 for(const side of [1,2])for(const zone of [1,2,4])check(Object.hasOwn(map,r.rowLabel(side,zone)),'whole row label exists '+locale+'/'+side+'/'+zone);
}
check(!board.includes('(side==1?"Ваш ":"Вражеский ")'),'row labels never concatenate adjective fragments');
const sources=[textPath,previewPath,boardPath,'tools/ui/check_release137.js','BetaGwent/ui/src/BetaGwentFonts.as','BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws'];
fs.writeFileSync('docs/evidence/ui137.json',JSON.stringify({stage:137,passed:true,checks,nativeRuntimeVerified:false,sources:Object.fromEntries(sources.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]))},null,2)+'\n');
console.log('PASS:',checks,'production AS language/playback/lifecycle regressions');
