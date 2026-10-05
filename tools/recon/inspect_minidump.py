"""Read exception/module metadata only from a Windows minidump, without executing it.

Uses documented MINIDUMP stream layouts. Optional stack words are module-mapped
address candidates, NOT a symbolized or unwound call stack. No memory strings,
application data, handles or credentials are extracted.
"""
import argparse
import hashlib
import json
import mmap
import struct
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def inspect(path):
    with path.open('rb') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
        def unpack(fmt, offset):
            if offset < 0 or offset + struct.calcsize(fmt) > len(data):
                raise ValueError('Out-of-bounds minidump record')
            return struct.unpack_from(fmt, data, offset)

        def string(rva):
            length, = unpack('<I', rva)
            if length % 2 or length > 65536 or rva + 4 + length > len(data):
                raise ValueError('Invalid module name string')
            return data[rva + 4:rva + 4 + length].decode('utf-16-le', errors='replace')

        if data[:4] != b'MDMP':
            raise ValueError('Not a minidump')
        _, count, directory, _, timestamp, flags = unpack('<IIIIIQ', 4)
        if count > 10000:
            raise ValueError('Invalid directory size')
        streams = {}
        for index in range(count):
            kind, size, rva = unpack('<III', directory + index * 12)
            if rva + size > len(data):
                raise ValueError('Out-of-bounds stream')
            streams[kind] = (size, rva)
        if 4 not in streams or 6 not in streams:
            raise ValueError('Missing module or exception stream')
        module_size, module_rva = streams[4]
        module_count, = unpack('<I', module_rva)
        if 4 + 108 * module_count > module_size:
            raise ValueError('Invalid module list extent')
        modules = []
        for index in range(module_count):
            offset = module_rva + 4 + index * 108
            base, size, _, pe_time, name_rva = unpack('<QIIII', offset)
            name = string(name_rva)
            modules.append(dict(path=name, name=name.replace('\\', '/').rsplit('/', 1)[-1],
                                base=f'0x{base:x}', size=size, peTimestamp=pe_time))

        def module_at(address):
            for module in modules:
                base = int(module['base'], 16)
                if base <= address < base + module['size']:
                    return dict(name=module['name'], path=module['path'], offset=f'0x{address - base:x}')
            return None

        exception_size, exception_rva = streams[6]
        if exception_size < 168:
            raise ValueError('Truncated exception stream')
        thread_id, = unpack('<I', exception_rva)
        code, exception_flags, nested, address, parameter_count, _ = unpack('<IIQQII', exception_rva + 8)
        if parameter_count > 15:
            raise ValueError('Invalid exception parameter count')
        parameters = list(unpack('<' + 'Q' * parameter_count, exception_rva + 40))
        context_size, context_rva = unpack('<II', exception_rva + 160)
        architecture = None
        if 7 in streams:
            architecture, = unpack('<H', streams[7][1])
        context = None
        candidates = []
        # Windows AMD64 CONTEXT: Rsp at152, Rip at248. Guard architecture first.
        if architecture == 9 and context_size >= 256:
            rsp, = unpack('<Q', context_rva + 152)
            rip, = unpack('<Q', context_rva + 248)
            context = dict(rip=f'0x{rip:x}', rsp=f'0x{rsp:x}', instructionModule=module_at(rip))
            if 3 in streams:
                thread_size, thread_rva = streams[3]
                threads, = unpack('<I', thread_rva)
                if 4 + 48 * threads > thread_size:
                    raise ValueError('Invalid thread stream')
                for index in range(threads):
                    offset = thread_rva + 4 + 48 * index
                    current, = unpack('<I', offset)
                    if current != thread_id:
                        continue
                    stack_start, stack_size, stack_rva = unpack('<QII', offset + 24)
                    if not stack_start <= rsp < stack_start + stack_size:
                        break
                    stack_offset = stack_rva + (rsp - stack_start)
                    size = min(1024, stack_start + stack_size - rsp)
                    for relative in range(0, size - 7, 8):
                        value, = unpack('<Q', stack_offset + relative)
                        module = module_at(value)
                        if module:
                            candidates.append(dict(stackByteOffset=relative, address=f'0x{value:x}', module=module))
                    break
        file.seek(0)
        digest = hashlib.file_digest(file, 'sha256').hexdigest()
        return dict(dump=str(path), bytes=len(data), sha256=digest,
                    timestampUtc=datetime.fromtimestamp(timestamp, timezone.utc).isoformat(),
                    architecture=architecture, flags=f'0x{flags:x}', threadId=thread_id,
                    exception=dict(code=f'0x{code:08x}', flags=exception_flags,
                                   address=f'0x{address:x}', module=module_at(address),
                                   parameters=[f'0x{value:x}' for value in parameters]),
                    context=context, stackModuleAddressCandidates=candidates,
                    modules=modules,
                    scope='Exception and module metadata. Stack word candidates are not unwound frames. No memory strings or application data extracted.',
                    references=['https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/ns-minidumpapiset-minidump_exception_stream',
                                'https://learn.microsoft.com/en-us/windows/win32/api/minidumpapiset/ns-minidumpapiset-minidump_module'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if not args.out.resolve().is_relative_to(ROOT):
        raise SystemExit('Output must be inside workspace')
    result = inspect(args.dump)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ['timestampUtc', 'threadId', 'exception', 'context']}, indent=2))
    print('Overlay-related modules: ' + ', '.join(module['name'] for module in result['modules']
          if any(word in module['name'].lower() for word in ['overlay', 'galaxy', 'rtss', 'dxgi'])))
