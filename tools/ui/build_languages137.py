"""Build lazy native text/font resources for the 13 selectable text languages."""
import hashlib
import ctypes
import json
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
from build_beta_fonts104 import define_font3, tag
from update_board_resource import validate_resource, unpack_root, movie_parts
from install_native_hd93 import properties, string
from externalize_gui96 import rebuild

LANGUAGES = [('ru_ru', 'Русский'), ('en_us', 'English'), ('de_de', 'Deutsch'),
             ('fr_fr', 'Français'), ('it_it', 'Italiano'), ('pl_pl', 'Polski'),
             ('es_es', 'Español'), ('es_mx', 'Español (Latinoamérica)'),
             ('pt_br', 'Português (Brasil)'), ('jp_jp', '日本語'),
             ('kr_kr', '한국어'), ('zh_cn', '简体中文'), ('zh_tw', '繁體中文')]
PREPARED = ROOT / 'BetaGwent/build/languages137'
WORK = ROOT / 'BetaGwent/build/text137'
DEPOT = 'gameplay/gui_new/swf/betagwenttext'
SHA = lambda b: hashlib.sha256(b).hexdigest()


class GlyphMetrics(ctypes.Structure):
    _fields_ = [('width', ctypes.c_uint32), ('height', ctypes.c_uint32),
                ('originX', ctypes.c_int32), ('originY', ctypes.c_int32),
                ('advanceX', ctypes.c_int16), ('advanceY', ctypes.c_int16)]


def font_family(path):
    data = path.read_bytes()
    count = struct.unpack_from('>H', data, 4)[0]
    start = next(struct.unpack_from('>I', data, 12+i*16+8)[0] for i in range(count)
                 if data[12+i*16:16+i*16] == b'name')
    _, count, offset = struct.unpack_from('>3H', data, start)
    names = []
    for i in range(count):
        platform, encoding, language, ident, length, position = struct.unpack_from('>6H', data, start+6+i*12)
        if ident == 1:
            raw = data[start+offset+position:start+offset+position+length]
            name = raw.decode('utf-16-be' if platform in (0, 3) else 'mac_roman')
            names.append((language == 0x409, platform == 3, name))
    return sorted(names, reverse=True)[0][2]


def outline(data):
    def point(at):
        fx, x, fy, y = struct.unpack_from('<HhHh', data, at)
        return (x+fx/65536, y+fy/65536)
    loops = []
    at = 0
    while at < len(data):
        length, kind = struct.unpack_from('<II', data, at)
        if kind != 24 or length < 16: raise ValueError('Unknown GDI polygon')
        current = [point(at+8)]
        pos = at+16
        while pos < at+length:
            primitive, count = struct.unpack_from('<HH', data, pos)
            points = [point(pos+4+i*8) for i in range(count)]
            if primitive == 1: current.extend(points)
            elif primitive == 2:
                for i in range(count-1):
                    begin, control = current[-1], points[i]
                    end = points[i+1] if i == count-2 else tuple((points[i][k]+points[i+1][k])/2 for k in (0, 1))
                    current.extend(tuple((1-t)**2*begin[k]+2*(1-t)*t*control[k]+t*t*end[k] for k in (0, 1)) for t in (j/6 for j in range(1, 7)))
            elif primitive == 3:
                for i in range(0, count, 3):
                    begin = current[-1]; c1, c2, end = points[i:i+3]
                    current.extend(tuple((1-t)**3*begin[k]+3*(1-t)**2*t*c1[k]+3*(1-t)*t*t*c2[k]+t**3*end[k] for k in (0, 1)) for t in (j/8 for j in range(1, 9)))
            else: raise ValueError('Unknown GDI curve')
            pos += 4+count*8
        if len(current) > 2: loops.append([list(p) for p in reversed(current)])
        at += length
    return loops


