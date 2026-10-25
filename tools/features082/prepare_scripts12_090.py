"""0.9.0 build 12 scripts: console and notification texts follow the mod text language.

Source: build 11 scripts (recoverable profile backup). Every console message of the
bg_* commands, the shop diagnostics, restored deck names and the restore-failure
notification use BetaGwentConsoleText/Format (13 languages, console_text12_090.py),
selected by the mod's text language setting (top-left in the Gwent menu; Auto follows
the game). CJK texts fall back to English when the game itself is not in that language.
Output: BetaGwent/build/release090-scripts12/scripts.
"""
from pathlib import Path
import shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from console_text12_090 import ws_function

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/release090-scripts11/scripts'
OUT = ROOT / 'BetaGwent/build/release090-scripts12'
MENU = 'game/betagwent/developmentBoardMenu.ws'
BACKUP = 'game/betagwent/profileBackup.ws'
SHOP = 'game/betagwent/shopRuntime.ws'
F = 'BetaGwentConsoleFormat'
T = 'BetaGwentConsoleText'

MENU_PATCHES = [
    ('BetaGwentConsoleMessage("Загрузите сохранение игры.")', 'BetaGwentConsoleMessage(%s(1))' % T),
    ('BetaGwentConsoleMessage("Закройте меню перед выдачей ресурсов.")', 'BetaGwentConsoleMessage(%s(2))' % T),
    ('BetaGwentConsoleMessage("Коллекция недоступна.")', 'BetaGwentConsoleMessage(%s(3))' % T),
    ('BetaGwentConsoleMessage("bg_allcards: добавлено "+granted+" копий карт и лидеров.")', 'BetaGwentConsoleMessage(%s(4,""+granted))' % F),
    ('BetaGwentConsoleMessage("bg_kegs(10): количество от 1 до 1000000.")', 'BetaGwentConsoleMessage(%s(5))' % T),
    ('BetaGwentConsoleMessage("Переполнение счётчика бочек.")', 'BetaGwentConsoleMessage(%s(6))' % T),
    ('BetaGwentConsoleMessage("bg_kegs: добавлено "+(player.BetaGwentKegCount()-before)+", всего "+player.BetaGwentKegCount()+".")',
     'BetaGwentConsoleMessage(%s(7,""+(player.BetaGwentKegCount()-before),""+player.BetaGwentKegCount()))' % F),
    ('BetaGwentConsoleMessage("bg_scraps(1000): количество от 1 до 1000000.")', 'BetaGwentConsoleMessage(%s(8))' % T),
    ('BetaGwentConsoleMessage("Переполнение счётчика осколков.")', 'BetaGwentConsoleMessage(%s(9))' % T),
    ('BetaGwentConsoleMessage("bg_scraps: добавлено "+(player.BetaGwentScraps()-before)+", всего "+player.BetaGwentScraps()+".")',
     'BetaGwentConsoleMessage(%s(10,""+(player.BetaGwentScraps()-before),""+player.BetaGwentScraps()))' % F),
    ('BetaGwentConsoleMessage("bg_card(132102,1): нужен ID коллекционной карты/лидера и количество 1–1000.")', 'BetaGwentConsoleMessage(%s(11))' % T),
    ('BetaGwentConsoleMessage(d.title+" ("+id+"): добавлено "+granted+", в наличии "+player.BetaGwentOwned(id)+" / "+BetaGwentCollectionCap(id)+".")',
     'BetaGwentConsoleMessage(%s(12,d.title,""+id,""+granted,""+player.BetaGwentOwned(id),""+BetaGwentCollectionCap(id)))' % F),
    ('BetaGwentConsoleMessage("bg_find(\'Имлерих\'): введите от 2 до 80 символов.")', 'BetaGwentConsoleMessage(%s(13))' % T),
    ('BetaGwentConsoleMessage(summary+"Найдено: "+total+". Полный список — в журнале BetaGwent.")', 'BetaGwentConsoleMessage(summary+%s(14,""+total))' % F),
    ('BetaGwentConsoleMessage("Фракции: neutral, monsters, nilfgaard, north, scoiatael, skellige.")', 'BetaGwentConsoleMessage(%s(15))' % T),
    ('BetaGwentConsoleMessage("bg_faction: добавлено "+granted+" копий до лимита фракции "+value+".")', 'BetaGwentConsoleMessage(%s(16,""+granted,value))' % F),
    ('BetaGwentConsoleMessage("bg_leaders: добавлено "+granted+" лидеров.")', 'BetaGwentConsoleMessage(%s(17,""+granted))' % F),
    ('BetaGwentConsoleMessage("Коллекция: "+distinct+" / "+ids.Size()+", копий: "+total+"; бочки: "+player.BetaGwentKegCount()+"; осколки: "+player.BetaGwentScraps()+"; выбор бочки: "+player.BetaGwentKegPending()+"; NG+: "+FactsQuerySum("NewGamePlus"))',
     'BetaGwentConsoleMessage(%s(18,""+distinct,""+ids.Size(),""+total,""+player.BetaGwentKegCount(),""+player.BetaGwentScraps(),""+player.BetaGwentKegPending(),""+FactsQuerySum("NewGamePlus")))' % F),
    ('BetaGwentConsoleMessage("Откройте магазин продавца.")', 'BetaGwentConsoleMessage(%s(19))' % T),
    ('BetaGwentConsoleMessage("bg_shoprefill(5): целевой запас от 1 до 99.")', 'BetaGwentConsoleMessage(%s(20))' % T),
    ('BetaGwentConsoleMessage("Откройте магазин корчмаря.")', 'BetaGwentConsoleMessage(%s(21))' % T),
]
BACKUP_PATCHES = [
    ('"Колода " + slot', '%s(27, IntToString(slot))' % F, 2),
    ('ShowNotification("Gwent Beta Classic: the Gwent profile backup could not be applied, a new profile was started. / Резервную копию профиля гвинта применить не удалось, начат новый профиль.", 12.0)',
     'ShowNotification(%s(28), 12.0)' % T, 1),
]
SHOP_PATCHES = [
    ('return "Откройте магазин продавца.";', 'return %s(19);' % T),
    ('return "Инвентарь продавца недоступен.";', 'return %s(23);' % T),
    ('return "Запас бочек должен быть от 1 до 99.";', 'return %s(24);' % T),
    ('return message+" · Пополнение доступно у корчмаря.";', 'return message+%s(25);' % T),
    ('return message+" · Предмет не создан: проверьте установку DLC с определением бочки.";', 'return message+%s(26);' % T),
    ('message+=" · Бочек в запасе нет; создание предмета не проверено.";', 'message+=%s(29);' % T),
    ('message+=" · Предмет бочки присутствует в запасе.";', 'message+=%s(30);' % T),
]


