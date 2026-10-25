// Source chosen-branch replay. Handlers, policy RNG and new search branches
// are forbidden here. Live round/mulligan boundaries stop speculative replay.
struct SBetaOriginalLiveStep { var finished, failed : bool; var mutations, callbacks : int; var phase : string; }
class CBetaOriginalReplay extends IScriptable {
    public var game : CBetaGwentDuelSession;public var tree : CBetaOriginalGameTree;
    public var choices : CBetaOriginalChoiceHandlers;public var node : CBetaOriginalNode;
    public var finished, failed : bool;public var error : string;public var callbacks : int;
    public function Fail(message : string){failed=true;error=message;}
    public function Start(runtime : CBetaOriginalRuntime, p : CBetaOriginalPersonality, live : CBetaGwentDuelSession, chosen : CBetaOriginalNode) : bool {
        var i : int;game=live;
        if(game.IsPending() || game.waiting || game.IsFatal()){Fail("Original live replay requires a stable turn");return false;}
        tree=new CBetaOriginalGameTree in this;tree.runtime=runtime;tree.p=p;
        choices=new CBetaOriginalChoiceHandlers in this;choices.runtime=runtime;choices.p=p;choices.replayOnly=true;
        node=new CBetaOriginalNode in this;node.Initialize();node.game=game;node.cardId=chosen.cardId;
        node.decisionSide=chosen.decisionSide;node.decisionRow=chosen.decisionRow;node.decisionIndex=chosen.decisionIndex;
        node.executingPlayerId=game.match.currentPlayerId;
        for(i=0;i<chosen.choiceRecords.Size();i+=1)node.choiceRecords.PushBack(choices.CopyRecord(chosen.choiceRecords[i]));
        finished=false;callbacks=0;return true;
    }
    public function Step() : SBetaOriginalLiveStep {
        var result : SBetaOriginalLiveStep;result.phase="replay";
        if(finished || failed){result.finished=finished;result.failed=failed;return result;}
        if(!node.started){node.started=true;tree.PerformInitial(node);}
        else if(node.awaitingInitialPlacement)tree.PlaceInitialLeader(node);
        else if(game.IsPending() && !game.mulligan) {
            if(!node.activeChoice && node.choiceCursor>=node.choiceRecords.Size()){Fail("Selected original node lacks a live request record");result.failed=true;return result;}
            choices.Request(node);
        } else{Fail("Original replay continuation outside action");result.failed=true;return result;}
        callbacks+=1;result.mutations=1;result.callbacks=callbacks;
        if(tree.failed)Fail(tree.error);if(choices.failed)Fail(choices.error);
        if(game.IsFatal())Fail("Fatal during original action replay: "+game.GetMessage());
        if(!failed && (game.waiting || game.mulligan || !game.IsPending())) {
            if(node.activeChoice)Fail("Original live action ended before whole choice set");
            if(node.choiceCursor!=node.choiceRecords.Size())Fail("Selected original node has unused live decision records");
            if(!failed)finished=true;
        }
        result.finished=finished;result.failed=failed;return result;
    }
}
class CBetaOriginalTurnController extends IScriptable {
    public var runtime : CBetaOriginalRuntime;public var p : CBetaOriginalPersonality;public var live : CBetaGwentDuelSession;
    public var tree : CBetaOriginalGameTree;public var search : CBetaOriginalAlphaBeta;
    public var root, chosen : CBetaOriginalNode;public var replay : CBetaOriginalReplay;
    public var finished, failed, forceRequested : bool;public var error, playmakerError : string;
    public var forceAfterMs, searchCallbacks : int;
    public function Fail(message : string){failed=true;error=message;}
    public function Start(game : CBetaGwentDuelSession, ownerRuntime : CBetaOriginalRuntime, personality : CBetaOriginalPersonality) : bool {
        var simulated : CBetaGwentDuelSession;
        runtime=ownerRuntime;p=personality;live=game;
        if(p.TreeSearchType!="AlphaBeta" || p.EvaluatorType!="MiniMax" || p.CardPickerType!="BestCardForPersonality"){Fail("Original policy path not ported: "+p.profileName);return false;}
        forceAfterMs=(int)((p.MaxTimeAllowed+1.0f)*1000.0f);forceRequested=false;searchCallbacks=0;finished=false;failed=false;replay=NULL;
        tree=new CBetaOriginalGameTree in this;tree.runtime=runtime;tree.p=p;
        tree.choices=new CBetaOriginalChoiceHandlers in this;tree.choices.runtime=runtime;tree.choices.p=p;
        tree.evaluator=new CBetaOriginalMiniMax in this;tree.evaluator.personality=p;
        simulated=runtime.CloneSession(game);simulated.externalPolicyMask=3;root=tree.Root(simulated);
        if(tree.failed){Fail(tree.error);return false;}
        search=new CBetaOriginalAlphaBeta in this;search.hooks=tree;search.Start(root,p,game.match.currentPlayerId);return true;
    }
    public function Choose() {
        var maker : CBetaOriginalPlayMaker;var candidates : array<CBetaOriginalNode>;var i : int;
        maker=new CBetaOriginalPlayMaker in this;maker.Apply(root,p);
        // Original BaseSearchTree catches PlayMaker exceptions independently
        // of the module's subsequent status/restriction filter.
        if(maker.failed)playmakerError="Original PlayMaker read an incomplete/invalid node";
        for(i=0;i<root.children.Size();i+=1)if(root.children[i].status==1 && root.children[i].hasState)candidates.PushBack(root.children[i]);
        chosen=BetaOriginalBestNode(candidates);if(!chosen){Fail("Original search produced no complete legal node; fallback module not ported");return;}
        replay=new CBetaOriginalReplay in this;if(!replay.Start(runtime,p,live,chosen))Fail(replay.error);
    }
    // Caller supplies elapsed milliseconds for this turn, avoiding a clock
    // dependency or a long-running absolute integer clock in portable logic.
    public function Step(elapsedMilliseconds : int) : SBetaOriginalLiveStep {
        var result : SBetaOriginalLiveStep;var step : SBetaOriginalSearchStep;var before : int;
        if(finished || failed){result.finished=finished;result.failed=failed;return result;}
        if(!search.finished) {
            result.phase="search";
            if(!forceRequested && elapsedMilliseconds>=forceAfterMs){search.RequestStop();forceRequested=true;}
            before=tree.mutations;step=search.Step(1,32);searchCallbacks+=1;result.mutations=tree.mutations-before;
            if(result.mutations>1 || step.actionAttempts>1)Fail("Original search exceeded one battle action per callback");
            if(tree.failed)Fail(tree.error);result.failed=failed;return result;
        }
        if(!replay){Choose();result.phase="pick";result.failed=failed;return result;}
        result=replay.Step();finished=result.finished;if(replay.failed)Fail(replay.error);result.failed=failed;return result;
    }
}
