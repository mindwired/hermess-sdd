"""Install and inspect the native Hermes Desktop adapter.

The Agent and Dashboard layers live in the normal Hermes plugin directory. Native
Desktop plugins are deliberately discovered from a separate directory, so this
small bridge is the only extra installation step required for full UI support.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from .storage import atomic_write_json, utc_now
from .version import PLUGIN_ID, __version__


def hermes_home() -> Path:
    return Path(os.getenv("HERMES_HOME", "~/.hermes")).expanduser().resolve()


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def desktop_source() -> Path:
    return plugin_root() / "desktop" / "plugin.js"


def desktop_dir(home: Path | None = None) -> Path:
    return (home or hermes_home()) / "desktop-plugins" / PLUGIN_ID


def desktop_target(home: Path | None = None) -> Path:
    return desktop_dir(home) / "plugin.js"


def _digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def desktop_status(home: Path | None = None) -> dict[str, Any]:
    source = desktop_source()
    target = desktop_target(home)
    resolved_target: str | None = None
    if target.is_symlink():
        try:
            resolved_target = str(target.resolve(strict=False))
        except OSError:
            resolved_target = None
    source_digest = _digest(source)
    target_digest = _digest(target)
    return {
        "ok": True,
        "source": str(source),
        "source_exists": source.is_file(),
        "target": str(target),
        "installed": target.exists() or target.is_symlink(),
        "mode": "link" if target.is_symlink() else ("copy" if target.is_file() else "missing"),
        "link_target": resolved_target,
        "current": bool(source_digest and target_digest and source_digest == target_digest),
        "source_sha256": source_digest,
        "target_sha256": target_digest,
        "version": __version__,
    }


def _remove_target(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink(missing_ok=True)
    elif target.exists():
        raise ValueError(f"Refusing to replace non-file Desktop target: {target}")


def install_desktop(
    *,
    mode: str = "auto",
    force: bool = False,
    home: Path | None = None,
) -> dict[str, Any]:
    """Install the Desktop adapter by symlink or copy.

    ``auto`` prefers a symlink on POSIX so ``hermes plugins update sdd`` also
    updates Desktop immediately. Windows defaults to a copy because symlink
    creation often requires additional privileges.
    """

    source = desktop_source()
    if not source.is_file():
        raise FileNotFoundError(f"Desktop adapter is missing: {source}")
    if mode not in {"auto", "link", "copy"}:
        raise ValueError("Desktop install mode must be auto, link, or copy")

    target_dir = desktop_dir(home)
    target = target_dir / "plugin.js"
    target_dir.mkdir(parents=True, exist_ok=True)

    before = desktop_status(home)
    selected = mode
    if selected == "auto":
        # Keep an already-current installation stable. This makes the normal
        # command idempotent even when an older install was explicitly made as
        # a copy on POSIX. The platform-preferred mode applies to fresh installs.
        if before["installed"] and before["current"] and not force:
            selected = before["mode"]
        else:
            selected = "copy" if os.name == "nt" else "link"

    if before["installed"] and before["current"]:
        if selected == "copy" and before["mode"] == "copy":
            return {**before, "changed": False}
        if selected == "link" and before["mode"] == "link":
            return {**before, "changed": False}
        if not force:
            return {
                **before,
                "changed": False,
                "warning": f"Desktop adapter is current but installed as {before['mode']}; pass --force to switch to {selected}.",
            }

    if before["installed"] and not force and not before["current"]:
        raise FileExistsError(
            f"Desktop adapter already exists and differs: {target}. Use --force to replace it."
        )

    _remove_target(target)
    installed_mode = selected
    warning = None
    if selected == "link":
        try:
            target.symlink_to(source)
        except OSError as exc:
            if mode == "link":
                raise
            shutil.copy2(source, target)
            installed_mode = "copy"
            warning = f"Symlink creation failed; installed a copy instead: {exc}"
    else:
        shutil.copy2(source, target)

    atomic_write_json(
        target_dir / "install.json",
        {
            "plugin": PLUGIN_ID,
            "version": __version__,
            "mode": installed_mode,
            "source": str(source),
            "installed_at": utc_now(),
        },
    )
    result = desktop_status(home)
    return {**result, "changed": True, "warning": warning}


def uninstall_desktop(*, home: Path | None = None) -> dict[str, Any]:
    target_dir = desktop_dir(home)
    target = target_dir / "plugin.js"
    existed = target.exists() or target.is_symlink()
    _remove_target(target)
    (target_dir / "install.json").unlink(missing_ok=True)
    try:
        target_dir.rmdir()
    except OSError:
        pass
    return {"ok": True, "removed": existed, "target": str(target)}


def format_status(result: dict[str, Any]) -> str:
    return json.dumps(result, ensure_ascii=False, indent=2)
