"""Run the real revised voice queue for every language, seat and delayed readiness."""
from pathlib import Path
import sys,subprocess,json
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release082-rc3'
if len(sys.argv)>1:BUILD=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(ROOT/'tools/ai'));import ws2js
def main():
    dev=BUILD/'scripts/game/betagwent';code,_=ws2js.build([dev/n for n in ['duelAudio.ws','duelAudioCatalog.ws','universalLanguages.ws']],[])
    tests=r'''
let clock=0,loaded=true,events=[],checks=0,voiceLanguage=1;const StringToFloat=Number;
const FactsQueryLatestValue=name=>name==='bg_voice_language'?voiceLanguage:0;
const theGame={GetEngineTimeAsSeconds(){return clock;},GetGameLanguageName(){return 'EN';},GetInGameConfigWrapper(){return {GetVarValue(){return '70';}};}};
const theSound={SoundIsBankLoaded(){return loaded;},SoundLoadBank(){},SoundUnloadBank(){},SoundGlobalParameter(){},SoundEvent(name){events.push({name,at:clock});}};
Host.random=()=>0;function check(v,n){if(!v)throw Error(n);checks++;}
function create(){const a=new CBetaGwentDuelAudio();a.Initialize();a.SetClock(0);events=[];return a;}
function tick(a,t){clock=t;a.SetClock(Math.round(t*1000));a.Tick();}
for(voiceLanguage=1;voiceLanguage<=5;voiceLanguage++)for(const leaders of [[201743,200166],[200166,201743],[201743,201743]]){
 clock=0;const a=create();a.Intro(...leaders);const roar=BetaGwentUniversalEvent(voiceLanguage,'bg79_vo_ArachasQueen');
 tick(a,1);check(!events.some(e=>e.name===roar),'no roar before portrait readiness');
 a.MarkIntroReady(2);a.MarkIntroReady(1);
 let firstAt=-1,side=0;for(let step=0;step<120&&a.IsIntroActive();step++){
  tick(a,1.25+step*.25);
  if(a.IntroVoiceSide()!==side){side=a.IntroVoiceSide();const matches=events.filter(e=>e.name===roar);
   check(a.IntroVoiceClock()===Math.round(clock*1000),'ack uses the actual shared Flash clock');
   if(a.IntroVoiceTemplate()===201743){check(matches.length>0&&matches.at(-1).at===clock,'Queen animation ack and roar start coincide');if(firstAt<0)firstAt=clock;}
  }
 }
 check(!a.IsIntroActive(),'intro queue completes');check(events.filter(e=>e.name===roar).length===leaders.filter(id=>id===201743).length,'exactly one roar for each Queen');
 a.CancelIntro();check(a.IntroVoiceSide()===0,'cancel clears stale start acknowledgements');
}
clock=0;const waiting=create();waiting.Intro(201743,200166);tick(waiting,5);check(waiting.IntroVoiceSide()===0,'slow first page cannot start audio early');waiting.MarkIntroReady(2);tick(waiting,5.25);check(waiting.IntroVoiceClock()===5250,'late readiness schedules the true start, not a fixed delay');waiting.CancelIntro();tick(waiting,50);check(!waiting.IsIntroActive(),'skip cancels pending leader');
for(const settings of [[true,false],[false,true],[false,false]]){clock=0;const a=create();a.Configure(...settings);events=[];a.Intro(201743,200166);a.MarkIntroReady(2);a.MarkIntroReady(1);tick(a,1.25);check((a.IntroVoiceSide()>0)===settings[1],'voice toggle controls acknowledgements independently of effects');a.Cancel();}
loaded=false;clock=0;const missing=create();missing.Intro(201743,200166);missing.MarkIntroReady(2);tick(missing,5);check(!missing.IsIntroActive()&&missing.IntroVoiceSide()===0,'missing bank never holds VS behind an inactive audio queue');
console.log(JSON.stringify({checks,languages:5,actualWitcherScript:true,nativePlaybackVerified:false}));
'''
    path=BUILD/'intro-audio-tests.js';path.write_text((ROOT/'tools/ai/jshost/runtime.js').read_text('utf8')+'\n'+code+'\n'+tests,'utf8')
    r=subprocess.run(['node',str(path)],capture_output=True,text=True,encoding='utf8');print(r.stdout,r.stderr);assert r.returncode==0
    (BUILD/'intro-audio-tests.json').write_text(json.dumps(json.loads(r.stdout),indent=2),'utf8')
if __name__=='__main__':main()
