import re,sys,pathlib,json,collections
RU=re.compile(r'"[^"\n]*[А-Яа-яЁё][^"\n]*"')
out=[]
files=list(pathlib.Path('ui/src').glob('*.as'))+list(pathlib.Path('development/scripts/game/betagwent').glob('*.ws'))
for f in files:
    if f.name=='BetaGwentTextData.as':continue
    for n,line in enumerate(f.read_text('utf-8-sig',errors='replace').splitlines(),1):
        lits=RU.findall(line)
        if not lits:continue
        if 'LogChannel' in line and len(lits)==1 and 'Notification' not in line:continue
        # literal followed or preceded by + and non-literal
        if re.search(r'"[^"\n]*[А-Яа-яЁё][^"\n]*"\s*\+\s*[A-Za-z_(]',line) or re.search(r'[A-Za-z_)\]]\s*\+\s*"[^"\n]*[А-Яа-яЁё]',line):
            out.append((str(f),n,line.strip()[:260]))
c=collections.Counter(o[0] for o in out)
print(len(out));print(c.most_common())
json.dump(out,open('/tmp/concat.json','w'),ensure_ascii=False,indent=0)
