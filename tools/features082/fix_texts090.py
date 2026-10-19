"""Replace the 0.9.0 BG1 clipboard paragraph in all Nexus texts with the native-copy text.

Every line that mentions Copy-Deck-Code in a language's own files is that
language's old paragraph; it is replaced in that file and in the combined
EN/RU and all-language files. The changelog bullet promising Ctrl+C/Ctrl+V is
replaced too. Backups go to tmp/backup-texts090 (nothing is deleted).
"""
from pathlib import Path
import re, shutil, json

ROOT = Path(__file__).resolve().parents[2]
NEXUS = ROOT / 'docs/releases/0.9.0/nexus'
BACKUP = ROOT / 'tmp/backup-texts090'
NEW = {
'en': 'Export shows a language-independent BG1 code. Copy puts it straight into the Windows clipboard; paste it anywhere with Ctrl+V. This needs the included bin files: dinput8.dll and plugins/GwentBetaClipboard.asi in the folder of witcher3.exe. If another mod already has its own dinput8.dll, keep it and let that mod\'s ASI loader load GwentBetaClipboard.asi. Without these files Copy says so; as a fallback, start the game with -debugscripts, export again and run Copy-Deck-Code.cmd. Import accepts the complete BG1 code in its text field.',
'ru': 'Экспорт показывает код колоды BG1, не зависящий от языка. «Копировать» сразу помещает его в буфер Windows — вставляйте куда угодно через Ctrl+V. Для этого нужны файлы bin из архива: dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe. Если у другого мода уже есть свой dinput8.dll, оставьте его и загрузите GwentBetaClipboard.asi через его ASI-загрузчик. Без этих файлов кнопка сообщит об этом; запасной путь — запустить игру с -debugscripts, повторить экспорт и запустить Copy-Deck-Code.cmd. Импорт принимает полный код BG1 в текстовом поле.',
'de': 'Export zeigt einen sprachunabhängigen BG1-Code. Kopieren legt ihn direkt in die Windows-Zwischenablage; mit Strg+V überall einfügen. Dafür werden die mitgelieferten bin-Dateien benötigt: dinput8.dll und plugins/GwentBetaClipboard.asi im Ordner von witcher3.exe. Hat ein anderer Mod bereits eine eigene dinput8.dll, diese behalten und GwentBetaClipboard.asi über dessen ASI-Loader laden. Fehlen die Dateien, meldet Kopieren das; als Ausweg mit -debugscripts starten, erneut exportieren und Copy-Deck-Code.cmd ausführen. Import nimmt den vollständigen BG1-Code im Textfeld an.',
'fr': 'Exporter affiche un code BG1 indépendant de la langue. Copier le place directement dans le presse-papiers Windows ; collez-le n’importe où avec Ctrl+V. Les fichiers bin fournis sont nécessaires : dinput8.dll et plugins/GwentBetaClipboard.asi dans le dossier de witcher3.exe. Si un autre mod a déjà son propre dinput8.dll, gardez-le et chargez GwentBetaClipboard.asi avec son chargeur ASI. Sans ces fichiers, Copier l’indique ; solution de repli : lancer le jeu avec -debugscripts, exporter à nouveau et exécuter Copy-Deck-Code.cmd. Importer accepte le code BG1 complet dans le champ de texte.',
'it': 'Esporta mostra un codice BG1 indipendente dalla lingua. Copia lo inserisce direttamente negli appunti di Windows; incollalo ovunque con Ctrl+V. Servono i file bin inclusi: dinput8.dll e plugins/GwentBetaClipboard.asi nella cartella di witcher3.exe. Se un’altra mod ha già il proprio dinput8.dll, tienilo e carica GwentBetaClipboard.asi con il suo loader ASI. Senza questi file Copia lo segnala; in alternativa avvia il gioco con -debugscripts, esporta di nuovo ed esegui Copy-Deck-Code.cmd. Importa accetta il codice BG1 completo nel campo di testo.',
'pl': 'Eksport wyświetla kod BG1 niezależny od języka. Kopiuj umieszcza go bezpośrednio w schowku Windows; wklej go gdziekolwiek przez Ctrl+V. Wymagane są dołączone pliki bin: dinput8.dll i plugins/GwentBetaClipboard.asi w folderze witcher3.exe. Jeśli inny mod ma już własny dinput8.dll, zostaw go i wczytaj GwentBetaClipboard.asi jego loaderem ASI. Bez tych plików Kopiuj o tym poinformuje; awaryjnie uruchom grę z -debugscripts, wyeksportuj ponownie i uruchom Copy-Deck-Code.cmd. Import przyjmuje cały kod BG1 w polu tekstowym.',
'es': 'Exportar muestra un código BG1 independiente del idioma. Copiar lo pone directamente en el portapapeles de Windows; pégalo donde quieras con Ctrl+V. Se necesitan los archivos bin incluidos: dinput8.dll y plugins/GwentBetaClipboard.asi en la carpeta de witcher3.exe. Si otro mod ya tiene su propio dinput8.dll, consérvalo y carga GwentBetaClipboard.asi con su cargador ASI. Sin estos archivos, Copiar lo indica; como alternativa, inicia el juego con -debugscripts, exporta otra vez y ejecuta Copy-Deck-Code.cmd. Importar acepta el código BG1 completo en el campo de texto.',
'es-mx': 'Exportar muestra un código BG1 independiente del idioma. Copiar lo pone directamente en el portapapeles de Windows; pégalo donde quieras con Ctrl+V. Se necesitan los archivos bin incluidos: dinput8.dll y plugins/GwentBetaClipboard.asi en la carpeta de witcher3.exe. Si otro mod ya tiene su propio dinput8.dll, consérvalo y carga GwentBetaClipboard.asi con su cargador ASI. Sin estos archivos, Copiar lo indica; como alternativa, inicia el juego con -debugscripts, exporta otra vez y ejecuta Copy-Deck-Code.cmd. Importar acepta el código BG1 completo en el campo de texto.',
'pt-br': 'Exportar mostra um código BG1 independente do idioma. Copiar o coloca direto na área de transferência do Windows; cole onde quiser com Ctrl+V. São necessários os arquivos bin incluídos: dinput8.dll e plugins/GwentBetaClipboard.asi na pasta do witcher3.exe. Se outro mod já tiver seu próprio dinput8.dll, mantenha-o e carregue GwentBetaClipboard.asi pelo carregador ASI dele. Sem esses arquivos, Copiar avisa; como alternativa, inicie o jogo com -debugscripts, exporte novamente e execute Copy-Deck-Code.cmd. Importar aceita o código BG1 completo no campo de texto.',
'ja': 'エクスポートで言語に依存しないBG1コードを表示します。「コピー」でWindowsのクリップボードに直接コピーされ、Ctrl+Vでどこにでも貼り付けられます。同梱のbinファイル（witcher3.exeと同じフォルダーのdinput8.dllとplugins/GwentBetaClipboard.asi）が必要です。他のModが独自のdinput8.dllを使っている場合はそれを残し、そのASIローダーでGwentBetaClipboard.asiを読み込んでください。ファイルがない場合はコピーボタンがその旨を表示します。代替手段として-debugscriptsで起動して再エクスポートし、Copy-Deck-Code.cmdを実行してください。インポート欄には完全なBG1コードを入力してください。',
'ko': '내보내기는 언어와 무관한 BG1 코드를 표시합니다. 복사를 누르면 Windows 클립보드에 바로 들어가며 Ctrl+V로 어디든 붙여넣을 수 있습니다. 함께 제공되는 bin 파일(witcher3.exe 폴더의 dinput8.dll과 plugins/GwentBetaClipboard.asi)이 필요합니다. 다른 모드가 이미 자체 dinput8.dll을 사용한다면 그대로 두고 해당 ASI 로더로 GwentBetaClipboard.asi를 불러오세요. 파일이 없으면 복사 버튼이 알려 줍니다. 대안으로 -debugscripts로 실행해 다시 내보낸 뒤 Copy-Deck-Code.cmd를 실행하세요. 가져오기에는 전체 BG1 코드를 입력하세요.',
'zh-cn': '导出会显示与语言无关的BG1代码。点击“复制”会直接放入Windows剪贴板，可用Ctrl+V粘贴到任何地方。需要压缩包中的bin文件：witcher3.exe所在文件夹中的dinput8.dll和plugins/GwentBetaClipboard.asi。若其他模组已有自己的dinput8.dll，请保留它，并用其ASI加载器加载GwentBetaClipboard.asi。缺少这些文件时，复制按钮会提示。备用方法：以-debugscripts启动游戏，重新导出，再运行Copy-Deck-Code.cmd。导入框接受完整BG1代码。',
'zh-tw': '匯出會顯示與語言無關的BG1代碼。按下「複製」會直接放入Windows剪貼簿，可用Ctrl+V貼到任何地方。需要壓縮檔中的bin檔案：witcher3.exe所在資料夾中的dinput8.dll與plugins/GwentBetaClipboard.asi。若其他模組已有自己的dinput8.dll，請保留它，並以其ASI載入器載入GwentBetaClipboard.asi。缺少這些檔案時，複製按鈕會提示。備用方法：以-debugscripts啟動遊戲，重新匯出，再執行Copy-Deck-Code.cmd。匯入欄接受完整BG1代碼。',
}
BULLET = {
 'en': ('- Import from the deck list or editor; export from the editor. A text field supports Ctrl+C/Ctrl+V when direct clipboard access is unavailable.',
        '- Import from the deck list or editor; export from the editor. Copy writes the code directly to the Windows clipboard (bin files required, see below).'),
 'ru': ('- Импорт доступен из списка колод и редактора; экспорт — в редакторе. При недоступном прямом доступе к буферу остаётся текстовое поле для Ctrl+C/Ctrl+V.',
        '- Импорт доступен из списка колод и редактора; экспорт — в редакторе. «Копировать» записывает код прямо в буфер Windows (нужны файлы bin, см. ниже).'),
}
POST = {
 'en': "Copy now puts the BG1 code straight into the Windows clipboard. Copy the archive's bin folder into the game directory too (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe); if another mod already has a dinput8.dll, keep it and load the ASI with that mod's loader. Fallback without these files: launch with -debugscripts, export again and run Copy-Deck-Code.cmd.",
 'ru': 'Кнопка «Копировать» теперь сразу помещает код BG1 в буфер Windows. Установите папку bin из архива в каталог игры (dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe); если у другого мода уже есть dinput8.dll, оставьте его и загрузите ASI его загрузчиком. Запасной путь без этих файлов: запуск с -debugscripts, повторный экспорт и Copy-Deck-Code.cmd.',
}
APPEND = {
 'For Next-Gen, replace the previous modBetaGwent0924 folder and copy Mods into the game directory.': ' Also copy the bin folder: it enables the Copy button.',
 'Для Next-Gen замените прежнюю папку modBetaGwent0924 и скопируйте Mods в каталог игры.': ' Также скопируйте папку bin: она нужна для кнопки «Копировать».',
 '3. Copy Mods from the archive into the game directory, next to bin and content.': ' Also copy the archive\'s bin folder (Copy button support).',
 '3. Скопируйте Mods из архива в корень игры, рядом с bin и content.': ' Также скопируйте папку bin из архива (для кнопки «Копировать»).',
}
LANGS = list(NEW)


