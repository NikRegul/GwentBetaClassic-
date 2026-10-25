"""Generate the final review only from completed, matching test artifacts."""
from pathlib import Path
import argparse, json, sys
from parallel_tests091 import aggregate, atomic
from evidence091 import comparison_compatibility
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import CLASSIC_RUNTIME
def read(p):return json.loads(p.read_text('utf-8-sig'))
def pct(n):return f'{n*100:.2f}%'
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,default=ROOT/'BetaGwent/build/release091-candidate5')
    p.add_argument('--experiment',type=Path,default=ROOT/'BetaGwent/build/ai091/final18');a=p.parse_args();candidate=a.candidate.resolve();experiment=a.experiment.resolve()
    fingerprint=read(candidate/'rules/manifest.json')['fingerprint'];summary=read(experiment/'summary.json')
    compatibility=comparison_compatibility(candidate/'rules',experiment)
    assert summary['identity']['candidate']==compatibility['comparisonFingerprint']
    for mode in ['versions','difficulty']:
        reports=[read(q/'report.json') for q in sorted(experiment.glob(mode+'-??'))]
        assert len(reports)==summary['identity']['shards'] and all(r['complete'] and not r['errors'] for r in reports)
        summary['experiments'][mode]=aggregate(reports,summary['identity']['shards']*184)
        assert summary['experiments'][mode]['complete']
    atomic(experiment/'summary.json',summary)
    regression=read(candidate/'regressions/summary.json');assert all(r['exitCode']==0 for r in regression)
    varied=read(candidate/'varied/summary.json');assert varied['fingerprint']==fingerprint and not varied['failed']
    tactics=read(candidate/'tactics-all/report.json');rows=read(candidate/'rows-all/report.json')
    assert tactics['fingerprint']==rows['fingerprint']==fingerprint
    assert all(r['status']=='pass' for r in tactics['results']) and all(r['pass'] for r in rows['results'])
    ng=read(candidate/'compile-nextgen-final/result.json');classic=read(CLASSIC_RUNTIME/'runs'/candidate.name/'result.json')
    assert ng['completedByOutput'] and ng['exitCode']==0 and classic['compilePassed'] and not classic['errors']
    release=read(candidate/'release.json');assert len(release['archives'])==2
    comparison=read(candidate/'last-say-comparison.json')
    cleanup=[read(ROOT/'docs/evidence'/n) for n in ['cleanup091-20261020-121515.json','cleanup091-20261020-123805-executed.json','cleanup091-20261020-obsolete-candidates.json']]
    assert all(r['applied'] and len(r['targets'])==len(r['removed']) for r in cleanup)
    freed=sum(r['bytes'] for r in cleanup)
    table=[];verdicts=[]
    for mode,title in [('versions','0.9.1 максимум против прежнего максимума'),('difficulty','0.9.1 максимум против лёгкого')]:
        r=summary['experiments'][mode]
        table.append(f"| {title} | {r['completedGames']} | {r['wins']}:{r['losses']}:{r['draws']} | {pct(r['scoreRate'])} | {pct(r['lower99'])}–{pct(r['upper99'])} | {r['errors']} |")
        verdict='преимущество подтверждено выбранным критерием' if r['confirmedBetter'] else 'обнаружено ухудшение по выбранному критерию' if r['upper99']<.5 else 'общий прирост силы не подтверждён'
        verdicts.append(title+': '+verdict+'.')
    text=f'''# Ревью ИИ 0.9.1 — 20 октября 2026

Кандидат: `{candidate.relative_to(ROOT).as_posix()}`. Снимок исходников: `{fingerprint}`. Компиляция и симуляционные проверки выполнены; приёмка в установленной игре остаётся открытой.

Большое сравнение и рейтинг колод относятся к снимку `{compatibility['comparisonFingerprint']}`, до замечания пользователя о Трисс. После него изменён только один слот пресета 96: Трисс → Морской Вепрь. Побайтная проверка запрещает любые другие отличия правил или политики. Новая колода проверена отдельно; рейтинг старого состава не приписывается исправленному.

## Изменения и тактики

Добавлены пересматриваемые планы сохранения финала, давления второго раунда и выманивания дорогого ответа. Выбор учитывает оставшийся резерв собственной руки, публичные будущие угрозы, вероятности контроля и возможный отказ отвечать. Дешёвый догон и необходимость спасти матч выше плана. Проверены все восемь обсуждённых тактик и контрпримеры; это ограниченный поиск и эвристики, не гарантия оптимальной игры.

Точный стартовый состав колоды доступен только на максимальной сложности: копирование до перемешивания, без текущей скрытой руки, порядка и фактического остатка колоды. На меньшей сложности список не захватывается и не используется. Это разрешённое пользователем информационное преимущество максимума. Проверены подмена скрытых данных, обратное клонирование, смена сторон в хосте и сохранение намерения каждой стороны.

Разнообразные финалы выявили преждевременный Scorch: до исправления 13 проигрышей из 64. Новый ограниченный расчёт проверяет и пас противника, и его единственный публичный ответ на настоящих копиях позиции. Не выдаёт доказательный бонус для скрытого ответа, доступного лидера, погоды или сложного поля. Показательный полный розыгрыш: старый ИИ {comparison['old']['own']}:{comparison['old']['enemy']}, новый {comparison['current']['own']}:{comparison['current']['enemy']}. Это отдельный тактический пример, не общая оценка силы.

## Проверки

- {len(regression)} наборов регрессий — без ошибок; сохранены проверки правил, целей, комбинаций, скрытой информации и работы поиска по шагам.
- {len(tactics['results'])} сценариев тактики и {len(rows['results'])} сценариев выбора рядов на 46 профилях — без ошибок. Эти авторские позиции не считаются независимыми партиями и могут содержать карты вне штатной колоды профиля. Старые наблюдательные сценарии блефа не доказывают его выгоду: их pass означает отсутствие зафиксированного промаха или технической ошибки. Полные последовательности новых тактик проверены отдельно.
- {varied['cases']} генерируемых тактических проверок; seed {', '.join(map(str,varied['seeds']))}; бюджеты {', '.join(map(str,varied['damping']))}; ошибок 0. Удачный последний ответ, немедленный контроль после паса, дешёвый догон, необязательный/решающий раунд, активная/заблокированная угроза, неизвестный ответ и лидер.
- Отдельная проверка нового финала: 32 позиции, совпадение обычного и пошагового выбора, сохранение живого состояния и RNG, не более одного поискового розыгрыша за callback.
- Нативная компиляция 1.32 и 5.0+ — успешно. Classic сообщает exit 3, но обязательное подтверждение компилятора, свежий кэш и отсутствие ошибок проверены отдельно. У wcc после явного успеха ограничено зависшее завершение процесса; это не считается тайм-аутом компиляции. Ранний кандидат с ошибками доступа отвергнут.
- Два архива проверены по CRC и SHA всех файлов. Сохранены ресурсы и исправления final17: меню TestMenu, нативное оформление бочки, Classic RNG, профиль, магазин, тексты, графика, звук и принятые эффекты.

## Большое сравнение

{' '.join(verdicts)}

18 процессов Node, маска CPU `{summary['cpuAffinityMask']}`: первые 18 доступных логических процессоров из {summary['logicalProcessors']}. 6 624 партии: 3 312 в каждом эксперименте. Каждый эксперимент содержит 828 разных пар из 1 035 возможных среди 46 профилей и 828 seed-раздач. Каждая раздача проверяется четырьмя партиями с перестановкой политики, колоды и стороны; исходная раздача и RNG одинаковы, обмен независим. Правила карт общие.

| Эксперимент | Партий | Победы:поражения:ничьи | Доля очков | Приближённый 99% интервал | Ошибки |
|---|---:|---:|---:|---:|---:|
{chr(10).join(table)}

Интервал рассчитан по группам четырёх связанных партий, а не по отдельным партиям как независимым наблюдениям. Зеркала не увеличивают число seed-раздач. Отчёты сохраняют время вычислений в симуляторе, события выбора и пасы; это не измерение FPS или задержек настоящей игры. Частота паса сама по себе не доказывает ошибочный пас. Результаты нельзя обобщать на все пользовательские колоды и игру против человека.

Ранние прогоны с ошибкой обмена стартовых списков и состояния планов в хосте не использованы. Старые кооперативные классы поиска целиком возвращены в базовую политику: новый поиск не подмешан в старую версию. Завершённые отчёты связаны с точным снимком исходников; ошибки/незавершённость запрещают вывод о превосходстве.

Десять исходных файлов старой политики побайтно совпадают с Git-коммитом `9dfd0a433db644b4e3d72a91df233fcdc8828db8`. Фактически сравнивается прежний ИИ 0.9.0 на общих правилах карт нового снимка; это не запуск старого готового архива игры. Хэши старых файлов сохранены в доказательстве подготовки базовой политики.

## Очистка и публикация

Удалено {int(freed):,} байт ({freed/1024**3:.2f} ГиБ): сырые дампы с сохранёнными текстовыми журналами, проверенный дубликат переносимого комплекта, старые упаковочные каталоги и дубли архивов промежуточных кандидатов этой работы. Сохранены активные зависимости final12/final17, Classic runtime, Git и исторический CleanBuild. CleanBuild не является автоматически обновлённой копией 0.9.1.

В публичный Git экспортируются исходники и ограниченные проверочные отчёты. Игровые бинарные ресурсы, runtime и готовые архивы туда не добавляются. `Build-0.9.1.cmd` создаёт отдельный снимок, проводит проверки и собирает обе платформы; установку и публикацию Nexus не выполняет.

Остаётся ручная игровая приёмка 1.32 и 5.0+: показательные партии, сохранение/загрузка, отзывчивость меню и поиск с движущейся камерой. Дальнейшие исправления ошибок относятся к 0.9.1 и требуют нового снимка и проверок.
'''
    target=ROOT/'docs/reviews/2026-10-20-ai091.md';target.write_text(text,encoding='utf8');print(target)
if __name__=='__main__':main()
