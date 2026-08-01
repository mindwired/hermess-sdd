"""Generate concise human-readable views from authoritative JSON state."""

from __future__ import annotations

from pathlib import Path
from .storage import atomic_write_text, read_json


def _bullets(values: list[str], empty: str = "None recorded.") -> str:
    return "\n".join(f"- {value}" for value in values) if values else empty


def render_all(root: Path) -> None:
    sdd = root / ".sdd"
    project = read_json(sdd / "project.json", {}) or {}
    requirements = read_json(sdd / "requirements.json", {"requirements": []}) or {
        "requirements": []
    }
    roadmap = read_json(sdd / "roadmap.json", {"milestones": []}) or {"milestones": []}
    state = read_json(sdd / "state.json", {}) or {}

    project_text = f"""# Project\n\n> Generated from `.sdd/project.json`; edit through the SDD tool or UI.\n\n## Goal\n\n{project.get("goal") or "Not recorded."}\n\n## Summary\n\n{project.get("summary") or "Not recorded."}\n\n## Mode\n\n`{project.get("mode", "standard")}`\n\n## Success criteria\n\n{_bullets(project.get("success_criteria", []))}\n\n## Constraints\n\n{_bullets(project.get("constraints", []))}\n\n## Non-goals\n\n{_bullets(project.get("non_goals", []))}\n\n## Engineering principles\n\n{_bullets(project.get("principles", []))}\n"""
    atomic_write_text(sdd / "PROJECT.md", project_text)

    req_lines = ["# Requirements", "", "> Generated from `.sdd/requirements.json`.", ""]
    for req in requirements.get("requirements", []):
        req_lines.extend(
            [
                f"## {req.get('id')} — {req.get('title', 'Untitled')}",
                "",
                req.get("statement", ""),
                "",
                f"- Priority: `{req.get('priority', 'must')}`",
                f"- Status: `{req.get('status', 'active')}`",
                "- Acceptance:",
                *[f"  - {item}" for item in req.get("acceptance", [])],
                "",
            ]
        )
    atomic_write_text(sdd / "REQUIREMENTS.md", "\n".join(req_lines).rstrip() + "\n")

    roadmap_lines = ["# Roadmap", "", "> Generated from `.sdd/roadmap.json`.", ""]
    for milestone in roadmap.get("milestones", []):
        reqs = ", ".join(milestone.get("requirement_ids", [])) or "none"
        roadmap_lines.extend(
            [
                f"## {milestone.get('id')} — {milestone.get('title', 'Untitled')}",
                "",
                milestone.get("objective", ""),
                "",
                f"- Status: `{milestone.get('status', 'planned')}`",
                f"- Risk: `{milestone.get('risk', 'medium')}`",
                f"- Requirements: {reqs}",
                "- Exit criteria:",
                *[f"  - {item}" for item in milestone.get("exit_criteria", [])],
                "",
            ]
        )
    atomic_write_text(sdd / "ROADMAP.md", "\n".join(roadmap_lines).rstrip() + "\n")

    state_text = f"""# Current state\n\n> Generated from `.sdd/state.json`. Keep this file small; details live in milestone plans.\n\n- Project status: `{state.get("status", "active")}`\n- Active milestone: `{state.get("active_milestone") or "none"}`\n- Current tasks: {", ".join(state.get("current_tasks", [])) or "none"}\n- Last checkpoint: `{state.get("last_checkpoint") or "none"}`\n- Updated: `{state.get("updated_at") or "unknown"}`\n"""
    atomic_write_text(sdd / "STATE.md", state_text)


def render_decision_index(root: Path) -> None:
    decisions_dir = root / ".sdd" / "decisions"
    lines = ["# Architectural decisions", ""]
    if decisions_dir.exists():
        for path in sorted(decisions_dir.glob("ADR-*.json")):
            decision = read_json(path, {}) or {}
            lines.extend(
                [
                    f"## {decision.get('id')} — {decision.get('title', 'Untitled')}",
                    "",
                    f"- Status: `{decision.get('status', 'accepted')}`",
                    f"- Decision: {decision.get('decision', '')}",
                    "",
                ]
            )
    atomic_write_text(root / ".sdd" / "DECISIONS.md", "\n".join(lines).rstrip() + "\n")
