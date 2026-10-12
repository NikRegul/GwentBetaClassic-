// 0.6.1 playtest fixes: package text default, CR newlines, immediate translation,
// first-load cover, board focus for placements, short voice wait. Executes production AS.
'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),cp=require('child_process');
let checks=0;function check(v,l){if(!v)throw Error('FAIL '+l);checks++;}
function extract(source,name){
 const at=source.indexOf('function '+name+'(');if(at<0)throw Error(name);
 const start=source.indexOf('{',at);let end=start+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:(?:String|Object|void|int|Number|Array|Boolean|TextField|TextFormat|Event|Loader)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)').replace(/\b([A-Za-z]+) as TextField\b/g,'$1');
}
const UI='BetaGwent/ui/',WS='BetaGwent/development/scripts/game/betagwent/';
const text=fs.readFileSync(UI+'src/BetaGwentTextLanguage.as','utf8');
const board=fs.readFileSync(UI+'src/BetaGwentBoard.as','utf8'),controller=fs.readFileSync(UI+'src/BetaGwentController.as','utf8');
// All five menu source copies stay identical.
for(const d of process.argv.includes('--source-only')?[]:['src-BetaGwentBoard','src-BetaGwentKeg','src-DeckBuilder','src-GwintGame'])
 for(const f of ['BetaGwentBoard.as','BetaGwentController.as','BetaGwentTextLanguage.as'])
  check(fs.readFileSync(UI+d+'/'+f,'utf8')===fs.readFileSync(UI+'src/'+f,'utf8'),'source copy '+d+'/'+f);

const codes=['','ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw'];
const english=JSON.parse(cp.execFileSync(process.env.PYTHON||'python',['-X','utf8','-c',
 'import sys,json;sys.path.insert(0,"tools");from localization89 import strings;sys.stdout.write(json.dumps(strings(),ensure_ascii=False))'],{maxBuffer:1<<28}).toString('utf8'));
function dictionary(id){
 if(process.argv.includes('--stage138')){
  const source=fs.readFileSync('BetaGwent/build/text138/'+codes[id]+'/BetaLocale137.as','utf8'),d={};
  for(const m of source.matchAll(/o\[("(?:\\.|[^"\\])*")\]=("(?:\\.|[^"\\])*");/g))d[JSON.parse(m[1])]=JSON.parse(m[2]);
  check(Object.keys(d).length>100,'stage138 native dictionary '+codes[id]);
  return d;
 }
 let d=id===2?{...english}:JSON.parse(fs.readFileSync('BetaGwent/build/languages137/ui/'+codes[id]+'.json','utf8'));
 return {...d,...Object.fromEntries(Object.entries(d).map(([k,v])=>[k.toUpperCase(),v.toUpperCase()]))};
}
const c=vm.createContext({Object,BetaGwentFonts:{BODY:'B',TITLE:'T',NUMBERS:'N'}});
vm.runInContext('var DEFAULT_LANGUAGE=1,language=1,pendingLanguage=0,fields=new Map(),maps,groups,protectedNames={},caches=[],cacheCount=0,resourceLoader=null,pendingLoader=null,bodyFont=null,titleFont=null,fontCharacters="",changed=null;var LABELS='+JSON.stringify(['','Русский','English','Deutsch','Français','Italiano','Polski','Español','Español (Latinoamérica)','Português (Brasil)','日本語','한국어','简体中文','繁體中文'])+';'+
 ['initialize','indexLanguage','longest','normalize','word','translate','track','forget','assign','sweep','loaded','update','hasGlyphs','refresh'].map(n=>extract(text,n)).join('\n')
 .replace(/fields\[(\w+)\]=/g,'fields.set($1,').replace(/fields\.set\((\w+),(\{[^;]*\});/g,'fields.set($1,$2);')
 .replace(/delete fields\[(\w+)\]/g,'fields.delete($1)').replace(/fields\[(\w+)\]/g,'fields.get($1)')
 .replace(/for\(var item in fields\)/g,'for(var item of fields.keys())').replace(/var state=fields\.get\(item\)/g,'var state=fields.get(item)'),c);
// Literal inventory: every Cyrillic source string (AS + WS) must translate fully, also with CR breaks.
const literals=new Set();
for(const f of fs.readdirSync(UI+'src').filter(n=>n.endsWith('.as')&&n!=='BetaGwentTextData.as'))
 for(const m of fs.readFileSync(UI+'src/'+f,'utf8').matchAll(/"((?:[^"\\\n]|\\.)*)"/g)){const v=m[1].replace(/\\n/g,'\n').replace(/\\"/g,'"').replace(/\\\\/g,'\\');if(/[А-Яа-яЁё]/.test(v))literals.add(v);}
