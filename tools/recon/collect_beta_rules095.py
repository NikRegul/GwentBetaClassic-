"""Collect separate engine/UI proofs for the whole-catalog Beta rules audit.

No package/readiness claim: original retail appearance and complete semantic
comparison of all 511 abilities remain separate acceptance work.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tools/ai')]
from build_inputs import CLASSIC_RUNTIME
from snapshot import verify
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--engine',type=Path,required=True);p.add_argument('--ui-build',type=Path,required=True);p.add_argument('--ui-source',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);a=p.parse_args()
 engine=a.engine.resolve();ui_build=a.ui_build.resolve();ui=a.ui_source.resolve();audit=a.audit.resolve();out=audit/'batch-verification.json'
 assert not out.exists(),'Preserve completed proofs; use a fresh audit folder'
 manifest=verify(engine/'rules');fingerprint=manifest['fingerprint']
 groups=read(engine/'regressions/summary.json');assert len(groups)==106 and all(x['exitCode']==0 for x in groups)
 targets={}
 for name,count in [('check_catalog_source095',5622),('check_olaf095',180),('check_xavier095',52),('check_whale094a',2242),('check_ciri_dash_round095',137),('check_mork_order095',120)]:
  file=engine/'regressions'/(name+'.json');r=read(file);assert r['checks']==count and not r['failures'] and r['fingerprint']==fingerprint
  targets[name]=dict(checks=count,path=str(file),sha256=sha(file))
 matrix=read(audit/'all-cards-rounds06.json');assert matrix['fingerprint']==fingerprint and matrix['testedCards']==511 and len(matrix['records'])==4088 and not matrix['failures']
 ng=read(engine/'compile-nextgen-final/result.json');classic_file=CLASSIC_RUNTIME/'runs'/engine.name/'result.json';classic=read(classic_file)
 assert ng['exitCode']==0 and classic['compilePassed'] and not classic['errors']
 for name in ['duelSkellige.ws','duelScoia.ws','duelNeutral.ws']:
  assert sha(engine/'scripts/game/betagwent'/name)==sha(ROOT/'BetaGwent/development/scripts/game/betagwent'/name)
  assert sha(engine/'scripts/game/betagwent'/name)==sha(engine/'rules/sources/BetaGwent/development/scripts/game/betagwent'/name)
 canonical=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as';raw=canonical.read_bytes()
 assert raw[:3]==b'\xef\xbb\xbf' and b'\n' not in raw.replace(b'\r\n',b'')
 for folder in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:assert (ROOT/'BetaGwent/ui'/folder/canonical.name).read_bytes()==raw
 assert sha(ui/'nextgen/ui/src/BetaGwentBoard.as')==sha(canonical)
 assert sha(ui/'classic/ui/src/BetaGwentBoard.as')==sha(ROOT/'tools/features091/BetaGwentBoard_classic093.as')
 patch_file=ui_build/'ui-patch/manifest.json';patch=read(patch_file);menus=[m for platform in patch['platforms'].values() for m in platform['menus']]
 assert len(menus)==8 and all(m['bytes']<65*1024**2 for m in menus)
 for platform in patch['platforms'].values():
  for item in platform['files'].values():assert sha(Path(item['path']))==item['sha256']
 for key,count in [('classic',1013),('nextgen',1005)]:
  r=read(ui_build/('editor-valid-'+key+'.json'));assert r['checks']==count and not r['failures']
  r=read(ui_build/('editor-layout-'+key+'.json'));assert r['checks']==55 and not r['failures'] and r['largePreview'][2]>=230
  for folder in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:assert sha(ui/key/'ui'/folder/canonical.name)==sha(ui/key/'ui/src'/canonical.name)
 record=dict(technicalBatchChecksPassed=True,engineFingerprint=fingerprint,regressionGroups=len(groups),targeted=targets,cards=511,technicalCardCases=4088,
  nativeCompilers=dict(classicPassed=True,nextgenPassed=True,classicResult=str(classic_file),nextgenResult=str(engine/'compile-nextgen-final/result.json')),
  ui=dict(source=str(ui),patchManifest=str(patch_file),patchManifestSha256=sha(patch_file),menus=8,maxMenuBytes=max(m['bytes'] for m in menus),canonicalBoardSha256=sha(canonical),layoutChecksPerPlatform=55,validVfxChecks=dict(classic=1013,nextgen=1005)),
  allCardSemanticComparisonComplete=False,nativeGameplayVerified=False,updatedArchivesCreated=False,installed=False,published=False)
 out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(record,ensure_ascii=False))
if __name__=='__main__':main()
