"""Audit the editor-saved board config; optionally copy it to project overlay.

No binary resource editing or UI control. The installed REDkit config is read
only, and every existing HUD/menu/popup/scene must remain semantically equal.
"""
import argparse
import json
from pathlib import Path
from read_gui_resource import GuiResource, ResourceError

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / 'GwentB/myproject1/workspace'
ORIGINAL = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\gameplay\gui_new\guirsrc\r4default.guiconfig')
CANDIDATE = WORKSPACE / 'betagwent/betagwent_dev.guiconfig'
OVERLAY = WORKSPACE / 'gameplay/gui_new/guirsrc/r4default.guiconfig'
EXPECTED = {'menuName': 'BetaGwentBoard', 'menuResource': r'betagwent\betagwent_board.menu'}
ORIGINAL_SHA256 = '6a6fa1cba73dc689570daff3a13f2be06776cc898caa298b781c9ab52bdd113d'


def validate_config(original, candidate):
    for field in ('huds', 'popups', 'scene'):
        if original[field] != candidate[field]:
            raise ResourceError('Existing GUI field changed: ' + field)
    old, new = original['menus'], candidate['menus']
    if new != old + [EXPECTED]:
        raise ResourceError('Expected unchanged original menus plus exactly one BetaGwentBoard entry')
    names = [entry['menuName'] for entry in new]
    if len(names) != len(set(names)):
        raise ResourceError('Duplicate menu registration name')


def audit(apply=False):
    source, candidate = GuiResource(ORIGINAL), GuiResource(CANDIDATE)
    if source.manifest()['sha256'] != ORIGINAL_SHA256:
        raise ResourceError('Installed source changed since the recorded baseline; review before applying')
    old, new = source.config(), candidate.config()
    validate_config(old, new)
    menu = GuiResource(WORKSPACE / 'betagwent/betagwent_board.menu')
    expected_menu = {'menuClass': 'CR4BetaGwentBoardMenu',
                     'menuFlashSwf': r'betagwent\betagwent_board.redswf'}
    if menu.menu() != expected_menu:
        raise ResourceError('Board menu class or Flash resource mismatch')
    movie = GuiResource(WORKSPACE / 'betagwent/betagwent_board.redswf')
    if movie.exports[0]['class'] != 'CSwfResource':
        raise ResourceError('Expected native CSwfResource')
    if apply:
        if OVERLAY.exists() and OVERLAY.read_bytes() != candidate.data:
            raise ResourceError('Different project overlay already exists; refusing to overwrite it')
        OVERLAY.parent.mkdir(parents=True, exist_ok=True)
        if not OVERLAY.exists():
            # Exclusive creation prevents replacing concurrent user changes.
            with OVERLAY.open('xb') as output:
                output.write(candidate.data)
        validate_config(old, GuiResource(OVERLAY).config())
    overlay_matches = OVERLAY.exists() and OVERLAY.read_bytes() == candidate.data
    report = dict(original=source.manifest(), candidate=candidate.manifest(),
                  overlay=GuiResource(OVERLAY).manifest() if overlay_matches else None,
                  menu=menu.manifest(), menuProperties=menu.menu(), movie=movie.manifest(),
                  originalMenuCount=len(old['menus']), menuCount=len(new['menus']),
                  addedMenu=EXPECTED, previousMenusPreserved=True,
                  hudPopupScenePreserved=True, installedSourceUnchanged=True,
                  savedRegistrationVerified=True, projectOverlayApplied=overlay_matches,
                  engineReloadVerified=False, runtimeVerified=False,
                  note='Semantic read of saved GUI resources; runtime loading/bridge require game observation.')
    (ROOT / 'docs/evidence/board-registration.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Copy the validated config into project overlay')
    args = parser.parse_args()
    try:
        result = audit(args.apply)
    except (ResourceError, OSError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps({key: result[key] for key in ('menuCount', 'previousMenusPreserved',
        'savedRegistrationVerified', 'projectOverlayApplied', 'engineReloadVerified', 'runtimeVerified')}, indent=2))
