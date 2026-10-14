# План работ: эффекты беты, редактор колоды, коллекция, бочки Лавка

Составлен 14.10.2026 для передачи другому агенту. Текущая база — исходники после 0.6.9 + анимация изгнания (см. `docs/reviews/2026-10-14-banish-vfx.md`, она служит образцом для всей работы ниже).

## 0. Решения пользователя (не пересматривать)

- Внешний вид — «1 в 1 как в бете 0.9.24». Улучшения UX, которых не было в бете (подсказки, история, стрелки), остаются.
- **Перемалывание карт не возвращать.** Лишние копии из бочек автоматически становятся осколками, как сейчас.
- **Бочки покупаются у корчмарей, как сейчас.** Витрину/магазин Лавка из беты не делать.
- Обычные карты статичны (premium-иллюстрации не добавлять). Анимированы только лидеры.
- В `D:\w3mod` ничего не удалять. Перед правкой копировать изменяемые файлы в `D:\w3mod\tmp\backup-<тема>-<дата>`.
- Критические ошибки (падение, зависание партии, потеря коллекции/валюты/колод) исправляются сразу, вне очереди.
- Правки баланса/ИИ не входят в этот план.
- Пользователь общается по-русски, коротко. Отчёт после каждого блока: что сделано, какие проверки прошли, что проверить в игре.

## 1. Средства воссоздания анимаций

### 1.1 Источник — оригинальная бета

- Игра: `D:\w3mod\Gwent 0.9.24.3.432\Gwent_Data`.
  - `sharedassets8.assets` — все VFX-префабы боя (70 шт., список в `docs/SPECIAL_VFX_0.6.6_RU.md`), материалы, текстуры, частицы.
  - `StreamingAssets/AssetBundles/gui/prefabs/*` — интерфейс: `deckbuilder_base`, `collection_shop`, `shop_base`, `shopmenu_base`; атласы `gui/spriteatlases/uber/*`.
  - `StreamingAssets/AssetBundles/Localization/{ru-ru,en-us}/text.*` — строки интерфейса беты (ключи `filter_*`, `db_filter_tooltip_*`, `panel_deck*`, `popup_*`, `input_card_management_*`).
  - `Managed/Assembly-CSharp.dll` — классы эффектов (IL уже выгружен: `docs/evidence/beta-animations80-il.txt`, поиск по имени класса, например `CardBanishVisualEffect`).
- Связь карта → эффект: `docs/evidence/special-vfx142.json` (85 особых карт: узел графа способности, `ElementType`, `AttackMethod`, префаб атаки/попадания/ряда). Генератор — `tools/recon/extract_special_vfx142.py`; он берёт только особые карты (`Type==2`). **Для отрядов его нужно расширить** на все шаблоны (см. 3.1).
  - `ElementType`: 1 Physical, 16 Fire, 32 Ice, 64 Lightning, 128 Earth, 256 Air, 512 LightMagic, 1024 DarkMagic, 2048 Nature, 4096 Water, 8192 Poison, 16384 Blood, 32768 Bubbles.
  - `AttackMethod`: 0 Direct (по цели), 1 Projectile (снаряд), 2 Row (ряд), 3 Side (сторона). Board — отдельные префабы `PowerBoard*`.
- Звук префабов: `docs/evidence/beta-audio86-vfx-map.json` (префаб → событие Wwise → банк). В моде звуки вызываются через `BetaGwentAudioCue(id)` в `duelAudioCatalog.ws` (`audioKind` кадра). Для каждого нового эффекта проверить, есть ли уже его звук.

### 1.2 Извлечение (UnityPy)

