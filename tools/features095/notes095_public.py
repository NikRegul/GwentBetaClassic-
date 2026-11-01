"""0.9.5 copy in all thirteen languages; preserve the previous releases."""
from pathlib import Path
import json
from ui_release095 import NOTES
from ui_release095_text import WINDOWS
from feedback099_text import FEEDBACK
from feedback100_text import PREFERENCES
from feedback101_text import UPDATES,FOLLOWUPS,OVERVIEW

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/releases/0.9.4a-public-20261027'
OUT=NOTES
# heading, interface, pass budget, carryover, limits/compatibility
COPY={
'RU':['Изменения в 0.9.5',
'Редактор: убраны пояснение под лидером и лишний промежуток перед картами. Фон и числа счётчиков выровнены со списком. Предпросмотр вместе со знаменем помещается в правое углубление. Убрано повторение «Соперник: Соперник», настоящие имена сохранены.',
'Hard: убран фиксированный минимум в 26 очков для паса. В развитом необязательном раунде оценка учитывает публичный темп ответа, разницу в картах и цену ещё одного розыгрыша, чтобы не тратить последние карты ради дополнительного запаса очков.',
'ИИ оценивает поле следующего раунда через настоящую очистку поля: стойкость, возвращение Моркварга, ослабление и блокировка. Если сухой пас оставляет его позади, он может сохранить руку и уступить инициативу; с достаточными ресурсами давление остаётся возможным. Скрытые карты и будущий добор Hard не читает.',
'Формат сохранений 0.9.4/0.9.4a сохранён. Общий прирост силы не заявляется. Автоматическая приёмка не заменяет проверку в игре на Classic 1.32 и Next-Gen 5.0+.'],
'EN':['Changes in 0.9.5',
'Deck editor: removed the leader note and extra gap before the cards. Counter backgrounds and numbers align with the list. The preview, including its banner, fits the right recess. Removed the repeated generic opponent label while keeping actual names.',
'Hard: removed the fixed 26-point minimum for passing. In a developed optional round, the decision weighs public reply tempo, card disadvantage and the cost of another play, preserving the last cards instead of buying more score margin.',
'The AI forecasts the next opening board through actual cleanup: resilience, Morkvarg returning, weakening and locking. When a dry pass would leave it behind, it can preserve its hand and concede initiative; sufficient resources still allow pressure. Hard does not read hidden cards or future draws.',
'The 0.9.4/0.9.4a save format is unchanged. No overall strength increase is claimed. Automated acceptance does not replace in-game checks on Classic 1.32 and Next-Gen 5.0+.'],
'DE':['Änderungen in 0.9.5',
'Deck-Editor: Hinweis unter dem Anführer und überflüssigen Abstand entfernt. Zähler und Hintergrund sind an der Liste ausgerichtet. Die Vorschau samt Banner passt in die rechte Vertiefung. Die doppelte allgemeine Gegnerbezeichnung entfällt; echte Namen bleiben erhalten.',
'Schwer: keine feste Mindestführung von 26 Punkten mehr fürs Passen. In einer fortgeschrittenen optionalen Runde zählen das öffentlich geschätzte Antworttempo, Kartennachteil und die Kosten eines weiteren Spielzugs, damit die letzten Karten erhalten bleiben.',
'Die KI berechnet das nächste Startfeld mit der echten Feldbereinigung: Widerstandsfähigkeit, Morkvargs Rückkehr, Schwächung und Sperre. Reicht ein trockener Pass nicht aus, kann sie Karten sparen und die Initiative abgeben; mit genügend Ressourcen bleibt Druck möglich. Verdeckte Karten und künftige Züge werden nicht gelesen.',
'Speicherformat 0.9.4/0.9.4a unverändert. Keine allgemeine Stärkesteigerung behauptet. Automatische Abnahme ersetzt keinen Spieltest auf Classic 1.32 und Next-Gen 5.0+.'],
'FR':['Nouveautés de la 0.9.5',
'Éditeur : suppression de la note sous le meneur et de l’espace avant les cartes. Compteurs et fonds alignés avec la liste. L’aperçu et sa bannière tiennent dans le renfoncement droit. Le nom générique de l’adversaire ne se répète plus ; les vrais noms sont conservés.',
'Difficile : suppression du seuil fixe de 26 points pour passer. Dans une manche facultative avancée, la décision tient compte du tempo de réponse public, du désavantage en cartes et du coût d’un tour supplémentaire afin de préserver les dernières cartes.',
'L’IA prévoit le prochain plateau initial avec le vrai nettoyage : résilience, retour de Morkvarg, affaiblissement et verrouillage. Si passer à vide la laisserait derrière, elle peut conserver sa main et céder l’initiative ; des ressources suffisantes permettent toujours de pousser. Les cartes cachées et les pioches futures ne sont pas lues.',
'Format de sauvegarde 0.9.4/0.9.4a inchangé. Aucun gain global de force annoncé. La validation automatique ne remplace pas les essais en jeu sur Classic 1.32 et Next-Gen 5.0+.'],
'IT':['Novità della 0.9.5',
'Editor: rimossi la nota sotto il comandante e lo spazio prima delle carte. Contatori e sfondi sono allineati alla lista. L’anteprima, stendardo incluso, entra nell’incavo destro. Il nome generico dell’avversario non si ripete più; i nomi reali restano.',
'Difficile: rimossa la soglia fissa di 26 punti per passare. In un round facoltativo avanzato la decisione valuta il ritmo di risposta pubblico, lo svantaggio di carte e il costo di un’altra giocata per conservare le ultime carte.',
'L’IA prevede il prossimo campo iniziale con la pulizia reale: resilienza, ritorno di Morkvarg, indebolimento e blocco. Se un passaggio a vuoto la lascerebbe indietro, può conservare la mano e cedere l’iniziativa; risorse sufficienti consentono ancora di premere. Carte nascoste e pescate future non vengono lette.',
'Formato dei salvataggi 0.9.4/0.9.4a invariato. Nessun aumento generale di forza dichiarato. La verifica automatica non sostituisce le prove in gioco su Classic 1.32 e Next-Gen 5.0+.'],
'PL':['Zmiany w 0.9.5',
'Edytor: usunięto notatkę pod dowódcą i odstęp przed kartami. Liczniki i tła wyrównano do listy. Podgląd wraz ze sztandarem mieści się we wnęce po prawej. Ogólna nazwa przeciwnika nie powtarza się; prawdziwe imiona pozostają.',
'Trudny: usunięto stały próg przewagi 26 punktów do pasowania. W rozwiniętej opcjonalnej rundzie decyzja uwzględnia publiczne tempo odpowiedzi, stratę kart i koszt kolejnego zagrania, aby zachować ostatnie karty.',
'SI przewiduje początkowe pole następnej rundy przez rzeczywiste czyszczenie: wytrzymałość, powrót Morkvarga, osłabienie i blokadę. Gdy suchy pas zostawiłby ją z tyłu, może zachować rękę i oddać inicjatywę; wystarczające zasoby nadal pozwalają naciskać. Nie odczytuje ukrytych kart ani przyszłego dobierania.',
'Format zapisów 0.9.4/0.9.4a bez zmian. Nie deklarujemy ogólnego wzrostu siły. Automatyczne sprawdzenie nie zastępuje testów w grze na Classic 1.32 i Next-Gen 5.0+.'],
'ES':['Cambios en la 0.9.5',
'Editor: eliminados la nota bajo el líder y el hueco antes de las cartas. Contadores y fondos alineados con la lista. La vista previa, incluido el estandarte, cabe en el hueco derecho. La etiqueta genérica del rival ya no se repite; los nombres reales se mantienen.',
'Difícil: eliminado el mínimo fijo de 26 puntos para pasar. En una ronda opcional avanzada se valoran el ritmo público de respuesta, la desventaja de cartas y el coste de otra jugada para conservar las últimas cartas.',
'La IA calcula el próximo tablero inicial mediante la limpieza real: resistencia, regreso de Morkvarg, debilitamiento y bloqueo. Si pasar en seco la dejaría por detrás, puede conservar la mano y ceder la iniciativa; con recursos suficientes aún puede presionar. No lee cartas ocultas ni robos futuros.',
'Formato de guardado 0.9.4/0.9.4a sin cambios. No se afirma una mejora general de fuerza. Las pruebas automáticas no sustituyen las pruebas en juego en Classic 1.32 y Next-Gen 5.0+.'],
'PT_BR':['Mudanças na 0.9.5',
'Editor: removidos o aviso sob o líder e o espaço antes das cartas. Contadores e fundos alinhados à lista. A prévia, incluindo a bandeira, cabe no recuo direito. O nome genérico do adversário não se repete; nomes reais permanecem.',
'Difícil: removido o mínimo fixo de 26 pontos para passar. Em uma rodada opcional avançada, a decisão considera o ritmo público de resposta, a desvantagem em cartas e o custo de outra jogada para preservar as últimas cartas.',
'A IA prevê o próximo campo inicial usando a limpeza real: resiliência, retorno de Morkvarg, enfraquecimento e bloqueio. Se passar a seco a deixaria atrás, pode preservar a mão e ceder a iniciativa; recursos suficientes ainda permitem pressionar. Não lê cartas ocultas nem compras futuras.',
'Formato de saves 0.9.4/0.9.4a inalterado. Não se afirma aumento geral de força. A validação automática não substitui testes no jogo em Classic 1.32 e Next-Gen 5.0+.'],
'JA':['0.9.5の変更点',
'デッキエディター：リーダー下の説明とカード一覧までの余白を削除しました。枚数表示と背景を一覧に整列し、旗を含むプレビューを右側のくぼみに収めました。汎用の対戦相手名の重複をなくし、実際の名前は維持します。',
'ハード：パスに必要だった固定26点差を廃止しました。任意に譲れるラウンドが進んだ時は、公開情報から見た応答の強さ、手札枚数差、さらに1枚使う費用を考慮し、最後のカードを温存します。',
'AIは実際の盤面整理処理で次ラウンドの初期盤面を予測します。耐性、モークヴァーグの復帰、弱体化、封印を反映します。空パスで不利になる時は手札を残して先手を譲ることも、十分な資源で攻めることも可能です。隠れたカードや将来のドローは読みません。',
'0.9.4/0.9.4aのセーブ形式は変わりません。全体的な強さの向上は主張しません。自動検証だけでなくClassic 1.32とNext-Gen 5.0+のゲーム内確認が必要です。'],
'KO':['0.9.5 변경 사항',
'덱 편집기: 지도자 아래 설명과 카드 목록 앞 빈 공간을 없앴습니다. 카운터와 배경을 목록에 맞추고 깃발을 포함한 미리보기를 오른쪽 홈 안에 배치했습니다. 일반 상대 이름의 중복을 없애고 실제 이름은 유지했습니다.',
'어려움: 패스에 필요했던 고정 26점 차 기준을 없앴습니다. 양보할 수 있는 라운드가 진행되면 공개 정보의 대응 템포, 손패 수 차이, 한 장 더 내는 비용을 고려해 마지막 카드들을 보존합니다.',
'AI는 실제 전장 정리로 다음 라운드의 시작 전장을 예측합니다. 회복력, 모크바그의 귀환, 약화와 봉쇄가 반영됩니다. 아무 카드 없이 패스하면 뒤처지는 경우 손패를 보존하고 선공을 넘길 수 있으며 자원이 충분하면 압박할 수 있습니다. 숨겨진 카드나 미래의 드로우는 읽지 않습니다.',
'0.9.4/0.9.4a 저장 형식은 그대로입니다. 전반적인 강도 향상을 주장하지 않습니다. 자동 검증은 Classic 1.32와 Next-Gen 5.0+의 게임 내 확인을 대신하지 않습니다.'],
'ZH_CN':['0.9.5 更新内容',
'卡组编辑器：移除领袖下方说明和卡牌列表前的多余间隔。计数器及背景与列表对齐，含旗帜的预览放入右侧凹槽。不再重复显示通用对手称呼，真实姓名保持不变。',
'困难：取消放弃出牌所需的固定26点领先。对于已进行较久、可以让出的回合，决策会考虑公开信息下的回应强度、手牌差和再打一张牌的成本，以保留最后的手牌。',
'AI通过真实清场流程预测下一回合的初始场面，包括坚韧、莫克瓦格归来、削弱和封锁。如果空过会使自己落后，可以保留手牌并让出先手；资源充足时仍可施压。不读取隐藏卡牌或未来抽牌。',
'0.9.4/0.9.4a存档格式不变。不宣称整体强度提升。自动验证不能代替Classic 1.32和Next-Gen 5.0+的游戏内测试。'],
'ZH_TW':['0.9.5 更新內容',
'牌組編輯器：移除領袖下方說明和卡牌列表前的多餘間隔。計數器及背景與列表對齊，含旗幟的預覽放入右側凹槽。不再重複顯示通用對手稱呼，真實姓名保持不變。',
'困難：取消放棄出牌所需的固定26點領先。對於已進行較久、可以讓出的回合，決策會考慮公開資訊下的回應強度、手牌差和再打一張牌的成本，以保留最後的手牌。',
'AI透過真實清場流程預測下一回合的初始場面，包括堅韌、莫克瓦格歸來、削弱和封鎖。如果空過會使自己落後，可以保留手牌並讓出先手；資源充足時仍可施壓。不讀取隱藏卡牌或未來抽牌。',
'0.9.4/0.9.4a存檔格式不變。不宣稱整體強度提升。自動驗證不能代替Classic 1.32和Next-Gen 5.0+的遊戲內測試。']}
COPY['ES_MX']=COPY['ES']
ORDER=['RU','EN','DE','FR','IT','PL','ES','ES_MX','PT_BR','JA','KO','ZH_CN','ZH_TW']
REVISION={
'RU':'Пересборка 0.9.5: исправлены история зверей Олафа, бонус Ксавьера от силы шаблона, стойкость Цири: натиск и ослабление Моркварга в сбросе перед возвращением. Восстановлен размер полотна предпросмотра, добавлены отступы фиолетовой плашки и исходный эффект достижения 25 карт в редакторе.',
'EN':'0.9.5 rebuild: corrected Olaf’s Beast history, Xavier Moran’s template-strength bonus, Ciri: Dash’s Resilience and Morkvarg’s weakening in the graveyard before returning. Restored the preview card size, added counter-panel insets and the original editor effect for reaching 25 cards.',
'DE':'0.9.5-Neubau: Olafs Bestienhistorie, Xavier Morans Bonus anhand der Vorlagenstärke, Ciri: Dashs Widerstandsfähigkeit und Morkvargs Schwächung im Friedhof vor der Rückkehr korrigiert. Kartenvorschau vergrößert, Zählerfläche eingerückt und ursprünglichen Effekt beim Erreichen von 25 Karten ergänzt.',
'FR':'Nouvelle version 0.9.5 : correction de l’historique des bêtes d’Olaf, du bonus de Xavier Moran fondé sur la force du modèle, de la résilience de Ciri: Dash et de l’affaiblissement de Morkvarg au cimetière avant son retour. Taille de l’aperçu rétablie, marges des compteurs corrigées et effet original des 25 cartes ajouté.',
'IT':'Nuova build 0.9.5: corretti lo storico delle bestie di Olaf, il bonus di Xavier Moran basato sulla forza originale, la resilienza di Ciri: Dash e l’indebolimento di Morkvarg nel cimitero prima del ritorno. Ripristinate le dimensioni dell’anteprima, aggiunti i margini del pannello e l’effetto originale al raggiungimento di 25 carte.',
'PL':'Przebudowa 0.9.5: poprawiono historię bestii Olafa, premię Xaviera Morana opartą na sile wzorca, wytrzymałość Ciri: Dash i osłabienie Morkvarga na cmentarzu przed powrotem. Przywrócono rozmiar podglądu, dodano marginesy liczników oraz oryginalny efekt osiągnięcia 25 kart.',
'ES':'Nueva compilación 0.9.5: corregidos el historial de bestias de Olaf, la bonificación de Xavier Moran según la fuerza de plantilla, la resistencia de Ciri: Dash y el debilitamiento de Morkvarg en el cementerio antes de volver. Restaurado el tamaño de la carta, ajustados los márgenes de contadores y añadido el efecto original al alcanzar 25 cartas.',
'PT_BR':'Nova compilação 0.9.5: corrigidos o histórico de feras de Olaf, o bônus de Xavier Moran pela força do modelo, a resiliência de Ciri: Dash e o enfraquecimento de Morkvarg no cemitério antes do retorno. Restaurado o tamanho da prévia, ajustadas as margens dos contadores e adicionado o efeito original ao atingir 25 cartas.',
'JA':'0.9.5再ビルド：Olafの野獣履歴、Xavier Moranの元のカード定義の戦力による強化、Ciri: Dashの耐性、Morkvargが復帰前に墓地で弱体化する順序を修正しました。プレビューのカードサイズとカウンターの余白を調整し、25枚到達時の元のエフェクトを追加しました。',
'KO':'0.9.5 재빌드: Olaf의 야수 기록, Xavier Moran의 카드 원형 전력 보너스, Ciri: Dash의 회복력, Morkvarg가 복귀 전에 무덤에서 약화되는 순서를 수정했습니다. 미리보기 카드 크기와 카운터 여백을 조정하고 25장 도달 시 원래 효과를 추가했습니다.',
'ZH_CN':'0.9.5重新构建：修正Olaf的野兽打出记录、Xavier Moran按卡牌模板战力获得的增益、Ciri: Dash的坚韧，以及Morkvarg在复归前于墓地削弱的顺序。恢复预览卡牌尺寸，调整计数面板边距，并加入达到25张牌时的原版特效。',
'ZH_TW':'0.9.5重新建置：修正Olaf的野獸打出紀錄、Xavier Moran依卡牌範本戰力獲得的增益、Ciri: Dash的堅韌，以及Morkvarg在回歸前於墓地削弱的順序。恢復預覽卡牌尺寸，調整計數面板邊距，並加入達到25張牌時的原版特效。'}
REVISION['ES_MX']=REVISION['ES']
MENUS={
'RU':'Новые меню колод и коллекции в оформлении беты: фракционный заголовок с именем колоды, сетка из шести колонок, квадратные фильтры и поиск, панель создания справа. Добавлены анимации строк и счётчиков копий, подсказки кнопок контроллера и удержание паса на монете.',
'EN':'New beta-style deck and collection menus: faction deck-name header, six-column grid, square filters and search, and a crafting panel on the right. Added deck-row and copy-counter animations, controller button hints and pass-hold feedback on the coin.',
'DE':'Neue Deck- und Sammlungsmenüs im Beta-Stil: Fraktionskopf mit Decknamen, sechs Spalten, quadratische Filter, Suche und Herstellung rechts. Dazu Animationen für Deckzeilen und Kopienzähler, Controller-Hinweise und Pass-Halten auf der Münze.',
'FR':'Nouveaux menus de decks et de collection de style bêta : titre de faction avec nom du deck, grille à six colonnes, filtres carrés, recherche et fabrication à droite. Animations des lignes et compteurs, indications manette et maintien pour passer sur la pièce.',
'IT':'Nuovi menu mazzi e collezione in stile beta: intestazione di fazione con nome del mazzo, sei colonne, filtri quadrati, ricerca e creazione a destra. Animazioni delle righe e dei contatori, suggerimenti controller e indicatore di passaggio sulla moneta.',
'PL':'Nowe menu talii i kolekcji w stylu bety: nagłówek frakcji z nazwą talii, sześć kolumn, kwadratowe filtry, wyszukiwanie i tworzenie po prawej. Animacje wierszy i liczników, podpowiedzi pada oraz przytrzymanie pasowania na monecie.',
'ES':'Nuevos menús de mazos y colección al estilo beta: cabecera de facción con nombre del mazo, seis columnas, filtros cuadrados, búsqueda y creación a la derecha. Animaciones de filas y contadores, indicaciones del mando y progreso al mantener pasar en la moneda.',
'PT_BR':'Novos menus de decks e coleção no estilo beta: cabeçalho de facção com nome, seis colunas, filtros quadrados, busca e criação à direita. Animações de linhas e contadores, dicas do controle e progresso ao segurar passar na moeda.',
'JA':'ベータ風のデッキ・コレクション画面：勢力とデッキ名の見出し、6列のカード、四角いフィルターと検索、右側の作成パネル。行と枚数のアニメーション、コントローラーのボタン表示、コイン上のパス長押し表示も追加しました。',
'KO':'베타 스타일 덱 및 수집품 메뉴: 진영과 덱 이름 머리글, 6열 카드, 사각 필터와 검색, 오른쪽 제작 패널. 덱 행과 장수 애니메이션, 컨트롤러 버튼 안내, 동전의 패스 길게 누르기 표시를 추가했습니다.',
'ZH_CN':'新版测试版风格卡组与收藏菜单：阵营及卡组名称标题、六列卡牌、方形筛选与搜索、右侧制作面板。新增卡组行和数量动画、手柄按钮提示及硬币上的长按放弃出牌进度。',
'ZH_TW':'新版測試版風格牌組與收藏選單：陣營及牌組名稱標題、六欄卡牌、方形篩選與搜尋、右側製作面板。新增牌組列與數量動畫、控制器按鈕提示及硬幣上的長按放棄出牌進度。'}
MENUS['ES_MX']=MENUS['ES']
RULES={
'RU':'Дальнейшая сверка с бетой: Проклятый рыцарь полностью сбрасывает другую свою копию; Губерт Рейк забирает усиления только усиленных карт колоды и не лечит повреждённые. Нулевая текущая и базовая сила в неактивной зоне вызывает удаление без предсмертного хрипа; Моркварг при ослаблении до нуля удаляется в сбросе.',
'EN':'Further beta rules checks: Cursed Knight fully resets another copy of itself; Hubert Rejk drains only boosted deck cards and does not heal damaged ones. Zero current and base strength in an inactive zone causes banishment without Deathwish; Morkvarg weakened to zero is banished in the graveyard.',
'DE':'Weitere Beta-Regelkorrekturen: Cursed Knight setzt eine andere eigene Kopie vollständig zurück; Hubert Rejk entzieht nur verstärkten Deckkarten den Bonus und heilt keine beschädigten Karten. Stärke und Grundstärke null in einer inaktiven Zone führen zur Verbannung ohne Todeswunsch, auch bei Morkvarg im Friedhof.',
'FR':'Règles bêta : Cursed Knight réinitialise entièrement une autre copie ; Hubert Rejk ne retire que les bonus des cartes renforcées du deck, sans soigner les blessées. Force actuelle et de base nulles dans une zone inactive entraînent le bannissement sans Dernier vœu, y compris pour Morkvarg au cimetière.',
'IT':'Regole beta: Cursed Knight ripristina completamente una seconda copia; Hubert Rejk assorbe solo i potenziamenti delle carte del mazzo, senza curare quelle danneggiate. Forza attuale e base pari a zero in una zona inattiva causano esilio senza Ultimo desiderio, anche per Morkvarg nel cimitero.',
'PL':'Zasady bety: Cursed Knight całkowicie resetuje drugą kopię; Hubert Rejk zabiera tylko premie wzmocnionych kart w talii i nie leczy rannych. Zerowa siła bieżąca i bazowa w nieaktywnej strefie powoduje wygnanie bez Życzenia śmierci, także Morkvarga na cmentarzu.',
'ES':'Reglas beta: Cursed Knight reinicia por completo otra copia; Hubert Rejk drena solo las mejoras de las cartas del mazo, sin curar las dañadas. Fuerza actual y base a cero en una zona inactiva provocan destierro sin Último deseo, incluido Morkvarg en el cementerio.',
'PT_BR':'Regras beta: Cursed Knight restaura completamente outra cópia; Hubert Rejk absorve apenas os bônus das cartas fortalecidas do deck, sem curar as feridas. Força atual e base zeradas em zona inativa causam banimento sem Último Desejo, inclusive para Morkvarg no cemitério.',
'JA':'ベータのルールを追加修正：Cursed Knightは別の同名カードを完全にリセットし、Hubert Rejkはデッキの強化分だけを吸収し、負傷カードを回復しません。非アクティブ領域で現在戦力と基本戦力がともに0になると、遺言なしで消滅します。墓地で0になったMorkvargにも適用されます。',
'KO':'베타 규칙 추가 수정: Cursed Knight는 다른 동일 카드의 상태를 완전히 초기화하고, Hubert Rejk는 덱 카드의 증폭만 흡수하며 손상된 카드를 치유하지 않습니다. 비활성 구역에서 현재 및 기본 전력이 모두 0이면 유언 없이 추방됩니다. 무덤에서 0이 된 Morkvarg에도 적용됩니다.',
'ZH_CN':'继续修正规则：Cursed Knight会完全重置另一张同名卡；Hubert Rejk只吸收牌库中已增益卡牌的增益，不会治疗受伤卡牌。非战场区域中当前与基础战力均为零时，会放逐且不触发遗愿；Morkvarg在墓地削弱至零时同样放逐。',
'ZH_TW':'繼續修正規則：Cursed Knight會完全重置另一張同名卡；Hubert Rejk只吸收牌庫中已增益卡牌的增益，不會治療受傷卡牌。非戰場區域中當前與基礎戰力均為零時，會放逐且不觸發遺願；Morkvarg在墓地削弱至零時同樣放逐。'}
RULES['ES_MX']=RULES['ES']
OLGIERD={
'RU':'Ольгерд возвращается в конце хода только после гибели: обычный сброс из руки не активирует возвращение, выход из сброса очищает отметку гибели.',
'EN':'Olgierd returns at turn end only after being killed: discarding him from hand does not enable his return, and leaving the graveyard clears the killed flag.',
'DE':'Olgierd kehrt am Zugende nur nach seinem Tod zurück: Abwerfen aus der Hand aktiviert dies nicht; beim Verlassen des Friedhofs wird die Todesmarkierung gelöscht.',
'FR':'Olgierd ne revient en fin de tour qu’après avoir été tué : une défausse depuis la main ne suffit pas ; sortir du cimetière efface cet état.',
'IT':'Olgierd ritorna a fine turno solo dopo essere stato ucciso: scartarlo dalla mano non basta e lasciare il cimitero cancella questo stato.',
'PL':'Olgierd wraca na koniec tury tylko po zabiciu: odrzucenie z ręki nie wystarcza, a opuszczenie cmentarza usuwa znacznik śmierci.',
'ES':'Olgierd vuelve al final del turno solo tras morir: descartarlo de la mano no activa el regreso y salir del cementerio borra esa marca.',
'PT_BR':'Olgierd retorna no fim do turno apenas após morrer: descartá-lo da mão não ativa o retorno, e sair do cemitério limpa essa marca.',
'JA':'Olgierdは倒された場合のみターン終了時に戻ります。手札から捨てても戻らず、墓地を離れると撃破フラグが解除されます。',
'KO':'Olgierd는 파괴된 경우에만 턴 종료 시 돌아옵니다. 손에서 버리는 것으로는 발동하지 않으며 무덤을 떠나면 파괴 표시가 해제됩니다.',
'ZH_CN':'Olgierd只在被消灭后于回合结束时返回；从手牌丢弃不会触发返回，离开墓地会清除被消灭标记。',
'ZH_TW':'Olgierd只在被消滅後於回合結束時返回；從手牌丟棄不會觸發返回，離開墓地會清除被消滅標記。'}
OLGIERD['ES_MX']=OLGIERD['ES']

