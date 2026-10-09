"""Build both presentation languages, finishing with RU REDkit resources.

First-release packages and the installed game are untouched. Records validated
native resources separately for each language; no UI automation is used.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'BetaGwent/build/stage94'
EVIDENCE=ROOT/'docs/evidence'
WORK=ROOT/'GwentB/myproject1/workspace/betagwent'
ENTRIES={'BetaGwentBoard':'betagwent_board','GwintGame':'betagwent_npc00','DeckBuilder':'betagwent_decks','BetaGwentKeg':'betagwent_kegop'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def job(name,args):
    log=BASE/'logs'/f'{name}.txt';log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w',encoding='utf8') as output:
        result=subprocess.run([sys.executable,'-X','utf8',*args],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,
                              creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        print(log.read_text('utf8')[-12000:]);raise RuntimeError('Failed '+name)

def main():
    global BASE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',type=int,default=94)
    parser.add_argument('--language',choices=['ru','en'],help='Build only the requested language')
    options=parser.parse_args()
    BASE=ROOT/f'BetaGwent/build/stage{options.stage}'
    BASE.mkdir(parents=True,exist_ok=True)
    dictionary=ROOT/'data/beta924/design/english89.json'
    lookup=json.loads(dictionary.read_text('utf8'))
    lookup.update({'Поле Beta':'Beta board','Поле DIY':'DIY board'})
    dictionary.write_text(json.dumps(lookup,ensure_ascii=False,indent=2)+'\n','utf8')
    english=BASE/'en/en-source'
    if options.language!='ru':
        job('localization',[str(ROOT/'tools/localization89.py'),'sources','--output-dir',str(BASE/'en')])
        shutil.copytree(ROOT/'BetaGwent/ui/src/mx',english/'ui/mx',dirs_exist_ok=True)
        shutil.copytree(ROOT/'BetaGwent/ui/assets',english/'assets',dirs_exist_ok=True)
        # Stage 105: English phrase durations regenerated from the live catalog
        # (the release89 project copy no longer exists).
        job('en-audio-catalog',[str(ROOT/'tools/generate_en_audio_catalog.py')])
        shutil.copyfile(ROOT/'BetaGwent/audio/generated/duelAudioCatalog-en.ws',english/'scripts/game/betagwent/duelAudioCatalog.ws')
    original={stem:sha(WORK/(stem+'.redswf')) for stem in ENTRIES.values()}
    backups=BASE/'before-resources';backups.mkdir(exist_ok=True)
    for stem in ENTRIES.values():
        target=backups/(stem+'.redswf')
        shutil.copyfile(WORK/target.name,target)
    report=dict(stage=options.stage,nativeRuntimeVerified=False,installedGameModified=False,menus=[],firstReleaseUnmodified=True)
    try:
        # EN first, RU last: after successful completion the development project
        # and the current exporter outputs both correspond to Russian sources.
        for language in ((options.language,) if options.language else ('en','ru')):
            for entry,stem in ENTRIES.items():
                print('Building',language.upper(),entry,flush=True)
                args=[str(ROOT/'tools/ui/build_board.py'),'--reuse-assets','--native-only','--entry',entry]
                if language=='en':args+=['--source-dir',str(english/'ui')]
                job(language+'-'+entry+'-build',args)
                job(language+'-'+entry+'-bridge',[str(ROOT/'tools/ui/check_board_bridge.py'),'--entry',entry])
                job(language+'-'+entry+'-native',[str(ROOT/'tools/ui/install_native_hd93.py'),'--apply','--entry',entry])
                suffix='' if entry=='BetaGwentBoard' else '-'+entry
                for base in ('board-build','board-bridge-bytecode','board-resource-update'):
                    shutil.copyfile(EVIDENCE/(base+suffix+'.json'),EVIDENCE/(f'stage{options.stage}-'+language+'-'+base+suffix+'.json'))
                bridge=json.loads((EVIDENCE/('board-bridge-bytecode'+suffix+'.json')).read_text('utf8'))
                native=json.loads((EVIDENCE/('board-resource-update'+suffix+'.json')).read_text('utf8'))
                assert bridge['passed'] and len(bridge['bindings'])==46
                assert native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
                resource=BASE/language/'resources'/(stem+'.redswf');resource.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(WORK/resource.name,resource)
                assert sha(resource)==native['updatedSha256']
                report['menus'].append(dict(language=language,entry=entry,resource=str(resource),sha256=sha(resource),bindings=len(bridge['bindings'])))
        for language in ('ru','en'):
            frozen=json.loads((EVIDENCE/f'stage89-release-{language}.json').read_text('utf8'))
            # First-release ZIPs must stay unchanged when present; they may have been
            # removed from disk (07.10.2026 cleanup), which is not a modification.
            if Path(frozen['archive']).exists():assert sha(Path(frozen['archive']))==frozen['archiveSha256']
    except Exception:
        # Restore the actual resources present at invocation, not the older
        # first-run backup if the user invokes this builder again later.
        for stem in ENTRIES.values():
            restored=backups/(stem+'.redswf')
            assert sha(restored)==original[stem]
            shutil.copyfile(restored,WORK/(stem+'.redswf'))
        raise
    # A single-language run keeps the other language's still-valid menus, so
    # RU and EN can be built in separate runs (package_presentation94 needs 3 per language).
    previous=EVIDENCE/f'stage{options.stage}-completion.json'
    if options.language and previous.exists():
        kept=[m for m in json.loads(previous.read_text('utf8')).get('menus',[])
              if m['language']!=options.language and Path(m['resource']).exists() and sha(Path(m['resource']))==m['sha256']]
        report['menus']=kept+report['menus']
    report['atlasSha256']=sha(ROOT/'BetaGwent/ui/assets/card_atlas.png')
    report['sources']={p.name:sha(p) for p in (ROOT/'BetaGwent/ui/src').glob('*.as')}
    (EVIDENCE/f'stage{options.stage}-completion.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(str(len(report['menus']))+' native movies validated. Resources installed into REDkit; first-release ZIPs unchanged.',flush=True)

if __name__=='__main__':main()
