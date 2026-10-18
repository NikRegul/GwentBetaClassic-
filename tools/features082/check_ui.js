'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root='D:/w3mod/',base=root+'BetaGwent/build/features082/',path=process.argv[2]||base+'candidate/ui/src/BetaGwentBoard.as';
const s=fs.readFileSync(path,'utf8');
function fn(name){let p=s.indexOf('function '+name+'('),a=s.indexOf('{',p),i=a+1,n=1;assert(p>=0,name);while(n){if(s[i]==='{')n++;if(s[i]==='}')n--;i++;}return s.slice(p,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|TextField|Event|Error)\b(?=\s*(?:[,)=;{]|in\b))/g,'');}
let checks=0;function check(v,n){assert(v,n);checks++;}
const c=vm.createContext({Math,String,Error,requestedTextLanguage:0,requestedVoiceLanguage:0,resolvedVoiceLanguage:2,gameTextLanguage:2,gameVoiceName:'EN',controllerMenuOpen:false,ready:true,calls:[],renders:0,
 BetaGwentTextLanguage:{language:1,label:()=> 'Русский',assign:(field,value)=>{field.text=value;}},setTextLanguage:v=>{c.resolvedText=v;},render:()=>c.renders++,closeControllerMenu:()=>{c.controllerMenuOpen=false;},openControllerMenu:()=>{c.controllerMenuOpen=true;},send:(event,args)=>c.calls.push([event,args])});
for(const name of ['voiceNames','textWords','voiceWords','autoWords']){const m=s.match(new RegExp('private const '+name+':Array=(\\[[^;]+\\]);'));assert(m,name);c[name]=vm.runInContext(m[1],c);}
vm.runInContext(['setLanguageSettings','cycleTextLanguage','cycleVoiceLanguage','textChoiceLabel','voiceChoiceLabel'].map(fn).join('\n'),c);
c.setLanguageSettings(0,0,2,1,1,'PL');check(c.voiceChoiceLabel().includes('PL → EN'),'fallback remains visible');
for(let i=1;i<=14;i++){c.cycleTextLanguage();check(c.calls.at(-1)[0]==='OnBetaGwentTextLanguage'&&c.calls.at(-1)[1][0]===i%14,'text cycle');}
for(let i=1;i<=6;i++){c.cycleVoiceLanguage();check(c.calls.at(-1)[0]==='OnBetaGwentVoiceLanguage'&&c.calls.at(-1)[1][0]===i%6,'voice cycle');}
for(let language=1;language<=13;language++){c.BetaGwentTextLanguage.language=language;check(c.textChoiceLabel().length>2&&c.voiceChoiceLabel().length>2,'labels for all 13 languages');}
const geometry=[...fn('betaPlaque').matchAll(/editorSmallButton\(content,(textChoiceLabel|voiceChoiceLabel)\(\),(\d+),(\d+),(\d+),(\d+)/g)].map(m=>m.slice(2).map(Number));
check(geometry.length===2,'two language controls');
const [text,audio]=geometry;
check(text[0]===audio[0]&&text[2]===audio[2]&&text[3]===audio[3],'same left edge, width and height');
check(text[0]===56&&text[0]+text[2]===420,'aligned with left deck pane content');
check(audio[1]-text[1]-text[3]===12&&audio[1]+audio[3]===120,'12 px gap; 16 px clearance before pane');
check(text[0]+text[2]<615,'neither control touches title plaque');
let clipboard='BG1:2:132101:132102',available=true,copyResult=true,closed=0;
Object.assign(c,{nameField:{text:'',setSelection(){}},exchangeMessage:{text:'',scrollV:1},ready:true,nameOpen:true,exchangeImport:true,exchangeQuotedCode:'',nameRevision:7,revision:7,textPurpose:3,
 closeNameInput:()=>{closed++;c.nameOpen=false;},getDefinitionByName:()=>{if(!available)throw Error('missing');return {generalClipboard:{getData:()=>clipboard,setData:(format,value)=>{clipboard=value;return copyResult;}}};}});
vm.runInContext(['clipboardText','copyExchange','pasteExchange','submitDeckExchange','setDeckExchange'].map(fn).join('\n'),c);
c.pasteExchange();check(c.nameField.text===clipboard&&c.exchangeQuotedCode==='','paste preserves whole ASCII code');
clipboard='x'.repeat(321);const before=c.nameField.text;c.pasteExchange();check(c.nameField.text===before,'oversized paste cannot truncate into another deck');
available=false;c.pasteExchange();check(c.nameField.text===before&&c.exchangeMessage.text.includes('Встав'),'missing API preserves input');available=true;
const calls=c.calls.length;c.submitDeckExchange(true);check(c.calls.length===calls,'craft needs prior quote');
c.submitDeckExchange();check(c.calls.at(-1)[0]==='OnBetaGwentDeckImport'&&c.calls.at(-1)[1][2]===false,'preview never authorizes craft');
c.setDeckExchange(7,'','Недостающие карты',false);check(c.exchangeQuotedCode===before&&closed===0,'missing list keeps modal open');
c.submitDeckExchange(true);check(c.calls.at(-1)[1][2]===true,'explicit craft confirmation');
c.nameField.text+='1';const after=c.calls.length;c.submitDeckExchange(true);check(c.calls.length===after,'changed composition needs new quote');
c.nameRevision=6;c.submitDeckExchange();check(c.calls.length===after,'stale modal ignored');c.nameRevision=7;
c.setDeckExchange(6,'','old',true);check(closed===0,'stale reply ignored');
c.setDeckExchange(7,'','done',true);check(closed===1,'accepted reply closes modal');
c.nameOpen=true;c.textPurpose=4;c.exchangeImport=false;c.setDeckExchange(7,'BG1:2:132101:132102','',false);check(clipboard==='BG1:2:132101:132102'&&c.exchangeMessage.text.includes('скопирован'),'export copies full string automatically');
copyResult=false;c.copyExchange();check(c.exchangeMessage.text.includes('недоступен')&&!c.exchangeMessage.text.includes('скопирован'),'failed copy never reports success');
for(const directory of ['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']){
 const p=root+'BetaGwent/ui/'+directory+'/BetaGwentBoard.as',raw=fs.readFileSync(p);
 check(raw.equals(fs.readFileSync(root+'BetaGwent/ui/src/BetaGwentBoard.as'))&&raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'canonical five mirrors BOM CRLF');
}
check(s.includes('if(clipboardText().length>0){pasteExchange();')&&s.includes('if(copyExchange()){e.preventDefault();'),'native copy/paste keys remain available if the clipboard API is unavailable');
const compiledUi=process.argv[3]||base+'menus-final/ui/';
for(const directory of ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'])check(fs.readFileSync(compiledUi+directory+'/BetaGwentBoard.as').equals(fs.readFileSync(compiledUi+'src/BetaGwentBoard.as')),'compiled universal five mirrors');
const report={checks,actualActionScript:true,clipboardHostSimulated:true,languageButtons:{text,audio},gameTested:false};
fs.writeFileSync(root+'docs/evidence/features082-ui.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