for(const f of fs.readdirSync(WS).filter(n=>n.endsWith('.ws')))
 for(const m of fs.readFileSync(WS+f,'utf8').matchAll(/"((?:[^"\\\n]|\\.)*)"/g)){const v=m[1].replace(/\\n/g,'\n').replace(/\\"/g,'"').replace(/\\\\/g,'\\');if(/[А-Яа-яЁё]/.test(v))literals.add(v);}
const allowed=new Set(['Русский','йцукенгшщзхъфывапролджэячсмитьбюё','ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮЁ']);
const menu=['Текст: Deutsch','Текст: English','Пауза ИИ: 0,4 с','Рука: сила','Сложность ИИ: лёгкая','Темп: 1.5×','Фразы: ждут банк',
 'Удерживайте LT — свой сброс, RT — колода\nОба курка — сброс соперника · View — колода\nR3 — лидер · X — подробности карты\nO — сортировка руки · удерживайте Y / △ для паса'];
for(let id=2;id<=13;id++){
 c.indexLanguage(id,dictionary(id));c.language=id;let missing=[];
 for(const v of [...literals,...menu]){if(allowed.has(v))continue;
  for(const form of [v,v.replace(/\n/g,'\r'),v.replace(/\n/g,'\r\n')]){const t=c.translate(form);if(/[А-Яа-яЁё]/.test(t.replace(/Русский/g,'')))missing.push(codes[id]+': '+JSON.stringify(form).slice(0,90));}}
 check(missing.length===0,'complete translation\n'+missing.slice(0,8).join('\n'));
}
// Scaleform reads "\n" back as "\r": tracked text must still translate and follow language changes.
class Field{constructor(t){this.type='dynamic';this.embedFonts=false;this.scrollV=1;this.format={font:'B'};this.text=t;}
 set text(v){this._t=String(v).replace(/\r\n|\n/g,'\r');} get text(){return this._t;}
 getTextFormat(){return this.format;} setTextFormat(f){this.format=f;} set defaultTextFormat(f){}}
c.indexLanguage(3,dictionary(3));c.language=3;
const keys=menu[7],field=new Field(keys);c.track(field);
check(field.text===dictionary(3)[keys].replace(/\n/g,'\r'),'CR multiline help translated (de)');
c.indexLanguage(5,dictionary(5));c.language=5;c.refresh();
check(field.text===dictionary(5)[keys].replace(/\n/g,'\r'),'CR multiline text follows a language change (it)');
c.assign(field,'Обучение');check(field.text===dictionary(5)['Обучение'],'assign translates in the same call');
field.text='Выбор колод';c.sweep();check(field.text===dictionary(5)['Выбор колод'],'sweep catches direct .text replacements');
const before=field.text;c.sweep();check(field.text===before,'sweep idempotent');
const offStage=new Field('Обучение');c.track(offStage);c.indexLanguage(3,dictionary(3));c.language=3;c.refresh();
check(offStage.text===dictionary(3)['Обучение'],'off-stage tracked fields refresh on language load');
check(c.loaded()===false,'not loaded before a language resource');
// Production board: no direct assignment of source text to tracked fields.
for(const name of ['replayHint','inspection','catalogScrapsLabel','nameCounter','tempoLabel','motionLabel','caption','mulliganTitle','mulliganReading'])
 check(!new RegExp('\\b'+name+'\\.text=(?!=)').test(board),'immediate translation for '+name);
