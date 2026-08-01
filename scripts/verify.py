#!/usr/bin/env python3
"""Repository-level validation with no third-party dependencies."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import py_compile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {"sdd-start", "sdd-plan", "sdd-execute", "sdd-verify", "sdd-recover"}
ALLOWED_DESKTOP_IMPORTS = {"@hermes/plugin-sdk", "react", "react/jsx-runtime"}


class VerificationError(RuntimeError):
    pass


def load_yaml_subset(path: Path) -> dict[str, Any]:
    """Parse the scalar/list subset used by plugin.yaml without requiring PyYAML."""
    result: dict[str, Any] = {}
    current_list: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - ") and current_list:
            result[current_list].append(stripped[2:].strip().strip("\"'"))
            continue
        current_list = None
        if ":" not in stripped:
            raise VerificationError(f"Unsupported YAML line in {path}: {raw}")
        key, value = stripped.split(":", 1)
        value = value.strip()
        if not value:
            result[key] = []
            current_list = key
        elif value.isdigit():
            result[key] = int(value)
        else:
            result[key] = value.strip("\"'")
    return result


def read_version() -> str:
    namespace: dict[str, Any] = {}
    exec((ROOT / "hermes_sdd" / "version.py").read_text(encoding="utf-8"), namespace)
    return str(namespace["__version__"])


def check_versions() -> list[str]:
    version = read_version()
    manifest = load_yaml_subset(ROOT / "plugin.yaml")
    dashboard = json.loads((ROOT / "dashboard" / "manifest.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    problems: list[str] = []
    for label, actual in {
        "plugin.yaml": str(manifest.get("version")),
        "dashboard/manifest.json": str(dashboard.get("version")),
    }.items():
        if actual != version:
            problems.append(f"{label} version {actual!r} != {version!r}")
    if f'version = "{version}"' not in pyproject:
        problems.append("pyproject.toml version is inconsistent")
    if f"## [{version}]" not in changelog:
        problems.append("CHANGELOG.md has no current version section")
    for skill in sorted(EXPECTED_SKILLS):
        content = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
        if f'version: "{version}"' not in content:
            problems.append(f"{skill} frontmatter version is inconsistent")
    return problems


def check_layout() -> list[str]:
    required = [
        "plugin.yaml",
        "__init__.py",
        "hermes_sdd/plugin.py",
        "hermes_sdd/core.py",
        "dashboard/manifest.json",
        "dashboard/plugin_api.py",
        "dashboard/dist/index.js",
        "desktop/plugin.js",
        "pyproject.toml",
        "uv.lock",
        "README.md",
        "LICENSE",
    ]
    problems = [
        f"missing required path: {path}" for path in required if not (ROOT / path).is_file()
    ]
    manifest = load_yaml_subset(ROOT / "plugin.yaml")
    if manifest.get("name") != "sdd":
        problems.append("plugin manifest name must remain 'sdd'")
    if manifest.get("provides_tools") != ["sdd"]:
        problems.append("plugin must expose exactly one Agent tool: sdd")
    for path in (ROOT / "README.md", ROOT / "docs" / "INSTALLATION.md", ROOT / "pyproject.toml"):
        if "OWNER" in path.read_text(encoding="utf-8"):
            problems.append(
                f"repository metadata still contains OWNER placeholder: {path.relative_to(ROOT)}"
            )
    actual_skills = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    if actual_skills != EXPECTED_SKILLS:
        problems.append(f"skill set differs: {sorted(actual_skills)}")
    return problems


def check_python() -> list[str]:
    problems: list[str] = []
    paths = [
        path
        for path in sorted(ROOT.rglob("*.py"))
        if not any(part in {".venv", "build", "release"} for part in path.parts)
    ]
    with tempfile.TemporaryDirectory(prefix="hermes-sdd-pyc-") as temp:
        for index, path in enumerate(paths):
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
                py_compile.compile(str(path), cfile=str(Path(temp) / f"{index}.pyc"), doraise=True)
            except (SyntaxError, py_compile.PyCompileError) as exc:
                problems.append(f"Python syntax: {path.relative_to(ROOT)}: {exc}")
    return problems


def check_json() -> list[str]:
    problems: list[str] = []
    for path in sorted(ROOT.rglob("*.json")):
        if any(part in {".venv", "release"} for part in path.parts):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"JSON syntax: {path.relative_to(ROOT)}: {exc}")
    return problems


def check_javascript(require_node: bool = False) -> list[str]:
    problems: list[str] = []
    node = shutil.which("node")
    targets = [ROOT / "dashboard" / "dist" / "index.js", ROOT / "desktop" / "plugin.js"]
    if node:
        for target in targets:
            run = subprocess.run([node, "--check", str(target)], text=True, capture_output=True)
            if run.returncode:
                problems.append(
                    f"JavaScript syntax: {target.relative_to(ROOT)}: {run.stderr.strip()}"
                )
    elif require_node:
        problems.append("Node.js is required but was not found")

    desktop = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    imports = set(re.findall(r"from\s+['\"]([^'\"]+)['\"]", desktop))
    unsupported = imports - ALLOWED_DESKTOP_IMPORTS
    if unsupported:
        problems.append(f"Desktop plugin imports unsupported modules: {sorted(unsupported)}")
    if "export default" not in desktop:
        problems.append("Desktop plugin must default-export a HermesPlugin")
    dashboard = (ROOT / "dashboard" / "dist" / "index.js").read_text(encoding="utf-8")
    if 'window.__HERMES_PLUGINS__.register("sdd"' not in dashboard:
        problems.append("Dashboard bundle does not register plugin name 'sdd'")
    return problems


def check_no_generated_files() -> list[str]:
    forbidden: list[str] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if "__pycache__" in rel.parts or path.suffix in {".pyc", ".pyo"}:
            forbidden.append(str(rel))
    return [f"generated file present: {item}" for item in sorted(forbidden)]


def run_verification(*, require_node: bool = False, allow_generated: bool = False) -> list[str]:
    problems: list[str] = []
    for check in (check_layout, check_versions, check_python, check_json):
        problems.extend(check())
    problems.extend(check_javascript(require_node=require_node))
    if not allow_generated:
        problems.extend(check_no_generated_files())
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-node", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    problems = run_verification(require_node=args.require_node, allow_generated=True)
    result = {
        "ok": not problems,
        "root": str(ROOT),
        "version": read_version(),
        "problems": problems,
        "sha256": hashlib.sha256((ROOT / "plugin.yaml").read_bytes()).hexdigest(),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif problems:
        print("Repository verification failed:", file=sys.stderr)
        for item in problems:
            print(f"- {item}", file=sys.stderr)
    else:
        print(f"Repository verification passed (Hermes SDD {result['version']}).")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
