"""Read only the captured menu and its textures from a local full-memory dump."""
import argparse
import bisect
import json
import mmap
from pathlib import Path
import struct

from capture_scaleform import Trace
from capture_all import REGISTERS


class DumpMemory:
    def __init__(self, path):
        self.file = path.open('rb')
        self.data = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        assert self.data[:4] == b'MDMP'
        count, directory = struct.unpack_from('<II', self.data, 8)
        self.streams = {}
        for i in range(count):
            kind, size, rva = struct.unpack_from('<III', self.data, directory + i * 12)
            assert rva + size <= len(self.data)
            self.streams[kind] = (size, rva)
        count, cursor = struct.unpack_from('<QQ', self.data, self.streams[9][1])
        self.ranges = []
        for i in range(count):
            address, size = struct.unpack_from('<QQ', self.data, self.streams[9][1] + 16 + i * 16)
            assert cursor + size <= len(self.data)
            self.ranges.append((address, size, cursor)); cursor += size
        self.ranges.sort()
        self.starts = [r[0] for r in self.ranges]
        self.base = None
        pos = self.streams[4][1]
        for i in range(struct.unpack_from('<I', self.data, pos)[0]):
            address, size, _, _, name = struct.unpack_from('<QIIII', self.data, pos + 4 + i * 108)
            length = struct.unpack_from('<I', self.data, name)[0]
            path = self.data[name + 4:name + 4 + length].decode('utf-16le')
            if path.lower().endswith('witcher3.exe'):
                self.base = address
        assert self.base

    def memory(self, address, size):
        i = bisect.bisect_right(self.starts, address) - 1
        if i < 0:
            return b''
        start, length, offset = self.ranges[i]
        if not start <= address < start + length:
            return b''
        size = min(size, start + length - address)
        return self.data[offset + address - start:offset + address - start + size]

    def contexts(self):
        pos = self.streams[3][1]
        for i in range(struct.unpack_from('<I', self.data, pos)[0]):
            offset = pos + 4 + i * 48
            tid = struct.unpack_from('<I', self.data, offset)[0]
            size, context = struct.unpack_from('<II', self.data, offset + 40)
            if size >= 256:
                yield tid, {name: struct.unpack_from('<Q', self.data, context + n)[0] for name, n in REGISTERS.items()}


def inspect(path, resource_address=None):
    memory = DumpMemory(path)
    helper = Trace.__new__(Trace)
    helper.memory, helper.base = memory.memory, memory.base
    report = dict(base=hex(memory.base), menuThreads=[])
    targets = []
    if resource_address:
        targets.append((0, resource_address, helper.file_details(helper.pointer(resource_address + 0x58))))
    else:
        for tid, regs in memory.contexts():
            if regs['rip'] - memory.base == 0x91566:
                targets.append((tid, helper.pointer(regs['rdi'] + 0x10), helper.file_details(regs['rdi'])))
    for tid, root, file in targets:
        record = dict(thread=tid, file=file, resource=hex(root), resourceType=helper.native_type(root),
                      resourceBytes=helper.memory(root, 512).hex(), textures=[])
        array = helper.pointer(root + 0x80)
        count_raw = helper.memory(root + 0x88, 4)
        count = struct.unpack('<I', count_raw)[0] if len(count_raw) == 4 else 0
        assert count <= 1024
        record.update(textureCount=count, textureArray=hex(array))
        for i in range(count):
            control = helper.pointer(array + i * 8)
            texture = helper.pointer(control + 0x10) if control else 0
            record['textures'].append(dict(index=i, control=hex(control), object=hex(texture),
                                            type=helper.native_type(texture) if texture else None,
                                            linkage=helper.native_string(texture + 0xe8) if texture else '',
                                            bytes=helper.memory(texture, 512).hex(),
                                            file=helper.file_details(helper.pointer(texture + 0x58)) if texture else None))
        report['menuThreads'].append(record)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--resource', type=lambda value: int(value, 0),
                        help='Root resource from RENDER_SNAPSHOT for a late dump')
    args = parser.parse_args()
    result = inspect(args.dump, args.resource)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(base=result['base'], menus=[dict(file=r['file'], textureCount=r['textureCount'],
                       loadedTextures=sum(int(t['object'], 16) != 0 for t in r['textures']),
                       textures=[{k: t[k] for k in ('index', 'object', 'type', 'linkage', 'file')} for t in r['textures']])
                       for r in result['menuThreads']]), ensure_ascii=False, indent=2))
