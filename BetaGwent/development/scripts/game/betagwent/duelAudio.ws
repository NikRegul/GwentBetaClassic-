// Presentation only. Never consumes match RNG, executes rules or republishes UI.
class CBetaGwentDuelAudio extends IScriptable
{
    private var enabled, voices, ownsBank : bool;
    private var bankReported, bankPendingReported : bool;
    private var bankRequestedAt : float;
    private var nextEffect, nextClick, voiceUntil : float;
    private var queuedVoices : array<int>;
    private var queuedAt : array<float>;

    public function Initialize()
    {
        enabled = true; voices = true;
        bankRequestedAt = theGame.GetEngineTimeAsSeconds();
        if (BetaGwentAudioBankInstalled() && !theSound.SoundIsBankLoaded("betagwent79.bnk"))
        { ownsBank = true; theSound.SoundLoadBank("betagwent79.bnk", true); }
        LogChannel('BetaGwent', "AUDIO_READY betaBankInstalled=" + BetaGwentAudioBankInstalled() + " fallback=TW3_GUI");
        Ui(2);
    }
    public function Configure(effects : bool, voice : bool)
    {
        enabled = effects; voices = voice;
        if (!voices) StopVoice();
        if (!enabled && BetaReady()) theSound.SoundEvent("bg79_stop_sfx");
        LogChannel('BetaGwent', "AUDIO_SETTINGS effects=" + effects + " voices=" + voice);
    }
    private function BetaReady() : bool
    { return BetaGwentAudioBankInstalled() && theSound.SoundIsBankLoaded("betagwent79.bnk"); }
    public function IsBankReady() : bool { return BetaReady(); }
    public function Ui(kind : int)
    {
        var now : float; var eventName : string;
        if (!enabled) return;
        now = theGame.GetEngineTimeAsSeconds(); if (now < nextClick) return;
        if (BetaReady()) eventName = BetaGwentAudioUi(kind);
        if (eventName == "") switch (kind)
        {
            case 1: eventName = "gui_global_ok"; break;
            case 2: eventName = "gui_global_panel_open"; break;
            case 3: eventName = "gui_gwint_cursor_movement"; break;
            case 4: eventName = "gui_global_cancel"; break;
            default: return;
        }
        nextClick = now + 0.08f; theSound.SoundEvent(eventName);
    }
    public function Cue(kind : int, templateId : int, flags : int, ownScore : int, enemyScore : int, rowToken : int, targetTokens : int)
    {
        var eventName : string; var now : float; var voiceTrigger, cueKind : int;
        now = theGame.GetEngineTimeAsSeconds();
        if (kind == 1) voiceTrigger = 8;
        else if (kind == 24) voiceTrigger = 4;
        else if (kind == 25) voiceTrigger = 16;
        if (voices && voiceTrigger != 0 && templateId > 0 && BetaReady() && (BetaGwentAudioVoiceTriggers(templateId) & voiceTrigger) != 0 && BetaGwentAudioVoice(templateId) != "")
        {
            // Bound the queue and skip stale chatter after long summon chains.
            if (queuedVoices.Size() < 4) { queuedVoices.PushBack(templateId); queuedAt.PushBack(now); }
            Tick();
        }
        if (!enabled || kind == 0 || kind == 8 || kind == 13 || kind == 14 && now < nextEffect) return;
        cueKind = kind;
        if (BetaReady())
        {
            if (kind == 1) eventName = BetaGwentAudioEffect(templateId);
            else if (kind == 24) eventName = BetaGwentAudioRevealEffect(templateId);
            else if (kind == 25) eventName = BetaGwentAudioTransformEffect(templateId);
            if (kind == 4) eventName = BetaGwentAudioWeather(rowToken);
            if (kind == 6)
            {
                if ((flags & 16) != 0 && (flags & 32) == 0) cueKind = 30;
                else if ((flags & 32) != 0 && (flags & 16) == 0) cueKind = 31;
                else if (ownScore < enemyScore) cueKind = 29;
            }
            if (eventName == "") eventName = BetaGwentAudioCue(cueKind);
            // The hide events are distinct from application of the token.
            if (kind == 9 && (targetTokens & 4) == 0) eventName = "bg79_fx_1734391030";
            if (kind == 26 && (targetTokens & 1) == 0) eventName = "bg79_fx_1954814168";
        }
        if (eventName == "")
        {
            switch (kind)
            {
                case 1: eventName = "gui_gwint_draw_card"; break;
                case 2: eventName = "gui_gwint_using_ability"; break;
                case 3: eventName = "gui_gwint_discard_card"; break;
                case 4: eventName = "gui_gwint_using_ability"; break;
                case 5: eventName = "gui_gwint_lock_in"; break;
                case 6:
                    if ((flags & 16) != 0 && (flags & 32) == 0) eventName = "gui_gwint_battle_won";
                    else if ((flags & 32) != 0 && (flags & 16) == 0) eventName = "gui_gwint_battle_lost";
                    else if (ownScore > enemyScore) eventName = "gui_gwint_clash_victory";
                    else if (ownScore < enemyScore) eventName = "gui_gwint_clash_defeat";
                    else eventName = "gui_gwint_lock_in";
                    break;
                case 7: eventName = "gui_gwint_game_start"; break;
                case 9: eventName = "gui_gwint_using_ability"; break;
                case 10: eventName = "gui_gwint_using_ability"; break;
                case 11: eventName = "gui_gwint_discard_card"; break;
                case 12: eventName = "gui_gwint_discard_card"; break;
                case 13: eventName = "gui_gwint_using_ability"; break;
                case 14: eventName = "gui_gwint_draw_card"; break;
                case 15: eventName = "gui_gwint_summon_clones"; break;
                case 16: eventName = "gui_gwint_summon_clones"; break;
                case 17: eventName = "gui_gwint_discard_card"; break;
                case 20: eventName = "gui_gwint_close_combat"; break;
                case 21: eventName = "gui_gwint_morale_boost"; break;
                case 22: eventName = "gui_gwint_gem_destruction"; break;
                case 23: eventName = "gui_gwint_using_ability"; break;
                case 24: eventName = "gui_gwint_using_ability"; break;
                case 25: eventName = "gui_gwint_using_ability"; break;
                case 26: eventName = "gui_gwint_using_ability"; break;
                case 27: eventName = "gui_gwint_using_ability"; break;
                case 32: eventName = "gui_gwint_using_ability"; break;
                default: return;
            }
        }
        // Damage bursts keep their visuals, while sound has a short independent throttle.
        if ((kind == 2 || kind >= 20) && now < nextEffect) return;
        nextEffect = now + 0.10f; theSound.SoundEvent(eventName);
    }
    public function Tick()
    {
        var id, voiceRoll : int; var now : float; var eventName : string;
        now = theGame.GetEngineTimeAsSeconds();
        if (!BetaReady())
        {
            if (BetaGwentAudioBankInstalled() && !bankPendingReported && now - bankRequestedAt > 10.0f)
            {
                bankPendingReported = true;
                LogChannel('BetaGwent', "AUDIO_BANK_PENDING name=betagwent79.bnk nativeLoaded=false action=check_native_soundbanks_pc_then_restart_editor");
            }
            return;
        }
        if (!bankReported)
        {
            bankReported = true;
            LogChannel('BetaGwent', "AUDIO_BANK_LOADED name=betagwent79.bnk nativeLoaded=true");
        }
        if (!voices || now < voiceUntil) return;
        while (queuedVoices.Size() > 0)
        {
            id = queuedVoices[0];
            if (now - queuedAt[0] > 4.0f) { queuedVoices.Erase(0); queuedAt.Erase(0); continue; }
            queuedVoices.Erase(0); queuedAt.Erase(0);
            voiceRoll=RandRange(1000000);eventName=BetaGwentAudioVoiceVariant(id,voiceRoll);theSound.SoundEvent(eventName);
            LogChannel('BetaGwent', "AUDIO_VOICE_REQUEST template=" + id + " event=" + eventName);
            voiceUntil = now + BetaGwentAudioVoiceVariantDuration(id,voiceRoll) + 0.12f;
            break;
        }
    }
    private function StopVoice()
    {
        queuedVoices.Clear(); queuedAt.Clear(); voiceUntil = 0.0f;
        if (BetaReady()) theSound.SoundEvent("bg79_stop_voice");
    }
    public function Cancel()
    {
        StopVoice();
        if (BetaReady()) theSound.SoundEvent("bg79_stop_sfx");
    }
    public function Close()
    {
        Cancel();
        if (ownsBank) { theSound.SoundUnloadBank("betagwent79.bnk"); ownsBank = false; }
    }
}
