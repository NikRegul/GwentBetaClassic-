# -*- coding: utf-8 -*-
T = {
'en': ("Decks, kegs and scraps now stay after loading", [
"Fixed the main problem of recent versions: on Next-Gen, decks, kegs and scraps could disappear after loading a save, and other script mods made it even more likely. The game keeps only a limited number of mod values per save, and that limit is shared by all mods; Beta Gwent used more than that. The whole Beta Gwent profile now fits into four values, and the backup copy was rebuilt so it can actually restore your data.",
"Your saves are converted automatically the first time you load them with 0.9.4 — nothing to do. Damaged data and broken decks are now set aside instead of being overwritten, so they can still be recovered. Data that is in neither the save nor the backup cannot be brought back.",
"AI: fixed a poor decision with spies in a short round.",
"[b]Back up your saves before updating.[/b] After saving with 0.9.4, do not go back to 0.9.3. If something is still missing after loading, please send your save and scriptslog.txt (see Bug reports)."]),
'ru': ("колоды, бочки и осколки больше не пропадают", [
"Исправлена главная проблема последних версий: на Next-Gen после загрузки сохранения могли пропадать колоды, бочки и осколки, а другие скриптовые моды делали это ещё вероятнее. Игра хранит в сохранении ограниченное число значений от модов, и этот лимит общий для всех модов, а Beta Gwent занимал больше. Теперь весь профиль Beta Gwent умещается в четыре значения, а резервная копия переделана так, чтобы действительно восстанавливать данные.",
"Сохранения переводятся на новый формат автоматически при первой загрузке в 0.9.4, делать ничего не нужно. Повреждённые данные и сломанные колоды теперь откладываются в сторону, а не перезаписываются, поэтому их ещё можно восстановить. Данные, которых нет ни в сохранении, ни в резервной копии, вернуть нельзя.",
"ИИ: исправлено неудачное решение со шпионами в коротком раунде.",
"[b]Перед обновлением сделайте резервную копию сохранений.[/b] После сохранения в 0.9.4 не возвращайтесь на 0.9.3. Если после загрузки что-то всё равно пропало, пришлите сохранение и scriptslog.txt (см. «Сообщения об ошибках»)."]),
'de': ("Decks, Fässer und Fetzen bleiben nach dem Laden erhalten", [
"Das größte Problem der letzten Versionen ist behoben: Auf Next-Gen konnten Decks, Fässer und Fetzen nach dem Laden eines Spielstands verschwinden, und andere Skript-Mods machten das noch wahrscheinlicher. Das Spiel speichert pro Spielstand nur eine begrenzte Zahl von Mod-Werten, und dieses Limit teilen sich alle Mods – Beta Gwent brauchte mehr. Jetzt passt das ganze Beta-Gwent-Profil in vier Werte, und die Sicherungskopie wurde so umgebaut, dass sie deine Daten tatsächlich wiederherstellen kann.",
"Spielstände werden beim ersten Laden mit 0.9.4 automatisch umgestellt – du musst nichts tun. Beschädigte Daten und defekte Decks werden jetzt beiseitegelegt statt überschrieben, damit sie sich noch wiederherstellen lassen. Daten, die weder im Spielstand noch in der Sicherung vorhanden sind, können nicht zurückgeholt werden.",
"KI: Eine schwache Entscheidung mit Spionen in einer kurzen Runde wurde korrigiert.",
"[b]Sichere vor dem Update deine Spielstände.[/b] Kehre nach dem Speichern mit 0.9.4 nicht zu 0.9.3 zurück. Fehlt nach dem Laden trotzdem etwas, schick bitte den Spielstand und scriptslog.txt (siehe „Fehlermeldungen“)."]),
'fr': ("Les decks, tonneaux et fragments restent après le chargement", [
"Le principal problème des dernières versions est corrigé : sur Next-Gen, les decks, tonneaux et fragments pouvaient disparaître après le chargement d’une sauvegarde, et d’autres mods de scripts rendaient cela encore plus probable. Le jeu ne conserve qu’un nombre limité de valeurs de mods par sauvegarde, et cette limite est partagée par tous les mods ; Beta Gwent en utilisait davantage. Tout le profil Beta Gwent tient désormais dans quatre valeurs, et la copie de secours a été refaite pour pouvoir réellement restaurer vos données.",
"Vos sauvegardes sont converties automatiquement au premier chargement avec la 0.9.4 : rien à faire. Les données endommagées et les decks cassés sont désormais mis de côté au lieu d’être écrasés, afin de pouvoir encore être récupérés. Les données absentes à la fois de la sauvegarde et de la copie de secours ne peuvent pas être restaurées.",
"IA : correction d’une mauvaise décision avec des espions lors d’une manche courte.",
"[b]Faites une copie de vos sauvegardes avant la mise à jour.[/b] Après avoir sauvegardé avec la 0.9.4, ne revenez pas à la 0.9.3. Si quelque chose manque encore après le chargement, envoyez votre sauvegarde et scriptslog.txt (voir « Signaler un bug »)."]),
'it': ("Mazzi, barili e frammenti restano dopo il caricamento", [
"Risolto il problema principale delle ultime versioni: su Next-Gen mazzi, barili e frammenti potevano sparire dopo il caricamento di un salvataggio, e altre mod di script lo rendevano ancora più probabile. Il gioco conserva solo un numero limitato di valori delle mod per salvataggio, e questo limite è condiviso da tutte le mod; Beta Gwent ne usava di più. Ora l’intero profilo di Beta Gwent sta in quattro valori e la copia di backup è stata rifatta per poter davvero ripristinare i tuoi dati.",
"I salvataggi vengono convertiti automaticamente al primo caricamento con la 0.9.4: non devi fare nulla. I dati danneggiati e i mazzi rovinati ora vengono messi da parte invece di essere sovrascritti, così si possono ancora recuperare. I dati assenti sia dal salvataggio sia dal backup non possono essere ripristinati.",
"IA: corretta una decisione sbagliata con le spie in un round breve.",
"[b]Prima di aggiornare, fai un backup dei salvataggi.[/b] Dopo aver salvato con la 0.9.4, non tornare alla 0.9.3. Se dopo il caricamento manca ancora qualcosa, invia il salvataggio e scriptslog.txt (vedi «Segnalazione bug»)."]),
'pl': ("Talie, beczki i skrawki nie znikają po wczytaniu", [
"Naprawiono główny problem ostatnich wersji: na Next-Gen talie, beczki i skrawki mogły znikać po wczytaniu zapisu, a inne mody skryptowe jeszcze to ułatwiały. Gra przechowuje w zapisie tylko ograniczoną liczbę wartości z modów, a ten limit jest wspólny dla wszystkich modów — Beta Gwent używał więcej. Teraz cały profil Beta Gwent mieści się w czterech wartościach, a kopię zapasową przebudowano tak, by naprawdę mogła przywrócić dane.",
"Zapisy są konwertowane automatycznie przy pierwszym wczytaniu w 0.9.4 — nic nie trzeba robić. Uszkodzone dane i zepsute talie są teraz odkładane na bok zamiast nadpisywane, więc nadal można je odzyskać. Danych, których nie ma ani w zapisie, ani w kopii zapasowej, nie da się przywrócić.",
"SI: poprawiono złą decyzję ze szpiegami w krótkiej rundzie.",
"[b]Przed aktualizacją zrób kopię zapasową zapisów.[/b] Po zapisaniu gry w 0.9.4 nie wracaj do 0.9.3. Jeśli po wczytaniu nadal czegoś brakuje, wyślij zapis i scriptslog.txt (zob. „Zgłaszanie błędów”)."]),
'es': ("Los mazos, barriles y fragmentos ya no desaparecen al cargar", [
"Se corrige el problema principal de las últimas versiones: en Next-Gen, los mazos, barriles y fragmentos podían desaparecer al cargar una partida guardada, y otros mods de scripts lo hacían aún más probable. El juego guarda solo un número limitado de valores de mods por partida, y ese límite lo comparten todos los mods; Beta Gwent usaba más. Ahora todo el perfil de Beta Gwent cabe en cuatro valores, y la copia de seguridad se ha rehecho para que realmente pueda restaurar tus datos.",
"Tus partidas se convierten automáticamente la primera vez que las cargas con la 0.9.4: no tienes que hacer nada. Los datos dañados y los mazos rotos ahora se apartan en lugar de sobrescribirse, para que aún puedan recuperarse. Los datos que no estén ni en la partida ni en la copia de seguridad no se pueden restaurar.",
"IA: corregida una mala decisión con espías en una ronda corta.",
"[b]Antes de actualizar, haz una copia de seguridad de tus partidas.[/b] Después de guardar con la 0.9.4, no vuelvas a la 0.9.3. Si tras cargar sigue faltando algo, envía la partida y scriptslog.txt (consulta «Informar de errores»)."]),
'es-mx': ("Los mazos, barriles y fragmentos ya no desaparecen al cargar", [
"Se corrigió el problema principal de las últimas versiones: en Next-Gen, los mazos, barriles y fragmentos podían desaparecer al cargar una partida guardada, y otros mods de scripts lo hacían aún más probable. El juego guarda solo una cantidad limitada de valores de mods por partida, y ese límite lo comparten todos los mods; Beta Gwent usaba más. Ahora todo el perfil de Beta Gwent cabe en cuatro valores, y la copia de seguridad se rehízo para que realmente pueda restaurar tus datos.",
"Tus partidas se convierten automáticamente la primera vez que las cargas con la 0.9.4: no tienes que hacer nada. Los datos dañados y los mazos rotos ahora se apartan en lugar de sobrescribirse, para que todavía puedan recuperarse. Los datos que no estén ni en la partida ni en la copia de seguridad no se pueden restaurar.",
"IA: se corrigió una mala decisión con espías en una ronda corta.",
"[b]Antes de actualizar, haz una copia de seguridad de tus partidas.[/b] Después de guardar con la 0.9.4, no regreses a la 0.9.3. Si después de cargar sigue faltando algo, envía la partida y scriptslog.txt (consulta «Reportar errores»)."]),
'pt-br': ("Baralhos, barris e fragmentos não somem mais ao carregar", [
"Corrigido o principal problema das últimas versões: no Next-Gen, baralhos, barris e fragmentos podiam sumir depois de carregar um save, e outros mods de script deixavam isso ainda mais provável. O jogo guarda só um número limitado de valores de mods por save, e esse limite é compartilhado por todos os mods; o Beta Gwent usava mais. Agora todo o perfil do Beta Gwent cabe em quatro valores, e a cópia de segurança foi refeita para realmente conseguir restaurar seus dados.",
"Seus saves são convertidos automaticamente no primeiro carregamento com a 0.9.4 — não é preciso fazer nada. Dados danificados e baralhos quebrados agora são guardados à parte em vez de sobrescritos, para que ainda possam ser recuperados. Dados que não estão nem no save nem na cópia de segurança não podem ser restaurados.",
"IA: corrigida uma decisão ruim com espiões em uma rodada curta.",
"[b]Antes de atualizar, faça backup dos seus saves.[/b] Depois de salvar com a 0.9.4, não volte para a 0.9.3. Se algo ainda faltar após carregar, envie o save e o scriptslog.txt (veja “Relatar bugs”)."]),
'ja': ("ロード後もデッキ・樽・スクラップが消えなくなりました", [
"最近のバージョンの最大の問題を修正しました。Next-Genではセーブデータをロードするとデッキ、樽、スクラップが消えることがあり、他のスクリプトModを導入しているとさらに起こりやすくなっていました。ゲームがセーブごとに保存できるModの値の数には上限があり、その上限はすべてのModで共有されますが、Beta Gwentはそれ以上を使っていました。現在はBeta Gwentのプロフィール全体が4つの値に収まり、バックアップも実際にデータを復元できるよう作り直しました。",
"セーブデータは0.9.4で初めてロードしたときに自動で変換されます。操作は不要です。破損したデータや壊れたデッキは上書きされずに別に保管されるため、後から復元できます。セーブにもバックアップにも残っていないデータは復元できません。",
"AI：短いラウンドでの密偵に関する判断ミスを修正しました。",
"[b]更新前にセーブデータをバックアップしてください。[/b]0.9.4で保存した後は0.9.3に戻さないでください。ロード後もまだ何か足りない場合は、セーブデータとscriptslog.txtを送ってください（「バグ報告」を参照）。"]),
'ko': ("불러온 뒤에도 덱, 통, 조각이 사라지지 않습니다", [
"최근 버전의 가장 큰 문제를 수정했습니다. Next-Gen에서 세이브를 불러오면 덱, 통, 조각이 사라질 수 있었고, 다른 스크립트 모드를 함께 쓰면 더 자주 발생했습니다. 게임은 세이브마다 모드 값을 제한된 개수만 저장하며 이 한도는 모든 모드가 공유하는데, Beta Gwent는 그보다 많이 사용했습니다. 이제 Beta Gwent 프로필 전체가 값 4개에 들어가며, 백업도 실제로 데이터를 복원할 수 있도록 새로 만들었습니다.",
"세이브는 0.9.4에서 처음 불러올 때 자동으로 변환되므로 따로 할 일은 없습니다. 손상된 데이터와 망가진 덱은 덮어쓰지 않고 따로 보관하므로 나중에도 복구할 수 있습니다. 세이브와 백업 어디에도 없는 데이터는 복구할 수 없습니다.",
"AI: 짧은 라운드에서 첩자와 관련된 잘못된 판단을 수정했습니다.",
"[b]업데이트 전에 세이브를 백업하세요.[/b] 0.9.4로 저장한 뒤에는 0.9.3으로 되돌리지 마세요. 불러온 뒤에도 무언가 빠져 있다면 세이브와 scriptslog.txt를 보내 주세요(‘버그 제보’ 참고)."]),
'zh-cn': ("读档后牌组、桶和碎片不再丢失", [
"修复了近期版本最主要的问题：在 Next-Gen 上读取存档后，牌组、桶和碎片可能会丢失，同时安装其他脚本模组时更容易发生。游戏每个存档只能保存有限数量的模组数值，而且这个上限由所有模组共享，Beta Gwent 占用的数量超出了上限。现在整个 Beta Gwent 档案只需 4 个数值，备份也已重做，能够真正恢复你的数据。",
"存档会在首次用 0.9.4 读取时自动转换，无需任何操作。损坏的数据和出错的牌组现在会另行保留而不会被覆盖，因此仍可恢复。存档和备份中都没有的数据无法恢复。",
"AI：修正了短小局中与间谍相关的错误决策。",
"[b]更新前请备份存档。[/b]使用 0.9.4 保存后，请勿退回 0.9.3。如果读档后仍有内容缺失，请发送存档和 scriptslog.txt（见“反馈问题”）。"]),
'zh-tw': ("讀檔後牌組、桶與碎片不再遺失", [
"修正了近期版本最主要的問題：在 Next-Gen 上讀取存檔後，牌組、桶與碎片可能會遺失，同時安裝其他腳本模組時更容易發生。遊戲每個存檔只能儲存有限數量的模組數值，而且這個上限由所有模組共用，Beta Gwent 使用的數量超過了上限。現在整個 Beta Gwent 檔案只需 4 個數值，備份也已重做，能夠真正還原你的資料。",
"存檔會在首次以 0.9.4 讀取時自動轉換，不需任何操作。損壞的資料與出錯的牌組現在會另外保留而不會被覆寫，因此仍可還原。存檔與備份中都沒有的資料無法還原。",
"AI：修正了短小局中與間諜相關的錯誤判斷。",
"[b]更新前請備份存檔。[/b]以 0.9.4 儲存後，請勿退回 0.9.3。如果讀檔後仍有內容缺失，請傳送存檔與 scriptslog.txt（見「回報問題」）。"]),
}
from p4_094 import P4
for _l in T: T[_l][1][3] = P4[_l]
NAMES = {'en':'English','ru':'Русский','de':'Deutsch','fr':'Français','it':'Italiano','pl':'Polski','es':'Español (España)','es-mx':'Español (Latinoamérica)','pt-br':'Português (Brasil)','ja':'日本語','ko':'한국어','zh-cn':'简体中文','zh-tw':'繁體中文'}
