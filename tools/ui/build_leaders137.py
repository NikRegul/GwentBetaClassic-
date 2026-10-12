"""24fps full native leader loops; stream two one-second atlas pages per owner."""
import io
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageFile
import build_leaders136 as native

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT/'BetaGwent/build/leaders137'
CAPTURE = ROOT/'BetaGwent/build/leader-loops137'
DEPOT = 'gameplay/gui_new/swf/betagwentleaders'
WIDTH, HEIGHT = 192, 234
ATLAS = (WIDTH*6, HEIGHT*4)
ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, ATLAS[0]*ATLAS[1]*4)


def main():
    bindings = json.loads((ROOT/'BetaGwent/build/release060-preparation/leaders/BetaGwentLeaderCatalog.json').read_text('utf8'))
    native.WORK = WORK
    native.TARGET = WORK/'resources'/DEPOT
    WORK.mkdir(parents=True, exist_ok=True)
    template = native.compile_template(Image.new('RGB', ATLAS), Path(__file__).parent/'leaders060/BetaLeaderMovie137.as')
    reference, _ = native.validate_resource(ROOT/'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf')
    root, _ = reference.properties_at(reference.exports[0]['data'])
    texture, _ = reference.properties_at(reference.exports[1]['data'])
    imports = next(raw for code, p, raw in native.movie_parts(native.unpack_root(reference)[1])[1] if code == 1000)
    arts = {}
    resources = {}
    for art in sorted(set(bindings.values())):
        folder = CAPTURE/art
        meta = json.loads((folder/'complete.json').read_text('utf8'))
        assert meta['fullCycle'] and meta['loopOnly'] and meta['introExcluded'] and meta['fps'] == 24
        frames = sorted(folder.glob('*.png'))
        assert len(frames) == meta['frames'] and abs(meta['frames']-math.ceil(meta['duration']*24)) <= 1
        overlap = 8
        images = [Image.open(p).convert('RGB') for p in frames]
        blended = []
        for i in range(overlap):
            t = (i+1)/overlap
            blended.append(Image.blend(images[-overlap+i], images[i], t*t*(3-2*t)))
        pictures = images[overlap:-overlap]+blended
        duration = meta['duration']*len(pictures)/len(frames)
        rows = []
        for start in range(0, len(pictures), 24):
            atlas = Image.new('RGB', ATLAS)
            for n in range(24):
                # Padding repeats the last real frame, and is never displayed.
                image = pictures[min(start+n, len(pictures)-1)]
                assert image.size == (WIDTH, HEIGHT)
                atlas.paste(image, ((n%6)*WIDTH, (n//6)*HEIGHT))
            stream = io.BytesIO(); atlas.save(stream, format='DDS', pixel_format='DXT1')
            name = art+'_p'+str(start//24).zfill(3)
            report = native.native_movie(name, atlas, template, reference, root, texture, imports,
                                         dds=stream.getvalue(), portrait=(WIDTH, HEIGHT))
            resources[name] = report; rows.append(report)
        arts[art] = dict(frames=len(pictures), sourceFrames=meta['frames'], duration=duration,
                         nativeDuration=meta['duration'], seamOverlap=overlap, pages=len(rows), fps=24,
                         captureSha256=hashlib.sha256((folder/'complete.json').read_bytes()).hexdigest())
        print('Leader', art, meta['frames'], 'frames;', len(rows), 'pages', flush=True)
    source = ['package { public class BetaGwentLeaderCatalog {',
              'private static const ARTS:Object='+json.dumps(bindings, separators=(',', ':'))+';',
              'private static const LOOPS:Object='+json.dumps(arts, separators=(',', ':'))+';',
              'public static function info(id:int):Object {var art:String=ARTS[String(id)];if(!art)return null;var d:Object=LOOPS[art];return {art:art,frames:d.frames,duration:d.duration,pages:d.pages};}',
              'public static function path(id:int,page:int=0):String {var d:Object=info(id);if(!d||page<0||page>=d.pages)return null;var n:String=String(page);while(n.length<3)n="0"+n;return "swf/betagwentleaders/"+d.art+"_p"+n+".swf";}',
              '} }']
    (ROOT/'BetaGwent/ui/src/BetaGwentLeaderCatalog.as').write_text('\n'.join(source), 'utf8')
    expected = {name+'.redswf' for name in resources}
    for stale in native.TARGET.glob('*.redswf'):
        if stale.name not in expected:
            assert stale.resolve().is_relative_to((WORK/'resources'/DEPOT).resolve())
            stale.unlink()
    report = dict(stage=137, bindings=bindings, loops=arts, resources=resources, fps=24, fullCycles=True,
                  portrait=[WIDTH, HEIGHT], framesPerPage=24, maxOwners=4, maxPagesPerOwner=2,
                  maxResidentPagesIncludingRetired=12,
                  conservativeAtlasMemoryMiB=12*ATLAS[0]*ATLAS[1]*4.5/1024**2,
                  atlasSize=list(ATLAS), nativeRuntimeVerified=False)
    report['sources']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                       ('tools/ui/build_leaders137.py','tools/ui/leaders060/BetaLeaderMovie137.as')}
    report['engineOwnedAtlasReleasedByLoader']=True
    (ROOT/'docs/evidence/leaders137.json').write_text(json.dumps(report, indent=2)+'\n', 'utf8')


if __name__ == '__main__': main()
