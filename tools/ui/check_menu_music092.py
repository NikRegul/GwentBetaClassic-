"""Execute the production editor music lifecycle; no game playback claim."""
from pathlib import Path
import argparse, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'));import ws2js
def main():
    p=argparse.ArgumentParser();p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    code,_=ws2js.build([ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws'],[])
    script=out/'lifecycle.js'
    script.write_text((a.snapshot/'runtime.js').read_text('utf8')+'\n'+code+'\n'+r'''
let checks=0,events=[],loads=[],unloads=[],loaded=new Set();
function check(v,n){if(!v)throw Error(n);checks++;}
function BetaGwentAudioBankInstalled(){return false;}
const theSound={SoundIsBankLoaded:n=>loaded.has(n),SoundLoadBank(n){loads.push(n);},SoundUnloadBank(n){unloads.push(n);loaded.delete(n);},SoundEvent(n){events.push(n);},SoundGlobalParameter(){}};
const a=new CBetaGwentDuelAudio();a.SetClock(0);
a.SetEditorMusic(true);a.SetEditorMusic(true);
check(loads.join(',')==='betagwentmenu.bnk','one bank load while waiting');
check(events.length===0,'native music is not paused before the new bank is ready');
loaded.add('betagwentmenu.bnk');a.Tick();
check(events.join(',')==='music_pause,bg_menu_music_play','ready tick pauses existing music and starts editor');
for(let i=0;i<20;i++)a.SetEditorMusic(true);
check(events.length===2&&loads.length===1,'editing and republishing do not restart the track');
a.enabled=false;a.voices=false;a.Tick();
check(events.length===2,'music is independent of effects and dialogue switches');
a.SetEditorMusic(false);
check(events.slice(-2).join(',')==='bg_menu_music_stop,music_resume','leaving editor restores native music');
check(unloads.join(',')==='betagwentmenu.bnk','owned music bank is released');
a.SetEditorMusic(false);check(events.length===4&&unloads.length===1,'repeated close is harmless');
const b=new CBetaGwentDuelAudio();b.SetEditorMusic(true);b.SetEditorMusic(false);
check(events.length===4,'cancel before ready never resumes someone else music');
loaded.add('betagwentmenu.bnk');const c=new CBetaGwentDuelAudio();c.SetEditorMusic(true);const before=unloads.length;c.Close();
check(unloads.length===before&&loaded.has('betagwentmenu.bnk'),'preloaded bank is borrowed and preserved');
check(events.slice(-2).join(',')==='bg_menu_music_stop,music_resume','closing the menu stops its track');
console.log(JSON.stringify({checks,actualWitcherScript:true,nativePlaybackVerified:false}));
''','utf8')
    r=subprocess.run(['node',str(script)],capture_output=True,encoding='utf8');(out/'result.log').write_text(r.stdout+r.stderr,'utf8');assert r.returncode==0,r.stdout+r.stderr
    report=json.loads(r.stdout.strip().splitlines()[-1]);(out/'result.json').write_text(json.dumps(report,indent=2),'utf8');print(report)
if __name__=='__main__':main()
