"""Prepare 0.8.2 RC sources from accepted, immutable platform snapshots."""
from pathlib import Path
import difflib, hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'BetaGwent/build/release082-rc1'
BASE = ROOT / 'BetaGwent/build'
sys.path.insert(0, str(ROOT / 'tools/classic132'))
from prepare_scripts import prepare

def read(p):
    raw = p.read_bytes()
    return raw.decode('utf16' if raw.startswith(b'\xff\xfe') else 'utf-8-sig').replace('\r\n', '\n')

def write(p, s):
    p.write_bytes(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def replace(s, old, new):
    assert s.count(old) == 1, old[:160]
    return s.replace(old, new)

def port(old, new, seed):
    a, b = old.splitlines(True), new.splitlines(True)
    for group in difflib.SequenceMatcher(None, a, b, autojunk=False).get_grouped_opcodes(3):
        seed = replace(seed, ''.join(a[group[0][1]:group[-1][2]]), ''.join(b[group[0][3]:group[-1][4]]))
    return seed

def patch_script(name, s):
    if name == 'duelVisualFrame.ws':
        s = replace(s, '    public var weatherTokens, weatherDamage : array<int>;',
                    '    public var destinationIds, destinationSides, destinationZones : array<int>;\n    public var weatherTokens, weatherDamage : array<int>;')
        s = replace(s, '    // 15 existing deck summon,16 created token,17 round cleanup (no Killed abilities).',
                    '    // 15 existing deck summon,16 created token,17 round cleanup (no Killed abilities).\n    // 19 resolved special entering its real graveyard (presentation only).')
    elif name == 'duelClone.ws':
        s = replace(s, '        dst.weatherTokens = src.weatherTokens;',
                    '        dst.destinationIds = src.destinationIds;\n        dst.destinationSides = src.destinationSides;\n        dst.destinationZones = src.destinationZones;\n        for (i = 0; i < dst.destinationSides.Size(); i += 1) dst.destinationSides[i] = Seat(src.destinationSides[i]);\n        dst.weatherTokens = src.weatherTokens;')
    elif name == 'duelSession.ws':
        s = replace(s, '            if (v.card.locationMask == 8 && side == 2) frame.enemyHand += 1;',
                    '            // Public destinations only: never expose hidden hand/deck identities.\n            if (v.card.locationMask == 32 || v.card.locationMask == 512)\n            { frame.destinationIds.PushBack(v.card.instanceId); frame.destinationSides.PushBack(side); frame.destinationZones.PushBack(v.card.locationMask); }\n            if (v.card.locationMask == 8 && side == 2) frame.enemyHand += 1;')
        s = replace(s, 'if (kind != 11 && visualAttack != 0', 'if (kind != 11 && kind != 19 && visualAttack != 0')
        s = replace(s, '            else card.Move(s.positionPlayerId,32,CountLocation(s.positionPlayerId,32));',
                    '            else\n            {\n                card.Move(s.positionPlayerId,32,CountLocation(s.positionPlayerId,32));\n                RecordVisual(19,s.instanceId,"",440);\n            }')
    elif name == 'developmentBoardMenu.ws':
        s = replace(s, '    private var pushCard : CScriptedFlashFunction;', '    private var pushCard : CScriptedFlashFunction;\n    private var pushDestination : CScriptedFlashFunction;')
        s = replace(s, '        pushCard = GetMenuFlash().GetMemberFlashFunction("pushBoardCard");',
                    '        pushCard = GetMenuFlash().GetMemberFlashFunction("pushBoardCard");\n        pushDestination = GetMenuFlash().GetMemberFlashFunction("pushCardDestination");')
        s = replace(s, '|| !pushCard ||', '|| !pushCard || !pushDestination ||')
        anchor = '        snapshot = frame.matchState; flags = frame.flags;'
        # Header must precede destination publishing, because it allocates the receiving frame.
        start = s.index(anchor)
        end = s.index('        entries = frame.cards;', start)
        s = s[:end] + '        for (i = 0; i < frame.destinationIds.Size(); i += 1)\n            pushDestination.InvokeSelfThreeArgs(FlashArgInt(frame.destinationIds[i]), FlashArgInt(frame.destinationSides[i]), FlashArgInt(frame.destinationZones[i]));\n' + s[end:]
    return s

def patch_ui(s):
    s = s.replace('if(!ready||nameOpen||!selectingDecks||!importing&&!editingDeck)return;',
                  'if(!ready||nameOpen||!(selectingDecks||editingDeck)||(!importing&&!editingDeck))return;')
    s = replace(s, '        public function setVisualTarget(',
        '        private var cardDestinations082:Object={};\n        public function pushCardDestination(id:int,side:int,zone:int):void\n        { if(incoming&&(zone==32||zone==512))incoming.destinations[id]={side:side,zone:zone}; }\n        public function setVisualTarget(')
    s = replace(s, 'cards:[],requestCards:[]', 'cards:[],destinations:{},requestCards:[]')
    s = replace(s, 'message=frame.message;cards=frame.cards;', 'message=frame.message;cards=frame.cards;cardDestinations082=frame.destinations||{};')
    s = replace(s, 'if((int(previous.tokens)&512)!=0||banishCueTarget(activeCue,int(oldId)))',
        'if((int(previous.tokens)&512)!=0||banishCueTarget(activeCue,int(oldId))||(cardDestinations082[oldId]&&int(cardDestinations082[oldId].zone)==512))')
    s = replace(s, '                var fading:Sprite=panel(content,previous.x,previous.y,previous.width,previous.height,0x171714,.9);',
        '                var destination082:Object=cardDestinations082[oldId];\n                var grave082:Boolean=destination082&&int(destination082.zone)==32;\n                var pile082:Array=grave082?(skin==3?betaPilePoint(int(destination082.side),true):[260,int(destination082.side)==1?748:398]):[previous.x,previous.y];\n                var fading:Sprite=panel(content,previous.x,previous.y,previous.width,previous.height,0x171714,.9);')
    s = replace(s, 'toX:260,toY:previous.side==1?748:398,', 'toX:pile082[0],toY:pile082[1],')
    s = replace(s, 'toScaleX:0.25,toScaleY:0.25});', 'toScaleX:grave082?80/previous.width:1,toScaleY:grave082?110/previous.height:1});')
    s = replace(s, 'case 17:return 750;case 18:return 620;', 'case 17:return 750;case 18:return 620;case 19:return 440;')
    s = replace(s, '            var origin:Object=displayedCards[activeCue.source];',
        '            if(activeCue.kind==19){drawResolvedSpecial082(fx);return;}\n            var origin:Object=displayedCards[activeCue.source];')
    marker = '        private function drawVisualCue():void'
    helper = '''        private function drawResolvedSpecial082(fx:Sprite):void
        {
            var view:Object=activeCue.targetView;
            var destination:Object=cardDestinations082[activeCue.target];
            if(!view||!destination||int(destination.zone)!=32)return;
            var point:Array=skin==3?betaPilePoint(int(destination.side),true):[260,int(destination.side)==1?748:398];
            var face:Sprite=new Sprite();fx.addChild(face);face.mouseEnabled=false;face.mouseChildren=false;
            paintPlacementCard(face,view,136,204);face.x=892;face.y=322;
            animations.push({sprite:face,fromX:892,fromY:322,toX:point[0],toY:point[1],
                fromScaleX:1,fromScaleY:1,toScaleX:80/136,toScaleY:110/204,
                fade:true,remove:true,duration:400,arc:28,delay:0});
        }
'''
    return replace(s, marker, helper + marker)

def main():
    assert not (OUT/'classic-prepared').exists(), 'Keep completed builds immutable'
    OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(BASE/'features082/candidate/scripts', OUT/'scripts',dirs_exist_ok=True)
    names = ['duelVisualFrame.ws','duelClone.ws','duelSession.ws','developmentBoardMenu.ws']
    for name in names:
        for folder in [OUT/'scripts/game/betagwent', ROOT/'BetaGwent/development/scripts/game/betagwent']:
            p=folder/name;s=read(p)
            marker={'duelVisualFrame.ws':'destinationIds','duelClone.ws':'dst.destinationIds','duelSession.ws':'frame.destinationIds','developmentBoardMenu.ws':'pushDestination'}[name]
            if marker not in s:write(p,patch_script(name,s))
    for platform, seed in [('nextgen',BASE/'features082/candidate/ui'),('classic',BASE/'classic081-effect-routes-fix18/ui')]:
        dest=OUT/platform/'ui';shutil.copytree(seed,dest,dirs_exist_ok=True)
        p=dest/'src/BetaGwentBoard.as';s=read(p)
        if platform=='classic':
            old=read(BASE/'universal081/ui/src/BetaGwentBoard.as')
            new=read(BASE/'features082/candidate/ui/src/BetaGwentBoard.as').replace('textChoiceLabel(),56,24,364,42','textChoiceLabel(),52,28,276,42').replace('voiceChoiceLabel(),56,78,364,42','voiceChoiceLabel(),340,28,276,42')
            s=port(old,new,s)
        write(p,patch_ui(s))
        for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            shutil.copy2(p,dest/mirror/p.name)
        manifest=json.loads((BASE/'universal081/ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:sha(p) for p in (dest/'src').glob('*.as')}
        (OUT/platform/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    # Canonical interface mirrors retain their own accepted geometry and renderer.
    canonical=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as';write(canonical,patch_ui(read(canonical)))
    for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        shutil.copy2(canonical,canonical.parent.parent/mirror/canonical.name)
    previous=BASE/'features082/candidate/classic-audit'
    audit=json.loads((previous/'audit.json').read_text('utf8'))
    audit['sourceScripts']={p.relative_to(OUT/'scripts').as_posix():sha(p) for p in (OUT/'scripts').rglob('*.ws')}
    audit['sourceScriptCount']=len(audit['sourceScripts']);audit['sourceValidationPassed']=False
    folder=OUT/'classic-audit';shutil.copytree(previous/'baseline/vanilla-targets',folder/'baseline/vanilla-targets')
    shutil.copytree(OUT/'scripts',folder/'baseline/scripts')
    (folder/'audit.json').write_text(json.dumps(audit,indent=2),'utf8')
    prepare(folder,OUT/'classic-prepared')
    shutil.copy2(BASE/'classic081-effect-routes-fix18/subimages.json',OUT/'classic/subimages.json')
    print(OUT)

if __name__=='__main__':main()
