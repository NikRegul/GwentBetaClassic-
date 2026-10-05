"""Catalog the supplied DIY PDF without importing its decks into Beta rules."""
from pathlib import Path
import hashlib
import json
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Gwent-09-2025-Tierlist 6.0.pdf'
OUT = ROOT / 'docs/evidence'
OUT.mkdir(parents=True, exist_ok=True)
NAMES = {
    4: ['Calveit Spies','Arachas Swarm'], 5: ['Drain Vampires'],
    6: ['Crach Greatsword','Nekker Consume'], 7: ['Dwarf-Elf Scorch','Eist Veterans'],
    8: ['Bloodmoon Wraiths','Anna Spalla Soldiers'], 9: ['Aretuza Foltest','Eggs Consume'],
    10: ['Wild Hunt Frost','Tempo Calveit'], 11: ['Adda Cursed','Scorch Ambush'],
    12: ['Henselt Machines','Queensguard'], 13: ['Alchemy','Lyrian Machines'],
    14: ['Ointment Spallas','Swap'], 15: ['Temerians','Morvran Reveal'],
    16: ['Deathwish','Lyrians Deckbuff'], 17: ['Fanatics','Discard'],
    18: ['Ice Trolls','Eithne Handbuff'], 19: ['Brouver Shupe','40 Foltest'],
    20: ['Dwarf Miner/Xavier','Tall Ogres'], 21: ['Frost Wraiths','Francesca Handbuff'],
    22: ['Brouver Handbuff','Cintrans'], 23: ['NG Handbuff','Cursed Ships'],
    24: ['Svalblod Rain','Slave Infantry'], 25: ['Armor','Spell’atael Decoctions'],
    26: ['Calanthe Deckbuff','Axemen'], 27: ['Dryads'],
}
reader = PdfReader(SOURCE)
(OUT/'tierlist-extracted.txt').write_text(''.join(f'\n--- PAGE {i+1} ---\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages)),encoding='utf-8')
records=[]
with pdfplumber.open(SOURCE) as pdf:
    for number,names in NAMES.items():
        page=pdf.pages[number-1]
        tier='Tier 1' if number<=5 else 'High Tier 2' if number<=13 else 'Low Tier 2' if number<=21 else 'Tier 3' if number<=25 else 'Tier 4'
        for i,name in enumerate(names):
            # One-article pages use the left panel. Article/body is text; card list is an image.
            x0=i*page.width/2; x1=(i+1)*page.width/2
            words=page.extract_words()
            code=''.join(w['text'] for w in words if w['top']>page.height*.90 and x0<=w['x0']<x1)
            records.append({'name':name,'page':number,'panel':'left' if i==0 else 'right','source_tier':tier,
                            'raw_diy_deck_code':code,'code_status':'text extracted; dictionary version and screenshot identities unverified',
                            'beta_compatibility':'unverified; archetype idea only'})
result={'source':str(SOURCE),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'metadata':{str(k):str(v) for k,v in reader.metadata.items()},
        'target':'Strict Beta 0.9.24.3.432; no DIY deck import','pages':len(reader.pages),'articles':len(records),
        'note':'Names/panels were visually cataloged. Tiers describe DIY 2025, not Beta 2018. No exact card lists have been reconstructed.', 'archetypes':records}
(OUT/'tierlist-catalog.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Cataloged {len(records)} articles; {sum(bool(r["raw_diy_deck_code"]) for r in records)} raw codes. No decks imported.')
