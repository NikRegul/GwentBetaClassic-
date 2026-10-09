"""Apply the reviewed 0.3.3 fixes once; source assertions prevent partial rewrites."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def edit(path, replacements):
    p=ROOT/path;s=p.read_text('utf-8-sig')
    for old,new in replacements:
        assert old in s, (path,old[:120]);s=s.replace(old,new)
    p.write_text(s,'utf-8-sig' if p.suffix=='.ws' else 'utf8')
edit('BetaGwent/ui/src/BetaGwentBoard.as',[
('var lines:Array=opponent.split("\\n");','var lines:Array=readableText(opponent).split("\\n");'),
('private var nameKeyAt:int=-1000;','private var nameKeyAt:int=-1000;\n        private var textPurpose:int=0;\n        private var textLimit:int=48;\n        private var pendingText:String="";\n        private var pendingTextAt:int=0;'),
('if(key>=136)return;','if(key>=136&&key<256)return;'),
('if(typed.length){nameKeyAt=getTimer();editName(typed);}', '''if(typed.length){
                        // Prefer a real Unicode TEXT_INPUT. Some retail GFx builds only send key codes.
                        if(nameRussian&&typed.length==1&&typed.charCodeAt(0)<128){
                            var latin:String="qwertyuiop[]asdfghjkl;'zxcvbnm,.`";
                            var russian:String="йцукенгшщзхъфывапролджэячсмитьбюё";
                            var at:int=latin.indexOf(typed.toLowerCase());
                            if(at>=0)typed=e.shiftKey?russian.charAt(at).toUpperCase():russian.charAt(at);
                        }
                        pendingText=typed;pendingTextAt=getTimer()+35;
                    }'''),
('if(searchDeadline==0||getTimer()<searchDeadline)return;', '''if(nameOpen&&pendingTextAt>0&&getTimer()>=pendingTextAt){var value:String=pendingText;pendingText="";pendingTextAt=0;editName(value);}
            if(searchDeadline==0||getTimer()<searchDeadline)return;'''),
('if(purpose==0)openNameInput();\n                else send("OnBetaGwentControllerSearch",[revision,purpose,field.text]);','openTextInput(purpose,field.text);'),
('if(purpose==0){openNameInput();e.preventDefault();}else if(keyboardStage)keyboardStage.focus=field;','openTextInput(purpose,field.text);e.preventDefault();'),
('nameOpen=false;nameField=null;nameCounter=null;', 'nameOpen=false;nameField=null;nameCounter=null;pendingText="";pendingTextAt=0;'),
('private function openNameInput():void\n        {\n            if(!ready||!editingDeck||nameOpen)return;', '''private function openNameInput():void {openTextInput(0,editorName);}
        private function openTextInput(purpose:int,value:String):void
        {
            if(!ready||nameOpen||purpose==0&&!editingDeck)return;
            textPurpose=purpose;textLimit=purpose==0?48:purpose==1?64:80;'''),
('text(box,"НАЗВАНИЕ КОЛОДЫ",30,20,920,30,0xF5D77F);','text(box,purpose==0?"НАЗВАНИЕ КОЛОДЫ":"ПОИСК КАРТ",30,20,920,30,0xF5D77F);'),
('nameField=text(box,editorName,30,82,940,28);','nameField=text(box,value,30,82,940,28);'),
('nameField.maxChars=48;', 'nameField.maxChars=textLimit;'),
('if(getTimer()-nameKeyAt>70)editName(e.text);','pendingText="";pendingTextAt=0;editName(e.text);'),
('if(next.length>48)return;','if(next.length>textLimit)return;'),
('next.length+" / 48 · Enter — принять · Esc — отменить"','next.length+" / "+textLimit+" · Enter — принять · Esc — отменить"'),
('if(!title.length){nameCounter.text="Введите название колоды.";return;}\n            var value:int=nameRevision;closeNameInput();send("OnBetaGwentDeckNameSubmit",[value,title]);', '''if(textPurpose==0&&!title.length){nameCounter.text="Введите название колоды.";return;}
            var value:int=nameRevision,purpose:int=textPurpose;closeNameInput();
            if(value!=revision)return;
            if(purpose==0)send("OnBetaGwentDeckNameSubmit",[value,title]);
            else if(purpose==1){editorSearch=title;editorPage=0;render();}
            else {catalogSearch=title;catalogPage=0;render();}'''),
('if(!nameField)return;\n            var title:String=', 'if(!nameField)return;\n            if(pendingTextAt>0){editName(pendingText);pendingText="";pendingTextAt=0;}\n            var title:String='),
('text(box,"Можно печатать с клавиатуры или выбирать буквы мышью / контроллером.\\nПринять меняет черновик; затем нажмите «Сохранить колоду».",30,580,940,20,0xB9B4A9).height=58;', 'text(box,textPurpose==0?"Клавиатура или кнопки букв · RU / EN переключает язык ввода.\\nПосле изменения названия сохраните колоду.":"Клавиатура или кнопки букв · RU / EN переключает язык ввода.\\nПустая строка убирает поиск; Enter применяет фильтр.",30,580,940,20,0xB9B4A9).height=58;'),
('nameField.text.length+" / 48 · Enter — принять · Esc — отменить"', 'nameField.text.length+" / "+textLimit+" · Enter — принять · Esc — отменить"'),
('var name:String=side==1?"Геральт":(npcDisplayName&&npcDisplayName.length?npcDisplayName:"Соперник");', 'var name:String=side==1?"Геральт":String(leaderNames[1]||"Соперник");'),
('betaLabel(content,"Соперник: "+npcDeckLabel', 'betaLabel(content,"Соперник: "+npcDisplayName'),
('if(canAct()&&!controller.active)drawBetaHint("Пас",BetaGwentHud104.KEY_LC,function():void{submitBoard("OnBetaGwentBoardPass",[revision]);},true);','// Pass is hold-only; the coin and controller/keyboard progress share the same action.'),
('if(value&&value.indexOf("\\n")<0&&field.textWidth>w-6){', 'if(value&&value.indexOf("\\n")<0&&Math.max(field.textWidth,BetaGwentTextMetrics.width(value,face,size,spacing))>w-6){'),
('while(field.textWidth>w-6&&fit>size*0.6)', 'while(Math.max(field.textWidth,BetaGwentTextMetrics.width(value,face,fit))>w-6&&fit>size*0.35)'),
('betaLabel(b,title.toUpperCase(),0,10,w,22,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2)', 'betaLabel(b,title.toUpperCase(),18,10,w-36,22,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2)'),
('betaLabel(content,title.toUpperCase(),615,46,690,30', 'betaLabel(content,title.toUpperCase(),635,46,650,30'),
('var scoreX:Number=scoreBox[0]-18,scoreY:Number=scoreBox[1]+scoreBox[3]/2-42;', 'var scoreX:Number=scoreBox[0]-18,scoreY:Number=scoreBox[1]+scoreBox[3]/2-42;'),
('if(playing&&activeCue&&activeCue.kind==2&&previousScores[side-1]!=scores[side-1]&&!reducedMotion){', 'centerBetaNumber(value,scoreBox[0]+scoreBox[2]/2,scoreBox[1]+scoreBox[3]/2,60);scoreX=value.x;scoreY=value.y;\n                if(playing&&activeCue&&activeCue.kind==2&&previousScores[side-1]!=scores[side-1]&&!reducedMotion){'),
('private function drawBetaCounter(icon:int,value:int,cx:Number,side:int):void', '''private function centerBetaNumber(field:TextField,cx:Number,cy:Number,size:Number):void
        {
            if(!field.embedFonts){field.y=cy-field.textHeight/2-2;return;}
            var offset:Array=BetaGwentTextMetrics.numberOffset(field.text,size);
            field.x=cx-field.width/2-offset[0];field.y=cy-offset[1];
        }
        private function drawBetaCounter(icon:int,value:int,cx:Number,side:int):void'''),
('rowTotal.setTextFormat(rowTotal.defaultTextFormat);}\n            }','rowTotal.setTextFormat(rowTotal.defaultTextFormat);}\n                if(skin==3)centerBetaNumber(rowTotal,rowScore[0]+rowScore[2]/2,rowScore[1]+rowScore[3]/2,32);\n            }'),
('ready&&editorState.valid,editorAction("OnBetaGwentDeckEditorSave")', 'ready,editorAction("OnBetaGwentDeckEditorSave")'),
])
edit('BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws',[
('return label+"\\n"+archetype;', 'return label+"|BG_DECK|"+archetype;'),
('revision += 1; visualBusy = false; validation = deckDraft.Validation();','revision += 1; visualBusy = false; validation = deckDraft.Validation();\n        LogChannel(\'BetaGwent\',"DECK_VALIDATION slot="+deckDraft.slot+" total="+validation.total+" valid="+validation.valid+" reason="+validation.message);'),
('event OnBetaGwentDeckEditorSave(value : int, title : string)\n    {\n        if (!configured || !deckDraft || value != revision) return false;\n        if (!deckLibrary.Save(deckDraft, title)) { PublishDeckEditor("Не удалось сохранить колоду. Проверьте состав и имя."); return false; }', '''event OnBetaGwentDeckEditorSave(value : int, title : string)
    {
        var validation : SBetaGwentDeckValidation;
        if (!configured || !deckDraft || value != revision) return false;
        validation=deckDraft.Validation();
        if(!validation.valid){PublishDeckEditor(validation.message);return false;}
        title=StrLeft(title,48);
        if (!deckLibrary.Save(deckDraft, title)) { LogChannel('BetaGwent',"DECK_SAVE_REJECT slot="+deckDraft.slot+" reason=profileStorage");PublishDeckEditor("Не удалось записать колоду в сохранение."); return false; }'''),
])
edit('BetaGwent/ui/src/BetaGwentBoard.as',[
('readableText(opponent).split("\\n")','readableText(opponent).split("|BG_DECK|").join("\\n").split("\\n")'),
])
edit('BetaGwent/development/scripts/game/betagwent/deckBuilder.ws',[
('draft.title = preset.title;', 'draft.title = StrLeft(preset.title,48);'),
])
