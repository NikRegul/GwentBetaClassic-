"""Stage and install hash-verified 0.9.2 into the user's two Witcher installations."""
from pathlib import Path
import argparse, datetime, hashlib, json, shutil, subprocess, zipfile

ROOT=Path(__file__).resolve().parents[2]
VERSION='0.9.2'
TARGETS={'1.32':Path(r'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt'),
         '5.0+':Path(r'F:\Steam\steamapps\common\The Witcher 3')}
MODS={'1.32':{'modBetaGwentClassic132','modBetaGwentMenuMusic'},
      '5.0+':{'modBetaGwent0924','modBetaGwentMenuMusic'}}

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def inside(p,root):
    resolved=p.resolve();assert resolved.is_relative_to(root.resolve()) and resolved!=root.resolve(),p
    # Reject junctions/symlinks anywhere between the named root and target.
    for part in [p,*p.parents]:
        if part==root:break
        assert not part.is_symlink() and not part.is_junction(),part
    return resolved

def tree(p):
    if not p.exists():return None
    return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file()}

def prepare(build):
    stage=build/'install-stage';stage.mkdir(exist_ok=True);plan={}
    release=json.loads((build/'release.json').read_text('utf8'));assert release['version']==VERSION
    for platform,game in TARGETS.items():
        archive=build/f'archives/GwentBetaClassic-{VERSION}-{platform}-AllLanguages.zip'
        record=next(r for r in release['archives'] if Path(r['path']).name==archive.name)
        assert sha(archive)==record['sha256'];folder=stage/platform
        assert not folder.exists(),'Staging already exists; inspect it rather than overwriting'
        folder.mkdir();expected={}
        with zipfile.ZipFile(archive) as z:
            names=z.namelist();assert len(names)==len(set(n.lower() for n in names))
            manifest=json.loads(z.read(f'manifest-{VERSION}.json'));assert manifest['version']==VERSION
            assert {f['path'] for f in manifest['files']}==set(names)-{f'manifest-{VERSION}.json'}
            for f in manifest['files']:
                n=f['path'];parts=Path(n).parts
                assert not Path(n).is_absolute() and '..' not in parts and '\\' not in n
                if not n.startswith(('Mods/','DLC/','BetaGwentDocs/')):continue
                if parts[0]=='Mods':assert parts[1] in MODS[platform]
                if parts[0]=='DLC':assert parts[1] in {'dlcBetaGwentClassic132Assets','dlcBetaGwentClassic132Items'}
                dest=inside(folder/n,folder);dest.parent.mkdir(parents=True,exist_ok=True)
                raw=z.read(n);assert len(raw)==f['bytes'] and hashlib.sha256(raw).hexdigest()==f['sha256']
                dest.write_bytes(raw);expected[n]=f['sha256']
        assert {p.name for p in (folder/'Mods').iterdir()}==MODS[platform]
        plan[platform]=dict(game=str(game),source=str(folder),expected=expected,archiveSha256=record['sha256'])
    (stage/'plan.json').write_text(json.dumps(plan,indent=2),'utf8')
    print('Staged and verified both packages:',stage,flush=True)

def apply(build):
    stage=build/'install-stage';plan=json.loads((stage/'plan.json').read_text('utf8'))
    assert set(plan)==set(TARGETS)
    tasks=subprocess.run(['tasklist','/FI','IMAGENAME eq witcher3.exe','/FO','CSV','/NH'],capture_output=True,text=True)
    assert tasks.returncode==0 and '"witcher3.exe"' not in tasks.stdout.lower(),'Close The Witcher 3 before installation; no process was stopped'
    backup=ROOT/'tmp'/('install092-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    backup.mkdir(parents=True);operations=[];report=dict(version=VERSION,backup=str(backup),games={},gameplayVerified=False)
    # Both backups and all staged hashes are verified before either game changes.
    for platform,record in plan.items():
        game=TARGETS[platform].resolve();assert game==Path(record['game']).resolve()
        assert any((game/f'bin/{variant}/witcher3.exe').is_file() for variant in ['x64','x64_dx12'])
        source=Path(record['source']);inside(source,stage)
        assert tree(source)==record['expected'],'Staging differs from verified archive'
        for top in ['Mods','DLC']:
            if not (source/top).exists():continue
            for directory in (source/top).iterdir():
                assert directory.is_dir()
                if top=='Mods':assert directory.name in MODS[platform]
                else:assert directory.name in {'dlcBetaGwentClassic132Assets','dlcBetaGwentClassic132Items'}
                dest=inside(game/top/directory.name,game);saved=inside(backup/platform/top/directory.name,backup)
                if dest.exists():
                    saved.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(dest,saved);assert tree(dest)==tree(saved)
                operations.append((directory,dest,saved,game))
        dest=inside(game/'BetaGwentDocs',game);saved=inside(backup/platform/'BetaGwentDocs',backup)
        if dest.exists():
            saved.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(dest,saved);assert tree(dest)==tree(saved)
        operations.append((source/'BetaGwentDocs',dest,saved,game))
    (backup/'plan.json').write_text(json.dumps(plan,indent=2),'utf8')
    changed=[]
    try:
        for source,dest,saved,game in operations:
            inside(dest,game);changed.append((dest,saved,game))
            if dest.exists():shutil.rmtree(dest)
            dest.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(source,dest)
            assert tree(dest)==tree(source),'Installation differs: '+str(dest)
        for platform,record in plan.items():
            game=TARGETS[platform]
            for name,digest in record['expected'].items():assert sha(game/name)==digest,name
            report['games'][platform]=dict(path=str(game),verifiedFiles=len(record['expected']),version=VERSION)
            print('Installed and SHA-256 verified:',platform,game,flush=True)
    except Exception:
        for dest,saved,game in reversed(changed):
            inside(dest,game)
            if dest.exists():shutil.rmtree(dest)
            if saved.exists():shutil.copytree(saved,dest)
        (backup/'rollback.json').write_text(json.dumps(dict(restored=True),indent=2),'utf8')
        raise
    for f in [stage/'installed.json',backup/'installed.json']:f.write_text(json.dumps(report,indent=2),'utf8')
    print('Backup:',backup,flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
    build=a.build.resolve();assert build.is_relative_to(ROOT/'BetaGwent/build')
    apply(build) if a.apply else prepare(build)

if __name__=='__main__':main()