- В Linux-оболочке пользователя (device_bash): `pip install --user UnityPy attrs` (attrs обязательно обновить: `pip install --user --upgrade attrs`). На Windows есть копия в `tools/vendor/audio-python`.
- Порядок для одного префаба (пример — `tools/ui/build_banish160.py`):
  1. Найти GameObject по имени (`env.objects`, `type.name=='GameObject'`).
  2. Пройти иерархию Transform → дочерние объекты, вывести компоненты (скрипт-образец: `tmp/banish/dump.py`).
  3. `ParticleSystem.read_typetree()`: `lengthInSec`, `startDelay`, `InitialModule` (life/speed/size/rotation/color), `ShapeModule` (тип, радиус, угол, randomDirection), `EmissionModule` (rate, кривая, bursts), `ColorModule` (ключи альфы), `SizeModule`, `RotationModule`, `VelocityModule`, `ForceModule`, `ClampVelocityModule`, `UVModule` (tilesX/Y — раскладка листа). Образец вывода: `tmp/banish/particles.txt`.
  4. `ParticleSystemRenderer`: `m_RenderMode` (0 billboard, 1 stretched), `m_LengthScale`, `m_Pivot`, материалы.
  5. Материал: шейдер (имя через внешний файл, например `resources.assets` id 419 = `VFX/Common/AlphaBlended`), `_MainTex`, `_TintColor`, `_DissolveTex`, `_DissolveRamp`, `_EmissionMulti` и т.п.
  6. Свои MonoBehaviour без typetree — читать сырые байты (`get_raw_data()`) и разбирать по полям из IL (`beta-animations80-il.txt`). Проверять смещения утверждениями (`assert`), как в `build_banish160.py`.
  7. Текстуры: `Texture2D.image` → PNG. Собирать небольшой атлас под нужный размер (ячейки 64–128 px), прямая альфа. Режим смешивания брать из исходного материала: Additive → `blendMode="add"`, AlphaBlended → обычное смешивание. Не заменять аддитивный свет обычной альфой; полные правила и исключения — `docs/VFX_RENDERING_RULES_RU.md`.
  8. Анимационные клипы UI (AnimationClip в бандлах gui) — для таймингов меню и редактора: кривые позиций/масштаба/альфы.
- Результаты извлечения записывать в `docs/evidence/<тема><этап>.json` (параметры, id объектов, SHA источника).

### 1.3 Перенос в GFx (ActionScript 3, Scaleform)

- Шейдеры Unity не исполняются. Используемые замены:
  - **Растворение (dissolve):** `BetaGwentDissolve144` — маска карты из сетки шума 44×60 (векторные прямоугольники, без BitmapData-шейдеров) + полоса кромки из 6 цветов градиента. Новый вид растворения = новые данные в `BetaGwentDissolveData144` + ветка `kind` в конструкторе.
  - **Частицы:** спрайты из атласа, каждый — **один четырёхугольник** через `graphics.beginBitmapFill(..., Matrix)`. Вложенный `scrollRect` на повёрнутом/масштабированном атласе в игре протекает (виден весь лист) — не использовать. Образцы: `BetaGwentKillArt144.cell`, `BetaGwentBanish160.cell`.
  - Цвет шейдера `AlphaBlended` = 2 × `_TintColor` × цвет вершины × текстура → `ColorTransform` с множителями (могут быть > 1).
  - Растянутые частицы (stretched) — четырёхугольник длиной `size × lengthScale`, повёрнутый по направлению скорости.
  - 3D-направления проецировать на плоскость стола; торможение `ClampVelocity` интегрировать заранее (функция `banishShards`).
- Единицы: мелкая карта на столе = **22 единицы Unity по ширине** (`u = poseW/22`). Ось Y Unity вверх → экранная Y вниз.
- Анимационная система поля (`BetaGwentBoard.as`):
  - `animations.push({...})`: `sprite`, `fromX/Y`, `toX/Y`, `delay`, `duration`, `fromScaleX/Y`, `toScaleX/Y`, `fromRotation/toRotation`, `fade` (линейное 1→0), `scene` (появление/исчезновение по 18%), `appear`, `hideBeforeDelay`, `remove`, `curve`/`scaleCurve` (кривые беты из `BetaGwentBetaMotion`), `hitFrames` (покадровый лист), `dissolve`/`burn` (вызов `render(progress)`), `arc`, `betaFlight`. Позиция по умолчанию — ease-out cubic.
  - Помощники: `killSprite`, `killMotion`, `killFrames`, `betaBurst`, `betaVisual`, `drawBetaHit`.
  - Точки входа: `drawVisualCue` (кадры с `activeCue.kind`), `drawCards` (появления/исчезновения карт, сравнение `before`/текущего состояния), цикл исчезнувших карт («Departures»).
  - Длительность кадра: `cueMinimumDuration(kind)` и пол `cue.floor` в `prepareReplayTiming`. При `playing` задержки и длительности обрезаются до длительности кадра — длинный эффект требует поднять пол (пример: изгнание → 1300 мс).
  - `reducedMotion` — короткий вариант без частиц, обязателен для каждого эффекта.
  - Виды кадров (`kind`): 1 розыгрыш, 2 изменение силы/брони, 3 смерть, 4 погода/жетон ряда и др. (`audioKind` уточняет), 5 пас, 6 конец раунда, 7 начало раунда, 8 триггер/засада/таймер/стойкость, 9 блокировка, 10 превращение, 11 поглощение, 12 изгнание/сброс/Ирден, 13 Завещание, 14 перемещение/добор, 15 из сброса/из колоды, 16 создание, 17 зачистка между раундами, 18 нет целей. Источник — `RecordVisual(...)` в `duelSession.ws`.
  - Жетоны карты (`tokens`): 1 стойкость, 4 блокировка, 64 вскрыта, 512 обречённая; шпион — по шаблону (`isSpyCard`).
