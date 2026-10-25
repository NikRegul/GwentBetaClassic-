"""Classic 1.32: register the mod's item XML through a DLC definition (.reddlc).

1.32 loads item definitions only from files registered by a CR4DefinitionsDLCMounter
(items) / CR4DefinitionsNGPlusDLCMounter (items_plus) in a DLC's .reddlc - see
dlc\\dlc1\\dlc1.reddlc. New XML files in a Mods bundle are ignored (only overrides of
already registered vanilla paths work). Without this, betagwent_keg, the Beta shop
cards and the Redux legacy items did not exist on 1.32: innkeepers had no kegs and
SHOP_KEG_STOCK reported quantity=0.

build_dlc() writes DLC/<name>/content/{bundles/blob0.bundle, metadata.store, dep.cache}
from a dlc1.reddlc template (classic081-complete-audit/dlc-template.reddlc).
"""
from pathlib import Path
import hashlib, struct, sys, zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / 'tools/classic132'), str(ROOT / 'tools/ui')]
from formats import write_bundle, bundle_entries, fnv64, header_crc, require, sha
from build_resources import vlq
from cr2w_gui_write109 import Res, prop

TEMPLATE = ROOT / 'BetaGwent/build/classic081-complete-audit/dlc-template.reddlc'


def string(value):
    # CR2W length prefix: bit7 = narrow (ASCII), bit6 = one more length byte (len // 64),
    # bits 0-5 = len % 64 (WolvenKit ReadLengthPrefixedString). Paths >= 64 chars need it.
    data = value.encode('ascii'); require(len(data) < 64 * 256, 'Native property string length')
    if not data: return b'\x80'
    head = 0x80 | (len(data) & 63) | (0x40 if len(data) >= 64 else 0)
    return bytes([head]) + (bytes([len(data) // 64]) if len(data) >= 64 else b'') + data


def read_string(raw):
    b = raw[0]; n = b & 63; pos = 1
    if b & 0x40: n += 64 * raw[1]; pos = 2
    require(b & 0x80, 'narrow string expected')
    return raw[pos:pos + n].decode('ascii')


def make_definition(dlc_id, title, items, plus):
    """CDLCDefinition with one definitions mounter per XML file (items, then NG+)."""
    data = bytearray(TEMPLATE.read_bytes())
    struct.pack_into('<I', data, 4, 164); struct.pack_into('<I', data, 32, header_crc(data))
    r = Res(data); names = r.name_list()
    kinds = [names[e[0]] for e in r.exports]
    require(kinds[0] == 'CDLCDefinition' and not r.imports, 'Unexpected DLC template')
    regular = r.exports[kinds.index('CR4DefinitionsDLCMounter')].copy()
    ngplus = r.exports[kinds.index('CR4DefinitionsNGPlusDLCMounter')].copy()
    count = len(items) + len(plus)
    root = (b'\0' + prop(r, 'id', 'CName', struct.pack('<H', r.add_name(dlc_id))) +
            prop(r, 'localizedNameKey', 'String', string(title)) +
            prop(r, 'localizedDescriptionKey', 'String', string('')) +
            prop(r, 'mounters', 'array:2,0,ptr:IGameplayDLCMounter',
                 struct.pack('<I', count) + b''.join(struct.pack('<I', i + 2) for i in range(count))) +
            prop(r, 'visibleInDLCMenu', 'Bool', b'\0') + b'\0\0')
    exports = [r.exports[0].copy()]; payloads = [root]
    for path, row in [(p, regular) for p in items] + [(p, ngplus) for p in plus]:
        e = row.copy(); e[2] = 1; exports.append(e)
        payloads.append(b'\0' + prop(r, 'definitionXmlFilePath', 'String', string(path)) + b'\0\0')
    r.exports = exports; r.payloads = payloads
    out = bytearray(r.build())
    check = Res(out); require(check.payloads == payloads and len(check.exports) == count + 1, 'DLC definition round trip')
    for path, payload in zip(items + plus, payloads[1:]):
        require(read_string(payload[9:]) == path, 'definitionXmlFilePath encoding: ' + path)
    struct.pack_into('<I', out, 4, 163); struct.pack_into('<I', out, 32, header_crc(out))
    for i, width in enumerate((1, 8, 8, 16, 24)):
        off, n, crc = struct.unpack_from('<III', out, 40 + i * 12)
        require(not n or zlib.crc32(out[off:off + n * width]) == crc, 'DLC table CRC')
    return bytes(out)


def make_metadata(bundle, relative_name):
    with bundle.open('rb') as stream:
        head = stream.read(32); toc = stream.read(struct.unpack_from('<I', head, 16)[0])
    strings = bytearray(b'\0')
    def add(value):
        pos = len(strings); strings.extend(value.encode('ascii') + b'\0'); return pos
    files, entries, dirs, init, hashes = [bytes(32)], [bytes(20)], [bytes(8)], [], []
    dir_ids = {'': 0}
    def directory(path):
        if path not in dir_ids:
            parent, _, leaf = path.rpartition('\\')
            parent_id = directory(parent); dir_ids[path] = len(dirs)
            dirs.append(struct.pack('<2I', add(leaf), parent_id))
        return dir_ids[path]
    maximum = 0
    for pos in range(0, len(toc), 320):
        row = toc[pos:pos + 320]; path = row[:256].split(b'\0')[0].decode('ascii')
        size, packed, offset = struct.unpack_from('<3I', row, 276); fid = len(files)
        require(size == packed and struct.unpack_from('<I', row, 316)[0] == 0, 'Uncompressed DLC expected')
        files.append(struct.pack('<8I', add(path), 0, packed, size, fid, 0, 0, 0))
        entries.append(struct.pack('<5I', fid, 1, offset, packed, 0))
        parent, _, leaf = path.rpartition('\\')
        init.append(struct.pack('<3I', fid, directory(parent), add(leaf)))
        hashes.append(struct.pack('<Qq', fnv64(path.encode('ascii')), fid)); maximum = max(maximum, size)
    start = 32 + len(toc)
    bundles = [bytes(24), struct.pack('<6I', add(relative_name), 1, len(files) - 1, bundle.stat().st_size - start, start, 0)]
    hashes.sort(key=lambda r: struct.unpack_from('<Q', r)[0])
    result = bytearray(b'\x03VTM' + struct.pack('<3I', 6, maximum, maximum) + vlq(len(strings)) + strings)
    for array in (files, entries, bundles, [], dirs, init, hashes): result += vlq(len(array)) + b''.join(array)
    return bytes(result)


def build_dlc(dlc_root, dlc_name, xml, title, work):
    """xml: {'items/<file>.xml' | 'items_plus/<file>.xml': bytes (UTF-16)} -> DLC folder."""
    low = dlc_name.lower(); files = {}; guids = {}
    items, plus = [], []
    for rel, raw in sorted(xml.items()):
        require(raw.startswith(b'\xff\xfe'), 'Classic XML must be UTF-16: ' + rel)
        mode, name = rel.split('/')
        depot = f'dlc\\{low}\\data\\gameplay\\{mode}\\{name}'
        (items if mode == 'items' else plus).append(depot)
        p = work / depot.replace('\\', '/'); p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        files[depot.replace('\\', '/')] = p
    definition = f'dlc\\{low}\\{low}.reddlc'
    p = work / definition.replace('\\', '/'); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(make_definition(low, title, items, plus))
    files[definition.replace('\\', '/')] = p
    guids[definition.replace('\\', '/')] = hashlib.sha256(definition.encode('ascii')).digest()[:16]
    content = dlc_root / dlc_name / 'content'; (content / 'bundles').mkdir(parents=True)
    bundle = content / 'bundles/blob0.bundle'
    write_bundle(files, bundle, guids)
    got = {n.replace('\\', '/'): hashlib.sha256(raw).hexdigest() for n, raw in bundle_entries(bundle)}
    require(got == {n: sha(q) for n, q in files.items()}, 'DLC bundle round trip')
    (content / 'metadata.store').write_bytes(make_metadata(bundle, r'bundles\blob0.bundle'))
    identities = [bytes(16)] + [guids[n] for n in sorted(guids)]
    cache = b'SPED' + struct.pack('<I', 2) + vlq(len(identities)) + b''.join(identities)
    cache += vlq(len(identities)) + bytes(4 * len(identities))
    cache += vlq(len(identities)) + bytes(4 * len(identities)) + vlq(1) + bytes(4)
    (content / 'dep.cache').write_bytes(cache)
    return dict(dlc=dlc_name, definition=definition, items=items, itemsPlus=plus)
