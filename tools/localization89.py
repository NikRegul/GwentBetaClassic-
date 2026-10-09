"""Build fixed-language sources without editing Russian development sources."""
from pathlib import Path
import argparse,json,re,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
PAT=re.compile(r'"(?:\\.|[^"\\])*"')
CYR=re.compile('[А-Яа-яЁё]')
def strings():
    c=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text('utf8'))
    ru,en=c['localization']['ru_ru'],c['localization']['en_us']
    result={}
    sys.path.insert(0,str(ROOT/'tools'))
    from ws_codegen import localized_plain_text
    for k,v in ru.items():
        if k in en:
            result[v]=en[k];result[localized_plain_text(v)]=localized_plain_text(en[k])
    result.update(json.loads((ROOT/'data/beta924/design/english89.json').read_text('utf8')) if (ROOT/'data/beta924/design/english89.json').exists() else {})
    return result
def sources():
    return list((ROOT/'BetaGwent/ui/src').glob('*.as'))+list((ROOT/'BetaGwent/development/scripts/game/betagwent').glob('*.ws'))+list((ROOT/'BetaGwent/scripts/game/betagwent').glob('*.ws'))+[ROOT/'tools/core-check/src/coreChecks.ws']
def value(literal):
    # WS and AS string escaping agrees for the generated values used here.
    try:return json.loads(literal)
    except ValueError:return literal[1:-1]
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['inventory','sources']);p.add_argument('--output-dir',type=Path);a=p.parse_args()
    lookup=strings();unknown={}
    for f in sources():
        for m in PAT.finditer(f.read_text('utf-8-sig')):
            v=value(m.group())
            if CYR.search(v) and v not in lookup:unknown.setdefault(v,[]).append(f.name)
    dest=a.output_dir or ROOT/'BetaGwent/build/release89';dest.mkdir(parents=True,exist_ok=True)
    (dest/'untranslated.json').write_text(json.dumps(unknown,ensure_ascii=False,indent=2),'utf8')
    print('Untranslated unique literals:',len(unknown))
    if a.action=='inventory':return
    if unknown:raise SystemExit('Finish english89.json first')
    for f in sources():
        category='ui' if f.suffix=='.as' else 'scripts/game/betagwent'
        out=dest/'en-source'/category/f.name;out.parent.mkdir(parents=True,exist_ok=True)
        s=f.read_text('utf-8-sig')
        def replace(m):
            v=value(m.group());return json.dumps(lookup[v],ensure_ascii=False) if CYR.search(v) else m.group()
        translated=PAT.sub(replace,s)
        if f.name=='BetaGwentBoard.as':translated=translated.replace('nameRussian:Boolean=true;', 'nameRussian:Boolean=false;')
        out.write_text(translated,'utf-8-sig' if f.suffix=='.ws' else 'utf8')
if __name__=='__main__':main()
