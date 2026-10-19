"""Prepare the requested multilingual Nexus description and EN/RU release post."""
from pathlib import Path
import sys,json,re,zipfile,hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'docs/releases/0.9.0/nexus'
spec=importlib.util.spec_from_file_location('nexus_bb',ROOT/'tools/universal/prepare_nexus081.py')
bb=importlib.util.module_from_spec(spec);spec.loader.exec_module(bb)
ORDER=['en','ru','de','fr','it','pl','es','es-mx','pt-br','ja','ko','zh-cn','zh-tw']
NAMES=dict(zip(ORDER,['English','Русский','Deutsch','Français','Italiano','Polski','Español (España)','Español (Latinoamérica)','Português (Brasil)','日本語','한국어','简体中文','繁體中文']))
OUTLAW={
'en': 'Isengrim: Outlaw now compares the actual special-card and Create branches, including when pulled by Royal Decree. The AI rejects Decoy without a legal allied Bronze or Silver target and estimates Create from its random three-card offer, without reading future random choices.',
'ru': 'Изенгрим: Изгой сравнивает реальную ценность веток особой карты и создания эльфа, в том числе после Королевского указа. ИИ не выбирает Чучело без допустимого союзного бронзового или серебряного отряда. Создание оценивается по случайной тройке предложений, без знания будущего результата генератора.',
'de': 'Isengrim: Gesetzloser vergleicht nun Sonderkarte und Erschaffen, auch nach Königlichem Erlass. Die KI vermeidet eine Vogelscheuche ohne gültiges verbündetes Bronze- oder Silberziel und bewertet die zufällige Auswahl aus drei Karten, ohne künftige Zufallsergebnisse zu kennen.',
'fr': 'Isengrim : Hors-la-loi compare les branches carte spéciale et création, même après Décret royal. L’IA écarte Leurre sans cible alliée Bronze ou Argent valide et estime la création à partir des trois propositions aléatoires, sans connaître les prochains tirages.',
'it': 'Isengrim: Fuorilegge confronta ora carta speciale e creazione, anche dopo Decreto reale. L’IA evita Esca senza un bersaglio alleato Bronzo o Argento valido e valuta la scelta casuale fra tre carte senza conoscere i risultati futuri.',
'pl': 'Isengrim: Wygnaniec porównuje teraz kartę specjalną i tworzenie elfa, także po Dekrecie królewskim. SI unika Manekina bez prawidłowego sojuszniczego celu brązowego lub srebrnego i ocenia losową ofertę trzech kart bez podglądania przyszłych wyników.',
'es': 'Isengrim: Proscrito compara ahora carta especial y creación, también tras Decreto real. La IA evita Señuelo sin un objetivo aliado de Bronce o Plata válido y calcula la oferta aleatoria de tres cartas sin conocer resultados futuros.',
'es-mx': 'Isengrim: Proscrito compara ahora carta especial y creación, también tras Decreto real. La IA evita Señuelo sin un objetivo aliado de Bronce o Plata válido y calcula la oferta aleatoria de tres cartas sin conocer resultados futuros.',
'pt-br': 'Isengrim: Fora da Lei compara carta especial e criação, inclusive após Decreto Real. A IA evita Isca sem alvo aliado Bronze ou Prata válido e estima a oferta aleatória de três cartas sem conhecer resultados futuros.',
'ja': 'イセングリム：無法者は「勅令」経由でも特殊カードと生成の価値を比較します。有効な味方のブロンズ・シルバー対象がなければ囮を選びません。生成はランダムな3枚の候補から評価し、将来の乱数結果は参照しません。',
'ko': '아이센그림: 무법자는 왕실 칙령으로 나와도 특수 카드와 생성의 가치를 비교합니다. 유효한 아군 브론즈 또는 실버 대상이 없으면 미끼를 선택하지 않습니다. 생성은 무작위 후보 3장을 기준으로 평가하며 미래 난수 결과는 보지 않습니다.',
'zh-cn': '伊森格林：亡命之徒现在会比较特殊牌与创造分支的价值，包括由皇家谕令打出时。没有合法的己方铜色或银色目标时，AI不会选择诱饵。创造按随机提供的三张候选牌估值，不读取未来的随机结果。',
'zh-tw': '伊森格林：亡命之徒現在會比較特殊牌與創造分支的價值，包括由皇家諭令打出時。沒有合法的己方銅色或銀色目標時，AI不會選擇誘餌。創造按隨機提供的三張候選牌估值，不讀取未來的隨機結果。',
}

