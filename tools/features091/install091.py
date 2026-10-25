"""Install verified 0.9.1 archives to the two explicitly selected local games."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[2]
TARGETS={'1.32':Path(r'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'),
         '5.0+':Path(r'F:\Steam\steamapps\common\The Witcher 3')}
MODS={'1.32':'modBetaGwentClassic132','5.0+':'modBetaGwent0924'}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def inside(p,root):
    resolved=p.resolve();assert resolved.is_relative_to(root.resolve()) and resolved!=root.resolve(),p
    assert not p.is_symlink() and not p.is_junction(),p
    return resolved

def prepare(build):
    stage=build/'install-stage';stage.mkdir(exist_ok=True)
    result={}
    release=json.loads((build/'release.json').read_text('utf8'));assert release['version']=='0.9.1'
    for platform,game in TARGETS.items():
        archive=build/f'archives/GwentBetaClassic-0.9.1-{platform}-AllLanguages.zip'
        assert sha(archive)==next(r['sha256'] for r in release['archives'] if Path(r['path']).name==archive.name)
        folder=stage/platform;folder.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            m=json.loads(z.read('manifest-0.9.1.json'))
            assert m['version']=='0.9.1' and m['gamepadHandPreviewFix'] and m['gamepadPileNavigationFix']
            expected={}
            for f in m['files']:
                n=f['path']
                if not n.startswith(('Mods/','DLC/','BetaGwentDocs/')):continue
                dest=inside(folder/n,folder);dest.parent.mkdir(parents=True,exist_ok=True)
                raw=z.read(n);assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256']
                dest.write_bytes(raw);expected[n]=f['sha256']
            assert set(p.name for p in (folder/'Mods').iterdir())=={MODS[platform]}
            assert all(p.name.startswith('dlcBetaGwent') for p in (folder/'DLC').iterdir()) if (folder/'DLC').exists() else True
        result[platform]=dict(game=str(game),source=str(folder),expected=expected)
    (stage/'plan.json').write_text(json.dumps(result,indent=2),'utf8')
    print('Verified installation staging:',stage,flush=True)
    return stage,result

def apply(stage,plan):
    # No process is stopped automatically. Both installed games must be closed.
    tasks=subprocess.run(['tasklist','/FI','IMAGENAME eq witcher3.exe','/FO','CSV','/NH'],capture_output=True,text=True)
    assert tasks.returncode==0 and '"witcher3.exe"' not in tasks.stdout.lower(),'Close The Witcher 3 before installing'
    backup=ROOT/'tmp'/('install091-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    backup.mkdir();report=dict(version='0.9.1',backup=str(backup),games={})
    operations=[]
    # Complete backups for both games before replacing either installation.
    for platform,record in plan.items():
        game=TARGETS[platform].resolve();assert game==Path(record['game']).resolve()
        assert any((game/f'bin/{variant}/witcher3.exe').is_file() for variant in ['x64','x64_dx12'])
        source=Path(record['source'])
        for top in ['Mods','DLC']:
            parent=source/top
            if not parent.exists():continue
            for directory in parent.iterdir():
                assert directory.is_dir()
                if top=='Mods':assert directory.name==MODS[platform]
                else:assert directory.name.startswith('dlcBetaGwent')
                dest=inside(game/top/directory.name,game);saved=inside(backup/platform/top/directory.name,backup)
                if dest.exists():
                    saved.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(dest,saved)
                    assert {p.relative_to(dest).as_posix():sha(p) for p in dest.rglob('*') if p.is_file()}=={p.relative_to(saved).as_posix():sha(p) for p in saved.rglob('*') if p.is_file()}
                operations.append((directory,dest,saved,game))
        docs=game/'BetaGwentDocs'
        if docs.exists():shutil.copytree(docs,backup/platform/'BetaGwentDocs')
    (backup/'plan.json').write_text(json.dumps(plan,indent=2),'utf8')
    for source,dest,saved,game in operations:
        # Each resolved removal target is a named Beta Gwent folder beneath this game.
        inside(dest,game)
        if dest.exists():shutil.rmtree(dest)
        try:shutil.copytree(source,dest)
        except Exception:
            if dest.exists():inside(dest,game);shutil.rmtree(dest)
            if saved.exists():shutil.copytree(saved,dest)
            raise
    for platform,record in plan.items():
        game=TARGETS[platform];source=Path(record['source'])
        shutil.copytree(source/'BetaGwentDocs',game/'BetaGwentDocs',dirs_exist_ok=True)
        for name,digest in record['expected'].items():assert sha(game/name)==digest,'Installed file differs: '+name
        for directory in (source/'Mods').iterdir():
            installed=game/'Mods'/directory.name
            assert {p.relative_to(installed).as_posix() for p in installed.rglob('*') if p.is_file()}=={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
        report['games'][platform]=dict(path=str(game),verifiedFiles=len(record['expected']),version='0.9.1',gameplayVerified=False)
        print('Installed and hash-verified',platform,game,flush=True)
    (stage/'installed.json').write_text(json.dumps(report,indent=2),'utf8')
    (backup/'installed.json').write_text(json.dumps(report,indent=2),'utf8')

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    build=a.build.resolve();assert build.is_relative_to((ROOT/'BetaGwent/build').resolve())
    if a.apply:
        stage=build/'install-stage';plan=json.loads((stage/'plan.json').read_text('utf8'))
        for platform,r in plan.items():
            for n,digest in r['expected'].items():assert sha(Path(r['source'])/n)==digest
        apply(stage,plan)
    else:prepare(build)

if __name__=='__main__':main()
