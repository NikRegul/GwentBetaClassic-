"""Build 13 changelog line (EN/RU): 1.32 merchants keep their stock with the mod."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from update_nexus11_090 import load, store, insert_after_list, NEXUS
from update_nexus9_090 import to_bbcode

LINE = {'en': 'Classic 1.32: merchants no longer lose their stock with the mod installed. The mod\'s loot tables and item definitions now use the game\'s native UTF-16 XML format.',
        'ru': 'Classic 1.32: у торговцев больше не пропадает ассортимент с установленным модом. Таблицы ассортимента и определения предметов мода теперь в родном для игры формате XML UTF-16.'}
SAVES = {'en': '## Saves and compatibility', 'ru': '## Сохранения и совместимость'}
for lang in ['en', 'ru']:
    p = NEXUS / lang / 'changelog.md'; t, bom, crlf = load(p)
    if LINE[lang] in t: print('changelog', lang, 'already'); continue
    t = insert_after_list(t, t.split('\n').index(SAVES[lang]), LINE[lang]); store(p, t, bom, crlf)
    bb = NEXUS / lang / 'changelog.bbcode.txt'; b0, bbom, bcrlf = load(bb); store(bb, to_bbcode(t), bbom, bcrlf)
    print('changelog', lang)
