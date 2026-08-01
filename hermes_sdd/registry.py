"""Global source registry used only by the visual adapters."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from .storage import resolve_root, utc_now


def hermes_home() -> Path:
    return Path(os.getenv("HERMES_HOME", "~/.hermes")).expanduser().resolve()


class SourceRegistry:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or hermes_home() / "sdd" / "sources.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    last_used_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    def register(self, path: str, name: str | None = None) -> dict[str, Any]:
        if not str(path or "").strip():
            raise ValueError("Source path is required")
        root = resolve_root(path)
        label = (name or root.name or str(root)).strip()
        now = utc_now()
        with closing(self._connect()) as connection:
            connection.execute(
                """
                INSERT INTO sources(name, path, created_at, last_used_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET name=excluded.name, last_used_at=excluded.last_used_at
                """,
                (label, str(root), now, now),
            )
            connection.commit()
            row = connection.execute(
                "SELECT * FROM sources WHERE path = ?", (str(root),)
            ).fetchone()
        return dict(row) if row else {"name": label, "path": str(root)}

    def list(self) -> list[dict[str, Any]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM sources ORDER BY last_used_at DESC, name COLLATE NOCASE"
            ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            root = Path(item["path"])
            item["exists"] = root.is_dir()
            item["initialized"] = (root / ".sdd" / "project.json").is_file()
            result.append(item)
        return result

    def remove(self, source_id: str | int) -> bool:
        with closing(self._connect()) as connection:
            if str(source_id).isdigit():
                cursor = connection.execute("DELETE FROM sources WHERE id = ?", (int(source_id),))
            else:
                cursor = connection.execute("DELETE FROM sources WHERE path = ?", (str(source_id),))
            connection.commit()
        return cursor.rowcount > 0
