**Gwent Beta Classic 0.9.0**

**English**

**Classic 1.32 and Next-Gen**
Choose one archive for your game version. Each contains all 13 text languages and all five voice languages: EN, RU, DE, IT and PT-BR. Text and voices can be selected independently in the mod menu; Auto follows the game's settings, with English as fallback. Works on Steam Deck as well (tested by the author).

For Next-Gen, replace the previous modBetaGwent0924 folder and copy Mods into the game directory. Optionally copy bin from Optional-CopyButton for the Copy button. For Classic 1.32, install BOTH Mods and DLC. Its DLC/dlcBetaGwentClassic132Assets + DLC/dlcBetaGwentClassic132Items folder is required for graphics and leader entrances. Classic is larger because the old loader needs a different resource layout; the cards and AI are the same.

**AI improvements**
Revised Igni and Yrden choices, Birna's weather forecast, armour breaks and the three Redanian armour abilities. Catch-up after a pass now follows real plays and turn boundaries. The AI can concede round one to preserve resources, but gives survival priority when another lost round would end the match. Automated scenarios cover all 46 opponent deck archetypes; unusual decisions are still worth reporting.

Isengrim: Outlaw now compares the actual special-card and Create branches, including when pulled by Royal Decree. The AI rejects Decoy without a legal allied Bronze or Silver target and estimates Create from its random three-card offer, without reading future random choices.

**Deck sharing and interface**
Import and Export use BG1 text codes. Missing cards appear as cards you can craft one by one or all at once; import unlocks when nothing is missing. Import creates a draft: save the deck afterward. Added console commands, improved translated buttons, editor spacing and controller navigation, and revised graveyard flights and leader animation timing.

Copy now puts the BG1 code straight into the Windows clipboard. Optional: copy the bin folder from Optional-CopyButton into the game directory (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe); the mod works without it; if another mod already has a dinput8.dll, keep it and load the ASI with that mod's loader. Without these files the Import and Export buttons are hidden.

**Card view and tutorial**
The full card view now follows Beta: a large card with the original Beta 0.9.24 faction banner, base power in white, readable flavour text and highlighted keywords. Deck screens use the same banner. The tutorial has 10 pages, including mulligan and draws, rows and neighbours, and card statuses. A deck code can also be pasted from the Windows clipboard (Paste or Ctrl+V; requires Optional-CopyButton).

**Card fixes**
Myrgtabrakke now deals 2 damage three times and Harald the Cripple's ability hits ten times, matching the Beta 0.9.24 card data.

**Installing after Redux**
Legacy item definitions are included: 203 missing names are recognized without replacing 197 native definitions, for normal games and NG+. This helps load old inventory after switching mods. It does not recover inventory already lost and saved or convert Redux cards into the Beta collection. Use a backup from before any loss. Remove the obsolete modBetaGwentReduxCompat folder and update Script Merger merges.

**Built-in cleanup**
No separate cleaner mod is needed. Back up your save; finish Gwent, leave combat and close menus. bg_clean_preview() shows instructions. To erase the Beta profile, run:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Save to a NEW slot, exit, remove this mod's folders, update affected script merges, load the new slot and save again. The uninstall flag blocks profile restoration while the mod is still installed. Cleanup does not undo quests, achievements or spent crowns, and does not traverse unloaded merchants or world containers. Read BetaGwentDocs/CLEANUP_EN.md first.

**What's next**
Until 1.0, the focus will be translation corrections, bug fixes and further AI and interface refinement.

**Found a problem? Please post it here.**
Bug reports, logs and translation suggestions are welcome. Include mod and exact game versions, text and voice languages, other mods, involved cards and steps to reproduce. A screenshot and a save from before the issue help.

**How to enable the log**

1. Add **-debugscripts** to the game's launch options. In Steam: Properties → General → Launch Options.
2. Start the game and reproduce the issue, then close it.
3. Copy the log before another launch overwrites it:

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

4. If Windows created a crash dump, attach the latest relevant .dmp from:

```text
%LOCALAPPDATA%\CrashDumps
```


**Русский**

**Classic 1.32 и Next-Gen**
Выбирайте один архив под свою версию игры. В каждом — все 13 языков текста и пять озвучек: EN, RU, DE, IT и PT-BR. Текст и голоса выбираются независимо в меню мода; «Авто» следует настройкам игры, при отсутствии языка используется английский. Мод работает и на Steam Deck (проверено автором).

