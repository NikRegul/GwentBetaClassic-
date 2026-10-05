# Как собрать Gwent Beta Classic

Сначала прочитайте README и ARCHITECTURE_AI_RU.md. Публикуются авторские
WitcherScript/ActionScript, генераторы, данные составов и инструкции. Оригинальные
клиенты игр, depot, изображения, PCM, банки, SDK и Wwise-ключ в Git не входят.
Готовые пакеты нужны игрокам; исходники — разработчикам.

## Среда

Windows, Python 3.13, Java, REDkit 5.0.1044630 с подготовленным depot и принятыми
человеком условиями Wcc; Apache Royale 0.9.12 и playerglobal 0.9.12 для AS3;
Scaleform exporter из REDkit. Для изменения звука — Wwise 2023.1.19.8928 с
подходящей лицензией, UnityPy, vgmstream-r2117 и wwiser. Для атласа — Pillow.
Python должен работать с UTF-8 (`$env:PYTHONIOENCODING='utf-8'` в PowerShell).

Локальная подтверждённая структура: корень D:\w3mod; REDkit
D:\GOG Galaxy\Games\The Witcher 3 REDkit; depot D:\w3mod\depot;
проект GwentB\myproject1. Ряд старых recon/UI-утилит ещё содержит эти абсолютные
пути: при другой установке поправьте константы ROOT/ORIGINAL/STREAM/EXPORTER
и пути SDK в board-config.xml. Полностью переносимый setup — отдельная задача.

Базовые ресурсы меню созданы в REDkit и сохранены на диск; утилиты меняют
содержимое существующего CR2W/redswf и проверяют его структуру. Из одного AS3
без этих шаблонов нативный ресурс не создаётся. Новый разработчик должен
подготовить такой же проект или взять resource bootstrap из готового пакета
через Wcc unbundle. Текущий release-builder использует замороженный проект87
как шаблон: BetaGwent/build/release87/project/BetaGwent0924. Эта папка не в Git.
Это реальное требование сборки, а не автоматически загружаемая зависимость.

## Источники

- BetaGwent/scripts/game/betagwent: общие типы, фильтры и правила.
- BetaGwent/development/scripts/game/betagwent: полноценная игра, ИИ,
  коллекция, NPC/магазины, редактор и связь с меню. Название development
  историческое: эти файлы входят в релиз.
- BetaGwent/ui/src: AS3-поле, редактор, контроллер, описание и каталог.
- data/beta924/duel: точные ID, эффекты и составы; design: экономика/NPC;
  ai/rules.json: импортированный отчёт по архетипам.
- tools: генераторы/сборка; docs: решения и инструкции.

Нужен исходный нормализованный catalog.json строгой 0.9.24. Генераторы проверяют
его SHA256: 022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3.
Нельзя молча заменить на актуальный DIY: там другие способности и баланс.
Исходные Beta definitions/локализация и DIY-арты — локальные внешние входы.

## Последовательность генерации

Из корня репозитория:

```powershell
python tools/build_progression.py
python tools/build_full_catalog.py
python tools/build_ai_rules.py
python tools/build_duel_catalog.py
python tools/build_full_catalog.py
python tools/build_shop_cards.py
```

Progression создаёт стартовые/квестовые составы и сохраняет хвост ИИ. Затем
build_ai_rules адаптирует deck_rules.txt и генерирует таблицы ИИ/составы54–93;
duel_catalog пересобирает определения и весь список составов. Full_catalog
собирает описания, теги и источники; повтор нужен после смены состава/артов.
Не редактируйте генерируемые duelCatalog/duelAICatalog/CardText вручную.
Новые карточные обработчики меняются в соответствующих WS-файлах фракций.

Перед компиляцией скопируйте общий и development набор в
BetaGwent/build/board-patch/game/betagwent, затем coreChecks.ws из
tools/core-check/src. Всего в текущей сборке 60 WS. Тот же набор положите
в GwentB/myproject1/workspace/scripts/game/betagwent. Разные копии одного
источника нельзя смешивать при сборке.

```powershell
python tools/recon/run_redkit_compile.py --out BetaGwent/build/board-compile89a --patch BetaGwent/build/board-patch --timeout 120 --terms-already-accepted
python tools/ui/build_menu_pack.py --apply
```

