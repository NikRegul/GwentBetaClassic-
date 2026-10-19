    private function AiRowTicks(actor : int) : int
    { return AiWeatherTicks(actor); }
    private function AiHazardMoveValue(actor : int, side : int, fromRow : int, toRow : int) : int
    {
        var token,ticks,value : int;if(fromRow==toRow)return -2147483647;
        token=weather.Token(side,fromRow);if(!MonsterIsHazard(token))return -2147483647;
        ticks=AiRowTicks(actor);
        value=weather.ForecastTokenLoss(side,toRow,token,ticks)-weather.ForecastTokenLoss(side,toRow,weather.Token(side,toRow),ticks)
            -weather.ForecastTokenLoss(side,fromRow,token,ticks);
        if(side==actor)value=-value;return value;
    }
    private function AiRowAbilityValue(source : CBetaGwentDuelCard, side : int, row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s,t : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var actor,id,i,j,total,highest,value,ticks,next,best,loss,destinations,penalty : int;
        d=source.Definition();actor=NorthActingSide(source);id=source.TemplateId();ticks=AiRowTicks(actor);
        GetZoneCards(side,row,cards);
        if(id==112102){
            if(side==actor)return -2147483647;
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.isWaitingToDie || (t.tokenMask&8)!=0)continue;total+=t.power.currentPower;highest=Max(highest,t.power.currentPower);}
            if(total<25)return 0;
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(!t.isWaitingToDie && (t.tokenMask&8)==0 && t.power.currentPower==highest)value+=AiDamageChoice(t,actor,t.power.currentPower+t.power.armor);}
            return value;
        }
        if(id==201523){
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.isWaitingToDie || (t.tokenMask&8)!=0)continue;
                // NeutralReset keeps permanent power and clears lock/resilience/spying.
                loss=t.power.basePower+t.power.permanentPower-t.power.currentPower;
                if((t.tokenMask&4)!=0){s=t;s.tokenMask=s.tokenMask&-5;loss+=AiEngineValue(s,actor);}
                if((t.tokenMask&1)!=0 && match.roundNumber<3)loss-=Max(0,t.power.basePower)/2;
                if(side!=actor)loss=-loss;value+=loss;
            }return value;
        }
        if(side==actor && id!=200089)return -2147483647;
        if(id==152105){
            if(weather.Token(side,row)==64)return 0;
            return weather.ForecastTokenLoss(side,row,64,ticks)-weather.ForecastTokenLoss(side,row,weather.Token(side,row),ticks);
        }
        if(id==162302 || id==142304){
            if(CountLocation(side,row)>=9)return -2147483647;
            if(id==162302){
                highest=2147483647;for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.isWaitingToDie || (t.tokenMask&264)!=0)continue;highest=Min(highest,t.power.currentPower);}
                for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(!t.isWaitingToDie && (t.tokenMask&264)==0 && t.power.currentPower==highest)value+=AiDamageChoice(t,actor,t.power.currentPower+t.power.armor);}
            }else for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(!t.isWaitingToDie && (t.tokenMask&8)==0)value+=AiDamageChoice(t,actor,3);}
            if(ticks==0)return -1;return value-1;
        }
        if(id==201700){
            if(source.monsterStage>0)return AiHazardMoveValue(actor,side,source.monsterStored,row);
            best=-2147483647;for(next=1;next<=4;next*=2)if(next!=row)best=Max(best,AiHazardMoveValue(actor,side,row,next));return best;
        }
        if(id==200089){
            // Evacuating an enemy weather row gives away its future damage.
            loss=weather.ForecastTokenLoss(side,row,weather.Token(side,row),ticks);destinations=0;
            for(next=1;next<=4;next*=2)if(next!=row && CountLocation(side,next)<9){destinations+=1;penalty+=weather.Damage(side,next)*Min(3,CountLocation(side,row));}
            if(destinations==0)return 0;value=penalty*ticks/(10*destinations)-loss;if(side==actor)value=-value;return value;
        }
        return CountLocation(side,row);
    }
