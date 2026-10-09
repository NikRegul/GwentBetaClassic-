# TW3 integration: контракты и неизвестные

## Вход

Confirmed hook: `r4Player.OnGwintGameRequested(deckName, forceFaction, additionalCards)`.

Adapter должен сохранить encounter context: legacy deckName, forced faction, additional vanilla cards, tutorial state, quest ownership request. NPC entity identity не передаётся явно в этом методе; mapping по существующему deckName наиболее доступен, но уникальность deckName ещё проверить по XML/quest graphs. Не утверждать, что уже можно восстановить NPC GUID из этого вызова.

Если request не поддержан profile, на раннем этапе оставлять vanilla fallback. Позже явно помечать unsupported encounters, не подставлять случайную колоду сюжетному NPC.

## Выход

Confirmed contract: player.SetGwintMinigameState(EMS_End_PlayerWon, EMS_End_PlayerLost, loss|forfeited); read method GetGwintMinigameState. OnGwintGameEnded очищает additionalCards.

Beta core returns {Winner, Draw, Forfeit, Abort, reason}. Adapter устанавливает vanilla result только один раз и завершает lifecycle; rewards/quest facts не должны выполняться внутри card effects.

**Vanilla draw contract раскрыт:** современный AS GwintEndGameDialog:275–283 преобразует PLAYER_INVALID в EndDefeat; FlowController.OnEndGameResult:1005 отправляет false; .ws при закрытии пишет EMS_End_PlayerLost. Beta core сохраняет Draw отдельно. Предложение для ordinary encounters — сохранить vanilla RPG mapping Draw→Lost, а replay оставить до окончательного close; сюжетные adapters проверять отдельно. Эта policy ещё не реализована и не проверена на quests.

Native scene/quest consumer пока не найден в доступных .ws; вероятно часть обработки native/resources, но это нужно подтвердить в REDkit. Не ставить произвольные victory facts вместо реального контракта.

## Коллекция и награды

Сохранять vanilla ownership/quest contracts отдельно от Beta owned counts. Vanilla GwintCard items выполняют AddGwentCard + tournament/achievement hooks. Нельзя автоматически перезаписать эти ID Beta ID или отключить AddGwentCard без анализа.

Предложение: compatibility mapping vanilla item/reward → Beta RewardProfile, одновременно сохранить необходимые legacy facts. Claims by encounter/reward ID исключают повторную first-win выплату. Merchant purchase/remove должны отражаться ровно один раз, не одновременно через old inventory callback и adapter.

Проверять IsGwentFactionPlayable (vanilla threshold22), UnlockSkelligeGwentDeck (direct native collection), CheckGwentTournamentDeck (weighted GwentTournament facts), collector achievement, almanac. Простой outcome adapter покрывает только win/loss, не эти проверки.

## UI lifecycle

Повторить observed conventions: EMPTY_CONTEXT store/restore, cursor, fade locks GwintStart/Gwint_EndFadeOut, ESGS_Gwent, soundbank lifecycle, popup deletion и forced faction cleanup. Core completion должен отработать при cancel, forfeit, exception и повторном открытии.

SWF view получает CardView/MatchView с уже посчитанными legal targets; выбранный intent всё равно проверяет core. Современные roots/callbacks подтверждены source/container audit; старый AIR Engine исключён из baseline. Пересборка FLA/SWF и новый bridge ещё требуют capability test. Definition names/descriptions и search index кэшировать вне per-frame path. Original localization rich tags преобразовать к TW3 supported markup.

## Save/Migration

В TW3 есть private saved var arrays и saved object refs; candidate host — существующий persisted player. Предложение BetaProfile fields: schemaVersion, dataVersion, owned IDs/counts, deck IDs/cards/leader, selectedDeck, claimedReward IDs, progression/settings.

Basic round-trip flat saved int/array на W3PlayerWitcher подтверждён runtime trace: ручное save/load сохраняет schema1, counter18 и два exact IDs, reseed не выполнялся. Поддержка нового nested profile object/large arrays/NG+ ещё не проверена. Для slice использовать flat saved arrays с явным version; не объявлять произвольный nested object автоматически безопасным. Default initialize на old save должен быть idempotent и не менять native vanilla collection.

Migrations sequential by schema; unknown newer version сохранять без разрушительной перезаписи. NewGamePlus и standalone DLC отдельно от обычного old save. Не сохранять runtime pending request/animation вместо устойчивого profile.

## Quest coverage queue

После установки: tutorial q001; ordinary first wins; fixed signature rewards; High Stakes; Skellige chain; HoS cg600; BoW cg700 tournament; forced-faction/additional-card encounters; deck readiness/ownership; reward/merchant/almanac/achievement. Для каждого: resource path → caller → input → outcome consumer → facts/reward → regression scenario.

Сейчас resource paths, callbacks, 56 XML collections, selected reward records и бинарные quest candidates найдены. Полная таблица NPC → Deck → AI → Reward отсутствует: generic collections переиспользуются, а string co-occurrence не устанавливает node связи. См. redkit_status.md и evidence/redkit-*.
