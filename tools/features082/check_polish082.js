'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const build=path.resolve(process.argv[2]),output=path.join(build,'ui-polish-tests.json');let checks=0;const previews=[];
function fn(s,name){const start=s.indexOf('function '+name+'(');assert(start>=0,name);const begin=s.indexOf('{',start);let depth=1,end=begin+1;for(;depth;end++){if(s[end]==='{')depth++;if(s[end]==='}')depth--;}
 return s.slice(start,end).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Event|TextEvent|MouseEvent|Sprite|TextField|Function|TextFormat)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/\s+as (?:Array|Sprite|TextField)\b/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');}
function check(v,n){assert(v,n);checks++;}
for(const platform of ['classic','nextgen']){
 const folder=path.join(build,platform,'ui'),s=fs.readFileSync(path.join(folder,'src/BetaGwentBoard.as'),'utf8'),lang=fs.readFileSync(path.join(folder,'src/BetaGwentTextLanguage.as'),'utf8');
 for(const mirror of ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']){
  const raw=fs.readFileSync(path.join(folder,mirror,'BetaGwentBoard.as'));check(raw.equals(fs.readFileSync(path.join(folder,'src/BetaGwentBoard.as'))),'five identical board mirrors');check(raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'BOM CRLF');
 }
 // Execute the real button fitting routine, including a late language/font load.
 const fitContext=vm.createContext({Math});vm.runInContext(fn(lang,'layoutButton'),fitContext);
 const samples=['Создать недостающие','Fehlende Karten herstellen','Criar cartas em falta','Annuler la modification de carte','不足しているカードを作成','누락된 카드 제작','Сложность ИИ: высокая'];
 for(const title of samples)for(const width of [80,120,184,240,320,544]){
  let format={size:18},field={width:width-24,text:title,multiline:false,wordWrap:false,getTextFormat(){return {...format};},setTextFormat(v){format={...v};}};
  Object.defineProperties(field,{textWidth:{get(){const raw=[...title].reduce((n,c)=>n+(/[^\u0000-\u2fff]/.test(c)?1:.61)*format.size,0);return field.wordWrap?Math.min(field.width-4,raw):raw;}},textHeight:{get(){const raw=[...title].reduce((n,c)=>n+(/[^\u0000-\u2fff]/.test(c)?1:.61)*format.size,0);return Math.ceil(field.wordWrap?raw/(field.width-4):1)*format.size*1.16;}}});
  fitContext.layoutButton(field,{buttonFit:{size:18,minimum:12,height:48,originY:0,padding:4}});
  // Very narrow keyboard keys only receive individual glyphs, not these phrases.
  if(width>=184)check(field.textHeight<=40&&field.y>=4&&field.y+field.height<=44,'translated button stays inside 48 px action');
  format.size=28;fitContext.layoutButton(field,{buttonFit:{size:18,minimum:12,height:48,originY:0,padding:4}});if(width>=184)check(field.textHeight<=40,'late font refresh is refitted');
 }
 check(lang.includes('layoutButton(field,state);'),'font/dictionary update invokes layout');
 if(lang.includes('originY:Number=0')){
  check(s.includes('BetaGwentTextLanguage.fitButton(caption,22,12,48)'),'wide footer actions share late font fitting');
  check(s.includes('fitButton(field,size,Math.min(size,12),h,y,2)'),'slot labels preserve their vertical origin after refresh');
 }
 check(s.includes('field.multiline=value!=null&&value.indexOf("\\n")>=0'),'explicit multiline history remains multiline');
 const nodes=[];function Sprite(value){if(value)return value;this.graphics={beginFill(){},drawRect(){},endFill(){}};this.addChild=()=>{};this.addEventListener=()=>{};}
 const box={numChildren:3,removeChildAt(){}};
 const c=vm.createContext({Math,int:v=>v|0,String,Sprite,Event:{CHANGE:'change'},TextEvent:{TEXT_INPUT:'input'},MouseEvent:{CLICK:'click',MOUSE_WHEEL:'wheel'},TextFieldType:{INPUT:'input'},WIDE_PAD:0,skin:3,ready:true,nameOpen:false,selectingDecks:true,editingDeck:true,revision:7,keyboardStage:null,controller:{focusTag(){}},
  nameLayer:{getChildAt:()=>box},nameRussian:true,nameUpper:false,textPurpose:0,textLimit:48,nameCounter:{},nameField:{text:'Колода'},BetaGwentFonts:{TITLE:'title',BODY:'body'},BetaGwentHud104:{POPUP:0,POPUP_TITLE:1},choiceLayer:{addChild(){}},BetaGwentTextLanguage:{forget(){},assign(){}},
  closeControllerMenu(){},pasteExchange(){},submitDeckExchange(){},copyExchange(){},closeNameInput(){},clipboardText:()=>'',send(){},nameLetter:()=>()=>{},editName(){},submitNameInput(){},
  panel(parent,x,y,w,h){nodes.push({kind:'panel',x,y,w,h});return box;},
  text(parent,value,x,y,w,size){const n={kind:'text',value,text:value,x,y,w,h:80,size,set height(v){this.h=v;},get height(){return this.h;},addEventListener(){},setSelection(){}};nodes.push(n);return n;},
  editorSmallButton(parent,title,x,y,w,h){nodes.push({kind:'button',value:title,x,y,w,h});},editorBetaButton(parent,title,x,y,w,h){nodes.push({kind:'button',value:title,x,y,w,h});},
  betaLabel(parent,title,x,y,w,size){const n={kind:'text',value:title,x,y,w,h:size*1.6,size};nodes.push(n);return n;},betaFace(){},paintArt(){}});
 vm.runInContext(['drawNameKeyboard','openTextInput','openDeckExchange','drawBetaConfirm'].map(n=>fn(s,n)).join('\n'),c);
 c.openTextInput(0,'Реданская броня');for(const n of nodes.filter(n=>n.kind!=='panel'))check(n.x>=48&&n.x+n.w<=952&&n.y>=48&&n.y+n.h<=674,'keyboard and hint share panel insets');
 previews.push({platform,screen:'name-keyboard',width:1000,height:720,nodes:JSON.parse(JSON.stringify(nodes.filter(n=>n.kind!=='panel')))});
 nodes.length=0;c.nameOpen=false;c.openDeckExchange(true);for(const n of nodes.filter(n=>n.kind!=='panel'))check(n.x>=48&&n.x+n.w<=1072&&n.y>=48&&n.y+n.h<=712,'exchange contents inside frame');
 previews.push({platform,screen:'import',width:1120,height:760,nodes:JSON.parse(JSON.stringify(nodes.filter(n=>n.kind!=='panel')))});
 nodes.length=0;c.drawBetaConfirm('Завершить замену карт?','Можно сохранить оставшиеся карты и продолжить раунд.',()=>{},()=>{});
 check(nodes.filter(n=>n.kind==='button').every(n=>n.y===580&&n.y+n.h<=628),'confirmation actions aligned');
 previews.push({platform,screen:'confirm',width:1920,height:1080,nodes:JSON.parse(JSON.stringify(nodes))});
}
fs.writeFileSync(output,JSON.stringify({checks,actualActionScript:true,fontMeasurement:'bounded display-list approximation; native visual acceptance required',previews},null,2));console.log(JSON.stringify({checks,previews:previews.length}));
