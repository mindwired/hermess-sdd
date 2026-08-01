#!/usr/bin/env python3
"""Build deterministic source archives after repository verification."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", "release", "build"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
FIXED_EPOCH = 315532800  # 1980-01-01, ZIP's minimum timestamp.


def files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        if path.is_file() and path.suffix not in EXCLUDED_SUFFIXES:
            result.append(path)
    return sorted(result, key=lambda p: p.relative_to(ROOT).as_posix())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_zip(output: Path, prefix: str) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in files():
            rel = source.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(f"{prefix}/{rel}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if os.access(source, os.X_OK) else 0o644) << 16
            archive.writestr(
                info, source.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9
            )


def add_tar(output: Path, prefix: str) -> None:
    with output.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9
        ) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for source in files():
                    rel = source.relative_to(ROOT).as_posix()
                    info = archive.gettarinfo(str(source), arcname=f"{prefix}/{rel}")
                    info.uid = info.gid = 0
                    info.uname = info.gname = ""
                    info.mtime = FIXED_EPOCH
                    with source.open("rb") as handle:
                        archive.addfile(info, handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "release")
    args = parser.parse_args()

    expected = {}
    exec((ROOT / "hermes_sdd" / "version.py").read_text(encoding="utf-8"), expected)
    if args.version != expected["__version__"]:
        raise SystemExit(
            f"Requested version {args.version} != source version {expected['__version__']}"
        )

    with tempfile.TemporaryDirectory(prefix="hermes-sdd-verify-") as temp:
        env = dict(os.environ)
        env["PYTHONPYCACHEPREFIX"] = temp
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify.py"), "--require-node"],
            cwd=ROOT,
            env=env,
        )
    if result.returncode:
        return result.returncode

    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    prefix = f"hermes-sdd-{args.version}"
    zip_path = output / f"{prefix}.zip"
    tar_path = output / f"{prefix}.tar.gz"
    add_zip(zip_path, prefix)
    add_tar(tar_path, prefix)
    for archive in (zip_path, tar_path):
        (archive.with_suffix(archive.suffix + ".sha256")).write_text(
            f"{sha256(archive)}  {archive.name}\n", encoding="utf-8"
        )
        print(f"{archive}  sha256={sha256(archive)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