def strip(line):
    s = re.sub(r'\[/?b\]|\*\*', '', line.strip())
    return s[2:] if s.startswith('- ') or s.startswith('* ') else s


def main():
    assert not BACKUP.exists()
    shutil.copytree(NEXUS, BACKUP)
    old = {}
    for lang in LANGS:
        for p in (NEXUS / lang).glob('*'):
            for line in p.read_text('utf8').splitlines():
                if 'Copy-Deck-Code' in line:
                    kind = 'post' if p.name.startswith('post') else 'text'
                    old[strip(line)] = (lang, kind)
    changed = {}
    for p in sorted(NEXUS.rglob('*')):
        if not p.is_file() or p.suffix not in ('.md', '.txt'):
            continue
        raw = p.read_text('utf8'); lines = raw.split('\n'); count = 0
        for i, line in enumerate(lines):
            end = '\r' if line.endswith('\r') else ''
            body = line[:-1] if end else line
            for lang, (a, b) in BULLET.items():
                if body.strip() == a or strip(body) == strip(a):
                    lines[i] = body.replace(body.strip(), b) + end if body.strip() == a else ('[*]' if body.lstrip().startswith('[*]') else '- ') + b[2:] + end
                    count += 1
            for start, extra in APPEND.items():
                at = body.find(start)
                if at >= 0 and extra.strip() not in body:
                    pos = at + len(start)
                    body = body[:pos] + extra + body[pos:]; lines[i] = body + end; count += 1
            key = strip(body)
            if key in old:
                lang, kind = old[key]
                text = POST[lang] if kind == 'post' and lang in POST else NEW[lang]
                prefix = re.match(r'\s*(?:- |\* |\[\*\])?', body).group(0)
                lines[i] = prefix + text + end; count += 1
        if count:
            p.write_text('\n'.join(lines), 'utf8'); changed[p.relative_to(NEXUS).as_posix()] = count
    left = [p.relative_to(NEXUS).as_posix() for p in NEXUS.rglob('*') if p.is_file() and 'scriptslog.txt → ' in p.read_text('utf8', errors='ignore')]
    print(json.dumps(dict(changed=changed, oldParagraphs=len(old), leftovers=left), ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