- Ограничения:
  - Порог упаковки меню **65 МиБ**. Атласы держать маленькими (изгнание — 256×448, 91 КБ). Большие PNG можно добавить в список уменьшения `tools/build_low_memory.py`.
  - Не пересобирать сетку коллекции на каждое движение мыши (см. `BETA_EDITOR_PIPELINE92.md`).

### 1.4 Проверка

- Офлайн-прорисовка на Python по тем же параметрам для визуальной самопроверки (образец `tmp/banish/preview_render.py`, результат `tmp/banish/banish_frames.png`). Картинку показать пользователю как черновик.
- Регрессия на Node: реальные функции AS извлекаются из `BetaGwentBoard.as` и исполняются в `vm` (образец `tools/ui/check_banish160.js`: данные, маршрутизация, тайминг, маски, число и время частиц, `reducedMotion`). Запуск из `D:\w3mod`: `node tools/ui/check_<имя>.js`.
- Подключение проверки к сборке: `tools/build_from_source.py`, список `additional` (этапы ≥160).
- Перед сдачей прогнать все `tools/ui/check_*.js`. Известные несвязанные падения (были до изменений): `check_controller125`, `check_fixes061`, `check_release136`, `check_native_consume156` без аргумента.
- Сборка: пользователь запускает `Build-Mod.cmd` в корне (60+ наборов проверок, компиляция 4 меню и скриптов, упаковка). Проверка в игре — только пользователем; после каждого блока дать ему короткий список сцен для проверки.

### 1.5 Правила правки файлов

- Рабочие исходники интерфейса — `BetaGwent/ui/src` (их собирает сборка). Ту же правку зеркалить в `src-BetaGwentBoard`, `src-GwintGame`, `src-BetaGwentKeg`, `src-DeckBuilder` (последние две слегка отличаются — править по якорям, проверяя `count==1`).
- `BetaGwentBoard.as`: UTF-8 **с BOM и CRLF**. Python `read_text`/`write_text` превращает CRLF в LF — читать/писать байтами или восстанавливать CRLF. Проверка: `file BetaGwentBoard.as`.
- WitcherScript: `BetaGwent/development/scripts/game/betagwent/*.ws` (70 скриптов, количество проверяется сборкой).
- Новые строки интерфейса — через существующий конвейер языков (13 языков текста, ноль непереведённых строк; см. `tools/ui/build_ui_text138.py`, `build_languages137.py`, проверку полноты переводов). Где есть строка беты — брать её (RU/EN из `Localization`), остальные языки — по действующему процессу проекта.
- Записка по каждому блоку: `docs/reviews/<дата>-<тема>.md` (источник, что сделано, проверки, что не покрыто).

## 2. Шаблон работы над одним эффектом

1. Найти в бете префаб и где он вызывается (граф способности, класс эффекта в IL).
2. Извлечь параметры и текстуры генератором `tools/ui/build_<эффект><этап>.py`; записать evidence JSON.
3. Сделать атлас/данные, класс-обёртку `BetaGwent<Имя><этап>.as` (только quad-отрисовка).
4. Встроить в `BetaGwentBoard.as` в нужной точке, с `reducedMotion` и полом длительности кадра.
5. Офлайн-превью → самопроверка.
6. Node-регрессия, подключение в `build_from_source.py`, прогон всех проверок.
7. Записка в `docs/reviews`, список сцен для проверки в игре.

