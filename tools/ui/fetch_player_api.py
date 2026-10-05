"""Fetch Apache Royale's open source player API typedefs, not a Flash runtime."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://repo.maven.apache.org/maven2/org/apache/royale/typedefs/royale-typedefs-playerglobal/0.9.12/'
NAME = 'royale-typedefs-playerglobal-0.9.12'
destination = ROOT / 'tools/vendor/royale-player-api-0.9.12'
destination.mkdir(exist_ok=True)
artifacts = []
for suffix in ('-swf.swc', '-sources.jar', '.pom'):
    url = BASE + NAME + suffix
    expected = urllib.request.urlopen(url + '.sha1', timeout=30).read().decode().strip()
    path = destination / (NAME + suffix)
    if not path.exists():
        path.write_bytes(urllib.request.urlopen(url, timeout=30).read())
    data = path.read_bytes()
    if hashlib.sha1(data).hexdigest() != expected:
        raise SystemExit('Checksum mismatch: ' + path.name)
    artifacts.append(dict(url=url, path=str(path), bytes=len(data), publishedSha1=expected,
                          sha256=hashlib.sha256(data).hexdigest()))
with zipfile.ZipFile(destination / (NAME + '-sources.jar')) as archive:
    for name in archive.namelist():
        if name.endswith(('LICENSE', 'NOTICE')):
            (destination / Path(name).name).write_bytes(archive.read(name))
with zipfile.ZipFile(destination / (NAME + '-swf.swc')) as archive:
    catalog = archive.read('catalog.xml').decode('utf-8')
    required = ['flash.display:Sprite', 'flash.text:TextField', 'flash.external:ExternalInterface']
    missing = [name for name in required if name not in catalog]
    if missing:
        raise SystemExit('Missing API: ' + ','.join(missing))
(ROOT / 'docs/evidence/player-api.json').write_text(json.dumps(dict(
    project='https://github.com/apache/royale-typedefs', artifacts=artifacts,
    role='Compile-time external definitions only. No Flash Player installation.',
    requiredApiPresent=True, systemSettingsChanged=False,
    verification='Official Maven HTTPS and published SHA1 checksums; PGP not verified'), indent=2), encoding='utf-8')
print('Player API downloaded and checked; SWC 183378 bytes expected.')
