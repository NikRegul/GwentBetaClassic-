"""Prepare the bounded native counterplay port; apply only after Stage112 freezes."""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[2]
DEV=ROOT/'BetaGwent/development/scripts/game/betagwent'
DRAFT=ROOT/'BetaGwent/build/stage113/draft'

def replace_once(code,old,new):
    if code.count(old)!=1: raise ValueError('Expected one integration point: '+old[:90])
    return code.replace(old,new,1)

def main():
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');args=p.parse_args()
    src=(DEV/'duelSession.ws').read_text('utf-8-sig')
    if 'public function AiReverseClone()' in src:raise ValueError('Stage113 already applied')
    new='''    // Disposable shadow seat: run the same side-2 rules as a plausible player reply.
    public function AiReverseClone() : CBetaGwentDuelSession
    {
        var cloner : CBetaGwentCloner; var g : CBetaGwentDuelSession;
        if(!aiSimulating)return NULL;
        aiCloneEpoch+=1;cloner=new CBetaGwentCloner in this;
        g=cloner.CloneSession(this,aiCloneEpoch,true);if(!g)return NULL;
        g.aiSimCloner=cloner;g.recordVisuals=false;g.aiSimulating=true;
        g.weatherAI.Initialize(g);g.weatherProfile=g.weatherAI.Matches(g.nilfInitialTwo);
        g.archetypeAI.Initialize(g,g.nilfInitialTwo,g.presetTwo,g.leaderTemplateTwo);
        return g;
    }
    public function AiCounterRisk(card : CBetaGwentDuelCard, model : CBetaGwentPublicResponseAI) : int
    {
        var g,h : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot;var result,first : int;
        if(aiSimulating || !card || !model)return 0;
        BetaGwentAISimEnter();g=AiSimClone();s=card.Snapshot();
        if(g){first=g.AiSimPlay(s.instanceId);if(first!=-2147483647){h=model.Apply(g);result=model.penalty;}}
        BetaGwentAISimLeave();return result;
    }
'''
    src=replace_once(src,'private function Leader(side : int)','public function Leader(side : int)')
    src=replace_once(src,'    public var aiLastStrategicValue : int;',new+'    public var aiLastStrategicValue : int;')
    src=replace_once(src,'g.aiSimCloner = cloner;g.nilfInitialOne.Clear();','g.aiSimCloner = cloner;g.nilfInitialOne.Clear();g.presetOne=0;')
    src=replace_once(src,'public function AiSequenceUplift(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>)','public function AiSequenceUplift(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>, optional model : CBetaGwentPublicResponseAI)')
    src=replace_once(src,'BetaGwentAISimEnter(); result = AiSequenceUpliftInner(card, ids, values); BetaGwentAISimLeave();',
        '''BetaGwentAISimEnter(); result = AiSequenceUpliftInner(card, ids, values, model); BetaGwentAISimLeave();
        if(model)BetaGwentLog("DUEL_AI_RESPONSE card="+card.TemplateId()+" profiles="+model.eligibleProfiles+" replies="+model.evaluated+" rejected="+model.rejected+" risk="+model.penalty+" uplift="+result);''')
    src=replace_once(src,'private function AiSequenceUpliftInner(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>)','private function AiSequenceUpliftInner(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>, model : CBetaGwentPublicResponseAI)')
    src=replace_once(src,'var i, best, after, first : int;','var i, best, after, first, risk, followLimit : int;')
    src=replace_once(src,'var s : SBetaGwentCardSnapshot; var i, best, after, first, risk, followLimit : int;',
        'var s : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; var i, best, after, first, risk, followLimit : int;')
    src=replace_once(src,'''        if (!g.AiSimSkipTurn()) return 0;
        for (i = 0; i < ids.Size() && i < BetaGwentAITune(7); i += 1)''','''        followLimit=BetaGwentAITune(7);
        if(model){h=model.Apply(g);risk=model.penalty;followLimit=Min(3,followLimit);if(h)g=h;}
        m=g.match.Snapshot();
        if(m.currentPlayerId==1 && !g.AiSimSkipTurn())return -risk;
        m=g.match.Snapshot();if(m.currentPlayerId!=2 || !m.turnActive)return -risk;
        for (i = 0; i < ids.Size() && i < followLimit; i += 1)''')
    src=replace_once(src,'return best / 2; // Public counterplay risk: setup is not guaranteed to survive.','return best / 2 - risk; // Risk affects ordering only, never catch-up points.')
    src=replace_once(src,'var leaderCard : CBetaGwentDuelCard;','var leaderCard : CBetaGwentDuelCard;var publicResponses : CBetaGwentPublicResponseAI;')
    src=replace_once(src,'        // Generation 3: simulate the most promising plays on a cloned session',
        '''        if(BetaGwentAIStrength()>=4 && !m.playerOne.hasPassed && aiSimDamp<50){
            publicResponses=new CBetaGwentPublicResponseAI in this;
            publicResponses.Initialize(this,3-aiSimDamp/25);
        }
        // Generation 3: simulate the most promising plays on a cloned session''')
    src=replace_once(src,'AiSequenceUplift(live[simIds[j]],exactIds,exactValues)','AiSequenceUplift(live[simIds[j]],exactIds,exactValues,publicResponses)')
    src=replace_once(src,'            cost = BetaGwentAILeaderReserve(m.roundNumber);','''            if(publicResponses && leaderExact!=-2147483647)value-=AiCounterRisk(leaderCard,publicResponses);
            cost = BetaGwentAILeaderReserve(m.roundNumber);''')
    DRAFT.mkdir(parents=True,exist_ok=True);(DRAFT/'duelSession.ws').write_text('\ufeff'+src,'utf8')
    if args.apply:
        for name in ('duelSession.ws','duelPublicResponseAI.ws'):(DEV/name).write_bytes((DRAFT/name).read_bytes())
        path=ROOT/'tools/ai/build_js.py';code=path.read_text('utf8')
        if "'duelPublicResponseAI'" not in code:code=replace_once(code,"NAMES = ['duelClone',","NAMES = ['duelClone','duelPublicResponseAI',")
        path.write_text(code,'utf8')
    print('Stage113', 'applied' if args.apply else 'prepared without changing game sources')
if __name__=='__main__':main()