AUDIT={
'RU':'Исправления аудита карт: восстановлены порядок раскрытия и реакций засад, выбор конкретных экземпляров и случайных целей, фильтры целей и расчёт усилений. Несколько целей Эгана, Радовида, Аарда и других способностей выбираются одним набором до применения эффектов; Лютик и Драйг Бон-Дху допускают предусмотренный пропуск выбора. Исправлены округление Скрытого, раскрытие Толстой Хельги перед выходом из руки, реакция Ледяного великана на мороз и условия драккара. Независимо сверены отдельные ветви 213 из 511 карт; полная проверка всех способностей продолжается.',
'EN':'Card-audit fixes restore reveal and ambush reaction order, exact-instance and random-target selection, target filters and boost calculations. Egan, Radovid, Aard and other multi-target abilities select one set before applying effects; Dandelion and Draig Bon-Dhu allow the intended optional selection. Fixed Unseen Elder’s rounding, Fat Helga’s reveal state before leaving hand, Ice Giant’s frost reaction and Drakkar conditions. Individual branches of 213 of 511 cards have independent checks; the full ability audit remains open.',
'DE':'Die Kartenprüfung korrigiert die Reihenfolge von Aufdecken und Hinterhaltreaktionen, die Auswahl konkreter Karten und Zufallsziele, Zielfilter und Verstärkungen. Egan, Radovid, Aard und weitere Fähigkeiten wählen mehrere Ziele vor den Effekten gemeinsam; Rittersporn und Draig Bon-Dhu erlauben die vorgesehene optionale Auswahl. Rundung, Helgas Aufdeckstatus, die Frostreaktion des Eisriesen und Drakkar-Bedingungen wurden korrigiert. Einzelne Zweige von 213 der 511 Karten sind unabhängig geprüft; die vollständige Prüfung bleibt offen.',
'FR':'L’audit corrige l’ordre des révélations et embuscades, le choix des exemplaires et cibles aléatoires, les filtres et les renforcements. Egan, Radovid, Aard et d’autres capacités choisissent leurs cibles ensemble avant les effets ; Jaskier et Draig Bon-Dhu permettent le choix facultatif prévu. Arrondi, révélation de Helga, réaction au gel du Géant de glace et conditions du Drakkar corrigés. Des branches de 213 cartes sur 511 ont été vérifiées indépendamment ; l’audit complet reste ouvert.',
'IT':'L’audit corregge l’ordine di rivelazione e imboscate, la scelta delle singole copie e dei bersagli casuali, i filtri e i potenziamenti. Egan, Radovid, Aard e altre abilità scelgono tutti i bersagli prima degli effetti; Dandelion e Draig Bon-Dhu consentono la selezione facoltativa prevista. Corretti arrotondamento, rivelazione di Helga, reazione al gelo del Gigante di ghiaccio e condizioni del Drakkar. Verificati indipendentemente singoli rami di 213 carte su 511; l’audit completo resta aperto.',
'PL':'Audyt poprawia kolejność ujawniania i reakcji zasadzek, wybór konkretnych kopii i losowych celów, filtry oraz wzmocnienia. Egan, Radovid, Aard i inne zdolności wybierają cały zestaw celów przed efektami; Jaskier i Draig Bon-Dhu pozwalają pominąć opcjonalny wybór. Poprawiono zaokrąglanie, ujawnienie Helgi, reakcję Lodowego Olbrzyma na mróz i warunki Drakkara. Niezależnie sprawdzono wybrane gałęzie 213 z 511 kart; pełny audyt nadal trwa.',
'ES':'La auditoría corrige el orden de revelación y emboscadas, la selección de copias y objetivos aleatorios, los filtros y las mejoras. Egan, Radovid, Aard y otras habilidades eligen un conjunto antes de aplicar efectos; Dandelion y Draig Bon-Dhu permiten omitir la selección opcional prevista. Corregidos el redondeo, la revelación de Helga, la reacción del Gigante de hielo a la escarcha y las condiciones del Drakkar. Se verificaron de forma independiente ramas de 213 de 511 cartas; la auditoría completa sigue abierta.',
'PT_BR':'A auditoria corrige a ordem de revelação e emboscadas, a seleção de cópias e alvos aleatórios, os filtros e os bônus. Egan, Radovid, Aard e outras habilidades escolhem um conjunto antes dos efeitos; Dandelion e Draig Bon-Dhu permitem pular a seleção opcional prevista. Corrigidos arredondamento, revelação de Helga, reação do Gigante de Gelo à geada e condições do Drakkar. Ramos de 213 das 511 cartas foram verificados independentemente; a auditoria completa continua aberta.',
'JA':'カード監査で公開と伏兵の反応順、個別のカードとランダム対象の選択、対象条件、強化計算を修正しました。Egan、Radovid、Aardなどは効果の適用前に対象をまとめて選び、DandelionとDraig Bon-Dhuは任意選択を省略できます。端数処理、Helgaの手札での公開状態、Ice Giantの霜への反応、Drakkarの条件も修正しました。511枚中213枚の一部の処理を独立検証済みですが、全能力の監査は未完了です。',
'KO':'카드 감사로 공개와 매복 반응 순서, 개별 카드 및 무작위 대상 선택, 대상 조건과 증폭 계산을 수정했습니다. Egan, Radovid, Aard 등은 효과 적용 전에 대상을 한 번에 선택하고 Dandelion과 Draig Bon-Dhu는 선택 사항을 건너뛸 수 있습니다. 반올림, Helga의 손패 공개 상태, Ice Giant의 서리 반응과 Drakkar 조건도 수정했습니다. 511장 중 213장의 일부 분기를 독립 검증했으며 전체 능력 감사는 진행 중입니다.',
'ZH_CN':'卡牌审计修正了揭示和伏击反应顺序、具体卡牌与随机目标选择、目标过滤及增益计算。Egan、Radovid、Aard等能力在应用效果前统一选择目标；Dandelion和Draig Bon-Dhu允许跳过原本可选的选择。另修正取整、Helga离开手牌前的揭示状态、Ice Giant的冰霜反应及Drakkar条件。已独立核对511张牌中213张的部分分支；全部能力审计仍未完成。',
'ZH_TW':'卡牌審計修正了揭示和伏擊反應順序、具體卡牌與隨機目標選擇、目標篩選及增益計算。Egan、Radovid、Aard等能力在套用效果前統一選擇目標；Dandelion和Draig Bon-Dhu允許跳過原本可選的選擇。另修正取整、Helga離開手牌前的揭示狀態、Ice Giant的冰霜反應及Drakkar條件。已獨立核對511張牌中213張的部分分支；全部能力審計仍未完成。'}
AUDIT['ES_MX']=AUDIT['ES']

