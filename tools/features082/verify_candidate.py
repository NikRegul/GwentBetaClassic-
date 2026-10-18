"""Verify the local 0.8.2 candidate and retain compilation/test provenance."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/features082'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from build_resources import strip_menu_authoring
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
compiled=json.loads((BASE/'universal-compile/result.json').read_text('utf8'))
assert compiled['exitCode']==0 and compiled['patchSourcesUnchangedDuringCompile'] and not compiled['timedOut']
actual={p.relative_to(BASE/'candidate/scripts').as_posix():sha(p) for p in (BASE/'candidate/scripts').rglob('*.ws')}
assert actual=={r['path']:r['sha256'] for r in compiled['patchSourcesAfter']},'Candidate WS differs from compiled input'
classic=BASE/'candidate/classic-prepared'
prep=json.loads((classic/'preparation.json').read_text('utf8'))
scripts=classic/'Mods/modBetaGwentClassic132/content/scripts'
assert prep['outputScripts']=={p.relative_to(scripts).as_posix():sha(p) for p in scripts.rglob('*.ws')}
menus=json.loads((BASE/'menus-final/menus.json').read_text('utf8'))
assert len(menus['menus'])==4
cooked=BASE/'cooked-menus';cooked.mkdir(exist_ok=True)
rows=[]
for row in menus['menus']:
    p=Path(row['path']);assert sha(p)==row['sha256'] and row['originalTextureChunksPreserved']
    raw=strip_menu_authoring(p.read_bytes());assert len(raw)<63*1024**2
    out=cooked/p.name;out.write_bytes(raw)
    rows.append(dict(entry=row['entry'],path=str(out),bytes=len(raw),MiB=round(len(raw)/1048576,3),sha256=sha(out),originalTextureChunksPreserved=True))
names=['deckBuilder.ws','collectionProfile.ws','developmentBoardMenu.ws','shopRuntime.ws']
files=[ROOT/'BetaGwent/development/scripts/game/betagwent'/n for n in names]
files+=[ROOT/'BetaGwent/ui'/d/'BetaGwentBoard.as' for d in ['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']]
for p in files:
    raw=p.read_bytes();assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'')
report=dict(featureVersion='0.8.2',sourceFiles={str(p.relative_to(ROOT)):sha(p) for p in files},
    nextgenCompilationPassed=True,nextgenScriptCount=len(actual),classicScriptCount=len(prep['outputScripts']),
    classicNativeCompilationRun=False,classicRedkitDiagnosticPassed=False,
    witcherScriptTests=json.loads((ROOT/'docs/evidence/features082-ws.json').read_text('utf8')),
    actionScriptTests=json.loads((ROOT/'docs/evidence/features082-ui.json').read_text('utf8')),
    menus=rows,guiLimitMiB=63,gameInstalled=False,gameTested=False,stableRelease=False,
    pending=['Native 1.32 compilation and gameplay acceptance','OS clipboard round trip in both games','Save/load and normal/NG+ purchases','Localization of new exchange dialogs before multilingual stable'])
(BASE/'menu-budget.json').write_text(json.dumps(rows,indent=2)+'\n','utf8')
(ROOT/'docs/evidence/features082.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps({'wsChecks':report['witcherScriptTests']['checks'],'uiChecks':report['actionScriptTests']['checks'],'maxMenuMiB':max(r['MiB'] for r in rows),'nextgenCompilationPassed':True,'classicNativeCompilationRun':False,'gameInstalled':False}))