# Extra sections supplement the already translated full descriptions. Existing
# features, requirements, languages, logging and credits stay in every language.
EXTRA={
'en':[
'AI and interface',
'''The AI has revised Igni and Yrden evaluation, Birna weather forecasts and armour interactions, including the Redanian Knight, Elite and Squire. After the opponent passes, catch-up follows real plays, deaths, armour and turn boundaries; a final pass does not grant an extra engine tick. Forecasts consider the available turns, rather than treating every weather card as guaranteed full-duration damage. An armour break that gives the enemy +5 can be a bad target.

In round one, a one-card disadvantage can be worthwhile; two cards require context, and optional post-pass chasing stops before a three-card disadvantage. Avoiding match defeat takes priority. Opponents' future cards are unknown: these are improved decisions, not a guarantee of perfect play. Translated buttons now fit again after fonts load; editor actions, history and input windows have revised spacing.''',
'Why Classic 1.32 is larger and needs the DLC folder',
'''Download one package for your game version. Classic is about 623 MB, Next-Gen about 448 MB; both have the same cards and AI. Classic uses a different native resource format and an older loader with an approximately 32 MiB limit per asynchronously loaded resource. Its graphics need separate pages and texture bindings; ZIP compression cannot bypass that limit.

Classic must include both Mods/modBetaGwentClassic132 and DLC/dlcBetaGwentClassic132Assets. The DLC folder supplies essential graphics and loader registration, including leader entrance pages; it adds no story content and does not replace either official expansion. About 105 MB of the Classic download belongs to this folder; the remaining size difference comes from resource preparation for the old engine. Next-Gen uses Mods/modBetaGwent0924. Players do not need REDkit, Wwise or build tools.''',
'Redux: what the compatibility layer does',
'''The audited list contains 400 legacy item names: 197 keep their native definitions and 203 missing definitions are supplied as inert placeholders, for both normal games and New Game+. They are hidden, weightless and have no value, equipment slots or abilities. This helps the engine recognize old inventory entries after switching mods. It does not convert Redux cards into the Beta collection, recover inventory already lost and saved, or establish compatibility with every Redux/Redo feature. Use a save from before any loss; remove the obsolete modBetaGwentReduxCompat folder. If legacy Redux items remain when uninstalling, restore their original definition provider before loading.''',
'Built-in cleanup before uninstalling',
'''Cleanup is included in the main 0.9.0 mod. No separate cleaner download is needed. Back up your save, finish Gwent, leave combat and close all menus. With the main mod still installed, bg_clean_preview() shows instructions without changing data. Explicitly confirm with:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

This clears the Beta collection, decks, scraps, kegs, settings, known reward ledgers, both backup banks and betagwent_* items in the player's current inventory. A saved uninstall flag prevents starter grants and backup restoration, including after reloading with the mod still installed. Save to a NEW slot, exit the game, remove this mod's folders (including its Classic DLC), rebuild affected Script Merger merges, load the new slot and save again. To cancel, load your original backup.

Completed quests, achievements and spent crowns are not rolled back. The command does not traverse unloaded merchants, stash or world containers; retrieve Beta items first. Orphaned reward facts can require the included read-only save_fact_index.py and bg_clean_keys('…') after confirmation. See BetaGwentDocs/CLEANUP_EN.md. This is profile cleanup, not a certification that every historical byte of an arbitrary save has been erased.''',
'Towards 1.0',
'''The releases leading to 1.0 will focus on translation corrections, bug fixes and further AI and interface refinement. Native compilation and automated scenarios do not replace in-game checks at your resolution or a real save/load test after cleanup. Please report reproducible problems.''',
'''Export displays a language-independent BG1 text code. The in-game clipboard may remain internal to Scaleform, so a “copied” message is not proof that another application can paste it. Select the code and try Ctrl+C. If external pasting fails, start the game with -debugscripts, export again, then run Copy-Deck-Code.cmd from the extracted archive: it reads the latest exported code from scriptslog.txt and places it in the Windows clipboard. Paste into your message with Ctrl+V. The helper does not run automatically, edit saves or send messages. Import accepts the complete BG1 code in its text field.'''],
'ru':[
'ИИ и интерфейс',
'''Исправлены оценка Игни и Ирдена, прогноз погоды Бирны и взаимодействия с бронёй Реданского рыцаря, элиты и оруженосца. После паса соперника догон учитывает реальные розыгрыши, гибель, броню, конец и начало хода. Последний пас не добавляет лишний тик движков. Погода оценивается с учётом оставшихся ходов: снятие брони, которое даст врагу +5, может быть невыгодным.

В первом раунде минус одна карта допустима, минус две требуют оценки ситуации. Необязательная погоня после паса останавливается перед минус тремя картами; при угрозе поражения в матче важнее выиграть раунд. ИИ не знает будущих карт соперника, улучшения не обещают идеальной игры. Подписи кнопок повторно подгоняются после загрузки шрифтов; выровнены действия редактора, история и окна ввода.''',
'Почему Classic 1.32 больше и зачем папка DLC',
'''Для Classic и Next-Gen нужны разные архивы. Classic занимает около 623 МБ, Next-Gen — 448 МБ; карты и логика ИИ у них одинаковые. У старого загрузчика Classic есть ограничение около 32 МиБ на один асинхронно загружаемый ресурс. Поэтому графика подготовлена в старом формате, с отдельными страницами и дополнительными привязками текстур. Сжатие ZIP не отменяет ограничение движка.

В 1.32 обязательны обе папки: Mods/modBetaGwentClassic132 и DLC/dlcBetaGwentClassic132Assets. DLC содержит графические ресурсы и регистрацию для загрузчика, включая страницы вступлений лидеров. Это техническая часть мода, без нового сюжета; официальные дополнения она не заменяет. На DLC приходится примерно 105 МБ сжатого архива Classic; остальная разница связана с подготовкой ресурсов под старый движок. Для Next-Gen используется Mods/modBetaGwent0924. REDkit, Wwise и инструменты сборки игроку не нужны.''',
'Что сделано для совместимости с Redux',
'''Проверены 400 старых названий предметов: 197 используют штатные определения, для 203 отсутствующих добавлены инертные определения в обычное прохождение и НГ+. У них нет веса, цены, слотов экипировки или способностей; они скрыты в инвентаре. Это помогает движку распознать старые записи после смены модов. Коллекция Redux не превращается в коллекцию беты, уже потерянный и сохранённый инвентарь не восстанавливается; совместимость со всеми функциями Redux/Redo не заявляется. Нужен сейв до потери данных. Удалите старую папку modBetaGwentReduxCompat. Если при удалении мода остаются предметы Redux, перед загрузкой верните исходный мод, предоставляющий их определения.''',
'Встроенная очистка перед удалением мода',
'''Очиститель включён в основной мод 0.9.0; отдельный архив устанавливать не нужно. Сделайте резервную копию сейва, завершите партию, выйдите из боя и закройте меню. Пока основной мод установлен, bg_clean_preview() покажет инструкцию без изменения данных. Для подтверждения введите:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Удаляются коллекция беты, колоды, осколки, бочки, настройки, известные наградные записи, оба банка резервных фактов и предметы betagwent_* из текущего инвентаря игрока. Сохраняемый флаг блокирует повторную выдачу стартовых колод и восстановление профиля даже после перезагрузки с установленным модом. Сохранитесь В НОВЫЙ СЛОТ, выйдите из игры, уберите папки мода (для Classic — также его DLC), обновите затронутые объединения Script Merger, загрузите новый слот и сохранитесь ещё раз. Для отмены загрузите исходную резервную копию.

Завершённые квесты, достижения и потраченные кроны не откатываются. Команда не обходит выгруженных торговцев, тайник и контейнеры мира: сначала заберите оттуда предметы беты. Для старых наградных фактов может потребоваться приложенный сканер save_fact_index.py и bg_clean_keys('…') после подтверждения очистки. Подробности — BetaGwentDocs/CLEANUP_RU.md. Это очистка профиля, без обещания физического удаления каждой исторической записи произвольного сейва.''',
'Дальше — к 1.0',
'''До 1.0 основной упор будет на исправления перевода и ошибок, дальнейшую доработку ИИ и интерфейса. Компиляция и автоматические сценарии не заменяют проверку в самой игре на своём разрешении и сохранение/перезагрузку после очистки. Присылайте воспроизводимые проблемы.''',
'''Экспорт показывает код колоды BG1, который не зависит от языка. Внутриигровой буфер может оставаться внутри Scaleform: сообщение об успехе не доказывает, что код вставится в другое приложение. Выделите код и попробуйте Ctrl+C. Если вставка не работает, запустите игру с -debugscripts, снова экспортируйте колоду и запустите Copy-Deck-Code.cmd из распакованного архива. Он прочитает последний экспортированный код из scriptslog.txt и поместит его в буфер Windows; затем вставьте его в сообщение через Ctrl+V. Скрипт не запускается сам, не меняет сейвы и ничего не отправляет. Импорт принимает полный код BG1 в текстовом поле.'''],
'de':[
'KI und Oberfläche',
'Igni, Yrden, Birnas Wetterprognose und die Rüstungsfähigkeiten von Redanischem Ritter, Elite und Knappen werden besser bewertet. Nach einem Pass berücksichtigt das Aufholen echte Spielzüge und Zugwechsel. Ein letzter Pass erzeugt keinen zusätzlichen Effekt. In Runde eins ist eine Karte Nachteil vertretbar; zwei erfordern Abwägung, drei werden beim freiwilligen Aufholen vermieden. Ein drohender Matchverlust hat Vorrang. Übersetzte Schaltflächen und Fensterabstände wurden überarbeitet.',
'Classic 1.32: Größe und DLC',
'Classic benötigt etwa 623 MB, Next-Gen 448 MB bei denselben Karten und Regeln. Das alte Ressourcenformat und die Grenze von etwa 32 MiB pro asynchron geladener Ressource erfordern getrennte Grafikseiten. Für Classic beide Ordner Mods und DLC installieren: DLC/dlcBetaGwentClassic132Assets enthält notwendige Grafik und deren Registrierung, keine neue Handlung. Etwa 105 MB des Downloads entfallen darauf; der Rest des Größenunterschieds entsteht durch die Aufbereitung für die alte Engine.',
'Redux',
'Von 400 geprüften alten Gegenstandsnamen behalten 197 ihre nativen Definitionen; 203 fehlende erhalten in normalen Spielen und NG+ inerte Definitionen. Sie sind unsichtbar, gewichtlos und wertlos. Bereits verlorenes Inventar wird nicht zurückgeholt. Beim Entfernen braucht verbleibendes Redux-Inventar wieder den ursprünglichen Anbieter seiner Definitionen.',
'Integrierte Bereinigung vor dem Entfernen',
'''Kein separater Cleaner nötig. Spielstand sichern, Partie beenden, Kampf und Menüs verlassen. bg_clean_preview() zeigt nur Hinweise. Mit installiertem Hauptmod ausdrücklich bestätigen:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Sammlung, Decks, Ressourcen, Einstellungen, bekannte Belohnungen, Sicherungsspiegel und betagwent_*-Gegenstände im Spielerinventar werden gelöscht. Eine gespeicherte Sperre verhindert die Wiederherstellung, auch nach erneutem Laden. In NEUEM Slot speichern, Spiel beenden, Mod samt Classic-DLC entfernen, Script Merger aktualisieren, neuen Slot laden und erneut speichern. Quests, Erfolge und ausgegebene Kronen bleiben. Unbeladene Händler, Lager und Weltbehälter werden nicht durchsucht. Für verwaiste Belohnungsfakten stehen save_fact_index.py und bg_clean_keys('…') nach Bestätigung bereit. Eine vollständige physische Löschung jeder historischen Speicherstelle wird nicht zugesichert.''',
'Bis 1.0',
'Bis 1.0 stehen Übersetzungen und Fehlerkorrekturen sowie weitere KI- und Oberflächenverbesserungen im Mittelpunkt. Automatische Tests ersetzen keine Prüfung im Spiel oder einen echten Speicher-/Ladedurchlauf nach der Bereinigung.',
'Export zeigt einen BG1-Textcode. Der Spiel-Clipboard kann intern bleiben: Code markieren und Strg+C versuchen. Wenn externes Einfügen scheitert, mit -debugscripts starten, erneut exportieren und Copy-Deck-Code.cmd aus dem entpackten Archiv ausführen. Das Hilfsskript kopiert den neuesten Export aus scriptslog.txt in die Windows-Zwischenablage. Danach mit Strg+V in eine Nachricht einfügen. Es startet nicht automatisch, verändert keine Spielstände und versendet nichts. Import nimmt den vollständigen Code im Textfeld an.'],
'fr':[
'IA et interface',
'L’évaluation d’Igni, d’Yrden, de la météo de Birna et des capacités d’armure du chevalier, de l’élite et de l’écuyer rédaniens a été améliorée. Après un passe, le calcul suit les actions et les changements de tour réels ; le dernier passe ne donne aucun effet supplémentaire. Au premier round, perdre une carte peut être acceptable, deux demandent une évaluation et trois sont évitées lors d’une poursuite facultative. Éviter de perdre le match reste prioritaire. Les boutons traduits et les espacements ont été revus.',
'Classic 1.32 : taille et dossier DLC',
'Classic occupe environ 623 Mo, Next-Gen 448 Mo, avec les mêmes cartes et règles. L’ancien format et la limite d’environ 32 Mio par ressource chargée de manière asynchrone nécessitent des pages graphiques séparées. Installez Mods et DLC pour Classic. DLC/dlcBetaGwentClassic132Assets contient des graphismes indispensables et leur enregistrement, sans nouvelle histoire. Environ 105 Mo du téléchargement viennent de ce dossier ; le reste de la différence provient de la préparation pour l’ancien moteur.',
'Redux',
'Sur 400 anciens noms d’objets vérifiés, 197 conservent leurs définitions natives et 203 reçoivent des définitions inertes, en partie normale et NG+. Ces objets sont cachés, sans poids ni valeur. Un inventaire déjà perdu n’est pas restauré. À la désinstallation, les objets Redux restants nécessitent de nouveau leur fournisseur de définitions d’origine.',
'Nettoyage intégré avant désinstallation',
'''Aucun mod de nettoyage séparé. Sauvegardez vos fichiers, terminez la partie et quittez combats et menus. bg_clean_preview() affiche seulement l’aide. Avec le mod principal encore installé, confirmez :

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Collection, decks, ressources, réglages, récompenses connues, miroirs de sauvegarde et objets betagwent_* de l’inventaire du joueur sont effacés. Un indicateur sauvegardé empêche leur restauration, même après rechargement. Sauvegardez dans un NOUVEL emplacement, quittez le jeu, retirez le mod et son DLC Classic, actualisez Script Merger, chargez ce nouvel emplacement et sauvegardez encore. Quêtes, succès et couronnes dépensées restent inchangés. Marchands non chargés, réserve et conteneurs du monde ne sont pas parcourus. Pour les anciens faits de récompense orphelins : save_fact_index.py puis bg_clean_keys('…') après confirmation. L’effacement physique de toute trace historique n’est pas garanti.''',
'Vers la 1.0',
'Jusqu’à la 1.0, priorité aux traductions, aux corrections de bugs et aux améliorations de l’IA et de l’interface. Les tests automatiques ne remplacent pas les vérifications en jeu ni un véritable cycle sauvegarde/chargement après nettoyage.',
'Exporter affiche un code BG1. Le presse-papiers du jeu peut rester interne : sélectionnez le code et essayez Ctrl+C. Si le collage externe échoue, lancez avec -debugscripts, exportez à nouveau, puis exécutez Copy-Deck-Code.cmd depuis l’archive extraite. Cet outil copie le dernier export de scriptslog.txt dans le presse-papiers Windows. Collez ensuite dans votre message avec Ctrl+V. Il ne démarre pas seul, ne modifie pas les sauvegardes et n’envoie rien. Importer accepte le code complet dans le champ de texte.'],
'it':[
'IA e interfaccia',
'Migliorate le valutazioni di Igni, Yrden, del meteo di Birna e delle abilità di armatura del cavaliere, dell’élite e dello scudiero redaniani. Dopo un passo, il recupero considera azioni e cambi di turno reali; l’ultimo passo non concede effetti aggiuntivi. Nel primo round una carta di svantaggio può andare bene, due richiedono una valutazione e tre vengono evitate negli inseguimenti facoltativi. Evitare la sconfitta nell’incontro ha precedenza. Rivisti pulsanti tradotti e spaziature.',
'Classic 1.32: dimensioni e DLC',
'Classic occupa circa 623 MB, Next-Gen 448 MB, con le stesse carte e regole. Il vecchio formato e il limite di circa 32 MiB per risorsa caricata in modo asincrono richiedono pagine grafiche separate. In Classic vanno installate entrambe le cartelle Mods e DLC. DLC/dlcBetaGwentClassic132Assets contiene grafica essenziale e la sua registrazione, senza nuova storia. Circa 105 MB del download provengono da questa cartella; il resto della differenza dipende dalla preparazione per il vecchio motore.',
'Redux',
'Dei 400 nomi di vecchi oggetti verificati, 197 mantengono le definizioni native e 203 ricevono definizioni inerti, nelle partite normali e NG+. Sono nascosti, senza peso o valore. L’inventario già perso non viene recuperato. Disinstallando, gli oggetti Redux rimasti richiedono di nuovo il fornitore originale delle definizioni.',
'Pulizia integrata prima della disinstallazione',
'''Non serve un mod di pulizia separato. Fai una copia del salvataggio, termina la partita ed esci da combattimenti e menu. bg_clean_preview() mostra soltanto istruzioni. Con il mod principale ancora installato, conferma:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Vengono eliminati collezione, mazzi, risorse, impostazioni, ricompense note, copie di riserva e oggetti betagwent_* nell’inventario del giocatore. Un indicatore salvato impedisce il ripristino anche dopo un nuovo caricamento. Salva in un NUOVO slot, esci, rimuovi il mod e il suo DLC Classic, aggiorna Script Merger, carica lo slot nuovo e salva ancora. Missioni, obiettivi e corone spese rimangono. Mercanti non caricati, deposito e contenitori del mondo non vengono esaminati. Per vecchi fatti di ricompensa orfani: save_fact_index.py e bg_clean_keys('…') dopo la conferma. Non è garantita la cancellazione fisica di ogni traccia storica.''',
'Verso la 1.0',
'Fino alla 1.0 l’attenzione sarà su traduzioni, correzioni di errori e ulteriori miglioramenti a IA e interfaccia. I test automatici non sostituiscono le prove nel gioco o un vero ciclo di salvataggio/caricamento dopo la pulizia.',
'Esporta mostra un codice BG1. Gli appunti del gioco potrebbero restare interni: seleziona il codice e prova Ctrl+C. Se non si incolla altrove, avvia con -debugscripts, esporta di nuovo ed esegui Copy-Deck-Code.cmd dall’archivio estratto. Lo strumento copia l’ultimo codice esportato da scriptslog.txt negli appunti di Windows. Incollalo nel messaggio con Ctrl+V. Non parte automaticamente, non modifica salvataggi e non invia messaggi. Importa accetta il codice completo nel campo di testo.'],
'pl':[
'SI i interfejs',
'Poprawiono ocenę Igni, Yrdena, pogody Birny i zdolności pancerza redańskiego rycerza, elity oraz giermka. Po pasie pościg uwzględnia rzeczywiste zagrania i granice tur; ostatni pas nie dodaje kolejnego efektu. W pierwszej rundzie jedna karta straty bywa opłacalna, dwie wymagają oceny, a trzech unika się przy opcjonalnym pościgu. Ratowanie meczu ma pierwszeństwo. Poprawiono dopasowanie tłumaczonych przycisków i odstępy.',
'Classic 1.32: rozmiar i DLC',
'Classic zajmuje około 623 MB, Next-Gen 448 MB, przy tych samych kartach i zasadach. Starszy format i limit około 32 MiB na asynchronicznie ładowany zasób wymagają osobnych stron grafiki. W Classic należy skopiować Mods oraz DLC. DLC/dlcBetaGwentClassic132Assets zawiera niezbędną grafikę i rejestrację zasobów, bez nowej fabuły. Około 105 MB pobieranego archiwum przypada na ten folder; reszta różnicy wynika z przygotowania zasobów dla starego silnika.',
'Redux',
'Spośród 400 sprawdzonych nazw starych przedmiotów 197 zachowuje definicje gry, a 203 otrzymują nieaktywne definicje w zwykłej grze i NG+. Są ukryte, nic nie ważą i nie mają wartości. Utracony ekwipunek nie jest odzyskiwany. Przy odinstalowaniu pozostałe przedmioty Redux ponownie potrzebują pierwotnego dostawcy definicji.',
'Wbudowane czyszczenie przed odinstalowaniem',
'''Osobny mod czyszczący nie jest potrzebny. Zrób kopię zapisu, zakończ partię, wyjdź z walki i zamknij menu. bg_clean_preview() tylko wyświetla pomoc. Przy nadal zainstalowanym modzie potwierdź:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Usuwane są kolekcja, talie, zasoby, ustawienia, znane nagrody, kopie zapasowe i przedmioty betagwent_* z ekwipunku gracza. Zapisana blokada zapobiega odtworzeniu danych także po ponownym wczytaniu. Zapisz w NOWYM slocie, zamknij grę, usuń mod i jego DLC Classic, zaktualizuj Script Merger, wczytaj nowy slot i zapisz ponownie. Zadania, osiągnięcia i wydane korony pozostają. Niewczytani kupcy, schowek i pojemniki świata nie są przeszukiwane. Osierocone fakty nagród mogą wymagać save_fact_index.py i bg_clean_keys('…') po potwierdzeniu. Fizyczne usunięcie wszystkich historycznych śladów nie jest gwarantowane.''',
'Do wersji 1.0',
'Do 1.0 priorytetem będą poprawki tłumaczeń i błędów oraz dalsze ulepszanie SI i interfejsu. Testy automatyczne nie zastępują prób w grze ani rzeczywistego zapisu i wczytania po czyszczeniu.',
'Eksport wyświetla kod BG1. Schowek gry może pozostać wewnętrzny: zaznacz kod i spróbuj Ctrl+C. Jeśli nie można wkleić go poza grą, uruchom grę z -debugscripts, wyeksportuj ponownie i uruchom Copy-Deck-Code.cmd z rozpakowanego archiwum. Narzędzie kopiuje ostatni eksport z scriptslog.txt do schowka Windows. Wklej go do wiadomości przez Ctrl+V. Nie uruchamia się samo, nie zmienia zapisów i niczego nie wysyła. Import przyjmuje cały kod w polu tekstowym.'],
}

