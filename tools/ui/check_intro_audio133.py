"""Translate actual RU/EN voice catalogs and audio queue; stub only native sound/clock."""
from pathlib import Path
import argparse,sys,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js
def main():
 p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);p.add_argument('output',type=Path);p.add_argument('--stage',type=int,default=133);a=p.parse_args()
 dev=ROOT/'BetaGwent/development/scripts/game/betagwent'
 # All 21 leaders in the supported Beta catalog; no dependency on review artifacts.
 leaders=[200158,201743,200055,201587,131101,200163,201580,200162,200164,200169,200168,200170,201595,200167,201589,200165,200166,200159,200160,200161,201597]
 reports=[]
 catalogs=[]
 for lang in (['en','ru','de','it','pt-br'] if a.stage>=137 else ['ru','en']):
  catalog=dev/'duelAudioCatalog.ws' if lang=='ru' else ROOT/'BetaGwent/audio/generated/duelAudioCatalog-en.ws'
  if a.stage>=137:catalog=ROOT/f'BetaGwent/build/stage{a.stage}/{lang}/sources/scripts/game/betagwent/duelAudioCatalog.ws'
  catalogs.append(catalog)
  code,_=ws2js.build([dev/'duelAudio.ws',catalog],[])
  script=a.output.parent/f'intro-audio133-{lang}.js';script.parent.mkdir(parents=True,exist_ok=True)
  script.write_text((a.snapshot/'runtime.js').read_text('utf8')+'\n'+code+'\n'+r'''
let clock=0,loaded=true,events=[],requests=[],rolls=[0,0],rollIndex=0;
const StringToFloat=Number;
const theGame={GetEngineTimeAsSeconds(){return clock;},GetInGameConfigWrapper(){return {GetVarValue(){return '70';}};}};
const theSound={SoundIsBankLoaded(){return loaded;},SoundLoadBank(){},SoundUnloadBank(){},SoundGlobalParameter(){},SoundEvent(name){events.push({time:clock,name});}};
Host.log=s=>{if(s.includes('AUDIO_VOICE_REQUEST'))requests.push({time:clock,message:s});};Host.random=()=>rolls[Math.min(rollIndex++,rolls.length-1)]/1000000;
let checks=0,pairs=0;function check(v,n){if(!v)throw Error(n);checks++;}
const leaders=LEADERS;
// Rolls are percentile thresholds, not a variant index. Enumerate each distinct
// event, then test the Cartesian product of both leaders' actual voice variants.
const variants={};for(const id of leaders){const seen=new Set();variants[id]=[];for(let roll=0;roll<100;roll++){const event=BetaGwentAudioVoiceVariant(id,roll);if(!seen.has(event)){seen.add(event);variants[id].push(roll);}}}
for(const opponent of leaders)for(const player of leaders)for(const opRoll of variants[opponent])for(const playerRoll of variants[player]){
 clock=0;events=[];requests=[];rolls=[opRoll,playerRoll];rollIndex=0;const a=new CBetaGwentDuelAudio();a.Initialize();a.SetClock(0);a.Intro(opponent,player);
 for(let t=1;t<=120&&a.IsIntroActive();t++){clock=t*.25;a.SetClock(clock*1000);a.Tick();}
 const count=[opponent,player].filter(id=>BetaGwentAudioVoice(id)!=='').length;
 check(requests.length===count,'both intro lines must survive long first voice '+opponent+'/'+player+'/'+opRoll+'/'+playerRoll);
 if(count===2)check(requests[1].time>=requests[0].time+BetaGwentAudioVoiceVariantDuration(opponent,opRoll),'intro voices must not overlap');
 check(!a.IsIntroActive(),'introduction must finish');pairs++;
}
clock=0;requests=[];const a=new CBetaGwentDuelAudio();a.Initialize();a.SetClock(0);a.Intro(leaders[0],leaders[1]);a.CancelIntro();
for(let t=1;t<=100;t++){clock=t*.25;a.SetClock(clock*1000);a.Tick();}
check(requests.length<=1&&!a.IsIntroActive(),'skip stops queued second voice');
const b=new CBetaGwentDuelAudio();b.Initialize();b.Configure(true,false);b.Intro(leaders[0],leaders[1]);check(!b.IsIntroActive(),'muted voices never gate intro');
loaded=false;const d=new CBetaGwentDuelAudio();d.Initialize();d.Intro(leaders[0],leaders[1]);check(!d.IsIntroActive(),'missing bank never gates intro');
loaded=true;clock=0;const e=new CBetaGwentDuelAudio();e.Initialize();e.SetClock(0);e.queuedVoices.push(leaders[0]);e.queuedAt.push(1);e.Tick();check(e.queuedVoices.length===1,'future ordinary cue is not played early');
e.SetClock(3000);e.Tick();check(e.queuedVoices.length===0,'ordinary stale chatter still expires');
console.log(JSON.stringify({checks,pairs,leaders:leaders.length,variantCounts:Object.fromEntries(leaders.map(id=>[id,variants[id].length])),exhaustiveLeaderVariantPairs:true,actualWitcherScript:true,nativeGameTested:false}));
'''.replace('LEADERS',json.dumps(leaders)),'utf8')
  result=subprocess.run(['node',str(script)],capture_output=True,text=True,encoding='utf8')
  if result.returncode:raise RuntimeError(result.stdout+result.stderr)
  reports.append(dict(language=lang,**json.loads(result.stdout.strip().splitlines()[-1])))
 sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [dev/'duelAudio.ws',*catalogs]}
 a.output.write_text(json.dumps(dict(reports=reports,sources=sources),indent=2)+'\n','utf8');print(json.dumps(reports))
if __name__=='__main__':main()
