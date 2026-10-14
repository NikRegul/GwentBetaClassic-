"""Run the established 0.6.5 suites plus the new special/merchant/spy regressions."""
from pathlib import Path

SOURCE=Path(__file__).with_name('check_work141.py')

def main():
    source=SOURCE.read_text('utf8')
    changes={
        "audit141/regressions":"audit142/regressions",
        "audit141/candidate":"audit142/final",
        "'check_consume_self','scenarios123'":"'check_innkeepers142','check_ciri_return062','check_deferred062','check_consume_self','scenarios123'",
        "'check_controller123','check_catalog123'":"'check_special_vfx142','check_controller123','check_catalog123'",
        "report=dict(stage=141,":"report=dict(stage=142,",
        "docs/evidence/regressions141.json":"docs/evidence/regressions142.json",
    }
    for old,new in changes.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    # Reuse only unchanged AI suites on the exact same frozen snapshot. UI
    # suites run again after presentation changes, even if their test is unchanged.
    source=source.replace('    records=[]',"""    previous_path=ROOT/'docs/evidence/regressions142.json'
    previous=json.loads(previous_path.read_text('utf8')) if previous_path.exists() else {}
    current_fingerprint=json.loads((SNAPSHOT/'manifest.json').read_text('utf8'))['fingerprint']
    previous_checks=previous.get('checks',[]) if previous.get('fingerprint')==current_fingerprint else []
    records=[]""")
    source=source.replace("        log=BASE/(Path(script).stem+'.log')", """        reusable=next((c for c in previous_checks if c['script']==script and c['exitCode']==0 and c['sha256']==hashlib.sha256((ROOT/script).read_bytes()).hexdigest()),None)
        if reusable and script.startswith('tools/ai/'):
            records.append(reusable);print('REUSE '+script,flush=True);continue
        log=BASE/(Path(script).stem+'.log')""")
    namespace={'__file__':str(SOURCE),'__name__':'checks142'}
    exec(compile(source,str(SOURCE),'exec'),namespace)
    namespace['main']()

if __name__=='__main__':main()
