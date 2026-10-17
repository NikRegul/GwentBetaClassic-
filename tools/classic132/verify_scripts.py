"""Verify emitted sources and untouched vanilla methods; not a compiler."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from prepare_scripts import class_span, extract_annotations, mask, member_span, read_source, sha


def class_members(text, target):
    opening, end = class_span(text, target)
    code = mask(text)
    depth, depth_at = 0, {}
    for i in range(opening + 1, end - 1):
        depth_at[i] = depth
        depth += (code[i] == '{') - (code[i] == '}')
    members = []
    for m in re.finditer(r'\b(function|event|var)\s+(\w+)', code[opening + 1:end - 1]):
        if depth_at[opening + 1 + m.start()] == 0:
            members.append((m[1], m[2]))
    return members


def verify(directory):
    report = json.loads((directory / 'preparation.json').read_text('utf8'))
    audit_path = Path(report['audit'])
    assert sha(audit_path) == report['auditSha256'], 'Audit changed'
    audit = json.loads(audit_path.read_text('utf8'))
    scripts = directory / 'Mods/modBetaGwentClassic132/content/scripts'
    actual = {p.relative_to(scripts).as_posix(): sha(p) for p in sorted(scripts.rglob('*.ws'))}
    assert actual == report['outputScripts'], 'Output files differ from preparation manifest'
    classes, texts, symbol_count = {}, {}, 0
    for relative in actual:
        p = scripts / relative
        raw = p.read_bytes()
        assert raw.startswith(b'\xff\xfe'), relative
        decoded = raw[2:].decode('utf-16le')
        assert '\n' not in decoded.replace('\r\n', ''), 'Non-CRLF newline: ' + relative
        text = read_source(p)
        texts[relative] = text
        code = mask(text)
        assert '@' not in code and not re.search(r'\bwrappedMethod\b', code), relative
        for name in re.findall(r'\bclass\s+(\w+)', code):
            assert name.lower() not in classes, 'Duplicate class: ' + name
            classes[name.lower()] = relative
            names = [('field' if kind == 'var' else 'method', member.lower())
                     for kind, member in class_members(text, name)]
            duplicates = [symbol for symbol, n in Counter(names).items() if n > 1]
            assert not duplicates, f'{name}: duplicate members {duplicates}'
            symbol_count += len(names)
    # Every renamed original helper must resolve within its target class.
    for wrapper in report['wrappers']:
        text = texts[classes[wrapper['target'].lower()]]
        member_span(text, wrapper['target'], wrapper['member'])
        member_span(text, wrapper['target'], wrapper['helper'])
        opening, end = class_span(text, wrapper['target'])
        assert len(re.findall(r'\b' + wrapper['helper'] + r'\s*\(', mask(text[opening:end]))) == 2, wrapper
    untouched, preserved_originals = 0, 0
    wrapped = {(x['target'], x['member']) for x in report['wrappers']}
    for relative in report['vanillaOverrides']:
        original = read_source(audit_path.parent / 'baseline/vanilla-targets' / relative)
        output = texts[relative]
        for name in re.findall(r'\bclass\s+(\w+)', mask(original)):
            for kind, member in class_members(original, name):
                if kind == 'var':
                    continue
                # Imported declarations have no implementation; never try to
                # confuse their next method's body with a native method body.
                try:
                    start, body, end, _ = member_span(original, name, member)
                except ValueError:
                    continue
                if (name, member) not in wrapped:
                    other_start, _, other_end, _ = member_span(output, name, member)
                    assert original[start:end].strip() == output[other_start:other_end].strip(), f'Untouched method changed: {name}.{member}'
                    untouched += 1
                else:
                    chain = [x for x in report['wrappers'] if (x['target'], x['member']) == (name, member)]
                    _, other_body, other_end, _ = member_span(output, name, chain[0]['helper'])
                    assert original[body:end] == output[other_body:other_end], f'Original body changed: {name}.{member}'
                    preserved_originals += 1
    result = dict(passed=True, scripts=len(actual), classes=len(classes), classMembers=symbol_count,
                  wrapperLayers=len(report['wrappers']), preservedOriginalBodies=preserved_originals,
                  unchangedVanillaMethods=untouched, nativeCompilationRun=False, runtimeVerified=False)
    (directory / 'static-verification.json').write_text(json.dumps(result, indent=2) + '\n', 'utf8')
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    verify(args.directory.resolve())
