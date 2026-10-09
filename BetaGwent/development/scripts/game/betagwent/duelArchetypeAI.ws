// Archetype layer: own hand/deck only; enemy board/graves are public.
// AI generation used by the game (self-play hosts override this per seat for A/B runs).
function BetaGwentAIStrength() : int { return 4; }
// Display name of an opponent deck archetype (shown instead of the NPC name).
function BetaGwentAIArchetypeName(preset : int) : string
{
    var profile : int;profile=BetaGwentAIPresetProfile(preset);
    if(profile>0)return BetaGwentAIProfileTitle(profile);
    switch(preset)
    {
    case 54: return "Шпионы";
    case 55: return "Вампиры";
    case 56: return "Рой главоглазов";
    case 57: return "Машины Хенсельта";
    case 58: return "Проклятие Адды";
    case 59: return "Темп Кальвейта";
    case 60: return "Мороз Дикой Охоты";
    case 61: return "Яйца и поглощение";
    case 62: return "Засады и Огонь";
    case 63: return "Алхимия";
    case 64: return "Кровавая луна";
    case 65: return "Ветераны Тиршаха";
    case 66: return "Краснолюды, эльфы и Огонь";
    case 67: return "Накеры и поглощение";
    case 68: return "Мечники ан Крайт";
    case 69: return "Лирийские машины";
    case 70: return "Королевская гвардия";
    case 71: return "Темерцы";
    case 72: return "Вскрытие Морврана";
    case 73: return "Мазь и пехота";
    case 74: return "Завещания";
    case 75: return "Сброс карт";
    case 76: return "Обмены";
    case 77: return "Усиление колоды Лирии";
    case 78: return "Ледяные тролли";
    case 79: return "Усиление руки Эитнэ";
    case 80: return "Морозные призраки";
    case 81: return "Усиление руки Францески";
    case 82: return "Брувер и Шуп";
    case 83: return "Сорок карт Фольтеста";
    case 84: return "Шахтёры и Ксавьер";
    case 85: return "Великаны и огры";
    case 86: return "Броня";
    case 87: return "Невольничья пехота";
    case 88: return "Усиление руки Нильфгаарда";
    case 89: return "Проклятые корабли";
    case 90: return "Усиление руки Брувера";
    case 91: return "Заклинания скоя'таэлей";
    case 92: return "Топорники";
    case 93: return "Дриады";
    }
    return "Соперник";
}

