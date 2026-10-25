// Exact source request kinds/hints mapped to the existing common FSM phases.
// A replay-only instance refuses handlers, policy RNG and branch generation.
class CBetaOriginalHandlerCache extends IScriptable { public var association : int;public var handler : CBetaOriginalHandler; }
class CBetaOriginalChoiceHandlers extends IScriptable {
    public var runtime : CBetaOriginalRuntime;public var p : CBetaOriginalPersonality;public var tree : CBetaOriginalGameTree;
    public var simulatorRandom : CBetaGwentRandomGenerator;public var cache : array<CBetaOriginalHandlerCache>;
    public var defaultHandler : CBetaOriginalHandler;public var failed, replayOnly : bool;public var error : string;
    public function Fail(message : string){failed=true;error=message;}
    public function BeginSimulation(owner : CBetaOriginalGameTree, game : CBetaGwentDuelSession) {
        var clone : CBetaGwentDuelSession;tree=owner;clone=runtime.CloneSession(game);simulatorRandom=clone.random;
    }
    public function Context(node : CBetaOriginalNode) : CBetaOriginalHandlerContext {
        var ctx : CBetaOriginalHandlerContext;var side,row : int;var token : SBetaOriginalRow;
        ctx=new CBetaOriginalHandlerContext in this;ctx.node=node;ctx.p=p;ctx.cards=BetaOriginalStateCards(node.game);
        ctx.actor=node.executingPlayerId;if(ctx.actor==0)ctx.actor=node.game.match.currentPlayerId;
        ctx.roundIndex=node.game.match.roundNumber-1;ctx.random=simulatorRandom;
        for(side=1;side<=2;side+=1)for(row=1;row<=4;row*=2){token.side=side;token.row=row;token.token=node.game.WeatherToken(side,row);ctx.rows.PushBack(token);}
        return ctx;
    }
    public function ExactAssociation(kind : int, templateId : int, sourceHint : int) : int {
        var i : int;for(i=0;i<p.associations.Size();i+=1)if(p.associations[i].kind==kind && p.associations[i].templateId==templateId && p.associations[i].sourceHint==sourceHint)return i;return -1;
    }
    public function Association(kind : int, templateId : int, sourceHint : int) : int {
        var index : int;index=ExactAssociation(kind,templateId,sourceHint);if(index>=0)return index;
        index=ExactAssociation(kind,templateId,1);if(index>=0)return index;return ExactAssociation(kind,0,sourceHint);
    }
    public function Handler(index : int) : CBetaOriginalHandler {
        var i : int;var scoreEntry : CBetaOriginalHandlerCache;
        if(replayOnly){Fail("Live original replay attempted to run a policy handler");return NULL;}
        if(index<0){if(!defaultHandler)defaultHandler=BetaOriginalCreateHandler(0,this);return defaultHandler;}
        for(i=0;i<cache.Size();i+=1)if(cache[i].association==index)return cache[i].handler;
        scoreEntry=new CBetaOriginalHandlerCache in this;scoreEntry.association=index;scoreEntry.handler=BetaOriginalCreateHandler(p.associations[index].handlerId,this);
        if(!scoreEntry.handler){Fail("Original handler definition missing");return NULL;}cache.PushBack(scoreEntry);return scoreEntry.handler;
    }
    public function PlayCard(node : CBetaOriginalNode, card : CBetaGwentDuelCard, association : int) : array<SBetaOriginalItem> {
        var result : array<SBetaOriginalItem>;var h : CBetaOriginalHandler;var ctx : CBetaOriginalHandlerContext;
        var request : SBetaOriginalRequest;var filtered : SBetaOriginalFilter;
        h=Handler(association);if(failed)return result;ctx=Context(node);ctx.actor=node.game.match.currentPlayerId;
        request.kind="play";request.items=BetaOriginalAvailablePositions(node.game,card);request.minimum=1;request.maximum=1;
        filtered=h.Filter(ctx,request);if(ctx.failed){Fail(ctx.error);return result;}if(!filtered.valid)return result;
        if(h.CanBranchPlacement())return filtered.items;if(filtered.items.Size()>0)result.PushBack(filtered.items[0]);return result;
    }
    public function SourceHint(source : int, kind : string, atNode : int) : int {
        var hints : array<SBetaOriginalSourceHint>;var i, result : int;var found : bool;
        BetaOriginalSourceRequests(source,hints);
        for(i=0;i<hints.Size();i+=1)if(hints[i].kind==kind && (atNode<0 || hints[i].node==atNode)) {
            if(found && result!=hints[i].sourceHint){Fail("Original request needs explicit phase: "+source+"/"+kind);return 0;}
            found=true;result=hints[i].sourceHint;
        }
        if(!found)Fail("Original request sourceHint missing: "+source+"/"+kind);return result;
    }
    public function StagedHint(source : int, kind : string, game : CBetaGwentDuelSession) : int {
        var node, stage, zone, i : int;var card : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;
        node=-1;stage=game.pendingCard.monsterStage;
        if(kind=="templates" && (source==201615 || source==200102)) {
            if(stage!=0 && stage!=1){Fail("Unknown original branch phase");return 0;}node=32;if(stage==1)node=464;
        }
        if(kind=="templates" && (source==201697 || source==201621 || source==201653 || source==132215)) {
            if(stage!=0 && stage!=1){Fail("Unknown original creation phase");return 0;}
            if(source==132215){node=51;if(stage==1)node=615;}else{node=32;if(stage==1)node=387;}
        }
        if(kind=="choices" && (source==200048 || source==200165)) {
            if(stage!=0 && stage!=1){Fail("Unknown original exchange phase");return 0;}
            if(source==200048){node=52;if(stage==1)node=295;}else{node=50;if(stage==1)node=95;}
            zone=8;if(stage==1)zone=16;
            for(i=0;i<game.pendingIds.Size();i+=1){card=game.FindCard(game.pendingIds[i]);if(!card){Fail("Original exchange card absent");return 0;}s=card.Snapshot();if(s.locationMask!=zone){Fail("Original exchange pool has wrong phase");return 0;}}
        }
        if(kind=="choices" && source==153201){if(stage!=0 && stage!=1){Fail("Unknown Restore phase");return 0;}node=23;if(stage==1)node=88;}
        if(kind=="targets" && source==200037){if(stage!=0 && stage!=1){Fail("Unknown Cyclops phase");return 0;}node=18;if(stage==1)node=74;}
        if(kind=="targets" && (source==163201 || source==201611)){if(stage!=0 && stage!=1){Fail("Unknown Treason phase");return 0;}node=18;if(stage==1)node=139;}
        if(kind=="targets" && source==201662) {
            if(game.pendingCard.monsterStored!=201713 && game.pendingCard.monsterStored!=201714){Fail("Unknown Cadaverine mode");return 0;}
            node=156;if(game.pendingCard.monsterStored==201713)node=74;
        }
        if(kind=="targets" && source==201648){node=130;if(game.pendingCard.selectedModeId==201711)node=87;}
        if(kind=="targets" && source==201731){node=1302;if(game.pendingCard.neutralChoice==201734)node=1199;}
        if(kind=="targets" && source==201737){node=1241;if(game.pendingCard.neutralChoice==201740)node=1166;}
        return SourceHint(source,kind,node);
    }
    public function FromTemplate(id : int, side : int) : SBetaOriginalItem {
        var item : SBetaOriginalItem;var t : SBetaOriginalTemplate;var d : SBetaGwentDuelDefinition;
        t=BetaOriginalTemplate(id);if(t.id==0){Fail("Original creation metadata missing");return item;}d=BetaGwentDuelDefinition(id);
        item.id=id;item.templateId=id;item.side=side;item.zone=128;item.power=d.header.power;item.basePower=d.header.power;
        item.templateTier=d.header.tierMask;item.typeMask=d.header.typeMask;item.tokens=t.tokens;item.playable=true;item.visibleToBoth=true;return item;
    }
    public function Describe(node : CBetaOriginalNode) : SBetaOriginalRequest {
        var request : SBetaOriginalRequest;var game : CBetaGwentDuelSession;var info : SBetaGwentRequestSnapshot;
        var hints : array<SBetaOriginalSourceHint>;var kinds : array<string>;var i, source, side, row : int;
        var item : SBetaOriginalItem;var card : CBetaGwentDuelCard;
        var handPower, handThenTarget, adventure, modeCard, donar, talisman, wholeSet : bool;
        game=node.game;request.actor=game.RequestDecisionSide();request.minimum=1;request.maximum=1;
        if(game.pendingRally){request.kind="play";request.source=game.pendingRally.TemplateId();request.sourceHint=1;request.items=BetaOriginalAvailablePositions(game,game.pendingRally);return request;}
        if(!game.pendingCard){Fail("Original request has no authoritative source");return request;}
        source=game.pendingCard.TemplateId();request.source=source;info=game.GetRequestSnapshot();BetaOriginalSourceRequests(source,hints);
        if(hints.Size()==0 && BetaOriginalHasPlayCardsNode(source) && game.pendingPileChoice && game.pendingIds.Size()==1) {
            card=game.FindCard(game.pendingIds[0]);if(!card){Fail("Forced source child absent");return request;}
            request.kind="forced";request.items.PushBack(BetaOriginalCardItem(game,card));return request;
        }
        if(game.pendingRow) {
            request.kind="locations";request.sourceHint=SourceHint(source,"locations",-1);request.minimum=info.limits.minimum;request.maximum=info.limits.maximum;
            for(side=1;side<=2;side+=1)for(row=1;row<=4;row*=2)if(game.CanSelectRow(game.requestId,side,row)){item.side=side;item.row=row;request.items.PushBack(item);}
            if(request.maximum>1)Fail("Multiple original locations not connected");return request;
        }
        for(i=0;i<hints.Size();i+=1)if((hints[i].kind=="targets" || hints[i].kind=="choices") && !kinds.Contains(hints[i].kind))kinds.PushBack(hints[i].kind);
        handPower=source==133301 || source==201656;handThenTarget=source==200162 || source==200031 || source==152106 || source==200020;
        adventure=source==201725 || source==201731 || source==201737;modeCard=source==201603;donar=source==152204;talisman=source==201598;
        if(!game.pendingChoice && kinds.Size()!=1 && !handPower && !handThenTarget && !adventure && !modeCard && !donar && !talisman){Fail("Original request needs explicit kind phase: "+source);return request;}
        if(game.pendingChoice)request.kind="templates";
        else if(handPower){request.kind="targets";if(game.pendingHandPower)request.kind="choices";}
        else if(handThenTarget){request.kind="targets";if(game.pendingCard.monsterStage==0)request.kind="choices";}
        else if(adventure){request.kind="targets";if(game.pendingCard.neutralChoice==201730 || game.pendingCard.neutralChoice==201736)request.kind="choices";}
        else if(modeCard){request.kind="targets";if(game.pendingCard.monsterStored==201695)request.kind="choices";}
        else if(donar){request.kind="choices";if(game.pendingCard.monsterStage==0)request.kind="targets";}
        else if(talisman){request.kind="choices";if(game.pendingCard.selectedModeId==201703)request.kind="targets";}
        else request.kind=kinds[0];
        request.sourceHint=StagedHint(source,request.kind,game);if(failed)return request;
        for(i=0;i<game.pendingIds.Size();i+=1) {
            if(request.kind=="templates")item=FromTemplate(game.pendingIds[i],request.actor);
            else{card=game.FindCard(game.pendingIds[i]);if(!card){Fail("Pending original instance absent");return request;}item=BetaOriginalCardItem(game,card);}
            request.items.PushBack(item);
        }
        wholeSet=((source==200159 || source==162103 || source==200163 || source==162316 || source==200227 || source==201616 || source==122204 || source==200209) && request.kind=="choices") || (source==200218 && request.kind=="targets");
        if(info.limits.maximum>1 && !(wholeSet && info.selectedCount==0)){Fail("Original whole-choice sequencing not mapped");return request;}
        request.minimum=info.limits.minimum;request.maximum=info.limits.maximum;return request;
    }
    public function CopyRecord(record : CBetaOriginalChoiceRecord) : CBetaOriginalChoiceRecord {
        var result : CBetaOriginalChoiceRecord;result=new CBetaOriginalChoiceRecord in this;
        result.kind=record.kind;result.source=record.source;result.sourceHint=record.sourceHint;result.chosen=record.chosen;result.sourceFallback=record.sourceFallback;return result;
    }
    public function MakeRecord(request : SBetaOriginalRequest, chosen : array<SBetaOriginalItem>, fallback : bool) : CBetaOriginalChoiceRecord {
        var record : CBetaOriginalChoiceRecord;record=new CBetaOriginalChoiceRecord in this;
        record.kind=request.kind;record.source=request.source;record.sourceHint=request.sourceHint;record.chosen=chosen;record.sourceFallback=fallback;return record;
    }
    public function Fork(node : CBetaOriginalNode, record : CBetaOriginalChoiceRecord) {
        var sibling : CBetaOriginalNode;var position : SBetaOriginalItem;var i : int;
        if(replayOnly){Fail("Live original replay attempted to generate a branch");return;}
        position.side=node.decisionSide;position.row=node.decisionRow;position.index=node.decisionIndex;sibling=tree.Child(node.parentNode,node.cardId,position);
        for(i=0;i<node.choiceCursor;i+=1)sibling.choiceRecords.PushBack(CopyRecord(node.choiceRecords[i]));
        sibling.choiceRecords.PushBack(record);sibling.handlerScore=node.handlerScore;sibling.mulliganChoices=node.mulliganChoices;node.parentNode.children.PushBack(sibling);
        for(i=0;i<node.parentNode.baseGroups.Size();i+=1)if(node.parentNode.baseGroups[i].cardId==node.cardId){node.parentNode.baseGroups[i].nodes.PushBack(sibling);break;}
    }
    public function Request(node : CBetaOriginalNode) {
        var game : CBetaGwentDuelSession;var request : SBetaOriginalRequest;var ctx : CBetaOriginalHandlerContext;
        var record : CBetaOriginalChoiceRecord;var h : CBetaOriginalHandler;var result : SBetaOriginalDecision;
        var branches, branch : array<SBetaOriginalItem>;var i, kind, anchor : int;var ok : bool;var location : SBetaOriginalLocation;
        if(node.activeChoice){ContinueChoice(node);return;}
        game=node.game;request=Describe(node);if(failed)return;ctx=Context(node);
        if(request.actor!=node.executingPlayerId){Fail("Opposing original reactive decision ownership not mapped");return;}
        kind=3;if(request.kind=="play")kind=1;else if(request.kind=="locations")kind=4;else if(request.kind=="targets")kind=2;
        if(node.choiceCursor<node.choiceRecords.Size()) {
            record=node.choiceRecords[node.choiceCursor];
            if(record.source!=request.source || record.kind!=request.kind || record.sourceHint!=request.sourceHint){Fail("Stored original request identity changed");return;}
        } else {
            if(replayOnly){Fail("Selected original branch lacks a live decision record");return;}
            if(request.kind=="forced")result.chosen=request.items;
            else {
                h=Handler(Association(kind,request.source,request.sourceHint));if(failed)return;result=h.Decision(ctx,request);if(ctx.failed){Fail(ctx.error);return;}
            }
            branches=result.branches;
            if(request.kind=="play") {
                branches.Clear();if(h.CanBranchPlacement() && result.filteredValid)for(i=1;i<result.filtered.Size();i+=1)branches.PushBack(result.filtered[i]);
            }
            for(i=0;i<branches.Size();i+=1){branch.Clear();branch.PushBack(branches[i]);Fork(node,MakeRecord(request,branch,result.sourceFallback));}
            record=MakeRecord(request,result.chosen,result.sourceFallback);node.choiceRecords.PushBack(record);node.handlerScore+=result.propagated;
        }
        node.choiceCursor+=1;
        if(request.maximum>1) {
            node.activeChoice=new CBetaOriginalActiveChoice in this;node.activeChoice.record=record;node.activeChoice.sourceId=game.pendingCard.cardState.instanceId;
            node.activeChoice.stage=game.pendingCard.monsterStage;node.activeChoice.actor=request.actor;ContinueChoice(node);return;
        }
        if(record.chosen.Size()==0)ok=game.FinishTarget(game.requestId);
        else if(request.kind=="play") {
            anchor=BetaOriginalAnchor(game,record.chosen[0].side,record.chosen[0].row,record.chosen[0].index);
            if(anchor!=0)ok=game.SelectPlacementBefore(game.requestId,anchor);else ok=game.SelectRow(game.requestId,record.chosen[0].side,record.chosen[0].row);
        } else if(request.kind=="locations")ok=game.SelectRow(game.requestId,record.chosen[0].side,record.chosen[0].row);
        else if(request.kind=="templates")ok=game.SelectTemplateChoice(game.requestId,record.chosen[0].templateId);
        else ok=game.SelectTarget(game.requestId,record.chosen[0].id);
        if(!ok){Fail("Common engine rejected original stored single choice: "+request.source+"/"+request.kind+"/"+game.GetMessage());return;}
        if(request.kind=="locations" && !node.hasFirstLocationSet) {
            node.hasFirstLocationSet=true;for(i=0;i<record.chosen.Size();i+=1){location.side=record.chosen[i].side;location.row=record.chosen[i].row;location.index=record.chosen[i].index;node.firstLocations.PushBack(location);}
        }
    }
    public function ContinueChoice(node : CBetaOriginalNode) {
        var game : CBetaGwentDuelSession;var active : CBetaOriginalActiveChoice;var id : int;var ok : bool;
        game=node.game;active=node.activeChoice;
        if(!game.pendingCard || game.pendingCard.cardState.instanceId!=active.sourceId || game.RequestDecisionSide()!=active.actor){Fail("Original whole-choice source changed");return;}
        if(active.index<active.record.chosen.Size()) {
            id=active.record.chosen[active.index].id;if(!game.pendingIds.Contains(id)){Fail("Stored original whole-choice is no longer legal");return;}
            ok=game.SelectTarget(game.requestId,id);active.index+=1;
        } else {ok=game.FinishTarget(game.requestId);node.activeChoice=NULL;}
        if(!ok){Fail("Common engine rejected original whole-choice continuation");return;}
        if(active.index==active.record.chosen.Size() && (!game.IsPending() || !game.pendingCard || game.pendingCard.cardState.instanceId!=active.sourceId || game.pendingCard.monsterStage!=active.stage))node.activeChoice=NULL;
    }
}
