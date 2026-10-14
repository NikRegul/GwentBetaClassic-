"""Build 0.6.8b from the verified 0.6.8 stage with smaller effect atlases."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from build_from_source import release_module,job
from build_release138 import presentation_lock

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n','utf8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-stage',type=int,default=148);p.add_argument('--stage',type=int,default=149);p.add_argument('--version',default='0.6.8b');a=p.parse_args()
    if not re.fullmatch(r'\d+\.\d+\.\d+[a-z]?',a.version):p.error('Invalid variant version')
    source=ROOT/f'BetaGwent/build/stage{a.source_stage}';base=ROOT/f'BetaGwent/build/stage{a.stage}'
    archive=ROOT/f'BetaGwent/release/GwentBetaClassic-{a.version}-RU.zip'
    if base.exists() or archive.exists():raise RuntimeError('Variant stage/version must be new')
    with presentation_lock():
        previous=release_module(a.source_stage);previous['VERSION']=read(ROOT/f'docs/evidence/inputs{a.source_stage}.json')['version'];previous['inputs']()
        base.mkdir(parents=True);logs=base/'logs';profile=base/'ui-profile';ui=profile/'src'
        canonical=ROOT/'BetaGwent/ui/src';shutil.copytree(canonical,ui)
        assets=[]
        for path in canonical.rglob('*.as'):
            for relative in re.findall(r'\[Embed\([^\]]*source="([^"]+)"',path.read_text('utf-8-sig')):
                original=(path.parent/relative).resolve();destination=(ui/path.relative_to(canonical)).parent/relative;destination=destination.resolve()
                if not destination.is_relative_to(profile.resolve()):raise RuntimeError('Embed path escapes isolated UI profile')
                destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,destination)
                if not any(e['path']==str(destination) for e in assets):assets.append(dict(path=str(destination),sha256=sha(destination)))
        reduced=[]
        for filename in ('kill_beta.png','kill2_beta.png','lightning_beta.png'):
            original=ROOT/'BetaGwent/ui/assets/special144'/filename;target=profile/'assets/special144'/filename
            with Image.open(original) as image:
                before=list(image.size);after=[v//2 for v in image.size]
                image.convert('RGBA').resize(after,Image.Resampling.LANCZOS).save(target)
            reduced.append(dict(file=filename,before=before,after=after,sourceSha256=sha(original),sha256=sha(target)))
        for filename in ('BetaGwentKillArt144.as','BetaGwentLightning144.as'):
            path=ui/filename;text=path.read_text('utf-8-sig');assert text.count('bitmap.smoothing=true;')==1
            changed=text.replace('bitmap.smoothing=true;','bitmap.smoothing=true;bitmap.scaleX=2;bitmap.scaleY=2;')
            path.write_text(changed,'utf-8-sig')
            assert path.read_text('utf-8-sig').replace('bitmap.scaleX=2;bitmap.scaleY=2;','')==(canonical/filename).read_text('utf-8-sig')
        for item in assets:item['sha256']=sha(Path(item['path']))
        save(base/'ui-profile.json',dict(sourceDir=str(ui),assets=assets,baseSources={p.name:sha(p) for p in canonical.glob('*.as')},reduced=reduced))
        save(base/'gui-budget.json',dict(guiLimitMiB=56,experimental=False,nativeGameTested=False))
        shutil.copytree(source/'ru/sources/scripts',base/'ru/sources/scripts');shutil.copytree(source/'compile',base/'compile')
        shutil.copytree(ROOT/f'BetaGwent/build/audit{a.source_stage}/source',ROOT/f'BetaGwent/build/audit{a.stage}/source')
        regressions=read(ROOT/f'docs/evidence/regressions{a.source_stage}.json');assert regressions['passed']
        regressions.update(stage=a.stage,reusedFromStage=a.source_stage,unchangedRules=True,unchangedBoardLogic=True)
        save(ROOT/f'docs/evidence/regressions{a.stage}.json',regressions)
        job('profile-check',['tools/ui/check_low_memory149.py',str(base/'ui-profile.json')],logs)
        job('native-menus',['tools/build_presentation94.py','--stage',a.stage,'--language','ru','--source-dir',ui],logs)
        variant=release_module(a.stage);variant['VERSION']=a.version
        publish=ROOT/'BetaGwent/release'/('publish-'+a.version)
        if publish.exists():raise RuntimeError('Variant documentation directory already exists')
        shutil.copytree(ROOT/'BetaGwent/release'/('publish-'+previous['VERSION']),publish)
        note='\nLow-memory variant: three effect atlases use half resolution in each dimension. Cards, leaders, text, timings, rules and AI are preserved. GUI loading target: 56 MiB.\n'
        for path in publish.glob('*.md'):path.write_text(path.read_text('utf8').replace(previous['VERSION'],a.version)+note,'utf8')
        overview=ROOT/f'docs/PRESENTATION{a.stage}_RU.md'
        overview.write_text('# Gwent Beta Classic '+a.version+' — вариант с прежним лимитом GUI\n\n'+
            'Основан на проверенной сборке '+previous['VERSION']+'. Три атласа частиц (Казнь/Игни/Жальница, Ирден и электричество) уменьшены вдвое по каждой стороне. Размеры, координаты, количество кадров и время эффектов сохранены; детали частиц мягче. Иллюстрации карт, портреты лидеров, тексты, правила и ИИ прежние.\n\n'+
            'Порог GUI остаётся 56 МиБ. Нативные меню пересобраны из отдельной копии UI; исходные изображения пользователя не изменены. Компиляция 70 скриптов и 52 набора регрессий переиспользованы после сверки идентичности. Дополнительно проверены сетки частиц и масштабирование. Отсутствие чёрного экрана проверяется в игре.\n','utf8')
        variant['inputs']()
        for phase in ('prepare','cook','strings','audio','dependencies','pack','metadata','archive'):
            variant['step']('package-ru-'+phase,'tools/build_language_release.py',phase,'--stage',a.stage,'--version',a.version,'--language','ru','--compiled',base/'compile')
        variant['verify_package']()
        report=read(ROOT/f'docs/evidence/validation{a.stage}.json');report['sourceStage']=a.source_stage;report['reducedEffectAtlases']=reduced
        save(ROOT/f'docs/evidence/validation{a.stage}.json',report)
if __name__=='__main__':main()
