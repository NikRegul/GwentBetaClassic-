"""One-time native bridge changes for the 0.7.1 editor block."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws'
s=p.read_text('utf8')
def rep(old,new):
    global s
    assert s.count(old)==1,(old[:70],s.count(old))
    s=s.replace(old,new)
rep('// Separate development menu;', '''struct SBetaGwentClearedDeck
{
    var cards : array<int>;
    var faction : int;
}
// Separate development menu;''')
rep('private var editorPublishedFaction : int;', '''private var editorPublishedFaction : int;
    private var deckClearHistory : array<SBetaGwentClearedDeck>;
    private var finishKegChoice : CScriptedFlashFunction;
    private var kegCanOpenNext : bool;''')
rep('beginKegOpening=GetMenuFlash().GetMemberFlashFunction("beginKegOpening");','beginKegOpening=GetMenuFlash().GetMemberFlashFunction("beginKegOpening");\n        finishKegChoice=GetMenuFlash().GetMemberFlashFunction("finishKegChoice");')
rep('if(!libraryOnly || npcMatch || player.IsInCombat())return false;', '''if(!libraryOnly || npcMatch || player.IsInCombat() || (kegOnly && !kegCanOpenNext))return false;
            kegCanOpenNext=false;''')
rep('if(!player.BetaGwentKegPending()){Publish("Нет неоткрытых бочек.");return false;}', '''if(!player.BetaGwentKegPending()){
                if(kegOnly && finishKegChoice)finishKegChoice.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgBool(true));
                else Publish("Нет неоткрытых бочек.");return false;
            }''')
rep('PublishKegInventory();\n        player.BetaGwentKegContents(ordinary,offers);', '''revision+=1;kegCanOpenNext=false;player.BetaGwentBackupProfile();PublishCollection();
        player.BetaGwentKegContents(ordinary,offers);''')
rep('''if(!configured || value!=revision || !player || !player.BetaGwentChooseKeg(id)) { OnBetaGwentKegOpen(revision);return false; }
        if(kegOnly){CloseMenu();return true;}''', '''if(!configured || value!=revision || !player || !finishKegChoice)return false;
        if(!player.BetaGwentChooseKeg(id)){
            finishKegChoice.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgBool(false));return false;
        }
        revision+=1;kegCanOpenNext=true;player.BetaGwentBackupProfile();
        if(kegOnly){PublishCollection();finishKegChoice.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgBool(true));return true;}''')
rep('editorPublishedFaction = 0; deckDraft = deckLibrary.Edit(id);','deckClearHistory.Clear();editorPublishedFaction = 0; deckDraft = deckLibrary.Edit(id);')
rep('deckDraft.leader = id; PublishDeckEditor(""); return true;', 'deckClearHistory.Clear();deckDraft.leader = id; PublishDeckEditor(""); return true;')
rep('''event OnBetaGwentDeckEditorClear(value : int)
    {
        if (!configured || !deckDraft || value != revision) return false;
        deckDraft.cards.Clear(); PublishDeckEditor(""); return true;
    }''', '''event OnBetaGwentDeckEditorLeave(value : int, save : bool, title : string, nextKeg : bool)
    {
        if(!configured || !deckDraft || value!=revision)return false;
        if(save){if(!OnBetaGwentDeckEditorSave(value,title))return false;}
        else if(!OnBetaGwentDeckEditorCancel(value))return false;
        if(nextKeg)OnBetaGwentKegOpen(revision);
        return true;
    }
    event OnBetaGwentDeckEditorClear(value : int)
    {
        var snapshot : SBetaGwentClearedDeck;
        if (!configured || !deckDraft || value != revision || deckDraft.cards.Size()==0) return false;
        snapshot.cards=deckDraft.cards;snapshot.faction=deckDraft.faction;
        deckClearHistory.PushBack(snapshot);if(deckClearHistory.Size()>20)deckClearHistory.Erase(0);
        deckDraft.cards.Clear(); PublishDeckEditor(""); return true;
    }
    event OnBetaGwentDeckEditorRestore(value : int)
    {
        var snapshot : SBetaGwentClearedDeck;var index : int;
        if(!configured || !deckDraft || value!=revision || deckDraft.cards.Size()!=0 || deckClearHistory.Size()==0)return false;
        index=deckClearHistory.Size()-1;snapshot=deckClearHistory[index];
        if(snapshot.faction!=deckDraft.faction)return false;
        deckDraft.cards=snapshot.cards;deckClearHistory.Erase(index);PublishDeckEditor("");return true;
    }''')
p.write_bytes(s.replace('\n','\r\n').encode('utf8'))
# Correct collection placement in the one-time AS patch.
p=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as'
s=p.read_text('utf-8-sig')
s=s.replace('            filtered.sort(sortEditorCollection);\n            var perPage:int=12;', '            var perPage:int=12;')
needle='            var pages:int=Math.max(1,Math.ceil(filtered.length/12));'
assert s.count(needle)==1
s=s.replace(needle,'            filtered.sort(sortEditorCollection);\n'+needle)
# Escape/Enter must preserve the intended keg transition from the dirty modal.
s=s.replace('private var editorExitPrompt:Boolean=false;', 'private var editorExitPrompt:Boolean=false;\n        private var editorExitNextKeg:Boolean=false;')
s=s.replace('editorExitPrompt=true;', 'editorExitPrompt=true;editorExitNextKeg=nextKeg;')
s=s.replace('else if(editorExitPrompt&&key==13)leaveEditor(true,false);', 'else if(editorExitPrompt&&key==13)leaveEditor(true,editorExitNextKeg);')
p.write_bytes(b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
for folder in ('src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'):
    (ROOT/'BetaGwent/ui'/folder/p.name).write_bytes(p.read_bytes())
print('Patched native bridge and collection sort')
