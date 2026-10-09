"""Stage and package RU/EN on the same code revision, using REDkit CLI only."""
from pathlib import Path
import argparse,hashlib,json,shutil,sqlite3,subprocess,sys,zipfile,re
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('step',choices=['prepare','cook','strings','audio','dependencies','pack','metadata','archive'])
parser.add_argument('--language',choices=['ru','en'],required=True)
parser.add_argument('--stage',type=int,default=89)
parser.add_argument('--version',default='0.2.0')
parser.add_argument('--compiled',type=Path,help='Verified script compilation for this package')
a=parser.parse_args();LANG=a.language;VERSION=a.version;STAGE=a.stage
if STAGE!=89 and VERSION=='0.2.0':raise SystemExit('New stages must use a new version; first-release archives are immutable')
if not re.fullmatch(r'[0-9A-Za-z.\-]+',VERSION):raise SystemExit('Invalid version')
BASE=ROOT/('BetaGwent/build/release'+str(STAGE)+'/'+LANG)
PROJECT=BASE/'project/BetaGwent0924';WORK=PROJECT/'workspace'
COOKED=BASE/'cooked';PACKAGE=BASE/'package';CONTENT=PACKAGE/'Mods/modBetaGwent0924/content'
# Stage 109 adds the keg-opening menu.
MENUS=('betagwent_board.redswf','betagwent_npc00.redswf','betagwent_decks.redswf')+(('betagwent_kegop.redswf',) if STAGE>=109 else ())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def job(name,args,expect=(),workspace=None):
    # Stage 105: completion by output + stall restart (see run_wcc_job.py).
    extra=[x for p in expect for x in ('--expect',str(p))]
    job_dir=BASE/'jobs'/name;retry=1
    while job_dir.exists():
        job_dir=BASE/'jobs'/(name+'-retry'+str(retry));retry+=1
    subprocess.run([sys.executable,str(ROOT/'tools/recon/run_wcc_job.py'),'--out',str(job_dir),'--timeout','1800',*extra,'--',*args,'-uncookDir',str(ROOT/'depot')+'\\','-workspaceDir',str(workspace or PROJECT)+'\\'],cwd=ROOT,check=True)
    log=(job_dir/'stdout.txt').read_text('utf8',errors='replace')
    # Wcc can return zero after failed writer assertions. Exit status alone
    # must never authorize a corrupt resource to enter the shipping bundle.
    fatal=('Internal cooking buffer is to small','!!! FATAL WRITING ERROR !!!','[Error][Assertion]','Cooking error for resource')
    if any(marker in log for marker in fatal):raise RuntimeError('Wcc resource failure in '+name+'; inspect '+str(job_dir/'stdout.txt'))
def checked():
    report=json.loads((BASE/'frozen.json').read_text('utf8'))
    for f in report['files']:
        if sha(PROJECT/f['path'])!=f['sha256']:raise RuntimeError('Frozen source changed: '+f['path'])
