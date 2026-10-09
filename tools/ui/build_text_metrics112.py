"""Export original Beta glyph advances/ink bounds for deterministic GFx layout."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[2]
fonts = json.loads((ROOT/'BetaGwent/ui/build/beta-fonts104.json').read_text('utf8'))
faces = {'Halis GR': 'HalisGRBold', 'PF Din Text Cond Pro': 'PFDinTextCondPro', 'Gwent Numbers': 'GwentNumbers'}
metrics = {name: {code: [g['advance'], *g['bounds']] for code, g in fonts[key]['glyphs'].items()} for name, key in faces.items()}
out = '''package {
    // Original Beta SDF glyph metrics, in the original 64 px em square.
    public class BetaGwentTextMetrics {
        private static const glyphs:Object=METRICS;
        public static function width(value:String,face:String,size:Number,spacing:Number=0):Number {
            var table:Object=glyphs[face];if(!table)return value.length*size*.65;
            var total:Number=0;for(var i:int=0;i<value.length;i++){
                var g:Array=table[value.charCodeAt(i)];total+=g?g[0]*size/64:size*.65;
                if(i>0)total+=spacing;
            }return total;
        }
        public static function numberOffset(value:String,size:Number):Array {
            var table:Object=glyphs["Gwent Numbers"],pen:Number=0,x0:Number=10000,x1:Number=-10000,y0:Number=10000,y1:Number=-10000;
            for(var i:int=0;i<value.length;i++){
                var g:Array=table[value.charCodeAt(i)];if(!g)continue;
                x0=Math.min(x0,pen+g[1]);x1=Math.max(x1,pen+g[3]);y0=Math.min(y0,g[2]);y1=Math.max(y1,g[4]);pen+=g[0];
            }
            // Horizontal correction to centred advance, vertical position of ink relative to field origin.
            return [(x0+x1-pen)*size/128,2+(35.09375-(y0+y1)/2)*size/64];
        }
    }
}
'''.replace('METRICS', json.dumps(metrics, ensure_ascii=True, separators=(',', ':')))
(ROOT/'BetaGwent/ui/src/BetaGwentTextMetrics.as').write_text(out, 'utf8')
print('Beta glyph metrics exported')
