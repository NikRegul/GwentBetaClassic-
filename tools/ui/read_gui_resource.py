"""Read the limited CR2W v164 GUI resource schema observed in local REDkit files.

This module never writes resources. Unknown layouts fail closed rather than
guessing at name/import references. It is not a general CR2W deserializer.
"""
from pathlib import Path
import hashlib
import struct


class ResourceError(ValueError):
    pass


class GuiResource:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        if len(self.data) < 160 or self.data[:4] != b'CR2W':
            raise ResourceError('Not a CR2W resource: ' + str(path))
        if self.unpack('<I', 4)[0] != 164:
            raise ResourceError('Unsupported CR2W version')
        self.tables = [self.unpack('<III', 40 + i * 12) for i in range(10)]
        offset, size, _ = self.tables[0]
        self.strings = self.slice(offset, size)
        offset, count, _ = self.tables[1]
        self.names = [self.string(self.unpack('<II', offset + i * 8)[0]) for i in range(count)]
        offset, count, _ = self.tables[2]
        self.imports = []
        for i in range(count):
            string_offset, class_index, flags = self.unpack('<IHH', offset + i * 8)
            self.imports.append({'path': self.string(string_offset),
                                 'class': self.name(class_index), 'flags': flags})
        offset, count, _ = self.tables[4]
        self.exports = []
        for i in range(count):
            class_index, flags, parent, size, position, template, checksum = self.unpack('<HHIIIII', offset + i * 24)
            self.exports.append({'class': self.name(class_index), 'flags': flags, 'parent': parent,
                                 'data': self.slice(position, size)})
        if not self.exports:
            raise ResourceError('No resource root')

    def slice(self, offset, size):
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise ResourceError('Resource range outside file')
        return self.data[offset:offset + size]

    def unpack(self, fmt, offset):
        return struct.unpack(fmt, self.slice(offset, struct.calcsize(fmt)))

    def string(self, offset):
        if offset < 0 or offset >= len(self.strings):
            raise ResourceError('String offset outside table')
        try:
            end = self.strings.index(0, offset)
            return self.strings[offset:end].decode('utf-8')
        except (ValueError, UnicodeError) as exc:
            raise ResourceError('Invalid resource string') from exc

    def name(self, index):
        if index < 0 or index >= len(self.names):
            raise ResourceError('Name index outside table')
        return self.names[index]

    def property(self, data, offset):
        if offset + 8 > len(data):
            raise ResourceError('Truncated property header')
        name, type_id, size = struct.unpack_from('<HHI', data, offset)
        end = offset + 4 + size
        if size < 4 or end > len(data):
            raise ResourceError('Invalid property size')
        return (self.name(name), self.name(type_id), data[offset + 8:end]), end

    def properties_at(self, data, offset=0):
        if offset >= len(data) or data[offset] != 0:
            raise ResourceError('Unsupported serialized object marker')
        output, offset = {}, offset + 1
        while offset + 2 <= len(data) and data[offset:offset + 2] != b'\0\0':
            (name, kind, value), offset = self.property(data, offset)
            if name in output:
                raise ResourceError('Duplicate property ' + name)
            output[name] = (kind, value)
        if data[offset:offset + 2] != b'\0\0':
            raise ResourceError('Unsupported object terminator')
        return output, offset + 2

    def properties(self, data):
        output, end = self.properties_at(data)
        if end != len(data):
            raise ResourceError('Trailing object bytes')
        return output

    def scalar(self, kind, value):
        if kind == 'CName' and len(value) == 2:
            return self.name(struct.unpack('<H', value)[0])
        if kind.startswith('soft:') and len(value) == 2:
            index = struct.unpack('<H', value)[0]
            if index == 0:
                return None
            if index > len(self.imports):
                raise ResourceError('Import reference outside table')
            entry = self.imports[index - 1]
            if entry['class'] != kind[5:]:
                raise ResourceError('Soft reference class mismatch')
            return entry['path']
        if kind == 'Bool' and value in (b'\0', b'\1'):
            return value == b'\1'
        raise ResourceError('Unsupported scalar ' + kind)

    def descriptions(self, kind, data, expected_kind, fields):
        if kind != expected_kind or len(data) < 4:
            raise ResourceError('Unexpected GUI description array')
        count = struct.unpack_from('<I', data)[0]
        if count > 1000:
            raise ResourceError('Unexpected GUI array count')
        offset, output = 4, []
        for _ in range(count):
            props, offset = self.properties_at(data, offset)
            expected = dict(fields)
            item = {name: None for name in expected}
            for name, (type_name, value) in props.items():
                if expected.get(name) != type_name:
                    raise ResourceError('Unexpected GUI description field')
                item[name] = self.scalar(type_name, value)
            output.append(item)
        if offset != len(data):
            raise ResourceError('Trailing GUI array bytes')
        return output

    def config(self):
        if len(self.exports) != 1 or self.exports[0]['class'] != 'CGuiConfigResource':
            raise ResourceError('Expected single CGuiConfigResource')
        props = self.properties(self.exports[0]['data'])
        if set(props) != {'huds', 'menus', 'popups', 'scene'}:
            raise ResourceError('Unsupported GUI config fields')
        result = {}
        for field, struct_name, prefix, resource in [
            ('huds', 'SHudDescription', 'hud', 'CHudResource'),
            ('menus', 'SMenuDescription', 'menu', 'CMenuResource'),
            ('popups', 'SPopupDescription', 'popup', 'CPopupResource'),
        ]:
            result[field] = self.descriptions(*props[field], 'array:2,0,' + struct_name,
                [(prefix + 'Name', 'CName'), (prefix + 'Resource', 'soft:' + resource)])
        kind, value = props['scene']
        if kind != 'SGuiSceneDescription':
            raise ResourceError('Unexpected scene schema')
        result['scene'] = {name: self.scalar(*prop) for name, prop in self.properties(value).items()}
        return result

    def menu(self):
        if self.exports[0]['class'] != 'CMenuResource':
            raise ResourceError('Expected CMenuResource')
        props = self.properties(self.exports[0]['data'])
        return {name: self.scalar(*props[name]) for name in ('menuClass', 'menuFlashSwf')}

    def manifest(self):
        return {'path': str(self.path), 'bytes': len(self.data),
                'sha256': hashlib.sha256(self.data).hexdigest()}
