"""Original Beta related-card hints, using its explicit HideInTooltip flags."""
from pathlib import Path
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from duel_nilf import nilf_pools

def references(node, hidden=None):
    hidden=node.get('attributes',{}).get('HideInTooltip',hidden)
    ident=int(node.get('attributes',{}).get('TemplateId',0))
    result=[ident] if ident and hidden!='True' else []
    for child in node.get('children',[]):result+=references(child,hidden)
    return result

def metadata(catalog):
    templates={t['templateId']:t for t in catalog['templates']}
    links={}
    for ability in catalog['abilities']:
        ident=ability.get('templateId')
        if ident not in templates:continue
        values=links.setdefault(ident,[])
        for target in references(ability['sourceTree']):
            if target in templates and target!=ident and target not in values:values.append(target)
    links={k:v for k,v in links.items() if v}
    # The two corrected creation pools follow the actual request order.
    for ident in [142202,162207]:
        order=nilf_pools(catalog)[ident]
        assert set(links[ident])==set(order)
        links[ident]=order
    collection={c['templateId'] for c in json.loads((ROOT/'data/beta924/planning/full_catalog.json').read_text('utf8'))['cards']}
    # Old removed card revisions also have graphs. Only current collection cards
    # and their recursively reachable public options can appear in this UI.
    reachable=set(collection)
    while True:
        expanded=reachable|{target for ident,targets in links.items() if ident in reachable for target in targets}
        if expanded==reachable:break
        reachable=expanded
    links={ident:targets for ident,targets in links.items() if ident in reachable}
    extras={}
    for ident in sorted({i for ids in links.values() for i in ids}-collection):
        t=templates[ident];f=t['fields']
        extras[ident]=dict(templateId=ident,title=catalog['localization']['ru_ru'][str(ident)+'_name'],power=f['Power'],typeMask=f['Type'],tier=f['Tier'],faction=f['FactionId'],leader=f['Tier']==1)
    assert max(map(len,links.values()))<=8,'Review related-card layout for more than eight cards'
    return links,extras

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'BetaGwent/ui/src/BetaGwentRelated091.as');a=p.parse_args()
    raw=(ROOT/'data/beta924/normalized/catalog.json').read_bytes();links,extras=metadata(json.loads(raw))
    source='''package {
    // Generated from the original Beta graphs; HideInTooltip=True references
    // (including exclusions and private helper lists) are intentionally absent.
    public class BetaGwentRelated091 {
        private static const LINKS:Object=LINK_DATA;
        private static const EXTRA:Object=EXTRA_DATA;
        public static function ids(id:int):Array {return LINKS[id]?LINKS[id].concat():null;}
        public static function find(id:int):Object {
            var card:Object=BetaGwentFullCatalog.find(id);if(card)return card;
            card=EXTRA[id];var original:Object=BetaGwentCardText.find(id);
            if(card&&original){card.description=original.description;return card;}
            return null;
        }
        public static function all():Array {
            var result:Array=BetaGwentFullCatalog.all().concat();
            for(var key:String in EXTRA){var card:Object=find(int(key));if(card)result.push(card);}
            return result;
        }
    }
}
'''.replace('LINK_DATA',json.dumps(links,ensure_ascii=False,separators=(',',':'))).replace('EXTRA_DATA',json.dumps(extras,ensure_ascii=False,separators=(',',':')))
    a.output.write_text(source,'utf8')
    print(json.dumps(dict(sources=len(links),links=sum(map(len,links.values())),internalCards=len(extras),maximum=max(map(len,links.values())),catalogSha256=hashlib.sha256(raw).hexdigest())))

if __name__=='__main__':main()