if a.step=='prepare':
    if (BASE/'frozen.json').exists():raise SystemExit('Already prepared: '+LANG)
    src=ROOT/'BetaGwent/build/release87/project/BetaGwent0924'
    shutil.copytree(src,PROJECT,dirs_exist_ok=True)
    current=ROOT/'GwentB/myproject1'
    for rel in ('workspace/betagwent','workspace/gameplay/gui_new','workspace/gameplay/items','workspace/gameplay/globals'):
        if (current/rel).exists():shutil.copytree(current/rel,PROJECT/rel,dirs_exist_ok=True)
    shutil.copyfile(current/'LocalEditorStringDataBaseW3_UTF8_mod.db',PROJECT/'LocalEditorStringDataBaseW3_UTF8_mod.db')
    code=ROOT/'BetaGwent/build/board-patch/game/betagwent' if LANG=='ru' else ROOT/('BetaGwent/build/release89/en-source/scripts/game/betagwent' if STAGE==89 else 'BetaGwent/build/stage'+str(STAGE)+'/en/en-source/scripts/game/betagwent')
    shutil.copytree(code,WORK/'scripts/game/betagwent',dirs_exist_ok=True)
    if STAGE!=89:
        visuals=ROOT/f'BetaGwent/build/stage{STAGE}/{LANG}/resources'
        for name in MENUS:
            shutil.copyfile(visuals/name,WORK/'betagwent'/name)
    if STAGE==96:
        sys.path.insert(0,str(ROOT/'tools/ui'))
        from externalize_gui96 import externalize
        preparation={}
        for name in MENUS:
            preparation[name]=externalize(WORK/'betagwent'/name,WORK/'betagwent'/name,WORK)
        (BASE/'menu-input.json').write_text(json.dumps(preparation,indent=2)+'\n','utf8')
    elif STAGE>=95:
        sys.path.insert(0,str(ROOT/'tools/ui'))
        from prepare_cooked_menu95 import strip_authoring
        preparation={}
        for name in MENUS:
            preparation[name]=strip_authoring(WORK/'betagwent'/name)
            if preparation[name]['after']>=100*1024*1024:raise RuntimeError('Menu exceeds verified Wcc writer budget: '+name)
            if STAGE>=98 and preparation[name]['after']>=55*1024*1024:raise RuntimeError('Compact GUI exceeds 55 MiB loading target: '+name)
        (BASE/'menu-input.json').write_text(json.dumps(preparation,indent=2)+'\n','utf8')
    if LANG=='en':
        sys.path.insert(0,str(ROOT/'tools'));from localization89 import strings
        lookup=strings();con=sqlite3.connect(PROJECT/'LocalEditorStringDataBaseW3_UTF8_mod.db')
        for rowid,text in con.execute('select rowid,TEXT from STRINGS').fetchall():
            en=lookup.get(text)
            if en is None and text.startswith('Карта Beta Gwent 0.9.24: '):
                title=text.split(': ',1)[1].split('. Покупка',1)[0]
                cap=re.search(r'Лимит: (\d+)',text)[1]
                en='Beta Gwent 0.9.24 card: '+lookup[title]+'. Adds to your collection. Limit: '+cap+' '+('copies.' if cap!='1' else 'copy.')
            if en is None and 'боч' in text.lower():
                en='Beta Gwent card keg' if len(text)<60 else 'Open from inventory outside combat. Up to four bronze cards and one rare choice. Bronze cap: 3; silver, gold and leaders: 1. Price: 150 crowns.'
            if en is None:raise RuntimeError('Untranslated item: '+text)
            con.execute('update STRINGS set TEXT=? where rowid=?',(en,rowid))
        con.commit();con.close()
    bank=ROOT/('BetaGwent/audio/wwise'+('-en89' if LANG=='en' else '')+'/GeneratedSoundBanks/Windows/BetaGwent79.bnk')
    (WORK/'soundbanks/pc').mkdir(parents=True,exist_ok=True)  # base project rebuilt without this folder (stage 105)
    shutil.copyfile(bank,WORK/'soundbanks/pc/BetaGwent79.bnk')
    metadata=json.loads((PROJECT/'myproject1.w3edit').read_text('utf8'))
    metadata.update(version=VERSION,description='Gwent Beta Classic 0.9.24 — '+LANG.upper()+', 479 cards, five factions, collection, decks and controller support.',excludedDlc=[])
    (PROJECT/'myproject1.w3edit').write_text(json.dumps(metadata,indent=2)+'\n','utf8')
    for p in WORK.rglob('*'):
        if p.suffix in ('.menu','.guiconfig','.redswf','.redswfx'):
            target=BASE/'cook-roots'/p.relative_to(WORK);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    files=[dict(path=p.relative_to(PROJECT).as_posix(),sha256=sha(p)) for p in sorted(PROJECT.rglob('*')) if p.is_file()]
    (BASE/'frozen.json').write_text(json.dumps(dict(stage=STAGE,language=LANG,files=files),indent=2),'utf8')
    print('Frozen '+LANG+' project',flush=True)
