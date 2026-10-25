> Текущий статус и команды: [AI_DEVELOPMENT_RU.md](../../../docs/AI_DEVELOPMENT_RU.md). Порт подключён к WS; старые pending и ссылки на временные drafts ниже — история этапов. Постоянные составы и план проверки находятся в data/beta924/ai/validation093.

# Актуальное дополнение24октября

Выбранные original Practice profiles исполняют полные партии:46 наших и45 подлинных колод без технических ошибок на v11.6 смешанных игр +4 four-group dispatch games прошли. Читать BetaGwent/drafts/day-iteration-20261023/CURRENT_DIRECT_JS_20261024_RU.md. Ниже сохранено описание предыдущего этапа; его pending не актуальны. Это ещё не итог силы и не готовый WS-релиз.

# Прямой перенос ИИ беты: исходники → JS → WitcherScript

Текущий путь по прямому исправлению пользователя. C# используется только для
чтения исходной логики. Native host, RPC и синхронизация двух движков остановлены.
Все действия выполняет один общий JS/WS-движок. Установка и публикация запрещены.

## Перенесено и подключено

- `core.cjs`: MiniMaxEvaluator, generic preferences, semantic/lowest-power
  mulligan, BestCardForPersonalityCardPicker. Float32, исходный порядок ties.
- `search.cjs`: AlphaBeta с углублением, буферами и остановкой. Явные кадры,
  максимум один вызов игрового действия на шаг. Незаконченный ход возвращает null.
- `profiles.cjs`:74 inherited scalars/defaults и исходный flatten-порядок semantic
  tags/четырёх association lists для229 профилей.698 исходных шаблонов.
- `actions.cjs`: исходный Node skeleton, пас, dedup шаблонов, размещения и реальные
  продолжения общего движка. Production clone stamps общие для runtime.
- `mulligan.cjs`: исходные pickers для живых начальных/следующих запросов обеих
  сторон. В поиске исходник моделирует только собственный муллиган; чужой
  заканчивает без обменов. Сохранённый собственный prefix повторяется без пересчёта.
- `handlers.cjs`: PlayAll, Random, Power/PowerRange, TemplateId, Semantic,
  HasTagsToken, Location, UnitOrEvent, Health, RowWith* и Summation.54листа/
  53uniqueID/161entry;357request-node hints/304templates из исходных XML.
- `choices.cjs`: одиночные цели/карты/ряды, PlayAll siblings и replay. Явные
  node IDs задают AIHint стадий201615/200102 и200048/200165. Bran200159 получает
  один набор0..3; общий движок исполняет его по одному действию на callback.
- `playmaker.cjs`: все21 source strategy families/30 DS cases, коррекция
  RevisedScore после поиска. Читает фактический счёт прошлого раунда и новый
  authoritative roundTurnIndex общего движка.
- `replay.cjs`: выбранная ветка исполняется в живой игре по сохранённым решениям.
  Повторный handler, policy RNG и новые search branches запрещены. Живой replay
  останавливается на границе раунда; реальные контроллеры затем делают муллиганы.

Первый исполняемый профиль — настоящий исходный Base: AlphaBeta/MiniMax/
SemanticPreference/BestCardForPersonality. Это пока не полное покрытие всех
профилей и не готовая высокая сложность для сравнения силы.

## Проверки и ограничения результата

Core321 (92начальные позиции46колод), search539 (96exhaustive/48pruned toytrees),
profiles18800, live mulligan1740 (184seat requests/366decisions), actions177
(242реальных узла). Эти счётчики относятся к разным проверкам, не числу партий.

Handlers288, choices170 (включая живой replay), stages294 (32fixture nodes,
все размеры0..3, exact stored replay, simulated mulligan prefix и граница
живого раунда), PlayMaker177. Тесты размеров Брана используют явно выбранный
source Random handler. Исходный Base PlayAll для0..3 возвращает empty set;
это сохранённое поведение, не заменённое полезной эвристикой.

Аудит04:42из46 depth1 opening searches с PlayMaker после настоящих source
муллиганов. Оставшиеся4 — технические остановки, не поражения. Аудиты01–04
сохранены отдельно; не менять их и не выдавать opening search за партию.

Технический games-audit-01:3полные партии на настоящих итоговых колодах
55/55,56/57,91/55 с фиксированными seed; обе стороны — частичный source Base
на глубине1. Все завершились без технических ошибок. Это НЕ смешанное сравнение
Beta против0.9.2, НЕ высокая сложность и НЕ доказательство усиления.

## Общий движок и следующий этап

Экспериментальный снимок v4:
`BetaGwent/build/day092-beta-external-controls-20261024-v4`, fingerprint
`245f6b2f73cd72baa193e457f4ff40ed4cd9a65bb4364fc3de06d18183373ff1`.
Он добавляет per-round turn counter к v3. Старые релизы/архивы неизменны.
`externalPolicyMask=3` передаёт обеим сторонам реальные запросы. В тестах
Beta запрещены Best*/Ai* selectors. CanSelectRow — общий read-only валидатор,
который использует и фактический SelectRow; второго XML-движка правил нет.

Остаётся:
-162302 Cow Tosser: исходник создаёт162402 и вызывает PlayCards; общий движок
  пока показывает row request родителя. Нужно настоящее дочернее размещение.
-162306 opposing reactive owner: сопоставить source request ownership с общим
  движком. Заодно убрать remaining BestOwnRow в external NilfNextReaction.
-133301 Wyvern Scale Shield: исходник выбирает hand затем board; общий движок
  пока наоборот. Требуется source-consistent порядок общей механики.
-Occurrence/OccurrenceRange/Wedge и остальные используемые non-Base handlers.
-Подключение фактических исходных профилей высокой сложности, полная смешанная
  партия, затем заранее зафиксированное парное сравнение/турнир четырёх групп.

Технические ошибки никогда не превращаются в поражения. Неперенесённый handler
останавливается явно. Beta разрешены скрытые данные; другие policies сохраняют
свои ограничения. Будущий отчёт должен явно указывать эту асимметрию.

## Буквальные особенности исходника

Сохранены первый matching semantic tag, недостижимая same-weather preference,
исходная проверка All=0x303 при common draw mask3 (в evaluator и PlayMaker),
TemplateIdHandler с неиспользованным player filter, RowWithAbstract Lowest с
двойной инверсией, пустой RowWithCeiling scratch list и Summation child-score
cleanup. Duplicate Summation ID выбирает первый Basic_LockTarget, а не поздний
Infiltrator_ChooseTarget. Исправления этих quirks — отдельные будущие изменения.

Node initial association lookup — только(template,1). Вложенный запрос:
(template,hint), затем(template,1), затем(0,hint), иначе source RandomHandler.
JS stable ties сохраняют input order; C# List.Sort не гарантирует stable ties.
SimulatorRandom копирует RNG перед поиском; живой RNG обработчиками не расходуется.

Пример запуска проверок без native runtime:

```
node tools/ai/check_beta_js_playmaker092.cjs BetaGwent/build/day092-beta-external-controls-20261024-v4
node tools/ai/check_beta_js_stages092.cjs BetaGwent/build/day092-beta-external-controls-20261024-v4
node tools/ai/check_beta_js_choices092.cjs BetaGwent/build/day092-beta-external-controls-20261024-v4
```

Полный актуальный статус и процессы: `state.json`, `DIRECT_JS_HANDOFF_RU.md`,
`direct-beta-js-port-status.json` в BetaGwent/drafts/day-iteration-20261023.
