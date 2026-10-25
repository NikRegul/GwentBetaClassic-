"""Build both 0.9.2 packages, or repackage a fully validated identical build."""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import ASSETS, UI, AUDIO, BASE_ARCHIVES, CLASSIC_RUNTIME
VERSION='0.9.2'
LATEST=ROOT/'BetaGwent/build/release092-latest.json'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def run(args):
    print('RUN',subprocess.list2cmdline([str(x) for x in args]),flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)

def limit_cpus():
    import psutil
    process=psutil.Process();available=process.cpu_affinity()
    chosen=[i for i in [0,2,4,6] if i in available]
    if not chosen:chosen=available[:4]
    process.cpu_affinity(chosen)
    print('Shared logical CPU set for this build and all children:',chosen,flush=True)

def preflight():
    required=[ROOT/'tools/features091/build091.py',ROOT/'tools/features091/prepare091.py',
              ASSETS/'ui-patch/manifest.json',ASSETS/'menu-music-caches/manifest.json',
              ASSETS/'menu-music/music.json',AUDIO/'manifest.json',UI/'classic/ui',UI/'nextgen/ui']
    required += [ROOT/f'docs/releases/{VERSION}_{kind}_{lang}.md'
                 for kind in ['CHANGELOG','DESCRIPTION','POST'] for lang in ['RU','EN']]
    required += [BASE_ARCHIVES/f'GwentBetaClassic-0.9.0-{p}-AllLanguages.zip' for p in ['1.32','5.0+']]
    from build_inputs import BASE_SCRIPTS
    required += [BASE_SCRIPTS/'scripts', BASE_SCRIPTS/'classic-audit/audit.json', CLASSIC_RUNTIME/'bin/x64/witcher3.exe']
    missing=[str(p) for p in required if not p.exists()]
    from build_inputs import AUDIO_MANIFEST_SHA256
    if (AUDIO/'manifest.json').exists() and sha(AUDIO/'manifest.json')!=AUDIO_MANIFEST_SHA256:raise RuntimeError('Classic audio inputs differ from the verified 0.9.2 set: '+str(AUDIO))
    if missing:raise RuntimeError('Missing build prerequisites:\n'+'\n'.join(missing))
    for executable in ['node','python']:
        if not shutil.which(executable):raise RuntimeError('Missing executable: '+executable)
    print('Prerequisites found. Full mode also requires the configured native compilers.',flush=True)

def rebase_assets(out):
    p=out/'ui-patch/manifest.json'
    if p.exists():
        d=json.loads(p.read_text('utf8'))
        for platform in d['platforms'].values():
            for record in platform['files'].values():
                old=Path(record['path']);rel=old.parts[old.parts.index('ui-patch')+1:]
                new=out/'ui-patch'/Path(*rel);assert sha(new)==record['sha256'];record['path']=str(new)
        p.write_text(json.dumps(d,indent=2),'utf8')
    p=out/'menu-music-caches/manifest.json';d=json.loads(p.read_text('utf8'))
    for record in d['platforms'].values():
        for key in ['cache','bank']:
            old=Path(record[key]);rel=old.parts[old.parts.index('menu-music-caches')+1:]
            new=out/'menu-music-caches'/Path(*rel);assert sha(new)==record[key+'Sha256'];record[key]=str(new)
    p.write_text(json.dumps(d,indent=2),'utf8')

def copy_assets(out, include_ui=True):
    for name in (['ui-patch'] if include_ui else [])+['menu-music-caches']:shutil.copytree(ASSETS/name,out/name)
    (out/'menu-music').mkdir();shutil.copy2(ASSETS/'menu-music/music.json',out/'menu-music/music.json')
    rebase_assets(out)

def select_ui_source(out, explicit=None):
    names=['BetaGwentBoard.as','BetaGwentController.as','BetaGwentCardText.as','BetaGwentRelated091.as','BetaGwentBanners090.as','BetaGwentReleaseText093.as']
    canonical={n:sha(ROOT/'BetaGwent/ui/src'/n) for n in names}
    source=explicit.resolve() if explicit else UI
    proof_path=source/'gamepad-source.json'
    proof=json.loads(proof_path.read_text('utf8')) if proof_path.exists() else {}
    if explicit:
        assert all(proof.get(n)==v for n,v in canonical.items()),'Prepared UI differs from current canonical sources'
    elif any(proof.get(n)!=v for n,v in canonical.items()):
        source=out/'ui-sources'
    return source,dict(source=str(source),canonical=canonical,reuseAcceptedPatch=source==UI)

