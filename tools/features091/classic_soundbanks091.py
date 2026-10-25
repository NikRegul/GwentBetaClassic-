"""Classic 1.32: replace the Next-Gen always-load sound bank list inside the mod bundle.

0.9.0 shipped the REDkit/Next-Gen gameplay/globals/soundbanks_always_load.csv in the
Classic bundle. It lists 18 banks absent from 1.32 (fx_haptic, cs_mq1060_*, ...).
It also always-loaded betagwent79.bnk (8 MB, 200 media). On 1.32 that permanent bank
blocks the Hearts of Stone q601 cutscene at the Seven Cats notice board: its banks never
finish loading (confirmed in game 2026-10-20; vanilla list without betagwent79 fixes it).
duelAudio.ws already loads/unloads betagwent79.bnk on demand for each match.
The fix ships exactly the vanilla 1.32 list (game content0/startup.bundle). The entry is
replaced in place with the original payload size (NUL padding, as the shipped file
already had), so offsets and metadata.store stay valid.
"""
from pathlib import Path
import hashlib, struct, zlib

HERE=Path(__file__).resolve().parent
VANILLA=HERE/'data/soundbanks_always_load.vanilla132.csv'
# content0/bundles/startup.bundle of the GOG 1.32 install, 303 banks, CRLF.
VANILLA_SHA256='55e5c2499cd611486818d52ba1f99dbaa9e9c1ce1f7defc88769c292b7ec3ac4'
ENTRY=b'gameplay\\globals\\soundbanks_always_load.csv'
GWENT_BANK=b'betagwent79.bnk'
NEXTGEN_ONLY=[b'fx_haptic.bnk',b'cs_mq1060_boss.bnk',b'cs_mq1060_epilogue.bnk',b'cs_mq1060_first_room.bnk',
    b'cs_mq1060_geralt_dead.bnk',b'cs_mq1060_potion_room.bnk',b'cs_mq1060_split.bnk',b'cs001_nightmare.bnk',
    b'cs403_finale_explosion_p2.bnk',b'cs403_finale_explosion_scream.bnk',b'cs403_finale_explosion_scream_p2.bnk',
    b'cs403_wild_hunt_approaches_p4.bnk',b'cs502_tower_ciri_by_light.bnk',b'cs502_tower_ciri_walks_in_p2.bnk',
    b'cs602_ceremony.bnk',b'generic_bob_foliage.bnk',b'ep2_mutations_02.bnk',b'ly_animal_dog.bnk']

def banks(data):
    return [line.strip() for line in data.rstrip(b'\0').split(b'\n') if line.strip()]

def classic_list(size):
    vanilla=VANILLA.read_bytes()
    assert hashlib.sha256(vanilla).hexdigest()==VANILLA_SHA256,'Vanilla 1.32 bank list changed'
    assert vanilla.endswith(b'\r\n') and GWENT_BANK not in vanilla
    data=vanilla
    assert len(data)<=size,'Classic bank list does not fit the original entry'
    return data+b'\0'*(size-len(data))

def fix_bundle(raw):
    """Return the Classic blob0.bundle bytes with the 1.32 bank list; idempotent."""
    raw=bytearray(raw)
    assert raw[:8]==b'POTATO70' and struct.unpack_from('<H',raw,20)[0]==3,'Classic bundle expected'
    count=struct.unpack_from('<I',raw,16)[0];assert count%320==0
    hits=0
    for pos in range(32,32+count,320):
        if bytes(raw[pos:pos+256]).split(b'\0')[0]!=ENTRY:continue
        size,packed,offset=struct.unpack_from('<III',raw,pos+276);crc,compression=struct.unpack_from('<II',raw,pos+312)
        assert compression==0 and size==packed,'Uncompressed bank list expected'
        old=bytes(raw[offset:offset+size]);assert zlib.crc32(old)==crc,'Bank list CRC'
        new=classic_list(size);listed=banks(new)
        assert old==new or GWENT_BANK in banks(old),'Unexpected bank list in the base bundle'
        assert GWENT_BANK not in listed and not any(b in listed for b in NEXTGEN_ONLY)
        raw[offset:offset+size]=new;struct.pack_into('<I',raw,pos+312,zlib.crc32(new));hits+=1
    assert hits==1,'Bank list entry not found exactly once'
    return bytes(raw)
