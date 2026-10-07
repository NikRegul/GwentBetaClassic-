"""Import admitted self-play constants after verifying their exact rule set."""
from pathlib import Path
import argparse, hashlib, json, re, shutil
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2]
TARGET=ROOT/'BetaGwent/development/scripts/game/betagwent/duelAITraining.ws'
MARKER='// EXPORT_WEIGHTS_BEGIN'
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('training',type=Path);args=ap.parse_args()
 folder=args.training.resolve();report=json.loads((folder/'export/report.json').read_text('utf8'))
 state=json.loads((folder/'checkpoint.json').read_text('utf8'))
 manifest=json.loads((folder/'source-manifest.json').read_text('utf8'))
 fingerprint=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 if fingerprint!=report['rulesHash'] or fingerprint!=state['rulesHash']:raise ValueError('Mismatched training evidence')
 for relative,digest in manifest.items():
  path=(ROOT/relative).resolve()
  if not path.is_relative_to(ROOT):raise ValueError('Manifest path outside workspace')
  if path==TARGET:
   data=path.read_text('utf-8-sig').split(MARKER)[0].encode()
  elif path.suffix=='.ws':data=path.read_text('utf-8-sig').encode()
  else:data=path.read_bytes()
  if hashlib.sha256(data).hexdigest()!=digest:raise ValueError('Rules changed since training: '+relative)
 if not report['hasLearnedPolicy']:
  print('No policy passed the promotion gates; current game AI retained.');return
 if report['generation']!=state['generation'] or report['promotions']!=state['promotions'] or not state['promotions']:raise ValueError('No matching admitted champion; wait for the generation to finish')
 exported=(folder/'export/duelAITraining.ws').read_text('utf-8-sig')
 if exported.split(MARKER)[0]!=TARGET.read_text('utf-8-sig').split(MARKER)[0]:raise ValueError('Feature code differs')
 # Recreate constants from the admitted checkpoint instead of trusting an edited export.
 from train import export
 scratch=ROOT/'BetaGwent/build/ai-import-check';scratch.mkdir(parents=True,exist_ok=True)
 export(state['champion'],scratch,fingerprint,report)
 if exported!=(scratch/'export/duelAITraining.ws').read_text('utf-8-sig'):raise ValueError('Export differs from admitted champion')
 backup=ROOT/'BetaGwent/training/backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f')/'duelAITraining.ws'
 backup.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(TARGET,backup)
 TARGET.write_text(exported,encoding='utf-8-sig')
 print('Imported: '+str(TARGET));print('Backup: '+str(backup))
 print('Offline candidate only. Validate representative NPC games before distributing.')
if __name__=='__main__':main()
