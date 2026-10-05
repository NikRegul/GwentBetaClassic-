"""Build AI alpha by reusing verified cooked stage87 assets and replacing scripts.

No installed game or frozen stage87 inputs are modified. No Wwise keys included.
"""
from pathlib import Path
import argparse,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--compile-dir',type=Path,default=ROOT/'BetaGwent/build/board-compile88e')
args=parser.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
compile_dir=args.compile_dir.resolve()
report=json.loads((compile_dir/'result.json').read_text(encoding='utf-8'))
log=(compile_dir/'stdout.txt').read_text(encoding='utf-8',errors='replace')
assert report['exitCode']==0 and not report['timedOut'] and 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
assert report['patchSourcesUnchangedDuringCompile'] and len(report['patchSourcesBefore'])==60
for entry in report['patchSourcesBefore']:
    assert sha(ROOT/'BetaGwent/build/board-patch'/entry['path'])==entry['sha256']
blob=compile_dir/'compiled/blob.rsblob'
assert sha(blob).upper()==next(x['sha256'] for x in report['artifacts'] if x['path'].endswith('blob.rsblob'))
base=ROOT/'BetaGwent/release/BetaGwent0924-0.1.0-alpha-RU.zip'
assert sha(base)=='66b202780c4a18872ba78e6de1b319e7b6a20a9c2eca1b185aed156a43bd213b'
rules=json.loads((ROOT/'data/beta924/ai/rules.json').read_text(encoding='utf-8'))
policy=json.loads((ROOT/'docs/evidence/stage88-ai-policy.json').read_text(encoding='utf-8'))
assert policy['passed'] and policy['imperaOneCardChaseVerified']
assert policy['sourceSha256']==sha(ROOT/'BetaGwent/development/scripts/game/betagwent/duelArchetypeAI.ws')
readme=(ROOT/'BetaGwent/release/README_RU.md').read_text(encoding='utf-8').replace('0.1.0-alpha','0.1.1-alpha')
readme=readme.replace('Английская локализация и стратегии остальных архетипов будут после этой сборки.',
    'Подключён первый проход ИИ по deck_rules: 40 адаптированных профилей и 70 связок.\nАнглийская локализация и дальнейшая доводка стратегий будут позже.')
readme+='\n## Обновление с 0.1.0-alpha\n\nЗакрой игру и распакуй этот полный архив с заменой `Mods/modBetaGwent0924`.\nПереустановка Wwise/REDkit не требуется. Не держи обе версии в разных папках Mods.\nПодробности и игровой проход — в `AI_RULES88.md`. Новая версия ИИ ещё требует игровой приёмки.\n'
notes=(ROOT/'docs/ai_rules88.md').read_bytes()
destination=ROOT/'BetaGwent/release/BetaGwent0924-0.1.1-alpha-RU.zip'
temp=destination.with_suffix('.zip.tmp')
files=[]
with zipfile.ZipFile(base) as old,zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as new:
    manifest=json.loads(old.read('manifest.json'));expected={x['path']:x for x in manifest['files']}
    replacements={'Mods/modBetaGwent0924/content/precompiled.rsblob':blob.read_bytes(),
                  'README_RU.md':readme.encode('utf-8')}
    info=json.loads(old.read('Mods/modBetaGwent0924/info.json'));info['version']='0.1.1-alpha'
    info['description']='Russian test alpha with adapted deck_rules archetype AI, 93 presets and shared round economy.'
    replacements['Mods/modBetaGwent0924/info.json']=(json.dumps(info,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    replacements['TEST_CHECKLIST_RU.md']=old.read('TEST_CHECKLIST_RU.md')+b'\n\nAI: see AI_RULES88.md for the combined battle check.\n'
    for entry in old.infolist():
        if entry.filename=='manifest.json':continue
        hasher=hashlib.sha256();size=0
        # Verify base bytes even for replaced entries.
        with old.open(entry) as src:
            while chunk:=src.read(1024*1024):hasher.update(chunk);size+=len(chunk)
        assert hasher.hexdigest()==expected[entry.filename]['sha256'] and size==expected[entry.filename]['bytes']
        data=replacements.get(entry.filename)
        if data is not None:
            new.writestr(entry.filename,data);hasher=hashlib.sha256(data);size=len(data)
        else:
            with old.open(entry) as src,new.open(entry.filename,'w') as dst:
                while chunk:=src.read(1024*1024):dst.write(chunk)
        files.append(dict(path=entry.filename,bytes=size,sha256=hasher.hexdigest()))
    new.writestr('AI_RULES88.md',notes)
    files.append(dict(path='AI_RULES88.md',bytes=len(notes),sha256=hashlib.sha256(notes).hexdigest()))
    manifest.update(version='0.1.1-alpha',stage=88,files=files,activeAIProfiles=40,comboPairs=70,presets=93,
        baseAssetsSha256=sha(base),compiledBlobSha256=sha(blob),runtimeVerified=False,
        notes='First archetype AI pass; cooked menu, art, audio and localization bytes reused from verified stage87. Native battle acceptance and English translation remain pending.')
    new.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(temp) as verify:
    assert verify.testzip() is None
    for entry in files:
        hasher=hashlib.sha256()
        with verify.open(entry['path']) as src:
            while chunk:=src.read(1024*1024):hasher.update(chunk)
        assert hasher.hexdigest()==entry['sha256']
temp.replace(destination)
evidence=dict(stage=88,version='0.1.1-alpha',archive=str(destination),archiveBytes=destination.stat().st_size,
    archiveSha256=sha(destination),files=files,compiledSources=60,activeAIProfiles=40,comboPairs=70,presets=93,
    archiveCRCVerified=True,archiveFileHashesVerified=True,originalStage87Unchanged=sha(base)==manifest['baseAssetsSha256'],
    reusedCookedAssets=True,installedGameModified=False,nativeRuntimeVerified=False,licenseIncluded=False)
(ROOT/'docs/evidence/stage88-ai-release.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in evidence.items() if k!='files'},ensure_ascii=False))
