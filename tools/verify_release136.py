"""Verify fresh 0.6.0 RU/EN archives, leader resources and independent text selection."""
from pathlib import Path
import hashlib,json,zipfile,struct,sys,zlib
import verify_release135
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()

def compare_audio_cache(previous,current):
    # Fresh REDkit cooks change the four-byte header field at offset 12.
    # The remaining header, complete embedded bank and trailing index must match.
    assert previous[:4]==current[:4]==b'CS3W'
    assert len(previous)==len(current) and len(current)>=104
    assert previous[:12]==current[:12] and previous[16:]==current[16:],'audio cache payload changed'
    return dict(cacheByteIdentical=previous==current,embeddedBankUnchanged=True,
                oldHeaderField12=previous[12:16].hex(),newHeaderField12=current[12:16].hex())
def font_payloads(path):
    sys.path.insert(0,str(ROOT/'tools/ui'))
    from update_board_resource import validate_resource,unpack_root
    resource,_=validate_resource(path);data=unpack_root(resource)[1]
    body=zlib.decompress(data[8:]) if data[:3] in (b'CWS',b'CFX') else data[8:]
    offset=(5+4*(body[0]>>3)+7)//8+4;fonts=[]
    while offset<len(body):
        tag=struct.unpack_from('<H',body,offset)[0];offset+=2;code,size=tag>>6,tag&63
        if size==63:size=struct.unpack_from('<I',body,offset)[0];offset+=4
        chunk=body[offset:offset+size];offset+=size
        # Symbol IDs may change; actual font data must remain identical.
        if code in (10,48,75,91):fonts.append(hashlib.sha256(chunk[2:]).hexdigest())
    assert fonts
    return sorted(fonts)

def main():
    verify_release135.main(stage=136,version='0.6.0',report_name='validation136-native')
    checks={name:read(E/(name+'.json')) for name in ['ui136','leader-checks136','text-language136','leaders136','profile136','audio-cache136']}
    for report in checks.values():
        for name,digest in report['sources'].items():assert sha(ROOT/name)==digest,('stale 0.6.0 evidence',name)
    assert checks['ui136']['checks']>=41
    assert checks['profile136']['checks']>=30
    assert checks['audio-cache136']['checks']>=8 and checks['audio-cache136']['actualVerifier']
    assert checks['leader-checks136']['introExcluded'] and checks['leader-checks136']['leaders']==21
    assert checks['leader-checks136']['packagingGuardChecks']>=6
    assert checks['text-language136']['originalLanguages']==13
    fonts=[]
    for language in ('ru','en'):
        baseline=ROOT/f'BetaGwent/build/release135/{language}/project/BetaGwent0924/workspace/betagwent/betagwent_board.redswf'
        expected=font_payloads(baseline)
        for resource in (ROOT/f'BetaGwent/build/stage136/{language}/resources').glob('*.redswf'):
            assert font_payloads(resource)==expected,('fonts changed from 0.5.4',resource)
            fonts.append(dict(language=language,resource=str(resource),sha256=sha(resource),definitions=len(expected)))
    assert len(fonts)==8
    (E/'fonts136.json').write_text(json.dumps(dict(unchangedFrom054=True,menus=fonts,newAgentFontsIncluded=False),indent=2)+'\n','utf8')
    report=read(E/'validation136-native.json');comparison=[]
    previous_release=read(E/'validation135.json')
    assert previous_release['version']=='0.5.4'
    previous_hashes={p['language']:p['sha256'] for p in previous_release['packages']}
    for package in report['packages']:
        lang=package['language'];base=ROOT/f'BetaGwent/build/release136/{lang}'
        packed=read(base/'packed-resources-verified.json')
        portraits=[p for p in packed['entries'] if '/betagwentleaders/' in p['path'].lower().replace('\\','/')]
        expected={r['path'].lower() for r in checks['leaders136']['resources'].values()}
        assert len(portraits)==21 and {p['path'].lower().replace('\\','/') for p in portraits}==expected
        cooked=read(base/'cooked-leaders-verified.json');assert len(cooked)==21
        with zipfile.ZipFile(package['archive']) as new:
            audio=new.getinfo('Mods/modBetaGwent0924/content/soundspc.cache')
            assert len([n for n in new.namelist() if n.endswith('soundspc.cache')])==1
            old=ROOT/f'BetaGwent/release/GwentBetaClassic-0.5.4-{lang.upper()}.zip'
            assert sha(old)==previous_hashes[lang],'0.5.4 archive changed'
            with zipfile.ZipFile(old) as previous:
                audio_comparison=compare_audio_cache(previous.read('Mods/modBetaGwent0924/content/soundspc.cache'),new.read('Mods/modBetaGwent0924/content/soundspc.cache'))
            comparison.append(dict(language=lang,oldBytes=old.stat().st_size,newBytes=package['bytes'],
                addedBytes=package['bytes']-old.stat().st_size,audioCompressedBytes=audio.compress_size,
                singleVoiceBank=True,voiceBankUnchangedFrom054=True,audioComparison=audio_comparison))
    report.update(checks136=checks,sizeComparison054=comparison,loopOnlyLeaders=21,otherAnimatedCards=0,fontsUnchangedFrom054=True,
        textLanguages=['ru','en'],voicePackaging='one voice language per archive',nativeGameTested=False)
    (E/'validation136.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(version='0.6.0',passed=True,packages=report['packages'],sizeComparison054=comparison),ensure_ascii=False))
if __name__=='__main__':main()
