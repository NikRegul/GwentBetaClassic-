// Independent saved choices: 0 means follow the game's current language.
function BetaGwentGameTextLanguage() : int
{
    var audio,text : string;
    theGame.GetGameLanguageName(audio,text);
    if(text=="RU" || text=="ru")return 1;
    if(text=="DE" || text=="de")return 3;
    if(text=="FR" || text=="fr")return 4;
    if(text=="IT" || text=="it")return 5;
    if(text=="PL" || text=="pl")return 6;
    if(text=="ES" || text=="es")return 7;
    if(text=="ESMX" || text=="ES_MX" || text=="ES-MX" || text=="MX" || text=="es-mx")return 8;
    if(text=="BR" || text=="PT" || text=="PTBR" || text=="PT_BR" || text=="PT-BR" || text=="br" || text=="pt-br")return 9;
    if(text=="JP" || text=="JA" || text=="jp")return 10;
    if(text=="KR" || text=="KO" || text=="kr")return 11;
    if(text=="CN" || text=="ZH" || text=="ZHCN" || text=="ZH_CN" || text=="ZH-CN" || text=="cn")return 12;
    if(text=="TW" || text=="ZHTW" || text=="ZH_TW" || text=="ZH-TW" || text=="tw")return 13;
    return 2;
}
function BetaGwentGameVoiceLanguage() : int
{
    var audio,text : string;
    theGame.GetGameLanguageName(audio,text);
    if(audio=="RU" || audio=="ru")return 1;
    if(audio=="DE" || audio=="de")return 3;
    if(audio=="IT" || audio=="it")return 4;
    if(audio=="BR" || audio=="PT" || audio=="PTBR" || audio=="PT_BR" || audio=="PT-BR" || audio=="br" || audio=="pt-br")return 5;
    return 2;
}
function BetaGwentSetupLanguage(voice : bool) : int
{
    var config : CInGameConfigWrapper;var value : string;var i,limit : int;
    config=theGame.GetInGameConfigWrapper();if(!config)return 0;
    if(voice){value=config.GetVarValue('Hidden','BetaGwentVoiceLanguage');limit=5;}
    else {value=config.GetVarValue('Hidden','BetaGwentTextLanguage');limit=13;}
    i=(int)StringToFloat(value);if(i>=0 && i<=limit)return i;
    return 0;
}
function BetaGwentInitializeLanguages()
{
    if(BetaGwentCleanupBlocked())return;
    if(FactsQueryLatestValue("bg_language_preferences_initialized")>0)return;
    // Preserve an existing text choice when upgrading an old save.
    if(FactsQueryLatestValue("bg_text_language")==0)FactsSet("bg_text_language",BetaGwentSetupLanguage(false));
    if(FactsQueryLatestValue("bg_voice_language")==0)FactsSet("bg_voice_language",BetaGwentSetupLanguage(true));
    FactsSet("bg_language_preferences_initialized",1);
}
function BetaGwentTextPreference() : int
{ return Clamp(FactsQueryLatestValue("bg_text_language"),0,13); }
function BetaGwentVoicePreference() : int
{ return Clamp(FactsQueryLatestValue("bg_voice_language"),0,5); }
function BetaGwentResolvedTextLanguage() : int
{ var choice : int;choice=BetaGwentTextPreference();if(choice==0)return BetaGwentGameTextLanguage();return choice; }
function BetaGwentVoiceLanguage() : int
{ var choice : int;choice=BetaGwentVoicePreference();if(choice==0)return BetaGwentGameVoiceLanguage();return choice; }
function BetaGwentUniversalEvent(language : int, eventName : string) : string
{
    if(eventName=="" || language==1)return eventName;
    if(language==3)return eventName+"_de";
    if(language==4)return eventName+"_it";
    if(language==5)return eventName+"_pt_br";
    return eventName+"_en";
}

function BetaGwentGameVoiceName() : string
{ var audio,text : string;theGame.GetGameLanguageName(audio,text);return audio; }
