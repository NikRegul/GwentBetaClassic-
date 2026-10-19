"""Apply post-build review repairs and common UI layout to a new 0.8.2 revision."""
from pathlib import Path
import json,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'BetaGwent/build/release082-ai1';OUT=ROOT/'BetaGwent/build/release082-polish1'
def read(p):return p.read_text('utf-8-sig')
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def replace(s,a,b):
    assert s.count(a)==1,a[:110]
    return s.replace(a,b)
def board(s):
    # History, tutorial and card summaries deliberately supply explicit newlines.
    s=replace(s,'field.multiline=false;field.wordWrap=false;field.height=size*1.6;',
        'field.multiline=value!=null&&value.indexOf("\\n")>=0;field.wordWrap=field.multiline;field.height=size*1.6;')
    old='''            label.multiline=false;label.wordWrap=false;label.height=h-label.y-3;
            if(label.textWidth>w-24){if(skin==3)BetaGwentFonts.apply(label,BetaGwentFonts.BODY,Math.max(12,Math.floor(18*(w-24)/label.textWidth)),chosen?0xFFE6A0:0xE3D6BE);else label.setTextFormat(new TextFormat("$NormalFont",Math.max(12,Math.floor(18*(w-24)/label.textWidth)),chosen?0xFFE6A0:0xE3D6BE));}
            var buttonFormat:TextFormat=label.defaultTextFormat;buttonFormat.align="center";
            label.defaultTextFormat=buttonFormat;label.setTextFormat(buttonFormat);
            label.y=Math.round((h-label.textHeight)/2)-2;label.height=label.textHeight+4;'''
    new='''            var buttonFormat:TextFormat=label.defaultTextFormat;buttonFormat.align="center";
            label.defaultTextFormat=buttonFormat;label.setTextFormat(buttonFormat);
            BetaGwentTextLanguage.fitButton(label,18,12,h);'''
    s=replace(s,old,new)
    # Input and keyboard share 48 px panel insets; five Cyrillic rows fit above actions.
    s=replace(s,'panel(nameLayer,460,220,1000,650','panel(nameLayer,460,180,1000,720')
    s=replace(s,'30,20,920,30,0xF5D77F);','48,48,904,30,0xF5D77F).height=48;')
    s=replace(s,'nameField=text(box,value,30,82,940,28)','nameField=text(box,value,48,116,904,28)')
    s=replace(s,'nameCounter=text(box,"",30,140,940,20','nameCounter=text(box,"",48,180,904,20')
    s=replace(s,'30+(i%11)*85,192+int(i/11)*64,76,54','48+(i%11)*82,230+int(i/11)*56,72,48')
    for a,b in [('30,520,158,50','48,536,148,48'),('200,520,116,50','212,536,104,48'),('328,520,180,50','332,536,160,48'),('520,520,180,50','508,536,156,48'),('712,520,120,50','680,536,128,48'),('844,520,126,50','824,536,128,48'),('30,580,940,20','48,616,904,18')]:s=replace(s,a,b)
    # History windows use the same 64 px decorative border as the battle menu.
    for name in ['openHistory','openHistoryEntry']:
        start=s.index('        private function '+name+'(');end=s.index('\n        private function ',start+20)
        old=s[start:end];new=old.replace('40,28,1340,26','64,52,1292,26').replace('40,824,220,48','64,792,220,48').replace('1030,824,76,48','1044,792,76,48').replace('1116,834,140,20','1130,802,140,20').replace('1266,824,76,48','1280,792,76,48')
        # Six event rows formerly reached y=774, leaving too little room for footer.
        if name=='openHistoryEntry':new=new.replace('*112','*104').replace('box,ev.actor,40,','box,ev.actor,64,').replace('box,ev.target,128,','box,ev.target,146,').replace('222,y+2,1110','236,y+2,1120')
        s=replace(s,old,new)
    return s
