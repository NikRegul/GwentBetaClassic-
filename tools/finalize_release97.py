"""Cross-check both 0.2.4 archives, frozen scripts and inline texture pixels."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/ui'))
from read_gui_resource import GuiResource
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 records={};textures=[]
 for lang in ('ru','en'):
  record=json.loads((ROOT/f'docs/evidence/stage97-release-{lang}.json').read_text('utf8'));archive=Path(record['archive'])
  assert record['version']=='0.2.4' and sha(archive)==record['archiveSha256'] and record['archiveVerified']
  base=ROOT/f'BetaGwent/build/release97/{lang}'
  compilation=json.loads((ROOT/f'BetaGwent/build/board-compile97{lang}-final/result.json').read_text('utf8'))
  assert compilation['exitCode']==0 and not compilation['timedOut'] and compilation['patchSourcesUnchangedDuringCompile'] and len(compilation['patchSourcesBefore'])==61
  log=(ROOT/f'BetaGwent/build/board-compile97{lang}-final/stdout.txt').read_text('utf8',errors='replace')
  assert 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   for f in record['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
   assert hashlib.sha256(z.read('Mods/modBetaGwent0924/content/precompiled.rsblob')).hexdigest()==sha(ROOT/f'BetaGwent/build/board-compile97{lang}-final/compiled/blob.rsblob')
  for f in compilation['patchSourcesBefore']:assert sha(base/'project/BetaGwent0924/workspace/scripts'/f['path'])==f['sha256']
  packed=json.loads((base/'packed-resources-verified.json').read_text('utf8'));assert packed['guiStoredUncompressed'] and packed['packedPayloadsVerified']
  assert not any(e['path'].endswith('.redswfx') for e in packed['entries'])
  records[lang]={k:record[k] for k in ('archive','archiveBytes','archiveSha256')}
 for name in ('betagwent_board.redswf','betagwent_decks.redswf','betagwent_npc00.redswf'):
  ru=GuiResource(ROOT/f'BetaGwent/build/release97/ru/cooked/betagwent/{name}');en=GuiResource(ROOT/f'BetaGwent/build/release97/en/cooked/betagwent/{name}')
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
 report=dict(version='0.2.4',archives=records,scriptSourcesPerLanguage=61,textures=textures,packageIntegrityVerified=True,nativeRuntimeVerified=False,installedGameModified=False)
 (ROOT/'docs/evidence/stage97-final.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
