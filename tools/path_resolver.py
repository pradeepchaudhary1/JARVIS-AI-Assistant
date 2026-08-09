"""
JARVIS Path Resolver
Phase 2.2 - Step 5.2

Resolves Windows special folders and user-provided
file/folder paths without modifying FileLauncher.
"""

from __future__ import annotations

import os
from pathlib import Path


class PathResolver:

    SPECIAL_FOLDERS = {
        "desktop": Path.home() / "Desktop",
        "pictures": Path.home() / "Pictures",
        "videos": Path.home() / "Videos",
        "downloads": Path.home() / "Downloads",
        "documents": Path.home() / "Documents",
        "music": Path.home() / "Music",
    }

    @classmethod
    def resolve(cls, target: str) -> Path | None:

        if not target:
            return None

        target = target.strip().strip('"').strip("'")

        if not target:
            return None

        # -------------------------
        # Special folder
        # -------------------------

        key = target.lower()

        if key in cls.SPECIAL_FOLDERS:

            path = cls.SPECIAL_FOLDERS[key]

            if path.exists():
                return path

            return None

        # -------------------------
        # Environment variables
        # -------------------------

        target = os.path.expandvars(target)

        # -------------------------
        # User home expansion
        # -------------------------

        target = os.path.expanduser(target)

        # -------------------------
        # Direct path
        # -------------------------

        path = Path(target)

        if path.exists():
            return path

        # -------------------------
        # Relative path
        # -------------------------

        if not path.is_absolute():

            current_path = Path.cwd() / path

            if current_path.exists():
                return current_path

        return None