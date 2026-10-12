"""Freeze fresh 0.6.2 script variants using the verified, unchanged voice banks."""
import hashlib
import json
import shutil
from pathlib import Path
from build_voice137 import durations, language_bridge, DEFAULT_TEXT, PACKAGE_ID, PROJECTS
from build_voice_mix135 import inventory

ROOT = Path(__file__).resolve().parents[2]
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    paths = ['data/beta924/ai/deck_patch128.json', 'data/beta924/ai/deck_variety128.json',
             'data/beta924/ai/rules.json', 'data/beta924/duel/presets.json',
             'BetaGwent/development/scripts/game/betagwent/duelSession.ws']
    patch_config = json.loads((ROOT/paths[0]).read_text('utf8'))
    presets = json.loads((ROOT/paths[3]).read_text('utf8'))['presets']
    restored = []
    for ident in (89,99):
        change = next(x for x in patch_config['decks'] if x['presetId']==ident)
        roster = next(x for x in presets if x['id']==ident)
        assert change.get('enabled') is False
        assert sorted(roster['templateIds']) == sorted(change['expectedTemplateIds'])
        restored.append(dict(presetId=ident,title=roster['title'],templateIds=roster['templateIds'],
                             leader=roster['leader'],revision128Enabled=False))
    inputs = dict(version='0.6.2',stage=138,restoredDecks=restored,
                  sources={name:SHA(ROOT/name) for name in paths})
    (ROOT/'docs/evidence/inputs138.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n','utf8')
    previous = json.loads((ROOT/'docs/evidence/voice137.json').read_text('utf8'))
    baseline = inventory(Path(previous['ru']['bank']).read_bytes())
    reports = {}
    for language, folder in PROJECTS.items():
        bank = Path(previous[language]['bank'])
        assert SHA(bank) == previous[language]['sha256'], ('Voice bank changed', language)
        actual = inventory(bank.read_bytes())
        assert len(actual) == len(baseline)
        assert {x for x in actual if x[0] == 4} == {x for x in baseline if x[0] == 4}
        if language != 'en': assert actual == baseline
        patch = ROOT/f'BetaGwent/build/stage138/{language}/sources/scripts'
        shutil.copytree(ROOT/'BetaGwent/build/board-patch', patch, dirs_exist_ok=True)
        assert len(list(patch.rglob('*.ws'))) == 70
        catalog = patch/'game/betagwent/duelAudioCatalog.ws'
        output, count = durations(catalog.read_text('utf-8-sig'),
                                 ROOT/'BetaGwent/audio'/folder/'Originals/SFX/BetaGwent79')
        catalog.write_text(output, 'utf-8-sig')
        bridge = patch/'game/betagwent/developmentBoardMenu.ws'
        bridge.write_text(language_bridge(bridge.read_text('utf-8-sig'), language), 'utf-8-sig')
        reports[language] = dict(previous[language], patch=str(patch),
                                 rewrittenDurations=count, catalogSha256=SHA(catalog),
                                 bridgeSha256=SHA(bridge), defaultTextLanguage=DEFAULT_TEXT[language],
                                 packageId=PACKAGE_ID[language], voiceBankReused=True)
        print('Fresh 0.6.2 scripts:', language, flush=True)
    (ROOT/'docs/evidence/voice138.json').write_text(json.dumps(reports, indent=2)+'\n', 'utf8')


if __name__ == '__main__': main()
