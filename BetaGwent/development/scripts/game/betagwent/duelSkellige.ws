// Concrete original Skellige graphs, including inactive and resurrection reactions.
class CBetaGwentDuelSkellige extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var beastsOne, beastsTwo : int;
    public function Initialize(owner : CBetaGwentDuelSession) {game=owner;beastsOne=0;beastsTwo=0;}
    private function Side(source : CBetaGwentDuelCard) : int {return game.NorthActingSide(source);}
    public function History(card : CBetaGwentDuelCard)
    {if(!BetaGwentSkelligeCategory(card.TemplateId(),8))return;if(Side(card)==1)beastsOne+=1;else beastsTwo+=1;}
    private function Query(side : int, zone : int, tier : int, types : int, category : int, ignore : int, source : CBetaGwentDuelCard, out ids : array<int>)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var s : SBetaGwentCardSnapshot;var i : int;
        ids.Clear();game.GetCards(cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].card;if((side!=0 && s.positionPlayerId!=side) || (s.locationMask&zone)==0 || (s.runtimeTierMask&tier)==0 || (s.runtimeTemplate.typeMask&types)==0 || s.isWaitingToDie || (s.tokenMask&ignore)!=0)continue;
         if(category>0 && !BetaGwentSkelligeCategory(s.runtimeTemplate.templateId,category))continue;if(source && source.monsterIds.Contains(s.instanceId))continue;ids.PushBack(s.instanceId);}
    }
    private function Request(source : CBetaGwentDuelCard, side : int, zone : int, tier : int, types : int, category : int, minimum : int)
    {var ids : array<int>;Query(side,zone,tier,types,category,BetaGwentNorthPick((zone&7)!=0,264,0),source,ids);game.MonsterRequest(source,ids,BetaGwentNorthPick((zone&7)!=0,0,2),minimum,1);}
    private function Enemy(source : CBetaGwentDuelCard, minimum : int) {Request(source,BetaGwentOpponentId(Side(source)),7,15,4,0,minimum);}
    private function Friendly(source : CBetaGwentDuelCard) {Request(source,Side(source),7,15,4,0,0);}
    private function RandomDamage(source : CBetaGwentDuelCard, side : int, row : int, damage : int)
    {var ids : array<int>;Query(side,row,15,4,0,8,NULL,ids);if(ids.Size()>0)game.MonsterPower(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),-damage);}
    private function Adjacent(source : CBetaGwentDuelCard, delta : int) : CBetaGwentDuelCard
    {var ids : array<int>;var s,t : SBetaGwentCardSnapshot;var i : int;s=source.Snapshot();Query(s.positionPlayerId,s.locationMask,15,4,0,8,NULL,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.locationIndex==s.locationIndex+delta)return game.FindCard(ids[i]);}return NULL;}
    private function CreateChoice(source : CBetaGwentDuelCard, randomThree : bool)
    {var ids : array<int>;BetaGwentSkelligePool(source.TemplateId(),ids);if(randomThree){game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);}game.MonsterRequest(source,ids,1,1,1);}
    public function Played(source : CBetaGwentDuelCard)
    {
        var id,side,enemy,i,count : int;var s,t,pos : SBetaGwentCardSnapshot;var ids,valid : array<int>;
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();source.monsterStage=0;source.monsterIds.Clear();source.monsterRemaining=1;
        BetaGwentLog("DUEL_SKELLIGE_PLAY template="+id+" side="+side);
        if(id==152101 || id==152201){pos=s;pos.positionPlayerId=enemy;pos.locationIndex=-3;game.QueueSpawn(pos,BetaGwentNorthPick(id==152101,152401,152403),1);}
        else if(id==200040){game.QueueTimer(source,2,2);}
        else if(id==152103 || id==152213){game.NilfDraw(side,14,false);if(id==152103)game.NilfDraw(side,14,false);source.monsterRemaining=BetaGwentNorthPick(id==152103,2,1);Request(source,side,8,14,14,0,1);return;}
        else if(id==152105){ids.PushBack(1);ids.PushBack(2);ids.PushBack(4);game.MonsterRequest(source,ids,3,1,1);return;}
        else if(id==152106 || id==200036){Request(source,side,16,2,BetaGwentNorthPick(id==152106,4,6),0,0);return;}
        else if(id==152107){Request(source,0,7,6,12,0,1);return;}
        else if(id==152202 || id==200028 || id==200105 || id==200300 || id==201578){Enemy(source,BetaGwentNorthPick(id==200300 || id==201578,1,0));return;}
        else if(id==152203 || id==152317 || id==200147){source.monsterRemaining=2;if(id==200147)game.NorthClearHazard(side,s.locationMask);Friendly(source);return;}
        else if(id==152204){Query(0,7,15,4,0,256,NULL,ids);game.MonsterRequest(source,ids,0,0,1);return;}
        else if(id==152205){source.monsterRemaining=2;Request(source,side,32,14,4,0,0);return;}
        else if(id==152206 || id==201581 || id==201642){CreateChoice(source,id!=152206);return;}
        else if(id==152207){Enemy(source,0);return;}
        else if(id==152109)source.monsterStage=0;
        else if(id==152208 || id==152303)game.MonsterPower(source,source,-1);
        else if(id==152211 || id==152310 || id==200145){Request(source,side,32,BetaGwentNorthPick(id==152211,6,2),4,BetaGwentNorthPick(id==152211,1,BetaGwentNorthPick(id==152310,4,5)),BetaGwentNorthPick(id==152211,0,1));return;}
        else if(id==152214){if(s.timerValue==1){Query(side,16,14,14,0,0,NULL,ids);game.ShuffleIds(ids);while(ids.Size()>2)ids.Erase(ids.Size()-1);source.monsterIds=ids;game.MonsterRequest(source,ids,2,1,1);return;}}
        else if(id==152302){Query(side,7,15,4,0,8,NULL,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower<t.power.basePower+t.power.permanentPower || BetaGwentSkelligeCategory(t.runtimeTemplate.templateId,3))count+=1;}game.MonsterPower(source,source,count);}
        else if(id==152305){Query(side,16,14,4,0,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==id)game.NilfDiscard(game.FindCard(ids[i]));}
        else if(id==152306){Query(side,16,2,12,2,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()!=id)valid.PushBack(ids[i]);game.MonsterRequest(source,valid,2,0,1);return;}
        else if(id==152307){Query(side,32,2,4,0,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==id)game.NorthResurrect(game.FindCard(ids[i]),0,s.locationMask,-3,false);}
        else if(id==152308){Request(source,side,7,15,4,1,0);return;}
        else if(id==152311){Friendly(source);return;}
        else if(id==201644){Query(side,7,15,4,0,264,NULL,ids);for(i=ids.Size()-1;i>=0;i-=1){t=game.FindCard(ids[i]).Snapshot();if(t.power.currentPower>=t.power.basePower+t.power.permanentPower)ids.Erase(i);}game.MonsterRequest(source,ids,0,1,1);return;}
        else if(id==152314)RandomDamage(source,enemy,7,2);
        else if(id==152318)game.NorthSummonCopies(source,id);
        else if(id==153201){Query(side,32,6,12,0,0,NULL,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();if(t.runtimeTemplate.factionMask==32)valid.PushBack(ids[i]);}game.MonsterRequest(source,valid,2,1,1);return;}
        else if(id==200043){pos=s;pos.locationIndex=s.locationIndex;game.QueueSpawn(pos,201573,1);pos.locationIndex=s.locationIndex+2;game.QueueSpawn(pos,201574,1);pos.positionPlayerId=enemy;pos.locationIndex=-3;game.QueueSpawn(pos,201572,1);}
        else if(id==200046){Query(side,31,15,4,7,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(ids[i]!=s.instanceId)game.MonsterOperation(source,game.FindCard(ids[i]),12,1,31);}
        else if(id==200081 || id==200212){Query(side,16,BetaGwentNorthPick(id==200081,2,6),BetaGwentNorthPick(id==200081,2,12),BetaGwentNorthPick(id==200081,6,3),0,NULL,ids);if(ids.Size()>0){game.MonsterPlayExisting(source,game.FindCard(ids[game.RandomIndex(ids.Size())]));return;}}
        else if(id==200102){ids.PushBack(201717);ids.PushBack(201718);game.MonsterRequest(source,ids,1,1,1);return;}
        else if(id==200103){if(side==1)count=beastsOne;else count=beastsTwo;game.MonsterPower(source,source,-Max(0,10-count*2));}
        else if(id==200104){Query(enemy,7,15,4,0,8,NULL,ids);for(i=0;i<ids.Size();i+=1){t=game.FindCard(ids[i]).Snapshot();game.MonsterPower(source,game.FindCard(ids[i]),-BetaGwentNorthPick(t.power.currentPower<t.power.basePower+t.power.permanentPower,2,1));}}
        else if(id==200146){Request(source,side,32,2,4,0,0);return;}
        else if(id==200149){Request(source,side,16,2,14,9,0);return;}
        else if(id==200528){Query(side,7,2,4,0,264,NULL,ids);Query(side,16,2,4,0,0,NULL,valid);for(i=ids.Size()-1;i>=0;i-=1){t=game.FindCard(ids[i]).Snapshot();if(!BetaGwentSkelligeCategory(t.runtimeTemplate.templateId,4) && !BetaGwentSkelligeCategory(t.runtimeTemplate.templateId,5)){ids.Erase(i);continue;}count=0;for(count=0;count<valid.Size();count+=1)if(game.FindCard(valid[count]).TemplateId()==t.runtimeTemplate.templateId)break;if(count==valid.Size())ids.Erase(i);}game.MonsterRequest(source,ids,0,0,1);return;}
        else if(id==201623){Query(side,7,15,4,0,8,NULL,ids);for(i=ids.Size()-1;i>=0;i-=1)if(ids[i]==s.instanceId)ids.Erase(i);if(ids.Size()>0){game.QueueDestroy(game.FindCard(ids[game.RandomIndex(ids.Size())]));game.MonsterPower(source,source,10);}}
        else if(id!=152104 && id!=152109 && id!=152209 && id!=152210 && id!=152301 && id!=152309 && id!=152316 && id!=200040 && id!=200177 && id!=201646 && id!=201778 && id!=152401 && id!=152402 && id!=152403 && id!=152405 && id!=201572 && id!=201573 && id!=201574){game.FailAbility("Карта Скеллиге не подключена.");return;}
        game.MonsterComplete(source);
    }
    public function Select(source : CBetaGwentDuelCard, selected : int)
    {
        var d : SBetaGwentDuelDefinition;var id,side,enemy,i,count,power : int;var target : CBetaGwentDuelCard;var s,t,u : SBetaGwentCardSnapshot;var ids,valid : array<int>;
        id=source.TemplateId();side=Side(source);enemy=BetaGwentOpponentId(side);s=source.Snapshot();target=game.FindCard(selected);
        if(id==152206 || id==201581 || id==201642){if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}
        if(id==200102){if(source.monsterStage==0){source.monsterStage=1;source.monsterStored=selected;if(selected==201717){Request(source,side,16,6,12,3,0);return;}game.NilfInitialPool(enemy,ids);for(i=ids.Size()-1;i>=0;i-=1){d=BetaGwentDuelDefinition(ids[i]);if(d.header.tierMask!=4 || d.header.typeMask!=4 || ids[i]==152214)ids.Erase(i);}game.ShuffleIds(ids);while(ids.Size()>3)ids.Erase(ids.Size()-1);game.MonsterRequest(source,ids,1,1,1);return;}if(source.monsterStored==201718){if(selected>0)game.MonsterCreate(source,selected);else game.MonsterComplete(source);return;}}
        if(!target){if(id==152204 && source.monsterStage==0){source.monsterStage=1;Request(source,enemy,32,2,4,0,0);return;}game.MonsterComplete(source);return;}t=target.Snapshot();
        if(id==152211 || id==152310 || id==200145 || id==152306 || id==200149 || id==200102){game.MonsterPlayExisting(source,target);return;}
        if(id==152103 || id==152213 || id==200036){game.NilfDiscard(target);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,side,8,14,14,0,1);return;}}
        else if(id==152106){if(source.monsterStage==0){source.monsterStored=t.power.basePower;source.monsterStage=1;game.NilfDiscard(target);Enemy(source,0);return;}game.MonsterPower(source,target,-source.monsterStored);}
        else if(id==152107)game.QueueTransform(source,target,200307);
        else if(id==152202)game.MonsterDuel(source,target,0,0);
        else if(id==152203 || id==152317 || id==200147){source.monsterIds.PushBack(selected);if(id==152203){game.MonsterPower(source,target,-1);game.MonsterOperation(source,source,12,2,7);}if(id==152317){game.MonsterOperation(source,target,13,Max(0,t.power.basePower+t.power.permanentPower-t.power.currentPower),7);game.QueueArmor(target,3,source);}if(id==200147)game.QueueRelocation(target,side,s.locationMask,false);source.monsterRemaining-=1;if(source.monsterRemaining>0){Friendly(source);return;}}
        else if(id==152204){if(source.monsterStage==0){game.MonsterOperation(source,target,6,0,7);source.monsterStage=1;Request(source,enemy,32,2,4,0,0);return;}game.NorthMoveInactive(target,side,32,false);}
        else if(id==152205){source.monsterIds.PushBack(selected);game.MonsterOperation(source,target,12,3,32);source.monsterRemaining-=1;if(source.monsterRemaining>0){Request(source,side,32,14,4,0,0);return;}}
        else if(id==152207){game.MonsterPower(source,target,-6);game.FlushDeaths();u=target.Snapshot();if((u.locationMask&7)==0){Query(side,32,14,4,0,8,NULL,ids);power=-1;for(i=0;i<ids.Size();i+=1){u=game.FindCard(ids[i]).Snapshot();power=Max(power,u.power.currentPower);}for(i=0;i<ids.Size();i+=1){u=game.FindCard(ids[i]).Snapshot();if(u.power.currentPower==power)valid.PushBack(ids[i]);}if(valid.Size()>0)game.MonsterOperation(source,game.FindCard(valid[game.RandomIndex(valid.Size())]),12,3,32);}}
        else if(id==152214){game.NilfTake(target,side);for(i=0;i<source.monsterIds.Size();i+=1)if(source.monsterIds[i]!=selected)game.NilfDiscard(game.FindCard(source.monsterIds[i]));game.QueueTimer(source,0,1);}
        else if(id==152308){Query(side,7,15,4,0,8,NULL,ids);for(i=0;i<ids.Size();i+=1)if(BetaGwentSkelligeSameClan(t.runtimeTemplate.templateId,game.FindCard(ids[i]).TemplateId()))game.MonsterPower(source,game.FindCard(ids[i]),1);}
        else if(id==152311){game.MonsterOperation(source,target,12,2,7);game.QueueArmor(target,2,source);}
        else if(id==153201){if(source.monsterStage==0){target.AddTokens(512);target.ChangeBasePower(8-t.power.basePower,true);game.NorthMoveInactive(target,side,8,false);source.monsterStage=1;Request(source,side,8,14,14,0,1);return;}game.MonsterPlayExisting(source,target);return;}
        else if(id==200028){if(t.power.currentPower<t.power.basePower+t.power.permanentPower)game.QueueDestroy(target);else game.MonsterPower(source,target,-2);}
        else if(id==200105){for(i=0;i<4;i+=1)game.MonsterPower(source,target,-1);}
        else if(id==200146)game.NorthMoveInactive(target,side,16,false);
        else if(id==200300){game.QueueRelocation(target,enemy,s.locationMask,false);game.FlushDeaths();game.MonsterPower(source,target,-game.CountLocation(enemy,s.locationMask));}
        else if(id==200528){game.MonsterPower(source,target,-1);Query(side,16,2,4,0,0,NULL,ids);for(i=0;i<ids.Size();i+=1)if(game.FindCard(ids[i]).TemplateId()==t.runtimeTemplate.templateId){game.MonsterPlayExisting(source,game.FindCard(ids[i]));return;}}
        else if(id==201578)game.MonsterPower(source,target,-BetaGwentNorthPick(source.playFromLocation==32,6,4));
        else if(id==201644){power=Max(0,t.power.basePower+t.power.permanentPower-t.power.currentPower);game.MonsterOperation(source,target,13,Max(0,t.power.basePower+t.power.permanentPower-t.power.currentPower),7);game.MonsterPower(source,target,power);}
        game.MonsterComplete(source);
    }
    public function ChildReturned(source : CBetaGwentDuelCard) : bool
    {var child : CBetaGwentDuelCard;child=source.TakePlayedChild();if(child && source.TemplateId()==201642)game.MonsterOperation(source,child,12,3,7);return false;}
    public function Row(source : CBetaGwentDuelCard, side : int, row : int) {game.MonsterWeather(side,row,64);game.MonsterComplete(source);}
    public function PowerChanged(target : CBetaGwentDuelCard, old : SBetaGwentCardSnapshot, current : SBetaGwentCardSnapshot)
    {var cards : array<SBetaGwentDevelopmentCard>;var source : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;var i : int;
     if(current.power.currentPower+current.power.basePower>=old.power.currentPower+old.power.basePower)return;
     if(target.TemplateId()==152301 && (current.locationMask&7)!=0 && (current.tokenMask&4)==0)game.QueueTransform(target,target,152405);
     if(old.power.currentPower+old.power.basePower>current.power.currentPower+current.power.basePower && (current.locationMask&7)!=0){game.GetCards(cards);for(i=0;i<cards.Size();i+=1){s=cards[i].card;if(s.runtimeTemplate.templateId==201646 && (s.locationMask&7)!=0 && (s.tokenMask&12)==0 && s.positionPlayerId!=current.positionPlayerId)game.MonsterPower(game.FindCard(s.instanceId),game.FindCard(s.instanceId),1);}}
    }
    public function Trigger(kind : int, cause : SBetaGwentCardSnapshot)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var source,target,left,right : CBetaGwentDuelCard;var s,t,pos : SBetaGwentCardSnapshot;var ids : array<int>;var m : SBetaGwentMatchSnapshot;var i,j,id,row,amount : int;
        game.GetCards(cards);target=game.FindCard(cause.instanceId);if(target)t=target.Snapshot();m=game.NilfMatch();
        for(i=0;i<cards.Size();i+=1){s=cards[i].card;source=game.FindCard(s.instanceId);id=s.runtimeTemplate.templateId;if(!source || s.isWaitingToDie || (s.tokenMask&4)!=0)continue;
         if(kind==3 && target && t.locationMask==32 && t.positionPlayerId==s.positionPlayerId && (cause.locationMask&24)!=0){if((s.locationMask&7)!=0 && id==152314)RandomDamage(source,BetaGwentOpponentId(s.positionPlayerId),7,2);if(id==201778 && t.runtimeTemplate.typeMask==4 && (s.locationMask&7)!=0 && s.timerValue>0 && (t.tokenMask&512)==0 && m.currentPlayerId==s.positionPlayerId){source.ChangeTimer(1,0);game.NilfQueueReaction(target,7,t.positionPlayerId);}}
         if(kind==15 && id==152209 && s.locationMask==32){amount=(s.power.basePower+1)/2;source.ChangeBasePower(-amount,true);t=source.Snapshot();if(t.power.basePower+t.power.permanentPower>0)game.NorthResurrect(source,0,0,-3,false);}
         if(kind==3 && t.instanceId==s.instanceId && s.locationMask==32 && (cause.locationMask&767)!=0){if(id==152209){amount=(s.power.basePower+1)/2;source.ChangeBasePower(-amount,true);t=source.Snapshot();if(t.power.basePower+t.power.permanentPower>0)game.NorthResurrect(source,0,BetaGwentNorthPick((cause.locationMask&7)!=0,cause.locationMask,0),BetaGwentNorthPick((cause.locationMask&7)!=0,cause.locationIndex,-3),false);}if(id==152316 && (cause.locationMask&24)!=0)game.NorthResurrect(source,0,0,-3,false);}
         if(kind==3 && id==200177 && s.locationMask==32 && target && cause.locationMask==32 && (t.locationMask&7)!=0 && (m.currentPlayerId==s.positionPlayerId || t.runtimeTemplate.templateId==112207 || t.runtimeTemplate.templateId==152209 || t.runtimeTemplate.templateId==200529)){source.ChangeTimer(1,0);t=source.Snapshot();if(t.timerValue==0)game.NorthResurrect(source,0,0,-3,false);}
         if(kind==3 && id==152210 && (s.locationMask&7)!=0 && target && cause.locationMask==8 && (t.locationMask&7)!=0 && t.positionPlayerId!=s.positionPlayerId && (t.tokenMask&8)==0)game.MonsterPower(source,target,-1);
         if(kind==9 && cause.instanceId==s.instanceId){pos=cause;pos.locationIndex=-3;if(id==152104)game.QueueRandomRowSpawn(pos,152402,1);if(id==152401){Query(BetaGwentOpponentId(cause.positionPlayerId),7,15,4,0,264,NULL,ids);for(j=0;j<ids.Size();j+=1)if(game.FindCard(ids[j]).TemplateId()==152101)game.MonsterPower(source,game.FindCard(ids[j]),10);}if(id==201572 && m.currentPlayerId==BetaGwentOpponentId(cause.positionPlayerId)){pos.positionPlayerId=BetaGwentOpponentId(cause.positionPlayerId);game.QueueRandomRowSpawn(pos,152406,1);}if(id==201573){Query(cause.positionPlayerId,7,15,4,0,8,NULL,ids);if(ids.Size()>0)game.MonsterOperation(source,game.FindCard(ids[game.RandomIndex(ids.Size())]),12,4,7);}if(id==201574){Query(BetaGwentOpponentId(cause.positionPlayerId),cause.locationMask,15,4,0,8,NULL,ids);for(j=0;j<ids.Size();j+=1)game.MonsterPower(source,game.FindCard(ids[j]),-4);}}
         if(kind==12 && cause.instanceId==s.instanceId && id==152402){Query(0,7,15,12,0,0,NULL,ids);for(j=0;j<ids.Size();j+=1)if(ids[j]!=s.instanceId)game.QueueDestroy(game.FindCard(ids[j]));for(row=1;row<=4;row*=2){game.NorthClearRow(1,row);game.NorthClearRow(2,row);}}
         if((s.locationMask&7)==0 || (s.tokenMask&8)!=0)continue;
         if(kind==5 && cause.positionPlayerId==s.positionPlayerId && id==200040 && s.timerValue>0){
             source.ChangeTimer(1,0);t=source.Snapshot();
             if(t.timerValue==0){
                 game.QueueTimer(source,1,2);
                 if(t.power.currentPower<t.power.basePower+t.power.permanentPower){
                     game.MonsterOperation(source,source,13,t.power.basePower+t.power.permanentPower-t.power.currentPower,7);
                     game.MonsterOperation(source,source,12,2,7);
                 }
                 BetaGwentLog("DUEL_SWORDSMAN_CYCLE card="+s.instanceId+" reset=2 damaged="+(t.power.currentPower<t.power.basePower+t.power.permanentPower));
             }
         }
         if(kind==6 && cause.positionPlayerId==s.positionPlayerId){if(id==152109){left=Adjacent(source,-1);right=Adjacent(source,1);if(left)game.MonsterOperation(source,left,12,1,7);if(right)game.MonsterPower(source,right,-1);}if(id==152309){right=Adjacent(source,1);if(right){game.MonsterPower(source,right,-1);game.MonsterPower(source,source,2);}}if(id==152403){ids.Clear();for(row=1;row<=4;row*=2)if(game.CountLocation(s.positionPlayerId,row)<9 || row==s.locationMask)ids.PushBack(row);if(ids.Size()>0){row=ids[game.RandomIndex(ids.Size())];game.QueueRelocation(source,s.positionPlayerId,row,false);game.FlushEffects();Query(s.positionPlayerId,row,15,4,0,8,NULL,ids);for(j=0;j<ids.Size();j+=1)if(ids[j]!=s.instanceId)game.MonsterPower(source,game.FindCard(ids[j]),-1);}}}
        }
    }
}