Для Next-Gen замените прежнюю папку modBetaGwent0924 и скопируйте Mods в каталог игры. По желанию скопируйте bin из Optional-CopyButton — для кнопки «Копировать». Для Classic 1.32 нужны ОБЕ папки — Mods и DLC. DLC/dlcBetaGwentClassic132Assets + DLC/dlcBetaGwentClassic132Items содержит обязательную графику и вступления лидеров. Classic весит больше из-за другого формата ресурсов и ограничений старого загрузчика; карты и ИИ в обеих сборках одинаковые.

**Улучшения ИИ**
Переработаны выбор Игни и Ирдена, прогноз погоды Бирны, снятие брони и три реданские способности. Догон после паса учитывает реальные розыгрыши и границы ходов. ИИ может отдать первый раунд ради сохранения ресурсов, но при угрозе поражения в матче важнее выиграть раунд. Автоматические сценарии охватывают все 46 архетипов соперников; о странных решениях по-прежнему стоит сообщать.

Изенгрим: Изгой сравнивает реальную ценность веток особой карты и создания эльфа, в том числе после Королевского указа. ИИ не выбирает Чучело без допустимого союзного бронзового или серебряного отряда. Создание оценивается по случайной тройке предложений, без знания будущего результата генератора.

**Обмен колодами и интерфейс**
Импорт и экспорт работают с текстовыми кодами BG1. Недостающие карты показываются картами: создайте их по одной или все сразу; импорт откроется, когда ничего не будет недоставать. Импорт создаёт черновик: затем сохраните колоду. Добавлены консольные команды, улучшены подгонка переведённых кнопок, отступы редактора и навигация с контроллера, полёты карт в сброс и синхронизация анимаций лидеров.

Кнопка «Копировать» теперь сразу помещает код BG1 в буфер Windows. По желанию скопируйте папку bin из Optional-CopyButton в каталог игры (dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe), мод работает и без неё; если у другого мода уже есть dinput8.dll, оставьте его и загрузите ASI его загрузчиком. Без этих файлов кнопки импорта и экспорта скрыты.

**Просмотр карт и обучение**
Полный просмотр карты теперь как в бете: большая карта с оригинальным знаменем фракции из Beta 0.9.24, базовая сила белым, читаемая цитата и подсветка ключевых слов. Экраны колод используют то же знамя. В обучении 10 страниц, включая муллиган и добор, ряды и соседей, статусы карт. Код колоды можно вставить из буфера Windows («Вставить» или Ctrl+V; нужна папка Optional-CopyButton).

**Исправления карт**
Миргтабракке теперь наносит 2 ед. урона три раза, а способность Харальда Хромого бьёт десять раз — как в данных карт Beta 0.9.24.

**Установка после Redux**
Встроены определения старых предметов: 203 отсутствующих названия распознаются без замены 197 штатных определений, в обычной игре и НГ+. Это помогает загрузить старый инвентарь после смены модов. Уже потерянный и сохранённый инвентарь не восстанавливается, карты Redux не превращаются в коллекцию беты. Используйте сейв до потери данных. Уберите старую папку modBetaGwentReduxCompat и обновите объединения Script Merger.

**Встроенная очистка**
Отдельный мод очистки не нужен. Сделайте резервную копию сейва, завершите партию, выйдите из боя и закройте меню. bg_clean_preview() покажет инструкцию. Для удаления профиля беты выполните:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Сохранитесь В НОВЫЙ СЛОТ, выйдите из игры, удалите папки мода, обновите затронутые объединения скриптов, загрузите новый слот и сохранитесь ещё раз. Флаг очистки блокирует восстановление профиля, пока мод ещё установлен. Квесты, достижения и потраченные кроны не откатываются; выгруженные торговцы и контейнеры мира не обходятся. Сначала прочитайте BetaGwentDocs/CLEANUP_RU.md.

**Что дальше**
До 1.0 основной упор будет на исправления перевода и ошибок, дальнейшую доработку ИИ и интерфейса.

**Есть проблема? Пишите сюда.**
Буду рад отчётам об ошибках, логам и замечаниям по переводу. Укажите версии мода и игры, языки текста и озвучки, другие моды, карты и шаги повторения. Помогут скриншот и сохранение перед ошибкой.

**Как включить лог**

1. Добавьте **-debugscripts** в параметры запуска игры. В Steam: Свойства → Общие → Параметры запуска.
2. Запустите игру, повторите ошибку и закройте её.
3. Скопируйте лог до следующего запуска: он перезаписывается.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

4. Если Windows создала дамп падения, приложите последний относящийся к ошибке .dmp из:

```text
%LOCALAPPDATA%\CrashDumps
```
