"""Compact EN/RU Nexus post; the5000 limit includes markup and CRLF."""
from pathlib import Path
import hashlib,re

EN=r'''[size=4][b]English[/b][/size]

[b]Classic1.32 / Next-Gen5.0+ / Steam Deck[/b]
One archive per game version;13 text languages and5 voice languages (EN/RU/DE/IT/PT-BR). Text and voices are selected separately in the mod menu.

[b]New since0.9.1[/b]
30 original beta decks added:76 ordinary lineups,33 thematic NPC presets,92 unique compositions. Classic is a fourth difficulty using the beta AI and sees your hand/deck; Hard keeps its information limits. Choose difficulty beside the language buttons before a match.
Improved AI follow-ups, passing, reveal and target choices, including Cyclops/Lugos against regenerating Greatswords. Fixed locked Yarpen carrying over, card-choice windows, gamepad White Frost focus, empty-hand auto-pass, voices and stray hand-targeting arrows. Reworked Classic RNG and recovery of damaged custom-deck slots from validated backups. Recovery depends on surviving data.

[b]Install / update[/b]
Back up saves and close the game. Move only the old Beta Gwent folder outside Mods; do not mix versions. Next-Gen: Mods/modBetaGwent0924. Classic: copy BOTH Mods and DLC (dlcBetaGwentClassic132Assets and dlcBetaGwentClassic132Items). Update affected Script Merger merges. Optional-CopyButton/bin enables clipboard Import/Export; modBetaGwentMenuMusic adds beta menu music. After-Uninstall is not for normal updates.

[b]After Redux[/b]
Legacy item definitions are retained; already lost inventory cannot be restored. Remove obsolete modBetaGwentReduxCompat.

[b]Uninstall[/b]
Back up, finish Gwent, leave combat and close menus. Run [font=Courier New]bg_clean_confirm('DELETE_BETA_GWENT')[/font], save to a NEW slot, exit and remove Beta Gwent folders. Then use After-Uninstall as described in BetaGwentDocs/CLEANUP_EN.md.

[b]Report a bug[/b]
Post here: exact mod/game versions, difficulty, text/voice languages, other mods, cards and steps. Attach a screenshot or pre-bug save if possible. Add -debugscripts to launch options, reproduce and close the game. Copy the log BEFORE restarting: the next launch overwrites it.
Log: %USERPROFILE%\Documents\The Witcher3\scriptslog.txt
After a crash: latest relevant.dmp from %LOCALAPPDATA%\CrashDumps.
'''

RU=r'''[size=4][b]Русский[/b][/size]

[b]Classic1.32 / Next-Gen5.0+ / Steam Deck[/b]
Отдельный архив для каждой версии игры;13 языков текста и5 озвучек (EN/RU/DE/IT/PT-BR). Текст и голоса выбираются независимо в меню мода.

[b]Новое после0.9.1[/b]
Добавлены30 подлинных колод беты:76 обычных составов,33 тематических варианта NPC,92 уникальных состава. «Классическая» — четвёртая сложность с ИИ беты, видящим руку/колоду; сложный ИИ сохраняет ограничения информации. Выбор сложности — рядом с языками перед боем.
Улучшены продолжения, пас, вскрытие и цели ИИ, включая Циклопа/Лугоса против восстанавливающихся мечников. Исправлены перенос заблокированного Ярпена, окна выбора карт, фокус Белого Хлада с геймпада, автопас пустой руки, озвучка и лишние стрелки к руке. Переработаны RNG Classic и восстановление пользовательских колод из проверенных резервов. Восстановление зависит от уцелевших данных.

[b]Установка / обновление[/b]
Сделайте копию сейвов и закройте игру. Вынесите только прежнюю папку Beta Gwent за пределы Mods; версии не смешивайте. Next-Gen: Mods/modBetaGwent0924. Classic: скопируйте ОБЕ папки — Mods и DLC (dlcBetaGwentClassic132Assets и dlcBetaGwentClassic132Items). Обновите затронутые слияния Script Merger. Optional-CopyButton/bin включает импорт/экспорт через буфер; modBetaGwentMenuMusic добавляет музыку беты. After-Uninstall не нужна при обновлении.

[b]После Redux[/b]
Определения старых предметов сохранены; потерянный инвентарь не восстанавливается. Удалите устаревшую modBetaGwentReduxCompat.

[b]Удаление[/b]
Сделайте копию сейва, завершите гвинт, выйдите из боя и закройте меню. Выполните [font=Courier New]bg_clean_confirm('DELETE_BETA_GWENT')[/font], сохранитесь в НОВЫЙ слот, выйдите и удалите папки Beta Gwent. Затем используйте After-Uninstall по BetaGwentDocs/CLEANUP_RU.md.

[b]Сообщить о баге[/b]
Пишите сюда: точные версии мода/игры, сложность, языки текста/голоса, другие моды, карты и шаги. По возможности приложите скриншот или сейв до ошибки. Добавьте -debugscripts в запуск, повторите ошибку и закройте игру. Скопируйте лог ДО перезапуска: следующий запуск его перезапишет.
Лог: %USERPROFILE%\Documents\The Witcher3\scriptslog.txt
После вылета: свежий связанный.dmp из %LOCALAPPDATA%\CrashDumps.
'''

def prepare_post(out:Path):
    from notes093_public import spaced
    from prepare_full_nexus093 import show
    text='[size=5][color=#e0b354][b]Gwent Beta Classic0.9.3[/b][/color][/size]\n\n'+EN.strip()+'\n\n'+RU.strip()+'\n'
    text=spaced(text).replace('relevant.dmp','relevant .dmp').replace('связанный.dmp','связанный .dmp')
    show.validate_bbcode(text)
    file=out/'NEXUS_POST_0.9.3_EN_RU.bbcode.txt';file.write_text(text,'utf8')
    raw=file.read_bytes().decode('utf-8');utf16=len(raw.encode('utf-16-le'))//2
    assert len(raw)<=5000 and utf16<=5000,('Combined post exceeds5000',len(raw),utf16)
    for token in ['English','Русский','-debugscripts','scriptslog.txt','CrashDumps','BEFORE','ДО перезапуска','CLEANUP_EN.md','CLEANUP_RU.md']:assert token in raw,token
    md=re.sub(r'\[size=\d+\](.*?)\[/size\]',r'## \1',text)
    md=re.sub(r'\[color=[^\]]+\](.*?)\[/color\]',r'\1',md)
    md=md.replace('[b]','**').replace('[/b]','**')
    md=re.sub(r'\[font=[^\]]+\](.*?)\[/font\]',r'`\1`',md)
    (out/'POST_0.9.3_EN_RU.md').write_text(md,'utf8')
    return dict(languages=['en','ru'],maximumCharacters=5000,charactersIncludingMarkupAndCrLf=len(raw),utf16Units=utf16,bbcodeBalanced=True,bugReportsInBothLanguages=True,sha256=hashlib.sha256(file.read_bytes()).hexdigest())

if __name__=='__main__':
    import sys,json
    print(json.dumps(prepare_post(Path(sys.argv[1]))))
