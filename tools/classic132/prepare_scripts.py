"""Lower the frozen REDkit patch into ordinary Classic WitcherScript overrides.

This prepares sources only. No game files or existing release inputs are edited.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/recon'))
from audit_classic132 import mask as source_mask, sha


@lru_cache(maxsize=8)
def mask(text):
    return source_mask(text)


def read_source(path):
    raw = path.read_bytes()
    return raw.decode('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig').replace('\r\n', '\n').replace('\r', '')


def block_end(code, opening):
    depth = 1
    for pos in range(opening + 1, len(code)):
        depth += (code[pos] == '{') - (code[pos] == '}')
        if not depth:
            return pos + 1
    raise ValueError('Unclosed declaration')


@lru_cache(maxsize=8)
def class_span(text, name):
    code = mask(text)
    matches = list(re.finditer(r'\bclass\s+' + re.escape(name) + r'\b[^{};]*\{', code))
    if len(matches) != 1:
        raise ValueError('Expected exactly one target class: ' + name)
    opening = matches[0].end() - 1
    return opening, block_end(code, opening)


def member_span(text, target, member):
    opening, end = class_span(text, target)
    code = mask(text)
    pattern = r'(?m)^[ \t]*(?:(?:public|private|protected|final|exec|latent)\s+)*(function|event)\s+(' + re.escape(member) + r')\s*\([^)]*\)(?:\s*:\s*\w+)?\s*\{'
    matches = list(re.finditer(pattern, code[opening + 1:end - 1]))
    if len(matches) != 1:
        raise ValueError(f'Expected one implemented method: {target}.{member}, found {len(matches)}')
    m = matches[0]
    offset = opening + 1
    start, body = offset + m.start(), offset + m.end() - 1
    return start, body, block_end(code, body), m[1]


def extract_annotations(text, source):
    code = mask(text)
    blocks = []
    for match in re.finditer(r'@(\w+)\((\w+)\)', code):
        kind, target = match[1], match[2]
        if kind not in ('addField', 'addMethod', 'wrapMethod'):
            raise ValueError('Unsupported annotation: ' + kind)
        start = match.end()
        if kind == 'addField':
            end = code.index(';', start) + 1
        else:
            body = code.index('{', start)
            end = block_end(code, body)
        declaration = text[start:end].strip()
        member = re.search(r'\b(?:function|event|var)\s+(\w+)', mask(declaration))
        if not member:
            raise ValueError('Unknown declaration in ' + source)
        blocks.append(dict(kind=kind, target=target, member=member[1], text=declaration,
                           source=source, line=code.count('\n', 0, match.start()) + 1,
                           start=match.start(), end=end))
    remaining = text
    for item in reversed(blocks):
        remaining = remaining[:item['start']] + '\n' + remaining[item['end']:]
    return remaining, blocks


def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError('Adaptation anchor missing or ambiguous: ' + before)
    return text.replace(before, after)


def replace_code_word(text, before, after):
    for match in reversed(list(re.finditer(r'\b' + re.escape(before) + r'\b', mask(text)))):
        text = text[:match.start()] + after + text[match.end():]
    return text


def adapt(source, text):
    if Path(source).name == 'deckNameInput.ws':
        # Classic does not expose the Next-Gen virtual-keyboard structure/API.
        # Use the existing GFx text panel through a Classic-specific public bridge.
        return '''// Classic text input uses the GFx keyboard panel, not a platform keyboard.
class CBetaGwentDeckNameInput extends IScriptable
{
    public function Open(menu : CR4BetaGwentBoardMenu, value : int, title : string, inputPurpose : int) : bool
    {
        if(!menu)return false;
        return menu.BeginClassicTextInput(value,inputPurpose,title);
    }
}
'''
    if Path(source).name in ('capabilityProbe.ws', 'nativeGwentEntry.ws'):
        text = replace_once(text, ', additionalCards : array<name>', '')
        text = replace_once(text, 'wrappedMethod(deckName, forceFaction, additionalCards);' if Path(source).name == 'capabilityProbe.ws' else 'wrappedMethod(deckName,forceFaction,additionalCards);',
                            'wrappedMethod(deckName, forceFaction);')
        text = replace_once(text, 'function OnGwintGameEnded()', 'function BetaGwentClassicGameEnded()')
    if Path(source).name == 'capabilityProbe.ws':
        text = replace_once(text, ' + " additional=" + additionalCards.Size()', '')
        # Classic has no native callback with this name. The probe provides the
        # innermost body; nativeGwentEntry wraps it, and our board calls it once.
        before = '@wrapMethod(CR4Player)\nfunction BetaGwentClassicGameEnded()'
        text = replace_once(text, before, '@addMethod(CR4Player)\nfunction BetaGwentClassicGameEnded()')
        before = '    wrappedMethod();\n}\n\n@wrapMethod(CR4GwintGameMenu)'
        text = replace_once(text, before, '}\n\n@wrapMethod(CR4GwintGameMenu)')
    if Path(source).name == 'nativeGwentEntry.ws':
        text = replace_once(text, 'function SetEnemyDeck(deckName : name)', 'function SetEnemyDeckByName(deckName : name)')
    if Path(source).name == 'developmentBoardMenu.ws':
        # Classic cannot open our separately registered practice menu at runtime.
        # DeckBuilder is a working stock entry; betaPracticeRequested selects practice.
        if 'exec function bgboard_open(' in text:
            text = replace_once(text, "nativePlayer=thePlayer;nativePlayer.betaPracticeRequested=true;\n    theGame.RequestMenu('BetaGwentBoard');",
                                "nativePlayer=thePlayer;nativePlayer.betaPracticeRequested=true;\n    theGame.RequestMenu('DeckBuilder');")
        text = replace_once(text, 'EMS_End_PlayerLost | EMS_End_PlayerForfeited', 'EMS_End_PlayerLost')
        text = replace_once(text, 'class CR4BetaGwentBoardMenu extends CR4Menu\n{',
                            'class CR4BetaGwentBoardMenu extends CR4Menu\n{\n    private var classicEndNotified : bool;')
        # Run before testMatch is reset, preserving exclusion of test rewards.
        text = replace_once(text, '            manager.testMatch=false;manager.SetForcedFaction(GwintFaction_Neutral);',
                            '            if(!classicEndNotified){classicEndNotified=true;((CR4Player)thePlayer).BetaGwentClassicGameEnded();}\n'
                            '            manager.testMatch=false;manager.SetForcedFaction(GwintFaction_Neutral);')
        text = replace_once(text, '    public function FinishControllerText(value : int, purpose : int, title : string)',
                            '''    public function BeginClassicTextInput(value : int, purpose : int, title : string) : bool
    {
        var openInput : CScriptedFlashFunction;
        if(!configured || value!=revision)return false;
        openInput=GetMenuFlash().GetMemberFlashFunction("openClassicTextInput");
        if(!openInput){theGame.GetGuiManager().ShowNotification("Classic text input requires the matching menu resource.",4.0);return false;}
        openInput.InvokeSelfThreeArgs(FlashArgInt(value),FlashArgInt(purpose),FlashArgString(title));
        return true;
    }
    public function FinishControllerText(value : int, purpose : int, title : string)''')
        text = replace_once(text, '        setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(0),FlashArgString(title),FlashArgBool(true));', '')
        text = replace_once(text, '        setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(purpose),FlashArgString(title),FlashArgBool(true));return true;', '        return true;')
    return text


def inject(text, target, declaration):
    opening, end = class_span(text, target)
    return text[:end - 1] + '\n    // Gwent Beta Classic 1.32 integration.\n' + declaration + '\n' + text[end - 1:]


def lower_wrapper(text, item, number):
    target, member = item['target'], item['member']
    start, body, end, original_kind = member_span(text, target, member)
    original = text[start:end]
    helper = f'BetaGwentClassicOriginal_{member}_{number}'
    if re.search(r'\b' + re.escape(helper) + r'\b', mask(text)):
        raise ValueError('Helper already exists: ' + helper)
    signature = original[:original.index('{')]
    wrapper = item['text']
    match = re.search(r'\bfunction\s+' + re.escape(member) + r'\s*\(([^)]*)\)(?:\s*:\s*(\w+))?', mask(wrapper))
    original_match = re.search(r'\b(?:function|event)\s+' + re.escape(member) + r'\s*\(([^)]*)\)(?:\s*:\s*(\w+))?', mask(signature))
    if not match or not original_match:
        raise ValueError('Unknown wrapper signature')
    # Parameter names are part of the body contract; Classic differs only in
    # capitalization for SetEnemyDeckByName. Reject any other silent mismatch.
    normalize = lambda s: re.sub(r'\s+', '', s).lower()
    if normalize(match[1]) != normalize(original_match[1]):
        raise ValueError('Wrapper parameters differ: ' + target + '.' + member)
    if (match[2] or 'void') != (original_match[2] or 'void'):
        raise ValueError('Wrapper return type differs: ' + target + '.' + member)
    # Keep event entry points as events, while helpers are ordinary functions.
    # Current wrapped vanilla events have no valued returns; fail if that changes.
    if original_kind == 'event' and re.search(r'\breturn\s+[^;\s][^;]*;', mask(original[original.index('{'):])):
        raise ValueError('Valued event return needs explicit lowering: ' + member)
    helper_code = re.sub(r'\b(?:function|event)\s+' + re.escape(member) + r'\b', 'function ' + helper, original, count=1)
    helper_code = re.sub(r'^\s*(?:(?:public|private|protected|final|exec|latent)\s+)*function', 'private function', helper_code, count=1)
    wrapper = replace_code_word(wrapper, 'wrappedMethod', helper)
    if original_kind == 'event':
        wrapper = re.sub(r'\bfunction\s+' + re.escape(member) + r'\b', 'event ' + member, wrapper, count=1)
        # The original Classic events here have no valued returns. A callable
        # helper is void; pass-through event paths therefore invoke it and keep
        # the original unhandled/default false result rather than return void.
        for returned in reversed(list(re.finditer(r'\breturn\s+' + re.escape(helper) + r'\s*\([^;]*\)\s*;', mask(wrapper)))):
            call = wrapper[returned.start():returned.end()].strip()[len('return'):].strip()
            wrapper = wrapper[:returned.start()] + '{ ' + call + ' return false; }' + wrapper[returned.end():]
    else:
        modifiers = re.match(r'\s*((?:(?:public|private|protected|final|exec|latent)\s+)*)function', signature)
        if modifiers and modifiers[1]:
            wrapper = modifiers[1] + wrapper
    item['helper'] = helper
    item['entryKind'] = original_kind
    return text[:start] + wrapper + '\n\n' + helper_code + text[end:]


def prepare(audit_dir, out):
    report = json.loads((audit_dir / 'audit.json').read_text('utf8'))
    source = audit_dir / 'baseline/scripts'
    vanilla = audit_dir / 'baseline/vanilla-targets'
    actual = {p.relative_to(source).as_posix(): sha(p) for p in sorted(source.rglob('*.ws'))}
    if actual != report['sourceScripts']:
        raise ValueError('Frozen baseline scripts changed')
    for p in vanilla.rglob('*.ws'):
        if sha(p) != report['vanillaScripts'][p.relative_to(vanilla).as_posix()]:
            raise ValueError('Frozen Classic source changed: ' + str(p))
    files, annotations = {}, []
    for relative in actual:
        text = adapt(relative, read_source(source / relative))
        remaining, items = extract_annotations(text, relative)
        files[relative] = remaining
        annotations.extend(items)
    target_paths = {}
    vanilla_files = {}
    for p in vanilla.rglob('*.ws'):
        relative = p.relative_to(vanilla).as_posix()
        text = read_source(p)
        vanilla_files[relative] = text
        for name in re.findall(r'\bclass\s+(\w+)\b', mask(text)):
            if name in target_paths:
                raise ValueError('Duplicate vanilla target class: ' + name)
            target_paths[name] = relative
    if set(x['target'] for x in annotations) - target_paths.keys():
        raise ValueError('A target class is missing')
    # Add all fields/methods before lowering wrappers, so a wrapper can wrap a
    # newly added Classic callback. Sort order is explicit and deterministic.
    for item in annotations:
        if item['kind'] == 'wrapMethod':
            continue
        path = target_paths[item['target']]
        text = vanilla_files[path]
        opening, end = class_span(text, item['target'])
        if re.search(r'\b(?:var|function|event)\s+' + re.escape(item['member']) + r'\b', mask(text[opening:end])):
            raise ValueError('Added member already exists: ' + item['target'] + '.' + item['member'])
        vanilla_files[path] = inject(text, item['target'], item['text'])
    for number, item in enumerate((x for x in annotations if x['kind'] == 'wrapMethod'), 1):
        path = target_paths[item['target']]
        vanilla_files[path] = lower_wrapper(vanilla_files[path], item, number)
    files.update(vanilla_files)
    for relative, text in files.items():
        code = mask(text)
        if '@' in code or re.search(r'\bwrappedMethod\b', code):
            raise ValueError('Unlowered patch directive: ' + relative)
    if out.exists():
        raise ValueError('Output exists; use a fresh directory')
    out.mkdir(parents=True)
    script_root = out / 'Mods/modBetaGwentClassic132/content/scripts'
    output_files = {}
    for relative, text in sorted(files.items()):
        target = script_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'\xff\xfe' + text.replace('\n', '\r\n').encode('utf-16le'))
        output_files[relative] = sha(target)
    evidence = dict(schema=1, createdUtc=datetime.now(timezone.utc).isoformat(),
                    generatorSha256=sha(Path(__file__)),
                    sourceStage=report['sourceStage'], sourceLanguage=report.get('sourceLanguage','ru'), audit=str(audit_dir / 'audit.json'),
                    auditSha256=sha(audit_dir / 'audit.json'), gameVersion='1.32',
                    sourceScriptCount=len(actual), outputScriptCount=len(files),
                    vanillaOverrides=sorted(vanilla_files),
                    loweredCounts=dict(Counter(x['kind'] for x in annotations)),
                    wrappers=[{k: x[k] for k in ('source', 'target', 'member', 'helper', 'entryKind')}
                              for x in annotations if x['kind'] == 'wrapMethod'],
                    sourceScripts=actual, outputScripts=output_files,
                    encoding='UTF-16LE BOM, CRLF', sourceOnly=True,
                    installedGameModified=False, nativeCompilationRun=False, runtimeVerified=False,
                    limitations=['Not an installable release; menus/resources/audio are not included.',
                                 'Classic compiler and runtime acceptance remain required.',
                                 'Index-only debug deck selection does not supply an NPC deck name.'])
    (out / 'preparation.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', 'utf8')
    (out / 'README.txt').write_text('SOURCE PREPARATION ONLY - NOT AN INSTALLABLE RELEASE.\n'
                                  'Classic native compilation and runtime verification have not run.\n'
                                  'Menus, textures, audio and resource compatibility are not included.\n'
                                  'Do not install alongside the existing Next-Gen mod.\n', 'utf8')
    print(json.dumps({k: evidence[k] for k in ('sourceStage', 'outputScriptCount', 'vanillaOverrides', 'loweredCounts', 'nativeCompilationRun')}, indent=2))
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    build = (ROOT / 'BetaGwent/build').resolve()
    if not out.is_relative_to(build) or out == build:
        parser.error('Output must be a fresh subdirectory of BetaGwent/build')
    prepare(args.audit.resolve(), out)


if __name__ == '__main__':
    main()
