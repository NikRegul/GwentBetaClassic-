'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.join(root,'BetaGwent/build/'+(process.env.BG_UI||'release090-native-clipboard'));let checks=0;
function check(ok,msg){assert(ok,msg);checks++;}
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|MouseEvent|KeyboardEvent|Error)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/\bis TextField\b/g,'instanceof TextField').replace(/for each\(var (\w+) in (\w+)\)/g,'for(var $1 of $2)');}
function host(source){
 const c=vm.createContext({introStart:0,controllerMenuOpen:false,nameOpen:true,textPurpose:4,exchangeImport:false,keyboardStage:{focus:null},
  nameField:{text:'BG1:2:131101:'+Array(25).fill(112210).join(','),setSelection(a,b){c.selection=[a,b];}},exchangeMessage:{text:''},
  api:true,bridge:false,writeOK:true,windows:'unchanged',internal:'old',calls:[],prevented:false,stopped:false,
  BetaGwentTextLanguage:{assign(field,text){field.text=text;}},
  getDefinitionByName(name){if(!c.api||name!=='flash.desktop.Clipboard')throw Error('unsupported API');return {generalClipboard:{setData(format,text){c.calls.push(format);
   if(format==='betagwent:windows-clipboard-v1')return c.bridge;
   c.internal=text;if(c.bridge&&c.writeOK)c.windows=text;return c.writeOK;
  }}};}});
 vm.runInContext(['copyExchange','onKey'].map(n=>fn(source,n)).join('\n'),c);return c;
}
for(const platform of ['classic','nextgen']){
 const base=path.join(build,platform,'ui'),source=fs.readFileSync(path.join(base,'src/BetaGwentBoard.as'),'utf8');
 const c=host(source);
 check(c.copyExchange()===false,'absent native bridge rejected');
 check(c.calls.length===1&&c.windows==='unchanged'&&c.internal==='old','probe never modifies either clipboard');
 check(!c.exchangeMessage.text.includes('скопирован')&&c.exchangeMessage.text.includes('bin'),'missing module has installation hint, not false success');
 c.bridge=true;c.writeOK=false;c.calls=[];
 check(c.copyExchange()===false&&c.windows==='unchanged','actual Windows failure is returned to UI');
 check(!c.exchangeMessage.text.includes('скопирован'),'write failure never reports copied');
 c.writeOK=true;c.calls=[];
 check(c.copyExchange()===true&&c.windows===c.nameField.text,'native success copies complete code');
 check(c.calls.join('|')==='betagwent:windows-clipboard-v1|air:text','capability checked before each copy');
 check(c.exchangeMessage.text==='Код колоды скопирован.','only native success reports copied');
 check(c.selection[1]===c.nameField.text.length&&c.keyboardStage.focus===c.nameField,'copy preserves selectable code focus');
 c.api=false;check(c.copyExchange()===false,'absent Clipboard API handled');c.api=true;
 c.nameField.text='';const calls=c.calls.length;check(c.copyExchange()===false&&c.calls.length===calls,'empty code never changes clipboard');
 c.onKey({keyCode:67,ctrlKey:true,preventDefault(){c.prevented=true;},stopImmediatePropagation(){c.stopped=true;}});
 check(!c.prevented&&!c.stopped,'native Ctrl+C event remains enabled');
 const localized=fs.readFileSync(path.join(base,'src/BetaGwentExchangeText082.as'),'utf8');
 const values=JSON.parse(localized.match(/VALUES:Array=(\[.*?\]);/s)[1]);
 check(values.length===14&&values.slice(1).every(row=>row[9].includes('bin')),'native module hint translated into 13 languages');
 check(!source.slice(source.indexOf('function copyExchange'),source.indexOf('function pasteExchange')).includes('scriptslog'),'copy has no log or helper dependency');
 const board=fs.readFileSync(path.join(base,'src/BetaGwentBoard.as'));
 for(const dir of ['src','src-BetaGwentBoard','src-DeckBuilder','src-GwintGame','src-BetaGwentKeg']){
  const raw=fs.readFileSync(path.join(base,dir,'BetaGwentBoard.as'));
  check(raw.equals(board)&&raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'matching BOM/CRLF mirror '+platform+'/'+dir);
 }
}
const report={checks,productionAS:true,logRequired:false,helperRequired:false,nativeGameCopyVerified:false};
fs.writeFileSync(path.join(build,'ui-clipboard-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
