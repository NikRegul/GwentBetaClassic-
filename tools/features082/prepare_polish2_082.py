"""Finish the same late-font fitting fix for wide footer actions and slot labels."""
from pathlib import Path
import json,shutil,hashlib
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'BetaGwent/build/release082-polish1';OUT=ROOT/'BetaGwent/build/release082-polish2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def main():
    assert not OUT.exists()
    for name in ['scripts','redux','classic-prepared','classic-audit','compile-nextgen']:shutil.copytree(BASE/name,OUT/name)
    for platform in ['classic','nextgen']:
        for name in ['ui','extra-resources']:shutil.copytree(BASE/platform/name,OUT/platform/name)
        for name in ['ui-inputs.json','subimages.json']:
            if(BASE/platform/name).exists():shutil.copy2(BASE/platform/name,OUT/platform/name)
        ui=OUT/platform/'ui';p=ui/'src/BetaGwentBoard.as';s=p.read_text('utf-8-sig')
        old='else betaLabel(b,title.toUpperCase(),18,10,w-36,22,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2).mouseEnabled=false;'
        new='else {var caption:TextField=betaLabel(b,title.toUpperCase(),18,10,w-36,22,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2);caption.mouseEnabled=false;BetaGwentTextLanguage.fitButton(caption,22,12,48);}'
        assert s.count(old)==1;s=s.replace(old,new)
        old='field.y=y+(h-field.textHeight)/2-2;field.height=field.textHeight+4;return field;'
        new='BetaGwentTextLanguage.fitButton(field,size,Math.min(size,12),h);field.y+=y;return field;'
        # Slot labels live at arbitrary y; keep that offset during future refreshes.
        new='BetaGwentTextLanguage.fitButton(field,size,Math.min(size,12),h,y,2);return field;'
        assert s.count(old)==1;s=s.replace(old,new);write(p,s)
        p=ui/'src/BetaGwentTextLanguage.as';s=p.read_text('utf-8-sig')
        s=s.replace('minimum:Number,height:Number):void','minimum:Number,height:Number,originY:Number=0,padding:Number=4):void').replace('minimum:minimum,height:height};','minimum:minimum,height:height,originY:originY,padding:padding};').replace('field.y=Math.round((spec.height-field.height)/2);','field.y=spec.originY+Math.round((spec.height-field.height)/2);')
        s=s.replace('while(field.textHeight>spec.height-12','while(field.textHeight+4>spec.height-2*spec.padding')
        s=s.replace('            field.height=Math.min(spec.height-8,field.textHeight+4);','            while(field.textHeight+4>spec.height-2*spec.padding&&size>spec.minimum){size--;f.size=size;field.defaultTextFormat=f;field.setTextFormat(f);}\n            field.height=Math.min(spec.height-2*spec.padding,field.textHeight+4);')
        write(p,s)
        for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            for name in ['BetaGwentBoard.as','BetaGwentTextLanguage.as']:shutil.copy2(ui/'src'/name,ui/mirror/name)
        m=json.loads((OUT/platform/'ui-inputs.json').read_text('utf8'));m['sources']={p.name:sha(p) for p in (ui/'src').glob('*.as')};(OUT/platform/'ui-inputs.json').write_text(json.dumps(m,indent=2),'utf8')
    for mirror in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name in ['BetaGwentBoard.as','BetaGwentTextLanguage.as']:shutil.copy2(OUT/'nextgen/ui'/mirror/name,ROOT/'BetaGwent/ui'/mirror/name)
    actual={p.relative_to(OUT/'scripts').as_posix():sha(p) for p in (OUT/'scripts').rglob('*.ws')}
    assert actual=={p['path']:p['sha256'] for p in json.loads((OUT/'compile-nextgen/result.json').read_text('utf8'))['patchSourcesBefore']}
    (OUT/'script-compile-reuse.json').write_text(json.dumps(dict(source=str(BASE),scriptHashes=actual,reason='UI-only final follow-up; exact same natively compiled scripts'),indent=2),'utf8')
    print(OUT)
if __name__=='__main__':main()
