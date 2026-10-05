"""Prepare board sources as UTF-8 BOM; preserve unexpected project edits."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
sources = list((ROOT / 'BetaGwent/scripts/game/betagwent').glob('*.ws'))
sources += list((ROOT / 'BetaGwent/development/scripts/game/betagwent').glob('*.ws'))
sources += [ROOT / 'tools/core-check/src/coreChecks.ws']
PATCH = ROOT / 'BetaGwent/build/board-patch/game/betagwent'
ACTIVE = ROOT / 'GwentB/myproject1/workspace/scripts/game/betagwent'
prepared = []
for source in sources:
    raw = source.read_bytes()
    text = raw.decode('utf-8-sig')  # Reject unknown encodings instead of guessing.
    encoded = b'\xef\xbb\xbf' + text.encode('utf-8')
    patch, active = PATCH / source.name, ACTIVE / source.name
    if active.exists():
        if not patch.exists() or active.read_bytes() != patch.read_bytes():
            raise SystemExit('Active project differs from previous prepared patch: ' + str(active))
    prepared.append((source, encoded))
# Validate the whole set before writing any target. Record source hashes so a
# later capture can distinguish a successful compile from a stale patch.
manifest = []
for source, encoded in prepared:
    for target in [source, PATCH / source.name, ACTIVE / source.name]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(encoded)
    manifest.append(dict(name=source.name, sha256=hashlib.sha256(encoded).hexdigest()))
(PATCH.parent.parent / 'prepared-sources.json').write_text(
    json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print(str(len(prepared)) + ' board sources prepared as UTF-8 BOM; capability probe untouched.')
