const fs=require('fs'),vm=require('vm'),assert=require('assert');
const ctx=vm.createContext({console});
vm.runInContext(`
class IScriptable{}
function StringToFloat(v){return Number(v)||0;}
var facts={},speech='EN',text='RU',setupText='0',setupVoice='0';
function FactsQueryLatestValue(k){return facts[k]||0;}
function FactsSet(k,v){facts[k]=v;}
function Clamp(v,a,b){return Math.max(a,Math.min(b,v));}
var theGame={GetGameLanguageName(a,t){a.v=speech;t.v=text;},GetInGameConfigWrapper(){return {GetVarValue(g,k){return k==='BetaGwentVoiceLanguage'?setupVoice:setupText;}};}};
`+fs.readFileSync(__dirname+'/universal_languages.js','utf8'),ctx);
let checks=0;const board=fs.readFileSync('D:/w3mod/BetaGwent/build/universal081/nextgen-sources/game/betagwent/developmentBoardMenu.ws','utf8');assert(board.includes('BetaGwentInitializeLanguages();'));assert(board.includes('PublishLanguageSettings();'));assert(!board.includes('FlashArgInt(BetaGwentTextLanguage137('));checks+=3;function test(code,name){assert(vm.runInContext(code,ctx),name);checks++;}
for(const [code,id] of [['ESMX',8],['ZHCN',12],['ZHTW',13],['RU',1],['EN',2],['DE',3],['FR',4],['IT',5],['PL',6],['ES',7],['MX',8],['BR',9],['JP',10],['KR',11],['CN',12],['TW',13],['AR',2],['ZZ',2]])test(`text='${code}';BetaGwentGameTextLanguage()===${id}`,'text '+code);
for(const [code,id] of [['RU',1],['EN',2],['DE',3],['IT',4],['BR',5],['PT-BR',5],['PL',2],['FR',2],['ES',2],['ZZ',2]])test(`speech='${code}';BetaGwentGameVoiceLanguage()===${id}`,'voice '+code);
test(`facts={};setupVoice='3';setupText='4';BetaGwentInitializeLanguages();facts.bg_voice_language===3&&facts.bg_text_language===4`,'first install applies independent defaults');
test(`setupVoice='1';setupText='1';BetaGwentInitializeLanguages();facts.bg_voice_language===3&&facts.bg_text_language===4`,'updating installer defaults preserves saved choices');
test(`facts={bg_text_language:6};setupVoice='2';BetaGwentInitializeLanguages();facts.bg_text_language===6&&facts.bg_voice_language===2`,'existing text selection preserved on migration');
test(`facts={bg_language_preferences_initialized:1,bg_text_language:0,bg_voice_language:0};speech='RU';text='DE';BetaGwentInitializeLanguages();BetaGwentVoiceLanguage()===1&&BetaGwentResolvedTextLanguage()===3`,'auto choices persist as auto');
test(`speech='PL';text='JP';BetaGwentVoiceLanguage()===2&&BetaGwentResolvedTextLanguage()===10`,'unsupported voice falls back without changing text');
test(`facts.bg_voice_language=4;speech='RU';BetaGwentVoiceLanguage()===4`,'manual voice ignores game language');
test(`facts.bg_text_language=2;text='RU';BetaGwentResolvedTextLanguage()===2`,'manual text ignores game language');
test(`BetaGwentUniversalEvent(1,'bg79_voice')==='bg79_voice'&&BetaGwentUniversalEvent(5,'bg79_voice')==='bg79_voice_pt_br'`,'event namespace follows selected voice');
test(`BetaGwentUniversalEvent(2,'')===''`,'missing voice remains missing rather than an invented event');
console.log(JSON.stringify({checks,actualWitcherScript:true,nativeGameplayTested:false}));
