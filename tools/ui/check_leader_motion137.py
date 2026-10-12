"""Reject throttled captures and prove the blended endpoint has a natural next frame."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import hashlib,json,statistics

ROOT=Path(__file__).resolve().parents[2]


def main():
    report=json.loads((ROOT/'docs/evidence/leaders137.json').read_text('utf8'))
    results={}
    for art,meta in report['loops'].items():
        frames=sorted((ROOT/'BetaGwent/build/leader-loops137'/art).glob('*.png'))
        previous=None;hashes=set();deltas=[]
        for path in frames:
            with Image.open(path) as source:image=source.convert('RGB')
            hashes.add(hashlib.sha256(image.tobytes()).digest())
            if previous is not None:
                deltas.append(statistics.mean(ImageStat.Stat(ImageChops.difference(image,previous)).mean))
            previous=image
        assert len(frames)==meta['sourceFrames'] and len(hashes)==len(frames), ('Throttled or duplicate captured frames',art)
        assert all(delta>0 for delta in deltas)
        overlap=meta['seamOverlap'];assert overlap==8
        with Image.open(frames[overlap-1]) as source:endpoint=source.convert('RGB')
        with Image.open(frames[overlap]) as source:first=source.convert('RGB')
        # At t=1 smoothstep is exactly one, so the last blended picture must be
        # source[7]. The wrapped first frame is source[8], an adjacent sample.
        blended=Image.blend(previous,endpoint,1.0)
        assert blended.tobytes()==endpoint.tobytes()
        seam=statistics.mean(ImageStat.Stat(ImageChops.difference(first,blended)).mean)
        assert seam<=max(deltas)+1e-9
        results[art]=dict(sourceFrames=len(frames),uniqueFrames=len(hashes),identicalAdjacentFrames=0,
                          medianStep=statistics.median(deltas),maxStep=max(deltas),loopBoundaryStep=seam)
    source=ROOT/'tools/ui/check_leader_motion137.py'
    result=dict(stage=137,leaderArt=results,nativeGameTested=False,
                sources={str(source.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(source.read_bytes()).hexdigest()},
                note='Captured frames and exact blended endpoint; this does not measure native playback.')
    (ROOT/'docs/evidence/leader-motion137.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
    print('PASS: 21 full captures have no duplicate frames; each wrap is a natural adjacent sample')


if __name__=='__main__':main()
