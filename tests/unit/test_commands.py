from __future__ import annotations

import argparse
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from hermes_sdd.commands import build_cli_parser, handle_cli, handle_sdd
from hermes_sdd.core import SDDService
from hermes_sdd.doctor import run_doctor
from hermes_sdd.registry import SourceRegistry


class CommandTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        self.service = SDDService(SourceRegistry(self.base / "registry.db"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_slash_init_and_status(self) -> None:
        initialized = handle_sdd(
            self.service, f'init quick "Build a focused service" --root {self.root}'
        )
        self.assertIn('"created": true', initialized.lower())
        status = handle_sdd(self.service, f"status --root {self.root}")
        self.assertIn("Build a focused service", (self.root / ".sdd" / "project.json").read_text())
        self.assertIn("Mode: `quick`", status)

    def test_cli_parser_status_json(self) -> None:
        self.service.execute("init", root=str(self.root), payload={"goal": "CLI", "mode": "quick"})
        parser = build_cli_parser(argparse.ArgumentParser(prog="hermes sdd"))
        args = parser.parse_args(["status", "--root", str(self.root), "--json"])
        stream = io.StringIO()
        with redirect_stdout(stream):
            result = handle_cli(self.service, args)
        self.assertEqual(result, 0)
        self.assertTrue(json.loads(stream.getvalue())["ok"])

    def test_doctor_uses_custom_hermes_home(self) -> None:
        home = self.base / "custom-home"
        home.mkdir()
        with patch.dict(os.environ, {"HERMES_HOME": str(home)}):
            result = run_doctor(str(self.root))
        self.assertEqual(result["hermes_home"], str(home.resolve()))
        self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