// Bounded combo forecasts are ordering preferences, never extra catch-up points.
function BetaGwentAIComboPriority(weight : int, heldPayoffs : int, activeSetups : int,
    heldSetups : int, playingSetup : bool, horizon : int) : int
{
    if(horizon<2)return 0;
    if(playingSetup)return Min(8,weight*heldPayoffs)*Min(3,horizon)/3;
    if(activeSetups==0 && heldSetups>0)return -Min(6,weight*heldSetups);
    return 0;
}
function BetaGwentAIKeyReserve(finisher : bool, round : int, enemyPassed : bool) : int
{
    if(!finisher || round>=3 || enemyPassed)return 0;
    if(round==1)return 6;
    return 3;
}
function BetaGwentAIImperaDeployGain(publicSpies : int) : int
{return Max(0,publicSpies)*2;}
class CBetaGwentArchetypeAI extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var profile : int;
    public var family : int;
    public var pairs : array<SBetaGwentAICombo>;
    public var hand, board : array<CBetaGwentDuelCard>;
    public var situation : SBetaGwentMatchSnapshot;
    public function Initialize(owner : CBetaGwentDuelSession, deck : array<int>, preset : int, leader : int)
    {
        var profiles, candidate : array<int>;var i,j,k,score,bestScore : int;
        game=owner;BetaGwentAICombos(pairs);profile=BetaGwentAIPresetProfile(preset);
        if(profile!=0){family=BetaGwentAIProfileFamily(profile);return;}
        BetaGwentAIProfileIds(profiles);bestScore=-1;
        // Only the AI's actual starting list. Multiset overlap prevents a single
        // shared gold from deciding which strategy a named NPC should follow.
        for(i=0;i<profiles.Size();i+=1)
        {
            if(BetaGwentAIProfileLeader(profiles[i])!=leader)continue;
            BetaGwentAIProfileDeck(profiles[i],candidate);score=0;
            for(j=0;j<deck.Size();j+=1)for(k=0;k<candidate.Size();k+=1)
                if(deck[j]==candidate[k]){score+=1;candidate.Erase(k);break;}
            if(score>bestScore){bestScore=score;profile=profiles[i];}
        }
        family=BetaGwentAIProfileFamily(profile);
    }
    public function Title() : string {return BetaGwentAIProfileTitle(profile);}
    public function ProfileId() : int {return profile;}
    public function PreferDecidingRound() : bool
    {
        // These profiles need time for their own engines; no unconditional bleed.
        return family!=0 && family!=BetaGwentAIProfileFamily(31) && family!=BetaGwentAIProfileFamily(27);
    }
    public function DryPass() : bool
    {
        if(situation.roundNumber!=2 || situation.playerTwo.crowns!=1 || situation.playerOne.crowns!=0)return false;
        // With no carryover on either side, force the opponent to spend a
        // card. A nonempty carryover position is evaluated as a real turn.
        return game.Score(1)==0 && game.Score(2)==0;
    }
    public function LongRound() : bool {return BetaGwentAIProfileLongRound(profile);}
    public function LiveEngines() : int
    {
        var i,count : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();if(s.isWaitingToDie || (s.tokenMask&12)!=0)continue;
            if(BetaGwentAIEngine(board[i].TemplateId())>0)count+=1;}
        return count;
    }
    public function Refresh()
    {
        var row,i : int;var part : array<CBetaGwentDuelCard>;
        situation=game.Snapshot();game.GetZoneCards(2,8,hand);board.Clear();
        for(row=1;row<=4;row*=2){game.GetZoneCards(2,row,part);for(i=0;i<part.Size();i+=1)board.PushBack(part[i]);}
    }
    private function Horizon() : int
    {
        if(situation.playerOne.hasPassed)return 0;
        return Min(3,Min(game.CountLocation(2,8),game.CountLocation(1,8)+1));
    }
    private function Count(cards : array<CBetaGwentDuelCard>, id : int, active : bool) : int
    {
        var i,total : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(cards[i].TemplateId()==id && !s.isWaitingToDie && (!active || (s.tokenMask&12)==0))total+=1;}
        return total;
    }
    public function Priority(d : SBetaGwentDuelDefinition) : int
    {
        var i,value,id,horizon,held,active : int;id=d.header.templateId;horizon=Horizon();
        for(i=0;i<pairs.Size();i+=1)
        {
            if(id==pairs[i].setup)value+=BetaGwentAIComboPriority(pairs[i].weight,Count(hand,pairs[i].payoff,false),0,0,true,horizon);
            if(id==pairs[i].payoff){active=Count(board,pairs[i].setup,true);held=Count(hand,pairs[i].setup,false);
                value+=BetaGwentAIComboPriority(pairs[i].weight,0,active,held,false,horizon);}
        }
        // Save returners for discard rather than spending a hand card on them.
        if(id==152209 || id==152316){if(Count(hand,152103,false)+Count(hand,152213,false)+Count(hand,200036,false)>0)value-=7;}
        // Queensguards multiply through resurrection; keep one seed to be killed.
        if(id==152307 && game.CountLocation(2,32)>0)value+=Min(12,QueensguardExtra(0));
        if(id==152205 && game.CountLocation(2,32)==0)value-=8;
        if(BetaGwentAIResurrector(id) && PileGain(d)<=0)value-=10;
        // Army strengthening benefits the whole deck before bodies are deployed.
        if(id==200046 && situation.roundNumber==1 && horizon>=2)value+=5;
        value+=ResearchOrdering(d,horizon);
        return Max(-18,Min(18,value));
    }
    private function AvailablePayoffs(id : int) : int
    {
        var i,count : int;var cards : array<CBetaGwentDuelCard>;var d : SBetaGwentDuelDefinition;
        game.GetZoneCards(2,16,cards);
        for(i=0;i<hand.Size();i+=1)cards.PushBack(hand[i]);
        for(i=0;i<cards.Size();i+=1){d=cards[i].Definition();if(d.header.templateId==id)continue;
            if(id==200301 && (d.unitTraits&4096)!=0)count+=1;
            else if(id==200046 && BetaGwentSkelligeCategory(d.header.templateId,7))count+=1;
            else if(id==162317 && (d.header.templateId==162316 || d.header.templateId==200163 || d.header.templateId==162103 || d.header.templateId==200031))count+=1;
            else if(id==200294 && BetaGwentSkelligeCategory(d.header.templateId,4))count+=1;
            else if(id==142201 && BetaGwentNilfDwarf(d.header.templateId))count+=1;
            else if(id==132408 && (d.unitTraits&512)!=0)count+=1;
            else if(id==142205 && d.header.typeMask==4 && !BetaGwentDuelSpying(d.header.templateId))count+=1;
            else if(id==201660 && (d.unitTraits&2176)!=0)count+=1;
            else if(id==132201 && (d.effect==16 || d.effect==23 || d.specialMode==11 || d.specialMode==20 || d.specialMode==21 || d.specialMode==24))count+=1;
            else if(id==152312 && (d.header.templateId==200105 || d.header.templateId==200300 || d.weatherToken>0))count+=1;
        }
        return count;
    }
    private function DeckItems() : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,count : int;var d : SBetaGwentDuelDefinition;
        game.GetZoneCards(2,16,cards);
        for(i=0;i<cards.Size();i+=1){d=cards[i].Definition();
            if(d.header.typeMask==2 && d.header.tierMask==2 && BetaGwentNorthernCategory(d.header.templateId,9))count+=1;}
        return count;
    }
    private function ResearchOrdering(d : SBetaGwentDuelDefinition, horizon : int) : int
    {
        var id,value,targets : int;id=d.header.templateId;
        if(horizon>=2){value=BetaGwentAIResearchOpening(profile,id);
            if(value>0 && (id==200301 || id==200046 || id==162317 || id==200294 || id==142201 || id==132408 || id==142205 || id==201660 || id==132201 || id==152312))
                value=Min(value,AvailablePayoffs(id)*2);}
        // Copy generators need an existing seed; the leader is not a reason
        // to sacrifice a live consume engine without a deathwish benefit.
        if(id==132211){if(Count(board,132305,true)==0)value-=8;else if(horizon>=2)value+=6;}
        if(id==200539 && game.CountLocation(2,32)==0)value-=12;
        if(id==132306 && game.CountLocation(2,32)==0)value-=10;
        if(id==200026 && game.CountLocation(2,16)==0)value-=12;
        if(id==162104 && ZoneCopies(32,game.LeaderTemplateId(2))==0)value-=12;
        if(id==142107 && ZoneCopies(16,113301)==0 && profile==30)value-=12;
        if(id==142107 && ZoneCopies(16,113301)==0 && profile==40)value-=12;
        if(id==122403 && game.CountLocation(1,1)+game.CountLocation(1,2)+game.CountLocation(1,4)==0 && game.CountLocation(2,32)==0 && board.Size()<2)value-=10;
        if(id==201628 && DeckItems()==0)value-=10;
        if(id==200136 && Count(board,142205,true)==0 && Count(hand,142205,false)>0)value-=4;
        return value;
    }
    public function MulliganKeepBonus(card : CBetaGwentDuelCard) : int
    {
        var limit : int;limit=BetaGwentAIResearchKeep(profile,card.TemplateId());
        if(limit>0 && Count(hand,card.TemplateId(),false)<=limit)return 8;
        return 0;
    }
    public function Reserve(d : SBetaGwentDuelDefinition) : int
    {return BetaGwentAIKeyReserve(BetaGwentAIFinisher(d.header.templateId),situation.roundNumber,situation.playerOne.hasPassed);}
    public function PublicDeployGain(d : SBetaGwentDuelDefinition) : int
    {
        var row,i,spies : int;var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        if(d.header.templateId!=162307)return 0;
        for(row=1;row<=4;row*=2){game.GetZoneCards(1,row,cards);
            for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!s.isWaitingToDie && (s.tokenMask&8)==0 && (s.tokenMask&128)!=0 && s.runtimeTemplate.typeMask==4)spies+=1;}}
        return BetaGwentAIImperaDeployGain(spies);
    }
    public function EngineThreat(s : SBetaGwentCardSnapshot, horizon : int) : int
    {
        if((s.tokenMask&12)!=0 || s.isWaitingToDie)return 0;
        return Min(12,BetaGwentAIEngine(s.runtimeTemplate.templateId)*horizon);
    }
    private function ZoneCopies(zone : int, id : int) : int
    {var cards : array<CBetaGwentDuelCard>;game.GetZoneCards(2,zone,cards);return Count(cards,id,false);}
    private function QueensguardExtra(exclude : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,total : int;var s : SBetaGwentCardSnapshot;
        game.GetZoneCards(2,32,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(cards[i].TemplateId()==152307 && s.instanceId!=exclude && !s.isWaitingToDie)total+=s.power.currentPower;}
        return total;
    }
    public function Mulligan(card : CBetaGwentDuelCard) : int
    {
        var id,limit : int;var d : SBetaGwentDuelDefinition;id=card.TemplateId();d=card.Definition();
        limit=BetaGwentAIResearchKeep(profile,id);
        if(situation.roundNumber==1 && limit>=0 && Count(hand,id,false)>limit)return 22*BetaGwentAITune(32)/100;
        if(id==112210 || id==142211 || id==132407)return 30*BetaGwentAITune(32)/100;
        if((profile==30 || profile==40) && id==113301 && Count(hand,142107,false)>0 && ZoneCopies(16,113301)==0)return 28;
        if(profile==11 && d.header.tierMask==2 && BetaGwentNorthernCategory(id,11) && Count(hand,122403,false)>0)return 25;
        if(id==200539 && (game.CountLocation(2,32)==0 || game.CountLocation(2,16)==0))return 18;
        if(id==162104 && situation.roundNumber==1 && game.CountLocation(2,16)<3)return 16;
        // Do not exchange the same instance again after it has returned to hand.
        if(id==113302 && Count(hand,132402,false)>0 && ZoneCopies(16,113302)>0)return 30*BetaGwentAITune(32)/100;
        if((id==132407 || id==132301 || id==142313) && ZoneCopies(16,id)>0)return 24*BetaGwentAITune(32)/100;
        if(id==152307 && Count(hand,id,false)>1)return 20*BetaGwentAITune(32)/100;
        if((id==152209 || id==152316) && game.LeaderAvailable(2) && game.LeaderTemplateId(2)==200159)return 23*BetaGwentAITune(32)/100;
        if(situation.roundNumber==1 && BetaGwentAIResurrector(id) && PileGain(d)==0)return 16*BetaGwentAITune(32)/100;
        if(id==152205 && game.CountLocation(2,32)==0)return 15*BetaGwentAITune(32)/100;
        return 0;
    }
    private function EligiblePile(source : int, t : SBetaGwentCardSnapshot) : bool
    {
        var id : int;id=t.runtimeTemplate.templateId;
        if(t.isWaitingToDie || t.runtimeTemplate.typeMask!=4 || (t.runtimeTierMask&6)==0)return false;
        if(source==152310)return t.runtimeTierMask==2 && BetaGwentSkelligeCategory(id,4);
        if(source==152211)return BetaGwentSkelligeCategory(id,1);
        if(source==200145)return t.runtimeTierMask==2 && BetaGwentSkelligeCategory(id,5);
        if(source==153201)return t.runtimeTemplate.factionMask==32;
        if(source==201619)return t.runtimeTierMask==2 && t.power.currentPower<=5;
        if(source==162304)return t.runtimeTierMask==2;
        if(source==201696)return t.runtimeTierMask==2 && BetaGwentNilfDwarf(id) && !BetaGwentNilfSupport(id);
        if(source==200520)return t.runtimeTemplate.factionMask==16 && t.power.currentPower<=3;
        return false;
    }
    // Concrete resurrection choices. No forecast calls for unknown card effects.
    public function PileGain(d : SBetaGwentDuelDefinition, optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,value,best,zoneSide,id : int;var s : SBetaGwentCardSnapshot;
        id=d.header.templateId;zoneSide=2;if(id==162304)zoneSide=1;
        if(id!=152310 && id!=152211 && id!=200145 && id!=153201 && id!=201619 && id!=162304 && id!=201696 && id!=200520)return 0;
        game.GetZoneCards(zoneSide,32,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!EligiblePile(id,s))continue;
            value=s.power.currentPower;if(id==153201)value+=8-s.power.basePower;
            if(s.runtimeTemplate.templateId==152307)value+=QueensguardExtra(s.instanceId);
            if(!immediate)value+=Min(6,BetaGwentAIEngine(s.runtimeTemplate.templateId)*Horizon());best=Max(best,value);}
        return best;
    }
    public function IsDiscard(source : CBetaGwentDuelCard) : bool
    {
        var id : int;id=source.TemplateId();
        if(id==200159 || id==152103 || id==152213 || id==200036)return true;
        return false;
    }
    public function DiscardValue(target : CBetaGwentDuelCard) : int
    {
        var d : SBetaGwentDuelDefinition;d=target.Definition();
        if(d.header.templateId==152209 || d.header.templateId==152316)return 100+d.header.power;
        if(d.header.templateId==152307)return 70;
        if(d.header.templateId==200177)return 60;
        return -d.header.power-Reserve(d)*4-BetaGwentAIEngine(d.header.templateId)*3;
    }
    // Setup leaders earn their value before draws and resurrection plays are spent.
    private function BranSetupPriority() : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,good,resurrections : int;
        if(situation.playerOne.hasPassed || situation.roundNumber>=3)return 0;
        game.GetZoneCards(2,16,cards);
        for(i=0;i<cards.Size();i+=1){
            if(cards[i].TemplateId()==152209 || cards[i].TemplateId()==152316)good+=2;
            if(cards[i].TemplateId()==200177 || cards[i].TemplateId()==152307)good+=1;
        }
        for(i=0;i<hand.Size();i+=1)if(BetaGwentAIResurrector(hand[i].TemplateId()) || hand[i].TemplateId()==152307)resurrections+=1;
        if(good==0)return 0;
        if(situation.roundNumber==1)return Min(18,good*3+resurrections*2);
        return Min(12,good*2+resurrections);
    }
    public function ChoiceBonus(d : SBetaGwentDuelDefinition) : int
    {return Priority(d)-Reserve(d);}
    public function CopyValue(allCopies : bool, target : CBetaGwentDuelCard, optional forecast : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,total,count : int;var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition;game.GetZoneCards(2,16,cards);
        for(i=0;i<cards.Size();i+=1)if(cards[i].TemplateId()==target.TemplateId()){
            s=cards[i].Snapshot();d=cards[i].Definition();total+=s.power.currentPower;count+=1;
            if(forecast && (d.specialMode==102 || d.effect==1))total+=Min(6,d.amount);
            if(!allCopies)break;
        }
        if(count==0)return -20;
        if(forecast)return total+Priority(target.Definition());return total;
    }
    public function LeaderGain(d : SBetaGwentDuelDefinition) : int
    {
        var i,best,value : int;var s : SBetaGwentCardSnapshot;
        if(d.header.templateId==200168){
            for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();if(!s.isWaitingToDie && (s.tokenMask&8)==0)best+=1;}
            return best;
        }
        if(d.header.templateId==200170){
            for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();if(s.runtimeTierMask!=2 || s.isWaitingToDie || (s.tokenMask&8)!=0)continue;
                if(!BetaGwentNorthernCategory(s.runtimeTemplate.templateId,5) || (s.tokenMask&256)!=0)continue;
                value=CopyValue(true,board[i]);best=Max(best,value);}
        }
        return best;
    }
    public function LeaderPriority(d : SBetaGwentDuelDefinition) : int
    {
        var i,units,engines,charges,slots : int;var held : SBetaGwentDuelDefinition;var s : SBetaGwentCardSnapshot;
        if(situation.playerOne.hasPassed || situation.roundNumber>=3)return 0;
        if(d.header.templateId==201743){
            for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();if(s.isWaitingToDie || (s.tokenMask&264)!=0)continue;
                if(s.runtimeTemplate.templateId==132201 && (s.tokenMask&4)==0 && s.timerValue>0){engines+=1;charges+=Min(3,s.timerValue);}
                else if(BetaGwentAIEngine(s.runtimeTemplate.templateId)==0)units+=1;
            }
            if(engines==0 && Count(hand,132201,false)>0)return -12;
            slots=Max(0,27-board.Size()-1);
            // Preparation preference only. Exact simulation decides actual points
            // and checks row capacity; this bonus never enters catch-up tempo.
            return Min(18,Min(charges,Min(3,units)*engines)*2+Min(3,units))-Max(0,3-slots)*4;
        }
        if(d.header.templateId==200159)return BranSetupPriority();
        if(d.header.templateId==200168){
            for(i=0;i<hand.Size();i+=1){held=hand[i].Definition();if(held.header.typeMask==4 && !BetaGwentDuelSpying(hand[i].TemplateId()))units+=1;}
            if(situation.roundNumber==1)return Min(18,units*3);
            return Min(8,units);
        }
        return 0;
    }
    public function PlacementAnchor(d : SBetaGwentDuelDefinition) : int
    {
        var i,id : int;var s : SBetaGwentCardSnapshot;id=d.header.templateId;
        if(d.header.typeMask!=4 || BetaGwentDuelSpying(id))return 0;
        // Boosts to both sides (Duda, Toruviel): stand in the middle of the fullest open row.
        if(id==112403 || id==142204)return MiddleAnchor(d);
        for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();if(s.isWaitingToDie || (s.tokenMask&12)!=0 || game.CountLocation(2,s.locationMask)>=9)continue;
            if((id==152309 || id==152109) && board[i].TemplateId()==200040)return s.instanceId;
            if(BetaGwentNorthernCategory(id,1) && (BetaGwentNorthernCategory(board[i].TemplateId(),3) || board[i].northernCrew))return s.instanceId;
        }
        return 0;
    }
    private function MiddleAnchor(d : SBetaGwentDuelDefinition) : int
    {
        var row,best,count,value,maximum : int;var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        maximum=-2147483647;
        for(row=1;row<=4;row*=2){count=game.CountLocation(2,row);if(count<2 || count>=9)continue;
            value=Min(4,count)*3-game.AiRowPlacementCost(2,row,d);if(value>maximum){maximum=value;best=row;}}
        if(best==0)return 0;
        game.GetZoneCards(2,best,cards);count=cards.Size();
        for(row=0;row<count;row+=1){s=cards[row].Snapshot();if(s.locationIndex==count/2)return s.instanceId;}
        return 0;
    }
    public function Row(d : SBetaGwentDuelDefinition, original : int) : int
    {
        var row,i,value,best,maximum,highest,total : int;var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        var id : int;id=d.header.templateId;best=original;maximum=-2147483647;
        // Effects with row-specific spawns/targets retain the existing evaluator.
        if(d.header.typeMask!=4 || BetaGwentDuelSpying(id) || d.deploySummonTemplate>0 || d.deploySpawnCount>0 || d.deathwishDamage>0 || d.deathwishSpawnCount>0)return original;
        for(row=1;row<=4;row*=2)
        {
            if(game.CountLocation(2,row)>=9)continue;game.GetZoneCards(2,row,cards);
            total=0;highest=0;for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if((s.tokenMask&8)!=0)continue;total+=s.power.currentPower;highest=Max(highest,s.power.currentPower);}
            value=-game.WeatherDamage(2,row)*Max(1,Horizon())-cards.Size();
            if(BetaGwentAIStrength()>=2)value=-game.AiRowPlacementCost(2,row,d);
            if(row==original)value+=1;
            if(!situation.playerOne.hasPassed && total+d.header.power>=25)value-=5;
            if(id==152309){for(i=0;i<cards.Size();i+=1)if(cards[i].TemplateId()==200040)value+=8;}
            if(value>maximum){maximum=value;best=row;}
        }
        return best;
    }
}
