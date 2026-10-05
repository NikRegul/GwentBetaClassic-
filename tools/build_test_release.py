"""Stage a frozen Russian test release, then cook/package it with installed REDkit."""
from pathlib import Path
import argparse,hashlib,json,shutil,sqlite3,subprocess,sys,zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'BetaGwent/build/release87'
PROJECT=BASE/'project/BetaGwent0924'
WORK=PROJECT/'workspace'
COOKED=BASE/'cooked'
PACKAGE=BASE/'package'
CONTENT=PACKAGE/'Mods/modBetaGwent0924/content'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('step',choices=['prepare','cook','strings','audio','dependencies','pack','metadata','archive'])
args=parser.parse_args()

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def job(name,arguments):
    command=[sys.executable,str(ROOT/'tools/recon/run_wcc_job.py'),'--out',str(BASE/'jobs'/name),'--timeout','300','--',*arguments,
             '-uncookDir',str(ROOT/'depot')+'\\','-workspaceDir',str(PROJECT)+'\\']
    subprocess.run(command,cwd=ROOT,check=True)
def verify_inputs():
    state=json.loads((BASE/'frozen-inputs.json').read_text('utf8'))
    for item in state['files']:
        if sha(PROJECT/item['path'])!=item['sha256']:raise RuntimeError('Frozen source changed: '+item['path'])
    return state

