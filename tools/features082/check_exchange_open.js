'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.resolve(root,process.argv[2]||'BetaGwent/build/release082-rc2');let checks=0;
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|MouseEvent|Error)\b(?=\s*(?:[,)=;{]|in\b))/g,'');}
function host(source,selecting,editing,ready=true,open=false){
 let clipboard='BG1:test';
 const c=vm.createContext({skin:3,ready,nameOpen:open,selectingDecks:selecting,editingDeck:editing,revision:19,nameLayer:{},WIDE_PAD:0,content:{},
  calls:[],buttons:[],panels:[],keyboardStage:{focus:null},controller:{focusTag(){}},TextFieldType:{INPUT:'input'},Event:{CHANGE:'change'},MouseEvent:{MOUSE_WHEEL:'wheel'},
  BetaGwentTextLanguage:{forget(){}},closeControllerMenu(){},closeNameInput(){},submitDeckExchange(){},pasteExchange(){},copyExchange(){return true;},
  getDefinitionByName(){return {generalClipboard:{getData:()=>clipboard}};},
  text(){return {text:'',setSelection(){},addEventListener(){}};},panel(...args){c.panels.push(args);return {};},
  editorSmallButton(parent,title,x,y,w,h,enabled,callback){c.buttons.push({title,enabled,callback});},betaWideButton(title,x,y,w,enabled,callback){c.buttons.push({title,enabled,callback});},send(...args){c.calls.push(args);}});
 vm.runInContext(['clipboardText','openDeckExchange','drawDeckExchangeButtons'].map(n=>fn(source,n)).join('\n'),c);return c;
}
for(const platform of ['nextgen','classic']){
 const previous=fs.readFileSync(path.join(root,'BetaGwent/build/release082-rc1',platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const source=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentBoard.as'),'utf8');
 const old=host(previous,false,true);old.drawDeckExchangeButtons();old.buttons[0].callback();assert(!old.nameOpen,'RC1 editor failure reproduced');checks++;
 for(const importing of [true,false]){
  const c=host(source,false,true);c.drawDeckExchangeButtons();const button=c.buttons.find(b=>b.title===(importing?'Импорт колоды':'Экспорт колоды'));assert(button&&button.enabled);checks++;
  button.callback();assert(c.nameOpen&&c.panels.length===2&&c.nameRevision===19&&c.textPurpose===(importing?3:4));checks++;
  assert(c.exchangeMessage&&c.nameField&&c.keyboardStage.focus===c.nameField);checks++;
  assert(importing?c.nameField.text==='BG1:test':c.calls[0][0]==='OnBetaGwentDeckExport'&&c.calls[0][1][0]===19);checks++;
 }
 const list=host(source,true,false);list.drawDeckExchangeButtons();assert(list.buttons.length===1);checks++;list.buttons[0].callback();assert(list.nameOpen);checks++;
 for(const [selecting,editing,ready,open,importing] of [[false,false,true,false,true],[true,false,true,false,false],[false,true,false,false,true],[false,true,true,true,false]]){
  const c=host(source,selecting,editing,ready,open);c.openDeckExchange(importing);assert(c.panels.length===0&&c.calls.length===0);checks++;
 }
}
const result={checks,actualActionScript:true,rc1FailureReproduced:true,editorImportAndExportOpen:true,deckSelectionImportOpens:true,nativeGameVerified:false};
fs.writeFileSync(path.join(build,'exchange-open-tests.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
