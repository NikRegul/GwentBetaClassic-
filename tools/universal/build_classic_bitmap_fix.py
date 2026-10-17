"""Patch only native movie bytecode in the verified mixed-texture fix10 layout."""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zipfile

import build_classic_streaming_fix as base
from formats import Resource, bundle_entries, require, sha, write_bundle
from update_board_resource import movie_parts

ROOT = base.ROOT
BUILD = ROOT / 'BetaGwent/build/classic081-bitmap-fix11'
SOURCE = ROOT / 'BetaGwent/build/classic081-native-resources-fix10'
VERSION = '0.8.1-classic-native-bitmap-fix11'
ARCHIVE_NAME = 'GwentBetaClassic-0.8.1-1.32-fix11-BitmapPatch.zip'
MAIN = {
    r'betagwent\betagwent_board.redswf': 'betagwent_board',
    r'gameplay\gui_new\swf\gwint\deck_builder.redswf': 'betagwent_decks',
    r'gameplay\gui_new\swf\gwint\gwint_game.redswf': 'betagwent_npc00',
    r'betagwent\betagwent_kegop.redswf': 'betagwent_kegop',
}


def native(resource):
    _, pos = resource.properties(resource.chunks[0])
    size = struct.unpack_from('<I', resource.chunks[0], pos)[0]
    return pos, resource.chunks[0][pos + 4:pos + 4 + size]


def image_names(movie):
    result = []
    for code, payload, _ in movie_parts(movie)[1]:
        if code == 1009:
            pos = 11 + payload[10]
            require(len(payload[pos + 1:]) == payload[pos], 'GFx filename extent')
            result.append(payload[pos + 1:])
    return result


def edit_movie(movie):
    return movie


def edit_other_resource(name, raw):
    return raw


def archive():
    path = ROOT / 'BetaGwent/release' / ARCHIVE_NAME
    with zipfile.ZipFile(path, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for file in sorted((BUILD / 'package').rglob('*')):
            if file.is_file(): target.write(file, file.relative_to(BUILD / 'package').as_posix())
    with zipfile.ZipFile(path) as target: require(target.testzip() is None, 'ZIP CRC failure')
    (BUILD / 'archive.json').write_text(json.dumps(dict(path=str(path), bytes=path.stat().st_size,
                                                      sha256=sha(path)), indent=2), 'utf8')


def main():
    require(not (BUILD / 'package').exists(), 'Fresh package required')
    source = SOURCE / 'package/Mods/modBetaGwentClassic132'
    target = BUILD / 'package/Mods/modBetaGwentClassic132'
    shutil.copytree(source, target)
    shutil.copytree(SOURCE / 'package/DLC', BUILD / 'package/DLC')
    menus = json.loads((BUILD / 'menus/menus.json').read_text('utf8'))
    compiled = {Path(r['path']).stem: Path(r['path']) for r in menus['menus']}
    verification = json.loads((SOURCE / 'verification.json').read_text('utf8'))
    guids = {n: bytes.fromhex(g) for n, g in verification['nativeGuids'].items()}
    files, changed, auxiliary_changed, unchanged = {}, [], [], 0
    resources = BUILD / 'resources'
    for name, raw in bundle_entries(source / 'content/blob0.bundle'):
        if name in MAIN:
            previous = Resource(raw)
            replacement = Resource(compiled[MAIN[name]].read_bytes())
            pos, old_movie = native(previous)
            _, movie = native(replacement)
            movie = edit_movie(movie)
            require(image_names(old_movie) == image_names(movie), 'Native texture filenames changed')
            old_images = [(c, p) for c, p, _ in movie_parts(old_movie)[1] if c == 1008]
            new_images = [(c, p) for c, p, _ in movie_parts(movie)[1] if c == 1008]
            original_ids = {struct.unpack_from('<H',p)[0] for c,p in old_images}
            require(old_images == [(c,p) for c,p in new_images if struct.unpack_from('<H',p)[0] in original_ids],
                    'Existing native image bounds or IDs changed')
            require(len(new_images) == len({struct.unpack_from('<H',p)[0] for c,p in new_images}),
                    'Duplicate native character IDs')
            root = previous.chunks[0][:pos] + struct.pack('<I', len(movie)) + movie + struct.pack('<I', 0)
            raw = previous.replace_chunks([root, *previous.chunks[1:]])
            checked = Resource(raw)
            require(checked.chunks[1:] == previous.chunks[1:], 'Inline texture bytes changed')
            require(checked.imports == previous.imports, 'External texture imports changed')
            require(len(raw) <= 0x2000000, 'Classic async cap exceeded')
            changed.append(dict(path=name, beforeBytes=len(previous.data), afterBytes=len(raw),
                                textureChunksUnchanged=True, imageBoundsUnchanged=True,
                                textureImportsUnchanged=True, movieSha256=hashlib.sha256(movie).hexdigest()))
        else:
            replacement_raw = edit_other_resource(name, raw)
            if replacement_raw != raw:
                auxiliary_changed.append(dict(path=name, beforeBytes=len(raw), afterBytes=len(replacement_raw)))
                raw = replacement_raw
            else:
                unchanged += 1
        path = resources / name.replace('\\', '/')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        files[name.replace('\\', '/')] = path
    require(len(changed) == 4 and unchanged + len(auxiliary_changed) == 384, 'Unexpected payload coverage')
    entries = write_bundle(files, target / 'content/blob0.bundle', guids)
    (target / 'content/metadata.store').write_bytes(base.metadata(
        (source / 'content/metadata.store').read_bytes(), target / 'content/blob0.bundle', {}))
    require(sha(target / 'content/dep.cache') == sha(source / 'content/dep.cache'), 'Dependencies changed')
    info = json.loads((target / 'info.json').read_text('utf8'))
    info.update(version=VERSION, classicUIRenderer='native-linked-bitmap', nativeGameplayVerified=False)
    (target / 'info.json').write_text(json.dumps(info, indent=2), 'utf8')
    verification.update(version=VERSION, menus=changed, entries=entries,
                        maximumResourceBytes=max(e['bytes'] for e in entries), unchangedPayloads=unchanged,
                        nativeGameplayVerified=False, atlasDiagnostics=True)
    if auxiliary_changed:
        verification['auxiliaryMoviesChanged'] = auxiliary_changed
    (BUILD / 'verification.json').write_text(json.dumps(verification, indent=2), 'utf8')
    names = ['content/blob0.bundle', 'content/metadata.store', 'content/dep.cache', 'info.json']
    manifest = dict(version=VERSION, sourceVersion=json.loads((source / 'info.json').read_text('utf8'))['version'],
                    installedBefore={n: sha(source / n) for n in names},
                    installFiles={n: sha(target / n) for n in names},
                    dlcFiles=json.loads((SOURCE / 'install-manifest.json').read_text('utf8'))['dlcFiles'])
    (BUILD / 'install-manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    archive()
    print(json.dumps(dict(version=VERSION, menus=len(changed), unchangedPayloads=unchanged,
                         maximumResourceBytes=verification['maximumResourceBytes']), indent=2))


if __name__ == '__main__':
    main()
