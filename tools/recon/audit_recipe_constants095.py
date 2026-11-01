"""Compare explicitly retained numeric recipe variables with original beta graphs.

This audits the values, not whether the runtime uses each value correctly.
"""
from pathlib import Path
import hashlib,json,sys

ROOT=Path(__file__).resolve().parents[2]
catalog_path=ROOT/'data/beta924/normalized/catalog.json'
catalog=json.loads(catalog_path.read_text('utf8'))
graphs={a['recordKey']:a for a in catalog['abilities']}
records=[];missing=[];differences=[];without_graph=[];recipes=0
for name in ['neutral','monsters','northern','nilfgaard','scoiatael','skellige']:
    p=ROOT/f'data/beta924/duel/{name}.json'
    for recipe in json.loads(p.read_text('utf8'))['cards']:
        recipes+=1
        if not recipe.get('abilityRecordKey'):
            without_graph.append(recipe['templateId'])
            if recipe.get('originalVariables'):missing.append(dict(id=recipe['templateId'],reason='No graph for retained variables'))
            continue
        a=graphs[recipe['abilityRecordKey']]
        variables={v['attributes']['Name']:v['attributes'] for section in a['sourceTree']['children']
                   if section['tag'].endswith('Variables') for v in section['children']}
        for key,value in recipe.get('originalVariables',{}).items():
            if isinstance(value,bool) or not isinstance(value,(int,float)):continue
            source=variables.get(key)
            rec=dict(id=recipe['templateId'],recipe=name,graph=a['nid'],variable=key,recipeValue=value)
            if source is None or source.get('Type') not in ('IntVar','FloatVar'):
                missing.append(rec);continue
            rec['sourceValue']=float(source['V'])
            records.append(rec)
            if rec['sourceValue']!=value:differences.append(rec)
report=dict(recipes=recipes,withoutGraph=without_graph,checks=len(records),missing=missing,differences=differences,
    catalogSha256=hashlib.sha256(catalog_path.read_bytes()).hexdigest(),records=records,
    scope='Explicit originalVariables numeric constants in six faction recipes; runtime use and unrecorded graph constants are separate.',
    allCardSemanticComparisonComplete=False)
if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({k:report[k] for k in ['recipes','checks','missing','differences']}))
if missing or differences:sys.exit(1)
