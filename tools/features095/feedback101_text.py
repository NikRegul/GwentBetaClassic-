"""November 1 AI and nested-placement fixes; release copy, no publishing."""
UPDATES = {
    'RU': [
        'Hard возвращает подходящие особые карты в колоду при муллигане, чтобы Итлинна и Эльфский наёмник сохраняли цели. Учитываются настоящий фильтр Итлинны и несколько карт, разыгрывающих особые.',
        'Исправлены бесполезное усиление противника и последняя Казнь по своему отряду без полезного продолжения. Аварийная защита от паса больше не заставляет разыгрывать уже отклонённую вредную карту; полезные комбинации с Казнью сохранены.',
        'Бран учитывает будущую пользу сброса под воскрешение и Серис, чтобы подготовить колоду до расходования этих возможностей. Немедленные очки и подготовка оцениваются раздельно.',
        'Отмена ещё не применённой способности вложенного отряда возвращает тот же обязательный отряд к выбору места без ложной анимации исчезновения. Родительская карта остаётся сыгранной.'
    ],
    'EN': [
        'Hard mulligans suitable special cards back into the deck to keep targets for Ithlinne and Elven Mercenary. It respects Ithlinne’s actual card filter and the number of cards drawing from that pool.',
        'Fixed unproductive enemy boosts and a last Scorch hitting the AI’s own unit without a useful follow-up. The emergency pass safeguard no longer forces a rejected harmful card back into play. Useful Scorch combinations remain available.',
        'Bran accounts for future discard value from resurrection and Cerys, preparing the deck before those opportunities are spent. Setup value is kept separate from immediate score.',
        'Cancelling an uncommitted nested unit ability returns that same mandatory unit to placement without a false disappearance animation. Its parent card remains played.'
    ],
    'DE': [
        'Schwer tauscht passende Spezialkarten zurück ins Deck, damit Ithlinne und Elfen-Söldner Ziele behalten. Ithlinnes tatsächlicher Kartenfilter und mehrere Verbraucher desselben Vorrats werden berücksichtigt.',
        'Nutzlose Verstärkungen des Gegners und eine letzte Verbrennen-Karte gegen die eigene Einheit ohne sinnvolle Fortsetzung wurden korrigiert. Der Notfallschutz vor dem Passen erzwingt keine bereits verworfene schädliche Karte mehr; nützliche Kombinationen bleiben möglich.',
        'Bran berücksichtigt den späteren Nutzen abgeworfener Karten für Wiederbelebung und Cerys und bereitet sie rechtzeitig vor. Vorbereitung und unmittelbare Punkte werden getrennt bewertet.',
        'Der Abbruch einer noch nicht ausgeführten Fähigkeit einer verschachtelten Einheit führt dieselbe Pflichtkarte ohne falsche Verschwindeeffekte zur Platzierung zurück. Die übergeordnete Karte bleibt gespielt.'
    ],
    'FR': [
        'Difficile renvoie des cartes spéciales adaptées dans le deck au mulligan pour conserver des cibles pour Ithlinne et le Mercenaire elfe. Le véritable filtre d’Ithlinne et les besoins de plusieurs cartes sont pris en compte.',
        'Correction des renforcements inutiles de l’adversaire et d’un dernier Incinération touchant une unité alliée sans suite utile. La protection contre un abandon ne force plus à jouer une carte nuisible déjà rejetée ; les combinaisons utiles restent possibles.',
        'Bran évalue le bénéfice futur de la défausse pour la résurrection et Cerys afin de préparer ces cartes à temps. La préparation reste distincte du score immédiat.',
        'Annuler une capacité non encore exécutée d’une unité jouée par une autre carte ramène cette même unité obligatoire au placement, sans fausse animation de disparition. La carte mère reste jouée.'
    ],
    'IT': [
        'Difficile rimette nel mazzo carte speciali adatte durante il mulligan, conservando bersagli per Ithlinne e il Mercenario elfico. Considera il vero filtro di Ithlinne e più carte che usano la stessa riserva.',
        'Corretti i potenziamenti inutili del nemico e un ultimo Incenerimento contro una propria unità senza seguito utile. La protezione dal passaggio non forza più una carta dannosa già scartata dalla valutazione; le combinazioni utili restano disponibili.',
        'Bran valuta il futuro beneficio dello scarto per resurrezione e Cerys, preparando le carte prima di perdere tali opportunità. La preparazione è separata dal punteggio immediato.',
        'Annullare un’abilità non ancora applicata di un’unità giocata da un’altra carta riporta la stessa unità obbligatoria al posizionamento, senza una falsa animazione di scomparsa. La carta madre resta giocata.'
    ],
    'PL': [
        'Trudny oddaje odpowiednie karty specjalne do talii podczas wymiany, zachowując cele dla Ithlinne i Najemnika elfów. Uwzględnia prawdziwy filtr Ithlinne i kilka kart korzystających z tej samej puli.',
        'Poprawiono bezcelowe wzmacnianie przeciwnika i ostatnią Pożogę niszczącą własną jednostkę bez korzystnej kontynuacji. Awaryjna ochrona przed pasem nie wymusza już zagrania odrzuconej szkodliwej karty; przydatne kombinacje pozostają możliwe.',
        'Bran uwzględnia przyszłą korzyść odrzucania pod wskrzeszenie i Cerys, przygotowując karty, zanim te możliwości zostaną zużyte. Przygotowanie jest oceniane oddzielnie od bieżących punktów.',
        'Anulowanie niewykonanej jeszcze zdolności jednostki zagranej przez inną kartę przywraca tę samą obowiązkową jednostkę do ustawiania, bez fałszywej animacji znikania. Karta nadrzędna pozostaje zagrana.'
    ],
    'ES': [
        'Difícil devuelve especiales adecuadas al mazo durante el mulligan para conservar objetivos para Ithlinne y el Mercenario elfo. Respeta el filtro real de Ithlinne y varias cartas que usan la misma reserva.',
        'Corregidas las mejoras inútiles del rival y una última Abrasar contra una unidad propia sin continuación útil. La protección de emergencia al pasar ya no fuerza una carta perjudicial descartada por la evaluación; se conservan las combinaciones útiles.',
        'Bran valora el beneficio futuro de descartar para resurrección y Cerys, preparando las cartas antes de gastar esas oportunidades. La preparación se distingue de la puntuación inmediata.',
        'Cancelar una habilidad todavía no aplicada de una unidad jugada por otra carta devuelve esa misma unidad obligatoria a colocación sin una falsa animación de desaparición. La carta principal sigue jugada.'
    ],
    'PT_BR': [
        'Difícil devolve especiais adequadas ao deck no mulligan para manter alvos para Ithlinne e o Mercenário élfico. Respeita o filtro real de Ithlinne e várias cartas que usam a mesma reserva.',
        'Corrigidos bônus inúteis ao adversário e um último Incinerar contra unidade própria sem continuação útil. A proteção emergencial de passe não força mais uma carta prejudicial já rejeitada pela avaliação; combinações úteis continuam disponíveis.',
        'Bran considera o benefício futuro de descartes para ressurreição e Cerys, preparando as cartas antes de gastar essas oportunidades. Preparação e pontuação imediata são avaliadas separadamente.',
        'Cancelar uma habilidade ainda não aplicada de uma unidade jogada por outra carta devolve a mesma unidade obrigatória à colocação sem falsa animação de desaparecimento. A carta principal permanece jogada.'
    ],
    'JA': [
        'ハードはマリガンで適切なスペシャルカードをデッキへ戻し、IthlinneとElven Mercenaryの対象を確保します。Ithlinneの実際の対象条件と、同じカード群を使う複数のカードを考慮します。',
        '有効な続きのない敵への強化や、最後のScorchで自分のユニットを破壊する判断を修正しました。パスの緊急防止処理が、却下済みの有害なカードを強制的に出すことも防ぎます。有効な組み合わせは維持します。',
        'Branは蘇生とCerysのために捨てる将来価値を考慮し、その機会を使い切る前に準備します。準備の価値と即時の得点は分けて評価します。',
        '別のカードから出したユニットの未実行能力をキャンセルすると、消滅演出なしで同じ必須ユニットの配置選択へ戻ります。親カードのプレイは取り消されません。'
    ],
    'KO': [
        '어려움은 멀리건에서 적절한 특수 카드를 덱에 돌려보내 Ithlinne와 Elven Mercenary의 대상을 남깁니다. Ithlinne의 실제 대상 조건과 같은 카드 풀을 쓰는 여러 카드를 고려합니다.',
        '유용한 후속 행동 없이 적을 강화하거나 마지막 Scorch로 자기 유닛을 파괴하는 판단을 수정했습니다. 긴급 패스 방지가 이미 거부한 해로운 카드를 다시 강제로 내지 않습니다. 유용한 조합은 유지됩니다.',
        'Bran은 부활과 Cerys를 위한 버리기의 미래 가치를 고려해 기회를 소모하기 전에 준비합니다. 준비 가치와 즉시 점수는 따로 평가합니다.',
        '다른 카드로 낸 유닛의 미실행 능력을 취소하면 거짓 소멸 효과 없이 같은 필수 유닛의 배치 선택으로 돌아갑니다. 부모 카드의 플레이는 취소되지 않습니다.'
    ],
    'ZH_CN': [
        '困难AI会在调度时把合适的特殊牌放回牌库，为Ithlinne和精灵佣兵保留目标，并考虑Ithlinne的实际条件及多个使用同一目标池的单位。',
        '修正没有有益后续时强化敌方单位，或用最后一张Scorch消灭己方单位的决策。紧急防止放弃出牌的逻辑不再强制打出已经判定有害的牌；有效组合仍可使用。',
        'Bran会计算为复活和Cerys弃牌的未来收益，在相关机会耗尽前进行准备。准备价值与即时分数分开评估。',
        '取消由其他卡牌打出的单位尚未执行的能力后，会返回同一必打单位的摆放选择，不再出现错误的消失动画；父卡牌仍视为已打出。'
    ],
    'ZH_TW': [
        '困難AI會在調度時把合適的特殊牌放回牌庫，為Ithlinne和精靈傭兵保留目標，並考慮Ithlinne的實際條件及多個使用同一目標池的單位。',
        '修正沒有有益後續時強化敵方單位，或用最後一張Scorch消滅己方單位的決策。緊急防止放棄出牌的邏輯不再強制打出已經判定有害的牌；有效組合仍可使用。',
        'Bran會計算為復活和Cerys棄牌的未來收益，在相關機會耗盡前進行準備。準備價值與即時分數分開評估。',
        '取消由其他卡牌打出的單位尚未執行的能力後，會返回同一必打單位的擺放選擇，不再出現錯誤的消失動畫；父卡牌仍視為已打出。'
    ]
}
UPDATES['ES_MX'] = UPDATES['ES']

