# Vanilla TW3 Gwent: карта зависимостей

База прочитанных scripts: `F:\Steam\steamapps\common\The Witcher 3\content\content0\scripts`. Слово в путях — **gwint**, многие API используют Gwent/Gwint вперемешку.

## Запуск и завершение — подтверждённые chains

```text
Внешний запрос (native quest/scene caller пока не раскрыт)
→ game/player/r4Player.ws: OnGwintGameRequested(deckName, forceFaction, additionalCards)
→ CR4GwintManager.SetEnemyDeck / SetAdditionalCards / SetForcedFaction
→ RequestMenu('DeckBuilder') или tutorial dialog
→ deckBuilderMenu.OnClosingMenu при gameRequested
→ RequestMenu('GwintGame')
→ gwintGameMenu.OnConfigUI: templates, values, decks, names → Flash
→ OnMatchResult(pWon): playerWon
→ OnClosingMenu: SetGwintMinigameState(EMS_End_PlayerWon/Lost/Forfeited)
→ engine/quest consumers результата (ещё исследовать)
```

Ссылки на строки: r4Player.ws:4133,4163; deckBuilderMenu.ws:76,98; gwintGameMenu.ws:64,106,228. OnGwintGameEnded очищает additionalCards (r4Player.ws:4155). Утрата этого cleanup может повлиять на следующего NPC.

## Границы native/script/Flash

`game/gui/menus/gwintManager.ws`: import class CR4GwintManager extends IGameSystem. GetCardDefs, GetLeaderDefs, GetDeck, GetPlayerCollection, AddCardToCollection, GetFactionDeck/SetFactionDeck и tutorial flags — import final functions. Их реализация не находится в этих .ws; native save layout неизвестен.

`gwintBaseMenu.ws`: CScriptedFlashObject/Array, SendCardTemplates → `gwint.card.templates`; StoreContext('EMPTY_CONTEXT'), ResetFadeLock('GwintStart'), FadeInAsync; closing восстанавливает input context.

`gwintGameMenu.ws`: Flash methods winGwint, setFirstTurn, showTutorial, AI toggle; deck/card data передаётся через value storage. Полная turn/round/card-resolution реализация находится в ActionScript, найденном в REDkit. SWF SymbolClass связывает текущие меню с `gameplay/gui_new/actionscript/red/game/witcher3/menus/gwint`; карта и ограничения в [redkit_status](D:/w3mod/docs/redkit_status.md). Старый AIR `gameplay/gui_new/gwint/Engine` использует другой callback и не является текущим integration baseline.

Ресурсы установленного REDkit доступны без `.download`:

- `r4data/gameplay/gui_new/swf/gwint/gwint_game.swf` и .redswf.
- `.../deck_builder.swf` и .redswf.
- `r4data/gameplay/items/def_gwint_cards_final.xml`, def_gwint_king_cards.xml, def_gwint_battle_king_cards.xml, def_gwint_decks.xml, def_item_gwint.xml.
- Есть counterparts items_plus; все пять пар побайтово одинаковы. Выбор runtime mount пока не подтверждён.

XML содержит 206 card definitions, 22 battle leader records, 197 inventory items и 56 deck collections / 168 difficulty variants в одном наборе. Starting/template/generic/signature collections не считать отдельными NPC. dynamicCards использует item names и difficulty; full native semantics ещё проверить. Сохранены redkit-gwent-xml.json и redkit-deck-catalog.csv.

## Данные, коллекция, экономика

SCardDefinition: cardName/title/itemName/description/power/picture/faction/typeFlags/effectFlags/summonFlags. SDeckDefinition: deckName, leaderCard, specialCard, difficulty, cards, unlocked. Это модель vanilla, не модель Beta.

При получении item: inventoryComponent.ws:4794 проверяет tag GwintCard → W3PlayerWitcher.AddGwentCard(itemName, amount):9699 → GetCardNameFromItemName/GetGwentCard → AddCardToCollection; устанавливается Gwint_Card_Looted и tutorial/faction/tournament facts. При удалении inventory:995 → RemoveGwentCard:9841 → RemoveCardFromCollection.

`gwintManager.OnGwintSetupNewgame`: native faction decks/starting cards. `OnGwintSetupSkellige` — отдельный начальный deck. Quest function UnlockSkelligeGwentDeck:6630 напрямую добавляет vanilla cards в native collection и ставит skel_gwint_base_deck_given.

Торговцы: cards — предметы inventory. Показанная add/remove chain применима к acquisition; конкретные shop inventories и reward tables ещё не прочитаны. Merchant fact pattern в quest_function.AddAllGwentCards: `merchant_card_<itemName>_already_given`.

## Квесты и special encounters

Прочитанные script hooks:

| Категория | Символ / источник |
|---|---|
| Проверка faction playable | quest_function.ws:6591 IsGwentFactionPlayable; считает vanilla creature copies и сравнивает с 22 |
| Forced faction | ForceGwentFaction:6673 и manager.SetForcedFaction |
| Дополнительные карты | gwintManager.SetAdditionalCards/AddAdditionalEnemyCards |
| Tournament readiness | playerWitcher.CheckGwentTournamentDeck:9946, HasGwentTournamentDeck, GwentTournamentObjective1/2/3 |
| Tutorial | r4Player.StartGwint_TutorialOrSkip; r4guimanager skip dialog; journal entries |
| Rewards/ownership | inventory tags + AddGwentCard/RemoveGwentCard + native collection |

REDkit имеет cg600_gwent (HoS), cg700_card_game/cg700_gwent_players (BoW), q001_academic/scenes и Gwent journals. Бинарные minigame class hits выявили High Stakes `quests/sidequests/novigrad/sq306_maverick.w2phase`, meta `quests/generic_quests/card_minigame_all_hubs/cg_card_minigame_meta.w2phase` и BoW cg700 quest resources. 69 generic minigame candidates, 39 с CGwintMinigame string; это не распарсенные node connections. Rewards XML прочитан отдельно: sq306 fixed card items и cg700 tournament/wager payouts подтверждены data. NPC → deck/reward binding ещё не установлен.

## Save, HUD, localization

Vanilla collection/decks сохраняются через native manager; формат не установлен. В playerWitcher есть `saved var` arrays и saved object reference reputationManager — реальная script persistence convention, но новый Beta profile ещё нужно проверить на round trip.

HUD/input: GwintGame — меню со своим Flash surface, cursor, input context, fades, sound bank gwint_ep2.bnk и ESGS_Gwent. Полноценную отдельную HUD схему не обнаружено; menu lifecycle следует сохранять адаптером.

Локализация: GetLocStringByKeyExt, ReplaceTagsToIcons, title/description keys, tutorial journal refs. Beta CSV rich text нельзя передавать как готовую TW3 строку без преобразования/проверки тегов и font coverage.

## Следующие проверки

Выполнена сверка installed REDkit scripts с TW3: 1524 из 1527 одинаковы, релевантные Gwent hooks совпали. User depot готов, проект найден в D:\w3mod\GwentB\myproject1; отдельный script capability probe успешно собран в .rsblob. Далее читать minigame node properties/connections, shop acquisition и проверять runtime save/load/UI. Современные AS FSM/AI/effects chains найдены, full behavior/binary parity ещё не проверены.
