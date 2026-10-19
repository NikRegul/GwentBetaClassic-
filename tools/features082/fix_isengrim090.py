"""Use legal child plays and real branch values for Isengrim: Outlaw."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release090-integrated'

def change(s,old,new):
    assert s.count(old)==1,old[:120]
    return s.replace(old,new)

helper='''    // Choice-only template IDs have no body/ability definition. Estimate the
    // actual branch, without drawing RNG or looking at the opponent's hand.
    public function AiOutlawBranchValue(branch : int, side : int, immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var ids,values : array<int>;
        var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var i,j,k,best,total,count : int;
        if(branch==201715){
            best=-1000000;LocationCards(side,16,cards);
            for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();d=cards[i].Definition();
                if(s.isWaitingToDie || IsPlayAncestor(cards[i]) || (s.runtimeTierMask&6)==0 || s.runtimeTemplate.typeMask!=2 || !HasRequiredPlayTargetForSide(d,side))continue;
                best=Max(best,AiPileCandidateValue(cards[i],side,immediate,1));
            }
            return best;
        }
        if(branch!=201716)return -1000000;
        BetaGwentScoiaPool(201615,ids);
        for(i=0;i<ids.Size();i+=1){d=BetaGwentDuelViewDefinition(ids[i]);values.PushBack(AiCreatedOptionValue(d,side,immediate));}
        // Create offers three distinct random candidates. Average the best
        // result over the 56 possible triples; never assume the best of all 8.
        for(i=0;i<values.Size();i+=1)for(j=i+1;j<values.Size();j+=1)for(k=j+1;k<values.Size();k+=1)
        {total+=Max(values[i],Max(values[j],values[k]));count+=1;}
        if(count>0)return total/count;
        if(values.Size()==0)return -1000000;
        best=values[0];for(i=1;i<values.Size();i+=1)best=Max(best,values[i]);return best;
    }
'''

def main():
    p=BUILD/'scripts/game/betagwent/duelSession.ws';s=p.read_text('utf-8-sig')
    old='''        d=card.Definition();source=card.Snapshot();
        for(i=0;i<live.Size();i+=1){target=live[i].Snapshot();
            if(target.positionPlayerId==source.positionPlayerId && MatchesCardTarget(target,d))return true;}
        return false;
    }
    // UI hint only;'''
    new='''        d=card.Definition();source=card.Snapshot();
        return HasRequiredPlayTargetForSide(d,source.positionPlayerId);
    }
    public function HasRequiredPlayTargetForSide(d : SBetaGwentDuelDefinition, side : int) : bool
    {
        var target : SBetaGwentCardSnapshot;var i : int;
        if(d.header.templateId!=113201)return true;
        for(i=0;i<live.Size();i+=1){target=live[i].Snapshot();
            if(target.positionPlayerId==side && MatchesCardTarget(target,d))return true;}
        return false;
    }
    // UI hint only;'''
    s=change(s,old,new)
    s=change(s,'score = -2147483647; best = ids[0]; bestSide=rowSide;', 'score = -2147483647; best = 0; bestSide=rowSide;')
    old='''                card = registry.Find(ids[i]); if (!card) continue; t = card.Snapshot(); value = AiAbilityChoiceValue(source,card,kind);'''
    new='''                card = registry.Find(ids[i]); if (!card) continue; t = card.Snapshot();
                if(kind==2 && BetaGwentDuelPlayChoice(source.TemplateId()) && !HasRequiredPlayTargetForSide(card.Definition(),NilfDecisionSide()))
                {AiExplain("TARGET_REJECT","source="+source.TemplateId()+" target="+ids[i]+" reason=no_legal_child_play_target");continue;}
                value = AiAbilityChoiceValue(source,card,kind);'''
    s=change(s,old,new)
    old='''            if(weatherProfile && kind!=1)value=weatherAI.ChoiceValue(source,ids[i],kind);'''
    new=old+'''
            if(source.TemplateId()==201615 && source.monsterStage==0 && kind==1)value=AiOutlawBranchValue(ids[i],NilfDecisionSide(),AiHorizon(NilfDecisionSide())==0);
            if(source.TemplateId()==201615 && source.monsterStored==201715 && kind==2 && card)value=AiPileCandidateValue(card,NilfDecisionSide(),AiHorizon(NilfDecisionSide())==0,1);'''
    s=change(s,old,new)
    s=change(s,'if (OptionalChoiceLimit(source) > 0 && score <= 0)', 'if(best==0){AiExplain("TARGET_FINISH","source="+source.TemplateId()+" reason=no_legal_child_play");monsters.Select(source,0);return;}\n        if (OptionalChoiceLimit(source) > 0 && score <= 0)')
    s=change(s,'        if(id==162205){AiFringillaSlot(side,value,count,amount);return amount;}', '        if(id==201615)return Max(AiOutlawBranchValue(201715,side,immediate),AiOutlawBranchValue(201716,side,immediate));\n        if(id==162205){AiFringillaSlot(side,value,count,amount);return amount;}')
    s=change(s,'    public function AiCreatedOptionValue(d : SBetaGwentDuelDefinition, side : int, optional immediate : bool) : int', helper+'    public function AiCreatedOptionValue(d : SBetaGwentDuelDefinition, side : int, optional immediate : bool) : int')
    s=change(s,'if(!card)return 0;s=card.Snapshot();d=card.Definition();value=s.power.currentPower;', 'if(!card)return 0;s=card.Snapshot();d=card.Definition();\n        if(!HasRequiredPlayTargetForSide(d,side))return -1000000;\n        value=s.power.currentPower;')
    s=change(s,'if(s.isWaitingToDie || IsPlayAncestor(cards[i]) || (s.runtimeTemplate.typeMask&d.targetTypes)==0', 'if(s.isWaitingToDie || IsPlayAncestor(cards[i]) || !HasRequiredPlayTargetForSide(td,side) || (s.runtimeTemplate.typeMask&d.targetTypes)==0')
    p.write_bytes(b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
    (ROOT/'BetaGwent/development/scripts/game/betagwent/duelSession.ws').write_bytes(p.read_bytes())
    print('Isengrim branches evaluate real special plays and expected Create offers; illegal Decoy excluded from AI child choices.')

if __name__=='__main__':main()