def language(s):
    anchor='        public static function forget(field:TextField):void'
    code='''        // Refit after asynchronous font/dictionary loading as well as initial drawing.
        public static function fitButton(field:TextField,size:Number,minimum:Number,height:Number):void
        {
            if(!fields[field])track(field);
            fields[field].buttonFit={size:size,minimum:minimum,height:height};
            layoutButton(field,fields[field]);
        }
        private static function layoutButton(field:TextField,state:Object):void
        {
            var spec:Object=state.buttonFit;if(!spec)return;
            var f:TextFormat=field.getTextFormat();var size:Number=spec.size;
            f.letterSpacing=0;f.size=size;f.align="center";field.multiline=false;field.wordWrap=false;
            field.defaultTextFormat=f;field.setTextFormat(f);
            while(field.textWidth>field.width-4&&size>spec.minimum){size--;f.size=size;field.defaultTextFormat=f;field.setTextFormat(f);}
            if(field.textWidth>field.width-4){
                field.multiline=true;field.wordWrap=true;size=spec.size;
                f.size=size;field.defaultTextFormat=f;field.setTextFormat(f);
                while(field.textHeight>spec.height-12&&size>spec.minimum){size--;f.size=size;field.defaultTextFormat=f;field.setTextFormat(f);}
            }
            field.height=Math.min(spec.height-8,field.textHeight+4);
            field.y=Math.round((spec.height-field.height)/2);
        }
'''
    s=replace(s,anchor,code+anchor)
    s=replace(s,'            state.shown=shown;state.seen=field.text;','            layoutButton(field,state);\n            state.shown=shown;state.seen=field.text;')
    return s
def main():
    assert not OUT.exists()
    for name in ['scripts','redux']:shutil.copytree(BASE/name,OUT/name)
    for platform in ['classic','nextgen']:
        for name in ['ui','extra-resources']:shutil.copytree(BASE/platform/name,OUT/platform/name)
        for name in ['ui-inputs.json','subimages.json']:
            if(BASE/platform/name).exists():shutil.copy2(BASE/platform/name,OUT/platform/name)
        ui=OUT/platform/'ui';write(ui/'src/BetaGwentBoard.as',board(read(ui/'src/BetaGwentBoard.as')))
        write(ui/'src/BetaGwentTextLanguage.as',language(read(ui/'src/BetaGwentTextLanguage.as')))
        for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            for name in ['BetaGwentBoard.as','BetaGwentTextLanguage.as']:shutil.copy2(ui/'src'/name,ui/mirror/name)
        manifest=json.loads((OUT/platform/'ui-inputs.json').read_text('utf8'))
        # New ABC over accepted art/fonts, with immutable original menu templates.
        manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ui/'src').glob('*.as')}
        (OUT/platform/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    p=OUT/'scripts/game/betagwent/duelSession.ws';s=read(p)
    s=replace(s,'        if(d.effect==34 && (d.specialMode==137 || d.specialMode==114 || d.specialMode==125 || d.specialMode==132))\n            return Max(0,8-useful)*BetaGwentAITune(31);',
        '        if(d.effect==34 && (d.specialMode==137 || d.specialMode==114 || d.specialMode==125 || d.specialMode==132)){\n            m=match.Snapshot();if(d.header.tierMask==2 && m.playerOne.hasPassed)return 0;\n            return Max(0,8-useful)*BetaGwentAITune(31);\n        }')
    write(p,s)
    p=OUT/'scripts/game/betagwent/duelWeather.ws';s=read(p)
    s=s.replace('t.power.currentPower+=1;cards[j]=t;break;','if((t.tokenMask&8)==0){t.power.currentPower+=1;cards[j]=t;}break;')
    s=replace(s,'game.GetZoneCards(side,row,live);for(i=0;i<live.Size();i+=1)cards.PushBack(live[i].Snapshot());',
        'game.GetZoneCards(side,row,live);for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();if(!s.isWaitingToDie)cards.PushBack(s);}')
    write(p,s)
    for name in ['duelSession.ws','duelWeather.ws']:shutil.copy2(OUT/'scripts/game/betagwent'/name,ROOT/'BetaGwent/development/scripts/game/betagwent'/name)
    for mirror in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name in ['BetaGwentBoard.as','BetaGwentTextLanguage.as']:shutil.copy2(OUT/'nextgen/ui'/mirror/name,ROOT/'BetaGwent/ui'/mirror/name)
    import rebuild_ai082 as rebuild
    rebuild.BUILD=OUT;rebuild.prepare()
    print(OUT)
if __name__=='__main__':main()
