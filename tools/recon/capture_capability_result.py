"""Record human-run capability results separately from direct log evidence."""
from pathlib import Path
import hashlib
import json
import shutil
import collections
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/evidence'
image_source = Path(r'C:\Users\NikR\AppData\Local\Temp\codex-clipboard-d281e794-7440-446c-a7c1-bcbbeee4d1de.png')
image_target = OUT / 'capability-gwent-ended-breakpoint.png'
shutil.copy2(image_source, image_target)
logs = []
editor_lines = []
for name in ['editor.log', 'scriptstudio.log']:
    path = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin') / name
    data = path.read_bytes()
    lines = data.decode('utf-8', errors='replace').splitlines()
    probes = [line for line in lines if 'PROBE_' in line or 'BetaGwent' in line]
    if name == 'editor.log':
        editor_lines = lines
    logs.append({'path': str(path), 'bytes': len(data),
                 'sha256': hashlib.sha256(data).hexdigest().upper(),
                 'probeLines': probes})
report = {
    'date': '2026-10-01',
    'humanStatement': 'все проверил, все ок; логи смотри сам',
    'commandExecution': 'verified by earlier runtime screenshot',
    'saveRoundTrip': 'See timeline validation below',
    'gwentRequestHook': 'Two PROBE_GWENT_REQUEST log entries, deck NilfPrologue',
    'gwentEndHook': 'breakpoint hit observed in screenshot, execution marker at line 66',
    'winLossQuit': 'passed according to human report; exact outcome values not captured',
    'existingStarterFlashBridge': 'Human reported checklist passed; no PROBE_UI_SET_STARTER captured. This branch is not independently confirmed.',
    'newSwfAuthoring': 'not tested by this probe',
    'screenshot': {'path': str(image_target),
                   'sha256': hashlib.sha256(image_target.read_bytes()).hexdigest().upper()},
    'logsAtCapture': logs,
    'logReview': 'Runtime files were initially empty and later became readable while applications were still running. The nonempty snapshot is used here. Engine/resource errors exist; this is not an error-free whole-editor validation.',
    'saveFiles': []}
timeline_keys = ['PROBE_', 'Saving session dump', 'OnSaveCompleted', 'OnLoadGameCalled']
timeline = [{'line': i + 1, 'text': line} for i, line in enumerate(editor_lines)
            if any(key in line for key in timeline_keys)]
report['timeline'] = timeline
loads = [i for i, line in enumerate(editor_lines) if 'OnLoadGameCalled( SGT_Manual' in line]
post_load_reads = [i for i, line in enumerate(editor_lines)
                   if 'PROBE_READ schema=1 counter=18 ids=2 valid=true' in line
                   and any(load < i for load in loads)]
verified = False
for index in post_load_reads:
    load = max(i for i in loads if i < index)
    completed_save = any('OnSaveCompleted SGT_Manual true' in line for line in editor_lines[:load])
    no_reseed = not any('PROBE_SEEDED' in line for line in editor_lines[load:index])
    if completed_save and no_reseed:
        verified = True
report['saveRoundTrip'] = ('Verified: manual save completed, manual load invoked, subsequent read counter18 and both IDs valid; no reseed between load and read.'
                           if verified else 'User reported passed; ordered save/load/read evidence not found.')
report['saveLoadLogVerified'] = verified
report['endStates'] = [line.split('PROBE_GWENT_ENDED state=', 1)[1]
                       for line in editor_lines if 'PROBE_GWENT_ENDED state=' in line]
report['starterBridgeLogVerified'] = any('PROBE_UI_SET_STARTER' in line for line in editor_lines)
report['outcomeLimitation'] = 'One end state has an empty enum string. Vanilla forfeit uses combined Lost|Forfeited flags; that is a possible explanation, not a verified outcome for this entry. Plain loss has no explicit log entry.'
errors = [line for line in editor_lines if '[Error]' in line]
report['errorLineCount'] = len(errors)
report['probeReferencedErrorLines'] = [line for line in errors if 'capabilityProbe' in line or 'BetaGwent' in line]
families = collections.Counter(re.sub(r"'[^']*'", "'<value>'",
                             re.sub(r'0x[0-9a-fA-F]+', '<addr>', line.split(']', 3)[-1].strip()))
                             for line in errors)
report['mostCommonErrorFamilies'] = [{'count': count, 'message': message}
                                     for message, count in families.most_common(10)]
(OUT / 'capability-runtime-trace.txt').write_text(
    '\n'.join(str(item['line']) + ': ' + item['text'] for item in timeline) + '\n', encoding='utf-8')
saves = Path(r'C:\Users\NikR\Documents\The Witcher 3\gamesaves')
for path in saves.glob('*.sav'):
    # Metadata only: a new save exists, but its contents are not decoded.
    import datetime
    modified = datetime.datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    if modified.date().isoformat() == '2026-10-01':
        report['saveFiles'].append({'path': str(path), 'bytes': path.stat().st_size,
                                    'lastWriteTime': modified.isoformat()})
(OUT / 'capability-runtime-result.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'runtimeLogBytes': [log['bytes'] for log in logs],
                  'sameDaySaveFiles': len(report['saveFiles']),
                  'evidence': str(OUT / 'capability-runtime-result.json')}, ensure_ascii=False))
