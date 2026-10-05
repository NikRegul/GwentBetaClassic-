// Explicit consumers for every remaining neutral graph; generated choices are views only.
class CBetaGwentDuelNeutral extends IScriptable
{
    private var game : CBetaGwentDuelSession;
    public function Initialize(owner : CBetaGwentDuelSession){game=owner;}
    private function Side(source : CBetaGwentDuelCard) : int{return game.NorthActingSide(source);}
    private function Query(side : int, zone : int, tier : int, types : int, ignore : int, out ids : array<int>)
    {var cards : array<SBetaGwentDevelopmentCard>;var s : SBetaGwentCardSnapshot;var i : int;ids.Clear();game.GetCards(cards);for(i=0;i<cards.Size();i+=1){s=cards[i].card;if((side==0 || s.positionPlayerId==side) && (s.locationMask&zone)!=0 && (s.runtimeTierMask&tier)!=0 && (s.runtimeTemplate.typeMask&types)!=0 && (s.tokenMask&ignore)==0 && !s.isWaitingToDie)ids.PushBack(s.instanceId);}}
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, minimum : int)
    {var ids : array<int>;var i : int;Query(side,zone,tier,types,BetaGwentNorthPick((zone&7)!=0,264,0),ids);for(i=ids.Size()-1;i>=0;i-=1)if(source.monsterIds.Contains(ids[i]))ids.Erase(i);game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),minimum,1);}
    private function Extremes(source : CBetaGwentDuelCard, side : int, row : int, strongest : bool, operation : int, amount : int, excluded : int)
    {var ids : array<int>;var s : SBetaGwentCardSnapshot;var i,best : int;Query(side,row,15,4,8,ids);best=BetaGwentNorthPick(strongest,-1,2147483647);for(i=0;i<ids.Size();i+=1){s=game.FindCard(ids[i]).Snapshot();if(s.instanceId==excluded)continue;if(strongest)best=Max(best,s.power.currentPower);else best=Min(best,s.power.currentPower);}for(i=0;i<ids.Size();i+=1){s=game.FindCard(ids[i]).Snapshot();if(s.instanceId!=excluded && s.power.currentPower==best)game.MonsterOperation(source,game.FindCard(ids[i]),operation,amount,7);}}
    private function ExtremeOne(source : CBetaGwentDuelCard, side : int, strongest : bool, amount : int)
    {var ids,valid : array<int>;var t : SBetaGwentCardSnapshot;var i,best : int;Query(side,7,15,4,8,ids);best=BetaGwentNorthPick(strongest,-1,2147483647);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(strongest)best=Max(best,t.power.currentPower);else best=Min(best,t.power.currentPower);}for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower==best)valid.PushBack(ids[i]);}if(valid.Size()>0)game.MonsterPower(source,game.FindCard(valid[game.RandomIndex(valid.Size())]),amount);}
    private function RandomHit(source : CBetaGwentDuelCard, side : int, amount : int)
    {var ids : array<int>;Query(side,7,15,4,8,ids);if(ids.Size()>0)game.MonsterPower(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),-amount);}
    private function Choices(source : CBetaGwentDuelCard, randomThree : bool)
    {var ids : array<int>;BetaGwentNeutralPool(source.TemplateId(),ids);if(randomThree){game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);}game.MonsterRequest(source,ids,1,1,1);}
    private function AdventureChoices(source : CBetaGwentDuelCard)
    {var ids : array<int>;var i,first : int;first=source.TemplateId()+1;for(i=first;i<first+5;i+=1)ids.PushBack(i);game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,1,1,1);}
    private function Initial(source : CBetaGwentDuelCard, side : int, tier : int, types : int, out ids : array<int>)
    {var all : array<int>;var d : SBetaGwentDuelDefinition;var i : int;ids.Clear();game.NeutralInitial(side,all);for(i=0;i<all.Size();i+=1){d=BetaGwentDuelDefinition(all[i]);if((d.header.tierMask&tier)!=0 && (d.header.typeMask&types)!=0 && !ids.Contains(all[i]))ids.PushBack(all[i]);}}
    private function TrissChoices(source : CBetaGwentDuelCard)
    {var ids,other : array<int>;var i : int;Initial(source,1,2,2,ids);Initial(source,2,2,2,other);for(i=0;i<other.Size();i+=1)if(!ids.Contains(other[i]))ids.PushBack(other[i]);game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,1,1,1);}
    public function Played(source : CBetaGwentDuelCard)
    {
        var id,side,enemy,i,j,count,power : int;var ids,valid,other : array<int>;var s,t,pos : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var target : CBetaGwentDuelCard;
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();source.monsterStage=0;source.monsterIds.Clear();source.monsterRemaining=1;
        LogChannel('BetaGwent',"DUEL_NEUTRAL_PLAY template="+id+" side="+side);
        if(id==112101 || id==112107)source.monsterStage=0;
        else if(id==112102 || id==201523){ids.PushBack(1);ids.PushBack(2);ids.PushBack(4);game.MonsterRequest(source,ids,3,1,1);return;}
        else if(id==200532)game.MonsterWeather(side,s.locationMask,128);
        else if(id==112104){Request(source,0,7,15,4,0);return;}
        else if(id==200226){if(s.timerValue==0){ExtremeOne(source,enemy,true,-6);ExtremeOne(source,side,false,6);}}
        else if(id==112105){Query(enemy,16,2,4,0,ids);game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,2,0,1);return;}
        else if(id==112108 || id==112109 || id==113208){Choices(source,false);return;}
        else if(id==112111 || id==112205){source.monsterRemaining=BetaGwentNorthPick(id==112111,3,2);Request(source,enemy,7,15,4,BetaGwentNorthPick(id==112205,1,0));return;}
        else if(id==112112){Initial(source,enemy,12,4,ids);if(ids.Size()>0){source.monsterStored=ids[game.RandomIndex(ids.Size())];game.MonsterCreate(source,source.monsterStored);return;}}
        else if(id==112201 || id==200235 || id==201772){Request(source,enemy,7,15,4,BetaGwentNorthPick(id==112201,0,1));return;}
        else if(id==112202 || id==112203 || id==112204){for(i=112202;i<=112204;i+=1)if(i!=id)game.NorthSummonCopies(source,i);}
        else if(id==112208){if(s.timerValue>0 && game.NilfTruce()){Request(source,side,8,2,4,0);return;}}
        else if(id==112211 || id==112212){Request(source,side,8,14,14,0);return;}
        else if(id==112213){power=Min(Max(0,game.Score(enemy)-game.Score(side)),Max(0,15-s.power.basePower));game.MonsterOperation(source,source,12,power,7);}
        else if(id==132105){if(game.NilfTruce()){game.NilfDraw(side,14,false);game.NilfDraw(side,14,false);game.NilfDraw(enemy,14,false);game.NilfDraw(enemy,14,false);}}
        else if(id==132215){ids.PushBack(200176);ids.PushBack(201770);ids.PushBack(200175);game.MonsterRequest(source,ids,1,1,1);return;}
        else if(id==200056 || id==200058 || id==200087){Choices(source,true);return;}
        else if(id==200062){source.monsterRemaining=2;AguaraChoices(source);return;}
        else if(id==200079){Query(enemy,32,8,4,0,ids);source.monsterIds=ids;game.MonsterRequest(source,ids,2,0,1);return;}
        else if(id==200083){Request(source,side,16,14,14,1);return;}
        else if(id==200091){if(game.NilfTruce()){for(i=1;i<=2;i+=1){Query(i,16,14,4,0,ids);if(ids.Size()>0){target=game.FindCard(ids[0]);game.NilfTake(target,i);game.MonsterOperation(source,target,11,1,8);}}}}
        else if(id==200236){Query(enemy,7,6,4,264,ids);for(i=ids.Size()-1;i>=0;i-=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower>t.power.basePower+t.power.permanentPower)ids.Erase(i);}game.MonsterRequest(source,ids,0,0,1);return;}
        else if(id==200237){Query(side,16,6,14,0,ids);for(i=ids.Size()-1;i>=0;i-=1)if(!BetaGwentNorthernCategory(game.FindCard(ids[i]).TemplateId(),11))ids.Erase(i);game.MonsterRequest(source,ids,2,1,1);return;}
        else if(id==200523){pos=s;pos.locationIndex=s.locationIndex;game.QueueSpawn(pos,201576,2);pos.locationIndex=s.locationIndex+3;game.QueueSpawn(pos,201576,2);}
        else if(id==201579){Query(side,32,6,4,0,ids);for(i=ids.Size()-1;i>=0;i-=1)if(!BetaGwentNeutralDraconid(game.FindCard(ids[i]).TemplateId()))ids.Erase(i);game.MonsterRequest(source,ids,2,1,1);return;}
        else if(id==201613){Query(side,8,14,14,0,ids);for(i=0;i<ids.Size();i+=1)game.NilfBanish(game.FindCard(ids[i]));for(i=0;i<ids.Size();i+=1)game.NilfDraw(side,14,false);}
        else if(id==201626){game.NeutralInitial(side,ids);count=1;for(i=0;i<ids.Size();i+=1){d=BetaGwentDuelDefinition(ids[i]);if(d.header.tierMask!=2)continue;power=0;for(j=0;j<ids.Size();j+=1)if(ids[i]==ids[j])power+=1;if(power!=2){count=0;break;}}if(count==1)game.MonsterOperation(source,source,19,22,7);}
        else if(id==201627){game.NeutralInitial(side,ids);for(i=0;i<ids.Size();i+=1)for(j=i+1;j<ids.Size();j+=1)if(ids[i]==ids[j]){game.MonsterComplete(source);return;}Choices(source,false);return;}
        else if(id==201631){BetaGwentNeutralPool(id,ids);power=game.NeutralFaction(side);for(i=ids.Size()-1;i>=0;i-=1){d=BetaGwentDuelDefinition(ids[i]);if(d.header.factionMask!=power)ids.Erase(i);}if(ids.Size()>0){source.monsterStored=ids[game.RandomIndex(ids.Size())];game.MonsterCreate(source,source.monsterStored);return;}}
        else if(id==201773){TrissChoices(source);return;}
        else if(id==201774){game.NeutralInitial(side,ids);for(i=0;i<ids.Size();i+=1)if(BetaGwentNeutralDandelionFamily(ids[i]))count+=1;game.MonsterPower(source,source,count*3);}
        else if(id==201776){game.NilfDraw(side,14,false);Request(source,side,8,14,14,1);return;}
        else if(id==201817)game.MonsterPower(source,source,-5);
        else if(id==112401 || id==112402){Query(0,7,15,4,8,ids);for(i=0;i<ids.Size();i+=1)if(ids[i]!=s.instanceId)game.MonsterPower(source,game.FindCard(ids[i]),BetaGwentNorthPick(id==112401,2,-2));}
        else if(id==112403 || id==112404){Query(side,s.locationMask,15,4,8,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.instanceId!=s.instanceId && Abs(t.locationIndex-s.locationIndex)<=2)game.MonsterPower(source,game.FindCard(ids[i]),BetaGwentNorthPick(id==112403,2,-2));}}
        else if(id==201725 || id==201731 || id==201737){if(source.neutralChoice>0){Adventure(source,source.neutralChoice);return;}AdventureChoices(source);return;}
        else if(id!=112110 && id!=112113 && id!=112206 && id!=112209 && id!=112210 && id!=122107 && id!=200226){game.FailAbility("Нейтральная карта не подключена.");return;}
        game.MonsterComplete(source);
    }
    private function AguaraChoices(source : CBetaGwentDuelCard)
    {var ids : array<int>;var i : int;for(i=201668;i<=201671;i+=1)if(!source.monsterIds.Contains(i))ids.PushBack(i);game.MonsterRequest(source,ids,1,1,1);}
    private function Aguara(source : CBetaGwentDuelCard, choice : int)
    {var ids : array<int>;var s,t : SBetaGwentCardSnapshot;var side,enemy,i,best : int;s=source.Snapshot();side=Side(source);enemy=BetaGwentOpponentId(side);
     if(choice==201668 || choice==201669){Query(BetaGwentNorthPick(choice==201668,side,enemy),7,15,4,8,ids);best=BetaGwentNorthPick(choice==201668,2147483647,-1);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(choice==201668)best=Min(best,t.power.currentPower);else best=Max(best,t.power.currentPower);}for(i=ids.Size()-1;i>=0;i-=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower!=best)ids.Erase(i);}if(ids.Size()>0)game.MonsterPower(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),BetaGwentNorthPick(choice==201668,5,-5));}
     if(choice==201670){Query(side,8,15,4,0,ids);if(ids.Size()>0)game.MonsterOperation(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),1,5,8);}
     if(choice==201671){Query(enemy,7,15,4,8,ids);for(i=ids.Size()-1;i>=0;i-=1){t=game.FindCard(ids[i]).Snapshot();if(!BetaGwentNilfElf(t.runtimeTemplate.templateId) || t.power.currentPower>5)ids.Erase(i);}if(ids.Size()>0){t=game.FindCard(ids[game.RandomIndex(ids.Size())]).Snapshot();game.QueueRelocation(game.FindCard(t.instanceId),side,t.locationMask,false);}}
     game.FlushDeaths();source.monsterIds.PushBack(choice);source.monsterRemaining-=1;if(source.monsterRemaining>0)AguaraChoices(source);else game.MonsterComplete(source);
    }
    public function Select(source : CBetaGwentDuelCard, selected : int)
    {
        var id,side,enemy,i,power,tier : int;var target : CBetaGwentDuelCard;var s,t : SBetaGwentCardSnapshot;var ids,other : array<int>;var d : SBetaGwentDuelDefinition;
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();target=game.FindCard(selected);
        if(id==112108 || id==112109 || id==113208 || id==200056 || id==200058 || id==200087 || id==201627 || id==201773){if(selected>0){source.monsterStored=selected;game.MonsterCreate(source,selected);}else game.MonsterComplete(source);return;}
        if(id==201725 || id==201731 || id==201737){if(source.monsterStage==0){source.neutralChoice=selected;Adventure(source,selected);return;}AdventureTarget(source,target);return;}
        if(id==132215){if(source.monsterStage==0){source.monsterStored=selected;source.monsterStage=1;BetaGwentNeutralPool(id,ids);if(ids.Size()>0){source.neutralChoice=ids[game.RandomIndex(ids.Size())];ids.Clear();ids.PushBack(source.neutralChoice);game.MonsterRequest(source,ids,1,0,1);return;}}else{d=BetaGwentDuelDefinition(source.neutralChoice);if((source.monsterStored==200176 && d.header.power<6) || (source.monsterStored==201770 && d.header.power==6) || (source.monsterStored==200175 && d.header.power>6)){game.MonsterCreate(source,source.neutralChoice);return;}}game.MonsterComplete(source);return;}
        if(id==200062){Aguara(source,selected);return;}
        if(!target){game.MonsterComplete(source);return;}t=target.Snapshot();
        if(id==112104){power=Max(0,t.power.currentPower-t.power.basePower);game.NeutralDrain(source,target,power);game.MonsterPower(source,source,power);}
        else if(id==112105){game.NilfBanish(target);game.MonsterPower(source,source,t.power.basePower);}
        else if(id==112111 || id==112205){game.MonsterPower(source,target,-BetaGwentNorthPick(id==112111,3,2));if(id==112111){source.monsterIds.PushBack(selected);if(t.locationMask==4 || t.locationMask==2)game.QueueRelocation(target,enemy,t.locationMask/2,false);}source.monsterRemaining-=1;game.FlushDeaths();if(source.monsterRemaining>0){Request(source,enemy,7,15,4,BetaGwentNorthPick(id==112205,1,0));return;}}
        else if(id==112201)game.MonsterOperation(source,source,11,t.power.currentPower,7);
        else if(id==112208){game.NeutralCopy(side,t.runtimeTemplate.templateId,8);game.NeutralCopy(enemy,t.runtimeTemplate.templateId,8);game.QueueTimer(source,0,1);}
        else if(id==112211){Initial(source,enemy,t.runtimeTierMask,14,ids);if(ids.Size()>0){game.NilfDiscard(target);game.NeutralCopy(side,ids[game.RandomIndex(ids.Size())],8);}}
        else if(id==112212){Query(side,16,t.runtimeTierMask,14,0,ids);for(i=ids.Size()-1;i>=0;i-=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId)ids.Erase(i);if(ids.Size()>0){game.NorthExchange(target,game.FindCard(ids[game.RandomIndex(ids.Size())]));}}
        else if(id==200079){source.monsterStored=t.runtimeTemplate.templateId;game.MonsterCreate(source,t.runtimeTemplate.templateId);return;}
        else if(id==200083){game.NilfTake(target,side);Query(side,8,14,14,0,ids);if(ids.Size()>0)game.NilfDiscard(game.FindCard(ids[game.RandomIndex(ids.Size())]));}
        else if(id==200235){Query(enemy,7,15,4,8,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId)game.MonsterPower(source,game.FindCard(ids[i]),-4);}
        else if(id==200236)game.QueueDestroy(target);
        else if(id==200237 || id==201579 || id==201776){game.MonsterPlayExisting(source,target);return;}
        game.MonsterComplete(source);
    }
    private function Adventure(source : CBetaGwentDuelCard, choice : int)
    {
        var side,enemy,i,row : int;var ids : array<int>;var s,t : SBetaGwentCardSnapshot;var hazards : array<int>;
        side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();source.monsterStage=1;
        if(choice==201726)game.NilfDraw(side,14,false);
        else if(choice==201727){Query(enemy,7,15,4,8,ids);if(ids.Size()>0){t=game.FindCard(ids[game.RandomIndex(ids.Size())]).Snapshot();game.QueueRelocation(game.FindCard(t.instanceId),side,t.locationMask,false);}}
        else if(choice==201728){hazards.PushBack(1);hazards.PushBack(2);hazards.PushBack(4);hazards.PushBack(16);hazards.PushBack(32);hazards.PushBack(64);hazards.PushBack(512);hazards.PushBack(1024);hazards.PushBack(2048);for(row=1;row<=4;row*=2)game.MonsterWeather(enemy,row,hazards[game.RandomIndex(hazards.Size())]);}
        else if(choice==201729 || choice==201732 || choice==201740){Request(source,enemy,7,15,4,1);return;}
        else if(choice==201730 || choice==201736){Request(source,side,16,6,BetaGwentNorthPick(choice==201730,2,4),1);return;}
        else if(choice==201733){for(i=0;i<8;i+=1){RandomHit(source,enemy,2);game.FlushDeaths();}}
        else if(choice==201734){Request(source,side,7,6,4,1);return;}
        else if(choice==201735){for(row=1;row<=4;row*=2)game.NorthClearHazard(side,row);Query(side,7,15,4,8,ids);for(i=0;i<ids.Size();i+=1)game.MonsterPower(source,game.FindCard(ids[i]),1);}
        else if(choice==201738)game.MonsterOperation(source,source,12,13,7);
        else if(choice==201739){if((s.tokenMask&1)==0)game.QueueResilienceToggle(source,source);}
        else if(choice==201741){Request(source,0,7,15,4,1);return;}
        else if(choice==201742){Query(enemy,7,15,4,8,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower<=3)game.QueueDestroy(game.FindCard(ids[i]));}}
        game.MonsterComplete(source);
    }
    private function AdventureTarget(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var t,s : SBetaGwentCardSnapshot;var ids : array<int>;var i,choice : int;
        if(!target){game.MonsterComplete(source);return;}choice=source.neutralChoice;t=target.Snapshot();s=source.Snapshot();
        if(choice==201730 || choice==201736){game.MonsterPlayExisting(source,target);return;}
        if(choice==201729){game.MonsterPower(source,target,-10);Query(t.positionPlayerId,t.locationMask,15,4,8,ids);for(i=0;i<ids.Size();i+=1){s=game.FindCard(ids[i]).Snapshot();if(Abs(s.locationIndex-t.locationIndex)==1)game.MonsterPower(source,game.FindCard(ids[i]),-5);}}
        else if(choice==201732)game.MonsterPower(source,target,-15);
        else if(choice==201734){game.QueueRelocation(target,t.positionPlayerId,8,true);game.FlushEffects();game.MonsterOperation(source,target,1,5,8);game.FlushEffects();game.MonsterPlayExisting(source,target);return;}
        else if(choice==201740)game.MonsterDuel(source,target,0,0);
        else if(choice==201741)game.QueueResetPower(source,target);
        game.MonsterComplete(source);
    }
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {var child : CBetaGwentDuelCard;child=source.TakePlayedChild();if(child && source.TemplateId()==200079)game.MonsterPower(source,child,2);return false;}
    public function Row(source : CBetaGwentDuelCard, side : int, row : int)
    {var ids : array<int>;var s : SBetaGwentCardSnapshot;var i,power : int;
     if(source.TemplateId()==200532)game.MonsterWeather(side,row,128);
     else if(source.TemplateId()==201523){Query(side,row,15,4,8,ids);for(i=0;i<ids.Size();i+=1)game.NeutralReset(game.FindCard(ids[i]));}
     else {Query(BetaGwentOpponentId(Side(source)),row,15,4,8,ids);for(i=0;i<ids.Size();i+=1){s=game.FindCard(ids[i]).Snapshot();power+=s.power.currentPower;}if(power>=25)Extremes(source,BetaGwentOpponentId(Side(source)),row,true,3,0,0);}
     game.MonsterComplete(source);
    }
    public function Trigger(kind : int, cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var source,target : CBetaGwentDuelCard;var s,t,pos : SBetaGwentCardSnapshot;var ids : array<int>;var m : SBetaGwentMatchSnapshot;var i,j,id,enemy,row,power : int;
        game.GetCards(cards);target=game.FindCard(cause.instanceId);if(target)t=target.Snapshot();m=game.NilfMatch();
        for(i=0;i<cards.Size();i+=1){s=cards[i].card;source=game.FindCard(s.instanceId);id=s.runtimeTemplate.templateId;if(!source || (s.tokenMask&4)!=0 || s.isWaitingToDie)continue;enemy=BetaGwentOpponentId(s.positionPlayerId);
         if(kind==3 && cause.instanceId==s.instanceId && id==112110 && s.locationMask==32){game.MonsterOperation(source,source,12,3,32);game.FlushEffects();game.NorthMoveInactive(source,s.positionPlayerId,16,true);}
         if(kind==9 && cause.instanceId==s.instanceId && id==112209){pos=cause;pos.locationIndex=-3;game.QueueRandomRowSpawn(pos,200320,1);}
         if(kind==4 && id==112210 && s.locationMask==16 && t.positionPlayerId==s.positionPlayerId && t.runtimeTemplate.typeMask==4 && t.runtimeTierMask==8 && target.playFromLocation==8)game.NorthRandomSummon(source);
         if(kind==6 && id==200226 && s.locationMask==32 && cause.positionPlayerId==s.positionPlayerId && s.timerValue>0){source.ChangeTimer(1,0);s=source.Snapshot();if(s.timerValue==0)game.NilfQueueReaction(source,8,s.positionPlayerId);}
         if((s.locationMask&7)==0 || (s.tokenMask&8)!=0)continue;
         if(kind==14 && id==112110){game.MonsterOperation(source,source,12,3,7);game.FlushEffects();game.NorthMoveInactive(source,s.positionPlayerId,16,true);}
         if(kind==14 && id==112101 && cause.timerValue==enemy)game.NorthMoveInactive(source,s.positionPlayerId,8,true);
         if(kind==6 && cause.positionPlayerId==s.positionPlayerId){if(id==112113)Extremes(source,enemy,7,true,1,-1,0);if(id==122107)Extremes(source,s.positionPlayerId,7,false,1,1,0);if(id==201817 && s.power.currentPower==s.power.basePower && s.timerValue==1){game.QueueTimer(source,0,1);Query(enemy,7,15,4,8,ids);game.ShuffleIds(ids);for(j=0;j<ids.Size() && j<3;j+=1)game.MonsterPower(source,game.FindCard(ids[j]),-7);}}
         if(kind==5 && cause.positionPlayerId==s.positionPlayerId && s.timerValue>0 && (id==112107 || id==112206)){source.ChangeTimer(1,0);s=source.Snapshot();if(s.timerValue==0){if(id==112107)Extremes(source,0,7,true,3,0,s.instanceId);else{Query(enemy,7,15,4,8,ids);for(j=0;j<ids.Size();j+=1)game.MonsterPower(source,game.FindCard(ids[j]),-1);game.NorthMoveInactive(source,s.positionPlayerId,8,true);game.QueueTimer(source,2,-1);}}}
        }
    }
}
