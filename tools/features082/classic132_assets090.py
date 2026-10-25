"""Classic 1.32 copies of the Next-Gen text and icon caches.

w3strings: the 5.0+ (v164) files have the same RTSW layout as 1.32 (v162 content0,
v163 DLC1): header, string table, key table (hash = h*31+c over the key name),
same language key. Only the version field differs; it is set to 162 and the
tables are re-checked.

texture.cache: 5.0+ writes v7, 1.32 reads v6. Verified against DLC1/content/texture.cache:
* footer: crc u64, usedPages, entryCount, stringTableSize, mipEntryCount, 'HCXT', version;
  crc = FNV-1a 64 over (mip table [4 bytes per mip entry] + string table + entries);
* entry (52 bytes): hash (h*31+c over the depot path), string offset, page offset,
  compressed, uncompressed, alignment, width, height, mips, slices, mip offset index,
  mip offset count, timestamp u64, type u16, cube u16;
* data page: compressed u32, uncompressed u32, u8 mip offset count, zlib stream.
v7 differs in the mip offset count field (u16 count + u16 extra); only single-mip,
single-slice textures are converted, which is what the keg icon is.
"""
import struct, zlib

H32 = 0xffffffff


def h31(data):
    h = 0
    for c in data: h = (h * 31 + c) & H32
    return h


def fnv64(data):
    h = 0xcbf29ce484222325
    for c in data: h = ((h ^ c) * 0x100000001b3) & 0xffffffffffffffff
    return h


# w3strings text block. Both versions XOR every unit with ((len + 1) * string_key) & 0xffff
# (1.32: whole UTF-16 unit; 5.0+: low byte only) and rotate string_key left by one bit
# after each unit. 1.32 (v162/v163) stores UTF-16 units, offsets/lengths/total in units,
# each string followed by one zero unit. 5.0+ (v164) stores UTF-8 bytes, offsets/lengths/
# total in bytes. So a v164 file is NOT readable by 1.32: the text must be re-encoded.
# string_key per language = (magic >> 8) & 0xffff, magic = stored id XOR real id. Values
# below were recovered from the 1.32 content0/<lang>.w3strings files (every string decodes)
# and agree with the magic of the mod's 5.0+ files. Keyed by the header/footer keys.
STRING_KEYS = {(0, 0): 0, (9368, 29524): 31026, (30088, 24888): 30993, (17303, 20793): 12823,
               (6265, 26193): 14453, (9094, 12662): 37401, (16951, 35122): 33330, (17811, 6292): 14169,
               (21635, 18579): 33366, (33609, 25143): 37992, (25416, 5254): 14435, (6243, 8566): 34644}


def read_vlq(raw, off):
    v = raw[off]; off += 1; n = v & 63; shift = 6; more = v & 64
    while more:
        v = raw[off]; off += 1; n |= (v & 127) << shift; shift += 7; more = v & 128
    return n, off


def write_vlq(n):
    out = bytearray([(n & 63) | (64 if n >= 64 else 0)]); n >>= 6
    while n:
        out.append((n & 127) | (128 if n >= 128 else 0)); n >>= 7
    return bytes(out)


def parse_strings(raw):
    assert raw[:4] == b'RTSW', 'w3strings magic'
    off = 10
    count, off = read_vlq(raw, off); entries = [struct.unpack_from('<III', raw, off + i * 12) for i in range(count)]; off += 12 * count
    keys, off = read_vlq(raw, off); key_rows = [struct.unpack_from('<II', raw, off + i * 8) for i in range(keys)]; off += 8 * keys
    units, data = read_vlq(raw, off)
    version = struct.unpack_from('<I', raw, 4)[0]
    width = 1 if version >= 164 else 2
    assert data + units * width + 2 == len(raw), 'w3strings text block size'
    return dict(version=version, key1=struct.unpack_from('<H', raw, 8)[0], key2=struct.unpack_from('<H', raw, len(raw) - 2)[0],
                entries=entries, keys=key_rows, tail=off, data=data, units=units, width=width)


def rotate(k):
    return ((k << 1) | (k >> 15)) & 0xffff


def decode_strings(raw):
    """{stored id: text} for v162/v163 (UTF-16) and v164 (UTF-8) files."""
    s = parse_strings(raw); sk0 = STRING_KEYS[(s['key1'], s['key2'])]; out = {}
    for sid, off, length in s['entries']:
        sk = sk0; units = []
        for i in range(length):
            if s['width'] == 1:
                units.append(raw[s['data'] + off + i] ^ (((length + 1) * sk) & 0xff))
            else:
                units.append(struct.unpack_from('<H', raw, s['data'] + 2 * (off + i))[0] ^ (((length + 1) * sk) & 0xffff))
            sk = rotate(sk)
        out[sid] = bytes(units).decode('utf-8') if s['width'] == 1 else struct.pack('<%dH' % length, *units).decode('utf-16-le')
    return s, out


