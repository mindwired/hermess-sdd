"""Hermes backend loader shim for the SDD dashboard namespace."""

from __future__ import annotations

import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parents[1]
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from hermes_sdd.dashboard_api import router  # noqa: E402

__all__ = ["router"]
