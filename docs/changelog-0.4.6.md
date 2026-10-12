# 0.4.6

## Русский

### ИИ
- Улучшен выбор целей урона и блокировки: ИИ учитывает будущую пользу движков, в том числе каэдвенских призраков и реданских оруженосцев с бронёй.
- Усилена проверка шпионов, которые добирают карту: учитываются возможный следующий ход и риск отдать выигранный раунд.
- Ирис и Сабрина оцениваются вместе со способом активировать их завещание; Фрингилья выбирает полезную пару соседей и порядок постановки.
- В первом раунде ИИ оценивает возможность догнать соперника всей оставшейся рукой вместе с лидером и может сохранить бесполезно расходуемые карты.
- Погода оценивается с учётом длительности раунда и уже действующих эффектов. Улучшены ранний розыгрыш глобальной погоды, сохранение повторной погоды и замена мороза/шторма лунным светом.
- Мулиган учитывает оставшиеся подходящие цели в колоде. Эльфский наёмник без бронзовых особых карт получает приоритет замены. «Гром» учитывает доступное число союзных отрядов.
- В лог добавлены причины замены пустых карт, прогноз оставшейся руки и планы активации завещаний.
- В решающем раунде погода получает приоритет раннего розыгрыша; усиления получают дополнительную срочность, когда союзников ослабляет погода.
- Корабли Скеллиге учитываются как движки при выборе целей. Дополнена оценка сдачи первого раунда при большом отставании.
- Наталис оценивает полезность оставшихся тактик, включая карты, которые сами разыгрывают другую карту из колоды.
- Превентивная погода учитывает публичную историю постановки по рядам; риск очистки уменьшает желание сохранять погоду на потом.
- Фрингилья использует любого слабого соседа слева и сильного справа; Эмиссар не обязателен. Драйг сохраняет роль подготовки сброса для жриц; Сабрина требует слабого отряда в ряду и способа активировать завещание.
- Дополнена оценка будущей пользы лёгкого драккара рядом с мечником, подготовка трёх соседних целей для «Грома» и оценка засад Моренн и Торувьель.
- Пересмотрены восемь составов по результатам парных испытаний. В «Завещания» добавлены Кухарка: ритуал, Плотва и Оззрел. Неудачные варианты для «Невольничьей пехоты» отклонены.
- Вместо четырёх похожих колод добавлены составы под Дагоном, Радовидом, Узурпатором и Филавандрелем. Русские названия доступны для всех 46 архетипов.

### Карты и квесты
- Плотва срабатывает от собственного золотого отряда, сыгранного из руки на свою половину поля.
- Воскрешение сохраняет блокировку отряда.
- Драуг поднимает подходящие отряды из собственного сброса в виде драугиров с учётом свободного места в ряду.
- Исправлено отображение прогресса квеста сбора колоды Скеллиге при открытии журнала: учитываются сохранённые награды квестовых противников, без повторного зачёта побед.

### Интерфейс и анимации
- Особые карты без выбора ряда играются на подсвеченную половину поля. Для них больше не нужно выбирать конкретный ряд.
- Улучшена навигация контроллером к кнопкам выбора, завершению обмена, выходу после боя и пустым областям редактора колод.
- Возвращены оригинальные цепи и замок блокировки из беты.
- При постановке, перетаскивании и превращении сохраняется полное оформление карты.
- Исправлена полная корона победы на обеих сторонах.
- Удары погоды показываются с одинаковой скоростью на всех рядах. Серии урона, включая четыре удара корабля, показывают отдельные попадания.
- Ускорение массового поглощения и реакций накеров сохраняется; усиление и броня одного действия показываются совместно.
- Добавлены сброс изменённой стартовой колоды к стандартному составу, фильтры владения и сортировка каталога, причины невалидности колод в списке.
- В меню действий доступны последние десять событий со сменой счёта и сохраняемая настройка паузы перед ходом ИИ.
- Дополнены полёт карт из стопки, переворот засады с подсветкой, разрушение брони до нуля и показ отсутствия подходящих карт при выборе из колоды/сброса.
- Удержание LT открывает свой сброс, RT — колоду, обоих курков — сброс противника. Отпускание возвращает к текущему выбору.
- Большие списки выбора способностей помещаются на одну страницу в два или три ряда, с полным предпросмотром. Переход за край ряда продолжает выбор в следующем ряду.
- Одинаковые карты отображаются отдельными событиями истории; погода получает собственную запись. Пауза ИИ не зависит от настройки уменьшенных эффектов.

