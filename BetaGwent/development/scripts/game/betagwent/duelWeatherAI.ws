// Eredin frost profile. Evaluation is deterministic and uses no match RNG.
// Hidden zones are queried only for side2; side1 contributes public board/graves.
class CBetaGwentWeatherAI extends IScriptable
{
    private var game : CBetaGwentDuelSession;
    public function Initialize(owner : CBetaGwentDuelSession) { game=owner; }
    private function ReadZone(side : int, zone : int, out cards : array<CBetaGwentDuelCard>)
    {
        var row,i : int;var part : array<CBetaGwentDuelCard>;
        if(zone!=7){game.GetZoneCards(side,zone,cards);return;}
        cards.Clear();for(row=1;row<=4;row*=2){game.GetZoneCards(side,row,part);for(i=0;i<part.Size();i+=1)cards.PushBack(part[i]);}
    }
    private function BoardCount(side : int) : int
    { return game.CountLocation(side,1)+game.CountLocation(side,2)+game.CountLocation(side,4); }
    public function Matches(ids : array<int>) : bool
    {
        var i,hounds,riders,ships : int;
        for(i=0;i<ids.Size();i+=1){if(ids[i]==132402)hounds+=1;if(ids[i]==132310)riders+=1;if(ids[i]==200301)ships+=1;}
        return hounds>=2 && riders>=2 && ships>=2;
    }
    private function CountTemplate(zone : int, id : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,total : int;
        ReadZone(2,zone,cards);
        for(i=0;i<cards.Size();i+=1)if(cards[i].TemplateId()==id)total+=1;
        return total;
    }
    private function HuntCount(zone : int, unlocked : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,total : int;var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        ReadZone(2,zone,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();d=cards[i].Definition();if((d.unitTraits&4096)!=0 && !s.isWaitingToDie && (!unlocked || (s.tokenMask&12)==0))total+=1;}
        return total;
    }
    private function Turns() : int
    {
        var m : SBetaGwentMatchSnapshot;m=game.Snapshot();
        if(m.playerOne.hasPassed)return 0;
        return Max(1,Min(5,Min(game.CountLocation(2,8)+1,game.CountLocation(1,8)+1)));
    }
    private function VisibleUnit(s : SBetaGwentCardSnapshot) : bool
    { return (s.locationMask&7)!=0 && !s.isWaitingToDie && s.power.currentPower>0 && (s.tokenMask&8)==0; }
    private function Threat(s : SBetaGwentCardSnapshot) : int
    {
        var d : SBetaGwentDuelDefinition;var value : int;d=BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
        if(Turns()==0)return 0;
        if((s.tokenMask&4)!=0)return 0;
        if(d.timerPeriod>0)value+=4;
        value+=d.consumePassiveBoost*3;
        if(d.passiveBoost>0)value+=d.passiveBoost*2;
        if(s.runtimeTemplate.templateId==200301)value+=Min(5,Turns());
        if(s.runtimeTemplate.templateId==132310 && game.WeatherToken(2,s.locationMask)==1)value+=Turns();
        return value;
    }
    private function Hit(s : SBetaGwentCardSnapshot, amount : int, optional immediate : bool) : int
    {
        var damage : int;damage=Min(s.power.currentPower,Max(0,amount-s.power.armor));
        if(damage>=s.power.currentPower){if(!immediate)damage+=Threat(s);
            if(s.positionPlayerId==1 && s.runtimeTemplate.templateId==112215 && (s.tokenMask&4)==0)damage+=Min(5,BoardCount(2))*5;}
        return damage;
    }
    private function BestHit(amount : int, frostAmount : int, optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,value,best,hit : int;var s : SBetaGwentCardSnapshot;
        ReadZone(1,7,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!VisibleUnit(s) || (s.tokenMask&264)!=0)continue;hit=amount;if(game.WeatherToken(1,s.locationMask)==1)hit=frostAmount;value=Hit(s,hit,immediate);best=Max(best,value);}
        return best;
    }
    private function MorvuddValue(optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,best,value : int;var s : SBetaGwentCardSnapshot;
        ReadZone(1,7,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!VisibleUnit(s) || (s.tokenMask&256)!=0)continue;value=s.power.currentPower/2;if(!immediate){if((s.tokenMask&4)==0)value+=Threat(s);else value-=3;}best=Max(best,value);}
        return best;
    }
    public function KillBonus(s : SBetaGwentCardSnapshot, amount : int) : int
    {
        var value : int;
        if(s.positionPlayerId!=1 || Max(0,amount-s.power.armor)<s.power.currentPower)return 0;
        value=0;if(Turns()>0)value=Threat(s);
        if(s.runtimeTemplate.templateId==112215 && (s.tokenMask&4)==0)value+=Min(5,BoardCount(2))*5;
        return value;
    }
    private function FrostValue(row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,lowest : int;var s : SBetaGwentCardSnapshot;
        if(game.WeatherToken(1,row)==1 || Turns()==0)return 0;
        ReadZone(1,row,cards);lowest=2147483647;
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(VisibleUnit(s))lowest=Min(lowest,s.power.currentPower);}
        if(lowest==2147483647)return 0;
        return Min(lowest+Max(0,cards.Size()-1)*3,2*Turns());
    }
    public function IrisValue(row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,eligible,ties,damage,payout : int;var s : SBetaGwentCardSnapshot;
        if(game.WeatherToken(1,row)!=1 || Turns()==0 || game.CountLocation(1,row)>=9)return 0;
        ReadZone(1,row,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!VisibleUnit(s))continue;if(s.power.currentPower<3)return 0;if(s.power.currentPower==3)ties+=1;}
        ReadZone(2,7,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(VisibleUnit(s))eligible+=1;}
        damage=game.WeatherDamage(1,row);if(damage*Turns()<3)return 0;
        payout=Min(5,eligible)*5+3;
        // Ties, a second weather tick and public weather answers reduce certainty.
        if(damage<3)payout=payout*2/3;
        return payout*3/(3+ties);
    }
    public function BurnValue(row : int, optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;var i,total,strongest,value : int;
        ReadZone(1,row,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(VisibleUnit(s)){total+=s.power.currentPower;strongest=Max(strongest,s.power.currentPower);}}
        if(total<25)return 0;
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(VisibleUnit(s) && s.power.currentPower==strongest){value+=s.power.currentPower;if(!immediate)value+=Threat(s);}}
        return value;
    }
    private function MoveValue(s : SBetaGwentCardSnapshot, row : int, amount : int, appliesFrost : bool, optional immediate : bool) : int
    {
        var value : int;
        if(!VisibleUnit(s) || (s.tokenMask&264)!=0 || s.locationMask==row || game.CountLocation(1,row)>=9)return 0;
        value=Hit(s,amount,immediate);if(immediate)return value;
        if(game.WeatherToken(1,row)==1 || appliesFrost){if(game.WeatherToken(1,s.locationMask)!=1)value+=Min(5,Turns()*2);}
        else if(game.WeatherToken(1,s.locationMask)==1)value-=Min(5,Turns()*2);
        return value;
    }
    private function MoverValue(id : int, row : int, optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        var i,j,value,amount,limit,total : int;var gains : array<int>;
        ReadZone(1,7,cards);limit=1;
        if(id==200218){limit=Min(3,9-game.CountLocation(1,row));amount=2;if(game.WeatherToken(1,row)==1)amount=3;}
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();value=MoveValue(s,row,amount,id==132104,immediate);if(value<=0)continue;j=0;while(j<gains.Size() && gains[j]>=value)j+=1;gains.Insert(j,value);}
        for(i=0;i<gains.Size() && i<limit;i+=1)total+=gains[i];
        if(!immediate && id==132104)total+=FrostValue(row);
        return total;
    }
    public function BestRow(d : SBetaGwentDuelDefinition) : int
    {
        var row,best,value,maximum,side : int;maximum=-2147483647;side=2;
        if(BetaGwentDuelSpying(d.header.templateId))side=1;
        for(row=1;row<=4;row*=2){
            if(game.CountLocation(side,row)>=9)continue;
            value=-game.WeatherDamage(side,row)*2-game.CountLocation(side,row);
            if(d.header.templateId==132310 && game.WeatherToken(1,row)==1)value+=Turns()*4;
            if(d.header.templateId==132104 || d.header.templateId==200218)value+=MoverValue(d.header.templateId,row)*3;
            if(d.header.templateId==132204){value=0;if(game.WeatherToken(1,row)==1)value+=Turns()*3;}
            if(d.header.templateId==112215)value=IrisValue(row)*3;
            if(value>maximum){maximum=value;best=row;}
        }
        return best;
    }
    private function GraveValue(optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;var i,side,best,value : int;
        for(side=1;side<=2;side+=1){ReadZone(side,32,cards);for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if((s.runtimeTierMask&6)==0 || s.runtimeTemplate.typeMask!=4 || (s.tokenMask&264)!=0)continue;value=s.power.currentPower;if(!immediate && side==1)value+=Min(4,Threat(s)+2);best=Max(best,value);}}
        return best;
    }
    public function Gain(d : SBetaGwentDuelDefinition, power : int, optional shallow : bool, optional fromHand : bool, optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;var option : SBetaGwentDuelDefinition;
        var i,row,value,best,body,gold,silver,golds,silvers : int;var ids : array<int>;
        body=power;if(BetaGwentDuelSpying(d.header.templateId))body=-power;
        if(d.header.templateId==132205)return body+MorvuddValue(immediate);
        if(d.header.templateId==132214){value=HuntCount(8,false);if(fromHand)value=Max(0,value-1);return body+BestHit(d.amount+value*d.conditionalDamage,d.amount+value*d.conditionalDamage,immediate);}
        if(d.header.templateId==132102)return body+BestHit(4,8,immediate);
        if(d.header.templateId==132309){value=BestHit(3,3,immediate);if(game.HasWeather(1))value+=2;return body+value;}
        if(d.header.templateId==132402 || d.header.templateId==113302){if(immediate || (d.header.templateId==132402 && CountTemplate(16,113302)==0))return body;for(row=1;row<=4;row*=2)best=Max(best,FrostValue(row));return body+best;}
        if(d.header.templateId==132310){row=BestRow(d);if(!immediate && game.WeatherToken(1,row)==1)body+=Turns();return body;}
        if(d.header.templateId==200301)return body+HuntCount(7,false)*d.amount;
        if(d.header.templateId==132104 || d.header.templateId==200218)return body+MoverValue(d.header.templateId,BestRow(d),immediate);
        if(d.header.templateId==112215){if(immediate)return body;return body+IrisValue(BestRow(d));}
        if(d.header.templateId==112102){for(row=1;row<=4;row*=2)best=Max(best,BurnValue(row,immediate));return body+best;}
        if(d.header.templateId==201698)return body+GraveValue(immediate);
        if(d.header.templateId==132204){if(immediate || game.CountLocation(2,16)==0 || Turns()==0)return body;return body+16;}
        if(d.header.templateId==200026){ReadZone(2,7,cards);for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();option=cards[i].Definition();if((option.unitTraits&4096)==0 || s.runtimeTierMask!=2 || (s.tokenMask&264)!=0 || option.header.templateId==200026 || CountTemplate(16,option.header.templateId)==0)continue;value=Gain(option,option.header.power,true,false,immediate);best=Max(best,value);}return body+best;}
        if(d.header.templateId==131101){BetaGwentMonsterTemplates(131101,ids);for(i=0;i<ids.Size();i+=1){option=BetaGwentDuelDefinition(ids[i]);best=Max(best,Gain(option,option.header.power,true,false,immediate));}return body+best;}
        if(d.header.templateId==131102 && !shallow){if(immediate){gold=2147483647;silver=2147483647;}ReadZone(2,16,cards);for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();option=cards[i].Definition();value=Gain(option,s.power.currentPower,true,false,immediate);if(s.runtimeTierMask==8){if(immediate)gold=Min(gold,value);else gold+=value;golds+=1;}if(s.runtimeTierMask==4){if(immediate)silver=Min(silver,value);else silver+=value;silvers+=1;}}if(golds>0){best=gold;if(!immediate)best=gold/golds;}if(silvers>0){value=silver;if(!immediate)value=silver/silvers;best=Max(best,value);}return body+best;}
        return body;
    }
    public function Setup(d : SBetaGwentDuelDefinition) : int
    {
        var value : int;
        if(Turns()==0)return 0;
        if(d.header.templateId==200301)value+=Min(Turns(),HuntCount(8,false)+HuntCount(16,false))*d.amount;
        if(d.header.templateId==132310 && game.WeatherToken(1,BestRow(d))!=1 && (CountTemplate(8,132402)>0 || CountTemplate(8,113302)>0))value+=2;
        if(d.header.templateId==132402 && CountTemplate(16,113302)>0 && BoardCount(1)>0)value+=2;
        if(d.header.templateId==132204 && game.CountLocation(2,16)>0){value+=8;if(game.Score(2)-game.Score(1)<13)value+=3;}
        if(d.header.templateId==131102 && game.CountLocation(2,16)>0)value+=2;
        if((d.header.templateId==200218 || d.header.templateId==132104) && Turns()>=3)value-=3;
        return value;
    }
    public function ChoiceValue(source : CBetaGwentDuelCard, id : int, kind : int) : int
    {
        var d,option : SBetaGwentDuelDefinition;var s,t : SBetaGwentCardSnapshot;var target : CBetaGwentDuelCard;
        var value,amount : int;d=source.Definition();s=source.Snapshot();
        if(kind==1){option=BetaGwentDuelViewDefinition(id);return Gain(option,option.header.power,true)+Setup(option);}
        if(kind==3 && d.header.templateId==112102)return BurnValue(id);
        if(kind==3)return game.CountLocation(1,id);
        target=game.FindCard(id);if(!target)return -2147483647;t=target.Snapshot();
        if(t.positionPlayerId==1 && (t.locationMask==16 || (t.locationMask==8 && (t.tokenMask&64)==0)))return 0;
        if(d.header.templateId==200026){option=target.Definition();return Gain(option,option.header.power,true)+Setup(option);}
        if(d.header.templateId==131102){option=target.Definition();return Gain(option,t.power.currentPower,true)+Setup(option);}
        if(d.header.templateId==132214)return Hit(t,d.amount+HuntCount(8,false)*d.conditionalDamage);
        if(d.header.templateId==132104 || d.header.templateId==200218 || d.header.templateId==132204){amount=0;if(d.header.templateId==200218){amount=2;if(game.WeatherToken(1,s.locationMask)==1)amount=3;}return MoveValue(t,s.locationMask,amount,d.header.templateId==132104);}
        if(d.header.templateId==201698){value=t.power.currentPower;if(t.positionPlayerId==1)value+=Min(4,Threat(t)+2);return value;}
        value=t.power.currentPower;if(t.runtimeTemplate.typeMask==2)value+=5;return value;
    }
}
