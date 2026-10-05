"""Import one generated SWF into an isolated Wcc depot inside workspace."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'tools/ui/build'
TOOL = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe')
DEPOT = (BUILD / 'import-depot').resolve()
STAGE = (BUILD / 'import-input').resolve()
for directory in (DEPOT, STAGE):
    if not directory.is_relative_to(ROOT): raise SystemExit('Output outside workspace')
    directory.mkdir(exist_ok=True)
# CFlashImporter invokes GFxExport itself, so it needs the raw SWF, not GFx.
# Isolated input has one file and no texture dependencies.
input_path = STAGE / 'betagwent_ui_probe.swf'
shutil.copyfile(BUILD / 'betagwent_ui_probe.swf', input_path)
relative = r'gameplay\gui_new\swf\betagwent'
command = [str(TOOL), 'swfimport', '-depot=' + str(DEPOT) + '\\',
           '-fromAbsPath=' + str(STAGE) + '\\', '-toDepotPath=' + relative,
           '-wcclog=' + str(BUILD / 'import-wcc.log'), '-agreetoterms']
if sys.argv[1:] == ['--single']:
    command = [str(TOOL), 'import', '-depot=' + str(DEPOT) + '\\',
               '-file=' + str(input_path), '-out=' + relative + '\\betagwent_ui_probe.redswf',
               '-wcclog=' + str(BUILD / 'import-wcc.log'), '-agreetoterms']
elif sys.argv[1:]:
    raise SystemExit('Only --single is supported')
timed_out = False
with (BUILD / 'import-stdout.txt').open('wb') as stdout, (BUILD / 'import-stderr.txt').open('wb') as stderr:
    p = subprocess.Popen(command, cwd=TOOL.parent, stdin=subprocess.DEVNULL,
                         stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW)
    try: p.wait(timeout=45)
    except subprocess.TimeoutExpired:
        timed_out=True; p.kill(); p.wait(timeout=5)
output = DEPOT / relative / 'betagwent_ui_probe.redswf'
artifacts = []
if output.exists():
    blob = output.read_bytes()
    artifacts.append(dict(path=str(output), bytes=len(blob), sha256=hashlib.sha256(blob).hexdigest(),
                          cr2w=blob[:4] == b'CR2W', swfPayloadContainsGFx=(BUILD / 'betagwent_ui_probe.gfx').read_bytes() in blob))
report = dict(command=command, exitCode=p.returncode, timedOut=timed_out,
              sandboxDepot=str(DEPOT), inputSha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
              artifacts=artifacts, humanPriorWccLicenseAcceptance=True,
              imported=bool(artifacts) and p.returncode == 0 and not timed_out,
              nativeMenuRegistered=False, runtimeVerified=False)
(ROOT / 'docs/evidence/ui-probe-import.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
raise SystemExit(0 if report['imported'] else 1)