TARGETING={
'RU':'Выбор направленной цели можно отменить правой кнопкой мыши, Esc или кнопкой «Назад» на геймпаде до первого действия способности. Королева главоглазов возвращается в слот лидера до первого поглощения. Вложенный отряд возвращается к выбору места, без отмены родительской карты. Выбор карт из колоды/сброса не отменяется. Исправлены рамки атласа и непрерывная прокрутка мулигана, колоды и сброса; прогресс и награда показывают фракцию полученной карты, включая нейтральную. Погодный прогноз ИИ больше не восстанавливает броню каждый тик и учитывает гибель более слабого соседа.',
'EN':'Cancel directed targeting with right-click, Escape or gamepad Back before the ability performs its first action. Arachas Queen returns to the leader slot before the first consume. A nested unit returns to placement without undoing its parent card. Deck/graveyard card offers cannot be cancelled. Fixed atlas frames and continuous scrolling in mulligan, deck and graveyard windows; reward art and progress use the received card’s faction, including Neutral. AI weather forecasts spend armour once and account for a weaker neighbour dying.',
'DE':'Gezielte Fähigkeiten lassen sich vor ihrer ersten Aktion mit Rechtsklick, Esc oder Zurück am Controller abbrechen. Die Krabbspinnenkönigin kehrt vor dem ersten Verzehren zum Anführerplatz zurück. Eine verschachtelte Einheit kehrt zur Platzierung zurück; die übergeordnete Karte bleibt gespielt. Kartenauswahl aus Deck/Friedhof ist nicht abbrechbar. Atlasrahmen und durchgehendes Scrollen korrigiert; Belohnung und Fortschritt verwenden die Fraktion der erhaltenen Karte, auch Neutral. Die Wetterprognose verbraucht Rüstung nur einmal und berücksichtigt sterbende schwächere Nachbarn.',
'FR':'Annulez le ciblage avec le clic droit, Échap ou Retour à la manette avant la première action de la capacité. La Reine arachas revient à son emplacement avant la première consommation. Une unité jouée par une autre carte revient au placement sans annuler sa carte mère. Les choix du deck/cimetière restent obligatoires. Cadres d’atlas et défilement continu corrigés ; récompense et progression utilisent la faction de la carte reçue, y compris Neutre. La prévision météo dépense l’armure une seule fois et tient compte de la mort du voisin plus faible.',
'IT':'Annulla il bersaglio con clic destro, Esc o Indietro sul controller prima della prima azione dell’abilità. La Regina arachas torna al posto del comandante prima del primo consumo. Un’unità giocata da un’altra carta torna al posizionamento senza annullare la carta madre. Le scelte da mazzo/cimitero restano obbligatorie. Corretti cornici dell’atlante e scorrimento continuo; ricompensa e progresso usano la fazione della carta ricevuta, anche Neutrale. La previsione meteo consuma l’armatura una sola volta e considera la morte del vicino più debole.',
'PL':'Anuluj celowanie prawym przyciskiem myszy, Esc lub przyciskiem Wstecz na padzie przed pierwszą akcją zdolności. Królowa krabopająków wraca na miejsce dowódcy przed pierwszym pochłonięciem. Jednostka zagrana przez inną kartę wraca do ustawiania, bez cofania karty nadrzędnej. Wybory z talii/cmentarza pozostają obowiązkowe. Poprawiono ramki atlasu i płynne przewijanie; nagroda i postęp używają frakcji otrzymanej karty, także Neutralnej. Prognoza pogody zużywa pancerz raz i uwzględnia śmierć słabszego sąsiada.',
'ES':'Cancela el objetivo con clic derecho, Esc o Atrás del mando antes de la primera acción de la habilidad. La Reina arachas vuelve a su puesto antes de consumir. Una unidad jugada por otra carta vuelve a colocación sin deshacer la carta principal. Las elecciones de mazo/cementerio no se cancelan. Corregidos marcos del atlas y desplazamiento continuo; recompensa y progreso usan la facción de la carta recibida, incluida Neutral. La previsión climática gasta la armadura una sola vez y considera la muerte del vecino más débil.',
'BR':'Cancele a mira com botão direito, Esc ou Voltar no controle antes da primeira ação da habilidade. A Rainha aracna volta ao espaço de líder antes de consumir. Uma unidade jogada por outra carta volta à colocação sem desfazer a carta principal. Escolhas do baralho/cemitério não podem ser canceladas. Corrigidos molduras do atlas e rolagem contínua; recompensa e progresso usam a facção da carta recebida, incluindo Neutra. A previsão do clima gasta armadura uma vez e considera a morte do vizinho mais fraco.',
'JP':'能力の最初の効果が発生する前なら、右クリック・Esc・ゲームパッドの戻るで対象選択をキャンセルできます。アラキス・クイーンは最初の捕食前にリーダー枠へ戻ります。別のカードからプレイしたユニットは親カードを取り消さず配置選択へ戻ります。デッキ・墓地のカード選択は取り消せません。アトラス枠と連続スクロールを修正。報酬と進行状況は中立を含む獲得カードの勢力を表示します。AIの天候予測は装甲を一度だけ消費し、弱い隣接ユニットの死亡を考慮します。',
'KR':'능력의 첫 효과가 적용되기 전에는 우클릭, Esc 또는 게임패드 뒤로로 대상 선택을 취소할 수 있습니다. 아라카스 여왕은 첫 섭취 전에 지도자 칸으로 돌아갑니다. 다른 카드로 낸 유닛은 부모 카드를 되돌리지 않고 배치 선택으로 돌아갑니다. 덱/무덤 카드 선택은 취소할 수 없습니다. 아틀라스 테두리와 연속 스크롤을 수정했습니다. 보상과 진행도는 중립을 포함해 받은 카드의 진영을 표시합니다. AI 날씨 예측은 방어력을 한 번만 소모하고 더 약한 이웃의 죽음을 고려합니다.',
'CN':'在能力首次产生效果前，可用右键、Esc 或手柄返回键取消选目标。蟹蜘蛛女王在首次吞噬前返回领袖栏。由其他卡牌打出的单位返回摆放选择，不撤销父卡牌。牌库/墓地选牌不可取消。修复图集边框和连续滚动；奖励与进度使用所得卡牌的阵营，包括中立。AI 天气预测只消耗一次护甲，并考虑较弱相邻单位的死亡。',
'TW':'在能力首次產生效果前，可用右鍵、Esc 或手把返回鍵取消選目標。蟹蜘蛛女王在首次吞噬前返回領袖欄。由其他卡牌打出的單位返回擺放選擇，不撤銷父卡牌。牌庫/墓地選牌不可取消。修復圖集邊框和連續捲動；獎勵與進度使用所得卡牌的陣營，包括中立。AI 天氣預測只消耗一次護甲，並考慮較弱相鄰單位的死亡。'}
TARGETING['ES_MX']=TARGETING['ES']
for previous,current in [('BR','PT_BR'),('JP','JA'),('KR','KO'),('CN','ZH_CN'),('TW','ZH_TW')]:TARGETING[current]=TARGETING.pop(previous)


