"""Package the validated stage94 visuals as separate RU/EN 0.2.1 packages."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.2.1'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--language',choices=['ru','en'],help='Build one language; default: both')
    parser.add_argument('--stage',type=int,default=94)
    parser.add_argument('--version',default=VERSION)
    parser.add_argument('--compiled',type=Path,help='Explicit fresh compilation for a single language')
    args=parser.parse_args()
    completed=json.loads((ROOT/f'docs/evidence/stage{args.stage}-completion.json').read_text('utf8'))
    per=4 if args.stage>=109 else 3
    assert len(completed['menus']) in (per,2*per)
    for item in completed['menus']:assert sha(Path(item['resource']))==item['sha256']
    for language in ((args.language,) if args.language else ('ru','en')):
        assert len([m for m in completed['menus'] if m['language']==language])==per
        base=ROOT/f'BetaGwent/build/release{args.stage}/{language}'
        logs=base/'preview-logs';logs.mkdir(parents=True,exist_ok=True)
        compilation=args.compiled or ROOT/f'BetaGwent/build/board-compile{args.stage}{language}'
        def step(name):
            print('Package',language.upper(),name,flush=True)
            command=[sys.executable,'-X','utf8',str(ROOT/'tools/build_language_release.py'),name,
                     '--stage',str(args.stage),'--version',args.version,'--language',language,
                     '--compiled',str(compilation)]
            with (logs/(name+'.txt')).open('w',encoding='utf8') as out:
                result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode:
                print((logs/(name+'.txt')).read_text('utf8')[-10000:]);raise RuntimeError('Package step failed '+language+' '+name)
        if not (base/'frozen.json').exists():step('prepare')
        # Gameplay changed: require the fresh stage94 script compilation.
        # Match every package source byte for byte before native cooking.
        compile_report=json.loads((compilation/'result.json').read_text('utf8'))
        for item in compile_report['patchSourcesBefore']:
            assert sha(base/'project/BetaGwent0924/workspace/scripts'/item['path'])==item['sha256']
        step('cook')
        # Item strings and audio are unchanged. Reuse only verified first-release
        # payloads, avoiding another unnecessary Wwise or string compiler run.
        old=ROOT/f'BetaGwent/build/release89/{language}/package'
        frozen=json.loads((ROOT/f'docs/evidence/stage89-release-{language}.json').read_text('utf8'))
        content=base/'package/Mods/modBetaGwent0924/content';content.mkdir(parents=True,exist_ok=True)
        database='LocalEditorStringDataBaseW3_UTF8_mod.db'
        previous_db=ROOT/f'BetaGwent/build/release89/{language}/project/BetaGwent0924'/database
        if args.stage>=109:
            # Stage 109: item strings changed (keg description) - cook them fresh; reuse only the audio cache.
            print('Item strings recooked for stage',args.stage,flush=True)
        elif previous_db.exists():
            with sqlite3.connect(base/'project/BetaGwent0924'/database) as current, sqlite3.connect(previous_db) as previous:
                assert current.execute('select * from STRINGS order by rowid').fetchall()==previous.execute('select * from STRINGS order by rowid').fetchall(),'Item strings changed; recook required'
        else:
            # Stage 105: the release89 project was deleted; item strings are pinned by the
            # stage89 w3strings hashes below (restored by tools/restore_build_base105.py).
            print('Item-string DB baseline missing; relying on pinned stage89 w3strings',flush=True)
        records={item['path']:item for item in frozen['files']}
        # Stage 109: strings (keg text) and sound bank (troll lines) are cooked fresh.
        for name in (() if args.stage>=109 else ('ru.w3strings','en.w3strings','soundspc.cache')):
            relative='Mods/modBetaGwent0924/content/'+name
            assert sha(old/relative)==records[relative]['sha256']
            shutil.copyfile(old/relative,content/name)
        if args.stage>=109:step('strings');step('audio')
        for name in ('dependencies','pack','metadata','archive'):step(name)
    print('Requested '+args.version+' archives ready; originals unchanged.',flush=True)

if __name__=='__main__':main()