else:
    checked();CONTENT.mkdir(parents=True,exist_ok=True)
    if a.step=='cook':
        job('cook',['cook','-platform=pc','-mod='+str(BASE/'cook-roots')+'\\','-outdir='+str(COOKED)+'\\'],[COOKED/'cook.db'])
        if STAGE==96:
            sys.path.insert(0,str(ROOT/'tools/ui'))
            from verify_external_gui96 import verify
            menus={name:verify(WORK/'betagwent'/name,COOKED/'betagwent'/name,WORK,COOKED)
                   for name in MENUS}
            (BASE/'cooked-menus-verified.json').write_text(json.dumps(menus,indent=2)+'\n','utf8')
        elif STAGE>=95:
            sys.path.insert(0,str(ROOT/'tools/ui'))
            from verify_cooked_menu95 import verify
            menus={name:verify(WORK/'betagwent'/name,COOKED/'betagwent'/name)
                   for name in MENUS}
            (BASE/'cooked-menus-verified.json').write_text(json.dumps(menus,indent=2)+'\n','utf8')
        for p in WORK.rglob('*'):
            if p.suffix in ('.xml','.csv'):
                target=COOKED/p.relative_to(WORK);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
    elif a.step=='strings':
        # Other game languages get English item names/descriptions. Never rename
        # an EN w3strings binary: native cooking writes each language's encoding.
        fallback=BASE/'string-fallback/BetaGwent0924';fallback.mkdir(parents=True,exist_ok=True)
        for file in PROJECT.glob('*.w3edit'):shutil.copyfile(file,fallback/file.name)
        shutil.copyfile(PROJECT/'LocalEditorStringDataBaseW3_UTF8_mod.db',fallback/'LocalEditorStringDataBaseW3_UTF8_mod.db')
        (fallback/'workspace').mkdir(exist_ok=True)
        sys.path.insert(0,str(ROOT/'tools'));from localization89 import strings
        lookup=strings()
        with sqlite3.connect(fallback/'LocalEditorStringDataBaseW3_UTF8_mod.db') as db:
            for rowid,text in db.execute('select rowid,TEXT from STRINGS').fetchall():
                english=text if LANG=='en' else lookup.get(text)
                if english is None and text.startswith('Карта Beta Gwent 0.9.24: '):
                    title=text.split(': ',1)[1].split('. Покупка',1)[0];cap=re.search(r'Лимит: (\d+)',text)[1]
                    english='Beta Gwent 0.9.24 card: '+lookup[title]+'. Adds to your collection. Limit: '+cap+' '+('copies.' if cap!='1' else 'copy.')
                if english is None:raise RuntimeError('Missing English vendor fallback: '+text)
                db.execute('update STRINGS set TEXT=? where rowid=?',(english,rowid))
            # Native cooking reads each language's rows; FALLBACK alone produces
            # empty files. Keep the template's IDs and explicitly populate them.
            db.execute("insert or ignore into LANGUAGES(ID,LANG,FALLBACK) values(18,'UA',2)")
            language_rows=db.execute("select ID,lower(LANG) from LANGUAGES where LANG!='DEBUG' order by ID").fetchall()
            english_rows=db.execute('select STRING_ID,VERSION,TEXT from STRINGS where LANG=2').fetchall()
            assert english_rows and len({row[0] for row in english_rows})==len(english_rows)
            versions=dict(db.execute('select STRING_ID,max(VERSION) from STRINGS group by STRING_ID').fetchall())
            for language_id,code in language_rows:
                if language_id==2:continue
                db.execute('delete from STRINGS where LANG=?',(language_id,))
                rows=[]
                for string_id,_,text in english_rows:
                    versions[string_id]+=1;rows.append((string_id,language_id,versions[string_id],text))
                db.executemany('insert into STRINGS(STRING_ID,LANG,VERSION,TEXT) values(?,?,?,?)',rows)
        languages=','.join(code for _,code in language_rows if code!='ru' or LANG=='en')
        if LANG=='ru':job('strings-ru',['cookstrings',str(CONTENT)+'\\',str(ROOT/'depot')+'\\','LATEST_STRINGS_WITH_INFO_NEW','-languages=ru','-platforms=pc'],expect=[CONTENT/'ru.w3strings'])
        job('strings-fallback',['cookstrings',str(CONTENT)+'\\',str(ROOT/'depot')+'\\','LATEST_STRINGS_WITH_INFO_NEW','-languages='+languages,'-platforms=pc'],expect=[CONTENT/(code+'.w3strings') for code in languages.split(',')],workspace=fallback)
        subprocess.run([sys.executable,str(ROOT/'tools/recon/verify_release_strings.py'),'--base',str(BASE),
                        '--stage',str(STAGE),'--package-language',LANG],cwd=ROOT,check=True)

    elif a.step=='audio':
        bankdir=BASE/'audio-banks/Windows';bankdir.mkdir(parents=True,exist_ok=True)
        source=ROOT/('BetaGwent/audio/wwise'+('-en89' if LANG=='en' else '')+'/GeneratedSoundBanks/Windows')
        for name in ('BetaGwent79.bnk','BetaGwent79.txt'):shutil.copyfile(source/name,bankdir/name)
        seed=WORK/'soundbanks/soundsplitseed.csv';seed.parent.mkdir(parents=True,exist_ok=True)
        seed.write_text('Bank;Chunk\nbetagwent79.bnk;content0\n','utf8')  # cooksounds needs the split seed (see build_test_release.py)
        cache=BASE/'audio-cooked/CookedPC/soundspc.cache';bank=(bankdir/'BetaGwent79.bnk').read_bytes()
        data=cache.read_bytes() if cache.exists() else b''
        reused=data[:4]==b'CS3W' and len(data)==len(bank)+104 and data[64:64+len(bank)]==bank
        if not reused:
            job('audio',['cooksounds','-outdir='+str(BASE/'audio-cooked')+'\\','-soundbanksdir='+str(bankdir)+'\\','-platform=windows','-r4remastersounds','-outsplitfile='+str(BASE/'audio-split.list')],
                [cache,BASE/'audio-split.list'])
            data=cache.read_bytes()
        assert data[:4]==b'CS3W' and data[64:64+len(bank)]==bank and len(data)==len(bank)+104
        (BASE/'audio-output-verified.json').write_text(json.dumps(dict(reusedVerifiedOutput=reused,
            cacheSha256=sha(cache),bankSha256=sha(bankdir/'BetaGwent79.bnk'),cacheBytes=len(data),
            bankBytes=len(bank),embeddedBankIdentical=True,runtimeVerified=False),indent=2)+'\n','utf8')
        shutil.copyfile(cache,CONTENT/'soundspc.cache')
    elif a.step=='dependencies':job('dependencies',['dependencies','-db='+str(COOKED/'cook.db'),'-out='+str(CONTENT/'dep.cache')],[CONTENT/'dep.cache'])
    elif a.step=='pack':
        clean=BASE/'bundle-input';clean.mkdir(exist_ok=True)
        for p in COOKED.rglob('*'):
            if p.is_file() and p.name!='cook.db':
                target=clean/p.relative_to(COOKED);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
        job('pack',['pack','-dir='+str(clean)+'\\','-outdir='+str(CONTENT)+'\\','-compression='+('None' if STAGE>=97 else 'LZ4HC')],[CONTENT/'blob0.bundle'])
        if STAGE>=96:
            sys.path.insert(0,str(ROOT/'tools/ui'))
            from verify_bundle96 import verify
            report=verify(CONTENT/'blob0.bundle',clean,require_uncompressed_gui=STAGE>=97,gui_limit_mib=55 if STAGE>=98 else 100)
            (BASE/'packed-resources-verified.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    elif a.step=='metadata':job('metadata',['metadatastore','-path='+str(CONTENT)+'\\','-out='+str(CONTENT/'metadata.store')],[CONTENT/'metadata.store'])
    elif a.step=='archive':
        compilation=a.compiled or ROOT/('BetaGwent/build/board-compile89a' if LANG=='ru' else 'BetaGwent/build/board-compile89enc')
        r=json.loads((compilation/'result.json').read_text('utf8'));log=(compilation/'stdout.txt').read_text('utf8',errors='replace')
        assert r['exitCode']==0 and not r['timedOut'] and 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
        for source in r['patchSourcesBefore']:
            assert sha(WORK/'scripts'/source['path'])==source['sha256'],'Compilation source mismatch: '+source['path']
        shutil.copyfile(compilation/'compiled/blob.rsblob',CONTENT/'precompiled.rsblob')
        for f in ('blob0.bundle','dep.cache','metadata.store','ru.w3strings','en.w3strings','soundspc.cache','precompiled.rsblob'):assert (CONTENT/f).stat().st_size>0
        info=json.loads((PROJECT/'myproject1.w3edit').read_text('utf8'));info['gameVersion']='5.01' if STAGE>=111 else info['gameVersion']
        (CONTENT.parent/'info.json').write_text(json.dumps({k:info[k] for k in ('name','modName','version','gameVersion','description','author','dependencies')},indent=2)+'\n','utf8')
        for name in ('README_'+LANG.upper()+'.md','CONTROLS_'+LANG.upper()+'.md','CHANGELOG_'+LANG.upper()+'.md'):shutil.copyfile(ROOT/'BetaGwent/release'/name,PACKAGE/name)
        for name in ('LICENSE','ATTRIBUTIONS.md'):
            shutil.copyfile(ROOT/'BetaGwent/build/public-source89/GwentBetaClassic'/name,PACKAGE/name)
        (PACKAGE/'SOURCE.txt').write_text('Source code (GPL-3.0-only): https://github.com/NikRegul/GwentBetaClassic-\n','ascii')
        files=[dict(path=p.relative_to(PACKAGE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p.name!='manifest.json']
        preview=ROOT/f'docs/PRESENTATION{STAGE}_{LANG.upper()}.md'
        if STAGE!=89 and preview.exists():shutil.copyfile(preview,PACKAGE/('PREVIEW.md' if 'preview' in VERSION else 'UPDATE.md'))
        files=[dict(path=p.relative_to(PACKAGE).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p.name!='manifest.json']
        report=dict(version=VERSION,stage=STAGE,language=LANG,mediaCount=1418,files=files,licenseIncluded=False,runtimeVerified=False,baseVersionUserAccepted=True)
        (PACKAGE/'manifest.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
        dest=ROOT/('BetaGwent/release/GwentBetaClassic-'+VERSION+'-'+LANG.upper()+'.zip')
        if dest.exists():raise SystemExit('Archive already exists; choose a new version instead of overwriting: '+str(dest))
        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(PACKAGE.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(PACKAGE).as_posix())
        with zipfile.ZipFile(dest) as z:
            assert z.testzip() is None
            for f in files:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
        report.update(archive=str(dest),archiveBytes=dest.stat().st_size,archiveSha256=sha(dest),archiveVerified=True)
        dest.with_suffix('.zip.sha256').write_text(report['archiveSha256']+'  '+dest.name+'\n','ascii')
        (ROOT/('docs/evidence/stage'+str(STAGE)+'-release-'+LANG+'.json')).write_text(json.dumps(report,indent=2)+'\n','utf8')
        print('Verified '+LANG+' archive: '+str(dest),flush=True)
