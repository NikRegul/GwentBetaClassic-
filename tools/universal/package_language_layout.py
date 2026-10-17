"""Build and package the compact language row for both game branches."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/universal081-language-layout'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import Resource,bundle_entries,sha,require
from dependencies import read_dependency_cache


def verify_art(old_bundle,new_bundle):
    previous=dict(bundle_entries(old_bundle));textures=0
    for name,raw in bundle_entries(new_bundle):
        old=previous.pop(name)
        if name.endswith('.redswf'):
            a,b=Resource(old),Resource(raw)
            require(a.classes==b.classes and a.chunks[1:]==b.chunks[1:],'Texture chunks changed: '+name)
            textures+=len(a.chunks)-1
    require(not previous,'Bundle file set changed')
    return textures


def package(key,source,old_resources,out=None,version=None):
    mod='modBetaGwentClassic132' if key=='classic' else 'modBetaGwent0924'
    platform='1.32-fix3' if key=='classic' else '5.0+'
    out=out or ROOT/f'BetaGwent/release/GwentBetaClassic-0.8.1-{platform}-LanguageLayout-AllLanguages.zip'
    require(not out.exists(),'Keep previous candidates immutable')
    resources=BASE/('resources-'+key)
    count=verify_art(old_resources/'blob0.bundle',resources/'blob0.bundle')
    expected={}
    version=version or '0.8.1-'+('classic-fix3-' if key=='classic' else '')+'language-layout'
    with zipfile.ZipFile(source) as old,zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as new:
        for entry in old.infolist():
            path=entry.filename
            if path in (f'Mods/{mod}/content/blob0.bundle',f'Mods/{mod}/content/metadata.store'):
                p=resources/Path(path).name;new.write(p,path);expected[path]=sha(p);continue
            data=old.read(entry)
            if path in (f'Mods/{mod}/info.json','BetaGwentDocs/BuildInfo.json'):
                info=json.loads(data);info.update(version=version,languageControlsLayout='compact-left-panel-row',nativeGameplayVerified=False)
                data=json.dumps(info,indent=2).encode('utf8')
            elif path=='README_RU.md':
                if key=='nextgen':
                    data='''# Gwent Beta Classic 0.8.1 — 5.0+, компактные кнопки языка

Основа — подтверждённый пользователем menu-fix2. Изменено только оформление
двух языковых кнопок: один ряд над левой панелью, небольшая высота, спокойная
рамка. Текст и озвучка по-прежнему выбираются отдельно, доступен режим Авто.

Установка: закройте игру; замените старую modBetaGwent0924 папкой из Mods
этого архива. Не смешивайте файлы разных версий. При других скриптовых модах
обновите объединение в Script Merger. Сделайте копию сохранений перед тестом.
Эта правка оформления скомпилирована, её внешний вид ещё нужно проверить в игре.
'''.encode('utf-8-sig')
                else:
                    data=data.decode('utf-8-sig').replace('Пиксели, размеры, код меню, правила, скрипты и озвучка сохранены из menu-fix2.',
                        'Пиксели, размеры, правила, скрипты и озвучка сохранены из menu-fix2.')
                    data+='\nДополнительно: кнопки языков выровнены одним компактным рядом над левой панелью; рамки сделаны спокойнее. Оформление также требует проверки в игре.\n'
                    data=data.encode('utf-8-sig')
                if 'fix4' in version:
                    data=data.decode('utf-8-sig').replace('0.8.1 — Classic 1.32, fix3','0.8.1 — Classic 1.32, fix4')
                    data+='\nFix4: регистрация меню вызывается до настройки ввода и отрисовки, без проверки ExternalInterface.available. Native-события вызываются прямым методом объекта, как в штатном Classic GameAdapter. В лог добавлена строка CONTROLLER_INPUT с action=AS_BRIDGE_READY и mode=classic_boot_fix4. При ошибке запуска причина записывается в focus, меню закрывается. Если зависание осталось, сохраните scriptslog.txt сразу после выхода из игры.\n'
                    data=data.encode('utf-8-sig')
            new.writestr(path,data);expected[path]=hashlib.sha256(data).hexdigest()
        dependency_path=f'Mods/{mod}/content/dep.cache'
        if key=='classic' and dependency_path not in expected:
            stage=json.loads((BASE/'menus/menus.json').read_text('utf8'))['sourceStage']
            baseline=ROOT/f'BetaGwent/build/release{stage}/ru/package'
            dependency=baseline/'Mods/modBetaGwent0924/content/dep.cache'
            manifest=json.loads((baseline/'manifest.json').read_text('utf-8-sig'))
            pinned=next(x for x in manifest['files'] if x['path'].endswith('/dep.cache'))
            require(sha(dependency)==pinned['sha256'],'Frozen dependency cache changed')
            read_dependency_cache(dependency.read_bytes())
            new.write(dependency,dependency_path);expected[dependency_path]=sha(dependency)
    with zipfile.ZipFile(out) as archive:
        for path,digest in expected.items():
            with archive.open(path) as stream:require(hashlib.file_digest(stream,'sha256').hexdigest()==digest,'Archive mismatch: '+path)
    report=dict(archive=str(out),sha256=sha(out),bytes=out.stat().st_size,verifiedFiles=len(expected),
                unchangedTextureChunks=count,scriptsAndAudioUnchanged=True,uiCopies=5,gameplayVerified=False)
    out.with_suffix('.zip.sha256').write_text(report['sha256']+'  '+out.name+'\n','ascii')
    out.with_suffix('.verification.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps(report,indent=2),flush=True)
    return report


def main():
    require((BASE/'menus/menus.json').is_file(),'Complete all four menu compilations first')
    spec=importlib.util.spec_from_file_location('ng_resources',ROOT/'tools/universal/build_resources.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.BASE=BASE;module.build()
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/classic132/build_resources.py'),'--stage','202',
        '--menus',str(BASE/'menus'),'--game','D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt',
        '--out',str(BASE/'resources-classic'),'--gui-limit-mib','63'],check=True)
    reports=[package('classic',ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix3-AllLanguages.zip',
                 ROOT/'BetaGwent/build/classic081-cooked-fix3/resources-classic'),
             package('nextgen',Path('C:/Users/NikR/Documents/Codex/2026-10-15/new-chat/outputs/GwentBetaClassic-0.8.1-AllLanguages.zip'),
                 ROOT/'BetaGwent/build/universal081-menu-fix2/resources-nextgen')]
    (BASE/'packages.json').write_text(json.dumps(reports,indent=2)+'\n','utf8')


if __name__=='__main__':main()
