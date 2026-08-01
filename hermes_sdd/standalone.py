"""Standalone development CLI: ``uv run python -m hermes_sdd.standalone``."""

from __future__ import annotations

from collections.abc import Sequence

from .commands import parse_and_run
from .core import SDDService


def main(argv: Sequence[str] | None = None) -> int:
    return parse_and_run(SDDService(), argv, prog="hermes-sdd")


if __name__ == "__main__":
    raise SystemExit(main())
