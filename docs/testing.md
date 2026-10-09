# Проверки и behavioral oracle

## Выполнено в разведке

- XML ZIP успешно прочитан; 698 уникальных Templates, duplicate=0.
- Все CardAbility.Template references существуют.
- 13 localization CSV разобраны csv parser с delimiter ';', quoted/multiline values; 2231 ключ на язык, missing template names=0.
- Manifest/evidence с SHA256 сохранены; unknown node types перечислены, их 183.
- DLL прочитана Mono.Cecil без исполнения Assembly-CSharp; metadata и IL записаны.
- PDF: прочитан текст всех 27 страниц и просмотрены три contact sheets; каталог 46 статей/46 raw codes.
- TW3 request/menu/outcome/acquisition chains прочитаны; installed REDkit .download=0; сверено 1527 .ws, Gwent hooks одинаковы.
- SWF containers разобраны (root classes, length/tags/end), modern AS FSM/AI/effects/output chains прочитаны.
- XML decks/dynamicCards, selected rewards и minigame binary string candidates записаны; node connections не декодировались.
- Original defaults/mulligan IL извлечён: hand до10, Choices3/1/1, blacklist fallback и replacement chain.

Дополнительно: оригинальный default deck validator/starter IL, зарегистрированный проект/depot manifest; Wcc script patch capability-06 успешно собран (exit0, 1774-byte blob, compilerErrors0). Это компиляция одного development probe, не завершённого gameplay мода.

Runtime probe запущен пользователем из REDkit. Log подтверждает basic flat saved int+array save/load и Gwent request/end hooks, в том числе victory. Другие исходы пользователь подтвердил; enum string первого end пустой, exact lost/forfeit flags не видны. Starter branch не наблюдалась в trace. Evidence: [runtime trace](D:/w3mod/docs/evidence/capability-runtime-trace.txt), [structured result](D:/w3mod/docs/evidence/capability-runtime-result.json).

Дополнительно выполнено: 24 pure methods извлечены с идентичными instruction texts; 20/20 checks на их IL для crowns/ties/match winners/pass reset. AS3-only UI собран Apache Royale и экспортирован bundled GFxExport, header/tag/root invariants проверены. Native board/bridge и116/104/123 assertions прошли в REDkit. В том запуске была отдельная switch128 diagnostic; исправление и новые FLOW43/interactive UI требуют следующего native запуска.

Не выполнено: сборка DIY, запуск серверов, полный dynamic original oracle, exact deck import, native39 action queue checks, полный profile/migration/NG+/capacity tests. Original gameplay полностью не восстановлен. Инструкция probe: [CAPABILITY_CHECK.md](D:/w3mod/GwentB/myproject1/CAPABILITY_CHECK.md).

