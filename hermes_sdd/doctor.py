"""Installation and project diagnostics."""

from __future__ import annotations

import importlib.metadata
import json
from pathlib import Path
from typing import Any

from .registry import hermes_home
from .ui_install import desktop_status, plugin_root
from .version import MIN_HERMES_VERSION, __version__


def _version_tuple(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for item in value.split("."):
        digits = "".join(char for char in item if char.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def detect_hermes_version() -> str | None:
    for distribution in ("hermes-agent", "hermes_agent"):
        try:
            return importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            continue
    return None


def run_doctor(root: str | None = None) -> dict[str, Any]:
    repo_root = plugin_root()
    home = hermes_home()
    installed_hermes = detect_hermes_version()
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, detail: str, severity: str = "error") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail, "severity": severity})

    add("plugin_manifest", (repo_root / "plugin.yaml").is_file(), str(repo_root / "plugin.yaml"))
    add("plugin_entrypoint", (repo_root / "__init__.py").is_file(), str(repo_root / "__init__.py"))
    add(
        "dashboard_manifest",
        (repo_root / "dashboard" / "manifest.json").is_file(),
        "Dashboard adapter is bundled",
    )
    add(
        "desktop_source",
        (repo_root / "desktop" / "plugin.js").is_file(),
        "Desktop source is bundled",
    )
    add("hermes_home", home.is_dir(), str(home), severity="warning")

    if installed_hermes:
        compatible = _version_tuple(installed_hermes) >= _version_tuple(MIN_HERMES_VERSION)
        add(
            "hermes_version",
            compatible,
            f"installed={installed_hermes}, tested-minimum={MIN_HERMES_VERSION}",
            severity="warning",
        )
    else:
        add(
            "hermes_version",
            False,
            "Hermes distribution metadata was not discoverable from this Python process",
            severity="warning",
        )

    desktop = desktop_status(home)
    add(
        "desktop_adapter",
        bool(desktop.get("installed") and desktop.get("current")),
        f"mode={desktop.get('mode')}, target={desktop.get('target')}",
        severity="warning",
    )

    project: dict[str, Any] | None = None
    if root:
        project_root = Path(root).expanduser().resolve()
        initialized = (project_root / ".sdd" / "project.json").is_file()
        add("project_initialized", initialized, str(project_root), severity="warning")
        project = {"root": str(project_root), "initialized": initialized}

    errors = [check for check in checks if not check["ok"] and check["severity"] == "error"]
    warnings = [check for check in checks if not check["ok"] and check["severity"] == "warning"]
    return {
        "ok": not errors,
        "plugin_version": __version__,
        "minimum_hermes_version": MIN_HERMES_VERSION,
        "hermes_version": installed_hermes,
        "hermes_home": str(home),
        "plugin_root": str(repo_root),
        "checks": checks,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "project": project,
    }


def format_doctor(result: dict[str, Any]) -> str:
    lines = [
        f"Hermes SDD {result['plugin_version']}",
        f"Hermes: {result.get('hermes_version') or 'not detected'} (tested minimum {result['minimum_hermes_version']})",
        f"HERMES_HOME: {result['hermes_home']}",
        "",
    ]
    for check in result["checks"]:
        marker = "PASS" if check["ok"] else ("WARN" if check["severity"] == "warning" else "FAIL")
        lines.append(f"[{marker}] {check['name']}: {check['detail']}")
    return "\n".join(lines)


def doctor_json(result: dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)
