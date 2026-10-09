"""Inspect a local reference video without re-encoding or changing the source."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import av
from PIL import Image, ImageDraw, ImageFont


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('video', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--every', type=float, default=300)
    p.add_argument('--times', type=float, nargs='+')
    p.add_argument('--start', type=float, default=0)
    p.add_argument('--end', type=float)
    a = p.parse_args()
    # Keep the explicitly supplied path: Windows may deny resolving a parent
    # while still allowing reads of the named attachment itself.
    video = a.video.absolute()
    a.out.mkdir(parents=True, exist_ok=True)
    c = av.open(str(video))
    stream = c.streams.video[0]
    duration = c.duration / av.time_base if c.duration else float(stream.duration * stream.time_base)
    end = min(a.end if a.end is not None else duration - .1, duration - .1)
    assert a.every > 0 and a.start >= 0
    times = a.times if a.times else [a.start + i * a.every for i in range(1 + math.floor((end-a.start)/a.every))]
    font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 17)
    frames = []
    for n, t in enumerate(times):
        assert 0 <= t < duration
        c.seek(int(t/stream.time_base), stream=stream, backward=True)
        for f in c.decode(stream):
            if f.time is not None and f.time >= t:
                name = f'frame-{n:04}-{t:09.3f}.png'
                im = f.to_image().convert('RGB')
                im.save(a.out/name)
                frames.append(dict(requested=t, actual=f.time, file=name, image=im))
                break
    sheets = []
    for start in range(0, len(frames), 8):
        subset = frames[start:start+8]
        sheet = Image.new('RGB', (1280, 210 * math.ceil(len(subset)/4)), '#101010')
        d = ImageDraw.Draw(sheet)
        for i, item in enumerate(subset):
            x, y = i % 4 * 320, i // 4 * 210
            sheet.paste(item['image'].resize((320, 180), Image.Resampling.LANCZOS), (x, y))
            t = item['actual']
            d.text((x+5, y+183), f'{int(t)//3600:02}:{int(t)//60%60:02}:{t%60:06.3f}', font=font, fill='white')
        name = f'sheet-{start//8:02}.jpg'
        sheet.save(a.out/name, quality=94)
        sheets.append(name)
    h = hashlib.sha256()
    with video.open('rb') as source:
        for chunk in iter(lambda: source.read(1024*1024), b''):
            h.update(chunk)
    for item in frames:
        del item['image']
    result = dict(source=str(video), bytes=video.stat().st_size, sha256=h.hexdigest(),
                  duration=duration, width=stream.width, height=stream.height,
                  fps=str(stream.average_rate), frames=frames, sheets=sheets)
    c.close()
    (a.out/'index.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['duration','width','height','fps','sheets']}))


if __name__ == '__main__':
    main()
