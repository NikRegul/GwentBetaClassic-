"""Verify the actual 0.5.4 release, fresh native builds and exclusion of premium assets."""
from pathlib import Path
import hashlib,json,zipfile
import verify_release133
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence'

def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()

def main(stage=135,version='0.5.4',report_name='validation135'):
    verify_release133.main(stage=stage,version=version,report_name=report_name+'-base.json')
    for name in ['ux135','audio135']:
        report=read(E/(name+'.json'))
        for source,digest in report['sources'].items():assert sha(ROOT/source)==digest,('stale 0.5.4 evidence',source)
        if name=='ux135':assert report['checks']>=56
        else:assert {r['language'] for r in report['reports']}=={'ru','en'} and all(r['checks']>=14 for r in report['reports'])
    mix=read(E/'voice-mix135.json')
    assert {b['language'] for b in mix['banks']}=={'ru','en'}
    for bank in mix['banks']:
        assert bank['voiceGainDb']==0 and bank['objectInventoryPreserved'] and sha(Path(bank['bank']))==bank['sha256']
        assert sha(Path(bank['actor']))==bank['actorSha256']
        base=ROOT/f"BetaGwent/build/release{stage}/{bank['language']}"
        assert sha(base/'project/BetaGwent0924/workspace/soundbanks/pc/BetaGwent79.bnk')==bank['sha256']
        packed=read(base/'packed-resources-verified.json')
        assert not any('betagwentpremium' in p['path'].lower() for p in packed['entries'])
        project=base/'project/BetaGwent0924/workspace'
        assert not any('betagwentpremium' in p.as_posix().lower() for p in project.rglob('*'))
        release=read(E/f"stage{stage}-release-{bank['language']}.json")
        with zipfile.ZipFile(release['archive']) as archive:
            assert not any('premium' in n.lower() for n in archive.namelist())
            # REDkit embeds the bank in soundspc.cache; no loose .bnk is shipped.
            cache=archive.read('Mods/modBetaGwent0924/content/soundspc.cache')
            native_bank=Path(bank['bank']).read_bytes()
            assert cache[:4]==b'CS3W' and len(cache)==len(native_bank)+104
            assert cache[64:64+len(native_bank)]==native_bank,'archive contains a stale dialogue bank'
            cooked_audio=read(base/'audio-output-verified.json')
            assert cooked_audio['embeddedBankIdentical'] and cooked_audio['bankSha256']==bank['sha256']
            assert hashlib.sha256(cache).hexdigest()==cooked_audio['cacheSha256']
    report=read(E/(report_name+'-base.json'))
    report.update(premiumPortraitsExcluded=True,dialogueBanksVerified=mix,ux135=read(E/'ux135.json'),audio135=read(E/'audio135.json'))
    (E/(report_name+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print('PASS: actual '+version+' RU/EN, current regressions, native menus/scripts, dialogue banks, CRC, manifest and SHA-256; no Redux or premium portraits')

if __name__=='__main__':main()
