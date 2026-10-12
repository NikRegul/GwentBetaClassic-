"""Run actual dialogue queue, music mix and deferred opponent code with a fake clock."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js

def main():
    parser=argparse.ArgumentParser();parser.add_argument('snapshot',type=Path);parser.add_argument('output',type=Path);parser.add_argument('--stage',type=int,default=135);a=parser.parse_args()
    dev=ROOT/'BetaGwent/development/scripts/game/betagwent'
    native=dev/'developmentBoardMenu.ws';source=native.read_text('utf-8-sig')
    start=source.index('private function ResumeOpponentAfterVoice(');end=source.index('\n    event ',start)
    gate=a.output.parent/'opponent-gate135.ws'
    gate.write_text('''class CBetaOpponentGate extends IScriptable {
public var configured,visualBusy,deferredOpponent : bool;
public var audio : CBetaGwentDuelAudio;
public var publications : int;
public var duel : CBetaFakeDuel;
public function Publish(status : string) { publications += 1; }
'''+source[start:end]+'\n}\n','utf8')
    reports=[]
    catalogs=[]
    for language in (['en','ru','de','it','pt-br'] if a.stage>=137 else ['ru','en']):
        catalog=dev/'duelAudioCatalog.ws' if language=='ru' else ROOT/'BetaGwent/audio/generated/duelAudioCatalog-en.ws'
        if a.stage>=137:catalog=ROOT/f'BetaGwent/build/stage{a.stage}/{language}/sources/scripts/game/betagwent/duelAudioCatalog.ws'
        catalogs.append(catalog)
        code,_=ws2js.build([dev/'duelAudio.ws',catalog,gate],[])
        script=a.output.parent/f'audio135-{language}.js'
        script.write_text((a.snapshot/'runtime.js').read_text('utf8')+'\n'+code+'\n'+r'''
let clock=0,loaded=true,volume='70',events=[],mix=[],checks=0;
const StringToFloat=Number;
const theGame={GetEngineTimeAsSeconds(){return clock;},GetInGameConfigWrapper(){return {GetVarValue(){return volume;}};}};
const theSound={SoundIsBankLoaded(){return loaded;},SoundLoadBank(){},SoundUnloadBank(){},
 SoundEvent(name){events.push({name,time:clock});},SoundGlobalParameter(name,value,fade){mix.push({name,value,fade});}};
Host.random=()=>0;
function check(v,n){if(!v)throw Error(n);checks++;}
const first=123301,second=132310;
const a=new CBetaGwentDuelAudio();a.Initialize();a.SetClock(0);events=[];a.Cue(1,first,0,0,0,0,0);
check(a.IsVoiceActive(),'ordinary played card starts a voice');
const deadline=a.voiceUntil;
check(mix.at(-1).name==='menu_volume_music'&&Math.abs(mix.at(-1).value-28)<.001,'music is ducked relative to user volume');
clock=.25;a.SetClock(250);a.Cue(1,second,0,0,0,0,0);
check(!events.some(e=>e.name==='bg79_stop_voice'),'next card cannot cut off the current line');
check(a.voiceUntil===deadline,'new cue preserves the current voice deadline');
for(let i=0;i<20;i++)a.Cue(1,second,0,0,0,0,0);
check(a.queuedVoices.length<=2,'summon chatter stays bounded');
const gate=new CBetaOpponentGate();gate.configured=true;gate.visualBusy=false;gate.deferredOpponent=true;gate.audio=a;gate.duel={IsPending(){return false;},GetMessage(){return '';}};
gate.ResumeOpponentAfterVoice();check(gate.publications===0&&gate.deferredOpponent,'opponent waits while the player line plays');
clock=30;a.SetClock(30000);a.Tick();gate.ResumeOpponentAfterVoice();
check(gate.publications===1&&!gate.deferredOpponent,'opponent resumes when voice and stale queue finish');
gate.ResumeOpponentAfterVoice();check(gate.publications===1,'audio ticks cannot publish the opponent twice');
check(mix.at(-1).value===70,'music returns to the user volume');
clock=31;a.SetClock(31000);a.Cue(1,first,0,0,0,0,0);volume='45';a.Cancel();
check(!a.IsVoiceActive()&&mix.at(-1).value===45,'cancel restores the current setting without writing preferences');
a.Cue(1,first,0,0,0,0,0);a.Configure(true,false);check(!a.IsVoiceActive()&&!a.musicDucked,'muting voices releases the gate and duck');
loaded=false;const missing=new CBetaGwentDuelAudio();missing.Initialize();missing.Cue(1,first,0,0,0,0,0);
check(!missing.IsVoiceActive(),'missing bank cannot block opponent');
gate.audio=missing;gate.deferredOpponent=true;gate.visualBusy=true;gate.ResumeOpponentAfterVoice();check(gate.publications===1,'visual replay still gates opponent');
gate.visualBusy=false;gate.ResumeOpponentAfterVoice();check(gate.publications===2,'missing bank allows opponent after visuals');
loaded=true;volume='70';clock=40;
const transition=new CBetaGwentDuelAudio();transition.Initialize();transition.SetClock(40000);transition.Intro(first,second);
clock=transition.voiceUntil+.01;transition.SetClock(Math.ceil(clock*1000));transition.Tick();
check(transition.IsIntroActive(),'second introductory line survives the ordinary queue timeout');
clock=transition.voiceUntil+.01;transition.SetClock(Math.ceil(clock*1000));transition.Tick();
check(!transition.IsIntroActive()&&!transition.introVoices,'completed introduction releases intro queue policy');
transition.Cue(1,first,0,0,0,0,0);transition.Cue(1,second,0,0,0,0,0);
clock=transition.voiceUntil+3;transition.SetClock(Math.ceil(clock*1000));transition.Tick();
check(!transition.IsVoiceActive()&&transition.queuedVoices.length===0,'ordinary stale chatter expires after an introduction');
console.log(JSON.stringify({checks,actualWitcherScript:true,nativePlaybackVerified:false}));
''','utf8')
        result=subprocess.run(['node',str(script)],capture_output=True,text=True,encoding='utf8')
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
        reports.append(dict(language=language,**json.loads(result.stdout.strip().splitlines()[-1])))
    paths=[dev/'duelAudio.ws',native,*catalogs]
    report=dict(reports=reports,sources={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    a.output.write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(reports))
if __name__=='__main__':main()