### Сборка
- Проверка интерфейса использует текущий набор из 48 связей вместо устаревшего фиксированного количества. Наличие методов и число аргументов по-прежнему проверяются по скомпилированному байткоду.
- Повторная упаковка звука сохраняет старый split-файл отдельно, устраняя конфликт после сбоя завершения REDkit.

## English

### AI
- Improved damage and lock target selection, including the future value of Kaedweni Revenants and armoured Redanian support units.
- Draw spies now account for playable follow-ups and the risk of giving away a winning round.
- Iris and Sabrina require a profitable Deathwish activation plan. Fringilla evaluates ordered neighbour pairs and placement.
- First-round concession considers the whole remaining hand and available leader, helping the AI save cards when it cannot catch up.
- Weather evaluation accounts for remaining turns and existing effects: earlier global weather, conserving redundant weather, and replacing Frost/Storm with Moonlight.
- Mulligan checks remaining legal tutor targets. Elven Mercenary with no Bronze Specials receives replacement priority; Thunder considers available allied bodies.
- Decision logs explain exhausted tutors, whole-hand forecasts and Deathwish activation plans.
- Decisive rounds prioritise early weather. Boosts gain urgency while allied units are being worn down by weather.
- Skellige longships count as removal targets with engine value. Expanded first-round concession evaluation for large deficits.
- Jan Natalis evaluates the remaining tactics, including cards that play another card from the deck.
- Preventive weather uses public row-placement history; Clear Skies risk reduces the incentive to hold weather for later.
- Fringilla uses any weak left neighbour and strong right neighbour; an Emissary is optional. Draig retains his graveyard preparation role for Priestesses; Sabrina requires a weak unit in the row and a viable Deathwish activation.
- Expanded future-value scoring for Light Longships next to Greatswords, building three adjacent Thunder targets, and Morenn/Toruviel Ambushes.
- Revised eight deck lists after paired trials. Deathwish gains Brewess: Ritual, Roach and Ozzrel. Unsuccessful Slave Infantry candidates were rejected.
- Replaced four similar lists with Dagon, Radovid, Usurper and Filavandrel decks. All 46 archetypes have Russian names.

### Cards and quests
- Roach triggers from its owner's Gold unit played from hand onto their own half.
- Resurrected units retain their Lock.
- Draug raises eligible units from its owner's graveyard as Draugirs, respecting available row space.
- Opening the quest journal repairs Skellige collection progress using saved quest-opponent reward claims, without counting repeat wins.

### Interface and animations
- Specials that do not require a row target use a single highlighted half-board cast area.
- Improved controller access to choice buttons, finishing mulligans, leaving completed matches and empty deck-editor panes.
- Restored the original Beta Lock chain and padlock effects.
- Full card frames and state icons remain visible during placement, dragging and transformations.
- Fixed complete victory crowns for both players.
- Weather hits use consistent timing across rows. Repeated attacks, including four ship hits, show individual impacts.
- Mass consumption and Nekker reactions remain accelerated; combined boost and armour actions retain a single presentation per target.
- Added resetting an edited starter deck to its default list, ownership filters and catalogue sorting, and invalid-deck reasons in the deck list.
- The actions menu includes the last ten events with score changes and a saved AI move-delay setting.
- Expanded pile-to-board flights, highlighted Ambush reveals, fully depleted armour breaks and feedback for empty deck/graveyard choices.
- Hold LT for your graveyard, RT for your deck, or both for the opponent's graveyard. Releasing the triggers returns to the pending choice.
- Large ability-choice lists fit on one page across two or three rows with full previews. Moving past a row edge continues into the next row.
- Identical cards retain separate history events, and weather has its own entry. AI move delay is independent of reduced effects.

### Build
- UI validation checks the current 48-method contract instead of an outdated fixed count. Compiled methods and argument counts remain strictly verified.
- Retried audio cooking preserves the previous split list separately, preventing conflicts after a REDkit shutdown failure.
