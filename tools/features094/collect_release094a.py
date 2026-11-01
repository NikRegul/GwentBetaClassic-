"""Gather everything needed to publish 0.9.4a into one folder (copies only, nothing deleted).

Usage: python -X utf8 tools/features094/collect_release094a.py <build-folder> [--dest release\\0.9.4a]
Accepts only a finished build: release-readiness.json + archive-verification.json + matching SHA-256.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
VERSION='0.9.4a'
NOTES=ROOT/'docs/releases/0.9.4a-public-20261027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CHECKLIST='''# 0.9.4a — что проверить в игре перед публикацией

Автоматические проверки и обе нативные компиляции пройдены сборкой. Ниже то, что можно подтвердить только в игре.
Отметьте пункты на Next-Gen 5.0+ и на Classic 1.32. Работайте на копиях сохранений.

## Эффекты редактора колод (новое в 0.9.4a)
- [ ] Редактор из меню паузы (Гвинт → колоды): клик по карте коллекции — на этой карте вспышка, синяя рамка и искры влево, затем карта улетает в список колоды.
- [ ] Удаление карты из списка колоды: карта прилетает в коллекцию, на ней вспышка с искрами вправо.
- [ ] То же через перетаскивание и через геймпад; эффект ровно над картой, в том числе после прокрутки коллекции.
- [ ] «Отменить карту» после добавления: проигрывается эффект удаления.
- [ ] Карта, которой не видно в коллекции (отфильтрована или прокручена): эффекта нет, только перелёт.
- [ ] Отказ (лимит 40 карт, золото/серебро, нет копии): ни эффекта, ни перелёта.
- [ ] «Эффекты: кратко»: эффектов нет.
- [ ] Редактор перед матчем с NPC (меню DeckBuilder) и тренировочный стол: эффекты те же.
- [ ] Бой после редактора: боевые эффекты (огонь, мороз, молния, усиления) выглядят как раньше.
- [ ] 1.32: меню редактора открывается без вылета и без чёрных или розовых квадратов вместо эффектов.

## Лидер, редактор и геймпад
- [ ] В редакторе нет кнопок смены фракции и лидера; лидер и фракция выбираются в окне новой колоды.
- [ ] Импорт кода с другим лидером в открытую колоду отклоняется; импорт новой колоды из списка берёт лидера из кода.
- [ ] Фильтр или поиск после прокрутки показывает список с начала.
- [ ] Геймпад: при выборе цели (например, урон по карте) видна стрелка от карты к цели.

## Карты и ИИ
- [ ] Кит из Пещеры Снов (Лугос Синий создаёт его у противника): в конце каждого хода переходит в другой ряд и бьёт по 1 соседей в новом ряду.
- [ ] Шелдон Скаггс у ИИ «Сложная» выставляется в ряд с союзниками и получает усиление.

## Сохранения (как в 0.9.4)
- [ ] Загрузить сейв 0.9.4: коллекция, колоды, осколки и бочки на месте; в логе `PROFILE_STORE_LOADED`, нет `PROFILE_STORE_REJECTED`.
- [ ] Сохранить → полностью выйти → загрузить: всё на месте.

## Пакет
- [ ] Установка из архивов 5.0+ и 1.32 на чистую копию; игра запускается, меню открываются.
'''
def bbcode(md):
    out=[]
    for line in md.splitlines():
        if line.startswith('# '):out.append('[size=5][b]'+line[2:]+'[/b][/size]')
        elif line.startswith('## '):out.append('[size=4][b]'+line[3:]+'[/b][/size]')
        elif line.startswith('- '):out.append('[*]'+line[2:])
        else:out.append(re.sub(r'\*\*(.+?)\*\*',r'[b]\1[/b]',line))
    text='\n'.join(out)
    return re.sub(r'((?:\[\*\].*\n?)+)',lambda m:'[list]\n'+m.group(1).rstrip('\n')+'\n[/list]\n',text)
def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--dest',type=Path,default=ROOT/'release'/VERSION);a=p.parse_args(argv)
    out=a.build.resolve();dest=a.dest.resolve()
    ready=json.loads((out/'release-readiness.json').read_text('utf8'));assert ready['status']=='ready' and ready['version']==VERSION
    json.loads((out/'archive-verification.json').read_text('utf8'))
    zips=sorted((out/'archives').glob(f'GwentBetaClassic-{VERSION}-*-AllLanguages.zip'));assert len(zips)==2,zips
    for z in zips:
        digest=(z.with_suffix('.zip.sha256')).read_text('ascii').split()[0];assert sha(z)==digest,z
    if dest.exists():
        n=2
        while (dest.parent/f'{dest.name}-{n}').exists():n+=1
        dest=dest.parent/f'{dest.name}-{n}'
    for sub in ['archives','nexus','reports']:(dest/sub).mkdir(parents=True)
    for z in zips:shutil.copy2(z,dest/'archives'/z.name);shutil.copy2(z.with_suffix('.zip.sha256'),dest/'archives'/(z.name+'.sha256'))
    for doc in sorted(NOTES.glob(VERSION+'_*.md'))+[NOTES/'README.md']:shutil.copy2(doc,dest/'nexus'/doc.name)
    # Nexus post: English first, then Russian.
    post=bbcode((NOTES/f'{VERSION}_POST_EN.md').read_text('utf8'))+'\n\n[line]\n\n'+bbcode((NOTES/f'{VERSION}_POST_RU.md').read_text('utf8'))
    post_chars=len((post+'\n').replace('\r\n','\n').replace('\n','\r\n'))
    if VERSION=='0.9.5':
        import sys
        sys.path.insert(0,str(ROOT/'tools/features095'))
        from nexus_posts095 import write_posts
        from nexus_description095 import write_description, FILENAME
        write_posts(NOTES,dest/'nexus',bbcode)
        write_description(NOTES,dest/'nexus/BBCode',bbcode)
        shutil.copy2(dest/'nexus/BBCode'/FILENAME,dest/'nexus'/FILENAME)
    (dest/f'nexus/NEXUS_POST_{VERSION}_EN_RU.bbcode.txt').write_text(post+'\n','utf8')
    for name in ['release-readiness.json','archive-verification.json','user-release-checks.json','save-safety-check/report.json','starter-recovery-check/report.json','profile-storage-check/report.json','profile-native-source-proof-complete.json','whale-check.json','editor-fx-source.json']:
        src=out/name
        if src.exists():shutil.copy2(src,dest/'reports'/name.replace('/','-'))
    gate=json.loads((out/'user-release-checks.json').read_text('utf8'))
    for row in gate['reports']:
        src=out/row['path'];assert src.resolve().is_relative_to(out)
        assert sha(src)==row['sha256'],row['path']
        shutil.copy2(src,dest/'reports'/row['path'].replace('/','-'))
    (dest/'CHECKLIST_RU.md').write_text(CHECKLIST,'utf8')
    lines=[f'# Gwent Beta Classic {VERSION} — файлы релиза','',f'Сборка: `{out}`','','## Архивы','']
    for z in zips:lines.append(f'- `archives/{z.name}` — {z.stat().st_size} байт, SHA-256 `{sha(z)}`')
    lines+=['','## Тексты для Nexus (13 языков)','',(f'Короткий пост EN/RU: `nexus/NEXUS_POST_{VERSION}_EN_RU.bbcode.txt`. Все изменения после 0.9.4 сохранены в подробном changelog.' if VERSION=='0.9.5' else f'Пост EN/RU: `nexus/NEXUS_POST_{VERSION}_EN_RU.bbcode.txt` ({post_chars} символов с CRLF).')+' Описание и changelog для каждого языка: `nexus/'+VERSION+'_*`.','',
      '## Отчёты','','`reports/`: готовность, независимая проверка архивов (SHA/CRC/manifest) и проверки хранения профиля.','',
      '## Перед публикацией','','Пройдите `CHECKLIST_RU.md` в игре на обеих версиях. Ничего не установлено и не опубликовано автоматически.','']
    (dest/'README_RU.md').write_text('\n'.join(lines),'utf8')
    if VERSION=='0.9.5':
        with (dest/'README_RU.md').open('a',encoding='utf8') as f:
            f.write('\nПолное описание главной Nexus: `nexus/'+FILENAME+'`. Английский открыт сверху, остальные 12 языков раскрываются отдельно.\n')
    print('Release files collected in',dest)
    return dest
if __name__=='__main__':main()
