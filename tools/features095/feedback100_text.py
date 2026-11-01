"""Additional November 1 feedback: mandatory offers and saved presentation."""
PREFERENCES={
'RU':'Выбор карты для розыгрыша теперь обязателен во всех аналогичных предложениях, включая Эльфского наёмника, Разведку и сотворение: старое правило необязательного выбора не отменяет это требование. Исправлено восстановление темпа и полноты эффектов из сохранённого профиля; эти настройки передаются отдельной командой и отражаются в меню сразу. Исправления корон и центрирования кнопок включены в те же архивы.',
'EN':'Playing a card is now mandatory in equivalent offers, including Elven Mercenary, Reconnaissance and creation; optional-choice defaults no longer override this obligation. Tempo and effect detail load from the saved profile, use a dedicated update command and refresh in the menu immediately. Crown and button-centering fixes are included in the same archives.',
'DE':'Bei entsprechenden Angeboten, darunter Elfen-Söldner, Aufklärung und Erschaffung, muss eine verfügbare Karte ausgespielt werden. Optionale Standardwerte heben diese Pflicht nicht mehr auf. Tempo und Effektdetails werden aus dem gespeicherten Profil geladen, separat aktualisiert und sofort im Menü angezeigt. Kronen- und Zentrierungskorrekturen sind ebenfalls enthalten.',
'FR':'Les offres équivalentes, dont Mercenaire elfe, Reconnaissance et création, imposent de jouer une carte disponible. Les valeurs facultatives ne suppriment plus cette obligation. Le rythme et le détail des effets sont restaurés depuis le profil sauvegardé, mis à jour séparément et affichés immédiatement dans le menu. Les corrections de couronnes et de centrage sont incluses.',
'IT':'Nelle offerte equivalenti, inclusi Mercenario elfico, Ricognizione e creazione, è obbligatorio giocare una carta disponibile. I valori facoltativi non annullano più tale obbligo. Ritmo e dettaglio degli effetti vengono caricati dal profilo salvato, aggiornati separatamente e mostrati subito nel menu. Incluse anche le correzioni di corone e centraggio.',
'PL':'W odpowiednich ofertach, w tym u Elfiego najemnika, w Rozpoznaniu i tworzeniu kart, trzeba zagrać dostępną kartę. Ustawienia wyboru opcjonalnego nie znoszą tego obowiązku. Tempo i szczegółowość efektów są odczytywane z zapisanego profilu, aktualizowane osobno i od razu widoczne w menu. Dołączono poprawki koron i wyśrodkowania przycisków.',
'ES':'Las ofertas equivalentes, incluidos Mercenario elfo, Reconocimiento y creación, exigen jugar una carta disponible. Los valores opcionales ya no anulan esta obligación. El ritmo y el detalle de efectos se recuperan del perfil guardado, se actualizan por separado y aparecen al instante en el menú. Se incluyen las correcciones de coronas y centrado.',
'PT_BR':'Ofertas equivalentes, incluindo Mercenário élfico, Reconhecimento e criação, exigem jogar uma carta disponível. Valores opcionais não anulam mais essa obrigação. Ritmo e detalhes dos efeitos são restaurados do perfil salvo, atualizados separadamente e exibidos imediatamente no menu. Incluídas as correções de coroas e centralização.',
'JA':'エルフの傭兵、偵察、カード生成など、プレイを求める選択では使用可能なカードを必ず選びます。任意選択の既定値による上書きを修正しました。速度とエフェクトの詳細設定は保存済みプロフィールから復元され、専用の更新処理でメニューへ即時反映されます。王冠とボタン中央配置の修正も同じアーカイブに含まれます。',
'KO':'엘프 용병, 정찰, 카드 생성 등 카드를 내도록 하는 선택에서는 사용 가능한 카드를 반드시 선택합니다. 선택 생략 기본값이 이를 덮어쓰던 문제를 수정했습니다. 속도와 효과 상세 설정은 저장된 프로필에서 복원되고 별도 명령으로 갱신되어 메뉴에 즉시 반영됩니다. 왕관과 버튼 가운데 정렬 수정도 같은 압축 파일에 포함됩니다.',
'ZH_CN':'精灵雇佣兵、侦察和创造等同类选牌中，有可用卡牌时必须选择打出；可选默认值不再覆盖此要求。速度与效果详细程度从保存的档案恢复，通过独立命令更新并立即显示在菜单中。同一压缩包包含王冠与按钮居中修复。',
'ZH_TW':'精靈傭兵、偵察和創造等同類選牌中，有可用卡牌時必須選擇打出；可選預設值不再覆蓋此要求。速度與效果詳細程度從儲存的檔案恢復，透過獨立命令更新並立即顯示於選單。同一壓縮檔包含王冠與按鈕置中修復。'}
PREFERENCES['ES_MX']=PREFERENCES['ES']
GLOBAL_READ={
'RU':'Общая загрузка профиля применяется также к сложности, паузе ИИ, выбранной колоде, коллекции, осколкам и незавершённым бочкам. Чтение не перезаписывает сохранение, включая неизвестный формат.',
'EN':'Shared profile initialization also covers difficulty, AI pause, selected deck, collection, scraps and pending kegs. Reading does not rewrite the save, including unknown formats.',
'DE':'Die gemeinsame Profilinitialisierung gilt auch für Schwierigkeit, KI-Pause, gewähltes Deck, Sammlung, Fragmente und offene Fässer. Lesen überschreibt keine Speicherdaten, auch bei unbekanntem Format.',
'FR':'L’initialisation commune couvre aussi difficulté, pause IA, deck choisi, collection, fragments et barils en attente. La lecture ne réécrit pas la sauvegarde, même de format inconnu.',
'IT':'L’inizializzazione comune include difficoltà, pausa IA, mazzo scelto, collezione, frammenti e barili in sospeso. La lettura non riscrive il salvataggio, anche in formato sconosciuto.',
'PL':'Wspólne wczytywanie profilu obejmuje też trudność, pauzę SI, wybraną talię, kolekcję, skrawki i otwarte beczki. Odczyt nie nadpisuje zapisu, także o nieznanym formacie.',
'ES':'La carga común también cubre dificultad, pausa de IA, mazo elegido, colección, fragmentos y barriles pendientes. La lectura no sobrescribe el guardado, incluidos formatos desconocidos.',
'PT_BR':'A carga comum também inclui dificuldade, pausa da IA, baralho selecionado, coleção, fragmentos e barris pendentes. A leitura não sobrescreve o save, inclusive em formato desconhecido.',
'JA':'共通のプロフィール初期化は難易度、AI待機、選択デッキ、コレクション、紙片、未完了のタルにも適用されます。未知の形式を含め、読み取りでセーブを書き換えません。',
'KO':'공통 프로필 초기화는 난이도, AI 대기, 선택 덱, 수집품, 조각, 미완료 술통에도 적용됩니다. 알 수 없는 형식을 포함해 읽기가 저장 데이터를 덮어쓰지 않습니다.',
'ZH_CN':'统一档案加载也覆盖难度、AI停顿、所选牌组、收藏、碎片和未完成的桶。读取不会覆盖存档，包括未知格式。',
'ZH_TW':'統一檔案載入也涵蓋難度、AI停頓、所選牌組、收藏、碎片與未完成的桶。讀取不會覆寫存檔，包括未知格式。'}
GLOBAL_READ['ES_MX']=GLOBAL_READ['ES']
for code in PREFERENCES:PREFERENCES[code]+=' '+GLOBAL_READ[code]