def validated_copy(source,out):
    sys.path.insert(0,str(ROOT/'tools/ai'))
    from comparison_inputs import validate_snapshot
    from snapshot import inputs,fingerprint
    from validate091 import NAMES
    source=source.resolve();assert source.is_relative_to(ROOT/'BetaGwent/build')
    assert not (source/'cancelled.json').exists(),'Cancelled build cannot be reused'
    manifest=validate_snapshot(source/'rules')
    assert manifest['fingerprint']==fingerprint(inputs()),'Current game/host inputs differ: use a fresh full build'
    release=json.loads((source/'release.json').read_text('utf8'))
    assert len(release['archives'])==2
    for record in release['archives']:assert sha(Path(record['path']))==record['sha256']
    regressions=json.loads((source/'regressions/summary.json').read_text('utf8'))
    assert {r['name'] for r in regressions}==set(NAMES) and all(r['exitCode']==0 for r in regressions)
    for check in ['regressions','tactics-all','rows-all','varied']:
        proof=json.loads((source/f'checkpoints/{check}.json').read_text('utf8'))
        assert proof['fingerprint']==manifest['fingerprint']
        for name,digest in proof['tools'].items():assert sha(ROOT/name)==digest,'Test tool changed: '+name
    tactics=json.loads((source/'tactics-all/report.json').read_text('utf8'));assert tactics['failed']==0 and len(tactics['results'])==1426
    rows=json.loads((source/'rows-all/report.json').read_text('utf8'));assert len(rows['results'])==414 and all(r['pass'] for r in rows['results'])
    varied=json.loads((source/'varied/summary.json').read_text('utf8'));assert varied['cases']==5632 and varied['failed']==0
    freeze=json.loads((source/'source-freeze.json').read_text('utf8'))
    for name,digest in freeze['scripts'].items():assert sha(source/'scripts'/name)==digest
    out.mkdir(parents=True)
    for name in ['scripts','classic-prepared-final','rules','compile-nextgen-final','ui-patch','menu-music',
                 'menu-music-caches','regressions','tactics-all','rows-all','varied','checkpoints','logs']:
        shutil.copytree(source/name,out/name)
    for name in ['source-freeze.json','ai-validation-equivalence.json','ai-quality-gate.json','AI_VALIDATION_RU.md']:
        if (source/name).exists():shutil.copy2(source/name,out/name)
    classic=source/'classic-compile.json'
    if not classic.exists():classic=CLASSIC_RUNTIME/'runs'/source.name/'result.json'
    shutil.copy2(classic,out/'classic-compile.json')
    rebase_assets(out)
    (out/'validation-reuse.json').write_text(json.dumps(dict(source=str(source),sourceVersion=release['version'],
        fingerprint=manifest['fingerprint'],identicalCurrentInputs=True,regressionGroups=len(regressions),
        explanation='Only release label and documentation change; immutable scripts, native outputs and test evidence are copied and hash-checked.'),indent=2),'utf8')
    # package() verifies source freeze, both native results, assets, every ZIP
    # entry and the new archive manifests. It does not claim new game testing.
    spec=importlib.util.spec_from_file_location('package091',ROOT/'tools/features091/build091.py')
    module=importlib.util.module_from_spec(spec);sys.path.insert(0,str(ROOT/'tools/features091'));spec.loader.exec_module(module)
    module.VERSION=VERSION;reports=module.package(out,AUDIO)
    print(json.dumps(dict(version=VERSION,archives=reports),indent=2),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path);p.add_argument('--resume',action='store_true')
    p.add_argument('--reuse-validated',type=Path,help='Repackage identical fully tested inputs; fails if code or test tools differ')
    p.add_argument('--ui-source',type=Path,help='Prepared UI matching current canonical sources; rebuild its menu patch')
    p.add_argument('--check-only',action='store_true');p.add_argument('--install',action='store_true',help='Install into both configured games with backups')
    a=p.parse_args();limit_cpus();preflight()
    if a.check_only:print('Preflight passed; no build or installation performed.');return
    if a.resume and a.reuse_validated:p.error('Use --resume or --reuse-validated, not both')
    if a.out:out=a.out.resolve()
    elif a.resume:out=Path(json.loads(LATEST.read_text('utf8'))['path']).resolve()
    else:out=ROOT/'BetaGwent/build'/('release'+VERSION.replace('.','')+'-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
    assert out.is_relative_to(ROOT/'BetaGwent/build') and out!=ROOT/'BetaGwent/build'
    if not a.resume:assert not out.exists(),'Use a new output directory'
    assert not (out/'cancelled.json').exists()
    LATEST.write_text(json.dumps(dict(path=str(out),version=VERSION),indent=2),'utf8')
    print('Output:',out,flush=True)
    if a.reuse_validated:validated_copy(a.reuse_validated,out)
    else:
        ui_source,selection=select_ui_source(out,a.ui_source)
        command=[sys.executable,'-X','utf8','tools/features091/build091.py','--out',out,'--version',VERSION]
        if not a.resume:
            run(command+['--prepare-only']);copy_assets(out,include_ui=selection['reuseAcceptedPatch'])
            (out/'ui-selection.json').write_text(json.dumps(selection,indent=2),'utf8')
        elif (out/'ui-selection.json').exists():
            assert json.loads((out/'ui-selection.json').read_text('utf8'))==selection,'UI inputs changed: use a fresh build'
        run(command+['--resume','--ui-source',ui_source,'--classic-audio',AUDIO])
    nexus=out/'nexus';shutil.copytree(ROOT/f'docs/releases/{VERSION}/nexus',nexus,dirs_exist_ok=True)
    if a.install:
        for flag in [[],['--apply']]:run([sys.executable,'-X','utf8','tools/features092/install092.py','--build',out]+flag)
    print('COMPLETE:',out,flush=True)

if __name__=='__main__':main()
