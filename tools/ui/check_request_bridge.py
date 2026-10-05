"""Inspect compiled request protocol and captured callback context, not native execution."""
import hashlib
import json
import re
import shutil
import subprocess
from check_board_bridge import ROOT, SWF, DUMPER


def main():
    result = subprocess.run([shutil.which('java'), '-jar', str(DUMPER), '-abc', str(SWF)],
                            capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))
    dump = result.stdout.decode('utf-8', errors='replace').replace('\r\n', '\n')
    methods = {}
    for name in ('setRequestHeader', 'pushRequestCard', 'sendRequest', 'requestAction', 'attachRequestCard'):
        match = re.search(r'^  (?:public|private) function ' + name + r'\([^\n]+\n  \{\n.*?^  \}', dump, re.M | re.S)
        if not match:
            raise RuntimeError('Missing compiled method: ' + name)
        methods[name] = match.group()
    request_action = methods['requestAction']
    sender = methods['sendRequest']
    checks = {
        'headerNineArguments': 'setRequestHeader(int,int,int,int,int,int,int,Boolean,String)' in methods['setRequestHeader'],
        'viewSixArguments': 'pushRequestCard(int,String,int,int,Boolean,Boolean)' in methods['pushRequestCard'],
        'contextCapturedInActivation': 'newactivation' in request_action and all(
            'internal var ' + name + ':int' in request_action
            for name in ('expectedRevision', 'expectedRequest', 'expectedPlayer', 'expectedKind')),
        'wireIncludesFourContextValues': bool(re.search(
            r'getlex\s+revision\s+\d+\s+getlex\s+requestId\s+\d+\s+getlex\s+requestPlayer\s+\d+\s+getlex\s+requestKind\s+\d+\s+newarray\s+4', sender)),
        'selectionDiscriminated': 'OnBetaGwentRequestSelect' in sender,
        'waitsForAuthoritativeSnapshot': bool(re.search(r'pushfalse\s+\d+\s+findproperty\s+ready\s+\d+\s+swap\s+\d+\s+setproperty\s+ready', sender)),
        'usesBoundSharedSender': bool(re.search(r'findpropstrict\s+send\s', sender)),
        'cardHandlerCapturesRequestContext': bool(re.search(r'findpropstrict\s+requestAction\s', methods['attachRequestCard'])),
    }
    evidence = ROOT / 'docs/evidence'
    (evidence / 'request-bridge-abc.txt').write_text('\n\n'.join(methods.values()) + '\n', encoding='utf-8')
    report = {'swf': str(SWF), 'sha256': hashlib.sha256(SWF.read_bytes()).hexdigest(),
              'checks': checks, 'passed': all(checks.values()), 'nativeRuntimeVerified': False,
              'scope': 'Compiled method signatures, request context capture and wire construction only. No executed AS3/native interaction.'}
    (evidence / 'request-bridge-bytecode.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
