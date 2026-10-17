"""Package explicit effect defaults and the same leader frames in Mods and DLC."""
import json
from pathlib import Path
import struct
import build_classic_subimages as fragments
import classic_leader_frames
from build_classic_native_resources_fix import make_metadata


def main():
    base=fragments.base;fragments.BUILD=base.ROOT/'BetaGwent/build/classic081-effect-state-fix16'
    base.BUILD=fragments.BUILD;base.SOURCE=base.ROOT/'BetaGwent/build/classic081-visual-fix15'
    base.VERSION='0.8.1-classic-effect-state-leaders-fix16'
    base.ARCHIVE_NAME='GwentBetaClassic-0.8.1-1.32-fix16-EffectsLeadersPatch.zip'
    editor=classic_leader_frames.Editor();base.edit_other_resource=editor.edit;base.edit_movie=fragments.add_fragments
    originalArchive=base.archive
    def archive():
        assert len(editor.reports)==322
        dlc='dlcBetaGwentClassic132Assets';source=base.SOURCE/'package/DLC'/dlc/'content'
        target=base.BUILD/'package/DLC'/dlc/'content'
        oldBundle=source/'bundles/blob0.bundle'
        with oldBundle.open('rb') as f:
            h=f.read(32);toc=f.read(struct.unpack_from('<I',h,16)[0])
        guids={toc[p:p+256].split(b'\0')[0].decode().replace('\\','/'):toc[p+256:p+272] for p in range(0,len(toc),320)}
        files={};auxiliary=[];dpath=base.BUILD/'dlc-resources'
        for name,raw in base.bundle_entries(oldBundle):
            mod=base.BUILD/'resources'/name.replace('\\','/')
            if mod.exists():
                replacement=mod.read_bytes()
            else:replacement=raw
            path=dpath/name.replace('\\','/');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(replacement)
            files[name.replace('\\','/')]=path
            if name.endswith('.redswf'):auxiliary.append(dict(path=name,bytes=len(replacement),sha256=base.sha(path)))
        entries=base.write_bundle(files,target/'bundles/blob0.bundle',guids)
        (target/'metadata.store').write_bytes(make_metadata(target/'bundles/blob0.bundle',r'bundles\blob0.bundle'))
        assert base.sha(target/'dep.cache')==base.sha(source/'dep.cache')
        report=dict(auxiliary=auxiliary,nativeGuids={n:g.hex() for n,g in guids.items()},
            definitionPath=r'dlc\dlcbetagwentclassic132assets\betagwent_gui.reddlc',scaleformDirectoryPath='gameplay\\gui_new\\',
            assetsIdenticalToMod=True,leaderPagesChanged=322)
        (base.BUILD/'dlc-verification.json').write_text(json.dumps(report,indent=2),'utf8')
        (base.BUILD/'leader-verification.json').write_text(json.dumps(dict(pages=editor.reports,framesPerPage=24,originalPixelsPreserved=True),indent=2),'utf8')
        name='content/soundspc.cache';audio=base.SOURCE/'package/Mods/modBetaGwentClassic132'/name
        assert base.sha(audio)==base.sha(base.BUILD/'package/Mods/modBetaGwentClassic132'/name)
        path=base.BUILD/'install-manifest.json';manifest=json.loads(path.read_text('utf8'))
        manifest['preservedFiles']={name:base.sha(audio)}
        manifest['dlcInstalledBefore']={p.relative_to(source.parent).as_posix():base.sha(p) for p in source.rglob('*') if p.is_file()}
        manifest['dlcFiles']={p.relative_to(target.parent).as_posix():base.sha(p) for p in target.rglob('*') if p.is_file()}
        path.write_text(json.dumps(manifest,indent=2),'utf8');originalArchive()
    base.archive=archive;base.main()


if __name__=='__main__':main()
