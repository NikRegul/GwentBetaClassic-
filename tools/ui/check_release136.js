// Execute production AS text and loader logic with deterministic Flash stubs.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
let checks=0;const check=(v,n)=>{if(!v)throw Error(n);checks++;};
// WitcherScript events implicitly return Bool: a bare return fails native compilation.
const bridgePath='BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws';
const bridge=fs.readFileSync(bridgePath,'utf8');
const languageEvent=bridge.match(/event OnBetaGwentTextLanguage\([^)]*\)\s*\{([\s\S]*?)\n    \}/)[1];
check(!/\breturn\s*;/.test(languageEvent)&&languageEvent.includes('return false;'),'language event guard returns Bool');
function extract(source,name){
 const at=source.indexOf('function '+name+'(');if(at<0)throw Error(name);
 const open=source.indexOf('{',at);let end=open+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(?:String|Object|void|int|Number|Array|Boolean|TextField|TextFormat|Event|TimerEvent|Sprite|BetaGwentLeaderPreview|Error)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');
}
const data=fs.readFileSync('BetaGwent/ui/src/BetaGwentTextData.as','utf8');
function table(label){
 const result={};const re=new RegExp('function '+label+'\\d+\\(o:Object\\):void\\{([\\s\\S]*?)\\n\\}','g');
 for(const method of data.matchAll(re))for(const row of method[1].matchAll(/o\[("(?:\\.|[^"\\])*")\]=("(?:\\.|[^"\\])*");/g))result[JSON.parse(row[1])]=JSON.parse(row[2]);
 return result;
}
const textPath='BetaGwent/ui/src/BetaGwentTextLanguage.as',textSource=fs.readFileSync(textPath,'utf8');
for(const language of [1,2]){
 const c=vm.createContext({BetaGwentTextData:{load:()=>table('load'),reverse:()=>table('reverse')},console});
 vm.runInContext(`var DEFAULT_LANGUAGE=${language},language=DEFAULT_LANGUAGE,fields={},maps,groups,protectedNames={},caches=[{},{},{}],cacheCount=0;function refresh(){}`+
 ['protect','initialize','longest','word','translate','track','forget','update','select','search'].map(n=>extract(textSource,n)).join('\n'),c);
 const opposite=language===1?2:1;
 const raw=language===1?'Выбрать карту':'Choose card';
 check(c.translate(raw,language)===raw,'package language round trip '+language);
 c.select(opposite);
 check(c.translate(raw)=== (language===1?'Choose card':'Выбрать карту'),'exact label '+language);
 const unit=language===1?'Кантарелла':'Cantarella';
 check(c.translate(unit)===(language===1?'Cantarella':'Кантарелла'),'card title '+language);
 const fragment=language===1?'Выбрать карту · 12':'Choose card · 12';
 check(c.translate(fragment)===(language===1?'Choose card · 12':'Выбрать карту · 12'),'longest fragment with count '+language);
 check(c.translate('X'+raw+'Z')==='X'+raw+'Z','do not translate inside a word '+language);
 c.protect(raw);
 check(c.translate(raw)===raw,'saved deck name stays opaque '+language);
 check(c.translate('«'+raw+'» · 12')==='«'+raw+'» · 12','embedded custom name preserved '+language);
 const field={text:unit,type:'dynamic',scrollV:3,getTextFormat:()=>({font:'Beta',size:22}),setTextFormat(f){this.format=f;}};
 c.track(field);
 check(field.text===(language===1?'Cantarella':'Кантарелла'),'new field translates immediately '+language);
 check(field.scrollV===3&&field.format.font==='Beta','font and scrolling preserved '+language);
 c.select(language);c.update(field,c.fields[field]);
 check(field.text===unit,'restore original field text '+language);
 field.text=language===1?'Геральт':'Geralt';c.select(opposite);c.update(field,c.fields[field]);
 check(field.text===(language===1?'Geralt':'Геральт'),'direct field assignment tracked '+language);
 const input={text:raw,type:'input'};c.track(input);check(input.text===raw,'input unchanged '+language);
 check(c.search(unit,(language===1?'cant':'кант')),'search in the other language '+language);
}
const loaderPath='BetaGwent/ui/src/BetaGwentLeaderPreview.as',loaderSource=fs.readFileSync(loaderPath,'utf8');
function loaderContext(){
 const calls={loads:[],close:0,unload:0},timers=[];
 class Events{addEventListener(){}removeEventListener(){}}
 class Timer extends Events{constructor(){super();timers.push(this);}start(){this.started=true;}stop(){this.stopped=true;}}
 class Loader extends Events{constructor(){super();this.contentLoaderInfo=new Events();this.width=256;this.height=312;}load(r){calls.loads.push(r.url);}close(){calls.close++;}unloadAndStop(){calls.unload++;}}
 const c=vm.createContext({Timer,Loader,URLRequest:class{constructor(url){this.url=url;}},BetaGwentLeaderCatalog:{path:id=>id===131101?'leader.swf':null},
 Event:{COMPLETE:'complete',REMOVED_FROM_STAGE:'removed'},IOErrorEvent:{IO_ERROR:'io'},SecurityErrorEvent:{SECURITY_ERROR:'security'},TimerEvent:{TIMER_COMPLETE:'timer'},
 addEventListener(){},removeEventListener(){},addChild(l){l.parent={removeChild(){}};},stage:{}});
 vm.runInContext('var loader=null,delay=null,disposed=false,resource=null,portraitWidth=0,portraitHeight=0;'+
 ['BetaGwentLeaderPreview','stopDelay','begin','loaded','failed','removed','dispose'].map(n=>extract(loaderSource,n)).join('\n'),c);
 return {c,calls,timers};
}
{
 const {c,calls,timers}=loaderContext();c.BetaGwentLeaderPreview(131101,312,380);
 check(timers[0].started&&calls.loads.length===0,'hover delay does not load eagerly');
 c.dispose();c.begin(null);
 check(timers[0].stopped&&calls.loads.length===0,'hover cancelled before delay never loads');
}
{
 const {c,calls}=loaderContext();c.BetaGwentLeaderPreview(131101,312,380);c.begin(null);
 check(calls.loads.length===1&&!c.loader.visible,'movie stays hidden until ready');
 c.loaded({currentTarget:c.loader.contentLoaderInfo});
 check(c.loader.visible&&c.loader.scaleX===312/256,'ready movie fits card');
 c.dispose();c.dispose();check(calls.close===1&&calls.unload===1,'cleanup is complete and idempotent');
}
{
 const {c,calls}=loaderContext();c.BetaGwentLeaderPreview(131101,312,380);c.begin(null);c.failed({});
 check(c.disposed&&c.loader===null&&calls.unload===1,'failed load keeps static fallback and releases loader');
}
{
 const {c,calls,timers}=loaderContext();c.BetaGwentLeaderPreview(123,312,380);
 check(timers.length===0&&calls.loads.length===0,'non-leader never requests a resource');
}
const boardPath='BetaGwent/ui/src/BetaGwentBoard.as',board=fs.readFileSync(boardPath,'utf8');
const c=vm.createContext({BetaGwentLeaderCatalog:{path:id=>id===131101?'leader.swf':null},BetaGwentLeaderPreview:class{dispose(){this.disposed=true;}}});
vm.runInContext('var reducedMotion=false,selectingDecks=false,editingDeck=false,browsingCatalog=false,kegOpen=false,pileOpen=false,tutorialPage=-1,detailOpen=false,leaderPreview=null,boardLeaderMovies=[];'+
 ['clearLeaderPreview','clearLeaderMovies','canAnimateLeader','attachLeaderMovie'].map(n=>extract(board,n)).join('\n'),c);
const parent={children:[],addChild(v){this.children.push(v);}};
for(let i=0;i<10;i++)c.attachLeaderMovie(parent,131101,100,122);
check(c.boardLeaderMovies.length===3,'board instances capped at three');
c.attachLeaderMovie(parent,131101,312,380,true);const first=c.leaderPreview;c.attachLeaderMovie(parent,131101,312,380,true);
check(first.disposed&&c.leaderPreview!==first&&c.boardLeaderMovies.length===3,'one hover slot replaces previous movie');
c.clearLeaderMovies();check(c.boardLeaderMovies.length===0&&c.leaderPreview===null,'redraw clears all movie owners');
c.reducedMotion=true;c.attachLeaderMovie(parent,131101,100,122);check(c.boardLeaderMovies.length===0,'reduced effects keeps leaders static');
check(extract(board,'cycleTextLanguage').includes('OnBetaGwentTextLanguage')&&!extract(board,'cycleTextLanguage').includes('AudioSettings'),'text setting independent of audio');
check(extract(board,'editorInput').includes('forget(field);field.text=value;'),'input creation restores raw user text');
check(extract(board,'openTextInput').includes('forget(nameField);nameField.text=value;'),'name modal restores raw user text');
const sources=[textPath,loaderPath,boardPath,bridgePath,'BetaGwent/ui/src/BetaGwentTextData.as','tools/ui/check_release136.js'];
const report={stage:136,checks,actualActionScript:true,nativeGameTested:false,sources:Object.fromEntries(sources.map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]))};
fs.writeFileSync('docs/evidence/ui136.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({stage:136,checks,actualActionScript:true}));
