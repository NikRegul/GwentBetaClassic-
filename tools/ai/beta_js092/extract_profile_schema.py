"""Read inherited scalar declarations from source text, never execute C#."""
from pathlib import Path
import hashlib,json,math,re
ROOT=Path(__file__).resolve().parents[3]
source=ROOT/'BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay.AI/AIPersonality.cs'
raw=source.read_bytes();text=raw.decode('utf-8-sig')
keys=re.findall(r'public\s+\w+\s+(\w+)Inherited\s*\{',text)
fields={}
for key in keys:
    declaration=re.search(r'\bpublic\s+(\w+)\s+'+key+r'(?:\s*=\s*([^;\n]+))?\s*;',text)
    kind,expression=declaration.groups()
    if expression is None:value=False if kind=='bool' else 0
    elif expression in ('true','false'):value=expression=='true'
    elif expression=='Math.Sqrt(2.0)':value=math.sqrt(2)
    else:
        try:value=float(expression.rstrip('f')) if kind in ('float','double') else int(expression)
        except ValueError:value=expression.split('.')[-1]
    fields[key]={'type':kind,'default':value}
out=Path(__file__).resolve().parent/'data/profile-scalars.json'
out.write_text(json.dumps({'source':str(source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(raw).hexdigest(),
                          'fields':fields},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'properties':len(fields),'path':str(out.relative_to(ROOT))}))
