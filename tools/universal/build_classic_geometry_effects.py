"""Package bounded hand geometry, linked effect cells and embedded Classic audio."""
import json
import shutil
import build_classic_subimages as fragments


def main():
    base=fragments.base
    fragments.BUILD=base.ROOT/'BetaGwent/build/classic081-geometry-effects-fix14'
    base.BUILD=fragments.BUILD
    base.SOURCE=base.ROOT/'BetaGwent/build/classic081-hand-fix13'
    base.VERSION='0.8.1-classic-geometry-effects-audio-fix14'
    base.ARCHIVE_NAME='GwentBetaClassic-0.8.1-1.32-fix14-BattlePatch.zip'
    base.edit_movie=fragments.add_fragments
    originalArchive=base.archive
    def archive():
        name='content/soundspc.cache'
        target=base.BUILD/'package/Mods/modBetaGwentClassic132'/name
        shutil.copy2(base.BUILD/'audio/soundspc.cache',target)
        manifestPath=base.BUILD/'install-manifest.json'
        manifest=json.loads(manifestPath.read_text('utf8'))
        manifest['installedBefore'][name]=base.sha(base.ROOT/'BetaGwent/build/universal081/audio-classic/soundspc.cache')
        manifest['installFiles'][name]=base.sha(target)
        manifestPath.write_text(json.dumps(manifest,indent=2),'utf8')
        originalArchive()
    base.archive=archive
    base.main()


if __name__=='__main__':main()
