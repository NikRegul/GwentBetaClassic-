"""0.9.0 texts: After-Uninstall item definitions (merchants keep their stock).

* 13 manual.md: paragraph after the uninstall result paragraph (after the
  bg_clean_confirm code block).
* en/ru changelog.md (+bbcode): bullet in "Saves and compatibility".
* docs/releases/0.9.0_CLEANUP_EN/RU.md (copied into BetaGwentDocs): section appended.
Idempotent. Backups: tmp/backup-texts090-keep.
"""
from pathlib import Path
import shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from update_nexus11_090 import load, insert_after_list, NEXUS, ROOT
from update_nexus9_090 import to_bbcode

BACKUP = ROOT / 'tmp/backup-texts090-keep'
P = {
 'en': "**After uninstalling:** copy the Mods folder from the archive's After-Uninstall folder into the game directory (Mods/modBetaGwentKeepItems). It keeps hidden definitions of the mod's items, so merchants, your stash and containers that still hold Beta cards or kegs don't lose their whole inventory. Do not install it together with the mod.",
 'ru': "**После удаления:** скопируйте папку Mods из папки After-Uninstall архива в каталог игры (Mods/modBetaGwentKeepItems). Она хранит скрытые определения предметов мода, и торговцы, тайник и контейнеры, где ещё лежат карты или бочки беты, не теряют весь инвентарь. Не устанавливайте её вместе с модом.",
 'de': "**Nach der Deinstallation:** Kopiere den Ordner Mods aus dem Ordner After-Uninstall des Archivs in das Spielverzeichnis (Mods/modBetaGwentKeepItems). Er enthält versteckte Definitionen der Mod-Gegenstände, damit Händler, Truhe und Behälter, die noch Beta-Karten oder Fässer enthalten, nicht ihr gesamtes Inventar verlieren. Nicht zusammen mit der Mod installieren.",
 'fr': "**Après la désinstallation :** copiez le dossier Mods du dossier After-Uninstall de l’archive dans le répertoire du jeu (Mods/modBetaGwentKeepItems). Il conserve des définitions cachées des objets du mod, afin que les marchands, la réserve et les conteneurs qui contiennent encore des cartes ou des barils de la bêta ne perdent pas tout leur inventaire. Ne l’installez pas en même temps que le mod.",
 'it': "**Dopo la disinstallazione:** copia la cartella Mods dalla cartella After-Uninstall dell’archivio nella cartella del gioco (Mods/modBetaGwentKeepItems). Conserva definizioni nascoste degli oggetti della mod, così mercanti, deposito e contenitori che contengono ancora carte o barili della beta non perdono l’intero inventario. Non installarla insieme alla mod.",
 'pl': "**Po odinstalowaniu:** skopiuj folder Mods z folderu After-Uninstall archiwum do katalogu gry (Mods/modBetaGwentKeepItems). Zawiera ukryte definicje przedmiotów moda, dzięki czemu kupcy, skrytka i pojemniki, w których wciąż są karty lub beczki bety, nie tracą całego ekwipunku. Nie instaluj go razem z modem.",
 'es': "**Después de desinstalar:** copia la carpeta Mods de la carpeta After-Uninstall del archivo al directorio del juego (Mods/modBetaGwentKeepItems). Conserva definiciones ocultas de los objetos del mod para que los comerciantes, el alijo y los contenedores que aún tengan cartas o barriles de la beta no pierdan todo su inventario. No la instales junto con el mod.",
 'es-mx': "**Después de desinstalar:** copia la carpeta Mods de la carpeta After-Uninstall del archivo al directorio del juego (Mods/modBetaGwentKeepItems). Conserva definiciones ocultas de los objetos del mod para que los comerciantes, el alijo y los contenedores que aún tengan cartas o barriles de la beta no pierdan todo su inventario. No la instales junto con el mod.",
 'pt-br': "**Depois de desinstalar:** copie a pasta Mods da pasta After-Uninstall do arquivo para o diretório do jogo (Mods/modBetaGwentKeepItems). Ela mantém definições ocultas dos itens do mod, para que mercadores, o baú e os contêineres que ainda tenham cartas ou barris da beta não percam todo o inventário. Não a instale junto com o mod.",
 'ja': "**アンインストール後：** アーカイブのAfter-UninstallフォルダーにあるModsフォルダーをゲームのフォルダーにコピーしてください（Mods/modBetaGwentKeepItems）。Modのアイテムの非表示定義が残るため、ベータのカードやタルが残っている商人、収納箱、コンテナの所持品がすべて失われるのを防ぎます。Modと一緒にはインストールしないでください。",
 'ko': "**제거 후:** 압축 파일의 After-Uninstall 폴더에 있는 Mods 폴더를 게임 폴더에 복사하세요(Mods/modBetaGwentKeepItems). 모드 아이템의 숨김 정의가 남아 있어, 베타 카드나 카드통이 남아 있는 상인, 보관함, 상자의 인벤토리 전체가 사라지는 것을 막습니다. 모드와 함께 설치하지 마세요.",
 'zh-cn': "**卸载后：** 将压缩包After-Uninstall文件夹中的Mods文件夹复制到游戏目录（Mods/modBetaGwentKeepItems）。它保留模组物品的隐藏定义，避免仍持有测试版卡牌或卡桶的商人、储物箱和容器丢失全部物品。不要与模组同时安装。",
 'zh-tw': "**解除安裝後：** 將壓縮檔After-Uninstall資料夾中的Mods資料夾複製到遊戲目錄（Mods/modBetaGwentKeepItems）。它保留模組物品的隱藏定義，避免仍持有測試版卡牌或卡桶的商人、儲物箱與容器遺失全部物品。不要與模組同時安裝。",
}
CHANGE = {'en': "Added an After-Uninstall folder with hidden item definitions: after removing the mod, merchants that still stock Beta cards or kegs no longer lose their whole inventory.",
          'ru': "Добавлена папка After-Uninstall со скрытыми определениями предметов: после удаления мода торговцы, у которых остались карты или бочки беты, больше не теряют весь ассортимент."}
