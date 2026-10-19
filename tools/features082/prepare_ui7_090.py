"""0.9.0 build 7 UI (from release090-banner-runtime3 -> release090-ui7).

User review of build 6 (1.32, banners now load):
  * power number centred on each banner's emblem slot (Nilfgaard sun disc,
    Northern shield; a common slot for the other banners);
  * full card view shows the printed base power in white (no boosts/damage);
  * readable flavour line (wraps, larger) and the layout below it follows;
  * deck screens (selection, editor, catalogue) use the big banner preview;
  * doomed units: no cross badge on the card (description is enough);
  * Scaleform closes filled paths back to the pen origin: the target
    outlines drew stray lines from the screen corner (Thunderbolt etc.);
  * battle hints on the right no longer overlap (request prompt yields to
    the target summary; duplicated lines removed);
  * tutorial: content moved away from the frame, 3 new pages
    (mulligan/draws, rows/neighbours, card statuses) in 13 languages.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/release090-banner-runtime3'
OUT = ROOT / 'BetaGwent/build/release090-ui7'
COPIES = ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']
LANGS = ['en', 'de', 'fr', 'it', 'pl', 'es', 'es-mx', 'pt-br', 'ja', 'ko', 'zh-cn', 'zh-tw']


def replace(s, a, b, count=1):
    assert s.count(a) == count, (s.count(a), a[:120])
    return s.replace(a, b)


def write(p, s):
    p.write_bytes(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))


# Emblem centres in card fractions, measured on the extracted Beta banner images
# (pixel centre -> x + u/px*w, y + v/px*h with the placement in banners.json).
SLOTS = {
    'Nilfgaard_Bronze': [-0.0487, 0.0741], 'Nilfgaard_Silver': [-0.0487, 0.0741],
    'Nilfgaard_Gold': [-0.0396, 0.0524],
    'Northern_Bronze': [-0.0398, 0.0630], 'Northern_Silver': [-0.0398, 0.0630],
    'Northern_Gold': [-0.0197, 0.0720],
}
DEFAULT_SLOT = [-0.035, 0.06]


def banners(s):
    s = replace(s, '        public static var lastError:String="";\n',
                '        public static var lastError:String="";\n'
                '        // Centre of the power number on each banner (card fractions).\n'
                '        private static const SLOTS:Object=' + json.dumps(SLOTS, separators=(',', ':')) + ';\n'
                '        public static function slot(faction:int,tier:int):Array\n'
                '        {var s:Array=SLOTS[key(faction,tier)];return s?s:' + json.dumps(DEFAULT_SLOT) + ';}\n')
    return s


TUTORIAL_NEW = [
    dict(after='КАРТЫ И РАУНДЫ', title='МУЛЛИГАН И ДОБОР', cards=['Талер', "Аваллак'х"],
         body=['M1', 'M2', 'M3'],
         demo='{setup:[{k:"e1",id:132301,side:2,slot:0},{k:"m1",id:122308,side:1,slot:0}],pile:"Колода",\n'
              '                  intro:"Посмотрите, сколько карт приходит в каждом раунде.",\n'
              '                  steps:[{at:0,op:"turn",text:"Раунд 1"},{at:300,op:"say",text:"Раунд 1: 10 карт в руке, до трёх замен."},\n'
              '                   {at:2600,op:"turn",text:"Раунд 2"},{at:2900,op:"say",text:"Раунд 2: +2 карты и одна замена."},\n'
              '                   {at:5200,op:"turn",text:"Раунд 3"},{at:5500,op:"say",text:"Раунд 3: +1 карта и одна замена. Сберегите карты к решающему раунду."}]}'),
    dict(after='МУЛЛИГАН И ДОБОР', title='РЯДЫ И СОСЕДИ', cards=['Командирский рог', 'Требушет'],
         body=['R1', 'R2', 'R3'],
         demo='{setup:[{k:"e1",id:132301,side:2,slot:0},{k:"e2",id:201748,side:2,slot:1},{k:"e3",id:122308,side:2,slot:2},{k:"m1",id:123301,side:1,slot:0}],\n'
              '                  intro:"У противника три отряда стоят рядом.",\n'
              '                  steps:[{at:0,op:"say",text:"Вы разыгрываете машину, которая бьёт выбранный отряд и двух его соседей."},{at:400,op:"play",k:"m2",id:122303,side:1,slot:1},\n'
              '                   {at:1600,op:"hit",k:"e1",n:1},{at:1600,op:"hit",k:"e2",n:1},{at:1600,op:"hit",k:"e3",n:1},{at:1700,op:"say",text:"Цель в центре — урон получают все три отряда."},\n'
              '                   {at:4000,op:"say",text:"Так же работают и усиления: ставьте свои отряды плотно, чтобы эффект задел больше карт."}]}'),
    dict(after='РЯДЫ И СОСЕДИ', title='СТАТУСЫ КАРТ', cards=['Реданский оруженосец', 'Выброс адреналина'],
         body=['ST1', 'ST2', 'ST3'],
         demo='{setup:[{k:"e1",id:132301,side:2,slot:0},{k:"m1",id:123301,side:1,slot:0,armor:2},{k:"m2",id:132402,side:1,slot:1}],\n'
              '                  intro:"Следите за цветом силы и бронёй.",\n'
              '                  steps:[{at:0,op:"boost",k:"m2",n:2},{at:100,op:"say",text:"Усиление делает силу зелёной."},\n'
              '                   {at:2200,op:"hit",k:"e1",n:2},{at:2300,op:"say",text:"Урон делает силу красной."},\n'
              '                   {at:4400,op:"hit",k:"m1",n:2},{at:4500,op:"say",text:"У оруженосца 2 ед. брони: первый удар снимает броню, а сила остаётся белой."}]}'),
]


def tutorial(s):
    # Pull everything away from the frame: 96 px side margins, a little lower,
    # buttons above the bottom border; demo panel inside the same margins.
    s = replace(s, 'betaLabel(box,"ОБУЧЕНИЕ · "+(page+1)+" / "+pages.length,56,40,1328,18',
                'betaLabel(box,"ОБУЧЕНИЕ · "+(page+1)+" / "+pages.length,96,64,1248,18')
    s = replace(s, 'betaLabel(box,String(p.title),56,76,1328,30', 'betaLabel(box,String(p.title),96,98,1248,30')
    s = replace(s, 'var body:TextField=text(box,String(p.body),56,140,720,20,0xEBE5D8);body.height=388;',
                'var body:TextField=text(box,String(p.body),96,162,680,19,0xEBE5D8);body.height=362;')
    s = replace(s, 'betaLabel(box,"Карты страницы · нажмите, чтобы посмотреть",56,548,720,15',
                'betaLabel(box,"Карты страницы · нажмите, чтобы посмотреть",96,530,680,15')
    s = replace(s, 'var stripX:Number=56+(720-stripW)/2;', 'var stripX:Number=96+(680-stripW)/2;')
    s = replace(s, 'tile.y=580;', 'tile.y=558;')
    s = replace(s, 'editorBetaButton(box,"‹ Назад",56,768,240,52', 'editorBetaButton(box,"‹ Назад",96,744,240,52')
    s = replace(s, 'editorBetaButton(box,page+1<pages.length?"Далее ›":"Готово",312,768,240,52',
                'editorBetaButton(box,page+1<pages.length?"Далее ›":"Готово",352,744,240,52')
    s = replace(s, 'editorBetaButton(box,tutorialFirstRun?"Пропустить обучение":"Закрыть",1084,768,300,52',
                'editorBetaButton(box,tutorialFirstRun?"Пропустить обучение":"Закрыть",1044,744,300,52')
    s = replace(s, 'panel(box,816,140,568,584,0x0B1015,.96);', 'panel(box,800,162,544,560,0x0B1015,.96);')
    s = replace(s, 'stageView.x=816;stageView.y=140;', 'stageView.x=800;stageView.y=162;')
    s = replace(s, 'caption=text(stageView,String(demo.intro),20,406,528,16,0xEBE5D8);caption.height=94;',
                'caption=text(stageView,String(demo.intro),20,404,504,16,0xEBE5D8);caption.height=86;')
    s = replace(s, 'editorBetaButton(box,"Попробовать",980,654,240,52', 'editorBetaButton(box,"Попробовать",952,658,240,52')
    for page in TUTORIAL_NEW:
        anchor = s.index('{title:"' + page['after'] + '"')
        end = s.index('\n                {title:', anchor + 10)
        body = '\\n\\n'.join(TEXT[k][0] for k in page['body'])
        cards = ','.join(json.dumps(c, ensure_ascii=False) for c in page['cards'])
        entry = ('\n                {title:"%s",body:"%s",cards:[%s],\n                 demo:%s},' %
                 (page['title'], body, cards, page['demo']))
        s = s[:end] + entry + s[end:]
    return s


def board(s):
    # 1. Banner number slots.
    s = replace(s, 'var face:Object={large:false,power:null,color:0xFFFFFF};',
                'var face:Object={large:false,power:null,color:0xFFFFFF,slot:BetaGwentBanners090.slot(entry?int(entry.faction):1,tier)};')
    s = replace(s, 'if(face.power)layoutBigPower090(face.power,w,h,uint(face.color));',
                'if(face.power)layoutBigPower090(face.power,w,h,uint(face.color),face.slot);')
    a = s.index('        private function layoutBigPower090(')
    b = s.index('        private function betaBigPowerField(', a)
    s = s[:a] + '''        private function layoutBigPower090(field:TextField,w:Number,h:Number,color:uint,slot:Array=null):void
        {
            if(!slot)slot=BetaGwentBanners090.slot(1,2);
            var size:int=Math.max(16,Math.round(h*.115));
            field.x=w*slot[0]-size;field.y=h*slot[1]-size*.85;field.width=size*2;field.height=size*1.7;
            if(!BetaGwentFonts.apply(field,BetaGwentFonts.NUMBERS,size,color,true,"center")){field.defaultTextFormat=new TextFormat("$NormalFont",size,color,true,null,null,null,null,"center");field.setTextFormat(field.defaultTextFormat);}
            centerBetaNumber(field,w*slot[0],h*slot[1],size);
        }
''' + s[b:]
    s = replace(s, 'if(face.large)layoutBigPower090(field,w,h,color);', 'if(face.large)layoutBigPower090(field,w,h,color,face.slot);')

    # 2. Full view: printed power in white; 3. readable flavour with a following layout.
    s = replace(s, 'if(unit)betaBigPowerField(picture,String(c.power!=null?c.power:original.power),cw,ch,c.power!=null?powerColor(c):0xFFFFFF,face);',
                'if(unit)betaBigPowerField(picture,String(original&&original.power!=null?original.power:c.power),cw,ch,0xFFFFFF,face);')
    a = s.index('            if(original&&original.flavor.length){', s.index('private function openCardDetail('))
    b = s.index('            var related:Array=', a)
    s = s[:a] + '''            var ruleY:Number=327;
            if(original&&original.flavor.length){
                var flavor:TextField=text(box,original.flavor,272,256,760,19,0x9C9585);
                flavor.wordWrap=true;flavor.multiline=true;
                var italic:TextFormat=flavor.getTextFormat();italic.italic=true;flavor.defaultTextFormat=italic;flavor.setTextFormat(italic);
                flavor.height=Math.max(30,flavor.textHeight+10);
                ruleY=Math.max(327,Math.round(256+flavor.textHeight+24));
            }
            var shift:Number=ruleY-327;
            var rule:Sprite=new Sprite();rule.mouseEnabled=false;box.addChild(rule);
            rule.graphics.lineStyle(3,0x3E3A33,1);rule.graphics.moveTo(250,ruleY);rule.graphics.lineTo(1022,ruleY);
            rule.graphics.lineStyle(1,0x6A645A,.8);rule.graphics.moveTo(262,ruleY-2);rule.graphics.lineTo(1010,ruleY-2);
            var top:Number=360+shift;
            if(unit){
                // Full view shows the printed (base) power in white, without boosts or damage.
                var powerLine:TextField=betaLabel(box,String(original&&original.power!=null?original.power:c.power),264,360+shift,80,52,0xFFFFFF,BetaGwentFonts.NUMBERS,false,"center");
                centerBetaNumber(powerLine,304,393+shift,52);
                betaLabel(box,"СИЛА",346,377+shift,400,28,0xF5F0E7,BetaGwentFonts.TITLE,true,null,6);
                top=450+shift;
            }
''' + s[b:]

    # 4. Deck screens: big banner preview (battle keeps the accepted small face).
    s = replace(s, 'var w:Number=312,h:Number=Math.round(312/BETA_CARD_ASPECT);',
                'var big:Boolean=(selectingDecks||editingDeck||browsingCatalog)&&int(c.templateId)>0;\n'
                '            var w:Number=big?260:312,h:Number=Math.round(big?260/BETA_LARGE_CARD_ASPECT:312/BETA_CARD_ASPECT);')
    s = replace(s, 'var previewX:Number=1477+(405-w)/2;', 'var previewX:Number=big?1580:1477+(405-w)/2;')
    s = replace(s, 'paintBetaFace(card,c.templateId,w,h,side,animatePortrait);',
                'var sideFace:Object=paintBetaFace(card,c.templateId,w,h,side,animatePortrait,true,big);')
    s = replace(s, 'if(c.power!=null&&(!original||original.typeMask==4||int(c.power)>0))betaPowerField(card,String(c.power),w,h,powerColor(c));',
                'if(c.power!=null&&(!original||original.typeMask==4||int(c.power)>0)){if(big)betaBigPowerField(card,String(c.power),w,h,powerColor(c),sideFace);else betaPowerField(card,String(c.power),w,h,powerColor(c));}')

    # 5. Doomed: no cross badge.
    s = replace(s, '                    var doomedBadge:Sprite=panel(p,3,39,20,19,0x271715,.9);doomedBadge.mouseEnabled=false;\n'
                   '                    text(p,"×",6,38,18,18,0xF2AC86);\n', '')

    # 6. Filled outlines: start the path at the rectangle (no line from the origin).
    s = replace(s, '            actionPreviewLayer.graphics.lineStyle(2,0x68DEEB,.95);\n            actionPreviewLayer.graphics.beginFill(0x68DEEB,.10);',
                '            actionPreviewLayer.graphics.lineStyle();actionPreviewLayer.graphics.moveTo(pose.x,pose.y);\n'
                '            actionPreviewLayer.graphics.lineStyle(2,0x68DEEB,.95);\n            actionPreviewLayer.graphics.beginFill(0x68DEEB,.10);')
    s = replace(s, 'if(target){dragLayer.graphics.lineStyle(2,0xB7D6C2,0.7);',
                'if(target){dragLayer.graphics.lineStyle();dragLayer.graphics.moveTo(target.x,target.y);dragLayer.graphics.lineStyle(2,0xB7D6C2,0.7);')
    s = replace(s, 'placementGhost.graphics.lineStyle(3,0xA3E9FF,.95);placementGhost.graphics.beginFill(0x8ED7FF,.18);',
                'placementGhost.graphics.lineStyle();placementGhost.graphics.moveTo(frostRow.x,frostRow.y);placementGhost.graphics.lineStyle(3,0xA3E9FF,.95);placementGhost.graphics.beginFill(0x8ED7FF,.18);')
    s = replace(s, 'h.graphics.lineStyle(1,0xD7BC75,.85);h.graphics.beginFill(0x17180F,.9);',
                'h.graphics.moveTo(-12,-5);h.graphics.lineStyle(1,0xD7BC75,.85);h.graphics.beginFill(0x17180F,.9);')

    # 7. Right-hand battle hints: the target summary replaces the request prompt.
    s = replace(s, 'prompt.height=58;betaFace(BetaGwentFonts.BODY,prompt,21,0xF5D77F);prompt.mouseEnabled=false;',
                'prompt.height=58;betaFace(BetaGwentFonts.BODY,prompt,21,0xF5D77F);prompt.mouseEnabled=false;requestPrompt090=prompt;')
    s = replace(s, '        private function previewOutline(c:Object):void',
                '        private var requestPrompt090:TextField;\n        private function previewOutline(c:Object):void')
    s = replace(s, 'actionPreviewLayer.graphics.clear();while(actionPreviewLayer.numChildren)actionPreviewLayer.removeChildAt(0);',
                'actionPreviewLayer.graphics.clear();while(actionPreviewLayer.numChildren)actionPreviewLayer.removeChildAt(0);if(requestPrompt090)requestPrompt090.visible=true;')
    s = replace(s, 'if(summary.length&&!placementPreview){var label:TextField=text(actionPreviewLayer,summary,1536,816,332,18,legal?0xA8EDF2:0xEACD91);label.height=104;label.mouseEnabled=false;}',
                '''if(summary.length&&!placementPreview){
                var prompted:Boolean=skin==3&&requestId>0&&requestKind!=1&&requestPrompt090!=null&&requestPrompt090.parent!=null;
                if(prompted){summary=summary.split("\\nНажмите, чтобы подтвердить цель").join("").split(" · выбор обязателен").join("");requestPrompt090.visible=false;}
                var label:TextField=text(actionPreviewLayer,summary,1536,prompted?778:816,332,prompted?17:18,legal?0xA8EDF2:0xEACD91);label.height=prompted?84:104;label.mouseEnabled=false;
            }''')
    s = tutorial(s)
    return s


def exchange(s):
    keys = json.loads(re.search(r'KEYS:Array=(\[.*?\]);', s, re.S).group(1))
    values = json.loads(re.search(r'VALUES:Array=(\[.*?\]);\s*\n', s, re.S).group(1))
    assert len(values) == 14 and all(len(v) == len(keys) for v in values[1:])
    for key, (ru, tr) in TEXT.items():
        assert len(tr) == 12, key
        if ru in keys:
            continue
        keys.append(ru); values[1].append(ru)
        for i, value in enumerate(tr):
            values[2 + i].append(value)
    s = re.sub(r'KEYS:Array=\[.*?\];', lambda m: 'KEYS:Array=' + json.dumps(keys, ensure_ascii=False) + ';', s, count=1, flags=re.S)
    s = re.sub(r'VALUES:Array=\[.*?\];(\s*\n)', lambda m: 'VALUES:Array=' + json.dumps(values, ensure_ascii=False) + ';' + m.group(1), s, count=1, flags=re.S)
    return s


sys.path.insert(0, str(Path(__file__).parent))
from tutorial_text7_090 import TEXT  # noqa: E402


def main():
    global OUT
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args(); OUT = args.out.resolve()
    assert not OUT.exists()
    for platform in ['classic', 'nextgen']:
        target = OUT / platform; target.mkdir(parents=True)
        shutil.copytree(args.source / platform / 'ui', target / 'ui')
        for name, patch in [('BetaGwentBoard.as', board), ('BetaGwentBanners090.as', banners), ('BetaGwentExchangeText082.as', exchange)]:
            p = target / 'ui/src' / name; write(p, patch(p.read_text('utf-8-sig')))
            for folder in COPIES:
                if folder != 'src' and (target / 'ui' / folder).is_dir(): shutil.copy2(p, target / 'ui' / folder / name)
                if platform == 'nextgen' and (ROOT / 'BetaGwent/ui' / folder).is_dir(): shutil.copy2(p, ROOT / 'BetaGwent/ui' / folder / name)
        manifest = json.loads((args.source / platform / 'ui-inputs.json').read_text('utf8'))
        manifest['sources'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (target / 'ui/src').glob('*.as')}
        (target / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
        if platform == 'classic': shutil.copy2(args.source / 'classic/subimages.json', target / 'subimages.json')
    if (args.source / 'scripts').is_dir():
        shutil.copytree(args.source / 'scripts', OUT / 'scripts')
    print('Prepared build 7 UI: banner slots, base power, flavour, deck preview, outlines, hints, tutorial.')


if __name__ == '__main__':
    main()
