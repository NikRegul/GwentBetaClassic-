"""Package the final 0.9.0 archives from release090-final (Windows or any host).

Uses the accepted package_integrated090/build_release pipeline unchanged, with:
  * INPUT = release090-final (cleaner fix, native copy menus, Math.max fix);
  * the new Classic native compile result (--classic-compile);
  * native clipboard files in bin/x64 (Classic) and bin/x64 + bin/x64_dx12 (Next-Gen).
Archives: release090-final/package-candidate/archives. Nothing is published.
"""
from pathlib import Path
import os
import argparse, hashlib, json, re, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final')
sys.path.insert(0, str(Path(__file__).parent))
import package_integrated090 as pi
import build_release as pack

BINS = {'classic': ['bin/x64'], 'nextgen': ['bin/x64', 'bin/x64_dx12']}
original_finish = pi.finish
original_redux = pack.redux
PLATFORM = None


BANNER_DEPOT = 'gameplay/gui_new/swf/betagwentbanners/'


def banner_guid(name):
    """Stable non-zero Classic resource identity for a new banner page."""
    digest = hashlib.md5(('betagwent090:' + name.lower()).encode('ascii')).digest()
    assert digest != bytes(16)
    return digest


def classic_banner_guids(base):
    """Classic bundles require a cook GUID for every CR2W entry (fix7 safety check)."""
    original = base.write_bundle

    def write_bundle(files, out, guids=None):
        guids = dict(guids or {})
        for name in files:
            if name.replace('\\', '/').startswith(BANNER_DEPOT):
                guids[name.replace('\\', '/')] = banner_guid(name.replace('\\', '/'))
        return original(files, out, guids)
    base.write_bundle = write_bundle


