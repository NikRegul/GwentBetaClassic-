"""Give the Beta Gwent CMenuResource files the vanilla Gwent pause setting.

Vanilla r4gwint_game.menu / r4deck_builder.menu serialize
CMenuPauseParam { pauseType: EMenuPauseType = MPT_FullPause }. The REDkit-saved
Beta menus contain an empty CMenuPauseParam, so the world keeps simulating behind
the board (guards, combat, potion hotkeys). This tool rewrites only that object.

Fail-closed: the file is first rebuilt from its parsed tables and must be
byte-identical to the input before any change is made. CR2W v164 only.
Name hash = FNV-1a32(name + NUL), empty name hash 0; table/export CRC = CRC32;
header CRC = CRC32 of header+table headers with the CRC field set to DEADBEEF.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, struct, zlib

HEADER = 160


class MenuError(ValueError):
    pass


def fnv(name):
    if not name:
        return 0
    h = 0x811c9dc5
    for b in name.encode('ascii') + b'\0':
        h = ((h ^ b) * 0x01000193) & 0xffffffff
    return h


def parse(data):
    if data[:4] != b'CR2W' or struct.unpack_from('<I', data, 4)[0] != 164:
        raise MenuError('Expected CR2W v164')
    head = struct.unpack_from('<4sIIQIIIII', data, 0)
    tabs = [struct.unpack_from('<III', data, 40 + i * 12) for i in range(10)]
    if any(t != (0, 0, 0) for t in tabs[5:]):
        raise MenuError('Unsupported extra tables (buffers/embedded)')
    so, ss, _ = tabs[0]
    strings = data[so:so + ss]

    def text(o):
        return strings[o:strings.index(0, o)].decode('ascii')
    no, nc, _ = tabs[1]
    names = []
    for i in range(nc):
        o, h = struct.unpack_from('<II', data, no + i * 8)
        n = text(o)
        if fnv(n) != h:
            raise MenuError('Name hash rule mismatch: ' + n)
        names.append(n)
    io, ic, _ = tabs[2]
    imports = [struct.unpack_from('<IHH', data, io + i * 8) for i in range(ic)]
    imports = [(text(o), c, f) for o, c, f in imports]
    po, pc, _ = tabs[3]
    props = data[po:po + pc * 16]
    eo, ec, _ = tabs[4]
    exports = []
    for i in range(ec):
        cls, flags, parent, size, pos, tmpl, crc = struct.unpack_from('<HHIIIII', data, eo + i * 24)
        blob = data[pos:pos + size]
        if zlib.crc32(blob) != crc:
            raise MenuError('Export CRC mismatch')
        exports.append([cls, flags, parent, tmpl, blob])
    return dict(head=head, names=names, imports=imports, props=props, exports=exports, pc=pc)


def build(m):
    strings = b'\0'
    name_off = []
    for n in m['names']:
        if n == '':
            name_off.append(0)
            continue
        name_off.append(len(strings))
        strings += n.encode('ascii') + b'\0'
    imp_off = []
    for path, _, _ in m['imports']:
        imp_off.append(len(strings))
        strings += path.encode('ascii') + b'\0'
    names = b''.join(struct.pack('<II', o, fnv(n)) for o, n in zip(name_off, m['names']))
    imports = b''.join(struct.pack('<IHH', o, c, f) for o, (_, c, f) in zip(imp_off, m['imports']))
    o_str = HEADER
    o_names = o_str + len(strings)
    o_imp = o_names + len(names)
    o_props = o_imp + len(imports)
    o_exp = o_props + len(m['props'])
    pos = o_exp + 24 * len(m['exports'])
    exports, body = b'', b''
    for cls, flags, parent, tmpl, blob in m['exports']:
        exports += struct.pack('<HHIIIII', cls, flags, parent, len(blob), pos, tmpl, zlib.crc32(blob))
        body += blob
        pos += len(blob)
    tables = [(o_str, len(strings), zlib.crc32(strings)),
              (o_names, len(m['names']), zlib.crc32(names)),
              (o_imp, len(m['imports']), zlib.crc32(imports)),
              (o_props, m['pc'], zlib.crc32(m['props'])),
              (o_exp, len(m['exports']), zlib.crc32(exports))] + [(0, 0, 0)] * 5
    magic, ver, flags, stamp, build_v, _, _, _, chunks = m['head']
    total = pos
    tab_bytes = b''.join(struct.pack('<III', *t) for t in tables)
    head = struct.pack('<4sIIQIIIII', magic, ver, flags, stamp, build_v, total, total, 0xDEADBEEF, chunks)
    crc = zlib.crc32(head + tab_bytes)
    head = struct.pack('<4sIIQIIIII', magic, ver, flags, stamp, build_v, total, total, crc, chunks)
    out = head + tab_bytes + strings + names + imports + m['props'] + exports + body
    if len(out) != total:
        raise MenuError('Layout size mismatch')
    return out


def name_index(m, n):
    if n not in m['names']:
        m['names'].append(n)
    return m['names'].index(n)


def read_props(m, blob):
    if blob[:1] != b'\0':
        raise MenuError('Unsupported object marker')
    out, o = [], 1
    while blob[o:o + 2] != b'\0\0':
        n, t, size = struct.unpack_from('<HHI', blob, o)
        out.append((m['names'][n], m['names'][t], blob[o + 8:o + 4 + size]))
        o += 4 + size
    if o + 2 != len(blob):
        raise MenuError('Trailing object bytes')
    return out


def patch(path):
    data = Path(path).read_bytes()
    m = parse(data)
    if build(m) != data:
        raise MenuError('Round-trip mismatch; refusing to edit ' + str(path))
    if m['names'][m['exports'][0][0]] != 'CMenuResource':
        raise MenuError('Not a CMenuResource')
    pause = [e for e in m['exports'] if m['names'][e[0]] == 'CMenuPauseParam']
    if len(pause) != 1:
        raise MenuError('Expected exactly one CMenuPauseParam')
    current = read_props(m, pause[0][4])
    for n, t, v in current:
        if n == 'pauseType':
            if t == 'EMenuPauseType' and m['names'][struct.unpack('<H', v)[0]] == 'MPT_FullPause':
                return dict(path=str(path), changed=False, sha256=hashlib.sha256(data).hexdigest())
            raise MenuError('Unexpected existing pauseType')
    if current:
        raise MenuError('Unexpected CMenuPauseParam fields')
    p, t, v = (name_index(m, 'pauseType'), name_index(m, 'EMenuPauseType'), name_index(m, 'MPT_FullPause'))
    pause[0][4] = b'\0' + struct.pack('<HHIH', p, t, 6, v) + b'\0\0'
    out = build(m)
    check = parse(out)
    if read_props(check, [e for e in check['exports'] if check['names'][e[0]] == 'CMenuPauseParam'][0][4]) != [('pauseType', 'EMenuPauseType', struct.pack('<H', v))]:
        raise MenuError('Verification of written pauseType failed')
    if build(check) != out:
        raise MenuError('Patched file does not round-trip')
    return dict(path=str(path), changed=True, before=hashlib.sha256(data).hexdigest(),
                after=hashlib.sha256(out).hexdigest(), bytes=len(out), data=out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('menus', nargs='+', type=Path)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--backup-dir', type=Path)
    ap.add_argument('--report', type=Path)
    a = ap.parse_args()
    results = []
    for menu in a.menus:
        r = patch(menu)
        if r.get('changed') and a.apply:
            if not a.backup_dir:
                raise SystemExit('--backup-dir required with --apply')
            a.backup_dir.mkdir(parents=True, exist_ok=True)
            backup = a.backup_dir / (menu.parent.name + '__' + menu.name)
            if not backup.exists():
                shutil.copyfile(menu, backup)
            menu.write_bytes(r['data'])
            r['backup'] = str(backup)
        r.pop('data', None)
        r['applied'] = bool(a.apply and r.get('changed'))
        results.append(r)
    text = json.dumps(dict(pauseType='MPT_FullPause', reference='vanilla r4gwint_game.menu/r4deck_builder.menu',
                           results=results), indent=2)
    if a.report:
        a.report.write_text(text + '\n', 'utf8')
    print(text)
