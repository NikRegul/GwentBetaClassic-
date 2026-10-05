"""Stage new scripts independently of immutable first-release projects."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/'BetaGwent/build/stage90';base.mkdir(parents=True,exist_ok=True)
files=['duelSession.ws','duelArchetypeAI.ws','duelWeather.ws','duelWeatherAI.ws']
rows=[]
for name in files:
    rel='game/betagwent/'+name
    p=ROOT/'BetaGwent/development/scripts'/rel
    backup=base/'release89-sources'/rel;backup.parent.mkdir(parents=True,exist_ok=True)
    if not backup.exists():shutil.copyfile(ROOT/'BetaGwent/build/release89/ru/project/BetaGwent0924/workspace/scripts'/rel,backup)
    for dest in (ROOT/'BetaGwent/build/board-patch'/rel,ROOT/'GwentB/myproject1/workspace/scripts'/rel):shutil.copyfile(p,dest)
    rows.append(dict(path=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
p=ROOT/'data/beta924/design/english89.json';d=json.loads(p.read_text('utf8'));d['Счёт:']='Score:';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
subprocess.run([sys.executable,str(ROOT/'tools/localization89.py'),'sources','--output-dir',str(base/'en')],check=True)
en=base/'en/en-source'
shutil.copytree(ROOT/'BetaGwent/ui/src/mx',en/'ui/mx',dirs_exist_ok=True)
shutil.copytree(ROOT/'BetaGwent/ui/assets',en/'assets',dirs_exist_ok=True)
shutil.copyfile(ROOT/'BetaGwent/build/release89/en/project/BetaGwent0924/workspace/scripts/game/betagwent/duelAudioCatalog.ws',en/'scripts/game/betagwent/duelAudioCatalog.ws')
rows.append(dict(path='BetaGwent/ui/src/BetaGwentBoard.as',sha256=hashlib.sha256((ROOT/'BetaGwent/ui/src/BetaGwentBoard.as').read_bytes()).hexdigest()))
(ROOT/'docs/evidence/stage90-sources.json').write_text(json.dumps(dict(stage=90,files=rows,firstReleaseUnmodified=True,installedGameModified=False,nativeRuntimeVerified=False),indent=2)+'\n','utf8')
print('Staged RU/EN sources; first-release projects and installed game untouched.')
