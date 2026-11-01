"""One-time reviewed edit, preserving Board BOM/CRLF and platform differences."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATHS = [ROOT/'BetaGwent/ui'/folder/'BetaGwentBoard.as' for folder in
         ['src','src-BetaGwentBoard','src-BetaGwentKeg','src-DeckBuilder','src-GwintGame']]
PATHS += [ROOT/'tools/features091/BetaGwentBoard_classic093.as']

def patch(source):
    def change(old, new, count=1):
        nonlocal source
        assert source.count(old) == count, old[:120]
        source = source.replace(old, new)

    change('if(!ready||!editingDeck||revision!=expected)return;\n                var args:Array=[expected];',
           'if(!ready||!editingDeck||revision!=expected||eventName=="OnBetaGwentDeckEditorLeader")return;\n                var args:Array=[expected];')
    change('                else if(eventName=="OnBetaGwentDeckEditorLeader")args.push(id);\n', '')
    change('var picked:Object=leaderOption(editorState.leader);var factionLeaders:Array=leadersForFaction(editorState.faction);var leaderIndex:int=0;\n            for(var li:int=0;li<factionLeaders.length;li++)if(factionLeaders[li].id==editorState.leader)leaderIndex=li;',
           'var picked:Object=leaderOption(editorState.leader);', 2)
    start = source.index('                if(factionLeaders.length>1){', source.index('private function drawBetaDeckEditor()'))
    end = source.index('\n                }', start) + len('\n                }')
    source = source[:start] + source[end:]
    change('            deckListTop178=picked&&factionLeaders.length>1?428:378;',
           '            betaLabel(content,BetaGwentReleaseText093.label("leaderLocked",BetaGwentTextLanguage.language),46,380,372,16,0xCFC8BA,BetaGwentFonts.BODY,false,"center");\n            deckListTop178=428;')
    change('''            var factions:Array=[2,8,4,16,32];
            for(var f:int=0;f<factions.length;f++){
                var fIndex:int=editorFactionIndex(factions[f]);
                betaFilterButton(BetaGwentDeckArt104.factionFilter(fIndex),1040+f*72,156,editorState.faction==factions[f],
                    editorFactionAvailable(factions[f])?editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(factions[f])):null);
            }''', '''            paintArt(content,BetaGwentDeckArt104.factionFilter(fi),64,64,1040,156);''')
    change('''            for(var f:int=0;f<factions.length;f++){
                var factionButton:Sprite=editorBetaButton(content,"       "+names[f],464+f*186,88,178,54,editorFactionAvailable(factions[f]),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(factions[f])),editorState.faction==factions[f]);
                paintArt(factionButton,-1240-editorFactionIndex(factions[f]),36,42,7,5);
            }''', '''            for(var f:int=0;f<factions.length;f++)if(editorState.faction==factions[f]){
                paintArt(content,-1240-editorFactionIndex(factions[f]),36,42,471,93);
                text(content,names[f],520,98,600,24,0xE8D3A6).height=40;
            }''')
    change('''            var previous:Object=factionLeaders.length?factionLeaders[(leaderIndex+factionLeaders.length-1)%factionLeaders.length]:null;
            var next:Object=factionLeaders.length?factionLeaders[(leaderIndex+1)%factionLeaders.length]:null;
            editorBetaButton(content,"← Лидер",56,372,174,36,ready&&factionLeaders.length>1,editorAction("OnBetaGwentDeckEditorLeader",previous?previous.id:0));
            editorBetaButton(content,"Лидер →",242,372,178,36,ready&&factionLeaders.length>1,editorAction("OnBetaGwentDeckEditorLeader",next?next.id:0));''',
           '            text(content,BetaGwentReleaseText093.label("leaderLocked",BetaGwentTextLanguage.language),56,372,364,17,0xCBC7BA).height=44;')
    change('''            if(message.length||!exchangeImport)BetaGwentTextLanguage.assign(exchangeMessage,message);''',
           '''            if(message=="Лидер выбирается при создании колоды.")message=BetaGwentReleaseText093.label("leaderLocked",BetaGwentTextLanguage.language);
            if(message.length||!exchangeImport)BetaGwentTextLanguage.assign(exchangeMessage,message);''')
    return source

if __name__ == '__main__':
    # Validate all inputs before modifying any copy.
    outputs = []
    for path in PATHS:
        raw = path.read_bytes()
        assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'')
        output = patch(raw.decode('utf-8-sig').replace('\r\n','\n'))
        outputs.append((path,b'\xef\xbb\xbf'+output.replace('\n','\r\n').encode('utf8')))
    for path, raw in outputs:
        path.write_bytes(raw)
    print('Updated five Boards and Classic overlay; creation flow unchanged.')
