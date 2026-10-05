"""Record stage90 compilation/presentation evidence and the post-release plan."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
proof=dict(stage=90,nativeRuntimeVerified=False,installedGameModified=False,firstReleaseUnmodified=True,compilation={},menus=[])
for language in ('ru','en'):
    path=ROOT/f'BetaGwent/build/board-compile90{language}'
    r=json.loads((path/'result.json').read_text('utf8'));log=(path/'stdout.txt').read_text('utf8',errors='replace')
    assert r['exitCode']==0 and not r['timedOut'] and r['patchSourcesUnchangedDuringCompile']
    assert len(r['patchSourcesBefore'])==60 and 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
    source=ROOT/('BetaGwent/build/board-patch' if language=='ru' else 'BetaGwent/build/stage90/en/en-source/scripts')
    for f in r['patchSourcesBefore']:assert hashlib.sha256((source/f['path']).read_bytes()).hexdigest()==f['sha256']
    proof['compilation'][language]=dict(passed=True,sources=60,blobSha256=hashlib.sha256((path/'compiled/blob.rsblob').read_bytes()).hexdigest())
for entry in ('BetaGwentBoard','GwintGame','DeckBuilder'):
    suffix='' if entry=='BetaGwentBoard' else '-'+entry
    for base in ('board-build','board-bridge-bytecode','board-resource-update'):
        name=base+suffix+'.json';shutil.copyfile(ROOT/'docs/evidence'/name,ROOT/'docs/evidence'/('stage90-'+name))
    bridge=json.loads((ROOT/'docs/evidence'/('board-bridge-bytecode'+suffix+'.json')).read_text('utf8'))
    resource=json.loads((ROOT/'docs/evidence'/('board-resource-update'+suffix+'.json')).read_text('utf8'))
    assert bridge['passed'] and len(bridge['bindings'])==44 and resource['nativeABCMatchesBuiltSWF'] and resource['headerTableChunkChecksumsVerified']
    assert hashlib.sha256(Path(resource['target']).read_bytes()).hexdigest()==resource['updatedSha256']
    proof['menus'].append(dict(entry=entry,language='ru',bridgeVerified=True,nativeResourceVerified=True,sha256=resource['updatedSha256']))
for language in ('ru','en'):
    frozen=json.loads((ROOT/f'docs/evidence/stage89-release-{language}.json').read_text('utf8'))
    assert hashlib.sha256(Path(frozen['archive']).read_bytes()).hexdigest()==frozen['archiveSha256']
(ROOT/'docs/evidence/stage90-completion.json').write_text(json.dumps(proof,indent=2)+'\n','utf8')
header='''## Текущий шаг — 90: ИИ и анимации после первого релиза

Пользователь сообщил о публикации первого релиза. План проверок и дальнейшей
разработки: [AI_ANIMATIONS_PLAN90.md](AI_ANIMATIONS_PLAN90.md).
Первый проход отделяет немедленный темп от стратегических прогнозов;
будущий урон/полезность движка не становятся очками догоняния.
Рассвет после паса сравнивает непосредственную очистку и консервативный
призыв. Импера по открытым шпионам остаётся реальным усилением.
Короткий поиск комбинаций и защита от повторного учёта общих целей ещё впереди.

Улучшены масштаб/поворот полёта, приземление, след удара и счёт при попадании.
Добавлены минимальные времена показа смерти, призыва, завещания и других фаз.
RU/EN: 60 WS нативно скомпилированы. RU: три меню/44 связи проверены,
ресурсы обновлены в REDkit-проекте. EN-исходники подготовлены, EN-меню
ещё не пересобраны. Игровое качество изменений пока не принято.

Опубликованные ZIP 0.2.0 не менялись; новая установка в обычную игру
и новая публикация не выполнялись. После DEV-набора общего паса/темпа
готовим одну проверочную сборку; затем сначала принимаем Погоду.
Декомпиляция локального клиента разрешена пользователем; извлечение
сериализованных визуальных ресурсов и их адаптация под GFx — следующий этап.

'''
p=ROOT/'docs/plan.md';s=p.read_text('utf8')
if '## Текущий шаг — 90:' not in s:
    i=s.index('## Текущий шаг');s=s[:i]+header+'## Предыдущие этапы\n\n'+s[i:]
p.write_text(s,'utf8')
p=ROOT/'docs/progress.md';s=p.read_text('utf8')
if '2026-10-05 — 90:' not in s:s+='\n## 2026-10-05 — 90: следующий этап после релиза\n\n'+header.split('\n\n',1)[1]
p.write_text(s,'utf8')
print(json.dumps(proof))