def edit(path, fix):
    raw = path.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
    s = fix(raw.decode('utf-8-sig').replace('\r\n', '\n'))
    if crlf: s = s.replace('\n', '\r\n')
    path.write_bytes((b'\xef\xbb\xbf' if bom else b'') + s.encode('utf8'))


def patch_menu(s):
    for old, new in MENU_PATCHES:
        assert s.count(old) == 1, old[:80]
        s = s.replace(old, new)
    a = s.index('exec function bg_help()')
    b = s.index('}', a) + 1
    s = s[:a] + 'exec function bg_help()\n{\n    BetaGwentConsoleMessage(BetaGwentConsoleHelp());\n}' + s[b:]
    return s.rstrip('\n') + '\n' + ws_function()


def patch_backup(s):
    for old, new, n in BACKUP_PATCHES:
        assert s.count(old) == n, old[:80]
        s = s.replace(old, new)
    return s


def patch_shop(s):
    for old, new in SHOP_PATCHES:
        assert s.count(old) == 1, old[:80]
        s = s.replace(old, new)
    return s


def check(root):
    import re
    for name in [MENU, SHOP]:
        s = (root / name).read_text('utf-8-sig')
        body = s.split('// Build 12: console')[0]
        left = [m for m in re.findall(r'"[^"\n]*[А-Яа-яЁё][^"\n]*"', body)]
        left = [x for x in left if 'Имлерих' not in x]
        if name == MENU:
            # Only the board (menu-side) texts may stay; no console output literals.
            seg = body[body.index('function BetaGwentConsoleMessage'):body.index('function BetaGwentTextLanguage137')]
            assert not re.search(r'"[^"\n]*[А-Яа-яЁё][^"\n]*"', seg), 'Russian literal left in console commands'
        else:
            seg = body[body.index('BetaGwentShopDiagnostic'):]
            seg = seg[:seg.index('\n}') ]
            assert not re.search(r'"[^"\n]*[А-Яа-яЁё][^"\n]*"', seg), 'Russian literal left in shop diagnostics'


def main():
    assert not OUT.exists(), 'Fresh output folder required'
    shutil.copytree(SOURCE, OUT / 'scripts')
    edit(OUT / 'scripts' / MENU, patch_menu)
    edit(OUT / 'scripts' / BACKUP, patch_backup)
    edit(OUT / 'scripts' / SHOP, patch_shop)
    check(OUT / 'scripts')
    print('Prepared build 12 scripts: console texts in 13 languages (mod text language).')


if __name__ == '__main__':
    main()
