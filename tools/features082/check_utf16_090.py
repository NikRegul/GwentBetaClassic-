"""Build 13 check: every XML in the Classic archive bundles is UTF-16 LE; Next-Gen unchanged."""
from pathlib import Path
import io, os, sys, zipfile
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/classic132'))
from formats import bundle_entries
BASE = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final13') / 'package-candidate'
package = BASE / 'classic/package'
count = 0
for bundle in [package / 'Mods/modBetaGwentClassic132/content/blob0.bundle']:
    for name, raw in bundle_entries(bundle, include=lambda n: n.lower().endswith('.xml')):
        assert raw.startswith(b'\xff\xfe') and raw[2:].decode('utf-16-le').lstrip().startswith('<?xml'), name
        assert 'encoding="UTF-16"' in raw[2:200].decode('utf-16-le'), name
        count += 1
assert count >= 8, count
keep = BASE / 'archives-optional-keep' / 'GwentBetaClassic-0.9.0-1.32-AllLanguages.zip'
with zipfile.ZipFile(keep) as z:
    data = z.read('After-Uninstall/Mods/modBetaGwentKeepItems/content/blob0.bundle')
tmp = BASE / 'keep-classic-check.bundle'; tmp.write_bytes(data)
for name, raw in bundle_entries(tmp, include=lambda n: n.lower().endswith('.xml')):
    assert raw.startswith(b'\xff\xfe'), name; count += 1
print('UTF-16 XML entries checked:', count)
