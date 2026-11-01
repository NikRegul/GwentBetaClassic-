"""Public 0.9.4a copy in all thirteen mod languages.

The 0.9.4 documents stay the base text; 0.9.4a adds its own section on top
(deck-editor Beta effects, fixed leader, editor/gamepad fixes, Spectral Whale,
two AI fixes). Card names follow languages137 card text.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/releases/0.9.4-public-20261026'
OUT=ROOT/'docs/releases/0.9.4a-public-20261027'
ORDER=['RU','EN','DE','FR','IT','PL','ES','ES_MX','PT_BR','JA','KO','ZH_CN','ZH_TW']
# heading, tagline, [items], closing note
COPY={
'RU':['Изменения в 0.9.4a','Эффекты беты в редакторе колод и исправления после 0.9.4.',[
 'Редактор колод: при добавлении и удалении карты играют эффекты беты UIDBCardAdd и UIDBCardRemove, перенесённые из её файлов. Эффект появляется на карте коллекции; при настройке «Эффекты: кратко» он не показывается.',
 'Лидер и фракция выбираются только при создании колоды. Раньше кнопки фракций в редакторе могли заменить лидера и убрать из колоды карты. Импорт в открытую колоду принимает только код с её лидером и фракцией.',
 'Фильтры и поиск в редакторе показывают результаты с первой карты, а запоздавшие ответы игры больше не сбивают редактор.',
 'Геймпад: при выборе цели снова видна стрелка прицеливания, как при игре мышью.',
 'Кит из Пещеры Снов в конце хода всегда переходит в другой ряд, как в бете, и не остаётся в своём. Если других свободных рядов нет, он остаётся на месте и всё равно наносит урон.',
 'ИИ: «Сложная» ставит Шелдона Скаггса в ряд, где он действительно разбрасывает отряды и получает усиление. «Классическая» больше не пасует из-за незавершённого расчёта, когда у неё есть выгодный ход.'],
 'Сохранения 0.9.4 подходят без изменений: формат хранилища не менялся. Автоматические проверки и обе компиляции не заменяют проверку в игре.'],
'EN':['Changes in 0.9.4a','Beta deck-editor effects and fixes after 0.9.4.',[
 'Deck editor: adding and removing a card now plays the Beta effects UIDBCardAdd and UIDBCardRemove, ported from the Beta files. The effect appears on the collection card and is not shown with reduced effects.',
 'Leader and faction are chosen only when a deck is created. Previously the faction buttons in the editor could replace the leader and remove cards from the deck. Importing into an open deck accepts only a code with its leader and faction.',
 'Editor filters and search show results from the first card, and late game replies no longer disturb the editor.',
 'Gamepad: the aiming arrow is shown again when choosing a target, as with the mouse.',
 'Spectral Whale now always moves to a different row at turn end, as in the Beta, and never stays in its own. If no other row has room, it stays and still deals its damage.',
 'AI: Hard places Sheldon Skaggs on a row where he really scatters units and gains his boost. Classic no longer passes because of an unfinished calculation when it has a good move.'],
 'Saves from 0.9.4 work as they are: the store format did not change. Automated checks and both compilers do not replace an in-game test.'],
'DE':['Änderungen in 0.9.4a','Beta-Effekte im Deck-Editor und Korrekturen nach 0.9.4.',[
 'Deck-Editor: Beim Hinzufügen und Entfernen einer Karte laufen jetzt die Beta-Effekte UIDBCardAdd und UIDBCardRemove, übernommen aus den Beta-Dateien. Der Effekt erscheint auf der Karte in der Sammlung und entfällt bei reduzierten Effekten.',
 'Anführer und Fraktion werden nur beim Erstellen eines Decks gewählt. Bisher konnten die Fraktionsknöpfe im Editor den Anführer ersetzen und Karten aus dem Deck entfernen. Ein Import in ein geöffnetes Deck nimmt nur einen Code mit dessen Anführer und Fraktion an.',
 'Filter und Suche im Editor zeigen die Ergebnisse ab der ersten Karte, und verspätete Antworten des Spiels bringen den Editor nicht mehr durcheinander.',
 'Gamepad: Bei der Zielwahl ist der Zielpfeil wieder zu sehen, wie mit der Maus.',
 'Spektralwal wechselt am Zugende jetzt immer in eine andere Reihe, wie in der Beta, und bleibt nie in seiner eigenen. Hat keine andere Reihe Platz, bleibt er stehen und verursacht trotzdem Schaden.',
 'KI: Hard setzt Sheldon Skaggs in eine Reihe, in der er tatsächlich Einheiten verteilt und seine Verstärkung erhält. Klassisch passt nicht mehr wegen einer unvollständigen Berechnung, wenn ein guter Zug möglich ist.'],
 'Spielstände aus 0.9.4 funktionieren unverändert: Das Speicherformat ist gleich geblieben. Automatische Tests und beide Compiler ersetzen keinen Test im Spiel.'],
'FR':['Nouveautés de la 0.9.4a','Effets de la bêta dans l’éditeur de decks et corrections après la 0.9.4.',[
 'Éditeur de decks : ajouter ou retirer une carte joue désormais les effets de la bêta UIDBCardAdd et UIDBCardRemove, repris de ses fichiers. L’effet apparaît sur la carte de la collection et n’est pas affiché avec les effets réduits.',
 'Le meneur et la faction ne se choisissent plus qu’à la création du deck. Auparavant, les boutons de faction de l’éditeur pouvaient remplacer le meneur et retirer des cartes du deck. L’import dans un deck ouvert n’accepte qu’un code avec son meneur et sa faction.',
 'Les filtres et la recherche de l’éditeur affichent les résultats depuis la première carte, et les réponses tardives du jeu ne perturbent plus l’éditeur.',
 'Manette : la flèche de visée réapparaît lors du choix d’une cible, comme à la souris.',
 'La Baleine spectrale passe désormais toujours sur une autre ligne en fin de tour, comme dans la bêta, et ne reste jamais sur la sienne. Si aucune autre ligne n’a de place, elle reste et inflige quand même ses dégâts.',
 'IA : Difficile place Sheldon Skaggs sur une ligne où il disperse réellement des unités et obtient son renforcement. Classique ne passe plus à cause d’un calcul inachevé lorsqu’elle a un bon coup.'],
 'Les sauvegardes de la 0.9.4 fonctionnent telles quelles : le format de stockage n’a pas changé. Les tests automatiques et les deux compilateurs ne remplacent pas un essai en jeu.'],
'IT':['Novità della 0.9.4a','Effetti della beta nell’editor dei mazzi e correzioni dopo la 0.9.4.',[
 'Editor dei mazzi: aggiungere o togliere una carta ora riproduce gli effetti della beta UIDBCardAdd e UIDBCardRemove, ripresi dai suoi file. L’effetto compare sulla carta della collezione e non viene mostrato con gli effetti ridotti.',
 'Comandante e fazione si scelgono solo alla creazione del mazzo. Prima i pulsanti delle fazioni nell’editor potevano sostituire il comandante e togliere carte dal mazzo. L’importazione in un mazzo aperto accetta solo un codice con il suo comandante e la sua fazione.',
 'Filtri e ricerca dell’editor mostrano i risultati dalla prima carta, e le risposte tardive del gioco non disturbano più l’editor.',
 'Gamepad: durante la scelta del bersaglio torna visibile la freccia di mira, come con il mouse.',
 'La Balena spettrale ora a fine turno si sposta sempre su un’altra fila, come nella beta, e non resta mai nella propria. Se nessun’altra fila ha posto, resta dov’è e infligge comunque il danno.',
 'IA: Difficile schiera Sheldon Skaggs in una fila dove sparpaglia davvero le unità e ottiene il potenziamento. Classica non passa più per un calcolo incompleto quando ha una buona mossa.'],
 'I salvataggi della 0.9.4 funzionano così come sono: il formato di salvataggio non è cambiato. I test automatici e i due compilatori non sostituiscono una prova in gioco.'],
'PL':['Zmiany w 0.9.4a','Efekty z bety w edytorze talii i poprawki po 0.9.4.',[
 'Edytor talii: dodanie i usunięcie karty odtwarza teraz efekty z bety UIDBCardAdd i UIDBCardRemove, przeniesione z jej plików. Efekt pojawia się na karcie w kolekcji i nie jest pokazywany przy ograniczonych efektach.',
 'Dowódcę i frakcję wybiera się tylko przy tworzeniu talii. Wcześniej przyciski frakcji w edytorze mogły zmienić dowódcę i usunąć karty z talii. Import do otwartej talii przyjmuje tylko kod z jej dowódcą i frakcją.',
 'Filtry i wyszukiwanie w edytorze pokazują wyniki od pierwszej karty, a spóźnione odpowiedzi gry nie zakłócają już edytora.',
 'Pad: przy wyborze celu znowu widać strzałkę celowania, jak przy grze myszą.',
 'Widmowy wieloryb na koniec tury zawsze przechodzi teraz do innego rzędu, jak w becie, i nigdy nie zostaje w swoim. Jeśli w żadnym innym rzędzie nie ma miejsca, zostaje i i tak zadaje obrażenia.',
 'SI: Trudny wystawia Sheldona Skaggsa w rzędzie, w którym naprawdę rozprasza jednostki i dostaje wzmocnienie. Klasyczny nie pasuje już z powodu niedokończonych obliczeń, gdy ma dobry ruch.'],
 'Zapisy z 0.9.4 działają bez zmian: format magazynu się nie zmienił. Testy automatyczne i oba kompilatory nie zastępują próby w grze.'],
'ES':['Cambios en la 0.9.4a','Efectos de la beta en el editor de mazos y correcciones tras la 0.9.4.',[
 'Editor de mazos: al añadir o quitar una carta se reproducen los efectos de la beta UIDBCardAdd y UIDBCardRemove, trasladados de sus archivos. El efecto aparece sobre la carta de la colección y no se muestra con los efectos reducidos.',
 'El líder y la facción solo se eligen al crear el mazo. Antes, los botones de facción del editor podían cambiar el líder y quitar cartas del mazo. Importar en un mazo abierto solo acepta un código con su líder y su facción.',
 'Los filtros y la búsqueda del editor muestran los resultados desde la primera carta, y las respuestas tardías del juego ya no desajustan el editor.',
 'Mando: al elegir objetivo vuelve a verse la flecha de puntería, como con el ratón.',
 'La Ballena espectral ahora siempre pasa a otra fila al final del turno, como en la beta, y nunca se queda en la suya. Si ninguna otra fila tiene sitio, se queda y aun así inflige su daño.',
 'IA: Difícil coloca a Sheldon Skaggs en una fila donde de verdad dispersa unidades y obtiene su mejora. Clásica ya no pasa por un cálculo sin terminar cuando tiene una buena jugada.'],
 'Las partidas guardadas de la 0.9.4 funcionan tal cual: el formato de guardado no ha cambiado. Las pruebas automáticas y los dos compiladores no sustituyen una prueba en el juego.'],
'PT_BR':['Mudanças na 0.9.4a','Efeitos da beta no editor de baralhos e correções após a 0.9.4.',[
 'Editor de baralhos: adicionar e remover uma carta agora reproduz os efeitos da beta UIDBCardAdd e UIDBCardRemove, trazidos dos arquivos dela. O efeito aparece na carta da coleção e não é exibido com efeitos reduzidos.',
 'Líder e facção são escolhidos apenas ao criar o baralho. Antes, os botões de facção do editor podiam trocar o líder e remover cartas do baralho. Importar para um baralho aberto aceita só um código com o líder e a facção dele.',
 'Os filtros e a busca do editor mostram os resultados a partir da primeira carta, e respostas atrasadas do jogo não atrapalham mais o editor.',
 'Controle: ao escolher um alvo, a seta de mira volta a aparecer, como no mouse.',
 'A Baleia Espectral agora sempre vai para outra fileira no fim do turno, como na beta, e nunca fica na própria. Se nenhuma outra fileira tiver espaço, ela fica e ainda causa o dano.',
 'IA: Difícil coloca Sheldon Skaggs em uma fileira onde ele realmente espalha unidades e recebe o fortalecimento. Clássica não passa mais por causa de um cálculo incompleto quando tem uma boa jogada.'],
 'Saves da 0.9.4 funcionam como estão: o formato de armazenamento não mudou. Testes automáticos e os dois compiladores não substituem um teste no jogo.'],
'JA':['0.9.4aの変更点','デッキエディターにベータのエフェクトを追加し、0.9.4以降の不具合を修正しました。',[
 'デッキエディター：カードの追加・削除時に、ベータのファイルから移植したエフェクトUIDBCardAddとUIDBCardRemoveが再生されます。エフェクトはコレクションのカード上に表示され、エフェクトを控えめにする設定では表示されません。',
 'リーダーと勢力はデッキ作成時にのみ選択するようになりました。以前はエディターの勢力ボタンでリーダーが置き換わり、デッキからカードが外れることがありました。開いているデッキへのインポートは、そのデッキのリーダーと勢力のコードのみ受け付けます。',
 'エディターのフィルターと検索は最初のカードから結果を表示し、ゲームからの遅れた応答でエディターが乱れることはなくなりました。',
 'ゲームパッド：対象を選ぶとき、マウスと同じく照準の矢印が再び表示されます。',
 '霊鯨はベータと同様に、ターン終了時に必ず別の列へ移動し、元の列にとどまらなくなりました。ほかの列に空きがない場合はその場にとどまり、ダメージは与えます。',
 'AI：ハードはシェルドン・スカッグスを、実際にユニットを散らしてブーストを得られる列に配置します。クラシックは、有利な手があるのに計算が未完了のためパスすることがなくなりました。'],
 '0.9.4のセーブはそのまま使えます。保存形式は変わっていません。自動テストと両方のコンパイラーは、ゲーム内での確認の代わりにはなりません。'],
'KO':['0.9.4a 변경 사항','덱 편집기에 베타 효과를 넣고 0.9.4 이후의 문제를 고쳤습니다.',[
 '덱 편집기: 카드를 넣거나 뺄 때 베타 파일에서 옮겨 온 UIDBCardAdd, UIDBCardRemove 효과가 재생됩니다. 효과는 컬렉션의 카드 위에 나타나며, 효과 줄이기 설정에서는 표시되지 않습니다.',
 '지도자와 세력은 덱을 만들 때만 고릅니다. 이전에는 편집기의 세력 버튼이 지도자를 바꾸고 덱에서 카드를 빼는 일이 있었습니다. 열린 덱으로 가져오기는 그 덱의 지도자와 세력이 담긴 코드만 받습니다.',
 '편집기의 필터와 검색은 첫 카드부터 결과를 보여 주며, 늦게 도착한 게임 응답이 더 이상 편집기를 흐트러뜨리지 않습니다.',
 '게임패드: 대상을 고를 때 마우스처럼 조준 화살표가 다시 보입니다.',
 '유령 고래는 이제 베타처럼 턴 종료 시 항상 다른 전열로 옮겨 가며 원래 전열에 남지 않습니다. 다른 전열에 빈자리가 없으면 그대로 남아 피해는 줍니다.',
 'AI: 어려움은 쉘든 스켁스를 실제로 유닛을 흩어 증폭을 얻는 전열에 놓습니다. 클래식은 좋은 수가 있을 때 계산이 끝나지 않았다는 이유로 패스하지 않습니다.'],
 '0.9.4 저장은 그대로 쓸 수 있습니다. 저장 형식은 바뀌지 않았습니다. 자동 테스트와 두 컴파일러는 게임 안 확인을 대신하지 않습니다.'],
'ZH_CN':['0.9.4a 更新内容','卡组编辑器加入测试版特效，并修复 0.9.4 之后的问题。',[
 '卡组编辑器：添加和移除卡牌时会播放从测试版文件移植的特效 UIDBCardAdd 和 UIDBCardRemove。特效显示在收藏中的卡牌上，减弱特效时不显示。',
 '领袖和阵营现在只在创建卡组时选择。此前编辑器中的阵营按钮可能更换领袖并从卡组中移除卡牌。导入到已打开的卡组时，只接受其领袖和阵营的代码。',
 '编辑器的筛选和搜索从第一张卡牌开始显示结果，游戏迟到的响应不会再打乱编辑器。',
 '手柄：选择目标时会像使用鼠标一样再次显示瞄准箭头。',
 '幽灵鲸现在会像测试版一样在回合结束时总是移到另一排，不会留在原排。若其他排都没有空位，它会留在原地并仍造成伤害。',
 'AI：困难模式会把谢尔顿·斯卡格斯放在真正能分散单位并获得增益的排。经典模式在有好招时不会再因计算未完成而放弃跟牌。'],
 '0.9.4 的存档可直接使用，存储格式没有变化。自动测试和两种编译器不能代替游戏内的确认。'],
'ZH_TW':['0.9.4a 更新內容','牌組編輯器加入測試版特效，並修正 0.9.4 之後的問題。',[
 '牌組編輯器：加入和移除卡牌時會播放從測試版檔案移植的特效 UIDBCardAdd 與 UIDBCardRemove。特效顯示在收藏中的卡牌上，減少特效時不顯示。',
 '領袖與陣營現在只在建立牌組時選擇。先前編輯器的陣營按鈕可能更換領袖並從牌組移除卡牌。匯入到已開啟的牌組時，只接受其領袖與陣營的代碼。',
 '編輯器的篩選與搜尋從第一張卡牌開始顯示結果，遊戲延遲的回應不會再打亂編輯器。',
 '手把：選擇目標時會像使用滑鼠一樣再次顯示瞄準箭頭。',
 '幽靈鯨現在會像測試版一樣在回合結束時一定移到另一列，不會留在原列。若其他列都沒有空位，它會留在原地並仍造成傷害。',
 'AI：困難模式會把雪爾登．史卡格放在真正能分散單位並獲得提升的列。經典模式在有好棋時，不會再因計算未完成而放棄出牌。'],
 '0.9.4 的存檔可直接使用，儲存格式沒有改變。自動測試與兩種編譯器不能取代遊戲內的確認。']}
EXTRA={
  "RU": [
    "ИИ учитывает эффекты конца текущего хода у кораблей после паса соперника и сохраняет выбранный ряд при размещении в его конце.",
    "Счётчики колоды отмечают превышение лимитов золота и серебра, а также выход за обе границы размера колоды: 25–40 карт."
  ],
  "EN": [
    "AI accounts for ships' end-of-turn effects after the opponent passes and preserves the selected row when placing a card at its end.",
    "Deck counters highlight gold and silver limit violations and both bounds of the 25–40 card limit."
  ],
  "DE": [
    "Die KI berücksichtigt die Effekte der Schiffe am Ende des laufenden Zuges auch nach dem Passen des Gegners und behält beim Platzieren am Reihenende die gewählte Reihe bei.",
    "Deckzähler markieren überschrittene Gold- und Silberlimits sowie beide Grenzen der Deckgröße von 25–40 Karten."
  ],
  "FR": [
    "L'IA tient compte des effets de fin du tour en cours des navires après le passe adverse et conserve la rangée choisie lors d'un placement à son extrémité.",
    "Les compteurs du deck signalent les dépassements des limites d'or et d'argent ainsi que les deux bornes de taille du deck : 25–40 cartes."
  ],
  "IT": [
    "L'IA considera gli effetti delle navi alla fine del turno in corso anche dopo il passo avversario e mantiene la fila scelta quando piazza una carta alla sua estremità.",
    "I contatori del mazzo segnalano i limiti superati di carte oro e argento e le due soglie di dimensione del mazzo: 25–40 carte."
  ],
  "PL": [
    "SI uwzględnia efekty statków na koniec bieżącej tury po pasie przeciwnika i zachowuje wybrany rząd przy umieszczaniu karty na jego końcu.",
    "Liczniki talii oznaczają przekroczenie limitów złota i srebra oraz obu granic rozmiaru talii: 25–40 kart."
  ],
  "ES": [
    "La IA tiene en cuenta los efectos de los barcos al final del turno actual después del pase rival y conserva la fila elegida al colocar una carta en su extremo.",
    "Los contadores del mazo señalan los límites superados de oro y plata y ambos extremos del tamaño del mazo: 25–40 cartas."
  ],
  "ES_MX": [
    "La IA tiene en cuenta los efectos de los barcos al final del turno actual después del pase rival y conserva la fila elegida al colocar una carta en su extremo.",
    "Los contadores del mazo señalan los límites superados de oro y plata y ambos extremos del tamaño del mazo: 25–40 cartas."
  ],
  "PT_BR": [
    "A IA considera os efeitos dos navios no fim do turno atual após o passe do adversário e mantém a fileira escolhida ao colocar uma carta na ponta.",
    "Os contadores do baralho destacam limites excedidos de ouro e prata e ambos os limites do tamanho do baralho: 25–40 cartas."
  ],
  "JA": [
    "AIは相手のパス後も現在のターン終了時に発動する船の効果を考慮し、列の端に配置する際も選択した列を維持します。",
    "デッキのカウンターはゴールドとシルバーの上限超過、および25～40枚というデッキ枚数の両方の境界を示します。"
  ],
  "KO": [
    "AI는 상대가 패스한 뒤에도 현재 턴 종료 시 발동하는 함선 효과를 계산하며, 전열 끝에 카드를 놓을 때도 선택한 전열을 유지합니다.",
    "덱 카운터는 골드·실버 한도 초과와 덱 크기 25~40장의 양쪽 한계를 표시합니다."
  ],
  "ZH_CN": [
    "AI会在对手放弃出牌后继续计算当前回合结束时触发的船只效果，并在排末放置卡牌时保留选定的排。",
    "卡组计数器会标示金卡、银卡超限，以及卡组25至40张的上下限。"
  ],
  "ZH_TW": [
    "AI會在對手放棄出牌後繼續計算目前回合結束時觸發的船隻效果，並在列尾放置卡牌時保留選定的列。",
    "牌組計數器會標示金卡、銀卡超限，以及牌組25至40張的上下限。"
  ]
}
COPY['ES_MX']=COPY['ES']

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for code in ORDER:
        heading,tag,items,note=COPY[code]
        items=list(items)+EXTRA[code]
        bullets='\n\n'.join('- '+x for x in items)
        base=(BASE/f'0.9.4_DESCRIPTION_{code}.md').read_text('utf8')
        assert base.startswith('# Gwent Beta Classic 0.9.4\n'),code
        body=base.split('\n',1)[1];first=body.index('\n## ')
        section=f'## {heading}\n\n{bullets}\n\n{note}\n\n'
        description='# Gwent Beta Classic 0.9.4a\n'+body[:first].rstrip('\n')+'\n\n'+section+body[first+1:].lstrip('\n')
        previous=(BASE/f'0.9.4_CHANGELOG_{code}.md').read_text('utf8').split('\n',1)[1].lstrip('\n')
        changelog=f'# Gwent Beta Classic 0.9.4a — {heading}\n\n{bullets}\n\n{note}\n\n## '+(BASE/f'0.9.4_CHANGELOG_{code}.md').read_text('utf8').split('\n',1)[0].split(' — ',1)[1]+'\n\n'+previous
        post=f'# Gwent Beta Classic 0.9.4a\n\n**{tag}**\n\n{bullets}\n\n{note}\n'
        for kind,text in [('DESCRIPTION',description),('CHANGELOG',changelog),('POST',post)]:
            (OUT/f'0.9.4a_{kind}_{code}.md').write_text(text,'utf8')
    rows=[f'| {c} | [Description](0.9.4a_DESCRIPTION_{c}.md) | [Post](0.9.4a_POST_{c}.md) | [0.9.4 → 0.9.4a](0.9.4a_CHANGELOG_{c}.md) |' for c in ORDER]
    (OUT/'README.md').write_text('# Gwent Beta Classic 0.9.4a · publication copy\n\n13 languages. Prepared for review; nothing published.\n\n| Language | Description | Post | Changelog |\n|---|---|---|---|\n'+'\n'.join(rows)+'\n','utf8')
    (OUT/'copy-source.json').write_text(json.dumps({code:[COPY[code][0],COPY[code][1],list(COPY[code][2])+EXTRA[code],COPY[code][3]] for code in ORDER},ensure_ascii=False,indent=2)+'\n','utf8')
    print('Prepared 39 localized 0.9.4a documents:',OUT)

if __name__=='__main__':main()
