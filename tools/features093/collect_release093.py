"""Gather everything needed to publish 0.9.3 into one folder (copies only, nothing deleted).

Usage: python -X utf8 tools/features093/collect_release093.py <build-folder> [--dest release\\0.9.3]
Accepts only a finished build: release-readiness.json + archive-verification.json + matching SHA-256.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
NOTES=ROOT/'docs/releases/0.9.3-public-20261025'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CHECKLIST='''# 0.9.3 — что проверить в игре перед публикацией

Автоматические проверки и обе нативные компиляции пройдены сборкой. Ниже то, что можно подтвердить только в самой игре.
Отметьте пункты на Next-Gen 5.0+ и на Classic 1.32.

## Подписи выбора карт (новое)
- [ ] Удальрик: окно «Возьмите одну карту», подсказка «Выбранная карта уйдёт в руку, вторая — в сброс». После выбора вторая карта лежит в сбросе.
- [ ] Талер / Яевинн: «Возьмите одну карту», вторая остаётся в колоде.
- [ ] Ге'эльс: «Разыграйте одну карту», вторая ложится на верх колоды.
- [ ] Шилярд Фиц-Эстерлен: «Оставьте одну карту», вторая уходит в руку соперника.
- [ ] Кантарелла: «Оставьте одну карту», вторая уходит вниз колоды.
- [ ] Сброс из руки (Ивасик, Мышовур, Сванриге Тиршах), замена (Сара, Бьянка, Офицер «Врихедд», Эльфская разведчица, Саския, Францеска Финдабаир, Учитель из Бан Арда), поглощение (Принц-жаба), сброс из колоды (Лугос Безумный, Друммонд: мародер, Бран Тиршах), Оператор — подпись объясняет, куда уйдёт карта.
- [ ] Другой выбор из колоды/сброса (например, Лютик, Неннеке): вместо общего текста показан текст способности карты.
- [ ] Смените язык текста (EN, DE, JA, ZH) — подписи переведены, текст не вылезает за рамки.
- [ ] То же с контроллером: фокус, подтверждение, отмена/«Вернуться к выбору».
- [ ] Сванриге / Мышовур и аналогичные выборы из руки/колоды: карта показана, стрелки к руке нет. Во время решения ИИ наведение на свою руку/поле не рисует его стрелку; обычное прицеливание по полю в свой ход работает.

## Исправления 0.9.3 по логам
- [ ] Пользовательские колоды: создать несколько новых, переименовать кириллицей/латиницей, сохранить игру, выйти полностью, загрузить сохранение. Составы, имена и стартовые переопределения сохранены; в журнале нет DECK_SAVE_REJECT/profileStorage.
- [ ] На копии сохранения после восстановления профиля: колоды загружаются и редактируются; удалённая вручную колода не появляется снова из старого резерва. Не стирать оригинальные сохранения ради этого теста.
- [ ] Циклоп: при выборе между восстанавливающимся мечником Ан Крайт вне смертельного урона и уязвимой целью предпочитает полезное добивание; добивание самого мечника по-прежнему доступно.
- [ ] Лугос Безумный: аналогичный выбор после сброса отряда — урон от его базовой силы учитывает восстановление мечника, добивание и единственная цель сохранены.
- [ ] Яд и Эльфская сабля: показывают правильный выбор цели; Кейран может поглотить Мирруну до её вражеского эффекта.
- [ ] Вскрытие (Алхимик, Морвран): выбираются карты соперника, скрытые показаны рубашкой; два вскрытия вызывают двух разных големов.
- [ ] Перед боем и в бою показано имя NPC, без ch_fac_*/внутренних профилей.
- [ ] Выбор колод: нет лишнего «Ваша колода»; в редакторе нет пустой полосы под лидером.
- [ ] Озвучка: RU/EN/DE/IT/PT-BR/Auto реально меняют голос в бою (не только подпись кнопки); выбор сохраняется после перезапуска.
- [ ] Сложность «Классическая» видна и выбирается рядом с языками.

## Пакет
- [ ] Полный прогон карт на настоящих обеих версиях остаётся отдельным: автоматические отчёты all-card-platforms исполняют перевод подготовленного WS на стенде, а не в установленной игре.
- [ ] Установка из архива 5.0+ и 1.32 на чистую копию; игра запускается, меню открываются.
- [ ] Папка с необязательными файлами копирования колоды (dinput8.dll + ASI) лежит отдельно; без неё кнопки импорта/экспорта скрыты.
'''
def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--dest',type=Path,default=ROOT/'release/0.9.3');a=p.parse_args(argv)
    out=a.build.resolve();dest=a.dest.resolve()
    ready=json.loads((out/'release-readiness.json').read_text('utf8'));assert ready['status']=='ready' and ready['version']=='0.9.3'
    audit=json.loads((out/'archive-verification.json').read_text('utf8'))
    zips=sorted((out/'archives').glob('GwentBetaClassic-0.9.3-*-AllLanguages.zip'));assert len(zips)==2,zips
    for z in zips:
        digest=(z.with_suffix('.zip.sha256')).read_text('ascii').split()[0];assert sha(z)==digest,z
    if dest.exists():
        n=2
        while (dest.parent/f'{dest.name}-{n}').exists():n+=1
        dest=dest.parent/f'{dest.name}-{n}'
    for sub in ['archives','nexus','reports']:(dest/sub).mkdir(parents=True)
    for z in zips:shutil.copy2(z,dest/'archives'/z.name);shutil.copy2(z.with_suffix('.zip.sha256'),dest/'archives'/(z.name+'.sha256'))
    for doc in sorted(NOTES.glob('0.9.3_*.md'))+[NOTES/'README.md']:shutil.copy2(doc,dest/'nexus'/doc.name)
    if (NOTES/'BBCode/manifest.json').is_file():shutil.copytree(NOTES/'BBCode',dest/'nexus/BBCode')
    for name in ['release-readiness.json','archive-verification.json','user-release-checks.json','choice-captions.json','choice-fates.json','user-ui-check.json','card-offer.json','full-ai-games/report.json',
                 'regressions/check_special_target_mode197.json','regressions/check_kayran_miruna197.json','regressions/check_cyclops_swordsman197.json','regressions/check_stored_damage198.json','stored-damage-witness198.json']:
        src=out/name
        if src.exists():shutil.copy2(src,dest/'reports'/name.replace('/','-'))
    gate=json.loads((out/'user-release-checks.json').read_text('utf8'))
    for row in gate['reports']:
        src=out/row['path'];assert src.resolve().is_relative_to(out)
        assert sha(src)==row['sha256'],row['path']
        shutil.copy2(src,dest/'reports'/row['path'].replace('/','-'))
    (dest/'CHECKLIST_RU.md').write_text(CHECKLIST,'utf8')
    lines=['# Gwent Beta Classic 0.9.3 — файлы релиза','',f'Сборка: `{out}`','','## Архивы','']
    for z in zips:lines.append(f'- `archives/{z.name}` — {z.stat().st_size} байт, SHA-256 `{sha(z)}`')
    lines+=['','## Тексты для Nexus (13 языков)','','`nexus/`: описание (`0.9.3_DESCRIPTION_*`), пост (`0.9.3_POST_*`) и changelog от 0.9.1 (`0.9.3_CHANGELOG_*`). Сначала английский, затем русский.','',
      '## Отчёты','','`reports/`: готовность, независимая проверка архивов (SHA/CRC/manifest) и проверки подписей выбора карт.','',
      '## Перед публикацией','','Пройдите `CHECKLIST_RU.md` в игре на обеих версиях. Ничего не установлено и не опубликовано автоматически.','']
    (dest/'README_RU.md').write_text('\n'.join(lines),'utf8')
    print('Release files collected in',dest)
    return dest
if __name__=='__main__':main()
