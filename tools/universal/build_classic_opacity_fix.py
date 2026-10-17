"""Package four opacity-fixed menus; keep fix16 audio and all auxiliary movies."""
import json
import build_classic_subimages as fragments


def main():
    base = fragments.base
    fragments.BUILD = base.ROOT / 'BetaGwent/build/classic081-opacity-fix17'
    base.BUILD = fragments.BUILD
    base.SOURCE = base.ROOT / 'BetaGwent/build/classic081-effect-state-fix16'
    base.VERSION = '0.8.1-classic-opacity-fix17'
    base.ARCHIVE_NAME = 'GwentBetaClassic-0.8.1-1.32-fix17-OpacityPatch.zip'
    base.edit_movie = fragments.add_fragments
    original_archive = base.archive

    def archive():
        name = 'content/soundspc.cache'
        source = base.SOURCE / 'package/Mods/modBetaGwentClassic132' / name
        target = base.BUILD / 'package/Mods/modBetaGwentClassic132' / name
        assert base.sha(source) == base.sha(target), 'Accepted audio changed'
        path = base.BUILD / 'install-manifest.json'
        manifest = json.loads(path.read_text('utf8'))
        manifest['preservedFiles'] = {name: base.sha(source)}
        manifest['dlcInstalledBefore'] = dict(manifest['dlcFiles'])
        for relative, digest in manifest['dlcFiles'].items():
            assert base.sha(base.BUILD / 'package/DLC/dlcBetaGwentClassic132Assets' / relative) == digest
        path.write_text(json.dumps(manifest, indent=2), 'utf8')
        original_archive()

    base.archive = archive
    base.main()


if __name__ == '__main__':
    main()
