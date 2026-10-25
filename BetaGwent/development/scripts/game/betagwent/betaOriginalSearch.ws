// Direct cooperative port of beta_js092/search.cjs. No threads, timers,
// dynamic code or second battle engine. Action callback yields -1/0/1.
class CBetaOriginalTreeHooks extends IScriptable {
    public function TryPlayAction(node : CBetaOriginalNode) : int { return 0; }
    public function Score(node : CBetaOriginalNode) : float { return 0.0f; }
    public function Finished(node : CBetaOriginalNode) : bool { return node.terminal; }
}
class CBetaOriginalSearchFrame extends IScriptable {
    public var node : CBetaOriginalNode;
    public var depth, stage, index : int;
    public var alpha, beta, best : float;
    public var maximize : bool;
}
struct SBetaOriginalSearchValue { var node : CBetaOriginalNode; var value : float; }
struct SBetaOriginalSearchStep { var finished : bool; var actionAttempts, operations, explored, furthestDepth, completedDepth : int; }
function BetaOriginalChildCompare(x : CBetaOriginalNode, y : CBetaOriginalNode, maximize : bool) : int {
    var difference : float;
    if(x.status==y.status) {
        difference=x.RevisedScore()-y.RevisedScore();if(maximize)difference=-difference;
        if(difference<0.0f)return -1;if(difference>0.0f)return 1;return 0;
    }
    // Literal asymmetric original Node.ReorderChildNodes error ordering.
    if(maximize){if(x.status==3)return 1;return -1;}
    if(x.status!=3)return 1;return -1;
}
function BetaOriginalReorder(node : CBetaOriginalNode, origin : int) {
    var i,j : int;var maximize : bool;var child : CBetaOriginalNode;
    if(node.children.Size()<2 || node.children[0].status==0)return;
    maximize=node.children[0].executingPlayerId==origin;
    // Stable input order for ties, matching the chosen JS port convention.
    for(i=1;i<node.children.Size();i+=1) {
        child=node.children[i];j=i-1;
        // Comparator is asymmetric for unlike non-error statuses. Compare the
        // incoming item to its predecessor (as in the JS sort's insertion
        // direction), rather than negating a reversed comparison. In forced
        // partial trees this preserves the source's unfinished-first behavior.
        while(j>=0 && BetaOriginalChildCompare(child,node.children[j],maximize)<0) {
            node.children[j+1]=node.children[j];j-=1;
        }
        node.children[j+1]=child;
    }
}
class CBetaOriginalAlphaBeta extends IScriptable {
    public var hooks : CBetaOriginalTreeHooks;
    public var personality : CBetaOriginalPersonality;
    public var root, lastNode : CBetaOriginalNode;
    public var frames : array<CBetaOriginalSearchFrame>;
    public var buffer0, buffer1 : array<SBetaOriginalSearchValue>;
    public var finalQueue : array<CBetaOriginalNode>;
    public var finished, stopRequested, iterationActive : bool;
    public var origin, depthLimit, depth, completedDepth, explored, furthest : int;
    public var currentBuffer, rootIndex, phase, finalHead, nodesBefore : int;
    public var lastResult : float;public var finishReason : string;
    public function Start(initial : CBetaOriginalNode, p : CBetaOriginalPersonality, side : int) {
        root=initial;personality=p;origin=side;depthLimit=p.DepthOfChecking;
        if(depthLimit<=0)depthLimit=2147483647;
        depth=-1;completedDepth=-1;explored=0;furthest=0;currentBuffer=0;
        buffer0.Clear();buffer1.Clear();frames.Clear();finalQueue.Clear();
        rootIndex=0;iterationActive=false;phase=0;stopRequested=false;finished=false;
    }
    public function RequestStop(){stopRequested=true;}
    public function Store(node : CBetaOriginalNode, value : float) {
        var i : int;var scoreEntry : SBetaOriginalSearchValue;
        if(currentBuffer==0) {
            for(i=0;i<buffer0.Size();i+=1)if(buffer0[i].node==node){scoreEntry=buffer0[i];scoreEntry.value=value;buffer0[i]=scoreEntry;return;}
            scoreEntry.node=node;scoreEntry.value=value;buffer0.PushBack(scoreEntry);
        } else {
            for(i=0;i<buffer1.Size();i+=1)if(buffer1[i].node==node){scoreEntry=buffer1[i];scoreEntry.value=value;buffer1[i]=scoreEntry;return;}
            scoreEntry.node=node;scoreEntry.value=value;buffer1.PushBack(scoreEntry);
        }
    }
    public function BeginFinish(reason : string) {
        var i : int;
        finishReason=reason;
        if(iterationActive) {
            currentBuffer=1-currentBuffer;
            if(currentBuffer==0)for(i=0;i<buffer0.Size();i+=1)buffer0[i].node.revised=buffer0[i].value;
            else for(i=0;i<buffer1.Size();i+=1)buffer1[i].node.revised=buffer1[i].value;
        }
        frames.Clear();finalQueue.Clear();finalQueue.PushBack(root);finalHead=0;phase=2;
    }
    public function ReturnFrame(value : float) {
        var frame : CBetaOriginalSearchFrame;
        lastResult=value;frame=frames[frames.Size()-1];frames.Erase(frames.Size()-1);lastNode=frame.node;
        if(frames.Size()==0) { frame.node.revised=value;Store(frame.node,value);rootIndex+=1; }
    }
    public function PushFrame(node : CBetaOriginalNode, atDepth : int, alpha : float, beta : float) {
        var frame : CBetaOriginalSearchFrame;
        frame=new CBetaOriginalSearchFrame in this;frame.node=node;frame.depth=atDepth;frame.alpha=alpha;frame.beta=beta;
        frames.PushBack(frame);
    }
    public function Step(maxActionAttempts : int, maxOperations : int) : SBetaOriginalSearchStep {
        var result : SBetaOriginalSearchStep;var attempts, operations, played, i : int;
        var frame : CBetaOriginalSearchFrame;var node : CBetaOriginalNode;var bound : float;
        if(finished){result.finished=true;return result;}
        while(!finished && operations<maxOperations) {
            if(phase==2) {
                if(finalHead>=finalQueue.Size()){finished=true;break;}
                node=finalQueue[finalHead];finalHead+=1;BetaOriginalReorder(node,origin);
                for(i=0;i<node.children.Size();i+=1)if(node.children[i].children.Size()>0)finalQueue.PushBack(node.children[i]);
                operations+=1;continue;
            }
            if(stopRequested){BeginFinish("stopped");operations+=1;continue;}
            if(phase==0) {
                depth+=1;if(depth>=depthLimit){BeginFinish("depth-limit");operations+=1;continue;}
                BetaOriginalReorder(root,origin);iterationActive=true;nodesBefore=explored;rootIndex=0;phase=1;
                operations+=1;continue;
            }
            if(frames.Size()==0) {
                if(rootIndex>=root.children.Size()) {
                    currentBuffer=1-currentBuffer;iterationActive=false;completedDepth=depth;
                    if(nodesBefore==explored)BeginFinish("no-new-nodes");else phase=0;
                    operations+=1;continue;
                }
                PushFrame(root.children[rootIndex],depth,BetaOriginalLow(),BetaOriginalHigh());
            }
            frame=frames[frames.Size()-1];node=frame.node;
            if(frame.stage==0) {
                if(node.status==0) {
                    if(attempts>=maxActionAttempts)break;
                    attempts+=1;played=hooks.TryPlayAction(node);
                    if(played==-1){operations+=1;break;}
                    if(played==1) {
                        explored+=1;if(node.depth>furthest)furthest=node.depth;
                        node.propagatedScore=0.0f;if(node.parentNode)node.propagatedScore=node.parentNode.propagatedScore;
                        node.score=hooks.Score(node);
                    }
                }
                if(node.status!=1){ReturnFrame(node.RevisedScore());operations+=1;continue;}
                if(frame.depth==0 || stopRequested || hooks.Finished(node)){ReturnFrame(node.RevisedScore());operations+=1;continue;}
                BetaOriginalReorder(node,node.executingPlayerId);
                frame.maximize=node.currentPlayerId==origin;frame.best=BetaOriginalHigh();if(frame.maximize)frame.best=BetaOriginalLow();
                frame.index=0;frame.stage=1;
            } else if(frame.stage==1) {
                if(frame.index>=node.children.Size()) {
                    bound=frame.beta;if(frame.maximize)bound=frame.alpha;
                    node.revised=bound;Store(node,bound);ReturnFrame(frame.best);
                } else {
                    frame.stage=2;PushFrame(node.children[frame.index],frame.depth-1,frame.alpha,frame.beta);
                }
            } else {
                if(lastNode.status!=3) {
                    if(frame.maximize) { if(lastResult>frame.best)frame.best=lastResult;if(frame.best>frame.alpha)frame.alpha=frame.best; }
                    else { if(lastResult<frame.best)frame.best=lastResult;if(frame.best<frame.beta)frame.beta=frame.best; }
                    if(frame.beta<=frame.alpha && personality.AllowPruning){node.status=2;frame.index=node.children.Size();}else frame.index+=1;
                } else frame.index+=1;
                frame.stage=1;
            }
            operations+=1;
        }
        result.finished=finished;result.actionAttempts=attempts;result.operations=operations;result.explored=explored;
        result.furthestDepth=furthest;result.completedDepth=completedDepth;return result;
    }
}