def encode_v162(s, texts):
    sk0 = STRING_KEYS[(s['key1'], s['key2'])]; buf = bytearray(); rows = []
    for sid, _, _ in s['entries']:
        units = struct.unpack('<%dH' % (len(texts[sid].encode('utf-16-le')) // 2), texts[sid].encode('utf-16-le'))
        rows.append(struct.pack('<III', sid, len(buf) // 2, len(units))); sk = sk0
        for u in units:
            buf += struct.pack('<H', u ^ (((len(units) + 1) * sk) & 0xffff)); sk = rotate(sk)
        buf += b'\0\0'
    out = (b'RTSW' + struct.pack('<IH', 162, s['key1']) + write_vlq(len(rows)) + b''.join(rows) +
           write_vlq(len(s['keys'])) + b''.join(struct.pack('<II', *k) for k in s['keys']) +
           write_vlq(len(buf) // 2) + bytes(buf) + struct.pack('<H', s['key2']))
    return out


def classic_strings(raw, required_keys=()):
    """Re-encode a 5.0+ (v164, UTF-8) w3strings file for 1.32 (v162, UTF-16); ids/key table kept."""
    src, texts = decode_strings(raw)
    assert src['version'] in (162, 163, 164) and texts, src['version']
    out = encode_v162(src, texts)
    got, back = decode_strings(out)
    assert got['version'] == 162 and back == texts and got['keys'] == src['keys'], 'w3strings round trip'
    assert [e[0] for e in got['entries']] == [e[0] for e in src['entries']]
    assert {r[1] for r in got['keys']} <= set(texts), 'key table points to missing ids'
    hashes = {r[0]: r[1] for r in got['keys']}
    for key in required_keys:
        assert texts[hashes[h31(key.encode('ascii'))]], 'missing localisation key ' + key
    return out, dict(strings=len(texts), keys=len(got['keys']), version=162, sourceVersion=src['version'])


def read_cache(data):
    crc, pages, n, strings, mips, magic, version = struct.unpack_from('<QIIII4sI', data, len(data) - 32)
    assert magic == b'HCXT', 'texture.cache magic'
    e0 = len(data) - 32 - n * 52; s0 = e0 - strings; m0 = s0 - mips * 4
    assert m0 >= pages * 4096 or pages == 0
    entries = [list(struct.unpack_from('<IiIIIIHHHHiIQHH', data, e0 + i * 52)) for i in range(n)]
    names = [data[s0 + e[1]:data.index(b'\0', s0 + e[1])].decode('ascii') for e in entries]
    assert fnv64(data[m0:e0 + n * 52]) == crc, 'texture.cache crc'
    return dict(version=version, pages=pages, entries=entries, names=names, strings=data[s0:e0],
                mips=data[m0:s0], body=data[:pages * 4096])


def classic_texture_cache(data):
    src = read_cache(data)
    assert src['version'] == 7 and not src['mips'], (src['version'], len(src['mips']))
    entries = []
    for e, name in zip(src['entries'], src['names']):
        hash_, soff, page, packed, size, align, w, h, mips, slices, mip_index, mip_count, stamp, kind, cube = e
        assert mips == 1 and slices == 1 and cube == 0 and mip_index == 0 and (mip_count & 0xffff) == 0, name
        start = page * 4096
        cpacked, csize, extra = struct.unpack_from('<IIB', data, start)
        assert extra == 0 and csize == size and 9 + cpacked == packed, name
        assert len(zlib.decompress(data[start + 9:start + 9 + cpacked])) == size, 'texture chunk'
        entries.append([h31(name.encode('ascii')), soff, page, packed, size, align, w, h, 1, 1, 0, 0, 0, kind, 0])
    rows = b''.join(struct.pack('<IiIIIIHHHHiIQHH', *e) for e in entries)
    tail = src['strings'] + rows
    out = src['body'] + tail + struct.pack('<QIIII4sI', fnv64(tail), src['pages'], len(entries),
                                           len(src['strings']), 0, b'HCXT', 6)
    check = read_cache(out)
    assert check['version'] == 6 and check['names'] == src['names'] and check['body'] == src['body']
    return out, dict(textures=src['names'], version=6, bytes=len(out))
