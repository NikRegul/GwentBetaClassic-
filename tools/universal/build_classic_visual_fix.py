"""Build the remaining Classic visual changes with fix14 audio kept exact."""
import json
import build_classic_subimages as fragments


def main():
    base=fragments.base
    fragments.BUILD=base.ROOT/'BetaGwent/build/classic081-visual-fix15'
    base.BUILD=fragments.BUILD
    base.SOURCE=base.ROOT/'BetaGwent/build/classic081-geometry-effects-fix14'
    base.VERSION='0.8.1-classic-visual-scale-clock-fix15'
    base.ARCHIVE_NAME='GwentBetaClassic-0.8.1-1.32-fix15-VisualPatch.zip'
    base.edit_movie=fragments.add_fragments
    originalArchive=base.archive
    def archive():
        name='content/soundspc.cache'
        source=base.SOURCE/'package/Mods/modBetaGwentClassic132'/name
        target=base.BUILD/'package/Mods/modBetaGwentClassic132'/name
        assert base.sha(source)==base.sha(target),'Accepted audio changed'
        path=base.BUILD/'install-manifest.json';manifest=json.loads(path.read_text('utf8'))
        manifest['preservedFiles']={name:base.sha(source)}
        path.write_text(json.dumps(manifest,indent=2),'utf8')
        originalArchive()
    base.archive=archive
    base.main()


if __name__=='__main__':main()
