"""Repackage the Classic hand/HUD change using the accepted pixel-preserving UI."""
import build_classic_subimages as fragments


def main():
    base=fragments.base
    fragments.BUILD=base.ROOT/'BetaGwent/build/classic081-hand-fix13'
    base.BUILD=fragments.BUILD
    # The menus are compiled from the original pinned art; native fragments
    # are injected exactly once, matching fix12, before replacing fix12 ABCs.
    base.SOURCE=base.ROOT/'BetaGwent/build/classic081-subimages-fix12'
    base.VERSION='0.8.1-classic-hand-hud-fix13'
    base.ARCHIVE_NAME='GwentBetaClassic-0.8.1-1.32-fix13-HandHudPatch.zip'
    base.edit_movie=fragments.add_fragments
    base.main()


if __name__=='__main__':main()
