"""0.9.0 import with crafting: missing cards as a card grid, per-card and "craft all",
import only when nothing is missing; literal \\n in exchange messages fixed.

Writes BetaGwent/build/release090-bannersUI from frozen inputs:
  classic|nextgen/ui  release090-native-clipboard UI (copy probe, Math.max fix) + this change
  scripts             release090-final/scripts (cleaner fix) + import events
Canonical BetaGwent/ui mirrors and development scripts follow the new sources.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil

ROOT = Path(__file__).resolve().parents[2]
UI_FROM = ROOT / 'BetaGwent/build/release090-native-clipboard'
SCRIPTS_FROM = ROOT / 'BetaGwent/build/release090-final/scripts'
OUT = ROOT / 'BetaGwent/build/release090-bannersUI'
COPIES = ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return p.read_text('utf-8-sig').replace('\r\n', '\n')


def write(p, s):
    p.write_bytes(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))


def between(s, start, end):
    a = s.index(start); b = s.index(end, a)
    return a, b


AS_EXCHANGE = r'''        private var exchangeMissing:Array=[];private var exchangeCost:int=0;private var exchangeBlocked:Boolean=false;
        private var exchangeChecked:Boolean=false;private var exchangePage:int=0;
        private var exchangeGrid:Sprite;private var exchangeActions:Sprite;
        private function exchangeCode():String{return nameField?nameField.text.replace(/^\s+|\s+$/g,""):"";}
        private function exchangeCurrent():Boolean{return exchangeChecked&&exchangeQuotedCode==exchangeCode()&&exchangeCode().length>0;}
        private function pasteExchange():void
        {
            if(!nameField)return;
            var value:String=clipboardText();
            if(value.length>320){BetaGwentTextLanguage.assign(exchangeMessage,"Максимум 320 символов.");return;}
            if(!value.length){BetaGwentTextLanguage.assign(exchangeMessage,"Буфер пуст. Вставьте код вручную.");return;}
            nameField.text=value.replace(/^\s+|\s+$/g,"");exchangeQuotedCode="";
            nameField.setSelection(0,nameField.text.length);
            if(exchangeImport)checkDeckExchange();
        }
        // Import never crafts and crafting never imports: both are separate, explicit steps.
        private function checkDeckExchange():void
        {
            if(!ready||!nameOpen||!exchangeImport||!nameField||nameRevision!=revision)return;
            var code:String=exchangeCode();if(!code.length)return;
            exchangeQuotedCode=code;exchangeChecked=false;exchangeMissing=[];redrawExchange();
            send("OnBetaGwentDeckImportCheck",[revision,code]);
        }
        private function submitDeckExchange(craft:Boolean=false):void
        {
            if(!ready||!nameOpen||!exchangeImport||!nameField||nameRevision!=revision)return;
            if(!exchangeCurrent()){checkDeckExchange();return;}
            if(craft){send("OnBetaGwentDeckImportCraft",[revision,exchangeQuotedCode,0]);return;}
            if(exchangeMissing.length){BetaGwentTextLanguage.assign(exchangeMessage,"Сначала создайте недостающие карты.");return;}
            send("OnBetaGwentDeckImport",[revision,exchangeQuotedCode,false]);
        }
        private function exchangeCraft(id:int):Function
        { return function():void{if(ready&&exchangeCurrent())send("OnBetaGwentDeckImportCraft",[revision,exchangeQuotedCode,id]);}; }
        public function setDeckExchangeMissing(value:int,ids:String,counts:String,cost:int,balance:int,blocked:Boolean):void
        {
            if(value!=revision||!nameOpen||!exchangeImport)return;
            var a:Array=ids.length?ids.split(","):[],b:Array=counts.length?counts.split(","):[];
            exchangeMissing=[];
            for(var i:int=0;i<a.length;i++)exchangeMissing.push({id:int(a[i]),count:Math.max(1,int(b[i]))});
            exchangeCost=cost;scraps=balance;exchangeBlocked=blocked;exchangeChecked=true;
            redrawExchange();
        }
        private function redrawExchange():void
        {
            if(!exchangeGrid||!exchangeActions||!nameOpen||!exchangeImport)return;
            while(exchangeGrid.numChildren)exchangeGrid.removeChildAt(0);
            while(exchangeActions.numChildren)exchangeActions.removeChildAt(0);
            var current:Boolean=exchangeCurrent();var total:int=0;var m:Object;
            for each(m in exchangeMissing)total+=int(m.count);
            var per:int=16,pages:int=Math.max(1,Math.ceil(exchangeMissing.length/per));
            exchangePage=Math.max(0,Math.min(exchangePage,pages-1));
            if(current){
                var summary:String=exchangeMissing.length==0?"Все карты есть. Можно импортировать.":
                    "Недостающие карты: "+total+" · создать все: "+exchangeCost+" осколков · у вас "+scraps;
                if(exchangeMissing.length&&exchangeBlocked)summary+="\nЗавершите выбор награды из бочки, чтобы создавать карты.";
                BetaGwentTextLanguage.assign(exchangeMessage,summary);
            }
            for(var i:int=exchangePage*per;current&&i<Math.min(exchangeMissing.length,(exchangePage+1)*per);i++){
                var n:int=i-exchangePage*per;m=exchangeMissing[i];
                var c:Object=BetaGwentFullCatalog.find(int(m.id));
                var tile:Sprite=new Sprite();tile.x=(n%8)*196;tile.y=int(n/8)*326;exchangeGrid.addChild(tile);
                paintBetaFace(tile,int(m.id),173,231,0);
                if(c&&(c.typeMask==4||c.leader))betaPowerField(tile,String(c.power),173,231,0xFFFFFF);
                var count:TextField=betaLabel(tile,"× "+m.count,113,6,54,22,0xFFE6A0,BetaGwentFonts.TITLE,true,"right");
                count.background=true;count.backgroundColor=0x11191C;
                var title:TextField=betaLabel(tile,c?c.title:String(m.id),0,236,173,17,0xEDE7D8,BetaGwentFonts.TITLE,false,"center");title.height=40;
                var cost:int=c?craftCost(c):0;
                editorBetaButton(tile,"Создать ("+cost+")",0,280,173,36,ready&&!exchangeBlocked&&c!=null&&scraps>=cost,exchangeCraft(int(m.id)));
            }
            var hasCode:Boolean=exchangeCode().length>0;
            editorSmallButton(exchangeActions,"Вставить",48,924,184,48,true,pasteExchange);
            editorSmallButton(exchangeActions,"Проверить",248,924,200,48,hasCode,checkDeckExchange);
            editorSmallButton(exchangeActions,"Создать все ("+exchangeCost+")",464,924,380,48,
                ready&&current&&exchangeMissing.length>0&&!exchangeBlocked&&scraps>=exchangeCost,function():void{submitDeckExchange(true);});
            editorSmallButton(exchangeActions,"Импортировать",860,924,300,48,ready&&current&&exchangeMissing.length==0,function():void{submitDeckExchange();});
            if(pages>1){
                editorSmallButton(exchangeActions,"←",1176,924,72,48,exchangePage>0,function():void{exchangePage--;redrawExchange();});
                editorSmallButton(exchangeActions,"→",1264,924,72,48,exchangePage+1<pages,function():void{exchangePage++;redrawExchange();});
                text(exchangeActions,(exchangePage+1)+" / "+pages,1352,936,72,22,0xD6C6A8);
            }
            editorSmallButton(exchangeActions,"Закрыть",1432,924,248,48,true,closeNameInput);
        }
        private function openDeckExchange(importing:Boolean):void
        {
            if(!ready||nameOpen||!(selectingDecks||editingDeck)||(!importing&&!editingDeck))return;
            closeControllerMenu();exchangeImport=importing;exchangeQuotedCode="";
            textPurpose=importing?3:4;textLimit=320;nameRevision=revision;nameOpen=true;
            panel(nameLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.85);
            if(importing){
                var sheet:Sprite=panel(nameLayer,96,40,1728,1000,0x10191F,.99);
                text(sheet,"ИМПОРТ КОЛОДЫ",48,28,1200,30,0xF5D77F);
                nameField=text(sheet,"",48,84,1632,23);nameField.height=72;
                BetaGwentTextLanguage.forget(nameField);nameField.type=TextFieldType.INPUT;
                nameField.multiline=true;nameField.wordWrap=true;nameField.selectable=true;nameField.mouseEnabled=true;nameField.maxChars=320;
                nameField.background=true;nameField.backgroundColor=0x233B45;
                nameField.addEventListener(Event.CHANGE,function(e:Event):void{exchangeChecked=false;exchangeMissing=[];redrawExchange();});
                exchangeMessage=text(sheet,"Вставьте код BG1. Импорт заменит черновик. Затем сохраните колоду.",48,168,1632,22);
                exchangeMessage.height=64;
                exchangeGrid=new Sprite();exchangeGrid.x=80;exchangeGrid.y=246;sheet.addChild(exchangeGrid);
                exchangeActions=new Sprite();sheet.addChild(exchangeActions);
                exchangeMissing=[];exchangeChecked=false;exchangePage=0;exchangeCost=0;exchangeBlocked=false;
                var pasted:String=clipboardText();if(pasted.length>0&&pasted.length<=320)nameField.text=pasted.replace(/^\s+|\s+$/g,"");
                redrawExchange();
                controller.focusTag("control");
                if(keyboardStage)keyboardStage.focus=nameField;
                if(nameField.text.length)checkDeckExchange();
                return;
            }
            exchangeGrid=null;exchangeActions=null;
            var box:Sprite=panel(nameLayer,400,160,1120,760,0x10191F,.99);
            text(box,"ЭКСПОРТ КОЛОДЫ",48,48,1024,30,0xF5D77F);
            nameField=text(box,"",48,116,1024,23);nameField.height=100;
            BetaGwentTextLanguage.forget(nameField);nameField.type=TextFieldType.INPUT;
            nameField.multiline=true;nameField.wordWrap=true;nameField.selectable=true;nameField.mouseEnabled=true;nameField.maxChars=320;
            nameField.background=true;nameField.backgroundColor=0x233B45;
            exchangeMessage=text(box,"",48,252,1024,22);
            exchangeMessage.height=300;exchangeMessage.mouseEnabled=true;
            exchangeMessage.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{exchangeMessage.scrollV-=e.delta;e.stopPropagation();});
            editorSmallButton(box,"↑",964,568,44,40,true,function():void{exchangeMessage.scrollV--;});
            editorSmallButton(box,"↓",1028,568,44,40,true,function():void{exchangeMessage.scrollV++;});
            editorSmallButton(box,"Копировать",48,642,280,48,true,copyExchange);
            send("OnBetaGwentDeckExport",[revision]);
            editorSmallButton(box,"Закрыть",824,642,248,48,true,closeNameInput);
            controller.focusTag("control");
            if(keyboardStage)keyboardStage.focus=nameField;
        }
        public function setDeckExchange(value:int,code:String,message:String,accepted:Boolean):void
        {
            if(value!=revision||!nameOpen||textPurpose<3||!exchangeMessage)return;
            if(accepted){closeNameInput();return;}
            // WitcherScript keeps "\n" as two characters.
            message=message==null?"":message.split("\\n").join("\n");
            if(message.length||!exchangeImport)BetaGwentTextLanguage.assign(exchangeMessage,message);
            exchangeMessage.scrollV=1;
            if(code.length){nameField.text=code;nameField.setSelection(0,code.length);copyExchange();if(keyboardStage)keyboardStage.focus=nameField;}
        }
'''

WS_IMPORT = r'''    // 0.9.0: missing cards are published as a list for a card grid. Crafting (one card
    // or all) never imports, and import is refused while anything is missing.
    private function ExchangeParse(value : int, code : string, out parsed : SBetaGwentDeckExchange) : bool
    {
        var player : W3PlayerWitcher;
        if(!configured || !selectingDecks || value!=revision)return false;
        parsed=BetaGwentParseDeckExchange(code);
        if(!parsed.valid){PublishDeckExchange("",parsed.message,false);return false;}
        if(npcMatch && forcedBetaFaction!=0 && parsed.faction!=forcedBetaFaction) {
            PublishDeckExchange("","Для квеста нужна другая фракция.",false);return false;
        }
        player=(W3PlayerWitcher)thePlayer;
        if((libraryOnly || npcMatch) && (!player || !player.BetaGwentEnsureCollection())) {
            PublishDeckExchange("","Коллекция недоступна.",false);return false;
        }
        return true;
    }
    private function ExchangeMissing(parsed : SBetaGwentDeckExchange, out missing : array<int>, out counts : array<int>) : int
    {
        var player : W3PlayerWitcher;
        missing.Clear();counts.Clear();
        player=(W3PlayerWitcher)thePlayer;
        if(!(libraryOnly || npcMatch) || !player)return 0;
        return player.BetaGwentExchangeMissing(parsed.cards,parsed.leader,missing,counts);
    }
    private function PublishExchangeMissing(parsed : SBetaGwentDeckExchange, message : string)
    {
        var reply : CScriptedFlashFunction;var player : W3PlayerWitcher;
        var missing,counts : array<int>;var cost,i,balance : int;var ids,copies : string;var blocked : bool;
        cost=ExchangeMissing(parsed,missing,counts);
        player=(W3PlayerWitcher)thePlayer;
        if(player){balance=player.BetaGwentScraps();blocked=missing.Size()>0 && player.BetaGwentKegPending();}
        for(i=0;i<missing.Size();i+=1){if(i>0){ids+=",";copies+=",";}ids+=IntToString(missing[i]);copies+=IntToString(counts[i]);}
        reply=GetMenuFlash().GetMemberFlashFunction("setDeckExchangeMissing");
        if(reply)reply.InvokeSelfSixArgs(FlashArgInt(revision),FlashArgString(ids),FlashArgString(copies),FlashArgInt(cost),FlashArgInt(balance),FlashArgBool(blocked));
        PublishDeckExchange("",message,false);
    }
    event OnBetaGwentDeckImportCheck(value : int, code : string)
    {
        var parsed : SBetaGwentDeckExchange;
        if(!ExchangeParse(value,code,parsed))return false;
        PublishExchangeMissing(parsed,"");return true;
    }
    event OnBetaGwentDeckImportCraft(value : int, code : string, id : int)
    { return ImportCraft(value,code,id); }
    // id 0 creates every missing copy at once (price and caps checked first).
    private function ImportCraft(value : int, code : string, id : int) : bool
    {
        var parsed : SBetaGwentDeckExchange;var player : W3PlayerWitcher;
        var missing,counts : array<int>;var crafted : bool;
        if(!ExchangeParse(value,code,parsed))return false;
        player=(W3PlayerWitcher)thePlayer;
        if(!(libraryOnly || npcMatch) || !player){PublishExchangeMissing(parsed,"");return false;}
        ExchangeMissing(parsed,missing,counts);
        if(player.BetaGwentKegPending())crafted=false;
        else if(id==0)crafted=missing.Size()>0 && player.BetaGwentCraftExchange(parsed.cards,parsed.faction,parsed.leader);
        else if(missing.Contains(id) && player.BetaGwentCraft(id)) {
            crafted=true;player.BetaGwentUpdateCollectionProgress();player.BetaGwentSyncTournamentAccess();player.BetaGwentBackupProfile();
        }
        LogChannel('BetaGwent',"IMPORT_CRAFT card="+id+" ok="+crafted+" scraps="+player.BetaGwentScraps());
        PublishCollection();
        if(crafted)PublishExchangeMissing(parsed,"");
        else PublishExchangeMissing(parsed,"Не хватает осколков или карта уже собрана.");
        return crafted;
    }
    event OnBetaGwentDeckImport(value : int, code : string, craft : bool)
    {
        var parsed : SBetaGwentDeckExchange;var missing,counts : array<int>;
        if(craft)return ImportCraft(value,code,0);
        if(!ExchangeParse(value,code,parsed))return false;
        if(!deckDraft && deckLibrary.FirstEmpty()==0){PublishDeckExchange("","Нет свободного слота. Откройте колоду для замены.",false);return false;}
        ExchangeMissing(parsed,missing,counts);
        if(missing.Size()>0){PublishExchangeMissing(parsed,"Сначала создайте недостающие карты.");return false;}
        if(!deckDraft)deckDraft=deckLibrary.Edit(0);
        if(!deckDraft){PublishDeckExchange("","Нет свободного слота.",false);return false;}
        deckDraft.cards=parsed.cards;deckDraft.faction=parsed.faction;deckDraft.leader=parsed.leader;
        deckClearHistory.Clear();editorPublishedFaction=0;
        PublishCollection();PublishDeckEditor("Колода импортирована. Сохраните изменения.");
        PublishDeckExchange("","Колода импортирована.",true);return true;
    }
'''

# Translations for new fragments: ru, en, de, fr, it, pl, es, es-mx, pt-br, ja, ko, zh-cn, zh-tw.
NEW_KEYS = {
'Проверить': ['Проверить','Check','Prüfen','Vérifier','Verifica','Sprawdź','Comprobar','Comprobar','Verificar','確認','확인','检查','檢查'],
'Создать все': ['Создать все','Craft all','Alle herstellen','Tout créer','Crea tutte','Stwórz wszystkie','Crear todas','Crear todas','Criar todas','すべて作成','모두 제작','全部制作','全部製作'],
'Создать (': ['Создать (','Craft (','Herstellen (','Créer (','Crea (','Stwórz (','Crear (','Crear (','Criar (','作成 (','제작 (','制作 (','製作 ('],
'Недостающие карты: ': ['Недостающие карты: ','Missing cards: ','Fehlende Karten: ','Cartes manquantes : ','Carte mancanti: ','Brakujące karty: ','Cartas que faltan: ','Cartas que faltan: ','Cartas ausentes: ','不足カード: ','부족한 카드: ','缺少的卡牌：','缺少的卡牌：'],
' · создать все: ': [' · создать все: ',' · craft all: ',' · alle herstellen: ',' · tout créer : ',' · crea tutte: ',' · stwórz wszystkie: ',' · crear todas: ',' · crear todas: ',' · criar todas: ',' · すべて作成: ',' · 모두 제작: ',' · 全部制作：',' · 全部製作：'],
' осколков · у вас ': [' осколков · у вас ',' scraps · you have ',' Fetzen · vorhanden: ',' fragments · vous avez ',' frammenti · ne hai ',' skrawków · masz ',' fragmentos · tienes ',' fragmentos · tienes ',' fragmentos · você tem ',' 紙片 · 所持 ',' 조각 · 보유 ',' 碎片 · 持有 ',' 碎片 · 持有 '],
'Все карты есть. Можно импортировать.': ['Все карты есть. Можно импортировать.','All cards owned. You can import now.','Alle Karten vorhanden. Import möglich.','Toutes les cartes sont possédées. Vous pouvez importer.','Hai tutte le carte. Puoi importare.','Masz wszystkie karty. Możesz importować.','Tienes todas las cartas. Ya puedes importar.','Tienes todas las cartas. Ya puedes importar.','Você tem todas as cartas. Já pode importar.','すべてのカードを所持しています。インポートできます。','모든 카드를 보유했습니다. 가져올 수 있습니다.','已拥有全部卡牌，可以导入。','已擁有全部卡牌，可以匯入。'],
'Сначала создайте недостающие карты.': ['Сначала создайте недостающие карты.','Craft the missing cards first.','Zuerst die fehlenden Karten herstellen.','Créez d’abord les cartes manquantes.','Prima crea le carte mancanti.','Najpierw stwórz brakujące karty.','Primero crea las cartas que faltan.','Primero crea las cartas que faltan.','Primeiro crie as cartas ausentes.','先に不足カードを作成してください。','먼저 부족한 카드를 제작하세요.','请先制作缺少的卡牌。','請先製作缺少的卡牌。'],
'Завершите выбор награды из бочки, чтобы создавать карты.': ['Завершите выбор награды из бочки, чтобы создавать карты.','Finish choosing your keg reward to craft cards.','Zuerst die Fassbelohnung auswählen, um Karten herzustellen.','Terminez le choix de la récompense du baril pour créer des cartes.','Completa la scelta della ricompensa del barile per creare carte.','Dokończ wybór nagrody z beczki, aby tworzyć karty.','Termina de elegir la recompensa del barril para crear cartas.','Termina de elegir la recompensa del barril para crear cartas.','Termine de escolher a recompensa do barril para criar cartas.','カードを作成するにはタルの報酬を選択してください。','카드를 제작하려면 카드통 보상 선택을 마치세요.','请先完成卡桶奖励选择再制作卡牌。','請先完成卡桶獎勵選擇再製作卡牌。'],
'Не хватает осколков или карта уже собрана.': ['Не хватает осколков или карта уже собрана.','Not enough scraps, or the card is already complete.','Nicht genug Fetzen oder Karte bereits vollständig.','Fragments insuffisants ou carte déjà complète.','Frammenti insufficienti o carta già completa.','Za mało skrawków albo karta jest już kompletna.','No hay fragmentos suficientes o la carta ya está completa.','No hay fragmentos suficientes o la carta ya está completa.','Fragmentos insuficientes ou carta já completa.','紙片が足りないか、カードはすでに揃っています。','조각이 부족하거나 이미 모두 보유한 카드입니다.','碎片不足或该卡已集齐。','碎片不足或該卡已集齊。'],
}


def patch_board(s):
    a, b = between(s, '        private function pasteExchange():void', '\n        private function openNameInput():void')
    s = s[:a] + AS_EXCHANGE + s[b:]
    for name in ['function openDeckExchange(', 'function setDeckExchange(', 'function submitDeckExchange(', 'function pasteExchange(']:
        assert s.count(name) == 1, name
    return s


def patch_text(s):
    data = {}
    for var in ['KEYS', 'VALUES']:
        m = re.search(r'private static const ' + var + r':Array=(\[.*?\]);', s, re.S)
        data[var] = (m, json.loads(m[1]))
    keys = data['KEYS'][1]; values = data['VALUES'][1]
    assert len(values) == 14
    for key, row in NEW_KEYS.items():
        assert len(row) == 13, key
        if key in keys:
            continue
        keys.append(key)
        for lang in range(1, 14):
            values[lang].append(row[lang - 1])
    for var in ['VALUES', 'KEYS']:  # replace later match first
        m = re.search(r'private static const ' + var + r':Array=(\[.*?\]);', s, re.S)
        s = s[:m.start(1)] + json.dumps(keys if var == 'KEYS' else values, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
    return s


def patch_script(s):
    a, b = between(s, '    event OnBetaGwentDeckImport(value : int, code : string, craft : bool)', '\n    event OnBetaGwentDeckCreate(')
    return s[:a] + WS_IMPORT.rstrip('\n') + '\n' + s[b:]


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=OUT)
    OUT=parser.parse_args().out.resolve()
    assert not OUT.exists()
    for platform in ['classic', 'nextgen']:
        target = OUT / platform; target.mkdir(parents=True)
        shutil.copytree(UI_FROM / platform / 'ui', target / 'ui')
        src = target / 'ui/src'
        write(src / 'BetaGwentBoard.as', patch_board(read(src / 'BetaGwentBoard.as')))
        write(src / 'BetaGwentExchangeText082.as', patch_text(read(src / 'BetaGwentExchangeText082.as')))
        for folder in COPIES[1:]:
            for name in ['BetaGwentBoard.as', 'BetaGwentExchangeText082.as']:
                shutil.copy2(src / name, target / 'ui' / folder / name)
        extra_ui(target)
        manifest = json.loads((UI_FROM / platform / 'ui-inputs.json').read_text('utf8'))
        manifest['sources'] = {p.name: sha(p) for p in src.glob('*.as')}
        (target / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
        if platform == 'classic':
            shutil.copy2(UI_FROM / 'classic/subimages.json', target / 'subimages.json')
        if platform == 'nextgen':
            for folder in COPIES:
                for name in ['BetaGwentBoard.as', 'BetaGwentExchangeText082.as', 'BetaGwentTextLanguage.as', 'BetaGwentKeywords090.as', 'BetaGwentBanners090.as']:
                    shutil.copy2(src / name, ROOT / 'BetaGwent/ui' / folder / name)
    shutil.copytree(SCRIPTS_FROM, OUT / 'scripts')
    menu = OUT / 'scripts/game/betagwent/developmentBoardMenu.ws'
    write(menu, patch_script(read(menu)))
    shutil.copy2(menu, ROOT / 'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws')
    print(json.dumps(dict(out=str(OUT), newKeys=len(NEW_KEYS))))



# ---- 0.9.0 card inspection: Beta UICardPreview layout (reference screenshots 2026-10-18) ----
AS_DETAIL = r'''        private var detailNav:Array=null;private var detailNavCard:Object=null;
        private function stepCardDetail(delta:int):void
        {
            if(!detailNav||!detailOpen||!detailNavCard)return;
            var at:int=-1;for(var k:int=0;k<detailNav.length;k++)if(int(detailNav[k].templateId)==int(detailNavCard.templateId)){at=k;break;}
            var next:int=at+delta;if(at<0||next<0||next>=detailNav.length)return;
            var target:Object=detailNav[next];openCardDetail(target,{description:target.description},false,true);
        }
        private function detailArrow(parent:Sprite,left:Boolean,callback:Function):void
        {
            // Beta outline chevrons at the screen edges; only when browsing a card list.
            var arrow:Sprite=new Sprite();parent.addChild(arrow);
            arrow.graphics.beginFill(0,0);arrow.graphics.drawRect(0,0,200,220);arrow.graphics.endFill();
            arrow.x=left?0:1720;arrow.y=430;
            var shape:Sprite=new Sprite();shape.mouseEnabled=false;arrow.addChild(shape);
            var tip:Number=left?24:176,back:Number=left?182:18,inner:Number=left?98:102;
            shape.graphics.lineStyle(2,0x9A958A,.9);
            shape.graphics.moveTo(back,30);shape.graphics.lineTo(tip,107);shape.graphics.lineTo(back,184);
            shape.graphics.moveTo(back,46);shape.graphics.lineTo(inner,107);shape.graphics.lineTo(back,168);
            arrow.buttonMode=true;
            arrow.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{shape.alpha=1;uiTween(shape,"alpha",1);});
            arrow.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();uiSound(3);callback();});
            controller.registerControl(arrow,left?"Предыдущая карта":"Следующая карта",callback,null,null,"control",null,new Rectangle(0,0,200,220));
        }
        private function openCardDetail(c:Object,detail:Object,keepBack:Boolean=false,keepNav:Boolean=false):void
        {
            if(!c||c.hidden||enemyAmbush(c))return;if(this.collectionNew&&collectionNew[c.templateId]&&(editingDeck||browsingCatalog))markCollectionSeen(int(c.templateId));clearDrag();clearPlacementGhost();detailOpen=true;
            if(!keepBack)detailBack=[];
            if(!keepNav){
                detailNav=keepBack?null:browsingCatalog?shelfCards178.catalog:editingDeck?shelfCards178.collection:null;
                if(detailNav){var listed:Boolean=false;for each(var item:Object in detailNav)if(int(item.templateId)==int(c.templateId)){listed=true;break;}if(!listed)detailNav=null;}
            }
            detailNavCard=c;
            setChildIndex(detailLayer,numChildren-1);
            setChildIndex(controller,numChildren-1);
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            while(detailLayer.numChildren)detailLayer.removeChildAt(0);
            // UICardPreviewPrefab as in Beta 0.9.24: opaque dark screen, framed by two thin
            // metal rules; name, tags, flavour, divider, power and ability on the left;
            // the large card with its faction glow on the right; "Back" centred below.
            var shade:Sprite=new Sprite();shade.x=-WIDE_PAD;detailLayer.addChild(shade);
            shade.graphics.beginFill(0x0C0B09,1);shade.graphics.drawRect(0,0,1920+2*WIDE_PAD,1080);shade.graphics.endFill();
            shade.graphics.beginFill(0x17130E,.9);shade.graphics.drawRect(0,0,1920+2*WIDE_PAD,113);shade.graphics.drawRect(0,971,1920+2*WIDE_PAD,109);shade.graphics.endFill();
            shade.graphics.lineStyle(2,0x6B5A3E,.95);
            shade.graphics.moveTo(WIDE_PAD+34,113);shade.graphics.lineTo(WIDE_PAD+1886,113);
            shade.graphics.moveTo(WIDE_PAD+34,971);shade.graphics.lineTo(WIDE_PAD+1886,971);
            shade.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();closeCardDetail();});
            var box:Sprite=new Sprite();detailLayer.addChild(box);
            box.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();});
            var entry:Object=BetaGwentFullCatalog.find(c.templateId);
            var original:Object=BetaGwentCardText.find(c.templateId);
            var side:int=int(c.side)||1;
            var cw:Number=468,ch:Number=Math.round(468/BETA_CARD_ASPECT);
            var picture:Sprite=new Sprite();picture.x=1205;picture.y=Math.round(530-ch/2);box.addChild(picture);
            var unit:Boolean=original&&(original.typeMask==4||entry&&entry.leader);
            if(c.templateId>0){
                paintBetaFace(picture,c.templateId,cw,ch,side);
                if(unit)betaPowerField(picture,String(c.power!=null?c.power:original.power),cw,ch,c.power!=null?powerColor(c):0xFFFFFF);
            }else paintCardBack(picture,cw,ch,2);
            picture.filters=[new GlowFilter(side==2?0xE0402A:0x3AA8F0,.9,22,22,2,2)];
            var name:TextField=betaLabel(box,readableText(c.title).toUpperCase(),272,150,880,40,0xF5F0E7,BetaGwentFonts.TITLE,true,null,8);
            if(name.textWidth>860)betaFace(BetaGwentFonts.TITLE,name,Math.max(24,Math.floor(40*850/name.textWidth)),0xF5F0E7,true,null,5);
            betaLabel(box,c.templateId>0?(BetaGwentCardTags.text(c.templateId)||""):"",272,210,760,22,0xD7D0C2,BetaGwentFonts.BODY);
            if(original&&original.flavor.length){
                var flavor:TextField=betaLabel(box,original.flavor,272,264,760,15,0x8C8679,BetaGwentFonts.BODY);
                flavor.wordWrap=true;flavor.multiline=true;flavor.height=48;
                var italic:TextFormat=flavor.getTextFormat();italic.italic=true;flavor.defaultTextFormat=italic;flavor.setTextFormat(italic);
            }
            var rule:Sprite=new Sprite();rule.mouseEnabled=false;box.addChild(rule);
            rule.graphics.lineStyle(3,0x3E3A33,1);rule.graphics.moveTo(250,327);rule.graphics.lineTo(1022,327);
            rule.graphics.lineStyle(1,0x6A645A,.8);rule.graphics.moveTo(262,325);rule.graphics.lineTo(1010,325);
            var top:Number=360;
            if(unit){
                var powerLine:TextField=betaLabel(box,String(c.power!=null?c.power:original.power),264,360,80,52,c.power!=null?powerColor(c):0xFFFFFF,BetaGwentFonts.NUMBERS,false,"center");
                centerBetaNumber(powerLine,304,393,52);
                betaLabel(box,"СИЛА",346,377,400,28,0xF5F0E7,BetaGwentFonts.TITLE,true,null,6);
                top=450;
            }
            var related:Array=c.templateId>0?relatedCards(int(c.templateId),String(detail&&detail.description?detail.description:(entry?entry.description:c.description||""))):[];
            var body:TextField=text(box,cardReading(c,detail,true,true,false,false),272,top,760,24,0xEBE5D8);
            body.height=(related.length?706:950)-top;
            if(related.length)drawRelatedCards(box,c,detail,related);
            detailBody=body;body.mouseEnabled=true;body.selectable=true;
            body.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopImmediatePropagation();e.preventDefault();body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV-e.delta*3));});
            if(detailNav){
                var at:int=-1;for(var k:int=0;k<detailNav.length;k++)if(int(detailNav[k].templateId)==int(c.templateId)){at=k;break;}
                if(at>0)detailArrow(box,true,function():void{stepCardDetail(-1);});
                if(at>=0&&at+1<detailNav.length)detailArrow(box,false,function():void{stepCardDetail(1);});
            }
            // Mod hint kept (UX additions not present in Beta stay), small in the lower band.
            betaLabel(box,detailNav?"Колесо — прокрутить описание · ←/→ — соседние карты · Esc или I — закрыть":"Колесо — прокрутить описание · Esc или I — закрыть",48,1010,800,15,0x8C8679,BetaGwentFonts.BODY);
            editorBetaButton(box,detailBack.length?"Назад к карте":"Назад",860,996,200,52,true,closeCardDetail);
        }
'''


def patch_inspect(s):
    a, b = between(s, '        private function openCardDetail(c:Object,detail:Object,keepBack:Boolean=false):void',
                   '\n        private function isInspectMouse(')
    s = s[:a] + AS_DETAIL.rstrip('\n') + '\n' + s[b:]
    old = 'private function cardReading(c:Object,detail:Object,complete:Boolean=false,skipHeader:Boolean=false):String'
    assert s.count(old) == 1
    s = s.replace(old, 'private function cardReading(c:Object,detail:Object,complete:Boolean=false,skipHeader:Boolean=false,withFlavor:Boolean=true,withState:Boolean=true):String')
    s = s.replace('if(complete){var state:String=BetaGwentUi138.stateLines(c,original);', 'if(complete&&withState){var state:String=BetaGwentUi138.stateLines(c,original);')
    old = 'if(complete&&original&&original.flavor.length)value+="\\n\\n«"+original.flavor+"»";'
    assert s.count(old) == 1, 'flavor line'
    s = s.replace(old, 'if(complete&&withFlavor&&original&&original.flavor.length)value+="\\n\\n«"+original.flavor+"»";')
    old = 'if(detailOpen){e.preventDefault();if(key==27||key==73)closeCardDetail();return;}'
    assert s.count(old) == 1, 'detail keys'
    s = s.replace(old, 'if(detailOpen){e.preventDefault();if(key==27||key==73)closeCardDetail();else if((key==37||key==39)&&detailNav)stepCardDetail(key==37?-1:1);return;}')
    old = 'tutorialFirstRun=false;detailOpen=false;detailBody=null;while(detailLayer.numChildren)detailLayer.removeChildAt(0);'
    assert s.count(old) == 1, 'detail close'
    s = s.replace(old, 'tutorialFirstRun=false;detailOpen=false;detailBody=null;detailNav=null;detailNavCard=null;while(detailLayer.numChildren)detailLayer.removeChildAt(0);')
    old = 'betaLabel(box,"Связанные карты · нажмите, чтобы посмотреть",220,700,750,18,0xD7C498,BetaGwentFonts.BODY).height=30;'
    assert s.count(old) == 1, 'related label'
    s = s.replace(old, 'betaLabel(box,"Связанные карты · нажмите, чтобы посмотреть",272,716,750,18,0xD7C498,BetaGwentFonts.BODY).height=30;')
    old = 'var r:Object=list[i];var tile:Sprite=new Sprite();tile.x=220+i*124;tile.y=732;box.addChild(tile);'
    assert s.count(old) == 1, 'related tiles'
    s = s.replace(old, 'var r:Object=list[i];var tile:Sprite=new Sprite();tile.x=272+i*124;tile.y=750;box.addChild(tile);')
    return s


_patch_board_exchange = patch_board


def patch_board(s):  # noqa: F811 - exchange + inspection, one UI build
    return patch_inspect(_patch_board_exchange(s))


NEW_KEYS.update({
'Назад': ['Назад','Back','Zurück','Retour','Indietro','Wstecz','Atrás','Atrás','Voltar','戻る','뒤로','返回','返回'],
'СИЛА': ['СИЛА','POWER','STÄRKE','PUISSANCE','POTERE','SIŁA','PODER','PODER','PODER','戦力','전투력','战力','戰力'],
'Предыдущая карта': ['Предыдущая карта','Previous card','Vorherige Karte','Carte précédente','Carta precedente','Poprzednia karta','Carta anterior','Carta anterior','Carta anterior','前のカード','이전 카드','上一张卡牌','上一張卡牌'],
'Следующая карта': ['Следующая карта','Next card','Nächste Karte','Carte suivante','Carta successiva','Następna karta','Carta siguiente','Carta siguiente','Próxima carta','次のカード','다음 카드','下一张卡牌','下一張卡牌'],
' · ←/→ — соседние карты': [' · ←/→ — соседние карты',' · ←/→ — neighbouring cards',' · ←/→ — benachbarte Karten',' · ←/→ — cartes voisines',' · ←/→ — carte vicine',' · ←/→ — sąsiednie karty',' · ←/→ — cartas contiguas',' · ←/→ — cartas contiguas',' · ←/→ — cartas vizinhas',' · ←/→ — 隣のカード',' · ←/→ — 인접 카드',' · ←/→ — 相邻卡牌',' · ←/→ — 相鄰卡牌'],
})


# ---- Beta keyword colouring (generated per-card phrases, all 13 locales) ----
def patch_text_language(s):
    old = 'field.defaultTextFormat=format;field.setTextFormat(format);field.scrollV=scroll;\n            layoutButton(field,state);'
    assert s.count(old) == 1, 'TextLanguage.update'
    s = s.replace(old, 'field.defaultTextFormat=format;field.setTextFormat(format);\n            if(state.keywordCard)BetaGwentKeywords090.apply(field,int(state.keywordCard),language);\n            field.scrollV=scroll;\n            layoutButton(field,state);')
    old = '        public static function forget(field:TextField):void{delete fields[field];}'
    assert s.count(old) == 1
    s = s.replace(old, old + '\n        // Beta colours keyword phrases of a card ability; kept across translation refreshes.\n        public static function keywords(field:TextField,templateId:int):void\n        { if(!field||field.type=="input")return;if(!fields[field])track(field);fields[field].keywordCard=templateId;BetaGwentKeywords090.apply(field,templateId,language); }')
    return s


def patch_keyword_calls(s):
    old = '            detailBody=body;body.mouseEnabled=true;body.selectable=true;\n'
    assert s.count(old) == 1, 'detail body'
    s = s.replace(old, '            BetaGwentTextLanguage.keywords(body,int(c.templateId));\n' + old)
    old = '            var body:TextField=text(info,reading,14,10,284,18,0xEDEAE2);body.wordWrap=true;body.multiline=true;\n'
    assert s.count(old) == 1, 'side preview body'
    s = s.replace(old, old + '            if(!hidden)BetaGwentTextLanguage.keywords(body,int(c.templateId));\n')
    return s


_patch_board_before_keywords = patch_board


def patch_board(s):  # noqa: F811
    return patch_keyword_calls(_patch_board_before_keywords(s))


def extra_ui(target):
    """TextLanguage hook + generated keyword table in src and all mirrors."""
    import subprocess, sys as _sys
    src = target / 'ui/src'
    write(src / 'BetaGwentTextLanguage.as', patch_text_language(read(src / 'BetaGwentTextLanguage.as')))
    subprocess.run([_sys.executable, str(Path(__file__).with_name('build_keywords090.py')), str(src)], check=True)
    for folder in COPIES[1:]:
        for name in ['BetaGwentTextLanguage.as', 'BetaGwentKeywords090.as']:
            shutil.copy2(src / name, target / 'ui' / folder / name)


# ---- Round end as in Beta 0.9.24 (video 2026-10-18: ~3 s crowns + score, ~3 s next-round line) ----
AS_ROUND = r'''        private function betaRoundCrownId(side:int,wins:int):int
        {return wins>=2?(side==1?-1525:-1527):wins==1?(side==1?-1524:-1526):-1523;}
        private var roundBannerFor:Object=null;private var roundBannerStart:int=0;
        private static const ROUND_SCORE_MS:int=3000;
        private function drawBetaRoundBanner(parent:Sprite,animate:Boolean):void
        {
            var result:Object=lastRoundResult;if(!result)return;
            if(roundBannerFor!==result){roundBannerFor=result;roundBannerStart=getTimer();}
            var matchWinner:int=int(result.flags)>>4;
            var winner:int=matchWinner>0?matchWinner:result.scores[0]>result.scores[1]?1:result.scores[0]<result.scores[1]?2:3;
            var title:String=matchWinner>0?(winner==1?"ПОБЕДА!":winner==2?"ПОРАЖЕНИЕ!":"НИЧЬЯ!"):(winner==1?"ВЫ ВЫИГРАЛИ РАУНД!":winner==2?"ПРОТИВНИК ВЫИГРАЛ РАУНД!":"НИЧЬЯ!");
            var next:int=int(result.round)+1;
            var line:String=matchWinner>0?"Партия завершена":next>=3?"Начало финального раунда!":"Начало второго раунда!";
            var root:Sprite=new Sprite();root.mouseEnabled=false;root.mouseChildren=false;parent.addChild(root);
            // Beta tints the whole screen: deep blue for your round, deep red for the opponent's.
            root.graphics.beginFill(winner==1?0x020F1C:winner==2?0x1C0202:0x0C0C0C,.86);root.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);root.graphics.endFill();
            var box:Sprite=new Sprite();box.x=499;box.y=440;root.addChild(box);
            box.graphics.beginFill(0x000000,.94);box.graphics.drawRect(0,0,929,136);box.graphics.endFill();
            var bar:Sprite=new Sprite();box.addChild(bar);paintArt(bar,BetaGwentHud104.POPUP_TITLE,929,70,0,0);
            bar.transform.colorTransform=winner==1?new ColorTransform(.35,.9,1.6):winner==2?new ColorTransform(1.9,.45,.35):new ColorTransform(1,1,1);
            box.graphics.lineStyle(2,0x8C8C8C,.9);box.graphics.drawRect(0,0,929,136);
            box.graphics.lineStyle(1,0x5A5A5A,.9);box.graphics.moveTo(0,70);box.graphics.lineTo(929,70);
            for each(var corner:Array in [[0,0,1,1],[929,0,-1,1],[0,136,1,-1],[929,136,-1,-1]]){
                box.graphics.lineStyle(2,0xBDBDBD,1);box.graphics.moveTo(corner[0],corner[1]+corner[3]*9);box.graphics.lineTo(corner[0],corner[1]);box.graphics.lineTo(corner[0]+corner[2]*9,corner[1]);
            }
            betaLabel(box,title,0,12,929,34,0xEDE9E2,BetaGwentFonts.TITLE,true,"center",7);
            // Phase 1: round crowns around the score, "yours | theirs", winner's number in gold.
            var scoreRow:Sprite=new Sprite();box.addChild(scoreRow);
            var own:int=int(result.crowns?result.crowns[0]:0),enemy:int=int(result.crowns?result.crowns[1]:0);
            paintArt(scoreRow,betaRoundCrownId(1,own),51,45,324,79);
            paintArt(scoreRow,betaRoundCrownId(2,enemy),51,45,563,79);
            var ownScore:TextField=betaLabel(scoreRow,String(result.scores[0]),380,82,100,30,winner==1?0xFFD52A:0xF2F0EA,BetaGwentFonts.NUMBERS,false,"center");
            var enemyScore:TextField=betaLabel(scoreRow,String(result.scores[1]),448,82,100,30,winner==2?0xFFD52A:0xF2F0EA,BetaGwentFonts.NUMBERS,false,"center");
            centerBetaNumber(ownScore,430,103,30);centerBetaNumber(enemyScore,498,103,30);
            ownScore.filters=enemyScore.filters=[new GlowFilter(0,1,4,4,4,1)];
            scoreRow.graphics.lineStyle(2,0x8C8C8C,.9);scoreRow.graphics.moveTo(464,86);scoreRow.graphics.lineTo(464,118);
            // Phase 2: the next-round line replaces the score in the same lower band.
            var lineField:TextField=betaLabel(box,line,0,90,929,20,0xF2F0EA,BetaGwentFonts.BODY,false,"center");
            var phase:Function=function(e:Event=null):void{
                var second:Boolean=getTimer()-roundBannerStart>=ROUND_SCORE_MS;
                scoreRow.visible=!second;lineField.visible=second;
            };
            phase();
            root.addEventListener(Event.ENTER_FRAME,phase);
            root.addEventListener(Event.REMOVED_FROM_STAGE,function(e:Event):void{root.removeEventListener(Event.ENTER_FRAME,phase);});
            if(animate&&!reducedMotion&&getTimer()-roundBannerStart<400){
                animations.push({sprite:root,fromX:0,fromY:0,toX:0,toY:0,appear:true,remove:false,duration:380});root.alpha=0;
            }
        }
'''


def patch_round(s):
    a, b = between(s, '        private function drawBetaRoundBanner(parent:Sprite,animate:Boolean):void',
                   '\n        private function drawYourTurnBanner():void')
    s = s[:a] + AS_ROUND.rstrip('\n') + '\n' + s[b:]
    old = 'case 5:return 1100;case 6:return 1050;'
    assert s.count(old) == 1, 'round cue duration'
    s = s.replace(old, 'case 5:return 1100;case 6:return 6000;')
    return s


_patch_board_before_round = patch_board


def patch_board(s):  # noqa: F811
    return patch_round(_patch_board_before_round(s))


# ---- Beta big-card faction banners: lazy native pages (tools/features082/build_banners090.py) ----
def banners_class():
    meta = json.loads((ROOT / 'BetaGwent/build/banners090-seamfix-input/banners.json').read_text('utf8'))
    data = {k: [v['x'], v['y'], v['w'], v['h'], *v['px']] for k, v in sorted(meta['banners'].items())}
    return '''package
{
    import flash.display.Loader;
    import flash.display.Sprite;
    import flash.events.Event;
    import flash.events.IOErrorEvent;
    import flash.events.SecurityErrorEvent;
    import flash.events.TimerEvent;
    import flash.net.URLRequest;
    import flash.utils.Timer;
    // Beta 0.9.24 LargeCardMesh banners (faction x Bronze/Silver/Gold; leaders use Gold),
    // Only the EdgeTex banner mesh, excluding MainTex art tiles and frame UVs.
    // Placement: x, y, w, h, source px width/height.
    public class BetaGwentBanners090
    {
        private static const DATA:Object=%s;
        private static const FACTIONS:Object={1:"Neutral",2:"Monsters",4:"Nilfgaard",8:"Northern",16:"Scoiatael",32:"Skellige"};
        private static var live:int=0;
        private static var retired:Array=[];
        private static var reaper:Timer;
        public static function key(faction:int,tier:int):String
        {
            var f:String=FACTIONS[faction]||"Neutral";var t:String=tier==1||tier==8?"Gold":tier==4?"Silver":"Bronze";
            if(t=="Silver"&&!DATA[f+"_Silver"])t="Bronze";
            return f+"_"+t;
        }
        // Adds the banner page above the art; on a load failure removes it and calls fallback.
        public static function paint(parent:Sprite,faction:int,tier:int,w:Number,h:Number,fallback:Function):Boolean
        {
            var name:String=key(faction,tier);var d:Array=DATA[name];if(!d||!parent||live>=8)return false;
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;
            holder.x=d[0]*w;holder.y=d[1]*h;holder.scaleX=d[2]*w/d[4];holder.scaleY=d[3]*h/d[5];parent.addChild(holder);
            var loader:Loader=new Loader();holder.addChild(loader);live++;
            var state:Object={loader:loader,done:false,retired:false};
            var complete:Function=function(e:Event):void{state.done=true;};
            var retire:Function=function():void{
                if(state.retired)return;state.retired=true;loader.visible=false;
                retired.push(state);
                if(!reaper){reaper=new Timer(40);reaper.addEventListener(TimerEvent.TIMER,reap);reaper.start();}
            };
            var failed:Function=function(e:Event):void{
                state.done=true;if(state.retired)return;
                trace("UI_ERROR banner_load_failed="+name);
                retire();
                if(holder.parent)holder.parent.removeChild(holder);
                if(fallback!=null)fallback();
            };
            var removed:Function=function(e:Event):void{if(e.target==holder)retire();};
            state.complete=complete;state.failed=failed;state.removed=removed;state.holder=holder;
            loader.contentLoaderInfo.addEventListener(Event.COMPLETE,complete);
            loader.contentLoaderInfo.addEventListener(IOErrorEvent.IO_ERROR,failed);
            loader.contentLoaderInfo.addEventListener(SecurityErrorEvent.SECURITY_ERROR,failed);
            holder.addEventListener(Event.REMOVED_FROM_STAGE,removed);
            try{loader.load(new URLRequest("swf/betagwentbanners/"+name+".swf"));}catch(error:Error){failed(null);}
            return true;
        }
        // Do not cancel in-flight native loads or unload inside loader events.
        private static function reap(e:TimerEvent):void
        {
            var keep:Array=[];
            for each(var state:Object in retired){
                if(!state.done){keep.push(state);continue;}
                var loader:Loader=state.loader;
                loader.contentLoaderInfo.removeEventListener(Event.COMPLETE,state.complete);
                loader.contentLoaderInfo.removeEventListener(IOErrorEvent.IO_ERROR,state.failed);
                loader.contentLoaderInfo.removeEventListener(SecurityErrorEvent.SECURITY_ERROR,state.failed);
                state.holder.removeEventListener(Event.REMOVED_FROM_STAGE,state.removed);
                if(loader.parent)loader.parent.removeChild(loader);
                try{loader.unloadAndStop(false);}catch(error:Error){}
                live--;
            }
            retired=keep;
            if(!retired.length&&reaper){reaper.stop();reaper.removeEventListener(TimerEvent.TIMER,reap);reaper=null;}
        }
    }
}
''' % json.dumps(data, separators=(',', ':'))


AS_BIG_POWER = r'''        // Big-card power number on the Beta banner (reference: inspection and side preview).
        private function betaBigPowerField(p:Sprite,value:String,w:Number,h:Number,color:uint):TextField
        {
            var size:int=Math.max(16,Math.round(h*.115));
            var field:TextField=text(p,value,w*.015-size,h*.004,size*2,size,color);field.height=size*1.7;
            if(!BetaGwentFonts.apply(field,BetaGwentFonts.NUMBERS,size,color,true,"center")){field.defaultTextFormat=new TextFormat("$NormalFont",size,color,true,null,null,null,null,"center");field.setTextFormat(field.defaultTextFormat);}
            field.filters=[new GlowFilter(0x000000,1,3,3,6,1)];
            centerBetaNumber(field,w*.015,h*.075,size);
            return field;
        }
'''


def patch_banners(s):
    old = 'private function paintBetaFace(p:Sprite,templateId:int,w:Number,h:Number,side:int=0,hover:Boolean=false,motion:Boolean=true):void'
    assert s.count(old) == 1, 'paintBetaFace signature'
    s = s.replace(old, 'private function paintBetaFace(p:Sprite,templateId:int,w:Number,h:Number,side:int=0,hover:Boolean=false,motion:Boolean=true,big:Boolean=false):void')
    old = '''            var b:Array=betaBannerRect(w,h);
            paintArt(p,-1610-(faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:5),b[2],b[3],b[0],b[1]);
        }'''
    assert s.count(old) == 1, 'small banner'
    s = s.replace(old, '''            var b:Array=betaBannerRect(w,h);
            var small:Function=function():void{
                paintArt(p,-1610-(faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:5),b[2],b[3],b[0],b[1]);
            };
            // Large previews wear the card's own Beta banner (Neutral cards: the Neutral one).
            if(!big||!BetaGwentBanners090.paint(p,entry?int(entry.faction):1,tier,w,h,small))small();
        }
''' + AS_BIG_POWER.rstrip('\n'))
    old = '                paintBetaFace(picture,c.templateId,cw,ch,side);\n                if(unit)betaPowerField(picture,'
    assert s.count(old) == 1, 'detail face'
    s = s.replace(old, '                paintBetaFace(picture,c.templateId,cw,ch,side,false,true,true);\n                if(unit)betaBigPowerField(picture,')
    old = '                paintBetaFace(card,c.templateId,w,h,side,animatePortrait);'
    assert s.count(old) == 1, 'side preview face'
    s = s.replace(old, '                paintBetaFace(card,c.templateId,w,h,side,animatePortrait,true,true);')
    old = 'if(c.power!=null&&(!original||original.typeMask==4||int(c.power)>0))betaPowerField(card,String(c.power),w,h,powerColor(c));'
    assert s.count(old) == 1, 'side preview power'
    s = s.replace(old, 'if(c.power!=null&&(!original||original.typeMask==4||int(c.power)>0))betaBigPowerField(card,String(c.power),w,h,powerColor(c));')
    s = s.replace('468/BETA_CARD_ASPECT', '468/BETA_LARGE_CARD_ASPECT')
    s = s.replace('312/BETA_CARD_ASPECT', '312/BETA_LARGE_CARD_ASPECT')
    s = s.replace('private static const BETA_CARD_ASPECT:Number=17.64/21.46;',
                  'private static const BETA_CARD_ASPECT:Number=17.64/21.46;\n        private static const BETA_LARGE_CARD_ASPECT:Number=15.85574533/22.7377556;')
    return s


_patch_board_before_banners = patch_board


def patch_board(s):  # noqa: F811
    return patch_banners(_patch_board_before_banners(s))


_extra_ui_before_banners = extra_ui


def extra_ui(target):  # noqa: F811
    _extra_ui_before_banners(target)
    write(target / 'ui/src/BetaGwentBanners090.as', banners_class())
    for folder in COPIES[1:]:
        shutil.copy2(target / 'ui/src/BetaGwentBanners090.as', target / 'ui' / folder / 'BetaGwentBanners090.as')


AS_TUTORIAL = r'''        private function openTutorial(page:int):void
        {
            var pages:Array=tutorialPages();page=Math.max(0,Math.min(pages.length-1,page));
            clearDrag();clearPlacementGhost();detailOpen=true;detailBack=[];tutorialPage=page;tutorialReturn=-1;
            tutorialLayer.filters=[];tutorialLayer.mouseChildren=true;
            setChildIndex(tutorialLayer,numChildren-1);setChildIndex(detailLayer,numChildren-1);setChildIndex(controller,numChildren-1);
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            while(detailLayer.numChildren)detailLayer.removeChildAt(0);
            while(tutorialLayer.numChildren)tutorialLayer.removeChildAt(0);
            var shade:Sprite=panel(tutorialLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.94);
            shade.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();});
            var box:Sprite=betaFrame(tutorialLayer,240,110,1440,860,-1414);
            var p:Object=pages[page];
            betaLabel(box,"ОБУЧЕНИЕ · "+(page+1)+" / "+pages.length,56,40,1328,18,0xCFB176,BetaGwentFonts.BODY).height=30;
            betaLabel(box,String(p.title),56,76,1328,30,0xF5F0E7,BetaGwentFonts.TITLE,true,null,2).height=50;
            // One grid for all seven pages: 720 px reading column, 40 px gap,
            // 568 px demo. Both start at 140 and finish above the shared footer.
            var body:TextField=text(box,String(p.body),56,140,720,20,0xEBE5D8);body.height=388;body.wordWrap=true;
            detailBody=body;tutorialBody=body;
            var cards:Array=p.cards as Array;
            betaLabel(box,"Карты страницы · нажмите, чтобы посмотреть",56,548,720,15,0xCFB176,BetaGwentFonts.BODY,false,"center").height=24;
            var thumbW:Number=104,thumbH:Number=thumbW/BETA_CARD_ASPECT;
            var stripW:Number=cards.length*thumbW+Math.max(0,cards.length-1)*24;
            var stripX:Number=56+(720-stripW)/2;
            for(var i:int=0;i<cards.length;i++){
                var entry:Object=catalogByTitle(String(cards[i]));if(!entry)continue;
                var tile:Sprite=new Sprite();tile.x=stripX+i*(thumbW+24);tile.y=580;box.addChild(tile);
                paintBetaFace(tile,int(entry.templateId),thumbW,thumbH,1);
                if(int(entry.typeMask)==4)betaPowerField(tile,String(entry.power),thumbW,thumbH,0xFFFFFF);
                var caption:TextField=text(tile,String(entry.title),-4,thumbH+6,thumbW+8,13,0xD8D1C2);
                betaFace(BetaGwentFonts.BODY,caption,13,0xD8D1C2,false,"center");caption.multiline=true;caption.wordWrap=true;caption.height=42;
                var look:Function=tutorialCardOpener(entry,page);
                attachEditorClick(tile,look);controller.registerControl(tile,String(entry.title),look,null,null,"control",null,new Rectangle(0,0,thumbW,thumbH));
            }
            if(p.demo)tutorialDemo(box,p.demo);
            editorBetaButton(box,"‹ Назад",56,768,240,52,page>0,function():void{openTutorial(page-1);});
            editorBetaButton(box,page+1<pages.length?"Далее ›":"Готово",312,768,240,52,true,function():void{if(page+1<pages.length)openTutorial(page+1);else{tutorialFirstRun=false;closeCardDetail();}});
            editorBetaButton(box,tutorialFirstRun?"Пропустить обучение":"Закрыть",1084,768,300,52,true,function():void{tutorialFirstRun=false;closeCardDetail();});
            controller.focusTag("control");
        }
'''


def patch_review(s):
    a,b=between(s,'        private function openTutorial(page:int):void','        private static const DEMO_W:')
    s=s[:a]+AS_TUTORIAL+s[b:]
    changes={
        'private static const DEMO_W:Number=92,DEMO_H:Number=128;':'private static const DEMO_W:Number=92,DEMO_H:Number=92*21.46/17.64;',
        'panel(box,872,140,512,516,0x0B1015,.92);':'panel(box,816,140,568,584,0x0B1015,.96);',
        'stageView.x=872;stageView.y=140;':'stageView.x=816;stageView.y=140;',
        'var rowY:Function=function(side:int):Number{return side==2?40:236;};':'var rowX:Number=demo.pile?52:134;\n            var rowY:Function=function(side:int):Number{return side==2?52:258;};',
        'return 60+slot*98;':'return rowX+6+slot*98;',
        'if(c.armor>0){var a:Sprite=panel(sp,4,4,DEMO_W-8,20,0x0E2A3A,.85);text(a,"Броня "+c.armor,0,0,DEMO_W-8,12,0xBFE3FF).height=20;}':
        'if(c.armor>0){var a:Sprite=panel(sp,4,DEMO_H-24,DEMO_W-8,20,0x0E2A3A,.94);betaLabel(a,"Броня "+c.armor,0,1,DEMO_W-8,12,0xBFE3FF,BetaGwentFonts.BODY,false,"center").height=20;}',
        'scores[1].text=String(s[1]);scores[2].text=String(s[2]);':
        'scores[1].text=String(s[1]);scores[2].text=String(s[2]);\n                for(var side:int=1;side<=2;side++)centerBetaNumber(scores[side],rowX-28,rowY(side)+DEMO_H/2,28);',
        'c.sp.x=400;c.sp.y=236;':'c.sp.x=448;c.sp.y=rowY(1);',
        'betaLabel(stageView,"Противник",12,10,200,14,':'betaLabel(stageView,"Противник",rowX,20,300,14,',
        'betaLabel(stageView,"Вы",12,206,200,14,':'betaLabel(stageView,"Вы",rowX,226,300,14,',
        'panel(stageView,52,rowY(side)-6,300,DEMO_H+12,':'panel(stageView,rowX,rowY(side)-6,300,DEMO_H+12,',
        'var sc:TextField=text(stageView,"0",4,rowY(side)+44,44,26,0xF5F0E7);sc.height=40;scores[side]=sc;':
        'var sc:TextField=betaLabel(stageView,"0",rowX-50,rowY(side),44,28,0xF5F0E7,BetaGwentFonts.NUMBERS,false,"center");sc.height=48;scores[side]=sc;',
        'pileView.x=400;pileView.y=236;':'pileView.x=448;pileView.y=rowY(1);',
        'caption=text(stageView,String(demo.intro),14,392,482,16,0xEBE5D8);caption.height=100;':'caption=text(stageView,String(demo.intro),20,406,528,16,0xEBE5D8);caption.height=94;',
        'panel(stageView,105,150,300,56,':'panel(stageView,134,194,300,48,',
        'tween(banner,105,150,1,900,function():void{tween(banner,105,150,0,400,':'tween(banner,134,194,1,900,function():void{tween(banner,134,194,0,400,',
        'editorBetaButton(box,"Попробовать",1008,676,240,52,':'editorBetaButton(box,"Попробовать",980,654,240,52,',
        'sp.x=158;sp.y=420;':'sp.x=rowX+106;sp.y=420;',
        'tween(sp,158,rowY(int(step.side)),1,450,function():void{tween(sp,158,rowY(int(step.side))-10,0,700,':
        'tween(sp,rowX+106,rowY(int(step.side)),1,450,function():void{tween(sp,rowX+106,rowY(int(step.side))-10,0,700,',
        'band.graphics.drawRoundRect(52,rowY(int(step.side))-6,300,DEMO_H+12,':'band.graphics.drawRoundRect(rowX,rowY(int(step.side))-6,300,DEMO_H+12,',
        'text(band,String(step.text),56,rowY(int(step.side))+DEMO_H-16,':'text(band,String(step.text),rowX+4,rowY(int(step.side))+DEMO_H-16,',
    }
    for old,new in changes.items():
        assert s.count(old)==1, 'tutorial review: '+old
        s=s.replace(old,new)
    return s


_patch_board_before_review=patch_board


def patch_board(s):  # noqa: F811
    return patch_review(_patch_board_before_review(s))


if __name__ == '__main__':
    main()
