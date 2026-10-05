"""Guard checks for applying a GUI overlay; uses local real resources read-only."""
import copy
import tempfile
import unittest
from pathlib import Path
from read_gui_resource import GuiResource, ResourceError
from register_board import ORIGINAL, CANDIDATE, validate_config


class RegistrationGuards(unittest.TestCase):
    def setUp(self):
        self.old = GuiResource(ORIGINAL).config()
        self.new = GuiResource(CANDIDATE).config()

    def test_editor_saved_resource_preserves_original_config(self):
        validate_config(self.old, self.new)

    def test_changed_vanilla_reference_rejected(self):
        self.new['menus'][0]['menuResource'] = r'betagwent\betagwent_board.menu'
        with self.assertRaises(ResourceError):
            validate_config(self.old, self.new)

    def test_wrong_new_menu_reference_rejected(self):
        self.new['menus'][-1]['menuResource'] = None
        with self.assertRaises(ResourceError):
            validate_config(self.old, self.new)

    def test_duplicate_registration_rejected(self):
        self.new['menus'].append(copy.deepcopy(self.new['menus'][-1]))
        with self.assertRaises(ResourceError):
            validate_config(self.old, self.new)

    def test_modified_scene_rejected(self):
        self.new['scene']['enabled'] = False
        with self.assertRaises(ResourceError):
            validate_config(self.old, self.new)

    def test_truncated_resource_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'truncated.guiconfig'
            path.write_bytes(CANDIDATE.read_bytes()[:170])
            with self.assertRaises(ResourceError):
                GuiResource(path).config()


if __name__ == '__main__':
    unittest.main()
