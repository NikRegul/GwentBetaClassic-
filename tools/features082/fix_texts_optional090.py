"""Describe the copy-button files as the optional Optional-CopyButton folder in all 0.9.0 texts."""
from pathlib import Path
import shutil, json
ROOT = Path(__file__).resolve().parents[2]
FILES = [*(ROOT / 'docs/releases/0.9.0/nexus').rglob('*.md'), *(ROOT / 'docs/releases/0.9.0/nexus').rglob('*.txt')]
BACKUP = ROOT / 'tmp/backup-texts090-optional'
R = [
('This needs the included bin files: dinput8.dll and plugins/GwentBetaClipboard.asi in the folder of witcher3.exe.','This needs the optional Optional-CopyButton folder from the archive: copy its bin folder into the game directory (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe). The mod itself works without it.'),
('Для этого нужны файлы bin из архива: dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe.','Для этого нужна необязательная папка Optional-CopyButton из архива: скопируйте её папку bin в каталог игры (dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe). Сам мод работает и без неё.'),
('Dafür werden die mitgelieferten bin-Dateien benötigt: dinput8.dll und plugins/GwentBetaClipboard.asi im Ordner von witcher3.exe.','Dafür den optionalen Ordner Optional-CopyButton nutzen: dessen bin-Ordner ins Spielverzeichnis kopieren (dinput8.dll und plugins/GwentBetaClipboard.asi neben witcher3.exe). Der Mod selbst funktioniert auch ohne ihn.'),
('Les fichiers bin fournis sont nécessaires : dinput8.dll et plugins/GwentBetaClipboard.asi dans le dossier de witcher3.exe.','Il faut pour cela le dossier facultatif Optional-CopyButton : copiez son dossier bin dans le répertoire du jeu (dinput8.dll et plugins/GwentBetaClipboard.asi à côté de witcher3.exe). Le mod fonctionne aussi sans lui.'),
('Servono i file bin inclusi: dinput8.dll e plugins/GwentBetaClipboard.asi nella cartella di witcher3.exe.','Serve la cartella facoltativa Optional-CopyButton: copia la sua cartella bin nella directory del gioco (dinput8.dll e plugins/GwentBetaClipboard.asi accanto a witcher3.exe). La mod funziona anche senza.'),
('Wymagane są dołączone pliki bin: dinput8.dll i plugins/GwentBetaClipboard.asi w folderze witcher3.exe.','Potrzebny jest opcjonalny folder Optional-CopyButton: skopiuj jego folder bin do katalogu gry (dinput8.dll i plugins/GwentBetaClipboard.asi obok witcher3.exe). Sam mod działa również bez niego.'),
('Se necesitan los archivos bin incluidos: dinput8.dll y plugins/GwentBetaClipboard.asi en la carpeta de witcher3.exe.','Se necesita la carpeta opcional Optional-CopyButton: copia su carpeta bin en el directorio del juego (dinput8.dll y plugins/GwentBetaClipboard.asi junto a witcher3.exe). El mod funciona también sin ella.'),
('São necessários os arquivos bin incluídos: dinput8.dll e plugins/GwentBetaClipboard.asi na pasta do witcher3.exe.','É necessária a pasta opcional Optional-CopyButton: copie a pasta bin dela para o diretório do jogo (dinput8.dll e plugins/GwentBetaClipboard.asi ao lado do witcher3.exe). O mod funciona também sem ela.'),
('同梱のbinファイル（witcher3.exeと同じフォルダーのdinput8.dllとplugins/GwentBetaClipboard.asi）が必要です。','任意フォルダーOptional-CopyButtonが必要です。その中のbinフォルダーをゲームのフォルダーにコピーしてください（witcher3.exeと同じ場所にdinput8.dllとplugins/GwentBetaClipboard.asi）。Mod本体はこれがなくても動作します。'),
('함께 제공되는 bin 파일(witcher3.exe 폴더의 dinput8.dll과 plugins/GwentBetaClipboard.asi)이 필요합니다.','선택 사항인 Optional-CopyButton 폴더가 필요합니다. 그 안의 bin 폴더를 게임 폴더에 복사하세요(witcher3.exe 옆에 dinput8.dll과 plugins/GwentBetaClipboard.asi). 모드 자체는 이 폴더 없이도 작동합니다.'),
('需要压缩包中的bin文件：witcher3.exe所在文件夹中的dinput8.dll和plugins/GwentBetaClipboard.asi。','需要压缩包中的可选文件夹Optional-CopyButton：将其中的bin文件夹复制到游戏目录（dinput8.dll和plugins/GwentBetaClipboard.asi位于witcher3.exe旁）。模组本身无需它也能运行。'),
('需要壓縮檔中的bin檔案：witcher3.exe所在資料夾中的dinput8.dll與plugins/GwentBetaClipboard.asi。','需要壓縮檔中的選用資料夾Optional-CopyButton：將其中的bin資料夾複製到遊戲目錄（dinput8.dll與plugins/GwentBetaClipboard.asi位於witcher3.exe旁）。模組本身無需它也能運作。'),
("Copy the archive's bin folder into the game directory too (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe);","Optional: copy the bin folder from Optional-CopyButton into the game directory (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe); the mod works without it;"),
('Установите папку bin из архива в каталог игры (dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe);','По желанию скопируйте папку bin из Optional-CopyButton в каталог игры (dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe), мод работает и без неё;'),
(' Also copy the bin folder: it enables the Copy button.',' Optionally copy bin from Optional-CopyButton for the Copy button.'),
(' Также скопируйте папку bin: она нужна для кнопки «Копировать».',' По желанию скопируйте bin из Optional-CopyButton — для кнопки «Копировать».'),
(" Also copy the archive's bin folder (Copy button support).",' Optional: copy bin from Optional-CopyButton (Copy button).'),
(' Также скопируйте папку bin из архива (для кнопки «Копировать»).',' По желанию: bin из Optional-CopyButton (кнопка «Копировать»).'),
('(bin files required, see below)','(optional Optional-CopyButton folder, see below)'),
('(нужны файлы bin, см. ниже)','(нужна необязательная папка Optional-CopyButton, см. ниже)'),
]
assert not BACKUP.exists(); shutil.copytree(ROOT / 'docs/releases/0.9.0/nexus', BACKUP)
counts = {a[:40]: 0 for a, _ in R}; changed = {}
for p in FILES:
    s = p.read_text('utf8'); n = 0
    for a, b in R:
        k = s.count(a); s = s.replace(a, b); counts[a[:40]] += k; n += k
    if n: p.write_text(s, 'utf8'); changed[p.name if p.parent.name == 'nexus' else p.parent.name + '/' + p.name] = n
missing = [k for k, v in counts.items() if not v]
print(json.dumps(dict(files=len(changed), missing=missing), ensure_ascii=False))
assert not missing
