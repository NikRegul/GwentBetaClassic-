"""Execute the actual cleaner methods against isolated facts/profile fixtures."""
from pathlib import Path
import sys,re,subprocess,json,struct
ROOT=Path(__file__).resolve().parents[2];OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BetaGwent/build/cleaner082'
sys.path.insert(0,str(ROOT/'tools/ai'));import ws2js
sys.path.insert(0,str(Path(__file__).parent));import save_fact_index as scan
def main():
    source=(OUT/'scripts/game/betagwent/cleaner082.ws').read_text('utf-8-sig')
    pattern=r'@addField\(W3PlayerWitcher\)\s*((?:private|public) saved var [^;]+;)'
    declarations=re.findall(pattern,source);s=re.sub(pattern,'',source)
    start=s.index('@addMethod(W3PlayerWitcher)');begin=s.index('{',start);depth=1;end=begin+1
    while depth:
        if s[end]=='{':depth+=1
        if s[end]=='}':depth-=1
        end+=1
    method=s[start:end].replace('@addMethod(W3PlayerWitcher)','');s=s[:start]+s[end:]
    wrapper='\n'.join(declarations).replace('saved var','var')+'\n'+method+'\npublic function GetInventory() : CInventoryComponent { return NULL; }\npublic function IsInCombat() : bool { return false; }'
    p=OUT/'test-wrapper.ws';p.write_text('class W3PlayerWitcher extends IScriptable {\n'+wrapper+'\n}\n'+s,'utf8')
    translated,_=ws2js.build([p],[])
    fields=json.loads((OUT/'inventory.json').read_text('utf8'))['allSavedFields'];fields=[f for f in fields if f['target']=='W3PlayerWitcher']
    js=(ROOT/'tools/ai/jshost/runtime.js').read_text('utf8')+'\n'+translated+'\n'+r'''
const assert=require('assert'),facts=new Map(),notices=[];let checks=0;
function check(v,n){assert(v,n);checks++;}
function FactsDoesExist(k){return facts.has(k);}function FactsRemove(k){facts.delete(k);return true;}
function StrLeft(v,n){return v.slice(0,n);}function StrMid(v,n,len){return v.slice(n,n+len);}function StrLen(v){return v.length;}
function LogChannel(){}function NameToString(v){return v;}
const theGame={GetGuiManager:()=>({ShowNotification(v){notices.push(v);},IsAnyMenu:()=>false})};
const thePlayer=new W3PlayerWitcher();let keg=5;thePlayer.GetInventory=()=>({GetAllItems:items=>items.push('betagwent_keg','betagwent_shop_card','Crowns','gwint_card_redux'),GetItemName:id=>id,RemoveItem:id=>{check(id.startsWith('betagwent_'),'only own mod inventory items removed');if(id==='betagwent_keg')keg=0;}});
'''+f'const fields={json.dumps(fields)};'+r'''
for(const f of fields)thePlayer[f.name]=f.type.startsWith('array<')?[1,2]:f.type==='bool'?true:17;
thePlayer.betaGwentRewardedNpcs=[123,-456];thePlayer.betaGwentRewardedQuests=['quest_deck'];
const owned=['bg_b2_cur','bg_b2_1_ci1000','bg_b2_2_cc2047','bg_b2_1_d13_39','bg_b2_2_d8_n','bg_b2_1_ni2000','bg_bk_ci_1000','bg_bk_d8_39','bg_bkn_123','bg_bkn_-456','bg_bkq_quest_deck','bg_text_language','betagwent_collection_owned'];
const native=['quest_native','gwint_all_cards_collected','Gwint_Card_Looted','HasGwentTournamentDeck','other_mod','bg_other_mod_fact','betagwent_other_mod_fact'];
for(const key of [...owned,...native,'bg_bkn_99999999'])facts.set(key,1);
const before=JSON.stringify([...facts]);bg_clean_preview();bg_clean_confirm('wrong');check(before===JSON.stringify([...facts])&&keg===5,'preview and wrong confirmation are read-only');
bg_clean_confirm('DELETE_BETA_GWENT');check(owned.every(k=>!facts.has(k)),'both banks, legacy format, settings and current reward ledgers removed');
check(keg===0,'physical mod inventory items removed');
check(native.every(k=>facts.get(k)===1),'native quests/achievements/admission and other mods preserved');
check(fields.every(f=>Array.isArray(thePlayer[f.name])?thePlayer[f.name].length===0:!thePlayer[f.name]),'all player saved fields cleared');
check(facts.has('bg_bkn_99999999'),'orphan ledger requires explicit fact list');
bg_clean_keys('bg_bkn_99999999|quest_native|other_mod|bg_other_mod_fact|betagwent_other_mod_fact|betagwent_all_cards_collected');check(!facts.has('bg_bkn_99999999')&&native.every(k=>facts.has(k)),'imported list stays in audited mod namespaces');
const after=JSON.stringify([...facts]);thePlayer.GetInventory=()=>null;bg_clean_confirm('DELETE_BETA_GWENT');check(after===JSON.stringify([...facts]),'repeat cleanup is idempotent');
console.log(JSON.stringify({checks,fields:fields.length,saveFilesModified:false,nativeSaveRoundTrip:false}));
'''
    script=OUT/'cleaner-tests.js';script.write_text(js,'utf8');subprocess.run(['node',str(script)],check=True,cwd=ROOT)
    # Independent decoder tests: literals, overlapping matches, malformed bounds,
    # multi-chunk container and UTF-16 strings. No personal saves are opened.
    check_count=0
    def check(v):
        nonlocal check_count
        assert v;check_count+=1
    raw=b'bg_bkn_99999999\0quest_native\0betagwent_collection_owned\0'
    block=bytes([0xf0,len(raw)-15])+raw
    check(scan.lz4(block,len(raw))==raw)
    check(scan.lz4(bytes([0x10])+b'a'+bytes([1,0,0x50])+b'bcdef',10)==b'aaaaabcdef')
    container=b'SNFHFZLC'+struct.pack('<II',1,28)+struct.pack('<III',len(block),len(raw),28+len(block))+block
    check(scan.names(scan.unpack(container))==['betagwent_collection_owned','bg_bkn_99999999'])
    for bad in [b'',container[:-1],container[:8]+bytes(8),b'not a save']:
        try:scan.unpack(bad)
        except (ValueError,IndexError,struct.error):check(True)
        else:raise AssertionError('malformed save accepted')
    (OUT/'tests.json').write_text(json.dumps(dict(decoderChecks=check_count,actualCleanerExecutedInHost=True,saveRoundTripVerified=False),indent=2),'utf8')
    print('Read-only scanner checks:',check_count)
if __name__=='__main__':main()
