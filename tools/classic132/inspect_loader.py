"""Read-only PE/RTTI inspection of the installed Classic loader.

Optional capstone/pefile are isolated under the audit output, not system-wide.
This tool never starts, attaches to, patches, or writes to the game.
"""
import argparse
import bisect
from pathlib import Path
import re
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'BetaGwent/build/classic081-complete-audit/python-tools'))
import capstone
import pefile


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--class-name', action='append', default=[])
    ap.add_argument('--address', action='append', default=[])
    ap.add_argument('--span', action='append', default=[], help='VA:length, for split unwind fragments')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    game = Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt/bin/x64/witcher3.exe')
    raw = game.read_bytes()
    pe = pefile.PE(data=raw, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']])
    base = pe.OPTIONAL_HEADER.ImageBase
    ranges = sorted((e.struct.BeginAddress, e.struct.EndAddress)
                    for e in pe.DIRECTORY_ENTRY_EXCEPTION)
    begins = [r[0] for r in ranges]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    md.detail = True
    output = []

    def string_at(address):
        try:
            data = pe.get_data(address - base, 160)
            if len(data) < 4:
                return ''
            if data[1] == 0:
                value = data.decode('utf-16le', errors='ignore').split('\0')[0]
            else:
                value = data.split(b'\0')[0].decode('ascii', errors='ignore')
            if len(value) >= 3 and all(c.isprintable() for c in value):
                return repr(value)
        except (pefile.PEFormatError, ValueError):
            pass
        return ''

    dumped = set()

    def dump(address):
        rva = address - base
        i = bisect.bisect_right(begins, rva) - 1
        if i < 0 or not ranges[i][0] <= rva < ranges[i][1]:
            return
        start, end = ranges[i]
        if start in dumped:
            return
        dumped.add(start)
        output.append(f'\nFUNCTION {base + start:#x}..{base + end:#x}')
        for ins in md.disasm(pe.get_data(start, end - start), base + start):
            note = ''
            for operand in ins.operands:
                if operand.type == capstone.x86.X86_OP_MEM and operand.mem.base == capstone.x86.X86_REG_RIP:
                    target = ins.address + ins.size + operand.mem.disp
                    note += f' ; {target:#x} {string_at(target)}'
            output.append(f'{ins.address:x}: {ins.mnemonic} {ins.op_str}{note}')

    for name in args.class_name:
        symbol = ('.?AV' + name + '@@\0').encode('ascii')
        offsets = [m.start() for m in re.finditer(re.escape(symbol), raw)]
        for offset in offsets:
            td = pe.get_rva_from_offset(offset - 16)
            output.append(f'\nRTTI {name}: descriptor {base + td:#x}')
            for match in re.finditer(re.escape(struct.pack('<I', td)), raw):
                col_offset = match.start() - 12
                if col_offset < 0:
                    continue
                col = struct.unpack_from('<6I', raw, col_offset)
                if col[0] != 1 or col[-1] != pe.get_rva_from_offset(col_offset):
                    continue
                col_address = base + col[-1]
                for pointer in re.finditer(re.escape(struct.pack('<Q', col_address)), raw):
                    vt_offset = pointer.start() + 8
                    output.append(f'VTABLE {base + pe.get_rva_from_offset(vt_offset):#x}, COL {col}')
                    for n in range(32):
                        fn = struct.unpack_from('<Q', raw, vt_offset + n * 8)[0]
                        if not base <= fn < base + pe.OPTIONAL_HEADER.SizeOfImage:
                            break
                        output.append(f'  [{n:#x}] {fn:#x}')
                        dump(fn)
    for address in args.address:
        dump(int(address, 0))
    for value in args.span:
        address, size = [int(x, 0) for x in value.split(':')]
        output.append(f'\nSPAN {address:#x} +{size:#x}')
        for ins in md.disasm(pe.get_data(address - base, size), address):
            output.append(f'{ins.address:x}: {ins.mnemonic} {ins.op_str}')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text('\n'.join(output) + '\n', 'utf8')
    print(args.out, 'functions', len(dumped), 'lines', len(output))


if __name__ == '__main__':
    main()
