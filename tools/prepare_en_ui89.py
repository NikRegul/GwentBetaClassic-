from pathlib import Path
import shutil,subprocess,sys,wave,re,json
ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'BetaGwent/build/release89/en-source'
event_keys={m['event']:m['key'] for m in json.loads((ROOT/'docs/evidence/audio-import79.json').read_text('utf8'))['media']}
shutil.copytree(ROOT/'BetaGwent/ui/assets',target/'assets',dirs_exist_ok=True)
shutil.copytree(ROOT/'BetaGwent/ui/src/mx',target/'ui/mx',dirs_exist_ok=True)
# The bank has identical event names but language-specific phrase durations.
p=target/'scripts/game/betagwent/duelAudioCatalog.ws';s=p.read_text('utf-8-sig')
voice_functions={}
for m in re.finditer(r'function (BetaGwentAudioVoice(?:\d+|VariantPart\d+))\([^\n]+\n\{(.*?)\n\}',s,re.S):voice_functions[m[1]]=m[2]
def update(m):
    header,body=m[1],m[2]
    name=re.search(r'function (\w+)',header)[1]
    name=name.replace('VoiceVariantDurationPart','VoiceVariantPart').replace('VoiceDuration','Voice')
    values=voice_functions.get(name)
    if not values:return m[0]
    returns=re.findall(r'return "(bg79_vo_[^"]+)";',values)
    events=iter(returns)
    def duration(n):
        event=next(events);path=ROOT/'BetaGwent/audio/wwise-en89/Originals/SFX/BetaGwent79'/(event_keys[event]+'.wav')
        with wave.open(str(path)) as w:sec=w.getnframes()/w.getframerate()
        return 'return '+f'{sec:.3f}f'+';'
    body=re.sub(r'return (?!0\.0f)[0-9.]+f;',duration,body)
    return header+body+'\n}'
s=re.sub(r'(function BetaGwentAudioVoice(?:Duration\d+|VariantDurationPart\d+)\([^\n]+\n\{)(.*?)\n\}',update,s,flags=re.S)
p.write_text(s,'utf-8-sig')
compiled=ROOT/'BetaGwent/build/board-compile89enc'
if not (compiled/'compiled/blob.rsblob').exists():
    subprocess.run([sys.executable,str(ROOT/'tools/recon/run_redkit_compile.py'),'--out',str(compiled),'--patch',str(target/'scripts'),'--timeout','120','--terms-already-accepted'],check=True)
    report=json.loads((compiled/'result.json').read_text('utf8'))
    assert report['exitCode']==0 and not report['timedOut'], 'Native compilation failed; see result.json'
else:
    import hashlib
    prior=json.loads((compiled/'result.json').read_text('utf8'))
    assert prior['exitCode']==0 and prior['patchSourcesUnchangedDuringCompile']
    for row in prior['patchSourcesBefore']:assert hashlib.sha256((target/'scripts'/row['path']).read_bytes()).hexdigest()==row['sha256']
for entry in ('BetaGwentBoard','DeckBuilder','GwintGame'):
    for tool,args in [('build_board.py',['--reuse-assets','--source-dir',str(target/'ui')]),('check_board_bridge.py',[]),('install_native_atlas.py',['--apply'])]:
        subprocess.run([sys.executable,str(ROOT/'tools/ui'/tool),'--entry',entry,*args],check=True)
subprocess.run([sys.executable,str(ROOT/'tools/build_language_release.py'),'prepare','--language','en'],check=True)
# Restore the development project to Russian; frozen English keeps its own movies.
ru=ROOT/'BetaGwent/build/release89/ru/project/BetaGwent0924/workspace/betagwent'
shutil.copytree(ru,ROOT/'GwentB/myproject1/workspace/betagwent',dirs_exist_ok=True)
print('English sources, movies and project prepared; Russian workspace restored.')
