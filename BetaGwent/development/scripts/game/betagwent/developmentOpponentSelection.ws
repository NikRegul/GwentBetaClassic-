// Debug opponents use the same active archetypes as ordinary NPCs.
// Kept separate from the generated AI catalog so regeneration preserves it.
function BetaGwentDebugOpponentAllowed(presetId : int) : bool
{
    var presets : array<int>;
    BetaGwentAIOrdinaryPresets(presets);
    return presets.Contains(presetId);
}

function BetaGwentDebugDeckVisible(presetId : int, ownPreset : int) : bool
{
    return (presetId >= 16 && presetId <= 20) || presetId == ownPreset || BetaGwentDebugOpponentAllowed(presetId);
}

exec function bgboard_decks()
{
    var presets : array<int>; var i : int;
    var preset : SBetaGwentDuelPreset; var leader : SBetaGwentDuelDefinition;
    BetaGwentAIOrdinaryPresets(presets);
    for(i=0;i<presets.Size();i+=1)
    {
        preset=BetaGwentDuelPreset(presets[i]);leader=BetaGwentDuelDefinition(preset.leaderTemplateId);
        LogChannel('BetaGwent', "DEBUG_OPPONENT preset="+presets[i]+" archetype="+BetaGwentAIArchetypeName(presets[i])+" leader="+leader.title);
    }
    LogChannel('BetaGwent', "DEBUG_OPPONENT_LIST count="+presets.Size()+" usage=bgboard_open(preset)");
}
