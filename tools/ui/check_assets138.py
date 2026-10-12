"""Verify the 0.6.2 UI supplement, native text resources and required glyphs."""
import hashlib
import json
import re
import struct
from pathlib import Path
from build_ui_text138 import dictionaries
from update_board_resource import validate_resource, unpack_root
from build_leaders136 import movie_parts
from check_assets137 import main as check_base_assets

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    # Preserve the full checks for current card/item dictionaries and native leader
    # pages, then verify that stage138 contains that base plus the UI supplement.
    check_base_assets()
    report=json.loads((ROOT/'docs/evidence/languages138.json').read_text('utf8'))
    base=json.loads((ROOT/'docs/evidence/languages137.json').read_text('utf8'))
    assert report['stage']==138 and len(report['languages'])==13
    result={}
    for locale,table in dictionaries().items():
        source=ROOT/f'BetaGwent/build/text138/{locale}/BetaLocale137.as'
        text=source.read_text('utf8')
        actual={json.loads(k):json.loads(v) for k,v in re.findall(r'o\[("(?:\\.|[^"\\])*")\]=("(?:\\.|[^"\\])*");',text)}
        previous=(ROOT/f'BetaGwent/build/text137/{locale}/BetaLocale137.as').read_text('utf8')
        expected_table={json.loads(k):json.loads(v) for k,v in re.findall(r'o\[("(?:\\.|[^"\\])*")\]=("(?:\\.|[^"\\])*");',previous)}
        expected_table.update(table)
        expected_table.update({k.upper():v.upper() for k,v in list(expected_table.items()) if k})
        assert actual==expected_table,(locale,'Native stage138 dictionary differs from current base/supplement')
        assert sha(source)==report['languages'][locale]['sourceSha256']
        assert hashlib.sha256(json.dumps(actual,ensure_ascii=True,sort_keys=True).encode()).hexdigest()==report['languages'][locale]['dictionarySha256']
        chars=json.loads(re.search(r'public var characters:String=("(?:\\.|[^"\\])*");',text)[1])
        expected=set(''.join(table.values())+''.join(table.keys()))
        assert expected<=set(chars),(locale,'Missing glyph metadata',expected-set(chars))
        for k,v in table.items():
            assert 'o['+json.dumps(k,ensure_ascii=True)+']='+json.dumps(v,ensure_ascii=True)+';' in text,(locale,k)
        resource=ROOT/'BetaGwent/build/text138/resources'/report['languages'][locale]['path']
        data=resource.read_bytes()
        assert hashlib.sha256(data).hexdigest()==report['languages'][locale]['sha256']
        parsed,_=validate_resource(resource)
        gfx=unpack_root(parsed)[1]
        font_tags=[payload for code,payload,_ in movie_parts(gfx)[1] if code==75]
        assert len(font_tags)==2,(locale,'Expected body/title fonts')
        # DefineFont3: flags/language/name length/name, then glyph count.
        for font in font_tags:
            name_length=font[4];count=int.from_bytes(font[5+name_length:7+name_length],'little')
            assert count>=len(set(chars)),(locale,'Not all declared glyphs embedded',count,len(set(chars)))
            offset_start=7+name_length
            assert font[2]&4 and font[2]&8
            code_offset=struct.unpack_from('<I',font,offset_start+4*count)[0]
            codes=set(struct.unpack_from('<'+str(count)+'H',font,offset_start+code_offset))
            assert set(map(ord,chars))<=codes,(locale,'Missing actual embedded glyph')
        result[locale]={'entries':len(table),'nativeBytes':len(data),'requiredCharacters':len(expected),'verified':True}
    output={'stage':138,'languages':result,'nativeGameTested':False,
            'sources':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in
             [ROOT/'data/beta924/design/ui-polish138.json',ROOT/'tools/ui/build_ui_languages138.py',ROOT/'tools/ui/build_ui_text138.py']}}
    (ROOT/'docs/evidence/assets138.json').write_text(json.dumps(output,indent=2)+'\n','utf8')
    print('PASS: 13 native language resources, dictionaries, both embedded font tables and glyph coverage')

if __name__=='__main__':main()
