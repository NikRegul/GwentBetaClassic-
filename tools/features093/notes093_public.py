"""Public0.9.3 copy in all thirteen mod languages; historical notes stay immutable."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/releases/0.9.3-public-20261025'
# title, lead, Classic, decks, AI, rules, UI, voice, RNG, validation
COPY={
'RU':[
'Большие колоды. Продуманные ходы. Гвинт времён беты.',
'Верните в The Witcher 3 Гвинт открытой беты: знакомые карты, полноценный редактор колод и поединки с персонажами мира. Релизная 0.9.3 объединяет изменения после 0.9.1 и исправления по последним игровым журналам.',
'«Классическая» — отдельная четвёртая сложность с перенесённым ИИ беты. 24 исходных профиля назначены 109 вариантам колод. Выбор доступен перед боем рядом с языками. Этот ИИ видит руку и колоду игрока; обычный сложный ИИ сохраняет свои ограничения информации.',
'30 одобренных подлинных колод беты дополняют 46 наших: всего 76 обычных составов и 33 тематических варианта квестовых соперников, 92 уникальных состава. Названия импортированных колод сохранены. 15 похожих составов отложены; 28 колод с недопустимым построением исключены.',
'Сложный ИИ лучше оценивает продолжение после лидера, порядок карт в коротком решающем раунде, добор перед уступкой и выгодный пас. Усиления учитывают риск Менно и сброса силы; урон учитывает восстановление мечников Ан Крайт. Колоды вскрытия оценивают чужую скрытую руку и собственные полезные синергии.',
'Исправлены повторное резервирование одного голема при нескольких вскрытиях и вместимость рядов при призыве. Блокировка снимает старые «Стойкость», «Засаду» и «Шпиона»: заблокированный Ярпен больше не переносится в следующий раунд за счёт прежнего статуса. Сохранены исправления цепочек, дочерних карт и допустимых целей.',
'Предложенные карты показаны отдельным окном: у Кантареллы ясно видно, что оставить и что вернуть вниз колоды. Скрытые карты остаются рубашками. Имя соперника заменяет внутренние названия профилей; убраны лишний заголовок «Ваша колода» и пустая полоса под лидером. Исправлены фокус Белого Хлада с контроллера, видимость сложности, автопас с пустой рукой и бесполезная погода после паса соперника.',
'13 языков текста и независимый выбор озвучки: русский, английский, немецкий, итальянский и бразильский португальский. Исправлена цепочка выбора голосов, из-за которой реплики оставались русскими после смены настройки. Auto следует языку озвучки игры.',
'RNG проверяет контрольные значения и не зависит от переполнения целых чисел. Если игровой runtime не проходит контракт, используется явно отмеченный резерв из 1024 значений игрового RNG с конечным циклом. Исправление повторов раздачи требует отдельной проверки непосредственно в игре.',
'Предназначено для Classic 1.32 и Next-Gen 5.0+. Принятые иллюстрации, VFX и музыка сохранены. Автоматические проверки и нативная компиляция не заменяют игровую приёмку интерфейса, озвучки и RNG. Исторические сравнения силы относятся к своим замороженным версиям; превосходство новой сборки на любой колоде не заявляется.'],
'EN':[
'More decks. Smarter turns. Gwent from the beta era.',
'Bring open-beta Gwent into The Witcher 3: familiar cards, a full deck editor and matches against characters across the world. Public0.9.3 brings together the changes since0.9.1 and fixes from recent play logs.',
'Classic is a separate fourth difficulty using the ported beta AI.24 original profiles serve109 deck presets. Choose it before a match beside the language controls. Classic sees your hand and deck; ordinary Hard retains its information restrictions.',
'30 approved original beta decks join our46:76 ordinary lineups and33 thematic quest-opponent presets,92 unique compositions. Imported deck names are retained.15 similar decks await review;28 invalid deck constructions are excluded.',
'Hard better evaluates follow-ups after leaders, card order in short decisive rounds, drawing before conceding and useful passes. Boosts account for Menno and power resets; damage accounts for Clan an Craite Greatsword recovery. Reveal decks weigh opposing hidden cards against useful own-hand synergies.',
'Fixed repeated reservation of the same golem during multiple reveals and row capacity for queued summons. Lock removes existing Resilience, Ambush and Spy: locked Yarpen no longer carries over through his old status. Chain, spawned-card and legal-target fixes are retained.',
'Offered cards now have their own choice window: Cantarella clearly shows what to keep and what returns to the deck bottom. Hidden cards stay face down. Opponent names replace internal profiles; the redundant Your Deck heading and unused space below the leader are removed. Controller White Frost focus, difficulty visibility, empty-hand auto-pass and wasted weather after an opposing pass are fixed.',
'13 text languages with independent voices in Russian, English, German, Italian and Brazilian Portuguese. Fixed voice selection leaving dialogue in Russian. Auto follows the game speech language.',
'RNG checks reference vectors without integer-overflow dependence. A runtime failing the contract uses an explicitly marked finite1024-value engine-RNG fallback. Repeated-deal recovery still needs direct in-game acceptance.',
'For Classic1.32 and Next-Gen5.0+. Accepted artwork, VFX and music are preserved. Automated checks and native compilation do not replace in-game UI, voice and RNG acceptance. Historical strength trials apply to their frozen versions; universal superiority of this build is not claimed.'],
'DE':[
'Mehr Decks. Klügere Züge. Gwint aus der Beta-Zeit.',
'Holt Gwint aus der offenen Beta in The Witcher3 zurück: vertraute Karten, ein vollständiger Deck-Editor und Gegner aus der Spielwelt. Die öffentliche0.9.3 vereint die Änderungen seit0.9.1 und Korrekturen aus aktuellen Spielprotokollen.',
'Klassisch ist der vierte Schwierigkeitsgrad mit der portierten Beta-KI.24 Originalprofile sind109 Deck-Voreinstellungen zugeordnet. Wählt ihn vor dem Kampf neben den Sprachen. Diese KI sieht eure Hand und euer Deck; Schwer behält seine Informationsgrenzen.',
'30 freigegebene Beta-Decks ergänzen unsere46:76 reguläre Zusammenstellungen und33 thematische Quest-Gegner,92 einzigartige Deckzusammenstellungen. Originalnamen bleiben erhalten.15 ähnliche Decks warten auf Prüfung;28 ungültige Konstruktionen sind ausgeschlossen.',
'Schwer bewertet Folgezüge nach Anführern, Kartenreihenfolgen in kurzen Entscheidungsrunden, Nachziehen vor dem Aufgeben und sinnvolles Passen besser. Verstärkungen beachten Menno und Zurücksetzen der Stärke; Schaden berücksichtigt die Heilung der Großschwerter von Clan an Craite. Aufdecken wägt gegnerische Handkarten gegen eigene Synergien ab.',
'Mehrfaches Reservieren desselben Golems beim Aufdecken und die Reihenbelegung bei vorgemerkten Beschwörungen sind korrigiert. Sperren entfernt vorhandene Zähigkeit, Hinterhalt und Spion: gesperrter Yarpen bleibt nicht durch seinen alten Status liegen. Korrekturen für Ketten, erzeugte Karten und Ziele bleiben erhalten.',
'Angebotene Karten erscheinen in einem eigenen Auswahlfenster. Bei Cantarella ist klar, welche Karte bleibt und welche unter das Deck kommt. Verdeckte Karten bleiben verdeckt. Gegnernamen ersetzen interne Profile; die überflüssige Deck-Überschrift und der leere Bereich unter dem Anführer entfallen. Controller-Fokus für Weiße Kälte, Schwierigkeitstaste, automatisches Passen und nutzloses Wetter nach gegnerischem Passen sind korrigiert.',
'13 Textsprachen und unabhängig wählbare Stimmen auf Russisch, Englisch, Deutsch, Italienisch und brasilianischem Portugiesisch. Der Fehler mit dauerhaft russischen Stimmen ist behoben. Auto folgt der gesprochenen Spielsprache.',
'RNG prüft Referenzwerte ohne Abhängigkeit von Ganzzahlüberlauf. Bei fehlerhaftem Laufzeitvertrag wird ein gekennzeichneter endlicher Ersatz mit1024 Engine-RNG-Werten verwendet. Wiederholte Austeilungen müssen noch direkt im Spiel geprüft werden.',
'Für Classic1.32 und Next-Gen5.0+. Freigegebene Grafik, VFX und Musik bleiben erhalten. Automatische Tests und native Kompilierung ersetzen keine Prüfung von Oberfläche, Stimmen und RNG im Spiel. Frühere Stärketests gelten für ihre eingefrorenen Versionen; allgemeine Überlegenheit wird nicht behauptet.'],
'FR':[
'Plus de jeux. Des tours mieux pensés. Le Gwynt de la bêta.',
'Retrouvez le Gwynt de la bêta ouverte dans The Witcher3: cartes familières, éditeur complet et adversaires du monde du jeu. La version publique0.9.3 réunit les changements depuis0.9.1 et les corrections issues des dernières parties.',
'Classique est une quatrième difficulté utilisant l’IA portée de la bêta.24 profils originaux sont associés à109 configurations. Choisissez-la avant le duel près des langues. Elle voit votre main et votre jeu; Difficile conserve ses limites d’information.',
'30 jeux authentiques approuvés rejoignent nos46:76 compositions ordinaires et33 adversaires de quête thématiques, soit92 compositions uniques. Les noms originaux sont conservés.15 jeux similaires attendent une décision;28 constructions invalides sont exclues.',
'Difficile évalue mieux les suites après un chef, l’ordre des cartes en manche décisive courte, la pioche avant concession et les passes utiles. Les améliorations tiennent compte de Menno et des réinitialisations; les dégâts tiennent compte du soin des espadons du clan an Craite. La révélation compare les cartes adverses cachées aux synergies de sa propre main.',
'Correction de la réservation répétée du même golem pendant plusieurs révélations et de la capacité des rangées lors des invocations en attente. Le verrouillage retire les statuts existants de résistance, d’embuscade et d’espion: Yarpen verrouillé ne reste plus grâce à son ancien statut. Les corrections des chaînes, cartes créées et cibles sont conservées.',
'Les cartes proposées disposent d’une fenêtre dédiée. Cantarella indique clairement la carte gardée et celle remise sous le jeu. Les cartes cachées restent face cachée. Le nom de l’adversaire remplace les profils internes; le titre Votre jeu et l’espace inutile sous le chef disparaissent. Corrections du ciblage du Froid blanc à la manette, du bouton de difficulté, de la passe automatique et de la météo inutile après une passe adverse.',
'13 langues de texte et voix indépendantes en russe, anglais, allemand, italien et portugais brésilien. Correction des répliques restant en russe après le changement de voix. Auto suit la langue parlée du jeu.',
'Le RNG vérifie des valeurs de référence sans dépendre des débordements d’entiers. Si le contrat échoue, un repli fini et signalé de1024 valeurs du RNG du moteur est utilisé. Les distributions répétées restent à vérifier directement en jeu.',
'Pour Classic1.32 et Next-Gen5.0+. Illustrations, effets et musique approuvés préservés. Les tests et compilations natives ne remplacent pas la validation en jeu de l’interface, des voix et du RNG. Les anciens tests de force concernent leurs versions figées; aucune supériorité universelle n’est annoncée.'],
'IT':[
'Più mazzi. Mosse più ragionate. Il Gwent della beta.',
'Riporta il Gwent della beta aperta in The Witcher3: carte familiari, editor completo e avversari nel mondo di gioco. La versione pubblica0.9.3 raccoglie le novità dalla0.9.1 e le correzioni tratte dalle ultime partite.',
'Classica è la quarta difficoltà con l’IA originale della beta trasferita nel mod.24 profili sono assegnati a109 configurazioni. Si sceglie prima dello scontro accanto alle lingue. Vede mano e mazzo del giocatore; Difficile mantiene i propri limiti informativi.',
'30 mazzi autentici approvati si aggiungono ai nostri46:76 composizioni ordinarie e33 avversari tematici delle missioni,92 composizioni uniche. Nomi originali conservati.15 mazzi simili restano da valutare;28 costruzioni non valide sono escluse.',
'Difficile valuta meglio le continuazioni dopo i leader, l’ordine delle carte nelle manche decisive brevi, la pesca prima di cedere e i passaggi utili. I potenziamenti considerano Menno e gli azzeramenti; i danni considerano la guarigione degli spadaccini an Craite. La rivelazione confronta le carte avversarie nascoste con le sinergie della propria mano.',
'Corretti la prenotazione ripetuta dello stesso golem durante più rivelazioni e lo spazio nelle file per le evocazioni in coda. Il blocco rimuove Resilienza, Imboscata e Spia già presenti: Yarpen bloccato non resta grazie al vecchio stato. Conservate le correzioni a catene, carte generate e bersagli.',
'Le carte proposte appaiono in una finestra dedicata. Cantarella mostra quale tenere e quale torna in fondo al mazzo. Le carte nascoste restano coperte. Il nome dell’avversario sostituisce i profili interni; rimossi il titolo Il tuo mazzo e lo spazio vuoto sotto il leader. Corretti il focus del Bianco gelo con controller, la difficoltà visibile, il passaggio automatico e il meteo sprecato dopo il passaggio avversario.',
'13 lingue di testo e voci indipendenti in russo, inglese, tedesco, italiano e portoghese brasiliano. Corretta la selezione che lasciava le battute in russo. Auto segue la lingua parlata del gioco.',
'Il RNG verifica valori di riferimento senza dipendere dall’overflow degli interi. Se il contratto fallisce, usa una riserva finita e segnalata di1024 valori del RNG del motore. Le distribuzioni ripetute richiedono ancora verifica diretta in gioco.',
'Per Classic1.32 e Next-Gen5.0+. Grafica, VFX e musica approvati conservati. Test e compilazioni native non sostituiscono la verifica in gioco di interfaccia, voci e RNG. I confronti storici valgono per le rispettive versioni congelate; non si dichiara superiorità universale.'],
'PL':[
'Więcej talii. Lepsze decyzje. Gwint z czasów bety.',
'Przywróć Gwinta z otwartej bety w The Witcher3: znane karty, pełny edytor talii i przeciwnicy ze świata gry. Publiczne0.9.3 łączy zmiany od0.9.1 z poprawkami z najnowszych zapisów rozgrywki.',
'Klasyczna to czwarty poziom trudności z przeniesioną SI bety.24 oryginalne profile przypisano do109 zestawów. Wybierz ją przed walką obok języków. Widzi rękę i talię gracza; Trudna zachowuje swoje ograniczenia informacji.',
'30 zatwierdzonych talii bety uzupełnia nasze46:76 zwykłych składów i33 tematyczne warianty przeciwników z zadań,92 unikalne składy. Nazwy oryginalnych talii zachowano.15 podobnych czeka na decyzję;28 niepoprawnych konstrukcji wykluczono.',
'Trudna lepiej ocenia kontynuacje po dowódcy, kolejność kart w krótkiej decydującej rundzie, dobieranie przed oddaniem rundy i korzystne pasy. Wzmocnienia uwzględniają Menno i reset siły; obrażenia uwzględniają leczenie mieczników an Craite. Ujawnianie porównuje ukryte karty przeciwnika z synergiami własnej ręki.',
'Poprawiono wielokrotną rezerwację tego samego golema przy ujawnianiu oraz pojemność rzędów dla przywołań w kolejce. Blokada usuwa istniejącą Wytrzymałość, Zasadzkę i Szpiega: zablokowany Yarpen nie przechodzi dalej dzięki dawnemu statusowi. Zachowano poprawki łańcuchów, tworzonych kart i celów.',
'Proponowane karty mają osobne okno wyboru. Cantarella pokazuje, którą zatrzymać, a którą odłożyć na spód talii. Ukryte karty pozostają zakryte. Nazwa przeciwnika zastępuje wewnętrzne profile; usunięto zbędny nagłówek Twoja talia i puste miejsce pod dowódcą. Poprawiono fokus Białego Zimna na kontrolerze, widoczność trudności, automatyczny pas i marnowanie pogody po pasie przeciwnika.',
'13 języków tekstu i niezależne głosy: rosyjski, angielski, niemiecki, włoski i portugalski brazylijski. Naprawiono pozostawanie rosyjskich głosów po zmianie ustawienia. Auto używa języka mowy gry.',
'RNG sprawdza wzorce bez zależności od przepełnienia liczb całkowitych. Przy niezgodnym kontrakcie używa oznaczonej, skończonej puli1024 wartości generatora silnika. Powtarzalne rozdania wymagają jeszcze sprawdzenia bezpośrednio w grze.',
'Dla Classic1.32 i Next-Gen5.0+. Zachowano zatwierdzoną grafikę, VFX i muzykę. Testy i natywna kompilacja nie zastępują odbioru interfejsu, głosów i RNG w grze. Historyczne porównania siły dotyczą zamrożonych wersji; nie obiecujemy przewagi w każdej talii.'],
'ES':[
'Más mazos. Mejores decisiones. El Gwynt de la beta.',
'Recupera el Gwynt de la beta abierta en The Witcher3: cartas conocidas, editor completo y rivales del mundo del juego. La versión pública0.9.3 reúne los cambios desde0.9.1 y las correcciones de las últimas partidas.',
'Clásica es la cuarta dificultad y usa la IA original de la beta portada al mod.24 perfiles se asignan a109 configuraciones. Elígela antes del combate junto a los idiomas. Ve tu mano y tu mazo; Difícil conserva sus límites de información.',
'30 mazos auténticos aprobados se suman a nuestros46:76 composiciones normales y33 variantes temáticas de personajes de misiones,92 composiciones únicas. Se conservan los nombres originales.15 mazos similares esperan revisión;28 construcciones inválidas quedan excluidas.',
'Difícil evalúa mejor las continuaciones tras el líder, el orden de cartas en rondas decisivas cortas, robar antes de ceder y los pases útiles. Las mejoras consideran a Menno y los reinicios de fuerza; el daño considera la curación de los espadones an Craite. Revelar compara las cartas ocultas rivales con las sinergias de la propia mano.',
'Corregidas la reserva repetida del mismo gólem al revelar varias cartas y la capacidad de las filas al invocar en cola. El bloqueo retira Resistencia, Emboscada y Espía ya presentes: Yarpen bloqueado no permanece por su estado anterior. Se conservan los arreglos de cadenas, cartas generadas y objetivos.',
'Las cartas ofrecidas aparecen en una ventana propia. Cantarella muestra cuál conservar y cuál vuelve al fondo del mazo. Las ocultas siguen boca abajo. El nombre del rival sustituye perfiles internos; se eliminan el título Tu mazo y el hueco bajo el líder. Corregidos el foco de Escarcha Blanca con mando, la dificultad visible, el pase automático y el clima desperdiciado tras el pase rival.',
'13 idiomas de texto y voces independientes en ruso, inglés, alemán, italiano y portugués de Brasil. Corregido el diálogo que seguía en ruso tras cambiar la voz. Auto sigue el idioma hablado del juego.',
'El RNG verifica valores de referencia sin depender del desbordamiento de enteros. Si falla el contrato, usa una reserva finita y señalada de1024 valores del RNG del motor. Los repartos repetidos aún requieren validación directa en el juego.',
'Para Classic1.32 y Next-Gen5.0+. Se conservan el arte, los efectos y la música aprobados. Las pruebas y compilaciones nativas no sustituyen la validación en juego de interfaz, voces y RNG. Las comparaciones históricas corresponden a sus versiones congeladas; no se afirma superioridad universal.'],
'PT_BR':[
'Mais baralhos. Jogadas mais inteligentes. O Gwent da beta.',
'Traga o Gwent da beta aberta para The Witcher3: cartas conhecidas, editor completo e adversários pelo mundo do jogo. A versão pública0.9.3 reúne as mudanças desde0.9.1 e correções das partidas mais recentes.',
'Clássica é a quarta dificuldade e usa a IA original da beta portada para o mod.24 perfis atendem109 configurações. Escolha antes da partida, junto dos idiomas. Ela vê sua mão e seu baralho; Difícil mantém suas restrições de informação.',
'30 baralhos autênticos aprovados somam-se aos nossos46:76 composições comuns e33 variantes temáticas de personagens de missões,92 composições únicas. Nomes originais preservados.15 baralhos semelhantes aguardam revisão;28 construções inválidas foram excluídas.',
'Difícil avalia melhor as continuações após líderes, a ordem das cartas em rodadas decisivas curtas, comprar antes de ceder e passes úteis. Fortalecimentos consideram Menno e redefinições de força; o dano considera a cura dos espadachins an Craite. Revelar compara cartas ocultas adversárias com sinergias da própria mão.',
'Corrigidas a reserva repetida do mesmo golem em várias revelações e a capacidade das fileiras para invocações na fila. Bloquear remove Resiliência, Emboscada e Espião existentes: Yarpen bloqueado não permanece por seu estado antigo. Correções de cadeias, cartas criadas e alvos preservadas.',
'Cartas oferecidas aparecem em uma janela própria. Cantarella mostra qual manter e qual retorna ao fundo do baralho. Cartas ocultas continuam viradas para baixo. O nome do adversário substitui perfis internos; removidos o título Seu baralho e o espaço vazio abaixo do líder. Corrigidos o foco da Geada Branca no controle, a dificuldade visível, o passe automático e o clima desperdiçado após o passe adversário.',
'13 idiomas de texto e vozes independentes em russo, inglês, alemão, italiano e português brasileiro. Corrigidas as falas que continuavam em russo após trocar a voz. Auto segue o idioma de fala do jogo.',
'O RNG verifica valores de referência sem depender de estouro de inteiros. Se o contrato falhar, usa uma reserva finita e identificada de1024 valores do RNG do motor. Distribuições repetidas ainda exigem validação direta no jogo.',
'Para Classic1.32 e Next-Gen5.0+. Arte, VFX e música aprovados preservados. Testes e compilação nativa não substituem a validação de interface, vozes e RNG no jogo. Comparações históricas valem para suas versões congeladas; não se promete superioridade universal.'],
'JA':[
'多彩なデッキ。考え抜かれた一手。ベータ時代のグウェント。',
'オープンベータのグウェントをThe Witcher3へ。おなじみのカード、デッキ編集、各地の人物との対戦を楽しめます。公開版0.9.3は0.9.1以降の変更と最新プレイログに基づく修正をまとめた版です。',
'「クラシック」はベータ版AIを移植した4つ目の難易度です。24種の元プロフィールを109のデッキ設定に割り当て、対戦前の言語設定横で選べます。このAIはプレイヤーの手札とデッキを参照します。通常のハードは従来の情報制限を維持します。',
'承認済みの元ベータデッキ30種を既存46種へ追加。通常構成76種、クエスト人物用33設定、重複を除く構成は92種です。元のデッキ名を保持。類似15種は保留、構築条件を満たさない28種は除外しました。',
'ハードは指導者後の展開、短い決着ラウンドのカード順、ラウンドを譲る前のドロー、有効なパスを改善。強化ではメンノや戦力リセット、ダメージではアンクライトの大剣使いの回復を考慮します。公開デッキは相手の非公開手札と自分の公開シナジーを比較します。',
'連続公開で同じゴーレムを重複予約する不具合と、召喚待ちを含む列の上限を修正。封印は既存の残留・待ち伏せ・密偵を解除し、封印されたヤーペンが古い状態で次ラウンドに残ることを防ぎます。連鎖、生成カード、対象条件の修正も維持します。',
'提示カードを専用画面で選択。カンタレラでは残すカードとデッキ最下部へ戻すカードが明確になります。非公開カードは裏向きのままです。内部プロフィール名を対戦相手名へ変更し、不要なデッキ見出しと指導者下の空白を削除。白き霜のコントローラー選択、難易度表示、自動パス、相手パス後の無駄な天候も修正しました。',
'テキスト13言語と独立したロシア語・英語・ドイツ語・イタリア語・ブラジルポルトガル語音声。音声を変更してもロシア語のままになる不具合を修正。Autoはゲーム音声言語に従います。',
'RNGは整数オーバーフローに依存せず基準値を検証します。実行環境が契約を満たさない場合、明示された1024個のエンジン乱数による有限循環へ切り替えます。同じ配札が繰り返される問題の解消は実機確認が別途必要です。',
'Classic1.32とNext-Gen5.0+向け。承認済みイラスト、VFX、音楽を保持。自動テストとネイティブコンパイルはゲーム内UI・音声・RNGの動作確認を代替しません。過去の強さ比較は各固定版の結果であり、本版の普遍的優位性は主張しません。'],
'KO':[
'더 다양한 덱. 더 나은 판단. 베타 시절의 궨트.',
'오픈 베타의 궨트를The Witcher3에서 만나보세요. 익숙한 카드, 완전한 덱 편집기, 세계 곳곳의 인물과 대결할 수 있습니다. 공개0.9.3은0.9.1 이후 변경과 최근 플레이 로그의 수정을 통합합니다.',
'클래식은 베타 AI를 이식한 네 번째 난이도입니다. 원본 프로필24개를 덱 설정109개에 배정했으며, 대전 전 언어 설정 옆에서 선택합니다. 플레이어의 손과 덱을 볼 수 있습니다. 일반 어려움은 기존 정보 제한을 유지합니다.',
'승인된 원본 베타 덱30개를 기존46개에 추가했습니다. 일반 구성76개와 퀘스트 인물 설정33개, 중복 없는 구성92개입니다. 원본 덱 이름을 유지합니다. 유사 덱15개는 보류하고 구성 조건에 어긋난28개는 제외했습니다.',
'어려움은 지도자 이후 연계, 짧은 결정 라운드의 카드 순서, 라운드를 양보하기 전 드로우, 유용한 패스를 개선했습니다. 강화는 메노와 전력 초기화, 피해는 안 크라이트 대검사의 회복을 고려합니다. 공개 덱은 상대 비공개 카드와 자신의 공개 시너지를 비교합니다.',
'연속 공개 시 같은 골렘을 중복 예약하는 문제와 대기 중인 소환의 행 정원을 수정했습니다. 봉인은 기존 잔류·매복·첩보원 상태를 제거하여 봉인된 야르펜이 이전 상태로 다음 라운드에 남지 않도록 합니다. 연쇄, 생성 카드, 유효 대상 수정도 유지합니다.',
'제시된 카드는 전용 창에서 고릅니다. 칸타렐라는 손에 남길 카드와 덱 맨 아래로 돌려보낼 카드를 명확히 보여줍니다. 숨겨진 카드는 뒷면을 유지합니다. 내부 프로필 대신 상대 이름을 표시하고 불필요한 덱 제목과 지도자 아래 빈 공간을 없앴습니다. 백색 서리 컨트롤러 포커스, 난이도 표시, 자동 패스, 상대 패스 후 낭비되는 날씨도 수정했습니다.',
'텍스트13개 언어와 독립적인 러시아어·영어·독일어·이탈리아어·브라질 포르투갈어 음성. 음성을 바꿔도 러시아어가 유지되던 문제를 수정했습니다. Auto는 게임의 음성 언어를 따릅니다.',
'RNG는 정수 오버플로에 의존하지 않고 기준값을 검증합니다. 실행 환경이 계약을 충족하지 못하면 명시된 엔진 난수1024개의 유한 순환 예비 방식으로 전환합니다. 반복 배분 해결은 게임 내 검증이 별도로 필요합니다.',
'Classic1.32 및Next-Gen5.0+용입니다. 승인된 그림, VFX, 음악을 유지합니다. 자동 테스트와 네이티브 컴파일은 게임 내 UI·음성·RNG 검증을 대신하지 않습니다. 과거 성능 비교는 각 고정 버전의 결과이며 이 빌드의 보편적 우위를 주장하지 않습니다.'],
'ZH_CN':[
'更多牌组，更周全的出牌，重温公测昆特牌。',
'将公测时期的昆特牌带回The Witcher3：熟悉的卡牌、完整牌组编辑器，以及遍布游戏世界的对手。公开版0.9.3汇总了0.9.1以来的变更和近期对局日志中发现的问题修复。',
'“经典”是移植原版公测AI的第四档难度，24个原始配置对应109套预设，可在对局前的语言设置旁选择。此AI能够查看玩家手牌和牌库；普通困难AI保留原有的信息限制。',
'新增30套获准导入的原版公测牌组，加上现有46套，共76套常规配置与33套任务角色主题预设，去重后92种构成。保留原始牌组名称。15套相似牌组暂缓，28套不符合构筑条件的牌组排除。',
'困难AI改进了领袖后的后续行动、短决胜局的出牌顺序、让局前的过牌与有效放弃跟牌。增益会考虑门诺和战力重置，伤害会考虑奎特家族巨剑士的恢复。揭示牌组会比较对手隐藏手牌与己方揭示联动的收益。',
'修复连续揭示重复预订同一个魔像，以及待执行召唤的排容量问题。锁定会移除已有的坚韧、伏击和间谍状态，锁定的亚尔潘不再凭旧状态留至下一小局。保留连锁、生成卡牌和合法目标修复。',
'候选卡牌现在以独立窗口展示。坎塔蕾拉清楚标明保留哪张、哪张放回牌库底。隐藏牌保持牌背显示。以对手姓名替代内部配置名，移除多余的“你的牌组”标题和领袖下方空白。修复白霜的手柄焦点、难度按钮显示、空手自动放弃跟牌，以及对手放弃后浪费天气牌的问题。',
'支持13种文本语言，语音可独立选择俄语、英语、德语、意大利语和巴西葡萄牙语。修复切换语音后仍播放俄语台词的问题。Auto跟随游戏语音语言。',
'RNG校验参考向量，不再依赖整数溢出。运行环境未通过契约时，使用明确标记的1024个引擎随机值有限循环备用方案。重复发牌问题是否在实际游戏中消失，仍需单独验收。',
'适用于Classic1.32与Next-Gen5.0+。保留已确认的美术、特效和音乐。自动测试及原生编译不能替代游戏内界面、语音和RNG验收。历史强度比较仅对应各自冻结版本，不宣称本版在所有牌组上都更强。'],
'ZH_TW':[
'更多牌組，更周全的出牌，重溫公測昆特牌。',
'將公測時期的昆特牌帶回The Witcher3：熟悉的卡牌、完整牌組編輯器，以及遍布遊戲世界的對手。公開版0.9.3彙整了0.9.1以來的變更及近期對局紀錄中的問題修正。',
'「經典」是移植原版公測AI的第四檔難度，24個原始設定對應109套預設，可在對局前的語言設定旁選擇。此AI能查看玩家手牌與牌庫；一般困難AI保留原有資訊限制。',
'新增30套核准匯入的原版公测牌組，加上現有46套，共76套一般配置與33套任務角色主題預設，去重後92種構成。保留原始牌組名稱。15套相似牌組暫緩，28套不符合構築條件的牌組排除。',
'困難AI改善領袖後的後續行動、短決勝局的出牌順序、讓局前抽牌及有效放棄跟牌。增益會考慮門諾和戰力重設，傷害會考慮奎特家族巨劍士的恢復。揭示牌組會比較對手隱藏手牌與己方揭示連動的收益。',
'修正連續揭示重複預約同一個魔像，以及待執行召喚的排容量問題。鎖定會移除既有的堅韌、伏擊與間諜狀態，鎖定的亞爾潘不再憑舊狀態留至下一小局。保留連鎖、生成卡牌與合法目標修正。',
'候選卡牌改以獨立視窗顯示。坎塔蕾拉清楚標示保留哪張、哪張放回牌庫底。隱藏牌保持牌背顯示。以對手姓名取代內部設定名，移除多餘的「你的牌組」標題與領袖下方空白。修正白霜的控制器焦點、難度按鈕顯示、空手自動放棄跟牌，以及對手放棄後浪費天候牌的問題。',
'支援13種文字語言，語音可獨立選擇俄語、英語、德語、義大利語與巴西葡萄牙語。修正切換語音後仍播放俄語台詞的問題。Auto跟隨遊戲語音語言。',
'RNG校驗參考向量，不再依賴整數溢位。執行環境未通過契約時，使用明確標記的1024個引擎隨機值有限循環備用方案。重複發牌是否在實際遊戲中消失，仍須另外驗收。',
'適用於Classic1.32與Next-Gen5.0+。保留已確認的美術、特效與音樂。自動測試及原生編譯不能取代遊戲內介面、語音與RNG驗收。歷史強度比較僅適用於各自凍結版本，不宣稱本版在所有牌組上均較強。']}
# Choice captions (user request, 25 October 2026): appended to the interface item.
CHOICE_CAPTIONS={'RU': 'Окна выбора карт объясняют результат: у Удальрика выбранная карта уходит в руку, а вторая — в сброс. Такие же подписи получили другие выборы, где важно, куда уйдут выбранная и оставшиеся карты; в остальных выборах показан текст способности карты.', 'EN': 'Card-choice windows now explain the outcome: with Udalryk the chosen card goes to your hand and the other to your graveyard. Other choices where it matters where the chosen and remaining cards go are captioned the same way; the rest show the card’s ability text.', 'DE': 'Kartenauswahlen erklären jetzt das Ergebnis: Bei Udalryk kommt die gewählte Karte auf die Hand, die andere auf den Friedhof. Weitere Auswahlen, bei denen der Verbleib der Karten wichtig ist, sind ebenso beschriftet; die übrigen zeigen den Fähigkeitstext der Karte.', 'FR': 'Les fenêtres de choix expliquent désormais le résultat : avec Udalryk, la carte choisie va dans votre main et l’autre au cimetière. Les autres choix où la destination des cartes compte sont annotés de la même façon ; les autres affichent le texte de la capacité.', 'IT': 'Le finestre di scelta spiegano ora il risultato: con Udalryk la carta scelta va in mano e l’altra nel cimitero. Le altre scelte in cui conta la destinazione delle carte hanno didascalie simili; le restanti mostrano il testo dell’abilità.', 'PL': 'Okna wyboru kart wyjaśniają teraz skutek: przy Udalryku wybrana karta trafia do ręki, a druga na cmentarz. Podobne podpisy mają inne wybory, w których ważne jest, dokąd trafią karty; pozostałe pokazują opis zdolności karty.', 'ES': 'Las ventanas de elección explican ahora el resultado: con Udalryk la carta elegida va a tu mano y la otra, al cementerio. Otras elecciones en las que importa el destino de las cartas llevan rótulos similares; las demás muestran el texto de la habilidad.', 'PT_BR': 'As janelas de escolha agora explicam o resultado: com Udalryk a carta escolhida vai para a mão e a outra, para o cemitério. Outras escolhas em que o destino das cartas importa têm legendas semelhantes; as demais mostram o texto da habilidade.', 'JA': 'カード選択画面に結果の説明を追加。ウダルリックでは選んだカードが手札に、もう1枚が墓場に送られます。カードの行き先が重要な他の選択にも同様の説明を付け、それ以外では能力テキストを表示します。', 'KO': '카드 선택 창에 결과 설명을 추가했습니다. 우달리크는 선택한 카드가 손으로, 나머지가 묘지로 갑니다. 카드의 행방이 중요한 다른 선택에도 같은 설명을 붙였고, 그 밖의 선택에는 능력 설명을 표시합니다.', 'ZH_CN': '选牌窗口现在会说明结果：乌达瑞克选中的牌加入手牌，另一张进入墓场。其他需要说明卡牌去向的选择也有类似提示，其余选择显示卡牌能力文本。', 'ZH_TW': '選牌視窗現在會說明結果：烏達瑞克選中的卡牌加入手牌，另一張進入墓場。其他需要說明卡牌去向的選擇也有類似提示，其餘選擇顯示卡牌能力文字。'}
for _code,_extra in CHOICE_CAPTIONS.items():COPY[_code][6]+=' '+_extra
# Latin-American Spanish has the same neutral-language copy, shipped separately.
COPY['ES_MX']=COPY['ES'].copy()
AMBUSH={
'RU':'При скрытой засаде дерево ответов теперь рассматривает ограниченный набор публично возможных засад, не читая настоящую скрытую карту. Для двух засад исправлены порядок таймеров и расход оставшихся копий. Сохраняется одно смоделированное действие за шаг; общий рост силы этим исправлением не доказан.',
'EN':'With a hidden ambush, the reply tree now considers a bounded set of publicly possible traps without reading the concealed card. Two-trap worlds correctly cover timer order and copies drawn without replacement. One simulated action per step is retained; this fix does not establish an overall strength gain.',
'DE':'Bei verdecktem Hinterhalt prüft der Antwortbaum eine begrenzte Menge öffentlich möglicher Fallen, ohne die verborgene Karte zu lesen. Bei zwei Fallen werden Timerreihenfolge und verbleibende Exemplare korrekt berücksichtigt. Ein simulierter Zug pro Schritt bleibt erhalten; eine allgemeine Spielstärkeverbesserung ist damit nicht belegt.',
'FR':'Face à une embuscade cachée, l’arbre de réponses examine un ensemble limité de pièges publiquement possibles sans lire la carte secrète. Deux pièges respectent l’ordre des compteurs et les exemplaires restants. Une action simulée par étape est conservée; le gain global de force n’est pas établi.',
'IT':'Con un’imboscata nascosta, l’albero delle risposte considera un insieme limitato di trappole pubblicamente possibili senza leggere la carta segreta. Due trappole rispettano ordine dei timer e copie rimanenti. Resta una sola azione simulata per passo; non è dimostrato un aumento generale della forza.',
'PL':'Przy ukrytej zasadzce drzewo odpowiedzi sprawdza ograniczony zestaw publicznie możliwych pułapek bez odczytu tajnej karty. Dwie pułapki uwzględniają kolejność liczników i pozostałe kopie. Nadal jedna symulowana akcja na krok; ogólnego wzrostu siły nie wykazano.',
'ES':'Ante una emboscada oculta, el árbol de respuestas considera un conjunto limitado de trampas públicamente posibles sin leer la carta secreta. Dos trampas respetan el orden de los contadores y las copias restantes. Se conserva una acción simulada por paso; no se demuestra una mejora global de fuerza.',
'ES_MX':'Ante una emboscada oculta, el árbol de respuestas considera un conjunto limitado de trampas públicamente posibles sin leer la carta secreta. Dos trampas respetan el orden de los contadores y las copias restantes. Se conserva una acción simulada por paso; no se demuestra una mejora global de fuerza.',
'PT_BR':'Com uma emboscada oculta, a árvore de respostas considera um conjunto limitado de armadilhas publicamente possíveis sem ler a carta secreta. Duas armadilhas respeitam a ordem dos contadores e as cópias restantes. Continua uma ação simulada por etapa; não foi demonstrado ganho global de força.',
'JA':'非公開の待ち伏せがある場合、相手の秘密カードを読まず、公開情報で可能な罠を予算内で検討します。罠が2枚ある際のカウント順と残り枚数の扱いを修正しました。1ステップ1行動のシミュレーションを維持します。全体的な強さの向上を示すものではありません。',
'KO':'숨겨진 매복이 있으면 실제 비밀 카드를 읽지 않고 공개 정보상 가능한 함정을 예산 안에서 검토합니다. 두 함정의 타이머 순서와 남은 복사본 수를 올바르게 고려합니다. 단계당 모의 행동1회를 유지하며, 전반적인 강도 향상이 입증된 것은 아닙니다.',
'ZH_CN':'存在隐藏伏击时，响应树会在预算内考虑公开信息允许的陷阱，不读取实际隐藏牌。修复了两个陷阱的计时器顺序及剩余副本数量计算。保留每步最多模拟一个行动；这并不证明整体强度提升。',
'ZH_TW':'存在隱藏伏擊時，回應樹會在預算內考慮公開資訊允許的陷阱，不讀取實際隱藏牌。修正兩個陷阱的計時器順序及剩餘副本數量計算。保留每步最多模擬一個行動；這並不證明整體強度提升。'}
for code,text in AMBUSH.items():COPY[code][4]+=' '+text
LATEST={
'RU':'Дополнительно: Циклоп учитывает урон от поглощённого отряда и полное восстановление мечника Ан Крайт при достаточном запасе ходов. Исправлены поглощение Мирруны Кейраном и выбор целей яда/Эльфской сабли. В RNG Classic1.32 убрана проблемная операция остатка. Повреждённые пользовательские слоты восстанавливаются из проверенных резервных банков; уцелевшие колоды и исходные повреждённые данные сохраняются. Запись с неизвестной схемой не затирает резерв. Проверка сохранения и загрузки в самой игре остаётся обязательной.',
'EN':'Additional fixes: Cyclops accounts for the consumed unit’s damage and full An Craite Swordsman recovery when enough turns remain. Kayran consuming Miruna and poison/Elven Saber target dispatch are corrected. Classic1.32 RNG avoids the faulty remainder operation. Damaged custom slots recover from validated backup banks while surviving decks and original damaged data are preserved. Unknown schemas cannot overwrite the backup. In-game save/load acceptance is still required.',
'DE':'Weitere Korrekturen: Zyklop berücksichtigt den Schaden der verschlungenen Einheit und die volle Heilung des An-Craite-Schwertkämpfers bei genügend verbleibenden Zügen. Kayran/Miruna und Gift/Elfensäbel-Ziele sind korrigiert. Classic1.32-RNG vermeidet die fehlerhafte Restoperation. Beschädigte eigene Deckplätze werden aus geprüften Sicherungen wiederhergestellt; erhaltene Decks und beschädigte Originaldaten bleiben bewahrt. Unbekannte Schemata überschreiben keine Sicherung. Speichern und Laden müssen noch im Spiel geprüft werden.',
'FR':'Corrections supplémentaires: le cyclope tient compte de la force consommée et du rétablissement complet de l’espadon an Craite s’il reste assez de tours. Corrections de Kayran/Miruna et des cibles poison/Sabre elfique. Le RNG Classic1.32 évite le modulo défectueux. Les emplacements personnalisés endommagés sont récupérés depuis des sauvegardes vérifiées, sans perdre les jeux survivants ni les données endommagées originales. Un schéma inconnu ne remplace pas la réserve. Sauvegarde et chargement restent à valider en jeu.',
'IT':'Altre correzioni: il ciclope considera la forza consumata e il recupero completo dello spadaccino an Craite quando restano abbastanza turni. Corretti Kayran/Miruna e i bersagli veleno/Sciabola elfica. Il RNG Classic1.32 evita il resto difettoso. Gli slot personalizzati danneggiati vengono recuperati da copie verificate, conservando mazzi superstiti e dati originali danneggiati. Schemi sconosciuti non sovrascrivono la riserva. Salvataggio e caricamento richiedono ancora verifica nel gioco.',
'PL':'Dodatkowo: cyklop uwzględnia siłę pochłoniętej jednostki i pełną regenerację miecznika an Craite, gdy pozostaje dość tur. Poprawiono Kayrana/Mirunę i cele trucizny/Elfiej szabli. RNG Classic1.32 omija wadliwą operację reszty. Uszkodzone własne talie odzyskuje się ze sprawdzonych kopii, zachowując ocalałe talie i oryginalne uszkodzone dane. Nieznany schemat nie nadpisuje kopii. Zapis i odczyt wymagają jeszcze testu w grze.',
'ES':'Más correcciones: el cíclope considera la fuerza consumida y la recuperación completa del espadón an Craite si quedan turnos suficientes. Corregidos Kayran/Miruna y los objetivos de veneno/Sable élfico. El RNG Classic1.32 evita el módulo defectuoso. Los espacios personalizados dañados se recuperan desde copias verificadas, conservando mazos supervivientes y datos originales dañados. Los esquemas desconocidos no sobrescriben la reserva. Guardar y cargar aún requiere validación en el juego.',
'PT_BR':'Mais correções: o ciclope considera a força consumida e a recuperação completa do espadachim an Craite quando restam turnos suficientes. Corrigidos Kayran/Miruna e alvos de veneno/Sabre élfico. O RNG Classic1.32 evita a operação de resto defeituosa. Espaços personalizados danificados são recuperados de cópias verificadas, preservando baralhos sobreviventes e dados originais danificados. Esquemas desconhecidos não sobrescrevem a reserva. Salvar e carregar ainda exige validação no jogo.',
'JA':'追加修正：サイクロプスは捕食したユニットの戦力と、十分なターンが残る場合のアンクライト大剣使いの完全回復を考慮します。ケイラン／ミルナと毒／エルフのサーベルの対象処理を修正。Classic1.32のRNGは不正な剰余演算を回避します。破損したカスタムデッキは検証済みバックアップから復元し、残存デッキと元の破損データを保持します。不明な保存形式はバックアップを上書きしません。ゲーム内でのセーブとロードの確認は別途必要です。',
'KO':'추가 수정: 사이클롭스는 소비한 유닛의 전력과 충분한 턴이 남을 때 안 크라이트 대검사의 완전 회복을 고려합니다. 케이런/미루나와 독/엘프 세이버 대상 처리를 수정했습니다. Classic1.32 RNG는 잘못된 나머지 연산을 피합니다. 손상된 사용자 덱은 검증된 백업에서 복구하며 남은 덱과 원본 손상 데이터를 보존합니다. 알 수 없는 저장 형식은 백업을 덮어쓰지 않습니다. 게임 내 저장/불러오기 검증은 별도로 필요합니다.',
'ZH_CN':'新增修复：独眼巨人会考虑吞噬单位提供的伤害，并在剩余回合足够时计入奎特家族巨剑士的完整恢复。修复Kayran/Miruna以及毒和精灵军刀的目标处理。Classic1.32随机数避开有缺陷的取余运算。损坏的自定义牌组从校验过的备份恢复，并保留尚存牌组及原始损坏数据。未知存档格式不会覆盖备份。仍需在游戏内验证保存和读取。',
'ZH_TW':'新增修正：獨眼巨人會考慮吞噬單位提供的傷害，並在剩餘回合足夠時計入奎特家族巨劍士的完整恢復。修正Kayran/Miruna以及毒和精靈軍刀的目標處理。Classic1.32亂數避開有缺陷的取餘運算。損壞的自訂牌組從校驗過的備份恢復，並保留尚存牌組及原始損壞資料。未知存檔格式不會覆蓋備份。仍需在遊戲內驗證儲存和讀取。'}
LATEST['ES_MX']=LATEST['ES']
LUGOS={
'RU':' Та же поправка на сохранённый урон добавлена Лугосу Безумному.',
'EN':' The same stored-damage correction also covers Madman Lugos.',
'DE':' Dieselbe Korrektur für gespeicherten Schaden gilt auch für Lugos den Irren.',
'FR':' La même correction des dégâts mémorisés couvre aussi Lugos le Dingue.',
'IT':' La stessa correzione del danno memorizzato vale anche per Lugos il Folle.',
'PL':' Ta sama poprawka zapamiętanych obrażeń obejmuje też Szalonego Lugosa.',
'ES':' La misma corrección del daño almacenado también cubre a Lugos el Loco.',
'ES_MX':' La misma corrección del daño almacenado también cubre a Lugos el Loco.',
'PT_BR':' A mesma correção do dano armazenado também vale para Lugos, o Louco.',
'JA':' 同じ保存ダメージの修正はルゴス狂人にも適用されます。',
'KO':' 같은 저장 피해 수정이 미치광이 루고스에게도 적용됩니다.',
'ZH_CN':' 同样的存储伤害修复也适用于疯子卢戈。',
'ZH_TW':' 相同的儲存傷害修正也適用於瘋子盧戈。'}
for code,text in LUGOS.items():LATEST[code]+=text
for code,text in LATEST.items():COPY[code][5]+=' '+text
HEADINGS={
'RU':['Возможности','Изменения с0.9.1','Совместимость и проверка','Релизный пост'],
'EN':['Features','Changes since0.9.1','Compatibility and validation','Release post'],
'DE':['Funktionen','Änderungen seit0.9.1','Kompatibilität und Prüfung','Veröffentlichungsbeitrag'],
'FR':['Fonctionnalités','Changements depuis0.9.1','Compatibilité et validation','Annonce'],
'IT':['Funzionalità','Novità dalla0.9.1','Compatibilità e verifica','Annuncio'],
'PL':['Możliwości','Zmiany od0.9.1','Zgodność i sprawdzenie','Ogłoszenie'],
'ES':['Características','Cambios desde0.9.1','Compatibilidad y validación','Anuncio'],
'ES_MX':['Características','Cambios desde0.9.1','Compatibilidad y validación','Anuncio'],
'PT_BR':['Recursos','Mudanças desde0.9.1','Compatibilidade e validação','Anúncio'],
'JA':['主な機能','0.9.1以降の変更','互換性と検証','リリース投稿'],
'KO':['주요 기능','0.9.1 이후 변경','호환성과 검증','출시 안내'],
'ZH_CN':['主要特色','自0.9.1以来的变更','兼容性与验证','发布帖'],
'ZH_TW':['主要特色','自0.9.1以來的變更','相容性與驗證','發布貼文']}

def spaced(text):
    import re
    # Keep version/quantity boundaries readable in prose, no changes to CJK words.
    return re.sub(r'(?<=[A-Za-zА-Яа-яЁё])(?=\d)|(?<=\d)(?=[A-Za-zА-Яа-яЁё])',' ',text).replace('The Witcher3','The Witcher 3')

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for code,row in COPY.items():
        assert len(row)==10
        tag,lead,mode,decks,ai,rules,ui,voice,rng,limit=map(spaced,row);features,changes,validation,post=map(spaced,HEADINGS[code])
        description=f'# Gwent Beta Classic 0.9.3\n\n**{tag}**\n\n{lead}\n\n## {features}\n\n'+ '\n\n'.join('- '+v for v in [decks,mode,ai,ui,voice])+f'\n\n{spaced(LATEST[code])}\n\n## {validation}\n\n{limit}\n'
        changelog=f'# Gwent Beta Classic 0.9.3 — {changes}\n\n'+ '\n\n'.join('- '+v for v in [mode,decks,ai,rules,ui,voice,rng])+f'\n\n## {validation}\n\n{limit}\n'
        announcement=f'# Gwent Beta Classic 0.9.3\n\n**{tag}**\n\n{lead}\n\n'+ '\n\n'.join('- '+v for v in [mode,decks,ai,ui,voice])+f'\n\n{spaced(LATEST[code])}\n\n{limit}\n'
        for kind,text in [('DESCRIPTION',description),('CHANGELOG',changelog),('POST',announcement)]:
            (OUT/f'0.9.3_{kind}_{code}.md').write_text(text,'utf8')
    entries=[]
    for code in COPY:entries.append(f'| {code} | [Description](0.9.3_DESCRIPTION_{code}.md) | [Post](0.9.3_POST_{code}.md) | [0.9.1 → 0.9.3](0.9.3_CHANGELOG_{code}.md) |')
    (OUT/'README.md').write_text('# Gwent Beta Classic 0.9.3 · publication copy\n\n13 languages. Prepared for review; nothing published.\n\n| Language | Description | Post | Changelog |\n|---|---|---|---|\n'+'\n'.join(entries)+'\n','utf8')
    (OUT/'copy-source.json').write_text(json.dumps(COPY,ensure_ascii=False,indent=2)+'\n','utf8')
    print('Prepared39 localized documents; original release notes unchanged:',OUT)

if __name__=='__main__':main()
