"""Build a new RU local package from current sources using the configured workspace."""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8',errors='replace')

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tools/ui'))
from build_release138 import presentation_lock
from build_voice137 import language_bridge

def job(label,args,logs,node=False):
    print(label,flush=True)
    log=logs/(label+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('wb') as out:
        command=['node',*map(str,args)] if node else [sys.executable,'-X','utf8',*map(str,args)]
        result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        print(log.read_text('utf8',errors='replace')[-5000:],flush=True)
        raise RuntimeError('Failed '+label+'; log: '+str(log))

def release_module(stage):
    source=(ROOT/'tools/build_release143.py').read_text('utf8')
    if stage!=143:
        for old,new in {
            'stage143':f'stage{stage}', 'audit143/final-v2':f'audit{stage}/source',
            'release143':f'release{stage}', 'regressions143':f'regressions{stage}',
            'inputs143':f'inputs{stage}', 'validation143':f'validation{stage}',
            'stage=143':f'stage={stage}', "'143'":repr(str(stage)),
            'compile-final-ru-v2':'compile',
            # One more AI suite (check_lock_choice144) than the frozen 0.6.7 list.
            "len(checks['checks'])==51":"len(checks['checks'])=="+str(81 if stage>=200 else 80 if stage>=191 else 79 if stage>=188 else 78 if stage>=181 else 77 if stage>=180 else 76 if stage>=178 else 72 if stage>=172 else 70 if stage>=168 else 66 if stage>=167 else 64 if stage>=165 else 63 if stage>=164 else 62 if stage>=163 else 61 if stage>=160 else 60 if stage>=158 else 57 if stage>=156 else 55 if stage>=155 else 54 if stage>=150 else 52),
        }.items():source=source.replace(old,new)
    namespace={'__name__':'source_release','__file__':str(ROOT/'tools/build_release143.py')}
    exec(compile(source,'source_release','exec'),namespace)
    return namespace

def dependencies():
    required=[
        ROOT/'BetaGwent/build/stage143/ru/sources/scripts',
        ROOT/'docs/evidence/voice141.json',ROOT/'docs/evidence/leader-intros142.json',
        ROOT/'BetaGwent/build/special-vfx142/manifest.json',
        ROOT/'BetaGwent/build/text138/resources',
        Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\x64_RedKit\wcc_lite.exe'),
        Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\tools\GFx4\gfxexport_mult4fix.exe'),
    ]
    missing=[str(p) for p in required if not p.exists()]
    if not shutil.which('node'):missing.append('Node.js in PATH')
    if missing:raise RuntimeError('Missing local build inputs:\n'+'\n'.join(missing))
    accepted=json.loads((ROOT/'BetaGwent/build/stage143/compile-final-ru-v2/result.json').read_text('utf8'))
    if not accepted.get('humanReportedPriorLicenseAcceptance'):
        raise RuntimeError('The REDkit license must have been accepted by the user before running this pipeline.')

def reuse_native_menus(source_stage,stage):
    import hashlib
    def digest(path):
        with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
    evidence=ROOT/'docs/evidence'
    record=json.loads((evidence/f'stage{source_stage}-completion.json').read_text('utf8'))
    current={p.name:digest(p) for p in (ROOT/'BetaGwent/ui/src').glob('*.as')}
    if record['sources']!=current or len(record['menus'])!=4:raise RuntimeError('Native menu reuse requires identical current ActionScript')
    for menu in record['menus']:
        if digest(menu['resource'])!=menu['sha256']:raise RuntimeError('Native menu resource changed: '+menu['entry'])
        destination=ROOT/f'BetaGwent/build/stage{stage}/ru/resources'/Path(menu['resource']).name
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(menu['resource'],destination)
        if digest(destination)!=menu['sha256']:raise RuntimeError('Reused native resource copy changed')
        menu['resource']=str(destination)
        suffix='' if menu['entry']=='BetaGwentBoard' else '-'+menu['entry']
        for kind in ('board-build','board-bridge-bytecode','board-resource-update'):
            source=evidence/f'stage{source_stage}-ru-{kind}{suffix}.json'
            item=json.loads(source.read_text('utf8'))
            if kind=='board-build' and item['sources']!=current:raise RuntimeError('Menu evidence sources do not match')
            if kind=='board-bridge-bytecode' and not item['passed']:raise RuntimeError('Menu bridge was not verified')
            if kind=='board-resource-update' and not (item['nativeABCMatchesBuiltSWF'] and item['headerTableChunkChecksumsVerified']):raise RuntimeError('Menu resource was not verified')
            if 'stage' in item:item['stage']=stage
            item['reusedFromStage']=source_stage
            (evidence/f'stage{stage}-ru-{kind}{suffix}.json').write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n','utf8')
    record['stage']=stage;record['reusedFromStage']=source_stage
    (evidence/f'stage{stage}-completion.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
    print('Reused four verified native menus from stage '+str(source_stage),flush=True)

def prepare_publication(version,stage):
    # An existing publish-<version> holds hand-written release notes: keep it.
    publish=ROOT/'BetaGwent/release'/('publish-'+version)
    if not publish.exists():
        shutil.copytree(ROOT/'BetaGwent/release/publish-0.6.7',publish)
        for document in publish.glob('*.md'):
            document.write_text(document.read_text('utf8').replace('# Gwent Beta Classic 0.6.7','# Gwent Beta Classic '+version).replace('# Управление 0.6.7','# Управление '+version).replace('# Controls 0.6.7','# Controls '+version),'utf8')
    notes=ROOT/'docs/releases'/version/'UPDATE_RU.md'
    presentation=(notes if notes.exists() else ROOT/'docs/PRESENTATION143_RU.md').read_text('utf8')
    (ROOT/f'docs/PRESENTATION{stage}_RU.md').write_text(presentation.replace('Gwent Beta Classic 0.6.7','Gwent Beta Classic '+version)+'\nЛокальная сборка из текущих исходников. Новые изменения требуют собственной игровой проверки.\n','utf8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',help='New version; default: 0.7.3-local-YYYYMMDD-HHMMSS')
    p.add_argument('--stage',type=int,help='Fresh build stage; allocated automatically by default')
    p.add_argument('--verify',action='store_true',help='Verify an existing package; requires its version and stage')
    p.add_argument('--check-only',action='store_true',help='Check inputs and show the plan without building')
    p.add_argument('--gui-limit-mib',type=int,help='Explicit loading target; new full builds default to 65 MiB')
    p.add_argument('--resume-package',action='store_true',help='Resume an unarchived stage after compilation; requires version/stage')
    p.add_argument('--reuse-native-menus',type=int,help='Reuse four verified native menus with identical current ActionScript')
    a=p.parse_args()
    if (a.verify or a.resume_package) and (not a.version or a.stage is None):p.error('--verify/--resume-package require --version and --stage')
    if a.verify and a.resume_package:p.error('--verify and --resume-package are mutually exclusive')
    if a.gui_limit_mib is not None and not 1<=a.gui_limit_mib<100:p.error('--gui-limit-mib must be 1..99')
    version=a.version or '0.7.3-local-'+datetime.now().strftime('%Y%m%d-%H%M%S')
    if not re.fullmatch(r'\d+\.\d+\.\d+[a-z]?(?:-[A-Za-z0-9-]+)?',version):p.error('Use a version such as 0.6.8b or 0.6.7-local-test')
    if a.stage is None:
        stages=[int(m[1]) for d in (ROOT/'BetaGwent/build').glob('stage*') if (m:=re.fullmatch(r'stage(\d+)',d.name))]
        stage=max([143,*stages])+1
    else:stage=a.stage
    if stage<143 or not a.verify and stage==143:p.error('New builds require a fresh stage greater than 143')
    if a.gui_limit_mib is None and not a.verify and not a.resume_package and stage>=150:a.gui_limit_mib=63 if stage>=198 else 65
    base=ROOT/f'BetaGwent/build/stage{stage}'
    archive=ROOT/f'BetaGwent/release/GwentBetaClassic-{version}-RU.zip'
    dependencies()
    if not a.verify and not a.resume_package and (base.exists() or archive.exists()):raise RuntimeError('Build directory/version already exists; choose a fresh version and stage')
    if a.resume_package and (not base.is_dir() or archive.exists()):raise RuntimeError('Resume requires an existing unarchived stage')
    plan=dict(version=version,stage=stage,archive=str(archive),verify=a.verify,guiLimitMiB=a.gui_limit_mib,
              steps=['snapshot','scripts','special-art','regressions','native-menus','native-compile','package','verify'],installsGame=False)
    print(json.dumps(plan,ensure_ascii=False,indent=2),flush=True)
    if a.check_only:return
    with presentation_lock():
        release=release_module(stage);release['VERSION']=version
        budget_path=base/'gui-budget.json'
        if a.gui_limit_mib is not None:
            budget=dict(guiLimitMiB=a.gui_limit_mib,experimental=a.gui_limit_mib>56,nativeGameTested=False)
            if budget_path.exists() and json.loads(budget_path.read_text())!=budget:raise RuntimeError('GUI target already fixed for this stage')
            if a.verify or a.resume_package:budget_path.write_text(json.dumps(budget,indent=2)+'\n','utf8')
        if a.verify:
            release['verify_package']();return
        if a.resume_package:
            prepare_publication(version,stage)
            release['inputs']()
            package_base=ROOT/f'BetaGwent/build/release{stage}/ru'
            phases=['prepare','cook','strings','audio','dependencies','pack','metadata','archive']
            if (package_base/'frozen.json').exists():
                raise RuntimeError('Package is already frozen; resume this configuration explicitly from its unfinished phase')
            for phase in phases:
                release['step']('package-ru-'+phase,'tools/build_language_release.py',phase,'--stage',stage,'--version',version,'--language','ru','--compiled',base/'compile')
            release['verify_package']();return
        # Recheck after acquiring the shared build lock.
        if base.exists() or archive.exists():raise RuntimeError('Output appeared while waiting for the build lock')
        logs=base/'logs';logs.mkdir(parents=True)
        if a.gui_limit_mib is not None:budget_path.write_text(json.dumps(budget,indent=2)+'\n','utf8')
        snapshot=ROOT/f'BetaGwent/build/audit{stage}/source'
        job('snapshot',['tools/ai/snapshot.py',snapshot],logs)
        patch=base/'ru/sources/scripts'
        shutil.copytree(ROOT/'BetaGwent/build/stage143/ru/sources/scripts',patch)
        for target in patch.rglob('*.ws'):
            relative=target.relative_to(patch)
            if target.name=='duelAudioCatalog.ws':continue # Verified RU bank durations and installed-bank flag.
            candidates=[ROOT/'BetaGwent/development/scripts'/relative,ROOT/'BetaGwent/scripts'/relative,ROOT/'tools/core-check/src'/relative.name]
            source=next((p for p in candidates if p.exists()),None)
            if source is None:raise RuntimeError('No canonical source for '+str(relative))
            if target.name=='developmentBoardMenu.ws':target.write_text(language_bridge(source.read_text('utf-8-sig'),'ru'),'utf-8-sig')
            else:shutil.copy2(source,target)
        if len(list(patch.rglob('*.ws')))!=70:raise RuntimeError('Unexpected patch source count')
        job('special-art',['tools/ui/build_spell_art143.py'],logs)
        if stage>=161:job('shop-keg-icon',['tools/shop_keg_icon161.py','--prepare-cache'],logs)
        if stage>=163:
            job('all-card-vfx',['tools/recon/extract_card_vfx163.py'],logs)
            job('all-card-vfx-routing',['tools/ui/build_special_vfx142.py'],logs)
        if stage>=178:job('presentation-prefabs',['tools/recon/extract_element_vfx163.py'],logs)
        if stage>=191:job('status-curves',['tools/ui/build_status191.py'],logs)
        if stage>=195:job('battle-curves',['tools/ui/build_battle080.py'],logs)
        if stage>=164:
            job('element-atlases',['tools/ui/build_elements164.py'],logs)
            job('element-audio',['tools/ui/build_element_audio164.py'],logs)
            shutil.copy2(ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws',patch/'game/betagwent/duelAudio.ws')
        # Run the maintained regression list against this fresh snapshot. Legacy
        # evidence is redirected into this run instead of overwriting old reports.
        check_source=(ROOT/'tools/check_work143.py').read_text('utf8')
        for old,new in {
            'audit143/final-v2':f'audit{stage}/source','audit143/regressions':f'audit{stage}/regressions',
            'regressions143':f'regressions{stage}','stage=143':f'stage={stage}',
            "'check_deferred062','check_consume_self'":"'check_deferred062','check_lock_choice144','check_consume_self'",
        }.items():
            assert check_source.count(old)>=1,old
            check_source=check_source.replace(old,new)
        if stage>=150:
            check_source=check_source.replace("'check_lock_choice144','check_consume_self'","'check_lock_choice144','check_playtest_rules150','check_consume_self'")
            check_source=check_source.replace("'check_fixes143','check_special_vfx142'","'check_playtest_vfx150','check_fixes143','check_special_vfx142'")
        check_namespace={'__name__':'source_checks','__file__':str(ROOT/'tools/check_work143.py')}
        exec(compile(check_source,'source_checks','exec'),check_namespace);check_namespace['main']()
        if stage>=155:
            script='tools/ai/audit_target_handlers155.py'
            job('target-handler-audit',[script,'--strict'],logs)
            report_path=ROOT/f'docs/evidence/regressions{stage}.json'
            report=json.loads(report_path.read_text('utf8'))
            report['checks'].append(dict(script=script,exitCode=0,sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),log=str(logs/'target-handler-audit.log')))
            if stage>=156:
                additional=[('cooperative-ai','tools/ai/check_cooperative156.js'),('native-consume','tools/ui/check_native_consume156.js')]
                if stage>=158:additional.extend([('assassin','tools/ai/check_assassin133.js'),('duel-vfx','tools/ai/check_duel_vfx158.js'),('followups','tools/ui/check_followups158.js')])
                if stage>=160:additional.append(('banish','tools/ui/check_banish160.js'))
                if stage>=163:additional.append(('all-card-vfx','tools/ui/check_card_vfx163.js'))
                if stage>=164:additional.append(('elements','tools/ui/check_elements164.js'))
                if stage>=165:additional.append(('armor-restore','tools/ai/check_armor_restore165.js'))
                if stage>=167:additional.append(('intro-focus','tools/ui/check_intro_focus167.js'))
                if stage>=168:additional.extend([('editor-keg','tools/ui/check_editor168.js'),('vfx-feedback','tools/ui/check_vfx168.js'),('external-review','tools/ai/check_review168.js'),('effect-gallery','tools/ui/check_gallery168.js')])
                if stage>=172:additional.extend([('presentation-feedback','tools/ui/check_presentation172.js'),('beta-vfx','tools/ui/check_presentation173.js')])
                if stage>=178:additional.extend([('editor073','tools/ui/check_editor178.js'),('presentation073','tools/ui/check_presentation178.js'),('trial-target','tools/ai/check_trial178.js')])
                if stage>=180:additional.append(('ai-playtest180','tools/ai/check_miruna_aglais_scorch180.js'))
                if stage>=181:additional.append(('emissary-mulligan181','tools/ai/check_emissary_mulligan181.js'))
                if stage>=188:additional.append(('ai-gold-playtest188','tools/ai/check_playtest188.js'))
                if stage>=191:additional.append(('status-armor074','tools/ui/check_status191.js'))
                if stage>=200:additional.append(('enemy-hand-tracer074b','tools/ui/check_drawbacks200.js'))
                for label,script in additional:
                    job(label,[script,snapshot],logs,node=True)
                    report['checks'].append(dict(script=script,exitCode=0,sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),log=str(logs/(label+'.log'))))
                if stage>=167:
                    script='tools/ai/check_quest126.py'
                    job('skellige-quest',[script,snapshot,logs/'skellige-quest.json'],logs)
                    report['checks'].append(dict(script=script,exitCode=0,sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),log=str(logs/'skellige-quest.log')))
            if stage>=178:
                script='tools/ai/check_profile136.py'
                job('collection-migration',[script,snapshot],logs)
                report['checks'].append(dict(script=script,exitCode=0,sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),log=str(logs/'collection-migration.log')))
            report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
        if a.reuse_native_menus:reuse_native_menus(a.reuse_native_menus,stage)
        else:job('native-menus',['tools/build_presentation94.py','--stage',stage,'--language','ru'],logs)
        # Keep a shared release input snapshot so other game targets can rebuild
        # its UI after active Next-Gen development has moved on.
        job('freeze-platform-inputs',['tools/freeze_platform_inputs.py','--stage',stage],logs)
        job('native-compile',['tools/recon/run_redkit_compile.py','--out',base/'compile','--patch',patch,'--timeout','300','--terms-already-accepted'],logs)
        prepare_publication(version,stage)
        release['inputs']()
        for phase in ('prepare','cook','strings','audio','dependencies','pack','metadata','archive'):
            release['step']('package-ru-'+phase,'tools/build_language_release.py',phase,'--stage',stage,'--version',version,'--language','ru','--compiled',base/'compile')
        release['verify_package']()

if __name__=='__main__':main()
