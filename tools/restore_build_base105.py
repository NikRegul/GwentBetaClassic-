"""Recreate the packaging baselines deleted on 07.10.2026 (stage 105).

Packaging reused verified first-release payloads from BetaGwent/build/release89 and a
frozen base project from BetaGwent/build/release87. Both folders are gone. This
rebuilds exactly what packaging reads, from the shipped 0.3.0-test archives:
  * release89/{ru,en}/package/.../{ru,en}.w3strings and soundspc.cache, each checked
    against the pinned hashes in docs/evidence/stage89-release-{ru,en}.json;
  * public-source89/GwentBetaClassic/{LICENSE,ATTRIBUTIONS.md};
  * BetaGwent/release/{README,CONTROLS,CHANGELOG}_{RU,EN}.md when missing;
  * release87/project/BetaGwent0924/myproject1.w3edit (GwentB project metadata with the
    shipped mod identity from info.json). Everything else of the project is overlaid
    from GwentB/myproject1 by build_language_release.py prepare.
Idempotent; never overwrites an existing file with different content silently.
"""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
REL=ROOT/'BetaGwent/release';BUILD=ROOT/'BetaGwent/build'
ARCHIVES={'ru':['GwentBetaClassic-0.3.0-test2-RU.zip','GwentBetaClassic-0.3.0-test1-RU.zip'],'en':['GwentBetaClassic-0.3.0-test1-EN.zip']}
C='Mods/modBetaGwent0924/content/'

def sha(b):return hashlib.sha256(b).hexdigest()
def archive(lang):
    for name in ARCHIVES[lang]:
        if (REL/name).exists():return zipfile.ZipFile(REL/name)
    raise SystemExit('No shipped '+lang.upper()+' archive to restore from')
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=data:raise SystemExit('Refusing to overwrite different file: '+str(path))
    path.write_bytes(data)

def main():
    report={}
    for lang in ('ru','en'):
        z=archive(lang);pinned={f['path']:f['sha256'] for f in json.loads((ROOT/f'docs/evidence/stage89-release-{lang}.json').read_text('utf8'))['files']}
        for name in ('ru.w3strings','en.w3strings','soundspc.cache'):
            data=z.read(C+name)
            if sha(data)!=pinned[C+name]:raise SystemExit(f'{lang} {name}: archive payload differs from stage89 pin')
            write(BUILD/f'release89/{lang}/package'/(C+name),data)
        for name in ('README','CONTROLS','CHANGELOG'):
            target=REL/f'{name}_{lang.upper()}.md'
            if not target.exists():target.write_bytes(z.read(f'{name}_{lang.upper()}.md'))
        for name in ('LICENSE','ATTRIBUTIONS.md'):
            target=BUILD/'public-source89/GwentBetaClassic'/name
            if not target.exists():write(target,z.read(name))
        if lang=='ru':info=json.loads(z.read('Mods/modBetaGwent0924/info.json'))
        report[lang]=z.filename
    meta=json.loads((ROOT/'GwentB/myproject1/myproject1.w3edit').read_text('utf8'))
    meta.update({k:info[k] for k in ('name','modName','version','gameVersion','author','dependencies') if k in info})
    meta.update(thumbnail='',useLooseScripts=False,succesfullyCooked=False)
    project=BUILD/'release87/project/BetaGwent0924';project.mkdir(parents=True,exist_ok=True)
    (project/'myproject1.w3edit').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n','utf8')
    (ROOT/'docs/evidence/stage105-restored-build-base.json').write_text(json.dumps(dict(sources=report,
        restored=['release89 w3strings+soundspc.cache (stage89 pins)','public-source89 LICENSE/ATTRIBUTIONS','release87 w3edit'],
        modName=meta.get('modName'),name=meta.get('name')),indent=2)+'\n','utf8')
    print('Restored packaging baselines from',report,'; mod',meta.get('name'),meta.get('modName'))

if __name__=='__main__':main()