# Regional variants intentionally share their technical instructions.
EXTRA['es']=[
'IA e interfaz','Mejoradas las evaluaciones de Igni, Yrden, el clima de Birna y las habilidades de armadura del caballero, la élite y el escudero redanianos. Tras un pase, la remontada considera jugadas y cambios de turno reales; el último pase no añade otro efecto. En la primera ronda, una carta de desventaja puede compensar, dos requieren valorar la situación y se evitan tres en remontadas opcionales. Evitar perder la partida tiene prioridad. Revisados los botones traducidos y los márgenes.',
'Classic 1.32: tamaño y DLC','Classic ocupa unos 623 MB y Next-Gen 448 MB, con las mismas cartas y reglas. El formato antiguo y el límite de unos 32 MiB por recurso cargado de forma asíncrona requieren páginas gráficas separadas. En Classic hay que instalar Mods y DLC. DLC/dlcBetaGwentClassic132Assets contiene gráficos esenciales y su registro, sin contenido narrativo nuevo. Unos 105 MB de la descarga corresponden a esa carpeta; el resto de la diferencia procede de la preparación para el motor antiguo.',
'Redux','De 400 nombres de objetos antiguos revisados, 197 conservan sus definiciones originales y 203 reciben definiciones inertes para partidas normales y NG+. Están ocultos y no tienen peso ni valor. No se recupera un inventario ya perdido. Al desinstalar, los objetos Redux restantes vuelven a necesitar su proveedor original de definiciones.',
'Limpieza integrada antes de desinstalar',"""No hace falta otro mod de limpieza. Haz una copia del guardado, termina la partida y sal de combates y menús. bg_clean_preview() solo muestra instrucciones. Con el mod principal instalado, confirma:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Se borran colección, mazos, recursos, ajustes, recompensas conocidas, copias de respaldo y objetos betagwent_* del inventario del jugador. Una marca guardada impide restaurarlos incluso al volver a cargar. Guarda en una ranura NUEVA, cierra el juego, retira el mod y su DLC Classic, actualiza Script Merger, carga la nueva ranura y guarda otra vez. Misiones, logros y coronas gastadas permanecen. No se recorren mercaderes sin cargar, el alijo ni contenedores del mundo. Los antiguos hechos de recompensa huérfanos pueden requerir save_fact_index.py y bg_clean_keys('…') después de confirmar. No se garantiza borrar físicamente todo rastro histórico.""",
'Hasta la 1.0','Hasta la 1.0 nos centraremos en corregir traducciones y errores, además de mejorar la IA y la interfaz. Las pruebas automáticas no sustituyen comprobar el juego ni guardar y cargar realmente después de la limpieza.',
'Exportar muestra un código BG1. El portapapeles del juego puede ser interno: selecciona el código y prueba Ctrl+C. Si no se pega fuera del juego, inicia con -debugscripts, exporta otra vez y ejecuta Copy-Deck-Code.cmd desde el archivo extraído. La herramienta copia la última exportación de scriptslog.txt al portapapeles de Windows. Pégala en el mensaje con Ctrl+V. No se ejecuta sola, no modifica guardados ni envía mensajes. Importar acepta el código completo en el campo de texto.']
EXTRA['es-mx']=EXTRA['es'][:]
EXTRA['pt-br']=[
'IA e interface','Melhoradas as avaliações de Igni, Yrden, do clima de Birna e das habilidades de armadura do cavaleiro, da elite e do escudeiro redanianos. Após um passe, a recuperação considera jogadas e mudanças de turno reais; o último passe não concede outro efeito. Na primeira rodada, uma carta de desvantagem pode compensar, duas exigem avaliação e três são evitadas em recuperações opcionais. Evitar perder a partida tem prioridade. Botões traduzidos e espaçamentos foram revistos.',
'Classic 1.32: tamanho e DLC','Classic ocupa cerca de 623 MB e Next-Gen 448 MB, com as mesmas cartas e regras. O formato antigo e o limite de cerca de 32 MiB por recurso carregado de forma assíncrona exigem páginas gráficas separadas. No Classic, instale Mods e DLC. DLC/dlcBetaGwentClassic132Assets contém gráficos essenciais e seu registro, sem nova história. Cerca de 105 MB do download vêm dessa pasta; o restante da diferença resulta da preparação para o motor antigo.',
'Redux','Dos 400 nomes de itens antigos verificados, 197 mantêm as definições nativas e 203 recebem definições inertes para jogos normais e NG+. São ocultos, sem peso ou valor. Inventário já perdido não é recuperado. Ao desinstalar, itens Redux restantes precisam novamente de seu fornecedor original de definições.',
'Limpeza integrada antes de desinstalar',"""Não é necessário outro mod de limpeza. Faça uma cópia do save, termine a partida e saia de combates e menus. bg_clean_preview() só mostra instruções. Com o mod principal instalado, confirme:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

São apagados coleção, baralhos, recursos, configurações, recompensas conhecidas, cópias de segurança e itens betagwent_* do inventário do jogador. Uma marca salva impede a restauração mesmo após carregar novamente. Salve em um NOVO espaço, feche o jogo, retire o mod e seu DLC Classic, atualize o Script Merger, carregue o novo espaço e salve outra vez. Missões, conquistas e coroas gastas permanecem. Comerciantes não carregados, baú e recipientes do mundo não são percorridos. Fatos antigos de recompensa órfãos podem exigir save_fact_index.py e bg_clean_keys('…') após a confirmação. Não há garantia de apagar fisicamente todo vestígio histórico.""",
'Até a 1.0','Até a 1.0, o foco será corrigir traduções e erros, além de aprimorar IA e interface. Testes automáticos não substituem verificações no jogo nem um ciclo real de salvar/carregar após a limpeza.',
'Exportar mostra um código BG1. A área de transferência do jogo pode ser interna: selecione o código e tente Ctrl+C. Se não colar fora do jogo, inicie com -debugscripts, exporte novamente e execute Copy-Deck-Code.cmd no arquivo extraído. A ferramenta copia a última exportação de scriptslog.txt para a área de transferência do Windows. Cole na mensagem com Ctrl+V. Ela não inicia sozinha, não modifica saves nem envia mensagens. Importar aceita o código completo no campo de texto.']
EXTRA['ja']=[
'AIとインターフェース','イグニ、イャーデン、ビルナの天候予測、レダニアの騎士・精鋭・従者の装甲能力の評価を改善しました。相手のパス後は実際のプレイとターン順に沿って追いつけるか判断し、最後のパスで余分な効果を加算しません。第1ラウンドでは手札1枚の不利を許容し、2枚は状況次第、任意の追い上げで3枚の不利は避けます。試合の敗北回避が優先です。翻訳されたボタンの文字と余白も調整しました。',
'Classic 1.32の容量とDLCフォルダー','同じカードとルールでもClassicは約623 MB、Next-Genは約448 MBです。旧形式と非同期読み込みリソース当たり約32 MiBの制限に対応するため、画像ページを分割しています。ClassicではModsとDLCの両方が必要です。DLC/dlcBetaGwentClassic132Assetsは必須の画像と登録情報で、新しい物語ではありません。ダウンロードの約105 MBがこのフォルダーで、残りの容量差は旧エンジン向けの準備によるものです。',
'Redux','確認した旧アイテム名400件のうち197件はゲーム本来の定義を維持し、不足する203件には通常プレイとNG+向けの無機能な定義を追加しました。非表示・重量と価格ゼロです。すでに失われた所持品は復元しません。削除時にReduxのアイテムが残る場合は、元の定義を提供するMODを戻してください。',
'削除前の内蔵クリーンアップ',"""別のクリーナーMODは不要です。セーブをバックアップし、対戦と戦闘を終えてメニューを閉じてください。bg_clean_preview()は説明のみを表示します。メインMODを入れたまま、明示的に次を実行します。

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

コレクション、デッキ、資源、設定、既知の報酬、予備データとプレイヤー所持品のbetagwent_*を消去します。保存されるフラグが、MODを残して再ロードした場合も復元を防ぎます。新しいスロットに保存して終了し、MODとClassic用DLCを削除してScript Mergerを更新し、そのスロットをロードして再保存してください。クエスト、実績、使用済みクラウンは戻しません。未ロードの商人、保管箱、世界の容器は走査しません。古い孤立した報酬フラグには、確認後にsave_fact_index.pyとbg_clean_keys('…')が必要な場合があります。すべての履歴データの物理的な完全消去は保証しません。""",
'1.0に向けて','1.0までは翻訳と不具合の修正、AIとUIの改善に重点を置きます。自動テストは実際のゲームやクリーンアップ後のセーブ・ロード確認の代わりにはなりません。',
'エクスポートでBG1コードを表示します。ゲーム内クリップボードは内部専用の場合があります。コードを選択してCtrl+Cを試し、外部に貼り付けられない場合は-debugscriptsで起動して再エクスポートし、展開したアーカイブのCopy-Deck-Code.cmdを実行してください。scriptslog.txtの最後のエクスポートをWindowsのクリップボードにコピーします。Ctrl+Vでメッセージに貼り付けられます。自動起動、セーブの編集、メッセージ送信はしません。インポート欄には完全なBG1コードを入力してください。']
EXTRA['ko']=[
'AI와 인터페이스','이그니, 이르덴, 비르나의 날씨 예측 및 르다니아 기사·정예·종자의 방어구 능력 평가를 개선했습니다. 상대 패스 후 실제 카드 사용과 턴 순서로 추격을 계산하며 마지막 패스에 추가 효과를 주지 않습니다. 첫 라운드에서 손패 한 장 손해는 허용할 수 있고, 두 장은 상황을 따지며, 선택적 추격으로 세 장 손해는 피합니다. 경기 패배를 피하는 것이 우선입니다. 번역된 버튼과 여백도 조정했습니다.',
'Classic 1.32 용량과 DLC 폴더','카드와 규칙은 같지만 Classic은 약 623 MB, Next-Gen은 약 448 MB입니다. 구형 형식과 비동기 로딩 리소스당 약 32 MiB 제한에 맞추어 그래픽 페이지를 나눕니다. Classic에는 Mods와 DLC가 모두 필요합니다. DLC/dlcBetaGwentClassic132Assets에는 필수 그래픽과 등록 정보가 있으며 새 이야기는 없습니다. 다운로드 중 약 105 MB가 이 폴더이며 나머지 차이는 구형 엔진용 리소스 준비에서 생깁니다.',
'Redux','검토한 옛 아이템 이름 400개 중 197개는 원래 정의를 유지하고 203개에는 일반 게임 및 NG+용 비활성 정의를 추가했습니다. 숨김 처리되며 무게와 가치가 없습니다. 이미 잃은 인벤토리는 복구하지 않습니다. 삭제할 때 Redux 아이템이 남아 있으면 원래 정의를 제공하는 모드를 복원하세요.',
'삭제 전 내장 정리',"""별도 정리 모드는 필요 없습니다. 저장 파일을 백업하고 카드 대전과 전투를 끝내고 메뉴를 닫으세요. bg_clean_preview()는 안내만 표시합니다. 메인 모드가 설치된 상태에서 명시적으로 확인하세요.

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

수집 목록, 덱, 자원, 설정, 알려진 보상, 백업 데이터와 플레이어 인벤토리의 betagwent_* 아이템을 지웁니다. 저장되는 플래그가 모드 설치 상태에서 다시 불러와도 복원을 막습니다. 새 슬롯에 저장하고 게임을 종료한 다음 모드와 Classic DLC를 제거하고 Script Merger를 갱신하세요. 새 슬롯을 불러와 다시 저장하세요. 퀘스트, 도전 과제, 사용한 크라운은 되돌리지 않습니다. 로드되지 않은 상인, 보관함, 월드 용기는 검색하지 않습니다. 과거의 고아 보상 팩트에는 확인 후 save_fact_index.py와 bg_clean_keys('…')가 필요할 수 있습니다. 모든 역사적 기록의 물리적 완전 삭제를 보장하지 않습니다.""",
'1.0까지의 계획','1.0까지 번역과 버그 수정, AI와 인터페이스 개선에 집중합니다. 자동 테스트는 실제 게임 및 정리 후 저장·불러오기 확인을 대신하지 않습니다.',
'내보내기는 BG1 코드를 표시합니다. 게임 클립보드가 내부 전용일 수 있으므로 코드를 선택하고 Ctrl+C를 시도하세요. 외부에 붙여넣어지지 않으면 -debugscripts로 실행해 다시 내보낸 뒤 압축을 푼 폴더의 Copy-Deck-Code.cmd를 실행하세요. scriptslog.txt의 마지막 내보내기를 Windows 클립보드에 복사하므로 Ctrl+V로 메시지에 붙여넣을 수 있습니다. 자동 실행, 저장 파일 수정, 메시지 전송은 하지 않습니다. 가져오기에는 전체 BG1 코드를 입력하세요.']
EXTRA['zh-cn']=[
'AI与界面','改进了伊格尼、亚登、碧尔娜天气预测，以及瑞达尼亚骑士、精英和侍从的护甲能力估值。对方放弃后，追分按实际出牌和回合顺序计算；最后一次放弃不会额外触发引擎。第一局可以接受少一张手牌，少两张需视情况，主动追分时避免少三张。避免整场落败优先。翻译按钮的文字适配与间距也已调整。',
'Classic 1.32为何更大且需要DLC文件夹','卡牌与规则相同，但Classic约623 MB，Next-Gen约448 MB。旧资源格式和每个异步加载资源约32 MiB的限制需要拆分图像页面。Classic必须同时安装Mods与DLC。DLC/dlcBetaGwentClassic132Assets包含必需图像及注册信息，不新增剧情。下载中约105 MB来自此文件夹，其余容量差异来自旧引擎的资源准备。',
'Redux','已检查400个旧物品名称：197个保留原生定义，为缺失的203个补充普通游戏与NG+的无功能定义。这些物品隐藏、无重量且无价值。已丢失的背包无法恢复。卸载时若仍有Redux物品，请恢复原先提供其定义的模组。',
'卸载前的内置清理',"""无需另装清理模组。先备份存档，结束牌局和战斗并关闭菜单。在主模组仍安装时，bg_clean_preview()只显示说明。明确确认：

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

清除收藏、牌组、资源、设置、已知奖励记录、备份镜像及玩家当前背包中的betagwent_*物品。存档标记会阻止恢复，即使仍装着模组重新读档。保存到新栏位，退出游戏，移除模组及其Classic DLC，更新Script Merger，再读取新栏位并保存一次。任务、成就和已花费克朗不会回退。未加载商人、储物箱及世界容器不会被遍历。旧的孤立奖励事实可能需要在确认后使用save_fact_index.py和bg_clean_keys('…')。不保证物理删除任意存档中的所有历史痕迹。""",
'迈向1.0','1.0之前将重点修正翻译与错误，并继续完善AI和界面。自动测试不能代替游戏内检查以及清理后的真实保存和读档测试。',
'导出会显示BG1代码。游戏剪贴板可能仅限内部使用：选中代码并尝试Ctrl+C。若无法粘贴到外部，请以-debugscripts启动游戏，重新导出，再运行解压文件夹中的Copy-Deck-Code.cmd。它将scriptslog.txt中的最后一次导出复制到Windows剪贴板，随后可用Ctrl+V粘贴到消息中。工具不会自动运行、修改存档或发送消息。导入框接受完整BG1代码。']
EXTRA['zh-tw']=[
'AI與介面','改善了伊格尼、亞登、碧爾娜天氣預測，以及瑞達尼亞騎士、精英和侍從的護甲能力估值。對方放棄後，追分按照實際出牌和回合順序計算；最後一次放棄不會額外觸發引擎。第一局可以接受少一張手牌，少兩張需視情況，主動追分時避免少三張。避免整場落敗優先。翻譯按鈕的文字適配與間距也已調整。',
'Classic 1.32為何較大且需要DLC資料夾','卡牌與規則相同，但Classic約623 MB，Next-Gen約448 MB。舊資源格式和每個非同步載入資源約32 MiB的限制需要拆分圖像頁面。Classic必須同時安裝Mods與DLC。DLC/dlcBetaGwentClassic132Assets包含必要圖像與註冊資訊，不新增劇情。下載中約105 MB來自此資料夾，其餘容量差異來自舊引擎的資源準備。',
'Redux','已檢查400個舊物品名稱：197個保留原生定義，為缺少的203個補充一般遊戲與NG+的無功能定義。這些物品隱藏、無重量且無價值。已遺失的背包無法復原。解除安裝時若仍有Redux物品，請恢復原先提供其定義的模組。',
'解除安裝前的內建清理',"""不必另裝清理模組。先備份存檔，結束牌局和戰鬥並關閉選單。在主模組仍安裝時，bg_clean_preview()只顯示說明。明確確認：

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

清除收藏、牌組、資源、設定、已知獎勵紀錄、備份鏡像與玩家目前背包中的betagwent_*物品。存檔標記會阻止復原，即使仍裝著模組重新讀檔。儲存至新欄位，退出遊戲，移除模組及其Classic DLC，更新Script Merger，再讀取新欄位並儲存一次。任務、成就和已花費克朗不會回退。未載入商人、儲物箱與世界容器不會被遍歷。舊的孤立獎勵事實可能需要在確認後使用save_fact_index.py和bg_clean_keys('…')。不保證物理刪除任意存檔中的所有歷史痕跡。""",
'邁向1.0','1.0之前將重點修正翻譯與錯誤，並持續完善AI和介面。自動測試無法取代遊戲內檢查及清理後的實際儲存與讀檔測試。',
'匯出會顯示BG1代碼。遊戲剪貼簿可能僅供內部使用：選取代碼並嘗試Ctrl+C。若無法貼到外部，請以-debugscripts啟動遊戲，重新匯出，再執行解壓縮資料夾中的Copy-Deck-Code.cmd。它會將scriptslog.txt中的最後一次匯出複製到Windows剪貼簿，隨後可用Ctrl+V貼到訊息中。工具不會自動執行、修改存檔或傳送訊息。匯入欄接受完整BG1代碼。']

