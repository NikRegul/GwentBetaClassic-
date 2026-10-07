// Self-play ranking policy. Neutral until an accepted training export is copied here.
// Never contributes to actual points or the post-pass catch-up planner.
function BetaGwentAITrainingFeature(index : int, d : SBetaGwentDuelDefinition, round : int, hand : int,
    advantage : int, tempo : int, forecast : int, reserve : int, setup : int) : int
{
    switch(index) {
    case 0: return Min(8,Max(0,tempo)/3);
    case 1: return Min(8,Max(-8,(forecast-tempo)/3));
    case 2: return Min(8,Max(0,reserve));
    case 3: return Min(8,Max(-8,setup));
    case 4: if(d.header.tierMask==8 && round<3)return 3;return 0;
    case 5: if(d.header.tierMask==4 && round<3)return 2;return 0;
    case 6: if(d.header.typeMask==2)return 2;return 0;
    case 7: if(BetaGwentDuelIsLeader(d.header.templateId))return 3;return 0;
    case 8: if(hand<=3 && d.header.tierMask==8)return 3;return 0;
    case 9: if(d.weatherToken!=0 && hand>=4)return 3;return 0;
    case 10: if(d.deploySummonTemplate!=0)return 3;return 0;
    case 11: if(BetaGwentDuelSpying(d.header.templateId))return 3;return 0;
    case 12: if(d.passiveBoost!=0 || d.consumePassiveBoost!=0 || d.initialTimer!=0)return Min(4,hand);return 0;
    case 13: if(d.deathwishDamage!=0 || d.deathwishSpawnTemplate!=0 || d.deathwishSummonTemplate!=0)return Min(3,hand);return 0;
    case 14: if(advantage<-10)return Min(8,Max(0,tempo)/3);return 0;
    case 15: if(round>=3)return Min(8,Max(0,tempo)/3);return 0;
    }
    return 0;
}
function BetaGwentAITrainingBias(preset : int, d : SBetaGwentDuelDefinition, round : int, hand : int,
    advantage : int, enemyPassed : bool, tempo : int, forecast : int, reserve : int, setup : int) : int
{
    var index, score : int;
    if(enemyPassed)return 0;
    for(index=0;index<16;index+=1)score+=BetaGwentAITrainingWeight(preset,index)*BetaGwentAITrainingFeature(index,d,round,hand,advantage,tempo,forecast,reserve,setup);
    return Min(120,Max(-120,score));
}
// EXPORT_WEIGHTS_BEGIN: learned constants; rules hash 95e1cc0d03639c7afec717464a7c59d9effc8660647f5da61ced77bed31a11d1
// candidate-7; offline self-play; native acceptance pending.
function BetaGwentAITrainingWeight(preset : int, index : int) : int {
    switch(preset) {
    case 61:
        switch(index) {
        case 2: return -2;
        case 5: return -2;
        case 7: return 2;
        case 9: return -2;
        default: return 0;
        }
        return 0;
    default: return 0;
    }
    return 0;
}
