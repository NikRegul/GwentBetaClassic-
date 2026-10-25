// Archetype layer: own hand/deck only; enemy board/graves are public.
// AI generation used by the game (self-play hosts override this per seat for A/B runs).
// AI generation by the player's difficulty: easy = 2 (round economy only), normal = 3
// (exact simulation of its own plays), hard = 4 (follow-ups and public replies).
function BetaGwentAIStrength() : int
{
    switch (BetaGwentDifficultyLevel()) { case 1: return 2; case 2: return 3; }
    return 4;
}
// Display name of an opponent deck archetype (shown instead of the NPC name).
function BetaGwentAIArchetypeName(preset : int) : string
{
    var originalName : string; var profile : int;
    originalName=BetaGwentOriginalBetaDeckName(preset);
    if(originalName!="")return originalName;
    profile=BetaGwentAIPresetProfile(preset);
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
    case 93: return "Дриады: Цири нова";
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
// Cards that eat our own units on deploy: Forktail, Vran Warrior, Kayran, Barbegazi.
function BetaGwentAIOwnConsumer(id : int) : bool
{return id==201606 || id==132308 || id==132107 || id==201701;}
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
    // Plans are observations/intent, not simulated knowledge of an enemy hand.
    // 0=ordinary play, 1=preserve final, 2=bleed, 3=draw a costly response.
    public var planRound, roundPlan, planEnemyInvestment, planOwnInvestment : int;
    public var publicControl, publicCombo, publicBurst, publicThreat : int;
    public var keyThreat, cheapThreat, handReserve, publicInvestment : int;
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
        return game.Score(1)==0 && game.Score(2)==0 && roundPlan!=2;
    }
    // Recomputed before every real decision. Linear scans only: no extra search
    // work is hidden inside a UI callback or inside the effect/target handlers.
    public function PlanTurn(model : CBetaGwentPublicResponseAI)
    {
        var i,threat,ownHand,enemyHand,enemyDelta : int;
        var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        if(game.aiSimulating)return;
        publicControl=0;publicCombo=0;publicBurst=14;publicThreat=0;
        keyThreat=0;cheapThreat=0;handReserve=0;publicInvestment=0;
        ownHand=game.CountLocation(2,8);enemyHand=game.CountLocation(1,8);
        if(model){publicControl=model.controlChance;publicCombo=model.comboChance;publicBurst=Max(14,model.publicBurst);}
        for(i=0;i<hand.Size();i+=1){
            d=hand[i].Definition();threat=BetaGwentAIEngine(d.header.templateId);
            if(BetaGwentAIFinisher(d.header.templateId))threat+=3;
            keyThreat=Max(keyThreat,threat);
            if(threat>0 && d.header.tierMask==2)cheapThreat=Max(cheapThreat,threat);
            handReserve+=Max(0,Reserve(d))+Max(0,Priority(d));
        }
        for(i=0;i<game.live.Size();i+=1){
            s=game.live[i].Snapshot();
            // Public ownership follows spies and stolen units; hidden traps
            // occupy places but their identity/value cannot affect this plan.
            if(s.ownerId!=1 || (s.locationMask&39)==0 || (s.tokenMask&8)!=0 || game.live[i].createdCopy)continue;
            d=game.live[i].Definition();
            if(d.header.tierMask==8)publicInvestment+=3;
            else if(d.header.tierMask==4)publicInvestment+=1;
            if(s.positionPlayerId==1 && (s.locationMask&7)!=0 && (s.tokenMask&4)==0)
                publicThreat=Max(publicThreat,game.AiEngineValue(s,2));
        }
        if(planRound!=situation.roundNumber){
            planRound=situation.roundNumber;roundPlan=0;
            planEnemyInvestment=publicInvestment;planOwnInvestment=ownHand;
        }
        // Nothing is held back when this round is needed to survive the match.
        if(situation.playerOne.crowns>0 || situation.roundNumber>=3 || situation.playerOne.hasPassed){roundPlan=0;return;}
        if(situation.playerTwo.crowns>0){
            // Prefer a short final only with evidence of an enemy combo, a
            // sufficient hand and our own relatively independent payoffs.
            if(ownHand>=4 && ownHand>=enemyHand && !FinalNeedsLongRound() && publicCombo>=20 && handReserve<ownHand*7)roundPlan=2;
            else roundPlan=1;
            if(roundPlan==2 && (ownHand<=3 || ownHand<enemyHand || game.Score(1)-game.Score(2)>16))roundPlan=1;
        }else if(roundPlan==0 && ownHand>=4 && cheapThreat>0 && handReserve>=6 && publicControl>=20){
            roundPlan=3;planEnemyInvestment=publicInvestment;planOwnInvestment=ownHand;
        }
        enemyDelta=publicInvestment-planEnemyInvestment;
        game.AiExplain("PLAN","goal="+roundPlan+" control="+publicControl+" combo="+publicCombo+" futureThreat="+publicThreat+" reserve="+handReserve+" enemyInvestment="+enemyDelta+" spent="+(planOwnInvestment-ownHand)+" reason=reconsider_public_actions");
    }
    public function EndPressure(bestTempo : int, bestValue : int) : bool
    {
        var gap,spent : int;
        if(situation.playerOne.hasPassed || situation.playerOne.crowns>0 || situation.roundNumber>=3)return false;
        gap=game.Score(1)-game.Score(2);spent=planOwnInvestment-game.CountLocation(2,8);
        // A cheap immediate catch remains preferable; do not concede on a plan
        // label when a normal useful card can already take the lead.
        if(gap<=0 || bestTempo>gap)return false;
        if(roundPlan==3 && spent>0 && publicInvestment-planEnemyInvestment>=3 && handReserve>=6 && gap>Max(bestTempo,bestValue))return true;
        if(roundPlan==1 && situation.playerTwo.crowns>0 && game.CountLocation(2,8)<=3 && gap>bestTempo)return true;
        return false;
    }
    public function TacticalPriority(d : SBetaGwentDuelDefinition, gain : int) : int
    {
        var threat,benefit,delay,ownHand,enemyHand,value : int;
        if(game.aiSimulating || situation.playerOne.hasPassed || BetaGwentAIStrength()<4)return 0;
        ownHand=game.CountLocation(2,8);enemyHand=game.CountLocation(1,8);
        if(ownHand<2 || enemyHand==0)return 0;
        threat=BetaGwentAIEngine(d.header.templateId);
        if(BetaGwentAIFinisher(d.header.templateId))threat+=3;
        // The opponent can ignore a bait. Discount its payoff by control prior,
        // and charge the tempo/delay before preferring it over the key engine.
        if(ownHand>=3 && keyThreat>cheapThreat && cheapThreat>0 && publicControl>=20 && threat>0 && publicThreat<5){
            benefit=(keyThreat-cheapThreat)*Min(3,Horizon())*publicControl/100;
            delay=Max(1,keyThreat-Max(0,gain)/4);
            if(benefit>delay){
                if(d.header.tierMask==2 && threat==cheapThreat)value+=Min(6,benefit-delay);
                else if(threat==keyThreat)value-=Min(4,benefit-delay);
            }
        }
        // Retain one responsive answer when we can act last and no engine
        // needs stopping now. Its immediate utility overrides the small reserve.
        if(ownHand>enemyHand && publicThreat<5 && gain<publicBurst && BetaGwentAIControlCard(d))
            value-=Min(8,Max(1,(publicBurst-gain+1)/2));
        if(roundPlan==3 && d.header.tierMask==2 && threat>0)value+=2;
        return value;
    }
    // Use evidence in our actual hand before the profile prior. An engine
    // package needs time even in a normally short deck; plain bodies do not.
    public function FinalNeedsLongRound() : bool
    {
        var i,engines,independent : int;var d : SBetaGwentDuelDefinition;
        for(i=0;i<hand.Size();i+=1){d=hand[i].Definition();
            if(BetaGwentAIEngine(d.header.templateId)>0 || d.passiveBoost>0 || d.timerPeriod>0)engines+=1;
            else if(d.header.typeMask==4 && d.effect==0 || BetaGwentAIFinisher(d.header.templateId))independent+=1;
        }
        if(engines>=2 && engines*3>=hand.Size())return true;
        if(engines==0 && independent>=4)return false;
        return LongRound();
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
    private function GraveSoldiers() : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,total : int;var s : SBetaGwentCardSnapshot;
        game.GetZoneCards(2,32,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!s.isWaitingToDie && s.runtimeTierMask==2 && BetaGwentSkelligeCategory(s.runtimeTemplate.templateId,4))total+=1;}
        return total;
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
        // Stage 127: Draig first, then a Priestess of Freya raises the strengthened soldier.
        if(id==152205 && Count(hand,152310,false)>0 && GraveSoldiers()>0)value+=6;
        if(id==152310 && Count(hand,152205,false)>0 && GraveSoldiers()>0)value-=6;
        if(BetaGwentAIResurrector(id) && PileGain(d)<=0)value-=10;
        // Army strengthening benefits the whole deck before bodies are deployed.
        if(id==200046 && situation.roundNumber==1 && horizon>=2)value+=5;
        value+=ResearchOrdering(d,horizon);
        value+=SwarmOrdering(d,horizon);
        value+=RevenantPreparation098(d,horizon);
        if(id==132108 && !situation.playerOne.hasPassed && hand.Size()>1 && !MirunaPugachSetup(d)
            && (game.AiMirunaTargetPower(2,game.AiBestMirunaRow(2,d))==0
                || game.CountLocation(2,game.AiBestMirunaRow(2,d))>=8))value-=12;
        return Max(-18,Min(18,value));
    }
    // A fresh Revenant needs an item/spell after it, not merely more bodies.
    // Only our actual hand/deck supplies the setup; no enemy identity is read.
    private function RevenantPreparation098(d : SBetaGwentDuelDefinition, horizon : int) : int
    {
        var i,items,mages : int;var held : SBetaGwentDuelDefinition;
        if(profile!=5 || horizon<2 || situation.playerOne.hasPassed)return 0;
        for(i=0;i<hand.Size();i+=1){held=hand[i].Definition();
            if(held.header.typeMask==2 && BetaGwentNorthernCategory(held.header.templateId,9))items+=1;
            else if(held.header.templateId==201628)mages+=1;
        }
        // Each new base copy can trigger the next spell/item in turn. Two
        // Mages are two continuations only if two real deck targets remain.
        // Bound the forecast by the remaining own turns as well as supply.
        items+=Min(mages,DeckItems());items=Min(items,horizon-1);
        if(items==0 || Count(board,201624,true)>0)return 0;
        if(d.header.templateId==201624)return Min(10,items*4);
        return 0;
    }
    // Miruna first, then Pugach into her row next turn: the spy becomes her charm target.
    private function MirunaPugachSetup(d : SBetaGwentDuelDefinition) : bool
    {
        var row : int;
        if(profile!=3 || Count(hand,132204,false)==0)return false;
        row=game.AiBestMirunaRow(2,d);
        return row!=0 && game.CountLocation(2,row)<8 && game.CountLocation(1,row)<9;
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
    public function SlyzardHasTarget(d : SBetaGwentDuelDefinition) : bool
    {
        var cards : array<CBetaGwentDuelCard>;var i : int;var s : SBetaGwentCardSnapshot;
        game.GetZoneCards(2,32,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();
            if(s.isWaitingToDie || (s.runtimeTierMask&d.targetTiers)==0 || (s.runtimeTemplate.typeMask&d.targetTypes)==0)continue;
            if(ZoneCopies(16,cards[i].TemplateId())>0)return true;}
        return false;
    }
    private function OwnConsumersInHand() : int
    {
        var i,count : int;
        for(i=0;i<hand.Size();i+=1)if(BetaGwentAIOwnConsumer(hand[i].TemplateId()))count+=1;
        return count;
    }
    private function NekkerSeedPending(horizon : int) : bool
    {return horizon>=2 && !situation.playerOne.hasPassed && Count(hand,132211,false)>0 && Count(board,132305,true)>0;}
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
        if(id==132211){if(Count(board,132305,true)==0)value-=8;else if(horizon>=2){value+=6;if(OwnConsumersInHand()>0)value+=6;}}
        // Nekker Warrior first: its two deck copies feed every Nekker deathwish the consumer triggers.
        if(BetaGwentAIOwnConsumer(id) && NekkerSeedPending(horizon))value-=8;
        // Slyzard needs a bronze unit in our grave with a copy left in the deck (the real request).
        if(id==200539 && !SlyzardHasTarget(d))value-=12;
        if(id==132306 && game.CountLocation(2,32)==0)value-=10;
        if(id==200026 && game.CountLocation(2,16)==0)value-=12;
        if(id==162104 && ZoneCopies(32,game.LeaderTemplateId(2))==0)value-=12;
        if(id==142107 && ZoneCopies(16,113301)==0 && profile==30)value-=12;
        if(id==142107 && ZoneCopies(16,113301)==0 && profile==40)value-=12;
        if(id==122403 && game.CountLocation(1,1)+game.CountLocation(1,2)+game.CountLocation(1,4)==0 && game.CountLocation(2,32)==0 && board.Size()<2)value-=10;
        // In a mandatory two-action finish this is a body we must spend anyway;
        // an empty tutor must not displace a useful reactive card into first place.
        if(id==201628 && DeckItems()==0 && !game.AiLateOrderWindow())value-=10;
        if(id==200136 && Count(board,142205,true)==0 && Count(hand,142205,false)>0)value-=4;
        return value;
    }
    // Keep one resurrection payoff for a concrete discard setup, even while
    // the opening grave is empty. Only our known hand/deck can supply targets.
    private function PlannedResurrection(id : int) : bool
    {
        var cards : array<CBetaGwentDuelCard>;var i : int;var s : SBetaGwentCardSnapshot;var handDiscard,deckDiscard : bool;
        if(!BetaGwentAIResurrector(id) || Count(hand,id,false)>1)return false;
        handDiscard=Count(hand,152103,false)+Count(hand,152213,false)>0;
        deckDiscard=game.LeaderAvailable(2) && game.LeaderTemplateId(2)==200159;
        if(!handDiscard && !deckDiscard)return false;
        if(deckDiscard)game.GetZoneCards(2,16,cards);
        if(handDiscard)for(i=0;i<hand.Size();i+=1)cards.PushBack(hand[i]);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();
            // These return immediately on discard, leaving no resurrection target.
            if(s.runtimeTemplate.templateId==id || s.runtimeTemplate.templateId==152209 || s.runtimeTemplate.templateId==152316)continue;
            if(EligiblePile(id,s) && s.power.currentPower>0)return true;}
        return false;
    }
    public function MulliganKeepBonus(card : CBetaGwentDuelCard) : int
    {
        var limit : int;limit=BetaGwentAIResearchKeep(profile,card.TemplateId());
        if(limit>0 && Count(hand,card.TemplateId(),false)<=limit)return 8;
        if(PlannedResurrection(card.TemplateId()))return 6;
        return 0;
    }
    public function Reserve(d : SBetaGwentDuelDefinition) : int
    {return BetaGwentAIKeyReserve(BetaGwentAIFinisher(d.header.templateId),situation.roundNumber,situation.playerOne.hasPassed)+ProfileReserve(d.header.templateId);}
    // After a pass, spending one point can still burn an entire later-round engine.
    // Preserve the resurrection and Nekker chain when another legal line can win.
    public function PassedRoundReserve(d : SBetaGwentDuelDefinition) : int
    {
        var id : int;id=d.header.templateId;
        if(!situation.playerOne.hasPassed || situation.roundNumber>=3)return 0;
        if(id==200221)return 12;
        if(id==132305 && ZoneCopies(16,132305)>0)return 6;
        if(id==200539 && ZoneCopies(32,132305)>0 && ZoneCopies(16,132305)>0)return 8;
        return 0;
    }
    // 0.9.1b author lines: profile-specific finishers kept for the decisive round.
    private function ProfileReserve(id : int) : int
    {
        if(situation.roundNumber>=3 || situation.playerOne.crowns>0)return 0;
        // Dryads: Ciri Nova is a 22-power finisher only with exactly two copies of each bronze.
        if(profile==46 && id==201626)return 12;
        if(profile==3){
            if(id==132305 || id==132202)return 10;
            if(id==132108)return 5;
        }
        return 0;
    }
    private function Decisive() : bool {return situation.roundNumber>=3 || situation.playerOne.crowns>0;}
    // Own Miruna on the board whose charm is still pending and active.
    private function MirunaRow() : int
    {
        var i : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();
            if(board[i].TemplateId()==132108 && !s.isWaitingToDie && (s.tokenMask&12)==0 && s.timerValue>0)return s.locationMask;}
        return 0;
    }
    private function MirunaTimer() : int
    {
        var i : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<board.Size();i+=1){s=board[i].Snapshot();
            if(board[i].TemplateId()==132108 && !s.isWaitingToDie && (s.tokenMask&12)==0 && s.timerValue>0)return s.timerValue;}
        return 0;
    }
    private function HighestDeckUnit() : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,best,power,id : int;var s : SBetaGwentCardSnapshot;
        game.GetZoneCards(2,16,cards);power=-1;
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();
            if(s.runtimeTemplate.typeMask!=4 || (s.runtimeTierMask&6)==0)continue;
            if(s.power.currentPower>power){power=s.power.currentPower;best=cards[i].TemplateId();}}
        return best;
    }
    // Pugach on the enemy row opposite our pending Miruna is charmed back as the strongest unit there.
    public function SpyRowBonus(d : SBetaGwentDuelDefinition, row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,highest : int;var s : SBetaGwentCardSnapshot;
        if(profile!=3 || d.header.templateId!=132204 || MirunaRow()!=row)return 0;
        game.GetZoneCards(1,row,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!s.isWaitingToDie && (s.tokenMask&8)==0)highest=Max(highest,s.power.currentPower);}
        if(highest<d.header.power)return 200;
        return 40;
    }
    // Consume food preference: Nekkers are finishers, armed Behemoths are engines, Olgierd returns.
    public function FoodPenalty(t : SBetaGwentCardSnapshot) : int
    {
        var id : int;id=t.runtimeTemplate.templateId;
        if(t.positionPlayerId!=2 || (t.tokenMask&8)!=0)return 0;
        if(profile==3){
            // Nekkers are finishers: keep them growing early. In a deciding round a
            // board Nekker with a deck copy is the payoff (its deathwish summons it).
            if(id==132305 && Decisive() && (t.locationMask&7)!=0 && ZoneCopies(16,132305)>0)return 0;
            if(id==132305)return 10;
            if(id==132201 && (t.tokenMask&4)==0 && t.timerValue>0)return 8;
            if(id==112207)return -4;
        }
        return 0;
    }
    private function SwarmOrdering(d : SBetaGwentDuelDefinition, horizon : int) : int
    {
        var id,value : int;id=d.header.templateId;
        if(profile!=3)return 0;
        if(id==132305 && !situation.playerOne.hasPassed){
            if(!Decisive())value-=12;
            else if(hand.Size()>1)value-=4;
        }
        if(id==132202){
            if(!Decisive())value-=10;
            else if(!situation.playerOne.hasPassed && (Count(hand,200539,false)>0 && game.CountLocation(2,32)>0 || Count(hand,133302,false)>0 || Count(hand,132308,false)>0))value-=6;
        }
        if(id==132108){
            if(Decisive() && horizon>=2)value+=6;
            else if(!Decisive())value-=6;
        }
        if(id==132204 && !situation.playerOne.hasPassed){
            // Only when Miruna will charm Pugach himself, not a stronger unit already opposite.
            if(MirunaRow()!=0 && MirunaSpyReturn(d)>0)value+=10;
            else if(Count(hand,132108,false)>0 || ZoneCopies(16,132108)>0)value-=8;
        }
        if(id==113209 && HighestDeckUnit()==132204){
            if(MirunaRow()!=0 && !situation.playerOne.hasPassed)value+=12;else value-=10;
        }
        if(id==200091 && situation.roundNumber<3){
            if(ZoneCopies(16,132304)==0)value+=4;else value-=4;
        }
        if(id==112207 && situation.roundNumber==1 && horizon>=2 && (Count(hand,132308,false)+Count(board,132308,true))>0)value+=4;
        return value;
    }
    // Delayed swing of Pugach charmed back by our pending Miruna. The spy draw
    // simulation replaces the static tempo, so it must add this part back itself.
    public function MirunaSpyReturn(d : SBetaGwentDuelDefinition) : int
    {
        var row : int;
        // The charm fires at our turn starts; an enemy pass or empty hand does not stop
        // them. We get the next one for sure and one more per further card we can play.
        if(profile!=3 || d.header.templateId!=132204 || MirunaTimer()==0 || MirunaTimer()>Max(1,hand.Size()))return 0;
        row=MirunaRow();
        if(row!=0 && game.CountLocation(2,row)<9 && game.CountLocation(1,row)<9)
            return Max(0,d.header.power-game.AiMirunaTargetPower(2,row))*2;
        return 0;
    }
    public function PublicDeployGain(d : SBetaGwentDuelDefinition) : int
    {
        var row,i,spies : int;var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        if(d.header.templateId==132204)return MirunaSpyReturn(d);
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
        // A round-two draw can put every grown Nekker in hand. Restore one
        // deathwish target before discarding a resurrection tool; keep the seed.
        if(profile==3 && id==132305 && Count(hand,id,false)>1 && ZoneCopies(16,id)==0
            && (OwnConsumersInHand()>0 || Count(board,132308,true)>0))return 28*BetaGwentAITune(32)/100;
        if(situation.roundNumber==1 && limit>=0 && Count(hand,id,false)>limit)return 22*BetaGwentAITune(32)/100;
        if(id==112210 || id==142211 || id==132407)return 30*BetaGwentAITune(32)/100;
        // Cursed: Tormented Mages tutor the Flails, so a Flail in hand is a wasted tutor target.
        if(profile==5 && id==201633 && Count(hand,201628,false)>=Max(1,ZoneCopies(16,201633)))return 20*BetaGwentAITune(32)/100;
        if((profile==30 || profile==40) && id==113301 && Count(hand,142107,false)>0 && ZoneCopies(16,113301)==0)return 28;
        if(profile==11 && d.header.tierMask==2 && BetaGwentNorthernCategory(id,11) && Count(hand,122403,false)>0)return 25;
        if(id==200539 && (game.CountLocation(2,32)==0 || game.CountLocation(2,16)==0))return 18;
        if(id==162104 && situation.roundNumber==1 && game.CountLocation(2,16)<3)return 16;
        // Do not exchange the same instance again after it has returned to hand.
        if(id==113302 && Count(hand,132402,false)>0 && ZoneCopies(16,113302)>0)return 30*BetaGwentAITune(32)/100;
        if((id==132407 || id==132301 || id==142313) && ZoneCopies(16,id)>0)return 24*BetaGwentAITune(32)/100;
        // Keep one Wardancer in hand; the others should be summoned from deck.
        if(id==142316 && Count(hand,id,false)>1)return 30*BetaGwentAITune(32)/100;
        if(id==152307 && Count(hand,id,false)>1)return 20*BetaGwentAITune(32)/100;
        if((id==152209 || id==152316) && game.LeaderAvailable(2) && game.LeaderTemplateId(2)==200159)return 23*BetaGwentAITune(32)/100;
        if(profile==39 && situation.roundNumber==1 && id==200177 && game.LeaderAvailable(2))return 32*BetaGwentAITune(32)/100;
        if(situation.roundNumber==1 && BetaGwentAIResurrector(id) && PileGain(d)==0 && !PlannedResurrection(id))return 16*BetaGwentAITune(32)/100;
        // The graveyard is always empty at the first mulligan; Draig waits for it to fill.
        if(id==152205 && game.CountLocation(2,32)==0 && situation.roundNumber>=3)return 15*BetaGwentAITune(32)/100;
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
        // Cursed Ships needs a dead machine before its Corsairs can resurrect.
        // Seed one Longship instead of discarding the small resurrectors.
        if(profile==39 && d.header.templateId==152309 && ZoneCopies(32,152309)==0
            && Count(hand,200145,false)>0)return 55;
        return -d.header.power-Reserve(d)*4-BetaGwentAIEngine(d.header.templateId)*3;
    }
    // Setup leaders earn their value before draws and resurrection plays are spent.
    private function BranSetupPriority() : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,good,resurrections,futureResurrections : int;var cerys : bool;
        if(situation.playerOne.hasPassed || situation.roundNumber>=3)return 0;
        game.GetZoneCards(2,16,cards);
        for(i=0;i<cards.Size();i+=1){
            if(cards[i].TemplateId()==152209 || cards[i].TemplateId()==152316)good+=2;
            if(cards[i].TemplateId()==200177 || cards[i].TemplateId()==152307)good+=1;
            if(cards[i].TemplateId()==200177)cerys=true;
            if(BetaGwentAIResurrector(cards[i].TemplateId()))futureResurrections+=1;
        }
        for(i=0;i<hand.Size();i+=1)if(BetaGwentAIResurrector(hand[i].TemplateId()) || hand[i].TemplateId()==152307)resurrections+=1;
        if(good==0)return 0;
        if(profile==39 && cerys && Horizon()>=2 && futureResurrections+resurrections>=4)
            return Min(30,good*3+resurrections*2+12);
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
