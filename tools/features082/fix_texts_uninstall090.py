"""Add to every 0.9.0 cleanup section: the INCOMPLETE result and removing Optional-CopyButton files."""
from pathlib import Path
import shutil, json
ROOT = Path(__file__).resolve().parents[2]; NEXUS = ROOT / 'docs/releases/0.9.0/nexus'
BACKUP = ROOT / 'tmp/backup-texts090-uninstall'
A = {
'en': ' If some Beta item stacks cannot be removed, the game shows INCOMPLETE instead of success: drop or sell them and run the command again.',
'ru': ' Если часть стопок предметов беты удалить не удалось, вместо успеха будет сообщение INCOMPLETE: выбросьте или продайте их и повторите команду.',
'de': ' Lassen sich einige Beta-Gegenstände nicht entfernen, erscheint INCOMPLETE statt der Erfolgsmeldung: diese wegwerfen oder verkaufen und den Befehl wiederholen.',
'fr': ' Si certains objets Beta ne peuvent pas être retirés, le jeu affiche INCOMPLETE au lieu du succès : jetez-les ou vendez-les, puis relancez la commande.',
'it': ' Se alcuni oggetti Beta non possono essere rimossi, appare INCOMPLETE invece del successo: gettali o vendili e ripeti il comando.',
'pl': ' Jeśli części przedmiotów Beta nie da się usunąć, zamiast sukcesu pojawi się INCOMPLETE: wyrzuć je lub sprzedaj i powtórz polecenie.',
'es': ' Si algunos objetos Beta no se pueden quitar, aparece INCOMPLETE en lugar del éxito: tíralos o véndelos y repite el comando.',
'es-mx': ' Si algunos objetos Beta no se pueden quitar, aparece INCOMPLETE en lugar del éxito: tíralos o véndelos y repite el comando.',
'pt-br': ' Se alguns itens Beta não puderem ser removidos, aparece INCOMPLETE em vez do sucesso: descarte ou venda esses itens e repita o comando.',
'ja': ' 一部のベータアイテムを削除できなかった場合は成功ではなくINCOMPLETEと表示されます。それらを捨てるか売却してから、もう一度コマンドを実行してください。',
'ko': ' 일부 베타 아이템을 제거하지 못하면 성공 대신 INCOMPLETE가 표시됩니다. 해당 아이템을 버리거나 판매한 뒤 명령을 다시 실행하세요.',
'zh-cn': ' 若部分Beta物品无法移除，将显示INCOMPLETE而不是成功信息：请丢弃或出售这些物品后再次执行命令。',
'zh-tw': ' 若部分Beta物品無法移除，將顯示INCOMPLETE而非成功訊息：請丟棄或出售這些物品後再次執行指令。',
}
B = {
'en': ' When uninstalling, also delete the Optional-CopyButton files if you installed them: bin\\…\\plugins\\GwentBetaClipboard.asi and the dinput8.dll from this mod (not another mod\'s).',
'ru': ' При удалении мода уберите и файлы Optional-CopyButton, если ставили их: bin\\…\\plugins\\GwentBetaClipboard.asi и dinput8.dll из этого мода (не чужой).',
'de': ' Beim Deinstallieren auch die Optional-CopyButton-Dateien löschen, falls installiert: bin\\…\\plugins\\GwentBetaClipboard.asi und die dinput8.dll dieses Mods (nicht die eines anderen).',
'fr': ' À la désinstallation, supprimez aussi les fichiers Optional-CopyButton s’ils sont installés : bin\\…\\plugins\\GwentBetaClipboard.asi et le dinput8.dll de ce mod (pas celui d’un autre).',
'it': ' Disinstallando, elimina anche i file di Optional-CopyButton se li hai installati: bin\\…\\plugins\\GwentBetaClipboard.asi e il dinput8.dll di questa mod (non di altre).',
'pl': ' Przy odinstalowaniu usuń też pliki Optional-CopyButton, jeśli je instalowano: bin\\…\\plugins\\GwentBetaClipboard.asi oraz dinput8.dll z tego moda (nie z innego).',
'es': ' Al desinstalar, borra también los archivos de Optional-CopyButton si los instalaste: bin\\…\\plugins\\GwentBetaClipboard.asi y el dinput8.dll de este mod (no el de otro).',
'es-mx': ' Al desinstalar, borra también los archivos de Optional-CopyButton si los instalaste: bin\\…\\plugins\\GwentBetaClipboard.asi y el dinput8.dll de este mod (no el de otro).',
'pt-br': ' Ao desinstalar, apague também os arquivos de Optional-CopyButton se os instalou: bin\\…\\plugins\\GwentBetaClipboard.asi e o dinput8.dll deste mod (não o de outro).',
'ja': ' アンインストール時は、Optional-CopyButtonを導入した場合そのファイル（bin\\…\\plugins\\GwentBetaClipboard.asiとこのModのdinput8.dll。他のModのものは除く）も削除してください。',
'ko': ' 제거할 때 Optional-CopyButton을 설치했다면 그 파일(bin\\…\\plugins\\GwentBetaClipboard.asi와 이 모드의 dinput8.dll, 다른 모드의 것은 제외)도 삭제하세요.',
'zh-cn': ' 卸载时，若安装过Optional-CopyButton，也请删除其文件：bin\\…\\plugins\\GwentBetaClipboard.asi以及本模组的dinput8.dll（不要删除其他模组的）。',
'zh-tw': ' 解除安裝時，若安裝過Optional-CopyButton，也請刪除其檔案：bin\\…\\plugins\\GwentBetaClipboard.asi以及本模組的dinput8.dll（勿刪除其他模組的）。',
}
CLEANUP = {'0.9.0_CLEANUP_EN.md': 'en', '0.9.0_CLEANUP_RU.md': 'ru'}


def paragraph_after_command(lines):
    for i, line in enumerate(lines):
        if "bg_clean_confirm('DELETE_BETA_GWENT')" == line.strip():
            for j in range(i + 1, len(lines)):
                t = lines[j].strip()
                if t and t not in ('```', '[/code]'):
                    return j
    return None


def main():
    assert not BACKUP.exists(); shutil.copytree(NEXUS, BACKUP / 'nexus')
    for f in CLEANUP: shutil.copy2(ROOT / 'docs/releases' / f, BACKUP / f)
    keys = {}
    for lang in A:
        p = NEXUS / lang / 'description.md'; lines = p.read_text('utf8').split('\n'); j = paragraph_after_command(lines)
        assert j is not None, lang
        keys[lines[j].rstrip('\r')] = lang
    targets = [*NEXUS.rglob('*.md'), *NEXUS.rglob('*.txt'), *(ROOT / 'docs/releases' / f for f in CLEANUP)]
    done = {}
    for p in targets:
        lines = p.read_text('utf8').split('\n'); n = 0
        for i, line in enumerate(lines):
            end = '\r' if line.endswith('\r') else ''; body = line[:-1] if end else line
            lang = next((l for k, l in keys.items() if body.startswith(k)), None)
            if lang is None and p.name in CLEANUP and body.startswith('Completed quests') | body.startswith('Завершённые квесты'):
                lang = CLEANUP[p.name]
            if lang is None or 'Optional-CopyButton' in body:
                continue
            add = ('' if 'INCOMPLETE' in body else A[lang]) + B[lang]
            if p.name in CLEANUP:
                add = B[lang]
            lines[i] = body + add + end; n += 1
        if n:
            p.write_text('\n'.join(lines), 'utf8'); done[str(p.relative_to(ROOT / 'docs/releases'))] = n
    print(json.dumps(done, indent=1))


if __name__ == '__main__':
    main()
