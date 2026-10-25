// Direct source handlers over typed request items. XML integer settings are
// resolved by the static generator. No Best*/Ai* policy calls are permitted.
struct SBetaOriginalItem {
    var id, templateId, side, zone, row, index, power, basePower, templateTier, typeMask, tokens : int;
    var visibleToBoth, inExecution, playable : bool;
}
struct SBetaOriginalRow { var side, row, token : int; }
struct SBetaOriginalRequest { var kind : string; var source, sourceHint, actor, minimum, maximum : int; var items : array<SBetaOriginalItem>; }
struct SBetaOriginalFilter { var valid : bool; var items : array<SBetaOriginalItem>; }
struct SBetaOriginalRank { var item : SBetaOriginalItem; var value : float; }
struct SBetaOriginalSummationEntry { var weight : float; var scoring : string; var rounds : int; }
struct SBetaOriginalPropagated { var node : CBetaOriginalNode; var key : int; var value : float; }
struct SBetaOriginalDecision {
    var chosen, branches, filtered : array<SBetaOriginalItem>;
    var filteredValid, sourceFallback : bool; var propagated : float;
}
class CBetaOriginalHandlerContext extends IScriptable {
    public var node : CBetaOriginalNode; public var p : CBetaOriginalPersonality;
    public var cards : array<SBetaOriginalItem>;public var rows : array<SBetaOriginalRow>;
    public var actor, roundIndex : int; public var random : CBetaGwentRandomGenerator;
    public var failed : bool;public var error : string;
    public function Next(minimum : int, maximum : int) : int {
        if(!random || maximum<=minimum){failed=true;error="Invalid original SimulatorRandom range";return minimum;}
        return minimum+random.NextBounded(maximum-minimum);
    }
}
function BetaOriginalSameItem(a : SBetaOriginalItem, b : SBetaOriginalItem, kind : string) : bool {
    if(kind=="play")return a.side==b.side && a.row==b.row && a.index==b.index;
    if(kind=="locations")return a.side==b.side && a.row==b.row;
    return a.id==b.id;
}
function BetaOriginalItemKey(item : SBetaOriginalItem, kind : string) : int {
    if(kind=="play" || kind=="locations")return item.side^item.row;
    return item.id;
}
function BetaOriginalByPlayer(items : array<SBetaOriginalItem>, actor : int, loyalty : string) : array<SBetaOriginalItem> {
    var result : array<SBetaOriginalItem>;var i, side : int;
    side=3-actor;if(loyalty=="Same")side=actor;
    for(i=0;i<items.Size();i+=1)if(loyalty=="Both" || items[i].side==side)result.PushBack(items[i]);return result;
}
function BetaOriginalByTier(items : array<SBetaOriginalItem>, tier : int) : array<SBetaOriginalItem> {
    var result : array<SBetaOriginalItem>;var i : int;
    for(i=0;i<items.Size();i+=1)if(tier==0 || (items[i].templateTier & tier)!=0)result.PushBack(items[i]);return result;
}
function BetaOriginalSorted(ranks : array<SBetaOriginalRank>, descending : bool) : array<SBetaOriginalItem> {
    var result : array<SBetaOriginalItem>;var i,j : int;var scoreEntry : SBetaOriginalRank;
    for(i=1;i<ranks.Size();i+=1) {
        scoreEntry=ranks[i];j=i-1;
        while(j>=0) {
            if((descending && ranks[j].value>=scoreEntry.value) || (!descending && ranks[j].value<=scoreEntry.value))break;
            ranks[j+1]=ranks[j];j-=1;
        }
        ranks[j+1]=scoreEntry;
    }
    for(i=0;i<ranks.Size();i+=1)result.PushBack(ranks[i].item);return result;
}
class CBetaOriginalHandler extends IScriptable {
    public var kind, SortOrder, PlayerType, EffectType, SummationName, LocationAction, PowerLevel, NumCards, Destination, WedgeType : string;
    public var CardGroup, SemanticTagId, TagsTokenType, Location, UnitOrEvent, Health, TemplateId, MinRange, MaxRange : int;
    public var Negate, hasSheet : bool;public var propagate : float;
    public var children : array<CBetaOriginalHandler>;public var entries : array<SBetaOriginalSummationEntry>;
    public var scores : array<SBetaOriginalPropagated>;
    public function Initialize() {
        CardGroup=15;SemanticTagId=1;TagsTokenType=1;Location=7;UnitOrEvent=14;Health=1;
        SortOrder="Highest";PlayerType="Both";EffectType="Hazard";LocationAction="CanGotoLocation";
        Destination="MatchSource";WedgeType="LeftOf";
    }
    public function Add(node : CBetaOriginalNode, key : int, value : float) {
        var i : int;var scoreEntry : SBetaOriginalPropagated;
        if(value==0.0f || kind=="Summation")return;
        for(i=0;i<scores.Size();i+=1)if(scores[i].node==node && scores[i].key==key){scoreEntry=scores[i];scoreEntry.value+=value;scores[i]=scoreEntry;return;}
        scoreEntry.node=node;scoreEntry.key=key;scoreEntry.value=value;scores.PushBack(scoreEntry);
    }
    public function Get(node : CBetaOriginalNode, key : int) : float {
        var i : int;var value : float;
        if(kind=="Summation"){for(i=0;i<children.Size();i+=1)value+=children[i].Get(node,key);return value;}
        for(i=0;i<scores.Size();i+=1)if(scores[i].node==node && scores[i].key==key)return scores[i].value;return 0.0f;
    }
    // Literal source: Summation does not override cleanup of child maps.
    public function Cleanup(){scores.Clear();}
    public function AddAll(node : CBetaOriginalNode, items : array<SBetaOriginalItem>, requestKind : string) {
        var i : int;for(i=0;i<items.Size();i+=1)Add(node,BetaOriginalItemKey(items[i],requestKind),propagate);
    }
    public function CanBranchPlacement() : bool {
        return kind=="PlayAll" || kind=="Power" || kind=="PowerRange" || kind=="Location" || kind=="Wedge" || kind=="Occurrence" || kind=="OccurrenceRange";
    }
    public function Advanced() : bool {
        return kind=="PowerRange" || kind=="OccurrenceRange" || kind=="Wedge" || kind=="RowWithCeiling" || kind=="RowWithEffect" || kind=="RowWithNumberOfUnits" || kind=="RowWithUnitStrength";
    }
    public function Weight(scoreEntry : SBetaOriginalSummationEntry, child : CBetaOriginalHandler, position : int, total : int, minimum : int, maximum : int) : float {
        var scoring : string;scoring="Linear";if(child.Advanced())scoring=scoreEntry.scoring;
        if(scoring=="MaxNumberFromRequestStaggered"){if(position>=maximum)return 0.0f;total=maximum;scoring="StaggeredPercentile";}
        if(scoring=="StaggeredPercentile"){if(total<=1)return scoreEntry.weight;return ((float)(total-position)/(float)(total))*scoreEntry.weight;}
        if(scoring=="MinNumberFromRequest"){if(position>=minimum)return 0.0f;return scoreEntry.weight;}
        if(scoring=="MaxNumberFromRequest"){if(position>=maximum)return 0.0f;return scoreEntry.weight;}
        if(scoring=="SingleBest"){if(position!=0)return 0.0f;return scoreEntry.weight;}
        return scoreEntry.weight;
    }
    public function RowPower(ctx : CBetaOriginalHandlerContext, item : SBetaOriginalItem, tier : int) : int {
        var i, total : int;var c : SBetaOriginalItem;
        if((item.row & 7)==0)return 0;
        for(i=0;i<ctx.cards.Size();i+=1){c=ctx.cards[i];if(c.side==item.side && c.zone==item.row && (c.templateTier & tier)!=0 && c.visibleToBoth && !c.inExecution)total+=c.power;}
        return total;
    }
    public function Occurrences(item : SBetaOriginalItem, pool : array<SBetaOriginalItem>) : int {
        var count, i : int;for(i=0;i<pool.Size();i+=1)if(pool[i].templateId==item.templateId)count+=1;return count;
    }
    public function FitsOccurrences(count : int) : bool { return kind=="Occurrence" || (count>=MinRange && count<=MaxRange); }
    public function Preference(ctx : CBetaOriginalHandlerContext, item : SBetaOriginalItem, cards : bool) : float {
        var value : float;var i : int;var t : SBetaOriginalTemplate;
        if(!ctx.p){ctx.failed=true;ctx.error="Preference requires original personality";return 0.0f;}
        if(!cards){if(item.row==1)return ctx.p.MeleePreference;if(item.row==2)return ctx.p.RangedPreference;if(item.row==4)return ctx.p.SiegePreference;return 0.0f;}
        t=BetaOriginalTemplate(item.templateId);
        for(i=0;i<ctx.p.semanticTags.Size();i+=1)if(t.semanticTags.Contains(ctx.p.semanticTags[i].id))value+=ctx.p.semanticTags[i].weight;return value;
    }
    public function Neighbour(ctx : CBetaOriginalHandlerContext, position : SBetaOriginalItem, atIndex : int, out item : SBetaOriginalItem) : bool {
        var i : int;
        for(i=0;i<ctx.cards.Size();i+=1)if(ctx.cards[i].side==position.side && ctx.cards[i].zone==position.row && ctx.cards[i].index==atIndex){item=ctx.cards[i];return true;}
        return false;
    }
    public function WedgePasses(item : SBetaOriginalItem) : bool {
        var t : SBetaOriginalTemplate;t=BetaOriginalTemplate(item.templateId);
        return (item.templateTier & CardGroup)!=0 && (TemplateId==0 || ((item.templateId==TemplateId)!=Negate)) && (SemanticTagId<=1 || (t.semanticTags.Contains(SemanticTagId)!=Negate));
    }
    public function RowScore(ctx : CBetaOriginalHandlerContext, item : SBetaOriginalItem, cards : bool) : int {
        var i, row, value, token, effect, tokenKind : int;var boon,hazard : bool;var c : SBetaOriginalItem;
        row=item.row;if(cards)row=item.zone;
        if(kind=="RowWithNumberOfUnits" || kind=="RowWithUnitStrength") {
            for(i=0;i<ctx.cards.Size();i+=1){c=ctx.cards[i];if(c.side==item.side && c.zone==row && (c.templateTier & CardGroup)!=0){if(kind=="RowWithNumberOfUnits")value+=1;else value+=c.power;}}
            return value;
        }
        if(kind=="RowWithCeiling")return 0;
        for(i=0;i<ctx.rows.Size();i+=1)if(ctx.rows[i].side==item.side && ctx.rows[i].row==row){token=ctx.rows[i].token;break;}
        effect=1;if(EffectType=="Invalid")effect=0;else if(EffectType=="Boon")effect=2;else if(EffectType=="All")effect=3;
        boon=(token & 384)!=0;hazard=(token & 7807)!=0;
        if(boon && !hazard)tokenKind=2;else if(hazard && !boon)tokenKind=1;
        if(((effect & tokenKind)!=0)==!Negate)return 1;return 0;
    }
    public function Filter(ctx : CBetaOriginalHandlerContext, request : SBetaOriginalRequest) : SBetaOriginalFilter {
        var result, childResult : SBetaOriginalFilter;var items, pool, selected : array<SBetaOriginalItem>;
        var ranks : array<SBetaOriginalRank>;var rank : SBetaOriginalRank;
        var item, other : SBetaOriginalItem;var t : SBetaOriginalTemplate;
        var cards, high, keep, at, unconstrained, leftFound, rightFound : bool;
        var i,j,index,count,destination,power,value,maximum,leftIndex,rightIndex,mask,roundBit,minimum,limit : int;
        var scoreEntry : SBetaOriginalSummationEntry;
        result.valid=true;cards=request.kind=="targets" || request.kind=="choices" || request.kind=="templates";
        high=SortOrder=="Highest";items=BetaOriginalByPlayer(request.items,ctx.actor,PlayerType);
        if(kind=="Preference") {
            if(cards)items=BetaOriginalByTier(items,CardGroup);
            for(i=0;i<items.Size();i+=1){rank.item=items[i];rank.value=Preference(ctx,items[i],cards);ranks.PushBack(rank);}
            result.items=BetaOriginalSorted(ranks,high);return result;
        }
        if(kind=="Occurrence" || kind=="OccurrenceRange") {
            if(!cards) {
                for(i=0;i<items.Size();i+=1) {
                    count=0;for(j=0;j<ctx.cards.Size();j+=1)if(ctx.cards[j].side==items[i].side && ctx.cards[j].zone==items[i].row && (TemplateId==0 || ctx.cards[j].templateId==TemplateId))count+=1;
                    rank.item=items[i];rank.value=0.0f;if(FitsOccurrences(count))rank.value=(float)(count);ranks.PushBack(rank);
                }
                result.items=BetaOriginalSorted(ranks,high);return result;
            }
            if(request.kind=="targets")pool=BetaOriginalByTier(request.items,CardGroup);else pool=BetaOriginalByTier(items,CardGroup);
            if(TemplateId!=0){for(i=0;i<pool.Size();i+=1)if(pool[i].templateId==TemplateId)selected.PushBack(pool[i]);pool=selected;selected.Clear();}
            if(Destination=="Deck")destination=16;else if(Destination=="Hand")destination=8;else if(Destination=="Graveyard")destination=32;else if(Destination=="Board")destination=7;
            if(destination!=0){pool.Clear();for(i=0;i<ctx.cards.Size();i+=1)if((ctx.cards[i].zone & destination)!=0)pool.PushBack(ctx.cards[i]);}
            pool=BetaOriginalByPlayer(pool,ctx.actor,PlayerType);
            for(i=0;i<request.items.Size();i+=1){rank.item=request.items[i];rank.value=(float)(Occurrences(request.items[i],pool));ranks.PushBack(rank);}
            items=BetaOriginalSorted(ranks,high);
            for(i=0;i<items.Size();i+=1)if(FitsOccurrences(Occurrences(items[i],pool)))result.items.PushBack(items[i]);return result;
        }
        if(kind=="Wedge") {
            if(request.kind!="play"){result.valid=false;return result;}
            unconstrained=SemanticTagId<=1 && TemplateId==0 && CardGroup==15;maximum=(-2147483647-1);
            for(i=0;i<items.Size();i+=1) {
                item=items[i];leftIndex=item.index;if(WedgeType!="LeftOf" && WedgeType!="InBetween")leftIndex=item.index-1;
                leftFound=Neighbour(ctx,item,leftIndex,other);if(!leftFound || (!unconstrained && !WedgePasses(other)))continue;
                value=other.power;
                if(WedgeType=="InBetween"){rightFound=Neighbour(ctx,item,item.index-1,other);if(!rightFound || (!unconstrained && !WedgePasses(other)))continue;value+=other.power;}
                if(!high)value=-value;
                if(unconstrained){if(value<maximum)continue;if(value>maximum){ranks.Clear();maximum=value;}}
                rank.item=item;rank.value=(float)(value);ranks.PushBack(rank);
            }
            result.items=BetaOriginalSorted(ranks,true);return result;
        }
        if(kind=="PlayAll") {
            if(request.kind!="play" && request.minimum!=1 && request.maximum!=1){result.valid=false;return result;}
            result.items=items;return result;
        }
        if(kind=="Random") {
            if(request.kind=="play") {
                if(request.items.Size()==0){result.valid=false;return result;}
                result.items.PushBack(request.items[ctx.Next(0,request.items.Size())]);return result;
            }
            if(cards)items=BetaOriginalByTier(items,CardGroup);
            count=ctx.Next(request.minimum,request.maximum+1);
            while(result.items.Size()<count && items.Size()>0){index=ctx.Next(0,items.Size());result.items.PushBack(items[index]);items.Erase(index);}return result;
        }
        if(kind=="Power" || kind=="PowerRange") {
            if(cards)items=BetaOriginalByTier(items,CardGroup);
            if(request.kind=="play") {
                maximum=(-2147483647-1);
                for(i=0;i<items.Size();i+=1){power=RowPower(ctx,items[i],CardGroup);if(!high)power=-power;if(power>maximum)maximum=power;}
                for(i=0;i<items.Size();i+=1){power=RowPower(ctx,items[i],CardGroup);if(!high)power=-power;if(power==maximum)result.items.PushBack(items[i]);}return result;
            }
            for(i=0;i<items.Size();i+=1) {
                power=items[i].power;if(!cards)power=RowPower(ctx,items[i],15);
                if(kind=="PowerRange" && (power<MinRange || (MaxRange!=0 && power>MaxRange)))continue;
                rank.item=items[i];rank.value=(float)(power);ranks.PushBack(rank);
            }
            result.items=BetaOriginalSorted(ranks,high);return result;
        }
        if(kind=="RowWithNumberOfUnits" || kind=="RowWithUnitStrength" || kind=="RowWithEffect" || kind=="RowWithCeiling") {
            for(i=0;i<items.Size();i+=1){rank.item=items[i];rank.value=(float)(RowScore(ctx,items[i],cards));ranks.PushBack(rank);}
            // Source's Lowest sign and ascending sort cancel each other.
            result.items=BetaOriginalSorted(ranks,true);return result;
        }
        if(kind=="Summation") {
            if(!hasSheet){result.valid=false;return result;}
            for(i=0;i<request.items.Size();i+=1){rank.item=request.items[i];rank.value=0.0f;ranks.PushBack(rank);}
            roundBit=0;if(ctx.roundIndex==0)roundBit=1;else if(ctx.roundIndex==1)roundBit=2;else if(ctx.roundIndex==2)roundBit=4;
            for(j=0;j<children.Size();j+=1) {
                scoreEntry=entries[j];mask=scoreEntry.rounds;
                if(mask!=0 && mask!=7 && (ctx.roundIndex<0 || ctx.roundIndex>2)){ctx.failed=true;ctx.error="Invalid original summation round";return result;}
                if((mask & roundBit)==0)continue;childResult=children[j].Filter(ctx,request);if(ctx.failed)return result;if(!childResult.valid)continue;
                minimum=request.minimum;limit=request.maximum;if(request.kind=="play"){minimum=1;limit=1;}
                for(i=0;i<childResult.items.Size();i+=1) {
                    keep=false;
                    for(index=0;index<ranks.Size();index+=1)if(BetaOriginalSameItem(ranks[index].item,childResult.items[i],request.kind)) {
                        rank=ranks[index];rank.value+=Weight(scoreEntry,children[j],i,childResult.items.Size(),minimum,limit);ranks[index]=rank;keep=true;break;
                    }
                    if(!keep){ctx.failed=true;ctx.error="Original handler candidate outside request";return result;}
                }
                children[j].AddAll(ctx.node,childResult.items,request.kind);
            }
            result.items=BetaOriginalSorted(ranks,true);return result;
        }
        if(kind=="TemplateId") {
            if(!cards){result.valid=false;return result;}
            // Source accidentally discards the computed player filter.
            for(i=0;i<request.items.Size();i+=1)if((request.items[i].templateId==TemplateId)!=Negate)result.items.PushBack(request.items[i]);return result;
        }
        if(kind=="Location" && !cards) {
            for(i=0;i<items.Size();i+=1)if((items[i].row & Location)!=0)result.items.PushBack(items[i]);return result;
        }
        if(!cards){result.valid=false;return result;}
        items=BetaOriginalByTier(items,CardGroup);
        for(i=0;i<items.Size();i+=1) {
            item=items[i];t=BetaOriginalTemplate(item.templateId);keep=false;
            if(kind=="Semantic")keep=t.semanticTags.Contains(SemanticTagId)!=Negate;
            else if(kind=="HasTagsToken")keep=((item.tokens & TagsTokenType)!=0)!=Negate;
            else if(kind=="Location") {
                if(LocationAction=="IsAtLocation")keep=Location==767 || (item.zone & Location)!=0;
                else keep=(((t.placementOwn|t.placementEnemy) & 7 & Location)!=0);
            } else if(kind=="UnitOrEvent")keep=(item.typeMask & UnitOrEvent)!=0;
            else if(kind=="Health"){value=1;if(item.power<item.basePower)value=2;else if(item.power>item.basePower)value=4;keep=(value & Health)!=0;}
            else{ctx.failed=true;ctx.error="Original handler not ported: "+kind;result.valid=false;return result;}
            if(keep)result.items.PushBack(item);
        }
        return result;
    }
    public function Decision(ctx : CBetaOriginalHandlerContext, request : SBetaOriginalRequest) : SBetaOriginalDecision {
        var result : SBetaOriginalDecision;var filtered : SBetaOriginalFilter;var i,j : int;var contains, valid : bool;
        filtered=Filter(ctx,request);result.filteredValid=filtered.valid;result.filtered=filtered.items;if(ctx.failed)return result;
        if(filtered.valid)for(i=0;i<filtered.items.Size();i+=1) {
            contains=false;for(j=0;j<result.chosen.Size();j+=1)if(BetaOriginalSameItem(result.chosen[j],filtered.items[i],request.kind)){contains=true;break;}
            if(result.chosen.Size()<request.maximum && !contains)result.chosen.PushBack(filtered.items[i]);
        }
        valid=result.chosen.Size()>=request.minimum && result.chosen.Size()<=request.maximum;result.sourceFallback=!valid;
        if(!valid)for(i=0;i<request.items.Size();i+=1) {
            contains=false;for(j=0;j<result.chosen.Size();j+=1)if(BetaOriginalSameItem(result.chosen[j],request.items[i],request.kind)){contains=true;break;}
            if(!contains)result.chosen.PushBack(request.items[i]);if(result.chosen.Size()>=request.minimum)break;
        }
        if(valid){for(i=0;i<result.chosen.Size();i+=1)result.propagated+=Get(ctx.node,BetaOriginalItemKey(result.chosen[i],request.kind));Cleanup();}
        if(kind=="PlayAll" && filtered.valid)for(i=1;i<filtered.items.Size();i+=1)result.branches.PushBack(filtered.items[i]);return result;
    }
}
