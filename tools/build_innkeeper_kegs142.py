"""Add five kegs to every named inn stock, keeping the native loot unchanged."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SDK=Path('D:/GOG Galaxy/Games/The Witcher 3 REDkit/r4data')
WORK=ROOT/'GwentB/myproject1/workspace'

def main():
    records=[]
    sources=[SDK/f'gameplay/{folder}/def_loot_shops.xml' for folder in ('items','items_plus')]
    sources+=sorted((SDK/'dlc').glob('*/data/gameplay/*/def_loot_shops.xml'))
    for source in sources:
        relative=source.relative_to(SDK);target=WORK/relative
        raw=target.read_bytes() if target.exists() else source.read_bytes()
        text=raw.decode('utf-8-sig');added=[];covered=[]
        def update(match):
            block=match.group();name=re.search(r'\bname="([^"]+)"',block).group(1)
            if not re.search(r'inn|tavern|barkeep',name,re.I):return block
            covered.append(name)
            if 'name="betagwent_keg"' in block:return block
            added.append(name);index=block.index('>')+1
            return block[:index]+'\n        <loot_entry name="betagwent_keg" player_level_min="0" player_level_max="0" quantity_min="5" quantity_max="5" chance="-1" />'+block[index:]
        changed=re.sub(r'<loot\s+name="[^\"]+"[^>]*>.*?</loot>',update,text,flags=re.S)
        if not covered:continue
        # Validate the resulting XML before writing an overlay.
        tree=ET.fromstring(changed)
        for loot in tree.iter('loot'):
            if loot.get('name') in covered:
                entries=[e for e in loot.iter('loot_entry') if e.get('name')=='betagwent_keg']
                assert len(entries)==1 and entries[0].get('quantity_min')==entries[0].get('quantity_max')=='5'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+changed.encode('utf8'))
        records.append(dict(path=relative.as_posix(),innStocks=covered,added=added,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),overlaySha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    report=dict(stage=142,overlays=records,runtimeFallback='W3MerchantComponent.GetMapPinType() == Innkeeper, one migration per NPC',nativeGameTested=False)
    (ROOT/'docs/evidence/innkeeper-kegs142.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('Covered',sum(len(r['innStocks']) for r in records),'loot definitions including NG+; runtime covers unnamed/DLC innkeepers')

if __name__=='__main__':main()