# Preserve the earlier card-fix details in the cumulative changelog. Remove
# only its superseded 213/511 progress sentence; the current audit status follows.
AUDIT_EARLIER={}
for _code,_text in AUDIT.items():
    if _code in ['JA','ZH_CN','ZH_TW']:
        AUDIT_EARLIER[_code]=_text.rstrip('。').rsplit('。',1)[0]+'。'
    else:
        AUDIT_EARLIER[_code]=_text.rsplit('. ',1)[0]+'.'
AUDIT.update({
'RU':'Сверка теперь охватывает основные ветви всех 511 карт; все сочетания способностей ещё не доказаны. Исправлены необязательные выборы, перемешивание и порядок карт, Францеска, Лугос, Агитатор, Лже-Цири и Волкобой. Закрыты девять отложенных пунктов: Кровавый бич создаёт Призрака и без цели; Лже-Цири сохраняет индекс ряда; Эмгыр возвращает карту в конце хода; Гнездо чудовищ усиливает созданный отряд до его развёртывания; исправлены случайный поток Димуна и порядок возврата карт Ге’эльсом, убрана пустая пауза Йеннифэр. Порядок пула шаблонов подтверждён. Все пять вариантов обоих Лавков проверены в каждой позиции предложения; удар охотника на 15 допускает отряд любой стороны.',
'EN':'Primary branches of all 511 cards now have independent checks; every ability combination is not yet proven. Fixed optional selections, shuffles and card order, Francesca, Lugos, Agitator, False Ciri and Wolfsbane. The nine deferred items are addressed: Bloody Flail spawns its token even without a target; False Ciri preserves her row index; Emhyr returns a card at turn end; Monster Nest boosts its child before deploy; Dimun’s random stream and Ge’els’ return order are corrected, and Yennefer’s empty pause is removed. Definition-pool order is verified. All five modes of both Shupe forms are checked in every offered slot; the Hunter’s 15-damage mode can target either side.',
'DE':'Die Hauptzweige aller 511 Karten sind unabhängig geprüft; nicht alle Fähigkeitskombinationen sind bewiesen. Optionale Auswahl, Mischen, Kartenreihenfolge sowie Francesca, Lugos, Agitator, Falsche Ciri und Wolfsbann wurden korrigiert. Die neun offenen Punkte sind bearbeitet: Bloody Flail erzeugt auch ohne Ziel eine Karte, Falsche Ciri behält ihren Reihenindex, Emhyr schickt die Karte am Zugende zurück und Monsternest verstärkt vor dem Ausspielen. Dimuns Zufallsfolge und Ge’els’ Rücklegereihenfolge sind korrigiert; Yennefers leere Pause entfällt. Der Vorlagenpool und alle fünf Modi beider Shupe-Formen in jedem Angebotsplatz sind geprüft; 15 Schaden können beide Seiten treffen.',
'FR':'Les branches principales des 511 cartes ont une vérification indépendante ; toutes les combinaisons restent à démontrer. Choix facultatifs, mélanges, ordre des cartes, Francesca, Lugos, Agitateur, Fausse Ciri et Wolfsbane sont corrigés. Les neuf points différés sont traités : Bloody Flail crée son unité même sans cible, Fausse Ciri conserve sa position, Emhyr renvoie en fin de tour et Nid de monstres renforce avant le déploiement. Suite aléatoire de Dimun et ordre de retour de Ge’els corrigés ; pause vide de Yennefer supprimée. L’ordre du pool et les cinq modes des deux formes de Shupe sont vérifiés dans chaque emplacement ; les 15 dégâts peuvent viser les deux camps.',
'IT':'I rami principali di tutte le 511 carte sono verificati indipendentemente; restano aperte le combinazioni complete. Corretti scelte facoltative, mescolamento, ordine delle carte, Francesca, Lugos, Agitatore, Falsa Ciri e Wolfsbane. Risolti i nove punti rinviati: Bloody Flail genera anche senza bersaglio, Falsa Ciri conserva la posizione, Emhyr restituisce a fine turno e Nido di mostri potenzia prima dello schieramento. Corretti casualità di Dimun e ordine di ritorno di Ge’els; rimossa la pausa vuota di Yennefer. Verificati ordine del pool e tutti i cinque modi di entrambe le forme di Shupe in ogni posizione; i 15 danni possono colpire entrambi i lati.',
'PL':'Główne gałęzie wszystkich 511 kart mają niezależne sprawdzenie; wszystkie kombinacje zdolności pozostają otwarte. Poprawiono opcjonalne wybory, tasowanie, kolejność kart, Francescę, Lugosa, Agitatora, Fałszywą Ciri i Wolfsbane. Zamknięto dziewięć odłożonych punktów: Bloody Flail tworzy kartę także bez celu, Fałszywa Ciri zachowuje pozycję, Emhyr zwraca kartę pod koniec tury, a Gniazdo potworów wzmacnia przed rozmieszczeniem. Poprawiono losowość Dimuna i kolejność zwrotu kart Ge’elsa; usunięto pustą pauzę Yennefer. Sprawdzono kolejność puli oraz pięć trybów obu form Shupe’a na każdej pozycji wyboru; 15 obrażeń może trafić obie strony.',
'ES':'Las ramas principales de las 511 cartas tienen comprobaciones independientes; quedan abiertas las combinaciones completas. Corregidos selección opcional, barajado, orden, Francesca, Lugos, Agitador, Falsa Ciri y Wolfsbane. Resueltos los nueve puntos aplazados: Bloody Flail crea su unidad incluso sin objetivo, Falsa Ciri conserva su posición, Emhyr devuelve al final del turno y Nido de monstruos mejora antes del despliegue. Corregidos el azar de Dimun y el orden de retorno de Ge’els; eliminada la pausa vacía de Yennefer. Verificados el orden del conjunto y los cinco modos de ambas formas de Shupe en cada posición; los 15 de daño pueden apuntar a ambos bandos.',
'PT_BR':'Os ramos principais das 511 cartas têm verificações independentes; as combinações completas continuam abertas. Corrigidos escolhas opcionais, embaralhamento, ordem, Francesca, Lugos, Agitador, Falsa Ciri e Wolfsbane. Resolvidos os nove pontos adiados: Bloody Flail cria sua unidade mesmo sem alvo, Falsa Ciri mantém a posição, Emhyr devolve no fim do turno e Ninho de Monstros fortalece antes do posicionamento. Corrigidos o fluxo aleatório de Dimun e a ordem de retorno de Ge’els; removida a pausa vazia de Yennefer. Verificados a ordem do conjunto e os cinco modos das duas formas de Shupe em cada posição; os 15 de dano podem atingir ambos os lados.',
'JA':'全511枚の主要な分岐を独立検証しました。すべての能力の組み合わせの証明は未完了です。任意選択、シャッフル、カード順、Francesca、Lugos、Agitator、False Ciri、Wolfsbaneを修正。保留の9項目にも対応し、Bloody Flailは対象なしでも生成、False Ciriは列位置を維持、Emhyrはターン終了時に戻し、Monster Nestは配置前に強化します。Dimunの乱数とGe’elsの戻す順を修正し、Yenneferの空の待機を削除。テンプレート順と、Shupe両形態の全5モードを各選択位置で検証しました。15ダメージは両陣営を対象にできます。',
'KO':'511장 모두의 주요 분기를 독립 검증했으며 모든 능력 조합의 증명은 아직 남아 있습니다. 선택 생략, 섞기, 카드 순서, Francesca, Lugos, Agitator, False Ciri, Wolfsbane를 수정했습니다. 보류된 9항목도 처리하여 Bloody Flail은 대상 없이도 생성하고, False Ciri는 열 위치를 유지하며, Emhyr는 턴 종료 시 반환하고, Monster Nest는 배치 전에 증폭합니다. Dimun의 난수와 Ge’els의 반환 순서를 수정하고 Yennefer의 빈 대기를 제거했습니다. 템플릿 순서와 Shupe 두 형태의 5가지 모드를 모든 제시 위치에서 검증했습니다. 15 피해는 양쪽 진영을 대상으로 할 수 있습니다.',
'ZH_CN':'全部511张牌的主要分支均已独立检查，所有能力组合仍待验证。修正可选选择、洗牌、卡牌顺序及Francesca、Lugos、Agitator、False Ciri和Wolfsbane。处理九项遗留问题：Bloody Flail无目标仍生成单位，False Ciri保留行内位置，Emhyr在回合结束时收回卡牌，Monster Nest在部署前增益；修正Dimun的随机流程与Ge’els的回牌顺序，移除Yennefer的空等待。已确认模板池顺序，并在每个选项位置验证Shupe两种形态的全部五种模式；15点伤害可选择双方单位。',
'ZH_TW':'全部511張牌的主要分支均已獨立檢查，所有能力組合仍待驗證。修正可選選擇、洗牌、卡牌順序及Francesca、Lugos、Agitator、False Ciri和Wolfsbane。處理九項遺留問題：Bloody Flail無目標仍生成單位，False Ciri保留行內位置，Emhyr在回合結束時收回卡牌，Monster Nest在部署前增益；修正Dimun的隨機流程與Ge’els的回牌順序，移除Yennefer的空等待。已確認範本池順序，並在每個選項位置驗證Shupe兩種形態的全部五種模式；15點傷害可選擇雙方單位。'})
AUDIT['ES_MX']=AUDIT['ES']

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for code in ORDER:
        heading,*lines=COPY[code];bullets='\n\n'.join('- '+v for v in UPDATES[code]+[FOLLOWUPS[code]]+lines[:3]+[REVISION[code],RULES[code],OLGIERD[code],AUDIT_EARLIER[code],AUDIT[code],MENUS[code],WINDOWS[code],TARGETING[code],FEEDBACK[code],PREFERENCES[code]]);note=lines[3]
        section=f'## {heading}\n\n{bullets}\n\n{note}\n\n'
        previous=(BASE/f'0.9.4a_DESCRIPTION_{code}.md').read_text('utf8').split('\n',1)[1]
        description='# Gwent Beta Classic 0.9.5\n\n'+section+previous.lstrip('\n')
        prior=(BASE/f'0.9.4a_CHANGELOG_{code}.md').read_text('utf8').split('\n## ',1)[0].strip()
        prior=prior.replace('# Gwent Beta Classic 0.9.4a','## Gwent Beta Classic 0.9.4a',1)
        changelog=f'# Gwent Beta Classic 0.9.4 → 0.9.5\n\n{section}'+prior+'\n'
        overview='\n'.join('- '+v for v in OVERVIEW[code])
        post=f'# Gwent Beta Classic 0.9.5\n\n{overview}\n'
        for kind,text in [('DESCRIPTION',description),('CHANGELOG',changelog),('POST',post)]:
            (OUT/f'0.9.5_{kind}_{code}.md').write_text(text,'utf8')
    rows=[f'| {c} | [Description](0.9.5_DESCRIPTION_{c}.md) | [Post](0.9.5_POST_{c}.md) | [0.9.4 → 0.9.5](0.9.5_CHANGELOG_{c}.md) |' for c in ORDER]
    (OUT/'README.md').write_text('# Gwent Beta Classic 0.9.5 · publication copy\n\n13 languages. Prepared for review; nothing published.\n\n| Language | Description | Post | Changelog |\n|---|---|---|---|\n'+'\n'.join(rows)+'\n','utf8')
    (OUT/'copy-source.json').write_text(json.dumps(COPY,ensure_ascii=False,indent=2)+'\n','utf8')
    print('Prepared 39 localized 0.9.5 documents:',OUT)


if __name__=='__main__':main()
