"""Read embedded SWF commandlet usage without executing Wcc.

swfimport does not treat -help as a help-only invocation in this REDkit build.
The original runtime usage probe remains in build/swfimport-usage as evidence.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
TOOL = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe')
strings = [match.decode('ascii') for match in re.findall(rb'[\x20-\x7e]{5,}', TOOL.read_bytes())]
index = strings.index('Bulk import resources preserving directory structure')
end = next((i for i in range(index + 1, len(strings)) if strings[i].startswith('CTestCollision')), index + 10)
usage = strings[index:end]
out = ROOT / 'docs/evidence/wcc-swf-usage.json'
out.write_text(json.dumps(dict(source=str(TOOL), usage=usage, executableRun=False,
    note='Embedded strings; not proof of successful import or complete modern CLI API.'), indent=2), encoding='utf-8')
print('\n'.join(usage))