if args.step=='prepare':
    if (BASE/'frozen-inputs.json').exists():raise SystemExit('Inputs already frozen')
    manifest=json.loads((BASE/'input-manifest.json').read_text('utf8'))
    source=ROOT/'GwentB/myproject1'
    for item in manifest['files']:
        src=source/item['path'];dst=PROJECT/item['path']
        assert sha(src)==item['sha256'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    metadata=json.loads((PROJECT/'myproject1.w3edit').read_text('utf8'))
    metadata.update(name='BetaGwent0924',modName='BetaGwent0924',version='0.1.0-alpha',gameVersion='5.0',
        description='Russian test alpha: Beta Gwent 0.9.24 replacement, five factions, cards, decks, NPC rewards and controller support.',
        author='BetaGwent Project',thumbnail='thumbnail.png',useLooseScripts=False,excludedDlc=[],succesfullyCooked=False)
    (PROJECT/'myproject1.w3edit').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n','utf8')
    shutil.copyfile(ROOT/'BetaGwent/ui/assets/board_classic.png',PROJECT/'thumbnail.png')
    seeds=BASE/'cook-roots'
    for p in WORK.rglob('*'):
        if p.suffix in ['.menu','.guiconfig','.redswf']:
            dst=seeds/p.relative_to(WORK);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    files=[dict(path=p.relative_to(PROJECT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(PROJECT.rglob('*')) if p.is_file()]
    (BASE/'frozen-inputs.json').write_text(json.dumps(dict(stage=87,language='ru',files=files,originalProjectModified=False),indent=2)+'\n','utf8')
    CONTENT.mkdir(parents=True,exist_ok=True)
    print('Frozen test project:',PROJECT,flush=True)
else:
    verify_inputs()
    if args.step=='cook':
        job('cook',['cook','-platform=pc','-mod='+str(BASE/'cook-roots')+'\\','-outdir='+str(COOKED)+'\\'])
        for p in WORK.rglob('*'):
            if p.suffix in ['.xml','.csv']:
                dst=COOKED/p.relative_to(WORK);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    elif args.step=='strings':
        job('strings-valid',['cookstrings',str(CONTENT)+'\\',str(ROOT/'depot')+'\\',
                       'LATEST_STRINGS_WITH_INFO_NEW','-languages=ru,en','-platforms=pc'])
    elif args.step=='audio':
        # Use the explicit 5.0 remaster path with a flat bank directory and a
        # split output, so the bank inventory and cooked bytes can be verified.
        bankdir=BASE/'audio-banks/Windows';bankdir.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(WORK/'soundbanks/pc/BetaGwent79.bnk',bankdir/'BetaGwent79.bnk')
        shutil.copyfile(ROOT/'BetaGwent/audio/wwise/GeneratedSoundBanks/Windows/BetaGwent79.txt',bankdir/'BetaGwent79.txt')
        seed=WORK/'soundbanks/soundsplitseed.csv'
        seed.write_text('Bank;Chunk\nbetagwent79.bnk;content0\n','utf8')
        destination=BASE/'audio-cooked'
        job('audio-final',['cooksounds','-outdir='+str(destination)+'\\',
                     '-soundbanksdir='+str(bankdir)+'\\','-platform=windows','-r4remastersounds',
                     '-outsplitfile='+str(BASE/'audio-final-split.list')])
        cache=destination/'CookedPC/soundspc.cache'
        raw=cache.read_bytes();bank=(bankdir/'BetaGwent79.bnk').read_bytes()
        assert raw[:4]==b'CS3W' and raw[64:64+len(bank)]==bank
        assert b'betagwent79.bnk\0' in raw and len(raw)==len(bank)+104
        CONTENT.mkdir(parents=True,exist_ok=True);shutil.copyfile(cache,CONTENT/'soundspc.cache')
        proof=dict(stage=87,cacheBytes=len(raw),cacheSha256=sha(cache),bankBytes=len(bank),
            bankSha256=sha(bankdir/'BetaGwent79.bnk'),bankOffset=64,bankBytesVerified=True,
            originalInitBankIncluded=False,mediaCount=1418,eventCount=1420,runtimeVerified=False)
        (ROOT/'docs/evidence/stage87-sound-cache.json').write_text(json.dumps(proof,indent=2)+'\n','utf8')
    elif args.step=='dependencies':
        job('dependencies',['dependencies','-db='+str(COOKED/'cook.db'),'-out='+str(CONTENT/'dep.cache')])
    elif args.step=='pack':
        CONTENT.mkdir(parents=True,exist_ok=True)
        clean=BASE/'bundle-input';clean.mkdir(exist_ok=True)
        for p in COOKED.rglob('*'):
            if not p.is_file() or p.name=='cook.db':continue
            dst=clean/p.relative_to(COOKED);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
        job('pack',['pack','-dir='+str(clean)+'\\','-outdir='+str(CONTENT)+'\\','-compression=LZ4HC'])
    elif args.step=='metadata':
        job('metadata',['metadatastore','-path='+str(CONTENT)+'\\','-out='+str(CONTENT/'metadata.store')])
    elif args.step=='archive':
        # Early sound probes can leave a second nested copy of the same bank.
        # Ship only the verified final cache at the content root.
        legacy=CONTENT/'CookedPC/soundspc.cache'
        if legacy.exists():
            assert legacy.resolve().is_relative_to(BASE.resolve())
            raw=legacy.read_bytes();bank=(WORK/'soundbanks/pc/BetaGwent79.bnk').read_bytes()
            assert raw[:4]==b'CS3W' and (len(raw)==64 or len(raw)==len(bank)+104 and raw[64:64+len(bank)]==bank)
            legacy.unlink()
            if not any(legacy.parent.iterdir()):legacy.parent.rmdir()
        compile_report=json.loads((ROOT/'BetaGwent/build/board-compile86a/result.json').read_text('utf8'))
        assert compile_report['exitCode']==0 and not compile_report['timedOut']
        blob=ROOT/'BetaGwent/build/board-compile86a/compiled/blob.rsblob'
        assert sha(blob).upper()==next(a['sha256'] for a in compile_report['artifacts'] if a['path'].endswith('blob.rsblob')).upper()
        shutil.copyfile(blob,CONTENT/'precompiled.rsblob')
        expected=[CONTENT/'dep.cache',CONTENT/'metadata.store',CONTENT/'ru.w3strings']
        for p in expected:
            if not p.is_file() or p.stat().st_size==0:raise RuntimeError('Missing required cooked output: '+str(p))
        if not list(CONTENT.glob('*.bundle')) and not list((CONTENT/'bundles').glob('*.bundle')):raise RuntimeError('No resource bundle')
        if not list(CONTENT.rglob('*sound*.cache')):raise RuntimeError('No cooked sound cache')
        assert list(CONTENT.rglob('*sound*.cache'))==[CONTENT/'soundspc.cache']
        sound_proof=json.loads((ROOT/'docs/evidence/stage87-sound-cache.json').read_text('utf8'))
        assert sha(CONTENT/'soundspc.cache')==sound_proof['cacheSha256']
        for name in ['README_RU.md','TEST_CHECKLIST_RU.md']:
            shutil.copyfile(ROOT/'BetaGwent/release'/name,PACKAGE/name)
        metadata=json.loads((PROJECT/'myproject1.w3edit').read_text('utf8'))
        info={key:metadata[key] for key in ['name','modName','version','gameVersion','description','author','dependencies']}
        (CONTENT.parent/'info.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n','utf8')
        files=[dict(path=p.relative_to(PACKAGE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p!=PACKAGE/'manifest.json']
        report=dict(version='0.1.0-alpha',stage=87,language='ru',files=files,runtimeVerified=False,installedGameModified=False,licenseIncluded=False,
            notes='Russian test alpha. English localization and archetype AI follow. Compiled annotated script blob; no loose scripts, original game, original audio bank, Wwise project or license.')
        (PACKAGE/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
        destination=ROOT/'BetaGwent/release/BetaGwent0924-0.1.0-alpha-RU.zip'
        with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(PACKAGE.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(PACKAGE).as_posix())
        with zipfile.ZipFile(destination) as z:
            assert z.testzip() is None
            for item in files:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
            assert not any(n.endswith(('.ws','.wproj','.wwu','.db')) for n in z.namelist())
        report.update(archive=str(destination),archiveBytes=destination.stat().st_size,archiveSha256=sha(destination),archiveVerified=True)
        destination.with_suffix('.zip.sha256').write_text(report['archiveSha256']+'  '+destination.name+'\n','ascii')
        (ROOT/'docs/evidence/stage87-test-release.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
        print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False),flush=True)
