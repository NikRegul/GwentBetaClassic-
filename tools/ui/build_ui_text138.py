"""Generate the small 0.6.2 UI dictionary supplement without rewriting 0.6.1 resources."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'data/beta924/design/ui-polish138.json'
LOCALES=['ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw']

def dictionaries():
    data=json.loads(SOURCE.read_text('utf8'));keys=data.pop('keys')
    assert len(set(keys))==len(keys)
    result={}
    for locale in LOCALES:
        values=keys if locale=='ru_ru' else data[locale]
        assert len(values)==len(keys),(locale,len(values),len(keys))
        assert all(isinstance(v,str) and v for v in values)
        table=dict(zip(keys,values));table.update({k.upper():v.upper() for k,v in list(table.items())})
        result[locale]=table
    return result

def generate(output):
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(dictionaries(),ensure_ascii=False,indent=2)+'\n','utf8')
    print('Generated 13-language UI supplement:',output)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=ROOT/'BetaGwent/drafts/ui-polish138/evidence/translations.json')
    generate(p.parse_args().output)
