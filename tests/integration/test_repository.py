from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RepositoryContractTest(unittest.TestCase):
    def test_dashboard_manifest_and_root_plugin_match(self) -> None:
        dashboard = json.loads((ROOT / "dashboard" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(dashboard["name"], "sdd")
        self.assertEqual(dashboard["api"], "plugin_api.py")
        self.assertTrue((ROOT / "plugin.yaml").is_file())
        self.assertTrue((ROOT / "__init__.py").is_file())

    def test_javascript_syntax_when_node_is_available(self) -> None:
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is not installed")
        for path in (ROOT / "dashboard" / "dist" / "index.js", ROOT / "desktop" / "plugin.js"):
            run = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