# Earlier 0.9.5 follow-ups must remain in the cumulative 0.9.4 -> current post.
FOLLOWUPS = {
    'RU': 'Францеска сохраняет более полезную карту при обмене и учитывает полученную карту вместе с усилением +3. Hard учитывает цену дальнейшей игры под неблагоприятной погодой даже при равной руке. Ослизг оценивает реальные усиленные копии в своей колоде, включая Накеров, а не силу жертвы в сбросе; случайный выбор копии сохранён.',
    'EN': 'Francesca preserves the more useful card when exchanging and accounts for the received card and its +3 boost. Hard considers the cost of continuing under harmful weather even with equal hand sizes. Slyzard values the actual boosted copies in its own deck, including Nekkers, rather than the graveyard victim’s strength; random copy selection is preserved.',
    'DE': 'Francesca behält beim Tauschen die nützlichere Karte und berücksichtigt die erhaltene Karte samt +3. Schwer berücksichtigt die Kosten weiterer Züge unter schädlichem Wetter auch bei gleich großen Händen. Slyzard bewertet die tatsächlich verstärkten Kopien im eigenen Deck, auch Nekker, statt der Stärke des Friedhofsziels; die Kopie wird weiterhin zufällig gewählt.',
    'FR': 'Francesca conserve la carte la plus utile lors de l’échange et tient compte de la nouvelle carte et de son bonus +3. Difficile évalue le coût de continuer sous une météo nuisible même à mains égales. Slyzard évalue les vrais exemplaires renforcés de son deck, dont les Nekkers, au lieu de la force de la cible au cimetière ; le choix de la copie reste aléatoire.',
    'IT': 'Francesca conserva la carta più utile nello scambio e considera quella ricevuta con il bonus +3. Difficile valuta il costo di continuare sotto meteo dannoso anche con mani di pari dimensione. Slyzard valuta le copie realmente potenziate nel proprio mazzo, inclusi i Nekker, anziché la forza del bersaglio nel cimitero; la copia resta scelta casualmente.',
    'PL': 'Francesca zachowuje przy wymianie przydatniejszą kartę i uwzględnia otrzymaną kartę wraz z premią +3. Trudny ocenia koszt dalszej gry przy szkodliwej pogodzie także przy równej liczbie kart. Slyzard ocenia faktycznie wzmocnione kopie we własnej talii, w tym Nekkery, zamiast siły celu na cmentarzu; wybór kopii pozostaje losowy.',
    'ES': 'Francesca conserva la carta más útil al intercambiar y tiene en cuenta la recibida con su mejora +3. Difícil considera el coste de seguir bajo clima dañino incluso con manos del mismo tamaño. Slyzard valora las copias realmente mejoradas de su mazo, incluidos los Nekkers, en lugar de la fuerza del objetivo del cementerio; la copia sigue siendo aleatoria.',
    'PT_BR': 'Francesca preserva a carta mais útil na troca e considera a recebida com o bônus +3. Difícil avalia o custo de continuar sob clima prejudicial mesmo com mãos do mesmo tamanho. Slyzard avalia as cópias realmente fortalecidas no próprio deck, incluindo Nekkers, em vez da força do alvo no cemitério; a cópia continua aleatória.',
    'JA': 'Francescaは交換時に有用なカードを残し、受け取ったカードと+3強化を考慮します。ハードは手札枚数が同じでも不利な天候下で続行する費用を評価します。Slyzardは墓地の対象の戦力ではなく、Nekkerを含む自分のデッキ内の実際に強化されたコピーを評価します。コピーのランダム選択は維持します。',
    'KO': 'Francesca는 교환 시 더 유용한 카드를 보존하고 받은 카드와 +3 증폭을 고려합니다. 어려움은 손패 수가 같아도 해로운 날씨 속에서 계속 플레이하는 비용을 평가합니다. Slyzard는 무덤 대상의 전력이 아니라 Nekker를 포함한 자기 덱의 실제 증폭된 복사본을 평가하며, 복사본 선택은 계속 무작위입니다.',
    'ZH_CN': 'Francesca换牌时保留更有用的卡，并考虑所得卡牌及其+3增益。困难AI在双方手牌数相同时也会计算恶劣天气下继续出牌的成本。Slyzard评估自己牌库中实际已增益的副本，包括Nekker，而非墓地目标的战力；副本仍随机选择。',
    'ZH_TW': 'Francesca換牌時保留更有用的卡，並考慮所得卡牌及其+3增益。困難AI在雙方手牌數相同時也會計算惡劣天氣下繼續出牌的成本。Slyzard評估自己牌庫中實際已增益的副本，包括Nekker，而非墓地目標的戰力；副本仍隨機選擇。'
}
FOLLOWUPS['ES_MX'] = FOLLOWUPS['ES']