POST_EN='''**Gwent Beta Classic 0.9.0**

**English**

**Classic 1.32 and Next-Gen**
Choose one archive for your game version. Each contains all 13 text languages and all five voice languages: EN, RU, DE, IT and PT-BR. Text and voices can be selected independently in the mod menu; Auto follows the game's settings, with English as fallback.

For Next-Gen, replace the previous modBetaGwent0924 folder and copy Mods into the game directory. For Classic 1.32, install BOTH Mods and DLC. Its DLC/dlcBetaGwentClassic132Assets folder is required for graphics and leader entrances. Classic is larger because the old loader needs a different resource layout; the cards and AI are the same.

**AI improvements**
Revised Igni and Yrden choices, Birna's weather forecast, armour breaks and the three Redanian armour abilities. Catch-up after a pass now follows real plays and turn boundaries. The AI can concede round one to preserve resources, but gives survival priority when another lost round would end the match. Automated scenarios cover all 46 opponent deck archetypes; unusual decisions are still worth reporting.

**Deck sharing and interface**
Import and Export use BG1 text codes. Missing cards and their crafting cost are shown before a separate crafting confirmation. Import creates a draft: save the deck afterward. Added console commands, improved translated buttons, editor spacing and controller navigation, and revised graveyard flights and leader animation timing.

The game's clipboard can remain internal to Scaleform. If Copy and Ctrl+C do not let you paste outside the game, launch with **-debugscripts**, export again and run **Copy-Deck-Code.cmd** from the extracted archive. It copies the latest export from scriptslog.txt into the Windows clipboard for Ctrl+V in your message. It does not edit saves or send anything.

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
%USERPROFILE%\\Documents\\The Witcher 3\\scriptslog.txt
```

4. If Windows created a crash dump, attach the latest relevant .dmp from:

```text
%LOCALAPPDATA%\\CrashDumps
```
'''
POST_RU='''**Русский**

**Classic 1.32 и Next-Gen**
Выбирайте один архив под свою версию игры. В каждом — все 13 языков текста и пять озвучек: EN, RU, DE, IT и PT-BR. Текст и голоса выбираются независимо в меню мода; «Авто» следует настройкам игры, при отсутствии языка используется английский.

Для Next-Gen замените прежнюю папку modBetaGwent0924 и скопируйте Mods в каталог игры. Для Classic 1.32 нужны ОБЕ папки — Mods и DLC. DLC/dlcBetaGwentClassic132Assets содержит обязательную графику и вступления лидеров. Classic весит больше из-за другого формата ресурсов и ограничений старого загрузчика; карты и ИИ в обеих сборках одинаковые.

**Улучшения ИИ**
Переработаны выбор Игни и Ирдена, прогноз погоды Бирны, снятие брони и три реданские способности. Догон после паса учитывает реальные розыгрыши и границы ходов. ИИ может отдать первый раунд ради сохранения ресурсов, но при угрозе поражения в матче важнее выиграть раунд. Автоматические сценарии охватывают все 46 архетипов соперников; о странных решениях по-прежнему стоит сообщать.

**Обмен колодами и интерфейс**
Импорт и экспорт работают с текстовыми кодами BG1. До отдельного подтверждения создания показываются недостающие карты и стоимость. Импорт создаёт черновик: затем сохраните колоду. Добавлены консольные команды, улучшены подгонка переведённых кнопок, отступы редактора и навигация с контроллера, полёты карт в сброс и синхронизация анимаций лидеров.

Буфер игры может оставаться внутри Scaleform. Если после «Копировать» и Ctrl+C ничего не вставляется вне игры, запустите игру с **-debugscripts**, повторите экспорт и запустите **Copy-Deck-Code.cmd** из распакованного архива. Он прочитает последний экспорт из scriptslog.txt и скопирует его в буфер Windows для вставки через Ctrl+V в сообщение. Сейвы он не меняет и ничего не отправляет.

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
%USERPROFILE%\\Documents\\The Witcher 3\\scriptslog.txt
```

4. Если Windows создала дамп падения, приложите последний относящийся к ошибке .dmp из:

```text
%LOCALAPPDATA%\\CrashDumps
```
'''

