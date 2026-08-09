"""
JARVIS File & Folder Path Searcher
Phase 2.2 - Step 5.7
"""

from __future__ import annotations

import os
from pathlib import Path


class PathSearcher:

    CURRENT_PROJECT = Path.cwd()

    SEARCH_ROOTS = [
        Path.home() / "Desktop",
        Path.home() / "Pictures",
        Path.home() / "Videos",
        Path.home() / "OneDrive",
        Path.home() / "Dropbox",
    ]

    @classmethod
    def find(cls, target: str):

        target = target.strip().strip('"').strip("'")

        if not target:
            return None

        # Direct path
        direct_path = Path(
            os.path.expandvars(
                os.path.expanduser(target)
            )
        )

        if direct_path.exists():
            return direct_path

        target_lower = target.lower()

        # -------------------------
        # Prefer current project
        # -------------------------

        if (
            cls.CURRENT_PROJECT.exists()
            and cls.CURRENT_PROJECT.name.lower() == target_lower
        ):
            return cls.CURRENT_PROJECT

        # -------------------------
        # Search known roots
        # -------------------------

        for root in cls.SEARCH_ROOTS:

            if not root.exists():
                continue

            try:

                for item in root.rglob("*"):

                    if item.name.lower() == target_lower:
                        return item

            except (PermissionError, OSError):
                continue

        return None