## 3. Эффекты боя (по приоритету)

### 3.1 Стихийные эффекты способностей — главный блок (8–12 ч)

Сейчас (`drawSpecialProjectile`): все стихии, кроме молнии, — общий тонированный всплеск (`betaBurst -103`) или общий снаряд. Цвет из `BetaGwentSpecialVfx.tint`.

Сделать по префабам беты:
- Свет: `PowerDirectLightMagic`, `PowerLightMagicProjectile`, `PowerRowLightMagic`, `PowerSideLightMagic`, `PowerBoardLightMagic`.
- Тьма: `PowerDirectDarkMagic`, `PowerDarkMagicProjectile`, `PowerRowDarkMagic`, `PowerSideDarkMagic`, `PowerBoardDarkMagic`.
- Физика: `PowerDirectPhysical`, `PowerPhysicalProjectile`, `PowerRowPhysical`.
- Огонь: `PowerDirectFire`, `PowerFireProjectile`, `PowerSideFire`.
- Лёд: `PowerRowIce`, `PowerSideIce`, `PowerBoardIce`.
- Земля: `PowerDirectEarth`. Воздух: `PowerRowAir`, `AirTokenAttack`.

Шаги:
1. Расширить `extract_special_vfx142.py` (новый файл, например `extract_card_vfx16x.py`) на **все** коллекционные шаблоны, включая отряды и лидеров: элемент/метод для урона, усиления, брони, жетонов. Сгенерировать `BetaGwentSpecialVfx` (или новый класс) с привязками для всех карт.
2. Для каждой стихии один атлас на все её варианты (общие текстуры) — экономия бюджета меню.
3. Встроить: Direct — в точке попадания; Projectile — полёт от источника к целям (траектория и время полёта — из префаба; молния уже сделана, `drawLightning143` — образец); Row/Side/Board — по геометрии ряда/стороны (`rowGeometry`).
4. Синхронизация: попадание = `cueImpactTime()`; числа силы и звук уже привязаны к этому времени — не ломать.
Готово, когда: каждая из ~25 комбинаций отрисована своим префабом; проверка на привязки всех карт и на тайминги; массовые эффекты (много целей) не роняют FPS — проверить на 9 целях в ряду.

### 3.2 Выкладка карты (1–1,5 ч)
`CardLandingEffect`, `GoldLanding` (золотые), `CardFrostLandingEffect`, `CardRainLandingEffect`, `CardMistLandingEffect` (выкладка в ряд с морозом/дождём/туманом). Сейчас `drawLandingCue` — тень и мелкие всплески. Встроить в `drawLandingCue` (вызывается при розыгрыше и призыве), выбор варианта по тиру карты и погоде ряда (`weatherRows`).

### 3.3 Появление созданной карты (0,5–1 ч)
`SpawnBlink`. Сейчас `drawSummonCue` — общий всплеск. Кадры 15/16.

### 3.4 Урон от погоды (1 ч)
`Fog_Damage` и тики мороза/дождя. Сейчас `drawWeatherImpact` — всплески из слоёв погоды. Проверить, какие префабы бета использует для тика каждой погоды (граф `ChangeLocationTokensNode`/погодные классы), воспроизвести.

### 3.5 Ясное небо (0,5–1 ч)
`BoardEffect_ClearWeather`. Сейчас ветка `token==-1` в `drawWeatherCast` — лучи `betaBurst`.

### 3.6 Появление/снятие статусов (1,5–2 ч)
`ResilienceToken`, `SpyingToken`, `RevealToken`, `CardTimerVFX` (тик счётчика). Сейчас значки статичны: `paintResilience`, `paintSpyRibbon`, `paintRevealedMark`, `paintTimer`. Образец появления статуса — блокировка (`LockToken` → `BetaGwentLock126`, сравнение `before.tokens` в `drawCards`). Кадры: стойкость — 8 c `audioKind 26`, таймер — 8 c `audioKind 32`, вскрытие — `NilfReveal`.

