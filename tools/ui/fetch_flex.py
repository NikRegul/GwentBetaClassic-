"""Download/unpack the Apache Flex compiler locally; no system installer.

No third-party download/acceptance scripts are invoked. Player API dependency
is checked separately when building the UI probe.
"""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
URL = 'https://dlcdn.apache.org/flex/4.16.1/binaries/apache-flex-sdk-4.16.1-bin.zip'
EXPECTED_MD5 = '8841c64bd5e32f8575eba86e2574873a'
vendor = ROOT / 'tools/vendor'
vendor.mkdir(exist_ok=True)
archive = vendor / 'apache-flex-sdk-4.16.1-bin.zip'
if not archive.exists():
    with urllib.request.urlopen(URL, timeout=60) as response, archive.open('wb') as out:
        while block := response.read(1024 * 1024):
            out.write(block)
blob = archive.read_bytes()
if hashlib.md5(blob).hexdigest() != EXPECTED_MD5:
    raise SystemExit('Archive integrity mismatch: will not extract')
destination = vendor / 'apache-flex-4.16.1'
destination.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as package:
    for entry in package.infolist():
        resolved = (destination / entry.filename).resolve()
        if not resolved.is_relative_to(destination.resolve()):
            raise SystemExit('Archive path outside SDK directory')
    package.extractall(destination)
report = dict(url=URL, publishedMd5=EXPECTED_MD5,
              checksumSource='https://downloads.apache.org/flex/4.16.1/binaries/apache-flex-sdk-4.16.1-bin.zip.md5',
              sha256=hashlib.sha256(blob).hexdigest(), archiveBytes=len(blob),
              sdk=str(destination), compilerJar=str(destination / 'lib/mxmlc.jar'),
              compilerPresent=(destination / 'lib/mxmlc.jar').exists(),
              playerglobalFiles=[str(p) for p in destination.rglob('*playerglobal*.swc')],
              thirdPartyInstallerRun=False, systemSettingsChanged=False,
              verification='HTTPS official distribution and matching published MD5; PGP signature not verified')
(ROOT / 'docs/evidence/flex-sdk.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ('archiveBytes','compilerPresent','playerglobalFiles')}))
