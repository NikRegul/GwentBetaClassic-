    // Read-only, bounded forecast. No live cards, queues or RNG are changed.
    // Each weather tick sees the surviving physical order from the last tick.
    private function ForecastHit(out cards : array<SBetaGwentCardSnapshot>, index : int, amount : int)
    {
        var s : SBetaGwentCardSnapshot; var absorbed, oldArmor : int;
        s=cards[index];if(s.power.currentPower<=0 || (s.tokenMask&8)!=0)return;
        oldArmor=s.power.armor;absorbed=Min(oldArmor,amount);s.power.armor-=absorbed;
        s.power.currentPower=Max(0,s.power.currentPower-amount+absorbed);
        if(oldArmor>0 && s.power.armor==0 && s.runtimeTemplate.templateId==122317 && (s.tokenMask&4)==0 && s.power.currentPower>0)s.power.currentPower+=5;
        cards[index]=s;
    }
    private function ForecastTurnEnd(out cards : array<SBetaGwentCardSnapshot>)
    {
        var i,j : int;var s,t : SBetaGwentCardSnapshot;
        for(i=0;i<cards.Size();i+=1){s=cards[i];if(s.power.currentPower<=0 || (s.tokenMask&12)!=0)continue;
            if(s.runtimeTemplate.templateId==122308 && s.power.armor==0){s.power.currentPower+=2;s.power.armor=2;cards[i]=s;}
            if(s.runtimeTemplate.templateId==123301 && s.power.armor>0){
                for(j=i-1;j>=0;j-=1){t=cards[j];if(t.power.currentPower<=0)continue;t.power.currentPower+=1;cards[j]=t;break;}
                for(j=i+1;j<cards.Size();j+=1){t=cards[j];if(t.power.currentPower<=0)continue;t.power.currentPower+=1;cards[j]=t;break;}
            }
        }
    }
    private function ForecastScore(cards : array<SBetaGwentCardSnapshot>) : int
    { var i,total : int;for(i=0;i<cards.Size();i+=1)if((cards[i].tokenMask&8)==0)total+=Max(0,cards[i].power.currentPower);return total; }
    private function ForecastRowScore(side : int, row : int, token : int, ticks : int) : int
    {
        var live : array<CBetaGwentDuelCard>;var cards : array<SBetaGwentCardSnapshot>;
        var i,k,n,remaining,weight,previous,current,total,extreme,picked,amount : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        game.GetZoneCards(side,row,live);for(i=0;i<live.Size();i+=1)cards.PushBack(live[i].Snapshot());
        m=game.Snapshot();previous=ForecastScore(cards);total=previous*10;remaining=Min(60,Max(0,ticks));
        while(remaining>0){
            if(k>0 || (m.currentPlayerId==side && m.turnActive))ForecastTurnEnd(cards);
            weight=Min(10,remaining);remaining-=weight;k+=1;
            if(token==64){
                n=0;for(i=0;i<cards.Size() && n<3;i+=1){s=cards[i];if(s.power.currentPower<=0)continue;
                    amount=1;if(n==0)amount=2;n+=1;ForecastHit(cards,i,amount);}
            }else if(token==1 || token==2 || token==16 || token==32){
                picked=-1;extreme=2147483647;if(token==2 || token==32)extreme=-2147483647;
                for(i=0;i<cards.Size();i+=1){s=cards[i];if(s.power.currentPower<=0 || (s.tokenMask&8)!=0)continue;
                    if(((token==1 || token==16) && s.power.currentPower<extreme) || ((token==2 || token==32) && s.power.currentPower>extreme)){extreme=s.power.currentPower;picked=i;}}
                if(picked>=0)ForecastHit(cards,picked,DamageFor(side,row,token));
            }else if(token==4){
                // Expected rain pressure; deterministic target order is a bounded approximation.
                n=0;for(i=0;i<cards.Size() && n<2;i+=1){s=cards[i];if(s.power.currentPower<=0 || (s.tokenMask&8)!=0)continue;n+=1;ForecastHit(cards,i,DamageFor(side,row,token));}
            }
            current=ForecastScore(cards);total+=(current-previous)*weight;previous=current;
        }
        return total/10;
    }
    public function ForecastTokenLoss(side : int, row : int, token : int, ticks : int) : int
    {
        if(ticks<=0 || token==0)return 0;
        if(token==1 || token==2 || token==4 || token==16 || token==32 || token==64)
            return ForecastRowScore(side,row,0,ticks)-ForecastRowScore(side,row,token,ticks);
        return 0;
    }
