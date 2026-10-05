"""Verify final preview artifacts and update the persistent work plan."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    evidence=ROOT/'docs/evidence'
    completion=json.loads((evidence/'stage91-completion.json').read_text('utf8'))
    assert len(completion['menus'])==6
    for item in completion['menus']:assert sha(Path(item['resource']))==item['sha256']
    for language in ('ru','en'):
        release=json.loads((evidence/f'stage91-release-{language}.json').read_text('utf8'))
        assert release['archiveVerified'] and sha(Path(release['archive']))==release['archiveSha256']
        original=json.loads((evidence/f'stage89-release-{language}.json').read_text('utf8'))
        assert sha(Path(original['archive']))==original['archiveSha256']
        for job in ('cook','dependencies','pack','metadata'):
            result=json.loads((ROOT/f'BetaGwent/build/release91/{language}/jobs/{job}/result.json').read_text('utf8'))
            assert result['exitCode']==0 and not result['timedOut']
    for item in completion['menus']:
        if item['language']=='ru':
            installed=ROOT/'GwentB/myproject1/workspace/betagwent'/Path(item['resource']).name
            assert sha(installed)==item['sha256']
    extraction=json.loads((ROOT/'BetaGwent/build/beta-presentation91/manifest.json').read_text('utf8'))
    assert extraction['sourceUnchanged'] and not extraction['errors']
    for path,digest in extraction['sourceHashes'].items():assert sha(Path(path))==digest
    completion['previewArchives']={lang:json.loads((evidence/f'stage91-release-{lang}.json').read_text('utf8'))['archive'] for lang in ('ru','en')}
    completion['extractionSourceHashesVerified']=True
    (evidence/'stage91-completion.json').write_text(json.dumps(completion,indent=2)+'\n','utf8')
    header='''## Текущий шаг — 91: фракционные доски и оригинальные эффекты Beta

Собраны отдельные RU/EN `0.2.1-preview.1`. Первый релиз ZIP0.2.0 сохранён.
Подробности и общая проверка: [PRESENTATION91_RU.md](PRESENTATION91_RU.md).
Порядок извлечения/сборки: [BETA_VISUAL_PIPELINE91.md](BETA_VISUAL_PIPELINE91.md).

Поле Beta включено по умолчанию. Нижняя половина выбирается по фракции
игрока, верхняя — соперника; используются десять оригинальных половин
из мешей/UV всех пяти фракций. DIY1/2 доступны переключателем.
Перенесены рамки/свечение целей, указатель, веер руки, плавная вставка,
вспышки, след, физические удары, дым и призыв. Туман использует30 кадров
и исходную кривую; ввод погоды — длительности оригинальных клипов.
Крупные hover-подсказки задерживаются и не закрывают поле при выборе цели.

Извлечены28 текстур досок/фонов,38 мешей,329 систем частиц с конфигурацией,
30 клипов и114 текстур эффектов. 81 stripped MonoBehaviour сохранён
бинарно и ещё требует декодирования. Полные Unity-шейдеры не перенесены;
часть основания Мороза остаётся из TW3. Исходный клиент не изменён.

Шесть меню RU/EN проверены:44 связи, ABC, DDS, CRC. Атлас4096×3780,
667 привязок. Упаковщик следует фактическому порядку ImageInfo.
Native cook/dependencies/pack/metadata и ZIP CRC/SHA успешны.
WS этапа90 переиспользованы после побайтового сравнения60 исходников.
Игра на F: не изменялась; в REDkit-проект установлены RU-ресурсы.

Следующее: одна игровая проверка смешанных/зеркальных фракций, вставки
и целей с мышью/контроллером, удара/призыва/погоды. Принятия в игре ещё нет.
После этого доработать совмещение рядов и эффекты школ урона/засад,
перенести оставшиеся кривые и продолжить ИИ по плану90.

'''
    plan=ROOT/'docs/plan.md';text=plan.read_text('utf8')
    if '## Текущий шаг — 91:' not in text:
        index=text.index('## Текущий шаг');text=text[:index]+header+'## Предыдущие этапы\n\n'+text[index:]
    text=text.replace('DIY/PDF2025 используются для досок и идей; способности — из локальной беты.',
                      'Доски: локальная Beta и DIY; PDF2025 — идеи. Правила — строгая локальная Beta.')
    plan.write_text(text,'utf8')
    progress=ROOT/'docs/progress.md';text=progress.read_text('utf8')
    if '2026-10-05 — 91:' not in text:text+='\n## 2026-10-05 — 91: фракционные половины и перенос презентации\n\n'+header.split('\n\n',1)[1]
    progress.write_text(text,'utf8')
    print('Stage91 recorded. Six native movies and two preview archives verified; runtime acceptance pending.')

if __name__=='__main__':main()