def add_dependency_entries(cache, names):
    """Leaf pages (languages, leader pages) are SPED v2 entries with an empty (0,0) range."""
    import struct
    sys.path.insert(0, str(ROOT / 'tools/classic132'))
    from dependencies import read_dependency_cache
    from build_resources import vlq
    data = cache.read_bytes(); d = read_dependency_cache(data)
    new = [banner_guid(n) for n in names if banner_guid(n) not in d['guids']]
    guids = d['guids'] + new; first = d['first'] + [0] * len(new); second = d['second'] + [0] * len(new)
    out = b'SPED' + struct.pack('<I', 2)
    for array, width in ((b''.join(guids), 16), (struct.pack('<%dI' % len(first), *first), 4),
                         (struct.pack('<%dI' % len(second), *second), 4), (struct.pack('<%dI' % len(d['pool']), *d['pool']), 4)):
        out += vlq(len(array) // width) + array
    checked = read_dependency_cache(out)
    assert checked['guids'][:len(d['guids'])] == d['guids'] and checked['pool'] == d['pool']
    cache.write_bytes(out)
    return len(new)


def register_classic_banner_dlc(part, banners):
    """Register new Loader URLs in the native Scaleform DLC, not only Mods."""
    import struct
    sys.path.insert(0, str(ROOT/'tools/universal'))
    from formats import bundle_entries, write_bundle
    from build_classic_native_resources_fix import make_metadata
    content=part/'package/DLC/dlcBetaGwentClassic132Assets/content'
    bundle=content/'bundles/blob0.bundle'
    with bundle.open('rb') as stream:
        header=stream.read(32);toc=stream.read(struct.unpack_from('<I',header,16)[0])
    guids={row[:256].split(b'\0')[0].decode('ascii').replace('\\','/'):row[256:272]
           for row in (toc[i:i+320] for i in range(0,len(toc),320))}
    folder=part/'dlc-banner-resources';folder.mkdir()
    files={};preserved={}
    for name,raw in bundle_entries(bundle):
        name=name.replace('\\','/');path=folder/name
        assert path.resolve().is_relative_to(folder.resolve())
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        files[name]=path;preserved[name]=hashlib.sha256(raw).hexdigest()
    names=[]
    for banner in banners:
        name=BANNER_DEPOT+banner.name;assert name not in files
        files[name]=banner;guids[name]=banner_guid(name);names.append(name)
    updated=bundle.with_name('banner-registration.bundle')
    write_bundle(files,updated,guids)
    assert {name.replace('\\','/'):hashlib.sha256(raw).hexdigest() for name,raw in bundle_entries(updated)
            if name.replace('\\','/') in preserved}==preserved
    updated.replace(bundle)
    (content/'metadata.store').write_bytes(make_metadata(bundle,r'bundles\blob0.bundle'))
    assert add_dependency_entries(content/'dep.cache',names)==len(banners)
    return len(names)


def to_utf16_xml(name, raw):
    """Classic 1.32 ships its XML definitions as UTF-16 LE; the mod's REDkit-derived
    XML (loot tables, Beta items, Redux items) was UTF-8 and left 1.32 shops empty."""
    if not name.lower().endswith('.xml') or raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        return raw
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    if text.startswith('<?xml'):
        end = text.index('?>')
        decl = re.sub(r"encoding\s*=\s*(['\"])[^'\"]*\1", 'encoding="UTF-16"', text[:end])
        if 'encoding=' not in decl: decl += ' encoding="UTF-16"'
        text = decl + text[end:]
    out = text.replace('\n', '\r\n').encode('utf-16')  # BOM + little endian
    assert out.startswith(b'\xff\xfe') and out.decode('utf-16').count('<') == raw.decode('utf-8-sig').count('<')
    return out


def classic_utf16_xml(base):
    """Wrap the Classic resource pass: every XML payload of the mod bundle becomes UTF-16."""
    original_main = base.main

    def main():
        edit = base.edit_other_resource
        base.edit_other_resource = lambda name, raw: to_utf16_xml(name, edit(name, raw))
        try:
            return original_main()
        finally:
            base.edit_other_resource = edit
    base.main = main


def redux():
    """Accepted Redux definitions plus the new Beta banner pages (new bundle entries)."""
    files = original_redux()
    if PLATFORM == 'classic':
        target = FINAL / 'classic-xml-utf16'
        for name, path in list(files.items()):
            if name.lower().endswith('.xml'):
                out = target / name; out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(to_utf16_xml(name, Path(path).read_bytes())); files[name] = out
    folder = FINAL / 'banners' / PLATFORM
    if folder.is_dir():
        for path in sorted(folder.rglob('*.redswf')):
            files[path.relative_to(folder).as_posix()] = path
    return files


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class _NoDeckCodeHelper:
    def __getattr__(self, name):
        return getattr(shutil, name)

    def copy2(self, src, dst, *args, **kwargs):
        if Path(src).name in ('Copy-Deck-Code.cmd', 'Copy-Deck-Code.ps1'):
            return dst
        return shutil.copy2(src, dst, *args, **kwargs)


def finish(part, mod, report):
    package = part / 'package'
    native = FINAL / 'native'
    expected = json.loads((FINAL / 'preparation.json').read_text('utf8'))['native']
    for folder in BINS[part.name]:
        target = package / folder
        (target / 'plugins').mkdir(parents=True, exist_ok=True)
        assert not (target / 'dinput8.dll').exists()
        shutil.copy2(native / 'dinput8.dll', target / 'dinput8.dll')
        shutil.copy2(native / 'GwentBetaClipboard.asi', target / 'plugins/GwentBetaClipboard.asi')
        assert sha(target / 'dinput8.dll') == expected['dinput8.dll']
        assert sha(target / 'plugins/GwentBetaClipboard.asi') == expected['GwentBetaClipboard.asi']
    banners = sorted((FINAL / 'banners' / part.name).rglob('*.redswf')) if (FINAL / 'banners').is_dir() else []
    if part.name == 'classic' and banners:
        names = [BANNER_DEPOT + p.name for p in banners]
        added = add_dependency_entries(package / 'Mods/modBetaGwentClassic132/content/dep.cache', names)
        report.update(classicBannerDependencyEntries=added,
                      classicBannerDLCEntries=register_classic_banner_dlc(part,banners))
    report.update(betaBanners=sorted(p.stem for p in (FINAL / 'banners' / part.name).rglob('*.redswf')) if (FINAL / 'banners').is_dir() else [],
                  nativeClipboard=dict(folders=BINS[part.name], directions=['game-to-windows']+
                      (['windows-to-game'] if b'betagwent:windows-paste-v1\0' in (FINAL/'native/GwentBetaClipboard.asi').read_bytes() else []), inGameVerified=False),
                  cleanerSingleResultMessage=True, numberDeclocalAbsent=True)
    # Release: Import/Export are hidden without bin, so the -debugscripts
    # Copy-Deck-Code fallback is not shipped.
    pi.shutil = _NoDeckCodeHelper()
    try:
        original_finish(part, mod, report)
    finally:
        pi.shutil = shutil
    assert not (package / 'Copy-Deck-Code.cmd').exists() and not (package / 'BetaGwentDocs/Copy-Deck-Code.ps1').exists()
    info = package / 'Mods' / mod / 'info.json'
    data = json.loads(info.read_text('utf8'))
    assert data['version'] == '0.9.0'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('platform', choices=['classic', 'nextgen'])
    parser.add_argument('--classic-compile', type=Path, required=True,
                        help='runs/<label>/result.json of native_compile.py for release090-final/classic-prepared-final')
    args = parser.parse_args()
    global PLATFORM
    PLATFORM = args.platform
    pack.redux = redux
    pi.INPUT = FINAL
    pi.BUILD = FINAL / 'package-candidate'
    pi.finish = finish
    pack.BUILD = pi.BUILD
    pack.VERSION = '0.9.0'
    pack.CLASSIC_COMPILE = args.classic_compile.resolve()
    pack.finish = finish
    if args.platform == 'classic':
        sys.path.insert(0, str(ROOT / 'tools/universal'))
        import build_classic_subimages as fragments
        classic_banner_guids(fragments.base)
        classic_utf16_xml(fragments.base)
    pi.prepare(args.platform)
    getattr(pack, args.platform)()


if __name__ == '__main__':
    main()
