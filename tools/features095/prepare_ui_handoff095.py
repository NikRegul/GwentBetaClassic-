"""Create/verify a UI-only handoff for the card-audit chat. No release build."""
from pathlib import Path
import argparse,datetime,json,shutil,subprocess,sys
import ui_release095 as ui
ROOT=ui.ROOT
CANDIDATE=ROOT/'BetaGwent/build/ui-windows095-20261028-01'
def verify(out):
    d=ui.read(out/'handoff.json');assert d['status']=='ui-ready-for-combined-build'
    assert ui.read(out/ui.CONTRACT)==ui.inputs(),'UI/audio changed after handoff'
    for n,h in d['files'].items():assert ui.sha(ROOT/n)==h,'Handoff file changed: '+n
    for r in d['checks']:assert r['exitCode']==0 and ui.sha(out/r['log'])==r['sha256']
    candidate=ROOT/d.get('candidate',str(CANDIDATE.relative_to(ROOT)))
    ui.reports(out,candidate/d.get('sources','ui-sources08'))
    print('PASS UI release handoff; card audit/fresh combined build still required')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--verify',action='store_true')
    p.add_argument('--candidate',type=Path,default=CANDIDATE);p.add_argument('--sources',default='ui-sources08');p.add_argument('--patch',default='ui-patch08');p.add_argument('--acceptance',default='acceptance08.json')
    a=p.parse_args();out=a.out.resolve();candidate=a.candidate.resolve()
    assert candidate.is_relative_to(ROOT/'BetaGwent/build')
    assert out.is_relative_to(ROOT/'BetaGwent/build') and out!=ROOT/'BetaGwent/build'
    if a.verify:verify(out);return
    assert not out.exists(),'Use a new handoff directory';out.mkdir(parents=True)
    ui.freeze(out);target=out/'scripts/game/betagwent/duelAudio.ws';target.parent.mkdir(parents=True);shutil.copy2(ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws',target)
    shutil.copy2(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws',target.with_name('developmentBoardMenu.ws'))
    checks=[]
    def run(name,args):
        log=out/'logs'/(name+'.log');log.parent.mkdir(exist_ok=True)
        r=subprocess.run(list(map(str,args)),cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);log.write_bytes(r.stdout)
        checks.append({'name':name,'exitCode':r.returncode,'log':str(log.relative_to(out)),'sha256':ui.sha(log)})
        if r.returncode:raise RuntimeError(name+'\n'+r.stdout.decode('utf8',errors='replace')[-3500:])
    for platform in ['classic','nextgen']:
        board=candidate/a.sources/platform/'ui/src/BetaGwentBoard.as'
        for prefix,tool in [('windows','check_windows095'),('preview-keywords','check_preview_keywords095'),('battle-cleanup','check_battle_cleanup095'),('pad-legend','check_pad_legend096'),('target-cancel','check_target_cancel098'),('feedback099','check_feedback099'),('presentation100','check_presentation100'),('side-keywords','check_side_keywords102')]:
            run(prefix+'-'+platform,['node',ROOT/'tools/ui'/(tool+'.cjs'),board,out/(prefix+'-'+platform+'.json')])
    run('window-audio',['node',ROOT/'tools/ui/check_window_audio095.cjs',target,out/'window-audio-check.json'])
    run('outcome-faction',['node',ROOT/'tools/ui/check_outcome_faction098.cjs',out/'outcome-faction-check.json'])
    for name,args in [
        ('user-ui',['node','tools/ai/check_user_ui093.cjs',out/'user-ui-check.json']),
        ('choice-captions',['node','tools/ai/check_choice_captions093.cjs',out/'choice-captions.json']),
        ('editor168',['node','tools/ui/check_editor168.js']),('editor178',['node','tools/ui/check_editor178.js']),
        ('editor-feedback',['node','tools/ui/check_editor_feedback094.cjs']),
        ('fonts',[sys.executable,'-X','utf8','tools/features093/check_user_fonts093.py',out/'user-font-check.json']),
        ('release-gates',[sys.executable,'-X','utf8','tools/features095/test_ui_release095.py']),
        ('glossary',[sys.executable,'-X','utf8','tools/features091/test_glossary091.py']),
        ('build-contracts',[sys.executable,'-X','utf8','tools/features091/test_build091.py']),
        ('layout',[sys.executable,'-X','utf8','tools/recon/check_project_layout.py'])]:run(name,args)
    ui.reports(out,candidate/a.sources)
    proof=ui.read(candidate/a.acceptance);assert proof['status']=='ui-technical-checks-passed' and proof['nativeMenus']==8
    for platform in ['classic','nextgen']:
        menus=ui.read(candidate/a.sources/platform/'menus/menus.json')
        for m in menus['menus']:assert ui.sha(Path(m['path']))==m['sha256']
    patch=ui.read(candidate/a.patch/'manifest.json')
    for row in patch['platforms'].values():
        for f in row['files'].values():assert ui.sha(Path(f['path']))==f['sha256']
    files=[ROOT/'tools/features095'/n for n in ['build_release095.py','ui_release095.py','ui_release095_text.py','feedback099_text.py','feedback100_text.py','notes095_public.py','test_ui_release095.py','prepare_ui_handoff095.py']]
    files += [ROOT/n for n in ['Build-0.9.5.cmd','tools/features091/prepare_ui091.py','tools/features094/build094a_public.py','tools/features091/build091.py','tools/features093/verify093.py','tools/build_inputs.py',
        'tools/ai/check_user_ui093.cjs','tools/ui/check_editor168.js','tools/ui/check_windows095.cjs','tools/ui/check_preview_keywords095.cjs','tools/ui/check_battle_cleanup095.cjs','tools/ui/check_pad_legend096.cjs','tools/ui/check_window_audio095.cjs','tools/features093/check_user_fonts093.py']]
    files += [ROOT/'docs/UI_RELEASE_HANDOFF_095_RU.md',ROOT/'docs/prompts/BUILD_095_AFTER_CARD_AUDIT_RU.md']
    files += [ROOT/'tools/ai/profile_provenance094.py',ROOT/'tools/ai/test_profile_provenance096.py',ROOT/'tools/features091/check_aim_source091.js',ROOT/'tools/ai/check_choice_fates093.cjs']
    files += [ROOT/'tools/features093/test_verify_plans095.py']
    files += [ROOT/'tools/features091'/n for n in ['test_glossary091.py','check_related091.js','build_related091.py']]
    files += [candidate/a.acceptance,candidate/a.patch/'manifest.json']
    files += [ROOT/n for n in proof.get('nativeCompilerReports',[str((CANDIDATE/'native-audio-final/compile-nextgen-final/result.json').relative_to(ROOT)),'BetaGwent/toolchains/classic-runtime/runs/ui-windows095-20261028-01-04/result.json'])]
    files += [ROOT/'tools/ui/window_art098.py',ROOT/'tools/ui/check_picker_native098.py',ROOT/'tools/ui/check_outcome_faction098.cjs',ROOT/'tools/ui/check_target_cancel098.cjs',ROOT/'tools/ui/check_feedback099.cjs',ROOT/'tools/ui/check_presentation100.cjs',ROOT/'data/beta924/design/window_art098.json']
    files += list(ui.NOTES.glob('0.9.5_*.md'));assert len(list(ui.NOTES.glob('0.9.5_*.md')))==39
    record={'schema':1,'status':'ui-ready-for-combined-build','createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidate':str(candidate.relative_to(ROOT)),'sources':a.sources,'patch':a.patch,'acceptance':a.acceptance,'checks':checks,'files':{f.relative_to(ROOT).as_posix():ui.sha(f)for f in files},
        'cardAuditComplete':False,'cardAuditFrozenHere':False,'fullReleaseBuilt':False,'installed':False,'published':False,
        'allBetaAnimationsPorted':False,'nativeGameTested':False,'nextAction':'Finish card audit, verify current handoff, run Build-0.9.5.cmd with a fresh --out; do not reuse old UI bundles or rule snapshots.'}
    (out/'handoff.json').write_text(json.dumps(record,indent=2)+'\n','utf8');verify(out)
    print(json.dumps({'out':str(out),'checks':len(checks),'notes':39,'nativeMenus':8,'releaseBuilt':False}))
if __name__=='__main__':main()
