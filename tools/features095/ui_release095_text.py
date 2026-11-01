"""UI-only release copy. Card audit notes remain owned by notes095_public.py."""
WINDOWS={
'RU':'Обновлены окна выбора и замены карт, итоги со страницей награды (карта и осколки), история, меню боя, просмотр колоды/сброса и диалоги импорта/подтверждений. Сохранены отдельные пояснения ключевых слов, выровнены кнопки контроллера, подключены звуки окон. Это функциональная адаптация: точное оформление, исходные анимации и игровая приёмка ещё не завершены.',
'EN':'Updated card choice and replacement windows, results with card/scrap rewards, history, match menu, deck/graveyard viewers and import/confirmation dialogs. Separate keyword explanations, aligned controller hints and window sounds are included. This is a functional adaptation; exact artwork, original animations and in-game acceptance remain incomplete.',
'DE':'Überarbeitete Kartenwahl und Austauschfenster, Ergebnisse mit Karten- und Restebelohnungen, Verlauf, Spielmenü, Deck-/Friedhofsansicht und Import-/Bestätigungsdialoge. Separate Schlüsselworterklärungen, ausgerichtete Controller-Hinweise und Fenstertöne sind enthalten. Funktionale Anpassung; exakte Grafik, Originalanimationen und Abnahme im Spiel sind noch offen.',
'FR':'Fenêtres de choix et remplacement, résultats avec récompenses en cartes et fragments, historique, menu de partie, vues du deck/cimetière et dialogues d’importation/confirmation mis à jour. Explications des mots-clés séparées, indications manette alignées et sons des fenêtres inclus. Adaptation fonctionnelle ; graphismes exacts, animations originales et validation en jeu restent à terminer.',
'IT':'Aggiornate le finestre di scelta e sostituzione, i risultati con premi in carte e frammenti, la cronologia, il menu partita, le viste mazzo/cimitero e i dialoghi di importazione/conferma. Inclusi spiegazioni separate delle parole chiave, indicazioni controller allineate e suoni delle finestre. Adattamento funzionale; grafica esatta, animazioni originali e verifica in gioco restano da completare.',
'PL':'Zaktualizowano wybór i wymianę kart, wyniki z nagrodami w kartach i fragmentach, historię, menu meczu, podgląd talii/cmentarza oraz import i potwierdzenia. Zachowano osobne objaśnienia słów kluczowych, wyrównano podpowiedzi pada i dodano dźwięki okien. Adaptacja funkcjonalna; dokładna grafika, oryginalne animacje i odbiór w grze pozostają otwarte.',
'ES':'Actualizadas las ventanas de elección y cambio, los resultados con recompensas de cartas y fragmentos, el historial, el menú de partida, las vistas del mazo/cementerio y los diálogos de importación/confirmación. Incluye explicaciones separadas de palabras clave, indicaciones del mando alineadas y sonidos de ventanas. Adaptación funcional; quedan pendientes el aspecto exacto, las animaciones originales y la validación en el juego.',
'PT_BR':'Atualizadas as janelas de escolha e troca, resultados com cartas e fragmentos, histórico, menu da partida, visualização do deck/cemitério e diálogos de importação/confirmação. Inclui explicações separadas de palavras-chave, dicas do controle alinhadas e sons das janelas. Adaptação funcional; arte exata, animações originais e validação no jogo ainda estão pendentes.',
'JA':'カードの選択・交換、カードと紙片の報酬を表示する結果画面、履歴、対戦メニュー、デッキ・墓地の閲覧、インポート・確認ダイアログを更新しました。独立したキーワード解説、整列したコントローラー表示、ウィンドウの効果音を含みます。機能面の移植であり、正確な外観、元のアニメーション、ゲーム内での確認は未完了です。',
'KO':'카드 선택과 교체, 카드 및 조각 보상을 표시하는 결과 화면, 기록, 대전 메뉴, 덱 및 무덤 보기, 가져오기 및 확인 창을 업데이트했습니다. 별도 키워드 설명, 정렬된 컨트롤러 안내, 창 효과음을 포함합니다. 기능 중심 이식이며 정확한 외형, 원본 애니메이션 및 게임 내 검증은 아직 완료되지 않았습니다.',
'ZH_CN':'更新选牌与换牌窗口、含卡牌和碎片奖励的结算页、历史记录、对战菜单、牌库及墓地查看、导入与确认对话框。保留独立关键词说明，对齐手柄提示并接入窗口音效。这是功能适配；精确外观、原版动画及游戏内验收仍未完成。',
'ZH_TW':'更新選牌與換牌視窗、含卡牌及碎片獎勵的結算頁、歷史紀錄、對戰選單、牌庫及墓地檢視、匯入與確認對話框。保留獨立關鍵字說明，對齊控制器提示並接入視窗音效。這是功能適配；精確外觀、原版動畫及遊戲內驗收仍未完成。'}
WINDOWS['ES_MX']=WINDOWS['ES']
CHECKLIST='''
## Настройки и обязательные предложения
- [ ] Темп и полнота эффектов сохраняются при закрытии/открытии меню, следующем бою и после сохранения/загрузки; подпись темпа меняется сразу.
- [ ] Эльфский наёмник с двумя Разведками не имеет «Без розыгрыша»; после выбора Разведки нужно выбрать её отряд.
- [ ] Создание и остальные предложения для розыгрыша нельзя завершить без карты при доступных вариантах; пустой пул не блокирует способность.
## Обратная связь 1 ноября
- [ ] Имлерих: до цели карта приподнята, Плотва остаётся в колоде; отмена возвращает только неподтверждённый розыгрыш. После выбора цели Плотва появляется один раз, отмена закрыта.
- [ ] Эмиссар: при доступных картах нет «Без розыгрыша», нельзя завершить выбор без карты.
- [ ] Короны без цветных пикселей, пергамент без полос; подписи центрируются с мышью и после смены геймпада.
- [ ] Разрушение брони звучит в момент попадания, включая одновременный урон силе; переключатель звука действует.
- [ ] Нет подсказки «Колесо — прокрутить описание».
- [ ] Харальд не тратится в восстановленной позиции с морозом: после ответного паса лучшая линия проигрывает 53:55. Без мороза полный залп выигрывает раунд.
## Окна и звук после аудита
- [ ] Выбор/замена: все варианты доступны, обязательный выбор не пропускается, повторный клик не отправляет второй запрос; позиция соседних карт при замене сохраняется.
- [ ] Предложения из руки показывают боковое описание; скрытая карта остаётся рубашкой.
- [ ] Итоги: счёт каждого завершённого раунда, вкладка «Награды», карта/осколки, отсутствие старой награды после новой партии; Esc/B и Enter/A закрывают один раз.
- [ ] История: список → подробности → карта → возврат; страницы с клавиатуры и LB/RB.
- [ ] Колода/сброс/мулиган: колесо, перетаскивание металлического ползунка, PageUp/PageDown и крестовина достигают последней карты; пергамент движется с картами, рамка обрезает ряды, реальный порядок добора не раскрывается.
- [ ] Импорт/экспорт: буфер обмена, создание недостающих карт, ожидание ответа, защита от повтора/неверной ревизии.
- [ ] Переименование и поиск: смена RU/EN и регистра сохраняет поле ввода и текст.
- [ ] Xbox/PlayStation, обмен A/B и смена устройства: правильные глифы, выравнивание и длинные переводы; в игре проверить все 13 языков.
- [ ] Слышны показ/скрытие выбора, замена, popup, фокус истории, вкладки/счёт итогов, объявление и появление награды. Замена звучит один раз; «Звук: выкл» гасит эти события.
- [ ] Нет старых служебных подсказок и debug-линии; молния, погода, растворение карт и отдельные пояснения ключевых слов сохранены.

Точное оформление и исходные анимации окон ещё не полностью перенесены. Подготовленные события отсутствующих анимаций корон/рангов не считать подключёнными. Автоматическая готовность архива не означает игровую приёмку.
'''
