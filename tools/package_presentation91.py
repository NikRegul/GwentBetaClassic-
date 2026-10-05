"""Package the validated stage91 visuals as separate RU/EN previews."""
from pathlib import Path
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
VERSION='0.2.1-preview.1'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    completed=json.loads((ROOT/'docs/evidence/stage91-completion.json').read_text('utf8'))
    assert len(completed['menus'])==6
    for item in completed['menus']:assert sha(Path(item['resource']))==item['sha256']
    for language in ('ru','en'):
        base=ROOT/f'BetaGwent/build/release91/{language}'
        logs=base/'preview-logs';logs.mkdir(parents=True,exist_ok=True)
        def step(name):
            print('Package',language.upper(),name,flush=True)
            command=[sys.executable,'-X','utf8',str(ROOT/'tools/build_language_release.py'),name,
                     '--stage','91','--version',VERSION,'--language',language,
                     '--compiled',str(ROOT/f'BetaGwent/build/board-compile90{language}')]
            with (logs/(name+'.txt')).open('w',encoding='utf8') as out:
                result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode:
                print((logs/(name+'.txt')).read_text('utf8')[-10000:]);raise RuntimeError('Package step failed '+language+' '+name)
        if not (base/'frozen.json').exists():step('prepare')
        # Script code has not changed in stage91. Reuse the native stage90
        # compilation only after matching every package source byte for byte.
        compile_report=json.loads((ROOT/f'BetaGwent/build/board-compile90{language}/result.json').read_text('utf8'))
        for item in compile_report['patchSourcesBefore']:
            assert sha(base/'project/BetaGwent0924/workspace/scripts'/item['path'])==item['sha256']
        step('cook')
        # Item strings and audio are unchanged. Reuse only verified first-release
        # payloads, avoiding another unnecessary Wwise or string compiler run.
        old=ROOT/f'BetaGwent/build/release89/{language}/package'
        frozen=json.loads((ROOT/f'docs/evidence/stage89-release-{language}.json').read_text('utf8'))
        content=base/'package/Mods/modBetaGwent0924/content';content.mkdir(parents=True,exist_ok=True)
        database='LocalEditorStringDataBaseW3_UTF8_mod.db'
        with sqlite3.connect(base/'project/BetaGwent0924'/database) as current, sqlite3.connect(ROOT/f'BetaGwent/build/release89/{language}/project/BetaGwent0924'/database) as previous:
            assert current.execute('select * from STRINGS order by rowid').fetchall()==previous.execute('select * from STRINGS order by rowid').fetchall(),'Item strings changed; recook required'
        records={item['path']:item for item in frozen['files']}
        for name in ('ru.w3strings','en.w3strings','soundspc.cache'):
            relative='Mods/modBetaGwent0924/content/'+name
            assert sha(old/relative)==records[relative]['sha256']
            shutil.copyfile(old/relative,content/name)
        for name in ('dependencies','pack','metadata','archive'):step(name)
    print('RU/EN preview archives ready; originals unchanged.',flush=True)

if __name__=='__main__':main()
