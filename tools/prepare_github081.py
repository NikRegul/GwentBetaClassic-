"""Publish the accepted 0.8.1 source snapshot, keeping 0.8.2 work separate."""
import hashlib
import json
from pathlib import Path
import shutil
import prepare_github138 as legacy

ROOT = Path(__file__).resolve().parents[1]
OUT = legacy.OUT


def main():
    legacy.EXCLUDE.add('features082')
    legacy.main()
    # These are the actual accepted 0.8.1 inputs. Canonical WS/UI already carry
    # draft 0.8.2 features, so do not publish them as the 0.8.1 runtime sources.
    origins = [
        (ROOT/'BetaGwent/build/universal081/nextgen-sources/game', OUT/'BetaGwent/development/scripts/game'),
        (ROOT/'BetaGwent/build/universal081/ui/src', OUT/'BetaGwent/ui/src'),
        (ROOT/'BetaGwent/build/classic081-effect-routes-fix18/ui/src', OUT/'BetaGwent/platforms/classic132/ui/src'),
        (ROOT/'BetaGwent/build/universal081/classic-prepared/Mods/modBetaGwentClassic132/content/scripts', OUT/'BetaGwent/platforms/classic132/scripts'),
    ]
    records = []
    for source, target in origins:
        assert source.is_dir(), str(source)
        for p in sorted(source.rglob('*')):
            if not p.is_file() or p.suffix not in ('.as', '.ws'):
                continue
            dest = target/p.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dest)
            records.append(dict(path=dest.relative_to(OUT).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    report=dict(version='0.8.1',classicAcceptedByUser=True,classicCandidate='fix18',
        sourceOnly=True,checkout=str(OUT),runtimeSources=records,assetsExcluded=True,pushed=False)
    (ROOT/'docs/evidence/github081-preparation.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    (OUT/'docs/evidence/github081-sources.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='runtimeSources'}))


if __name__=='__main__':main()
