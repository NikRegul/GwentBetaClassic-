'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(process.argv[2]||'BetaGwent/development/scripts/game/betagwent/duelAudio.ws','utf8');
function extract(n){const a=source.indexOf('function '+n+'('),o=source.indexOf('{',a);let end=o+1,d=1;while(d){d+=(source[end]==='{')-(source[end]==='}');end++;}
 return source.slice(a,end).replace(/:\s*(int|string|float)\b/g,'').replace(/(\d+(?:\.\d+)?)f\b/g,'$1');}
const emitted=[];let checks=0;const failures=[];function check(v,n){checks++;if(!v)failures.push(n);}
const c=vm.createContext({enabled:true,time:1,nextClick:0,nextBetaUiClick:0,lastBetaUiKind:0,Now:()=>c.time,BetaReady:()=>true,
 BetaGwentAudioUi:()=>'',theSound:{SoundEvent:n=>emitted.push(n)}});
vm.runInContext(extract('BetaGwentAudioUi096')+'\n'+extract('Ui'),c);
const want={14:1126876212,15:347636528,16:2518508117,17:3223397756,18:186293181,19:3623975022,20:2909756106,21:3558782073,22:310403972,23:331755273,24:827469296};
const ref=JSON.parse(fs.readFileSync('docs/evidence/beta-sound-events86.json'));
for(const [kind,id]of Object.entries(want)){
 check(ref.ui.some(x=>(Number(x.eventId)>>>0)===id),'original beta event '+id);
 c.time++;c.Ui(1);c.Ui(Number(kind));check(emitted.at(-1)==='bg79_fx_'+id,'window cue survives preceding generic mouse/pad click '+kind);
 const n=emitted.length;c.Ui(Number(kind));check(emitted.length===n,'repeat cue debounced '+kind);
 for(const project of ['wwise','wwise-en89','wwise-de137','wwise-it137','wwise-pt-br137'])check(fs.readFileSync('BetaGwent/audio/'+project+'/Events/BetaGwent79.wwu','utf8').includes('bg79_fx_'+id),'event imported in '+project+'/'+id);
}
c.enabled=false;const n=emitted.length;c.time++;c.Ui(20);check(emitted.length===n,'sound toggle mutes new windows');
vm.runInContext(extract('ArmorBreak099'),c);
c.enabled=true;c.ArmorBreak099();check(emitted.at(-1)==='bg79_fx_2876994866','armor depletion emits original Beta ArmorDecrease event');
c.enabled=false;const muted=emitted.length;c.ArmorBreak099();check(emitted.length===muted,'sound toggle mutes armor break');
c.enabled=true;c.BetaReady=()=>false;c.ArmorBreak099();check(emitted.at(-1)==='gui_gwint_gem_destruction','armor break has a native sound fallback');
for(const project of ['wwise','wwise-en89','wwise-de137','wwise-it137','wwise-pt-br137'])check(fs.readFileSync('BetaGwent/audio/'+project+'/Events/BetaGwent79.wwu','utf8').includes('bg79_fx_2876994866'),'armor event shipped in '+project);
const report={checks,failures,sourceSha256:require('crypto').createHash('sha256').update(fs.readFileSync(process.argv[2]||'BetaGwent/development/scripts/game/betagwent/duelAudio.ws')).digest('hex'),actualWitcherScript:true,audibleGameVerified:false};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;
