const fs=require('fs'),vm=require('vm'),assert=require('assert');
const s=fs.readFileSync('D:/w3mod/BetaGwent/build/universal081/ui/src/BetaGwentBoard.as','utf8');
function fn(name){let p=s.indexOf('function '+name+'('),open=s.indexOf('{',p),i=open+1,n=1;assert(p>=0,name);while(n){if(s[i]==='{')n++;if(s[i]==='}')n--;i++;}return s.slice(p,i).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'');}
let checks=0;function check(v,n){assert(v,n);checks++;}
const c=vm.createContext({Math,requestedTextLanguage:0,requestedVoiceLanguage:0,resolvedVoiceLanguage:2,gameTextLanguage:2,gameVoiceName:'EN',controllerMenuOpen:false,ready:true,calls:[],renders:0,
 BetaGwentTextLanguage:{language:1,label:()=> 'Русский'},setTextLanguage:v=>{c.resolvedText=v;},render:()=>c.renders++,closeControllerMenu:()=>{c.controllerMenuOpen=false;},openControllerMenu:()=>{c.controllerMenuOpen=true;},send:(event,args)=>c.calls.push([event,args])});
for(const name of ['voiceNames','textWords','voiceWords','autoWords']){const m=s.match(new RegExp('private const '+name+':Array=(\\[[^;]+\\]);'));assert(m,name);c[name]=vm.runInContext(m[1],c);}
vm.runInContext(['setLanguageSettings','cycleTextLanguage','cycleVoiceLanguage','textChoiceLabel','voiceChoiceLabel'].map(fn).join('\n'),c);
c.setLanguageSettings(0,0,2,1,1,'PL');check(c.resolvedText===1&&c.voiceChoiceLabel().includes('PL → EN'),'independent auto values and explicit fallback label');
for(let i=1;i<=14;i++){c.cycleTextLanguage();check(c.calls.at(-1)[0]==='OnBetaGwentTextLanguage'&&c.calls.at(-1)[1][0]===i%14,'text cycle '+i);}
check(c.resolvedText===1,'auto restores game text');
for(let i=1;i<=6;i++){c.cycleVoiceLanguage();check(c.calls.at(-1)[0]==='OnBetaGwentVoiceLanguage'&&c.calls.at(-1)[1][0]===i%6,'voice cycle '+i);}
check(c.requestedTextLanguage===0,'voice cycle leaves text unchanged');
c.controllerMenuOpen=true;c.setLanguageSettings(3,4,4,1,3,'RU');check(c.controllerMenuOpen&&c.requestedTextLanguage===3&&c.requestedVoiceLanguage===4,'settings update retains controller menu and independent choices');
check(!fn('textLanguageReady').includes('OnBetaGwentTextLanguage'),'resource-ready callback does not overwrite auto with resolved language');
check(s.includes('voiceChoiceLabel(),340,28,276,42')&&s.includes('textChoiceLabel(),52,28,276,42'),'adjacent buttons fit before header plaque');
console.log(JSON.stringify({checks,actualActionScriptMethods:true,nativeGameplayTested:false}));
