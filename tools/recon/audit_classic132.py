"""Inventory a Classic installation and freeze a released script baseline.

Reads the game only. Does not compile, install, launch, or accept SDK terms.
Annotation target checks are static evidence, not compiler compatibility.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def mask(text):
    # Preserve positions and newlines while hiding braces in comments/strings.
    return re.sub(r'//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), text)


def classes(scripts):
    index = {}
    for path in sorted(scripts.rglob('*.ws')):
        text = path.read_text('utf-8-sig', errors='replace')
        code = mask(text)
        for match in re.finditer(r'\bclass\s+(\w+)(?:\s+extends\s+(\w+))?[^{};]*\{', code):
            start = match.end()
            depth, end = 1, start
            while end < len(code) and depth:
                depth += (code[end] == '{') - (code[end] == '}')
                end += 1
            if depth:
                raise ValueError('Unclosed class: ' + str(path))
            methods = {}
            for method in re.finditer(r'\b(?:function|event)\s+(\w+)\s*\([^)]*\)(?:\s*:\s*\w+)?', code[start:end - 1]):
                methods[method[1]] = ' '.join(text[start + method.start():start + method.end()].split())
            name = match[1]
            if name in index:
                raise ValueError('Ambiguous class: ' + name)
            index[name] = dict(path=path.relative_to(scripts).as_posix(),
                               parent=match[2], methods=methods)
    return index


def lookup(index, target, member):
    seen = set()
    while target in index and target not in seen:
        seen.add(target)
        definition = index[target]
        if member in definition['methods']:
            return dict(owner=target, path=definition['path'], signature=definition['methods'][member])
        target = definition['parent']
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--source-stage', type=int, default=187)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    game, out = args.game.resolve(), args.out.resolve()
    build_root = (ROOT / 'BetaGwent/build').resolve()
    if not out.is_relative_to(build_root) or out == build_root:
        parser.error('Output must be a fresh subdirectory of BetaGwent/build')
    if out.exists():
        parser.error('Output already exists; select a fresh directory')
    exe = game / 'bin/x64/witcher3.exe'
    base = game / 'content/content0/scripts'
    source = ROOT / f'BetaGwent/build/stage{args.source_stage}/ru/sources/scripts'
    if not exe.is_file() or not base.is_dir() or not source.is_dir():
        parser.error('Game executable, loose vanilla scripts and frozen stage scripts are required')
    versions = sorted(set(m.decode('ascii') for m in re.findall(rb'\bv 1\.\d{2}\b', exe.read_bytes())))
    if versions != ['v 1.32']:
        parser.error('Expected an unambiguous v 1.32 marker: ' + repr(versions))
    index = classes(base)
    sources = list(sorted(source.rglob('*.ws')))
    stage_report = json.loads((ROOT / f'docs/evidence/validation{args.source_stage}.json').read_text('utf-8-sig'))
    if not stage_report.get('passed'):
        parser.error('Selected source stage has no passed validation report')
    compiled = json.loads((ROOT / f'BetaGwent/build/stage{args.source_stage}/compile/result.json').read_text('utf-8-sig'))
    expected = {item['path']: item['sha256'].lower() for item in compiled['patchSourcesBefore']}
    actual = {p.relative_to(source).as_posix(): sha(p) for p in sources}
    if actual != expected or not compiled['patchSourcesUnchangedDuringCompile']:
        parser.error('Frozen scripts differ from the selected native compilation')
    annotations = []
    for path in sources:
        text = path.read_text('utf-8-sig')
        code = mask(text)
        for match in re.finditer(r'@(\w+)\((\w+)\)\s*([^@]*?)(?=[{;])', code):
            kind, target, declaration = match[1], match[2], match[3]
            member = re.search(r'\b(?:function|event|var)\s+(\w+)', declaration)
            if not member:
                raise ValueError('Unknown annotated declaration: ' + str(path))
            item = dict(source=path.relative_to(source).as_posix(),
                        line=code.count('\n', 0, match.start()) + 1,
                        kind=kind, target=target, member=member[1],
                        declaration=' '.join(declaration.split()),
                        classPresent=target in index)
            if kind in ('wrapMethod', 'replaceMethod'):
                item['classicMethod'] = lookup(index, target, member[1])
            annotations.append(item)
    unresolved = [x for x in annotations if not x['classPresent'] or
                  x['kind'] in ('wrapMethod', 'replaceMethod') and not x['classicMethod']]
    mods = []
    mods_dir = game / 'Mods'
    if mods_dir.is_dir():
        for folder in sorted(mods_dir.iterdir()):
            if not folder.is_dir():
                continue
            info = folder / 'info.json'
            mods.append(dict(name=folder.name, metadata=json.loads(info.read_text('utf-8-sig')) if info.exists() else None,
                             hasPrecompiledBlob=(folder / 'content/precompiled.rsblob').exists()))
    base_manifest = {p.relative_to(base).as_posix(): sha(p) for p in sorted(base.rglob('*.ws'))}
    report = dict(schema=1, createdUtc=datetime.now(timezone.utc).isoformat(),
                  game=str(game), gameVersion='1.32', versionMarkers=versions,
                  executableSha256=sha(exe), sourceStage=args.source_stage,
                  sourceValidationPassed=True, sourceScriptCount=len(sources),
                  sourceScripts=actual, vanillaScriptCount=len(base_manifest), vanillaScripts=base_manifest,
                  installedMods=mods, annotationCounts=dict(Counter(x['kind'] for x in annotations)),
                  targetClasses=sorted(set(x['target'] for x in annotations)),
                  annotations=annotations, unresolvedTargets=unresolved,
                  gameModified=False, nativeCompilationRun=False, runtimeVerified=False,
                  limitations=['Static target presence does not validate signatures, types, access, native API or behavior.',
                               'REDkit annotations require a separate Classic integration strategy.',
                               'Resources, audio and save round trips remain unverified.'])
    out.mkdir(parents=True)
    shutil.copytree(source, out / 'baseline/scripts')
    # Retain exact vanilla inputs for the classes we must integrate with.
    for relative in sorted(set(index[name]['path'] for name in report['targetClasses'] if name in index)):
        destination = out / 'baseline/vanilla-targets' / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(base / relative, destination)
    if actual != {p.relative_to(source).as_posix(): sha(p) for p in sources}:
        raise RuntimeError('Source scripts changed during audit')
    (out / 'audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps(dict(report=str(out / 'audit.json'), gameVersion='1.32',
                         scripts=len(sources), vanillaScripts=len(base_manifest),
                         annotations=report['annotationCounts'], unresolvedTargets=unresolved,
                         installedMods=mods, nativeCompilationRun=False), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
