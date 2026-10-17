"""Build/verify five Classic 1.32 ZIPs from one completed Next-Gen voice batch."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

from formats import ROOT, require, sha
sys.path.insert(0,str(ROOT/'tools'))
from build_release138 import presentation_lock

VOICES=('ru','en','de','it','pt-br')
DEFAULT_GAME=Path(r'D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt')

def read(path):return json.loads(Path(path).read_text('utf-8-sig'))

def generator_hashes():
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted((ROOT/'tools/classic132').glob('*')) if p.suffix in ('.py','.inc')}

def archive_path(version,language):
    return ROOT/'BetaGwent/release'/f'GwentBetaClassic-{version}-1.32-{language.upper()}.zip'

def resolve_stage(version,stage):
    source=ROOT/'BetaGwent/release'/f'GwentBetaClassic-{version}-RU.zip'
    if not source.exists():return stage or None
    with zipfile.ZipFile(source) as z:manifest=json.loads(z.read('manifest.json'))
    require(manifest['version']==version and manifest['language']=='ru','Next-Gen source version/language mismatch')
    require(not stage or stage==manifest['stage'],'Requested stage differs from the Next-Gen RU archive')
    return manifest['stage']

def verify_zip(path,version,language,stage,budget=63,generators=None,source_manifest=None):
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json'))
        require((m['version'],m['sourceVersion'],m['sourceStage'],m['gameVersion'],m['voiceLanguage'])==(version,version,stage,'1.32',language),'Classic archive identity mismatch')
        require(m['nativeCompilationPassed'] and len(m['textLanguages'])==13 and m['guiLimitMiB']==budget,'Classic verification metadata mismatch')
        if generators is not None:require(m.get('generators')==generators,'Classic generators changed; choose a new release version')
        if source_manifest is not None:require(m.get('sourceManifestSha256')==source_manifest,'Classic source manifest changed')
        require(z.testzip() is None,'ZIP CRC failed')
        files={row['path']:row for row in m['files']}
        require(set(z.namelist())==set(files)|{'manifest.json'},'Unexpected or missing ZIP files')
        require(len(z.namelist())==len(set(z.namelist())),'Duplicate ZIP paths')
        for name,row in files.items():
            data=z.read(name)
            require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'ZIP payload mismatch: '+name)
    digest=sha(path);require(path.with_suffix('.zip.sha256').read_text('ascii').split()[0]==digest,'Archive SHA mismatch')
    return dict(path=str(path),bytes=path.stat().st_size,sha256=digest,voice=language,textLanguages=13,verified=True)

def run(*args):
    command=[sys.executable,'-X','utf8',*map(str,args)]
    if '--out' not in args:
        subprocess.run(command,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        return
    # A hidden child can lose its console output. Always retain its actual error.
    output=Path(args[args.index('--out')+1]);output.mkdir(parents=True,exist_ok=True)
    log=output/'build.log'
    print('Classic build log: '+str(log),flush=True)
    with log.open('ab') as stream:
        result=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        print(log.read_text('utf8',errors='replace')[-12000:],flush=True)
        raise subprocess.CalledProcessError(result.returncode,command)


def recovery_output(base,inputs,explicit=False):
    """Keep a failed batch intact when generators change; reuse verified menus."""
    stamp=base/'batch-inputs.json'
    if not stamp.exists() or read(stamp)==inputs:return base,None
    require(not explicit,'Batch inputs changed; select a fresh output directory')
    previous=read(stamp)
    # Never reuse art from another source manifest, game or GUI budget.
    comparable=lambda x:{k:v for k,v in x.items() if k!='generators'}
    require(comparable(previous)==comparable(inputs),'Batch source inputs changed; select a fresh output directory')
    digest=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()[:12]
    recovered=base.with_name(base.name+'-recovery-'+digest)
    menus=base/'ru/menus'
    menu_generators=('build_menus.py','formats.py','classic_text_bridge.as.inc')
    unchanged=all(previous.get('generators',{}).get('tools/classic132/'+name)==inputs['generators'].get('tools/classic132/'+name) for name in menu_generators)
    if not unchanged or not (menus/'menus.json').is_file():menus=None
    return recovered,menus

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',default='0.8.0');p.add_argument('--source-stage',type=int,default=0)
    p.add_argument('--game',type=Path,default=DEFAULT_GAME);p.add_argument('--out',type=Path)
    p.add_argument('--gui-limit-mib',type=int,default=63)
    p.add_argument('--check-only',action='store_true');p.add_argument('--verify',action='store_true')
    a=p.parse_args(argv)
    require(re.fullmatch(r'\d+\.\d+\.\d+[a-z]?(?:-[A-Za-z0-9-]+)?',a.version),'Invalid version')
    require(1<=a.gui_limit_mib<=65,'GUI budget must be 1..65 MiB')
    stage=resolve_stage(a.version,a.source_stage)
    base=(a.out or ROOT/'BetaGwent/build'/f'classic132-{a.version}-stage{stage or "pending"}').resolve()
    require(base.is_relative_to(ROOT/'BetaGwent/build') and base!=ROOT/'BetaGwent/build','Output must be a build subdirectory')
    sources={v:bool(stage and (ROOT/f'BetaGwent/build/release{stage}/{v}/package/manifest.json').is_file()) for v in VOICES}
    plan=dict(version=a.version,sourceStage=stage,gameVersion='1.32',voices=list(VOICES),textLanguages=13,guiLimitMiB=a.gui_limit_mib,
              sourcePackagesReady=sources,output=str(base),archives=[str(archive_path(a.version,v)) for v in VOICES],
              installsGame=False,buildStarted=False)
    print(json.dumps(plan,ensure_ascii=False,indent=2),flush=True)
    if a.check_only:return plan
    require(stage is not None,'Build the Next-Gen 0.8.0 voice batch first, or select its source stage')
    if a.verify:
        outputs=[verify_zip(archive_path(a.version,v),a.version,v,stage,a.gui_limit_mib) for v in VOICES]
        print('Verified all five Classic voice packages.',flush=True);return outputs
    require(all(sources.values()),'Build all five Next-Gen source packages first with Build-All-0.8.0.cmd')
    # Reuse the maintained verifier, including the RU stage and source hashes.
    # --verify cannot build a missing package.
    run('tools/build_voice_packages168.py','--version',a.version,'--stage',stage,'--gui-limit-mib',a.gui_limit_mib,'--verify')
    frozen={v:sha(ROOT/f'BetaGwent/build/release{stage}/{v}/package/manifest.json') for v in VOICES}
    base.mkdir(parents=True,exist_ok=True)
    generators=generator_hashes()
    inputs=dict(version=a.version,sourceStage=stage,game=str(a.game.resolve()),guiLimitMiB=a.gui_limit_mib,sourceManifests=frozen,generators=generators)
    base,reuse_menus=recovery_output(base,inputs,explicit=a.out is not None)
    base.mkdir(parents=True,exist_ok=True)
    if reuse_menus:print('Fresh recovery output: '+str(base)+'; reusing hash-verified menus from '+str(reuse_menus),flush=True)
    shared_menus=reuse_menus or base/'ru/menus'
    stamp=base/'batch-inputs.json'
    if stamp.exists():require(read(stamp)==inputs,'Batch inputs changed; select a fresh output directory')
    else:stamp.write_text(json.dumps(inputs,indent=2)+'\n','utf8')
    outputs=[]
    with presentation_lock():
        for voice in VOICES:
            archive=archive_path(a.version,voice)
            if archive.exists():
                outputs.append(verify_zip(archive,a.version,voice,stage,a.gui_limit_mib,generators,frozen[voice]));continue
            args=['tools/classic132/build.py','--version',a.version,'--source-stage',stage,'--language',voice,
                  '--release','--game',a.game,'--out',base/voice,'--gui-limit-mib',a.gui_limit_mib]
            if voice=='ru' and reuse_menus:args+=['--menus',reuse_menus]
            if voice!='ru':
                require((shared_menus/'menus.json').is_file() and (base/'ru/resources-classic/resources.json').is_file(),
                        'Shared RU outputs are missing; reuse the original Classic output directory')
                args+=['--menus',shared_menus,'--resources',base/'ru/resources-classic']
            run(*args)
            outputs.append(verify_zip(archive,a.version,voice,stage,a.gui_limit_mib,generators,frozen[voice]))
        report=dict(version=a.version,sourceStage=stage,gameVersion='1.32',passed=True,packages=outputs,nativeGameTested=False,installedGameModified=False)
        (base/'batch-result.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
        (ROOT/f'docs/evidence/classic132-voice-batch{stage}.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('Verified five Classic 1.32 voice packages; 13 text languages in each.',flush=True)
    return outputs

if __name__=='__main__':main()
