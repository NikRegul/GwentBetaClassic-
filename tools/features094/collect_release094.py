"""Gather everything needed to publish 0.9.4 into one folder (copies only, nothing deleted).

Usage: python -X utf8 tools/features094/collect_release094.py <build-folder> [--dest release\\0.9.4]
Accepts only a finished build: release-readiness.json + archive-verification.json + matching SHA-256.
"""
from pathlib import Path
import argparse,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
NOTES=ROOT/'docs/releases/0.9.4-public-20261026'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CHECKLIST='''# 0.9.4 — что проверить в игре перед публикацией

Автоматические проверки и обе нативные компиляции пройдены сборкой. Ниже то, что можно подтвердить только в игре.
Отметьте пункты на Next-Gen 5.0+ и на Classic 1.32. Работайте на копиях сохранений.

## Хранилище профиля (главное в 0.9.4)
- [ ] Перенос: загрузить сейв, сделанный в 0.9.3. В scriptslog есть `PROFILE_STORE_EMPTY`, коллекция, колоды, осколки и бочки на месте.
- [ ] Сделать ручное сохранение, полностью выйти из игры, запустить, загрузить его. В логе `PROFILE_STORE_LOADED`, всё на месте.
- [ ] Создать новую колоду, переименовать, сохранить игру → выйти → загрузить. Колода и имя на месте.
- [ ] Изменить осколки (скрафтить карту) и бочки (купить, открыть, оставить выбор незавершённым) → сохранить → выйти → загрузить. Значения и незавершённый выбор сохранились.
- [ ] Изменить сложность, паузу ИИ, темп анимаций → сохранить → выйти → загрузить.
- [ ] Выиграть у NPC с наградой → автосохранение/ручное → загрузить: награда и счётчик наград NPC сохранились.
- [ ] Next-Gen вместе с несколькими другими скриптовыми модами (если есть): тот же цикл сохранить → выйти → загрузить.
- [ ] В логе нет `PROFILE_STORE_REJECTED`.

## Пакет
- [ ] Установка из архива 5.0+ и 1.32 на чистую копию; игра запускается, меню открываются.
- [ ] Папка с необязательными файлами копирования колоды (dinput8.dll + ASI) лежит отдельно; без неё кнопки импорта/экспорта скрыты.
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
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--dest',type=Path,default=ROOT/'release/0.9.4');a=p.parse_args(argv)
    out=a.build.resolve();dest=a.dest.resolve()
    ready=json.loads((out/'release-readiness.json').read_text('utf8'));assert ready['status']=='ready' and ready['version']=='0.9.4'
    json.loads((out/'archive-verification.json').read_text('utf8'))
    zips=sorted((out/'archives').glob('GwentBetaClassic-0.9.4-*-AllLanguages.zip'));assert len(zips)==2,zips
    for z in zips:
        digest=(z.with_suffix('.zip.sha256')).read_text('ascii').split()[0];assert sha(z)==digest,z
    if dest.exists():
        n=2
        while (dest.parent/f'{dest.name}-{n}').exists():n+=1
        dest=dest.parent/f'{dest.name}-{n}'
    for sub in ['archives','nexus','reports']:(dest/sub).mkdir(parents=True)
    for z in zips:shutil.copy2(z,dest/'archives'/z.name);shutil.copy2(z.with_suffix('.zip.sha256'),dest/'archives'/(z.name+'.sha256'))
    for doc in sorted(NOTES.glob('0.9.4_*.md'))+[NOTES/'README.md']:shutil.copy2(doc,dest/'nexus'/doc.name)
    # Nexus post: English first, then Russian.
    post=bbcode((NOTES/'0.9.4_POST_EN.md').read_text('utf8'))+'\n\n[line]\n\n'+bbcode((NOTES/'0.9.4_POST_RU.md').read_text('utf8'))
    (dest/'nexus/NEXUS_POST_0.9.4_EN_RU.bbcode.txt').write_text(post+'\n','utf8')
    for name in ['release-readiness.json','archive-verification.json','user-release-checks.json','save-safety-check/report.json','starter-recovery-check/report.json','profile-storage-check/report.json','profile-native-source-proof-complete.json']:
        src=out/name
        if src.exists():shutil.copy2(src,dest/'reports'/name.replace('/','-'))
    gate=json.loads((out/'user-release-checks.json').read_text('utf8'))
    for row in gate['reports']:
        src=out/row['path'];assert src.resolve().is_relative_to(out)
        assert sha(src)==row['sha256'],row['path']
        shutil.copy2(src,dest/'reports'/row['path'].replace('/','-'))
    (dest/'CHECKLIST_RU.md').write_text(CHECKLIST,'utf8')
    lines=['# Gwent Beta Classic 0.9.4 — файлы релиза','',f'Сборка: `{out}`','','## Архивы','']
    for z in zips:lines.append(f'- `archives/{z.name}` — {z.stat().st_size} байт, SHA-256 `{sha(z)}`')
    lines+=['','## Тексты для Nexus (13 языков)','',f'Пост EN/RU: `nexus/NEXUS_POST_0.9.4_EN_RU.bbcode.txt` ({len(post)} символов). Описание и changelog для каждого языка: `nexus/0.9.4_*`.','',
      '## Отчёты','','`reports/`: готовность, независимая проверка архивов (SHA/CRC/manifest) и проверки хранения профиля.','',
      '## Перед публикацией','','Пройдите `CHECKLIST_RU.md` в игре на обеих версиях. Ничего не установлено и не опубликовано автоматически.','']
    (dest/'README_RU.md').write_text('\n'.join(lines),'utf8')
    print('Release files collected in',dest)
    return dest
if __name__=='__main__':main()
