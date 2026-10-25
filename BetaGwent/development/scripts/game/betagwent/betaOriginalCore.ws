// Direct JS -> WS port of beta_js092/core.cjs. The original source quirks
// are preserved. This staging module is NOT connected to game difficulty yet.
struct SBetaOriginalLocation { var side, row, index : int; }
struct SBetaOriginalQuality { var bronze, silver, gold, leader, carryover, count : int; }
struct SBetaOriginalScore {
    var score, ownValue, oppValue, semantic, handler, generic, stacking, row, preference, handMultiplier : float;
    var round, carryMultiplier : int; var terminal, valid : bool;
}
class CBetaOriginalNode extends IScriptable {
    public var game, parentGame : CBetaGwentDuelSession;
    public var parentNode : CBetaOriginalNode;
    public var children : array<CBetaOriginalNode>;
    public var baseGroups : array<CBetaOriginalCardGroup>;
    public var choiceRecords : array<CBetaOriginalChoiceRecord>;
    public var mulliganChoices : array<SBetaOriginalMulliganChoice>;
    public var choiceCursor, mulliganCursor : int;
    public var activeChoice : CBetaOriginalActiveChoice;
    public var started, awaitingInitialPlacement : bool;
    public var id, depth, status, executingPlayerId, currentPlayerId : int;
    public var cardId, decisionSide, decisionRow, decisionIndex : int;
    public var terminal, hasFirstLocationSet, hasState : bool;
    public var firstLocations : array<SBetaOriginalLocation>;
    public var score, propagatedScore, revised, handlerScore : float;
    public function Initialize() { revised=BetaOriginalLow(); }
    public function RevisedScore() : float {
        if(revised!=BetaOriginalLow())return revised;
        return score+propagatedScore;
    }
}
function BetaOriginalLow() : float { return -340282346638528859811704183484516925440.0f; }
function BetaOriginalHigh() : float { return 340282346638528859811704183484516925440.0f; }
function BetaOriginalValidRound(tag : SBetaOriginalSemantic, index : int) : bool {
    var mask : int;
    if(tag.rounds==7)return true;
    if(tag.rounds==0 || index<0 || index>2)return false;
    mask=1;if(index==1)mask=2;else if(index==2)mask=4;
    return (tag.rounds & mask)!=0;
}
function BetaOriginalTokenType(token : int) : int {
    var boon, hazard : bool;
    boon=(token & 384)!=0;hazard=(token & 7807)!=0;
    if(boon && hazard)return 0;
    if(boon)return 1;if(hazard)return 2;return 0;
}
function BetaOriginalQuality(game : CBetaGwentDuelSession, side : int) : SBetaOriginalQuality {
    var q : SBetaOriginalQuality;var i : int;var s : SBetaGwentCardSnapshot;
    for(i=0;i<game.live.Size();i+=1) {
        s=game.live[i].Snapshot();
        if(s.positionPlayerId!=side || !s.canBePlayed || (s.locationMask!=8 && s.locationMask!=64))continue;
        q.count+=1;
        if(s.runtimeTemplate.tierMask==2)q.bronze+=1;
        else if(s.runtimeTemplate.tierMask==4)q.silver+=1;
        else if(s.runtimeTemplate.tierMask==8)q.gold+=1;
        else if(s.runtimeTemplate.tierMask==1)q.leader+=1;
        if((s.tokenMask & 1)!=0)q.carryover+=s.power.currentPower;
    }
    return q;
}
function BetaOriginalHandValue(q : SBetaOriginalQuality, multiplier : float) : float {
    var value : float;
    value=(float)(q.bronze)*9.0f+(float)(q.silver)*12.0f;
    value+=(float)(q.gold)*15.0f;value+=(float)(q.leader)*14.0f;
    return value*multiplier;
}
class CBetaOriginalMiniMax extends IScriptable {
    public var personality : CBetaOriginalPersonality;
    public var handlerScore : float;
    public function Semantic(node : CBetaOriginalNode, card : CBetaGwentDuelCard) : float {
        var i : int;var t : SBetaOriginalTemplate;var tag : SBetaOriginalSemantic;
        if(node.cardId==0 || !card)return 0.0f;
        t=BetaOriginalTemplate(card.TemplateId());
        for(i=0;i<personality.semanticTags.Size();i+=1) {
            tag=personality.semanticTags[i];
            if(tag.usage!=1 && t.semanticTags.Contains(tag.id) && BetaOriginalValidRound(tag,node.game.match.roundNumber-1))
                return personality.SemanticEvaluatorScoringWeight*tag.weight;
        }
        return 0.0f;
    }
    public function Generic(node : CBetaOriginalNode, card : CBetaGwentDuelCard) : float {
        var value, weather : float;var i : int;var s : SBetaGwentCardSnapshot;var t : SBetaOriginalTemplate;
        if(node.cardId==0 || !card)return 0.0f;
        s=card.Snapshot();t=BetaOriginalTemplate(card.TemplateId());
        if(node.decisionRow==1)value+=personality.MeleePreference;
        else if(node.decisionRow==2)value+=personality.RangedPreference;
        else if(node.decisionRow==4)value+=personality.SiegePreference;
        if(s.runtimeTemplate.typeMask==2)value+=personality.EventCardPreference;
        else if(s.runtimeTemplate.typeMask==4) {
            if(s.runtimeTemplate.tierMask==1)value+=personality.LeaderPreference;else value+=personality.UnitCardPreference;
        } else if(s.runtimeTemplate.typeMask==8)value+=personality.UnitEventCardPreference;
        if(s.runtimeTierMask==2)value+=personality.BronzePreference;
        else if(s.runtimeTierMask==4)value+=personality.SilverPreference;
        else if(s.runtimeTierMask==8)value+=personality.GoldPreference;
        if(t.categories.Contains(52) && node.hasFirstLocationSet) {
            weather=personality.WeatherCardPreference;
            // Source's same-weather flag is never set, so retain that behavior.
            for(i=0;i<node.firstLocations.Size();i+=1)
                if(node.game.WeatherToken(node.firstLocations[i].side,node.firstLocations[i].row)!=0)weather+=personality.PlayWeatherOntoWeatherPreference;
            value+=weather;
        }
        if((s.tokenMask & 128)!=0)value+=personality.DisloyalCardPreference;
        if((s.tokenMask & 8)!=0)value+=personality.AmbushCardPreference;
        return value;
    }
    public function Stacking(node : CBetaOriginalNode) : float {
        var row, count, maximum, minimum, chosen : int;
        if(node.cardId==0 || personality.RowStackingPreference==0.0f || (node.decisionRow & 7)==0)return 0.0f;
        minimum=9;
        for(row=1;row<=4;row*=2) {
            count=node.parentGame.CountLocation(node.decisionSide,row);
            if(count>maximum && count<9)maximum=count;
            if(count<minimum)minimum=count;if(row==node.decisionRow)chosen=count;
        }
        if(maximum==0 || maximum==minimum)return 0.0f;
        if(chosen==maximum)return personality.RowStackingPreference;
        return personality.RowStackingPreference*((float)(chosen-minimum)/(float)(maximum-minimum));
    }
    public function RowEffect(node : CBetaOriginalNode) : float {
        var kind, sign : int;
        if(node.cardId==0 || (node.decisionRow & 7)==0)return 0.0f;
        kind=BetaOriginalTokenType(node.parentGame.WeatherToken(node.decisionSide,node.decisionRow));
        sign=-1;if(node.decisionSide==node.executingPlayerId)sign=1;
        if(kind==1)return personality.PlayingIntoBoonsPreference*(float)(sign);
        if(kind==2)return personality.PlayingIntoHazardsPreference*(float)(sign);
        return 0.0f;
    }
    public function Details(node : CBetaOriginalNode) : SBetaOriginalScore {
        var result : SBetaOriginalScore;var game : CBetaGwentDuelSession;var card : CBetaGwentDuelCard;
        var own, opp : SBetaOriginalQuality;var s : SBetaGwentCardSnapshot;var match : SBetaGwentMatchSnapshot;
        var side, enemy, won, lost, i, winner, ownCarry, oppCarry, ownTurn, oppTurn : int;
        var total : float;
        game=node.game;if(!game || !personality)return result;
        side=node.executingPlayerId;enemy=3-side;match=game.Snapshot();result.valid=true;
        if(match.matchWinnerMask!=0 && match.matchWinnerMask!=3) {
            result.terminal=true;if(match.matchWinnerMask==side)result.score=100.0f;return result;
        }
        if(node.cardId!=0) { card=game.FindCard(node.cardId);if(!card){result.valid=false;return result;} }
        own=BetaOriginalQuality(game,side);opp=BetaOriginalQuality(game,enemy);
        for(i=0;i<match.roundNumber-1;i+=1) {
            winner=game.match.results[i].winnerMask;
            // Original EPlayerId.All=0x303, not the common engine's draw3.
            if(winner==771){won+=1;lost+=1;}else if(winner==side)won+=1;else if(winner==enemy)lost+=1;
        }
        result.round=match.roundNumber;if(won==1 && lost==1)result.round=3;
        result.handMultiplier=1.0f;result.carryMultiplier=1;
        if(result.round==3){result.handMultiplier=1.5f;result.carryMultiplier=0;}
        else if(result.round==2){result.handMultiplier=1.2f;result.carryMultiplier=2;}
        ownCarry=own.carryover;oppCarry=opp.carryover;
        for(i=0;i<game.live.Size();i+=1) {
            s=game.live[i].Snapshot();
            if((s.locationMask & 7)!=0 && (s.tokenMask & 1)!=0) {
                if(s.positionPlayerId==side)ownCarry+=s.power.currentPower;else if(s.positionPlayerId==enemy)oppCarry+=s.power.currentPower;
            }
        }
        if(match.startingPlayerId!=match.currentPlayerId) {
            ownTurn=-1;oppTurn=-1;if(match.startingPlayerId==side)ownTurn=1;if(match.startingPlayerId==enemy)oppTurn=1;
        }
        result.ownValue=BetaOriginalHandValue(own,result.handMultiplier)+(float)(won)*30.0f;
        result.ownValue+=(float)(ownCarry)*(float)(result.carryMultiplier);result.ownValue+=(float)(game.Score(side));
        result.ownValue+=(float)(own.count-opp.count+ownTurn)*5.0f;
        result.oppValue=BetaOriginalHandValue(opp,result.handMultiplier)+(float)(lost)*30.0f;
        result.oppValue+=(float)(oppCarry)*(float)(result.carryMultiplier);result.oppValue+=(float)(game.Score(enemy));
        result.oppValue+=(float)(opp.count-own.count+oppTurn)*5.0f;
        total=result.ownValue+result.oppValue;
        result.semantic=Semantic(node,card);result.handler=node.handlerScore;
        result.generic=Generic(node,card);result.stacking=Stacking(node);result.row=RowEffect(node);
        result.preference=result.semantic+result.handler;result.preference+=result.generic;result.preference+=result.stacking;result.preference+=result.row;
        if(result.preference!=0.0f) { result.ownValue+=total*(result.preference/100.0f);total=result.ownValue+result.oppValue; }
        if(total!=0.0f)result.score=(result.ownValue/total)*100.0f;
        return result;
    }
    public function Evaluate(node : CBetaOriginalNode) : float { var d : SBetaOriginalScore;d=Details(node);return d.score; }
}
class CBetaOriginalMulligan extends IScriptable {
    public var personality : CBetaOriginalPersonality;
    public function SemanticScore(card : CBetaGwentDuelCard, hand : array<CBetaGwentDuelCard>) : float {
        var value : float;var i, duplicates, linked : int;var t, other : SBetaOriginalTemplate;var tag : SBetaOriginalSemantic;
        t=BetaOriginalTemplate(card.TemplateId());value=(float)(card.Power().GetCurrentPower());duplicates=-1;linked=-1;
        for(i=0;i<personality.semanticTags.Size();i+=1) {
            tag=personality.semanticTags[i];if(tag.usage!=2 && t.semanticTags.Contains(tag.id))value+=tag.weight;
        }
        if(t.semanticTags.Contains(2))value-=50.0f;else if(t.semanticTags.Contains(4))value+=50.0f;
        for(i=0;i<hand.Size();i+=1) {
            if(hand[i].TemplateId()==card.TemplateId())duplicates+=1;
            other=BetaOriginalTemplate(hand[i].TemplateId());
            if(t.linkedTemplateId!=0 && other.linkedTemplateId==t.linkedTemplateId)linked+=1;
        }
        if(duplicates>0 && t.semanticTags.Contains(3))value-=(float)(duplicates)*51.0f;
        else if(duplicates>0 && t.semanticTags.Contains(5))value+=(float)(duplicates)*51.0f;
        if(t.linkedTemplateId!=0 && linked>0) {
            if(t.semanticTags.Contains(19))value+=(float)(linked)*55.0f;else if(t.semanticTags.Contains(20))value-=(float)(linked)*51.0f;
        }
        return value;
    }
    public function Choose(hand : array<CBetaGwentDuelCard>) : CBetaGwentDuelCard {
        var best : CBetaGwentDuelCard;var i : int;var lowest, value : float;var s : SBetaGwentCardSnapshot;
        lowest=BetaOriginalHigh();
        if(personality.MulliganPickerType=="LowestPower") {
            for(i=0;i<hand.Size();i+=1)if(!best || hand[i].Power().GetCurrentPower()<=best.Power().GetCurrentPower())best=hand[i];
            if(!best)return NULL;s=best.Snapshot();if(s.runtimeTemplate.power<5)return best;return NULL;
        }
        if(personality.MulliganPickerType!="SemanticPreference")return NULL;
        for(i=0;i<hand.Size();i+=1) { value=SemanticScore(hand[i],hand);if(value<lowest){lowest=value;best=hand[i];} }
        if(lowest<=5.0f)return best;return NULL;
    }
    public function Step(game : CBetaGwentDuelSession) : bool {
        var hand : array<CBetaGwentDuelCard>;var i, side, requestId : int;var selected : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;
        if(!game.mulligan)return false;side=game.RequestDecisionSide();requestId=game.requestId;
        if(!game.IsExternalPolicy(side))return false;
        for(i=0;i<game.live.Size();i+=1) { s=game.live[i].Snapshot();if(s.positionPlayerId==side && s.locationMask==8 && s.canBePlayed)hand.PushBack(game.live[i]); }
        // Player.GetMulliganableCards retains board-manager hand ordering.
        // Stable insertion by location index, then instance ID.
        SortHand(hand);selected=Choose(hand);
        if(!selected)return game.FinishMulligan(requestId);
        return game.SelectMulligan(requestId,selected.cardState.instanceId);
    }
    public function SortHand(out hand : array<CBetaGwentDuelCard>) {
        var i, j : int;var card : CBetaGwentDuelCard;var a,b : SBetaGwentCardSnapshot;
        for(i=1;i<hand.Size();i+=1) {
            card=hand[i];a=card.Snapshot();j=i-1;
            while(j>=0) { b=hand[j].Snapshot();if(b.locationIndex<a.locationIndex || (b.locationIndex==a.locationIndex && b.instanceId<=a.instanceId))break;hand[j+1]=hand[j];j-=1; }
            hand[j+1]=card;
        }
    }
}
function BetaOriginalBestNode(nodes : array<CBetaOriginalNode>) : CBetaOriginalNode {
    var best : CBetaOriginalNode;var i : int;
    if(nodes.Size()==0)return NULL;best=nodes[0];
    for(i=1;i<nodes.Size();i+=1)if(nodes[i].RevisedScore()>best.RevisedScore())best=nodes[i];return best;
}
