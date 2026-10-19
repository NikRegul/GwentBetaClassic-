'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.join(root,'BetaGwent/build/release090-integrated');let checks=0;
function check(ok,msg){assert(ok,msg);checks++;}
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|MouseEvent|KeyboardEvent|Error)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/\bis TextField\b/g,'instanceof TextField').replace(/for each\(var (\w+) in (\w+)\)/g,'for(var $1 of $2)');}
function host(source){
 const c=vm.createContext({introStart:0,controllerMenuOpen:false,nameOpen:true,textPurpose:4,exchangeImport:false,keyboardStage:{focus:null},
  nameField:{text:'BG1:32:200160:'+Array(25).fill(112102).join(','),setSelection(a,b){c.selection=[a,b];}},exchangeMessage:{text:'',appendText(s){this.text+=s;}},
  available:true,internal:'old',windows:'unchanged',copyCalls:0,prevented:false,stopped:false,
  BetaGwentTextLanguage:{assign(field,text){field.text=text;}},
  getDefinitionByName(name){if(!c.available||name!=='flash.desktop.Clipboard')throw Error('unsupported API');return {generalClipboard:{getData:()=>c.internal,setData(format,text){c.copyCalls++;c.internal=text;return true;}}};}});
 vm.runInContext(['clipboardText','copyExchange','onKey'].map(n=>fn(source,n)).join('\n'),c);return c;
}
for(const platform of ['classic','nextgen']){
 const before=fs.readFileSync(path.join(root,'BetaGwent/build/release082-polish2',platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const source=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const old=host(before);old.copyExchange();check(old.windows==='unchanged'&&old.exchangeMessage.text.includes('скопирован'),'old false success reproduced with internal-only clipboard');
 const c=host(source);check(c.copyExchange()===true,'internal API accepts code');
 check(c.internal===c.nameField.text&&c.windows==='unchanged','internal and OS clipboard are distinct in regression fixture');
 check(!c.exchangeMessage.text.includes('скопирован')&&c.exchangeMessage.text.includes('Copy-Deck-Code.cmd'),'internal success never claims Windows success');
 check(c.keyboardStage.focus===c.nameField&&c.selection[1]===c.nameField.text.length,'Copy restores text focus and selects the complete code');
 const calls=c.copyCalls;c.keyboardStage.focus=null;
 c.onKey({keyCode:67,ctrlKey:true,preventDefault(){c.prevented=true;},stopImmediatePropagation(){c.stopped=true;}});
 check(!c.prevented&&!c.stopped&&c.copyCalls===calls,'Ctrl+C retains the native event instead of swallowing it after internal success');
 check(c.keyboardStage.focus===c.nameField,'Ctrl+C returns focus to code field');
 c.available=false;check(c.copyExchange()===false,'absent API handled without success');
 check(c.exchangeMessage.text.includes('Copy-Deck-Code.cmd'),'fallback instructions survive absent API');
 c.nameField.text='';check(c.copyExchange()===false,'empty export does not replace clipboard');
 const values=JSON.parse(fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentExchangeText082.as'),'utf8').match(/VALUES:Array=(\[.*?\]);/s)[1]);
 check(values.length===14&&values.slice(1).every(v=>v[9].includes('Copy-Deck-Code.cmd')),'fallback instructions present in all 13 translations');
 for(const dir of ['src','src-BetaGwentBoard','src-DeckBuilder','src-GwintGame','src-BetaGwentKeg']){
  const raw=fs.readFileSync(path.join(build,platform,'ui',dir,'BetaGwentBoard.as'));
  check(raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'BOM and CRLF '+platform+'/'+dir);
  check(raw.equals(fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'))),'five source mirrors match '+platform+'/'+dir);
 }
}
const report={checks,actualActionScript:true,oldFalseSuccessReproduced:true,osClipboardInGameVerified:false};
fs.writeFileSync(path.join(build,'export-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