# Public post: major changes only. Detailed fixes stay in the cumulative changelog.
OVERVIEW = {
    'RU': ['Сделаны меню колод, коллекции и боя в стиле беты.', 'Исправлены решения ИИ при выборе карт, использовании лидеров, муллигане и пасах.', 'Исправлены правила и способности карт по результатам сверки с бетой.', 'Исправлена загрузка профиля и настроек.'],
    'EN': ['Added Beta-style deck, collection and battle menus.', 'Fixed AI decisions involving cards, leaders, mulligans and passing.', 'Corrected card rules and abilities through comparison with the Beta.', 'Fixed profile and settings loading.'],
    'DE': ['Deck-, Sammlungs- und Kampfmenüs im Stil der Beta erstellt.', 'KI-Entscheidungen zu Karten, Anführern, Kartentausch und Passen korrigiert.', 'Kartenregeln und Fähigkeiten anhand der Beta korrigiert.', 'Laden von Profil und Einstellungen korrigiert.'],
    'FR': ['Ajout des menus de decks, de collection et de combat dans le style de la bêta.', 'Correction des décisions de l’IA pour les cartes, meneurs, mulligans et passes.', 'Correction des règles et capacités des cartes après comparaison avec la bêta.', 'Correction du chargement du profil et des paramètres.'],
    'IT': ['Creati menu di mazzi, collezione e battaglia nello stile della beta.', 'Corrette le decisioni dell’IA su carte, comandanti, mulligan e passaggi.', 'Corrette regole e abilità delle carte confrontandole con la beta.', 'Corretto il caricamento del profilo e delle impostazioni.'],
    'PL': ['Dodano menu talii, kolekcji i walki w stylu bety.', 'Poprawiono decyzje SI dotyczące kart, dowódców, wymiany i pasowania.', 'Poprawiono zasady i zdolności kart po porównaniu z betą.', 'Poprawiono wczytywanie profilu i ustawień.'],
    'ES': ['Creados menús de mazos, colección y combate al estilo de la beta.', 'Corregidas decisiones de la IA sobre cartas, líderes, mulligan y pasar.', 'Corregidas reglas y habilidades de cartas mediante comparación con la beta.', 'Corregida la carga del perfil y los ajustes.'],
    'PT_BR': ['Criados menus de decks, coleção e batalha no estilo da beta.', 'Corrigidas decisões da IA sobre cartas, líderes, mulligan e passe.', 'Corrigidas regras e habilidades de cartas em comparação com a beta.', 'Corrigido o carregamento do perfil e das configurações.'],
    'JA': ['ベータ風のデッキ・コレクション・対戦メニューを実装しました。', 'カード、リーダー、マリガン、パスに関するAIの判断を修正しました。', 'ベータとの照合に基づいてカードのルールと能力を修正しました。', 'プロフィールと設定の読み込みを修正しました。'],
    'KO': ['베타 스타일의 덱, 컬렉션, 전투 메뉴를 만들었습니다.', '카드, 지도자, 멀리건과 패스에 관한 AI 판단을 수정했습니다.', '베타와 대조하여 카드 규칙과 능력을 수정했습니다.', '프로필과 설정 불러오기를 수정했습니다.'],
    'ZH_CN': ['制作了测试版风格的牌组、收藏和战斗菜单。', '修正AI在卡牌、领袖、调度和放弃出牌方面的决策。', '通过与测试版核对，修正卡牌规则和能力。', '修正个人资料和设置的加载。'],
    'ZH_TW': ['製作了測試版風格的牌組、收藏和戰鬥選單。', '修正AI在卡牌、領袖、調度和放棄出牌方面的決策。', '透過與測試版核對，修正卡牌規則和能力。', '修正個人資料和設定的載入。']
}
OVERVIEW['ES_MX'] = OVERVIEW['ES']
