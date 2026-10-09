// Bounded public counterplay model. Frequencies are priors, not known hands.
class CBetaGwentPublicResponseAI extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var templates, weights : array<int>;
    public var evaluated, rejected, eligibleProfiles, penalty : int;
    public function Initialize(game : CBetaGwentDuelSession, limit : int)
    {
        var profiles, deck, pool, mass, seen : array<int>;
        var i,j,k,id,weight,faction,best : int;
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        templates.Clear(); weights.Clear(); evaluated=0; rejected=0; penalty=0; eligibleProfiles=0;
        d=BetaGwentDuelDefinition(game.leaderTemplateOne); faction=d.header.factionMask;
        // Public original ownership includes spies now standing on our side.
        for(i=0;i<game.live.Size();i+=1){
            s=game.live[i].Snapshot();
            if(s.ownerId==1 && (s.locationMask&39)!=0 && (s.tokenMask&8)==0 && !game.live[i].createdCopy)
                seen.PushBack(s.runtimeTemplate.templateId);
            if(s.positionPlayerId==1 && s.locationMask==8 && (s.tokenMask&64)!=0 && !templates.Contains(s.runtimeTemplate.templateId) && templates.Size()<limit){
                templates.PushBack(s.runtimeTemplate.templateId);weights.PushBack(100);
            }
        }
        BetaGwentAIProfileIds(profiles);
        for(i=0;i<profiles.Size();i+=1){
            id=BetaGwentAIProfileLeader(profiles[i]); d=BetaGwentDuelDefinition(id);
            if(d.header.factionMask!=faction)continue;
            eligibleProfiles+=1;weight=1;if(id==game.leaderTemplateOne)weight=3;
            BetaGwentAIProfileDeck(profiles[i],deck);
            for(j=0;j<seen.Size();j+=1){k=deck.FindFirst(seen[j]);if(k>=0)deck.Erase(k);}
            for(j=0;j<deck.Size();j+=1){
                k=pool.FindFirst(deck[j]);if(k<0){pool.PushBack(deck[j]);mass.PushBack(weight);}
                else mass[k]+=weight;
            }
        }
        // One common control reply plus the most frequent remaining cards.
        best=-1;
        for(i=0;i<pool.Size();i+=1){
            d=BetaGwentDuelDefinition(pool[i]);
            if(d.effect!=1 && d.effect!=6 && d.effect!=13 && d.effect!=17 && d.effect!=25 && d.effect!=27)continue;
            if(best<0 || mass[i]>mass[best])best=i;
        }
        if(best>=0 && templates.Size()<limit && !templates.Contains(pool[best])){templates.PushBack(pool[best]);weights.PushBack(mass[best]);mass[best]=0;}
        for(i=0;i<pool.Size();i+=1)if(templates.Contains(pool[i]))mass[i]=0;
        while(templates.Size()<limit){
            best=-1;for(i=0;i<pool.Size();i+=1)if(mass[i]>0 && (best<0 || mass[i]>mass[best]))best=i;
            if(best<0)break;templates.PushBack(pool[best]);weights.PushBack(mass[best]);mass[best]=0;
        }
    }
    // Return the most disruptive legal modeled reply, in the original seats.
    // All mutations occur in disposable clones; no real turn/request/RNG moves.
    public function Apply(root : CBetaGwentDuelSession) : CBetaGwentDuelSession
    {
        var h,best : CBetaGwentDuelSession; var c,slot : CBetaGwentDuelCard;
        var m : SBetaGwentMatchSnapshot; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i,j,id,gain,extra,worst,total,sum,w : int;
        evaluated=0;rejected=0;penalty=0;m=root.match.Snapshot();worst=-2147483647;
        if(m.playerOne.hasPassed || m.currentPlayerId!=1 || !m.turnActive)return NULL;
        for(i=0;i<=templates.Size();i+=1){
            if(i==templates.Size() && !root.LeaderAvailable(1))continue;
            if(i<templates.Size() && root.CountLocation(1,8)==0)continue;
            h=root.AiReverseClone();if(!h){rejected+=1;continue;}c=NULL;slot=NULL;
            if(i==templates.Size()) {c=h.Leader(2);w=1;}
            else {
                for(j=0;j<h.live.Size();j+=1){
                    s=h.live[j].Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8)continue;
                    if((s.tokenMask&64)!=0 && s.runtimeTemplate.templateId==templates[i]){c=h.live[j];break;}
                    if((s.tokenMask&64)==0 && !slot)slot=h.live[j];
                }
                if(!c && slot){
                    slot.Move(2,512,0);h.registry.Allocate(id);c=new CBetaGwentDuelCard in h;
                    c.Setup(h,id,templates[i],2,8,0);h.registry.Put(id,c);h.live.PushBack(c);
                }
                w=weights[i];
            }
            if(!c){rejected+=1;continue;}s=c.Snapshot();d=c.Definition();gain=h.AiSimPlay(s.instanceId);
            if(gain==-2147483647 || h.IsFatal() || h.IsPending()){rejected+=1;continue;}
            // Ordinary body tempo is common to all our choices. Penalize the
            // extra control/engine swing instead of treating it as scored points.
            extra=Max(0,gain-d.header.power);evaluated+=1;total+=w;sum+=extra*w;
            if(extra>worst){worst=extra;best=h;}
        }
        if(total>0)penalty=Min(12,(sum/total+Max(0,worst))/4);
        if(!best)return NULL;return best.AiReverseClone();
    }
}
