"""Generate special power-effect routing from the inspected beta graphs."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]

def main():
    extended=ROOT/'docs/evidence/card-vfx163.json'
    source=json.loads((extended if extended.exists() else ROOT/'docs/evidence/special-vfx142.json').read_text('utf8'))
    bindings={};prefabs={}
    for card in source.get('cards',source.get('specials',[])):
        powers=[e for e in card['effects'] if e['node']=='ChangePowerNode' and e['fields'].get('Operation') in (0,1) and e['elementName']]
        if powers:bindings[str(card['templateId'])]=[[e['fields']['ElementType'],e['fields'].get('AttackMethod',0),e['fields']['Operation']] for e in powers]
        if powers:prefabs[str(card['templateId'])]=[[e['attack']['prefab'] if e.get('attack') else None,e['impact']['prefab'] if e.get('impact') else None,e['fields'].get('AttackMethod',0),e['fields']['ElementType'],e['fields']['Operation']] for e in powers]
    output='''package {
    // Generated from the original beta graphs. Rendering is a GFx adaptation.
    public class BetaGwentSpecialVfx {
        private static const BINDINGS:Object=BINDINGS_VALUE;
        private static const PREFABS:Object=PREFAB_VALUE;
        public static function profile(id:int,hurting:Boolean):Object {
            var list:Array=BINDINGS[String(id)];if(!list)return null;
            for each(var v:Array in list)if(int(v[2])==(hurting?1:0))return {element:int(v[0]),method:int(v[1])};
            return null;
        }
        public static function projectile(id:int):Boolean {
            var p:Object=profile(id,true);return p!=null&&p.method==1;
        }
        public static function prefabs(id:int,hurting:Boolean):Object {
            var list:Array=PREFABS[String(id)];if(!list)return null;
            for each(var v:Array in list)if(int(v[4])==(hurting?1:0))return {attack:v[0],impact:v[1],method:int(v[2]),element:int(v[3])};
            return null;
        }
        public static function tint(element:int,fallback:uint):uint {
            switch(element){
                case 16:return 0xFF8C3D;case 32:return 0xBDEEFF;case 64:return 0xB1CFFF;
                case 128:return 0xC1A67C;case 256:return 0xB4F2E7;case 512:return 0xFFE69C;
                case 1024:return 0xD45BFF;case 2048:return 0x9DD783;case 4096:return 0x81CFFF;
                case 8192:return 0x96DA56;case 16384:return 0xDD5970;case 32768:return 0xFFD776;
            }
            return fallback;
        }
    }
}
'''.replace('BINDINGS_VALUE',json.dumps(bindings,separators=(',',':'))).replace('PREFAB_VALUE',json.dumps(prefabs,separators=(',',':')))
    # Keep all generated menu source copies coherent; filtered HD-art bindings
    # in these folders are deliberately left alone.
    for folder in ('src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'):
        target=ROOT/'BetaGwent/ui'/folder/'BetaGwentSpecialVfx.as'
        if target.parent.exists():target.write_bytes(b'\xef\xbb\xbf'+output.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
    print('Generated original power-effect graph bindings for',len(bindings),'cards')

if __name__=='__main__':main()
