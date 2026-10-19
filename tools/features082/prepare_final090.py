"""0.9.0 final inputs: integrated scripts + one honest cleaner result message.

Creates BetaGwent/build/release090-final from frozen inputs, never modifying them:
  scripts           release090-integrated/scripts with the cleaner fix
  classic-audit     release090-integrated/classic-audit-final with that script
  classic-prepared-final  prepare_scripts.prepare() output (UTF-16 Classic sources)
  classic|nextgen/menus-final  menus from release090-native-clipboard (native
                    copy probe and the Math.max fix that removes Number declocal)
  classic|nextgen/extra-resources, classic UI fragments, locale verification
  native            dinput8.dll + GwentBetaClipboard.asi from clipboard090-r4
The layout matches what package_integrated090.prepare() expects as INPUT.

Run on Windows from D:\\w3mod: python -X utf8 tools/features082/prepare_final090.py
--scripts-only stops after scripts (used for checks on other hosts).
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
INTEGRATED = ROOT / 'BetaGwent/build/release090-integrated'
MENUS = ROOT / 'BetaGwent/build/release090-native-clipboard'
NATIVE = ROOT / 'BetaGwent/build/clipboard090-r4'
CLEANER = 'game/betagwent/profileCleanup090.ws'

OLD = '''    if(failed>0)BetaGwentCleanMessage("Some Beta Gwent inventory stacks could not be removed: "+failed+". Retry before uninstalling.");
    BetaGwentCleanMessage("Beta Gwent profile and known mirrors cleared.'''
NEW = '''    if(failed>0)
    {
        // One result only: a later success notification must not hide this.
        BetaGwentCleanMessage("Beta Gwent cleanup is INCOMPLETE: "+failed+" inventory stack(s) could not be removed. Do not uninstall yet. Drop or sell the remaining Beta Gwent items, then run bg_clean_confirm('DELETE_BETA_GWENT') again.");
        return;
    }
    BetaGwentCleanMessage("Beta Gwent profile and known mirrors cleared.'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def local(path):
    # Manifests store Windows paths; map them when checking from another host.
    p = Path(path)
    if not p.exists() and str(path).lower().startswith('d:\\w3mod\\'):
        p = ROOT / str(path)[9:].replace('\\', '/')
    return p


def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))


def patch_cleaner(path):
    s = path.read_text('utf-8-sig')
    assert s.replace('\r\n', '\n').count(OLD) == 1, 'cleaner message block changed upstream'
    s = s.replace('\r\n', '\n').replace(OLD, NEW)
    # The success text must remain reachable only after the failure branch.
    assert s.index('cleanup is INCOMPLETE') < s.index('profile and known mirrors cleared')
    write(path, s)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'BetaGwent/build/release090-final')
    parser.add_argument('--scripts-only', action='store_true')
    parser.add_argument('--scripts-from', type=Path, default=INTEGRATED / 'scripts')
    parser.add_argument('--menus', type=Path, default=MENUS)
    parser.add_argument('--native', type=Path, default=NATIVE)
    parser.add_argument('--banners', type=Path, default=None, help='build_banners090.py output (optional)')
    parser.add_argument('--phase', choices=['all', 'scripts', 'stage'], default='all',
                        help='scripts: scripts + Classic preparation; stage: menus and native files into an existing --out')
    args = parser.parse_args()
    out = args.out
    menus_dir, native_dir = args.menus, args.native
    if args.phase != 'stage':
        assert not out.exists(), 'Keep completed or interrupted candidates immutable; choose a new --out'
        out.mkdir(parents=True)
        changed = prepare_scripts_phase(out, args.scripts_from, args.scripts_only)
        if args.scripts_only or args.phase == 'scripts':
            print(json.dumps(dict(out=str(out), changed=changed)))
            return
    else:
        assert (out / 'classic-prepared-final/preparation.json').is_file() and not (out / 'preparation.json').exists()
        changed = json.loads((out / 'scripts-changed.json').read_text('utf8'))
    stage_phase(out, menus_dir, native_dir, changed, args.banners)


# Build 7 card fixes (Myrgtabrakke, Harald) checked against Beta 0.9.24 graphs.
CARD_FIXES = {'game/betagwent/duelNeutral.ws', 'game/betagwent/duelNilf.ws'}
ALLOWED = {CLEANER, 'game/betagwent/developmentBoardMenu.ws'} | CARD_FIXES


def prepare_scripts_phase(out, scripts_from, scripts_only):
    shutil.copytree(scripts_from, out / 'scripts')
    if 'cleanup is INCOMPLETE' not in (out / 'scripts' / CLEANER).read_text('utf-8-sig'):
        patch_cleaner(out / 'scripts' / CLEANER)
    changed = [p.relative_to(out / 'scripts').as_posix() for p in (out / 'scripts').rglob('*.ws')
               if sha(p) != sha(INTEGRATED / 'scripts' / p.relative_to(out / 'scripts'))]
    assert CLEANER in changed and set(changed) <= ALLOWED, changed
    (out / 'scripts-changed.json').write_text(json.dumps(changed), 'utf8')
    if scripts_only:
        return changed

    # Canonical development source follows the frozen release input.
    for name in changed:
        shutil.copy2(out / 'scripts' / name, ROOT / 'BetaGwent/development/scripts' / name)

    adir = out / 'classic-audit'
    shutil.copytree(INTEGRATED / 'classic-audit-final', adir)
    for name in changed:
        shutil.copy2(out / 'scripts' / name, adir / 'baseline/scripts' / name)
    audit_path = adir / 'audit.json'
    audit = json.loads(audit_path.read_text('utf-8-sig'))
    audit['sourceScripts'] = {p.relative_to(out / 'scripts').as_posix(): sha(p) for p in (out / 'scripts').rglob('*.ws')}
    audit['sourceScriptCount'] = len(audit['sourceScripts'])
    audit['featureCandidate'] = '0.9.0-final'
    audit_path.write_text(json.dumps(audit, indent=2), 'utf8')
    sys.path.insert(0, str(ROOT / 'tools/classic132'))
    from prepare_scripts import prepare
    prepare(adir, out / 'classic-prepared-final')
    prep = json.loads((out / 'classic-prepared-final/preparation.json').read_text('utf8'))
    old = json.loads((INTEGRATED / 'classic-prepared-final/preparation.json').read_text('utf8'))
    diff = sorted(k for k in set(prep['outputScripts']) | set(old['outputScripts'])
                  if prep['outputScripts'].get(k) != old['outputScripts'].get(k))
    # Classic lowers @addMethod bodies into the vanilla class file.
    assert diff and set(diff) <= {'game/betagwent/profileCleanup090.ws', 'game/player/playerWitcher.ws', 'game/betagwent/developmentBoardMenu.ws'} | CARD_FIXES, diff
    for name in [d for d in diff if not d.endswith('developmentBoardMenu.ws') and d not in CARD_FIXES]:
        fresh = (out / 'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts' / name).read_text('utf-16')
        frozen = (INTEGRATED / 'classic-prepared-final/Mods/modBetaGwentClassic132/content/scripts' / name).read_text('utf-16')
        assert fresh.replace('\r\n', '\n').replace(NEW, OLD) == frozen.replace('\r\n', '\n'), 'unexpected Classic change in ' + name
    (out / 'classic-prepared-diff.json').write_text(json.dumps(diff), 'utf8')
    return changed


def stage_phase(out, menus_dir, native_dir, changed, banners=None):
    MENUS, NATIVE = menus_dir, native_dir
    diff = json.loads((out / 'classic-prepared-diff.json').read_text('utf8'))

    for platform in ['classic', 'nextgen']:
        menus = json.loads((MENUS / platform / 'menus/menus.json').read_text('utf8'))
        assert len(menus['menus']) == 4
        for m in menus['menus']:
            assert sha(local(m['path'])) == m['sha256'], m['path']
        text = (MENUS / platform / 'ui/src/BetaGwentTextLanguage.as').read_text('utf-8-sig')
        assert 'size--' not in text, 'Number declocal source must not be packaged'
        board = (MENUS / platform / 'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
        assert 'betagwent:windows-clipboard-v1' in board
        target = out / platform
        (target / 'menus-final').mkdir(parents=True)
        shutil.copy2(MENUS / platform / 'menus/menus.json', target / 'menus-final/menus.json')
        shutil.copytree(INTEGRATED / platform / 'extra-resources', target / 'extra-resources')
        shutil.copytree(MENUS / platform / 'ui', target / 'ui')
        shutil.copy2(MENUS / platform / 'ui-inputs.json', target / 'ui-inputs.json')
        if platform == 'classic':
            shutil.copy2(MENUS / 'classic/subimages.json', target / 'subimages.json')
    (out / 'classic-languages-fixed').mkdir()
    shutil.copy2(INTEGRATED / 'classic-languages-fixed/verification.json', out / 'classic-languages-fixed/verification.json')
    for name in ['dinput8.dll', 'GwentBetaClipboard.asi']:
        (out / 'native').mkdir(exist_ok=True)
        shutil.copy2(NATIVE / name, out / 'native' / name)
    banner_report = None
    if banners:
        banner_report = json.loads((banners / 'banners-report.json').read_text('utf8'))
        for platform in ['classic', 'nextgen']:
            shutil.copytree(banners / platform / 'resources', out / 'banners' / platform)
            for key, row in banner_report['banners'].items():
                p = out / 'banners' / platform / banner_report['depot'] / row.get('file',key + '.redswf')
                assert sha(p) == row[platform]['sha256'], p
    report = dict(version='0.9.0', changedScripts=changed, classicPreparedDiff=diff, banners=banner_report and sorted(banner_report['banners']),
                  menusFrom=str(MENUS), native={n: sha(out / 'native' / n) for n in ['dinput8.dll', 'GwentBetaClipboard.asi']})
    (out / 'preparation.json').write_text(json.dumps(report, indent=2), 'utf8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
