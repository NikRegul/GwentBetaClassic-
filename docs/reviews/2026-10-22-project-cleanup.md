# Очистка проекта — 22 октября 2026

Очистка выполнена по прямому указанию пользователя. Удалены все 24 согласованные цели: 729 файлов, 40,823 ГиБ логически. Свободное место на D: увеличилось на 40,823 ГиБ. Перед удалением проверены размеры, отсутствие отслеживаемых Git файлов и reparse points в целях и их родительских путях.

Текущий выпуск, последняя резервная копия установки и перечисленные ниже входы сборки сохранены. Контрольные SHA-256 файлов release.json и указателей latest не изменились. Журнал выполнения: `docs/reviews/2026-10-22-project-cleanup-executed.json`. Python-кэши в эту очистку не включены.

Команда `py -3 -X utf8 tools/features092/build092.py --check-only` успешно прошла до и после удаления. Она проверяет наличие входов, а не выполняет полную пересборку или игровую проверку.

Полный обход без перехода по reparse points: 947,34 ГиБ логических размеров, в том числе BetaGwent/build — 792,41 ГиБ. Ошибок чтения нет. Жёсткие ссылки не дедуплицированы; фактически освобождённое место может отличаться. Инвентарь: `tmp/project-cleanup-inventory-20261022.json`.

## Выполненная очистка

1. **13,32 ГиБ — два дампа падений**, если больше не нужен анализ этих состояний:
   - `data/witcher3.DMP`
   - `data/witcher3 (2).DMP`
2. **15,70 ГиБ — только подкаталоги archives** следующих прежних сборок. Удаление убирает соответствующие ZIP для установки/отката; исходники и отчёты следует сохранить:
   - `BetaGwent/build/release091-candidate4/archives`
   - `BetaGwent/build/release091-candidate5/archives`
   - `BetaGwent/build/release091-candidate6/archives`
   - `BetaGwent/build/release091-candidate7/archives`
   - `BetaGwent/build/release091-candidate8/archives`
   - `BetaGwent/build/release091-candidate9/archives`
   - `BetaGwent/build/release091-candidate11/archives`
   - `BetaGwent/build/release091-candidate12/archives`
   - `BetaGwent/build/release091a/archives`
   - `BetaGwent/build/release091b/archives`
   - `BetaGwent/build/release091d/archives`
   - `BetaGwent/build/release091e/archives`
   - `BetaGwent/build/release091f/archives`
3. **11,81 ГиБ — прежние резервные копии**, только если эти точки отката больше не нужны:
   - `tmp/install091-backup-20261020-172320`
   - `tmp/install091-backup-20261020-172354`
   - `tmp/install091-backup-20261020-190945`
   - `tmp/install091-backup-20261020-194053`
   - `tmp/release-0.9.0-before-final11`
   - `tmp/release-0.9.0-before-final12`
   - `tmp/release-0.9.0-before-final13`
   - `tmp/release-0.9.0-before-final16`
   - `tmp/release-0.9.0-before-final17`

Итого по трём группам — около **40,82 ГиБ** логически. Дополнительно Python __pycache__ занимает 58,68 МиБ; он пересоздаётся. Логи автоматически не включены: они могут быть доказательствами диагностики.

## Сохранять

- Текущий выпуск `BetaGwent/build/release092-final1` и предыдущий проверенный `release091i-final2`.
- Последнюю резервную копию установки `tmp/install092-backup-20261022-002532-418573` (1,78 ГиБ).
- Входы текущих инструментов: `release091h-final2`, `release091-ui4`, `classic-audio091-split1`, `release090-final12`, `release090-final17-release/package-candidate/archives-optional-keep`, `universal081` внутри BetaGwent/build. Это минимальный подтверждённый перечень зависимостей, не полный список всех нужных каталогов.
- Исходники, depot, оригинальные игровые ресурсы, Wwise-проекты, языковые ресурсы, CleanBuild и его архив, .git.
- Игровые texture.cache и sound.cache нельзя считать обычными временными кэшами по расширению.

Полностью удалять build, tmp или ui/build на основании имени нельзя. Крупные исторические каталоги (например history137 — 22,59 ГиБ, recovery-282e70b6ecd0 — 39,84 ГиБ) требуют отдельной проверки зависимостей и ссылок перед удалением. Перед применением перечня проверить актуальность, активные сборки и границы путей; удаление каталогов со ссылками требует обработки самих ссылок без обхода их целей.