def face(source, charset):
    fallbacks = [source, PREPARED/'fonts/sources/beta-ttf/PFDinTextCondPro-Regular.ttf',
                 PREPARED/'fonts/sources/noto-cjk/NotoSansSC-Medium.otf',
                 PREPARED/'fonts/sources/noto-cjk/NotoSansKR-Medium.otf', Path('C:/Windows/Fonts/arial.ttf')]
    gdi = ctypes.WinDLL('gdi32', use_last_error=True)
    gdi.CreateCompatibleDC.restype = ctypes.c_void_p
    gdi.CreateFontW.restype = ctypes.c_void_p
    gdi.CreateFontW.argtypes = [ctypes.c_int]*13+[ctypes.c_wchar_p]
    gdi.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    gdi.GetGlyphIndicesW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    gdi.GetGlyphOutlineW.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
    gdi.AddFontMemResourceEx.restype = ctypes.c_void_p
    gdi.AddFontMemResourceEx.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_void_p]
    gdi.DeleteObject.argtypes = [ctypes.c_void_p]
    gdi.DeleteDC.argtypes = [ctypes.c_void_p]
    fonts = []
    font_memory = []
    for path in dict.fromkeys(fallbacks):
        buffer = ctypes.create_string_buffer(path.read_bytes()); count = ctypes.c_uint32()
        if not gdi.AddFontMemResourceEx(buffer, len(buffer)-1, None, ctypes.byref(count)): raise RuntimeError('Cannot read font '+str(path))
        font_memory.append(buffer)
        handle = gdi.CreateFontW(-64, 0, 0, 0, 700 if 'Bold' in path.stem else 400, 0, 0, 0, 1, 0, 0, 0, 0, font_family(path))
        dc = gdi.CreateCompatibleDC(None)
        gdi.SelectObject(dc, handle)
        fonts.append((path, dc, handle))
    matrix = struct.pack('<8H', 0, 1, 0, 0, 0, 0, 0, 1)
    glyphs = {}
    missing = []
    origins = {}
    for code in sorted(charset):
        if code < 32: continue
        font = None
        glyph = ctypes.c_uint16()
        for candidate in fonts:
            gdi.GetGlyphIndicesW(candidate[1], chr(code), 1, ctypes.byref(glyph), 1)
            if glyph.value != 0xffff:
                font = candidate; break
        if font is None:
            missing.append(chr(code)); continue
        metrics = GlyphMetrics()
        size = gdi.GetGlyphOutlineW(font[1], glyph.value, 2|128|256, ctypes.byref(metrics), 0, None, matrix)
        if size == 0xffffffff: raise RuntimeError('Cannot read glyph '+hex(code))
        buffer = ctypes.create_string_buffer(size)
        gdi.GetGlyphOutlineW(font[1], glyph.value, 2|128|256, ctypes.byref(metrics), size, buffer, matrix)
        loops = outline(buffer.raw)
        xs = [x for loop in loops for x, y in loop] or [0]
        ys = [y for loop in loops for x, y in loop] or [0]
        glyphs[str(code)] = dict(advance=metrics.advanceX,
                                bounds=[min(xs), min(ys), max(xs), max(ys)], loops=loops)
        if font != fonts[0]: origins[str(code)] = font[0].name
    for path, dc, handle in fonts:
        gdi.DeleteDC(dc); gdi.DeleteObject(handle)
    if missing: raise RuntimeError('Font misses: '+repr(''.join(missing)))
    return dict(info=dict(Ascender=60, Descender=-16, LineHeight=76, CapHeight=46),
                glyphs=glyphs, kerning=[]), origins


def native_resource(swf, destination, source_name):
    reference, _ = validate_resource(ROOT/'GwentB/myproject1/workspace/betagwent/betagwent_board.redswf')
    root, _ = reference.properties_at(reference.exports[0]['data'])
    root = dict(root)
    root['importFile'] = ('String', string(source_name))
    root['importFileTimeStamp'] = ('CDateTime', bytes(8))
    root['linkageName'] = ('String', string(destination.stem+'.gfx'))
    root['textures'] = ('array:2,0,handle:CSwfTexture', struct.pack('<I', 0))
    prefix, tags, tail = movie_parts(swf)
    imports = next(raw for code, p, raw in movie_parts(unpack_root(reference)[1])[1] if code == 1000)
    body = prefix+imports+b''.join(raw for code, p, raw in tags if code != 1000)+tail
    gfx = b'CFX'+swf[3:4]+struct.pack('<I', len(body)+8)+zlib.compress(body, 9)
    payload = properties(reference, root)+struct.pack('<I', len(gfx))+gfx+struct.pack('<I', 0)
    data = rebuild(reference, [('CSwfResource', payload)])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    result, _ = validate_resource(destination)
    assert unpack_root(result)[1] == gfx
    return dict(path=DEPOT+'/'+destination.name, bytes=len(data), sha256=SHA(data))


