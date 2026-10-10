"""Check the packed original foam frames and the scrolling storm join."""
from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
report = json.loads((ROOT / 'docs/evidence/beta-weather107.json').read_text('utf8'))
atlas = Image.open(report['atlas']).convert('RGBA')
checks = 0

def check(condition, label):
    global checks
    if not condition:
        raise AssertionError(label)
    checks += 1

def tile(label):
    page, x, y, w, h = report['layers'][label]
    check(page == 19 and x + w <= atlas.width and y + h <= atlas.height, label + ' atlas bounds')
    return atlas.crop((x, y, x + w, y + h))

foam = tile('froth-foam')
check(foam.size == (384, 384), 'complete 6 by 6 foam sheet')
for frame in (5, 11, 17, 23, 29, 35):
    x, y = frame % 6 * 64, frame // 6 * 64
    alpha = foam.crop((x, y, x + 64, y + 64)).getchannel('A')
    check(alpha.getbbox() is not None and alpha.getpixel((32, 32)) > 100, 'whole foam blob in frame ' + str(frame))
storm = tile('storm-sea')
check(all(storm.getpixel((0, y))[3] == storm.getpixel((storm.width - 1, y))[3]
          for y in range(storm.height)), 'storm alpha is continuous at the wrap')
check(storm.getpixel((0, storm.height // 2))[3] > 240, 'no horizontal fading hole at the join')
check(max(abs(a - b) for y in range(storm.height)
          for a, b in zip(storm.getpixel((0, y)), storm.getpixel((storm.width - 1, y)))) <= 5,
      'storm colour remains continuous after resampling')
result = dict(stage=121, checks=checks, foamFrames=36, atlasSize=list(atlas.size), nativeVisualVerified=False)
(ROOT / 'docs/evidence/weather-atlas121.json').write_text(json.dumps(result, indent=2) + '\n', 'utf8')
print(json.dumps(result))
