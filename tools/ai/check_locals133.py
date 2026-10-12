"""Reject the local-declaration order accepted by JS but rejected by REDkit."""
import json
from pathlib import Path
from ws2js import Parser, lex

ROOT = Path(__file__).resolve().parents[2]
checks = 0

def parse(source):
    return Parser(lex(source), set()).decl()

for source in (
    'function F() : int { var x : int; var y : int; x=1; return x; }',
    'function F() : int { /* comment */ var x : int; return 0; }',
    'function F() : int { return 0; }',
):
    parse(source)
    checks += 1

for source in (
    'function F() : int { if(true)return 0; var damage : int; return damage; }',
    'function F() : int { var x : int; x=1; var y : int; return x; }',
):
    try:
        parse(source)
    except SyntaxError as error:
        assert 'locals must precede' in str(error)
        checks += 1
    else:
        raise AssertionError('Invalid native local order accepted by JS translator')

report = dict(stage=133, checks=checks, invalidNativeLocalsRejected=True)
(ROOT/'docs/evidence/locals133.json').write_text(json.dumps(report, indent=2)+'\n', 'utf8')
print(json.dumps(report))