def build(locale, label, index):
    target = WORK/locale
    target.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT/'tools'))
    from localization89 import strings
    english = strings()
    if locale == 'ru_ru': dictionary = {}
    elif locale == 'en_us': dictionary = english
    else: dictionary = json.loads((PREPARED/'ui'/f'{locale}.json').read_text('utf8'))
    supplement = json.loads((ROOT/'data/beta924/design/ui-overrides137.json').read_text('utf8'))
    rows = ['Ваш ближний ряд', 'Ваш дальний ряд', 'Ваш осадный ряд',
            'Вражеский ближний ряд', 'Вражеский дальний ряд', 'Вражеский осадный ряд']
    for key, value in zip(rows, supplement.get(locale, rows)):
        dictionary.setdefault(key, value)
    dictionary.update({k.upper(): v.upper() for k, v in list(dictionary.items()) if k})
    all_labels = ''.join(name for _, name in LANGUAGES)
    charset = set(map(ord, all_labels+' '+''.join(english.keys())+''.join(dictionary.keys())+''.join(dictionary.values())+' *^|·×←↑→↓−△○□'))
    charset.update(range(32, 127))
    # Keep untranslated dynamic diagnostics and user-entered Cyrillic legible.
    charset.update(range(0x410, 0x450)); charset.update([0x401, 0x451])
    plan = json.loads((PREPARED/'fonts/prepared'/locale/'plan.json').read_text('utf8'))
    font_tags = b''
    symbols = []
    fallback_report = {}
    for number, role in enumerate(('body', 'title'), 1):
        face_name = f'BG137_{locale}_{role}'
        class_name = f'BetaLocaleFont137{number}'
        font, fallbacks = face(ROOT/plan['faces'][role]['source'], charset)
        font_tags += define_font3(number, face_name, role == 'title', font)
        symbols.append((number, class_name))
        fallback_report[role] = fallbacks
        (target/f'{class_name}.as').write_text('package { import flash.text.Font; public class '+class_name+' extends Font {} }', 'utf8')
    lines = ['package { import flash.display.Sprite; import flash.text.Font;',
             '[SWF(width="1",height="1",frameRate="30")] public class BetaLocale137 extends Sprite {',
             'public function BetaLocale137(){Font.registerFont(BetaLocaleFont1371);Font.registerFont(BetaLocaleFont1372);}',
             f'public var bodyFont:String="BG137_{locale}_body";public var titleFont:String="BG137_{locale}_title";',
             'public var characters:String='+json.dumps(''.join(chr(c) for c in sorted(charset) if c>=32), ensure_ascii=True)+';',
             'public function dictionary():Object {var o:Object={};']
    chunks = [list(dictionary.items())[i:i+40] for i in range(0, len(dictionary), 40)]
    lines += [f'part{i}(o);' for i in range(len(chunks))]+['return o;}']
    for i, rows in enumerate(chunks):
        lines += [f'private function part{i}(o:Object):void {{']
        lines += ['o['+json.dumps(k, ensure_ascii=True)+']='+json.dumps(v, ensure_ascii=True)+';' for k, v in rows]
        lines += ['}']
    lines += ['} }']
    source = target/'BetaLocale137.as'
    source.write_text('\n'.join(lines), 'utf8')
    swf = target/'language.swf'
    java = Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    command = [str(java), '-Xmx1g', '-jar', str(ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
               '-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'), '-source-path='+str(target),
               '-source-path+='+str(ROOT/'BetaGwent/ui/src'), '-output='+str(swf), str(source)]
    with (target/'compile.log').open('wb') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
    data = swf.read_bytes()
    prefix, tags, tail = movie_parts(data)
    # This movie has no artwork; font IDs start after the compiler's symbols.
    max_id = max([struct.unpack_from('<H', p)[0] for c, p, raw in tags
                  if c in (2, 10, 11, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 48, 75, 87, 91) and len(p) >= 2] or [0])
    if max_id:
        raise RuntimeError('Unexpected drawing symbols in text/font resource')
    binding = struct.pack('<H', len(symbols))+b''.join(struct.pack('<H', n)+c.encode()+b'\0' for n, c in symbols)
    chunks_out = []
    inserted = False
    for code, p, raw in tags:
        if code in (72, 82) and not inserted:
            chunks_out.append(font_tags); inserted = True
        chunks_out.append(raw)
        if code in (72, 82):
            chunks_out.append(tag(76, binding))
    body = prefix+b''.join(chunks_out)+tail
    data = b'FWS'+data[3:4]+struct.pack('<I', len(body)+8)+body
    swf.write_bytes(data)
    output = WORK/'resources'/DEPOT/f'{locale}.redswf'
    report = native_resource(data, output, f'generated/text137/{locale}.swf')
    report.update(id=index, label=label, entries=len(dictionary), glyphs=len(charset), fallbacks=fallback_report,
                  sourceSha256=SHA(source.read_bytes()), dictionarySha256=SHA(json.dumps(dictionary, ensure_ascii=True, sort_keys=True).encode()))
    print('Built text/font', locale, report['bytes'], flush=True)
    return report


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    reports = {}
    for index, (locale, label) in enumerate(LANGUAGES, 1):
        reports[locale] = build(locale, label, index)
    report = dict(stage=137, languages=reports, allTextInEveryVoicePackage=True, loadedAtOnce=1,
                  nativeRuntimeVerified=False)
    (ROOT/'docs/evidence/languages137.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', 'utf8')


if __name__ == '__main__': main()
