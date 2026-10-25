"""Check imperative matching and both card-text generators without rewriting inputs."""
import ast, json, sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from keyword_glossary import keyword_mentioned
from ws_codegen import localized_plain_text
from duel_nilf import nilf_pools

class GlossaryChecks(unittest.TestCase):
    def test_related_metadata_matches_original_graphs(self):
        from build_related091 import metadata
        import re
        catalog=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text('utf8'))
        links,extras=metadata(catalog)
        source=(ROOT/'BetaGwent/ui/src/BetaGwentRelated091.as').read_text('utf8')
        for name,expected in [('LINKS',links),('EXTRA',extras)]:
            actual=json.loads(re.search(r'const '+name+r':Object=(.*);',source).group(1))
            self.assertEqual(actual,{str(k):v for k,v in expected.items()})
        self.assertEqual(links[113303],[113401,113402])
        self.assertEqual(len(links[133302]),8)
        self.assertEqual(links[200102],[201717,201718])

    def test_words_and_boundaries(self):
        for text in ['Создать карту', 'Создайте Трескучий мороз', 'создайте карту', 'Создай карту', 'Создавайте копии']:
            self.assertTrue(keyword_mentioned('Создать',text),text)
        for text in ['пересоздайте', 'создайтека', 'создатель', 'Не имеет способности']:
            self.assertFalse(keyword_mentioned('Создать',text),text)
        self.assertTrue(keyword_mentioned('Spawn','Spawn a card.'))
        self.assertFalse(keyword_mentioned('Spawn','Respawn a card.'))

    def test_language_generator_and_translation(self):
        # Load only definitions; importing this historical generator runs its build.
        p=ROOT/'tools/languages137/prepare_card_text.py'
        tree=ast.parse(p.read_text('utf8'));tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build']
        catalog=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text('utf8'))
        ns=dict(catalog=catalog,localized_plain_text=localized_plain_text,keyword_mentioned=keyword_mentioned)
        import re
        ns['re']=re;exec(compile(tree,str(p),'exec'),ns)
        ru=ns['build'](catalog['localization']['ru_ru'])[0]
        en=ns['build'](catalog['localization']['en_us'])[0]
        for ident in ['142202','162207']:
            self.assertIn('Создать: добавить карту в игру и сыграть ее.',ru[ident]['glossary'])
            self.assertIn('Spawn:',en[ident]['glossary'])
        from localization89 import strings
        glossary=ru['142202']['glossary']
        self.assertEqual(strings()[glossary],en['142202']['glossary'])
        # Generator pools must also follow the original graphs, not just a patched WS table.
        def ids(node):
            value=int(node.get('attributes',{}).get('TemplateId',0))
            return ([value] if value else [])+[v for child in node.get('children',[]) for v in ids(child)]
        pools=nilf_pools(catalog)
        for ident in [142202,162207]:
            graph=next(a for a in catalog['abilities'] if a['type']=='CardAbility' and a['templateId']==ident)
            self.assertEqual(sorted(pools[ident]),sorted(ids(graph['sourceTree'])))

if __name__=='__main__':unittest.main()
