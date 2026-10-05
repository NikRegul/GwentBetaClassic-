"""Verify the deckbuilder preview and record the continuation point."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    evidence=ROOT/'docs/evidence';report=json.loads((evidence/'stage92-completion.json').read_text('utf8'))
    assert len(report['menus'])==6
    for item in report['menus']:
        assert sha(Path(item['resource']))==item['sha256']
        if item['language']=='ru':assert sha(ROOT/'GwentB/myproject1/workspace/betagwent'/Path(item['resource']).name)==item['sha256']
    for name,digest in report['sources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest
    for lang in ('ru','en'):
        release=json.loads((evidence/f'stage92-release-{lang}.json').read_text('utf8'))
        assert release['archiveVerified'] and sha(Path(release['archive']))==release['archiveSha256']
        for stage in (89,91):
            old=json.loads((evidence/f'stage{stage}-release-{lang}.json').read_text('utf8'))
            assert sha(Path(old['archive']))==old['archiveSha256']
        for job in ('cook','dependencies','pack','metadata'):
            result=json.loads((ROOT/f'BetaGwent/build/release92/{lang}/jobs/{job}/result.json').read_text('utf8'))
            assert result['exitCode']==0 and not result['timedOut']
    extraction=json.loads((evidence/'beta-editor92.json').read_text('utf8'))
    assert extraction['sourceUnmodified'] and len(extraction['sprites'])==35
    for path,digest in extraction['sources'].items():assert sha(Path(path))==digest
    atlas=json.loads((evidence/'card-art-build.json').read_text('utf8'))
    assert atlas['atlasSize']==[4096,3960] and len(atlas['betaEditor'])==35
    report['previewArchives']={lang:json.loads((evidence/f'stage92-release-{lang}.json').read_text('utf8'))['archive'] for lang in ('ru','en')}
    report['editorSourceHashesVerified']=True
    (evidence/'stage92-completion.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    header='''## Текущий шаг — 92: редактор создания колоды в оформлении Beta

Собраны отдельные RU/EN `0.2.1-preview.2`, включая поле и эффекты preview.1.
Первый релиз0.2.0 и preview.1 сохранены. В REDkit-проекте обновлены RU-меню;
установленная игра не менялась. [Изменения и общая проверка](PRESENTATION92_RU.md).
[Порядок извлечения и сборки](BETA_EDITOR_PIPELINE92.md).

Оригинальная компоновка Beta: состав/лидер слева, коллекция по центру,
постоянная крупная карта/описание справа. Извлечены фон, деревянные полки,
рамки редкости, значки фильтров/фракций и цветные панели всех пяти фракций;
35 новых привязок. Экспортирована иерархия RectTransform редактора Beta.
Атлас4096×3960 содержит702 привязки. Исходные Unity-бандлы не изменены.

Сохранены восемь слотов, переименование, поиск/фильтры, правила колод.
Обновлены View между составом/коллекцией, LT/RT копий, LB/RB страниц,
Start сохранения; лидеры защищены от изменения количества триггерами.
Правая панель показывает каноническое описание, теги, словарь и flavour;
прокрутка колесом/стиком. Наведение меняет только панель выбранной карты.

Шесть меню RU/EN:44 связи, ABC, DDS/CRC проверены. Native cook/dependencies/
pack/metadata и ZIP CRC/SHA прошли.60 WS совпали с компиляцией этапа90.
Качество внешнего вида и управления в игре пока не принято.

Следующее: общая проверка создания/переименования/сохранения колоды, всех
фракций/лидеров, фильтров/страниц мышью и контроллером, затем один NPC-бой.
После этого перенести выбор сохранённых колод и каталог в оформление Beta,
продолжить переходы/эффекты поля и ИИ по плану90. Полные Unity-шейдеры
и премиум-анимации ещё не перенесены.

'''
    plan=ROOT/'docs/plan.md';text=plan.read_text('utf8')
    if '## Текущий шаг — 92:' not in text:
        index=text.index('## Текущий шаг');text=text[:index]+header+text[index:]
        text=text.replace('## Текущий шаг — 91:','## Этап91:',1)
    plan.write_text(text,'utf8')
    progress=ROOT/'docs/progress.md';text=progress.read_text('utf8')
    if '2026-10-05 — 92:' not in text:text+='\n## 2026-10-05 — 92: редактор Beta\n\n'+header.split('\n\n',1)[1]
    progress.write_text(text,'utf8')
    print('Stage92: six native menus and two preview archives verified; runtime acceptance pending.')
if __name__=='__main__':main()
