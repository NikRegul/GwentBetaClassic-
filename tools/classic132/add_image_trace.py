"""Add audited Classic image-binding points to the complete trace manifest."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / 'BetaGwent/build/classic081-complete-audit'
sys.path.insert(0, str(AUDIT / 'python-tools'))
import pefile

POINTS = {
    'GFX_IMAGE_FILE': 0x689c50,
    'GFX_IMAGE_BINDING': 0x689f20,
    'GFX_IMAGE_TEXTURE': 0x68a087,
    'GFX_IMAGE_CREATED': 0x68a0b1,
    'GFX_TEXTURE_LOOKUP_RESULT': 0x6890d6,
    'GFX_IMAGE_FILE_CREATED': 0x68a35f,
}


def main():
    path = AUDIT / 'all-trace-points.json'
    manifest = json.loads(path.read_text('utf8'))
    exe = Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt/bin/x64/witcher3.exe').read_bytes()
    assert hashlib.sha256(exe).hexdigest() == manifest['executableSha256']
    pe = pefile.PE(data=exe, fast_load=True)
    for name, rva in POINTS.items():
        row = dict(name=name, rva=rva, signature=pe.get_data(rva, 8).hex(),
                   purpose='Late UI image binding diagnosis')
        previous = next((p for p in manifest['points'] if p['name'] == name), None)
        if previous:
            assert previous == row
        else:
            assert not any(p['rva'] == rva for p in manifest['points'])
            manifest['points'].append(row)
    path.write_text(json.dumps(manifest, indent=2), 'utf8')
    print('Verified image-binding points:', len(POINTS), 'total points:', len(manifest['points']))


if __name__ == '__main__':
    main()
