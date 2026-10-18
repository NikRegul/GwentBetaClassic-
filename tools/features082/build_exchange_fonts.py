"""Add missing exchange glyphs to the four existing CJK language resources."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release082-rc3'
sys.path[:0]=[str(ROOT/'tools/ui'),str(ROOT/'tools/classic132')]
from formats import Resource
def main():
    file=ROOT/'tools/ui/build_languages137.py';source=file.read_text('utf8')
    source=source.replace("WORK = ROOT / 'BetaGwent/build/text137'","WORK = ROOT / 'BetaGwent/build/release082-rc3/exchange-fonts'")
    marker='    dictionary.update({k.upper(): v.upper() for k, v in list(dictionary.items()) if k})'
    extra='''    from build_ui_text138 import dictionaries
    dictionary.update(dictionaries()[locale])
    additions=json.loads((ROOT/'data/beta924/design/ui-exchange082.json').read_text('utf8'))
    values=additions.get(locale,additions['es_es'] if locale=='es_mx' else additions['keys'])
    dictionary.update(dict(zip(additions['keys'],values)))
'''
    assert source.count(marker)==1;source=source.replace(marker,extra+marker)
    namespace={'__file__':str(file),'__name__':'exchange_fonts082'};exec(compile(source,str(file),'exec'),namespace)
    report={}
    for index,(locale,label) in enumerate(namespace['LANGUAGES'],1):
        if locale not in ['jp_jp','kr_kr','zh_cn','zh_tw']:continue
        row=namespace['build'](locale,label,index);report[locale]=row
        source=Path(row['path']);source=BUILD/'exchange-fonts/resources'/source
        raw=source.read_bytes()
        for platform in ['nextgen','classic']:
            p=BUILD/platform/'extra-resources'/row['path'];p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(Resource(raw).classic() if platform=='classic' else raw)
    (BUILD/'exchange-fonts.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
if __name__=='__main__':main()
