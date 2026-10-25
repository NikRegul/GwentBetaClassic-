"""Classic-only language bank lifecycle, applied before native compilation."""

def patch(text):
    assert 'private var bankName : string;' not in text
    text=text.replace('    private var enabled, voices, ownsBank : bool;',
                      '    private var enabled, voices, ownsBank : bool;\n    private var bankName : string;')
    a=text.index('    public function Initialize()');b=text.index('    public function Configure(',a)
    text=text[:a]+'''    private function DesiredBank() : string
    {
        var language : int;language=BetaGwentVoiceLanguage();
        if(language==3)return "betagwent091_de.bnk";
        if(language==4)return "betagwent091_it.bnk";
        if(language==5)return "betagwent091_pt_br.bnk";
        if(language==2)return "betagwent091_en.bnk";
        return "betagwent091_ru.bnk";
    }
    public function RefreshBank()
    {
        var wanted : string;wanted=DesiredBank();
        if(wanted==bankName)return;
        if(bankName!="")
        {
            Cancel();
            if(ownsBank)theSound.SoundUnloadBank(bankName);
        }
        bankName=wanted;ownsBank=false;bankReported=false;bankPendingReported=false;
        bankRequestedAt=Now();
        if(BetaGwentAudioBankInstalled() && !theSound.SoundIsBankLoaded(bankName))
        {
            ownsBank=true;
            LogChannel('BetaGwent',"AUDIO_BANK_REQUEST name="+bankName+" async=false scope=menu");
            theSound.SoundLoadBank(bankName,false);
        }
        LogChannel('BetaGwent',"AUDIO_BANK_RESULT name="+bankName+" nativeLoaded="+theSound.SoundIsBankLoaded(bankName));
    }
    public function Initialize()
    {
        enabled=true;voices=true;RefreshBank();
        LogChannel('BetaGwent',"AUDIO_READY betaBankInstalled="+BetaGwentAudioBankInstalled()+" fallback=TW3_GUI");
        Ui(2);
    }
''' +text[b:]
    text=text.replace('theSound.SoundIsBankLoaded("betagwent79.bnk")','bankName!="" && theSound.SoundIsBankLoaded(bankName)')
    text=text.replace('LogChannel(\'BetaGwent\', "AUDIO_BANK_PENDING name=betagwent79.bnk nativeLoaded=false action=check_native_soundbanks_pc_then_restart_editor");',
                      'LogChannel(\'BetaGwent\', "AUDIO_BANK_PENDING name="+bankName+" nativeLoaded=false");')
    text=text.replace('LogChannel(\'BetaGwent\', "AUDIO_BANK_LOADED name=betagwent79.bnk nativeLoaded=true");',
                      'LogChannel(\'BetaGwent\', "AUDIO_BANK_LOADED name="+bankName+" nativeLoaded=true");')
    text=text.replace('if (ownsBank) { theSound.SoundUnloadBank("betagwent79.bnk"); ownsBank = false; }',
                      'if (ownsBank) { theSound.SoundUnloadBank(bankName); ownsBank = false; }\n        bankName="";')
    text=text.replace('        now = Now();\n        if (!BetaReady())','        RefreshBank();now = Now();\n        if (!BetaReady())')
    assert '"betagwent79.bnk"' not in text
    return text

def patch_menu(text):
    old='        FactsSet("bg_voice_language",language);'
    assert text.count(old)==1
    return text.replace(old,old+'\n        if(audio)audio.RefreshBank();')