def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n','utf8')

def main():
    assert set(EXTRA)==set(ORDER)
    assert set(OUTLAW)==set(ORDER)
    bodies={};rendered={}
    for lang in ORDER:
        src=(ROOT/'docs/releases/0.8.2/nexus'/lang/'description.md').read_text('utf-8-sig').replace('0.8.2','0.9.0')
        sections=re.split(r'(?m)^## ',src);assert len(sections)==13,(lang,len(sections))
        x=list(EXTRA[lang]);assert len(x)==11
        x[1]+='\n\n'+OUTLAW[lang]
        # Exchange's first paragraph formerly promised automatic OS clipboard.
        exchange=sections[5].split('\n\n');exchange[1]=x[10];sections[5]='\n\n'.join(exchange)
        changes=sections[4].splitlines();first=next(i for i,v in enumerate(changes) if v.startswith('- '))
        changes[first]='- '+x[10].split('. ')[0]+'.'
        sections[4]='\n'.join(changes)+'\n\n'
        extras=['## '+x[i]+'\n\n'+x[i+1]+'\n\n' for i in range(0,10,2)]
        body=sections[0]+'## '+sections[1]+'## '+sections[4]+extras[0]
        body+=''.join('## '+sections[i] for i in [2,3,5,6,7,8])
        body+=extras[1]+'## '+sections[9]+'## '+sections[10]+extras[2]+extras[3]+extras[4]
        body+='## '+sections[11]+'## '+sections[12]
        assert '0.8.2' not in body and '\ufffd' not in body
        bodies[lang]=body;rendered[lang]=bb.bbcode('\n'.join(body.splitlines()[2:]))
        write(OUT/lang/'description.md',body);write(OUT/lang/'description.bbcode.txt',bb.bbcode(body))
    intro='''[center][size=6][b]Gwent Beta Classic[/b][/size]
Standalone Gwent Beta 0.9.24 inside The Witcher 3

[b]Version 0.9.0[/b] · Changelog tab for all changes · [url=https://github.com/NikRegul/GwentBetaClassic-]GitHub[/url]

Language · Язык · Sprache · Langue · Lingua · Język · Idioma · 言語 · 언어 · 语言 · 語言
English is shown below. Pick your language and press Show.[/center]
'''
    combined=intro
    preview='# Gwent Beta Classic 0.9.0\n\nStandalone Gwent Beta 0.9.24 inside The Witcher 3\n\n'
    for lang in ORDER[1:]:
        combined+='\n[b]'+NAMES[lang]+'[/b]\n[spoiler]\n'+rendered[lang]+'[/spoiler]\n'
        preview+='<details><summary>'+NAMES[lang]+'</summary>\n\n'+bodies[lang]+'\n</details>\n\n'
    combined+='\n[line]\n[b]English[/b]\n\n'+rendered['en']
    preview+='## English\n\n'+bodies['en']
    write(OUT/'NEXUS_DESCRIPTION_0.9.0.bbcode.txt',combined)
    write(OUT/'DESCRIPTION_0.9.0.md',preview)
    posts={
        'en':POST_EN.replace('**Deck sharing and interface**',OUTLAW['en']+'\n\n**Deck sharing and interface**'),
        'ru':POST_RU.replace('**Обмен колодами и интерфейс**',OUTLAW['ru']+'\n\n**Обмен колодами и интерфейс**'),
    }
    assert OUTLAW['en'] in posts['en'] and OUTLAW['ru'] in posts['ru']
    post=posts['en']+'\n\n'+posts['ru']
    write(OUT/'POST_0.9.0_EN_RU.md',post);write(OUT/'NEXUS_POST_0.9.0_EN_RU.bbcode.txt',bb.bbcode(post))
    for lang,text in [('en',posts['en']),('ru','**Gwent Beta Classic 0.9.0**\n\n'+posts['ru'])]:
        write(OUT/lang/'post.md',text);write(OUT/lang/'post.bbcode.txt',bb.bbcode(text))
        changes=(ROOT/'docs/releases/0.8.2-polish2/nexus'/lang/'changelog.md').read_text('utf8').replace('0.8.2','0.9.0')
        changes+='\n## '+('Isengrim: Outlaw' if lang=='en' else 'Изенгрим: Изгой')+'\n\n'+OUTLAW[lang]+'\n\n## '+EXTRA[lang][6]+'\n\n'+EXTRA[lang][7]+'\n\n## BG1\n\n'+EXTRA[lang][10]+'\n'
        write(OUT/lang/'changelog.md',changes);write(OUT/lang/'changelog.bbcode.txt',bb.bbcode(changes))
        write(ROOT/f'docs/releases/0.9.0_CLEANUP_{lang.upper()}.md','# Gwent Beta Classic 0.9.0 — '+EXTRA[lang][6]+'\n\n'+EXTRA[lang][7]+'\n')
    write(ROOT/'docs/releases/0.9.0_CLEANER_RU.md','# Очистка Gwent Beta Classic 0.9.0\n\nОчиститель встроен в основной мод. Отдельный мод устанавливать не нужно. Актуальная инструкция: [0.9.0_CLEANUP_RU.md](0.9.0_CLEANUP_RU.md).\n')
    write(OUT/'README_RU.md','''# Тексты Nexus 0.9.0

NEXUS_DESCRIPTION_0.9.0.bbcode.txt — описание целиком: шапка, 12 переводов под Show и английский текст ниже, как в образце.

NEXUS_POST_0.9.0_EN_RU.bbcode.txt — отдельный пост: English, затем Русский, с жирными подзаголовками и инструкцией по логам.

Файлы .md — для чтения и правок; .bbcode.txt — для вставки в редактор Nexus в режиме исходного BBCode. Очистка описана как встроенная в основной мод. Для буфера обмена указано ограничение движка и явный Windows-помощник; автоматическое копирование в другие приложения не обещается.

Тексты не опубликованы. Автоматические проверки не заменяют игровую приёмку, перенос кода через системный буфер и сохранение/загрузку реального сейва после очистки.
''')
    checked=[]
    for p in OUT.rglob('*.bbcode.txt'):
        text=p.read_text('utf8');stack=[]
        for m in re.finditer(r'\[(/?)([a-z]+)(?:=[^\]]+)?\]',text):
            close,tag=m.groups()
            if tag=='line':continue
            if close:assert stack and stack.pop()==tag,(p,m[0])
            else:stack.append(tag)
        assert not stack,(p,stack)
        assert '**' not in text and '\ufffd' not in text
        checked.append(p.relative_to(OUT).as_posix())
    assert combined.count('[spoiler]')==combined.count('[/spoiler]')==12
    for lang,body in bodies.items():
        for token in ['0.9.0','bg_clean_confirm','DELETE_BETA_GWENT','bg_clean_keys','Copy-Deck-Code.cmd','1.32','5.0+','203','197']:
            assert token in body,(lang,token)
    write(OUT/'validation.json',json.dumps(dict(version='0.9.0',descriptionLanguages=13,spoilers=12,englishDefault=True,postLanguages=['en','ru'],embeddedCleaner=True,published=False,bbcodeFiles=checked),indent=2))
    print('Prepared 13 descriptions, English/Russian post and integrated cleanup instructions.')

if __name__=='__main__':main()
