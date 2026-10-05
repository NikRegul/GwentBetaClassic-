"""Check the actual compiled ABC receiver, not just the ActionScript spelling.

Royale 0.9.12 compiles an unqualified Function-slot invocation with
getglobalscope as receiver. GFx rejects that receiver in CallGameEvent.
This check saves only the relevant methods, excluding embedded image data.
It does not claim the repaired SWF has been imported or run in REDkit.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import argparse

ROOT = Path(__file__).resolve().parents[2]
SWF = ROOT / 'BetaGwent/ui/build/betagwent_board.swf'
DUMPER = ROOT / 'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/compiler-swfdump.jar'


def extract_methods(dump):
    dump = dump.replace('\r\n', '\n')
    methods = {}
    for name in ('waitForBridge', 'send'):
        match = re.search(r'^  private function ' + name + r'\([^\n]+\n  \{\n.*?^  \}', dump, re.M | re.S)
        if not match:
            raise RuntimeError('Missing compiled bridge method: ' + name)
        methods[name] = match.group()
    return methods


def main():
    global SWF
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entry',choices=['BetaGwentBoard','DeckBuilder','GwintGame'],default='BetaGwentBoard')
    args=parser.parse_args()
    stem,root={'BetaGwentBoard':('betagwent_board','BetaGwentBoard'),'DeckBuilder':('betagwent_decks','BetaGwentDeckMenu'),'GwintGame':('betagwent_npc00','BetaGwentNpcMenu')}[args.entry]
    SWF=SWF.with_name(stem+'.swf')
    result = subprocess.run([shutil.which('java'), '-jar', str(DUMPER), '-abc', str(SWF)],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            creationflags=subprocess.CREATE_NO_WINDOW, timeout=30)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', errors='replace'))
    dump = result.stdout.decode('utf-8', errors='replace').replace('\r\n','\n')
    methods = extract_methods(dump)
    script = (ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws').read_text(encoding='utf-8-sig')
    bindings = sorted(set(re.findall(r'GetMemberFlashFunction\("([^"]+)"\)', script)))
    missing_bindings = [name for name in bindings if not re.search(r'public function ' + re.escape(name) + r'\(', dump)]
    variables = dict(re.findall(r'(\w+)\s*=\s*GetMenuFlash\(\)\.GetMemberFlashFunction\("([^"]+)"\)', script))
    numbers = dict(One=1, Two=2, Three=3, Four=4, Five=5, Six=6, Seven=7, Eight=8, Nine=9)
    arity_mismatches = []
    for variable, word in re.findall(r'(\w+)\.InvokeSelf(One|Two|Three|Four|Five|Six|Seven|Eight|Nine)Arg[s]?\(', script):
        if variable not in variables:
            continue
        name = variables[variable]
        signature = re.search(r'public function ' + re.escape(name) + r'\(([^)]*)\)', dump)
        if signature:
            count = len(signature[1].split(',')) if signature[1].strip() else 0
            if count != numbers[word]:
                arity_mismatches.append(dict(function=name, scriptArguments=numbers[word], compiledParameters=count))
    send = methods['send']
    # getlex nativeFunction; getlocal0 (this); getlocal1/2 (event/args);
    # callpropvoid (Function.call). This is the exact compiler output fixed here.
    checks = dict(
        exactRegistrationName=bool(re.search(r'protected (?:override )?function registrationName\([^\n]*\n  \{[^}]*pushstring\s+"'+re.escape(args.entry)+r'"',dump,re.S)),
        allScriptBindingsPresent=not missing_bindings,
        scriptInvocationArityMatchesABC=not arity_mismatches,
        handshakeUsesSharedSender=bool(re.search(r'findpropstrict\s+send\s', methods['waitForBridge'])),
        nativeFunctionReceivesThis=bool(re.search(
            r'getlex\s+_NATIVE_callGameEvent\s+\d+\s+getlocal0\s+\d+\s+getlocal1\s+\d+\s+getlocal2\s+\d+\s+callpropvoid', send)),
        noGlobalReceiver=all('getglobalscope' not in method for method in methods.values()),
        controllerLinked=bool(re.search(r'public class BetaGwentController extends flash.display::Sprite',dump)),
        scaleformInputTypesLinked=all(re.search(r'public final class scaleform.gfx::'+name+r' extends ',dump)
                                    for name in ('Extensions','GamePad','GamePadAnalogEvent','KeyboardEventEx')),
    )
    report = dict(swf=str(SWF), bytes=SWF.stat().st_size,
                  sha256=hashlib.sha256(SWF.read_bytes()).hexdigest(), checks=checks, bindings=bindings, missingBindings=missing_bindings,
                  arityMismatches=arity_mismatches,
                  passed=all(checks.values()), nativeRuntimeVerified=False,
                  note='Compiled ABC check only; native reimport and runtime are pending.')
    evidence = ROOT / 'docs/evidence'
    trace = '\n\n'.join(methods.values())
    suffix='' if args.entry=='BetaGwentBoard' else '-'+args.entry
    (evidence / ('board-bridge-after-abc'+suffix+'.txt')).write_text('\n'.join(line.rstrip() for line in trace.splitlines()) + '\n', encoding='utf-8')
    (evidence / ('board-bridge-bytecode'+suffix+'.json')).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