### 3.7 Броня (0,5 ч)
`ArmorIncrease` (рост брони; сейчас значок просто появляется за 140 мс), сверить `ArmorDecrease` с текущим `drawArmorHit`.

### 3.8 Усиление и урон на карте (1 ч)
`PowerUp`, `PowerDown`, `CardPowerChangeIndicator`. Кривые пульса цифр уже из беты (`POWER_UP`/`POWER_DOWN`). Заменить свои частицы `drawBoostCue` (зелёный подъём) и общий лист `drawBetaHit` на префабы беты, если они отличаются. Учесть решение 0.6.9: «без большого повёрнутого блика и яркой постоянной рамки» — сверить с префабом.

### 3.9 Засада (0,5 ч)
`AmbushEffect`. Сейчас в `drawCards` своя золотая вспышка («Ambush sprung»). Кадр 8 «Засада раскрылась».

### 3.10 Превращение, повышение/понижение (1–1,5 ч)
`NatureTransform` (кадр 10, `RecordTransformVisual`, `audioKind 25`), `PromoteSimpleVFX`, `DemoteParticleSimpleVFX` — сначала найти, какие карты беты их вызывают.

### 3.11 Геральт: Аард (0,5–1 ч)
Префаб `Aard`. Найти шаблон карты и узел графа.

### 3.12 Сверка (0,5–2 ч)
По имени в коде не найдены: `RowEffect_Fire`, `[152402]PowerBoardFire`, `Fire`, `RaghNarRoogInitializationEffect`, `GoldenFrothCardEffect`. Найти вызывающие карты, сравнить с тем, что сейчас показывает мод, сделать недостающее.

### 3.13 Изгнание — проверить в игре
Уже сделано (`drawBanishDeparture`, `check_banish160.js`). Не покрыто: изгнание из руки (201613) и из сброса — решить по бете, есть ли там видимая анимация.

## 4. Редактор колоды, коллекция, бочки

Источник беты: `gui/prefabs/deckbuilder_base` (`UIDBPrefab`: `Collection/Filters`, `CreateDeck`, `DeckPickerPrefab`, `SidePreview`, VFX `UIDBCardAdd`, `UIDBCardRemove`, `DBVFX_CardViewRemove`, пулы `SpawnDragCardVFXPool`/`ReleaseDragCardVFXPool`), `shop_base` (`CardDecoratorKegOpeningPrefab`, `..._Reveal`, «Already owned»), `collection_shop` (`UICardManagementBackgroundPrefab`). Раскладка RectTransform уже выгружалась: `tools/ui/beta_editor_sources.py` → `BetaGwent/ui/assets/beta-editor/layout.json`. Код мода: `drawBetaDeckEditor`, `redrawBetaCollection`, `drawBetaDeckPicker`, `drawBetaCatalog`, `redrawBetaCatalogGrid`, `drawKegBeta`; WitcherScript: `deckBuilder.ws`, `collectionProfile.ws`, `developmentBoardMenu.ws`.

Все пункты — мышь, клавиатура и геймпад (`BetaGwentController.registerControl`), все 13 языков текста.

### 4.1 Создание колоды «фракция → лидер» (1,5–2 ч)
Бета: `CreateDeck` — сетка лидеров на полках (`Shelves`), панель описания (`FactionPreviewWidget`, имя, художественный текст), строки `panel_deckcreate_faction_description`, `panel_deckcreate_leader_description`, `popup_no_leaders_desc`. Сейчас «Новая колода» сразу открывает редактор, фракция и лидер — кнопками и стрелками. Сделать отдельный экран перед редактором; в редакторе оставить смену лидера.

### 4.2 Фильтры редактора (1 ч)
Бета: фракция, цвет, принадлежность, «Новые», премиальные (не нужно), сортировка «Слабые/Сильные», позиция (`filter_position_*`: рукопашный, дальнобойный, осадный, подвижные, событие), кнопка сброса (`ResetButton`). В моде нет: «Новые», сортировка по силе, позиция, сброс. Данные о ряде — из определения карты (поле ряда/«любой ряд» в каталоге).

