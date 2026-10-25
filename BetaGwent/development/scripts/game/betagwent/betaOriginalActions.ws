// One common battle engine. Every TryPlayAction performs at most one battle
// operation and returns -1 until every nested request is resolved.
struct SBetaOriginalMulliganChoice { var side, requestId, cardId : int; }
class CBetaOriginalCardGroup extends IScriptable { public var cardId : int; public var nodes : array<CBetaOriginalNode>; }
class CBetaOriginalChoiceRecord extends IScriptable {
    public var kind : string;public var source, sourceHint : int;public var chosen : array<SBetaOriginalItem>;public var sourceFallback : bool;
}
class CBetaOriginalActiveChoice extends IScriptable {
    public var record : CBetaOriginalChoiceRecord;public var index, sourceId, stage, actor : int;
}
class CBetaOriginalRuntime extends IScriptable {
    public var cloneStamp : int;
    public function CloneSession(game : CBetaGwentDuelSession) : CBetaGwentDuelSession {
        var cloner : CBetaGwentCloner;
        if(cloneStamp==0)cloneStamp=-2000000000;cloneStamp+=1;
        cloner=new CBetaGwentCloner in this;return cloner.CloneSession(game,cloneStamp);
    }
}
function BetaOriginalCardItem(game : CBetaGwentDuelSession, card : CBetaGwentDuelCard) : SBetaOriginalItem {
    var item : SBetaOriginalItem;var s : SBetaGwentCardSnapshot;
    s=card.Snapshot();item.id=s.instanceId;item.templateId=card.TemplateId();item.side=s.positionPlayerId;
    item.zone=s.locationMask;item.index=s.locationIndex;item.power=s.power.currentPower;item.basePower=s.power.basePower;
    item.templateTier=s.runtimeTemplate.tierMask;item.typeMask=s.runtimeTemplate.typeMask;item.tokens=s.tokenMask;
    item.visibleToBoth=(s.tokenMask & 8)==0;item.inExecution=s.isInExecutionStack || game.playStack.Contains(card);item.playable=s.canBePlayed;return item;
}
function BetaOriginalItemBefore(a : SBetaOriginalItem, b : SBetaOriginalItem) : bool {
    if(a.side!=b.side)return a.side<b.side;if(a.zone!=b.zone)return a.zone<b.zone;
    if(a.index!=b.index)return a.index<b.index;return a.id<=b.id;
}
function BetaOriginalStateCards(game : CBetaGwentDuelSession) : array<SBetaOriginalItem> {
    var items : array<SBetaOriginalItem>;var item : SBetaOriginalItem;var i,j : int;
    for(i=0;i<game.live.Size();i+=1)items.PushBack(BetaOriginalCardItem(game,game.live[i]));
    for(i=1;i<items.Size();i+=1){item=items[i];j=i-1;while(j>=0 && !BetaOriginalItemBefore(items[j],item)){items[j+1]=items[j];j-=1;}items[j+1]=item;}
    return items;
}
function BetaOriginalAnchor(game : CBetaGwentDuelSession, side : int, row : int, index : int) : int {
    var i : int;var s : SBetaGwentCardSnapshot;
    for(i=0;i<game.live.Size();i+=1){s=game.live[i].Snapshot();if(s.positionPlayerId==side && s.locationMask==row && s.locationIndex==index)return s.instanceId;}return 0;
}
function BetaOriginalAvailablePositions(game : CBetaGwentDuelSession, card : CBetaGwentDuelCard) : array<SBetaOriginalItem> {
    var result : array<SBetaOriginalItem>;var position : SBetaOriginalItem;var s : SBetaGwentCardSnapshot;
    var t : SBetaOriginalTemplate;var side, own, row, count, i, mask, j : int;
    s=card.Snapshot();t=BetaOriginalTemplate(card.TemplateId());own=s.positionPlayerId;
    if(t.typeMask==2){position.side=own;position.row=32;position.index=-3;result.PushBack(position);return result;}
    for(j=0;j<2;j+=1) {
        side=own;mask=t.placementOwn;if(j==1){side=3-own;mask=t.placementEnemy;}
        for(row=1;row<=4;row*=2)if((mask & row)!=0) {
            if(game.pendingRally==card){if(!game.CanSelectRow(game.requestId,side,row))continue;}
            else if(side!=game.MonsterPlaySide(card,own))continue;
            count=game.CountLocation(side,row);
            if(count<9)for(i=0;i<=count;i+=1){position.side=side;position.row=row;position.index=i;result.PushBack(position);}
        }
    }
    return result;
}
class CBetaOriginalGameTree extends CBetaOriginalTreeHooks {
    public var runtime : CBetaOriginalRuntime;public var p : CBetaOriginalPersonality;
    public var choices : CBetaOriginalChoiceHandlers;public var evaluator : CBetaOriginalMiniMax;
    public var nextId, mutations : int;public var failed : bool;public var error : string;
    public function Fail(message : string){failed=true;error=message;}
    public function Root(game : CBetaGwentDuelSession) : CBetaOriginalNode {
        var node : CBetaOriginalNode;
        if(game.externalPolicyMask!=3 || game.IsPending() || game.waiting || game.IsFatal()){Fail("Original tree requires a stable external-policy turn");return NULL;}
        nextId=1;node=new CBetaOriginalNode in this;node.Initialize();node.id=nextId;nextId+=1;
        node.game=game;node.parentGame=game;node.hasState=true;node.executingPlayerId=game.match.currentPlayerId;node.currentPlayerId=game.match.currentPlayerId;node.status=1;
        choices.BeginSimulation(this,game);InitializeChildren(node);return node;
    }
    public function Child(parentNode : CBetaOriginalNode, cardId : int, position : SBetaOriginalItem) : CBetaOriginalNode {
        var node : CBetaOriginalNode;
        node=new CBetaOriginalNode in this;node.Initialize();node.id=nextId;nextId+=1;node.parentNode=parentNode;node.depth=parentNode.depth+1;
        node.cardId=cardId;node.decisionSide=position.side;node.decisionRow=position.row;node.decisionIndex=position.index;
        node.handlerScore=parentNode.handlerScore;node.parentGame=parentNode.game;return node;
    }
    public function InitializeChildren(node : CBetaOriginalNode) {
        var game : CBetaGwentDuelSession;var hand : array<SBetaOriginalItem>;var positions : array<SBetaOriginalItem>;
        var blank : SBetaOriginalItem;var i,j,side,association : int;var seen : array<int>;var card : CBetaGwentDuelCard;
        var group : CBetaOriginalCardGroup;var childNode : CBetaOriginalNode;var snapshot : SBetaGwentMatchSnapshot;
        node.children.Clear();node.baseGroups.Clear();game=node.game;side=game.match.currentPlayerId;
        snapshot=game.Snapshot();if(snapshot.matchWinnerMask!=0){node.terminal=true;return;}
        if(p.AllowedToPass)node.children.PushBack(Child(node,0,blank));
        hand=BetaOriginalStateCards(game);
        for(i=0;i<hand.Size();i+=1) {
            if(hand[i].side!=side || !hand[i].playable || (hand[i].zone!=8 && (!p.AllowedToUseLeader || hand[i].zone!=64)))continue;
            card=game.FindCard(hand[i].id);if(!game.HasRequiredPlayTarget(card))continue;
            if(seen.Contains(hand[i].templateId))continue;seen.PushBack(hand[i].templateId);
            positions.Clear();association=choices.ExactAssociation(1,hand[i].templateId,1);
            if(association>=0)positions=choices.PlayCard(node,card,association);
            if(choices.failed){Fail(choices.error);return;}
            if(positions.Size()==0)positions=BetaOriginalAvailablePositions(game,card);
            group=new CBetaOriginalCardGroup in this;group.cardId=hand[i].id;
            for(j=0;j<positions.Size();j+=1){childNode=Child(node,hand[i].id,positions[j]);node.children.PushBack(childNode);group.nodes.PushBack(childNode);}
            node.baseGroups.PushBack(group);
        }
    }
    public function PerformInitial(node : CBetaOriginalNode) {
        var game : CBetaGwentDuelSession;var card : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;
        var side,anchor : int;var ok : bool;var definition : SBetaGwentDuelDefinition;
        game=node.game;side=game.match.currentPlayerId;node.executingPlayerId=side;
        if(node.cardId==0)ok=game.Pass(side);
        else {
            card=game.FindCard(node.cardId);if(!card){Fail("Original tree card absent");return;}s=card.Snapshot();
            if(s.locationMask==64){ok=game.UseLeader(side);node.awaitingInitialPlacement=ok;}
            else { definition=card.Definition();
            if(definition.header.typeMask!=4)ok=game.Play(side,node.cardId,1);
            else {
                anchor=BetaOriginalAnchor(game,node.decisionSide,node.decisionRow,node.decisionIndex);
                if(anchor!=0)ok=game.PlayBefore(side,node.cardId,anchor);else ok=game.Play(side,node.cardId,node.decisionRow);
            } }
        }
        mutations+=1;if(!ok)Fail("Common engine rejected original initial action: "+game.GetMessage());
    }
    public function PlaceInitialLeader(node : CBetaOriginalNode) {
        var game : CBetaGwentDuelSession;var anchor : int;var ok : bool;game=node.game;
        if(!game.pendingLeader){Fail("Original leader placement request lost");return;}
        anchor=BetaOriginalAnchor(game,node.decisionSide,node.decisionRow,node.decisionIndex);
        if(anchor!=0)ok=game.SelectPlacementBefore(game.requestId,anchor);else ok=game.SelectRow(game.requestId,node.decisionSide,node.decisionRow);
        node.awaitingInitialPlacement=false;mutations+=1;if(!ok)Fail("Original leader position rejected");
    }
    public function Mulligan(node : CBetaOriginalNode) {
        var game : CBetaGwentDuelSession;var picker : CBetaOriginalMulligan;var hand : array<CBetaGwentDuelCard>;
        var selected : CBetaGwentDuelCard;var stored : SBetaOriginalMulliganChoice;var s : SBetaGwentCardSnapshot;var side,i : int;var ok : bool;
        game=node.game;side=game.RequestDecisionSide();
        if(side!=node.executingPlayerId)ok=game.FinishMulligan(game.requestId);
        else {
            if(node.mulliganCursor<node.mulliganChoices.Size()) {
                stored=node.mulliganChoices[node.mulliganCursor];if(stored.side!=side){Fail("Stored original mulligan seat changed");return;}
            } else {
                picker=new CBetaOriginalMulligan in this;picker.personality=p;
                for(i=0;i<game.live.Size();i+=1){s=game.live[i].Snapshot();if(s.positionPlayerId==side && s.locationMask==8 && s.canBePlayed)hand.PushBack(game.live[i]);}
                picker.SortHand(hand);selected=picker.Choose(hand);stored.side=side;stored.requestId=game.requestId;
                if(selected)stored.cardId=selected.cardState.instanceId;node.mulliganChoices.PushBack(stored);
            }
            if(stored.cardId==0)ok=game.FinishMulligan(game.requestId);else ok=game.SelectMulligan(game.requestId,stored.cardId);node.mulliganCursor+=1;
        }
        mutations+=1;if(!ok)Fail("Common engine rejected original simulated mulligan");
    }
    public function TryPlayAction(node : CBetaOriginalNode) : int {
        var result : int;
        // Native logs must describe the live duel, not speculative clones.
        // Live replay calls PerformInitial/Request directly outside this scope.
        BetaGwentAISimEnter();result=TrySimulatedAction(node);BetaGwentAISimLeave();return result;
    }
    public function TrySimulatedAction(node : CBetaOriginalNode) : int {
        var game : CBetaGwentDuelSession;var snapshot : SBetaGwentMatchSnapshot;
        if(node.status!=0)return 0;
        if(!node.game){node.game=runtime.CloneSession(node.parentNode.game);node.game.recordVisuals=false;}
        game=node.game;
        if(!node.started){node.started=true;PerformInitial(node);}
        else if(node.awaitingInitialPlacement)PlaceInitialLeader(node);
        else if(game.IsPending()) {
            if(game.mulligan)Mulligan(node);else{choices.Request(node);mutations+=1;if(choices.failed)Fail(choices.error);}
        } else if(game.waiting){if(!game.BeginNextRound())Fail("Common next round rejected");mutations+=1;}
        if(game.IsFatal())Fail("Fatal common rules error: "+game.GetMessage());
        if(failed){node.status=3;return 0;}
        if(game.IsPending() || game.waiting)return -1;
        node.currentPlayerId=game.match.currentPlayerId;node.hasState=true;snapshot=game.Snapshot();node.terminal=snapshot.matchWinnerMask!=0;
        InitializeChildren(node);if(failed){node.status=3;return 0;}node.status=1;return 1;
    }
    public function Score(node : CBetaOriginalNode) : float { return evaluator.Evaluate(node); }
}
