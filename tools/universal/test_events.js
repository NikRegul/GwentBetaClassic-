const fs=require('fs'),vm=require('vm'),assert=require('assert');const c=vm.createContext({console});
const source=fs.readFileSync(__dirname+'/universal_audio_rules.js','utf8');
vm.runInContext(`class IScriptable{};var voice=1;function FactsQueryLatestValue(k){return k==='bg_voice_language'?voice:0;}function FactsSet(){};function Clamp(v,a,b){return Math.max(a,Math.min(b,v));}function StringToFloat(v){return Number(v)||0;}`+source,c);
const events=new Set(JSON.parse(fs.readFileSync(__dirname+'/universal_event_ids.json')));const hashCache=new Map();
function fnv(name){if(hashCache.has(name))return hashCache.get(name);let v=2166136261;for(const b of Buffer.from(name.toLowerCase()))v=(Math.imul(v,16777619)^b)>>>0;hashCache.set(name,v);return v;}
const catalog=fs.readFileSync('D:/w3mod/BetaGwent/build/universal081/nextgen-sources/game/betagwent/duelAudioCatalog.ws','utf8');const ids=[...new Set([...catalog.matchAll(/case (\d+):/g)].map(m=>Number(m[1])))];let checks=0;
for(let lang=1;lang<=5;lang++){
 c.voice=lang;
 for(const id of ids)for(let roll=0;roll<100;roll++){
  const name=c.BetaGwentAudioVoiceVariant(id,roll);if(!name)continue;
  assert(events.has(fnv(name)),lang+'/'+id+'/'+roll+' missing '+name);assert(c.BetaGwentAudioVoiceVariantDuration(id,roll)>0,'nonempty voice duration');checks+=2;
 }
 for(const event of ['bg79_stop_voice','bg79_vo_ArachasQueen','bg79_vo_keg_ShopTrollDialogues_37']){const name=c.BetaGwentUniversalEvent(lang,event);assert(events.has(fnv(name)),name);checks++;}
}
console.log(JSON.stringify({checks,templates:ids.length,eventNamesVerified:hashCache.size,actualWitcherScript:true,nativePlaybackVerified:false}));
