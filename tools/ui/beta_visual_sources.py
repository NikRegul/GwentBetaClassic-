"""Read original Beta sprites/particles into the existing native GFx atlas.

Original Unity bundles are read only. The images are CD Projekt assets, not
part of the GPL code license. Unity particle systems still require 2D adaptation.
"""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
import UnityPy

SOURCE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/prefabs/game_base'
OUTPUT = ROOT / 'BetaGwent/ui/assets/beta-visuals'
WANTED = {
    -101: ('Texture2D', 'UI_HighlightFrameTexSprite'),
    -102: ('Texture2D', 'UI_HighlightGlow'),
    -103: ('Texture2D', 'Flare00'),
    -104: ('Texture2D', 'SmokePuff_p1'),
    -105: ('Texture2D', 'GoldSparkle'),
    -106: ('Texture2D', 'Streak'),
    -107: ('Sprite', 'card_selection_card_picker'),
    -108: ('Texture2D', 'LightNova1'),
    -201: ('Texture2D', 'SimpleCloud1_Alpha'),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def light_alpha(image):
    image = image.convert('RGBA')
    if image.getchannel('A').getextrema() != (255, 255):
        return image, 'original-alpha'
    pixels = []
    for r, g, b, _ in image.getdata():
        intensity = max(r, g, b)
        pixels.append((round(r * 255 / intensity), round(g * 255 / intensity),
                       round(b * 255 / intensity), intensity) if intensity else (0, 0, 0, 0))
    image.putdata(pixels)
    return image, 'additive-light-to-straight-alpha'

def sample_curve(keys, t):
    if t <= keys[0]['time']:
        return keys[0]['value']
    for a, b in zip(keys, keys[1:]):
        if t > b['time']:
            continue
        span = b['time'] - a['time']
        u = (t - a['time']) / span
        return (2*u**3-3*u**2+1)*a['value']+(u**3-2*u**2+u)*span*a['outSlope']+(-2*u**3+3*u**2)*b['value']+(u**3-u**2)*span*b['inSlope']
    return keys[-1]['value']

def weather_and_hit_frames():
    source = SOURCE.parents[4] / 'sharedassets8.assets'
    digest = sha(source)
    environment = UnityPy.load(str(source))
    objects = {obj.path_id: obj for obj in environment.objects}
    entries = []
    # IDs and sheet dimensions come from renderer material bindings and the
    # particle UVModule, rather than guesses based on the PNG dimensions.
    specs = [(716, -202, 1, 1), (657, -203, 1, 1), (713, -210, 2, 15),
             (645, -240, 1, 4), (550, -250, 2, 2)]
    for path_id, first, columns, rows in specs:
        obj = objects[path_id];assert obj.type.name == 'Texture2D'
        data = obj.read();image, conversion = light_alpha(data.image)
        for frame in range(columns * rows):
            col, row = frame % columns, rows-1-frame//columns
            box = (round(col*image.width/columns), round(row*image.height/rows),
                   round((col+1)*image.width/columns), round((row+1)*image.height/rows))
            tile = image.crop(box)
            ident = first-frame if columns*rows>1 else first
            target = OUTPUT / (str(ident) + '.png')
            tile.resize((128,180),Image.Resampling.LANCZOS).save(target)
            entries.append(dict(atlasId=ident, name=data.m_Name, type='Texture2D', pathId=path_id,
                source=str(source), sourceSha256=digest, frame=frame, sheet=[columns,rows], crop=list(box),
                thumbnail=str(target), thumbnailSha256=sha(target), conversion=conversion))
    fog = objects[2993].read_typetree()
    assert fog['UVModule']['tilesX']==2 and fog['UVModule']['tilesY']==15
    keys = fog['UVModule']['frameOverTime']['maxCurve']['m_Curve']
    lookup = [min(29,max(0,int(sample_curve(keys,i/119)*29.999))) for i in range(120)]
    durations = {}
    for obj in environment.objects:
        if obj.type.name == 'AnimationClip':
            data = obj.read()
            if data.m_Name in ('FogFadeInAnimation','FrostInitialAnim','RainInitialAnim'):
                clip = obj.read_typetree()['m_MuscleClip']
                durations[data.m_Name] = clip['m_StopTime']-clip['m_StartTime']
    assert len(durations)==3
    runtime = '''package {
    // Generated from Beta serialized clips and the Fog particle Hermite curve.
    public class BetaGwentVisualTimings {
        public static const FOG_LIFE:Number=FOG_LIFE_VALUE;
        public static const FOG_FRAMES:Array=[FOG_FRAME_VALUES];
        public static const FOG_INTRO:Number=FOG_INTRO_VALUE;
        public static const FROST_INTRO:Number=FROST_INTRO_VALUE;
        public static const RAIN_INTRO:Number=RAIN_INTRO_VALUE;
    }
}
'''.replace('FOG_LIFE_VALUE',str(fog['InitialModule']['startLifetime']['scalar']))
    runtime=runtime.replace('FOG_FRAME_VALUES',','.join(map(str,lookup)))
    for key, name in [('FOG','FogFadeInAnimation'),('FROST','FrostInitialAnim'),('RAIN','RainInitialAnim')]:
        runtime=runtime.replace(key+'_INTRO_VALUE',str(durations[name]))
    (ROOT/'BetaGwent/ui/src/BetaGwentVisualTimings.as').write_text(runtime,'utf8')
    assert sha(source)==digest
    return entries,dict(fogLifetime=fog['InitialModule']['startLifetime']['scalar'],fogCurve=keys,introDurations=durations)

def extract():
    source_paths = [SOURCE, SOURCE.parents[1] / 'spriteatlases/uber/cardpicker']
    source_hashes = {str(path): sha(path) for path in source_paths}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    environments = [(path, UnityPy.load(str(path))) for path in source_paths]
    wanted = {value: key for key, value in WANTED.items()}
    entries = []
    for path, obj in [(path, obj) for path, env in environments for obj in env.objects]:
        if obj.type.name not in ('Texture2D', 'Sprite'):
            continue
        data = obj.read()
        ident = wanted.get((obj.type.name, data.m_Name))
        if ident is None:
            continue
        if obj.type.name == 'Sprite' and path == SOURCE:
            continue  # Packed sprite resolves inside its owning atlas bundle.
        if any(item['atlasId'] == ident for item in entries):
            raise RuntimeError('Ambiguous original visual: ' + data.m_Name)
        image = data.image.convert('RGBA')
        original = OUTPUT / (data.m_Name + '.png')
        image.save(original)
        target = OUTPUT / (str(ident) + '.png')
        # Runtime restores aspect to each effect. Preserve alpha, including the
        # transparent centre of target frames; never flatten onto a dark canvas.
        image, conversion = light_alpha(image)
        if ident == -101:
            image = image.crop(image.getchannel('A').getbbox())
        image.resize((128, 180), Image.Resampling.LANCZOS).save(target)
        entries.append(dict(atlasId=ident, name=data.m_Name, type=obj.type.name,
                            pathId=obj.path_id, source=str(path), sourceSha256=source_hashes[str(path)],
                            original=str(original), originalSize=list(image.size),
                            thumbnail=str(target), thumbnailSha256=sha(target), conversion=conversion))
    entries.sort(key=lambda item: item['atlasId'], reverse=True)
    assert {item['atlasId'] for item in entries} == set(WANTED), 'Missing Beta visual'
    assert all(sha(Path(path)) == value for path, value in source_hashes.items()), 'Original bundle changed'
    sheet = Image.new('RGB', (4 * 240, ((len(entries)+3)//4) * 230), '#243340')
    draw = ImageDraw.Draw(sheet)
    for i, item in enumerate(entries):
        image = Image.open(item['original']).convert('RGBA')
        image.thumbnail((214, 184), Image.Resampling.LANCZOS)
        x, y = (i % 4) * 240, (i // 4) * 230
        sheet.paste(image, (x + 12, y + 8), image)
        draw.text((x + 8, y + 195), str(item['atlasId']) + ' ' + item['name'], fill='white')
    preview = ROOT / 'BetaGwent/ui/build/beta-visuals91.png'
    preview.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(preview)
    frames, timings = weather_and_hit_frames()
    entries.extend(frames)
    assert len({entry['atlasId'] for entry in entries}) == len(entries)
    report = dict(stage=91, sourceUnchanged=True, sprites=entries, timings=timings,
                  contactSheet=str(preview), policy='Original Beta art; GFx animation adapted separately')
    (ROOT / 'docs/evidence/beta-visuals91.json').write_text(json.dumps(report, indent=2) + '\n', 'utf8')
    return entries

if __name__ == '__main__':
    print('Extracted', len(extract()), 'original Beta visuals; original bundle unchanged.')
