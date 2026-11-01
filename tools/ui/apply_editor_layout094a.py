"""Reviewed follow-up to retail feedback; keep every Board's encoding/overlay."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS = [ROOT/'BetaGwent/ui'/folder/'BetaGwentBoard.as' for folder in
         ['src','src-BetaGwentBoard','src-BetaGwentKeg','src-DeckBuilder','src-GwintGame']]
PATHS += [ROOT/'tools/features091/BetaGwentBoard_classic093.as']


def patch(source):
    def change(old, new):
        nonlocal source
        assert source.count(old) == 1, old[:120]
        source = source.replace(old, new)

    change('            betaLabel(content,BetaGwentReleaseText093.label("leaderLocked",BetaGwentTextLanguage.language),46,380,372,16,0xCFC8BA,BetaGwentFonts.BODY,false,"center");\n            deckListTop178=428;',
           '            deckListTop178=378;')
    change('            text(content,BetaGwentReleaseText093.label("leaderLocked",BetaGwentTextLanguage.language),56,372,364,17,0xCBC7BA).height=44;\n', '')
    change('editorState.total+" / 25–40 карт",56,424,364,27', 'editorState.total+" / 25–40 карт",56,372,364,27')
    change('units+" отрядов · "+specials+" особых",56,469,364,18', 'units+" отрядов · "+specials+" особых",56,417,364,18')
    change('panel(content,56,530+(i-editorListPage*12)*34', 'panel(content,56,478+(i-editorListPage*12)*34')
    change('по1.",56,545,364,22', 'по1.",56,493,364,22')

    # Both screens use the same inset, counter baseline and validation colours.
    start = source.index('            paintArt(content,BetaGwentDeckArt104.stats(', source.index('private function drawBetaDeckList('))
    end = source.index('            var leader:Object=', start)
    source = source[:start] + '''            var golds:int=0,silvers:int=0,bronzes:int=0,total:int=0;
            for each(var c:Object in viewed.cards){var n:int=int(c.copies);total+=n;if(c.tier==8)golds+=n;else if(c.tier==4)silvers+=n;else if(c.tier==2)bronzes+=n;}
            betaStatsWidget(fi,golds,silvers,bronzes,total,150);
''' + source[end:]
    change('stats(Math.min(4,fi)),371,108,52,y', 'stats(Math.min(4,fi)),372,108,46,y')
    change('paintArt(content,counters[k][0],46,54,152+k*62,y+8);', 'paintArt(content,counters[k][0],46,54,147+k*62,y+8);')
    change('betaSlotLabel(content,counters[k][1],152+k*62,y+8,46,54', 'betaSlotLabel(content,counters[k][1],147+k*62,y+8,46,54')
    change('"КАРТЫ: "+total,52,y+72,371,18', '"КАРТЫ: "+total,46,y+72,372,18')

    change('"Соперник: "+opponentName()+" · выход из боя считается поражением",500,912',
           'npcMatchHint(),500,912')
    change('        private var npcDisplayName:String="";', '''        private function npcMatchHint():String
        {
            var name:String=opponentName();
            var generic:String=BetaGwentReleaseText093.opponent("",BetaGwentTextLanguage.language);
            return name==generic?"Выход из боя считается поражением.":"Соперник: "+name+" · выход из боя считается поражением";
        }
        private var npcDisplayName:String="";''')

    change('''            var w:Number=big?240:312,h:Number=Math.round(big?240/BETA_LARGE_CARD_ASPECT:312/BETA_CARD_ASPECT);
            // Title/ability block keeps the panel position; the large card is centred in the same slot.
            var previewX:Number=1477+(405-312)/2,cardX:Number=1477+(405-w)/2;
            var card:Sprite=new Sprite();card.x=cardX;card.y=572-h;parent.addChild(card);''', '''            var placement:Array=betaSidePreviewPlacement(big);
            var w:Number=placement[2],h:Number=placement[3];
            var previewX:Number=1477+(405-312)/2,cardX:Number=placement[0];
            var card:Sprite=new Sprite();card.x=cardX;card.y=placement[1];parent.addChild(card);''')
    change('''        private function drawBetaSidePreview(c:Object,detail:Object,previewParent:Sprite=null,animatePortrait:Boolean=false):void''', '''        private function betaSidePreviewPlacement(big:Boolean):Array
        {
            if(!big){var normalH:Number=Math.round(312/BETA_CARD_ASPECT);return [1477+(405-312)/2,572-normalH,312,normalH];}
            // Native PREVIEW_SLOT is 190x266. Its inner card opening is
            // (18,22,156,224), scaled by paintArt to (1545,177,285,398).
            // Fit the card BODY to this opening; native banners keep their own
            // proportions and may overlap the surrounding wooden recess.
            var innerX:Number=1545+18*285/190,innerY:Number=177+22*398/266;
            var innerW:Number=156*285/190,innerH:Number=224*398/266;
            var h:Number=Math.min(innerH,innerW/BETA_LARGE_CARD_ASPECT);
            var w:Number=h*BETA_LARGE_CARD_ASPECT;
            return [innerX+(innerW-w)/2,innerY+(innerH-h)/2,w,h];
        }
        private function drawBetaSidePreview(c:Object,detail:Object,previewParent:Sprite=null,animatePortrait:Boolean=false):void''')
    change('animations.push({sprite:card,fromX:cardX+24,fromY:card.y,toX:cardX,toY:card.y,curve:"PREVIEW",',
           'animations.push({sprite:card,fromX:cardX+(big?0:24),fromY:card.y,toX:cardX,toY:card.y,curve:"PREVIEW",')
    change('card.x=cardX+24;card.alpha=0;', 'card.x=cardX+(big?0:24);card.alpha=0;')
    return source


if __name__ == '__main__':
    outputs = []
    for path in PATHS:
        raw = path.read_bytes()
        assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n', b'')
        source = raw.decode('utf-8-sig').replace('\r\n','\n')
        outputs.append((path,b'\xef\xbb\xbf'+patch(source).replace('\n','\r\n').encode('utf8')))
    for path, raw in outputs:
        path.write_bytes(raw)
    print('Updated five Boards and Classic overlay; BOM/CRLF preserved.')
