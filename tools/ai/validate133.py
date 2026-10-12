"""Run source regressions in an isolated copy; never overwrite shared test evidence."""
from pathlib import Path
import argparse,shutil,subprocess,json,time,concurrent.futures,hashlib,sys
ROOT=Path(__file__).resolve().parents[2]
AI=['check_consume_self','scenarios123','scenarios124','scenarios125','check_followups126','check_engines126','check_weather_visual126','check_decisive127','check_ships127','check_concede127','check_tutor127','check_preventive127','check_clearrisk127','check_draug127','check_combo127','check_no_targets127','check_deck_combos128','check_losing131','check_cavalry131','check_ciri131','check_public_response113','scenarios111','scenarios112','scenarios114','scenarios115','scenarios118','scenarios119','scenarios120','scenarios121','check_policy133']
AI.append('check_hidden_information133')
UI=['check_controller123','check_catalog123','check_optional124','check_halfcast126','check_controller126','check_timing126','check_card_presentation126','check_followups127','check_mulligan121','check_presentation133']
def main():
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--workers',type=int,choices=[1,2],default=2);a=p.parse_args();out=a.output.resolve()
 if (out/'inputs.json').exists():raise ValueError('Use a fresh output directory')
 out.mkdir(parents=True,exist_ok=True);files=set()
 for name in ['tools/ai','tools/ui','BetaGwent/scripts','BetaGwent/development/scripts','BetaGwent/ui/src','data/beta924']:
  files.update(f for f in (ROOT/name).rglob('*') if f.suffix in {'.ws','.as','.json','.js','.py','.ps1'} and '__pycache__' not in f.parts)
 files.update(f for f in (ROOT/'tools').glob('*') if f.suffix in {'.py','.ps1'})
 files.add(ROOT/'BetaGwent/audio/generated/duelAudioCatalog-en.ws')
 digests={}
 for f in sorted(files):
  name=f.relative_to(ROOT);target=out/name;target.parent.mkdir(parents=True,exist_ok=True);data=f.read_bytes();target.write_bytes(data);digests[str(name)]=hashlib.sha256(data).hexdigest()
 (out/'docs/evidence').mkdir(parents=True,exist_ok=True);(out/'logs').mkdir(exist_ok=True)
 (out/'inputs.json').write_text(json.dumps(digests,indent=2),'utf8')
 if not (out/'frozen/manifest.json').exists():subprocess.run([sys.executable,'-X','utf8','tools/ai/snapshot.py',str(out/'frozen')],cwd=out,check=True)
 jobs=[(n,['node','tools/ai/'+n+'.js','frozen','docs/evidence/'+n+'.json']) for n in AI]
 jobs += [(n,['node','tools/ui/'+n+'.js','docs/evidence/'+n+'.json']) for n in UI]
 jobs += [('check_rosters128',[sys.executable,'-X','utf8','tools/ai/check_rosters128.py']),('check_intro_audio133',[sys.executable,'-X','utf8','tools/ui/check_intro_audio133.py','frozen','docs/evidence/intro-audio133.json'])]
 def run(job):
  name,cmd=job;start=time.time()
  try:
   r=subprocess.run(cmd,cwd=out,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf8',errors='replace',timeout=240);code=r.returncode;log=r.stdout
  except subprocess.TimeoutExpired as e:code=-1;log=str(e)
  (out/'logs'/(name+'.log')).write_text(log,'utf8')
  return dict(name=name,exitCode=code,seconds=round(time.time()-start,2),passLines=sum(s.startswith('PASS') for s in log.splitlines()),failureTail=log[-2000:] if code else None)
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  for r in pool.map(run,jobs):
   results.append(r);(out/'checks-summary.json').write_text(json.dumps(results,indent=2),'utf8');print(r['name'],r['exitCode'],r['passLines'],flush=True)
 drift=[n for n,h in digests.items() if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
 (out/'source-drift.json').write_text(json.dumps(drift,indent=2),'utf8')
 print('TOTAL',len(results),'FAILED',sum(r['exitCode']!=0 for r in results),'sourceDrift',len(drift),flush=True)
 if any(r['exitCode'] for r in results):raise SystemExit(1)
if __name__=='__main__':main()
