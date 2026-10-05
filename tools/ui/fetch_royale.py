"""Extract only Apache Royale compiler libraries/config from official ZIP."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
NAME = 'apache-royale-0.9.12-bin-js-swf.zip'
URL = 'https://dlcdn.apache.org/royale/0.9.12/binaries/' + NAME
SUM_URL = 'https://downloads.apache.org/royale/0.9.12/binaries/' + NAME + '.sha512'
vendor = ROOT / 'tools/vendor'
archive = vendor / NAME
expected = urllib.request.urlopen(SUM_URL, timeout=30).read().decode().split()[0]
if not archive.exists():
    with urllib.request.urlopen(URL, timeout=60) as response, archive.open('wb') as out:
        while block := response.read(1024 * 1024): out.write(block)
data = archive.read_bytes()
if hashlib.sha512(data).hexdigest() != expected:
    raise SystemExit('SHA512 mismatch; will not extract')
destination = vendor / 'apache-royale-0.9.12'
destination.mkdir(exist_ok=True)
extracted = []
with zipfile.ZipFile(archive) as package:
    for entry in package.infolist():
        path = Path(entry.filename)
        # Libraries retain their relative layout for the compiler manifest classpath.
        # Framework libs and build/install scripts are unnecessary for this AS3 probe.
        keep = '/lib/' in entry.filename or path.name in ('LICENSE', 'NOTICE') or entry.filename.endswith('royale-config.xml')
        if not keep: continue
        target = (destination / path).resolve()
        if not target.is_relative_to(destination.resolve()): raise SystemExit('Unsafe ZIP path')
        package.extract(entry, destination)
        extracted.append(entry.filename)
compiler = list(destination.rglob('mxmlc.jar'))
report = dict(url=URL, checksumUrl=SUM_URL, publishedSha512=expected,
              sha256=hashlib.sha256(data).hexdigest(), archiveBytes=len(data),
              destination=str(destination), extractedFiles=len(extracted),
              compilerJars=[str(p) for p in compiler], thirdPartyInstallerRun=False,
              systemSettingsChanged=False)
(ROOT / 'docs/evidence/royale-sdk.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: report[k] for k in ('archiveBytes', 'extractedFiles', 'compilerJars')}))
