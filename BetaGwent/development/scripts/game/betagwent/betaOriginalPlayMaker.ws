// Direct source PlayMaker strategy selection and revised-score correction.
// No simulations or other AI policy calls are made in this component.
function BetaOriginalSign(value : int) : string {
    if(value>0)return "Ahead";if(value<0)return "Behind";return "Drawing";
}
function BetaOriginalHandCount(game : CBetaGwentDuelSession, side : int) : int {
    var i, count : int;var s : SBetaGwentCardSnapshot;
    for(i=0;i<game.live.Size();i+=1){s=game.live[i].Snapshot();if(s.positionPlayerId==side && s.locationMask==8 && s.canBePlayed)count+=1;}
    return count;
}
function BetaOriginalCarryover(game : CBetaGwentDuelSession, side : int) : int {
    var i, value : int;var s : SBetaGwentCardSnapshot;
    for(i=0;i<game.live.Size();i+=1){s=game.live[i].Snapshot();if(s.positionPlayerId==side && (s.locationMask & 7)!=0 && (s.tokenMask & 1)!=0)value+=s.power.currentPower;}
    return value;
}
class CBetaOriginalPlayMaker extends IScriptable {
    public var root, passNode, best, strongest : CBetaOriginalNode;
    public var p : CBetaOriginalPersonality;
    public var side, opponent, turn, diff, carryDiff, hand : int;
    public var scoreStatus, carryStatus, cardStatus, passStatus, round, chosenStrategy : string;
    public var failed : bool;
    public function OriginalDiff(node : CBetaOriginalNode) : int {
        var r : SBetaGwentRoundResult;
        if(!node || !node.hasState || !node.game){failed=true;return 0;}
        if(node.game.match.roundNumber==root.game.match.roundNumber)return node.game.Score(side)-node.game.Score(opponent);
        if(node.game.match.results.Size()==0){failed=true;return 0;}
        r=node.game.match.results[node.game.match.results.Size()-1];
        if(side==1)return r.scoreOne-r.scoreTwo;return r.scoreTwo-r.scoreOne;
    }
    public function Determine(initial : CBetaOriginalNode, personality : CBetaOriginalPersonality) : string {
        var game : CBetaGwentDuelSession;var i, first, tempo, value : int;var node : CBetaOriginalNode;
        root=initial;p=personality;side=root.executingPlayerId;opponent=3-side;failed=false;game=root.game;
        turn=game.match.roundTurnIndex;diff=game.Score(side)-game.Score(opponent);scoreStatus=BetaOriginalSign(diff);
        carryDiff=BetaOriginalCarryover(game,side)-BetaOriginalCarryover(game,opponent);carryStatus=BetaOriginalSign(carryDiff);
        hand=BetaOriginalHandCount(game,side);cardStatus=BetaOriginalSign(hand-BetaOriginalHandCount(game,opponent));
        passStatus="OpponentStillPlaying";
        if((opponent==1 && game.match.playerOne.hasPassed) || (opponent==2 && game.match.playerTwo.hasPassed))passStatus="OpponentPassed";
        else if(BetaOriginalHandCount(game,opponent)==0)passStatus="OpponentWillAutoPass";
        if(game.match.results.Size()>0)first=game.match.results[0].winnerMask;
        if(game.match.roundNumber==1)round="Round1";else if(game.match.roundNumber==3)round="Round3";
        else if(first==side)round="Round2WonFirstRound";else if(first==771)round="Round2DrewFirstRound";else round="Round2LostFirstRound";
        passNode=NULL;best=NULL;strongest=NULL;tempo=(-2147483647-1);
        for(i=0;i<root.children.Size();i+=1) {
            node=root.children[i];if(node.status!=1 || !node.hasState)continue;
            if(node.cardId==0){if(!passNode)passNode=node;continue;}
            if(!best)best=node;value=OriginalDiff(node)-diff;
            if(value>tempo){strongest=node;tempo=value;}
        }
        chosenStrategy=Strategy();return chosenStrategy;
    }
    public function Strategy() : string {
        var playing : bool;var turns : int;
        playing=passStatus=="OpponentStillPlaying";
        if(round=="Round1") {
            if(playing) {
                if(scoreStatus=="Ahead")return "PassIfOpponentCantCatchUpIn1Card";
                if(scoreStatus=="Behind"){if(hand==1)return "PlayIfAbleToOvertakeInOneCard";return "PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard";}
                if(carryStatus=="Ahead")return "PassIfStillWinningOrDrawingOtherwisePlayStrongestCard";
                if(carryStatus=="Behind")return "PlayStrongestCard";
                if(cardStatus=="Behind")return "PlayBestCard";
                if(turn%2!=1)turns=turn/2-1;else turns=(turn-1)/2;
                if(turns>=p.FirstRoundTurnsNeededBeforePassingWhenDrawingAndHavingSameCarryover)return "PassIfStillWinningOrDrawingOtherwisePlayBestCard";
                return "PlayBestCard";
            }
            if(scoreStatus=="Ahead")return "PassIfStillWinningOtherwisePlayBestCard";
            if(scoreStatus=="Behind")return "PlayIfAbleToOvertakeInOneCard";
            if(cardStatus=="Behind")return "PassIfStillWinningOrDrawingOtherwisePlayBestCard";
            if(cardStatus=="Ahead")return "PlayBestCard";return "PlayLowTempoCardIfAbleOtherwisePlayBest";
        }
        if(round=="Round2WonFirstRound") {
            if(!playing){if(scoreStatus=="Behind")return "PlayIfAbleToOvertakeInOneCard";return "PassIfStillWinningOrDrawingOtherwisePlayStrongestCard";}
            if(scoreStatus=="Ahead"){if(carryDiff>=10)return "PassIfStillWinningOtherwisePlayBestCard";return "PassIfOpponentCantCatchUpIn1Card";}
            if(scoreStatus=="Behind")return "PlayLowTempoCardIfAbleOtherwisePass";
            if(turn>2 || p.CanDryPassOnRound2)return "PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass";
            return "PlayLowTempoCardIfAbleOtherwisePass";
        }
        if(round=="Round2LostFirstRound") {
            if(playing){if(scoreStatus=="Ahead")return "PlayLowTempoCardIfAbleOtherwisePlayStrongest";if(scoreStatus=="Behind")return "PlayBestCard";return "PlayStrongestCard";}
            if(scoreStatus=="Ahead")return "PassIfStillWinningOtherwisePlayStrongestCard";
            if(scoreStatus=="Behind")return "PlayStrongestCard";return "PlayLowTempoCardIfAbleOtherwisePlayBest";
        }
        if(round=="Round2DrewFirstRound") {
            if(!playing && scoreStatus=="Ahead")return "PassIfStillWinningOtherwisePlayBestCard";return "DontPassUnlessAllPlayActionsAreDetrimental";
        }
        if(round=="Round3") {
            if(playing){if(scoreStatus=="Ahead")return "DontPassUnlessAllPlayActionsAreDetrimental";return "PlayBestCard";}
            if(scoreStatus=="Behind")return "DontPassUnlessAllPlayActionsAreDetrimental";return "PassIfStillWinningOtherwisePlayBestCard";
        }
        return "Default";
    }
    public function Threshold(winning : bool) : int {
        if(round=="Round1") {
            if(turn<=2){if(winning)return p.VeryFirstTurnWinPointDiffBeforePassingThreshold;return p.VeryFirstTurnLosePointDiffBeforePassingThreshold;}
            if(winning)return p.FirstRoundWinPointDiffBeforePassingThreshold;return p.FirstRoundLosePointDiffBeforePassingThreshold;
        }
        if(winning)return p.WinPointDiffBeforePassingThreshold;return p.LosePointDiffBeforePassingThreshold;
    }
    public function WinningAfterPass(drawing : bool) : bool {
        var game : CBetaGwentDuelSession;var winner, i, value : int;
        if(!passNode)return false;game=passNode.game;if(!passNode.hasState || !game){failed=true;return false;}
        if(passStatus=="OpponentPassed") {
            if(round!="Round3" && round!="Round2DrewFirstRound") {
                if(game.match.results.Size()>0)winner=game.match.results[game.match.results.Size()-1].winnerMask;
            } else for(i=0;i<game.match.results.Size();i+=1)if(game.match.results[i].roundNumber==game.match.roundNumber){winner=game.match.results[i].winnerMask;break;}
            return winner==side || (drawing && winner==771);
        }
        value=game.Score(side)-game.Score(opponent);if(drawing)return value>=0;return value>0;
    }
    public function SetBest(node : CBetaOriginalNode) {
        var passValue, bestValue : float;var winner : CBetaOriginalNode;
        if(!node)return;passValue=BetaOriginalLow();bestValue=BetaOriginalLow();
        if(passNode)passValue=passNode.RevisedScore();if(best)bestValue=best.RevisedScore();
        if(passValue>=bestValue)winner=passNode;else winner=best;
        if(node!=winner && winner)node.revised=winner.RevisedScore()+1.0f;
        BetaOriginalReorder(root,side);
    }
    public function LowTempo() : CBetaOriginalNode {
        var chosen, node : CBetaOriginalNode;var card : CBetaGwentDuelCard;var i, value, current : int;var t : SBetaOriginalTemplate;
        value=2147483647;
        for(i=0;i<root.children.Size();i+=1) {
            node=root.children[i];if(node.cardId==0 || !node.hasState)continue;
            card=node.game.FindCard(node.cardId);if(!card)continue;t=BetaOriginalTemplate(card.TemplateId());
            if(!t.semanticTags.Contains(6))continue;current=OriginalDiff(node);
            if(current>=diff && current<value){chosen=node;value=current;}
        }
        return chosen;
    }
    public function PassVariant(strategy : string, out drawing : bool, out fallback : string) : bool {
        drawing=false;
        switch(strategy) {
        case "PassIfStillWinningOtherwisePlayBestCard": fallback="PlayBestCard";return true;
        case "PassIfStillWinningOrDrawingOtherwisePlayBestCard":drawing=true;fallback="PlayBestCard";return true;
        case "PassIfStillWinningOtherwisePlayStrongestCard":fallback="PlayStrongestCard";return true;
        case "PassIfStillWinningOrDrawingOtherwisePlayStrongestCard":drawing=true;fallback="PlayStrongestCard";return true;
        case "PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePlayBest":fallback="PlayLowTempoCardIfAbleOtherwisePlayBest";return true;
        case "PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePlayBest":drawing=true;fallback="PlayLowTempoCardIfAbleOtherwisePlayBest";return true;
        case "PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePlayStrongest":fallback="PlayLowTempoCardIfAbleOtherwisePlayStrongest";return true;
        case "PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePlayStrongest":drawing=true;fallback="PlayLowTempoCardIfAbleOtherwisePlayStrongest";return true;
        case "PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePass":fallback="PlayLowTempoCardIfAbleOtherwisePass";return true;
        case "PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass":drawing=true;fallback="PlayLowTempoCardIfAbleOtherwisePass";return true;
        }
        return false;
    }
    public function Able(node : CBetaOriginalNode, limit : int) : bool {
        var value : int;value=OriginalDiff(node);return value>0 || Abs(value)<=limit;
    }
    public function Implement(strategy : string) {
        var low, chosen, node : CBetaOriginalNode;var drawing : bool;var fallback : string;var i, highest, value, limit : int;
        if(failed || strategy=="Default")return;
        if(strategy=="Pass"){if(passNode && best && best.RevisedScore()>=passNode.RevisedScore())passNode.revised=best.RevisedScore()+1.0f;return;}
        if(strategy=="PlayBestCard"){if(passNode && best && passNode.RevisedScore()>=best.RevisedScore())passNode.revised=best.RevisedScore()-1.0f;return;}
        if(strategy=="PlayStrongestCard"){if(strongest)SetBest(strongest);else Implement("PlayBestCard");return;}
        if(PassVariant(strategy,drawing,fallback)){if(WinningAfterPass(drawing))Implement("Pass");else Implement(fallback);return;}
        if(strategy=="PlayLowTempoCardIfAbleOtherwisePlayBest" || strategy=="PlayLowTempoCardIfAbleOtherwisePlayStrongest" || strategy=="PlayLowTempoCardIfAbleOtherwisePass") {
            low=LowTempo();if(failed)return;
            if(low)SetBest(low);else if(strategy=="PlayLowTempoCardIfAbleOtherwisePlayBest")Implement("PlayBestCard");
            else if(strategy=="PlayLowTempoCardIfAbleOtherwisePlayStrongest")Implement("PlayStrongestCard");else Implement("Pass");return;
        }
        if(strategy=="DontPassUnlessAllPlayActionsAreDetrimental") {
            highest=(-2147483647-1);
            for(i=0;i<root.children.Size();i+=1) {
                node=root.children[i];if(node.cardId==0)continue;value=OriginalDiff(node);if(failed)return;
                if(value>=diff){if(node!=best){SetBest(node);best=node;}Implement("PlayBestCard");return;}
                if(value>highest){highest=value;chosen=node;}
            }
            if(passNode && chosen){value=OriginalDiff(passNode);if(failed)return;if(highest>value){SetBest(chosen);best=chosen;Implement("PlayBestCard");return;}}
            Implement("Pass");return;
        }
        if(strategy=="PassIfOpponentCantCatchUpIn1Card") {
            if(passNode){value=OriginalDiff(passNode);if(failed)return;if(value<Threshold(scoreStatus=="Ahead"))Implement("PlayBestCard");else Implement("Pass");}return;
        }
        if(strategy=="PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard") {
            if(!best)return;limit=Threshold(scoreStatus=="Ahead");
            if(Able(best,limit))Implement("PlayBestCard");else if(strongest && strongest!=best && Able(strongest,limit))Implement("PlayStrongestCard");else Implement("Pass");return;
        }
        if(strategy=="PlayIfAbleToOvertakeInOneCard") {
            if(best && OriginalDiff(best)>0)Implement("PlayBestCard");else if(strongest && OriginalDiff(strongest)>0)Implement("PlayStrongestCard");else Implement("Pass");return;
        }
        failed=true;
    }
    public function Apply(initial : CBetaOriginalNode, personality : CBetaOriginalPersonality) : bool {
        if(!personality.UsePlayMakerSystemAfterTreeSearch || !initial || initial.children.Size()==0)return false;
        Determine(initial,personality);Implement(chosenStrategy);if(!failed)BetaOriginalReorder(initial,side);return !failed;
    }
}
