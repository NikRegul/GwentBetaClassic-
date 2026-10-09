# Инвентаризация источников

## Реальные пути и авторитетность

| Источник | Путь | Что найдено / статус |
|---|---|---|
| Рабочая папка | `D:\w3mod` | Каталог источников и документации; .git на верхнем уровне не найдено |
| DIY | `D:\w3mod\LegacyGwent-diy(1)\LegacyGwent-diy` | C# server/common/AI, Unity, локализации, эффекты, тестовые консоли |
| Оригинальный клиент | `D:\w3mod\Gwent 0.9.24.3.432` | Unity/Mono, managed DLL, bundles, data_definitions; MelonLoader и мод уже установлены |
| Неофициальный сервер | `D:\w3mod\Unofficial-Gwent-Beta-0.9.24.3.432-Private-Server-main` | Python HTTP backend, broker, relay, nginx, launcher, Harmony/MelonLoader patch |
| Данные Beta | `D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data\StreamingAssets\data_definitions` | ZIP без расширения; 21 файл; Info содержит 432 и 431 |
| Локализация Beta | В том же ZIP: `Localization/ru_ru.csv`, `en_us.csv` и ещё 11 | 2231 ключ в каждом языке; названия всех 698 Template IDs присутствуют |
| Русские bundles Beta | `...\StreamingAssets\AssetBundles\Localization\ru-ru\text.ru-ru` | Отдельные bundles текстов и flowcharts; бинарные assets не распаковывались |
| Тирлист | `D:\w3mod\Gwent-09-2025-Tierlist 6.0.pdf` | 27 страниц, DIY 2025 Q3; 46 подробных статей и 46 извлечённых сырых deck codes |
| TW3 | `F:\Steam\steamapps\common\The Witcher 3` | Доступны текстовые scripts в content/content0/scripts |
| REDkit | `D:\GOG Galaxy\Games\The Witcher 3 REDkit` | Установлен, editor 5.0.0.1042178; .download=0; scripts/AS/SWF/XML проверены, см. redkit_status.md |
| User depot | `D:\w3mod\depot` | Пользователь подтвердил готовность; depot_info.json version1.6, 41306 records |
| Mod project | `D:\w3mod\GwentB\myproject1\myproject1.w3edit` | Создан пользователем; workspace/scripts содержит компилируемый capability probe |
| Версия 1.0.1.26 | `D:\w3mod\Gwent-1.0.1.26-Russian-GOG` | Частичные ресурсы/сравнения; исключены из canonical Beta rules |
| Резервные голоса | `D:\w3mod\Gwent-0.9.24.3.432-Russian-Voice-Backups` | Существующий каталог; резервные копии не являются источником правил |

Исходники официального сервера CDPR не найдены. Слово Private-Server в имени папки не доказывает их наличие. REDkit создал вложенный проект MyProject1 в GwentB; metadata не переименовывалась. useLooseScripts=false. excludedDlc содержит стандартные имена: это настройки упаковки DLC/mod, не доказательство отключения DLC encounters.

Порядок источников: original client/data → original localization → DIY как reference. Пользователь подтвердил: PDF только для идей архетипов, без переноса DIY-баланса.

## Снимок данных

Подтверждено разбором XML и metadata:

- 698 уникальных Template IDs, дубликатов нет.
- 480 записей Availability=BaseSet и 218 NonOwnable. Это сырые записи, не доказанное число уникальных коллекционных карт.
- Tier: 253 Bronze, 178 Silver, 161 Gold, 28 Leader, 78 с нулевым Tier.
- 567 Ability records: 554 CardAbility и 13 LocationTokenAbility.
- Все CardAbility.Template ссылаются на существующие Templates.
- 183 различных типа узлов в Nodes; 70 записей Categories.
- 13 языков, 2231 уникальный ключ на язык; проверено наличие names, но не полнота descriptions/tooltip dependencies.
- 943 верхнеуровневых типа namespaces GwentGameplay* в DLL; сохранены metadata и 8253 строки IL выбранных классов.

Число «около 900 карт» из ТЗ не подтверждается как 900 уникальных collectible definitions этого ZIP. Нужна классификация tokens, variants, leaders, service templates и premium; не расширять пул ради заданного числа.

## Доказательства и воспроизводимость

Все результаты в `D:\w3mod\docs\evidence`:

- beta-archive.json: entries, размеры и SHA256 каждого содержимого.
- beta-data-summary.json: counts, references, localization coverage.
- beta-template-manifest.csv: все 698 записей с IDs, power, tier, art и names.
- beta-assembly-summary.json: SHA256 Assembly-CSharp.dll.
- beta-enums.json / beta-types.json / beta-core-il.txt: прочитанные metadata/IL.
- diy-audit.json / diy-to-beta-candidates.json: кандидаты связей, не подтверждённый mapping.
- tierlist-catalog.json / tierlist-extracted.txt: страницы, имена, raw codes, происхождение.

Скрипты: `D:\w3mod\tools\recon\audit_sources.py`, `inspect_beta_assembly.ps1`, `inspect_tierlist.py`, `inspect_redkit.py`, `inspect_beta_defaults.ps1`. Они читают источники, пишут evidence. Generated evidence не редактировать вручную; менять скрипт и повторять анализ. REDkit audit добавляет scripts hashes/diff, AS symbols, SWF roots, XML/decks/rewards, FLA reader result и quest candidates; defaults audit — IL/settings field writers.

## Окружение

DIY csproj: Server netcoreapp3.0, Common netstandard2.0; README говорит .NET Core 3.1. Фактический csproj имеет приоритет. Unity README: 2019.4.1f1; установленный Unity редактор не проверялся. Mongo в docker-compose: 4.2.24-rc0, server 5005.

Доступны dotnet SDK 5.0.415 и 7.0.101; старые runtime/NuGet dependencies и возможность сборки не проверены. Анализ не запускал серверы и не менял сетевые настройки.

В TW3 найден bin/x64_dx12/witcher3.exe с FileVersion `5.0.0.1044392(Build Machine)`; это строка файла, не подтверждение маркетинговой версии игры. Есть конфигурация modGwentReduxConfig.xml, но наличие активного Gwent Redux по ней не установлено. Перед интеграцией проверить scripts.sha256/моды/версию и исходную чистоту scripts.
