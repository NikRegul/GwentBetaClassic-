"""Run release regressions on a frozen copy without changing working scripts."""
import hashlib
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'BetaGwent/build/stage137/regressions'
SNAPSHOT = BASE/'snapshot'


def main():
    global BASE,SNAPSHOT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,default=SNAPSHOT)
    arguments=parser.parse_args()
    SNAPSHOT=arguments.snapshot.resolve();BASE=SNAPSHOT.parent
    BASE.mkdir(parents=True,exist_ok=True)
    commands = []
    for name in ('check_consume_self','scenarios123','scenarios124','scenarios125',
                 'check_followups126','check_engines126','check_weather_visual126',
                 'check_decisive127','check_ships127','check_concede127','check_tutor127',
                 'check_preventive127','check_clearrisk127','check_draug127','check_combo127',
                 'check_no_targets127','check_losing131','check_cavalry131','check_ciri131',
                 'check_policy133','check_hidden_information133','check_ciri_return062','check_deferred062'):
        commands.append(['node', f'tools/ai/{name}.js', str(SNAPSHOT), str(BASE/(name+'.json'))])
    commands.append(['node','tools/ai/check_deck_combos128.js',str(SNAPSHOT)])
    for name in ('check_controller123','check_catalog123','check_optional124',
                 'check_halfcast126','check_controller126','check_timing126',
                 'check_card_presentation126','check_followups127','check_presentation133',
                 'check_ux135','check_release137','check_leader_release137','check_fixes061'):
        commands.append(['node', f'tools/ui/{name}.js'])
    for name in ('check_rotation123','check_crafting123','check_quest126',
                 'check_rewards121','check_profile136'):
        commands.append([sys.executable,'-X','utf8',f'tools/ai/{name}.py',str(SNAPSHOT)])
    for name in ('tools/ai/check_locals133.py','tools/recon/check_cook_completion133.py',
                 'tools/recon/check_wcc_retry123.py','tools/ai/check_rosters128.py',
                 'tools/recon/check_expected_list137.py',
                 'tools/recon/check_build_selection137.py',
                 'tools/ui/check_assets137.py'):
        commands.append([sys.executable,'-X','utf8',name])
    commands.append([sys.executable,'-X','utf8','tools/ui/check_leader_motion137.py'])
    for name in ('check_intro_audio133','check_audio135'):
        commands.append([sys.executable,'-X','utf8',f'tools/ui/{name}.py',str(SNAPSHOT),
                         str(BASE/(name+'.json')),'--stage','137'])
    records = []
    for index, command in enumerate(commands):
        script = next(arg for arg in command if arg.startswith('tools/'))
        log = BASE/f'{index:02}-{Path(script).stem}.log'
        with log.open('wb') as output:
            result = subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT)
        if result.returncode:
            print(log.read_text('utf8',errors='replace')[-10000:],flush=True)
            raise RuntimeError('Regression failed: '+script)
        print('PASS '+script,flush=True)
        records.append(dict(script=script,sha256=hashlib.sha256((ROOT/script).read_bytes()).hexdigest(),
                            log=str(log),logSha256=hashlib.sha256(log.read_bytes()).hexdigest()))
    manifest=json.loads((SNAPSHOT/'manifest.json').read_text('utf8'))
    report=dict(stage=137,checks=records,snapshot=str(SNAPSHOT),fingerprint=manifest['fingerprint'],
                nativeGameTested=False)
    (ROOT/'docs/evidence/regressions137.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('PASS: '+str(len(records))+' release regression suites',flush=True)


if __name__=='__main__':main()
