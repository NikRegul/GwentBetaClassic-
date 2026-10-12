import json,re,collections
W=re.compile(r'[A-Za-z0-9_А-Яа-яЁё]')
def word(c): return bool(c) and bool(W.match(c))
class T:
    def __init__(s,d):
        s.m=d;s.g=collections.defaultdict(list)
        for k in d:
            if k:s.g[k[0]].append(k)
        for v in s.g.values():v.sort(key=len,reverse=True)
    def tr(s,v):
        if v in s.m:return s.m[v]
        r='';a=0
        while a<len(v):
            ch=None
            for k in s.g.get(v[a],[]):
                if v[a:a+len(k)]!=k:continue
                if word(k[0]) and a>0 and word(v[a-1]):continue
                if word(k[-1]) and word(v[a+len(k):a+len(k)+1]):continue
                ch=k;break
            if ch:r+=s.m[ch];a+=len(ch)
            else:r+=v[a];a+=1
        return r
lines=[x for x in json.load(open('/tmp/concat.json')) if 'Checks' not in x[0] and 'LogChannel' not in x[2]]
LIT=re.compile(r'"([^"\n]*)"')
locs=['de_de','fr_fr','it_it','pl_pl','es_es','pt_br','jp_jp','kr_kr','zh_cn']
res={};bad=collections.Counter();examples={}
for loc in locs:
    t=T(json.load(open(f'BetaGwent/build/languages137/ui/{loc}.json',encoding='utf8')))
    for f,n,l in lines:
        lits=[x for x in LIT.findall(l) if re.search('[А-Яа-яЁё]',x)]
        sample='7'.join(lits)
        out=t.tr(sample)
        left=re.findall(r'[А-Яа-яЁё]+',out)
        if left:
            bad[(f.split('/')[-1],n)]+=1
            examples.setdefault((f.split('/')[-1],n),{})[loc]=(sample[:120],out[:160],left[:6])
print(len(lines),'lines;',len(bad),'leave Cyrillic in some locale')
for k,c in bad.most_common(60):
    e=examples[k];loc='de_de' if 'de_de' in e else next(iter(e))
    print(k,c,loc,e[loc][2],'|',e[loc][1][:110])
print('---- literal alone')
alone=collections.defaultdict(set)
for loc in locs:
    t=T(json.load(open(f'BetaGwent/build/languages137/ui/{loc}.json',encoding='utf8')))
    for f,n,l in lines:
        for x in LIT.findall(l):
            if not re.search('[А-Яа-яЁё]',x):continue
            o=t.tr(x)
            if re.search('[А-Яа-яЁё]',o): alone[(f.split('/')[-1],n,x)].add(loc)
for k,v in sorted(alone.items()): print(k,len(v),t.tr(k[2]) if 'zh_cn' in v else '')
json.dump({'%s:%d'%(a,b):[c,sorted(v)] for (a,b,c),v in alone.items()},open('/tmp/alone.json','w'),ensure_ascii=False,indent=0)
