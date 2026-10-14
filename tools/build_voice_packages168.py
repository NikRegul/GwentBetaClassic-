"""Build five voice ZIPs from one verified RU revision; each has all 13 text languages."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tools/ui'))
from build_from_source import release_module
from build_release138 import presentation_lock
from build_voice137 import language_bridge
VOICES=('ru','en','de','it','pt-br')
PHASES=('prepare','cook','strings','audio','dependencies','pack','metadata','archive')
def sha(p):
    with Path(p).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def verify_zip(path,version,language,stage):
    with zipfile.ZipFile(path) as archive:
        manifest=json.loads(archive.read('manifest.json'))
        assert (manifest['version'],manifest['language'],manifest['stage'])==(version,language,stage)
        assert len(manifest['textLanguages'])==13 and manifest['voiceLanguage']==language
        assert archive.testzip() is None
        expected={f['path']:f for f in manifest['files']}
        assert set(archive.namelist())==set(expected)|{'manifest.json'}
        for name,item in expected.items():
            data=archive.read(name);assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],name
    digest=sha(path);assert path.with_suffix('.zip.sha256').read_text('ascii').split()[0]==digest
    return dict(path=str(path),bytes=path.stat().st_size,sha256=digest,voice=language,textLanguages=13,verified=True)
def unbridge(text):
    marker='\nfunction BetaGwentTextLanguage137(value:int):int\n'
    assert text.count(marker)==1,'Expected the frozen RU language wrapper'
    text=text.split(marker)[0]
    wrapped='FlashArgInt(BetaGwentTextLanguage137(FactsQueryLatestValue("bg_text_language")))'
    assert text.count(wrapped)==1
    return text.replace(wrapped,'FlashArgInt(FactsQueryLatestValue("bg_text_language"))')
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',default='0.7.1');p.add_argument('--stage',type=int,default=0)
    p.add_argument('--verify',action='store_true');p.add_argument('--check-only',action='store_true')
    a=p.parse_args();assert re.fullmatch(r'[0-9A-Za-z.\-]+',a.version)
    banks=read(ROOT/'docs/evidence/voice141.json')
    for language in VOICES:
        item=banks[language];catalog=Path(item['patch'])/'game/betagwent/duelAudioCatalog.ws'
        assert sha(item['bank'])==item['sha256'] and sha(catalog)==item['catalogSha256'],language
    ru=ROOT/f'BetaGwent/release/GwentBetaClassic-{a.version}-RU.zip'
    if a.check_only:
        print(json.dumps(dict(version=a.version,voices=list(VOICES),textLanguages=13,ruReady=ru.exists(),banksVerified=True,installsGame=False),indent=2));return
    if not ru.exists():
        if a.verify:raise RuntimeError('RU package has not been built')
        with presentation_lock():
            subprocess.run([sys.executable,'-X','utf8','tools/ui/build_ui_languages138.py'],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        command=[sys.executable,'-X','utf8','tools/build_from_source.py','--version',a.version,'--gui-limit-mib','65']
        if a.stage:command+=['--stage',str(a.stage)]
        subprocess.run(command,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    with zipfile.ZipFile(ru) as archive:stage=json.loads(archive.read('manifest.json'))['stage']
    if a.stage and stage!=a.stage:raise RuntimeError('RU archive belongs to a different stage')
    base=ROOT/f'BetaGwent/build/stage{stage}';logs=base/'voice-package-logs';logs.mkdir(exist_ok=True)
    budget=read(base/'gui-budget.json')['guiLimitMiB']
    if budget!=65:raise RuntimeError('0.7.1 batch requires the reviewed 65 MiB target')
    def job(label,*args):
        print(label,flush=True);log=logs/(label+'.log')
        with log.open('wb') as output:
            result=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise RuntimeError('Build failed; inspect '+str(log))
    with presentation_lock():
        release=release_module(stage);release['VERSION']=a.version;release['verify_package']()
        # Packaging uses shared lazy text/leader resources. They must still match
        # the verified RU cook, even if unrelated current sources were changed.
        ru_work=ROOT/f'BetaGwent/build/release{stage}/ru/project/BetaGwent0924/workspace'
        for relative in ('text138/resources','leaders137/resources','leader-intro-resources142/resources'):
            for resource in (ROOT/'BetaGwent/build'/relative).rglob('*.redswf'):
                depot=resource.relative_to(ROOT/'BetaGwent/build'/relative)
                assert sha(resource)==sha(ru_work/depot),'Shared resource changed after RU build: '+str(depot)
        patch=base/'ru/sources/scripts';frozen_bridge=unbridge((patch/'game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig'))
        inputs=dict(stage=stage,version=a.version,guiLimitMiB=budget,ruSha256=sha(ru),scripts={str(f.relative_to(patch)):sha(f) for f in patch.rglob('*.ws')},voiceCatalogs={v:banks[v]['catalogSha256'] for v in VOICES})
        frozen=base/'voice-package-inputs.json'
        if frozen.exists():assert read(frozen)==inputs,'Batch inputs changed; use a new version'
        else:frozen.write_text(json.dumps(inputs,indent=2)+'\n','utf8')
        outputs=[verify_zip(ru,a.version,'ru',stage)]
        for language in VOICES[1:]:
            archive=ROOT/f'BetaGwent/release/GwentBetaClassic-{a.version}-{language.upper()}.zip'
            if archive.exists():outputs.append(verify_zip(archive,a.version,language,stage));continue
            if a.verify:raise RuntimeError('Package is missing: '+str(archive))
            notes=ROOT/f'docs/PRESENTATION{stage}_{language.upper()}.md'
            if not notes.exists():shutil.copy2(ROOT/f'docs/releases/{a.version}/UPDATE_EN.md',notes)
            destination=base/language/'sources/scripts';receipt=base/language/'voice-steps.json'
            done=read(receipt) if receipt.exists() else []
            if not destination.exists():
                shutil.copytree(patch,destination)
                shutil.copy2(Path(banks[language]['patch'])/'game/betagwent/duelAudioCatalog.ws',destination/'game/betagwent/duelAudioCatalog.ws')
                (destination/'game/betagwent/developmentBoardMenu.ws').write_text(language_bridge(frozen_bridge,language),'utf-8-sig')
            expected={str(f.relative_to(destination)):sha(f) for f in destination.rglob('*.ws')}
            assert len(expected)==70
            for name,digest in inputs['scripts'].items():
                if name.replace('\\','/') not in ('game/betagwent/duelAudioCatalog.ws','game/betagwent/developmentBoardMenu.ws'):assert expected[name]==digest,(language,name)
            assert sha(destination/'game/betagwent/duelAudioCatalog.ws')==banks[language]['catalogSha256']
            assert (destination/'game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig')==language_bridge(frozen_bridge,language)
            compilation=base/language/'compile'
            if 'compile' not in done:
                attempt=1;output=compilation
                while output.exists():output=compilation.with_name('compile-retry'+str(attempt));attempt+=1
                job(language+'-compile','tools/recon/run_redkit_compile.py','--out',output,'--patch',destination,'--timeout','300','--terms-already-accepted')
                (base/language/'voice-compile.json').write_text(json.dumps(dict(path=str(output),sources=expected),indent=2)+'\n','utf8')
                done.append('compile');receipt.write_text(json.dumps(done)+'\n','utf8')
            record=read(base/language/'voice-compile.json');assert record['sources']==expected
            compilation=Path(record['path']);result=read(compilation/'result.json');assert result['exitCode']==0 and result['patchSourcesUnchangedDuringCompile']
            for phase in PHASES:
                if phase in done:continue
                job(language+'-'+phase,'tools/build_language_release.py',phase,'--stage',stage,'--version',a.version,'--language',language,'--compiled',compilation,'--gui-limit-mib',budget)
                done.append(phase);receipt.write_text(json.dumps(done)+'\n','utf8')
            outputs.append(verify_zip(archive,a.version,language,stage))
        (ROOT/f'docs/evidence/voice-batch{stage}.json').write_text(json.dumps(dict(version=a.version,stage=stage,passed=True,packages=outputs,nativeGameTested=False),indent=2)+'\n','utf8')
        print('Verified all five voice packages; 13 selectable text languages in each.',flush=True)
if __name__=='__main__':main()
