"""
JARVIS Scheduler Store
Day 3 — persistent timer/reminder storage (SQLite, stdlib only).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional


DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "scheduler.db"
)


class SchedulerStore:

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    fire_at TEXT NOT NULL,
                    recurring TEXT,
                    created_at TEXT NOT NULL,
                    fired INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.commit()

    def add_reminder(
        self,
        message: str,
        fire_at: datetime,
        recurring: Optional[str] = None,
    ) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO reminders (message, fire_at, recurring, created_at, fired)
                VALUES (?, ?, ?, ?, 0)
                """,
                (
                    message,
                    fire_at.isoformat(),
                    recurring,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            reminder_id = cursor.lastrowid
            if reminder_id is None:
                raise RuntimeError("Failed to obtain reminder ID after insertion.")
            return reminder_id

    def get_due(self, now: Optional[datetime] = None) -> list[dict]:
        """Reminders whose fire_at has passed and are not yet fired."""
        now = now or datetime.now()
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM reminders WHERE fired = 0 AND fire_at <= ?",
                (now.isoformat(),),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_all_pending(self) -> list[dict]:
        """All not-yet-fired reminders, regardless of time (for 'what reminders do I have')."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM reminders WHERE fired = 0 ORDER BY fire_at ASC"
            ).fetchall()
            return [dict(row) for row in rows]

    def mark_fired(self, reminder_id: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE reminders SET fired = 1 WHERE id = ?",
                (reminder_id,),
            )
            conn.commit()