## Узкая проверка оригинальных IL методов

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\oracle\extract_beta_flow.ps1
dotnet run --project .\tools\oracle\beta-flow-ref\BetaFlowRef.csproj -- D:\w3mod
python .\tools\ui\build_probe.py
```

Fixtures: [round-cases.json](D:/w3mod/tools/oracle/beta-flow-ref/round-cases.json). Проверяются оба победителя, нулевая/ненулевая ничья, ничья при одном/двух накопленных crowns, две победы, split rounds и две ничьи; также score snapshot не удерживает входной массив. Все комбинации pass и сброс round/turn flags проверяются отдельно. [Результат](D:/w3mod/docs/evidence/beta-flow-fixtures.json) сохраняет actual/expected и hashes. Извлечённая сборка содержит minimal holders, не оригинальный module initializer. Board scores/scheduler/request validity и cleanup не исполнялись.

## Повторение анализа

Из `D:\w3mod`:

```powershell
python .\tools\recon\audit_sources.py
& .\tools\recon\inspect_beta_assembly.ps1
& .\tools\recon\inspect_beta_defaults.ps1
python .\tools\recon\inspect_redkit.py
& 'C:\Users\NikR\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' .\tools\recon\inspect_tierlist.py
```

Для DLL используется уже имеющаяся MelonLoader/Mono.Cecil.dll. Для PDF используется bundled Python pypdf/pdfplumber. Источники не модифицируются. Два audit JSON с regex/art-derived candidates не заменяют компиляцию C# или проверенный mapping.

## Oracle proposal

Baseline для каждого run: client version/hash, data ZIP hash, restoration DLL hash, enabled patches, mode, exact decks, RNG seed/state. Сначала training/offline reference; multiplayer patch ordering не принимать без сверки.

Capture logical normalized snapshots + action/event trace: match phase, round, active player, wins/pass/leader, scores, each card instance ID/definition ID/owner/controller/zone/index/power layers/armor/tokens/visibility, row tokens, pending requests, action/ability/play/execution stacks, RNG state. Для AI fixtures отдельно public observation.

Сравнение: identical initial state → same legal intent/choices → logical resulting state + ordered trace. Presentation timing и network BundleID исключить из logical comparison. Для случайности без exact MT parity сначала фиксированные choices или invariant/seed-подготовленные scenarios; не называть approximate comparison deterministic parity.

GameController.Clone/SetupAIvsAI/Step дают кандидат seam, но DLL зависит от Unity/shared data; headless harness ещё технически не подтверждён.

## Обязательные regression группы

| Группа | Сценарии |
|---|---|
| Legality | чужая карта/цель, row capacity, expired choice, invalid leader, unknown IDs, duplicate responses; state неизменен |
| Power | boost vs strengthen, damage vs weaken, armor, reset, permanent power, inactive reset |
| Ordering | priority, row/zone tie, index tie, active player tie, reentrant effects, death batches, triggers after transform/lock |
| Zones | draw/discard/banish/create/spawn/resurrect/consume/move, owner/controller и hidden visibility |
| FSM | mulligan end, pass, empty hand+leader, draw round, double pass, ties/wins, cleanup |
| AI/pass | must-win, safe pass, bleed, reach vs engines/weather, preserve combo, hidden-state leakage |
| Deck/data | original IDs, faction/leader/copies/tiers, missing localization/assets/abilities, unknown IR nodes |
| Rewards | first-win claims, repeat win, duplicate policy, merchant callbacks, quest fixed reward |
| Save | old save initialize twice, profile round-trip, new version, NG+, standalone DLC |
| TW3 | request→deck→match→result→quest, cancel/forfeit/draw policy, input/fade/sound cleanup |

При AI batch записывать seed/decks/profiles, wins/losses/draws, rounds, card advantage, suspicious/illegal actions, crashes и resolution budget. Pass tests должны проверять решения в конкретном state; порог score>enemy не является достаточной политикой.

Slice readiness: exact 10–20 cards, legal decks, expected traces, UI/save smoke test, один NPC и win/loss/forfeit. Full pool/rewards/tournament integration только после этого. REDkit5.0 compile/runtime/flat save/hooks подтверждены; новые39 queue checks и полный профиль остаются отдельными проверками. Vanilla scripts целиком в мод не копировались. Проверять compiler success message + exit + artifact, не просто наличие файла: GFxExport может вернуть0 при Error в логе.

## 2026-10-02: request и seeded RNG oracle

Original copied IL request18/18 и RNG37/37 passed. Их manifests перечисляют exact copied methods и explicit shims/stubs; сообщения исключений RNG не проверяются. Это не whole-game traces. Generator переносит18 request observations в123 native checks. Их assertions прошли в версии15 (два batches failed0), но switch128 diagnostic сохранена в отдельной [приёмке](D:/w3mod/docs/evidence/request-runtime-accepted-20261002.json).

Board-compile18 exit0/blob71006bytes,16 sources и новый Flash приняты по трём116/104/123/43 batches без mod script errors. Кнопка поля запускает116/104/123/43 отдельно от текущего матча. Compile/receiver ABC3/request ABC8/resource guards5/runtime parser15 проверки прошли; FLOW43 и отсутствие switch diagnostic подтверждены. Live choices modal/target intents пока не наблюдались. Fixture logs не считаются действиями пользователя. [Manual check](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md), [подготовка версии18](D:/w3mod/docs/evidence/request-flow-development-result.json), [oracle workflow](D:/w3mod/tools/oracle/README.md).

## 2026-10-02: action queue boundary

Original21 methods с exact instruction checks и пять explicit boundary shims:36/36 fixtures passed. WS39:31 original observation IDs, два exception/guard differences и шесть added guards; debug-break observations не перенесены. Dispatch не исполняет real ApplyAction/effects. Board-compile20 exit0/blob80738bytes,18 sources; before/after compile input hashes совпадают. ACTION39 теперь принят в native20. Shared Action/Apply parser12 synthetic guards passed. Следующий шаг: bgapply_check() по BOARD_CHECK.md. См. [beta_actions.md](D:/w3mod/docs/beta_actions.md).


## Актуальная приёмка20 и подготовка21

Queue39/39 и два116/104/123/43 batches прошли 2026-10-02 13:07–13:09.
Live DEV choices/targets/end/abort и BOARD_CLOSED подтверждены.
Frozen native20-acceptance.json различает ошибки мода и оставшиеся engine
audio/HUD/native assertions. Индивидуальные toggle/Esc/reopen жесты в этой
трассе не следует объявлять отдельно доказанными; пользователь сообщил
успешное выполнение всех команд.

Original manager Apply49/49: четыре exact methods/24 external callbacks.
Direct Apply WS20 checks устанавливаются в21 и ещё ждут bgapply_check().
Compile21 successful20 sources/blob85867bytes;18 accepted20 files и Flash
неизменны. Preparation/native evidence разделены. Parser12 synthetic guards
проверяют также невозможность принять ACTION summary за APPLY batch.


## Native21 и manager26

17:07:53 APPLY20/20 failed0 принят,20 source copies/frozen log сохранены.
Original manager56/56 включает Int64 boundaries,4 exact methods/24 shims.
Новые86 native checks готовятся из56 recipes+30 local guards, не replay trace.
Shared parser12, suite parser16 и board parser15 synthetic checks прошли.
Compile26 exit0/blob121531bytes,22 inputs before/after active/authoritative
совпадают.19 prior files+GUI/Flash unchanged; queue authority binding changed,
поэтому bgmanager_check включает39/20 regression. Native suite пока pending.
Power111 methods прочитаны статически; effects/executed power fixtures отсутствуют.

## Numeric28 и следующий registry/death

Native26 queue39/Apply20/manager86 accepted, frozen source association22.
Original power18 exact methods/1 seam/40 passed; registry IDs4/no shims/16 passed.
Active28 numeric55 compile successful, no native evidence yet. Full current
source24/compiled hash/resource unchanged audit: power-number-preparation-audit.
Parser22 synthetic, Manager16/Action12 checks passed; do not label them native.
Registry allocator draft not installed/compiled.26 death/CardManager methods
static; next original fixtures before live event/death/ExecutionStack handlers.
[Queue](D:/w3mod/docs/deferred_checks.md).
