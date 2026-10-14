"""Apply the focused 14 October playtest fixes, preserving source encodings."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEV=ROOT/'BetaGwent/development/scripts/game/betagwent'

def edit(path,old,new):
    raw=path.read_bytes(); text=raw.decode('utf-8-sig').replace('\r\n','\n')
    if text.count(old)!=1: raise RuntimeError(f'{path}: anchor count {text.count(old)}')
    text=text.replace(old,new)
    path.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+text.replace('\n','\r\n').encode('utf8'))

# Every play/summon cue is authoritative. A pending-choice snapshot may already
# contain the placed card; that must not suppress its later landing overlay.
for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']:
    edit(ROOT/'BetaGwent/ui'/folder/'BetaGwentBoard.as',
        '            var old:Object=previousPoses[activeCue.kind==1?activeCue.source:activeCue.target];\n            if((activeCue.kind==1||activeCue.kind==15||activeCue.kind==16)&&definition&&definition.tier==8&&!definition.leader&&(!old||(int(old.zone)&7)==0))drawPresentation178(fx,"GoldLanding",pose,arrival,100);',
        '            // A choice snapshot may already show the unit on the board.\n            // The play/summon cue, rather than its previous zone, owns landing.\n            if((activeCue.kind==1||activeCue.kind==15||activeCue.kind==16)&&definition&&definition.tier==8&&!definition.leader)drawPresentation178(fx,"GoldLanding",pose,arrival,100);')

edit(DEV/'duelSession.ws',
    '        if(s.runtimeTemplate.templateId!=122206)return 0;',
    '''        // Undvik's deathwish boosts every living opposing Hjalmar by ten.
        // This is immediate resolved power, including after the enemy passed.
        if(s.runtimeTemplate.templateId==152401){
            beneficiary=BetaGwentOpponentId(s.positionPlayerId);
            for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                if(t.positionPlayerId==beneficiary && t.runtimeTemplate.templateId==152101
                    && (t.locationMask&7)!=0 && !t.isWaitingToDie)value+=10;}
            if(beneficiary!=side)value=-value;return value;
        }
        if(s.runtimeTemplate.templateId!=122206)return 0;''')
edit(DEV/'duelSession.ws',
    '            reason=BetaGwentAIChasePassReason(plan.reachable,plan.cards,spent,ownHand,enemyHand,m.playerTwo.crowns,m.playerOne.crowns);',
    '''            // A leader plus a hand card is a two-action investment in an
            // optional round. A lone free leader still costs no hand card.
            cost=plan.cards;if(m.playerOne.crowns==0 && plan.actions>1)cost=Max(cost,plan.actions);
            reason=BetaGwentAIChasePassReason(plan.reachable,cost,spent,ownHand,enemyHand,m.playerTwo.crowns,m.playerOne.crowns);''')

# GoldLanding already exists in every bank. Dispatch it in addition to each
# unit's own ability SFX; leaders keep their existing entrance behavior.
edit(DEV/'duelAudio.ws',
    '    public function Cue(kind : int, templateId : int, flags : int, ownScore : int, enemyScore : int, rowToken : int, targetTokens : int)',
    '    public function Cue(kind : int, templateId : int, flags : int, ownScore : int, enemyScore : int, rowToken : int, targetTokens : int, optional landingTemplate : int)')
edit(DEV/'duelAudio.ws',
    '        var eventName : string; var now : float; var voiceTrigger, cueKind : int;',
    '        var eventName, landingEvent : string; var now : float; var voiceTrigger, cueKind : int;var landing : SBetaGwentDuelDefinition;')
edit(DEV/'duelAudio.ws',
    '        cueKind = kind;\n        if (BetaReady())',
    '''        cueKind = kind;
        if(BetaReady() && (kind==1 || kind==15 || kind==16)){
            if(landingTemplate==0 && kind==1)landingTemplate=templateId;
            landing=BetaGwentDuelDefinition(landingTemplate);
            if(landing.header.typeMask==4 && landing.header.tierMask==8 && !BetaGwentAudioIsLeader(landingTemplate)){
                landingEvent=BetaGwentAudioCue(28);if(landingEvent!="")theSound.SoundEvent(landingEvent);
            }
        }
        if (BetaReady())''')
edit(DEV/'developmentBoardMenu.ws',
    '        var i, kind, id, j, token, targetTokens, rowIndex : int; var frame : CBetaGwentDuelVisualFrame; var s : SBetaGwentCardSnapshot;',
    '        var i, kind, id, j, token, targetTokens, rowIndex, landingTemplate : int; var frame : CBetaGwentDuelVisualFrame; var s : SBetaGwentCardSnapshot;')
edit(DEV/'developmentBoardMenu.ws',
    '                if (s.instanceId == frame.targetId) targetTokens = s.tokenMask;',
    '''                if (s.instanceId == frame.targetId) targetTokens = s.tokenMask;
                if((s.locationMask&7)!=0 && (s.tokenMask&8)==0
                    && (frame.kind==1 && s.instanceId==frame.sourceId
                        || (frame.kind==15 || frame.kind==16) && s.instanceId==frame.targetId))landingTemplate=s.runtimeTemplate.templateId;''')
edit(DEV/'developmentBoardMenu.ws',
    '            audio.Cue(kind, id, frame.flags, frame.scoreOne, frame.scoreTwo, token, targetTokens); return true;',
    '            audio.Cue(kind, id, frame.flags, frame.scoreOne, frame.scoreTwo, token, targetTokens, landingTemplate); return true;')

# The audio bridge owns the exact landing card. Keep the audio class independent
# of the gameplay catalog so voices and bank fallback remain independently testable.
edit(DEV/'duelAudio.ws','optional landingTemplate : int)','optional goldLanding : bool)')
edit(DEV/'duelAudio.ws','var landing : SBetaGwentDuelDefinition;','')
edit(DEV/'duelAudio.ws',
    '''        if(BetaReady() && (kind==1 || kind==15 || kind==16)){
            if(landingTemplate==0 && kind==1)landingTemplate=templateId;
            landing=BetaGwentDuelDefinition(landingTemplate);
            if(landing.header.typeMask==4 && landing.header.tierMask==8 && !BetaGwentAudioIsLeader(landingTemplate)){
                landingEvent=BetaGwentAudioCue(28);if(landingEvent!="")theSound.SoundEvent(landingEvent);
            }
        }''',
    '''        if(BetaReady() && goldLanding && (kind==1 || kind==15 || kind==16)){
            landingEvent=BetaGwentAudioCue(28);if(landingEvent!="")theSound.SoundEvent(landingEvent);
        }''')
edit(DEV/'duelAudio.ws','nextEffect = now + 0.10f; theSound.SoundEvent(eventName);','nextEffect = now + 0.10f; if(eventName!=landingEvent)theSound.SoundEvent(eventName);')
edit(DEV/'developmentBoardMenu.ws',
    'var s : SBetaGwentCardSnapshot;\n        if (!configured || !audio) return false;',
    'var s : SBetaGwentCardSnapshot;var landing : SBetaGwentDuelDefinition;var goldLanding : bool;\n        if (!configured || !audio) return false;')
edit(DEV/'developmentBoardMenu.ws',
    '            audio.Cue(kind, id, frame.flags, frame.scoreOne, frame.scoreTwo, token, targetTokens, landingTemplate); return true;',
    '''            landing=BetaGwentDuelDefinition(landingTemplate);
            goldLanding=landing.header.typeMask==4 && landing.header.tierMask==8 && !BetaGwentAudioIsLeader(landingTemplate);
            audio.Cue(kind, id, frame.flags, frame.scoreOne, frame.scoreTwo, token, targetTokens, goldLanding); return true;''')
edit(DEV/'developmentBoardMenu.ws',
    'else audio.Cue(kind,id,0,0,0,token,0);',
    'else audio.Cue(kind,id,0,0,0,token,0,definition.header.typeMask==4 && definition.header.tierMask==8 && !BetaGwentAudioIsLeader(id));')

if __name__=='__main__':print('Applied playtest188 fixes')
