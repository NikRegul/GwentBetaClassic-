from pathlib import Path
import struct
import tempfile
import unittest

from formats import ROOT,bundle_entries,write_bundle


class BundleGuids(unittest.TestCase):
    def setUp(self):
        self.parent=(ROOT/'tmp/classic132-bundle-guid-tests').resolve()
        self.parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=self.parent)
        self.root=Path(self.temp.name).resolve()
        self.addCleanup(self.cleanup)
        self.resource=self.root/'menu.redswf';self.resource.write_bytes(b'CR2Wfixture-payload')

    def cleanup(self):
        assert self.root.is_relative_to(self.parent)
        self.temp.cleanup()

    def test_records_resource_guid_and_preserves_payload(self):
        identity=bytes(range(1,17));out=self.root/'blob.bundle'
        write_bundle({'test/menu.redswf':self.resource},out,guids={'test/menu.redswf':identity})
        data=out.read_bytes()
        self.assertEqual(data[32+256:32+272],identity)
        self.assertEqual(dict(bundle_entries(out))[r'test\menu.redswf'],self.resource.read_bytes())

    def test_missing_zero_or_malformed_gui_guid_is_rejected(self):
        for mapping in (None,{}, {'test/menu.redswf':bytes(16)}, {'test/menu.redswf':b'short'}):
            with self.subTest(mapping=mapping),self.assertRaisesRegex(ValueError,'resource GUID'):
                write_bundle({'test/menu.redswf':self.resource},self.root/'bad.bundle',guids=mapping)

    def test_non_resource_xml_does_not_require_cook_guid(self):
        xml=self.root/'items.xml';xml.write_bytes(b'<items/>')
        out=self.root/'xml.bundle';write_bundle({'items.xml':xml},out)
        self.assertEqual(out.read_bytes()[32+256:32+272],bytes(16))


if __name__=='__main__':unittest.main()
