"""
JARVIS Session Context
Day 7 — tracks the most recently produced artifact (e.g. a generated
file) for THIS run only. Not persistent across restarts — that's
long_memory's job. This is short-lived "what did we just make"
context for resolving follow-ups like "isko PDF bana do".
"""

from __future__ import annotations

from typing import Optional


class SessionContext:

    def __init__(self):
        self._last_artifact_path: Optional[str] = None
        self._last_artifact_type: Optional[str] = None

    def set_last_artifact(self, path: str, artifact_type: str = "file") -> None:
        self._last_artifact_path = path
        self._last_artifact_type = artifact_type

    def get_last_artifact(self) -> Optional[dict]:
        if self._last_artifact_path is None:
            return None
        return {
            "path": self._last_artifact_path,
            "type": self._last_artifact_type,
        }

    def clear(self) -> None:
        self._last_artifact_path = None
        self._last_artifact_type = None