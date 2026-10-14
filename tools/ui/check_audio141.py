"""Execute real audio and request handlers against controlled clocks and swaps."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
import ws2js
def main():
    p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    dev=ROOT/'BetaGwent/development/scripts/game/betagwent'
    source=(dev/'developmentBoardMenu.ws').read_text('utf-8-sig')
    start=source.index('    event OnBetaGwentRequestSelect(');end=source.index('    event OnBetaGwentRequestFinish(',start)
    gate=a.output.parent/'mulligan-bridge141.ws';gate.parent.mkdir(parents=True,exist_ok=True)
    gate.write_text('''class CBetaMulliganBridge extends IScriptable {
public var revision, publications : int;
public var duel, session, requestFlow : IScriptable;
public var audio : CBetaGwentDuelAudio;
public function AcceptRevision(value:int):bool{return value==revision;}
public function Publish(message:string){publications+=1;}
'''+source[start:end].replace('event OnBetaGwentRequestSelect(', 'public function OnBetaGwentRequestSelect(').replace('itemId : int)\n','itemId : int) : bool\n')+'}\n','utf8')
    launch_start=source.index('    event OnBetaGwentAudioSpellLaunch(')
    launch_end=source.index('    event OnBetaGwentAudioCue(',launch_start)
    gate_source=gate.read_text('utf8')
    gate_source=gate_source[:-2]+'public var configured : bool;\npublic var audioRevisions, spellLaunchRevisions : array<int>;\npublic var audioFrames : array<CBetaGwentDuelVisualFrame>;\n'+source[launch_start:launch_end].replace('event OnBetaGwentAudioSpellLaunch(', 'public function OnBetaGwentAudioSpellLaunch(').replace('clock : int)\n','clock : int) : bool\n')+'}\n'
    gate.write_text(gate_source,'utf8')
    reports=[]
    for lang in ('ru','en','de','it','pt-br'):
        catalog=ROOT/f'BetaGwent/build/stage141/{lang}/sources/scripts/game/betagwent/duelAudioCatalog.ws'
        code,_=ws2js.build([dev/'duelAudio.ws',catalog,gate],[])
        script=a.output.parent/f'audio141-{lang}.js'
        script.write_text((a.snapshot/'runtime.js').read_text('utf8')+'\n'+code+'\n'+r'''
let clock=0,loaded=true,events=[],checks=0;const StringToFloat=Number;
const theGame={GetEngineTimeAsSeconds(){return clock;},GetInGameConfigWrapper(){return {GetVarValue(){return '70';}};}};
const theSound={SoundIsBankLoaded(){return loaded;},SoundLoadBank(){},SoundUnloadBank(){},SoundGlobalParameter(){},SoundEvent(name){events.push(name);}};
Host.random=()=>0;
function check(v,n){if(!v)throw Error(n);checks++;}
function audio(){const a=new CBetaGwentDuelAudio();a.Initialize();a.SetClock(clock*1000);events=[];return a;}
const roar='bg79_vo_ArachasQueen',oldRoar=BetaGwentAudioEffect(201743),swap=BetaGwentAudioUi(5);
clock=0;const lightning=audio();lightning.SpellLaunch(113301,22);lightning.Cue(20,113301,0,0,0,0,0);
check(events.join(',')==='bg79_fx_3688214988,bg79_fx_3403686934','Alzur uses original travel and impact events');
lightning.Configure(false,true);events=[];lightning.SpellLaunch(113301,22);lightning.Cue(20,113301,0,0,0,0,0);
check(events.length===0,'muted effects suppress both lightning sounds');
clock=0;const unrelated=audio();unrelated.SpellLaunch(200224,22);check(events.join(',')==='bg79_fx_2549828339','Crow Eye uses its original dark magic travel sound');
clock=0;const launchBridge=new CBetaMulliganBridge();launchBridge.configured=true;launchBridge.audio=audio();
launchBridge.audioRevisions.PushBack(10);launchBridge.audioFrames.PushBack({kind:2,templateId:113301,sourceId:1,audioKind:22,cards:[]});
check(!launchBridge.OnBetaGwentAudioSpellLaunch(9,100)&&events.length===0,'stale or invented launch revision rejected');
check(launchBridge.OnBetaGwentAudioSpellLaunch(10,100)&&events.filter(x=>x==='bg79_fx_3688214988').length===1,'validated frame launches lightning once');
check(!launchBridge.OnBetaGwentAudioSpellLaunch(10,100)&&events.length===1,'duplicate UI launch cannot replay the sound');
launchBridge.audioRevisions.PushBack(11);launchBridge.audioFrames.PushBack({kind:2,templateId:200224,sourceId:1,audioKind:22,cards:[]});
check(launchBridge.OnBetaGwentAudioSpellLaunch(11,100)&&events.at(-1)==='bg79_fx_2549828339','Crow Eye launches its own original audio through the validated bridge');
launchBridge.audioRevisions.PushBack(12);launchBridge.audioFrames.PushBack({kind:2,templateId:113301,sourceId:0,audioKind:22,cards:[]});
check(!launchBridge.OnBetaGwentAudioSpellLaunch(12,100),'weather cannot masquerade as a special-card launch');
for(const pair of [[201743,200166],[200166,201743],[201743,201743]]){
 clock=0;const a=audio();a.Intro(...pair);const deadlines=[];
 for(let t=1;t<=120&&a.IsIntroActive();t++){deadlines.push(a.voiceUntil);clock=t*.25;a.SetClock(clock*1000);a.Tick();}
 check(events.filter(x=>x===roar).length===pair.filter(x=>x===201743).length,'Queen intro in either seat, including mirror');
 check(!a.IsIntroActive()&&deadlines.some(x=>x>=3.739),'roar is spaced using original WAV duration');
}
clock=0;let a=audio();a.Cue(1,201743,0,0,0,0,0);
check(events.filter(x=>x===roar).length===1&&!events.includes(oldRoar),'Queen play queues one original roar');
check(a.IsVoiceActive()&&a.musicDucked,'play roar participates in voice timing and music mix');
a.CancelIntro();check(a.IsVoiceActive(),'intro cancel does not cancel a played card');a.Cancel();
check(!a.IsVoiceActive()&&events.includes('bg79_stop_voice'),'cancel stops creature voice');
clock=0;a=audio();a.Intro(201743,200166);a.CancelIntro();clock=20;a.SetClock(20000);a.Tick();
check(events.filter(x=>x===roar).length===1&&!a.IsIntroActive(),'skip clears later introductory lines');
for(const kind of [24,25]){clock=0;a=audio();a.Cue(kind,201743,0,0,0,0,0);check(!events.includes(roar),'reveal/transform cannot repeat Queen call');}
for(const settings of [[true,false],[false,true],[false,false]]){
 clock=0;a=audio();a.Configure(...settings);events=[];a.Cue(1,201743,0,0,0,0,0);
 check(events.includes(roar)===settings[1],'voice toggle controls creature call');
 check(!events.includes(oldRoar)&&events.includes('bg79_fx_1979737770')===settings[0],'leader play uses gold landing without a separate entrance effect');
 events=[];a.Intro(201743,200166);check(events.includes(roar)===settings[1],'intro respects voice toggle');
}
loaded=false;clock=0;a=audio();a.Intro(201743,200166);a.Cue(1,201743,0,0,0,0,0);
check(!a.IsVoiceActive()&&!events.includes(roar),'missing bank cannot gate or request a missing roar');
a.Ui(1);a.Ui(5);check(events.includes('gui_gwint_draw_card'),'replacement fallback survives same-tick click');loaded=true;
clock=0;a=audio();a.Ui(1);a.Ui(5);check(events.filter(x=>x===swap).length===1,'replacement sound bypasses generic click throttle');
a.Configure(false,true);events=[];a.Ui(5);check(events.length===0,'muted effects mute replacements');
clock=0;a=audio();const b=new CBetaMulliganBridge();b.audio=a;b.revision=10;b.session={GetMessage(){return '';}};
const leaders=[131101,200055,200158,200159,200160,200161,200162,200163,200164,200165,200166,200167,200168,200169,200170,201580,201587,201589,201595,201597,201743];
for(const id of leaders){
 clock=0;const leaderAudio=audio();leaderAudio.Configure(true,false);events=[];leaderAudio.Cue(1,id,0,0,0,0,0);
 check(events.length===1&&events[0]==='bg79_fx_1979737770','each leader plays with gold landing and no entrance SFX '+id);
 leaderAudio.Intro(id,id);events=[];leaderAudio.LeaderEntrance(id,2);
 check(events.length===1&&events[0]===(BetaGwentAudioEffect(id)||'bg79_fx_1979737770'),'original leader SFX is reserved for its introduction '+id);
 leaderAudio.LeaderEntrance(id,2);check(events.length===1,'same entrance cannot sound twice '+id);
 leaderAudio.LeaderEntrance(id,1);check(events.length===2,'mirror leader has a separate entrance in each seat '+id);
}
clock=0;a=audio();a.Intro(131101,200055);events=[];a.LeaderEntrance(200055,2);a.LeaderEntrance(131101,0);check(events.length===0,'wrong leader or seat cannot request an entrance effect');
let swaps=0,allowed=true,mulligan=true,finishWithoutSwap=false;
b.duel={IsPending(){return mulligan;},IsMulligan(){return mulligan;},MulliganSwapCount(){return swaps;},SelectMulligan(request,item){if(request!==7||item!==8||!allowed)return false;if(!finishWithoutSwap)swaps++;mulligan=false;return true;}};
for(const args of [[9,7,1,1,8],[10,7,2,1,8],[10,6,1,1,8],[10,7,1,1,9]]){
 events=[];b.OnBetaGwentRequestSelect(...args);check(!events.includes(swap),'stale, wrong side/request/item cannot sound');
}
allowed=false;events=[];b.OnBetaGwentRequestSelect(10,7,1,1,8);check(!events.includes(swap),'rejected swap cannot sound');
allowed=true;finishWithoutSwap=true;events=[];b.OnBetaGwentRequestSelect(10,7,1,1,8);check(!events.includes(swap),'empty-deck finish cannot sound');
mulligan=true;finishWithoutSwap=false;events=[];b.OnBetaGwentRequestSelect(10,7,1,1,8);
check(swaps===1&&events.filter(x=>x===swap).length===1,'successful final replacement sounds exactly once after state change');
launchBridge.audioRevisions.PushBack(13);launchBridge.audioFrames.PushBack({kind:2,templateId:200224,sourceId:1,targetId:1,audioKind:22,cards:[]});
check(!launchBridge.OnBetaGwentAudioSpellLaunch(13,100),'self trigger cannot launch a projectile sound');
launchBridge.audioRevisions.PushBack(14);launchBridge.audioFrames.PushBack({kind:2,templateId:200224,sourceId:1,audioKind:22,cards:[{card:{instanceId:1,positionPlayerId:2,tokenMask:8}}]});
check(!launchBridge.OnBetaGwentAudioSpellLaunch(14,100),'hidden ambush cannot identify itself through projectile audio');
launchBridge.audioRevisions.PushBack(15);launchBridge.audioFrames.PushBack({kind:3,templateId:200224,sourceId:1,targetId:2,audioKind:3,cards:[]});
check(launchBridge.OnBetaGwentAudioSpellLaunch(15,100)&&events.at(-1)==='bg79_fx_2549828339','collapsed Crow death revision still launches original projectile audio');
clock=0;const crowDeath=audio();crowDeath.Configure(true,false);events=[];crowDeath.Cue(3,200224,0,0,0,0,0);
check(events.join(',')==='bg79_fx_565602893','collapsed Crow death revision sounds the original dark impact');
const elementSoundProof=JSON.parse(require('fs').readFileSync('docs/evidence/element-audio164.json','utf8')).bindings;
for(const p of elementSoundProof){
 const kind=p.operation===1?22:21;
 check(BetaGwentAudioElement164(p.templateId,kind,p.launch)===p.event,'original elemental mapping '+p.templateId);
 clock=0;const sound=audio();sound.Configure(true,false);events=[];
 if(p.launch)sound.SpellLaunch(p.templateId,kind);else sound.Cue(kind,p.templateId,0,0,0,0,0);
 check(events.includes(p.event),'actual audio plays original event '+p.templateId);
}
console.log(JSON.stringify({checks,actualWitcherScript:true,nativePlaybackVerified:false}));
''','utf8')
        r=subprocess.run(['node',str(script)],capture_output=True,text=True,encoding='utf8')
        if r.returncode:raise RuntimeError(r.stdout+r.stderr)
        reports.append(dict(language=lang,**json.loads(r.stdout.strip().splitlines()[-1])))
    a.output.write_text(json.dumps(dict(reports=reports,sources={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [dev/'duelAudio.ws',dev/'developmentBoardMenu.ws']}),indent=2)+'\n','utf8')
    print(json.dumps(reports))
if __name__=='__main__':main()
