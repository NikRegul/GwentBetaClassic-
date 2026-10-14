"""Original Beta shop keg sprite and its native inventory binding.

Extraction is explicit; normal source builds validate the committed PNG without
requiring UnityPy or the original client. Native texture caching happens in the
language package's cook phase, separately from the inline battle GUI textures.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ICON_PATH = 'icons/inventory/betagwent/ico_betagwent_keg.png'
DEPOT_PATH = 'gameplay/gui_new/' + ICON_PATH
ASSET = ROOT/'BetaGwent/ui/assets/shop161/keg-beta-original.png'
MANIFEST = ASSET.with_suffix('.json')
WORK = ROOT/'GwentB/myproject1/workspace'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract():
    sys.path.insert(0, str(ROOT/'tools/vendor/audio-python'))
    import UnityPy
    source = ROOT/'Gwent 0.9.24.3.432/Gwent_Data/resources.assets'
    unity = UnityPy.load(str(source))
    sprite = next(o for o in unity.objects if o.path_id == 1594).read()
    assert sprite.m_Name == 'Keg' and sprite.m_RD.texture.path_id == 136
    # Unity's extracted sprite is trimmed. Restore its original 64px canvas
    # using the atlas offset, rather than stretching this small original asset.
    cropped = sprite.image.convert('RGBA')
    width, height = int(sprite.m_Rect.width), int(sprite.m_Rect.height)
    x = round(sprite.m_RD.textureRectOffset.x)
    y = height - round(sprite.m_RD.textureRectOffset.y) - cropped.height
    image = Image.new('RGBA', (width, height))
    image.paste(cropped, (x, y))
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    image.save(ASSET)
    MANIFEST.write_text(json.dumps(dict(
        client='Gwent Beta 0.9.24.3.432', source=source.relative_to(ROOT).as_posix(),
        sourceSha256=sha(source), spritePathId=1594, spriteName='Keg',
        texturePathId=136, originalCanvas=[width, height], trimmedSize=list(cropped.size),
        restoredOffset=[x, y], resampled=False, pngSha256=sha(ASSET),
        pixelsSha256=hashlib.sha256(image.tobytes()).hexdigest(),
        inventoryIconPath=ICON_PATH, depotPath=DEPOT_PATH,
        nativeRuntimeVerified=False), indent=2)+'\n', 'utf8')
    destination = WORK/DEPOT_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(ASSET.read_bytes())


def validate(workspace=WORK):
    manifest = json.loads(MANIFEST.read_text('utf8'))
    assert sha(ASSET) == manifest['pngSha256'], 'Keg original asset changed'
    with Image.open(ASSET) as icon:
        assert icon.mode == 'RGBA' and icon.size == (64, 64)
        assert hashlib.sha256(icon.tobytes()).hexdigest() == manifest['pixelsSha256']
        assert icon.getextrema()[3][0] == 0 and icon.getextrema()[3][1] == 255
    assert (workspace/DEPOT_PATH).read_bytes() == ASSET.read_bytes(), 'Stale shop keg icon'
    items = ET.parse(workspace/'gameplay/items/betagwent_shop.xml')
    kegs = [item for item in items.iter('item') if item.get('name') == 'betagwent_keg']
    assert len(kegs) == 1 and kegs[0].get('icon_path') == ICON_PATH, 'Missing keg icon binding'
    return dict(icon=DEPOT_PATH, sha256=sha(ASSET), size=[64,64], originalBetaSprite=True,
                sourceAndBindingVerified=True, nativeRuntimeVerified=False)


def prepare_cache():
    """Cook only this icon: do not externalize the board's inline textures."""
    binding = validate()
    base = ROOT/'BetaGwent/build/shop161'
    base.mkdir(parents=True, exist_ok=True)
    report_path = base/'cache.json'
    if report_path.exists():
        report = json.loads(report_path.read_text('utf8'))
        cache = Path(report['cache'])
        if report['iconSha256'] == binding['sha256'] and cache.exists() and sha(cache) == report['cacheSha256']:
            return report
    run = Path(tempfile.mkdtemp(prefix='native-', dir=base))
    roots = run/'input'
    icon = roots/DEPOT_PATH
    icon.parent.mkdir(parents=True)
    shutil.copyfile(ASSET, icon)
    cooked = run/'cooked'
    database = cooked/'cook.db'
    cache = run/'texture.cache'
    runner = ROOT/'tools/recon/run_wcc_job.py'
    project = run/'project'
    project.mkdir()
    baseline = ROOT/'BetaGwent/build/release87/project/BetaGwent0924'
    for name in ('myproject1.w3edit', 'LocalEditorStringDataBaseW3_UTF8_mod.db'):
        shutil.copyfile(baseline/name, project/name)
    mounted_icon = project/'workspace'/DEPOT_PATH
    mounted_icon.parent.mkdir(parents=True)
    shutil.copyfile(ASSET, mounted_icon)
    common = ['-uncookDir', str(ROOT/'depot')+'\\', '-workspaceDir', str(project)+'\\']
    def native(label, arguments, expected):
        subprocess.run([sys.executable, '-X', 'utf8', str(runner), '--out', str(run/'jobs'/label),
                        '--timeout', '180', '--expect', str(expected), '--', *arguments, *common],
                       cwd=ROOT, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    native('cook', ['cook', '-platform=pc', '-mod='+str(roots)+'\\',
                    '-outdir='+str(cooked)+'\\'], database)
    entries = json.loads(database.read_text('utf8'))['files']
    assert any(entry['path'].replace('\\','/') == DEPOT_PATH for entry in entries), 'Icon missing from cook.db'
    native('textures', ['buildcache', 'textures', '-platform=pc', '-db='+str(database),
                        '-out='+str(cache)], cache)
    assert cache.stat().st_size > 128, 'Empty inventory texture cache'
    report = dict(icon=DEPOT_PATH, iconSha256=binding['sha256'], cache=str(cache),
                  cacheSha256=sha(cache), bytes=cache.stat().st_size, cookDatabase=str(database),
                  nativeCookAndCacheCompleted=True, nativeRuntimeVerified=False)
    report_path.write_text(json.dumps(report, indent=2)+'\n', 'utf8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--extract', action='store_true')
    parser.add_argument('--workspace', type=Path, default=WORK)
    parser.add_argument('--prepare-cache', action='store_true')
    args = parser.parse_args()
    if args.extract:
        extract()
    print(json.dumps(prepare_cache() if args.prepare_cache else validate(args.workspace), indent=2))
