"""Forward-port this work onto the frozen universal 0.8.1 sources, in isolation.

Uses frozen Stage 202 as the common base. Never edits universal081 or installs a mod.
"""
from pathlib import Path
import difflib,hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/features082'
SEED=ROOT/'BetaGwent/build/universal081'
OUT=BASE/'candidate'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from prepare_scripts import prepare
def read(p):
    raw=p.read_bytes();return raw.decode('utf16' if raw[:2]==b'\xff\xfe' else 'utf-8-sig').replace('\r\n','\n')
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def port(old,new,seed):
    a=old.splitlines(True);b=new.splitlines(True)
    for group in difflib.SequenceMatcher(None,a,b,autojunk=False).get_grouped_opcodes(3):
        oldblock=''.join(a[group[0][1]:group[-1][2]])
        newblock=''.join(b[group[0][3]:group[-1][4]])
        if seed.count(oldblock)!=1:raise RuntimeError('Forward-port anchor ambiguous: '+oldblock[:120])
        seed=seed.replace(oldblock,newblock)
    return seed
if OUT.exists():raise SystemExit('Use a fresh candidate directory; the existing candidate is retained.')
OUT.mkdir(parents=True)
shutil.copytree(SEED/'nextgen-sources',OUT/'scripts')
for name in ['deckBuilder.ws','collectionProfile.ws','developmentBoardMenu.ws','shopRuntime.ws']:
    rel=Path('BetaGwent/development/scripts/game/betagwent')/name
    p=OUT/'scripts/game/betagwent'/name
    old=read(ROOT/'BetaGwent/build/stage202/ru/sources/scripts/game/betagwent'/name)
    if name=='developmentBoardMenu.ws':
        old=old.replace('BetaGwentTextLanguage137(FactsQueryLatestValue("bg_text_language"))','FactsQueryLatestValue("bg_text_language")')
        old=old[:old.index('\nfunction BetaGwentTextLanguage137(')].rstrip()+'\n'
    write(p,port(old,read(ROOT/rel),read(p)))
shutil.copytree(SEED/'ui',OUT/'ui')
p=OUT/'ui/src/BetaGwentBoard.as';rel=Path('BetaGwent/ui/src/BetaGwentBoard.as')
old=read(ROOT/'BetaGwent/build/stage202/common/ui/src/BetaGwentBoard.as');new=read(ROOT/rel)
# Geometry is deliberately changed on the universal pair, outside the generic port.
new=new.replace('editorSmallButton(content,BetaGwentTextLanguage.label(),56,24,364,42,true,cycleTextLanguage);','editorSmallButton(content,BetaGwentTextLanguage.label(),52,28,276,42,true,cycleTextLanguage);')
s=port(old,new,read(p))
s=s.replace('textChoiceLabel(),52,28,276,42','textChoiceLabel(),56,24,364,42').replace('voiceChoiceLabel(),340,28,276,42','voiceChoiceLabel(),56,78,364,42')
assert s.count('textChoiceLabel(),56,24,364,42')==1 and s.count('voiceChoiceLabel(),56,78,364,42')==1
write(p,s)
for directory in ['src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']:
    (OUT/'ui'/directory).mkdir(exist_ok=True)
    for source in (OUT/'ui/src').glob('*.as'):shutil.copy2(source,OUT/'ui'/directory/source.name)
# Preserve 0.8.1 artwork and universal languages. Compile into new files only.
manifest=json.loads((SEED/'ui-inputs.json').read_text('utf8'))
manifest['sources']={p.name:sha(p) for p in (OUT/'ui/src').glob('*.as')}
(OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2)+'\n','utf8')
# Reuse the audited vanilla 1.32 input and lower the new common code afresh.
prep=json.loads((SEED/'classic-prepared/preparation.json').read_text('utf8'))
audit_path=Path(prep['audit']);audit=json.loads(audit_path.read_text('utf8'))
audit['sourceScripts']={p.relative_to(OUT/'scripts').as_posix():sha(p) for p in (OUT/'scripts').rglob('*.ws')}
audit['sourceScriptCount']=len(audit['sourceScripts'])
audit['sourceValidationPassed']=False # Candidate compilation is a separate step.
audit['featureCandidate']='0.8.2'
adir=OUT/'classic-audit';shutil.copytree(audit_path.parent/'baseline/vanilla-targets',adir/'baseline/vanilla-targets')
shutil.copytree(OUT/'scripts',adir/'baseline/scripts')
(adir/'audit.json').write_text(json.dumps(audit,indent=2)+'\n','utf8')
prepare(adir,OUT/'classic-prepared')
print(json.dumps({'candidate':str(OUT),'scripts':len(audit['sourceScripts']),'universal081Modified':False,'gameInstalled':False}))
