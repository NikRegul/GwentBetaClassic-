"""Finish display-only NPC role localization with fresh frozen menus."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--ui-folder',default='ui-sources-localized');p.add_argument('--backup-folder',default='ui-patch-before-role-localization');a=p.parse_args();out=a.build.resolve()
    assert out.is_relative_to(ROOT/'BetaGwent/build')
    ui=out/a.ui_folder
    assert ui.is_relative_to(out)
    def run(command,log):
        with (out/'logs'/log).open('w',encoding='utf8') as f:subprocess.run([str(x) for x in command],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        print('PASS',log,flush=True)
    for platform in ['classic','nextgen']:
        run([sys.executable,'-X','utf8','tools/universal/build_menus.py','--stage','203','--prepared',out/'classic-prepared-final','--source-ui',ui/platform/'ui','--input-manifest',ui/platform/'ui-inputs.json','--out',ui/platform/'menus'],'menus-localized-'+platform+'.log')
    old=out/'ui-patch';backup=out/a.backup_folder
    assert backup.is_relative_to(out)
    assert old.is_dir() and not backup.exists()
    old.rename(backup)
    run([sys.executable,'-X','utf8','tools/features091/build_ui091.py','--ui',ui,'--out',out/'ui-patch'],'ui-patch-localized.log')
    run(['node','tools/features091/check_gamepad091.js',ui,out/'gamepad-tests.json'],'gamepad-localized.log')
    run(['node','tools/features091/check_aim_source091.js',ui],'aim-source-localized.log')
    canonical=json.loads((ui/'gamepad-source.json').read_text('utf8'))
    for name,digest in canonical.items():assert hashlib.sha256((ROOT/'BetaGwent/ui/src'/name).read_bytes()).hexdigest()==digest,name
    (out/'ui-selection.json').write_text(json.dumps(dict(source=str(ui),canonical=canonical,reuseAcceptedPatch=False),indent=2)+'\n','utf8')
    (out/'user-ui-rebuild.json').write_text(json.dumps(dict(complete=True,reason='Explicit13-language generic NPC roles; no engine or board-script changes',source=str(ui),previousPatchPreserved=str(backup),canonical=canonical),indent=2)+'\n','utf8')

if __name__=='__main__':main()