SAVES = {'en': '## Saves and compatibility', 'ru': '## Сохранения и совместимость'}
CLEANUP = {'en': "\n## After uninstalling: keep item definitions\n\n" + P['en'] + "\n",
           'ru': "\n## После удаления: определения предметов\n\n" + P['ru'] + "\n"}


def store(p, t, bom, crlf):
    target = BACKUP / p.relative_to(ROOT)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)
    if crlf: t = t.replace('\n', '\r\n')
    p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))


def main():
    for lang, para in P.items():
        p = NEXUS / lang / 'manual.md'; t, bom, crlf = load(p)
        if 'modBetaGwentKeepItems' in t: print('manual', lang, 'already'); continue
        lines = t.split('\n')
        i = lines.index("bg_clean_confirm('DELETE_BETA_GWENT')")
        assert lines[i + 1] == '```' and lines[i + 2] == '' and lines[i + 3].strip(), (lang, lines[i + 1:i + 4])
        lines[i + 4:i + 4] = ['', para]
        store(p, '\n'.join(lines), bom, crlf); print('manual', lang)
    for lang in ['en', 'ru']:
        p = NEXUS / lang / 'changelog.md'; t, bom, crlf = load(p)
        if CHANGE[lang] not in t:
            t = insert_after_list(t, t.split('\n').index(SAVES[lang]), CHANGE[lang]); store(p, t, bom, crlf)
            bb = NEXUS / lang / 'changelog.bbcode.txt'; b0, bbom, bcrlf = load(bb); store(bb, to_bbcode(t), bbom, bcrlf)
            print('changelog', lang)
        c = ROOT / f'docs/releases/0.9.0_CLEANUP_{lang.upper()}.md'; t, bom, crlf = load(c)
        if 'modBetaGwentKeepItems' not in t:
            store(c, t.rstrip('\n') + '\n' + CLEANUP[lang], bom, crlf); print('cleanup doc', lang)


if __name__ == '__main__':
    main()
