"""Cross-check both 0.2.4 archives, frozen scripts and inline texture pixels."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/ui'))
from read_gui_resource import GuiResource
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--stage',type=int,default=97)
 parser.add_argument('--version',default='0.2.4')
 parser.add_argument('--compiled-stage',type=int,default=97)
 parser.add_argument('--compiled-ru',type=Path)
 parser.add_argument('--compiled-en',type=Path)
 args=parser.parse_args();stage=args.stage;version=args.version;compiled_stage=args.compiled_stage
 records={};textures=[]
 if stage>=98:
  compact=json.loads((ROOT/'docs/evidence/compact-art98.json').read_text('utf8'))
  for item in compact['records']:
   assert sha(Path(item['source']))==item['sourceSha256'] and sha(Path(item['output']))==item['sha256']
 for lang in ('ru','en'):
  record=json.loads((ROOT/f'docs/evidence/stage{stage}-release-{lang}.json').read_text('utf8'));archive=Path(record['archive'])
  assert record['version']==version and sha(archive)==record['archiveSha256'] and record['archiveVerified']
  base=ROOT/f'BetaGwent/build/release{stage}/{lang}'
  compile_dir=(args.compiled_ru if lang=='ru' else args.compiled_en) or ROOT/f'BetaGwent/build/board-compile{compiled_stage}{lang}-final'
  compilation=json.loads((compile_dir/'result.json').read_text('utf8'))
  assert compilation['exitCode']==0 and not compilation['timedOut'] and compilation['patchSourcesUnchangedDuringCompile'] and len(compilation['patchSourcesBefore'])==61
  log=(compile_dir/'stdout.txt').read_text('utf8',errors='replace')
  assert 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   for f in record['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
   assert hashlib.sha256(z.read('Mods/modBetaGwent0924/content/precompiled.rsblob')).hexdigest()==sha(compile_dir/'compiled/blob.rsblob')
  for f in compilation['patchSourcesBefore']:assert sha(base/'project/BetaGwent0924/workspace/scripts'/f['path'])==f['sha256']
  packed=json.loads((base/'packed-resources-verified.json').read_text('utf8'));assert packed['guiStoredUncompressed'] and packed['packedPayloadsVerified']
  if stage>=98:
   assert packed['guiLimitMiB']==55
   assert all(e['size']<55*1024**2 for e in packed['entries'] if e['path'].endswith('.redswf'))
  assert not any(e['path'].endswith('.redswfx') for e in packed['entries'])
  records[lang]={k:record[k] for k in ('archive','archiveBytes','archiveSha256')}
  records[lang]['compilation']=str(compile_dir)
 for name in ('betagwent_board.redswf','betagwent_decks.redswf','betagwent_npc00.redswf'):
  ru=GuiResource(ROOT/f'BetaGwent/build/release{stage}/ru/cooked/betagwent/{name}');en=GuiResource(ROOT/f'BetaGwent/build/release{stage}/en/cooked/betagwent/{name}')
  assert len(ru.exports)==len(en.exports)
  # The exporter can number the same bitmap pages differently in each build.
  # Each movie's ordered linkages were already checked against its own input.
  def pixel_set(resource):
   items=[]
   for chunk in resource.exports[1:]:
    _,end=resource.properties_at(chunk['data'])
    items.append(hashlib.sha256(chunk['data'][end:]).hexdigest())
   return Counter(items)
  assert pixel_set(ru)==pixel_set(en)
  textures.append(dict(menu=name,pages=len(ru.exports)-1,ruEnPixelBlockSetsIdentical=True))
 for path in ('turn-liveness97.json','aglais94.json'):
  result=json.loads((ROOT/'docs/evidence'/path).read_text('utf8'));assert result['passed']
 report=dict(version=version,stage=stage,compiledStageDefault=compiled_stage,archives=records,scriptSourcesPerLanguage=61,textures=textures,packageIntegrityVerified=True,nativeRuntimeVerified=False,installedGameModified=False)
 (ROOT/f'docs/evidence/stage{stage}-final.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
