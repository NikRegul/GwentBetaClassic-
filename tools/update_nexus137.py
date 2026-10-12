"""Apply reviewed 0.6.1 clarifications to the existing 13-language Nexus text."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'BetaGwent/release/publish-0.6.1/NEXUS_DESCRIPTION_0.6.1.txt'
# Each entry: release note, package/localization details, compatibility paragraph.
UPDATES = {
'Русский': (
'[b]Исправление 0.6.1:[/b] устранена причина падения при показе лидеров; результат повторно проверен пользователем на RU. Анимированы портреты карт 21 лидера на столе, в руке при её наличии и в правом просмотре. Наведение не должно перезапускать цикл. Крупные анимации появления персонажей запланированы отдельно.',
'Каждый из пяти пакетов содержит все 13 языков текста; EN — универсальный вариант с английскими голосами. Для смены озвучки установите другой пакет. В DE и IT тролль говорит по-русски. Язык текста сохраняется вместе с сохранением игры. Новый интерфейс переведён ИИ и ожидает вычитки носителями; ES-MX и ZH-TW используют адаптации испанского и упрощённого китайского. Нативные названия предметов зависят от языка игры; часть внешних уведомлений пока остаётся на RU/EN.',
'Удалите устаревшую папку [b]modBetaGwentReduxCompat[/b]: отдельный слой совместимости больше не входит в мод. Совместимость с Redux/Redo Expansion отдельно не подтверждена. Другие переработки гвинта и моды, меняющие его меню, обмен карт или награды, могут конфликтовать. После изменения набора модов заново выполните объединение скриптов в Script Merger.'),
'Deutsch': (
'[b]0.6.1-Korrektur:[/b] Die Ursache des Absturzes bei der Anführervorstellung wurde behoben; der Nutzer hat den RU-Build erneut erfolgreich getestet. Animiert sind die Kartenporträts der 21 Anführer auf dem Feld, gegebenenfalls auf der Hand und in der rechten Vorschau. Das Überfahren mit der Maus sollte den Zyklus nicht neu starten. Große Auftrittsanimationen der Figuren sind separat geplant.',
'Jedes der fünf Pakete enthält alle 13 Textsprachen; EN ist die universelle Variante mit englischen Stimmen. Für andere Stimmen installiere ein anderes Paket. In DE und IT spricht der Fass-Troll Russisch. Die Textsprache wird mit dem Spielstand gespeichert. Die neue Oberfläche wurde mit KI übersetzt und benötigt muttersprachliche Prüfung; ES-MX und ZH-TW sind Anpassungen des spanischen und vereinfachten chinesischen Texts. Native Gegenstandsnamen folgen der Spielsprache; einige Meldungen außerhalb der Oberfläche bleiben vorerst RU/EN.',
'Entferne den veralteten Ordner [b]modBetaGwentReduxCompat[/b]; die separate Kompatibilitätsschicht ist nicht mehr enthalten. Die Kompatibilität mit Redux/Redo Expansion wurde nicht separat bestätigt. Andere Gwint-Überarbeitungen und Mods für Gwint-Menüs, Kartenhandel oder Belohnungen können Konflikte verursachen. Führe nach Änderungen an der Mod-Auswahl die Skriptzusammenführung in Script Merger erneut aus.'),
'Français': (
'[b]Correctif 0.6.1 :[/b] la cause du plantage pendant la présentation des chefs a été corrigée ; le joueur a confirmé le résultat sur le paquet RU. Les portraits des cartes des 21 chefs sont animés sur le plateau, en main lorsque la carte y figure et dans l’aperçu à droite. Le survol ne devrait pas relancer la boucle. Les grandes animations d’apparition des personnages sont prévues séparément.',
'Chacun des cinq paquets contient les 13 langues de texte ; EN est la version universelle avec les voix anglaises. Pour changer les voix, installez un autre paquet. Dans DE et IT, le troll des tonneaux parle russe. La langue du texte est enregistrée avec la sauvegarde. La nouvelle interface a été traduite par IA et doit être relue par des locuteurs natifs ; ES-MX et ZH-TW adaptent l’espagnol et le chinois simplifié. Les noms natifs des objets suivent la langue du jeu ; certaines notifications extérieures restent en RU/EN.',
'Supprimez l’ancien dossier [b]modBetaGwentReduxCompat[/b] : la couche de compatibilité séparée n’est plus incluse. La compatibilité avec Redux/Redo Expansion n’a pas été confirmée séparément. Les autres refontes du Gwynt et les mods touchant ses menus, les échanges de cartes ou les récompenses peuvent entrer en conflit. Après avoir modifié vos mods, refaites la fusion des scripts avec Script Merger.'),
'Italiano': (
'[b]Correzione 0.6.1:[/b] risolta la causa del crash durante la presentazione dei comandanti; l’utente ha confermato il risultato con il pacchetto RU. Sono animati i ritratti delle carte dei 21 comandanti sul campo, in mano quando presenti e nell’anteprima a destra. Il passaggio del mouse non dovrebbe riavviare il ciclo. Le grandi animazioni di apparizione dei personaggi sono previste separatamente.',
'Ognuno dei cinque pacchetti contiene tutte le 13 lingue di testo; EN è la variante universale con voci inglesi. Per cambiare le voci, installa un altro pacchetto. In DE e IT il troll dei barili parla russo. La lingua del testo viene registrata nel salvataggio. La nuova interfaccia è stata tradotta con IA e richiede una revisione da parte di madrelingua; ES-MX e ZH-TW adattano lo spagnolo e il cinese semplificato. I nomi nativi degli oggetti seguono la lingua del gioco; alcuni messaggi esterni restano in RU/EN.',
'Elimina la vecchia cartella [b]modBetaGwentReduxCompat[/b]: il livello di compatibilità separato non è più incluso. La compatibilità con Redux/Redo Expansion non è stata confermata separatamente. Altre revisioni di Gwent e mod che cambiano menu, scambi di carte o ricompense possono causare conflitti. Dopo aver cambiato le mod installate, ripeti l’unione degli script con Script Merger.'),
'Polski': (
'[b]Poprawka 0.6.1:[/b] usunięto przyczynę awarii podczas prezentacji dowódców; użytkownik potwierdził wynik w paczce RU. Animowane są portrety kart 21 dowódców na planszy, w ręce, gdy karta tam występuje, oraz w podglądzie po prawej. Najechanie kursorem nie powinno rozpoczynać pętli od nowa. Duże animacje pojawiania się postaci są planowane osobno.',
'Każda z pięciu paczek zawiera wszystkie 13 języków tekstu; EN to uniwersalny wariant z angielskimi głosami. Aby zmienić głosy, zainstaluj inną paczkę. W DE i IT troll od beczek mówi po rosyjsku. Język tekstu jest zapisywany wraz ze stanem gry. Nowy interfejs przetłumaczono za pomocą AI i wymaga on korekty przez rodzimych użytkowników języka; ES-MX i ZH-TW to adaptacje hiszpańskiego i chińskiego uproszczonego. Natywne nazwy przedmiotów zależą od języka gry; część komunikatów poza interfejsem pozostaje w RU/EN.',
'Usuń stary folder [b]modBetaGwentReduxCompat[/b]: osobna warstwa zgodności nie jest już dołączana. Zgodność z Redux/Redo Expansion nie została osobno potwierdzona. Inne przeróbki gwinta oraz mody zmieniające jego menu, handel kartami lub nagrody mogą powodować konflikty. Po zmianie zestawu modów ponownie scal skrypty w Script Merger.'),
'Español (España)': (
'[b]Corrección de 0.6.1:[/b] se ha corregido la causa del cierre inesperado al presentar a los líderes; el usuario ha confirmado el resultado con el paquete RU. Se animan los retratos de las cartas de los 21 líderes en el tablero, en la mano cuando aparecen allí y en la vista previa derecha. Pasar el cursor no debería reiniciar el ciclo. Las grandes animaciones de aparición de personajes están previstas por separado.',
'Cada uno de los cinco paquetes incluye los 13 idiomas de texto; EN es la opción universal con voces inglesas. Para cambiar las voces, instala otro paquete. En DE e IT, el trol de los barriles habla ruso. El idioma del texto se almacena con la partida guardada. La nueva interfaz se ha traducido con IA y necesita revisión por hablantes nativos; ES-MX y ZH-TW adaptan el español y el chino simplificado. Los nombres nativos de los objetos siguen el idioma del juego; algunos avisos externos siguen en RU/EN.',
'Elimina la carpeta antigua [b]modBetaGwentReduxCompat[/b]: la capa de compatibilidad independiente ya no se incluye. La compatibilidad con Redux/Redo Expansion no se ha confirmado por separado. Otras revisiones de Gwent y mods que cambien sus menús, el intercambio de cartas o las recompensas pueden causar conflictos. Tras cambiar los mods instalados, vuelve a combinar los scripts con Script Merger.'),
'Español (Latinoamérica)': (
'[b]Corrección de 0.6.1:[/b] se corrigió la causa del cierre inesperado al presentar a los líderes; el usuario confirmó el resultado con el paquete RU. Se animan los retratos de las cartas de los 21 líderes en el tablero, en la mano cuando aparecen allí y en la vista previa derecha. Pasar el cursor no debería reiniciar el ciclo. Las grandes animaciones de aparición de personajes están previstas por separado.',
'Cada uno de los cinco paquetes incluye los 13 idiomas de texto; EN es la opción universal con voces en inglés. Para cambiar las voces, instala otro paquete. En DE e IT, el troll de los barriles habla ruso. El idioma del texto se guarda con la partida. La nueva interfaz se tradujo con IA y necesita revisión por hablantes nativos; ES-MX y ZH-TW adaptan el español y el chino simplificado. Los nombres nativos de los objetos siguen el idioma del juego; algunos avisos externos siguen en RU/EN.',
'Elimina la carpeta anterior [b]modBetaGwentReduxCompat[/b]: la capa de compatibilidad independiente ya no se incluye. La compatibilidad con Redux/Redo Expansion no se confirmó por separado. Otras modificaciones de Gwent y mods que cambien sus menús, el intercambio de cartas o las recompensas pueden causar conflictos. Después de cambiar los mods instalados, vuelve a combinar los scripts con Script Merger.'),
'Português (Brasil)': (
'[b]Correção da 0.6.1:[/b] a causa do fechamento inesperado na apresentação dos líderes foi corrigida; o usuário confirmou o resultado no pacote RU. São animados os retratos das cartas dos 21 líderes no tabuleiro, na mão quando aparecem nela e na prévia à direita. Passar o cursor não deve reiniciar o ciclo. As grandes animações de entrada dos personagens estão previstas separadamente.',
'Cada um dos cinco pacotes inclui os 13 idiomas de texto; EN é a opção universal com vozes em inglês. Para mudar as vozes, instale outro pacote. Em DE e IT, o troll dos barris fala russo. O idioma do texto é registrado no save. A nova interface foi traduzida com IA e precisa de revisão por falantes nativos; ES-MX e ZH-TW adaptam o espanhol e o chinês simplificado. Os nomes nativos dos itens seguem o idioma do jogo; alguns avisos externos continuam em RU/EN.',
'Remova a pasta antiga [b]modBetaGwentReduxCompat[/b]: a camada de compatibilidade separada não é mais incluída. A compatibilidade com Redux/Redo Expansion não foi confirmada separadamente. Outras reformulações do Gwent e mods que alterem seus menus, trocas de cartas ou recompensas podem causar conflitos. Depois de mudar os mods instalados, refaça a mesclagem dos scripts com Script Merger.'),
'日本語': (
'[b]0.6.1の修正：[/b]リーダー紹介中にクラッシュする原因を修正し、RUパッケージではユーザーが再テストで改善を確認しました。21人のリーダーのカード内の肖像が、盤面、手札にある場合の手札、右側のプレビューで動きます。カーソルを合わせてもループが最初から始まらない設計です。キャラクターが大きく登場する演出は別途追加予定です。',
'5種類の各パッケージに13言語すべてのテキストが含まれます。ENは英語音声の汎用パッケージです。音声を変更するには別のパッケージをインストールしてください。DEとITでは樽のトロールがロシア語で話します。テキスト言語はゲームのセーブに保存されます。新しいUIはAI翻訳で、ネイティブによる確認が必要です。ES-MXとZH-TWのUIはスペイン語と簡体字中国語を基に調整しています。ゲーム標準のアイテム名はゲームの言語に従い、一部の外部通知はまだRU/ENです。',
'古い[b]modBetaGwentReduxCompat[/b]フォルダを削除してください。独立した互換レイヤーは含まれなくなりました。Redux/Redo Expansionとの互換性は個別には確認されていません。他のグウェント改変MODや、メニュー、カード取引、報酬を変更するMODとは競合する可能性があります。MOD構成を変更した後はScript Mergerでスクリプトを再マージしてください。'),
'한국어': (
'[b]0.6.1 수정:[/b] 리더 소개 중 충돌을 일으키던 원인을 수정했으며, 사용자가 RU 패키지에서 재시험하여 개선을 확인했습니다. 리더 21명의 카드 초상화가 게임판, 손에 있을 때의 손패, 오른쪽 미리보기에서 움직입니다. 마우스를 올려도 반복 애니메이션이 처음부터 다시 시작되지 않도록 했습니다. 캐릭터가 크게 등장하는 연출은 별도로 추가할 예정입니다.',
'다섯 패키지 모두 13개 텍스트 언어를 포함합니다. EN은 영어 음성을 사용하는 범용 패키지입니다. 음성을 바꾸려면 다른 패키지를 설치하세요. DE와 IT에서는 술통 트롤이 러시아어로 말합니다. 텍스트 언어는 게임 저장 데이터에 기록됩니다. 새 UI는 AI로 번역되어 원어민 검수가 필요하며, ES-MX와 ZH-TW UI는 스페인어와 중국어 간체를 바탕으로 조정했습니다. 게임 기본 아이템 이름은 게임 언어를 따르며 일부 외부 알림은 아직 RU/EN입니다.',
'예전 [b]modBetaGwentReduxCompat[/b] 폴더를 삭제하세요. 별도의 호환 계층은 더 이상 포함되지 않습니다. Redux/Redo Expansion과의 호환성은 별도로 확인되지 않았습니다. 다른 궨트 개편 모드나 메뉴, 카드 거래, 보상을 변경하는 모드는 충돌할 수 있습니다. 설치한 모드 구성을 바꾼 후 Script Merger로 스크립트를 다시 병합하세요.'),
'简体中文': (
'[b]0.6.1 修复：[/b]已修复领袖展示时导致崩溃的原因，用户已在 RU 安装包中复测确认改善。21 张领袖牌的卡面肖像会在牌桌、手牌中出现时以及右侧预览中播放动画。移动鼠标悬停不应让循环重新开始。角色以大幅画面登场的动画将另行加入。',
'五种安装包均包含全部 13 种文字语言；EN 是使用英语语音的通用版本。更换语音需要安装另一种安装包。DE 和 IT 包中的酒桶巨魔使用俄语。文字语言随游戏存档保存。新界面由 AI 翻译，需要母语者校对；ES-MX 和 ZH-TW 界面分别基于西班牙语和简体中文调整。游戏原生物品名称跟随游戏语言，部分界面外通知目前仍为 RU/EN。',
'请删除旧的 [b]modBetaGwentReduxCompat[/b] 文件夹，独立兼容层已不再附带。与 Redux/Redo Expansion 的兼容性尚未单独确认。其他昆特牌改动模组，以及修改菜单、卡牌交易或奖励的模组可能产生冲突。更改模组组合后，请用 Script Merger 重新合并脚本。'),
'繁體中文': (
'[b]0.6.1 修正：[/b]已修正領導牌展示時導致當機的原因，使用者已在 RU 安裝包中重新測試並確認改善。21 張領導牌的卡面肖像會在牌桌、手牌中出現時以及右側預覽中播放動畫。滑鼠移過卡牌不應讓循環重新開始。角色以大幅畫面登場的動畫將另行加入。',
'五種安裝包均包含全部 13 種文字語言；EN 是使用英文語音的通用版本。更換語音需要安裝另一種安裝包。DE 和 IT 包中的酒桶巨魔使用俄語。文字語言隨遊戲存檔儲存。新介面由 AI 翻譯，需要母語者校對；ES-MX 和 ZH-TW 介面分別以西班牙文和簡體中文為基礎調整。遊戲原生物品名稱跟隨遊戲語言，部分介面外通知目前仍為 RU/EN。',
'請刪除舊的 [b]modBetaGwentReduxCompat[/b] 資料夾，獨立相容層已不再附帶。與 Redux/Redo Expansion 的相容性尚未單獨確認。其他昆特牌改動模組，以及修改選單、卡牌交易或獎勵的模組可能產生衝突。更改模組組合後，請用 Script Merger 重新合併指令碼。'),
'English': (
'[b]0.6.1 hotfix:[/b] fixed the cause of the crash during leader introductions; the user confirmed the result when retesting the RU package. The card portraits of all 21 leaders are animated on the board, in hand when present there, and in the right preview. Hovering should not restart the loop. Large character entrance animations are planned separately.',
'Each of the five packages includes all 13 text languages; EN is the universal option with English voices. To change voices, install another package. The keg troll speaks Russian in DE and IT. Text language is stored with the game save. The new UI was translated with AI and needs native-speaker proofreading; ES-MX and ZH-TW adapt Spanish and Simplified Chinese UI. Native item names follow the game language; some notifications outside the UI remain RU/EN.',
'Remove the obsolete [b]modBetaGwentReduxCompat[/b] folder; the separate compatibility layer is no longer included. Compatibility with Redux/Redo Expansion has not been separately confirmed. Other Gwent overhauls and mods changing its menus, card trading or rewards may conflict. After changing your mod setup, merge scripts again with Script Merger.'),
}


def validate(text):
    headers = re.findall(r'\[size=3\]\[b\]\[color=#d4af37\](.*?)\[/color\]\[/b\]\[/size\]', text)
    assert headers == list(UPDATES), headers
    stack = []
    for match in re.finditer(r'\[(/?)(b|size|color|center|spoiler|list|url)(?:=[^\]]*)?\]', text):
        closing, name = match.groups()
        if closing:
            assert stack and stack.pop() == name, f'Unbalanced BBCode at {match.start()}'
        else:
            stack.append(name)
    assert not stack, stack
    assert text.count('[spoiler]') == text.count('[/spoiler]') == 12
    assert text.count('Redux/Redo Expansion') == 13
    assert text.count('modBetaGwentReduxCompat') == 13
    assert text.count('AI') + text.count('ИИ') + text.count('IA') + text.count('KI') >= 13
    assert '\ufffd' not in text


def main():
    original = TARGET.read_bytes()
    text = original.decode('utf-8-sig').replace('\r\n', '\n')
    parts = re.split(r'(?=\[size=3\]\[b\]\[color=#d4af37\])', text)
    assert len(parts) == 14
    for index, (language, (fix, details, compatibility)) in enumerate(UPDATES.items(), 1):
        part = parts[index]
        assert part.startswith('[size=3][b][color=#d4af37]' + language + '[/color]')
        lines = part.splitlines()
        intro = next(i for i, line in enumerate(lines) if line.startswith('[b]') and '0.6.1' in line)
        # Idempotent: replace our earlier note if present, retain user-authored paragraphs.
        if fix not in lines:
            lines[intro+1:intro+1] = [fix]
        voice = next(i for i, line in enumerate(lines) if line.startswith('[b]') and all(code in line for code in ('EN', 'RU', 'DE', 'IT', 'PT-BR')))
        if details not in lines:
            lines[voice+1:voice+1] = [details]
        compat = next(i for i, line in enumerate(lines) if 'Redux/Redo Expansion' in line)
        lines[compat] = compatibility
        parts[index] = '\n'.join(lines).rstrip() + '\n'
    updated = '\n'.join(part.rstrip() for part in parts) + '\n'
    validate(updated)
    backup = ROOT/'BetaGwent/build/nexus137/description-before-update.txt'
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_bytes(original)
    TARGET.write_bytes(updated.replace('\n', '\r\n').encode('utf8'))
    report = {'languages': list(UPDATES), 'languageCount': 13, 'spoilers': 12,
              'bbcodeBalanced': True, 'nexusPreviewPerformed': False,
              'nativeSpeakerProofread': False,
              'sha256': hashlib.sha256(TARGET.read_bytes()).hexdigest()}
    (ROOT/'docs/evidence/nexus137.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', 'utf8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
