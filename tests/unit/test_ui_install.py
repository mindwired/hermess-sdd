from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hermes_sdd.ui_install import desktop_status, install_desktop, uninstall_desktop


class DesktopInstallTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name) / "hermes"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_copy_install_is_idempotent_and_removable(self) -> None:
        first = install_desktop(mode="copy", home=self.home)
        self.assertTrue(first["installed"])
        self.assertTrue(first["current"])
        self.assertEqual(first["mode"], "copy")
        self.assertTrue(first["changed"])
        second = install_desktop(mode="copy", home=self.home)
        self.assertFalse(second["changed"])
        removed = uninstall_desktop(home=self.home)
        self.assertTrue(removed["removed"])
        self.assertFalse(desktop_status(self.home)["installed"])

    def test_link_install_points_to_bundled_adapter(self) -> None:
        result = install_desktop(mode="link", home=self.home)
        self.assertEqual(result["mode"], "link")
        self.assertTrue(Path(result["target"]).is_symlink())
        self.assertTrue(result["current"])

    def test_different_existing_target_requires_force(self) -> None:
        target = self.home / "desktop-plugins" / "sdd" / "plugin.js"
        target.parent.mkdir(parents=True)
        target.write_text("different", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            install_desktop(mode="copy", home=self.home)
        result = install_desktop(mode="copy", force=True, home=self.home)
        self.assertTrue(result["current"])


if __name__ == "__main__":
    unittest.main()
