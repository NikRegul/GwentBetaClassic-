"""Stage 104: original Beta 'attack' presentation (ACardAttack: one attacker, many targets).
Consecutive actions enqueued by the same source with the same operation/sign form one
attack; its frames of the same kind merge into one frame (final snapshot, count of targets).
Rule order is unchanged; presentation only. Fail-closed exact anchors, BOM/CRLF kept."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
D = ROOT / 'BetaGwent/development/scripts/game/betagwent'

def edit(path, pairs):
    raw = path.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
    t = raw.decode('utf-8-sig').replace('\r\n', '\n')
    for old, new in pairs:
        n = t.count(old)
        if n != 1: raise SystemExit(f'{path.name}: anchor matched {n}x: {old[:80]!r}')
        t = t.replace(old, new)
    out = t.replace('\n', '\r\n') if crlf else t
    path.write_bytes((b'\xef\xbb\xbf' if bom else b'') + out.encode('utf8'))
    print('edited', path.name, len(pairs))

edit(D / 'duelVisualFrame.ws', [(
"    public var audioKind : int;\n",
"    public var audioKind : int;\n    // Original Beta ACardAttack grouping: one attack, attackCount targets (presentation only).\n    public var attackId, attackCount : int;\n")])

edit(D / 'duelSession.ws', [
("    private var visualSourceId, visualTemplateId, visualSide, visualRow : int;\n",
 "    private var visualSourceId, visualTemplateId, visualSide, visualRow : int;\n    private var visualAttack : int;\n"),
("    public function RecordVisual(kind : int, targetId : int, caption : string, duration : int, optional audioType : int)\n    {\n        var frame : CBetaGwentDuelVisualFrame; var target : CBetaGwentDuelCard; var t : SBetaGwentCardSnapshot;\n        if (!recordVisuals || visualOverflow) return;\n",
 "    public function SetVisualAttack(id : int) : int { var previous : int; previous = visualAttack; visualAttack = id; return previous; }\n    public function RecordVisual(kind : int, targetId : int, caption : string, duration : int, optional audioType : int)\n    {\n        var frame, merged : CBetaGwentDuelVisualFrame; var target : CBetaGwentDuelCard; var t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;\n        if (!recordVisuals || visualOverflow) return;\n        // Same attack, same kind: the original applies all targets at once. Keep one\n        // frame (first cue, latest snapshot) instead of one frame per target.\n        if (visualAttack != 0 && visualFrames.Size() > 0)\n        {\n            merged = visualFrames[visualFrames.Size() - 1];\n            if (merged.attackId == visualAttack && merged.kind == kind)\n            {\n                frame = VisualSnapshot(); frame.kind = merged.kind; frame.targetId = merged.targetId; frame.audioKind = merged.audioKind;\n                frame.sourceId = merged.sourceId; frame.templateId = merged.templateId; frame.side = merged.side; frame.row = merged.row;\n                frame.targetTemplateId = merged.targetTemplateId; frame.targetPower = merged.targetPower; frame.targetSide = merged.targetSide; frame.targetZone = merged.targetZone;\n                frame.attackId = merged.attackId; frame.attackCount = merged.attackCount + 1; frame.duration = Max(merged.duration, duration);\n                d = BetaGwentDuelDefinition(merged.templateId);\n                if (d.header.templateId != 0) frame.status = d.title + \": целей \" + frame.attackCount; else frame.status = merged.status;\n                visualFrames[visualFrames.Size() - 1] = frame; return;\n            }\n        }\n"),
("        frame = VisualSnapshot(); frame.kind = kind; frame.targetId = targetId; frame.audioKind = audioType;\n",
 "        frame = VisualSnapshot(); frame.kind = kind; frame.targetId = targetId; frame.audioKind = audioType;\n        frame.attackId = visualAttack; frame.attackCount = 1;\n"),
])

edit(D / 'duelEffectRuntime.ws', [
("    private var operation, amount, allowedLocations : int;\n    private var ignoreArmor : bool;\n",
 "    private var operation, amount, allowedLocations : int;\n    private var ignoreArmor : bool;\n    private var attackId : int;\n    public function SetAttack(id : int) { attackId = id; }\n"),
("    protected function ApplyImpl() : bool\n    {\n        var old, next : SBetaGwentCardSnapshot;\n        old = target.Snapshot();\n",
 "    protected function ApplyImpl() : bool\n    {\n        var previous : int; var result : bool;\n        previous = runtime.BeginAttack(attackId); result = ApplyEffect(); runtime.EndAttack(previous);\n        return result;\n    }\n    private function ApplyEffect() : bool\n    {\n        var old, next : SBetaGwentCardSnapshot;\n        old = target.Snapshot();\n"),
("    private var beforeCount, appliedCount, afterCount, skippedCount : int;\n",
 "    private var beforeCount, appliedCount, afterCount, skippedCount : int;\n    // Attack grouping (original ACardAttack): consecutive enqueues, same source/op/sign.\n    private var attackSerial, attackKey : int; private var attackSource : CBetaGwentDuelCard; private var attackOpen : bool;\n    public function BeginAttack(id : int) : int { return game.SetVisualAttack(id); }\n    public function EndAttack(previous : int) { game.SetVisualAttack(previous); }\n"),
("        action = new CBetaGwentDuelEffectAction in this;\n        if (!action.Setup(this, card, kind, value, bypassArmor, context, source, locations) || !PushPrepared(action))\n",
 "        action = new CBetaGwentDuelEffectAction in this;\n        key = kind * 2; if (value < 0) key += 1;\n        if (!attackOpen || attackSource != source || attackKey != key) { attackSerial += 1; attackOpen = true; attackSource = source; attackKey = key; }\n        action.SetAttack(attackSerial);\n        if (!action.Setup(this, card, kind, value, bypassArmor, context, source, locations) || !PushPrepared(action))\n"),
("    public function Enqueue(card : CBetaGwentDuelCard, kind : int, value : int, bypassArmor : bool, optional source : CBetaGwentDuelCard, optional locations : int) : bool\n    {\n        var action : CBetaGwentDuelEffectAction;\n",
 "    public function Enqueue(card : CBetaGwentDuelCard, kind : int, value : int, bypassArmor : bool, optional source : CBetaGwentDuelCard, optional locations : int) : bool\n    {\n        var action : CBetaGwentDuelEffectAction; var key : int;\n"),
("        managed = (CBetaGwentManagedAction)action;\n",
 "        managed = (CBetaGwentManagedAction)action;\n        attackOpen = false;\n"),
])

edit(D / 'developmentBoardMenu.ws', [
("setVisualCue.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(frame.kind), FlashArgInt(frame.sourceId),",
 "setVisualCue.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(frame.kind + 256 * Min(255, Max(1, frame.attackCount))), FlashArgInt(frame.sourceId),"),
])
