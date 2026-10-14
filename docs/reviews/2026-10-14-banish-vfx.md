# 14.10.2026: анимация изгнания (Beta BanishCardEffect) и список недостающих эффектов

## Изгнание

Источник: `Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets`, префаб `BanishCardEffect` (GameObject 1150), компонент `CardBanishVisualEffect` (MonoBehaviour 4266). Генератор: `tools/ui/build_banish160.py` (UnityPy, шаг разработки), параметры: `docs/evidence/banish160.json`.

Что делает бета:
1. Снимает с карты статусы (`RemoveTokensFromTarget`).
2. Растворяет карту материалом `Banish_Small_Material` за 1,2 с, кривая линейная 0→1: шум `NoiseSoftEge` (края уходят первыми), кромка — градиент `EpicHighlightGradient` (фиолетовый → белый → фиолетовый) × `_EmissionMulti` 1,86.
3. Частицы: `BackLines` (0,03 с, 8 тёмно-индиговых растянутых штрихов `BanishHit`, растут 0→1 за 0,18–0,3 с), `EmissionElementMid` (0,18 с, 11 + ~14 осколков `BanishSparks`, скорость 27–75 с ограничением), `EmissionElementRim` (0,23 с, 11 + ~13 осколков, 45–120). Корневая система `ExplosionFragments` имеет нулевую эмиссию и ничего не показывает.
4. Звук `vfx_custom_banish` (3040005591) — уже был в моде как звуковой сигнал 12.

В моде (GFx-адаптация):
- `BetaGwentDissolve144.BANISH` + данные шума/градиента в `BetaGwentDissolveData144` (BANISH, BANISH_RAMP, BANISH_MS).
- `BetaGwentBanish160.as` + `assets/special144/banish_beta.png` (256×448, 91 КБ): ячейки BanishHit 2×2 и BanishSparks 3×3.
- `BetaGwentBoard.as`: `banishCueTarget`, `drawBanishDeparture`, `banishShards`. Срабатывает для отрядов, ушедших с поля по изгнанию (кадр 12, кроме Ирдена 201523), по любой операции со звуком изгнания (NilfBanish и др.), и для обречённых (токен 512). Казнь/Игни/Виллентретенмерт/Эпидемия сохраняют приоритет своего растворения. Прежний «подъём на 32 px с затуханием» убран.
- `prepareReplayTiming`: кадр с изгнанием длится не меньше 1300 мс, чтобы растворение не обрезалось.
- Регрессия `tools/ui/check_banish160.js` (29 проверок, реальный ActionScript), подключена в `build_from_source.py` для этапов ≥160. Все прежние JS-проверки, которые проходили до правки, проходят.
- Резервные копии: `tmp/backup-banish-1014`.
- При сборке 0.6.10 исправлена неоднозначная для Flex запись тернарного оператора перед дробью (`?.336`): добавлены пробелы и ведущие нули, расчёт времени частиц сохранён. Проверки JavaScript не обнаруживали эту ошибку синтаксиса ActionScript; её выявила настоящая компиляция меню.

Не покрыто: изгнание из руки (Шилард 201613) и из сброса — эти карты не видны на поле, анимации нет (в бете тоже рисуется только у видимой карты). Игровая проверка внешнего вида нужна.

## Чего ещё нет из 70 префабов беты (sharedassets8)

Уже есть: погодные слои всех жетонов (мороз, туман, дождь, засуха, шторм, Рагх-Нар-Рог, пена, волчья яма, Мечта дракона, луна), Молния Альзура, Казнь/Игни (огонь), Эпидемия (яд), поглощение (кровь), Ирден и сброс усилений, блокировка, растворение изгнания, кривые цифр силы.

Нет (используется общий тонированный «удар» или ничего):
1. Стихийные заклинания отдельными префабами: свет (PowerDirect/Row/Side/Board LightMagic + LightMagicProjectile), тьма (DarkMagic, все 5), физика (PowerDirectPhysical, PowerRowPhysical, PowerPhysicalProjectile), огонь (PowerDirectFire, PowerSideFire, PowerFireProjectile), лёд (PowerRowIce, PowerSideIce, PowerBoardIce), земля (PowerDirectEarth), воздух (PowerRowAir, AirTokenAttack). Сейчас все они — один общий вспышка/снаряд с цветом стихии. Затрагивает 85 особых карт и способности отрядов.
2. Выкладка карты: CardLandingEffect, GoldLanding (золотые), CardFrostLandingEffect / CardRainLandingEffect / CardMistLandingEffect (выкладка в ряд с погодой). Сейчас — общая тень и искры.
3. Появление созданных карт: SpawnBlink. Сейчас — общая вспышка.
4. Урон погодой: Fog_Damage и тики мороза/дождя — сейчас общие всплески по слоям погоды.
5. Ясное небо: BoardEffect_ClearWeather (сейчас общие лучи).
6. Статусы с анимацией появления: ResilienceToken, SpyingToken, RevealToken, CardTimerVFX (тик счётчика). Сейчас — статичные значки.
7. Броня: ArmorIncrease (есть только разрушение щита, близкое к ArmorDecrease).
8. Усиление/урон на карте: PowerUp / PowerDown / CardPowerChangeIndicator — кривые цифр взяты из беты, но частицы на карте свои.
9. Засада: AmbushEffect (сейчас своя золотая вспышка).
10. Превращение: NatureTransform; повышение/понижение: PromoteSimpleVFX / DemoteParticleSimpleVFX.
11. Геральт: Аард — префаб Aard.
12. По имени в коде не найдены, нужна сверка в игре: RowEffect_Fire, [152402]PowerBoardFire, Fire (огонь на поле); RaghNarRoogInitializationEffect (вступление Рагх-Нар-Рога); GoldenFrothCardEffect (пена на карте — в 0.6.9 переделана пена в ряду, эффект на карте отдельно не воспроизводился).

## Редактор колоды, коллекция, бочки — отличия от беты (14.10.2026)

Источник беты: `StreamingAssets/AssetBundles/gui/prefabs/{deckbuilder_base,collection_shop,shop_base,shopmenu_base}` и `Localization/ru-ru/text.ru-ru` (ключи `filter_*`, `db_filter_tooltip_*`, `popup_crafting_*`, `panel_deck*`, `input_card_management_*`). Мод: `drawBetaDeckEditor`, `redrawBetaCollection`, `drawBetaCatalog`, `drawBetaDeckPicker`, `drawKegBeta`.

Редактор: нет экрана создания колоды «фракция → лидер» (CreateDeck с полками и описанием фракции); нет фильтров «Новые», сортировки по силе (Слабые/Сильные), позиции (ряд/подвижные), выбора фракции «только нейтральные»; коллекция листается страницами вместо прокрутки; нет перетаскивания карты в колоду и обратно; нет эффектов добавления/удаления (UIDBCardAdd/UIDBCardRemove); нет «Очистить колоду»; нет подтверждения при выходе без сохранения; нет поштучного и массового перемалывания (убрано в этапе 111 — нужно решение).
Коллекция: нет фильтров позиции и «Новые», нет отметки новых карт в сетке, нет перемалывания из просмотра карты, нет предупреждения «карта используется в колоде».
Бочки (Лавк): нет «Открыть ещё одну бочку?» после итога (приходится возвращаться в меню колод); нет витрины Лавка с покупкой нескольких бочек и выбором количества (в моде бочки покупаются у корчмарей по одной — осознанная адаптация); переход «тролль → карты» без анимации раскрытия бочки на столе (в бете CardDecoratorKegOpening с отдельными позициями «скрыто/показано»).
