"""Build 12 changelog line (EN/RU): console messages follow the mod text language."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from update_nexus11_090 import load, store, insert_after_list, NEXUS
from update_nexus9_090 import to_bbcode

LINE = {'en': 'Console command messages use the text language selected in the mod settings (13 languages).',
        'ru': 'Сообщения консольных команд выводятся на языке текста, выбранном в настройках мода (13 языков).'}
HEAD = {'en': '## Console', 'ru': '## Консоль'}

for lang in ['en', 'ru']:
    p = NEXUS / lang / 'changelog.md'; t, bom, crlf = load(p)
    if LINE[lang] in t: print('changelog', lang, 'already'); continue
    t = insert_after_list(t, t.split('\n').index(HEAD[lang]), LINE[lang]); store(p, t, bom, crlf)
    bb = NEXUS / lang / 'changelog.bbcode.txt'; b0, bbom, bcrlf = load(bb)
    store(bb, to_bbcode(t), bbom, bcrlf); print('changelog', lang)