Каждый compile-out должен быть новым: утилита отвергает уже существующий blob.
Ключ terms применяется только после личного принятия условий Wcc.
Успех: сообщение Success! Patch scripts blob saved, отсутствие Script Error,
совпадение хешей входов до/после. Меню собирается как SWF → GFx/DDS → нативный
redswf. Проверяется реальный ABC, receiver вызова и все44 связи; затем
устанавливаются три ресурса: practice, DeckBuilder, GwintGame. Папка build
содержит промежуточные результаты и не публикуется в Git.

## Звук и языки

```powershell
python tools/recon/extract_beta_audio.py --decode-voices
python tools/ui/prepare_audio_import.py --full
python tools/ui/build_audio_bank.py --console "C:\Audiokinetic\Wwise_2023.1.19.8928\images\Authoring\x64\Release\bin\WwiseConsole.exe" --install
python tools/prepare_english89.py
python tools/merge_english89.py
python tools/localization89.py sources
python tools/ui/build_english_audio89.py
```

Источники звука — локальная Beta, AudioId/CardAudio.xml определяет связи.
Не подменять Init.bnk. Оригинальные банки версии128 не грузятся в TW3:
записи извлекаются и собираются новым Wwise в отдельный BetaGwent79.
Ключ лицензии сохраняется локально и не публикуется. EN использует те же
event names, но английские PCM и длительности; FX общие по происхождению.

english89.json — таблица перевода собственных строк. Канонические тексты,
имена, теги и glossary берутся из en_us. Indexed.txt — первоначальная партия
перевода, привязанная к сохранённому translation-index.json; для новых строк
редактируйте английский JSON напрямую. Не заменяйте буквенные подстроки
в описаниях: переводятся целые строковые литералы.

## Упаковка текущей версии

После готового русского UI:

```powershell
python tools/build_language_release.py prepare --language ru
python tools/prepare_en_ui89.py
```

prepare_en_ui89 компилирует английский набор, собирает три EN-меню, замораживает
EN-проект и восстанавливает RU-ресурсы рабочего проекта. Выполнить после
RU prepare, поскольку восстановление берётся из его замороженной копии.
Если шаг уже выполнен, не запускать prepare повторно поверх существующего frozen.

Для каждого языка ru и en по порядку:

```powershell
python tools/build_language_release.py cook --language ru
python tools/build_language_release.py strings --language ru
python tools/build_language_release.py audio --language ru
python tools/build_language_release.py dependencies --language ru
python tools/build_language_release.py pack --language ru
python tools/build_language_release.py metadata --language ru
python tools/build_language_release.py archive --language ru
```

Для EN заменить ru на en. Cook обрабатывает 8 нативных ресурсов; XML/CSV
копируются отдельно. Strings создаёт 396 предметных строк для языковых слотов;
в каждом фиксированном пакете EN/RU слоты несут выбранный язык. Audio создаёт
soundspc.cache и проверяет встроенные байты банка. Dependencies строит dep.cache;
Pack — LZ4HC bundle; Metadata — metadata.store; Archive добавляет правильный
precompiled.rsblob, документацию, manifest и SHA256, проверяет CRC/хеши файлов.
Выход: BetaGwent/release/GwentBetaClassic-0.2.0-RU.zip и EN.zip.

После изменения версии/compile-dir поправьте VERSION и имена compile в
build_language_release.py; не смешивайте новый UI со старым blob. Уже
замороженные входы не перезаписывайте: используйте новый stage-каталог.

## Разумная проверка перед публикацией

Обязательны нативная компиляция и целостность пакета. Для ИИ можно запустить
tools/core-check/check_ai_rules.py и check_pass_policy.py. Затем одна обычная
установленная партия, обязательный выбор, управление контроллером, сохранение/
полная перезагрузка. Сборка не подтверждает прохождение квестов или всех
комбинаций карт. Исходники не требуют постоянного запуска большого набора тестов.


0.2.1 / stage94: see [BUILD_POLISH94.md](BUILD_POLISH94.md), [Russian changes](PRESENTATION94_RU.md) and [English changes](PRESENTATION94_EN.md).
