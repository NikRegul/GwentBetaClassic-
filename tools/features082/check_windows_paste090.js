'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.join(root,'BetaGwent/build/'+(process.env.BG_UI||'release090-windows-paste'));let checks=0;
function check(ok,msg){assert(ok,msg);checks++;}
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|MouseEvent|KeyboardEvent|Error)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/\bis TextField\b/g,'instanceof TextField').replace(/for each\(var (\w+) in (\w+)\)/g,'for(var $1 of $2)');}
const deck=n=>'BG1:2:131101:'+Array(n).fill(112210).join(',');
function host(source){
 const c=vm.createContext({introStart:0,controllerMenuOpen:false,nameOpen:true,textPurpose:3,exchangeImport:true,keyboardStage:{focus:null},
  nameField:{text:'manual draft',setSelection(a,b){c.selection=[a,b];}},exchangeMessage:{text:''},exchangeQuotedCode:'old quote',
  api:true,bridge:true,readOK:true,windows:deck(25),internal:'stale Flash text',calls:[],reads:0,checked:0,prevented:false,stopped:false,corrupt:0,
  BetaGwentTextLanguage:{assign(field,text){field.text=text;}},checkDeckExchange(){c.checked++;},
  getDefinitionByName(name){if(!c.api||name!=='flash.desktop.Clipboard')throw Error('unsupported API');return {generalClipboard:{
   getData(){throw Error('must never read stale Flash clipboard');},
   setData(format,text){c.calls.push([format,text]);
    if(format==='betagwent:windows-paste-v1')return c.bridge;
    if(format==='betagwent:windows-paste-begin-v1'){c.reads++;c.snapshot=c.readOK?c.windows:'';return c.readOK;}
    if(format==='betagwent:windows-paste-bit-v1'){
     const [position,bit]=text.split(':').map(Number),char=c.snapshot[position];
     const symbol=c.corrupt||(char?'0123456789:,BG'.indexOf(char)+1:0);
     if(c.changeDuringRead)c.windows='new unrelated Windows text';
     return !!(symbol&(1<<bit));
    }
    throw Error('unexpected clipboard operation '+format);
   }}};}});
 vm.runInContext(['clipboardText','pasteExchange','onKey'].map(n=>fn(source,n)).join('\n'),c);return c;
}
for(const platform of ['classic','nextgen']){
 const base=path.join(build,platform,'ui'),source=fs.readFileSync(path.join(base,'src/BetaGwentBoard.as'),'utf8');
 for(const n of [25,40]){
  const c=host(source);c.windows=deck(n);const expected=c.windows;c.changeDuringRead=true;
  c.pasteExchange();check(c.nameField.text===expected,'complete Windows code wins over stale Flash text');
  check(c.reads===1,'one immutable Windows read for entire paste');
  check(c.checked===1&&c.exchangeQuotedCode==='','paste only requests validation, invalidates old quote');
  check(c.selection[1]===expected.length,'full pasted code selected');
  check(c.calls.length===2+4*(expected.length+1),'bounded Boolean snapshot decoding');
 }
 for(const failure of ['api','bridge','readOK']){
  const c=host(source);c[failure]=false;c.pasteExchange();
  check(c.nameField.text==='manual draft'&&c.exchangeQuotedCode==='old quote'&&c.checked===0,'failed paste preserves draft and quote: '+failure);
  check(c.exchangeMessage.text.includes('BG1')&&c.exchangeMessage.text.includes('bin'),'failure gives installation/code hint');
 }
 for(const bad of ['', 'ordinary text',deck(24),deck(41),deck(25)+',']){
  const c=host(source);c.windows=bad;c.pasteExchange();check(c.nameField.text==='manual draft'&&!c.checked,'defensive invalid-response rejection');
 }
 for(const symbol of [15,13]){
  const c=host(source);c.corrupt=symbol;c.pasteExchange();
  check(c.nameField.text==='manual draft'&&!c.checked,'invalid symbol and nonterminated responses rejected');
  check(c.calls.length<=1286,'malformed native response bounded to 321 characters');
 }
 for(const ok of [true,false]){
  const c=host(source);c.readOK=ok;
  c.onKey({keyCode:86,ctrlKey:true,preventDefault(){c.prevented=true;},stopImmediatePropagation(){c.stopped=true;}});
  check(c.prevented&&c.stopped,'Ctrl+V suppresses stale default GFx paste on success and failure');
  check(c.reads===1,'Ctrl+V reads Windows exactly once');
  check(c.checked===(ok?1:0),'Ctrl+V validates only successfully read code');
 }
 const c=host(source);c.nameField=null;c.pasteExchange();check(!c.calls.length,'closed input never accesses clipboard');
 check(!fn(source,'clipboardText').includes('getData('),'no fallback to stale Flash clipboard');
 check(!/send\(|submitDeckExchange\(|exchangeCraft\(/.test(fn(source,'pasteExchange')),'paste cannot craft or import automatically');
 const localized=fs.readFileSync(path.join(base,'src/BetaGwentExchangeText082.as'),'utf8');
 const keys=JSON.parse(localized.match(/KEYS:Array=(\[.*?\]);/s)[1]),values=JSON.parse(localized.match(/VALUES:Array=(\[.*?\]);/s)[1]);
 const index=keys.findIndex(k=>k.startsWith('Не удалось вставить код BG1.'));
 check(index>=0&&values.length===14&&values.slice(1).every(row=>row[index].includes('BG1')&&row[index].includes('bin')),'paste error translated into all 13 languages');
 const board=fs.readFileSync(path.join(base,'src/BetaGwentBoard.as'));
 for(const dir of ['src','src-BetaGwentBoard','src-DeckBuilder','src-GwintGame','src-BetaGwentKeg']){
  const raw=fs.readFileSync(path.join(base,dir,'BetaGwentBoard.as'));
  check(raw.equals(board)&&raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'matching BOM/CRLF mirror '+platform+'/'+dir);
 }
}
const report={checks,productionAS:true,windowsReadsPerPaste:1,userClipboardModified:false,inGameVerified:false};
fs.writeFileSync(path.join(build,'windows-paste-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