check(!/hint\.text=line/.test(controller)&&controller.includes('BetaGwentTextLanguage.assign(hint,line)'),'controller hint translated immediately');
check(board.includes('BetaGwentTextLanguage.sweep();updateTextGate(now);')&&board.includes('addEventListener("exitFrame",sweepTextLate)'),'per-frame sweeps');
check(board.includes('addChild(textGate);textGateUntil=getTimer()+6000;')&&/if\(BetaGwentTextLanguage\.loaded\(\)\|\|now>=textGateUntil\)/.test(board),'first language load covered with timeout');
// Board focus for every placement / row choice, executed on production code.
const focusStart=board.indexOf('var placing:Boolean=');
const focusCode=board.slice(focusStart,board.indexOf('finishLeaderRender();',focusStart));
const r=vm.createContext({});vm.runInContext('var playing,selected,requestId,rowRequest,detailOpen=false,pileOpen=false,controllerMenuOpen=false,boardFocusKey="",asked=[],ps=false,pp=false;'+
 'var controller={active:true,restoreFocus:function(t){asked.push(t);}};function canPlaceSelected(){return ps;}function canPlacePending(){return pp;}'+
 'function run(){'+focusCode.replace(/:(Boolean|String)\b/g,'')+'}',r);
function step(state){Object.assign(r,state);r.run();return r.asked.splice(0);}
check(step({playing:false,ps:true,pp:false,selected:7,requestId:0,rowRequest:false}).join()==='position','hand card placement focuses board');
check(step({}).length===0,'no refocus on redraw of the same placement');
check(step({ps:false,pp:true,selected:0,requestId:41}).join()==='position','deck summon (Подкрепление) focuses board');
check(step({pp:false,requestId:42,rowRequest:true}).join()==='row','row choice focuses rows');
check(step({playing:true,rowRequest:false,requestId:0,ps:true,selected:9}).length===0,'no focus jump during replay');
check(step({playing:false}).join()==='position','focus after replay ends');
r.controller.active=false;check(step({selected:11}).length===0,'mouse users keep their pointer (no ghost)');
// Controller: a fallback focus yields to board positions when they appear.
check(/if\(autoPicked&&focus\.tag!=s\.preferred&&\(s\.mode=="placement"\|\|s\.mode=="rows"\|\|s\.mode=="target"\)\)/.test(controller)&&controller.includes('autoPicked=focus.tag!=s.preferred;'),'fallback focus yields to preferred');
// WS: opponent waits at most 1 s for a card line.
const menuWs=fs.readFileSync(WS+'developmentBoardMenu.ws','utf8'),audioWs=fs.readFileSync(WS+'duelAudio.ws','utf8');
check(menuWs.includes('audio.IsVoiceActive() && audio.CurrentTime()-deferredVoiceAt<1.0f)return;')&&menuWs.includes('if(audio)deferredVoiceAt=audio.CurrentTime();')&&audioWs.includes('public function CurrentTime() : float { return Now(); }'),'bounded voice wait');
// Package default: each voice package resets the text language once to its own language.
const bridge=JSON.parse(cp.execFileSync(process.env.PYTHON||'python',['-X','utf8','-c',
 'import sys,json;sys.path.insert(0,"tools/ui");from build_voice137 import language_bridge,DEFAULT_TEXT,PACKAGE_ID;'+
 'sys.stdout.write(json.dumps({l:[language_bridge(\'a FlashArgInt(FactsQueryLatestValue("bg_text_language")) b\',l),DEFAULT_TEXT[l],PACKAGE_ID[l]] for l in DEFAULT_TEXT}))']).toString('utf8'));
const want={en:2,ru:1,de:3,it:5,'pt-br':9};
check(new Set(Object.values(bridge).map(x=>x[2])).size===5,'distinct package ids');
for(const [l,[src,def,pkg]] of Object.entries(bridge)){
 check(def===want[l]&&codes[def].startsWith(l==='pt-br'?'pt_br':l),'package default '+l);
 check(src.includes(`if(FactsQueryLatestValue("bg_text_language_package")!=${pkg})`)&&src.includes(`FactsSet("bg_text_language",${def});`)&&src.includes(`FactsSet("bg_text_language_package",${pkg});`),'package reset '+l);
}
console.log('PASS: '+checks+' 0.6.1 playtest-fix regressions');