### 4.3 Признак «новая карта» (1–1,5 ч, затрагивает сохранения)
Бета: карта новая, пока игрок её не посмотрел. Нужно хранить «просмотрено» по шаблону в профиле коллекции (`collectionProfile.ws` + зеркало профиля, формат с контрольной суммой — см. `tools/ai/check_profile136.py`). Поднять версию формата, старые сейвы — все карты «не новые». Сбрасывать при наведении/просмотре. Используется в 4.2, 4.6, бочках (`kegNewIds`).

### 4.4 Перетаскивание (1–1,5 ч)
Перенос карты из коллекции в колоду и обратно мышью с подсветкой зоны (`DragHighlight`) и эффектами пулов беты. Клики остаются. Не мешать прокрутке.

### 4.5 Эффекты добавления/удаления карты (1 ч)
`UIDBCardAdd` (вспышка, волна, искры, подсветка кромки), `UIDBCardRemove`, `DBVFX_CardViewRemove` — по методике раздела 1.

### 4.6 Прокрутка вместо страниц (1,5 ч)
Коллекция редактора и каталога, список карт колоды (сейчас страницы по 12). Колесо, полоса прокрутки, геймпад; затенения сверху/снизу (`TopShade`/`BottomShade`). Только видимые плитки, без пересоздания всей сетки на кадр. Сохранить фокус геймпада.

### 4.7 «Очистить колоду» (0,5 ч)
Строки `input_clear_preview_board`, `dialog_clear_board_title/desc`. Работает с существующей отменой (undo).

### 4.8 Подтверждение выхода без сохранения (0,5 ч)
`popup_save_deck_title/desc`: «Сохранить / Не сохранять / Отмена». Нужен признак изменений (сравнение с исходным составом и именем).

### 4.9 Коллекция (0,5 ч)
Добавить фильтры «Новые» и позиция, отметку новых карт в сетке (после 4.3). Перемалывание и предупреждения о нём — не делать.

### 4.10 Бочки: «Открыть ещё одну бочку?» (0,5–1 ч)
После итога, если есть неоткрытые бочки (`unopenedKegs`), предложить следующую (строки `input_card_management_shop_open_barrel_summary_open_next`, `open_keg_prompt`). Сейчас `kegFinish` → `OnBetaGwentKegChoose` (`developmentBoardMenu.ws`) и выход. Нужна цепочка выбор → сохранение → `OnBetaGwentKegOpen` без закрытия меню. Проверить сохранение и защиту от повторного начисления при закрытии посреди цепочки.

### 4.11 Бочки: сверка анимации раскрытия (1–2 ч)
Бета: `CardDecoratorKegOpeningPrefab` и `_Reveal` (позиции «скрыто/показано», способность «скрыта/показана», подсказка), папка «Already owned» с анимацией для дубликатов. Извлечь AnimationClip/RectTransform, сравнить с текущими полётом из центра, переворотом и надписью «Лишняя копия → осколки». Желательна запись экрана беты от пользователя. Витрину/покупку не делать.

## 5. Порядок и объём

1. 3.1 стихийные эффекты (самое заметное в каждой партии) — 8–12 ч.
2. Быстрые улучшения редактора/бочек: 4.2, 4.7, 4.8, 4.10 — 2,5–3 ч.
3. 3.2, 3.3, 3.6–3.9 — 5–7 ч.
4. 4.3 → 4.9 (затрагивает сохранения, отдельная сборка и проверка сейвов) — 2 ч.
5. 4.1, 4.4, 4.5, 4.6 — 5–6 ч.
6. 3.4, 3.5, 3.10–3.12, 4.11 — 4–7 ч.

Итого ≈ 27–37 ч работы агента плюс игровые проверки пользователя (на каждый блок вероятен круг правок). Сборку делать после каждого пункта списка выше, не копить.

## 6. Что сдавать по каждому блоку

- Изменённые файлы, резервные копии в `tmp/backup-*`.
- Генераторы и evidence JSON, атласы, новая Node-регрессия, подключённая к сборке; все прежние проверки проходят.
- Офлайн-превью эффекта (картинка) — для эффектов боя.
- Записка в `docs/reviews/`.
- Короткий список для проверки в игре: какие карты сыграть, что должно быть видно, где возможны отличия от беты.
