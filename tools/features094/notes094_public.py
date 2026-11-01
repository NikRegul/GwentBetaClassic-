"""Public 0.9.4 copy in all thirteen mod languages (save safety and post-tournament AI).

The 0.9.3 description stays the base text; only the title and a 0.9.4 section change.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/releases/0.9.3-public-20261025'
OUT=ROOT/'docs/releases/0.9.4-public-20261026'
# heading, tagline, cause+fix, migration, compatibility
COPY={
'RU':['Изменения в 0.9.4','Исправлено сохранение колод, бочек и осколков.',
 'Next-Gen 5.x сохраняет у Геральта только первые 45 полей, добавленных модами, и этот лимит общий для всех установленных модов. Факты игры хранят лишь 16-битные числа. Beta Gwent занимал больше полей, поэтому вместе с другими модами колоды, бочки и осколки могли пропадать после загрузки. Теперь весь профиль хранится в одном хранилище из четырёх полей, а резервная копия в фактах записывается частями, которые помещаются в 16 бит.',
 'Старые сохранения переносятся автоматически при первой загрузке.',
 'Для Next-Gen 5.0+ и Classic 1.32. На 1.32 старые поля сохраняются как раньше, рядом с новым хранилищем. После сохранения в 0.9.4 откат на 0.9.3 не поддерживается. Автоматические проверки и нативная компиляция не заменяют проверку цикла «сохранить — выйти — загрузить» в игре.'],
'EN':['Changes in 0.9.4','Decks, kegs and scraps now persist.',
 'Next-Gen 5.x saves only the first 45 mod-added fields of Geralt, and that limit is shared by every installed mod. Game facts keep only 16-bit numbers. Beta Gwent used more fields, so with other mods installed, decks, kegs and scraps could vanish after loading. The whole profile now lives in a single four-field store, and the facts backup is written in parts that fit 16 bits.',
 'Existing saves are migrated automatically on first load.',
 'For Next-Gen 5.0+ and Classic 1.32. On 1.32 the old fields are still saved next to the new store. Going back to 0.9.3 after saving with 0.9.4 is not supported. Automated checks and native compilation do not replace an in-game save, quit and load test.'],
'DE':['Änderungen in 0.9.4','Decks, Fässer und Splitter bleiben jetzt erhalten.',
 'Next-Gen 5.x speichert bei Geralt nur die ersten 45 von Mods hinzugefügten Felder, und diese Grenze teilen sich alle installierten Mods. Spielfakten speichern nur 16-Bit-Zahlen. Beta Gwent nutzte mehr Felder, daher konnten mit anderen Mods Decks, Fässer und Splitter nach dem Laden verschwinden. Das gesamte Profil liegt jetzt in einem einzigen Speicher aus vier Feldern, und die Sicherung in den Fakten wird in 16-Bit-taugliche Teile aufgeteilt.',
 'Bestehende Spielstände werden beim ersten Laden automatisch übernommen.',
 'Für Next-Gen 5.0+ und Classic 1.32. Unter 1.32 werden die alten Felder weiterhin neben dem neuen Speicher gesichert. Nach dem Speichern mit 0.9.4 wird ein Wechsel zurück auf 0.9.3 nicht unterstützt. Automatische Tests und native Kompilierung ersetzen keinen Test aus Speichern, Beenden und Laden im Spiel.'],
'FR':['Nouveautés de la 0.9.4','Les decks, tonneaux et fragments sont désormais conservés.',
 'Next-Gen 5.x n’enregistre que les 45 premiers champs ajoutés par des mods à Geralt, et cette limite est partagée par tous les mods installés. Les faits du jeu ne conservent que des nombres sur 16 bits. Beta Gwent utilisait davantage de champs : avec d’autres mods, decks, tonneaux et fragments pouvaient disparaître après un chargement. Tout le profil tient désormais dans un stockage unique de quatre champs, et la sauvegarde dans les faits est écrite en parties compatibles 16 bits.',
 'Les sauvegardes existantes sont migrées automatiquement au premier chargement.',
 'Pour Next-Gen 5.0+ et Classic 1.32. Sur 1.32, les anciens champs restent enregistrés à côté du nouveau stockage. Revenir à la 0.9.3 après avoir sauvegardé en 0.9.4 n’est pas pris en charge. Les tests automatiques et la compilation native ne remplacent pas un essai en jeu : sauvegarder, quitter, recharger.'],
'IT':['Novità della 0.9.4','Mazzi, barili e frammenti ora vengono conservati.',
 'Next-Gen 5.x salva solo i primi 45 campi aggiunti dalle mod a Geralt, e questo limite è condiviso da tutte le mod installate. I fatti del gioco conservano solo numeri a 16 bit. Beta Gwent usava più campi, quindi con altre mod mazzi, barili e frammenti potevano sparire dopo il caricamento. Ora l’intero profilo è in un unico archivio di quattro campi e il backup nei fatti è scritto in parti che stanno in 16 bit.',
 'I salvataggi esistenti vengono convertiti automaticamente al primo caricamento.',
 'Per Next-Gen 5.0+ e Classic 1.32. Su 1.32 i vecchi campi restano salvati accanto al nuovo archivio. Tornare alla 0.9.3 dopo aver salvato con la 0.9.4 non è supportato. I test automatici e la compilazione nativa non sostituiscono una prova in gioco: salvare, uscire, ricaricare.'],
'PL':['Zmiany w 0.9.4','Talie, beczki i okruchy są teraz zapisywane.',
 'Next-Gen 5.x zapisuje u Geralta tylko pierwsze 45 pól dodanych przez mody, a ten limit jest wspólny dla wszystkich zainstalowanych modów. Fakty gry przechowują tylko liczby 16-bitowe. Beta Gwent używał więcej pól, więc przy innych modach talie, beczki i okruchy mogły znikać po wczytaniu. Cały profil jest teraz w jednym magazynie z czterech pól, a kopia zapasowa w faktach jest zapisywana w częściach mieszczących się w 16 bitach.',
 'Istniejące zapisy są przenoszone automatycznie przy pierwszym wczytaniu.',
 'Dla Next-Gen 5.0+ i Classic 1.32. Na 1.32 stare pola nadal są zapisywane obok nowego magazynu. Powrót do 0.9.3 po zapisie w 0.9.4 nie jest obsługiwany. Testy automatyczne i natywna kompilacja nie zastępują próby w grze: zapis, wyjście, wczytanie.'],
'ES':['Cambios en la 0.9.4','Los mazos, barriles y fragmentos ya se conservan.',
 'Next-Gen 5.x solo guarda los primeros 45 campos que los mods añaden a Geralt, y ese límite lo comparten todos los mods instalados. Los hechos del juego solo guardan números de 16 bits. Beta Gwent usaba más campos, así que con otros mods los mazos, barriles y fragmentos podían desaparecer al cargar. Ahora todo el perfil está en un único almacén de cuatro campos, y la copia de seguridad en los hechos se escribe en partes que caben en 16 bits.',
 'Las partidas existentes se migran automáticamente en la primera carga.',
 'Para Next-Gen 5.0+ y Classic 1.32. En 1.32 los campos antiguos siguen guardándose junto al nuevo almacén. No se admite volver a la 0.9.3 tras guardar con la 0.9.4. Las pruebas automáticas y la compilación nativa no sustituyen una prueba en el juego: guardar, salir y cargar.'],
'PT_BR':['Mudanças na 0.9.4','Baralhos, barris e fragmentos agora são mantidos.',
 'O Next-Gen 5.x salva apenas os primeiros 45 campos que os mods adicionam ao Geralt, e esse limite é compartilhado por todos os mods instalados. Os fatos do jogo guardam só números de 16 bits. O Beta Gwent usava mais campos, então com outros mods baralhos, barris e fragmentos podiam sumir ao carregar. Agora todo o perfil fica em um único armazenamento de quatro campos, e o backup nos fatos é gravado em partes que cabem em 16 bits.',
 'Saves existentes são migrados automaticamente no primeiro carregamento.',
 'Para Next-Gen 5.0+ e Classic 1.32. No 1.32 os campos antigos continuam salvos ao lado do novo armazenamento. Voltar para a 0.9.3 depois de salvar com a 0.9.4 não é suportado. Testes automáticos e compilação nativa não substituem um teste no jogo: salvar, sair e carregar.'],
'JA':['0.9.4の変更点','デッキ、樽、スクラップが正しく保存されるようになりました。',
 'Next-Gen 5.xは、MODがゲラルトに追加したフィールドのうち最初の45個しか保存せず、この上限はインストールされた全MODで共有されます。また、ゲームのファクトは16ビットの数値しか保持しません。Beta Gwentはより多くのフィールドを使っていたため、他のMODと併用するとロード後にデッキ、樽、スクラップが消えることがありました。現在はプロフィール全体を4つのフィールドからなる単一の保存領域に格納し、ファクトのバックアップも16ビットに収まる部分に分けて書き込みます。',
 '既存のセーブは初回ロード時に自動で移行されます。',
 'Next-Gen 5.0+とClassic 1.32に対応。1.32では従来のフィールドも新しい保存領域と並んで保存されます。0.9.4で保存した後に0.9.3へ戻すことはサポートされません。自動テストとネイティブコンパイルは、ゲーム内での「保存・終了・ロード」の確認の代わりにはなりません。'],
'KO':['0.9.4 변경 사항','덱, 통, 조각이 이제 제대로 저장됩니다.',
 'Next-Gen 5.x는 모드가 게롤트에 추가한 필드 중 처음 45개만 저장하며, 이 한도는 설치된 모든 모드가 함께 씁니다. 게임 팩트는 16비트 숫자만 보관합니다. Beta Gwent는 더 많은 필드를 사용했기 때문에 다른 모드와 함께 쓰면 불러온 뒤 덱, 통, 조각이 사라질 수 있었습니다. 이제 전체 프로필은 네 개의 필드로 된 단일 저장소에 보관되며, 팩트 백업은 16비트에 맞는 조각으로 나뉘어 기록됩니다.',
 '기존 저장은 처음 불러올 때 자동으로 옮겨집니다.',
 'Next-Gen 5.0+와 Classic 1.32용입니다. 1.32에서는 기존 필드도 새 저장소와 함께 계속 저장됩니다. 0.9.4로 저장한 뒤 0.9.3으로 되돌리는 것은 지원하지 않습니다. 자동 테스트와 네이티브 컴파일은 게임 안에서 저장, 종료, 불러오기를 확인하는 일을 대신하지 않습니다.'],
'ZH_CN':['0.9.4 更新内容','卡组、酒桶和碎片现在可以正常保存。',
 'Next-Gen 5.x 只保存模组为杰洛特添加的前 45 个字段，且该上限由所有已安装的模组共享。游戏事实只保存 16 位数值。Beta Gwent 使用的字段更多，因此与其他模组同时使用时，读档后卡组、酒桶和碎片可能消失。现在整个档案存放在由四个字段组成的单一存储中，事实中的备份也拆分为可容纳于 16 位的部分写入。',
 '现有存档会在首次读取时自动迁移。',
 '适用于 Next-Gen 5.0+ 和 Classic 1.32。在 1.32 上，旧字段仍会与新存储一同保存。使用 0.9.4 保存后，不支持退回 0.9.3。自动测试和原生编译不能代替在游戏中进行“保存、退出、读取”的确认。'],
'ZH_TW':['0.9.4 更新內容','牌組、酒桶和碎片現在可以正常儲存。',
 'Next-Gen 5.x 只會儲存模組為傑洛特新增的前 45 個欄位，且此上限由所有已安裝的模組共用。遊戲事實只保存 16 位元數值。Beta Gwent 使用的欄位較多，因此與其他模組一同使用時，讀檔後牌組、酒桶和碎片可能消失。現在整個檔案存放在由四個欄位組成的單一儲存區，事實中的備份也拆成可放入 16 位元的部分寫入。',
 '既有存檔會在首次讀取時自動移轉。',
 '適用於 Next-Gen 5.0+ 與 Classic 1.32。在 1.32 上，舊欄位仍會與新儲存區一同保存。以 0.9.4 存檔後，不支援退回 0.9.3。自動測試與原生編譯不能取代在遊戲中進行「存檔、退出、讀取」的確認。']}
COPY['ES_MX']=COPY['ES']
ORDER=['RU','EN','DE','FR','IT','PL','ES','ES_MX','PT_BR','JA','KO','ZH_CN','ZH_TW']
DETAILS={
'RU':[
 'Дополнительно защищено восстановление: профиль загружается до первого изменения; повреждённый исходник и карантин колод сохраняются для восстановления, а неизвестный будущий формат доступен только для чтения. Формат 2 читает формат 1 и проверяет длину и целостность текста вместе с числовой частью, прежде чем принять запись. Данные, которых нет ни в сохранении, ни в доступных резервных копиях, восстановить невозможно.',
 'После турнира исправлено решение ИИ при коротком раунде со шпионом. Разработческая выборка: 368 партий, 50%, ошибок нет. Отложенная выборка не запускалась; общий прирост силы не установлен. Hard по-прежнему ограничен доступной игроку информацией, у «Классической» доступ к скрытой информации шире.'],
'EN':[
 'Recovery is also hardened: the profile loads before its first change; the damaged original and quarantined decks are preserved for recovery, and an unknown future format is read-only. Format 2 reads format 1 and validates text length and integrity together with the numeric data before accepting a record. Data absent from both the save and available backups cannot be restored.',
 'After the tournament, an AI decision involving a spy in a short round was corrected. Development sample: 368 games, 50%, zero errors. The holdout was not run; an overall strength gain has not been established. Hard still observes player-visible information limits; Classic has broader access to hidden information.'],
'DE':[
 'Die Wiederherstellung ist zusätzlich abgesichert: Das Profil wird vor der ersten Änderung geladen; beschädigte Originaldaten und ausgesonderte Decks bleiben zur Wiederherstellung erhalten, und ein unbekanntes künftiges Format ist schreibgeschützt. Format 2 liest Format 1 und prüft Textlänge und Integrität zusammen mit den Zahlen, bevor ein Datensatz übernommen wird. Daten, die weder im Spielstand noch in verfügbaren Sicherungen vorhanden sind, können nicht wiederhergestellt werden.',
 'Nach dem Turnier wurde eine KI-Entscheidung mit einem Spion in einer kurzen Runde korrigiert. Entwicklungsstichprobe: 368 Partien, 50 %, keine Fehler. Die zurückgehaltene Teststichprobe wurde nicht ausgeführt; ein allgemeiner Stärkegewinn ist nicht belegt. Hard bleibt auf spielersichtbare Informationen beschränkt; Klassisch hat umfassenderen Zugriff auf verborgene Informationen.'],
'FR':[
 'La récupération est renforcée : le profil est chargé avant sa première modification ; les données originales endommagées et les decks mis en quarantaine sont conservés, et tout format futur inconnu reste en lecture seule. Le format 2 lit le format 1 et vérifie la longueur et l’intégrité du texte avec les données numériques avant d’accepter un enregistrement. Les données absentes à la fois de la sauvegarde et des copies disponibles ne peuvent pas être restaurées.',
 'Après le tournoi, une décision de l’IA impliquant un espion dans une manche courte a été corrigée. Échantillon de développement : 368 parties, 50 %, aucune erreur. L’échantillon réservé n’a pas été testé ; aucun gain global de force n’est établi. Difficile reste limité aux informations visibles par le joueur ; Classique accède à davantage d’informations cachées.'],
'IT':[
 'Anche il recupero è più robusto: il profilo viene caricato prima della prima modifica; i dati originali danneggiati e i mazzi in quarantena vengono conservati, mentre un formato futuro sconosciuto rimane in sola lettura. Il formato 2 legge il formato 1 e controlla lunghezza e integrità del testo insieme ai dati numerici prima di accettare un record. I dati assenti sia dal salvataggio sia dai backup disponibili non possono essere ripristinati.',
 'Dopo il torneo è stata corretta una decisione dell’IA con una spia in un round breve. Campione di sviluppo: 368 partite, 50%, nessun errore. Il campione riservato non è stato eseguito; non è dimostrato un aumento generale della forza. Difficile mantiene i limiti delle informazioni visibili al giocatore; Classica ha un accesso più ampio alle informazioni nascoste.'],
'PL':[
 'Wzmocniono też odzyskiwanie: profil jest wczytywany przed pierwszą zmianą; uszkodzony oryginał i talie w kwarantannie pozostają dostępne do odzyskania, a nieznany przyszły format jest tylko do odczytu. Format 2 odczytuje format 1 i sprawdza długość oraz integralność tekstu razem z danymi liczbowymi przed przyjęciem wpisu. Danych nieobecnych zarówno w zapisie, jak i dostępnych kopiach nie można przywrócić.',
 'Po turnieju poprawiono decyzję SI ze szpiegiem w krótkiej rundzie. Próba rozwojowa: 368 partii, 50%, brak błędów. Nie przeprowadzono próby na odłożonym zestawie; ogólny wzrost siły nie został wykazany. Trudny nadal korzysta tylko z informacji widocznych dla gracza; Klasyczny ma szerszy dostęp do informacji ukrytych.'],
'ES':[
 'También se refuerza la recuperación: el perfil se carga antes del primer cambio; se conservan el original dañado y los mazos en cuarentena, y un formato futuro desconocido queda en modo de solo lectura. El formato 2 lee el formato 1 y comprueba la longitud e integridad del texto junto con los datos numéricos antes de aceptar un registro. No se pueden restaurar datos ausentes tanto de la partida como de las copias disponibles.',
 'Tras el torneo se corrigió una decisión de la IA con un espía en una ronda corta. Muestra de desarrollo: 368 partidas, 50%, cero errores. No se ejecutó la muestra reservada; no se ha demostrado una mejora general de fuerza. Difícil mantiene los límites de información visible para el jugador; Clásica tiene mayor acceso a la información oculta.'],
'PT_BR':[
 'A recuperação também foi reforçada: o perfil é carregado antes da primeira alteração; o original danificado e os baralhos em quarentena são preservados, e um formato futuro desconhecido fica somente para leitura. O formato 2 lê o formato 1 e verifica comprimento e integridade do texto junto com os dados numéricos antes de aceitar um registro. Dados ausentes tanto do save quanto dos backups disponíveis não podem ser restaurados.',
 'Após o torneio, foi corrigida uma decisão da IA com um espião em uma rodada curta. Amostra de desenvolvimento: 368 partidas, 50%, nenhum erro. A amostra reservada não foi executada; não foi estabelecido um ganho geral de força. Difícil mantém os limites de informação visível ao jogador; Clássica tem acesso mais amplo às informações ocultas.'],
'JA':[
 '復元処理も強化しました。プロフィールは最初の変更前に読み込まれ、破損した元データと隔離されたデッキは復元用に保持されます。未知の将来形式は読み取り専用です。形式2は形式1を読み込み、記録を受け入れる前に数値データとともにテキストの長さと整合性を検証します。セーブにも利用可能なバックアップにも存在しないデータは復元できません。',
 '大会後、短いラウンドでスパイを使う際のAIの判断を修正しました。開発用サンプルは368試合、50%、エラー0件です。保留テスト用サンプルは実行しておらず、総合的な強さの向上は確認されていません。ハードは引き続きプレイヤーに見える情報に制限され、クラシックはより広く隠し情報へアクセスします。'],
'KO':[
 '복구 절차도 강화했습니다. 프로필은 첫 변경 전에 불러오며, 손상된 원본과 격리된 덱을 복구용으로 보존합니다. 알 수 없는 미래 형식은 읽기 전용입니다. 형식 2는 형식 1을 읽고, 기록을 받아들이기 전에 숫자 데이터와 함께 텍스트 길이와 무결성을 검증합니다. 저장과 사용 가능한 백업 모두에 없는 데이터는 복원할 수 없습니다.',
 '토너먼트 이후 짧은 라운드에서 첩자를 다루는 AI 판단을 수정했습니다. 개발 표본은 368경기, 50%, 오류 0건입니다. 별도 보류 표본은 실행하지 않았으며 전반적인 실력 향상은 입증되지 않았습니다. 어려움은 계속 플레이어에게 보이는 정보로 제한되며, 클래식은 숨겨진 정보에 더 넓게 접근합니다.'],
'ZH_CN':[
 '恢复流程也得到加强：首次修改前先读取档案；损坏的原始数据和隔离的卡组会保留用于恢复，未知的未来格式则设为只读。格式 2 可读取格式 1，并在接受记录前同时验证数值数据以及文本的长度和完整性。若数据既不在存档中，也不在可用备份中，则无法恢复。',
 '锦标赛后修正了 AI 在短局中涉及间谍的一项决策。开发样本为 368 场、50%、零错误。尚未运行留出的测试样本，整体实力提升尚未得到证实。困难模式仍受玩家可见信息的限制；经典模式可访问更多隐藏信息。'],
'ZH_TW':[
 '復原流程也已加強：首次修改前先讀取檔案；受損的原始資料和隔離的牌組會保留供復原使用，未知的未來格式則設為唯讀。格式 2 可讀取格式 1，並在接受紀錄前同時驗證數值資料以及文字的長度與完整性。若資料既不在存檔中，也不在可用備份中，便無法復原。',
 '錦標賽後修正了 AI 在短局中涉及間諜的一項決策。開發樣本為 368 場、50%、零錯誤。尚未執行保留的測試樣本，整體實力提升尚未獲得證實。困難模式仍受玩家可見資訊的限制；經典模式可存取更多隱藏資訊。']}
DETAILS['ES_MX']=DETAILS['ES']

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for code in ORDER:
        heading,tag,fix,migration,limit=COPY[code]
        hardening,ai=DETAILS[code]
        base=(BASE/f'0.9.3_DESCRIPTION_{code}.md').read_text('utf8')
        assert base.startswith('# Gwent Beta Classic 0.9.3\n'),code
        body=base.split('\n',1)[1]
        section=f'## {heading}\n\n- {fix}\n\n- {hardening}\n\n- {migration}\n\n- {ai}\n\n{limit}\n\n'
        # Put the 0.9.4 section right after the lead paragraph.
        first=body.index('\n## ')
        description='# Gwent Beta Classic 0.9.4\n'+body[:first].rstrip('\n')+'\n\n'+section+body[first+1:].lstrip('\n')
        changelog=f'# Gwent Beta Classic 0.9.4 — {heading}\n\n- {fix}\n\n- {hardening}\n\n- {migration}\n\n- {ai}\n\n{limit}\n'
        post=f'# Gwent Beta Classic 0.9.4\n\n**{tag}**\n\n{fix}\n\n{hardening}\n\n{migration}\n\n{ai}\n\n{limit}\n'
        for kind,text in [('DESCRIPTION',description),('CHANGELOG',changelog),('POST',post)]:
            (OUT/f'0.9.4_{kind}_{code}.md').write_text(text,'utf8')
    rows=[f'| {c} | [Description](0.9.4_DESCRIPTION_{c}.md) | [Post](0.9.4_POST_{c}.md) | [0.9.3 → 0.9.4](0.9.4_CHANGELOG_{c}.md) |' for c in ORDER]
    (OUT/'README.md').write_text('# Gwent Beta Classic 0.9.4 · publication copy\n\n13 languages. Prepared for review; nothing published.\n\n| Language | Description | Post | Changelog |\n|---|---|---|---|\n'+'\n'.join(rows)+'\n','utf8')
    (OUT/'copy-source.json').write_text(json.dumps({code:COPY[code]+DETAILS[code] for code in ORDER},ensure_ascii=False,indent=2)+'\n','utf8')
    print('Prepared 39 localized 0.9.4 documents:',OUT)

if __name__=='__main__':main()
