// Bounded public counterplay model. Frequencies are priors, not known hands.
function BetaGwentAIControlCard(d : SBetaGwentDuelDefinition) : bool
{
    if(d.effect==1 || d.effect==6 || d.effect==13 || d.effect==17 || d.effect==25 || d.effect==27 || d.effect==28 || d.lockTokens!=0)return true;
    return d.effect==34 && (d.specialMode==801 || d.specialMode==102 || d.specialMode==114 || d.specialMode==125 || d.specialMode==132 || d.specialMode==137);
}
class CBetaGwentPublicResponseAI extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var templates, weights, knownIds : array<int>;
    public var evaluated, rejected, eligibleProfiles, penalty : int;
    public var applyIndex, applyTotal, applySum, applyBestSupport, applyPassChance : int;
    public var applyBest : CBetaGwentDuelSession;
    public var applyDone : bool;
    // Optional frontier for alternating search; original seats are restored by its consumer.
    public var keepBranches097 : bool;
    public var lastReply097 : CBetaGwentDuelSession;
    public var lastWeight097, lastExtra097, lastTemplate097 : int;
    // 0.9.1: weighted public priors over the full pool, before the reply cap.
    public var controlChance, comboChance, publicBurst : int;
    public function Initialize(game : CBetaGwentDuelSession, limit : int)
    {
        var profiles, deck, pool, mass, seen : array<int>;
        var i,j,k,id,weight,faction,best,total,control,combo,knownControl,knownHand,knownCombo : int;
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        templates.Clear(); weights.Clear(); knownIds.Clear(); evaluated=0; rejected=0; penalty=0; eligibleProfiles=0;
        controlChance=0;comboChance=0;publicBurst=10;
        d=BetaGwentDuelDefinition(game.leaderTemplateOne); faction=d.header.factionMask;
        // Public original ownership includes spies now standing on our side.
        for(i=0;i<game.live.Size();i+=1){
            s=game.live[i].Snapshot();
            if(s.ownerId==1 && (s.locationMask&39)!=0 && (s.tokenMask&8)==0 && !game.live[i].createdCopy)
                seen.PushBack(s.runtimeTemplate.templateId);
            if(s.positionPlayerId==1 && s.locationMask==8 && (s.tokenMask&64)!=0){
                knownHand+=1;
                d=game.live[i].Definition();
                if(BetaGwentAIControlCard(d))knownControl=80;
                if(BetaGwentAIEngine(d.header.templateId)>0 || BetaGwentAIFinisher(d.header.templateId))knownCombo=80;
                publicBurst=Max(publicBurst,Max(0,s.power.currentPower)+Max(0,d.amount));
                if(templates.Size()<limit){
                    templates.PushBack(s.runtimeTemplate.templateId);weights.PushBack(100);knownIds.PushBack(s.instanceId);
                }
            }
        }
        // Do not invent an additional hidden removal when every hand card is
        // already public. Still respect the bounded reply simulation cap.
        if(knownHand>0 && knownHand>=game.CountLocation(1,8)){
            controlChance=knownControl;comboChance=knownCombo;return;
        }
        // At maximum difficulty the user authorizes an open starting list.
        // Publicly seen copies are subtracted; the unseen pool is NOT the
        // actual remaining deck, and never reveals draws, mulligans or order.
        if(BetaGwentAIStrength()>=4 && game.aiStartingDeckOne.Size()>0){
            for(i=0;i<game.aiStartingDeckOne.Size();i+=1)deck.PushBack(game.aiStartingDeckOne[i]);
            for(j=0;j<seen.Size();j+=1){k=deck.FindFirst(seen[j]);if(k>=0)deck.Erase(k);}
            for(j=0;j<deck.Size();j+=1){
                k=pool.FindFirst(deck[j]);if(k<0){pool.PushBack(deck[j]);mass.PushBack(24);}else mass[k]+=24;
            }
            eligibleProfiles=1;
        }else BetaGwentAIProfileIds(profiles);
        for(i=0;i<profiles.Size();i+=1){
            id=BetaGwentAIProfileLeader(profiles[i]); d=BetaGwentDuelDefinition(id);
            if(d.header.factionMask!=faction)continue;
            eligibleProfiles+=1;weight=12;if(id==game.leaderTemplateOne)weight=24;
            BetaGwentAIProfileDeck(profiles[i],deck);
            // Soft evidence: custom lists/transforms must not eliminate every prior.
            // Remove seen copies, and reduce support for profiles missing public cards.
            for(j=0;j<seen.Size();j+=1){k=deck.FindFirst(seen[j]);if(k>=0){deck.Erase(k);weight=Min(64,weight+2);}else weight=Max(1,weight/2);}
            for(j=0;j<deck.Size();j+=1){
                k=pool.FindFirst(deck[j]);if(k<0){pool.PushBack(deck[j]);mass.PushBack(weight);}
                else mass[k]+=weight;
            }
        }
        // Unknown hand identities and the exact enemy preset are never read.
        // Count remaining copies after public plays, not merely reply candidates.
        for(i=0;i<pool.Size();i+=1){
            d=BetaGwentDuelDefinition(pool[i]);total+=mass[i];
            if(BetaGwentAIControlCard(d))control+=mass[i];
            if(BetaGwentAIEngine(pool[i])>0 || BetaGwentAIFinisher(pool[i]))combo+=mass[i];
            publicBurst=Max(publicBurst,Min(30,d.header.power+Max(0,d.amount)));
        }
        if(total>0){controlChance=Min(70,control*Min(6,game.CountLocation(1,8))*100/total);comboChance=Min(80,combo*400/total);}
        controlChance=Max(controlChance,knownControl);
        // One common control reply plus the most frequent remaining cards.
        best=-1;
        for(i=0;i<pool.Size();i+=1){
            d=BetaGwentDuelDefinition(pool[i]);
            if(!BetaGwentAIControlCard(d))continue;
            if(best<0 || mass[i]>mass[best])best=i;
        }
        if(best>=0 && templates.Size()<limit && !templates.Contains(pool[best])){templates.PushBack(pool[best]);weights.PushBack(mass[best]);knownIds.PushBack(0);mass[best]=0;}
        for(i=0;i<pool.Size();i+=1)if(templates.Contains(pool[i]))mass[i]=0;
        while(templates.Size()<limit){
            best=-1;for(i=0;i<pool.Size();i+=1)if(mass[i]>0 && (best<0 || mass[i]>mass[best]))best=i;
            if(best<0)break;templates.PushBack(pool[best]);weights.PushBack(mass[best]);knownIds.PushBack(0);mass[best]=0;
        }
    }
    // Return the most disruptive legal modeled reply, in the original seats.
    // All mutations occur in disposable clones; no real turn/request/RNG moves.
    public function Apply(root : CBetaGwentDuelSession) : CBetaGwentDuelSession
    {
        BeginApply(root);while(!ApplyStep(root)){}return FinishApply();
    }
    public function BeginApply(root : CBetaGwentDuelSession)
    {
        var m : SBetaGwentMatchSnapshot;
        evaluated=0;rejected=0;penalty=0;applyIndex=0;applyTotal=0;applySum=0;applyBestSupport=0;applyBest=NULL;
        lastReply097=NULL;lastWeight097=0;lastExtra097=0;lastTemplate097=0;
        m=root.match.Snapshot();applyDone=m.playerOne.hasPassed || m.currentPlayerId!=1 || !m.turnActive;
        applyPassChance=BetaGwentAIReplyPassChance(m.roundNumber,m.playerOne.crowns,m.playerTwo.crowns,root.Score(1)-root.Score(2),root.CountLocation(1,8),root.CountLocation(2,8),root.LeaderAvailable(1));
    }
    public function ApplyStep(root : CBetaGwentDuelSession) : bool
    {
        var h : CBetaGwentDuelSession;var c,slot : CBetaGwentDuelCard;
        var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var i,j,id,gain,extra,w,pendingBefore : int;
        lastReply097=NULL;
        if(applyDone)return true;
        if(applyIndex>templates.Size()){applyDone=true;return true;}
        i=applyIndex;applyIndex+=1;
        if(i==templates.Size() && !root.LeaderAvailable(1) || i<templates.Size() && root.CountLocation(1,8)==0)return false;
        pendingBefore=root.AiPendingCharmValue(2);
        h=root.AiReverseClone();if(!h){rejected+=1;return false;}
        if(i==templates.Size()){c=h.Leader(2);w=1;}
        else {
            // A revealed card is an actual public instance: two copies may
            // have different boosts, charges or other runtime state.
            if(i<knownIds.Size() && knownIds[i]!=0){
                c=h.FindCard(knownIds[i]);
                if(c){s=c.Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8 || (s.tokenMask&64)==0)c=NULL;}
            }else{
                for(j=0;j<h.live.Size();j+=1){
                    s=h.live[j].Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8)continue;
                    if((s.tokenMask&64)!=0 && s.runtimeTemplate.templateId==templates[i]){c=h.live[j];break;}
                    if((s.tokenMask&64)==0 && !slot)slot=h.live[j];
                }
                if(!c && slot){
                    slot.Move(2,512,0);h.registry.Allocate(id);c=new CBetaGwentDuelCard in h;
                    c.Setup(h,id,templates[i],2,8,0);h.registry.Put(id,c);h.live.PushBack(c);
                }
            }
            w=weights[i];
        }
        if(!c){rejected+=1;return false;}s=c.Snapshot();d=c.Definition();gain=h.AiSimPlay(s.instanceId);
        if(gain==-2147483647 || h.IsFatal() || h.IsPending()){rejected+=1;return false;}
        // Losing a pending charm is real counterplay against the first move.
        // If the charm actually fired, its material gain is already negative
        // in the reply's swing and cancels the consumed deferred credit.
        extra=Max(0,gain-d.header.power+pendingBefore-h.AiPendingCharmValue(1));
        if(keepBranches097){lastReply097=h;lastWeight097=w;lastExtra097=extra;lastTemplate097=d.header.templateId;}
        evaluated+=1;applyTotal+=w;applySum+=extra*w;
        if(!applyBest || extra*w>applyBestSupport){applyBestSupport=extra*w;applyBest=h;}
        return false;
    }
    public function FinishApply() : CBetaGwentDuelSession
    {
        if(applyTotal>0)penalty=Min(12,(applySum/applyTotal)*(100-applyPassChance)/200);
        if(applyPassChance==100 || !applyBest)return NULL;
        return applyBest.AiReverseClone();
    }
}
