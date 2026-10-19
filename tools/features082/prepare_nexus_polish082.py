"""Prepare RU/EN Nexus descriptions and BBCode, preserving the original release copy."""
from pathlib import Path
import re,json,zipfile
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'docs/releases/0.8.2/nexus';OUT=ROOT/'docs/releases/0.8.2-polish1/nexus'
RU='''
## Как ИИ считает догон и отложенные эффекты

Догон после паса соперника проверяется симуляцией реального розыгрыша: выбор цели, броня, урон, гибель, цепочки способностей, конец хода и начало следующего хода с погодой. Сравнивается результат последовательности, а не только напечатанная сила карты. Последний пас закрывает раунд без очередного AfterTurn: ИИ не должен приписывать себе лишнее усиление движка. Пока человек ещё не спасовал, его следующий розыгрыш неизвестен; известные эффекты стола учитываются, ответы соперника оцениваются по публичной информации.

Игни выбирает ряд по порогу и фактическим целям уничтожения; Ирден сравнивает сброс силы на обеих сторонах. Бирна учитывает доступные ходы, броню, гибель целей и изменение порядка ряда. Прогноз включает восстановление брони Реданского рыцаря, бонус +5 Реданской элиты и отключение усилений оруженосца. Поэтому снятие брони не всегда полезно: иногда оно усиливает врага. Ловушки учитывают свободное место, перенос погоды — потерю прежнего эффекта и замену эффекта в новом ряду.

В первом раунде победа в минус одну карту допустима; минус две оцениваются по затратам и резерву. Необязательная погоня после паса, оставляющая минус три карты, останавливается. При угрозе поражения в матче сохранение ресурсов уступает необходимости выиграть раунд. Это правила принятия решений, а не обещание безошибочной игры во всех сочетаниях карт.

## Почему Classic 1.32 больше и зачем папка DLC

Classic и Next-Gen используют разные форматы ресурсов и загрузчики. Это две отдельные сборки из общей логики мода. Пакет 1.32 нельзя получить простым переименованием архива Next-Gen.

У загрузчика Classic есть ограничение около 32 МиБ на один асинхронно загружаемый ресурс. Большие меню и графические страницы подготовлены для этого ограничения: используются ресурсы старого формата, отдельные страницы и дополнительные привязки текстур. Сохранены принятые изображения, портреты и анимации. Простое сильное сжатие ZIP не устраняет ограничение движка: он проверяет размер загружаемого ресурса.

Папка DLC/dlcBetaGwentClassic132Assets содержит обязательный пакет графических ресурсов и регистрации для загрузчика Classic, в том числе страницы вступлений лидеров. Это техническая часть мода, дополнительного сюжета она не добавляет. Без неё часть интерфейса и анимаций не сможет найти свои ресурсы. Она не заменяет Hearts of Stone или Blood and Wine и не должна копироваться внутрь Mods.

В предыдущей пересборке этой же 0.8.2 ZIP Classic занимал около 623 МБ, Next-Gen — 448 МБ (десятичные МБ). Примерно 105 МБ сжатого архива Classic приходились на DLC; остальное отличие связано с подготовкой и упаковкой ресурсов старого движка. Сам DLC bundle без ZIP-сжатия — около 191 МБ и содержит 336 записей. Это не больше карт или правил: содержание коллекции и логика ИИ общие. Точные размеры текущих файлов указаны на вкладке Files и в контрольных суммах.

Для 1.32 нужны ОБЕ папки из архива: Mods/modBetaGwentClassic132 и DLC/dlcBetaGwentClassic132Assets. Для Next-Gen устанавливается Mods/modBetaGwent0924. Одновременно обе версии не ставятся. Для игры пользователю не нужны REDkit, Wwise или компиляторы.

## Что именно сделано для Redux

При загрузке старого сохранения движок должен знать определения предметов, уже находящихся в инвентаре. У Redux встречаются названия карт, которых нет среди штатных определений. После удаления их прежнего поставщика загрузка такого инвентаря могла повреждать его состояние, вплоть до исчезновения тела/инвентаря.

Встроен проверенный список из 400 названий: 197 уже обслуживаются штатными определениями; для оставшихся 203 добавлены инертные определения. Они находятся в обоих наборах items и items_plus, чтобы охватывать обычное прохождение и НГ+. Штатные 197 определений не заменяются. Заглушки не имеют шаблона предмета, слота экипировки, действий или способности; помечены как скрытые предметы без веса и цены. Их задача — дать загрузчику распознать старые записи, а не вводить в игру дополнительные карты Redux.

Используйте сохранение ДО исчезновения тела или инвентаря. Если потеря уже произошла и была сохранена, эти определения не восстановят прежние вещи. Это не перенос коллекции Redux в Beta Gwent и не гарантия совместимости со всем Redux/Redo Expansion. Другие изменения гвинта, меню, торговли и наград могут конфликтовать. Отдельная старая папка modBetaGwentReduxCompat больше не нужна рядом с полной 0.8.2.

## Обновление, сохранения и удаление

Перед обновлением сохраните резервную копию. Полностью заменяйте только папки этого мода подходящим пакетом; не смешивайте файлы разных версий и не удаляйте чужие Mods/DLC. В Classic обновляйте также DLC-папку мода. После изменения состава модов заново проверьте Script Merger; готовое старое объединение может содержать прежние скрипты.

Коллекция, колоды, осколки, бочки, настройки и награды сохраняются в профиле и резервных фактах. Поэтому простое удаление папки мода не равно очистке его прогресса: после возвращения мода резервная копия может восстановиться. Для удаления профиля подготовлен отдельный временный мод очистки с отдельной инструкцией. Он требует явной консольной команды; обычная установка основной сборки ничего не очищает. Завершённые квесты, полученные достижения и уже потраченные кроны назад не откатываются.

У старого профиля могут остаться факты наград NPC, идентификаторы которых уже отсутствуют в текущем массиве наград. Для них есть дополнительный сканер, который только читает выбранную копию .sav и формирует список команд очистки. Он не редактирует и не отправляет сохранение. Без проверки этого списка нельзя обещать физическое отсутствие каждой старой записи. При удалении встроенных определений Redux старым предметам вновь нужен поставщик определений — например, восстановленный исходный мод Redux.

## Что проверено и что ещё требует игры

Проверки выполняются на коде 0.8.2: матрица 46 колод, выбор целей и рядов, экономика раундов, скрытая информация, цепочки карт, погода и три реданских способности. Проверяется последовательность известных тиков до следующего хода. Интерфейс проверяется на компиляцию, привязки, ограничения размеров, зеркала исходников, размещение элементов и подгонку переведённых кнопок после загрузки шрифтов.

Нативная компиляция, проверки контейнеров и сценарии хоста не заменяют игровую приёмку: загрузку своего сохранения, партию с NPC, сохранение/перезапуск и визуальную проверку на своём разрешении. Улучшения ИИ не означают, что перебраны все возможные состояния игры. Для отчёта приложите версии игры/мода, колоды и карты, порядок ходов, выбранные языки, другие моды и скриншот; особенно полезно сохранение перед проблемой.
'''
EN='''
## AI catch-up, engines and weather

After the opponent passes, catch-up uses real play simulation: targets, armour, damage, deaths, ability chains, turn-end effects and the next turn-start weather. The final pass ends the round without another AfterTurn tick. When the human is still playing, their next card is unknown; public board effects and plausible replies inform evaluation.

Igni compares the row threshold and actual burn targets. Yrden evaluates resets on both sides. Birna forecasts available turns, armour depletion, deaths and shifting row order, including Redanian Knight armour renewal, Redanian Elite's +5 and the Squire's adjacent boosts. Removing armour can benefit the enemy. Traps consider row capacity; weather movement includes the effect lost at the origin and replaced at the destination.

Winning round one one card down is acceptable; two cards down requires context. Optional post-pass chasing stops at a three-card disadvantage. Avoiding match defeat overrides resource preservation. These policies do not promise perfect play in every possible state.

## Why the Classic 1.32 download is larger and needs DLC

Classic and Next-Gen use different native resource formats and loaders. Classic has an approximately 32 MiB limit per asynchronously loaded resource. Large menus and graphics therefore need a layout suitable for the old engine, separate pages and additional texture bindings. Compressing the ZIP cannot bypass the engine's resource-size check.

DLC/dlcBetaGwentClassic132Assets is an essential technical asset package, including leader entrance pages and Classic loader registration. It adds no story content and does not replace either official expansion. Install it into the game's DLC directory, alongside Mods/modBetaGwentClassic132. Missing it can leave interface or animation resources unavailable. Next-Gen uses Mods/modBetaGwent0924; install only the package for your game version.

The preceding 0.8.2 rebuild measured about 623 MB for Classic and 448 MB for Next-Gen (decimal MB). About 105 MB of Classic's compressed archive was its DLC folder. That DLC bundle holds 336 entries and is about 191 MB before ZIP compression. The remaining difference comes from old-engine resource preparation and packaging, not extra cards or different AI rules. See Files and checksums for exact current sizes. Players do not need REDkit, Wwise or build tools.

## Redux inventory compatibility: exact scope

Loading an old save requires definitions for item names already stored in its inventory. Removing a mod that supplied those names could corrupt loading, including disappearing inventory/body symptoms. The audited list covers 400 names: 197 already have native definitions, while 203 missing names receive inert placeholders in both items and items_plus for ordinary play and NG+.

Native definitions are not replaced. Placeholders have no equipment/hold slot, entity template, actions or abilities; they are hidden, weightless and have no value. This supports deserialization of legacy items. It does not convert Redux cards into the Beta Gwent collection or guarantee compatibility with every Redux/Redo Expansion feature.

Load a backup from BEFORE the loss. Already lost and saved items cannot be recovered by these definitions. The old separate modBetaGwentReduxCompat folder is unnecessary beside full 0.8.2. Other Gwent/menu/trading/reward overhauls can still conflict; update Script Merger merges after changing mods.

## Updating, saves and uninstalling

Back up saves first. Replace only this mod's own folders completely, using the correct platform package; update its DLC folder on Classic too. Do not mix versions or delete unrelated Mods/DLC.

Collection, decks, scraps, kegs, settings and rewards have saved fields and facts mirrors. Removing the mod alone does not erase that progress: reinstalling can restore it. A separate temporary cleaner and instructions are provided; cleanup requires an explicit console command and never runs merely by installing the main mod. Completed quests, achievements and spent crowns are not rolled back.

Orphaned NPC reward facts require the optional read-only save fact scanner and its generated cleanup commands. It does not edit or upload the save. Without checking those keys, complete physical removal of historical records cannot be guaranteed. If legacy Redux inventory items remain after uninstalling these definitions, reinstall their original definition provider, such as Redux, before loading.

## Validation limits

Checks target 0.8.2: all 46 decks, targets/rows, round economy, hidden information, card chains, weather and the three Redanian abilities. UI checks cover compilation, bindings, resource budgets, source mirrors, layout and translated button fitting after font loading.

Native compilation, container checks and host scenarios do not replace gameplay acceptance: loading your save, an NPC match, saving/restarting and visual checks at your resolution. No finite test suite covers every game state. Bug reports should include game/mod versions, decks/cards, move order, languages, other mods and a screenshot; a save immediately before the issue is especially useful.
'''
def bbcode(s):
    s=re.sub(r'^### (.*)$',r'[b]\1[/b]',s,flags=re.M);s=re.sub(r'^## (.*)$',r'[size=5][b]\1[/b][/size]',s,flags=re.M);s=re.sub(r'^# (.*)$',r'[size=6][b]\1[/b][/size]',s,flags=re.M)
    s=re.sub(r'```[^\n]*\n(.*?)```',r'[code]\1[/code]',s,flags=re.S);s=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',r'[url=\2]\1[/url]',s)
    s=re.sub(r'^> ', '', s,flags=re.M);s=re.sub(r'`([^`]+)`',r'\1',s)
    lines=s.splitlines();out=[];active=False
    for line in lines:
        if line.startswith('- '):
            if not active:out.append('[list]');active=True
            out.append('[*]'+line[2:])
        else:
            if active:out.append('[/list]');active=False
            out.append(line)
    if active:out.append('[/list]')
    return '\n'.join(out)+'\n'
def main():
    for lang,extra in [('ru',RU),('en',EN)]:
        target=OUT/lang;target.mkdir(parents=True,exist_ok=True)
        source=(BASE/lang/'description.md').read_text('utf-8-sig');source=source.replace('## Благодарности',extra+'\n## Благодарности') if lang=='ru' else source.replace('## Credits',extra+'\n## Credits')
        assert extra in source,lang
        (target/'description.md').write_text(source,'utf8');(target/'description.bbcode.txt').write_text(bbcode(source),'utf8')
        changes=(BASE/lang/'changelog.md').read_text('utf-8-sig')
        changes+='\n'+('## Дополнение: ИИ и интерфейс\n\n- Исправления выбора рядов и прогноз брони/погоды, экономика догона, подгонка переведённых кнопок после загрузки шрифта, многострочная история, отступы окон ввода и истории.\n' if lang=='ru' else '## AI and interface update\n\n- Row choice and armour/weather forecasts, catch-up economy, translated button fitting after font loading, multiline history and input/history window spacing.\n')
        (target/'changelog.md').write_text(changes,'utf8');(target/'changelog.bbcode.txt').write_text(bbcode(changes),'utf8')
    print(OUT)
if __name__=='__main__':main()
