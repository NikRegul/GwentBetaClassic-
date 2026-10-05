"""Prepare English catalogue and exact localized-literal correspondence."""
from pathlib import Path
import json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'tools/build_full_catalog.py'
s=p.read_text('utf8').replace("source['localization']['ru_ru']","source['localization'][LOCALE]")
for name in ('BetaGwentCardTags','BetaGwentCardText','BetaGwentFullCatalog'):
    s=s.replace("(ROOT/'BetaGwent/ui/src/"+name+".as')","(UI_OUT/'"+name+".as')")
s=s.replace("target=ROOT/'data/beta924/planning/full_catalog.json'","target=UI_OUT/'full_catalog.json' if args.output_dir else ROOT/'data/beta924/planning/full_catalog.json'")
p.write_text(s,'utf8')
out=ROOT/'BetaGwent/build/release89/en-generated'
subprocess.run([sys.executable,str(p),'--language','en','--output-dir',str(out)],check=True)
lookup={}
def load(name,folder):
    text=(folder/(name+'.as')).read_text('utf8')
    if name=='BetaGwentCardTags':return {int(k):json.loads(v) for k,v in re.findall(r'values\[(\d+)\]=("(?:\\.|[^"\\])*");',text)}
    if name=='BetaGwentCardText':return {int(k):json.loads(v) for k,v in re.findall(r'values\[(\d+)\]=(.*);',text)}
    return {x['templateId']:x for x in json.loads((folder/'full_catalog.json').read_text('utf8'))['cards']}
for name in ('BetaGwentCardTags','BetaGwentCardText'):
    ru=load(name,ROOT/'BetaGwent/ui/src');en=load(name,out)
    for k,v in ru.items():
        if isinstance(v,str):lookup[v]=en[k]
        else:
            for key,x in v.items():
                if isinstance(x,str):lookup[x]=en[k][key]
p=ROOT/'data/beta924/design/english89.json'
lookup.update(json.loads(p.read_text('utf8')) if p.exists() else {})
p.write_text(json.dumps(lookup,ensure_ascii=False,indent=2),'utf8')
print('Resolved canonical text/tag mappings:',len(lookup))
