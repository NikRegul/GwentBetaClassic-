"""Pack original Beta resilience textures beside the existing HUD atlas."""
from pathlib import Path
from PIL import Image
import json, re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'BetaGwent/ui/assets/tokens111'

def main():
    base = Image.open(ROOT / 'BetaGwent/ui/assets/battle104/hud104.png').convert('RGBA')
    page = Image.new('RGBA', (base.width, base.height + 128))
    page.paste(base, (0, 0))
    items = [(-1890, 'TokenResilienceShield.png', 72, 88),
             (-1891, 'TokenResilienceBar.png', 180, 44),
             (-1892, 'TokenResilienceFittingL.png', 32, 64),
             (-1893, 'TokenResilienceFittingR.png', 32, 64)]
    src = ROOT / 'BetaGwent/ui/src/BetaGwentHDArt.as'
    code = src.read_text('utf-8-sig')
    slots = json.loads(re.search(r'private static var slots:Object=(\{.*?\});', code)[1])
    x = 0
    for ident, name, w, h in items:
        image = Image.open(OUT / name).convert('RGBA').resize((w, h), Image.Resampling.LANCZOS)
        page.paste(image, (x, base.height))
        slots[str(ident)] = [15, x, base.height, w, h]
        x += w + 8
    page.save(OUT / 'hud111.png')
    code = re.sub(r'private static var slots:Object=\{.*?\};',
                  'private static var slots:Object=' + json.dumps(slots, separators=(',', ':')) + ';', code)
    code = code.replace('battle104/hud104.png', 'tokens111/hud111.png')
    src.write_text(code, 'utf-8-sig')
    print('HUD atlas', page.size, 'four original resilience elements')

if __name__ == '__main__':
    main()
