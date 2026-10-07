"""English duelAudioCatalog.ws from the current Russian catalog (stage 105).

The English bank (BetaGwent/audio/wwise-en89) has the same event names; only the
spoken phrase durations differ. Same transformation as tools/prepare_en_ui89.py,
but from the live development catalog, so packaging no longer needs the deleted
BetaGwent/build/release89 project. Output: BetaGwent/audio/generated/duelAudioCatalog-en.ws
"""
from pathlib import Path
import json,re,sys,wave
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws'
OUT=ROOT/'BetaGwent/audio/generated/duelAudioCatalog-en.ws'
WAV=ROOT/'BetaGwent/audio/wwise-en89/Originals/SFX/BetaGwent79'

def main():
    event_keys={m['event']:m['key'] for m in json.loads((ROOT/'docs/evidence/audio-import79.json').read_text('utf8'))['media']}
    s=SRC.read_text('utf-8-sig');changed=[0]
    voice_functions={}
    for m in re.finditer(r'function (BetaGwentAudioVoice(?:\d+|VariantPart\d+))\([^\n]+\n\{(.*?)\n\}',s,re.S):voice_functions[m[1]]=m[2]
    cache={}
    def seconds(event):
        if event not in cache:
            with wave.open(str(WAV/(event_keys[event]+'.wav'))) as w:cache[event]=w.getnframes()/w.getframerate()
        return cache[event]
    def update(m):
        header,body=m[1],m[2]
        name=re.search(r'function (\w+)',header)[1].replace('VoiceVariantDurationPart','VoiceVariantPart').replace('VoiceDuration','Voice')
        values=voice_functions.get(name)
        if not values:return m[0]
        events=iter(re.findall(r'return "(bg79_vo_[^"]+)";',values))
        def duration(n):
            changed[0]+=1;return 'return '+f'{seconds(next(events)):.3f}f'+';'
        return header+re.sub(r'return (?!0\.0f)[0-9.]+f;',duration,body)+'\n}'
    s=re.sub(r'(function BetaGwentAudioVoice(?:Duration\d+|VariantDurationPart\d+)\([^\n]+\n\{)(.*?)\n\}',update,s,flags=re.S)
    if changed[0]<100:raise SystemExit('English duration rewrite matched only %d returns' % changed[0])
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(s,'utf-8-sig')
    print('English audio catalog:',OUT,'durations rewritten:',changed[0])

if __name__=='__main__':main()
