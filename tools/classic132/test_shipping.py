import contextlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_all as batch
from build_resources import strip_menu_authoring
from formats import Resource, header_crc

def fixture(author=b'editor-only-pixels'):
    strings=b'CSwfResource\0CSwfTexture\0'
    names=struct.pack('<II',0,0)+struct.pack('<II',13,0)
    texture=b'\0\0\0'+struct.pack('<6I',0,1,4,4,16,16)+bytes(range(16))+bytes(4)
    chunks=[b'\0\0\0'+struct.pack('<I',9)+b'CFXnative'+struct.pack('<I',len(author))+author,texture]
    data=bytearray(160);data[:4]=b'CR2W';struct.pack_into('<I',data,4,164)
    for index,payload,count in [(0,strings,len(strings)),(1,names,2)]:
        off=len(data);data+=payload;struct.pack_into('<III',data,40+index*12,off,count,zlib.crc32(payload))
    table=len(data);data+=bytes(48)
    for i,chunk in enumerate(chunks):
        struct.pack_into('<HHIIIII',data,table+i*24,i,0,0,len(chunk),len(data),0,zlib.crc32(chunk));data+=chunk
    struct.pack_into('<III',data,88,table,2,zlib.crc32(data[table:table+48]))
    struct.pack_into('<II',data,24,len(data),len(data));struct.pack_into('<I',data,32,header_crc(data))
    return bytes(data)

def test_root():
    root=Path(__file__).resolve().parents[2]/'tmp/classic132-shipping-tests'
    root.mkdir(parents=True,exist_ok=True)
    return root

class ShippingTests(unittest.TestCase):
    def test_editor_removed_but_native_and_textures_preserved(self):
        data=fixture();original=Resource(data);output=strip_menu_authoring(data);result=Resource(output)
        self.assertEqual(len(data)-len(output),len(b'editor-only-pixels'))
        self.assertEqual(result.chunks[0],original.chunks[0][:-len(b'editor-only-pixels')-4]+bytes(4))
        self.assertEqual(result.chunks[1:],original.chunks[1:])
        self.assertEqual(strip_menu_authoring(output),output)
        cooked=Resource(result.classic())
        self.assertEqual(cooked.classes,original.classes)
        self.assertTrue(all(r[1]==8192 for r in cooked.records))
        self.assertEqual(cooked.chunks[1][-16:],bytes(range(16)))
        self.assertEqual(cooked.classic(),cooked.data)

    def test_bad_editor_extent_is_rejected(self):
        resource=Resource(fixture());root=resource.chunks[0]
        invalid=resource.replace_chunks([root[:-1],*resource.chunks[1:]])
        with self.assertRaisesRegex(ValueError,'editor movie extent'):strip_menu_authoring(invalid)

    def test_recovery_preserves_original_and_reuses_same_stage(self):
        with tempfile.TemporaryDirectory(dir=test_root()) as temp:
            base=Path(temp)/'batch';base.mkdir()
            old={'version':'0.8.0','sourceStage':202,'generators':{'adapter':'before'}}
            current=dict(old,generators={'adapter':'after'})
            (base/'batch-inputs.json').write_text(json.dumps(old))
            menus=base/'ru/menus';menus.mkdir(parents=True);(menus/'menus.json').write_text('{}')
            target,reused=batch.recovery_output(base,current)
            self.assertNotEqual(target,base);self.assertEqual(reused,menus)
            self.assertEqual(json.loads((base/'batch-inputs.json').read_text()),old)
            self.assertEqual(batch.recovery_output(base,current)[0],target)
            with self.assertRaisesRegex(ValueError,'fresh output'):batch.recovery_output(base,current,True)
            with self.assertRaisesRegex(ValueError,'source inputs'):batch.recovery_output(base,dict(current,sourceStage=203))

    def test_failed_child_log_retains_error(self):
        with tempfile.TemporaryDirectory(dir=test_root()) as temp:
            script=Path(temp)/'child.py';script.write_text("import sys;print('real cause',flush=True);sys.exit(3)")
            output=Path(temp)/'out';capture=io.StringIO()
            with contextlib.redirect_stdout(capture),self.assertRaises(batch.subprocess.CalledProcessError):
                batch.run(script,'--out',output)
            self.assertIn('real cause',(output/'build.log').read_text())
            self.assertIn('real cause',capture.getvalue())

if __name__=='__main__':unittest.main()
