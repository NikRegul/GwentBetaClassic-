"""Editable ordering/mulligan tables for all researched profiles.

These are bounded preferences, never invented points in a catch-up calculation.
The JSON is seeded once; later hand edits survive regeneration/builds.
"""
import json
from pathlib import Path
from ws_codegen import bounded_helpers

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/'data/beta924/ai/strategy115.json'

def main():
    rules=json.loads((ROOT/'data/beta924/ai/rules.json').read_text(encoding='utf-8'))
    catalog=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text(encoding='utf-8'))
    full=json.loads((ROOT/'data/beta924/planning/full_catalog.json').read_text(encoding='utf-8'))['cards']
    names={catalog['localization']['en_us'][str(c['templateId'])+'_name']:c['templateId'] for c in full}
    # Keep at most this many copies in an opening hand. The runtime protects
    # useful singletons and checks tutor/engine prerequisites separately.
    keep={
      'spies':{'Impera Enforcers':2,'Emissary':1,'Impera Brigade':1,'Rainfarn of Attre':1},
      'drain':{'Ancient Foglet':2,'Ekimmara':1,'Woodland Spirit':1},
      'swarm':{'Arachas Behemoth':2,'Arachas Drone':1,'Vran Warrior':1,'Forktail':1},
      'machines':{'Battering Ram':1,'Ballista':1,'Reinforced Ballista':1,'Siege Master':2,'Siege Support':2},
      'cursed':{'Damned Sorceress':1,'Tormented Mage':1},
      'reveal':{'Mangonel':2,'Alchemist':1,'Imperial Golem':0,'Fire Scorpion':1},
      'weather':{'Wild Hunt Hound':1,'Wild Hunt Rider':1,'Wild Hunt Navigator':1},
      'consume':{'Nekker':1,'Nekker Warrior':2,'Vran Warrior':1,'Forktail':1,'Celaeno Harpy':1},
      'ambush':{'Vrihedd Sappers':1,'Dol Blathanna Archer':1},
      'alchemy':{'Vicovaro Novice':2,'Viper Witcher':1},
      'moonlight':{'Siren':1,'Nekurat':1,'Lamia':1},
      'veterans':{'Tuirseach Veteran':2},
      'dwarves':{'Yarpen Zigrin':1,'Dennis Cranmer':1,'Dwarven Agitator':1,'Mahakam Volunteers':1},
      'greatswords':{'An Craite Greatsword':1,'Dimun Light Longship':1,'An Craite Armorsmith':1},
      'queensguard':{'Drummond Queensguard':1,'Dimun Pirate':1},
      'temerians':{'Blue Stripe Scout':1,'Blue Stripe Commando':1,'Temerian Infantry':1,'Kaedweni Knight':0},
      'soldiers':{'Standard Bearer':1,'Slave Infantry':1,'Sentry':1,'Recruit':1},
      'deathwish':{'Celaeno Harpy':1,'Vran Warrior':1,'Griffin':1},
      'discard':{'An Craite Longship':1,'Drummond Warmonger':1,'Dimun Pirate':1},
      'swap':{'Vrihedd Officer':1,'Vrihedd Vanguard':1,'Elven Scout':1},
      'tall':{'Old Speartip':1,'Ice Giant':1,'Ice Troll':1},
      'handbuff':{'Vrihedd Dragoon':2,'Elven Swordmaster':1,'Farseer':1},
      'singleton':{},
      'armor':{'Redanian Knight-Elect':1,'Kaedweni Cavalry':1},
      'ng-handbuff':{'Nilfgaardian Knight':1,'Spotter':1,'Magne Division':1},
      'spells':{'Dol Blathanna Sentry':2,'Elven Mercenary':1},
      'axemen':{'Tuirseach Axeman':2,'Dimun Warship':1,'An Craite Whaler':1,'Dimun Pirate Captain':1},
      'dryads':{'Braenn':1,'Vrihedd Neophyte':1},
    }
    opening={
      'spies':{'Impera Enforcers':6},'drain':{'Woodland Spirit':4,'Ancient Foglet':4},
      'swarm':{'Ruehin':6,'Arachas Behemoth':6},'machines':{'Siege Support':5,'Ronvid the Incessant':3},
      'cursed':{'Tormented Mage':3},'reveal':{'Mangonel':6},
      'weather':{'Wild Hunt Drakkar':6},'consume':{'Nekker':4,'Celaeno Harpy':3},
      'ambush':{'Vrihedd Dragoon':4},'alchemy':{},'moonlight':{},
      'veterans':{'Tuirseach Veteran':7},'dwarves':{'Dennis Cranmer':6,'Yarpen Zigrin':5},
      'greatswords':{},'queensguard':{},'temerians':{'Blue Stripe Scout':5},
      'soldiers':{'Standard Bearer':6},'deathwish':{'Celaeno Harpy':4},
      'discard':{'An Craite Longship':6},'swap':{},'tall':{'Old Speartip':6},
      'handbuff':{'Vrihedd Dragoon':6},'singleton':{},'armor':{'Redanian Knight-Elect':4},
      'ng-handbuff':{},'spells':{},'axemen':{'Tuirseach Axeman':6,'Derran':5},'dryads':{},
    }
    if not FILE.exists():
        entries=[]
        for p in rules['profiles']:
            entries.append(dict(profileId=p['id'],family=p['family'],passPolicy=p['passPolicy'],
                keep={str(names[n]):v for n,v in keep[p['family']].items() if names[n] in p['templateIds']},
                opening={str(names[n]):v for n,v in opening[p['family']].items() if names[n] in p['templateIds']}))
        FILE.write_text(json.dumps(dict(schema=1,stage=115,profiles=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    data=json.loads(FILE.read_text(encoding='utf-8'));assert data['schema']==1
    by_id={p['id']:p for p in rules['profiles']}
    assert {p['profileId'] for p in data['profiles']}==set(by_id)
    lines=['// Generated from editable data/beta924/ai/strategy115.json. Ordering only.']
    for function,field,default in [('BetaGwentAIResearchKeep','keep',-1),('BetaGwentAIResearchOpening','opening',0)]:
        lines += [f'function {function}(profile : int, card : int) : int {{','    switch(profile) {']
        for p in data['profiles']:
            if not p[field]:continue
            lines += [f'    case {p["profileId"]}:','        switch(card) {']
            for card,value in p[field].items():
                assert int(card) in by_id[p['profileId']]['templateIds'] and -1<=value<=12
                lines.append(f'        case {card}: return {value};')
            lines += [f'        default: return {default};','        }']
        lines += [f'    default: return {default};','    }','}']
    (ROOT/'BetaGwent/development/scripts/game/betagwent/duelAIResearch.ws').write_text('\n'.join(bounded_helpers(lines))+'\n',encoding='utf-8-sig')
    print('Generated editable researched keep/opening tables for all 46 profiles.')

if __name__=='__main__':main()
