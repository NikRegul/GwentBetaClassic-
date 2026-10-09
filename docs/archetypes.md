# Архетипы: источник и границы использования

Источник: `D:\w3mod\Gwent-09-2025-Tierlist 6.0.pdf`. Титул — DIY Gwent 2025 Q3 Tierlist; metadata creation 2025-10-07. Это мета DIY спустя годы после original Beta. Пользователь подтвердил: использовать **только идеи архетипов**. Варианты могут отличаться несколькими tech cards; не создавать отдельный AI для каждого варианта.

Извлечены текст всех 27 страниц, каталог 46 статей и raw deck codes. Все страницы просмотрены в контактных листах; точный состав карт с изображений и соответствие кодов текущему CardMap не проверены. Не называть это импортом historical Beta decks.

## Каталог

Tiers здесь сохранены только как классификация самого PDF, не рейтинг Beta.

| Страница | Архетипы | Tier в PDF |
|---|---|---|
| 4–5 | Calveit Spies; Arachas Swarm; Drain Vampires | 1 |
| 6 | Crach Greatsword; Nekker Consume | High 2 |
| 7 | Dwarf-Elf Scorch; Eist Veterans | High 2 |
| 8 | Bloodmoon Wraiths; Anna Spalla Soldiers | High 2 |
| 9 | Aretuza Foltest; Eggs Consume | High 2 |
| 10 | Wild Hunt Frost; Tempo Calveit | High 2 |
| 11 | Adda Cursed; Scorch Ambush | High 2 |
| 12 | Henselt Machines; Queensguard | High 2 |
| 13 | Alchemy; Lyrian Machines | High 2 |
| 14 | Ointment Spallas; Swap | Low 2 |
| 15 | Temerians; Morvran Reveal | Low 2 |
| 16 | Deathwish; Lyrians Deckbuff | Low 2 |
| 17 | Fanatics; Discard | Low 2 |
| 18 | Ice Trolls; Eithne Handbuff | Low 2 |
| 19 | Brouver Shupe; 40 Foltest | Low 2 |
| 20 | Dwarf Miner/Xavier; Tall Ogres | Low 2 |
| 21 | Frost Wraiths; Francesca Handbuff | Low 2 |
| 22 | Brouver Handbuff; Cintrans | 3 |
| 23 | NG Handbuff; Cursed Ships | 3 |
| 24 | Svalblod Rain; Slave Infantry | 3 |
| 25 | Armor; Spell’atael Decoctions | 3 |
| 26 | Calanthe Deckbuff; Axemen | 4 |
| 27 | Dryads | 4 |

Источник доказывает version drift собственным текстом: Queensguard обсуждает DIY Warmonger/Pillager; Reveal — нового finisher Lady of the Lake; Aretuza Foltest — избегание power-crept DIY cards; Deathwish — Endrega eggs. Название архетипа, знакомое из Beta, не делает его 2025 decklist совместимым.

## Идеи, которые проверять первыми

Это proposal стратегии, не восстановленные списки Beta:

| Семейство | Faction/leader-кандидат | Core plan и ресурсы | Вопрос для Beta |
|---|---|---|---|
| Consume | Monsters / Arachas Queen | Setup Nekkers, copies/consumers, payoff короткого R3; сохранять combo resources | Какие exact cards и power были в 432 |
| Greatswords | Skellige / Crach | Greatsword + damage ships; engines длинного раунда, resurrect | Original sequencing/trigger ordering |
| Alchemy | Nilfgaard / Calveit | Witchers + alchemy, removal, tutors | Исключить новые alchemy карты DIY |
| Spies | Nilfgaard / Calveit | Engines/agents, tempo swings, card advantage | Убрать Azar/Caldwell/другие новые combo если отсутствуют в original |
| Reveal | Nilfgaard / Morvran | Reveal engines, known information, short-round finisher | Original finishers вместо DIY Lady |
| Machines | Northern Realms / Henselt | Setup matching machines, tutor/copy, engine removal | Original targets/leader limits |
| Discard/Resurrect | Skellige / Bran | Thin deck, graveyard preparation, resurrection/payoff | Original deck/target legality |
| Weather/Axemen | Skellige / original leader | Damage per turn, long round, weather resilience | Svalblod Rain не переносить как exact deck |
| Deathwish | Monsters / original leader | Death triggers/consume, tempo/carryover | Проверить eggs и changed cards |
| Handbuff/Swap | Scoia'tael / Francesca/Brouver/Eithne | Hand setup, tempo recovery, finisher | Original leader abilities и отсутствие DIY combos |

Mulligan targets/leader usage/pass должны выводиться из выбранного exact Beta decklist, а не из label. Для первой AI strategy разумны 1–2 механически проверенных семейства; 60–70 NPC decks позже получаются variants этих семейств с difficulty и reward profiles.

## Нормализация M2

Хранить source page/panel/hash, source version, faction/leader, exact card IDs/counts, core cards, tech slots, setup/engines/payoff, mulligan, round plan/pass/leader, incompatibilities. Для каждой карточки нужны original Template ID и version evidence.

DIY deck code кодирует **индекс CardMap**, а не canonical Beta ID. NumberConverter использует alphabet длиной 62, несмотря на имя To64; multiplicities/length markers в CommonFunctionalExtensions.CompressDeck/DeCompressToDeck. Изменение порядка/версии CardMap меняет значение кода. Текущая CardMapVersion=1.0.0.161; соответствие PDF 2025 этому словарю не доказано. Сохранять raw codes, не декодировать их в Beta автоматически.

Следующий M2 результат: небольшой проверенный каталог строгих Beta decks, с явным разграничением core и optional tech cards. Не модифицировать PDF и не обещать 46 legal Beta decks по этому документу.
