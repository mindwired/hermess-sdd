"""Hermes plugin registration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .commands import register_commands
from .core import SDDService, tool_response
from .schemas import SDD_SCHEMA

logger = logging.getLogger(__name__)
_PLUGIN_ROOT = Path(__file__).resolve().parents[1]
_SERVICE: SDDService | None = None


def _handler(args: dict[str, Any], **_: Any) -> str:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = SDDService()
    return tool_response(_SERVICE, args)


def register(ctx: Any) -> None:
    """Register one compact tool, portable commands, and on-demand skills."""

    global _SERVICE
    _SERVICE = SDDService()
    ctx.register_tool(
        name="sdd",
        toolset="sdd",
        schema=SDD_SCHEMA,
        handler=_handler,
        description="Adaptive, durable, context-efficient spec-driven development",
        emoji="🧭",
    )
    register_commands(ctx, _SERVICE)

    skills_dir = _PLUGIN_ROOT / "skills"
    if hasattr(ctx, "register_skill") and skills_dir.is_dir():
        for child in sorted(skills_dir.iterdir()):
            skill_md = child / "SKILL.md"
            if child.is_dir() and skill_md.exists():
                try:
                    ctx.register_skill(child.name, skill_md)
                except Exception:
                    logger.warning("Failed to register SDD skill %s", child.name, exc_info=True)
